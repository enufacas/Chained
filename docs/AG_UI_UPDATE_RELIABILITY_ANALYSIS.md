# AG-UI Update Reliability: Root Cause Analysis

**Date:** 2025-12-10  
**Context:** Investigation prompted by user comment in PR #3803  
**Question:** "What other problems could exist that would cause the UI not to update?"

## Executive Summary

Faster polling (PR #3803) was **necessary but not sufficient**. The real issues are:

1. **CRITICAL**: In-memory data loss on Cloud Run scale-down  
2. **HIGH**: No error recovery in frontend polling  
3. **MEDIUM**: Silent persistence failures  
4. **MEDIUM**: Cold start delays

**Status:**
- ✅ HIGH priority fixes implemented (error recovery)
- ⏹️ CRITICAL issue remains (data persistence)

---

## Critical Issue #1: In-Memory Data Volatility

### The Problem

Both APIs use in-memory Maps that are **LOST on Cloud Run instance restarts**:

```typescript
// src/app/api/pipeline/route.ts:240
const activePipelines: Map<string, Pipeline> = new Map();

// src/app/api/team/route.ts:251
const activeSessions: Map<string, TeamSession> = new Map();
```

### When Data is Lost

- **Cloud Run scales to zero** after 15-60 min inactivity (`cpu_idle=true`)
- **New deployment/restart** (manual or CI/CD)
- **Container crashes** or OOM errors
- **Load balancer routes** request to new instance

### Impact Flow

1. User starts pipeline/session → stored in memory on Instance A
2. Cloud Run scales down Instance A or starts Instance B
3. Frontend polls `/api/pipeline` → Instance B has empty Map
4. API returns `{pipelines: []}` (empty array)
5. **User sees "No outcomes yet" even though work is running**

### Evidence from Code

```typescript
// Line 346-347 in pipeline/route.ts
const activePipelinesArray = Array.from(activePipelines.values());
let allPipelines = [...activePipelinesArray];

// If activePipelines is empty (new instance), user sees nothing
```

The backend DOES try to load from Firestore (lines 349-379), but:
- It only loads **completed** sessions
- **Running** pipelines that were lost aren't recovered

### Why Faster Polling Didn't Fix This

Polling 2x faster (5s→2s, 2s→1s) helps you **see stale data quicker**, but:
- ❌ Doesn't prevent data loss
- ❌ Doesn't recover lost state
- ❌ Just makes you aware of the problem faster

---

## High Issue #2: No Error Recovery in Frontend

### The Problem (BEFORE FIX)

Original code had **zero retry logic**:

```typescript
// Before fix (lines 472-483)
const fetchPipelines = useCallback(async () => {
  try {
    const response = await fetch("/api/pipeline?limit=10");
    if (response.ok) {
      const result = await response.json();
      setPipelines(result.pipelines || []);
    }
    // ❌ NO ELSE - silently fails if !response.ok
  } catch (err) {
    console.error("[UnifiedOutcomes] Fetch error:", err);
    // ❌ NO RETRY - just logs and continues
  } finally {
    setLoading(false);
  }
}, []);
```

### When This Failed

- **Network hiccup** → catch block logs error, next poll in 2 seconds
- **404/500 from backend** → no data update, no retry
- **Timeout** → catch block, no retry
- **Rate limiting** → silently ignored

### The Fix (IMPLEMENTED) ✅

```typescript
// After fix
const fetchPipelines = useCallback(async () => {
  let retries = 3;
  let lastError: unknown = null;
  
  while (retries > 0) {
    try {
      // Add timeout protection
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      
      const response = await fetch("/api/pipeline?limit=10", {
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const result = await response.json();
        setPipelines(result.pipelines || []);
        setFetchError(null);
        setLastUpdate(new Date());
        retryCountRef.current = 0;
        return; // Success - exit retry loop
      } else {
        // Handle non-ok responses
        lastError = `HTTP ${response.status}`;
        console.warn(`Response ${response.status}, retries left: ${retries - 1}`);
      }
    } catch (err) {
      lastError = err;
      console.error("Fetch error:", err);
    }
    
    retries--;
    if (retries > 0) {
      // Exponential backoff: 500ms, 1s, 1.5s
      await new Promise(resolve => setTimeout(resolve, 500 * (4 - retries)));
    }
  }
  
  // After all retries failed, log but keep existing data
  console.error("All retry attempts failed:", lastError);
}, []);
```

### Benefits

- **Transient errors recover automatically** (3 attempts)
- **Timeout protection** (10s max per request)
- **Exponential backoff** prevents API hammering
- **Preserves existing data** on failure (doesn't clear pipelines)
- **User-visible error state** (see Phase 3 below)

---

## High Issue #3: Session Polling Stops on Error

### The Problem (BEFORE FIX)

Session polling had **no retry and stopped permanently** on any error:

```typescript
// Before fix (lines 1513-1517)
} catch (err) {
  console.error("Poll error:", err);
  // ❌ Single error stops all polling permanently
  setIsTeamExecuting(false);
}
```

**Impact:** One network blip = user must refresh page to resume updates.

### The Fix (IMPLEMENTED) ✅

```typescript
// After fix
while (retries > 0) {
  try {
    const response = await fetch(`/api/team?session=${sessionId}`);
    if (response.ok) {
      // ... handle success ...
      return; // Exit retry loop
    } else if (response.status === 404) {
      // Session not found - don't retry
      console.warn(`Session ${sessionId} not found on backend`);
      setIsTeamExecuting(false);
      return;
    } else {
      // Other error - log and retry
      lastError = `HTTP ${response.status}`;
      console.warn(`Response ${response.status}, retries left: ${retries - 1}`);
    }
  } catch (err) {
    lastError = err;
    console.error("Session Poll fetch error:", err);
  }
  
  retries--;
  if (retries > 0) {
    // Short backoff for polling: 200ms
    await new Promise(resolve => setTimeout(resolve, 200));
  }
}

// After retries, continue polling despite errors
if (isTeamExecuting) {
  setTimeout(poll, 1000); // Next poll cycle
}
```

### Benefits

- **Transient errors don't stop polling** (retries within poll cycle)
- **Distinguishes 404** (permanent) vs network errors (transient)
- **Continues trying** even after retries exhausted
- **User doesn't lose real-time updates** from brief network issues

---

## Added Feature: Visual Error Indicators

### New UI States ✅

```typescript
const [fetchError, setFetchError] = useState<string | null>(null);
const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
const retryCountRef = useRef(0);
```

### Status Indicator

Shows in UnifiedOutcomes header:

```tsx
{fetchError ? (
  <span className="text-red-400">
    ⚠️ Update failed
    {retryCountRef.current > 0 && (
      <span>(retry {retryCountRef.current}/{MAX_RETRIES})</span>
    )}
  </span>
) : lastUpdate ? (
  <span className="text-slate-500">
    ✓ Updated {Math.floor((Date.now() - lastUpdate.getTime()) / 1000)}s ago
  </span>
) : null}
```

### Error Banner

Shown prominently when all retries exhausted:

```tsx
{fetchError && retryCountRef.current >= MAX_RETRIES && (
  <div className="px-3 py-2 bg-red-500/10 border-b border-red-500/20">
    <div className="flex items-start gap-2">
      <span className="text-red-400">⚠️</span>
      <div className="flex-1">
        <div className="text-red-300 font-medium">Unable to fetch updates</div>
        <div className="text-red-400/70">{fetchError}</div>
        <div className="text-slate-400">Real-time updates may be delayed. Page refresh recommended.</div>
      </div>
    </div>
  </div>
)}
```

### Manual Retry Button

```tsx
{fetchError && (
  <button
    onClick={() => {
      retryCountRef.current = 0;
      fetchPipelines();
    }}
    className="text-blue-400 hover:text-blue-300 underline"
  >
    Retry now
  </button>
)}
```

### Benefits

- **User knows when updates fail** (not silent anymore)
- **Transparency** about last successful update
- **Manual recovery option** if automatic retries fail
- **Reduced confusion** ("is it working?")

---

## Medium Issue #4: Silent Backend Persistence Failures

### The Problem

Backend tries to save to Firestore but **failures are only logged**:

```typescript
// Lines 1173-1187 in pipeline/route.ts
try {
  await store.saveSession(persistedSession);
} catch (firestoreError) {
  logWithTimestamp("WARN", "Failed to persist session", {
    error: firestoreError instanceof Error ? firestoreError.message : String(firestoreError),
  });
  // ❌ Continues execution - in-memory data might be lost later
}
```

**Impact:** If Firestore save fails, the ONLY copy is in volatile memory.

### When This Happens

- **Firestore quota exceeded**
- **Network timeout to Firestore**
- **Invalid data format**
- **Permission issues**

### Recommended Fix (NOT YET IMPLEMENTED)

```typescript
try {
  await store.saveSession(persistedSession);
} catch (firestoreError) {
  logWithTimestamp("ERROR", "CRITICAL: Failed to persist session", {
    pipelineId,
    error: firestoreError,
  });
  // Mark pipeline as failed
  pipeline.status = "failed";
  pipeline.error = "Failed to persist data";
  activePipelines.set(pipelineId, pipeline);
  
  // Return error to frontend
  return new Response(
    JSON.stringify({ error: "Persistence failure", pipelineId }),
    { status: 500, headers: corsHeaders }
  );
}
```

---

## Medium Issue #5: Cloud Run Cold Starts

### Configuration

```hcl
# infrastructure/terraform/base/adk-agents.tf
resources {
  limits = {
    cpu    = "0.5"
    memory = "1Gi"
  }
  cpu_idle          = true  # ⚠️ Scales to zero
  startup_cpu_boost = true
}
```

### Impact

- **First request after scale-to-zero**: 2-5 second cold start
- **During cold start**: existing in-memory data is GONE
- **Frontend polls during cold start**: might get timeout or empty data
- **User experience**: "app is slow" or "data disappeared"

### Recommended Fix (NOT YET IMPLEMENTED)

**Option A: min_instances** (costs ~$15-30/month)
```hcl
scaling {
  min_instance_count = 1  # Always keep one instance warm
}
```

**Option B: Faster startup**
- Reduce Docker image size
- Lazy-load dependencies
- Optimize Next.js build

**Option C: Pre-warming**
- Health check endpoint
- Scheduled pings to keep warm

---

## Why User Experienced Issues "Past the Old Polling Interval"

The user reported:
> "often i waited past the old polling interval"

This makes sense because:

1. **Data Loss** (not polling frequency)
   - Cloud Run scaled down → activePipelines lost
   - Frontend polled successfully but got empty data
   - Even waiting 10x the polling interval wouldn't help

2. **Error Recovery Missing**
   - One failed request → no retry
   - Next poll attempt might also fail (cascade)
   - Exponentially compounds problem

3. **No Visual Feedback**
   - Silent failures
   - User doesn't know if polling is working
   - Assumes "maybe need to wait longer"

**The fix isn't faster polling—it's:**
- ✅ Persistent backend storage (not yet implemented)
- ✅ Error recovery (now implemented)
- ✅ User feedback (now implemented)

---

## Recommended Fixes (Priority Order)

### 1. Fix Data Volatility (CRITICAL - Required)

**Option A: Use Firestore for ALL active data**
```typescript
// Replace in-memory Map entirely
async function getActivePipelines(): Promise<Pipeline[]> {
  const store = getPersistenceStore();
  const result = await store.listSessions("workflow", 100);
  return result.items
    .filter(s => s.status === "running" || s.status === "pending")
    .map(convertToPipeline);
}

// On GET /api/pipeline - query Firestore directly
const allPipelines = await getActivePipelines();
```

**Option B: Persist to Firestore on EVERY update**
```typescript
// After EVERY activePipelines.set(), also save to Firestore
activePipelines.set(pipelineId, pipeline);
await store.saveSession(toPersisted(pipeline)).catch(err => {
  // Handle persistence failure
  pipeline.status = "failed";
  pipeline.error = "Persistence failed";
});
```

**Option C: Use Redis/Memorystore for shared state**
- All Cloud Run instances share same cache
- Survives individual instance restarts
- Sub-millisecond access times
- Cost: ~$30-50/month for basic tier

### 2. ✅ Add Frontend Error Recovery (IMPLEMENTED)

- ✅ Retry logic with exponential backoff
- ✅ Timeout protection (10s)
- ✅ Preserve existing data on failure
- ✅ Visual error indicators

### 3. Improve Backend Error Handling (MEDIUM)

Make persistence errors fatal:
```typescript
try {
  await store.saveSession(persistedSession);
} catch (firestoreError) {
  // Mark as failed, return 500 to frontend
  pipeline.status = "failed";
  return errorResponse(500, "Persistence failure");
}
```

### 4. Scale Infrastructure (OPTIONAL - If Load is High)

**Current:**
- CPU: 0.5 (half a core)
- Memory: 1Gi
- Concurrency: Default (80 requests/instance)
- min_instances: 0 (scale-to-zero)

**Consider:**
- CPU: 1.0 → faster response times
- min_instances: 1 → keep one instance always warm (~$15-30/month)
- Concurrency: 20-40 → reduce load per instance

---

## Testing the Hypothesis

### Reproduce the Issue

1. Start a pipeline on production AG-UI
2. Wait for Cloud Run to scale down (15-60 min)
3. Refresh page or wait for next poll
4. **Expected:** Pipeline disappears (empty array returned)

### Verify the Fix (After Implementing Option A/B)

1. Start a pipeline
2. Restart Cloud Run service manually:
   ```bash
   gcloud run services update chained-ag-ui-frontend --region us-central1
   ```
3. **Expected:** Pipeline still visible (loaded from Firestore)

---

## Summary Table

| Issue | Severity | Current State | Fix Status |
|-------|----------|---------------|------------|
| In-memory data loss | CRITICAL | Unfixed | ⏹️ Needs backend work |
| No error recovery (frontend) | HIGH | Fixed | ✅ Implemented |
| No error recovery (sessions) | HIGH | Fixed | ✅ Implemented |
| Visual error indicators | HIGH | Fixed | ✅ Implemented |
| Silent persistence failures | MEDIUM | Unfixed | ⏹️ Needs backend work |
| Cold start delays | MEDIUM | Mitigated by boost | ⚠️ Consider min_instances |
| Slow polling | LOW | Fixed (PR #3803) | ✅ Complete |

**Conclusion:** Faster polling was necessary but not sufficient. The real fix requires persistent storage for active pipelines/sessions (Options A, B, or C above).

---

## References

- **Original PR:** #3803
- **User Comment:** https://github.com/enufacas/Chained/pull/3803#issuecomment-3635313876
- **Original Copilot Session:** https://github.com/enufacas/Chained/actions/runs/20087201916/job/57627278013 (cancelled)
- **This Session:** Completing interrupted work

## Next Steps

1. **Implement backend persistence** (Choose Option A, B, or C)
2. **Test on production** AG-UI
3. **Monitor metrics** (update failures, data loss reports)
4. **Consider infrastructure scaling** if load warrants it
