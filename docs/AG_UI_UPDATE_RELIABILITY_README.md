# AG-UI Update Reliability: Quick Reference

**Date:** 2025-12-10  
**PRs:** #3803 (merged), #TBD (this PR)  
**Full Analysis:** [AG_UI_UPDATE_RELIABILITY_ANALYSIS.md](./AG_UI_UPDATE_RELIABILITY_ANALYSIS.md)

## TL;DR

**User Question:** Why does the UI not update even after waiting past the old polling interval?

**Answer:** Faster polling (PR #3803) helped but wasn't enough. The real problems are:
1. **CRITICAL (unfixed):** Data lost on Cloud Run restart - backend uses in-memory Map
2. **HIGH (fixed):** No error recovery - transient failures break updates permanently
3. **MEDIUM (unfixed):** Silent failures - persistence errors not surfaced to user

## What Was Fixed (This PR)

✅ **Frontend Error Recovery:**
- Retry logic with exponential backoff (3 attempts)
- Timeout protection (10s per request)
- Visual error indicators (status line, error banner, retry button)
- Session polling continues despite transient errors

**Impact:** Transient network issues no longer break real-time updates. Users see when updates fail.

## What Remains Unfixed (Needs Backend Work)

⚠️ **Data Persistence** (CRITICAL):
- `activePipelines` and `activeSessions` are volatile Maps
- Lost when Cloud Run scales to zero or restarts
- Frontend polls but gets empty data
- **This is why user "waited past polling interval" - data was gone**

**Solution Options:**
- Option A: Load from Firestore on startup
- Option B: Save to Firestore on every update
- Option C: Use Redis/Memorystore for shared state

## Quick Comparison

| Issue | Before | After (This PR) | Future |
|-------|--------|-----------------|--------|
| Network error | ❌ No retry, silent fail | ✅ 3 retries, user notified | - |
| Request timeout | ❌ Hangs indefinitely | ✅ 10s limit | - |
| Cloud Run restart | ❌ Data lost forever | ❌ Still lost | ⏹️ Needs persistence |
| Error visibility | ❌ Console only | ✅ UI banner + status | - |
| Polling stops | ❌ On any error | ✅ Continues with retry | - |

## Files Changed

- `infrastructure/docker/ag-ui-frontend/src/app/page.tsx` - Error recovery logic
- `docs/AG_UI_UPDATE_RELIABILITY_ANALYSIS.md` - Comprehensive analysis (14KB)
- `docs/a2a-ui/CHANGELOG.md` - Detailed changelog entry

## Testing

**Verify error recovery:**
1. Start AG-UI locally
2. Simulate network failure (throttle or offline mode)
3. Should see error banner and retry attempts
4. Should recover when network restored

**Reproduce data loss** (demonstrates unfixed issue):
1. Start pipeline on production AG-UI
2. Wait for Cloud Run to scale down (15-60 min) OR restart manually
3. Observe: Pipeline disappears from UI
4. **This is the CRITICAL issue that needs backend persistence**

## Related Documents

- **Full Analysis:** [AG_UI_UPDATE_RELIABILITY_ANALYSIS.md](./AG_UI_UPDATE_RELIABILITY_ANALYSIS.md)
- **Changelog:** [docs/a2a-ui/CHANGELOG.md](../a2a-ui/CHANGELOG.md)
- **Original PR:** #3803
- **User Comment:** https://github.com/enufacas/Chained/pull/3803#issuecomment-3635313876
- **Copilot Session:** https://github.com/enufacas/Chained/actions/runs/20087201916 (cancelled)

## Next Steps

1. **Critical:** Implement backend persistence (see Options A/B/C in full analysis)
2. **Recommended:** Test error recovery on production
3. **Optional:** Consider min_instances=1 for better reliability (~$15-30/month)

## Quick Stats

- **5 root causes identified** (1 critical, 2 high, 2 medium)
- **3 issues fixed** (both HIGH priority + visual indicators)
- **2 issues remain** (1 CRITICAL data persistence, 1 MEDIUM cold starts)
- **519 lines of documentation** created
- **103 lines of code** changed for error recovery
