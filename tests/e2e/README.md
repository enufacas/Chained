# AG-UI End-to-End Tests

Comprehensive Playwright tests for the live deployed AG-UI at:
**https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app**

## Overview

These tests validate the complete AG-UI pipeline execution against the live deployment:

- ✅ Multi-agent blog writing workflow
- ✅ Real Vertex AI API calls (no mocking)
- ✅ UI polling and update mechanisms
- ✅ Pipeline completion and result display
- ✅ Error handling
- ✅ Agent coordination

## Quick Start

### Install Dependencies

```bash
cd tests/e2e
npm install
npx playwright install  # Install browsers
```

### Run Tests

```bash
# Run all tests
npm test

# Run with UI (watch mode)
npm run test:ui

# Run in headed mode (see browser)
npm run test:headed

# Run live tests only
npm run test:live

# Run quick tests only
npm run test:quick

# Debug mode
npm run test:debug
```

## Test Structure

### `specs/ag-ui-live.spec.ts`

Comprehensive end-to-end test suite covering:

1. **Homepage Load** (@quick)
   - Verifies AG-UI loads correctly
   - Checks for key UI elements

2. **Agent Canvas Display** (@quick)
   - Validates agent selection interface
   - Screenshots agent display

3. **Multi-Agent Blog Writing** (@live)
   - Creates pipeline via API
   - Waits for completion (up to 3 minutes)
   - Verifies results (research, trends, blog post)
   - Tests full workflow end-to-end

4. **UI Polling** (@live)
   - Monitors pipeline status updates
   - Verifies UI polling mechanism
   - Tracks progress changes

5. **Pipeline History** (@quick)
   - Lists recent pipelines
   - Verifies API responses

6. **Multi-Agent Coordination** (@live)
   - Tests agent handoffs
   - Verifies A2A protocol steps
   - Checks multiple agents involved

7. **Error Handling** (@quick)
   - Tests 404 responses
   - Validates error messages

8. **Agent Activity** (@quick)
   - Checks real-time activity API
   - Displays agent health status

## Environment Variables

```bash
# Override default URL
export AG_UI_URL=https://your-custom-url.run.app

# For CI/CD
export CI=true  # Enables retries and single worker
```

## Test Tags

- `@live` - Tests that make real API calls and may take longer
- `@quick` - Fast tests that verify basic functionality

## Screenshots

Tests automatically capture screenshots on failure:
- `test-results/ag-ui-homepage.png`
- `test-results/pipeline-started.png`
- `test-results/pipeline-completed.png`
- `test-results/final-state.png`
- etc.

## CI/CD Integration

Tests are configured for CI with:
- 2 retries on failure
- Single worker (sequential execution)
- JSON + HTML reports
- Automatic screenshot/video capture on failure

## Debugging

```bash
# Run with Playwright Inspector
npm run test:debug

# View test report
npx playwright show-report

# Run specific test
npx playwright test --grep "should load AG-UI homepage"
```

## Notes

### Real API Calls

These tests use REAL Vertex AI API calls. They:
- Hit the live AG-UI deployment
- Execute actual A2A agent pipelines
- Create real blog posts in GCP
- May incur API costs

### Timeouts

- Test timeout: 2 minutes
- Action timeout: 30 seconds
- Navigation timeout: 1 minute
- Pipeline completion: up to 3 minutes

### Known Issues

1. **Firestore Permission Error**: The AG-UI service account needs `roles/datastore.user` permission to persist pipeline data. This has been fixed in Terraform but needs deployment.

2. **Polling Delay**: UI updates every 2 seconds via API polling. Tests account for this delay.

3. **Agent Availability**: Tests assume all agents (academic-research, google-trends, blog-writer) are deployed and healthy.

## Troubleshooting

### Test Failures

1. **Navigation Timeout**
   - Check if AG-UI is deployed and accessible
   - Verify URL in config

2. **Pipeline Timeout**
   - Agents may be cold starting (first request takes longer)
   - Increase timeout if needed
   - Check agent logs in GCP

3. **API Errors**
   - Verify service account permissions
   - Check Cloud Run logs for errors

### Viewing Logs

```bash
# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=chained-ag-ui-frontend" \
  --limit=50 --format=json

# Check for errors
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=chained-ag-ui-frontend \
  AND severity>=ERROR" \
  --limit=20
```

## Related Documentation

- [AG-UI Frontend README](../../infrastructure/docker/ag-ui-frontend/README.md)
- [Deployed URLs](../../DEPLOYED_AG_UI_URLS.md)
- [A2A Protocol](https://a2a-protocol.org/)
- [Playwright Docs](https://playwright.dev/)

## Contributing

When adding new tests:
1. Use descriptive test names
2. Add appropriate tags (@live or @quick)
3. Include console.log statements for debugging
4. Capture screenshots at key points
5. Handle timeouts gracefully
6. Test both success and error paths
