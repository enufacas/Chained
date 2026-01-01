# Intentional Bug - Final Verification Checklist

## Pre-Deployment Checklist

- [x] Bug code added to `infrastructure/docker/adk-agents/code-reviewer/agent.py`
- [x] Bug triggers on "test_error_observer" keyword (case-insensitive)
- [x] Bug logic tested locally - PASSED
- [x] Python syntax validated - PASSED
- [x] Error reporting mechanism verified - EXISTS (line 347)
- [x] Documentation created:
  - [x] `docs/ERROR_OBSERVER_TESTING.md` - User guide
  - [x] `INTENTIONAL_BUG_SUMMARY.md` - Implementation summary
  - [x] `tests/test_code_reviewer_intentional_bug.py` - Test script
  - [x] `scripts/trigger-bug-test.sh` - Trigger automation
- [x] Code committed to branch `copilot/introduce-bug-for-error-observer`
- [x] PR ready for review

## Deployment Checklist

After PR is merged and code is deployed to GCP:

### Step 1: Deploy Code-Reviewer Agent
```bash
cd infrastructure/docker/adk-agents
gcloud builds submit --tag gcr.io/chained-ai/code-reviewer code-reviewer/
gcloud run deploy chained-code-reviewer \
  --image gcr.io/chained-ai/code-reviewer \
  --region us-central1 \
  --set-env-vars ERROR_OBSERVER_URL=https://[ERROR-OBSERVER-URL]
```

- [ ] Build successful
- [ ] Deployment successful
- [ ] Service URL obtained: ___________________________

### Step 2: Verify Configuration
```bash
# Check ERROR_OBSERVER_URL is set
gcloud run services describe chained-code-reviewer \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env[?name='ERROR_OBSERVER_URL'].value)"
```

- [ ] ERROR_OBSERVER_URL is set correctly
- [ ] Value: ___________________________

```bash
# Check error_observer is healthy
curl https://[ERROR-OBSERVER-URL]/health
```

- [ ] Error observer health check returns 200 OK

```bash
# Check code-reviewer is healthy
curl https://[CODE-REVIEWER-URL]/health
```

- [ ] Code reviewer health check returns 200 OK
- [ ] AI mode is "enabled" (Gemini configured)

### Step 3: Trigger the Bug

**Method A: Using the trigger script**
```bash
./scripts/trigger-bug-test.sh https://[CODE-REVIEWER-URL]
```

- [ ] Script executed successfully
- [ ] Agent returned "failed" task state
- [ ] Error message mentions ZeroDivisionError

**Method B: Via A2A UI**
1. Navigate to https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/
2. Ask: "Please review this code: `# test_error_observer\ndef test(): pass`"

- [ ] UI sent request
- [ ] Agent responded with error
- [ ] Error visible in UI

### Step 4: Verify Error Observer Received Error

```bash
# Check error observer status
curl https://[ERROR-OBSERVER-URL]/status
```

- [ ] Error observer received error event
- [ ] Status shows recent error processing
- [ ] Last error details visible

```bash
# Check error observer logs
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=chained-error-observer" \
  --limit 50 --format json
```

- [ ] Log entry shows error event received
- [ ] Log entry shows GitHub dispatch attempt
- [ ] No errors in error observer processing

### Step 5: Verify GitHub Issue Created

1. Go to https://github.com/enufacas/Chained/issues
2. Look for recently created issue

- [ ] GitHub issue created automatically
- [ ] Issue title mentions "Cloud Run Error" or "code-reviewer"
- [ ] Issue body contains:
  - [ ] Service name: code-reviewer
  - [ ] Error message: "division by zero"
  - [ ] Stack trace present
  - [ ] Error hash for deduplication
  - [ ] Timestamp
  - [ ] Region and environment info
- [ ] Issue has appropriate labels (e.g., `cloudrun-error`)

### Step 6: Verify A2A UI Shows Error

1. Navigate to https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/
2. Look for error observer status/activity

- [ ] Error observer agent shows recent activity
- [ ] Error details visible in UI
- [ ] Error state shows "dispatched" or "success"

### Step 7: Verify Normal Operations Not Affected

Test code review WITHOUT the trigger keyword:

```bash
curl -X POST "https://[CODE-REVIEWER-URL]/a2a/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "parts": [{"text": "Review: def hello(): return \"world\""}]
    }
  }'
```

- [ ] Request processed successfully (or fails due to Gemini config, not bug)
- [ ] No ZeroDivisionError
- [ ] Normal error handling if Gemini is unavailable

### Step 8: Test Repeated Triggers (Deduplication)

Trigger the bug 2-3 more times with the same code:

- [ ] Error observer receives all events
- [ ] GitHub issues deduplicated (same hash = same issue updated)
- [ ] Error observer shows occurrence count incrementing

## Troubleshooting Checklist

If verification fails at any step:

### Error Observer Not Receiving Errors

- [ ] Verify ERROR_OBSERVER_URL in code-reviewer environment
- [ ] Check code-reviewer logs for error reporting attempts
- [ ] Verify network connectivity between services
- [ ] Check A2A protocol compatibility

### GitHub Issue Not Created

- [ ] Verify GITHUB_PAT in error-observer environment
- [ ] Check PAT has `repo` scope and dispatch permissions
- [ ] Check error-observer logs for GitHub API errors
- [ ] Verify repository name and owner are correct
- [ ] Test GitHub API manually with PAT

### Bug Not Triggering

- [ ] Verify keyword is spelled correctly: "test_error_observer"
- [ ] Check if bug code was deployed (view logs or source)
- [ ] Verify keyword check is case-insensitive
- [ ] Check Python version compatibility

### A2A UI Not Showing Error

- [ ] Verify error observer status endpoint is accessible
- [ ] Check UI frontend is polling error observer
- [ ] Check for UI errors in browser console
- [ ] Verify ERROR_OBSERVER_URL in UI backend

## Success Criteria

All of the following must be true for successful verification:

- [x] Bug implementation is working correctly
- [ ] Bug deployed to GCP Cloud Run
- [ ] Bug triggers with keyword "test_error_observer"
- [ ] Error reported to error_observer via A2A protocol
- [ ] Error observer processes error event
- [ ] GitHub issue created automatically
- [ ] Error visible in A2A UI
- [ ] Normal operations not affected
- [ ] Error deduplication working
- [ ] All documentation in place

## Post-Testing Cleanup

After successful testing, schedule removal:

- [ ] Create issue: "Remove intentional bug from code-reviewer"
- [ ] Schedule deployment of clean code
- [ ] Remove test documentation files
- [ ] Update this checklist status

## Sign-Off

### Deployment Sign-Off
- [ ] Deployed by: _________________ Date: _______
- [ ] Deployment verified by: _________________ Date: _______

### Testing Sign-Off
- [ ] Tests executed by: _________________ Date: _______
- [ ] All verification steps passed
- [ ] Results documented

### Approval for Cleanup
- [ ] Approved for bug removal by: _________________ Date: _______
- [ ] Bug removal scheduled for: _______

---

**Document Version:** 1.0  
**Created:** 2025-12-04  
**Purpose:** Track verification of intentional bug implementation  
**Status:** Ready for deployment verification
