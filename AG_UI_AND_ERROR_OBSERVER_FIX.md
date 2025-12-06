# AG-UI and Error Observer Fix Summary

**Date**: 2025-12-06
**Issue**: AG-UI stopped updating after 2 tasks, error observer not capturing/shipping errors

## Problems Identified

### 1. UI Update Problem ✅ FIXED

**Symptom**: Pipeline execution UI stops updating after the first 2 tasks, even though backend continues processing.

**Root Cause**: Missing state updates after A2A step completion.

**Technical Details**:
- Pipeline execution flow: research → trends → writing
- Each phase calls an agent, gets response, creates A2A step detail
- Code pushed step detail to `pipeline.a2aSteps` array
- **Critical Bug**: Code did NOT call `activePipelines.set(pipelineId, pipeline)` after the push
- Result: Map contained stale pipeline object without new steps
- Frontend polls `/api/pipeline` → Gets old data without completed steps
- UI stuck showing only initial phases

**Fix Locations** (`infrastructure/docker/ag-ui-frontend/src/app/api/pipeline/route.ts`):
```typescript
// After line 542 - Research success
pipeline.a2aSteps?.push(createA2AStepDetail(...));
activePipelines.set(pipelineId, pipeline); // ← ADDED

// After line 563 - Research fallback  
pipeline.a2aSteps?.push(createA2AStepDetail(...));
activePipelines.set(pipelineId, pipeline); // ← ADDED

// After line 638 - Trends success
pipeline.a2aSteps?.push(createA2AStepDetail(...));
activePipelines.set(pipelineId, pipeline); // ← ADDED

// After line 658 - Trends fallback
pipeline.a2aSteps?.push(createA2AStepDetail(...));
activePipelines.set(pipelineId, pipeline); // ← ADDED

// After line 833 - Writing success
pipeline.a2aSteps?.push(createA2AStepDetail(...));
activePipelines.set(pipelineId, pipeline); // ← ADDED

// After line 860 - Writing fallback
pipeline.a2aSteps?.push(createA2AStepDetail(...));
activePipelines.set(pipelineId, pipeline); // ← ADDED
```

**Why This Fixes It**:
- Now every A2A step addition immediately updates the Map
- Frontend polling gets fresh data with all completed steps
- UI updates in real-time as each agent completes its work
- No more stuck progress indicators

### 2. Error Observer Problem ✅ FIXED

**Symptom**: Error observer not shipping errors to GitHub for triage.

**Root Cause**: Environment variable name mismatch.

**Technical Details**:
- Terraform configuration: Sets `GIT_REPO` environment variable
- Python agent code: Reads `GITHUB_REPO` environment variable
- Result: Agent receives empty string, uses default, may fail dispatch
- Compounded by insufficient logging for debugging

**Fix Locations**:

1. **Terraform** (`infrastructure/terraform/adk-agents.tf` line 1357-1360):
```terraform
# BEFORE (WRONG)
env {
  name  = "GIT_REPO"
  value = var.git_repo != "" ? var.git_repo : "enufacas/Chained"
}

# AFTER (CORRECT)
env {
  name  = "GITHUB_REPO"
  value = var.git_repo != "" ? var.git_repo : "enufacas/Chained"
}
```

2. **Enhanced Logging** (`infrastructure/docker/adk-agents/error-observer/agent.py`):

**Startup logging**:
```python
print(f"🚀 Error Observer Agent starting on port {PORT}")
print(f"   GitHub integration: {'✅ Configured' if GITHUB_TOKEN else '❌ Not configured'}")
print(f"   GitHub repository: {GITHUB_REPO}")  # ← ADDED
print(f"   Agent URL: {os.getenv('SERVICE_URL', f'http://localhost:{PORT}')}")  # ← ADDED
```

**Dispatch logging**:
```python
print(f"📤 Dispatching error to GitHub: {url}")  # ← ADDED
print(f"   Event type: cloudrun-error")  # ← ADDED
print(f"   Service: {error_event.service}")  # ← ADDED
print(f"   Error hash: {error_event.error_hash}")  # ← ADDED
print(f"   Response headers: {dict(response.headers)}")  # ← ADDED when error
traceback.print_exc()  # ← ADDED for exceptions
```

**Why This Fixes It**:
- Correct environment variable name ensures proper GitHub integration
- Enhanced logging makes issues immediately visible in Cloud Run logs
- Easier to diagnose configuration problems during deployment
- Full stack traces help debug API call failures

## System Architecture

### Pipeline Update Flow (Fixed)
```
1. POST /api/pipeline (create pipeline)
   ↓
2. executePipelineWithAgents() starts
   ↓
3. Phase 1: Research
   - Call research agent
   - Create A2A step detail
   - Push to pipeline.a2aSteps
   - ✅ activePipelines.set() [FIXED]
   ↓
4. Phase 2: Trends
   - Call trends agent
   - Create A2A step detail
   - Push to pipeline.a2aSteps
   - ✅ activePipelines.set() [FIXED]
   ↓
5. Phase 3: Writing
   - Call writer agent
   - Create A2A step detail
   - Push to pipeline.a2aSteps
   - ✅ activePipelines.set() [FIXED]
   ↓
6. Complete pipeline
   - Save to localStorage
   - ✅ activePipelines.set()
   ↓
7. Frontend polls GET /api/pipeline
   - Gets fresh data with all steps ✅
   - UI updates in real-time ✅
```

### Error Observer Flow (Fixed)
```
1. Frontend captures error
   ↓
2. POST /api/ui-error-report
   - Creates ErrorEvent
   ↓
3. POST error-observer/a2a/tasks
   - Error observer receives event
   - Logs: "📤 Dispatching to GitHub: ..."
   ↓
4. POST https://api.github.com/repos/GITHUB_REPO/dispatches
   - ✅ GITHUB_REPO now set correctly [FIXED]
   - event_type: "cloudrun-error"
   - Logs: "✅ Successfully dispatched" or detailed error
   ↓
5. GitHub triggers workflow
   - .github/workflows/handle-cloudrun-errors.yml
   ↓
6. Workflow creates issue
   - Title: "🚨 Cloud Run Error: {service}"
   - Body: Stack trace, context, console links
   - Labels: bug, automated, cloud-run-error
```

## Deployment Instructions

### 1. Deploy AG-UI Frontend

```bash
# Build and deploy
cd infrastructure/terraform
terraform apply -target=google_cloud_run_v2_service.ag_ui_frontend

# Or using gcloud
cd infrastructure/docker
gcloud builds submit --tag gcr.io/chained-ai/ag-ui-frontend ag-ui-frontend/
gcloud run deploy chained-ag-ui-frontend \
  --image gcr.io/chained-ai/ag-ui-frontend \
  --region us-central1 \
  --update-env-vars ERROR_OBSERVER_URL=https://chained-error-observer-xxx.run.app
```

### 2. Deploy Error Observer

```bash
# Apply terraform changes
cd infrastructure/terraform
terraform apply -target=google_cloud_run_v2_service.error_observer

# Verify environment variables
gcloud run services describe chained-error-observer \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"

# Should include:
# - GITHUB_PAT (from secret)
# - GITHUB_REPO=enufacas/Chained
# - SERVICE_URL=https://...
```

### 3. Verify Deployment

**Check Cloud Run Logs**:
```bash
# Error observer startup
gcloud logging read \
  'resource.type="cloud_run_revision" AND 
   resource.labels.service_name="chained-error-observer" AND
   textPayload=~"🚀 Error Observer Agent starting"' \
  --limit 5 --format json

# Should show:
# "🚀 Error Observer Agent starting on port 8090"
# "   GitHub integration: ✅ Configured"
# "   GitHub repository: enufacas/Chained"
# "   Agent URL: https://..."
```

**Test Error Dispatch**:
1. Open https://chained-ag-ui-frontend-xxx.run.app/
2. Find "Error Observer" section
3. Click "Send Test Error" button
4. Check GitHub for new issue: https://github.com/enufacas/Chained/issues
5. Verify workflow run: https://github.com/enufacas/Chained/actions

## Testing Checklist

### UI Update Testing
- [ ] Deploy AG-UI frontend with fixes
- [ ] Create new pipeline with topic "Testing real-time updates"
- [ ] Open browser DevTools → Network tab
- [ ] Watch polling requests to `/api/pipeline?id=...`
- [ ] Verify progress updates immediately after each phase:
  - [ ] Research phase (progress 25%)
  - [ ] Trends phase (progress 50%)
  - [ ] Writing phase (progress 90%)
  - [ ] Complete (progress 100%)
- [ ] Check `a2aSteps` array length increases: 0 → 1 → 2 → 3
- [ ] Verify UI reflects all phases without page reload

### Error Observer Testing
- [ ] Deploy error observer with terraform fix
- [ ] Check Cloud Run logs for startup messages
- [ ] Verify GITHUB_REPO shown in logs
- [ ] Navigate to AG-UI frontend
- [ ] Click "Send Test Error" in Error Observer section
- [ ] Wait 10 seconds, check for success message
- [ ] Go to GitHub Issues: https://github.com/enufacas/Chained/issues
- [ ] Verify new issue created:
  - [ ] Title: "🚨 Cloud Run Error: a2a-ui-test"
  - [ ] Body includes stack trace
  - [ ] Labels: bug, automated, cloud-run-error
- [ ] Check workflow run completed successfully
- [ ] Verify error observer logs show:
  - [ ] "📤 Dispatching error to GitHub: ..."
  - [ ] "✅ Successfully dispatched error to GitHub: ..."

### End-to-End Testing
- [ ] Trigger real error in AG-UI (e.g., invalid input)
- [ ] Verify error flows: UI → observer → GitHub → Issue
- [ ] Check all logs at each stage
- [ ] Verify issue created automatically
- [ ] Verify error details are complete and accurate

## Known Limitations

1. **In-Memory State**: Pipeline state still stored in-memory only
   - Lost on service restart
   - Use localStorage for persistence between user sessions
   - Consider Redis/Firestore for production persistence

2. **Polling Frequency**: Frontend polls every 5 seconds
   - Good for real-time updates
   - Could use Server-Sent Events (SSE) for better efficiency

3. **Error Deduplication**: Current implementation tracks by hash
   - Works for preventing duplicate issues
   - Could enhance with time-windowing

## Monitoring

### Metrics to Watch

**AG-UI Frontend**:
- `activePipelines.size` - Number of active pipelines
- Pipeline completion rate
- Average phase duration
- State update frequency

**Error Observer**:
- Errors received per hour
- GitHub dispatch success rate
- Dispatch latency
- Error distribution by service

### Alerts to Set Up

1. **Pipeline Stuck**: No progress for > 5 minutes
2. **Error Observer Down**: Health check fails
3. **GitHub API Errors**: Dispatch failure rate > 10%
4. **High Error Rate**: > 50 errors/hour from same service

## Related Documentation

- [Error Observer Overview](./docs/error_observer_overview.md)
- [Error Observer Schema](./docs/error_observer_schema.md)
- [A2A UI Documentation](./docs/a2a-ui/README.md)
- [Pipeline API Documentation](./infrastructure/docker/ag-ui-frontend/README.md)

## Success Criteria

✅ **Pipeline Updates**:
- UI updates within 5 seconds of each phase completion
- All 3 phases show in real-time
- No stuck progress indicators
- Browser console shows state updates

✅ **Error Observer**:
- Test errors create GitHub issues
- Dispatch success rate > 95%
- Cloud Run logs show all dispatch attempts
- Issue body contains complete error details

✅ **System Health**:
- No OOM crashes (memory limits adequate)
- Error observer responds to health checks
- Frontend polling successful
- End-to-end latency < 30 seconds

## Next Steps

1. **Immediate**: Deploy fixes and verify testing checklist
2. **Short-term**: Add Server-Sent Events for real-time updates
3. **Medium-term**: Implement Redis for pipeline state persistence
4. **Long-term**: Add error analytics dashboard
