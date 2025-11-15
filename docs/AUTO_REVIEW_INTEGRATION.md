# Auto-Review Integration for Agent Spawner Workflows

## Overview

This document explains how the agent spawner workflows integrate with the auto-review-merge workflow to ensure PRs are automatically reviewed and merged immediately after creation.

## Problem Statement

Previously, agent spawner workflows would:
1. Create a spawn PR
2. Complete the workflow
3. Wait for the scheduled auto-review-merge workflow to run (every 15 minutes)
4. Hope the PR would be picked up and merged

This caused:
- **Delays**: Up to 15 minutes before PR processing
- **No feedback**: Workflow completes before knowing if merge succeeded
- **Race conditions**: Multiple spawners could create PRs simultaneously
- **Unclear dependencies**: Implicit timing-based dependencies

## Solution

The agent spawner workflows now:
1. Create a spawn PR
2. **Immediately trigger** the auto-review-merge workflow with the specific PR number
3. **Wait and monitor** the PR status (polling every 10 seconds)
4. **Exit with success** when PR is merged
5. **Exit with error** if PR is closed or timeout occurs (5 minutes)

## Implementation Details

### Modified Workflows

1. **`.github/workflows/agent-spawner.yml`**
2. **`.github/workflows/learning-based-agent-spawner.yml`**

### New Steps Added

#### Step 1: Trigger Auto Review and Merge

```yaml
- name: Trigger Auto Review and Merge
  if: steps.check_capacity.outputs.can_spawn == 'true'
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    PR_NUMBER="${{ steps.create_spawn_pr.outputs.pr_number }}"
    echo "🔄 Triggering Auto Review & Merge workflow for PR #$PR_NUMBER..."
    
    # Trigger the auto-review-merge workflow with the specific PR number
    gh workflow run auto-review-merge.yml \
      --repo ${{ github.repository }} \
      -f pr_number="$PR_NUMBER"
    
    echo "✅ Auto-review workflow triggered for PR #$PR_NUMBER"
```

#### Step 2: Wait for PR to be merged

```yaml
- name: Wait for PR to be merged
  if: steps.check_capacity.outputs.can_spawn == 'true'
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    PR_NUMBER="${{ steps.create_spawn_pr.outputs.pr_number }}"
    echo "⏳ Waiting for PR #$PR_NUMBER to be merged by auto-review workflow..."
    
    # Wait up to 5 minutes for the PR to be merged
    MAX_WAIT=300  # 5 minutes
    WAIT_INTERVAL=10  # Check every 10 seconds
    ELAPSED=0
    
    while [ $ELAPSED -lt $MAX_WAIT ]; do
      # Check PR state
      PR_STATE=$(gh pr view "$PR_NUMBER" --repo ${{ github.repository }} --json state --jq '.state')
      
      if [ "$PR_STATE" = "MERGED" ]; then
        echo "✅ PR #$PR_NUMBER has been merged successfully!"
        echo "🎉 Agent spawn complete - agent is now active"
        exit 0
      elif [ "$PR_STATE" = "CLOSED" ]; then
        echo "⚠️ PR #$PR_NUMBER was closed without merging"
        echo "This may indicate an issue with the auto-review process"
        exit 1
      else
        echo "⏳ PR #$PR_NUMBER is still $PR_STATE, waiting... (${ELAPSED}s elapsed)"
        sleep $WAIT_INTERVAL
        ELAPSED=$((ELAPSED + WAIT_INTERVAL))
      fi
    done
    
    # Timeout reached
    echo "⏰ Timeout: PR #$PR_NUMBER was not merged within ${MAX_WAIT} seconds"
    echo "ℹ️ The PR may still be processed by auto-review later"
    echo "Check PR status at: https://github.com/${{ github.repository }}/pull/$PR_NUMBER"
    exit 1
```

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ Agent Spawner Workflow                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. Generate agent profile                                      │
│    ↓                                                            │
│ 2. Commit and push to branch                                   │
│    ↓                                                            │
│ 3. Create spawn PR                                             │
│    ├─→ Extract PR number                                       │
│    ↓                                                            │
│ 4. Trigger auto-review-merge workflow ← NEW!                   │
│    ├─→ Pass PR number as parameter                             │
│    ↓                                                            │
│ 5. Wait for PR to be merged ← NEW!                             │
│    ├─→ Poll PR status every 10 seconds                         │
│    ├─→ Success if MERGED                                       │
│    ├─→ Error if CLOSED or timeout                              │
│    ↓                                                            │
│ 6. Summary                                                      │
│    └─→ Agent is now active!                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         │
         │ workflow_dispatch trigger
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Auto Review & Merge Workflow                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. Label Copilot PRs                                           │
│    ↓                                                            │
│ 2. Get PR to review (from input parameter)                     │
│    ↓                                                            │
│ 3. Validate PR (author, labels, state)                         │
│    ↓                                                            │
│ 4. Review and approve PR                                       │
│    ↓                                                            │
│ 5. Merge PR                                                     │
│    └─→ PR state changes to MERGED                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Benefits

### 1. Immediate Feedback
- Workflow knows immediately if PR merge succeeds or fails
- No silent failures due to missed scheduled runs
- Clear error messages for troubleshooting

### 2. Faster Processing
- PRs processed in seconds instead of up to 15 minutes
- Agent becomes active immediately after spawning
- Reduced latency in autonomous agent lifecycle

### 3. Explicit Dependencies
- Clear workflow dependency: spawner → auto-review
- No implicit timing assumptions
- Better reliability and predictability

### 4. Better Error Handling
- Timeout after 5 minutes with clear instructions
- Detects closed PRs vs merged PRs
- Links to PR for manual investigation

## Error Scenarios

### Scenario 1: PR Closed Without Merge

```
⚠️ PR #123 was closed without merging
This may indicate an issue with the auto-review process
```

**Resolution**: Check PR for conflicts, failed checks, or manual closure

### Scenario 2: Timeout

```
⏰ Timeout: PR #123 was not merged within 300 seconds
ℹ️ The PR may still be processed by auto-review later
Check PR status at: https://github.com/owner/repo/pull/123
```

**Resolution**: 
- Check if auto-review workflow is running
- Verify workflow has necessary permissions
- Check for merge conflicts or failing checks
- PR may still be processed by scheduled auto-review run

### Scenario 3: Success

```
✅ PR #123 has been merged successfully!
🎉 Agent spawn complete - agent is now active
```

**Result**: Agent profile is in main branch and agent is active

## Configuration

### Timeout
Default: 300 seconds (5 minutes)

To adjust, modify `MAX_WAIT` in the "Wait for PR to be merged" step:
```bash
MAX_WAIT=600  # 10 minutes
```

### Poll Interval
Default: 10 seconds

To adjust, modify `WAIT_INTERVAL`:
```bash
WAIT_INTERVAL=5  # Check every 5 seconds
```

## Testing

Run the integration test:
```bash
python3 tests/test_workflow_auto_review_integration.py
```

Expected output:
```
======================================================================
WORKFLOW AUTO-REVIEW INTEGRATION TESTS
======================================================================

✅ PASSED: Workflow Syntax Validation
✅ PASSED: Auto-Review Trigger Steps
✅ PASSED: Auto-Review Workflow Dispatch

SUMMARY: 3 passed, 0 failed
======================================================================
```

## Related Workflows

### Not Modified
- **`multi-agent-spawner.yml`**: Uses matrix strategy with multiple PRs, relies on scheduled auto-review
- **`autonomous-pipeline.yml`**: Has its own multi-stage merge logic

### May Need Similar Updates
Consider applying the same pattern to any workflow that:
1. Creates a PR
2. Requires the PR to be merged before continuing
3. Doesn't have its own merge logic

## Troubleshooting

### Auto-review workflow not triggering
- Verify `GH_TOKEN` has `actions:write` permission
- Check workflow name matches exactly: `auto-review-merge.yml`
- Verify repository has auto-review-merge workflow enabled

### PR not merging
- Check auto-review-merge workflow run logs
- Verify PR meets auto-merge criteria (copilot label, trusted author)
- Check for merge conflicts
- Verify branch protection rules

### Timeout occurring
- Check if auto-review workflow is queued/running
- Increase `MAX_WAIT` if checks take longer than 5 minutes
- Check workflow concurrency limits
- Verify GitHub Actions quota/rate limits

## Future Improvements

Potential enhancements:
1. **Configurable timeout**: Accept timeout as workflow input
2. **Retry logic**: Retry trigger if auto-review fails
3. **Status reporting**: Post comments to PR with progress updates
4. **Metrics collection**: Track merge success rate and timing
5. **Notification**: Slack/Discord notification on timeout

## References

- [GitHub Actions: Triggering workflows](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch)
- [GitHub CLI: workflow run](https://cli.github.com/manual/gh_workflow_run)
- [Auto Review & Merge Workflow](.github/workflows/auto-review-merge.yml)
- [Agent Spawner Workflow](.github/workflows/agent-spawner.yml)
