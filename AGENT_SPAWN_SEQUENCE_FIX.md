# Agent Spawn Sequence Fix

## Problem Statement

Issue #424 identified race condition and sequence problems in the agent spawning system where:
- Work issues were created and immediately assigned to Copilot
- Assignment happened before the agent's spawn PR was merged
- This caused Copilot to work on agents that weren't yet "active" in the system
- Issue descriptions said "wait for PR to merge" but Copilot was assigned immediately

## Root Cause

The `copilot-graphql-assign.yml` workflow triggers on `issues: types: [opened]`, which runs immediately when any issue is created - including agent work issues that need to wait for their spawn PR to merge first.

**Broken Sequence:**
```
1. agent-spawner creates spawn PR (#423) + work issue (#424)
2. work issue created → copilot-graphql-assign triggered immediately
3. Copilot assigned and starts working on #424
4. auto-review merges spawn PR #423 (may be slower)
5. ❌ Copilot worked before agent was "active"
```

## Solution

Implemented a **three-layer protection system** to prevent premature assignment:

### Layer 1: spawn-pending Label

- **When created**: Agent work issues get `spawn-pending` label at creation
- **Purpose**: Clear visual indicator that assignment should wait
- **Removed**: After spawn PR merges

### Layer 2: Issue Body Check

- **Detection**: Script checks for "⚠️ Agent Spawn Sequence" marker
- **Extraction**: Extracts spawn PR number from issue body
- **Verification**: Checks if spawn PR is still open via GitHub API
- **Action**: Skips assignment if spawn PR is open, adds explanatory comment

### Layer 3: Workflow Trigger

- **After merge**: Auto-review workflow removes `spawn-pending` label
- **Trigger**: Dispatches `copilot-graphql-assign` workflow for the specific issue
- **Comments**: Adds status updates to work issue

## Fixed Sequence

```
1. agent-spawner creates spawn PR (#423) + work issue (#424) with spawn-pending label
2. copilot-graphql-assign skips #424 (has spawn-pending + checks spawn PR status)
3. auto-review workflow merges spawn PR #423
4. After merge: auto-review removes spawn-pending & triggers assignment
5. copilot-graphql-assign assigns Copilot to #424
6. ✅ Copilot works on now-active agent
```

## Changes Made

### 1. `.github/workflows/agent-spawner.yml`

- Added `spawn-pending` label creation
- Work issues now created with label: `agent-system,agent-work,spawn-pending`
- Updated issue text: "after spawn PR merges" instead of "for implementation"

```yaml
create_label_if_missing "spawn-pending" "d4c5f9" "Waiting for agent spawn PR to merge"
```

```yaml
--label "agent-system,agent-work,spawn-pending"
```

### 2. `.github/workflows/auto-review-merge.yml`

- Detects agent spawn PRs via `agent-system` label
- After merge:
  - Removes `spawn-pending` label from linked work issue
  - Triggers `copilot-graphql-assign` workflow for that specific issue
  - Adds status update comments

```bash
gh issue edit ${linked_issue} --remove-label "spawn-pending"
gh workflow run copilot-graphql-assign.yml -f issue_number="${linked_issue}"
```

### 3. `tools/assign-copilot-to-issue.sh`

Enhanced with multiple checks:

**Check 1: spawn-pending label**
```bash
if echo "$issue_labels" | grep -q "spawn-pending"; then
  echo "⏭️  Skipping - has spawn-pending label (waiting for spawn PR to merge)"
  continue
fi
```

**Check 2: Issue body marker + PR status**
```bash
if echo "$issue_body" | grep -q "⚠️ Agent Spawn Sequence"; then
  # Extract spawn PR number
  spawn_pr_number=$(echo "$issue_body" | grep -oP 'PR #\K\d+' | head -1)
  
  # Check if spawn PR is still open
  pr_state=$(gh pr view "$spawn_pr_number" --json state --jq '.state')
  
  if [ "$pr_state" = "OPEN" ]; then
    echo "⏳ Spawn PR still open, skipping assignment"
    continue
  fi
fi
```

**Check 3: Skip agent-system (but not agent-work)**
```bash
if echo "$issue_labels" | grep -q "agent-system" && ! echo "$issue_labels" | grep -q "agent-work"; then
  echo "⏭️  Skipping - agent-system issues handled by spawner"
  continue
fi
```

### 4. `test_spawn_sequence.py`

Created comprehensive test suite with 11 tests:

**Unit Tests:**
- Label detection logic
- Spawn sequence marker detection
- PR number extraction from issue body
- Label logic for agent-work vs agent-system
- State transitions in spawn sequence

**Integration Tests:**
- Label creation in spawner workflow
- Label added to work issues
- Label removal in auto-review workflow
- Spawn-pending check in assignment script
- Spawn PR status verification
- Assignment trigger after merge

All tests passing ✅

## How It Works

### Scenario 1: New Agent Spawn

1. **Agent Spawner** runs (scheduled/manual)
   - Creates spawn PR with agent registration
   - Creates work issue with `spawn-pending` label
   - Links PR to issue in comments

2. **Copilot Assignment** workflow triggered (issue opened)
   - Sees `spawn-pending` label → skips
   - Sees "Agent Spawn Sequence" marker → checks PR status
   - PR is open → skips with explanatory comment

3. **Auto-Review** workflow processes spawn PR
   - Detects `agent-system` label
   - Merges PR (agent now active)
   - Removes `spawn-pending` from work issue
   - Triggers assignment workflow for work issue

4. **Copilot Assignment** re-runs (workflow_dispatch)
   - No `spawn-pending` label → proceeds
   - Checks PR status → merged → proceeds
   - Assigns Copilot to work issue
   - Agent starts working ✅

### Scenario 2: Scheduled Assignment Check

Every 3 hours, `copilot-graphql-assign` scans all open issues:

- Sees agent-work issue with `spawn-pending` → skips
- Sees agent-work issue without `spawn-pending`:
  - Checks for spawn marker in body
  - If found, verifies PR is merged
  - Only assigns if agent is active

## Benefits

1. **No Race Conditions**: Assignment only happens after spawn completes
2. **Clear State**: `spawn-pending` label shows issues waiting for spawn
3. **Fail-Safe**: Multiple layers ensure spawn completes before assignment
4. **Informative**: Comments explain why assignment is waiting
5. **Automatic**: No manual intervention needed
6. **Testable**: Comprehensive test coverage validates behavior

## Migration

For existing agent-work issues created before this fix:

- They won't have `spawn-pending` label
- The issue body check (Layer 2) provides backward compatibility
- Script checks spawn PR status before assigning
- No manual cleanup needed

## Future Enhancements

Possible improvements:

1. Add spawn PR status to issue labels (e.g., `spawn-in-progress`, `spawn-complete`)
2. Dashboard showing spawn pipeline status
3. Metrics on spawn → assignment time
4. Automated cleanup of failed/stalled spawns

## Testing

Run the test suite:

```bash
python3 test_spawn_sequence.py
```

Expected output:
```
test_agent_work_label_logic ... ok
test_sequence_flow_states ... ok
test_spawn_pending_label_detection ... ok
test_spawn_pr_number_extraction ... ok
test_spawn_sequence_marker_detection ... ok
test_assignment_trigger_after_merge ... ok
test_label_added_to_issue ... ok
test_label_creation_in_spawner ... ok
test_label_removal_in_auto_review ... ok
test_spawn_pending_check_in_script ... ok
test_spawn_pr_status_check ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.002s

OK
```

## References

- Original Issue: #424
- Example Spawn PR: #423
- Related Workflows:
  - `.github/workflows/agent-spawner.yml`
  - `.github/workflows/auto-review-merge.yml`
  - `.github/workflows/copilot-graphql-assign.yml`
- Assignment Script: `tools/assign-copilot-to-issue.sh`
- Test Suite: `test_spawn_sequence.py`
