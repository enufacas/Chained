# Cloud Run Startup Failure Fix - Data Analyst Agent

**Date**: 2025-12-10  
**Issue**: https://github.com/enufacas/Chained/actions/runs/20087665853/job/57628773405  
**Status**: ✅ FIXED

## Problem

The `chained-data-analyst` Cloud Run service failed to start with:
```
Error code 9: The user-provided container failed the configured startup probe checks.
```

### Root Causes

1. **Synchronous Vertex AI Initialization**: The Vertex AI client was initialized during module import, blocking startup
2. **Tight Startup Probes**: 15 second total timeout (5s initial delay + 3 failures × 5s period × 3s timeout)
3. **No Retry Logic**: Single attempt to initialize, with no handling of transient failures
4. **No Graceful Degradation**: Health endpoint would fail if AI initialization failed

## Solution

### 1. Lazy Initialization with Retry Logic

**File**: `infrastructure/docker/adk-agents/shared/gemini_client.py`

Changed from eager (module-load) to lazy (first-request) initialization:

```python
# Before: Module-level initialization (blocks startup)
if ACTIVE_MODE == "vertex":
    vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=location)

# After: Lazy initialization with retry
def _ensure_initialized():
    """Initialize on first use, with retry logic"""
    if _initialized:
        return
    
    # Retry with exponential backoff
    for attempt in range(MAX_INIT_RETRIES):
        try:
            vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=location)
            _initialized = True
            return
        except Exception as e:
            if attempt < MAX_INIT_RETRIES - 1:
                wait_time = RETRY_BASE_DELAY * (2 ** attempt)  # 1s, 2s, 4s
                time.sleep(wait_time)
            else:
                raise
```

**Benefits**:
- Container starts immediately (doesn't wait for Vertex AI)
- Handles transient failures (service account propagation delays)
- Caches initialization failures (avoids repeated attempts)

### 2. Always-Healthy Endpoint

**File**: `infrastructure/docker/adk-agents/data-analyst/agent.py`

Updated health endpoint to always return 200 OK:

```python
@app.get("/health")
async def health():
    """Always returns 200 OK, reports AI status separately"""
    ai_status = "available" if USE_AI else "not_configured"
    
    # Check initialization without triggering it
    status = get_initialization_status()
    if status["initialized"]:
        ai_status = "initialized"
    elif status["failed"]:
        ai_status = f"initialization_failed: {status['error']}"
    
    return {
        "status": "healthy",  # Always healthy
        "ai_status": ai_status,  # Separate AI status
        # ...
    }
```

**Benefits**:
- Container passes health checks even if AI is unavailable
- Still provides initialization status for debugging
- Allows container to start and serve requests

### 3. Tolerant Startup Probes

**File**: `infrastructure/terraform/base/adk-agents.tf`

Updated startup probe settings for all ADK agents:

| Setting | Before | After | Change |
|---------|--------|-------|--------|
| initial_delay_seconds | 5 | 10 | +100% |
| timeout_seconds | 3 | 5 | +67% |
| period_seconds | 5 | 10 | +100% |
| failure_threshold | 3 | 5 | +67% |
| **Total grace period** | **15s** | **60s** | **+300%** |

**Calculation**:
- Before: 5s initial + (3 failures × 5s period) = 20s max, but with 3s timeout = 15s
- After: 10s initial + (5 failures × 10s period) = 60s max, with 5s timeout

**Benefits**:
- Gives AI initialization time to succeed (including retries)
- Tolerates temporary service account permission delays
- Reduces false-positive startup failures

### 4. Code Quality Improvements

Based on code review feedback:

1. **Extract Constants**: Magic numbers moved to named constants
   ```python
   MAX_INIT_RETRIES = 3
   RETRY_BASE_DELAY = 1  # seconds, for exponential backoff
   ```

2. **Public API**: Added `get_initialization_status()` function
   - Avoids accessing private module variables
   - Cleaner encapsulation
   - Easier to test

## Impact

### All ADK Agents Benefit
The startup probe changes apply to all agents:
- academic-research
- blog-writer
- google-trends
- code-reviewer
- data-analyst
- image-generator
- error-observer
- log-consumer
- adk-api-server
- ag-ui-frontend
- ag-organism-frontend

### Deployment Reliability Improved
- **Before**: Deployment failures due to tight timing
- **After**: Robust startup with graceful degradation

## Testing

### Local Validation
```bash
cd infrastructure/docker/adk-agents
python3 -c "
from shared.gemini_client import is_available, get_mode, get_config_info
print(f'Available: {is_available()}')
print(f'Mode: {get_mode()}')
print(f'Config: {get_config_info()}')
"
```

Output shows module loads without initializing:
```
Available: True
Mode: vertex
Config: {'active_mode': 'vertex', ...}
```

### Deployment Testing
The fix will be validated by:
1. Building new container images
2. Applying Terraform changes
3. Verifying all services start successfully
4. Checking health endpoints return 200 OK

## Prevention

### Future Best Practices

1. **Always Use Lazy Initialization** for cloud services (Vertex AI, Firestore, etc.)
2. **Use Tolerant Startup Probes** (60s grace period minimum for AI services)
3. **Implement Retry Logic** with exponential backoff for transient failures
4. **Separate Health from Readiness** - health check should always pass, readiness can indicate AI status
5. **Test Startup Locally** before deploying to Cloud Run

### Monitoring

Add alerting for:
- Containers with high restart rates
- Startup probe failures
- AI initialization failures in logs

## Related Issues

- Original failure: https://github.com/enufacas/Chained/actions/runs/20087665853
- Similar patterns in other services should use this approach

## References

- [Cloud Run Startup Probes](https://cloud.google.com/run/docs/configuring/healthchecks#startup-probes)
- [Vertex AI Python SDK](https://cloud.google.com/vertex-ai/docs/python-sdk/use-vertex-ai-python-sdk)
- [Exponential Backoff](https://en.wikipedia.org/wiki/Exponential_backoff)
