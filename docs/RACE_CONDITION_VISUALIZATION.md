# Race Condition Visualization

## Before Fix: The Problem

```
Issue #681 Created (23:20:50 UTC)
│
├─── Trigger 1: issues:opened event
│    └─── Workflow Run 1 starts (23:21:13 UTC)
│         │
│         ├─ Check assignees: ❌ None found
│         ├─ Check comments: ❌ None found
│         ├─ Start agent matching (5 seconds...)
│         │
│         │    ┌─── Trigger 2: scheduled event (23:30)
│         │    │    └─── Workflow Run 2 starts (23:39:35 UTC)
│         │    │         │
│         │    │         ├─ Check assignees: ❌ None found (Run 1 not done)
│         │    │         ├─ Check comments: ❌ None found (Run 1 not done)
│         │    │         ├─ Start agent matching (5 seconds...)
│         │    │         │
│         ├─ Add label    │
│         ├─ Assign       ├─ Add label
│         ├─ Comment      ├─ Assign ❌ DUPLICATE
│         └─ Create PR #682  ├─ Comment ❌ DUPLICATE
│                         └─ Create PR #683 ❌ DUPLICATE
│
Result: TWO branches, TWO PRs, TWO assignments for ONE issue ❌
```

## After Fix: The Solution

### Defense Layer 1: Workflow Concurrency Control

```yaml
concurrency:
  group: copilot-assignment-${{ github.event.issue.number }}
```

```
Issue #681 Created
│
├─── Trigger 1: issues:opened
│    └─── Workflow Run 1 starts
│         [Takes lock: copilot-assignment-681]
│         │
│         │    ┌─── Trigger 2: scheduled
│         │    │    └─── Workflow Run 2 starts
│         │    │         [Tries lock: copilot-assignment-681]
│         │    │         [QUEUED - waiting for Run 1]
│         │    │         │
│         ├─ Processing   │
│         ├─ Assign       │ [Still queued...]
│         ├─ Complete     │
│         [Release lock]  │
│                         │ [Gets lock]
│                         ├─ Check assignees: ✅ Already assigned
│                         └─ Skip ✅ No duplicate!
```

### Defense Layer 2: Label-Based Locking

```
Workflow Run 1                 Workflow Run 2 (concurrent)
│                              │
├─ Check assignees: ❌         ├─ Check assignees: ❌
├─ Check label: ❌              ├─ Check label: ❌
├─ Add label [t=0.5s] ✅       │
│  (copilot-assigned)          ├─ Add label [t=0.6s] ✅
│                              │  (already exists, no-op)
│                              │
│                              ├─ Check label AGAIN: ✅ EXISTS!
│                              └─ Skip ✅ No duplicate!
│
├─ [5s agent matching...]
├─ Assign
└─ Complete
```

### Combined Defense (Both Layers)

```
Issue Created
│
├─── Run 1 starts
│    ├─ [Workflow concurrency: Lock acquired]
│    ├─ Check assignees: ❌
│    ├─ Check label: ❌
│    ├─ Add label: ✅ (Lock #2)
│    ├─ [Processing...]
│    ├─ Assign
│    └─ Complete
│         [Workflow concurrency: Lock released]
│
└─── Run 2 starts (concurrent or queued)
     │
     ├─ [Option A: Queued by workflow concurrency]
     │  └─ When started, checks find assignee → Skip ✅
     │
     └─ [Option B: Started during Run 1]
        ├─ Check assignees: ❌ (Run 1 not done)
        ├─ Check label: ✅ EXISTS (Run 1 added it)
        └─ Skip ✅
```

## Edge Case Handling

### Case 1: Scheduled Run Processing Multiple Issues

```
Scheduled Run starts [concurrency: scheduled]
│
├─── Issue #100 (unassigned)
│    ├─ Check: ❌ Not assigned
│    ├─ Add label: ✅
│    ├─ Assign: ✅
│    └─ Complete
│
├─── Issue #101 (unassigned)
│    ├─ Check: ❌ Not assigned
│    ├─ Add label: ✅
│    ├─ Assign: ✅
│    └─ Complete
│
└─── Issue #681 (already has label from earlier run)
     ├─ Check label: ✅ Has copilot-assigned
     └─ Skip ✅

Note: Scheduled run uses 'scheduled' concurrency group,
      doesn't conflict with issue-specific runs.
```

### Case 2: Rapid Manual Dispatches

```
User triggers workflow on Issue #681 (Manual dispatch 1)
│
├─── Run 1 starts [concurrency: copilot-assignment-681]
│    ├─ Lock acquired
│    └─ [Processing...]
│
User triggers again (Manual dispatch 2)
│
├─── Run 2 queued [concurrency: copilot-assignment-681]
│    └─ [Waiting for Run 1...]
│
Run 1 completes
│
├─── Run 2 starts
     ├─ Check assignees: ✅ Already assigned
     └─ Skip ✅
```

### Case 3: Label Addition Fails

```
Run 1                          Run 2 (concurrent)
│                              │
├─ Check label: ❌              ├─ Check label: ❌
├─ Try add label: ❌ FAILED!   ├─ Try add label: ❌ FAILED!
│  (API error/permissions)     │  (API error/permissions)
│                              │
├─ Log warning                 ├─ Log warning
├─ Continue processing         ├─ Continue processing
│                              │
│  [Workflow concurrency       │  [Workflow concurrency
│   still prevents overlap]    │   queued or serialized]
│                              │
└─ Assign ✅                   └─ Check: Already assigned ✅
                                  Skip ✅
```

## Timeline Comparison

### Issue #681: What Happened (Before Fix)

```
23:20:50 ────── Issue #681 created
                │
23:21:13 ────── Run 1: Assign & Create PR #682 ✅
                │
23:39:35 ────── Run 2: Assign & Create PR #683 ❌ DUPLICATE
                │
Result:         Two branches, confusion, wasted work
```

### Issue #681: What Would Happen Now (After Fix)

```
23:20:50 ────── Issue #681 created
                │
23:21:13 ────── Run 1: Acquire lock, add label, assign ✅
                │       Create PR #682 ✅
                │
23:39:35 ────── Run 2: Check label → Already assigned
                │       Skip processing ✅
                │
Result:         One branch, one PR, no duplicates ✅
```

## Summary

The fix implements **defense in depth**:

1. **Workflow Concurrency** → Prevents parallel execution at GitHub Actions level
2. **Label-Based Lock** → Provides additional safety if concurrency fails
3. **Assignee Check** → Catches issues already assigned
4. **Comment Check** → Final fallback for detecting duplicates

Each layer protects against different failure modes, ensuring robust prevention of duplicate assignments even in edge cases or when individual mechanisms fail.

---

*Visual documentation for the duplicate assignment fix*
*See docs/DUPLICATE_ASSIGNMENT_FIX.md for detailed explanation*
