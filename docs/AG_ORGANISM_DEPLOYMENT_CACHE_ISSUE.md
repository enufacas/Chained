# AG-Organism Frontend Deployment Cache Issue - Root Cause Analysis

## Problem Summary

The AG-Organism frontend at `https://chained-ag-organism-frontend-sguacxy5gq-uc.a.run.app/` was displaying 404 errors and not showing the fixes from recent PRs, despite the Docker image being rebuilt and pushed successfully.

## Root Cause

**The Terraform workflow was NOT deploying the ag-organism-frontend service** because it was missing from the `-target` list in the `Terraform Plan` step.

### Evidence

1. **Docker Image Built Successfully** (Run #85, Job 57317281864):
   ```
   ✅ AG-Organism Frontend built and pushed
   Image: us-central1-docker.pkg.dev/.../ag-organism-frontend:f2d0017...
   SHA: 356a490ee17d50fa9b8fc4dcb2955a49ca29170af6213e5a9ecf2f1dbda2ee9c
   ```

2. **Current Deployed Revision Using Old Image**:
   ```bash
   $ gcloud run revisions list --service=chained-ag-organism-frontend
   NAME: chained-ag-organism-frontend-00001-zm8
   IMAGE: ...@sha256:fe4957ad21745ff...  # OLD IMAGE from Run #83
   ```

3. **Terraform Plan Missing Target**:
   ```yaml
   # .github/workflows/deploy-adk-agents.yml
   - name: Terraform Plan
     run: |
       terraform plan \
         -target=google_cloud_run_v2_service.adk_api_server \
         -target=google_cloud_run_v2_service.ag_ui_frontend \
         # ❌ MISSING: -target=google_cloud_run_v2_service.ag_organism_frontend
         -target=google_cloud_run_v2_service.error_observer \
         ...
   ```

## Timeline of Events

### 2025-12-06 05:35 - Run #83: Initial Deployment
- **PR #3634**: "Host AG-Organism visualization on Cloud Run"
- Built Docker image: `fe4957ad...` (OLD)
- Deployed to Cloud Run successfully
- **Issue**: Three.js files not accessible (CDN blocked)

### 2025-12-06 06:17 - Run #84: Three.js Fix
- **PR #3636**: "Bundle Three.js locally and add error logging"
- Built Docker image: `(new image SHA)`
- **PROBLEM**: Terraform didn't deploy it! (ag-organism-frontend missing from targets)
- Service still running OLD image `fe4957ad...`

### 2025-12-06 06:49 - Run #85: Added to Workflow
- **PR #3638**: "Fix: ag-organism-frontend not deployed by Terraform workflow"
- Added ag-organism-frontend to build jobs dependency list
- Built Docker image: `356a490ee...` (NEW)
- **PROBLEM**: Still missing from Terraform Plan `-target` list!
- Service STILL running OLD image `fe4957ad...`

## Why This Happened

The PR #3638 fixed part of the problem by adding ag-organism-frontend to the workflow **build dependencies**, but **did NOT add it to the Terraform deployment targets**.

### What PR #3638 Fixed

✅ Added to build job dependencies:
```yaml
deploy-terraform:
  needs: [..., build-ag-organism-frontend]  # ✅ FIXED
```

❌ **DID NOT** add to Terraform targets:
```yaml
terraform plan \
  -target=google_cloud_run_v2_service.ag_organism_frontend  # ❌ MISSING
```

## The Fix

Add two missing `-target` lines to the Terraform Plan step in `.github/workflows/deploy-adk-agents.yml`:

```yaml
- name: Terraform Plan
  run: |
    terraform plan \
      # ... other targets ...
      -target=google_cloud_run_v2_service.ag_organism_frontend \  # ✅ ADD THIS
      # ... other IAM targets ...
      -target=google_cloud_run_v2_service_iam_member.ag_organism_frontend_public \  # ✅ ADD THIS
      -out=tfplan
```

Also add URL output:
```yaml
- name: Get service URLs
  run: |
    echo "ag_organism_frontend_url=$(terraform output -raw ag_organism_frontend_url 2>/dev/null || echo '')" >> $GITHUB_OUTPUT
```

## Impact

Without this fix:
- ❌ Docker images rebuilt but never deployed
- ❌ Three.js bundling fix (PR #3636) never reached production
- ❌ Home button fix (this PR) won't reach production
- ❌ Favicon fix (this PR) won't reach production
- ❌ Service stuck on old image from run #83

With this fix:
- ✅ New Docker images will be deployed to Cloud Run
- ✅ All pending fixes will go live
- ✅ Service will use latest code

## Verification After Fix

After this PR merges and workflow runs:

1. **Check deployed image SHA**:
   ```bash
   gcloud run revisions list --service=chained-ag-organism-frontend --region=us-central1
   # Should show NEW image SHA from latest build
   ```

2. **Verify Three.js accessible**:
   ```bash
   curl -I https://chained-ag-organism-frontend-sguacxy5gq-uc.a.run.app/vendor/three/build/three.module.js
   # Should return HTTP 200
   ```

3. **Check home button**:
   - Open browser dev tools
   - Inspect home button element
   - Should have `href` set to AG-UI frontend URL

4. **Check favicon**:
   - Look at browser tab
   - Should see robot emoji 🤖

## Lessons Learned

1. **Complete Deployment Configuration**: When adding a new service, check ALL places it needs to be referenced:
   - Docker build job ✅
   - Build dependencies ✅
   - Terraform `-target` list ❌ (was missing)
   - URL outputs ❌ (was missing)
   - Summary display (optional)

2. **Verify Deployment**: After workflow succeeds, check that:
   - New revision was created
   - Image SHA matches what was built
   - Service is actually using the new code

3. **Targeted Deployment Complexity**: Using `-target` in Terraform requires maintaining an explicit list of all resources to deploy. This is error-prone when adding new services.

## Alternative Solutions (Future)

Consider these alternatives to prevent similar issues:

1. **Remove `-target` usage**: Deploy all Terraform resources on every run
   - Pros: Never miss a service
   - Cons: Slower deployments, may touch unrelated resources

2. **Dynamic target generation**: Generate `-target` list from Terraform code
   ```bash
   TARGETS=$(terraform state list | grep 'google_cloud_run_v2_service\.' | sed 's/^/-target=/')
   terraform plan $TARGETS -out=tfplan
   ```

3. **Service registry**: Maintain a single list of services used by both:
   - Build job dependencies
   - Terraform targets
   - URL outputs

## Related PRs

- **PR #3634**: Initial AG-Organism Cloud Run deployment
- **PR #3636**: Bundle Three.js locally (never deployed)
- **PR #3638**: Add to workflow dependencies (incomplete fix)
- **This PR**: Complete the fix by adding Terraform targets

## Files Changed

**This PR:**
- `.github/workflows/deploy-adk-agents.yml`:
  - Added `-target=google_cloud_run_v2_service.ag_organism_frontend`
  - Added `-target=google_cloud_run_v2_service_iam_member.ag_organism_frontend_public`
  - Added `ag_organism_frontend_url` to outputs
- `infrastructure/docker/ag-organism-frontend/public/ag-organism.html`:
  - Fixed home button link
  - Fixed favicon with URL-encoded SVG
  - Added fallback for missing AG_UI_FRONTEND_URL
- `infrastructure/docker/ag-organism-frontend/public/assets/.gitkeep`:
  - Created assets directory
