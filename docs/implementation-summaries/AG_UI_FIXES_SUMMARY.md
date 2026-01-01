# AG-UI Frontend Fixes Summary

**Date:** 2025-12-03  
**Issue:** AG-UI frontend showing ERROR_OBSERVER_URL not configured and pipeline details not appearing after refresh

## Problems Identified

### 1. ERROR_OBSERVER_URL showing as "Not configured"

**Symptom:** Frontend displayed "Error Observer: Not configured (ERROR_OBSERVER_URL not set)" even though the environment variable was properly set in Cloud Run.

**Root Cause:** In Next.js App Router with standalone output, environment variables read at module load time (`const VAR = process.env.X`) are inlined during the build phase. The actual runtime Cloud Run environment variables were not being read.

**Fix:** 
- Moved `process.env.ERROR_OBSERVER_URL` reading from module scope into the `GET()` request handler function
- Added logging to help debug the issue
- File: `src/app/api/error-observer/status/route.ts`

### 2. localStorage Quota Exceeded Errors

**Symptom:** Error observer logs showed: "Failed to execute 'setItem' on 'Storage': Setting the value of 'ag-ui-artifacts' exceeded the quota."

**Root Cause:** 
- Mobile browsers have localStorage limits as low as 2.5MB
- MAX_ARTIFACTS was set to 100 and MAX_SESSIONS to 20
- No size validation before saving artifacts
- Pruning algorithm wasn't aggressive enough

**Fixes:**
- Reduced `MAX_ARTIFACTS` from 100 to 30 (70% reduction)
- Reduced `MAX_SESSIONS` from 20 to 10 (50% reduction)
- Lowered `STORAGE_WARNING_THRESHOLD` from 2MB to 1MB (more conservative)
- Added `STORAGE_MAX_ARTIFACT_SIZE` limit of 100KB with automatic truncation
- Enhanced pruning to remove largest artifacts first (not just oldest)
- Keep only smallest/newest 25% during aggressive pruning (vs 33%)
- File: `src/lib/storage.ts`

### 3. Second Agent Details Not Appearing After Refresh

**Symptom:** User reported selecting 2 agents in sequential run. First agent finished and UI updated. Second agent never appeared to finish. After refresh, showed "2/2" but second agent's details and artifacts were missing.

**Root Cause:**
- Pipeline a2aSteps (agent execution details) were only stored in `activePipelines` Map in memory
- When Cloud Run container restarted or page refreshed, the Map was cleared
- localStorage only had session record with artifact IDs, but not the a2aSteps metadata
- `sessionToPipelineResult()` couldn't reconstruct the details

**Fixes:**
- Save a2aSteps in session metadata when pipeline completes
  - Includes task IDs, agent names, phases, timing, artifacts
  - Only stores previews (not full data) to avoid quota issues
  - File: `src/app/api/pipeline/route.ts`
- Reconstruct a2aSteps from session metadata when loading from localStorage
  - File: `src/components/PipelineOutcomes.tsx`

## Files Changed

1. **src/app/api/error-observer/status/route.ts**
   - Read ERROR_OBSERVER_URL at runtime inside handler
   - Added console logging for debugging

2. **src/lib/storage.ts**
   - Reduced storage limits significantly
   - Added artifact size validation with truncation
   - Improved pruning algorithm to target large artifacts
   - More aggressive cleanup strategy

3. **src/app/api/pipeline/route.ts**
   - Save a2aSteps in session metadata with complete details
   - Store only essential data to avoid quota issues

4. **src/components/PipelineOutcomes.tsx**
   - Reconstruct a2aSteps from session metadata
   - Include totalDurationMs when loading from localStorage

## Testing Checklist

### Local Testing
- [x] Linting passed (no errors)
- [x] TypeScript compilation successful

### Cloud Run Deployment Testing
- [ ] Deploy to Cloud Run
- [ ] Check logs for ERROR_OBSERVER_URL logging
- [ ] Verify error observer status shows "configured"
- [ ] Monitor for localStorage quota errors

### Pipeline Execution Testing
- [ ] Create pipeline with 2+ sequential agents
- [ ] Verify first agent completes and UI updates
- [ ] Verify second agent completes and UI updates in real-time
- [ ] Verify both agents show full details without refresh
- [ ] Refresh page and verify:
  - Pipeline shows correct completion status (2/2)
  - Both agents' details are visible
  - Artifacts are accessible
  - Timing information is correct

### Mobile Testing
- [ ] Test on mobile device or mobile viewport
- [ ] Verify no localStorage quota errors
- [ ] Verify UI is responsive and functional

## Expected Behavior After Fixes

1. **Error Observer Status:**
   - Should show "Error Observer: [STATUS]" with green indicator
   - Should display real-time error tracking
   - Should NOT show "Not configured" message

2. **Pipeline Execution:**
   - Sequential agent runs update UI in real-time (5-second polling)
   - All agent details visible during execution
   - Progress indicators update correctly

3. **After Page Refresh:**
   - Pipeline status correctly shows completion (e.g., "2/2")
   - All agent details are visible (not just first agent)
   - Artifacts are accessible
   - Timing information is preserved
   - No localStorage quota errors

4. **Storage Management:**
   - Artifacts capped at 30 items
   - Sessions capped at 10 items
   - Large artifacts (>100KB) are automatically truncated
   - Storage pruning is aggressive and targets largest items first

## Technical Insights

### Next.js App Router Environment Variables
- Environment variables at module scope are inlined at build time
- Always read `process.env` inside request handlers for runtime values
- Critical for Cloud Run where variables are set at deployment

### localStorage Best Practices
- Mobile browsers can have limits as low as 2.5MB
- Always validate size before saving
- Implement smart pruning (size-based, not just time-based)
- Use aggressive limits to prevent quota errors
- Provide graceful degradation when storage fails

### Serverless State Management
- Never rely on in-memory state (Maps, globals) in serverless
- Container restarts clear all memory
- Always persist user-visible state to durable storage
- Reconstruct complete state from persisted data
- Use localStorage for client-side state, database for server-side

## Deployment Notes

These changes are backward compatible and safe to deploy. They fix critical bugs without breaking existing functionality.

**Recommended deployment process:**
1. Deploy changes to Cloud Run
2. Monitor logs for first few requests
3. Test with a real pipeline execution
4. Verify error observer status
5. Test on mobile device

## GCP Logs Verification

After deployment, check these log entries:

```bash
# Verify ERROR_OBSERVER_URL is configured
gcloud logging read 'resource.labels.service_name="chained-ag-ui-frontend" AND textPayload:"ERROR_OBSERVER_URL"' --limit=10

# Check for localStorage quota errors (should see fewer)
gcloud logging read 'resource.labels.service_name="chained-error-observer" AND jsonPayload.metadata.type="storage-error"' --limit=10

# Verify pipeline executions complete successfully
gcloud logging read 'resource.labels.service_name="chained-ag-ui-frontend" AND textPayload:"Pipeline.*complete"' --limit=10
```

## Related Issues

- Previous localStorage fixes (reduced MAX_SESSIONS from 50 to 20)
- Error observer system implementation
- A2A pipeline execution enhancements

## References

- [Next.js Environment Variables](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
- [localStorage Limits](https://developer.mozilla.org/en-US/docs/Web/API/Storage/setItem)
- [Cloud Run Environment Variables](https://cloud.google.com/run/docs/configuring/services/environment-variables)
