# Intentional Bug Implementation Summary

## Overview

Successfully implemented an intentional, real runtime bug in the code-reviewer A2A agent to test the error_observer system end-to-end.

## Implementation Status: ✅ COMPLETE

### What Was Implemented

1. **Intentional Bug in Code-Reviewer Agent**
   - File: `infrastructure/docker/adk-agents/code-reviewer/agent.py`
   - Location: Line 141 in `review_code()` function
   - Type: `ZeroDivisionError` (division by zero)
   - Trigger: Keyword "test_error_observer" in code to be reviewed (case-insensitive)

2. **Documentation**
   - Created `docs/ERROR_OBSERVER_TESTING.md` with:
     - Complete bug description
     - Three methods to trigger the bug (UI, API, Workflow)
     - Expected behavior and verification checklist
     - Debugging guide
     - Removal instructions
   
3. **Test Verification**
   - Created `tests/test_code_reviewer_intentional_bug.py`
   - Verified bug logic works correctly
   - Tested both trigger and non-trigger scenarios

4. **Safety Measures**
   - Clear comments marking code as intentional bug
   - TODO comment for removal
   - Only triggers with specific keyword
   - Normal operations unaffected

## Architecture

### Error Flow
```
User/Workflow Request
    ↓
code-reviewer agent (A2A)
    ↓
Detects "test_error_observer" keyword
    ↓
Raises ZeroDivisionError
    ↓
Exception caught in send_message() handler
    ↓
report_agent_error() called
    ↓
ErrorEvent created with:
    - service: "code-reviewer"
    - error_message: "division by zero"
    - stack_trace: full Python traceback
    - error_hash: for deduplication
    - source_channel: "runtime"
    ↓
Sent to error_observer via A2A protocol
    ↓
error_observer receives error_event task
    ↓
Validates and enriches error
    ↓
Dispatches to GitHub API (repository_dispatch)
    ↓
GitHub creates issue with error details
    ↓
Error visible in A2A UI error observer status
```

### Key Components

1. **Bug Location**
   ```python
   # File: infrastructure/docker/adk-agents/code-reviewer/agent.py
   async def review_code(code: str, language: Optional[str] = None) -> Dict[str, Any]:
       # INTENTIONAL BUG FOR ERROR OBSERVER TESTING
       if "test_error_observer" in code.lower():
           _ = 1 / 0  # This will raise ZeroDivisionError
   ```

2. **Error Reporting** (already exists in agent)
   ```python
   # File: infrastructure/docker/adk-agents/code-reviewer/agent.py (line 347)
   except Exception as e:
       await report_agent_error(
           agent_name="code-reviewer",
           exception=e,
           task_type="agent_task",
       )
   ```

3. **Error Event Structure** (from shared/error_event.py)
   ```python
   {
       "service": "code-reviewer",
       "error_message": "division by zero",
       "stack_trace": "...",
       "error_hash": "...",
       "first_seen": "2025-12-04T...",
       "source_channel": "runtime",
       "metadata": {}
   }
   ```

## Next Steps for Testing

### 1. Deploy Updated Agent to GCP

```bash
cd infrastructure/docker/adk-agents

# Build and deploy code-reviewer with the bug
gcloud builds submit --tag gcr.io/chained-ai/code-reviewer code-reviewer/
gcloud run deploy chained-code-reviewer \
  --image gcr.io/chained-ai/code-reviewer \
  --region us-central1 \
  --set-env-vars ERROR_OBSERVER_URL=https://chained-error-observer-XXX.a.run.app
```

### 2. Verify Configuration

```bash
# Check ERROR_OBSERVER_URL is set
gcloud run services describe chained-code-reviewer \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env[?name='ERROR_OBSERVER_URL'].value)"

# Check error_observer is healthy
curl https://chained-error-observer-XXX.a.run.app/health
```

### 3. Trigger the Bug

**Option A: Via A2A UI** (Recommended)
```
1. Go to: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/
2. In the chat, ask: "Please review this code:

```python
# test_error_observer
def test_function():
    return "hello"
```"
```

**Option B: Via Direct API Call**
```bash
CODE_REVIEWER_URL="https://chained-code-reviewer-XXX.a.run.app"

curl -X POST "$CODE_REVIEWER_URL/a2a/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "parts": [
        {
          "text": "Review this code:\n```python\n# test_error_observer\ndef test():\n    pass\n```"
        }
      ]
    }
  }'
```

### 4. Verify Results

**Check A2A UI:**
- Error should appear in error observer agent status
- Error details should be visible

**Check GitHub:**
- New issue should be created
- Title: Something like "Cloud Run Error: code-reviewer"
- Body: Contains error details, stack trace, hash
- Labels: `cloudrun-error` or similar

**Check Cloud Run Logs:**
```bash
# Code reviewer logs
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=chained-code-reviewer" \
  --limit 50 --format json

# Error observer logs
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=chained-error-observer" \
  --limit 50 --format json
```

## Verification Checklist

After triggering the bug:

- [ ] Code-reviewer returns failed task response
- [ ] Error message mentions "ZeroDivisionError"
- [ ] Error observer receives error event
- [ ] Error observer logs show processing
- [ ] GitHub issue is automatically created
- [ ] Issue contains:
  - [ ] Service name: code-reviewer
  - [ ] Error message
  - [ ] Stack trace
  - [ ] Error hash
  - [ ] Timestamp
- [ ] A2A UI shows error in error observer status
- [ ] Normal code review requests still work (without trigger keyword)

## Troubleshooting

### If Error Doesn't Flow Through:

1. **Check Environment Variables**
   ```bash
   # Verify ERROR_OBSERVER_URL in code-reviewer
   gcloud run services describe chained-code-reviewer --region us-central1 --format yaml | grep ERROR_OBSERVER_URL
   
   # Verify GITHUB_PAT in error-observer
   gcloud run services describe chained-error-observer --region us-central1 --format yaml | grep GITHUB_PAT
   ```

2. **Check Agent Health**
   ```bash
   # Code reviewer health
   curl https://chained-code-reviewer-XXX.a.run.app/health
   
   # Error observer health
   curl https://chained-error-observer-XXX.a.run.app/health
   ```

3. **Check Agent Cards**
   ```bash
   # Code reviewer A2A card
   curl https://chained-code-reviewer-XXX.a.run.app/.well-known/agent.json
   
   # Error observer A2A card
   curl https://chained-error-observer-XXX.a.run.app/.well-known/agent.json
   ```

4. **Review Logs for Errors**
   ```bash
   # Recent errors in code-reviewer
   gcloud logging read \
     "resource.type=cloud_run_revision AND resource.labels.service_name=chained-code-reviewer AND severity>=ERROR" \
     --limit 20
   
   # Recent errors in error-observer
   gcloud logging read \
     "resource.type=cloud_run_revision AND resource.labels.service_name=chained-error-observer AND severity>=ERROR" \
     --limit 20
   ```

### If GitHub Issue Not Created:

1. **Check GitHub PAT Permissions**
   - Must have `repo` scope
   - Must have access to enufacas/Chained repository
   - Must be able to trigger repository_dispatch events

2. **Check error_observer GitHub Integration**
   ```bash
   # Check error_observer logs for GitHub API calls
   gcloud logging read \
     "resource.type=cloud_run_revision AND resource.labels.service_name=chained-error-observer AND textPayload:'github'" \
     --limit 20
   ```

3. **Manual Test GitHub API**
   ```bash
   curl -X POST \
     -H "Authorization: token $GITHUB_PAT" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/repos/enufacas/Chained/dispatches \
     -d '{"event_type":"cloudrun-error","client_payload":{"test":"manual"}}'
   ```

## Removal Instructions

When testing is complete, remove the intentional bug:

### Step 1: Remove Bug Code
```bash
# Find the bug
grep -n "INTENTIONAL BUG" infrastructure/docker/adk-agents/code-reviewer/agent.py

# Edit the file and delete lines 136-143
# (The entire block from "# INTENTIONAL BUG" to the end of the if statement)
```

### Step 2: Remove Test Files
```bash
rm docs/ERROR_OBSERVER_TESTING.md
rm tests/test_code_reviewer_intentional_bug.py
```

### Step 3: Redeploy
```bash
cd infrastructure/docker/adk-agents
gcloud builds submit --tag gcr.io/chained-ai/code-reviewer code-reviewer/
gcloud run deploy chained-code-reviewer \
  --image gcr.io/chained-ai/code-reviewer \
  --region us-central1
```

### Step 4: Verify
```bash
# Test with trigger keyword - should NOT raise error
curl -X POST "https://chained-code-reviewer-XXX.a.run.app/a2a/tasks" \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","parts":[{"text":"Review: test_error_observer"}]}}'
```

## Benefits of This Approach

1. **Real Error**: Actual Python exception, not simulated
2. **Controlled**: Only triggers with specific keyword
3. **Safe**: Doesn't affect normal operations
4. **Observable**: Flows through entire A2A error system
5. **Testable**: Can be repeatedly triggered
6. **Documented**: Clear instructions for use and removal
7. **Removable**: Easy to find and delete with clear markers

## Related Files

- `infrastructure/docker/adk-agents/code-reviewer/agent.py` - Agent with bug
- `infrastructure/docker/adk-agents/shared/a2a_utils.py` - Error reporting utilities
- `infrastructure/docker/adk-agents/shared/error_event.py` - ErrorEvent model
- `infrastructure/docker/adk-agents/error-observer/agent.py` - Error observer agent
- `docs/error_observer_overview.md` - Error observer system overview
- `docs/ERROR_OBSERVER_TESTING.md` - Testing guide (this PR)

## Status

✅ **Implementation Complete**
⏳ **Deployment Pending**
⏳ **Testing Pending**

The intentional bug is ready to be deployed and tested. Follow the "Next Steps for Testing" section above to proceed.

---

**Created:** 2025-12-04  
**Purpose:** Test error_observer A2A agent with real runtime error  
**Agent:** @troubleshoot-expert (error handling and debugging specialist)
