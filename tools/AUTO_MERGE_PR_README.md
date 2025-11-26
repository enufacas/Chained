# Auto-Merge PR Script - README

## Overview

`auto-merge-pr.sh` is the **single source of truth** for PR auto-merge logic in the Chained repository. It encapsulates all eligibility checks and merge execution in one deterministic script.

## Why This Script Exists

The meta-coordinator system needed a reliable, deterministic way to:
1. Check if a PR is eligible for auto-merge
2. Handle draft→ready transitions safely
3. Execute merge with proper fallback
4. Provide clear feedback on why PRs are/aren't eligible

**Problem Solved:** Previous implementation had eligibility logic scattered across multiple locations (workflow, agent instructions, helper scripts) leading to inconsistent behavior and non-deterministic outcomes.

## Usage

### Basic Usage
```bash
# Check and merge a PR
export GH_TOKEN="your_token"
./tools/auto-merge-pr.sh 123

# Dry run (no changes)
./tools/auto-merge-pr.sh 123 --dry-run

# JSON output for programmatic use
./tools/auto-merge-pr.sh 123 --json
```

### Exit Codes
- `0` - PR was merged successfully
- `1` - PR not eligible (see output for reason)
- `2` - Merge failed (PR was eligible but merge command failed)
- `3` - Usage error

## Eligibility Criteria

The script checks 6 criteria in order:

### 1. PR State (MUST be OPEN)
- Closed PRs (including closed drafts) automatically fail
- Merged PRs automatically fail

### 2. WIP Markers (BLOCKS regardless of draft status)
- Checks title for: `[WIP]`, `WIP:`, `[DNM]`, `[do not merge]`, etc.
- **Critical:** This check happens BEFORE marking draft as ready
- Prevents WIP PRs from being processed even if marked ready

### 3. Trusted Author (Security requirement)
- Repository owner always trusted
- Copilot/GitHub Actions bots always trusted
- All other authors blocked

### 4. Draft Status (Handled automatically)
- Draft PRs without WIP markers are marked as ready
- Waits 5 seconds for GitHub to calculate merge status
- Updates mergeable status after marking ready
- Further retries handled in Check 5 if status still UNKNOWN

### 5. Mergeable Status (with intelligent retry)
- `MERGEABLE` → passes
- `CONFLICTING` → fails (has merge conflicts)
- `UNKNOWN` → retries up to 4 times with progressive backoff (5s, 8s, 12s, 15s = 40s total)
- **Retry logic:** Waits for GitHub to finish calculating merge status
- **Graceful handling:** If still UNKNOWN after 40s, fails with helpful message

### 6. CI Checks
- All checks must pass OR no checks configured
- Unavailable checks treated as passed

## Key Decisions

### Why Progressive Backoff for UNKNOWN Status?
**Problem:** GitHub's mergeable status calculation can be slow, especially for PRs with complex branch states. Immediate rejection meant many eligible PRs were skipped unnecessarily.

**Solution:** 
- Retry up to 4 times with progressive backoff: 5s → 8s → 12s → 15s (40s total)
- Gives GitHub adequate time to calculate merge status
- Reduces false negatives from temporary UNKNOWN status
- More graceful error messages when status truly unavailable

### Why Check WIP Before Marking Ready?
**Problem:** Original logic marked drafts ready first, then checked WIP markers. This could process WIP PRs incorrectly.

**Solution:** Check WIP markers in Step 2, BEFORE marking ready in Step 4. Explicit note that WIP check passed before marking ready.

### Why 3 Second Wait After Marking Ready?
**Problem:** GitHub returns `UNKNOWN` mergeable status for drafts until marked ready. 2 seconds wasn't always enough.

**Solution:** Increased to 3 seconds for more reliable status updates. Added explicit status logging to debug when more time is needed.

### Why Squash Merge with Branch Delete?
**Decision:** Keep main branch history clean while preserving PR discussions. Branch cleanup prevents clutter.

**Fallback:** If immediate merge fails, enable auto-merge (queued). PR merges when checks complete.

## Integration

### From Workflow
```yaml
- name: Auto-merge eligible PRs
  env:
    GH_TOKEN: ${{ secrets.COPILOT_PAT }}
  run: |
    for pr_num in $(gh pr list --json number --jq '.[].number'); do
      ./tools/auto-merge-pr.sh $pr_num || true
    done
```

### From Agent
```bash
# In meta-coordinator-system agent
export GH_TOKEN="$COPILOT_PAT"

# Get list of PRs
mergeable_prs=$(gh pr list --json number,mergeable \
  --jq '.[] | select(.mergeable == "MERGEABLE") | .number')

# Attempt auto-merge
for pr in $mergeable_prs; do
  echo "Checking PR #$pr..."
  if ./tools/auto-merge-pr.sh $pr; then
    echo "✅ Merged PR #$pr"
  else
    echo "⏭️  Skipped PR #$pr (not eligible)"
  fi
done
```

## Comparison with check-pr-merge-eligibility.sh

| Feature | check-pr-merge-eligibility.sh | auto-merge-pr.sh |
|---------|------------------------------|-------------------|
| Purpose | Check eligibility only | Check + execute merge |
| Merge execution | No | Yes |
| Success comment | No | Yes |
| Dry run mode | No | Yes |
| JSON output | No | Yes (future) |
| Use case | Programmatic checks | Complete automation |

**When to use which:**
- **check-pr-merge-eligibility.sh:** When you only need to check eligibility (e.g., reporting, filtering)
- **auto-merge-pr.sh:** When you want to check AND merge in one operation

## Future Enhancements

1. **JSON Output:** Structured output for programmatic consumption
   ```json
   {
     "eligible": true,
     "reason": "",
     "action": "merged_immediate",
     "checks": {
       "state": "pass",
       "wip": "pass",
       "author": "pass",
       "draft": "converted",
       "mergeable": "pass",
       "ci": "pass"
     }
   }
   ```

2. **Batch Mode:** Process multiple PRs efficiently
3. **Webhook Integration:** React to PR events in real-time

## Troubleshooting

### "Mergeable status is UNKNOWN"
**Cause:** GitHub still calculating merge status (usually for recently updated PRs)

**Solution:** 
- Script now automatically retries with progressive backoff (up to 40s)
- If still UNKNOWN after retries, PR will be checked again in next run (every 2 hours)
- Manual intervention rarely needed unless PR has complex merge requirements

### "Failed to mark ready"
**Cause:** Permission issues or PR already ready

**Solution:** Check bot permissions and verify PR state manually

### "Merge failed"
**Cause:** Merge was eligible but GitHub rejected the merge

**Solution:** Check for:
- Branch protection rules blocking merge
- Required reviewers not met
- Status checks changed between eligibility and merge

## Testing

```bash
# Test with dry run
./tools/auto-merge-pr.sh 123 --dry-run

# Test each exit code
./tools/auto-merge-pr.sh 123        # Should exit 0 if eligible
./tools/auto-merge-pr.sh 456        # Should exit 1 if not eligible
./tools/auto-merge-pr.sh invalid    # Should exit 3 (usage error)
```

## Related Files

- `.github/agents/meta-coordinator-system.md` - Agent using this script
- `tools/check-pr-merge-eligibility.sh` - Eligibility check only
- `tools/cleanup-stale-prs.sh` - Stale PR cleanup
- `.github/workflows/meta-coordinator.yml` - Workflow integration
