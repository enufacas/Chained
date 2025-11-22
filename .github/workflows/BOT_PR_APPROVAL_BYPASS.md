# GitHub Actions Approval Bypass for Bot PRs

## Problem
Workflows with write permissions triggered by bot-created PRs (like Copilot) require manual approval, blocking automation.

## Solution
Use `pull_request_target` trigger with explicit base branch checkout:

```yaml
on:
  pull_request_target:
    types: [opened, synchronize, ready_for_review, reopened]

jobs:
  job_name:
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.repository.default_branch }}
        # IMPORTANT: Explicitly checkout base branch for security
```

## Why This Works
- `pull_request_target` runs in base repository context (no approval needed)
- Has write permissions without approval requirement  
- Explicit `ref` ensures base branch code is checked out (security)
- Workflow can analyze PR via GitHub API without executing PR code

## Security
✅ Safe because:
- Checks out base branch, not PR branch
- Only runs trusted repository code
- PR data accessed via GitHub API only
- No untrusted PR code is executed

## When to Use
- Workflow needs write permissions (labels, comments, etc.)
- Must process bot-created PRs immediately
- Workflow doesn't need to run PR code
- PR analysis via API is sufficient

## When NOT to Use
- Workflow needs to run tests from PR code
- Workflow needs to build PR code
- Workflow needs PR branch files

## Common Mistakes
❌ Using `pull_request_target` without explicit `ref`:
```yaml
- uses: actions/checkout@v4  # BAD: Checks out PR code!
```

✅ Correct usage with explicit base branch:
```yaml
- uses: actions/checkout@v4
  with:
    ref: ${{ github.event.repository.default_branch }}  # GOOD: Base branch only
```

## Examples in This Repository
- `.github/workflows/tech-lead-review.yml` - Assigns tech leads to PRs
- Fixed in commit: d9f2ed0d
- Original issue: https://github.com/enufacas/Chained/actions/runs/19590187488

## Alternative Approaches
If you need to run PR code:
1. **Scheduled workflow**: Run on schedule, processes all open PRs (no approval)
2. **Read-only permissions**: Use `contents: read` only (but can't modify PR)
3. **Manual approval**: Accept the approval requirement

## References
- [GitHub Docs: pull_request_target](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request_target)
- [GitHub Docs: Approving workflow runs](https://docs.github.com/en/actions/managing-workflow-runs/approving-workflow-runs-from-public-forks)

---

*Created by **@workflows-tech-lead** - November 2025*
*Preventing future approval requirement issues*
