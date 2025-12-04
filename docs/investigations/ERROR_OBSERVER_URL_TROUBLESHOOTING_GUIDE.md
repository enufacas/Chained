# ERROR_OBSERVER_URL Troubleshooting Guide

**Date:** 2025-12-04  
**Issue:** ERROR_OBSERVER_URL environment variable shows as "not set" in deployed ag-ui-frontend  
**Status:** Investigating

## Problem Statement

The AG-UI Frontend debug endpoint shows ERROR_OBSERVER_URL is not set:

```json
{
  "ERROR_OBSERVER_URL": {"set": false, "value": "not set", "length": 0}
}
```

However, the Terraform configuration clearly sets it on line 1157-1159 of `infrastructure/terraform/adk-agents.tf`:

```terraform
env {
  name  = "ERROR_OBSERVER_URL"
  value = google_cloud_run_v2_service.error_observer.uri
}
```

## Why Rebuilds Aren't Enough

### Evidence Rebuilds Have Occurred

Commit history shows:
- **Dec 3, 2025** - PR #3554: Fixed dependencies
- **Dec 3, 2025** - PR #3558: Fixed ERROR_OBSERVER_URL runtime config
- **Dec 3, 2025** - Multiple ag-ui-frontend code changes triggering rebuilds
- **Dec 4, 2025** - Issue still persists

**Conclusion:** The problem is NOT lack of rebuilds. Containers have been rebuilt and redeployed multiple times.

### The Real Issue

The environment variable is being set by Terraform, BUT the value being set is likely:
1. **Empty string** - error_observer.uri evaluates to ""
2. **Stale value** - Old deployment URL before error_observer was created
3. **Not propagating** - Cloud Run service config has it but container doesn't receive it

## Diagnostic Steps

### Step 1: Check Actual Cloud Run Configuration

```bash
# Check ag-ui-frontend environment variables
gcloud run services describe chained-ag-ui-frontend \
  --region=us-central1 \
  --project=chained-ai \
  --format='json' | jq '.spec.template.spec.containers[0].env[] | select(.name=="ERROR_OBSERVER_URL")'
```

**Expected output:**
```json
{
  "name": "ERROR_OBSERVER_URL",
  "value": "https://chained-error-observer-...-uc.a.run.app"
}
```

**If empty/missing:** Terraform isn't setting the variable correctly.

### Step 2: Verify Error Observer Service Exists

```bash
# Get error observer URL
gcloud run services describe chained-error-observer \
  --region=us-central1 \
  --project=chained-ai \
  --format='value(status.url)'
```

**Expected output:**
```
https://chained-error-observer-<hash>-uc.a.run.app
```

**If error:** error_observer service doesn't exist or isn't deployed.

### Step 3: Check Terraform State

```bash
cd infrastructure/terraform

# Initialize if needed
terraform init

# Check error_observer URI in state
terraform state show google_cloud_run_v2_service.error_observer | grep uri

# Check ag_ui_frontend env vars in state  
terraform state show google_cloud_run_v2_service.ag_ui_frontend | grep -A 5 ERROR_OBSERVER_URL
```

**What to look for:**
- error_observer.uri should have a value
- ag_ui_frontend should reference that value in env block

### Step 4: Check Terraform Plan

```bash
cd infrastructure/terraform

# Run plan to see what would change
terraform plan \
  -var="project_id=chained-ai" \
  -var="region=us-central1" \
  -var="environment=dev" \
  -var="image_tag=latest" \
  -target=google_cloud_run_v2_service.ag_ui_frontend \
  -target=google_cloud_run_v2_service.error_observer
```

**What to look for:**
- If plan shows changes to ERROR_OBSERVER_URL, Terraform state is stale
- If plan shows "No changes", state matches config but deployment might be wrong

## Common Issues and Fixes

### Issue 1: Terraform State Drift

**Symptom:** `terraform plan` shows no changes but Cloud Run service is missing ERROR_OBSERVER_URL

**Cause:** Cloud Run service was manually modified or Terraform apply partially failed

**Fix:**
```bash
cd infrastructure/terraform

# Force Terraform to recreate the service
terraform taint google_cloud_run_v2_service.ag_ui_frontend

# Apply with explicit image tag to force update
terraform apply \
  -var="project_id=chained-ai" \
  -var="region=us-central1" \
  -var="environment=dev" \
  -var="image_tag=$(git rev-parse HEAD)" \
  -target=google_cloud_run_v2_service.ag_ui_frontend
```

### Issue 2: Error Observer Deployed After AG-UI

**Symptom:** error_observer.uri is empty in Terraform state

**Cause:** ag_ui_frontend was deployed before error_observer existed

**Fix:**
```bash
cd infrastructure/terraform

# Deploy error_observer first
terraform apply \
  -var="project_id=chained-ai" \
  -var="region=us-central1" \
  -var="environment=dev" \
  -var="image_tag=$(git rev-parse HEAD)" \
  -target=google_cloud_run_v2_service.error_observer

# Then deploy ag_ui_frontend
terraform apply \
  -var="project_id=chained-ai" \
  -var="region=us-central1" \
  -var="environment=dev" \
  -var="image_tag=$(git rev-parse HEAD)" \
  -target=google_cloud_run_v2_service.ag_ui_frontend
```

### Issue 3: Cloud Run Not Picking Up Env Var Changes

**Symptom:** Terraform state is correct but running container doesn't have the variable

**Cause:** Cloud Run is serving an old revision

**Fix:**
```bash
# Force a new revision by updating a different env var
gcloud run services update chained-ag-ui-frontend \
  --region=us-central1 \
  --project=chained-ai \
  --set-env-vars="FORCE_UPDATE=$(date +%s)"

# Or manually set ERROR_OBSERVER_URL
ERROR_OBSERVER_URL=$(gcloud run services describe chained-error-observer \
  --region=us-central1 \
  --project=chained-ai \
  --format='value(status.url)')

gcloud run services update chained-ag-ui-frontend \
  --region=us-central1 \
  --project=chained-ai \
  --set-env-vars="ERROR_OBSERVER_URL=$ERROR_OBSERVER_URL"
```

### Issue 4: Next.js Build-Time vs Runtime

**Symptom:** Variable is set in Cloud Run but Next.js can't read it

**Cause:** Next.js might be caching environment variables at build time

**Fix:** Verify the API route is using `process.env` at runtime:

```typescript
// ✅ CORRECT - reads at runtime
export async function GET() {
  const ERROR_OBSERVER_URL = process.env.ERROR_OBSERVER_URL || "";
  // ...
}

// ❌ WRONG - reads at build time
const ERROR_OBSERVER_URL = process.env.ERROR_OBSERVER_URL || "";
export async function GET() {
  // ...
}
```

Our code is correct - all API routes read `process.env` inside the handler.

## Verification After Fix

### 1. Check Environment Variable is Set

```bash
curl https://chained-ag-ui-frontend-<hash>-uc.a.run.app/api/debug/env | jq '.envStatus.ERROR_OBSERVER_URL'
```

**Expected:**
```json
{
  "set": true,
  "value": "configured",
  "length": 65
}
```

### 2. Check Error Observer Status

```bash
curl https://chained-ag-ui-frontend-<hash>-uc.a.run.app/api/error-observer/status | jq
```

**Expected:**
```json
{
  "configured": true,
  "url": "https://chained-error-observer-...",
  "state": {
    "status": "success",
    ...
  }
}
```

### 3. Test Error Reporting

```bash
curl -X POST https://chained-ag-ui-frontend-<hash>-uc.a.run.app/api/ui-error-report \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test error",
    "stack": "Error: Test\n  at test:1:1"
  }'
```

**Expected:** Returns 200 and error is forwarded to error_observer.

## Root Cause Determination

After running diagnostics, the root cause will be one of:

1. **Terraform state issue** - State doesn't match reality
2. **Deployment order issue** - error_observer wasn't created when ag_ui_frontend deployed
3. **Cloud Run caching issue** - Old revision being served
4. **Value resolution issue** - error_observer.uri evaluates to empty string

## Prevention

### Best Practices

1. **Always deploy services in order:**
   - Deploy error_observer first
   - Then deploy services that depend on it

2. **Use explicit dependencies:**
   - Already done: ag_ui_frontend `depends_on` includes error_observer

3. **Verify after every deployment:**
   - Check /api/debug/env endpoint
   - Ensure all required env vars are set

4. **Use Terraform outputs:**
   - Consider outputting error_observer.uri
   - Reference outputs instead of .uri directly

### Monitoring

Add alerts for missing environment variables:
- Health check that verifies ERROR_OBSERVER_URL is set
- Startup script that logs all env vars
- Automated test after deployment

## Related Documentation

- `ERROR_OBSERVER_URL_NOT_SET_FIX.md` - Initial investigation
- `ERROR_OBSERVER_FIXES_2025-12-02.md` - Previous fixes
- `ERROR_OBSERVER_TROUBLESHOOTING_SUMMARY.md` - GitHub API issues
- `infrastructure/terraform/adk-agents.tf` - Terraform configuration

## Conclusion

**The issue is NOT:**
- ❌ Lack of code changes
- ❌ Missing dependencies
- ❌ Need for rebuilds

**The issue IS:**
- ❓ Terraform state/deployment issue
- ❓ Cloud Run not applying env var updates
- ❓ error_observer.uri resolving incorrectly

**Next Action:** Run diagnostic steps above to identify the actual root cause.
