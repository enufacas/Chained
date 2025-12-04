# ERROR_OBSERVER_URL Runtime Access Fix - Complete Summary

## Problem Statement

The ERROR_OBSERVER_URL environment variable was correctly configured in Terraform and visible in Cloud Run service configuration, but the running ag-ui-frontend containers could not access it at runtime. The debug endpoint consistently showed:

```json
{
  "envStatus": {
    "ERROR_OBSERVER_URL": {
      "set": false,
      "value": "not set",
      "length": 0
    }
  }
}
```

## Investigation Using GCP Access

With direct access to GCP, I was able to verify the actual state:

### What I Found

1. **Cloud Run Configuration ✅**
   ```bash
   gcloud run revisions describe chained-ag-ui-frontend-00103-6tx --region us-central1
   ```
   Result: ERROR_OBSERVER_URL **IS** set to `https://chained-error-observer-sguacxy5gq-uc.a.run.app`

2. **Runtime Check ❌**
   ```bash
   curl https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/debug/env
   ```
   Result: Shows ERROR_OBSERVER_URL as "not set"

3. **Critical Discovery: Timestamp Never Changes**
   - Multiple requests to the debug endpoint returned the EXACT same timestamp: `2025-12-04T06:09:00.927Z`
   - This timestamp was **before** the workflow completed (06:13:20Z)
   - This indicated **Next.js API route caching**

## Root Causes Identified

### 1. Next.js API Route Caching (PRIMARY ISSUE)

By default, Next.js 13+ App Router **caches API route responses** for static optimization. This means:

- The first request to `/api/debug/env` created a cached response
- All subsequent requests served the cached response
- Even new container instances served the old cached response
- Environment variables read at build time were frozen in the cache

**Evidence:**
- Timestamp frozen at `2025-12-04T06:09:00.927Z` across multiple requests
- Response never changed despite new deployments
- Multiple routes affected: `/api/debug/env`, `/api/activity`, `/api/error-observer/status`

### 2. Missing Dynamic Exports

Next.js requires explicit opt-out from caching via:
```typescript
export const dynamic = 'force-dynamic';
export const revalidate = 0;
```

None of the API routes reading environment variables had this, causing them all to be cached.

## Solution Implemented

### 1. Fixed Next.js API Route Caching

Added dynamic exports to all routes that read environment variables:

**Files Modified:**
- `infrastructure/docker/ag-ui-frontend/src/app/api/debug/env/route.ts`
- `infrastructure/docker/ag-ui-frontend/src/app/api/activity/route.ts`
- `infrastructure/docker/ag-ui-frontend/src/app/api/error-observer/status/route.ts`
- `infrastructure/docker/ag-ui-frontend/src/app/api/ui-error-report/route.ts`
- `infrastructure/docker/ag-ui-frontend/src/app/api/test-github-webhook/route.ts`

**Change Pattern:**
```typescript
// Force dynamic rendering - environment variables must be read at runtime
export const dynamic = 'force-dynamic';
export const revalidate = 0;
```

### 2. Enhanced Terraform Revision Tracking

Added deployment-version label to Cloud Run template to ensure new revisions are created:

**File:** `infrastructure/terraform/adk-agents.tf`

```hcl
template {
  # Add label to track deployment version - forces new revision when image_tag changes
  labels = {
    "deployment-version" = substr(replace(var.image_tag, ".", "-"), 0, 63)
  }
  
  containers {
    # ... rest of config
  }
}
```

### 3. Improved Deployment Verification

Enhanced the workflow to:
- Wait for new revisions to be ready before testing
- Retry runtime checks to handle cold starts
- Show detailed debug output on failure
- **Fail the workflow** if environment variables aren't accessible after retries

**File:** `.github/workflows/deploy-adk-agents.yml`

Key improvements:
- Checks latest revision readiness
- Retries runtime checks up to 3 times with 10-second delays
- Exits with error if ERROR_OBSERVER_URL remains unavailable
- Provides detailed debugging information

## Why This Happened

1. **Next.js Defaults Changed**: Next.js 13+ App Router defaults to caching API routes for performance
2. **No Documentation**: The caching behavior wasn't obvious from the code
3. **Runtime vs Build Time**: Environment variables were being read, but the response was cached at build/first-request time
4. **Revision Updates Worked**: Cloud Run WAS creating new revisions correctly, but cached responses masked the fix

## Expected Outcome After Fix

After the next deployment with these changes:

1. ✅ New container images will be built with the dynamic export fixes
2. ✅ Cloud Run will create new revisions
3. ✅ API routes will read environment variables at runtime (not from cache)
4. ✅ Debug endpoint will show ERROR_OBSERVER_URL as configured
5. ✅ Error Observer UI features will work correctly

## Testing the Fix

After deployment, verify with:

```bash
# Check the debug endpoint multiple times
for i in {1..3}; do
  curl -s https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/debug/env | jq '.envStatus.ERROR_OBSERVER_URL, .timestamp'
done
```

Expected:
- Timestamp should be **different** on each request (or at least recent)
- ERROR_OBSERVER_URL.set should be `true`
- ERROR_OBSERVER_URL.value should show "configured"

## Lessons Learned

1. **Always check for caching** when environment variables appear to not propagate
2. **Use `dynamic = 'force-dynamic'`** for all API routes that read runtime config
3. **Monitor timestamps** to detect caching issues quickly
4. **Test with GCP CLI** to verify the actual deployed state vs perceived state
5. **Next.js App Router caching** requires explicit opt-out for dynamic content

## Related Issues

This fix resolves the following related problems:
- Error Observer "Not configured" message persisting in UI
- Agent activity monitoring showing stale data
- Error reporting webhook tests not finding ERROR_OBSERVER_URL
- All routes that depend on ERROR_OBSERVER_URL being unavailable

## Files Changed

### Frontend Code (5 files)
- `infrastructure/docker/ag-ui-frontend/src/app/api/debug/env/route.ts`
- `infrastructure/docker/ag-ui-frontend/src/app/api/activity/route.ts`
- `infrastructure/docker/ag-ui-frontend/src/app/api/error-observer/status/route.ts`
- `infrastructure/docker/ag-ui-frontend/src/app/api/ui-error-report/route.ts`
- `infrastructure/docker/ag-ui-frontend/src/app/api/test-github-webhook/route.ts`

### Infrastructure (2 files)
- `infrastructure/terraform/adk-agents.tf` - Added deployment-version label
- `.github/workflows/deploy-adk-agents.yml` - Enhanced verification with retries

## Commits

1. `ba08dcc2` - Fix: Prevent Next.js caching of debug endpoint and add revision tracking
2. `7b194da0` - Fix: Add dynamic exports to all routes reading ERROR_OBSERVER_URL

---

**Issue Resolution:** After these changes are deployed, the ERROR_OBSERVER_URL will be accessible at runtime and the "Not configured" message will disappear from the UI.
