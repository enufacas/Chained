# Stale Issue and Conflicted PR Cleanup

This directory contains automated workflows and tools for maintaining repository health by closing stale issues and PRs with merge conflicts.

## Overview

Two automated workflows handle cleanup:

1. **Close Stale Issues** - Closes issues that have been open longer than a threshold (default: 2 hours)
2. **Close Conflicted PRs** - Closes PRs that have unresolved merge conflicts

## Workflows

### 1. Close Stale Issues (`close-stale-issues.yml`)

**Triggers:**
- Schedule: Every hour (on the hour)
- Manual: Via workflow_dispatch

**Configuration:**
- `hours_threshold`: Number of hours before an issue is considered stale (default: 2)
- `dry_run`: When true, shows what would be closed without actually closing (default: false)

**What it does:**
- Fetches all open issues
- Calculates age of each issue
- Closes issues older than the threshold
- Posts an explanatory comment on each closed issue
- Provides instructions for re-opening if needed

**Usage:**
```bash
# Trigger manually via GitHub UI or CLI
gh workflow run close-stale-issues.yml

# With custom threshold (e.g., 4 hours)
gh workflow run close-stale-issues.yml -f hours_threshold=4

# Dry run mode (preview without closing)
gh workflow run close-stale-issues.yml -f dry_run=true
```

### 2. Close Conflicted PRs (`close-conflicted-prs.yml`)

**Triggers:**
- Schedule: Every 30 minutes
- Pull Request events: When PRs are synchronized, opened, or reopened
- Manual: Via workflow_dispatch

**Configuration:**
- `pr_number`: Specific PR to check (leave empty to check all)
- `dry_run`: When true, shows what would be closed without actually closing (default: false)

**What it does:**
- Fetches open PRs (all or specific one)
- Checks mergeable status
- Closes PRs with `CONFLICTING` or `DIRTY` merge state
- Posts explanatory comment with resolution steps
- Optionally deletes feature branches (keeps protected branches)

**Usage:**
```bash
# Trigger manually to check all PRs
gh workflow run close-conflicted-prs.yml

# Check specific PR
gh workflow run close-conflicted-prs.yml -f pr_number=123

# Dry run mode
gh workflow run close-conflicted-prs.yml -f dry_run=true
```

## Command-Line Tool

### `tools/close-stale-issues-and-prs.sh`

A standalone script that can be run locally or in CI/CD.

**Usage:**
```bash
# Close both stale issues and conflicted PRs
./tools/close-stale-issues-and-prs.sh --close-issues --close-prs

# Close only stale issues (older than 2 hours)
./tools/close-stale-issues-and-prs.sh --close-issues

# Close only conflicted PRs
./tools/close-stale-issues-and-prs.sh --close-prs

# Custom threshold for issues (e.g., 4 hours)
./tools/close-stale-issues-and-prs.sh --close-issues --issue-hours 4

# Dry run (preview without closing)
./tools/close-stale-issues-and-prs.sh --close-issues --close-prs --dry-run

# Show help
./tools/close-stale-issues-and-prs.sh --help
```

**Requirements:**
- `gh` (GitHub CLI) installed and authenticated
- `jq` for JSON processing
- `python3` for date calculations
- `GH_TOKEN` environment variable set

**Example:**
```bash
# Set GitHub token
export GH_TOKEN="your_github_token"

# Run cleanup with 3-hour threshold
./tools/close-stale-issues-and-prs.sh \
  --close-issues \
  --close-prs \
  --issue-hours 3 \
  --dry-run
```

## Configuration

### Issue Closure Policy

**Default threshold:** 2 hours

**Rationale:**
- Issues should have clear requirements and scope
- 2 hours is sufficient time to add details or clarify
- Stale issues clutter the backlog
- Authors can re-open if still relevant

**Exceptions:**
- None currently - all open issues are subject to closure
- Can be adjusted via workflow inputs

### PR Merge Conflict Policy

**Trigger:** PRs with `CONFLICTING` or `DIRTY` merge state

**Rationale:**
- Merge conflicts indicate PR is out of sync
- Conflicts prevent automatic merging
- Unresolved conflicts suggest abandonment
- Starting fresh is often easier than resolving old conflicts

**What happens:**
1. PR is closed with explanation
2. Comment includes resolution instructions
3. Feature branch is deleted (protected branches kept)
4. Author can create new PR with resolved conflicts

## Monitoring

### Check Workflow Runs

```bash
# List recent runs of stale issue workflow
gh run list --workflow=close-stale-issues.yml --limit 5

# List recent runs of conflicted PR workflow
gh run list --workflow=close-conflicted-prs.yml --limit 5

# View details of a specific run
gh run view RUN_ID
```

### Check Logs

```bash
# View logs for a specific run
gh run view RUN_ID --log

# Download logs
gh run view RUN_ID --log > cleanup-logs.txt
```

## Troubleshooting

### Issues Not Being Closed

**Possible causes:**
1. Workflow is not enabled
2. `GH_TOKEN` lacks `issues: write` permission
3. Threshold is too high (issues are not old enough)
4. Issues are being created faster than cleanup runs

**Solutions:**
1. Check workflow status in Actions tab
2. Verify token permissions in workflow file
3. Adjust threshold via workflow inputs
4. Increase cleanup frequency in schedule

### PRs Not Being Closed

**Possible causes:**
1. PRs don't have actual merge conflicts
2. `GH_TOKEN` lacks `pull-requests: write` permission
3. Dry run mode is enabled
4. Workflow failed before reaching closure step

**Solutions:**
1. Check PR mergeable status: `gh pr view PR_NUMBER --json mergeable`
2. Verify token permissions
3. Ensure dry_run is false in production
4. Check workflow logs for errors

### False Positives

**If issues/PRs are closed incorrectly:**
1. Re-open the issue/PR
2. Add a comment explaining why it should stay open
3. Adjust thresholds if needed
4. Consider excluding via labels (future enhancement)

## Future Enhancements

Possible improvements:
- [ ] Exclude issues with specific labels (e.g., `keep-open`, `in-progress`)
- [ ] Different thresholds for different issue types
- [ ] Notification to issue authors before closing
- [ ] Grace period for first-time contributors
- [ ] Integration with project boards
- [ ] Metrics dashboard for cleanup activity

## Related Documentation

- [GitHub Actions Workflows](../../.github/workflows/)
- [Merge Conflict Resolver](../../.github/workflows/merge-conflict-resolver.yml) - Creates issues for conflicts instead of closing
- [Cleanup Stale PRs](../../tools/cleanup-stale-prs.sh) - More sophisticated PR cleanup with multiple policies

## Support

For questions or issues:
1. Check workflow logs in GitHub Actions
2. Review this documentation
3. Create an issue with `workflow` label
4. Tag `@workflows-tech-lead` for workflow-related questions
