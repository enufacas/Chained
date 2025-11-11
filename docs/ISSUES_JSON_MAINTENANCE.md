# issues.json Maintenance Guide

## Overview

The `docs/data/issues.json` file powers the GitHub Pages dashboard statistics, showing the number of ideas generated, issue states, and repository activity. This file must be kept up-to-date to display accurate information on the website.

## File Location

```
/home/runner/work/Chained/Chained/docs/data/issues.json
```

## Data Structure

The file contains an array of issue objects. Each issue must have the following fields:

```json
[
  {
    "number": 123,
    "title": "Issue title",
    "body": "Issue description",
    "state": "OPEN" | "CLOSED",
    "createdAt": "2025-11-11T00:00:00Z",
    "closedAt": "2025-11-11T00:00:00Z" | null,
    "labels": [
      {"name": "label1"},
      {"name": "label2"}
    ],
    "url": "https://github.com/owner/repo/issues/123"
  }
]
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `number` | integer | Yes | The issue number |
| `title` | string | Yes | The issue title |
| `body` | string | Yes | The issue description (can be empty string) |
| `state` | string | Yes | Either "OPEN" or "CLOSED" |
| `createdAt` | string | Yes | ISO 8601 timestamp when issue was created |
| `closedAt` | string/null | Yes | ISO 8601 timestamp when issue was closed, or null if still open |
| `labels` | array | Yes | Array of label objects, each with a `name` property |
| `url` | string | Yes | Full GitHub URL to the issue |

## Update Methods

### Method 1: Automated (Recommended)

Re-enable the System Monitor workflow to automatically update the file:

1. Edit `.github/workflows/system-monitor.yml`
2. Change line 58 from `if: false` to `if: true`
3. The workflow will run on its schedule and update `issues.json` automatically

```yaml
jobs:
  timeline-update:
    runs-on: ubuntu-latest
    if: true  # Changed from false
```

The workflow uses this command:
```bash
gh issue list --limit 100 --json number,title,body,state,createdAt,closedAt,labels,url > docs/data/issues.json
```

### Method 2: Manual via GitHub CLI

If you have the GitHub CLI (`gh`) installed and authenticated:

```bash
cd /home/runner/work/Chained/Chained
gh issue list --limit 100 --json number,title,body,state,createdAt,closedAt,labels,url > docs/data/issues.json
```

### Method 3: Manual via Script

Use the Python script to fetch and update the file:

```bash
cd /home/runner/work/Chained/Chained
python3 tools/populate_issues.py  # (if script is created in tools/)
```

### Method 4: Manual via API

Use the GitHub REST API to fetch issues:

```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/enufacas/Chained/issues?state=all&per_page=100 \
  | jq 'map({
      number: .number,
      title: .title,
      body: .body,
      state: .state | ascii_upcase,
      createdAt: .created_at,
      closedAt: .closed_at,
      labels: [.labels[] | {name: .name}],
      url: .html_url
    })' > docs/data/issues.json
```

## Validation

After updating the file, run the health check test to verify:

```bash
cd /home/runner/work/Chained/Chained
python3 test_github_pages_health.py
```

Look for these passing tests:
- ✅ Data Files Exist
- ✅ issues.json Not Empty
- ✅ JSON Files Valid

## Common Issues

### Empty File (`[]`)

**Symptom:** GitHub Pages shows "0 Ideas Generated"

**Cause:** The file contains an empty array

**Solution:** Run any of the update methods above to populate it

### Invalid JSON

**Symptom:** Test fails with "invalid JSON" error

**Cause:** Syntax error in the JSON file

**Solution:** 
1. Validate the JSON: `python3 -m json.tool docs/data/issues.json`
2. Fix syntax errors or regenerate the file

### Missing Fields

**Symptom:** Dashboard displays incomplete information

**Cause:** Issue objects missing required fields

**Solution:** Ensure all issues have all required fields listed in the Data Structure section

### Stale Data

**Symptom:** Dashboard doesn't reflect recent activity

**Cause:** File hasn't been updated recently

**Solution:**
1. Check the `last_updated` timestamp in `docs/data/stats.json`
2. If older than 24-48 hours, run an update
3. Consider re-enabling the automated workflow

## Integration with GitHub Pages

The GitHub Pages dashboard uses this file to:

1. Display total issue count
2. Show open vs closed issue breakdown  
3. Calculate "Ideas Generated" metric
4. Display issue activity timeline
5. Show issue labels distribution

## Monitoring

### Check File Status

```bash
# Check file size (should be > 100 bytes)
ls -lh docs/data/issues.json

# Check number of issues
jq 'length' docs/data/issues.json

# Check last update time
stat -c %y docs/data/issues.json
```

### Set Up Alerts

Consider adding monitoring for:
- File size dropping below threshold
- No updates in > 48 hours
- Empty array (`[]`)
- Invalid JSON structure

## Best Practices

1. **Update Frequency**: At least daily, preferably on push/PR events
2. **Data Limits**: Keep to 100 most recent issues to manage file size
3. **Validation**: Always validate JSON after manual edits
4. **Backup**: System Monitor creates automatic backups via git history
5. **Testing**: Run health checks after updates

## Troubleshooting

### GitHub CLI Not Available

Install the GitHub CLI:
```bash
# On Ubuntu/Debian
sudo apt install gh

# On macOS
brew install gh

# Authenticate
gh auth login
```

### Permissions Issues

Ensure the script/workflow has:
- Read access to repository issues
- Write access to `docs/data/` directory
- Valid GitHub token with `repo` scope

### Workflow Disabled

Check `.github/workflows/system-monitor.yml` line 58 - it should be `if: true` not `if: false`

## Related Files

- `docs/data/pulls.json` - Pull request data (similar structure)
- `docs/data/stats.json` - Aggregated statistics
- `docs/data/workflows.json` - Workflow run data
- `.github/workflows/system-monitor.yml` - Automated update workflow

## References

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub Issues API](https://docs.github.com/en/rest/issues)
- [GitHub Pages Test Suite](../test_github_pages_health.py)
- [System Monitor Workflow](../.github/workflows/system-monitor.yml)

---

**Last Updated:** 2025-11-11  
**Maintained By:** Doc Master Agent  
**Status:** Active
