# Error Observer System Overview

## Introduction

The **Error Observer System** is an A2A-native error reporting and triage pipeline for the Chained autonomous AI ecosystem. It treats errors as **first-class A2A tasks/messages**, enabling agents, UI, and infrastructure to participate in a unified error handling workflow.

## Philosophy

Traditional error handling often involves:
- Separate logging systems
- Disconnected monitoring tools
- Manual triage processes
- No integration with autonomous agents

The Error Observer System instead:
- **Treats errors as A2A tasks** - Errors flow through the same agent network
- **Maintains A2A principles** - All components are agents communicating via protocol
- **Enables autonomous triage** - GitHub integration allows Copilot-driven error resolution
- **Provides visibility** - UI visualization shows real-time error processing

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Error Sources                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Agent Runtime   │  │ UI Frontend     │  │ Cloud Run Logs  │ │
│  │ Exceptions      │  │ Errors          │  │ ERROR Severity  │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                     │           │
└───────────┼────────────────────┼─────────────────────┼───────────┘
            │                    │                     │
            │ error_event        │ error_event         │ error_event
            │ (A2A task)         │ (A2A task)          │ (A2A task)
            │                    │                     │
            v                    v                     v
    ┌───────────────────────────────────────────────────────────┐
    │                   error_observer Agent                     │
    │                  (System-Level Observer)                   │
    ├───────────────────────────────────────────────────────────┤
    │                                                             │
    │  State Machine:                                            │
    │  idle → ingesting → dispatching → success/failure → idle  │
    │                                                             │
    │  Functions:                                                │
    │  • Receive error_event tasks                              │
    │  • Validate and enrich errors                             │
    │  • Forward to GitHub via repository_dispatch              │
    │  • Track state for UI visualization                       │
    │                                                             │
    └────────────────────────┬──────────────────────────────────┘
                             │
                             │ repository_dispatch
                             │ (GitHub API)
                             v
                    ┌────────────────────┐
                    │   GitHub Issues    │
                    │ (Copilot Triage)   │
                    └────────────────────┘
                             │
                             │ Autonomous triage
                             v
                    ┌────────────────────┐
                    │   Fix/Resolution   │
                    └────────────────────┘
```

## Components

### 1. Error Event Schema

**Location:** `/infrastructure/docker/adk-agents/shared/error_event.py`

Canonical error structure used across all sources:

```python
class ErrorEvent:
    service: str              # Service name
    region: str               # GCP region
    environment: str          # Environment
    error_message: str        # Error description
    stack_trace: Optional[str]
    logs: List[str]
    error_hash: str           # Deduplication hash
    first_seen: str           # RFC3339 timestamp
    last_seen: str
    occurrences: int
    source_agent: Optional[str]
    source_channel: str       # "runtime", "ui", "cloudrun"
    metadata: Dict[str, Any]
```

**Key Features:**
- Helper methods for different sources (`from_exception`, `from_ui_error`, `from_cloudrun_log`)
- Automatic error hashing for deduplication
- A2A artifact conversion
- GitHub payload conversion

### 2. error_observer Agent

**Location:** `/infrastructure/docker/adk-agents/error-observer/`

System-level A2A agent that:
- Subscribes to `error_event` task type
- Processes incoming error events
- Forwards to GitHub via repository_dispatch
- Maintains state for UI visualization

**State Machine:**
- `idle` - Waiting for errors
- `ingesting` - Received error, validating
- `dispatching` - Calling GitHub API
- `success` - Successfully dispatched
- `failure` - Dispatch failed

**Endpoints:**
- `POST /a2a/tasks` - A2A protocol task handler
- `GET /.well-known/agent.json` - A2A agent card
- `GET /status` - Current agent state (for UI)
- `GET /health` - Health check

**GitHub Integration:**
```python
async def dispatch_to_github(error_event: ErrorEvent):
    # POST to https://api.github.com/repos/enufacas/Chained/dispatches
    payload = {
        "event_type": "cloudrun-error",
        "client_payload": error_event.to_github_payload()
    }
```

### 3. Agent Runtime Error Reporting

**Location:** `/infrastructure/docker/adk-agents/shared/a2a_utils.py`

Helpers for agents to report errors:

```python
# Convenience wrapper
await report_agent_error(
    agent_name="academic-research",
    exception=e,
    task_type="research_task",
    a2a_ui_url="/pipeline/123"
)

# Low-level API
await send_error_to_observer(
    error_event_dict,
    error_observer_url
)
```

### 4. UI Error Reporting

**Backend:** `/infrastructure/docker/ag-ui-frontend/src/app/api/ui-error-report/route.ts`

```typescript
POST /api/ui-error-report
{
  message: "Error message",
  stack: "Stack trace",
  url: "https://...",
  user_agent: "...",
  extra: {...}
}
```

Converts UI errors to ErrorEvent and sends to error_observer.

**Frontend Integration:**
- `ErrorBoundary.tsx` - React error boundary
- `error-logging.ts` - Global error handlers

```typescript
// Automatic error capture
window.addEventListener('error', (event) => {
  fetch('/api/ui-error-report', {
    method: 'POST',
    body: JSON.stringify({...})
  });
});
```

### 5. Log Consumer Agent

**Location:** `/infrastructure/docker/adk-agents/log-consumer/`

Scaffold for Cloud Logging integration:
- Receives Cloud Run logs via Pub/Sub push
- Filters ERROR-level severity
- Converts to ErrorEvent
- Sends to error_observer

**Endpoint:**
```
POST /pubsub/push - Pub/Sub push subscription
```

**Future:** Wire Cloud Logging → Log Router → Pub/Sub → log-consumer

### 6. UI Visualization

**Location:** TBD - To be implemented in ag-ui-frontend

Visual representation of error_observer agent showing:
- Current state (idle, ingesting, dispatching, success, failure)
- Last error processed
- Recent error history
- Dispatch statistics

## Error Flow Examples

### Example 1: Agent Runtime Error

```python
# 1. Agent task fails
try:
    result = fetch_research_papers(topic)
except APIError as e:
    # 2. Report to error observer
    await report_agent_error("academic-research", e)
    raise

# 3. error_observer receives A2A task
# 4. Validates and enriches error
# 5. Dispatches to GitHub
# 6. GitHub creates repository_dispatch event
# 7. Copilot workflow triages the error
```

### Example 2: UI Frontend Error

```typescript
// 1. React component throws
<ErrorBoundary>
  <PipelineView /> // Throws error
</ErrorBoundary>

// 2. ErrorBoundary catches
componentDidCatch(error, errorInfo) {
  // 3. Sends to /api/ui-error-report
  fetch('/api/ui-error-report', {...})
}

// 4. Backend converts to ErrorEvent
// 5. Sends to error_observer via A2A
// 6. error_observer → GitHub
```

### Example 3: Cloud Run Logs

```
1. Cloud Run service logs ERROR
2. Cloud Logging captures entry
3. Log Router → Pub/Sub topic
4. Pub/Sub → log-consumer (push)
5. log-consumer parses and filters
6. Converts to ErrorEvent
7. Sends to error_observer via A2A
8. error_observer → GitHub
```

## Benefits

### 1. Unified Error Handling
- All errors flow through same A2A network
- Consistent schema across sources
- Single point of GitHub integration

### 2. Autonomous Triage
- GitHub repository_dispatch triggers workflows
- Copilot can analyze and fix errors
- Automated issue creation and tracking

### 3. Observable System
- UI shows error_observer state in real-time
- Track error history and patterns
- Monitor system health

### 4. A2A Native
- No separate monitoring infrastructure
- Agents participate as first-class citizens
- Leverages existing A2A protocol

### 5. Deduplication
- Error hashing prevents duplicate reports
- Track occurrences and patterns
- Efficient error aggregation

## Configuration

### Environment Variables

**error_observer:**
```bash
GITHUB_PAT=ghp_xxxxx          # GitHub personal access token
PORT=8090                      # Service port
SERVICE_URL=https://...        # Public URL for agent card
```

**log-consumer:**
```bash
ERROR_OBSERVER_URL=https://chained-error-observer-xxx.run.app
PORT=8091
```

**UI Backend:**
```bash
ERROR_OBSERVER_URL=https://chained-error-observer-xxx.run.app
```

**Agents:**
```bash
ERROR_OBSERVER_URL=https://chained-error-observer-xxx.run.app
```

## Deployment

### 1. Deploy error_observer

```bash
cd infrastructure/docker/adk-agents
gcloud builds submit --tag gcr.io/chained-ai/error-observer error-observer/
gcloud run deploy chained-error-observer \
  --image gcr.io/chained-ai/error-observer \
  --region us-central1 \
  --set-env-vars GITHUB_PAT=ghp_xxx
```

### 2. Configure Agents

Update agent environment variables to include ERROR_OBSERVER_URL.

### 3. Deploy log-consumer (Optional)

```bash
gcloud builds submit --tag gcr.io/chained-ai/log-consumer log-consumer/
gcloud run deploy chained-log-consumer \
  --image gcr.io/chained-ai/log-consumer \
  --region us-central1 \
  --set-env-vars ERROR_OBSERVER_URL=https://...
```

### 4. Configure Cloud Logging (Optional)

Set up log sink → Pub/Sub → log-consumer push subscription.

## GitHub Workflow

Expected workflow to handle repository_dispatch:

```yaml
name: Handle Cloud Run Errors

on:
  repository_dispatch:
    types: [cloudrun-error]

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - name: Extract error details
        run: |
          echo "Service: ${{ github.event.client_payload.service }}"
          echo "Error: ${{ github.event.client_payload.error_message }}"
      
      - name: Create issue or comment
        uses: actions/github-script@v7
        with:
          script: |
            // Create issue or find existing by error_hash
            // Add comment with error details
            // Trigger Copilot for analysis
```

## Testing

### Unit Tests

Test ErrorEvent creation:
```python
def test_error_event_from_exception():
    try:
        raise ValueError("Test error")
    except Exception as e:
        event = ErrorEvent.from_exception("test-service", e)
        assert event.service == "test-service"
        assert event.error_message == "Test error"
        assert event.source_channel == "runtime"
```

### Integration Tests

Test full flow:
1. Send error to error_observer
2. Verify GitHub API call (mock)
3. Check state transitions

### End-to-End Tests

1. Deploy to staging
2. Trigger errors from agents/UI
3. Verify GitHub repository_dispatch
4. Check error_observer status endpoint

## Monitoring

### Metrics to Track

- Errors processed per hour
- GitHub dispatch success rate
- Error distribution by source (runtime, ui, cloudrun)
- Error distribution by service
- Average processing time

### Alerts

- error_observer health check failures
- High error rate from specific service
- GitHub API failures
- Log consumer processing delays

## Future Enhancements

1. **Error Grouping**: Batch similar errors by hash before dispatching
2. **Rate Limiting**: Prevent error floods
3. **Smart Routing**: Different handling based on error type/severity
4. **Auto-Resolution**: Track fixes and close resolved errors
5. **Machine Learning**: Predict error patterns
6. **Cross-Service Correlation**: Link related errors across services

## Related Documentation

- [Error Observer Schema](./error_observer_schema.md) - Detailed error event schema
- [Cloud Run Log Consumer](./cloudrun_log_consumer.md) - Log processing details
- [A2A Protocol](./a2a/) - A2A protocol documentation

## Support

For issues or questions:
1. Check error_observer logs in Cloud Run console
2. Verify GitHub PAT permissions
3. Test with curl to error_observer /health endpoint
4. Review error_observer /status for current state
