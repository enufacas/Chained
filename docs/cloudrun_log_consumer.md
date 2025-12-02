# Cloud Run Log Consumer

## Overview

The **log-consumer agent** is a scaffold for processing Google Cloud Run logs and converting ERROR-level entries into `error_event` tasks sent to the `error_observer` agent.

This agent demonstrates how to integrate Cloud Logging with the A2A error observation system.

## Architecture

```
Cloud Run Services
    ↓ (logs)
Cloud Logging
    ↓ (log router)
Pub/Sub Topic
    ↓ (push subscription)
log-consumer Agent
    ↓ (A2A error_event)
error_observer Agent
    ↓ (repository_dispatch)
GitHub Issues
```

## Log Consumer Agent

**Location:** `/infrastructure/docker/adk-agents/log-consumer/`

**Purpose:** 
- Receive Cloud Run logs via Pub/Sub push
- Filter ERROR-level severity logs
- Convert to ErrorEvent schema
- Send as A2A task to error_observer

**Endpoints:**
- `POST /pubsub/push` - Pub/Sub push subscription endpoint
- `GET /health` - Health check
- `GET /` - Agent info and configuration

## Cloud Logging Entry Format

Cloud Logging sends entries in this format:

```json
{
  "textPayload": "Database connection failed",
  "jsonPayload": {
    "message": "Connection timeout",
    "error_code": "TIMEOUT"
  },
  "severity": "ERROR",
  "timestamp": "2025-12-02T10:40:00.123456Z",
  "resource": {
    "type": "cloud_run_revision",
    "labels": {
      "service_name": "chained-blog-writer",
      "revision_name": "chained-blog-writer-00042-xyz",
      "location": "us-central1",
      "project_id": "chained-ai"
    }
  },
  "labels": {
    "instanceId": "00bf4bf02d...",
    "execution_id": "8ab3cd..."
  },
  "insertId": "abc123..."
}
```

## Log Processing Logic

### 1. Service Name Extraction

```python
def extract_service_name(log_entry: CloudRunLogEntry) -> str:
    if log_entry.resource:
        labels = log_entry.resource.get("labels", {})
        service_name = labels.get("service_name")
        if service_name:
            return service_name
    return "unknown-service"
```

Tries:
1. `resource.labels.service_name`
2. `labels.service_name`
3. Falls back to `"unknown-service"`

### 2. Severity Filtering

```python
def should_process_log(log_entry: CloudRunLogEntry) -> bool:
    # Only process ERROR severity logs
    if log_entry.severity not in ("ERROR", "CRITICAL", "ALERT", "EMERGENCY"):
        return False
    return True
```

Processes only:
- ERROR
- CRITICAL
- ALERT
- EMERGENCY

Skips:
- INFO
- WARNING
- DEBUG
- DEFAULT

### 3. Error Event Conversion

```python
error_event = ErrorEvent.from_cloudrun_log(
    service_name="chained-blog-writer",
    log_entry=log_entry.model_dump(),
    region="us-central1",
    environment="production"
)
```

Extracts:
- **error_message**: From `textPayload` or `jsonPayload.message`
- **stack_trace**: From `jsonPayload.stack_trace` if present
- **logs**: Array with raw log payload
- **service**: Extracted service name
- **region**: From `resource.labels.location`
- **timestamp**: From log entry timestamp

## Pub/Sub Integration

### Log Router Setup (Future)

To wire Cloud Logging to the log-consumer agent:

1. **Create Pub/Sub Topic**:
```bash
gcloud pubsub topics create cloudrun-error-logs
```

2. **Create Log Sink**:
```bash
gcloud logging sinks create cloudrun-errors \
  pubsub.googleapis.com/projects/chained-ai/topics/cloudrun-error-logs \
  --log-filter='resource.type="cloud_run_revision" severity>="ERROR"'
```

3. **Grant Permissions**:
```bash
# Get the service account from the sink
SERVICE_ACCOUNT=$(gcloud logging sinks describe cloudrun-errors --format='value(writerIdentity)')

# Grant Publisher role
gcloud pubsub topics add-iam-policy-binding cloudrun-error-logs \
  --member=$SERVICE_ACCOUNT \
  --role=roles/pubsub.publisher
```

4. **Create Push Subscription**:
```bash
gcloud pubsub subscriptions create cloudrun-errors-push \
  --topic=cloudrun-error-logs \
  --push-endpoint=https://chained-log-consumer-sguacxy5gq-uc.a.run.app/pubsub/push \
  --push-auth-service-account=log-consumer@chained-ai.iam.gserviceaccount.com
```

## Example: Processing Flow

### Input: Cloud Run Log Entry

```json
{
  "textPayload": "Failed to connect to database: connection timeout",
  "severity": "ERROR",
  "timestamp": "2025-12-02T15:30:45.123Z",
  "resource": {
    "type": "cloud_run_revision",
    "labels": {
      "service_name": "chained-academic-research",
      "location": "us-central1"
    }
  }
}
```

### Step 1: Pub/Sub Push

Pub/Sub sends to `/pubsub/push`:

```json
{
  "message": {
    "data": "eyJ0ZXh0UGF5bG9hZCI6IkZhaWxlZC...",  // base64 encoded log entry
    "messageId": "123456789",
    "publishTime": "2025-12-02T15:30:46.000Z"
  },
  "subscription": "projects/chained-ai/subscriptions/cloudrun-errors-push"
}
```

### Step 2: Decode and Parse

Agent decodes base64 and parses JSON:

```python
import base64
import json

data_decoded = base64.b64decode(message.data).decode('utf-8')
log_entry_dict = json.loads(data_decoded)
log_entry = CloudRunLogEntry(**log_entry_dict)
```

### Step 3: Filter

Check severity:
- ✅ "ERROR" → Process
- ❌ "INFO" → Skip

### Step 4: Convert to ErrorEvent

```python
error_event = ErrorEvent.from_cloudrun_log(
    service_name="chained-academic-research",
    log_entry=log_entry.model_dump(),
    region="us-central1",
    environment="production"
)
```

Result:

```json
{
  "service": "chained-academic-research",
  "region": "us-central1",
  "environment": "production",
  "error_message": "Failed to connect to database: connection timeout",
  "stack_trace": null,
  "logs": [
    "Failed to connect to database: connection timeout"
  ],
  "error_hash": "d4e5f6a7b8c9d012",
  "first_seen": "2025-12-02T15:30:45.123Z",
  "last_seen": "2025-12-02T15:30:45.123Z",
  "occurrences": 1,
  "source_channel": "cloudrun",
  "metadata": {
    "log_entry": {...}
  }
}
```

### Step 5: Send to Error Observer

```python
from shared.a2a_utils import send_error_to_observer

await send_error_to_observer(
    error_event.model_dump(),
    ERROR_OBSERVER_URL
)
```

Makes A2A task request:

```json
POST https://chained-error-observer-xxx.run.app/a2a/tasks
{
  "message": {
    "role": "user",
    "parts": [{"text": "{...error_event_json...}"}]
  },
  "contextId": "error-1733154645",
  "metadata": {
    "error_event": {...}
  }
}
```

### Step 6: Error Observer Processes

error_observer:
1. Receives A2A task
2. Extracts ErrorEvent
3. Validates and enriches
4. Calls GitHub repository_dispatch
5. Returns task result

## Configuration

### Environment Variables

**log-consumer agent:**
```bash
ERROR_OBSERVER_URL=https://chained-error-observer-sguacxy5gq-uc.a.run.app
PORT=8091
```

**error_observer agent:**
```bash
GITHUB_PAT=ghp_xxxxx
PORT=8090
```

## Testing Locally

### 1. Start error_observer

```bash
cd infrastructure/docker/adk-agents/error-observer
export GITHUB_PAT=ghp_your_token_here
python -m agent
```

### 2. Start log-consumer

```bash
cd infrastructure/docker/adk-agents/log-consumer
export ERROR_OBSERVER_URL=http://localhost:8090
python -m agent
```

### 3. Send Test Log

```bash
# Simulate Pub/Sub push with ERROR log
curl -X POST http://localhost:8091/pubsub/push \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "data": "'$(echo '{
        "textPayload": "Test error from Cloud Run",
        "severity": "ERROR",
        "timestamp": "2025-12-02T16:00:00Z",
        "resource": {
          "type": "cloud_run_revision",
          "labels": {
            "service_name": "test-service",
            "location": "us-central1"
          }
        }
      }' | base64)'",
      "messageId": "test-123",
      "publishTime": "2025-12-02T16:00:00Z"
    }
  }'
```

Expected flow:
1. log-consumer receives Pub/Sub message
2. Decodes and parses log entry
3. Converts to ErrorEvent
4. Sends to error_observer
5. error_observer forwards to GitHub
6. GitHub creates repository_dispatch event

## Deployment

Deploy as Cloud Run service:

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/chained-ai/log-consumer
gcloud run deploy chained-log-consumer \
  --image gcr.io/chained-ai/log-consumer \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars ERROR_OBSERVER_URL=https://chained-error-observer-xxx.run.app
```

Then configure Pub/Sub push subscription to point to the service URL.

## Future Enhancements

1. **Rate Limiting**: Prevent duplicate errors flooding the system
2. **Error Grouping**: Batch similar errors by hash
3. **Filtering Rules**: Configurable ignore patterns
4. **Metrics**: Track error counts by service
5. **Alerting**: Threshold-based alerts
6. **Dead Letter Queue**: Handle failed processing

## Related Documentation

- [Error Observer Schema](./error_observer_schema.md)
- [Error Observer Overview](./error_observer_overview.md)
- [Cloud Logging Documentation](https://cloud.google.com/logging/docs)
- [Pub/Sub Push Subscriptions](https://cloud.google.com/pubsub/docs/push)
