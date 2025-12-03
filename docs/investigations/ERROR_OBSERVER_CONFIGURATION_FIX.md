# Error Observer Configuration Fix

**Date:** 2025-12-03  
**Issue:** AG-UI live site shows "Error Observer - Not configured (ERROR_OBSERVER_URL not set)"  
**Status:** ✅ Fixed

## Problem Statement

The AG-UI frontend on the live site (https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app) was displaying:

```
Error Observer
Not configured (ERROR_OBSERVER_URL not set)
```

This indicated that the `ERROR_OBSERVER_URL` environment variable was not being set correctly in the deployed Cloud Run service.

## Root Cause Analysis

### Investigation Steps

1. **Checked `.env.example`**: ERROR_OBSERVER_URL was missing from the local development environment example
2. **Checked Terraform configuration**: ERROR_OBSERVER_URL WAS configured in `infrastructure/terraform/adk-agents.tf` at line 1157
3. **Checked deployment history**: PR #3546 added ERROR_OBSERVER_URL to ag-ui-frontend on 2025-12-02
4. **Checked Terraform dependencies**: **FOUND THE ISSUE**

### Root Cause

The `ag_ui_frontend` Cloud Run service in Terraform:

**Referenced these services:**
```terraform
env {
  name  = "ERROR_OBSERVER_URL"
  value = google_cloud_run_v2_service.error_observer.uri  # Line 1158
}

env {
  name  = "AGENT_LOG_CONSUMER_URL"
  value = google_cloud_run_v2_service.log_consumer.uri  # Line 1164
}
```

**But didn't depend on them:**
```terraform
depends_on = [
  google_project_service.required_apis,
  google_cloud_run_v2_service.adk_api_server,
  google_cloud_run_v2_service.academic_research,
  google_cloud_run_v2_service.blog_writer,
  google_cloud_run_v2_service.google_trends,
  google_cloud_run_v2_service.code_reviewer,
  google_cloud_run_v2_service.data_analyst,
  google_cloud_run_v2_service.image_generator,
  # ❌ MISSING: google_cloud_run_v2_service.error_observer
  # ❌ MISSING: google_cloud_run_v2_service.log_consumer
]
```

### Why This Caused the Issue

Terraform's dependency resolution:
1. Without explicit `depends_on`, Terraform might deploy `ag_ui_frontend` before `error_observer` is created
2. When `ag_ui_frontend` deploys and tries to reference `google_cloud_run_v2_service.error_observer.uri`, the value might be:
   - Empty string
   - Not yet available
   - Result in deployment error (but service still deploys)
3. The deployed service ends up with `ERROR_OBSERVER_URL=""` (empty)
4. The UI code checks `if (!ERROR_OBSERVER_URL)` and shows "Not configured"

## Solution

### Changes Made

#### 1. Documentation (For Local Development)

**File:** `infrastructure/docker/ag-ui-frontend/.env.example`

Added:
```env
# =============================================================================
# Error Observer & Monitoring (Required for error tracking and activity display)
# =============================================================================

# Error Observer URL for UI error reporting and real-time status monitoring
# This agent receives error events and dispatches them to GitHub for triage
ERROR_OBSERVER_URL=https://chained-error-observer-sguacxy5gq-uc.a.run.app

# Log Consumer URL for agent activity monitoring (optional)
AGENT_LOG_CONSUMER_URL=https://chained-log-consumer-sguacxy5gq-uc.a.run.app
```

**File:** `infrastructure/docker/ag-ui-frontend/README.md`

Updated environment variables section to include ERROR_OBSERVER_URL.

#### 2. Terraform Fix (For Production Deployment)

**File:** `infrastructure/terraform/adk-agents.tf`

Added missing dependencies:
```terraform
depends_on = [
  google_project_service.required_apis,
  google_cloud_run_v2_service.adk_api_server,
  google_cloud_run_v2_service.academic_research,
  google_cloud_run_v2_service.blog_writer,
  google_cloud_run_v2_service.google_trends,
  google_cloud_run_v2_service.code_reviewer,
  google_cloud_run_v2_service.data_analyst,
  google_cloud_run_v2_service.image_generator,
  google_cloud_run_v2_service.error_observer,      # ✅ ADDED
  google_cloud_run_v2_service.log_consumer,        # ✅ ADDED
]
```

## Deployment Process

### What Happens When This PR Merges

1. **Automated Workflow Trigger**: `deploy-adk-agents.yml` workflow runs automatically on push to main with changes to:
   - `infrastructure/terraform/adk-agents.tf`
   - `infrastructure/docker/ag-ui-frontend/**`

2. **Terraform Apply**: 
   - Terraform detects the dependency change
   - Will update `ag_ui_frontend` service
   - Ensures `error_observer` and `log_consumer` exist first
   - Redeploys `ag_ui_frontend` with correct environment variables

3. **Result**:
   - ERROR_OBSERVER_URL will have correct value: `https://chained-error-observer-sguacxy5gq-uc.a.run.app`
   - UI will show Error Observer status correctly
   - Real-time error monitoring will work

## Verification Steps

After deployment, verify the fix:

### 1. Check Live Site
Visit: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/history

The Error Observer section should show:
- ✅ Status indicator (idle/success/etc)
- ✅ Real-time status updates
- ✅ 24h error count
- ❌ NOT "Not configured (ERROR_OBSERVER_URL not set)"

### 2. Check Cloud Run Environment Variables
```bash
gcloud run services describe chained-ag-ui-frontend \
  --region us-central1 \
  --format='value(spec.template.spec.containers[0].env)'
```

Should include:
```
ERROR_OBSERVER_URL=https://chained-error-observer-sguacxy5gq-uc.a.run.app
```

### 3. Check Error Observer API
```bash
curl https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/error-observer/status
```

Should return:
```json
{
  "configured": true,
  "url": "https://chained-error-observer-sguacxy5gq-uc.a.run.app",
  "state": { ... },
  "lastUpdated": "2025-12-03T..."
}
```

## Related Issues

- PR #3546: Added ERROR_OBSERVER_URL to ag-ui-frontend initially
- PR #3548: Fixed error-observer GitHub dispatch issues
- PR #3550: Fixed localStorage quota and error observer status display

## Lessons Learned

### Terraform Best Practices

1. **Always add explicit dependencies when referencing other resources**
   - Even if Terraform might infer the dependency
   - Makes deployment order explicit and predictable

2. **Check `depends_on` when adding environment variables**
   - If env var references another resource, add that resource to `depends_on`
   - Prevents race conditions and empty values

3. **Document environment variables in both places**
   - `.env.example` for local development
   - Terraform for production deployment

### Testing Checklist for Similar Issues

When adding new inter-service references:
- [ ] Environment variable is set in Terraform
- [ ] Referenced service is in `depends_on` list
- [ ] Environment variable is in `.env.example`
- [ ] README documents the variable
- [ ] Deployment workflow includes the service

## References

- **Terraform File**: `infrastructure/terraform/adk-agents.tf`
- **Environment Example**: `infrastructure/docker/ag-ui-frontend/.env.example`
- **Deployment Workflow**: `.github/workflows/deploy-adk-agents.yml`
- **Error Observer Status Component**: `infrastructure/docker/ag-ui-frontend/src/components/ErrorObserverStatus.tsx`
- **Status API Route**: `infrastructure/docker/ag-ui-frontend/src/app/api/error-observer/status/route.ts`
