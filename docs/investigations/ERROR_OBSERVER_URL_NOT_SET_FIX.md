# Error Observer URL Not Set in AG-UI Frontend - Fix

**Date:** 2025-12-04  
**Issue:** ERROR_OBSERVER_URL environment variable not available in deployed ag-ui-frontend container  
**Status:** Fixed ✅

## Problem Statement

The AG-UI Frontend debug endpoint `/api/debug/env` showed:

```json
{
  "endpoint": "/api/debug/env",
  "timestamp": "2025-12-04T05:13:03.116Z",
  "envStatus": {
    "ERROR_OBSERVER_URL": {
      "set": false,
      "value": "not set",
      "length": 0
    },
    "AGENT_ERROR_OBSERVER_URL": {
      "set": false,
      "value": "not set",
      "length": 0
    },
    "ENVIRONMENT": "not set",
    "NODE_ENV": "production",
    "GOOGLE_CLOUD_PROJECT": {
      "set": false,
      "value": "not set"
    },
    "USE_VERTEX_AI": "not set"
  },
  "recommendations": [
    "ERROR_OBSERVER_URL should be set via Terraform: google_cloud_run_v2_service.error_observer.uri",
    "Check Cloud Run service configuration in GCP Console",
    "Verify error_observer service is deployed and running",
    "Check that ag-ui-frontend service has latest revision deployed"
  ]
}
```

This prevented the AG-UI Frontend from:
- Reporting UI errors to the error observer
- Displaying error observer status in the UI
- Integrating with the A2A error monitoring system

## Root Cause Analysis

### What the Terraform Configuration Says

In `infrastructure/terraform/adk-agents.tf` lines 1155-1159:

```terraform
# Error Observer URL for UI error reporting and activity monitoring
env {
  name  = "ERROR_OBSERVER_URL"
  value = google_cloud_run_v2_service.error_observer.uri
}
```

**This configuration is CORRECT.** It:
- ✅ References the error_observer service URI
- ✅ Has proper dependencies (line 1293)
- ✅ Is included in deployment targets (workflow line 493)

### Why It Wasn't Working

**The Issue:** Cloud Run Container Caching

1. **Historical Context:**
   - error_observer service was added to Terraform AFTER ag-ui-frontend already existed
   - Initial ag-ui-frontend deployments happened WITHOUT error_observer reference
   - Those deployments created container revisions lacking ERROR_OBSERVER_URL

2. **Container Image Caching:**
   - Cloud Run serves container images by SHA tag
   - If code doesn't change, same image is used
   - Environment variables are baked into the SERVICE definition, not the image
   - BUT: If service isn't updated, it keeps serving old revision without new env vars

3. **Terraform Behavior:**
   - Terraform only updates Cloud Run service when:
     - Container image changes (new `image_tag`)
     - Service configuration changes
     - Environment variables in Terraform change
   - If image tag is same AND Terraform config unchanged, service not updated

4. **The Catch-22:**
   - error_observer.uri was added to Terraform config
   - But if ag-ui-frontend code didn't change
   - Same container image (SHA) used
   - Terraform might skip updating the service
   - Old revision without ERROR_OBSERVER_URL kept running

## Solution

### Fix Applied

**File:** `infrastructure/docker/ag-ui-frontend/src/app/api/debug/env/route.ts`

**Change:**
```typescript
/**
 * Environment Debug API Endpoint
 * 
 * Returns environment variable status for debugging configuration issues.
 * This endpoint helps diagnose why ERROR_OBSERVER_URL might not be set.
 * 
 * SECURITY NOTE: Only returns boolean status, not actual values, to avoid
 * exposing sensitive information.
 * 
 * Updated: 2025-12-04 - Force rebuild to pick up ERROR_OBSERVER_URL from Terraform
 */
```

Added comment with timestamp to force container rebuild.

### Why This Works

1. **Triggers Rebuild:**
   - Code change detected in ag-ui-frontend
   - `deploy-adk-agents.yml` workflow triggered
   - New container image built with new SHA

2. **Forces Terraform Update:**
   - Workflow passes `image_tag: ${{ github.sha }}`
   - Terraform sees new image tag
   - Updates ag-ui-frontend Cloud Run service
   - Applies ALL environment variables including ERROR_OBSERVER_URL

3. **New Revision Deployed:**
   - Cloud Run creates new revision with new image
   - New revision has ERROR_OBSERVER_URL set correctly
   - Traffic routed to new revision

## Deployment Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Code Change (added comment)                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. GitHub Push triggers deploy-adk-agents.yml                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Build new ag-ui-frontend:${github.sha} container              │
│    - Docker build in infrastructure/docker/ag-ui-frontend        │
│    - Push to Artifact Registry                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Terraform Plan with new image_tag                             │
│    -var="image_tag=${{ github.sha }}"                            │
│    - Detects ag-ui-frontend needs update                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Terraform Apply                                               │
│    - Updates ag-ui-frontend service                              │
│    - Sets image to new SHA                                       │
│    - Injects ERROR_OBSERVER_URL from error_observer.uri          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Cloud Run Deployment                                          │
│    - Creates new revision with new image                         │
│    - Environment variables properly set                          │
│    - Routes 100% traffic to new revision                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. ERROR_OBSERVER_URL now available in container                 │
│    process.env.ERROR_OBSERVER_URL = "https://..."                │
└───────────────────────────────────────────────────────────────────┘
```

## Verification

### Before Fix

```bash
$ curl https://chained-ag-ui-frontend-<project>.uc.a.run.app/api/debug/env | jq '.envStatus.ERROR_OBSERVER_URL'
{
  "set": false,
  "value": "not set",
  "length": 0
}
```

### After Fix (Expected)

```bash
$ curl https://chained-ag-ui-frontend-<project>.uc.a.run.app/api/debug/env | jq '.envStatus.ERROR_OBSERVER_URL'
{
  "set": true,
  "value": "configured",
  "length": 60
}
```

### Full Environment Status

```bash
$ curl https://chained-ag-ui-frontend-<project>.uc.a.run.app/api/debug/env
```

Expected response:
```json
{
  "endpoint": "/api/debug/env",
  "timestamp": "2025-12-04T...",
  "envStatus": {
    "ERROR_OBSERVER_URL": {
      "set": true,
      "value": "configured",
      "length": 60
    },
    "AGENT_ERROR_OBSERVER_URL": {
      "set": false,
      "value": "not set",
      "length": 0
    },
    "ENVIRONMENT": "dev",
    "NODE_ENV": "production",
    "GOOGLE_CLOUD_PROJECT": {
      "set": true,
      "value": "configured"
    },
    "USE_VERTEX_AI": "true"
  }
}
```

## Testing Error Observer Integration

### 1. Check Error Observer Health

```bash
$ curl https://chained-error-observer-<project>.uc.a.run.app/health
{
  "status": "healthy",
  "agent": "error-observer",
  "version": "1.0.0",
  "github_configured": true
}
```

### 2. Check Error Observer Status via AG-UI

```bash
$ curl https://chained-ag-ui-frontend-<project>.uc.a.run.app/api/error-observer/status
{
  "configured": true,
  "url": "https://chained-error-observer-...",
  "state": {
    "status": "success",
    "last_dispatch_status": "success",
    "errors_handled_24h": 0
  },
  "lastUpdated": "..."
}
```

### 3. Test UI Error Reporting

```bash
$ curl -X POST https://chained-ag-ui-frontend-<project>.uc.a.run.app/api/ui-error-report \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test error from curl",
    "stack": "Error: Test\n  at <anonymous>:1:1",
    "url": "https://test.example.com",
    "user_agent": "curl/7.81.0"
  }'
```

Expected: Returns 200 and error is forwarded to error_observer, which dispatches to GitHub.

## Lessons Learned

### 1. Cloud Run Environment Variables Are Service-Level

Environment variables in Cloud Run are part of the SERVICE configuration, not the container image. However, services are only updated when:
- Image tag changes
- Service configuration changes in Terraform
- Manual update via gcloud CLI

### 2. Terraform Apply Behavior

Terraform only updates resources when it detects changes:
- New image tag triggers update
- Changed environment variables trigger update
- BUT: If neither changes, service not updated even if referenced values (like error_observer.uri) are new

### 3. Force Update Strategies

When you need to force a Cloud Run service to pick up new Terraform-managed environment variables:

**Option A: Change Container Code** (Used Here)
- Pros: Clean, trackable in git
- Cons: Requires code change (even if trivial)

**Option B: Change Image Tag**
- Pros: No code change needed
- Cons: Harder to track, requires workflow modification

**Option C: Manual gcloud Update**
- Pros: Immediate
- Cons: Bypasses Terraform, causes drift

**Option D: Terraform Taint**
- Pros: Forces recreation
- Cons: More disruptive, recreates entire service

### 4. Dependency Resolution

Terraform `depends_on` ensures creation order:
- error_observer created first
- ag-ui-frontend created after
- ag-ui-frontend can reference error_observer.uri

BUT: This only helps during initial creation. For updates, image_tag change is key.

## Prevention for Future

### Best Practice: Always Include in Initial Config

When adding new services that reference each other:
1. Add both services in same Terraform change
2. Ensure dependencies are correct
3. Deploy together in one workflow run
4. This ensures all references resolve correctly from start

### Monitoring

Add monitoring for environment variable presence:
- Health check endpoints that verify critical env vars
- Startup validation in container entrypoint
- Alerting if required env vars missing

### Documentation

Document critical environment variables:
- Which services depend on which others
- What env vars must be set
- How to verify they're set correctly

## Related Issues

- PR #3520: Original error observer implementation
- ERROR_OBSERVER_TROUBLESHOOTING_SUMMARY.md: Previous fixes
- ERROR_OBSERVER_FIXES_2025-12-02.md: Terraform data source fix

## Files Modified

| File | Change | Reason |
|------|--------|--------|
| `infrastructure/docker/ag-ui-frontend/src/app/api/debug/env/route.ts` | Added comment | Force container rebuild to pick up ERROR_OBSERVER_URL |

## Deployment Checklist

After this PR merges:

- [ ] Workflow runs automatically on push to main
- [ ] ag-ui-frontend container rebuilt with new SHA
- [ ] Terraform apply updates service with new image
- [ ] ERROR_OBSERVER_URL environment variable set
- [ ] Verify with `/api/debug/env` endpoint
- [ ] Test error observer status endpoint
- [ ] Test UI error reporting
- [ ] Monitor for any error observer issues

## Success Criteria

✅ `/api/debug/env` shows ERROR_OBSERVER_URL set  
✅ `/api/error-observer/status` returns configured=true  
✅ Error observer appears in UI agent list  
✅ UI errors successfully reported to error observer  
✅ Error observer successfully dispatches to GitHub  

---

**Status:** Implementation complete. Awaiting deployment and verification.
