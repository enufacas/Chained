# Draft PR Auto-Merge Fix

## Issue
PRs #3004, #3025, and other draft PRs were not being auto-merged despite meeting all eligibility criteria.

## Root Cause
The auto-merge eligibility script (`tools/check-pr-merge-eligibility.sh`) only marked draft PRs as ready when their `mergeable` status was `UNKNOWN`. Draft PRs that already had `mergeable: MERGEABLE` were being skipped entirely.

## Problem PRs
- **PR #3004**: meta-coordination update (draft, mergeable, hours old)
- **PR #3025**: TypeScript trends learning mission (draft, mergeable, hours old)

Both PRs met all criteria:
- ✅ Open
- ✅ No WIP in title
- ✅ Trusted author (Copilot)
- ✅ Mergeable status: MERGEABLE
- ✅ Draft: true (but this should NOT block)

## Agent Definition Requirement
From `.github/agents/meta-coordinator-system.md` line 1060:
> **Draft PRs:** Always mark as ready before attempting merge (triggers status calculation)

The agent definition clearly states that **ALL** draft PRs should be marked as ready before attempting merge, not just those with UNKNOWN status.

## The Fix

### Before (Incorrect)
```bash
# STEP 4: Handle UNKNOWN mergeable state
if [ "${mergeable}" = "UNKNOWN" ]; then
    if [ "${is_draft}" = "true" ]; then
        gh pr ready "${PR_NUM}"
        # ... wait and re-fetch
    fi
fi
# Then check mergeable status
```

**Problem**: Only draft PRs with UNKNOWN status were being marked as ready.

### After (Correct)
```bash
# STEP 4: Mark draft PRs as ready (ALWAYS)
if [ "${is_draft}" = "true" ]; then
    gh pr ready "${PR_NUM}"
    sleep 2  # Wait for GitHub to recalculate
    mergeable=$(gh pr view "$PR_NUM" --json mergeable --jq -r '.mergeable')
fi

# STEP 5: Check mergeable status
if [ "${mergeable}" = "MERGEABLE" ]; then
    # ...
fi
```

**Solution**: ALL draft PRs are now marked as ready BEFORE checking mergeable status.

## Implementation Changes

**File**: `tools/check-pr-merge-eligibility.sh`

**Changes**:
1. Moved draft handling to STEP 4 (before mergeable check)
2. Separated draft status handling from mergeable status checking  
3. Always calls `gh pr ready` for draft PRs regardless of mergeable status
4. Waits 2 seconds for GitHub to recalculate merge status
5. Re-fetches mergeable status after marking ready
6. Renumbered subsequent steps (5→6)

## Expected Behavior

Now when the meta-coordinator runs, eligible draft PRs will:

1. **STEP 1**: Pass open check (PR is open) ✅
2. **STEP 2**: Pass WIP check (no WIP in title) ✅
3. **STEP 3**: Pass trust check (Copilot author) ✅
4. **STEP 4**: **Mark as ready** (new behavior!) → Wait 2s → Re-fetch status ✅
5. **STEP 5**: Pass mergeable check (should be MERGEABLE after step 4) ✅
6. **STEP 6**: Pass CI check (or skip if no CI) ✅
7. **Result**: Auto-merge ✅

## Testing

The next meta-coordinator run (every 2 hours per workflow schedule) should:
- Run the updated eligibility script
- Mark PRs #3004 and #3025 as ready
- Find them eligible for auto-merge
- Merge them successfully

## Verification

To verify the fix works:

```bash
# Test the script manually
export GH_TOKEN="$COPILOT_PAT"
./tools/check-pr-merge-eligibility.sh 3004
# Should output: "🎯 RESULT: ELIGIBLE FOR AUTO-MERGE"

# Check next coordination run
# Wait for meta-coordinator.yml to run (every 2 hours)
# Check coordination issue for auto-merge actions
```

## Related Files
- `tools/check-pr-merge-eligibility.sh` - Fixed eligibility script
- `.github/agents/meta-coordinator-system.md` - Agent definition (reference)
- `.github/workflows/meta-coordinator.yml` - Scheduled workflow

## Date
2025-11-26

## Fix By
@copilot (troubleshoot-expert specialization)
