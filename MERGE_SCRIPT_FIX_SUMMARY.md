# Merge Script Fix Summary

## Problem Statement
The merge script was not merging PRs as expected. Reference workflow run: https://github.com/enufacas/Chained/actions/runs/19707903159/job/56460248564

Example PRs that should have been merged:
- PR #3125: Daily Learning Reflection (github-actions[bot], mergeable: true, clean state)
- PR #3097: Fix direct assignment test suite (Copilot, mergeable: true, unstable state)

## Root Cause Analysis

### Issue 1: JQ Syntax Error (PRIMARY BLOCKER)
**Error Message:** `accepts at most 1 arg(s), received 2`

**Location:** 
- `tools/auto-merge-pr.sh` lines 155, 159, 162
- `tools/check-pr-merge-eligibility.sh` lines 113, 127, 131

**Cause:**
```bash
# INCORRECT - gh CLI's --jq doesn't accept -r as separate flag
mergeable=$(gh pr view "$PR_NUM" --json mergeable --jq -r '.mergeable')
```

When using `gh --jq`, the value after `--jq` is passed directly to jq's filter expression. By adding `-r` after `--jq`, the command became:
```bash
gh pr view 123 --json mergeable --jq '-r' '.mergeable'
```

jq then received `-r` as the first argument and `.mergeable` as the second argument, causing the error "accepts at most 1 arg(s), received 2".

**Fix:**
```bash
# CORRECT - pipe through jq separately
mergeable=$(gh pr view "$PR_NUM" --json mergeable | jq -r '.mergeable')
```

**Impact:**
- Blocked PRs #3147 and #3145 from merging in the referenced workflow run
- Any draft PR that was marked as ready would trigger this error
- Error occurred in 2 out of 10 PRs processed (20% failure rate)

### Issue 2: Insufficient Wait After Marking Draft as Ready

**Location:** `tools/auto-merge-pr.sh` line 153

**Cause:**
After marking a draft PR as ready, the script only waited 3 seconds before checking the mergeable status. GitHub's API can take longer to recalculate the status, resulting in UNKNOWN status.

**Fix:**
```bash
# Increased wait time from 3s to 5s
sleep 5

# Added retry logic
if [ "${mergeable}" = "UNKNOWN" ]; then
  echo "  → Status still UNKNOWN, waiting 3 more seconds..."
  sleep 3
  mergeable=$(gh pr view "$PR_NUM" --json mergeable | jq -r '.mergeable')
fi
```

**Impact:**
- Reduced transient UNKNOWN status failures
- Better handling of GitHub API timing

### Issue 3: Many PRs with UNKNOWN Status (EXPECTED BEHAVIOR)

**Observation:** 20 out of 31 PRs had UNKNOWN mergeable status

**Cause:**
GitHub's API returns UNKNOWN for:
- Newly created PRs (status not yet calculated)
- PRs with pending CI checks
- PRs where GitHub is still computing mergeable status

**Status:** This is normal operation. The workflow runs every 2 hours, so PRs will be picked up on subsequent runs once their status is calculated.

### Issue 4: Only 10 PRs Processed Per Run (EXPECTED BEHAVIOR)

**Location:** `.github/workflows/meta-coordinator.yml` line 201

**Rationale:**
```yaml
if [ $pr_count -gt 10 ]; then
  echo "⚠️  Stopping after 10 PRs to avoid timeout"
  break
fi
```

The workflow has a 5-minute timeout. Processing 10 PRs (with potential draft marking, wait times, and merge operations) keeps the workflow within this limit.

**Impact on PR #3125 and #3097:**
- These PRs were eligible but beyond the 10-PR limit in the referenced run
- They will be processed in subsequent runs
- With the jq fix, more PRs will successfully merge, reducing the queue

## Changes Made

### 1. tools/auto-merge-pr.sh
- Fixed 3 instances of `--jq -r` pattern (lines 155, 159, 162)
- Increased wait time after marking ready: 3s → 5s
- Added retry logic for UNKNOWN status (additional 3s wait)

### 2. tools/check-pr-merge-eligibility.sh
- Fixed 3 instances of `--jq -r` pattern (lines 113, 127, 131)
- Ensures consistency across all merge-related scripts

## Expected Improvements

### Immediate (Next Workflow Run)
1. **Zero jq Errors:** No more "accepts at most 1 arg(s), received 2" failures
2. **Higher Success Rate:** Draft PRs more likely to merge successfully
3. **PR #3125 Merged:** Should be processed and merged (fully eligible)
4. **PRs #3147, #3145 Merged:** Should merge successfully (were blocked by jq error)

### Ongoing
1. **Reduced UNKNOWN Failures:** Better handling with retry logic
2. **Consistent Behavior:** Both scripts now use same approach
3. **Better Queue Processing:** As more PRs merge, older PRs get processed faster

## Why PR #3097 May Not Merge

**Status:** `mergeable_state: unstable`

This indicates:
- PR has merge conflicts, OR
- PR has failing CI checks, OR
- PR has blocking issues

The script will correctly reject this PR until:
1. Conflicts are resolved
2. CI checks pass
3. Any blocking issues are addressed

## Verification Steps

```bash
# Verify no more --jq -r patterns exist
grep -r "\-\-jq.*\-r" tools/*.sh
# Should return empty

# Test script syntax
bash -n tools/auto-merge-pr.sh
bash -n tools/check-pr-merge-eligibility.sh
# Both should succeed

# Test jq command
echo '{"mergeable":"MERGEABLE"}' | jq -r '.mergeable'
# Should output: MERGEABLE
```

## Monitoring Recommendations

1. **Next 2 Workflow Runs:** Monitor for improvements
2. **Error Rate:** Should drop to ~0% for jq errors
3. **Merge Rate:** Should increase as backlog clears
4. **UNKNOWN Count:** Should remain ~50% (normal for 2-hour cycle)

## Documentation

- This fix documented in PR comments
- Workflow behavior explained in meta-coordinator.yml
- Script behavior documented in inline comments

## Related Files

- `.github/workflows/meta-coordinator.yml` - Main orchestrator
- `tools/auto-merge-pr.sh` - Primary merge script (FIXED)
- `tools/check-pr-merge-eligibility.sh` - Eligibility checker (FIXED)

## Timeline

- **Issue Reported:** 2025-11-26
- **Workflow Run Analyzed:** 19707903159 (2025-11-26 14:54 UTC)
- **Root Cause Identified:** jq syntax error + timing issues
- **Fix Applied:** 2025-11-26 15:XX UTC
- **Next Test:** Next meta-coordinator run (~2 hours from fix)

## Conclusion

The primary blocker was a **gh CLI + jq syntax error** that prevented draft PRs from being successfully merged. This affected 20% of PR processing attempts in the analyzed workflow run.

With the fix applied:
- ✅ Syntax error eliminated
- ✅ Better handling of UNKNOWN status  
- ✅ Consistent behavior across scripts
- ✅ PRs #3125, #3097 will be processed in next runs

The 10-PR per-run limit and 2-hour cycle are **working as designed** to prevent workflow timeouts while ensuring all PRs eventually get processed.
