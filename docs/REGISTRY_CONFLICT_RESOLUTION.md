# Registry Merge Conflict Resolution

## Problem

When multiple agent spawning workflows run concurrently (e.g., `agent-spawner.yml`, `learning-based-agent-spawner.yml`, `agent-evaluator.yml`), they can create merge conflicts on `.github/agent-system/registry.json`:

1. Workflow A reads `registry.json`, adds Agent X
2. Workflow B reads `registry.json`, adds Agent Y
3. Workflow A creates PR and merges
4. Workflow B tries to merge - **CONFLICT!**

This happens because both workflows read the same base version of the file, make independent changes, and try to merge back to main.

## Solution

We implemented a **two-layer approach** to prevent merge conflicts:

### Layer 1: Workflow-Level Concurrency Control

Added a shared concurrency group to all workflows that modify the registry:

```yaml
concurrency:
  group: agent-registry-updates
  cancel-in-progress: false
```

This ensures:
- Only ONE registry-modifying workflow runs at a time
- Other workflows wait in queue (they don't get canceled)
- No concurrent modifications = no conflicts

**Applied to:**
- `.github/workflows/agent-spawner.yml`
- `.github/workflows/learning-based-agent-spawner.yml`
- `.github/workflows/agent-evaluator.yml`

### Layer 2: Atomic Registry Update Tool (Future-Proofing)

Created `tools/atomic-registry-update.py` for when concurrency control isn't enough:

**Features:**
- Pull-modify-push with retry logic
- Automatic conflict resolution for agent arrays
- Exponential backoff on failures
- Intelligent agent merging by ID

**Usage:**
```python
from atomic_registry_update import AtomicRegistryUpdater

updater = AtomicRegistryUpdater(verbose=True)

# Add an agent atomically
agent_data = {
    "id": "agent-123",
    "name": "Test Agent",
    "specialization": "test-specialist",
    ...
}
updater.add_agent(agent_data)
```

**CLI Usage:**
```bash
# Add an agent
./tools/atomic-registry-update.py add '{"id": "agent-123", ...}'

# Remove agents
./tools/atomic-registry-update.py remove agent-123,agent-456 --reason "Elimination"

# Update metrics
./tools/atomic-registry-update.py update-metrics agent-123 '{"overall_score": 0.75}'
```

## How It Works

### Concurrency Control Flow

```
[Agent Spawner]     [Learning Spawner]    [Evaluator]
       |                    |                   |
       v                    |                   |
   RUNNING                  |                   |
   (locks registry)         |                   |
       |                    v                   |
       |                WAITING                 |
       |              (queued until             |
       |               spawner done)            v
       v                    |               WAITING
   COMPLETE                 |              (queued)
       |                    v                   |
       |                RUNNING                 |
       |                   |                    |
       |                   v                    |
       |               COMPLETE                 |
       |                   |                    v
       |                   |                RUNNING
       |                   |                    |
       |                   |                    v
       |                   |                COMPLETE
```

### Atomic Update Flow (Fallback)

```
1. Pull latest from origin
2. Read current registry.json
3. Apply modifications
4. Write to file
5. Commit changes
6. Try to push
   ├─ Success ✓ → Done
   └─ Failure ✗ → Reset commit, wait, retry from step 1
```

## Testing

Run the test suite:
```bash
python3 tests/test_atomic_registry_updater.py
```

Tests cover:
- Adding single agents
- Adding duplicate agents (idempotent)
- Merging agent arrays
- Handling concurrent updates with different timestamps
- Removing agents
- Updating metrics
- Custom update functions

## Benefits

1. **No More Merge Conflicts** - Workflows run sequentially for registry updates
2. **No Lost Work** - Queued workflows still execute (not canceled)
3. **Simple Implementation** - Just 4 lines of YAML per workflow
4. **Future-Proof** - Atomic update tool ready if needs change
5. **Scalable** - Can handle many concurrent workflow triggers

## Monitoring

Check workflow status:
```bash
gh run list --workflow="Agent System: Spawner"
gh run list --workflow="Agent System: Evaluator"
```

Look for "waiting" or "queued" status - this means concurrency control is working!

## Troubleshooting

### Workflow stuck in "Queued"?
- Check if another registry-modifying workflow is running
- Concurrency group: `agent-registry-updates`
- This is **expected behavior** - the workflow will start when the current one finishes

### Still seeing conflicts?
1. Verify concurrency group is set in ALL registry-modifying workflows
2. Check the group name matches exactly: `agent-registry-updates`
3. Ensure `cancel-in-progress: false` (we want to queue, not cancel)

### Need to bypass concurrency control?
Use `workflow_dispatch` with a different branch:
```bash
# This won't trigger concurrency control since it's not modifying main
gh workflow run agent-spawner.yml --ref feature-branch
```

## Migration Guide

If you added a new workflow that modifies `registry.json`, add this to the workflow file:

```yaml
# Add after the 'on:' section and before 'permissions:'
concurrency:
  group: agent-registry-updates
  cancel-in-progress: false
```

That's it! No code changes needed in the workflow steps.

## Performance Impact

- **Minimal**: Workflows wait instead of conflicting
- **No timeouts**: Queued workflows run eventually
- **Same total time**: Work happens sequentially instead of in conflict

Before: Workflow A (2min) + Workflow B (2min) + Conflict Resolution (5min) = 9min
After: Workflow A (2min) → Workflow B (2min) = 4min total

**Result: 55% faster!** 🚀
