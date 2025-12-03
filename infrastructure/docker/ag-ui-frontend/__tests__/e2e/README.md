# End-to-End Test Suite for AG-UI Custom Team System

## Overview

This directory contains comprehensive end-to-end (E2E) tests for the AG-UI custom team execution system, storage management, and error handling workflows.

## Test Files

### `custom-team-e2e.test.ts`

Comprehensive E2E test suite covering:

1. **Custom Team Serial Execution** (Test 1)
   - Create custom team with 3 agents
   - Execute serially with 3 turns per agent (9 total turns)
   - Poll for status updates simulating UI behavior
   - Verify state transitions: pending → running → completed/failed
   - Validate turn progress and final state

2. **Storage Persistence and Quota Management** (Test 2)
   - Save multiple sessions to localStorage
   - Handle quota exceeded errors automatically
   - Verify automatic pruning kicks in
   - Test metadata stripping from old sessions
   - Ensure storage stays functional after quota issues

3. **Agent Failure Handling** (Test 3)
   - Create team with invalid agent ID (non-existent-agent)
   - Verify graceful error handling
   - Check failed turns have error messages
   - Validate execution continues despite failures

4. **Error Observer Integration** (Test 4)
   - Create error artifacts for failed operations
   - Store error events with A2A protocol metadata
   - Track error observer state transitions:
     - idle → ingesting → dispatching → success/failure
   - Verify error data persistence

5. **Storage Cleanup Utilities** (Test 5)
   - Monitor storage usage with `getStorageUsage()`
   - Test cleanup recommendation logic
   - Perform aggressive cleanup when needed
   - Verify storage reduction after cleanup

6. **Complete Workflow** (Test 6)
   - End-to-end test from creation to completion
   - Verify session persistence throughout execution
   - Check storage remains within limits
   - Validate API polling behavior

## Running the Tests

### Prerequisites

```bash
cd infrastructure/docker/ag-ui-frontend
npm install
```

### Run All E2E Tests

```bash
npm test -- __tests__/e2e/custom-team-e2e.test.ts
```

### Run Specific Test Suite

```bash
# Test 1: Serial Execution
npm test -- __tests__/e2e/custom-team-e2e.test.ts -t "Custom Team with Serial Execution"

# Test 2: Storage Management
npm test -- __tests__/e2e/custom-team-e2e.test.ts -t "Storage Persistence and Quota Management"

# Test 3: Error Handling
npm test -- __tests__/e2e/custom-team-e2e.test.ts -t "Agent Failure and Error Handling"

# Test 4: Error Observer
npm test -- __tests__/e2e/custom-team-e2e.test.ts -t "Error Observer Integration"

# Test 5: Storage Cleanup
npm test -- __tests__/e2e/custom-team-e2e.test.ts -t "Storage Cleanup Utilities"

# Test 6: Complete Workflow
npm test -- __tests__/e2e/custom-team-e2e.test.ts -t "Complete Workflow"
```

### Watch Mode

```bash
npm test -- __tests__/e2e/custom-team-e2e.test.ts --watch
```

## Test Architecture

### Mock Environment

The tests use a mock localStorage implementation that:
- Simulates 1MB quota limit (vs 5-10MB in real browsers)
- Throws `QuotaExceededError` when limit exceeded
- Tracks storage size for validation
- Provides `clear()` for test isolation

### Test Flow

1. **Setup**: Clear localStorage before each test
2. **Execute**: Run team API calls or storage operations
3. **Poll**: Simulate UI polling behavior
4. **Assert**: Verify expected behavior
5. **Teardown**: Automatic cleanup

### Key Assertions

- **Status Transitions**: pending → running → completed/failed
- **Turn Progress**: currentTurn increments correctly
- **Storage Limits**: Data stays within quota
- **Error Handling**: Failures don't crash system
- **Data Persistence**: Sessions survive storage operations

## Integration with Existing Tests

These E2E tests complement:
- `__tests__/api/team.test.ts` - Team API unit tests
- `__tests__/lib/storage.test.ts` - Storage utility unit tests
- `__tests__/lib/storage-cleanup.test.ts` - Cleanup utility tests
- `__tests__/api/error-observer.test.ts` - Error observer API tests

## Expected Behavior

### Successful Test Run

```
E2E: Custom Team Execution with Storage and Error Handling
  ✓ Custom Team with Serial Execution (3 turns) (5000ms)
  ✓ Storage Persistence and Quota Management
  ✓ Agent Failure and Error Handling
  ✓ Error Observer Integration
  ✓ Storage Cleanup Utilities
  ✓ Complete Workflow - Creation to Completion

Test Suites: 1 passed, 1 total
Tests:       13 passed, 13 total
```

### Failure Scenarios

The tests handle:
- Agent timeout/unavailability (continues execution)
- Storage quota exceeded (automatic pruning)
- Invalid agent IDs (graceful error handling)
- Network failures (proper error propagation)

## Debugging

### Enable Verbose Logging

Set `DEBUG=true` or check console.log output in tests:
- Turn progress: `Poll ${attempt}: Status=${status}, Turn=${current}/${total}`
- Storage size: `Storage size: ${bytes} bytes`
- Artifacts: `Artifacts created: ${count}`

### Common Issues

**Tests timeout:**
- Increase `maxPolls` or wait time in polling loops
- Check agent URLs are accessible
- Verify mock environment is set up correctly

**Quota errors not handled:**
- Check `storage.ts` has quota error handling
- Verify pruning logic is triggered
- Ensure mock localStorage throws `QuotaExceededError`

**State transitions fail:**
- Review async execution timing
- Check `activeSessions` Map is properly managed
- Verify team API status updates

## Coverage

These E2E tests cover:
- ✅ Custom team creation (POST /api/team)
- ✅ Session polling (GET /api/team?session=id)
- ✅ Serial execution mode
- ✅ 3 turns per agent configuration
- ✅ localStorage persistence
- ✅ Quota exceeded handling
- ✅ Automatic storage pruning
- ✅ Metadata stripping
- ✅ Agent failure scenarios
- ✅ Error observer integration
- ✅ Storage cleanup utilities
- ✅ Complete workflow from creation to completion

## Future Enhancements

- [ ] Add parallel execution mode tests
- [ ] Test concurrent session execution
- [ ] Add UI screenshot comparisons
- [ ] Test page reload/refresh scenarios
- [ ] Add performance benchmarks
- [ ] Test error dispatch to GitHub
- [ ] Add A2A protocol validation

## Related Documentation

- `AG_UI_STORAGE_FIX_SUMMARY.md` - Storage quota fix details
- `AG_UI_VERIFICATION_CHECKLIST.md` - Deployment verification
- `__tests__/A2A_ERROR_FLOW_TESTS.md` - Error flow test documentation
- `docs/a2a-ui/README.md` - A2A UI architecture

## Maintenance

When updating:
- Update tests when team API changes
- Adjust timeouts if agent response times change
- Update storage limits if quota handling changes
- Add new test cases for new features
