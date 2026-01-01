# Error Observer - Quick Start Guide

## Problem

The error observer shows "Not configured (ERROR_OBSERVER_URL not set)" on the deployed site.

## Solution

We've added two new features to help diagnose and test the error observer:

### 1. Test Dispatch Button 🧪

**Where**: In the "Error Observer" section of the AG-UI Frontend

**What it does**:
- Sends a test error to verify the error observer is working
- Shows immediate feedback (success or failure)
- Auto-refreshes status after dispatch

**How to use**:
1. Go to https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/
2. Scroll to "Error Observer" section
3. Click "Send Test Error" button
4. Watch for success/failure message

**Expected Result**:
```
✓ Test error dispatched successfully! Hash: abc123...
```

### 2. Environment Debug Endpoint 🔍

**Where**: `/api/debug/env`

**What it does**:
- Shows whether ERROR_OBSERVER_URL is set
- Returns environment variable status
- Provides troubleshooting recommendations

**How to use**:
Visit: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/debug/env

**Expected Result**:
```json
{
  "envStatus": {
    "ERROR_OBSERVER_URL": {
      "set": true,
      "value": "configured",
      "length": 75
    }
  }
}
```

## Troubleshooting

### If ERROR_OBSERVER_URL is "not set"

1. Check that error_observer service is deployed:
   ```bash
   gcloud run services list | grep error-observer
   ```

2. Redeploy ag-ui-frontend:
   ```bash
   cd infrastructure/terraform
   terraform apply -target=google_cloud_run_v2_service.ag_ui_frontend
   ```

3. Wait 2-3 minutes for deployment to complete

4. Refresh the page and check again

### If Test Dispatch Fails

1. Check error observer service is running:
   ```bash
   curl https://chained-error-observer-XXXX.a.run.app/health
   ```

2. Check Cloud Run logs:
   ```bash
   gcloud logging read "resource.labels.service_name=chained-error-observer" --limit 10
   ```

3. Verify Terraform configuration:
   - File: `infrastructure/terraform/adk-agents.tf`
   - Line 1157-1159: `ERROR_OBSERVER_URL = google_cloud_run_v2_service.error_observer.uri`

## What Happens When You Click "Send Test Error"

1. Frontend sends POST to `/api/ui-error-report` with test data
2. Backend creates error_event payload
3. Backend sends A2A task to error_observer at `ERROR_OBSERVER_URL/a2a/tasks`
4. Error observer processes the error
5. Error observer forwards to GitHub (creates issue or comment)
6. UI shows success/failure result

## Success Indicators

✅ Error Observer shows "configured" status
✅ Test dispatch succeeds with hash
✅ Error appears in error observer logs
✅ GitHub issue is created (check repository issues)

## Links

- **Deployed Site**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/
- **Debug Endpoint**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/debug/env
- **Documentation**: ERROR_OBSERVER_FIX_IMPLEMENTATION.md
- **Terraform Config**: infrastructure/terraform/adk-agents.tf

## Next Steps After Verification

Once the error observer is working:
1. ✅ Real errors from agents will be captured
2. ✅ Errors will be dispatched to GitHub issues
3. ✅ Copilot can automatically fix errors
4. ✅ Error observer status will show activity
5. ✅ Recent errors will be visible in expanded view

## Support

If issues persist:
1. Check ERROR_OBSERVER_FIX_IMPLEMENTATION.md for detailed troubleshooting
2. Review Cloud Run logs for both services
3. Verify Terraform state matches expected configuration
4. Check GitHub repository issues for dispatched errors
