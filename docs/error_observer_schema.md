# Error Observer Schema

## Overview

The `error_event` is a canonical task/message type used across the A2A network for error reporting and observation. This document describes the schema, usage patterns, and examples from different sources.

## ErrorEvent Schema

All error events conform to the following structure:

```typescript
interface ErrorEvent {
  // Service identification
  service: string;              // Service name (e.g., "academic-research", "a2a-ui")
  region: string;               // GCP region (default: "us-central1")
  environment: string;          // Environment (e.g., "production", "staging", "development")
  
  // Error details
  error_message: string;        // The error message or description
  stack_trace?: string;         // Stack trace if available
  logs: string[];               // Additional log entries
  
  // URLs for context
  run_console_url?: string;     // GCP Cloud Run console URL
  a2a_ui_url?: string;          // A2A UI view URL
  
  // Deduplication and tracking
  error_hash: string;           // Stable hash for deduplication
  first_seen: string;           // RFC3339 timestamp when first observed
  last_seen: string;            // RFC3339 timestamp when last observed
  occurrences: number;          // Number of times this error occurred
  
  // Source information
  source_agent?: string;        // Agent where error originated
  source_channel: string;       // Channel: "runtime", "ui", "cloudrun"
  
  // Additional context
  metadata: Record<string, any>; // Extra metadata
}
```

## Error Hash Computation

Error hashing is used for deduplication and tracking:

```python
def compute_error_hash(service: str, error_message: str, task_type: str = "error") -> str:
    hash_input = f"{service}|{error_message}|{task_type}"
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
```

This ensures:
- Same error from same service gets same hash
- Different services can have same error message with different hashes
- Errors can be grouped and tracked over time

## Source: Agent Runtime Errors

When an agent task throws an unhandled error, it creates an error_event:

```python
from shared.error_event import ErrorEvent
from shared.a2a_utils import report_agent_error

# In agent task handler
try:
    # Agent logic here
    result = process_task(task)
except Exception as e:
    # Report error to observer
    await report_agent_error(
        agent_name="academic-research",
        exception=e,
        task_type="research_task",
        a2a_ui_url="https://chained-ag-ui-frontend.run.app/pipeline/abc123",
        metadata={"task_id": "task-123", "context_id": "ctx-456"}
    )
    raise
```

### Example: Agent Runtime Error Event

```json
{
  "service": "academic-research",
  "region": "us-central1",
  "environment": "production",
  "error_message": "Failed to fetch research papers from API",
  "stack_trace": "Traceback (most recent call last):\n  File ...",
  "logs": [],
  "run_console_url": null,
  "a2a_ui_url": "https://chained-ag-ui-frontend.run.app/pipeline/abc123",
  "error_hash": "a3f8b12c4d5e6f90",
  "first_seen": "2025-12-02T10:30:00Z",
  "last_seen": "2025-12-02T10:30:00Z",
  "occurrences": 1,
  "source_agent": "academic-research",
  "source_channel": "runtime",
  "metadata": {
    "task_id": "task-123",
    "context_id": "ctx-456"
  }
}
```

## Source: UI Frontend Errors

Frontend errors captured by ErrorBoundary or global handlers:

```typescript
// Frontend captures error
window.addEventListener('error', (event) => {
  fetch('/api/ui-error-report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: event.error.message,
      stack: event.error.stack,
      url: window.location.href,
      user_agent: navigator.userAgent,
      extra: { filename: event.filename, lineno: event.lineno }
    })
  });
});
```

Backend converts to error_event:

```python
error_event = ErrorEvent.from_ui_error(
    message=body.message,
    stack=body.stack,
    url=body.url,
    user_agent=body.user_agent,
    extra=body.extra
)
```

### Example: UI Error Event

```json
{
  "service": "a2a-ui",
  "region": "us-central1",
  "environment": "production",
  "error_message": "Cannot read property 'artifacts' of undefined",
  "stack_trace": "TypeError: Cannot read property 'artifacts' of undefined\n    at PipelineView ...",
  "logs": [
    "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...",
    "Extra: {\"filename\": \"/static/js/main.123.js\", \"lineno\": 45}"
  ],
  "run_console_url": null,
  "a2a_ui_url": "https://chained-ag-ui-frontend.run.app/",
  "error_hash": "b2c9d1e3f4a5b678",
  "first_seen": "2025-12-02T10:35:00Z",
  "last_seen": "2025-12-02T10:35:00Z",
  "occurrences": 1,
  "source_agent": "a2a-ui-backend",
  "source_channel": "ui",
  "metadata": {
    "filename": "/static/js/main.123.js",
    "lineno": 45
  }
}
```

## Source: Cloud Run Logs

Log consumer agent processes Cloud Logging entries:

```python
# Cloud Run log entry
log_entry = {
    "severity": "ERROR",
    "textPayload": "Database connection timeout after 30s",
    "timestamp": "2025-12-02T10:40:00Z",
    "resource": {
        "type": "cloud_run_revision",
        "labels": {
            "service_name": "chained-blog-writer",
            "location": "us-central1"
        }
    }
}

# Convert to error event
error_event = ErrorEvent.from_cloudrun_log(
    service_name="chained-blog-writer",
    log_entry=log_entry,
    region="us-central1",
    environment="production"
)
```

### Example: Cloud Run Log Error Event

```json
{
  "service": "chained-blog-writer",
  "region": "us-central1",
  "environment": "production",
  "error_message": "Database connection timeout after 30s",
  "stack_trace": null,
  "logs": [
    "Database connection timeout after 30s",
    "JSON: {\"severity\": \"ERROR\", \"timestamp\": \"2025-12-02T10:40:00Z\"}"
  ],
  "run_console_url": null,
  "a2a_ui_url": null,
  "error_hash": "c3d4e5f6a7b8c901",
  "first_seen": "2025-12-02T10:40:00Z",
  "last_seen": "2025-12-02T10:40:00Z",
  "occurrences": 1,
  "source_agent": null,
  "source_channel": "cloudrun",
  "metadata": {
    "log_entry": {
      "severity": "ERROR",
      "textPayload": "Database connection timeout after 30s",
      ...
    }
  }
}
```

## A2A Task Format

When sent to error_observer agent, error events are wrapped in A2A protocol:

```json
{
  "message": {
    "role": "user",
    "parts": [
      {
        "text": "{...error_event_json...}"
      }
    ]
  },
  "contextId": "error-1733141400.123",
  "metadata": {
    "error_event": {
      ...error_event_fields...
    }
  }
}
```

## GitHub Dispatch Payload

error_observer forwards errors to GitHub as repository_dispatch:

```json
{
  "event_type": "cloudrun-error",
  "client_payload": {
    ...error_event_fields...
  }
}
```

## Usage Patterns

### From Agents

```python
from shared.a2a_utils import report_agent_error

try:
    dangerous_operation()
except Exception as e:
    await report_agent_error("my-agent", e, a2a_ui_url="/pipeline/123")
    raise
```

### From UI Backend

```typescript
import { ErrorEvent } from '@/types/error-event';

const errorEvent = createErrorEventFromUIError(reportedError);
await sendErrorToObserver(errorEvent);
```

### From Log Consumer

```python
from shared.error_event import ErrorEvent

error_event = ErrorEvent.from_cloudrun_log(
    service_name="my-service",
    log_entry=log_entry_dict
)
await send_error_to_observer(error_event.model_dump())
```

## Best Practices

1. **Always include context**: Set `a2a_ui_url` when available to help debugging
2. **Enrich metadata**: Add task IDs, context IDs, and relevant debug info
3. **Use proper channels**: Set `source_channel` correctly (runtime, ui, cloudrun)
4. **Error deduplication**: Use consistent service names to enable proper hashing
5. **Timestamps**: Always use RFC3339/ISO 8601 format with 'Z' suffix

## Error Observer Processing

The error_observer agent:
1. Receives error_event task
2. Validates required fields
3. Enriches with additional context
4. Forwards to GitHub via repository_dispatch
5. Updates internal state for UI visualization
6. Returns processing result

State transitions:
- `idle` → `ingesting` (error received)
- `ingesting` → `dispatching` (calling GitHub)
- `dispatching` → `success` (GitHub accepted)
- `dispatching` → `failure` (GitHub rejected)
- `success/failure` → `idle` (ready for next error)
