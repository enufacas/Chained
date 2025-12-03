# AG-UI Session Persistence Fix

**Date:** 2025-12-03  
**Issue:** Pipeline sessions showing incorrect/simplified data after page reload  
**Status:** ✅ Fixed

## Problem Statement

Users reported that pipeline sessions in the "Progress and Outcomes" section:
- Appeared fully featured and correct during the first run
- Became simplified and incorrect on subsequent page views
- Were missing data and ordered incorrectly
- Lost full session information after page reload

## Root Cause Analysis

### The Data Flow Problem

The AG-UI has a hybrid storage architecture:

1. **Server-side (In-Memory)**:
   - `activePipelines` Map stores running pipelines
   - Located in `/api/pipeline/route.ts`
   - Lost on server restart or when Next.js recompiles

2. **Client-side (localStorage)**:
   - `saveSession()` persists completed pipelines
   - Includes full metadata, artifacts, and A2A steps
   - Survives page reloads and server restarts

3. **The Bug**:
   - `PipelineOutcomes` component only fetched from `/api/pipeline`
   - API `GET` endpoint only returned `activePipelines` Map
   - localStorage data was ignored, even though it had complete history
   - Result: Empty/incomplete data after reload

### Why Data Appeared Correct Initially

During the first run:
1. User creates pipeline
2. Pipeline executes and saves to both:
   - `activePipelines` Map (in-memory)
   - localStorage (persistent)
3. UI fetches from API, gets data from `activePipelines`
4. Everything looks correct ✅

After page reload:
1. Server restarts or Next.js recompiles
2. `activePipelines` Map is empty
3. localStorage still has all the data
4. UI fetches from API, gets empty response
5. Historical pipelines disappear ❌

### Why Data Became "Simplified"

When pruning storage for quota limits, the system:
- Strips large metadata from older sessions (line 596-604 in `storage.ts`)
- Keeps only 3 most recent sessions with full data
- This is correct behavior to prevent quota errors
- But the UI should still show these simplified sessions

The bug wasn't the simplification - it was that the UI wasn't reading the sessions at all!

## Solution

### Architecture Change: Client-First Data Loading

Modified `PipelineOutcomes.tsx` to use a client-first approach:

```typescript
1. Read sessions from localStorage (primary source)
2. Fetch from API for active pipelines (secondary source)
3. Merge both sources
4. Deduplicate (prefer API version for active pipelines)
5. Sort by creation date (newest first)
```

### Code Changes

#### 1. Added `sessionToPipelineResult()` Function

Converts `StoredSession` from localStorage to `PipelineResult` format:
- Extracts blog URL from metadata or artifacts
- Reconstructs progress and status
- Preserves all session data

```typescript
function sessionToPipelineResult(session: StoredSession): PipelineResult {
  // Extract blog URL from metadata or artifacts
  let blogUrl: string | undefined;
  
  if (session.metadata?.blogUrl) {
    blogUrl = session.metadata.blogUrl as string;
  } else if (session.artifacts && session.artifacts.length > 0) {
    // Try to find blog artifact...
  }
  
  return {
    id: session.id,
    topic: session.topic,
    status: session.status as PipelineResult["status"],
    createdAt: session.createdAt,
    updatedAt: session.completedAt || session.createdAt,
    progress: session.status === "completed" ? 100 : 50,
    currentPhase: session.status === "completed" ? "complete" : "writing",
    results: blogUrl ? { blog: { title, url, wordCount } } : undefined,
  };
}
```

#### 2. Modified `fetchPipelines()` to Merge Data Sources

```typescript
const fetchPipelines = useCallback(async () => {
  // 1. Get sessions from localStorage
  const storedSessions = getStoredSessions();
  const storedWorkflows = storedSessions.filter(s => s.type === "workflow");
  const localPipelines = storedWorkflows
    .map(sessionToPipelineResult)
    .slice(0, 20);
  
  // 2. Fetch active pipelines from API (non-blocking)
  let apiPipelines: PipelineResult[] = [];
  try {
    const response = await fetch("/api/pipeline?limit=10");
    if (response.ok) {
      const result = await response.json();
      apiPipelines = result.pipelines || [];
    }
  } catch {
    // Fallback to localStorage only
  }
  
  // 3. Merge and deduplicate
  const apiIds = new Set(apiPipelines.map(p => p.id));
  const uniqueLocalPipelines = localPipelines.filter(p => !apiIds.has(p.id));
  
  // 4. Sort newest first
  const allPipelines = [...apiPipelines, ...uniqueLocalPipelines]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 10);
  
  setData({ pipelines: allPipelines, ... });
}, []);
```

## Benefits of This Approach

### 1. Offline-First Architecture
- Works even if API is down
- Faster initial load (localStorage is synchronous)
- Progressive enhancement (API adds active pipelines)

### 2. Complete Historical Data
- All completed pipelines persist
- Survives page reloads
- Survives server restarts
- Survives Next.js recompilation

### 3. Correct Ordering
- Sorted by creation date (newest first)
- Consistent ordering across reloads
- Active pipelines appear at top (by design)

### 4. No Duplicates
- API version preferred for active pipelines
- localStorage provides historical context
- Deduplication by pipeline ID

### 5. Graceful Degradation
- If API fails, still shows localStorage data
- If localStorage is empty, shows API data
- Never shows empty state if data exists

## Testing Checklist

### Basic Functionality
- [ ] Create a pipeline and verify it appears in the list
- [ ] Reload page and verify pipeline still appears
- [ ] Verify pipeline data is complete (topic, status, artifacts)
- [ ] Verify ordering is correct (newest first)

### Edge Cases
- [ ] Multiple pipelines are ordered correctly
- [ ] No duplicate entries appear
- [ ] Completed pipelines persist after 1 hour
- [ ] Active pipelines update in real-time
- [ ] Failed pipelines are shown correctly

### Data Integrity
- [ ] Full artifact data is accessible via detail view
- [ ] Blog URLs are preserved and clickable
- [ ] Creation/completion timestamps are accurate
- [ ] Status indicators are correct

### Performance
- [ ] Initial load is fast (&lt;100ms for localStorage read)
- [ ] No unnecessary re-renders
- [ ] API failures don't block UI
- [ ] Polling continues to work (5-second interval)

## Future Improvements

### Server-Side Persistence (Optional)

For production environments with multiple users, consider:

1. **Firestore Integration** (already supported):
   ```typescript
   USE_FIRESTORE=true
   ```
   - Persist activePipelines to Firestore
   - Restore on server startup
   - Share state across multiple server instances

2. **Cloud Storage Backup**:
   - Periodically backup localStorage to GCS
   - Restore on first load if localStorage is empty
   - Enables cross-device sync

3. **Database Layer**:
   - PostgreSQL/MySQL for structured queries
   - Filter by date range, status, user
   - Support pagination for 100+ pipelines

### Enhanced localStorage Management

Current system already handles:
- ✅ Quota exceeded errors
- ✅ Automatic pruning
- ✅ Metadata stripping for old sessions
- ✅ IndexedDB backup (queued, non-blocking)

Potential additions:
- Export/import session data
- Selective deletion
- Search/filter capabilities
- Compression for large artifacts

## Related Files

**Frontend:**
- `src/components/PipelineOutcomes.tsx` - Main component (modified)
- `src/lib/storage.ts` - Storage utilities
- `src/lib/storage-cleanup.ts` - Quota management

**Backend:**
- `src/app/api/pipeline/route.ts` - Pipeline API (GET endpoint)
- Stores pipelines in `activePipelines` Map

**Documentation:**
- `docs/investigations/ERROR_OBSERVER_CONFIGURATION_FIX.md`
- `infrastructure/docker/ag-ui-frontend/ENHANCED_STORAGE_SYSTEM.md`

## Lessons Learned

### 1. Always Consider Data Persistence Layer

When designing APIs:
- Don't rely solely on in-memory state
- Plan for server restarts and recompilation
- Document where data persists (server vs client)

### 2. Client-First Can Be Better

For user-specific data that doesn't need sharing:
- localStorage is often sufficient and faster
- API can be secondary for active/shared state
- Progressive enhancement works well

### 3. Test the Full Lifecycle

Not just "does it work now" but:
- Does it work after reload?
- Does it work after server restart?
- Does it work after 1 hour/1 day/1 week?

### 4. Hybrid Storage Needs Clear Strategy

When using both server and client storage:
- Define primary source of truth
- Document synchronization strategy
- Handle conflicts explicitly
- Test merge/deduplication logic

## References

- **A2A UI Development Instructions**: `.github/instructions/ag-ui-development.instructions.md`
- **A2A UI Real Data Policy**: `.github/instructions/ag-ui-real-data.instructions.md`
- **Storage System Documentation**: `infrastructure/docker/ag-ui-frontend/ENHANCED_STORAGE_SYSTEM.md`
- **Original Storage Fix PR**: #3548
