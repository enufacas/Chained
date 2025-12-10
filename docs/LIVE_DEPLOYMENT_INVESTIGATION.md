# Live Deployment Investigation Summary

**Date**: 2025-12-10
**Investigator**: @troubleshoot-expert

## Overview

This document summarizes the investigation into the live AG-UI deployment, including URL documentation, GCP error analysis, and E2E test implementation.

## 1. Live Deployment URLs

### Primary AG-UI (Standard Interface)

**URL**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app

**Description**:
- CopilotKit-powered A2A Pipeline Visualization UI
- Clean, modern interface with cards and timelines
- Production-focused interface for real work
- 2D card-based agent display

**Use Cases**:
- Production workflows
- Detailed pipeline management
- Agent coordination monitoring
- Real-time A2A task execution

### 3D Organism Interface (Cyberpunk Visualization)

**URL**: https://chained-ag-organism-frontend-sguacxy5gq-uc.a.run.app

**Description**:
- 3D visualization of A2A agent coordination
- Cyberpunk aesthetic with dark theme and cyan/magenta colors
- Agents displayed as 3D humanoid figures using Three.js
- Real-time animation with bloom effects and post-processing
- Built with React + react-three-fiber

**Use Cases**:
- Visual exploration
- Demonstrations
- Monitoring agent coordination
- Showcasing the system

### Reference Documentation

The primary documentation for these URLs is maintained in:
- `DEPLOYED_AG_UI_URLS.md` (root level)

This document provides:
- Complete URL information
- Feature comparisons
- Architecture details
- Deployment instructions
- GCP configuration

## 2. GCP Error Analysis (Last 20 Minutes)

### Critical Error Identified

**Error Type**: Firestore Permission Denied
**Frequency**: Every 2 seconds (continuous)
**Severity**: High (impacts production functionality)

### Error Details

```
Error: 7 PERMISSION_DENIED: Missing or insufficient permissions.
```

**Location**: Pipeline API route (`/api/pipeline`)
**Operation**: Listing from persistent storage (Firestore)
**First Observed**: Multiple occurrences in the last 20 minutes

### Log Samples

```
[2025-12-10T05:16:01.344Z] [Pipeline API] [WARN] Error listing from persistent storage: 
  Error: 7 PERMISSION_DENIED: Missing or insufficient permissions.

[2025-12-10T05:15:59.300Z] [Pipeline API] [WARN] Error listing from persistent storage: 
  Error: 7 PERMISSION_DENIED: Missing or insufficient permissions.
```

### Root Cause

The Cloud Run service for AG-UI uses the service account:
- `chained-adk-agents@cogent-tine-479302-j0.iam.gserviceaccount.com`

**Current Permissions**:
- `roles/aiplatform.user` ✅
- `roles/cloudtrace.agent` ✅
- `roles/secretmanager.secretAccessor` ✅
- `roles/datastore.user` ❌ **MISSING**

**Required Permission**:
- `roles/datastore.user` - Required for Firestore read/write operations

### Impact

**What's Affected**:
- ❌ Pipeline persistence to Firestore
- ❌ Historical pipeline retrieval
- ❌ Session recovery after Cloud Run restart
- ✅ In-memory pipeline execution (still works)
- ✅ Active pipeline tracking (works until restart)

**User Experience**:
- Pipelines execute successfully
- Results are visible during active session
- Pipeline history is lost on container restart
- Error messages in logs but not user-facing

### Fix Applied

**Terraform Update**: `infrastructure/terraform/base/adk-agents.tf`

Added IAM binding:
```hcl
resource "google_project_iam_member" "adk_agents_datastore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.adk_agents.email}"
}
```

**Deployment Required**: 
This fix needs to be applied via Terraform/GitHub Actions workflow to take effect in production.

### Health Check Summary

**Overall System Health**: ✅ Healthy (9/9 agents healthy)

**Log Sample**:
```json
{
  "healthyCount": 9,
  "unhealthyCount": 0,
  "unknownCount": 0,
  "overallHealth": "healthy",
  "totalTimeMs": 1073
}
```

**Other Status**:
- Error Observer: Configured ✅
- Agent Health Checks: Passing ✅
- API Responses: Normal ✅

## 3. E2E Test Implementation

### Test Suite Created

**Location**: `tests/e2e/`

**Files**:
- `package.json` - NPM configuration
- `playwright.config.ts` - Playwright configuration
- `tsconfig.json` - TypeScript configuration
- `specs/ag-ui-live.spec.ts` - Comprehensive test suite
- `README.md` - Test documentation

### Test Coverage

1. **Homepage Load** (@quick)
   - Validates AG-UI loads and displays correctly
   - Checks for key UI elements
   - Screenshots homepage

2. **Agent Canvas Display** (@quick)
   - Verifies agent selection interface
   - Validates agent-related UI elements

3. **Multi-Agent Blog Writing** (@live)
   - Creates pipeline via POST /api/pipeline
   - Polls for completion (up to 3 minutes)
   - Verifies status progression
   - Checks results (research, trends, blog)
   - Full end-to-end workflow

4. **UI Polling Mechanism** (@live)
   - Monitors pipeline status updates
   - Verifies polling frequency
   - Tracks progress changes
   - Validates UI responsiveness

5. **Pipeline History** (@quick)
   - Lists recent pipelines
   - Verifies API responses
   - Checks pagination

6. **Multi-Agent Coordination** (@live)
   - Tests agent handoffs
   - Verifies A2A protocol steps
   - Validates multiple agents involved

7. **Error Handling** (@quick)
   - Tests 404 responses
   - Validates error messages
   - Checks graceful degradation

8. **Agent Activity** (@quick)
   - Checks real-time activity API
   - Displays agent health status

### Test Features

**Real API Calls**:
- Tests hit live deployment
- No mocking or simulation
- Real Vertex AI calls
- Actual pipeline execution
- Real blog post creation

**Comprehensive Validation**:
- ✅ UI rendering
- ✅ API functionality
- ✅ Pipeline execution
- ✅ Status updates
- ✅ Error handling
- ✅ Multi-agent coordination

**CI/CD Ready**:
- Automatic retries (2x in CI)
- Screenshot on failure
- Video recording on failure
- JSON + HTML reports
- Configurable timeouts

### Running Tests

```bash
cd tests/e2e

# Install dependencies
npm install
npx playwright install

# Run all tests
npm test

# Run live tests only
npm run test:live

# Run quick tests only
npm run test:quick

# Run with UI (interactive)
npm run test:ui

# Debug mode
npm run test:debug
```

### Test Configuration

**Base URL**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app

**Timeouts**:
- Test: 120 seconds (2 minutes)
- Action: 30 seconds
- Navigation: 60 seconds
- Pipeline completion: 180 seconds (3 minutes)

**Browsers**:
- Chromium (Desktop)
- Firefox (Desktop)
- WebKit (Safari)
- Chrome Mobile (Pixel 5)

**Tags**:
- `@live` - Real API calls, longer execution
- `@quick` - Fast validation tests

## 4. Findings and Recommendations

### Issues Identified

1. **Firestore Permission Error** (Critical)
   - Status: Fix applied in Terraform, needs deployment
   - Priority: High
   - Impact: Pipeline persistence

2. **No Playwright Tests** (Medium)
   - Status: Fixed - comprehensive suite created
   - Priority: Medium
   - Impact: Quality assurance

### Recommendations

1. **Deploy Terraform Changes**
   - Apply the IAM role update
   - Verify Firestore access works
   - Monitor logs for permission errors

2. **Run E2E Tests Regularly**
   - Integrate into CI/CD pipeline
   - Run on every deployment
   - Monitor for regressions

3. **Monitor GCP Logs**
   - Set up alerts for permission errors
   - Track error patterns
   - Monitor agent health

4. **Document Deployment Process**
   - Update runbooks
   - Document service account requirements
   - Include troubleshooting guides

## 5. Next Steps

### Immediate Actions

1. ✅ Document live URLs
2. ✅ Identify and document GCP errors
3. ✅ Create comprehensive E2E tests
4. ⏳ Deploy Terraform fix for Firestore permissions
5. ⏳ Run E2E tests against live deployment
6. ⏳ Verify fixes resolve issues

### Future Improvements

1. **Enhanced Monitoring**
   - Set up GCP alerting for errors
   - Create dashboard for service health
   - Track SLOs/SLIs

2. **Test Automation**
   - Add E2E tests to GitHub Actions
   - Schedule regular test runs
   - Alert on test failures

3. **Documentation**
   - Keep URL documentation current
   - Document known issues
   - Maintain troubleshooting guides

## 6. References

### Documentation
- [DEPLOYED_AG_UI_URLS.md](./DEPLOYED_AG_UI_URLS.md)
- [tests/e2e/README.md](./tests/e2e/README.md)
- [AG-UI Frontend README](./infrastructure/docker/ag-ui-frontend/README.md)

### Terraform
- [adk-agents.tf](./infrastructure/terraform/base/adk-agents.tf)

### GCP Resources
- Service Account: `chained-adk-agents@cogent-tine-479302-j0.iam.gserviceaccount.com`
- Project: `cogent-tine-479302-j0`
- Region: `us-central1`

### External Resources
- [A2A Protocol](https://a2a-protocol.org/)
- [Playwright Documentation](https://playwright.dev/)
- [GCP IAM Roles](https://cloud.google.com/iam/docs/understanding-roles)

---

**Investigation Complete**: 2025-12-10T05:30:00Z
