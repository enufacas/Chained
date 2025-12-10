# Stale Cleanup Quick Reference

## TL;DR

**What it does:**
- Closes issues older than 2 hours
- Closes PRs with merge conflicts

**How to use:**
```bash
# Test mode (safe)
./tools/close-stale-issues-and-prs.sh --close-issues --close-prs --dry-run

# Actually close them
./tools/close-stale-issues-and-prs.sh --close-issues --close-prs
```

## Quick Commands

### Via GitHub Actions
```bash
# Trigger manually with defaults
gh workflow run close-stale-issues-and-prs.yml

# Trigger with custom threshold (4 hours)
gh workflow run close-stale-issues-and-prs.yml -f issue_hours=4

# Test mode
gh workflow run close-stale-issues-and-prs.yml -f dry_run=true
```

### Via Command Line
```bash
# Set token
export GH_TOKEN="your_github_token"

# Close both issues and PRs
./tools/close-stale-issues-and-prs.sh --close-issues --close-prs

# Only issues
./tools/close-stale-issues-and-prs.sh --close-issues

# Only PRs
./tools/close-stale-issues-and-prs.sh --close-prs

# Custom threshold
./tools/close-stale-issues-and-prs.sh --close-issues --issue-hours 4

# Dry run (test)
./tools/close-stale-issues-and-prs.sh --close-issues --close-prs --dry-run
```

## Configuration

### Workflow Inputs
| Input | Default | Description |
|-------|---------|-------------|
| `issue_hours` | 2 | Hours before issue is stale |
| `close_issues` | true | Enable issue closure |
| `close_prs` | true | Enable PR closure |
| `dry_run` | false | Test mode (no closures) |

### Script Options
| Option | Description |
|--------|-------------|
| `--close-issues` | Enable closing stale issues |
| `--close-prs` | Enable closing conflicted PRs |
| `--issue-hours HOURS` | Set threshold (default: 2) |
| `--dry-run` | Test without closing |
| `--help` | Show help message |

## Schedule

- **Automatic**: Every hour (top of the hour)
- **Manual**: Anytime via Actions UI or `gh workflow run`

## What Gets Closed

### Issues
- Open longer than threshold (default: 2 hours)
- All open issues (no exceptions currently)
- Marked as "not planned"
- Comment posted with explanation

### PRs
- Merge status is CONFLICTING or DIRTY
- All open PRs checked
- Feature branches optionally deleted
- Comment posted with resolution steps

## Safety

✅ Dry-run mode available
✅ Explanatory comments posted
✅ Protected branches never deleted
✅ Easy to re-open if needed
✅ Full audit trail in logs

## Monitoring

```bash
# Recent runs
gh run list --workflow=close-stale-issues-and-prs.yml

# View logs
gh run view RUN_ID --log

# Watch live
gh run watch
```

## Troubleshooting

**Nothing closed?**
- Check threshold settings
- Verify items meet criteria
- Check workflow logs for errors

**Wrong items closed?**
- Adjust threshold in workflow inputs
- Use label-based filtering (future)
- Re-open and add comment explaining

**Script fails?**
- Ensure `GH_TOKEN` is set
- Check `gh`, `jq`, `python3` installed
- Run with `--dry-run` to test

## Get Help

📖 [Full Documentation](./STALE_CLEANUP_README.md)
🔧 [Implementation Details](./STALE_CLEANUP_IMPLEMENTATION_SUMMARY.md)
⚙️ [Workflow File](../.github/workflows/close-stale-issues-and-prs.yml)
🛠️ [Script Source](../tools/close-stale-issues-and-prs.sh)

---

**Quick Start**: Run with `--dry-run` first to see what would be closed!
