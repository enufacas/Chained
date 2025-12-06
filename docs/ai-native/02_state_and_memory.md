# AI-Native Control Plane — World State Data Model

This document defines the complete data model for the AI-Native Control Plane, including:
- Structured database tables (state-db)
- Operation event logging
- Vector database schema (vector-db)  
- Semantic memory classification

Together, these replace Git history, file diffs, and traditional state management.

---

## Structured Database Tables (state-db)

The state-db serves as the **ground truth** for all system state. It uses PostgreSQL or Google Cloud SQL.

### Table: `apps`

Stores all applications managed by the control plane.

```sql
CREATE TABLE apps (
    app_id VARCHAR(64) PRIMARY KEY,  -- Deterministic hash: SHA256(name + creation_timestamp)
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    app_type VARCHAR(50) NOT NULL,  -- 'static', 'dynamic', 'hybrid'
    owner_user_id VARCHAR(64) NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,  -- Soft delete
    status VARCHAR(50) NOT NULL,  -- 'draft', 'deploying', 'active', 'failed', 'archived'
    metadata JSONB,  -- Flexible metadata (tags, custom fields)
    current_version VARCHAR(64),  -- References plan_versions(version_hash)
    CONSTRAINT app_type_check CHECK (app_type IN ('static', 'dynamic', 'hybrid')),
    CONSTRAINT status_check CHECK (status IN ('draft', 'deploying', 'active', 'failed', 'archived'))
);

CREATE INDEX idx_apps_owner ON apps(owner_user_id);
CREATE INDEX idx_apps_status ON apps(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_apps_name ON apps(name) WHERE deleted_at IS NULL;
```

**Key Fields**:
- `app_id`: Deterministic ID derived from name and creation time (no UUIDs)
- `app_type`: Static (GCS bucket), dynamic (Cloud Run), or hybrid
- `current_version`: Links to the plan that generated the current deployment
- `metadata`: JSONB for extensible properties without schema changes

---

### Table: `infra_objects`

Stores all infrastructure resources created by the control plane.

```sql
CREATE TABLE infra_objects (
    object_id VARCHAR(64) PRIMARY KEY,  -- Deterministic hash
    app_id VARCHAR(64) NOT NULL REFERENCES apps(app_id),
    object_type VARCHAR(100) NOT NULL,  -- 'gcs_bucket', 'cloud_run_service', 'domain_mapping', 'cdn', 'database'
    gcp_resource_name VARCHAR(500) NOT NULL,  -- Full GCP resource name
    gcp_resource_id VARCHAR(500),  -- GCP internal ID (if applicable)
    region VARCHAR(50),
    configuration JSONB NOT NULL,  -- Full resource configuration
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    health_status VARCHAR(50),  -- 'healthy', 'degraded', 'unhealthy', 'unknown'
    last_health_check TIMESTAMP,
    CONSTRAINT object_type_check CHECK (object_type IN ('gcs_bucket', 'cloud_run_service', 'domain_mapping', 'cdn', 'database', 'secret', 'load_balancer'))
);

CREATE INDEX idx_infra_app ON infra_objects(app_id);
CREATE INDEX idx_infra_type ON infra_objects(object_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_infra_health ON infra_objects(health_status) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_infra_gcp_name ON infra_objects(gcp_resource_name) WHERE deleted_at IS NULL;
```

**Key Fields**:
- `gcp_resource_name`: Full GCP resource name (e.g., `projects/my-project/buckets/my-bucket`)
- `configuration`: Complete JSONB snapshot of resource config
- `health_status`: Real-time health from observability layer

---

### Table: `operations` (Event Log)

Immutable log of every infrastructure mutation. This is the **event sourcing** foundation.

```sql
CREATE TABLE operations (
    operation_id VARCHAR(64) PRIMARY KEY,  -- Deterministic hash
    operation_type VARCHAR(100) NOT NULL,  -- 'deploy', 'scale', 'update', 'delete', 'heal'
    actor_type VARCHAR(50) NOT NULL,  -- 'user', 'ai_agent', 'system'
    actor_id VARCHAR(64) NOT NULL,  -- user_id or agent identifier
    app_id VARCHAR(64) REFERENCES apps(app_id),
    plan_hash VARCHAR(64) NOT NULL,  -- Links to the plan that produced this operation
    object_id VARCHAR(64) REFERENCES infra_objects(object_id),
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(50) NOT NULL,  -- 'pending', 'running', 'success', 'failed', 'rolled_back'
    before_snapshot JSONB,  -- State before mutation
    after_snapshot JSONB,  -- State after mutation (NULL if failed)
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    parent_operation_id VARCHAR(64) REFERENCES operations(operation_id),  -- For multi-step plans
    vector_embedding_id VARCHAR(64),  -- Link to vector-db for pattern analysis
    metadata JSONB,
    CONSTRAINT actor_type_check CHECK (actor_type IN ('user', 'ai_agent', 'system')),
    CONSTRAINT status_check CHECK (status IN ('pending', 'running', 'success', 'failed', 'rolled_back'))
);

CREATE INDEX idx_operations_app ON operations(app_id);
CREATE INDEX idx_operations_actor ON operations(actor_id, actor_type);
CREATE INDEX idx_operations_plan ON operations(plan_hash);
CREATE INDEX idx_operations_status ON operations(status);
CREATE INDEX idx_operations_time ON operations(started_at DESC);
CREATE INDEX idx_operations_embedding ON operations(vector_embedding_id) WHERE vector_embedding_id IS NOT NULL;
```

**Key Fields**:
- `plan_hash`: SHA256 of the complete plan that generated this operation
- `before_snapshot` / `after_snapshot`: Complete state captures for time-travel debugging
- `vector_embedding_id`: Links to vector-db for learning from this operation
- `parent_operation_id`: Enables hierarchical multi-step plans

**Why This Replaces Git**:
- Complete audit trail without commits/pushes
- No merge conflicts (single source of truth)
- Time-travel via snapshot replay
- Automatic linking to semantic patterns

---

### Table: `users`

Basic user management.

```sql
CREATE TABLE users (
    user_id VARCHAR(64) PRIMARY KEY,  -- Deterministic hash from identity provider
    email VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'developer',  -- 'admin', 'developer', 'viewer'
    CONSTRAINT role_check CHECK (role IN ('admin', 'developer', 'viewer'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;
```

---

### Table: `policies`

Constraints and rules that the AI must respect.

```sql
CREATE TABLE policies (
    policy_id VARCHAR(64) PRIMARY KEY,
    policy_name VARCHAR(255) NOT NULL UNIQUE,
    policy_type VARCHAR(50) NOT NULL,  -- 'resource_limit', 'region_restriction', 'cost_cap', 'security_rule'
    scope VARCHAR(50) NOT NULL,  -- 'global', 'user', 'app'
    scope_id VARCHAR(64),  -- user_id or app_id (NULL for global)
    rules JSONB NOT NULL,  -- Policy rules in structured format
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT policy_type_check CHECK (policy_type IN ('resource_limit', 'region_restriction', 'cost_cap', 'security_rule')),
    CONSTRAINT scope_check CHECK (scope IN ('global', 'user', 'app'))
);

CREATE INDEX idx_policies_active ON policies(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_policies_scope ON policies(scope, scope_id);
```

**Example Policy**:
```json
{
  "policy_name": "max_cloud_run_instances",
  "policy_type": "resource_limit",
  "scope": "global",
  "rules": {
    "max_instances": 10,
    "per_service": 5
  }
}
```

---

### Table: `plan_versions`

Stores validated plans before execution.

```sql
CREATE TABLE plan_versions (
    version_hash VARCHAR(64) PRIMARY KEY,  -- SHA256 of plan content
    app_id VARCHAR(64) NOT NULL REFERENCES apps(app_id),
    plan_content JSONB NOT NULL,  -- Complete plan specification
    plan_type VARCHAR(50) NOT NULL,  -- 'initial_deploy', 'update', 'scale', 'migration'
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by_actor_type VARCHAR(50) NOT NULL,
    created_by_actor_id VARCHAR(64) NOT NULL,
    validated_at TIMESTAMP,
    validation_status VARCHAR(50),  -- 'pending', 'valid', 'invalid'
    validation_errors JSONB,
    executed_at TIMESTAMP,
    execution_operation_id VARCHAR(64) REFERENCES operations(operation_id),
    CONSTRAINT plan_type_check CHECK (plan_type IN ('initial_deploy', 'update', 'scale', 'migration')),
    CONSTRAINT validation_status_check CHECK (validation_status IN ('pending', 'valid', 'invalid'))
);

CREATE INDEX idx_plans_app ON plan_versions(app_id);
CREATE INDEX idx_plans_created ON plan_versions(created_at DESC);
CREATE INDEX idx_plans_validation ON plan_versions(validation_status);
```

---

### Table: `schema_versions`

Tracks database schema evolution.

```sql
CREATE TABLE schema_versions (
    version_id VARCHAR(64) PRIMARY KEY,  -- Format: schema_{timestamp}_{description}
    applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
    migration_script TEXT NOT NULL,
    rollback_script TEXT,
    status VARCHAR(50) NOT NULL,  -- 'applied', 'failed', 'rolled_back'
    CONSTRAINT status_check CHECK (status IN ('applied', 'failed', 'rolled_back'))
);

CREATE INDEX idx_schema_applied ON schema_versions(applied_at DESC);
```

---

## Field-Level Requirements

### Deterministic IDs
All primary keys must be **hash-based**, not random:

```python
def generate_deterministic_id(entity_type: str, key_attributes: dict) -> str:
    """
    Generate a deterministic ID for any entity.
    
    Examples:
      app_id = SHA256("app:my-forum:2025-01-01T00:00:00Z")
      object_id = SHA256("infra:my-forum:gcs_bucket:my-forum-static")
    """
    canonical_repr = f"{entity_type}:" + ":".join(
        str(v) for k, v in sorted(key_attributes.items())
    )
    return hashlib.sha256(canonical_repr.encode()).hexdigest()
```

**Benefits**:
- Same inputs always produce same IDs
- No need for ID generation coordination
- IDs are reproducible across environments
- Simplifies testing and validation

### Constraints
- All `VARCHAR` lengths are generous but bounded
- All `CHECK` constraints enforce valid states
- All foreign keys enforce referential integrity
- All timestamps use `TIMESTAMP` with timezone awareness

### Indexes
- Optimized for common query patterns:
  - Lookup by ID (primary key)
  - Filter by status and active records
  - Time-series queries on operations
  - Joins on foreign keys

---

## Operation Events: Complete Logging

Every infrastructure mutation MUST log to the `operations` table with:

### Required Fields
1. **actor**: Who initiated the operation (user, AI agent, system)
2. **plan_hash**: Links to the validated plan
3. **before_snapshot**: Complete state before mutation (JSONB)
4. **after_snapshot**: Complete state after mutation (JSONB) (or NULL if failed)
5. **timestamps**: `started_at` and `completed_at`
6. **vector_embedding_id**: Link to semantic memory (if applicable)

### Snapshot Format
```json
{
  "object_id": "abc123...",
  "object_type": "cloud_run_service",
  "gcp_resource_name": "projects/my-project/locations/us-central1/services/my-service",
  "configuration": {
    "image": "gcr.io/my-project/my-app:v1.2.3",
    "memory": "512Mi",
    "cpu": "1",
    "max_instances": 10,
    "env_vars": {"KEY": "value"}
  },
  "health_status": "healthy",
  "last_health_check": "2025-01-01T12:00:00Z"
}
```

### Audit Trail Example
```sql
-- Find all operations on a specific app
SELECT * FROM operations 
WHERE app_id = 'app_abc123' 
ORDER BY started_at DESC;

-- Find who scaled a service and when
SELECT actor_type, actor_id, started_at, before_snapshot, after_snapshot
FROM operations
WHERE operation_type = 'scale' 
  AND object_id = 'obj_xyz789'
ORDER BY started_at DESC;

-- Replay state at a specific timestamp (time-travel debugging)
SELECT after_snapshot 
FROM operations
WHERE object_id = 'obj_xyz789'
  AND completed_at <= '2025-01-01T10:00:00Z'
  AND status = 'success'
ORDER BY completed_at DESC
LIMIT 1;
```

---

## Vector Database Schema (vector-db)

The vector-db stores **semantic memory** for pattern reuse and learning. Uses Pinecone, Weaviate, or pgvector.

### Embedding Structure

Each embedding represents a **semantic pattern** (successful plan, error+repair, template, etc.).

```python
{
    "embedding_id": "emb_abc123...",  # Deterministic hash
    "vector": [0.123, -0.456, ...],  # 1536-dimensional embedding (OpenAI ada-002)
    "metadata": {
        "pattern_type": "template",  # See classification below
        "system_version": "v0.1.0",
        "created_at": "2025-01-01T12:00:00Z",
        "source_operation_id": "op_xyz789",  # Links to operations table
        "source_plan_hash": "plan_abc123",
        "app_type": "dynamic",
        "gcp_services_used": ["cloud_run", "cloud_sql"],
        "success_score": 1.0,  # 0-1 (0 = failure, 1 = perfect success)
        "usage_count": 42,  # How many times this pattern has been reused
        "last_used_at": "2025-01-15T08:00:00Z",
        "tags": ["forum", "authentication", "postgres"],
        "natural_language_description": "Deploy a forum with user auth and PostgreSQL database"
    }
}
```

### Pattern Classification (Enhanced Metadata)

The `pattern_type` field classifies semantic patterns:

1. **`template`**: Reusable starting point for common apps
   - Example: "Static blog site", "REST API with database"
   
2. **`style`**: Coding or architectural preference
   - Example: "Use React for SPAs", "Prefer serverless over VMs"
   
3. **`intent`**: User goal or desired outcome
   - Example: "Deploy quickly", "Optimize for cost", "Maximize reliability"
   
4. **`system_upgrade_proposal`**: Proposed improvement to the control plane itself
   - Example: "Add CDN support", "Improve error recovery"
   
5. **`migration_plan`**: Strategy for moving between states
   - Example: "Zero-downtime database migration", "Blue-green deployment"
   
6. **`error_repair`**: Known failure + successful recovery
   - Example: "Out of memory → increased instance size", "CORS error → added headers"

### Similarity Search Query

```python
def find_similar_patterns(query_text: str, top_k: int = 5, filters: dict = None):
    """
    Find the top_k most similar patterns to a natural language query.
    
    Args:
        query_text: Natural language description (e.g., "deploy a forum with auth")
        top_k: Number of results to return
        filters: Optional metadata filters (e.g., {"app_type": "dynamic"})
    
    Returns:
        List of (embedding_id, similarity_score, metadata)
    """
    query_embedding = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=query_text
    )
    
    results = vector_db.query(
        vector=query_embedding,
        top_k=top_k,
        filter=filters,
        include_metadata=True
    )
    
    return results
```

**Example Usage**:
```python
# User request: "Create a news site with automatic content aggregation"
similar_patterns = find_similar_patterns(
    query_text="news site automatic content aggregation",
    filters={"pattern_type": "template", "success_score": {"$gte": 0.8}}
)

# Returns patterns for:
# 1. Static news site with RSS feeds (similarity: 0.92)
# 2. Dynamic blog with auto-posting (similarity: 0.87)
# 3. Content aggregator with webhooks (similarity: 0.84)
```

---

## Why Semantic Memory Matters

### 1. **Enables Planning Reuse**
Instead of planning from scratch every time:
- New request → vector search → find analogous past plans → adapt and execute
- Reduces planning time from minutes to seconds
- Improves consistency (reuse proven patterns)

### 2. **Enables System Self-Improvement**
The control plane can evolve itself:
- Analyze patterns with high `success_score` → generalize into templates
- Analyze patterns with low `success_score` → identify common failures
- Propose upgrades based on usage trends (e.g., "90% of apps need auth, should add auth tool")

### 3. **Replaces Git History**
Traditional approach:
```
Git log → file diffs → manual code review → infer patterns
```

AI-Native approach:
```
Operations log → semantic embeddings → automatic pattern extraction → instant reuse
```

**Benefits**:
- No merge conflicts
- No manual code review needed
- Automatic learning from every deployment
- Patterns transferable across languages/frameworks

### 4. **Removes Need for File Diffs**
Instead of:
```diff
- max_instances: 5
+ max_instances: 10
```

We store:
```json
{
  "operation": "scale",
  "before": {"max_instances": 5},
  "after": {"max_instances": 10},
  "embedding": [vector representing "scaling up due to traffic spike"]
}
```

Later requests like "handle more traffic" automatically retrieve this pattern.

---

## Integration: state-db ↔ vector-db

### Writing Pattern
1. Operation completes successfully → log to `operations` table
2. Extract semantic representation of the operation
3. Generate embedding via OpenAI API
4. Store in vector-db with link to `operation_id`
5. Update `operations.vector_embedding_id`

### Reading Pattern
1. New user request → classify intent
2. Generate embedding of request
3. Query vector-db for similar patterns
4. Retrieve `operation_id` from top matches
5. Query `operations` table for full details
6. Adapt plan based on historical context
7. Execute new plan and log new operation

---

## Next Steps

With the data model in place, the next documents will detail:

1. **Services Layout** (`03_services_layout.md`): How services interact with these databases
2. **Infra Runner API** (`04_infra_runner_api.md`): API endpoints for infrastructure mutation
3. **LangChain Tools** (`05_langchain_tools.md`): Tools that read/write state and memory
4. **Agent Graph** (`06_agent_graph.md`): How agents use semantic memory for planning

---

*This document is part of the AI-Native Control Plane specification defined in `.github/copilot/tasks/ai-native-control-plane.md`*
