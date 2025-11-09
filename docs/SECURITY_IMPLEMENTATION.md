# Security Implementation: Restricting Outside Contributions

## Overview

This document describes the security implementation that prevents unauthorized external contributions from being auto-merged while maintaining the autonomous operation of Copilot/AI workflows.

## Problem Statement

The repository needed to:
1. **Block** external contributions from being auto-merged without owner review
2. **Allow** Copilot/AI to continue autonomous operations (generating issues, creating PRs, auto-merging)
3. **Maintain** the "perpetual AI motion machine" functionality

## Solution Architecture

### Components

#### 1. CODEOWNERS File (`.github/CODEOWNERS`)

- Requires repository owner (@enufacas) to review all changes
- GitHub automatically requests review from code owners on all PRs
- Prevents any PR from being merged without owner awareness

#### 2. Enhanced Auto-Review Workflow (`.github/workflows/auto-review-merge.yml`)

The workflow now includes strict authorization checks:

```bash
# Check 1: Is PR author the repository owner?
is_repo_owner=0
if [ "${author}" = "${repo_owner}" ]; then
  is_repo_owner=1
fi

# Check 2: Is PR author a trusted bot?
is_trusted_bot=0
if echo "${author}" | grep -qE "^(github-actions\[bot\]|dependabot\[bot\]|copilot)$"; then
  is_trusted_bot=1
fi

# Check 3: Does PR have copilot label?
has_copilot_label=$(echo "${pr_data}" | jq -r '.labels[].name' | grep -c "copilot")

# Decision: Auto-merge only if authorized
should_auto_merge=0
if [ "${is_repo_owner}" -eq 1 ] && [ "${has_copilot_label}" -gt 0 ]; then
  should_auto_merge=1
elif [ "${is_trusted_bot}" -eq 1 ] && [ "${has_copilot_label}" -gt 0 ]; then
  should_auto_merge=1
fi
```

#### 3. Branch Protection Rules (Configured in Repository Settings)

Recommended settings:
- ✅ Require a pull request before merging
- ✅ Require approvals (1 approval required)
- ✅ Require review from Code Owners
- ✅ Allow specified actors to bypass required pull requests:
  - `github-actions[bot]` (for autonomous workflows)
- ✅ Allow auto-merge
- ✅ Automatically delete head branches

## Authorization Matrix

| PR Author | Has `copilot` Label | Auto-Merge? | Reason |
|-----------|-------------------|-------------|---------|
| Repository Owner (@enufacas) | ✅ Yes | ✅ **YES** | Owner with copilot label |
| Repository Owner (@enufacas) | ❌ No | ❌ **NO** | Missing copilot label |
| github-actions[bot] | ✅ Yes | ✅ **YES** | Trusted bot with copilot label |
| github-actions[bot] | ❌ No | ❌ **NO** | Missing copilot label |
| dependabot[bot] | ✅ Yes | ✅ **YES** | Trusted bot with copilot label |
| copilot | ✅ Yes | ✅ **YES** | Trusted bot with copilot label |
| External User | ✅ Yes | ❌ **NO** | Not authorized |
| External User | ❌ No | ❌ **NO** | Not authorized |
| random-bot | ✅ Yes | ❌ **NO** | Not in trusted bot list |

## Workflow for Different PR Types

### Owner/Copilot PRs (Autonomous)

1. Owner or github-actions[bot] creates PR with `copilot` label
2. Auto-review workflow detects authorized PR
3. Workflow automatically approves PR
4. PR is auto-merged (if mergeable)
5. Issue is automatically closed

**Timeline:** ~10-15 minutes from PR creation to merge

### External Contributor PRs (Manual Review)

1. External user creates PR
2. CODEOWNERS automatically requests review from @enufacas
3. Auto-review workflow detects unauthorized PR
4. Workflow adds comment explaining manual review is required
5. Owner manually reviews and approves/rejects
6. PR is merged manually or by auto-merge after approval

**Timeline:** Depends on owner availability

## Security Features

### Defense in Depth

1. **CODEOWNERS File**: First line of defense - requires owner review
2. **Workflow Authorization**: Second line - checks PR author and labels
3. **Branch Protection**: Third line - enforces rules at GitHub level
4. **Explicit Trusted List**: Only specific bots can auto-merge

### Attack Mitigation

| Attack Vector | Mitigation |
|--------------|------------|
| User adds `copilot` label to their PR | Workflow checks author, not just label |
| User creates account with "bot" in name | Workflow uses exact regex match for trusted bots |
| User creates account named "copilot" | Workflow checks for exact match `copilot`, not substring |
| Bot not in trusted list | Workflow explicitly allows only specific bots |
| PR without review | CODEOWNERS requires owner review |

## Testing

The implementation has been tested with the following scenarios:

✅ Owner PR with copilot label → Auto-merges
✅ github-actions[bot] PR with copilot label → Auto-merges  
✅ External user PR with copilot label → Requires manual review
✅ External user PR without label → Requires manual review
✅ Owner PR without copilot label → Requires manual review
✅ Random bot PR with copilot label → Requires manual review

## Maintenance

### Adding a New Trusted Bot

To add a new trusted bot to the auto-merge list:

1. Edit `.github/workflows/auto-review-merge.yml`
2. Update the regex on line ~82:
   ```bash
   if echo "${author}" | grep -qE "^(github-actions\[bot\]|dependabot\[bot\]|copilot|NEW_BOT_NAME)$"; then
   ```
3. Test with a PR from that bot
4. Commit and push changes

### Monitoring

Check the Actions tab for workflow runs to see:
- Which PRs were auto-merged
- Which PRs were flagged for manual review
- Reasons for each decision

### Troubleshooting

**Issue:** Owner's Copilot PR not auto-merging

**Solutions:**
- Verify PR has `copilot` label
- Check workflow logs for authorization decision
- Ensure branch protection allows github-actions[bot] to bypass

**Issue:** External PR auto-merged incorrectly

**Solutions:**
- Review workflow logs to identify why
- Check PR author and labels
- Verify CODEOWNERS file is in place
- Review branch protection rules

## Benefits

1. ✅ **Security**: External contributions require explicit owner approval
2. ✅ **Autonomy**: Copilot workflows continue operating independently  
3. ✅ **Transparency**: Clear feedback on why PRs aren't auto-merged
4. ✅ **Flexibility**: Owner can still create manual PRs that require review
5. ✅ **Auditability**: All decisions logged in workflow runs

## Conclusion

This implementation successfully balances security with automation, ensuring:
- The repository remains secure from unauthorized contributions
- The perpetual AI motion machine continues functioning autonomously
- The owner maintains full control over what gets merged
- External contributors can still submit PRs, but they require review

The solution uses multiple layers of security (CODEOWNERS, workflow checks, branch protection) to provide defense in depth while maintaining the autonomous development experience.
