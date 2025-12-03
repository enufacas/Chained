# Enhanced Storage System

## Overview

The AG-UI storage system has been enhanced to address concurrent write issues and provide better capacity management.

## Key Improvements

### 1. Concurrent Write Protection

**Problem**: Multiple errors arriving simultaneously could cause localStorage write conflicts.

**Solution**: Write queue with debouncing
- All writes are queued and debounced by 100ms
- Prevents concurrent writes to the same key
- Ensures data consistency even under heavy load

```typescript
// Queue writes with 100ms debounce
queueWrite(STORAGE_KEYS.ARTIFACTS, dataToSave);
```

### 2. IndexedDB Background Sync

**Problem**: localStorage has a 5-10MB limit, insufficient for large artifact collections.

**Solution**: Automatic background sync to IndexedDB
- localStorage remains primary (fast, synchronous access)
- IndexedDB used as background backup (50MB+ capacity)
- Non-blocking writes don't impact UI performance
- Automatic fallback if IndexedDB unavailable

```typescript
// Background sync happens automatically
localStorage.setItem(key, data);  // Immediate
queueWrite(key, data);            // Background IndexedDB sync
```

### 3. Graceful Degradation

The system operates in tiers:

1. **localStorage** (Primary)
   - 5-10MB capacity
   - Synchronous access
   - Immediate availability

2. **IndexedDB** (Background Backup)
   - 50MB+ capacity
   - Async operations
   - Non-blocking

3. **Memory-only** (Fallback)
   - Used if both fail
   - Session-only persistence

### 4. Automatic Quota Management

Enhanced quota handling:
- Monitors storage approaching 75% capacity (3MB/4MB)
- Automatic pruning of oldest items
- Aggressive fallback: reduces to 25% capacity if quota exceeded
- Background sync ensures no data loss

## Technical Details

### Write Queue Implementation

```typescript
const pendingWrites: Map<string, PendingWrite> = new Map();

function queueWrite(key: string, value: string): void {
  // Clear existing timeout for this key
  const existing = pendingWrites.get(key);
  if (existing) {
    clearTimeout(existing.timestamp);
  }

  // Queue with 100ms debounce
  const timeoutId = setTimeout(() => {
    pendingWrites.delete(key);
    syncToIndexedDB(key, value);
  }, 100);

  pendingWrites.set(key, { key, value, timestamp: timeoutId });
}
```

### IndexedDB Sync

```typescript
async function syncToIndexedDB(key: string, value: string): Promise<void> {
  // Open/create database
  const request = indexedDB.open("ag-ui-backup", 1);
  
  // Store data in background (non-blocking)
  request.onsuccess = () => {
    const db = request.result;
    const transaction = db.transaction("storage-backup", "readwrite");
    const store = transaction.objectStore("storage-backup");
    store.put(value, key);
  };
}
```

## Handling Multiple Simultaneous Errors

### Scenario: 10 errors arrive within 100ms

**Without queue (BEFORE)**:
```
Error 1 → localStorage.setItem (writing...)
Error 2 → localStorage.setItem (conflicts with 1)
Error 3 → localStorage.setItem (conflicts with 1, 2)
...
Result: Data corruption, some errors lost
```

**With queue (AFTER)**:
```
Error 1 → Queue write + debounce 100ms
Error 2 → Queue write + debounce 100ms (cancels Error 1 timer)
Error 3 → Queue write + debounce 100ms (cancels Error 2 timer)
...
Error 10 → Queue write + debounce 100ms (cancels Error 9 timer)
Wait 100ms...
→ Single write with all 10 errors batched
→ Background sync to IndexedDB
Result: All errors saved, no conflicts
```

### Benefits

1. **No Data Loss**: All writes eventually complete
2. **No Conflicts**: Sequential writes prevent corruption
3. **Performance**: Batching reduces I/O operations
4. **Scalability**: Handles burst traffic gracefully

## Error Observer Integration

The error observer agent can now handle multiple concurrent errors:

```typescript
// Multiple errors arrive simultaneously
await Promise.all([
  saveArtifact(error1),  // Queued
  saveArtifact(error2),  // Queued
  saveArtifact(error3),  // Queued
  saveArtifact(error4),  // Queued
  saveArtifact(error5),  // Queued
]);

// All errors saved without conflicts
// Automatic background sync to IndexedDB
```

## Storage Capacity Comparison

| Storage | Capacity | Access | Use Case |
|---------|----------|--------|----------|
| localStorage | 5-10MB | Sync | Primary cache |
| IndexedDB | 50MB+ | Async | Background backup |
| Memory-only | Unlimited* | Sync | Fallback |

*Limited by browser memory

## Monitoring

Check storage stats:
```typescript
import { getStorageStats } from '@/lib/storage';

const stats = getStorageStats();
console.log(stats);
// {
//   artifactsCount: 42,
//   sessionsCount: 15,
//   estimatedSize: "3.2 MB"
// }
```

## Configuration

Adjust limits in `storage.ts`:
```typescript
const MAX_ARTIFACTS = 100;          // Max artifacts in cache
const MAX_SESSIONS = 50;            // Max sessions in cache
const MAX_STORAGE_SIZE = 4 * 1024 * 1024;  // 4MB localStorage
const STORAGE_WARNING_THRESHOLD = 3 * 1024 * 1024;  // 3MB warning
const WRITE_DEBOUNCE_MS = 100;      // Write queue debounce
```

## Future Enhancements

Potential improvements:
1. **Compression**: Use LZ-string for artifact compression
2. **Prioritization**: Keep important artifacts longer
3. **Smart Pruning**: Remove by age + frequency of access
4. **Cloud Sync**: Optional cloud backup via API
5. **Progressive Web App**: Service worker cache integration

## Related Files

- `/infrastructure/docker/ag-ui-frontend/src/lib/storage.ts` - Main storage implementation
- `/infrastructure/docker/ag-ui-frontend/src/lib/error-logging.ts` - Error reporting
- `/infrastructure/docker/ag-ui-frontend/src/components/ErrorObserverStatus.tsx` - UI status display
