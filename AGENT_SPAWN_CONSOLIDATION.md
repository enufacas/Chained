# Agent Spawn Workflow Consolidation

## Overview

This document describes the consolidation of agent registration and assignment workflows to eliminate conflicts and duplication.

## Problem Statement

Prior to this consolidation, there was overlap and potential conflict between two workflows:

1. **agent-spawner.yml** - Spawns new agents and creates their first work issue
2. **copilot-graphql-assign.yml** - Automatically assigns Copilot to ALL newly created issues

### The Conflict

When the agent-spawner workflow created a new agent's welcome/work issue:

1. ✅ Spawner registers the agent in registry.json
2. ✅ Spawner creates the agent profile
3. ✅ Spawner creates the work issue with `agent-system` label
4. ✅ Spawner assigns the issue to Copilot
5. ⚠️ **copilot-graphql-assign workflow triggers** (because issue was opened)
6. ❌ **copilot-graphql-assign tries to assign Copilot again** (duplicate work)
7. ❌ **copilot-graphql-assign may add duplicate comments**
8. ❌ **Race conditions possible**

## Solution

All agent-related registration and assignment now happens exclusively in the **agent-spawner workflow**.

### Changes Made

#### 1. Updated copilot-graphql-assign.yml

Added a condition to skip issues with the `agent-system` label:

```yaml
jobs:
  assign-to-copilot:
    runs-on: ubuntu-latest
    if: |
      (github.event_name == 'issues' && !contains(github.event.issue.labels.*.name, 'agent-system')) ||
      github.event_name == 'schedule' ||
      github.event_name == 'workflow_dispatch'
```

**Result**: The workflow no longer triggers for agent-system issues during the `issues: opened` event.

#### 2. Updated assign-copilot-to-issue.sh

Added a check at the beginning of issue processing:

```bash
# Skip agent-system issues as they are handled by agent-spawner workflow
issue_labels=$(gh issue view "$issue_number" --repo "$GITHUB_REPOSITORY" --json labels --jq '.labels[].name')
if echo "$issue_labels" | grep -q "agent-system"; then
  echo "⏭️  Skipping issue #$issue_number - agent-system issues are handled by agent-spawner workflow"
  already_assigned_count=$((already_assigned_count + 1))
  continue
fi
```

**Result**: When running on schedule or manual dispatch, the script skips agent-system issues.

### Workflow Responsibilities

#### agent-spawner.yml (Primary Agent Workflow)

**Handles**:
- ✅ Agent registration in registry.json
- ✅ Agent profile creation
- ✅ PR creation with agent files
- ✅ Welcome/work issue creation with `agent-system` label
- ✅ Copilot assignment for agent issues

**When**: Runs on schedule (every 3 hours) or manual trigger

#### copilot-graphql-assign.yml (General Issue Assignment)

**Handles**:
- ✅ Copilot assignment for regular project issues
- ✅ Intelligent agent matching for non-agent-system issues
- ✅ Adding appropriate agent labels to regular issues

**Skips**:
- ❌ Issues with `agent-system` label
- ❌ Issues already assigned to Copilot

**When**: Runs on issue opened event (except agent-system), schedule, or manual trigger

## Benefits

1. **No Duplicate Work**: Each issue is processed by exactly one workflow
2. **No Race Conditions**: Agent issues are handled atomically in one workflow
3. **Clear Separation**: Agent lifecycle is clearly separated from general issue assignment
4. **Better Performance**: Fewer unnecessary workflow runs and API calls
5. **Easier Debugging**: Clear ownership of each step in the agent lifecycle

## Testing

Comprehensive tests were added in `test_agent_spawn_consolidation.py`:

- ✅ copilot-graphql-assign skips agent-system issues
- ✅ agent-spawner creates issues with agent-system label
- ✅ agent-spawner handles registration and assignment
- ✅ assign-copilot-to-issue.sh skips agent-system issues
- ✅ No duplicate assignment logic

Run tests with:
```bash
python3 test_agent_spawn_consolidation.py
```

## Migration Notes

This consolidation is **backward compatible**:

- Existing agent-system issues continue to work
- Regular issues continue to be assigned by copilot-graphql-assign
- No manual intervention required
- No data migration needed

## Future Considerations

- If adding new workflows that process issues, check for `agent-system` label to avoid conflicts
- If modifying agent spawn workflow, ensure all steps remain consolidated
- Consider similar consolidation for other workflow types if conflicts arise

## Related Files

- `.github/workflows/agent-spawner.yml` - Primary agent lifecycle workflow
- `.github/workflows/copilot-graphql-assign.yml` - General Copilot assignment
- `tools/assign-copilot-to-issue.sh` - Issue assignment script
- `test_agent_spawn_consolidation.py` - Consolidation tests

## Summary

Agent registration, profile creation, issue creation, and Copilot assignment are now fully consolidated in the agent-spawner workflow. The copilot-graphql-assign workflow correctly skips agent-system issues to prevent conflicts and duplication.
