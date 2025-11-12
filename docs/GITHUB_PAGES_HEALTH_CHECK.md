# GitHub Pages Health Check System

**Last Updated:** 2025-11-12  
**Status:** 🟡 Warning - Data Staleness Detected  
**Agent:** doc-master

## Overview

The Chained repository includes an automated GitHub Pages health check system that monitors the health and freshness of the project's documentation website. This document explains how the system works, what triggers warnings, and how to resolve common issues.

## Health Check Components

### 1. Automated Monitoring

The health check runs automatically via the **System Monitor** workflow:

- **Schedule:** Every 3 hours (cron: `0 */3 * * *`)
- **Workflow File:** `.github/workflows/system-monitor.yml` (lines 920-1060)
- **Job Name:** `github-pages-health`
- **Trigger:** Scheduled runs, workflow_dispatch, and on issues/PR events

### 2. Health Check Criteria

The health check validates four key areas:

#### Check 1: HTML File Presence
Verifies that essential HTML files exist in the `docs/` directory:
- ✅ `index.html` - Main landing page
- ✅ `ai-knowledge-graph.html` - Interactive knowledge graph
- ✅ `ai-friends.html` - AI conversations display
- ✅ `agents.html` - Agent dashboard

#### Check 2: Data File Presence
Ensures all required data files exist in `docs/data/`:
- ✅ `stats.json` - Repository statistics
- ✅ `issues.json` - Issue data
- ✅ `pulls.json` - Pull request data
- ✅ `workflows.json` - Workflow run data
- ✅ `automation-log.json` - Automation activity log

#### Check 3: Data Freshness ⚠️
**This is where the current warning originates.**

The system checks the `last_updated` field in `docs/data/stats.json`:

```json
{
  "last_updated": "2025-11-11T01:08:44Z"
}
```

**Freshness Threshold:** 12 hours

- **Age calculation:** Current time minus `last_updated` timestamp
- **Warning trigger:** Data older than 12 hours
- **Current status:** ~28 hours old (exceeds threshold)

#### Check 4: GitHub Pages Accessibility
Performs a basic HTTP check to verify the site is accessible:
- **URL:** `https://enufacas.github.io/Chained/`
- **Check:** HTTP 200 response
- **Status:** ✅ Accessible

### 3. Health Status Levels

| Status | Issues Found | Description |
|--------|-------------|-------------|
| **Healthy** ✅ | 0 | All checks passing |
| **Warning** 🟡 | 1-2 | Minor issues detected |
| **Critical** 🔴 | 3+ | Multiple issues require attention |

**Current Status:** 🟡 Warning (1 issue: data staleness)

## Understanding the Current Warning

### Root Cause Analysis

The current warning is triggered because:

1. **Timeline Update Job is Disabled**
   - Location: `.github/workflows/system-monitor.yml` line 58
   - Current setting: `if: false`
   - Reason: "Temporarily disabled - spawning too many events, will fix later"

2. **Data Not Being Refreshed**
   - The disabled job normally updates `stats.json` every 6 hours
   - Without updates, the `last_updated` timestamp becomes stale
   - After 12 hours, the health check raises a warning

3. **Impact**
   - GitHub Pages displays outdated statistics
   - Health check reports warning status
   - Automated issue creation if problems persist

### Why Timeline Updates Were Disabled

The `timeline-update` job was intentionally disabled because it was:
- Creating too many GitHub events
- Potentially overwhelming the system
- Scheduled for future optimization

This is a **known and intentional** state, not a critical failure.

## Resolution Strategies

### Option 1: Re-enable Timeline Updates (Recommended Long-term)

Once the "spawning too many events" issue is resolved, re-enable the job:

```yaml
# .github/workflows/system-monitor.yml line 58
jobs:
  timeline-update:
    runs-on: ubuntu-latest
    if: true  # Change from 'false' to 'true' or remove the line
```

**Prerequisites:**
- Resolve the event spawning issue
- Ensure the job won't create excessive GitHub events
- Test in a controlled environment first

### Option 2: Manual Data Refresh (Immediate Solution)

Manually trigger a data update to clear the warning:

```bash
# Using GitHub CLI
gh workflow run system-monitor.yml

# Or manually update stats.json with current timestamp
cd docs/data
# Update the last_updated field to current UTC time
echo '{"last_updated": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'", ...other fields...}' > stats.json
```

**Note:** This is a temporary fix. The data will become stale again without regular updates.

### Option 3: Adjust Freshness Threshold

If 12 hours is too aggressive, modify the threshold:

```yaml
# .github/workflows/system-monitor.yml line 984
if [ ${age_hours} -gt 24 ]; then  # Changed from 12 to 24
  echo "⚠️ Stats data is ${age_hours} hours old"
  issues_found=$((issues_found + 1))
```

**Considerations:**
- Longer threshold means less frequent warnings
- But also means staler data on GitHub Pages
- Balance between alerting and data freshness

### Option 4: Accept Warning Status (Current Approach)

Since this is a known state with an intentional cause:
- Acknowledge the warning exists
- Document the reason (timeline updates disabled)
- Plan to resolve when event spawning is fixed
- Close health check issues with explanation

## Data Update Workflow Details

### How Data Gets Updated (When Enabled)

The `timeline-update` job performs these operations:

1. **Fetch Issues:** `gh issue list --limit 100 --json ...`
2. **Fetch PRs:** `gh pr list --limit 100 --state all --json ...`
3. **Fetch Workflow Runs:** `gh run list --limit 100 --json ...`
4. **Calculate Metrics:**
   - Total/open/closed issues
   - Total/merged PRs
   - AI-generated content count
   - Completion and merge rates
5. **Update stats.json:** Write new data with current timestamp

### Manual Update Script

If you need to update data manually, here's the core logic:

```bash
#!/bin/bash
# Manual data refresh script

cd docs/data

# Fetch data
gh issue list --limit 100 --json number,title,body,state,createdAt,closedAt,labels,url > issues.json
gh pr list --limit 100 --state all --json number,title,body,state,createdAt,closedAt,mergedAt,url,author > pulls.json
gh run list --limit 100 --json databaseId,name,status,conclusion,createdAt,displayTitle > workflows.json

# Calculate statistics
total_issues=$(gh issue list --state all --limit 1000 --json number | jq '. | length')
open_issues=$(gh issue list --state open --limit 1000 --json number | jq '. | length')
# ... (more calculations)

# Update stats.json
cat > stats.json << EOF
{
  "total_issues": ${total_issues},
  "open_issues": ${open_issues},
  "closed_issues": ${closed_issues},
  "total_prs": ${total_prs},
  "merged_prs": ${merged_prs},
  "ai_generated": ${ai_generated},
  "copilot_assigned": ${copilot_assigned},
  "completed": ${completed},
  "in_progress": ${in_progress},
  "completion_rate": ${completion_rate},
  "merge_rate": ${merge_rate},
  "last_updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
```

## Automated Issue Creation

When the health check detects problems, it automatically:

1. **Checks for Existing Issues**
   - Searches for open issues with `pages-health` label
   - Prevents duplicate issue creation

2. **Creates or Updates Issue**
   - **New Issue:** If none exists with the label
   - **Comment:** If issue already exists
   - **Labels:** `pages-health`, `automated`, `documentation`

3. **Issue Content Includes:**
   - Timestamp of check
   - Health status (healthy/warning/critical)
   - Number of issues found
   - Recommended actions
   - Context about 3-hour check interval

### Example Issue Report

```markdown
## 📄 GitHub Pages Health Check

**Timestamp:** 2025-11-12 05:00:00 UTC
**Status:** warning
**Issues Found:** 1

### Health Check Results

The GitHub Pages health check has identified issues that need attention.

### Recommended Actions

1. Verify all essential HTML files exist in `docs/`
2. Check that data files in `docs/data/` are up to date
3. Ensure System Monitor workflow is running regularly
4. Verify GitHub Pages deployment is active in repository settings

### Next Steps

This health check runs every 3 hours. The issue will be automatically 
updated with the latest status. Close this issue once all problems are resolved.
```

## Testing the Health Check

### Comprehensive Test Suite

A full test suite exists: `test_github_pages_health.py`

**Test Coverage:**
- ✅ 16 tests across 4 categories
- ✅ File existence checks
- ✅ Data file content validation
- ✅ HTML structure verification
- ✅ AI conversations integrity

**Run Tests:**
```bash
python3 test_github_pages_health.py
```

**Current Status:** 16/16 tests passing (100% success rate)

### Manual Health Check

To manually verify health status:

```bash
# Check if pages are accessible
curl -I https://enufacas.github.io/Chained/

# Verify data files exist
ls -lh docs/data/*.json

# Check data freshness
cat docs/data/stats.json | jq '.last_updated'

# Run automated health check
gh workflow run system-monitor.yml --ref main
```

## Troubleshooting Guide

### Warning: Data Staleness

**Symptom:** Health check reports data is >12 hours old

**Diagnosis:**
```bash
# Check last update time
cat docs/data/stats.json | jq '.last_updated'

# Check if timeline-update is disabled
grep -A 5 "timeline-update:" .github/workflows/system-monitor.yml | grep "if:"
```

**Solutions:**
1. Re-enable timeline-update job (if event issues resolved)
2. Manually refresh data files
3. Adjust freshness threshold
4. Document and accept current state

### Critical: Missing Files

**Symptom:** HTML or data files are missing

**Diagnosis:**
```bash
# Check HTML files
ls docs/*.html

# Check data files
ls docs/data/*.json
```

**Solutions:**
1. Restore missing files from Git history
2. Run timeline-update job manually
3. Verify GitHub Pages deployment settings

### Warning: Pages Not Accessible

**Symptom:** HTTP check fails for GitHub Pages URL

**Diagnosis:**
```bash
curl -I https://enufacas.github.io/Chained/
```

**Solutions:**
1. Check GitHub Pages settings in repository
2. Verify `docs/` folder is set as Pages source
3. Check for GitHub Pages service status
4. Review recent commits for breaking changes

## Best Practices

### For Maintainers

1. **Monitor Health Check Results**
   - Review automated issues regularly
   - Understand root causes before closing
   - Document intentional warning states

2. **Plan Data Updates**
   - Re-enable timeline-update when safe
   - Consider update frequency needs
   - Balance freshness vs. event volume

3. **Test Changes**
   - Run `test_github_pages_health.py` before committing
   - Verify data file structure matches expectations
   - Check manual data updates work correctly

4. **Document Decisions**
   - Explain why features are disabled
   - Set timelines for re-enabling
   - Keep this documentation updated

### For Contributors

1. **Don't Panic on Warnings**
   - Warnings don't always indicate problems
   - Check for known/intentional states
   - Read this documentation first

2. **Verify Before "Fixing"**
   - Understand why something is disabled
   - Check if "fix" might cause new issues
   - Coordinate with maintainers

3. **Update Documentation**
   - Keep health check docs current
   - Document new checks or changes
   - Explain threshold rationale

## Related Documentation

- **Test Suite:** `test_github_pages_health.py`
- **Previous Report:** `GITHUB_PAGES_HEALTH_REPORT.md`
- **System Monitor:** `.github/workflows/system-monitor.yml`
- **Issues Data:** `docs/ISSUES_JSON_MAINTENANCE.md`

## Current Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| HTML Files | ✅ Healthy | All required files present |
| Data Files | ✅ Healthy | All files exist with content |
| Data Freshness | 🟡 Warning | 28 hours old (>12h threshold) |
| Site Accessibility | ✅ Healthy | Pages accessible online |
| **Overall Status** | **🟡 Warning** | **1 issue: data staleness** |

### Why This Warning Exists

- `timeline-update` job intentionally disabled (line 58 of system-monitor.yml)
- Reason: Spawning too many GitHub events
- Resolution: Planned after event issue is fixed
- Current state: Known and documented

### Recommended Action

**Accept current warning state** until event spawning issue is resolved, then re-enable the `timeline-update` job.

**No immediate action required** - this is an intentional, documented state.

---

## Change Log

| Date | Agent | Change |
|------|-------|--------|
| 2025-11-11 | test-champion | Initial health verification report created |
| 2025-11-11 | doc-master | Resolved empty issues.json file |
| 2025-11-12 | doc-master | Created comprehensive health check documentation |

---

*Documentation maintained by the Doc Master agent*  
*Part of the Chained autonomous AI ecosystem*
