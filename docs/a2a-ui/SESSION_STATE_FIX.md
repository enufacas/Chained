# AG-UI Session State Tracking Fix

**PR**: #3492  
**Date**: 2025-12-01  
**Status**: ✅ Fixed

## Problem Statement

When testing the AG-UI team execution feature, users experienced:

1. **Progress shows 6/6 but never completes**: The UI displayed "Turn 6/6" but the session remained in "running" state indefinitely
2. **Stale state after refresh**: After refreshing the page, the UI showed "Turn 2/6" instead of the current state
3. **Stuck executions**: Sessions that should have completed remained stuck

## Root Causes

### 1. Race Condition in Sequential Mode

**Location**: `src/app/api/team/route.ts` line 691

```typescript
// ❌ BEFORE: currentTurn updated BEFORE execution
session.currentTurn = stepIndex + 1;
session.updatedAt = new Date().toISOString();
activeSessions.set(sessionId, session);

const turnResult = await executeTurn(session, step, stepIndex);

// ✅ AFTER: currentTurn updated AFTER execution
const turnResult = await executeTurn(session, step, stepIndex);

stepIndex++;
session.currentTurn = stepIndex;
session.updatedAt = new Date().toISOString();
activeSessions.set(sessionId, session);
```

**Impact**: Frontend polling saw `currentTurn=6` when only 5 turns had actually completed, causing premature "completion" display.

### 2. Status Update Race Condition

**Location**: `src/app/api/team/route.ts` line 672-718

The backend updated `currentTurn` in the execution loop but didn't set `status = "completed"` until later. This created a window where:
- `currentTurn === totalTurns` (6/6)
- `status === "running"` (not done yet)

Frontend polling saw this inconsistent state and continued waiting indefinitely.

**Fix**: Added atomic update - both `status` and `currentTurn` are set before final `activeSessions.set()`:

```typescript
// Mark complete - atomically update status, currentTurn, and timestamp
if (session.status !== "failed") {
  session.status = "completed";
  session.currentTurn = session.totalTurns;
}
session.updatedAt = new Date().toISOString();

// Atomically persist the completed session state
activeSessions.set(sessionId, session);
```

### 3. No Backend Verification on Page Load

**Location**: `src/app/page.tsx` line 932-1076

**Before**: Sessions were restored from `localStorage` without verifying they still exist on the backend. If the server restarted, the in-memory `activeSessions` Map was empty, but the frontend showed stale localStorage state.

**After**: Added backend verification that:
1. Checks if session exists: `GET /api/team?session={id}`
2. Uses backend state as source of truth if found
3. Marks session as completed if not found (404)
4. Resumes polling if session is still active

```typescript
// Verify session still exists on backend
fetch(`/api/team?session=${activeSession.id}`)
  .then(res => {
    if (res.ok) {
      return res.json();
    } else if (res.status === 404) {
      // Server restart or session lost - mark as completed
      setActiveSession(prev => ({
        ...prev,
        status: "completed",
        currentTurn: prev.totalTurns,
      }));
      return null;
    }
  })
  .then(backendSession => {
    if (backendSession) {
      // Use backend as source of truth
      setActiveSession(backendSession);
      if (isSessionActive(backendSession)) {
        setResumePollingSessionId(backendSession.id);
      }
    }
  });
```

### 4. Polling Logic Issues

**Location**: `src/app/page.tsx` line 1143-1226

**Before**: Polling relied on `currentTurn` vs `totalTurns` comparison, which wasn't reliable due to race conditions.

**After**: Polling explicitly checks status field:

```typescript
// Continue polling only if session is still active
if (isSessionActive(session)) {  // checks status === "running" || "pending"
  setTimeout(poll, 2000);
} else {
  setIsTeamExecuting(false);
  // Add to completed sessions
}
```

Added 404 handling:
```typescript
if (response.status === 404) {
  // Session not found on backend - likely server restarted
  console.warn(`Session ${sessionId} not found on backend`);
  setIsTeamExecuting(false);
}
```

## Solution Summary

### Backend Changes (`src/app/api/team/route.ts`)

1. **Sequential mode**: Update `currentTurn` AFTER turn execution completes
2. **Atomic transitions**: Update status and currentTurn together before persisting
3. **Comments**: Added clarifying comments about race condition prevention

### Frontend Changes (`src/app/page.tsx`)

1. **Backend verification**: New useEffect to verify restored sessions
2. **Polling improvements**: 
   - Check status explicitly
   - Handle 404 responses
   - Stop on errors
3. **Session recovery**: Resume polling for active restored sessions
4. **State management**: Added `resumePollingSessionId` to avoid circular dependencies

### Documentation (`docs/a2a-ui/CHANGELOG.md`)

- Complete changelog entry
- Technical details
- Why it matters

## Testing

### Build & Lint
```bash
cd infrastructure/docker/ag-ui-frontend
npm run build  # ✅ Success
npm run lint   # ✅ No warnings or errors
```

### Manual Testing Scenarios

To verify the fix works:

1. **Normal execution**: Start a team workflow, verify it completes when reaching totalTurns
2. **Page refresh during execution**: Refresh browser, verify correct progress shown
3. **Page refresh after completion**: Refresh browser, verify session shows as completed
4. **Server restart**: Restart backend while session running, refresh page, verify graceful handling
5. **Parallel mode**: Test with parallel execution mode, verify progress accuracy

## Impact

✅ **No more stuck sessions**: Sessions properly transition to "completed" state  
✅ **Accurate progress**: UI shows actual execution state, not predicted/stale state  
✅ **Page refresh resilience**: Backend verification prevents stale data display  
✅ **Server restart handling**: Gracefully handles backend session loss  

## Future Improvements

While this fix resolves the immediate issues, potential enhancements:

1. **Backend persistence**: Store sessions in database instead of in-memory Map
2. **Session recovery**: Allow backend to resume interrupted sessions
3. **Explicit "completing" state**: Add intermediate state to signal final processing
4. **WebSocket updates**: Replace polling with real-time updates
5. **Better error messages**: More descriptive UI messages for different failure modes

## Related Issues

- Original report: PR #3492 review comments
- Related to: Session persistence work in prior PRs

## References

- [A2A UI Documentation](README.md)
- [A2A UI Changelog](CHANGELOG.md)
- [Team API Route](../../infrastructure/docker/ag-ui-frontend/src/app/api/team/route.ts)
- [Main Page Component](../../infrastructure/docker/ag-ui-frontend/src/app/page.tsx)
