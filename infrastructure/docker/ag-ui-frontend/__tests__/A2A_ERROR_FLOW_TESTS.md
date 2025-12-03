# A2A Error Flow Validation Tests

## Overview

This document describes the test suite for validating the A2A (Agent-to-Agent) error handling flow, including the error-observer agent integration and localStorage quota management.

## Test Coverage

### 1. Error Observer API Tests (`__tests__/api/error-observer.test.ts`)

**Purpose**: Validate the error-observer status endpoint and integration.

#### Test Cases:

1. **Configuration Detection**
   - ✅ Returns `configured: false` when `ERROR_OBSERVER_URL` not set
   - ✅ Returns `configured: true` when URL is set
   - ✅ Fallback to `AGENT_ERROR_OBSERVER_URL` if primary not set

2. **Error Handling**
   - ✅ Handles fetch timeout gracefully
   - ✅ Handles non-OK HTTP responses (503, etc.)
   - ✅ Returns error state with details

3. **State Reporting**
   - ✅ Includes error observer state when available
   - ✅ Shows success state with dispatch metrics
   - ✅ Shows failure state with error details
   - ✅ Tracks recent errors (last 10)

4. **GitHub API Integration**
   - ✅ Detects GitHub API 422 errors (property limit)
   - ✅ Validates dispatch failure messages

### 2. Storage Utility Tests (`__tests__/lib/storage.test.ts`)

**Purpose**: Validate localStorage persistence with quota handling.

#### Test Cases:

1. **Basic Storage Operations**
   - ✅ Save and retrieve artifacts
   - ✅ Save and retrieve sessions
   - ✅ Limit artifacts to MAX_ARTIFACTS (100)
   - ✅ Limit sessions to MAX_SESSIONS (50)

2. **Quota Management**
   - ✅ Handle QuotaExceededError by pruning old artifacts
   - ✅ Handle QuotaExceededError by pruning old sessions
   - ✅ Automatic cleanup when approaching limit
   - ✅ Aggressive fallback pruning on quota errors

3. **Storage Statistics**
   - ✅ Calculate storage size correctly
   - ✅ Show size in appropriate units (B, KB, MB)
   - ✅ Track artifact and session counts

4. **A2A Error Flow States**
   - ✅ Store error artifacts from error flow
   - ✅ Track error handling workflow sessions
   - ✅ Handle multiple error states in session
   - ✅ Store error dispatch results
   - ✅ Track error observer state transitions (idle → ingesting → dispatching → success/failure)

### 3. Error Event Model Tests (`test_error_observer.py`)

**Purpose**: Validate error event creation and GitHub payload formatting.

#### Test Cases:

1. **Error Event Creation**
   - ✅ Create from Python exception
   - ✅ Create from UI error report
   - ✅ Create from Cloud Run log entry

2. **GitHub Payload Validation** ⚠️ **Critical Fix Validated**
   - ✅ Payload has exactly 10 fields (GitHub API limit)
   - ✅ Includes essential fields for triage
   - ✅ Excludes non-essential fields (metadata, logs, region)
   - ✅ Prevents 422 "too many properties" error

3. **Data Conversion**
   - ✅ Convert to A2A artifact format
   - ✅ Error hash consistency for deduplication

## Test Execution

### Python Tests
```bash
cd infrastructure/docker/adk-agents
python test_error_observer.py
```

**Expected Output**: All 6 tests pass, including the critical GitHub payload 10-field limit test.

### TypeScript Tests
```bash
cd infrastructure/docker/ag-ui-frontend
npm install
npm test -- --testPathPattern="error-observer|storage"
```

**Expected Output**: All tests pass for error-observer API and storage utilities.

## Critical Bug Fixes Validated

### Issue #1: GitHub Dispatch 422 Error ✅ FIXED

**Problem**: Error-observer was sending 15 fields in GitHub dispatch payload, exceeding the 10-property limit.

**Fix**: `error_event.py` `to_github_payload()` now returns only 10 most important fields:
- `service`, `error_message`, `error_hash`, `stack_trace`
- `first_seen`, `last_seen`, `occurrences`, `source_agent`
- `a2a_ui_url`, `environment`

**Validation**: Test `test_error_event_to_github_payload()` now validates:
- Payload has ≤ 10 fields
- Essential fields are included
- Non-essential fields are excluded

### Issue #2: UI Shows Only 4 Agents ✅ FIXED

**Problem**: `CompactAgentStatus` component had `.slice(0, 4)` limiting display to 4 agents.

**Fix**: Removed slice limit, added scrollable container for all 9 agents.

**Validation**: Manual testing shows all agents visible when dropdown expanded.

### Issue #3: localStorage Quota Exceeded ✅ FIXED

**Problem**: AG-UI accumulating data without cleanup, hitting 5-10MB localStorage limit.

**Fix**: `storage.ts` now includes:
- 4MB storage limit with 3MB warning threshold
- Automatic pruning before saves
- Aggressive fallback when quota exceeded
- Size monitoring and cleanup logic

**Validation**: Tests simulate quota errors and verify automatic cleanup behavior.

## A2A Error Flow States

The error handling workflow follows these states:

1. **Error Occurs** → Error event created in agent/UI
2. **Error Reported** → Sent to error-observer via A2A
3. **Idle** → Error-observer waiting for errors
4. **Ingesting** → Processing incoming error event
5. **Dispatching** → Forwarding to GitHub via repository_dispatch
6. **Success/Failure** → Final state with dispatch result

Tests validate each state transition and artifact creation at each step.

## Future Enhancements

1. **End-to-End Integration Test**: Test full flow from UI error → error-observer → GitHub dispatch
2. **Performance Tests**: Validate storage pruning under heavy load
3. **Concurrency Tests**: Validate multiple simultaneous error events
4. **UI Visual Tests**: Validate error observer status visualization in UI

## Related Files

- `/infrastructure/docker/adk-agents/shared/error_event.py` - Error event model
- `/infrastructure/docker/adk-agents/error-observer/agent.py` - Error observer agent
- `/infrastructure/docker/ag-ui-frontend/src/app/api/error-observer/status/route.ts` - Status API
- `/infrastructure/docker/ag-ui-frontend/src/lib/storage.ts` - Storage utilities
- `/infrastructure/docker/ag-ui-frontend/src/app/page.tsx` - CompactAgentStatus component

## Maintenance

- Run tests before deploying error-observer changes
- Update tests when adding new error event fields
- Validate GitHub API limits remain at 10 properties
- Monitor localStorage usage in production
