# 🧹 Learning Files Cleanup Policy

## Overview

**@edge-cases-pro** has implemented an automated cleanup system to prevent repository bloat from accumulated learning files. The system runs daily and removes old learning files while preserving important documentation.

## Retention Policy

- **Default retention period**: 60 days
- **Cleanup schedule**: Daily at 2 AM UTC
- **Manual trigger**: Available via workflow_dispatch

## Protected Files

The following files and directories are **never deleted**:

### Always Protected
- `learnings/README.md` - Documentation for the learning system
- `learnings/CLAUDE_QUICKSTART.md` - Quick start guide
- `learnings/book/` - Knowledge base (categorized learnings)
- `learnings/agent_memory/` - Agent memory storage
- `learnings/discussions/` - Discussion history

### What Gets Cleaned Up

Files older than the retention period from:

1. **learnings/ directory**
   - `*.json` - Learning session data (TLDR, HackerNews, GitHub Trending)
   - `*.md` - Investigation reports, analysis documents
   - Timestamped files: `analysis_YYYYMMDD_HHMMSS.json`
   - Source files: `tldr_*.json`, `hn_*.json`, `github_trending_*.json`

2. **Root directory**
   - `*LEARNING*.md` - Learning session summaries
   - `*TLDR*.md` - TLDR analysis reports
   - `*COMBINED*.md` - Combined learning session reports
   - `TASK_COMPLETION_*.md` - Task completion summaries
   - `COORDINATION_PLAN_*.md` - Learning coordination plans

3. **summaries/ directory**
   - `*LEARNING*.md` - Learning analysis summaries
   - `HN_LEARNING*.md` - HackerNews learning summaries

4. **investigation-reports/ directory**
   - `*learning*.md` - Learning investigation reports

## Usage

### Automatic Cleanup

The cleanup runs automatically every day at 2 AM UTC via GitHub Actions schedule:

```yaml
schedule:
  - cron: '0 2 * * *'
```

### Manual Cleanup

You can trigger cleanup manually with custom options:

1. Go to **Actions** → **Cleanup: Old Learning Files**
2. Click **Run workflow**
3. Configure options:
   - **days_old**: Number of days to retain (default: 60)
   - **dry_run**: Preview mode without deletions (default: false)

### Dry Run Mode

Test the cleanup without deleting files:

```bash
gh workflow run cleanup-old-learning-files.yml \
  --field days_old=60 \
  --field dry_run=true
```

This will show what would be deleted without making any changes.

### Custom Retention Period

Run cleanup with a different retention period:

```bash
gh workflow run cleanup-old-learning-files.yml \
  --field days_old=30
```

## Edge Cases Handled

**@edge-cases-pro** has implemented robust edge case handling:

### 1. Empty Directories
- Directories without matching files are skipped
- No errors on missing directories

### 2. Protected Files
- Multiple layers of protection patterns
- Case-insensitive matching
- Subdirectory protection

### 3. File Access Errors
- Gracefully handles permission errors
- Uses safe defaults (0) for missing timestamps
- Continues processing on individual file errors

### 4. Concurrent Modifications
- Timestamps checked at deletion time
- Files modified during cleanup are kept
- Race conditions handled safely

### 5. Zero Deletions
- Workflow succeeds even if no files match criteria
- Informative messages when nothing needs cleanup
- No empty PRs created

### 6. Large Cleanup Operations
- Efficient file finding with `-print0` and null delimiters
- Batch processing to handle thousands of files
- Progress reporting during execution

## Cleanup Process

1. **Calculate cutoff date** based on retention period
2. **Scan learning directories** for old files
3. **Check protection status** for each file
4. **Compare file modification time** with cutoff
5. **Delete qualifying files** (or preview in dry run)
6. **Track statistics** (files deleted, space freed)
7. **Commit changes** to new branch
8. **Create PR** with cleanup summary
9. **Log activity** for audit trail

## Pull Request Format

When cleanup deletes files, a PR is automatically created:

```markdown
## Automated Learning Files Cleanup

**@edge-cases-pro** has automatically cleaned up old learning files.

### Cleanup Summary
- Files deleted: 42
- Files kept: 179
- Space freed: 2.3 MB
- Retention policy: 60 days

### Protected Files
- README.md files
- QUICKSTART.md files
- learnings/book/ (knowledge base)
- learnings/agent_memory/
- learnings/discussions/

### Files Deleted
Old learning files from:
- learnings/ directory
- Root directory
- summaries/ directory
- investigation-reports/ directory
```

## Statistics and Monitoring

The cleanup workflow reports:
- Number of files deleted
- Number of files kept
- Total space freed
- Retention period used
- Timestamp of cleanup

These statistics are logged and included in the PR for transparency.

## Customization

### Adjust Retention Period

Edit `.github/workflows/cleanup-old-learning-files.yml`:

```yaml
inputs:
  days_old:
    default: '60'  # Change this value
```

### Add More Protected Patterns

Add patterns to the `PROTECTED_PATTERNS` array:

```bash
PROTECTED_PATTERNS=(
  "README.md"
  "QUICKSTART.md"
  "learnings/book/"
  "learnings/agent_memory/"
  "learnings/discussions/"
  "your_pattern_here"  # Add your pattern
)
```

### Change Schedule

Modify the cron expression:

```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
  # Examples:
  # - cron: '0 */12 * * *'  # Every 12 hours
  # - cron: '0 0 * * 0'     # Weekly on Sunday
  # - cron: '0 0 1 * *'     # Monthly on 1st
```

## Troubleshooting

### No Files Being Deleted

Check if:
- Files are newer than retention period
- Files match protected patterns
- Dry run mode is enabled

### Too Many Files Being Deleted

- Increase the `days_old` parameter
- Review protected patterns
- Use dry run mode first

### Workflow Fails

- Check workflow logs for specific errors
- Verify file permissions
- Ensure git configuration is correct

## Safety Features

1. **Dry run mode** - Test before executing
2. **Protected patterns** - Critical files never deleted
3. **Timestamp verification** - Only old files deleted
4. **PR review** - All deletions reviewable before merge
5. **Audit logging** - Complete record of actions
6. **Error handling** - Graceful failures, no data loss

## Benefits

- **Prevents repository bloat** - Old learning files removed automatically
- **Maintains performance** - Smaller repository size improves operations
- **Preserves important data** - Protected files never touched
- **Full transparency** - All actions logged and reviewable
- **Flexible configuration** - Easy to customize retention policy
- **Safe operation** - Multiple safeguards prevent data loss

---

**Workflow**: `.github/workflows/cleanup-old-learning-files.yml`
**Agent**: @edge-cases-pro
**Status**: Active
**Last Updated**: 2025-11-18
