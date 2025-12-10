# AG-UI Persistence System

## Overview

The AG-UI frontend uses a **three-tier persistence strategy** to ensure session and artifact data survive server restarts, Cloud Run instance cycling, and provide reliable access to historical runs.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Client (Browser)                                                 │
│                                                                  │
│  localStorage (5-10MB)                                           │
│  ├── Lightweight session summaries                              │
│  ├── Artifact IDs and previews                                  │
│  └── Quick access for UI rendering                              │
│                                                                  │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP API
┌──────────────────────────▼───────────────────────────────────────┐
│ Server (Cloud Run)                                               │
│                                                                  │
│  1. activeSessions / activePipelines Map (in-memory)            │
│     ├── Full session/pipeline data                              │
│     ├── Active workflows only                                   │
│     └── Lost on restart/scale-down                              │
│                                                                  │
│  2. Firestore (persistent database)                             │
│     ├── Collection: ag_ui_sessions                              │
│     │   └── Complete session history with turnResults           │
│     ├── Collection: ag_ui_artifacts                             │
│     │   └── All artifacts with A2A protocol data                │
│     └── Survives restarts, available across instances           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Session Creation
1. POST `/api/team` or `/api/pipeline` creates session
2. Session added to in-memory Map (`activeSessions` or `activePipelines`)
3. Lightweight summary saved to **localStorage** (client-side)
4. Execution starts asynchronously

### During Execution
1. Each turn/phase completes
2. Full turnResult added to in-memory session
3. Lightweight summary added to **localStorage**
4. Complete data saved to **Firestore** (async, non-blocking)
5. UI polls GET endpoint for real-time updates

### On Server Restart/Redeploy
- **In-memory data is lost** (activeSessions/activePipelines Maps cleared)
- GET `/api/team?session=<id>` checks:
  1. First: in-memory Map (fast path for active sessions)
  2. If not found: Firestore (persistent fallback)
3. Session recovered from Firestore with complete data
4. No more 404 errors when backend restarts!

### Page Reload
1. Frontend loads lightweight summaries from localStorage
2. Shows basic status immediately (currentTurn/totalTurns)
3. Polls API for full data
4. API returns from in-memory or Firestore

## Storage Comparison

| Storage | Capacity | Speed | Persistence | Data Completeness |
|---------|----------|-------|-------------|-------------------|
| localStorage | 5-10MB | Instant | Browser session | Lightweight summaries |
| In-Memory Map | Unlimited* | Instant | Until restart | Full data |
| Firestore | 1GB+ | 50-200ms | Permanent | Full data |

*Limited by Cloud Run memory allocation

## Configuration

### Environment Variables

```bash
# Enable Firestore persistence (default: true in production)
USE_FIRESTORE=true

# GCP Project ID (required for Firestore)
GCP_PROJECT_ID=your-project-id
GOOGLE_CLOUD_PROJECT=your-project-id
```

### Development Mode

In `NODE_ENV=development`, the system automatically falls back to in-memory storage unless `USE_FIRESTORE=true` is explicitly set.

### Testing Firestore Locally

```bash
# Install gcloud and authenticate
gcloud auth application-default login

# Set project
export GCP_PROJECT_ID=your-project-id
export GOOGLE_CLOUD_PROJECT=your-project-id
export USE_FIRESTORE=true

# Run development server
npm run dev
```

## API Changes

### GET /api/team

**Before:**
- Only returned sessions from in-memory Map
- 404 if session not found after restart

**After:**
- Checks in-memory Map first (fast path)
- Falls back to Firestore if not found
- Returns complete session data from persistent storage
- Supports pagination: `?limit=20&cursor=<id>`

**New Query Params:**
- `limit` (default: 20) - Number of sessions to return
- `cursor` - Pagination cursor (session ID)

**Response includes:**
```json
{
  "sessions": [...],
  "total": 42,
  "active": 3,
  "hasMore": true,
  "nextCursor": "session-123456"
}
```

### GET /api/pipeline

Same improvements as `/api/team`:
- Firestore fallback for historical pipelines
- Pagination support
- Complete data recovery after restarts

## Data Storage Details

### localStorage (Client)

Stores lightweight summaries:
```javascript
{
  id: "session-123",
  type: "workflow",
  status: "completed",
  currentTurn: 3,
  totalTurns: 3,
  turnSummaries: [
    {
      agentId: "academic-research",
      status: "completed",
      artifactCount: 4,
      hasAgentCard: true,
      hasTask: true,
      // NO full artifacts - just counts and flags
    }
  ]
}
```

### Firestore (Server)

Stores complete data:
```javascript
{
  id: "session-123",
  type: "workflow",
  status: "completed",
  metadata: {
    turnResults: [
      {
        agentId: "academic-research",
        artifacts: [...], // FULL artifacts
        agentCard: {...}, // Complete A2A protocol object
        task: {...},      // Complete A2A protocol object
        // All data available
      }
    ]
  }
}
```

## Benefits

### 1. Survives Restarts ✅
- Sessions persist across Cloud Run restarts
- No more 404 errors after redeployment
- Complete data available from Firestore

### 2. Pagination ✅
- Can handle hundreds of historical runs
- Efficient queries with cursors
- Minimal memory footprint on server

### 3. Complete Data ✅
- Full turnResults available for all runs
- No fallback to lightweight summaries
- A2A protocol objects preserved

### 4. Reliable UI ✅
- Graceful fallback to localStorage on API errors
- Polls with exponential backoff
- Clear status indicators

### 5. Performance ✅
- Fast path through in-memory Map for active sessions
- Background sync to Firestore (non-blocking)
- Client-side caching with localStorage

## Migration from Previous System

### What Changed

**Before:**
- 100% in-memory storage (volatile)
- localStorage as fallback (limited data)
- Sessions lost on restart
- 404 errors common after redeploys

**After:**
- Dual storage: in-memory + Firestore
- localStorage for UI responsiveness
- Firestore for long-term persistence
- Graceful recovery after restarts

### Backward Compatibility

✅ Fully backward compatible:
- Existing code continues to work
- Automatic fallback to in-memory if Firestore unavailable
- No breaking changes to API responses
- localStorage format unchanged

## Troubleshooting

### Firestore Not Working

**Symptoms:**
- Logs show: "Failed to initialize Firestore, falling back to in-memory"
- Sessions lost after restart

**Solutions:**
1. Check GCP credentials:
   ```bash
   gcloud auth application-default login
   ```

2. Verify project ID:
   ```bash
   echo $GCP_PROJECT_ID
   echo $GOOGLE_CLOUD_PROJECT
   ```

3. Enable Firestore API:
   ```bash
   gcloud services enable firestore.googleapis.com
   ```

4. Check service account permissions (Cloud Run):
   - Need: `roles/datastore.user` or `roles/owner`

### Sessions Not Persisting

**Check:**
1. Is `USE_FIRESTORE=true` set?
2. Are there errors in console/logs?
3. Is Firestore database created in GCP Console?

**Debug:**
```javascript
// Check which store is active
console.log(process.env.USE_FIRESTORE);
console.log(process.env.GCP_PROJECT_ID);
```

### High Firestore Costs

**Optimization tips:**
1. Use pagination (`limit` param) to reduce reads
2. Client-side caching reduces redundant queries
3. Background sync is non-blocking and efficient
4. Consider batch writes if costs become significant

## Future Enhancements

Potential improvements:
1. **Compression**: Use gzip for artifact data
2. **TTL**: Auto-delete old sessions after 90 days
3. **Sharding**: Distribute across multiple collections
4. **Caching**: Add Redis layer between Firestore and app
5. **Real-time**: Use Firestore real-time listeners for live updates

## Related Files

- `/src/lib/persistence.ts` - Persistence layer implementation
- `/src/app/api/team/route.ts` - Team API with persistence
- `/src/app/api/pipeline/route.ts` - Pipeline API with persistence
- `/src/lib/storage.ts` - localStorage utilities
- `.env.example` - Environment variable documentation
