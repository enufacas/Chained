# AI Control Plane Service

**AI-Native Control Plane - Natural Language Infrastructure Interface**

This service provides a natural language interface to autonomous AI-driven infrastructure operations. It orchestrates multi-agent workflows using LangChain/LangGraph to translate user commands into infrastructure actions.

## ⚠️ Implementation Status

**Phase 6 (Production Integration): IN PROGRESS**

- ✅ **Intent Classification**: LLM-based classification implemented (OpenAI/Gemini)
- ✅ **Fallback Mode**: Keyword-based classification for development without API keys
- 🚧 **Plan Generation**: Stub implementation (LLM integration in progress)
- 🚧 **Tool Implementations**: Stubs with TODO markers
- 🚧 **Vector Database**: Not yet integrated
- 🚧 **State Database**: Schema ready, integration in progress

## 🎯 Purpose

The AI Control Plane service:
- Accepts natural language commands from users
- Classifies intent and generates execution plans
- Orchestrates 7 specialized AI agents through a state machine
- Retrieves learned patterns from semantic memory
- Executes infrastructure operations via the Infra Runner service
- Maintains world state in PostgreSQL and vector embeddings
- Proposes system self-improvements

## 🏗️ Architecture

### Multi-Agent Workflow

The service implements a LangGraph state machine with 7 specialized agents:

```
User Request
     ↓
Planner Agent → Policy Agent → Memory Agent → Builder Agent → 
Infra Agent → State Manager Agent → Output Agent
     ↓
User Response
```

### Agent Responsibilities

1. **Planner Agent**: Classify intent, generate execution plans, score alternatives
2. **Policy Agent**: Validate against quotas, budgets, security policies
3. **Memory Agent**: Retrieve relevant patterns from vector database
4. **Builder Agent**: Generate application code and configurations
5. **Infra Agent**: Execute infrastructure operations (via infra-runner)
6. **State Manager**: Update world state, log operations, store patterns
7. **Output Agent**: Format results for user consumption

### State Machine

States:
- `PLANNING` - Intent classification and plan generation
- `POLICY_CHECK` - Policy validation
- `MEMORY_RETRIEVAL` - Pattern retrieval
- `BUILDING` - Code and config generation
- `DEPLOYING` - Infrastructure execution
- `STATE_UPDATE` - State persistence
- `COMPLETED` - Success
- `FAILED` - Failure with error context

## 📡 API Endpoints

### POST /execute
Execute a natural language infrastructure command.

**Request Example:**
```json
{
  "user_request": "Create a blog platform with authentication and deploy it",
  "user_id": "user-123",
  "mode": "normal",
  "dry_run": false
}
```

**Response Example:**
```json
{
  "success": true,
  "correlation_id": "corr_abc123",
  "intent": "create_app",
  "message": "✅ Successfully deployed your application!\n\n🌐 Your site is live at: https://...",
  "urls": [
    {
      "label": "Website",
      "url": "https://storage.googleapis.com/app-blog-prod/index.html"
    }
  ],
  "summary": {
    "intent": "create_app",
    "confidence": 0.85,
    "policy_approved": true,
    "operation_id": "op:abc123"
  },
  "next_steps": [
    "Monitor the deployment health",
    "Configure custom domain if needed"
  ],
  "execution_time_seconds": 45,
  "state_trace": [
    "planning",
    "policy_check",
    "memory_retrieval",
    "building",
    "deploying",
    "state_update",
    "completed"
  ]
}
```

### GET /status/{operation_id}
Get the status of a previously executed operation.

### GET /health
Service health check for Cloud Run.

## 🧠 LangChain Tools

The service implements 10 LangChain tools (all stubbed in skeleton):

1. **create_app_spec** - Generate app specification from natural language
2. **build_static_app** - Generate static website code
3. **build_dynamic_app** - Generate backend service code
4. **deploy_static_site** - Deploy to GCS (calls infra-runner)
5. **deploy_dynamic_service** - Deploy to Cloud Run (calls infra-runner)
6. **update_app_state** - Update state-db records
7. **fetch_memory_context** - Query vector-db for patterns
8. **write_memory_context** - Store successful patterns
9. **propose_system_upgrade** - Generate self-improvement proposals
10. **evaluate_upgrade_proposal** - Assess upgrade safety

## 🚀 Running Locally

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)
- OpenAI API key (for production LLM integration)

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (for future LLM integration)
export OPENAI_API_KEY="sk-..."

# Run the service
python main.py
```

The service will start on `http://localhost:8081`.

### Test Endpoint
```bash
# Health check
curl http://localhost:8081/health

# Execute command (skeleton mode)
curl -X POST http://localhost:8081/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "Create a simple blog website",
    "user_id": "user-test",
    "mode": "normal",
    "dry_run": false
  }'
```

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t ai-control-plane:latest .
```

### Run Container
```bash
docker run -p 8081:8081 \
  -e OPENAI_API_KEY=sk-... \
  ai-control-plane:latest
```

### Deploy to Cloud Run
```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-control-plane:latest

# Deploy to Cloud Run
gcloud run deploy ai-control-plane \
  --image gcr.io/PROJECT_ID/ai-control-plane:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 10 \
  --memory 1Gi \
  --cpu 2 \
  --set-env-vars OPENAI_API_KEY=sk-...
```

## 🔧 Configuration

### Environment Variables

**LLM Configuration (Phase 6):**
- `LLM_PROVIDER`: LLM provider to use (`openai` or `gemini`, default: `gemini`)
- `OPENAI_API_KEY`: OpenAI API key (required if provider=openai)
- `OPENAI_MODEL`: OpenAI model name (default: `gpt-4-turbo-preview`)
- `GEMINI_API_KEY`: Google Gemini API key (required if provider=gemini)
- `GEMINI_MODEL`: Gemini model name (default: `gemini-1.5-flash`)
- `LLM_MAX_RETRIES`: Max retries for LLM calls (default: 3)
- `LLM_TIMEOUT`: LLM request timeout in seconds (default: 30)

**Database Configuration:**
- `STATE_DB_URL`: PostgreSQL connection string (default: `postgresql://postgres:@localhost/ai_native_control_plane`)
- `VECTOR_DB_URL`: Vector database connection string (TODO)
- `INFRA_RUNNER_URL`: Infra Runner service URL (TODO)

**Service Configuration:**
- `PORT`: Server port (default: 8081)
- `LOG_LEVEL`: Logging level (default: INFO)

### LLM Provider Setup

#### Option 1: OpenAI
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4-turbo-preview  # Optional
```

#### Option 2: Google Gemini (Default)
```bash
export LLM_PROVIDER=gemini
export GEMINI_API_KEY=...  # Get from https://aistudio.google.com/app/apikey
export GEMINI_MODEL=gemini-1.5-flash  # Optional
```

#### Fallback Mode (No API Key)
If no API key is configured, the service falls back to keyword-based intent classification. This is suitable for development and testing but not recommended for production.

### Getting API Keys

**OpenAI:**
1. Create account at https://platform.openai.com/
2. Go to API Keys section
3. Create new secret key
4. Copy and set as `OPENAI_API_KEY`

**Google Gemini:**
1. Go to https://aistudio.google.com/app/apikey
2. Click "Get API Key"
3. Copy and set as `GEMINI_API_KEY`
4. **Note**: This is different from GCP service account keys

## 📋 TODO: Production Implementation

### Critical Path
- [x] Integrate LangChain with OpenAI/Gemini for intent classification ✅ **COMPLETED (Phase 6)**
- [ ] Implement plan generation with LLM
- [ ] Implement LangGraph StateGraph with conditional routing
- [ ] Build actual vector database integration (ChromaDB/Pinecone/pgvector)
- [ ] Connect to PostgreSQL state-db (schema ready, integration pending)
- [ ] Implement all 10 LangChain tools with proper schemas
- [ ] Add HTTP client for calling infra-runner service
- [ ] Implement retry logic with exponential backoff
- [ ] Add OpenTelemetry tracing spans

### Agent Implementation
- [ ] Planner: Multi-plan generation and scoring
- [ ] Policy: GCP quota checks and cost estimation
- [ ] Memory: Semantic search with embeddings
- [ ] Builder: Code generation with LLM
- [ ] Infra: Robust API calls to infra-runner
- [ ] State Manager: Database writes and pattern storage
- [ ] Output: Natural language response formatting

### Advanced Features
- [ ] Streaming responses (SSE)
- [ ] Circuit breaker pattern
- [ ] Repair mode with error embeddings
- [ ] Migration mode with blue-green deployments
- [ ] Self-upgrade proposal workflow
- [ ] Human-in-the-loop for high-risk operations
- [ ] Multi-user support with authentication
- [ ] Audit logging and compliance

## 🎓 Design Patterns

### Deterministic IDs
All entities use SHA256 hash-based IDs:
```python
app_id = generate_deterministic_id("app", user_request, timestamp)
# Result: "app:a3f2d9e1b4c8f7a2"
```

### State Machine Pattern
LangGraph manages explicit state transitions with routing logic:
```python
graph.add_conditional_edges(
    "policy",
    route_after_policy,
    {"approved": "memory", "rejected": "planner", "needs_review": END}
)
```

### Tool Pattern
All tools follow the same structure:
- Pydantic input/output schemas
- Deterministic execution
- Structured logging
- Error classification
- OpenTelemetry spans

### Memory Pattern
Successful operations are stored as vector embeddings for reuse:
- Pattern type classification
- Similarity search
- Success rate tracking
- Automatic pattern application

## 📊 Performance Targets

| Operation | Target p50 | Target p95 |
|-----------|------------|------------|
| Intent classification | 500ms | 1s |
| Plan generation | 3s | 10s |
| Memory retrieval | 200ms | 1s |
| End-to-end execution | 45s | 120s |

## 📖 Related Documentation

- **LangChain Tools**: `docs/ai-native/05_langchain_tools.md`
- **Agent Graph**: `docs/ai-native/06_agent_graph.md`
- **Services Layout**: `docs/ai-native/03_services_layout.md`
- **Master Spec**: `.github/copilot/tasks/ai-native-control-plane.md`

## 🤝 Contributing

This is a skeleton implementation. When implementing production features:

1. Replace TODO markers with actual implementations
2. Add comprehensive error handling and retries
3. Include unit tests for all agents and tools
4. Add integration tests with mocked LLM responses
5. Update this README with actual configuration
6. Document LLM prompts and tool schemas

## 🔒 Security Considerations

### API Key Management
- Store OpenAI API key in Secret Manager
- Rotate keys regularly
- Use service account authentication

### Input Validation
- Sanitize all user input
- Validate against injection attacks
- Rate limit per user
- Audit all operations

### Policy Enforcement
- Enforce resource quotas
- Validate budget constraints
- Block high-risk operations
- Require human approval for destructive changes

---

**Status**: Skeleton implementation (Step 8 of AI-Native Control Plane)  
**Version**: 0.1.0  
**Last Updated**: 2025-12-06
