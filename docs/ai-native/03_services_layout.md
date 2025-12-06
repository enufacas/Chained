# AI-Native Control Plane — Services Layout

This document defines the service architecture for the AI-Native Control Plane, including:
- Service responsibilities and boundaries
- Networking and security requirements
- Observability and logging standards
- Service versioning and compatibility

---

## Service Responsibilities

The AI-Native Control Plane consists of seven core services that work together to enable autonomous infrastructure management:

### 1. **ai-control-plane**

**Role**: Central intelligence and orchestration hub

**Responsibilities**:
- Natural language intent classification and parsing
- Multi-agent planning orchestration (LangGraph)
- Tool invocation and result aggregation
- Memory retrieval from vector-db
- Pattern recognition and reuse
- Plan generation and validation
- Error recovery and replanning
- Self-improvement proposal generation

**Technology Stack**:
- Python 3.11+
- LangChain/LangGraph for agent orchestration
- OpenAI/Gemini API for LLM reasoning
- FastAPI for HTTP endpoints
- Cloud Run for deployment

**Key Endpoints**:
- `POST /intent` - Process natural language requests
- `POST /plan` - Generate execution plan from intent
- `GET /status/{request_id}` - Check request status
- `POST /feedback` - Submit feedback for learning

**Dependencies**:
- state-db (read/write)
- vector-db (read/write)
- infra-runner (invoke)

---

### 2. **infra-runner**

**Role**: Deterministic GCP infrastructure executor

**Responsibilities**:
- Execute validated infrastructure plans
- Manage GCP resources (Cloud Run, GCS, IAM, etc.)
- Ensure idempotent operations
- Health checks and validation
- Rollback capabilities
- Resource state verification
- Deterministic ID generation

**Technology Stack**:
- Python 3.11+
- Google Cloud SDK (gcloud, gsutil)
- FastAPI for HTTP endpoints
- Cloud Run for deployment

**Key Endpoints**:
- `POST /deploy_static_site` - Deploy static site to GCS bucket
- `POST /deploy_dynamic_service` - Deploy Cloud Run service
- `POST /scale_service` - Scale Cloud Run service
- `POST /attach_domain` - Configure custom domain
- `POST /validate_plan` - Validate execution plan
- `GET /check_service_health` - Health check for Cloud Run service
- `GET /check_bucket_health` - Health check for GCS bucket

**Dependencies**:
- GCP APIs (Cloud Run, GCS, IAM)
- state-db (read for validation)

**Security Requirements**:
- Service account with minimal required GCP permissions
- No direct human access
- All operations logged to event-log

---

### 3. **state-db**

**Role**: Ground truth for all system state

**Responsibilities**:
- Store all managed applications
- Track infrastructure objects and their states
- Record all operations (event sourcing)
- User and policy management
- Plan version history
- Schema version tracking
- Soft-delete support
- Transactional consistency

**Technology Stack**:
- PostgreSQL 15+ (Cloud SQL)
- Connection pooling (PgBouncer)
- Automated backups and point-in-time recovery
- Read replicas for query scaling

**Schema Components**:
- `apps` - Application registry
- `infra_objects` - Infrastructure resource tracking
- `operations` - Complete event log (replaces Git history)
- `users` - User accounts and permissions
- `policies` - Access control and governance rules
- `plan_versions` - Versioned execution plans
- `schema_versions` - Database schema evolution tracking

**Access Pattern**:
- ai-control-plane: read/write for planning and state updates
- infra-runner: read for validation, write for operation logging
- Direct queries prohibited (access only via services)

---

### 4. **vector-db**

**Role**: Semantic memory and pattern library

**Responsibilities**:
- Store embeddings of all operations, plans, and outcomes
- Enable semantic search for similar patterns
- Support pattern classification (template, style, intent, etc.)
- Facilitate learning from successful and failed operations
- Enable system self-improvement proposals
- Replace Git history with semantic memory

**Technology Stack**:
- Pinecone, Weaviate, or pgvector (PostgreSQL extension)
- Embedding model: OpenAI text-embedding-3-large or Vertex AI
- Hybrid search (semantic + metadata filters)

**Data Structure**:
```json
{
  "vector_id": "sha256_hash_of_content",
  "embedding": [0.123, -0.456, ...],  // 3072-dim or 768-dim
  "metadata": {
    "pattern_type": "template|style|intent|error_repair|system_upgrade_proposal|migration_plan",
    "operation_id": "op_xxxx",
    "timestamp": "2025-12-06T00:00:00Z",
    "success": true,
    "app_type": "static|dynamic|hybrid",
    "tags": ["deployment", "auth", "forum"],
    "plan_hash": "sha256_of_plan",
    "error_type": null,
    "recovery_method": null
  },
  "content": "Original text or structured data"
}
```

**Query Patterns**:
- Similarity search for pattern reuse
- Metadata filtering for context-specific retrieval
- Error embedding lookup for failure avoidance
- System upgrade proposal ranking

**Access Pattern**:
- ai-control-plane: read/write for memory operations
- Batch updates for offline pattern analysis

---

### 5. **static-app-host**

**Role**: GCS bucket-based static site hosting

**Responsibilities**:
- Host static HTML/CSS/JS sites
- Serve static assets (images, fonts, etc.)
- CDN integration for performance
- Custom domain support
- HTTPS via load balancer
- Versioned deployments with rollback

**Technology Stack**:
- Google Cloud Storage (GCS)
- Cloud CDN for caching
- Cloud Load Balancing for HTTPS/domains
- Automatic gzip compression

**Access Pattern**:
- infra-runner: deploys/updates buckets
- Public internet: reads static content
- No direct service-to-service calls

**Naming Convention**:
```
Bucket: {app_id}-static-{env}
Example: app-forum-2025-static-prod
```

---

### 6. **dynamic-app-host**

**Role**: Cloud Run-based dynamic application hosting

**Responsibilities**:
- Run containerized dynamic services
- Auto-scaling based on traffic
- Request routing and load balancing
- Environment variable management
- Secret management (via Secret Manager)
- Health checks and liveness probes
- Zero-downtime deployments

**Technology Stack**:
- Google Cloud Run (fully managed)
- Container Registry for images
- Secret Manager for sensitive config
- Cloud Load Balancing for custom domains

**Configuration Requirements**:
- Minimum 1 instance for critical services
- Maximum instances based on app requirements
- Request timeout: 60-300 seconds
- Concurrency: 80-1000 requests per instance
- CPU allocation: always (for background tasks) or request-only

**Access Pattern**:
- infra-runner: deploys/scales services
- ai-control-plane: may invoke services for health checks
- Public internet or VPC: service endpoints

**Naming Convention**:
```
Service: {app_id}-dynamic-{env}
Example: app-forum-2025-dynamic-prod
```

---

### 7. **event-log**

**Role**: Structured record of all infrastructure operations

**Responsibilities**:
- Immutable operation logging
- Correlation ID tracking
- Trace and span recording
- Error and warning aggregation
- Compliance audit trail
- Operations analytics
- Debugging and incident investigation

**Technology Stack**:
- Cloud Logging (Google Cloud)
- Structured JSON logs
- Log-based metrics and alerts
- Log retention: 30-400 days based on compliance needs

**Log Structure**:
```json
{
  "timestamp": "2025-12-06T12:00:00.123Z",
  "severity": "INFO|WARNING|ERROR|CRITICAL",
  "trace": "projects/PROJECT_ID/traces/TRACE_ID",
  "span_id": "SPAN_ID",
  "correlation_id": "request_xxxx",
  "service": "ai-control-plane|infra-runner|...",
  "operation": "deploy_static_site|plan_generation|...",
  "actor": "user_id|system",
  "resource": {
    "type": "app|service|bucket",
    "id": "resource_id"
  },
  "details": {
    "plan_hash": "sha256_hash",
    "duration_ms": 1234,
    "success": true,
    "error_code": null,
    "error_message": null
  },
  "metadata": {
    "app_type": "static|dynamic",
    "region": "us-central1",
    "version": "1.0.0"
  }
}
```

**Access Pattern**:
- All services: write structured logs
- ai-control-plane: read for error analysis
- Operations dashboards: query aggregated logs
- Automated alerts on ERROR/CRITICAL

---

## Networking Architecture

### Network Topology

```
                        ┌─────────────────────────┐
                        │   Public Internet       │
                        │   (HTTPS Traffic)       │
                        └───────────┬─────────────┘
                                    │
                        ┌───────────▼─────────────┐
                        │  Cloud Load Balancer    │
                        │  (HTTPS, CDN, WAF)      │
                        └───────┬─────────┬───────┘
                                │         │
                    ┌───────────▼──┐  ┌──▼──────────────┐
                    │  GCS Buckets │  │  Cloud Run      │
                    │  (Static)    │  │  (Dynamic)      │
                    └──────────────┘  └─────┬───────────┘
                                            │
            ┌───────────────────────────────┼────────────────────┐
            │         Private VPC Network                        │
            │                                                    │
            │  ┌──────────────────┐     ┌────────────────────┐  │
            │  │ ai-control-plane │────▶│  infra-runner      │  │
            │  │  (Cloud Run)     │     │  (Cloud Run)       │  │
            │  └────────┬─────────┘     └────────┬───────────┘  │
            │           │                        │               │
            │           │                        │               │
            │  ┌────────▼─────────┐     ┌───────▼────────────┐  │
            │  │   state-db       │     │   vector-db        │  │
            │  │  (Cloud SQL)     │     │  (Pinecone/pgvec)  │  │
            │  └──────────────────┘     └────────────────────┘  │
            │                                                    │
            └────────────────────────────────────────────────────┘
                                    │
                        ┌───────────▼─────────────┐
                        │   Cloud Logging         │
                        │   (event-log)           │
                        └─────────────────────────┘
```

### Service-to-Service Communication

**Private Cloud Run**:
- ai-control-plane and infra-runner deployed with `--ingress=internal`
- No public endpoints for internal services
- VPC Connector for database access
- Service identity authentication (no API keys)

**Database Access**:
- Private IP connections via Cloud SQL Proxy or VPC peering
- Connection pooling to optimize connections
- Read replicas for query scaling (state-db)
- No direct internet access to databases

**Service Account Architecture**:

```yaml
ai-control-plane Service Account:
  - roles/cloudsql.client (state-db access)
  - roles/run.invoker (infra-runner invocation)
  - Custom role for vector-db access
  - roles/logging.logWriter

infra-runner Service Account:
  - roles/storage.admin (GCS bucket management)
  - roles/run.admin (Cloud Run service management)
  - roles/iam.serviceAccountUser (for deployment)
  - roles/cloudsql.client (state-db access)
  - roles/logging.logWriter
  - Deny rules: no project-level IAM changes
```

---

## Security Requirements

### Authentication and Authorization

**Service-to-Service**:
- Google Cloud IAM service account authentication
- No API keys or bearer tokens between services
- JWT tokens with short expiration (15 minutes)
- Workload Identity for GKE (if used in future)

**User Authentication** (future):
- OAuth 2.0 / OpenID Connect
- Identity Platform or Cloud Identity
- Role-based access control (RBAC)
- Multi-factor authentication (MFA) required

**API Security**:
- Rate limiting per service account
- Request size limits (10MB max)
- Input validation on all endpoints
- SQL injection prevention (parameterized queries)
- XSS prevention in generated apps

### Network Security

**Egress Control**:
- ai-control-plane: OpenAI/Gemini APIs, vector-db
- infra-runner: GCP APIs only (Storage, Run, IAM)
- Deny-by-default firewall rules
- VPC Service Controls for sensitive projects

**Endpoint Protection**:
- Cloud Armor for DDoS protection
- WAF rules for common attacks
- TLS 1.3 only (no TLS 1.2 or below)
- Certificate management via Certificate Manager

**Secret Management**:
- All secrets in Secret Manager (API keys, DB passwords)
- Automatic secret rotation (90 days)
- No secrets in environment variables or code
- Audit logging for all secret access

---

## Observability and Logging

### Structured Logging Standards

All services must emit structured JSON logs to Cloud Logging with the following mandatory fields:

```json
{
  "timestamp": "ISO 8601 with milliseconds",
  "severity": "DEBUG|INFO|WARNING|ERROR|CRITICAL",
  "service": "service_name",
  "version": "service_version",
  "trace": "Cloud Trace ID",
  "span_id": "Span ID",
  "correlation_id": "Request correlation ID",
  "operation": "operation_name",
  "duration_ms": 1234,
  "success": true,
  "error": null,
  "metadata": {}
}
```

### OpenTelemetry Integration

**Trace Propagation**:
- W3C Trace Context standard
- Correlation IDs for request tracking
- Span IDs for operation boundaries
- Parent-child span relationships

**Instrumentation Requirements**:
- HTTP requests (incoming/outgoing)
- Database queries
- External API calls
- Tool invocations in ai-control-plane
- GCP API calls in infra-runner

**Sampling Strategy**:
- 100% sampling for errors
- 10% sampling for successful requests
- 100% sampling for operations > 5 seconds
- Adaptive sampling based on traffic

### Metrics and Monitoring

**Golden Signals** (per service):
- **Latency**: p50, p95, p99 response times
- **Traffic**: Requests per second
- **Errors**: Error rate (4xx, 5xx)
- **Saturation**: CPU, memory, active connections

**Custom Metrics**:
- ai-control-plane:
  - Plans generated per minute
  - Tool invocation success rate
  - Memory retrieval latency
  - LLM token usage
- infra-runner:
  - Deployment success rate
  - Rollback frequency
  - GCP API call rate
  - Validation failures

**Alerting**:
- Error rate > 5% for 5 minutes
- Latency p99 > 30 seconds
- Service downtime > 1 minute
- Database connection pool saturation > 80%
- Disk usage > 85%

### Distributed Tracing

**Trace Structure**:
```
Request Trace (correlation_id: req_abc123)
├── ai-control-plane: intent_classification (50ms)
├── ai-control-plane: memory_retrieval (120ms)
│   └── vector-db: similarity_search (100ms)
├── ai-control-plane: plan_generation (800ms)
│   ├── LLM API: generate_plan (750ms)
│   └── state-db: validate_constraints (40ms)
├── infra-runner: deploy_static_site (2500ms)
│   ├── GCS API: create_bucket (800ms)
│   ├── GCS API: upload_files (1600ms)
│   └── state-db: log_operation (50ms)
└── ai-control-plane: response_generation (100ms)
```

---

## Service Versioning and Compatibility

### Version Scheme

Each service uses semantic versioning: `MAJOR.MINOR.PATCH`

**Example**: `ai-control-plane:1.2.3`
- **MAJOR**: Breaking API changes, incompatible schema updates
- **MINOR**: New features, backward-compatible changes
- **PATCH**: Bug fixes, no API/schema changes

### Compatibility Matrix

Services must declare compatibility with other service versions:

```yaml
# ai-control-plane:1.2.3
compatibility:
  state_db_schema: ">=2.0.0,<3.0.0"
  vector_db_api: ">=1.0.0,<2.0.0"
  infra_runner: ">=1.1.0,<2.0.0"
  langchain_tools: ">=0.8.0,<1.0.0"
```

### Schema Versioning (state-db)

**Migration Strategy**:
1. Add `schema_versions` table tracking applied migrations
2. Backward-compatible schema changes deployed first
3. Service updates deployed after schema changes
4. Old service versions continue working during rollout
5. Breaking changes require coordinated deployment

**Schema Version Format**: `YYYYMMDD_HHMMSS_description`

**Example**:
```
20250106_120000_add_app_metadata_field.sql
20250110_093000_create_policies_table.sql
```

### Tool Versioning (LangChain)

Each LangChain tool includes version in metadata:

```python
{
  "name": "deploy_static_site",
  "version": "1.0.0",
  "description": "Deploy a static site to GCS",
  "parameters": {...},
  "returns": {...}
}
```

**Compatibility Rules**:
- Tool major version must match ai-control-plane expectations
- New tools can be added without version bump
- Deprecated tools marked but not removed for 2 minor versions

### Rolling Updates

**Deployment Strategy**:
1. Blue-green deployments for state-db schema changes
2. Canary deployments for ai-control-plane (10% → 50% → 100%)
3. Immediate rollout for infra-runner (low traffic)
4. Health checks before traffic routing
5. Automatic rollback on elevated error rates

**Rollback Policy**:
- Database migrations have reversible down-migrations
- Service rollback within 5 minutes of deployment
- State-db changes cannot be rolled back (append-only operations)

---

## Service Deployment Configuration

### ai-control-plane (Cloud Run)

```yaml
Service: ai-control-plane
Region: us-central1
CPU: 2
Memory: 4Gi
Min Instances: 1
Max Instances: 10
Concurrency: 20  # LLM calls are slow
Timeout: 300s  # 5 minutes for complex plans
Ingress: internal  # No public access
Environment Variables:
  - OPENAI_API_KEY (from Secret Manager)
  - STATE_DB_CONNECTION (Cloud SQL connection string)
  - VECTOR_DB_URL (Pinecone/pgvector endpoint)
  - INFRA_RUNNER_URL (internal Cloud Run URL)
  - LOG_LEVEL: INFO
  - SERVICE_VERSION: 1.0.0
```

### infra-runner (Cloud Run)

```yaml
Service: infra-runner
Region: us-central1
CPU: 1
Memory: 2Gi
Min Instances: 0  # Scale to zero when idle
Max Instances: 5
Concurrency: 10
Timeout: 600s  # 10 minutes for large deployments
Ingress: internal
Service Account: infra-runner@PROJECT.iam.gserviceaccount.com
Environment Variables:
  - GCP_PROJECT_ID
  - STATE_DB_CONNECTION
  - LOG_LEVEL: INFO
  - SERVICE_VERSION: 1.0.0
  - DRY_RUN: false  # Set to true for testing
```

### state-db (Cloud SQL)

```yaml
Database: PostgreSQL 15
Tier: db-custom-2-8192  # 2 vCPU, 8GB RAM
Storage: 100GB SSD (auto-resize enabled)
Backups: Automated daily, 7-day retention
Point-in-Time Recovery: Enabled
High Availability: Regional (future)
Authorized Networks: VPC only (no public IP)
```

### vector-db (Pinecone or pgvector)

**Option A: Pinecone**
```yaml
Environment: Production
Index: ai-control-plane-memory
Dimensions: 3072  # OpenAI text-embedding-3-large
Metric: cosine
Pods: 1 (p1.x1)
Replicas: 1
```

**Option B: pgvector (PostgreSQL extension)**
```sql
CREATE EXTENSION vector;
CREATE TABLE embeddings (
  id TEXT PRIMARY KEY,
  embedding vector(3072),
  metadata JSONB,
  content TEXT
);
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);
```

---

## Inter-Service Communication Patterns

### Synchronous Calls

**ai-control-plane → infra-runner**
```python
# ai-control-plane makes HTTP POST to infra-runner
import httpx

response = httpx.post(
    f"{INFRA_RUNNER_URL}/deploy_static_site",
    json={
        "app_id": "app-forum-2025",
        "bucket_name": "app-forum-2025-static-prod",
        "files": [...],
        "plan_hash": "sha256_abc123"
    },
    timeout=300.0,
    headers={"X-Correlation-ID": correlation_id}
)
```

### Asynchronous Operations (Future)

For long-running operations (> 5 minutes):
1. infra-runner returns 202 Accepted with operation_id
2. ai-control-plane polls `/operations/{operation_id}` for status
3. Or, infra-runner publishes to Pub/Sub topic when complete
4. ai-control-plane subscribes and updates state-db

### Error Handling

**Retry Strategy**:
- Exponential backoff: 1s, 2s, 4s, 8s, 16s
- Max retries: 5
- Idempotent operations only
- Non-retryable errors: 400, 401, 403, 404, 422

**Circuit Breaker**:
- Open circuit after 10 consecutive failures
- Half-open after 60 seconds
- Close circuit after 3 successful requests

---

## Performance Requirements

### Latency Targets

| Operation | Target (p95) | Maximum (p99) |
|-----------|--------------|---------------|
| Intent classification | 500ms | 1s |
| Plan generation | 3s | 10s |
| Static site deployment | 30s | 60s |
| Dynamic service deployment | 90s | 180s |
| Memory retrieval | 200ms | 500ms |
| Health check | 100ms | 200ms |

### Throughput Targets

| Service | Requests/second | Notes |
|---------|-----------------|-------|
| ai-control-plane | 10 | Limited by LLM API rate limits |
| infra-runner | 5 | Limited by GCP API quotas |
| state-db | 100 queries/s | Read-heavy workload |
| vector-db | 50 queries/s | Semantic search |

### Scalability Goals

- Support 100 concurrent users (future)
- Manage 1000 deployed apps (future)
- Store 100K operation events
- Handle 500K vector embeddings

---

## Disaster Recovery and Business Continuity

### Backup Strategy

**state-db**:
- Automated daily backups (retained 7 days)
- Point-in-time recovery window: 7 days
- Cross-region backup replication (future)

**vector-db**:
- Daily snapshot exports to GCS
- Rebuild index from state-db operations table if needed

**Deployed Apps**:
- GCS buckets have versioning enabled
- Cloud Run service definitions stored in state-db
- Can redeploy from stored plans

### Recovery Time Objectives (RTO)

| Component | RTO | Notes |
|-----------|-----|-------|
| ai-control-plane | 5 minutes | Redeploy Cloud Run service |
| infra-runner | 5 minutes | Redeploy Cloud Run service |
| state-db | 15 minutes | Restore from latest backup |
| vector-db | 30 minutes | Rebuild index from GCS |
| Deployed apps | Varies | Depends on app size |

### Recovery Point Objectives (RPO)

| Component | RPO | Notes |
|-----------|-----|-------|
| state-db | 5 minutes | Transaction log-based recovery |
| vector-db | 24 hours | Daily snapshots |
| Deployed apps | 0 | Immutable after deployment |

---

## Cost Optimization

### Resource Allocation

**Cloud Run**:
- ai-control-plane: Min 1 instance (always-on for responsiveness)
- infra-runner: Min 0 instances (scale to zero when idle)
- CPU allocation: Request-only (reduce idle costs)

**Databases**:
- state-db: Right-size based on active app count
- Start with db-custom-2-8192, scale up as needed
- Use Cloud SQL connection pooling

**Storage**:
- GCS Standard class for active apps
- Nearline class for archived apps (> 30 days inactive)
- Lifecycle policies to transition automatically

### Estimated Monthly Costs

**Base Infrastructure** (low usage):
- ai-control-plane: $50 (1 instance, 50% CPU)
- infra-runner: $10 (scales to zero)
- state-db: $200 (db-custom-2-8192)
- vector-db: $70 (Pinecone starter)
- Cloud Logging: $50 (50GB/month)
- **Total: ~$380/month**

**With 100 Apps Deployed**:
- Static sites: $20 (GCS storage + egress)
- Dynamic services: $500 (10 active Cloud Run services)
- Additional logging: $100
- **Total: ~$1000/month**

---

## Compliance and Auditing

### Audit Logging

All operations must be auditable:
- Who performed the action (user or system)
- What was changed (before/after snapshots)
- When it occurred (precise timestamp)
- Why (plan_hash, correlation_id)
- Result (success/failure, error details)

### Data Retention

| Data Type | Retention Period | Rationale |
|-----------|------------------|-----------|
| Operations log | 1 year | Compliance, debugging |
| Vector embeddings | Indefinite | Learning and improvement |
| State-db records | Indefinite (soft delete) | Audit trail |
| Cloud Logs | 30 days | Cost optimization |
| Backups | 7 days | Disaster recovery |

### Privacy Considerations (Future)

- User data stored in compliance with GDPR/CCPA
- Right to erasure supported (soft delete)
- Data anonymization for analytics
- Encryption at rest and in transit

---

## Future Enhancements

### High Availability

- Multi-region deployment (active-passive)
- Cross-region database replication
- Global load balancing
- Automated failover

### Advanced Features

- WebSocket support for real-time updates
- GraphQL API for complex queries
- Batch operation APIs
- Scheduled maintenance windows
- Cost prediction and optimization
- Capacity planning automation

### Observability

- Custom Grafana dashboards
- Proactive anomaly detection
- Cost attribution per app
- Performance regression detection
- SLO/SLI tracking

---

*This document is part of the AI-Native Control Plane specification defined in `.github/copilot/tasks/ai-native-control-plane.md`*

**Last updated**: 2025-12-06
