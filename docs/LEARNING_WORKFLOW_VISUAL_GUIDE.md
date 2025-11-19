# Learning Workflow Merge Conflict Resolution - Visual Guide

## Problem: Race Condition

```
┌─────────────────────────────────────────────────────────────────┐
│ BEFORE: Multiple Issues Close → Concurrent Workflows → Conflicts│
└─────────────────────────────────────────────────────────────────┘

Issue #100 Closes                    Issue #101 Closes
       ↓                                    ↓
┌──────────────────┐              ┌──────────────────┐
│ self-documenting │              │ self-documenting │
│     -ai.yml      │              │  -ai-enhanced.yml│
└────────┬─────────┘              └────────┬─────────┘
         │                                  │
         │ Both Start at Same Time          │
         ↓                                  ↓
  ┌─────────────┐                    ┌─────────────┐
  │ Checkout    │                    │ Checkout    │
  │ main@ABC123 │                    │ main@ABC123 │
  └──────┬──────┘                    └──────┬──────┘
         │                                  │
         │ Both Work on Same Base           │
         ↓                                  ↓
  ┌─────────────┐                    ┌─────────────┐
  │ Add file:   │                    │ Add file:   │
  │ issue_100.  │                    │ issue_101.  │
  │ json        │                    │ json        │
  └──────┬──────┘                    └──────┬──────┘
         │                                  │
         │                                  │
         ↓                                  ↓
  ┌─────────────┐                    ┌─────────────┐
  │ Create PR 1 │                    │ Create PR 2 │
  │ base: ABC123│                    │ base: ABC123│
  └──────┬──────┘                    └──────┬──────┘
         │                                  │
         │ PR 1 Merges First                │
         ↓                                  │
  ┌─────────────┐                          │
  │ main@DEF456 │                          │
  │ (has issue_ │                          │
  │  100.json)  │                          │
  └─────────────┘                          │
                                            │
                    PR 2 Tries to Merge ───┘
                            ↓
                    ┌─────────────┐
                    │   CONFLICT! │
                    │ base: ABC123│
                    │ main: DEF456│
                    │             │
                    │ ❌ Failed   │
                    └─────────────┘
```

## Solution: Concurrency Control + Pull-Before-Push

```
┌─────────────────────────────────────────────────────────────────┐
│ AFTER: Concurrency Groups → Sequential Execution → No Conflicts │
└─────────────────────────────────────────────────────────────────┘

Issue #100 Closes                    Issue #101 Closes
       ↓                                    ↓
┌──────────────────┐              ┌──────────────────┐
│ self-documenting │              │ self-documenting │
│     -ai.yml      │              │  -ai-enhanced.yml│
└────────┬─────────┘              └────────┬─────────┘
         │                                  │
         │ Concurrency Group:               │
         │ "learning-discussions"           │
         ↓                                  ↓
  ┌─────────────┐                    ┌─────────────┐
  │ Workflow 1  │                    │ Workflow 2  │
  │   STARTS    │                    │   QUEUED    │
  └──────┬──────┘                    └─────────────┘
         │                                  │
         │                                  │ Waiting...
         ↓                                  │
  ┌─────────────┐                          │
  │ Checkout    │                          │
  │ main@ABC123 │                          │
  └──────┬──────┘                          │
         │                                  │
         ↓                                  │
  ┌─────────────┐                          │
  │ Fetch main  │                          │
  │ (still      │                          │
  │  ABC123)    │                          │
  └──────┬──────┘                          │
         │                                  │
         ↓                                  │
  ┌─────────────┐                          │
  │ Add file:   │                          │
  │ issue_100.  │                          │
  │ json        │                          │
  └──────┬──────┘                          │
         │                                  │
         ↓                                  │
  ┌─────────────┐                          │
  │ Create PR 1 │                          │
  │ base: ABC123│                          │
  └──────┬──────┘                          │
         │                                  │
         ↓                                  │
  ┌─────────────┐                          │
  │ PR 1 Merges │                          │
  │ main@DEF456 │                          │
  └──────┬──────┘                          │
         │                                  │
         │ Workflow 1 Complete              │
         └──────────────────────────────────┘
                                            ↓
                                     ┌─────────────┐
                                     │ Workflow 2  │
                                     │   STARTS    │
                                     └──────┬──────┘
                                            │
                                            ↓
                                     ┌─────────────┐
                                     │ Checkout    │
                                     │ main@DEF456 │← New base!
                                     └──────┬──────┘
                                            │
                                            ↓
                                     ┌─────────────┐
                                     │ Fetch main  │
                                     │ (DEF456)    │
                                     │ No changes  │
                                     └──────┬──────┘
                                            │
                                            ↓
                                     ┌─────────────┐
                                     │ Add file:   │
                                     │ issue_101.  │
                                     │ json        │
                                     └──────┬──────┘
                                            │
                                            ↓
                                     ┌─────────────┐
                                     │ Create PR 2 │
                                     │ base: DEF456│← Updated!
                                     └──────┬──────┘
                                            │
                                            ↓
                                     ┌─────────────┐
                                     │ PR 2 Merges │
                                     │ main@GHI789 │
                                     │             │
                                     │ ✅ Success  │
                                     └─────────────┘
```

## Key Components

### 1. Concurrency Group

```yaml
concurrency:
  group: learning-discussions-${{ github.ref }}
  cancel-in-progress: false
```

**Effect**: Workflows with same group don't run simultaneously
- First workflow: Starts immediately
- Second workflow: Waits in queue
- Third workflow: Also waits

### 2. Pull-Before-Push

```bash
# Before creating PR
git fetch origin main      # Get latest commits
git merge origin/main      # Merge into branch
```

**Effect**: Always working from latest main
- Workflow 1: Merges from main@ABC
- Workflow 2: Sees main@DEF (includes Workflow 1's changes)
- No conflicts because different base

### 3. Conflict Resolution

```bash
git merge origin/main --no-edit || {
  # If merge fails
  git checkout --ours learnings/
  git add learnings/
  git commit --no-edit
}
```

**Effect**: Automatic resolution if needed
- Usually not needed (different files)
- If needed, keeps our new learning data
- Safe because files are timestamped

## Data Flow

### Learning Data Structure

```
learnings/discussions/
├── issue_100_20251119_013300.json    ← Workflow 1
├── issue_100_20251119_013300.md      ← Workflow 1
├── issue_101_20251119_013310.json    ← Workflow 2 (10 sec later)
├── issue_101_20251119_013310.md      ← Workflow 2
└── consolidated_learnings.json       ← Both update
```

**Why no conflicts**:
- Different issue numbers → Different filenames
- Timestamps ensure uniqueness
- consolidated_learnings.json merged with `--ours` if needed

## Workflow States

### Concurrency State Machine

```
┌─────────────┐
│   QUEUED    │ ← Workflow waiting for its turn
└──────┬──────┘
       │
       │ Previous workflow completes
       ↓
┌─────────────┐
│   RUNNING   │ ← Workflow actively executing
└──────┬──────┘
       │
       │ Workflow finishes
       ↓
┌─────────────┐
│  COMPLETED  │ ← Next queued workflow can start
└─────────────┘
```

### GitHub Actions Queue

```
Group: learning-discussions

┌────────────────────────────────┐
│ Currently Running:             │
│ self-documenting-ai.yml #1234  │
└────────────────────────────────┘
         ↑
         │ Blocks
         ↓
┌────────────────────────────────┐
│ Queued (waiting):              │
│ 1. self-doc-enhanced.yml #1235 │
│ 2. self-documenting-ai.yml #1236│
└────────────────────────────────┘
```

## Benefits Visualized

### Before: High Conflict Rate

```
10 Issues Close → 10 Workflows Start → 5-8 Conflicts ❌
```

### After: Zero Conflicts

```
10 Issues Close → 10 Workflows Queue → All Merge ✅
```

## Monitoring

### What to Watch

```
GitHub Actions Tab
├── Workflow runs should show:
│   ├── Some "Running" (active)
│   └── Some "Queued" (waiting)
│
Pull Requests
├── All learning PRs should:
│   ├── Merge successfully
│   └── Show "No conflicts"
│
learnings/discussions/
└── All learning files should:
    ├── Have sequential timestamps
    └── No duplicates or overwrites
```

## Success Indicators

✅ **No "Merge conflict" messages** in PR checks
✅ **Sequential execution** visible in Actions tab
✅ **All learning data captured** in learnings directory
✅ **100% auto-merge rate** for learning PRs
✅ **Queue length &lt; 5** (typical scenario)

---

*Visual guide created by **@APIs-architect** for the learning workflow merge conflict resolution*
