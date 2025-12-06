# AI-Native Control Plane — Overview

## What is an AI-Native Control Plane?

An **AI-Native Control Plane** is a cloud infrastructure management system where artificial intelligence agents, not humans, operate and orchestrate cloud resources. Instead of writing Terraform configurations, managing Git repositories, or configuring CI/CD pipelines, developers interact with the system using **natural language commands**.

The system accepts requests like:
- *"Create a web forum with posts, comments, upvotes, auth, and admin tools. Deploy it."*
- *"Build a news site that automatically pulls infrastructure announcements and displays them with tags."*
- *"Deploy version 0.2 of this control plane with improved planning and stronger validation."*

The AI autonomously:
1. **Plans** the required architecture
2. **Builds** the application code and infrastructure
3. **Deploys** to cloud services
4. **Monitors** and self-heals
5. **Evolves** by learning from patterns and failures

## Why This Removes Traditional DevOps Tools

### No Terraform or Infrastructure-as-Code (IaC)
- **Traditional**: Write declarative configs, run `terraform plan`, review diffs, apply changes
- **AI-Native**: Describe desired state in natural language; AI plans and executes deterministically
- **Benefits**: No YAML/HCL syntax to learn, no state file management, instant deployment

### No Git-Based Workflows
- **Traditional**: Commit code, push to repository, trigger CI pipeline, review PRs
- **AI-Native**: World state stored in structured databases with full event logs; semantic memory in vector DB
- **Benefits**: Complete traceability without merge conflicts; patterns reused via embeddings instead of file diffing

### No Manual CI/CD Pipelines
- **Traditional**: Configure Jenkins/GitHub Actions/GitLab CI with build/test/deploy stages
- **AI-Native**: AI orchestrates build and deployment based on intent; operations logged as events
- **Benefits**: Zero pipeline configuration; automatic error recovery; self-improving deployment strategies

### No Manual Infrastructure Operations
- **Traditional**: SSH into servers, kubectl commands, manual scaling, incident response
- **AI-Native**: AI monitors health, auto-scales, self-heals failures, learns from incidents
- **Benefits**: 24/7 autonomous operations; instant response to anomalies; continuous optimization

---

## Components Summary

The AI-Native Control Plane consists of eight core components:

### 1. **ai-control-plane**
- **Role**: Central intelligence and orchestration
- **Responsibilities**: 
  - Natural language intent classification
  - Multi-step planning with LangChain/LangGraph
  - Tool orchestration and execution
  - Pattern retrieval from vector memory
  - Self-improvement proposal generation
- **Technology**: Python, LangChain, LangGraph, OpenAI/Gemini APIs

### 2. **infra-runner**
- **Role**: Deterministic cloud infrastructure mutation
- **Responsibilities**:
  - Execute validated infrastructure plans
  - Deploy static sites to GCS buckets
  - Deploy dynamic services to Cloud Run
  - Manage scaling, domains, and health checks
  - Validate plans before execution
- **Technology**: Python, FastAPI, Google Cloud SDK

### 3. **state-db**
- **Role**: Ground truth for all system state
- **Responsibilities**:
  - Store applications, infrastructure objects, operations
  - Maintain deterministic IDs for all resources
  - Track schema versions
  - Provide audit trail via event log
- **Technology**: PostgreSQL or Cloud SQL
- **Tables**: `apps`, `infra_objects`, `operations`, `users`, `policies`, `plan_versions`, `schema_versions`

### 4. **vector-db**
- **Role**: Semantic memory for pattern reuse and learning
- **Responsibilities**:
  - Store embeddings of successful plans
  - Enable similarity search for analogous problems
  - Classify patterns (template, style, intent, error+repair)
  - Support self-improvement by tracking upgrades
- **Technology**: Pinecone, Weaviate, or pgvector
- **Metadata**: pattern type, system version, success metrics, usage count

### 5. **static-app-host**
- **Role**: Host static websites and single-page applications
- **Responsibilities**:
  - Serve HTML/CSS/JS files from GCS buckets
  - CDN integration for global distribution
  - Custom domain mapping
  - SSL certificate management
- **Technology**: Google Cloud Storage, Cloud CDN

### 6. **dynamic-app-host**
- **Role**: Host server-side applications and APIs
- **Responsibilities**:
  - Deploy containerized services to Cloud Run
  - Auto-scaling based on traffic
  - Private networking with IAM-based service auth
  - Environment variable and secret management
- **Technology**: Cloud Run, Docker containers

### 7. **event-log**
- **Role**: Immutable record of all system operations
- **Responsibilities**:
  - Log every infrastructure mutation with before/after snapshots
  - Track actor, plan hash, timestamps
  - Link to vector embeddings for pattern analysis
  - Enable time-travel debugging and rollback
- **Technology**: Integrated into `state-db` as `operations` table

### 8. **observability-layer**
- **Role**: Real-time monitoring and tracing
- **Responsibilities**:
  - Collect structured logs from all services
  - Trace requests with correlation IDs
  - Generate OpenTelemetry spans
  - Alert on anomalies and failures
  - Feed data into self-healing and learning systems
- **Technology**: Cloud Logging, Cloud Trace, OpenTelemetry


---

## Architecture Diagrams

### Request Flow
```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INPUT                                 │
│          "Create a web forum with auth and admin tools"            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AI-CONTROL-PLANE                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │  Intent      │  │  Planner     │  │  Memory Agent           │  │
│  │  Classifier  │──│  Agent       │──│  (fetch patterns)       │  │
│  └──────────────┘  └──────┬───────┘  └─────────────────────────┘  │
│                            │                                         │
│  ┌─────────────────────────┴───────────────────────┐               │
│  │           LangChain Tool Calls                   │               │
│  │  - create_app_spec()                             │               │
│  │  - build_dynamic_app()                           │               │
│  │  - deploy_dynamic_service()                      │               │
│  └──────────────────────────┬───────────────────────┘               │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌────────────────┐  ┌────────────────┐
│  INFRA-RUNNER   │  │   STATE-DB     │  │   VECTOR-DB    │
│  (GCP mutation) │  │  (world state) │  │  (patterns)    │
└────────┬────────┘  └────────────────┘  └────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│        GCP SERVICES                 │
│  - Cloud Storage (static sites)     │
│  - Cloud Run (dynamic services)     │
│  - Cloud SQL (databases)            │
│  - Load Balancers                   │
└─────────────────────────────────────┘
```

### Data Access Patterns
```
┌─────────────────────────────────────────────────────────────────────┐
│                     AI-CONTROL-PLANE                                │
└───────┬─────────────────────────┬───────────────────────────────────┘
        │                         │
        │ (1) Fetch analogous     │ (2) Read/Write
        │     patterns            │     current state
        │                         │
        ▼                         ▼
┌─────────────────┐         ┌──────────────────────────────┐
│   VECTOR-DB     │         │         STATE-DB             │
│                 │         │                              │
│ - embeddings    │         │  ┌────────┐  ┌────────────┐ │
│ - metadata      │         │  │  apps  │  │  policies  │ │
│ - similarity    │         │  └────────┘  └────────────┘ │
│   search        │         │                              │
│                 │         │  ┌──────────────┐           │
│                 │         │  │  operations  │ (event log)│
│                 │         │  └──────────────┘           │
└─────────────────┘         └──────────────────────────────┘
        │                           │
        │                           │
        └────────────┬──────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │  OBSERVABILITY LAYER   │
         │  - logs                │
         │  - traces              │
         │  - metrics             │
         └────────────────────────┘
```

### Plan Execution Lifecycle
```
┌───────────────────────────────────────────────────────────────────┐
│ 1. USER REQUEST                                                   │
│    Natural language input                                         │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ 2. INTENT CLASSIFICATION                                          │
│    Classify as: create_app | update_app | deploy | scale | heal  │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ 3. PATTERN RETRIEVAL                                              │
│    Query vector-db for similar past plans                         │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ 4. PLAN GENERATION                                                │
│    LangGraph agents create multi-step execution plan             │
│    - Planner Agent: high-level strategy                          │
│    - Policy Agent: validate constraints                          │
│    - App Builder Agent: generate code artifacts                  │
│    - Infra Agent: plan GCP resources                             │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ 5. PLAN VALIDATION                                                │
│    infra-runner validates plan for safety and feasibility         │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ 6. EXECUTION                                                      │
│    infra-runner executes plan deterministically                   │
│    - Deploy artifacts to GCS/Cloud Run                           │
│    - Update state-db with new infra objects                      │
│    - Log operation to event log                                  │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ 7. MEMORY UPDATE                                                  │
│    Store successful plan in vector-db with embeddings            │
│    Link operation events to semantic patterns                    │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ 8. RESPONSE                                                       │
│    Return success message with deployment URLs and metadata      │
└───────────────────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. **Determinism**
Every plan execution produces the same result given the same input state. This enables:
- Reproducible deployments
- Safe plan validation before execution
- Time-travel debugging via event log replay
- Predictable system behavior

**Implementation**:
- Deterministic ID generation (hash-based, not random)
- Plan hashing to detect changes
- Idempotent operations (running twice = same result)
- No hidden global state

### 2. **Idempotency**
Operations can be safely repeated without side effects:
- `deploy_static_site(spec)` → deploys if needed, no-op if already deployed
- `scale_service(name, instances=3)` → sets to 3, regardless of current count
- `attach_domain(service, domain)` → maps domain, no error if already mapped

**Benefits**:
- Safe retries on transient failures
- Simplified error recovery
- No need for complex "undo" logic

### 3. **Pattern Recognition**
The system learns from every operation:
- Successful plans stored as embeddings
- Failures tagged with error patterns
- Similar problems retrieve analogous solutions
- System upgrades based on pattern analysis

**Workflow**:
```
New Request → Vector Search → Find Similar Plans → Adapt & Execute → Store New Pattern
```

### 4. **High Traceability**
Every action leaves a complete audit trail:
- **Who**: actor (user ID or AI agent)
- **What**: operation type and parameters
- **When**: timestamp (microsecond precision)
- **Why**: plan hash linking to original intent
- **Result**: before/after snapshots of state

**Uses**:
- Compliance auditing
- Incident investigation
- Performance analysis
- Self-improvement feedback

### 5. **Extensible Tool System**
New capabilities added by defining LangChain tools:
```python
@tool
def deploy_cdn(bucket_name: str, cache_ttl: int) -> dict:
    """Enable CDN for a static site with specified cache TTL."""
    # Implementation
    return {"cdn_url": "...", "status": "active"}
```

AI automatically discovers and uses new tools when appropriate. No code changes needed in the agent graph.

---

## Versioning Scheme

### System Versioning
- **Format**: `v{major}.{minor}.{patch}`
- **Semantic Meaning**:
  - `major`: Breaking changes to APIs or data models
  - `minor`: New features, backward-compatible
  - `patch`: Bug fixes, no new functionality

**Example**: `v0.1.0` → initial MVP with static/dynamic deployment

### Schema Versioning
- **Format**: `schema_{timestamp}_{description}`
- **Purpose**: Track state-db and vector-db schema evolution
- **Migration**: Automatic or manual based on complexity

**Example**: `schema_20250101_add_cdn_metadata`

**Benefits**:
- Safe upgrades without data loss
- Rollback capability
- Multi-version compatibility during transitions

---

## Next Steps

With this overview in place, the next documents will detail:

1. **World State Data Model** (`02_state_and_memory.md`): Complete database schemas and semantic memory structure
2. **Services Layout** (`03_services_layout.md`): Detailed service responsibilities and networking
3. **Infra Runner API** (`04_infra_runner_api.md`): Complete API contract with request/response schemas
4. **LangChain Tools** (`05_langchain_tools.md`): Tool definitions for AI agent capabilities
5. **Agent Graph** (`06_agent_graph.md`): LangGraph architecture for multi-agent planning
6. **Implementation Files**: Actual Python code for infra-runner and ai-control-plane services
7. **Examples & Release Notes**: End-to-end flows and deployment instructions

---

*This document is part of the AI-Native Control Plane specification defined in `.github/copilot/tasks/ai-native-control-plane.md`*
