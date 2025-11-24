# PR Merge Eligibility Checker

## Overview

`check-pr-merge-eligibility.sh` is a deterministic script that checks if a PR meets all criteria for auto-merge according to the @meta-coordinator-system agent's requirements.

## Usage

```bash
./tools/check-pr-merge-eligibility.sh <PR_NUMBER>
```

## Exit Codes

- **0**: PR is ELIGIBLE for auto-merge
- **1**: PR is NOT ELIGIBLE (reason printed to stdout)

## Eligibility Criteria (ALL must be met)

1. **State:** PR must be OPEN
2. **No WIP:** No WIP markers in title (blocks regardless of draft status)
3. **Trusted Author:** Repository owner OR copilot/github-actions bot
4. **Mergeable:** MERGEABLE status (handles UNKNOWN automatically)
5. **CI Status:** All checks passed OR no checks configured

## WIP Marker Detection

The script detects these patterns in PR titles (case-insensitive):
- `[WIP]`
- `WIP:`
- `WIP ` (with space)
- `work in progress`
- `work.in.progress`
- `[do not merge]`
- `[do.not.merge]`
- `[dnm]`

**Important:** WIP markers **always block** merging, regardless of draft status.

## UNKNOWN Mergeable State Handling

When GitHub returns `mergeable: UNKNOWN` (common for draft PRs):

1. Script detects UNKNOWN status
2. If PR is draft, marks it as ready
3. Waits 2 seconds for GitHub to calculate
4. Re-fetches mergeable status
5. Proceeds with check

## Example Output

### Eligible PR
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PR #123 Eligibility Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: Add new feature
Author: app/copilot-swe-agent
Draft: true
Mergeable: UNKNOWN

STEP 1: Check state...
  ✅ PASS: PR is open

STEP 2: Check for WIP markers in title...
  ✅ PASS: No WIP markers in title

STEP 3: Verify trusted author...
  ✅ PASS: Trusted bot (app/copilot-swe-agent)

STEP 4: Check mergeable status...
  ⚠️  Status UNKNOWN
  → Marking draft as ready to trigger calculation...
  → Waiting 2 seconds for status update...
  → Updated status: MERGEABLE
  ✅ PASS: Mergeable

STEP 5: Check CI status...
  ✅ PASS: No CI checks configured (OK)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 RESULT: ELIGIBLE FOR AUTO-MERGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Blocked PR (WIP in title)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PR #456 Eligibility Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: [WIP] Work in progress feature
Author: app/copilot-swe-agent
Draft: true
Mergeable: UNKNOWN

STEP 1: Check state...
  ✅ PASS: PR is open

STEP 2: Check for WIP markers in title...
  ❌ FAIL: Has WIP marker in title
  Note: WIP markers block regardless of draft status
```

## Integration Examples

### In Bash Scripts
```bash
if bash tools/check-pr-merge-eligibility.sh "$PR_NUM"; then
  echo "Eligible, merging..."
  gh pr merge "$PR_NUM" --squash --delete-branch
else
  echo "Not eligible, skipping"
fi
```

### In Workflows
```yaml
- name: Check PR Eligibility
  id: check
  run: |
    if bash tools/check-pr-merge-eligibility.sh ${{ github.event.pull_request.number }}; then
      echo "eligible=true" >> $GITHUB_OUTPUT
    else
      echo "eligible=false" >> $GITHUB_OUTPUT
    fi

- name: Auto-merge if eligible
  if: steps.check.outputs.eligible == 'true'
  run: gh pr merge ${{ github.event.pull_request.number }} --squash
```

### Batch Processing
```bash
# Check all open PRs
for pr_num in $(gh pr list --state open --json number --jq '.[].number'); do
  if bash tools/check-pr-merge-eligibility.sh "$pr_num"; then
    echo "Merging PR #$pr_num"
    gh pr merge "$pr_num" --squash --delete-branch
  fi
done
```

## Determinism

The script is **deterministic** - given the same PR state, it will always produce the same result:

- ✅ Same criteria evaluated in same order
- ✅ Clear pass/fail for each criterion
- ✅ No randomness or timing dependencies (except UNKNOWN handling)
- ✅ Explicit exit codes

## Environment Variables

- `GITHUB_REPOSITORY_OWNER`: Override default owner (default: `enufacas`)
- `GH_TOKEN` or `GITHUB_TOKEN`: GitHub authentication token (required)

## Dependencies

- `gh` CLI (GitHub CLI)
- `jq` (JSON processor)

## Related Documentation

- `.github/agents/meta-coordinator-system.md` - Agent definition with full eligibility logic
- `docs/WORKFLOWS.md` - Workflow documentation

## Maintenance

When updating eligibility criteria:

1. Update this script
2. Update `.github/agents/meta-coordinator-system.md` 
3. Test with sample PRs
4. Update examples in documentation

## Testing

Test the script with various PR states:

```bash
# WIP marker in title
bash tools/check-pr-merge-eligibility.sh 2847  # Should fail

# Eligible PR
bash tools/check-pr-merge-eligibility.sh 2823  # Should pass (if all criteria met)

# Draft PR with UNKNOWN status
bash tools/check-pr-merge-eligibility.sh <draft-pr>  # Should handle UNKNOWN
```
