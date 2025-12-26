# ADK A2A Blog Pipeline - Tracking Issue Setup Guide

**Author:** @create-botter  
**Date:** 2025-12-26  
**Purpose:** Complete guide for setting up and verifying ADK A2A Blog Pipeline tracking issues

---

## Overview

This guide explains how to properly set up and initialize a tracking issue for the ADK A2A Blog Pipeline. The tracking issue serves as a centralized location where the automated workflow posts status updates after each pipeline run.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Access to the repository with issue write permissions
- Basic understanding of GitHub labels and issues

## Quick Setup

### Step 1: Verify or Create Tracking Issue

The tracking issue should have:
- **Title:** `🤖 ADK A2A Blog Pipeline Status`
- **Labels:** `adk-pipeline`, `automated`
- **Body:** `Tracking issue for ADK A2A blog pipeline runs. See comments for run history.`

**Check if tracking issue exists:**
```bash
gh issue list --label "adk-pipeline" --state open
```

**If no issue exists, create one:**
```bash
gh issue create \
  --title "🤖 ADK A2A Blog Pipeline Status" \
  --label "adk-pipeline,automated" \
  --body "Tracking issue for ADK A2A blog pipeline runs. See comments for run history."
```

### Step 2: Initialize with Welcome Comment (Recommended ✨)

Run the new welcome posting script to add a comprehensive welcome comment:

```bash
# Auto-detect tracking issue (RECOMMENDED)
./tools/post-adk-tracking-welcome.sh

# Or specify issue number explicitly
./tools/post-adk-tracking-welcome.sh 4069
```

**Alternative (Legacy):**
```bash
# Legacy initialization script
./tools/initialize-adk-tracking-issue.sh

# Or specify issue number
./tools/initialize-adk-tracking-issue.sh 194
```

The welcome script posts a detailed comment that includes:
- Complete system status with component verification
- Quick command references for all operations
- A2A pipeline architecture visual diagram
- Comprehensive documentation links
- Monitoring & diagnostics commands
- Pipeline schedule information
- Expected comment format examples
- Infrastructure design principles
- Full @create-botter attribution

### Step 3: Verify Setup

**Check the tracking issue:**
```bash
./tools/adk-pipeline-status.sh view
```

**Verify workflow configuration:**
```bash
# Check that workflow exists and is enabled
gh workflow list | grep "adk-a2a-blog-pipeline"

# View workflow schedule
gh workflow view adk-a2a-blog-pipeline.yml
```

### Step 4: Test Pipeline Run (Optional)

Trigger a test run to verify the tracking system:

```bash
# Trigger dry run (no actual deployment)
gh workflow run adk-a2a-blog-pipeline.yml -f dry_run=true

# Watch the run
gh run watch

# Check that comment was posted
./tools/adk-pipeline-status.sh recent
```

## Label Requirements

The tracking issue **MUST** have the `adk-pipeline` label for the workflow to find it.

### Why This Label Matters

The workflow uses **label-based discovery** to find the tracking issue:

```yaml
# From .github/workflows/adk-a2a-blog-pipeline.yml
ISSUE_NUMBER=$(gh issue list --label "adk-pipeline" --state open --limit 1 --json number --jq '.[0].number')
```

**Benefits of label-based discovery:**
- ✅ No hardcoded issue numbers
- ✅ Self-healing if issue is recreated
- ✅ Works with any issue number
- ✅ Automatic synchronization

### Adding/Verifying Labels

**Check current labels:**
```bash
gh issue view <issue_number> --json labels --jq '.labels[].name'
```

**Add missing label:**
```bash
gh issue edit <issue_number> --add-label "adk-pipeline"
```

**Add automated label (recommended):**
```bash
gh issue edit <issue_number> --add-label "automated"
```

## Workflow Integration

### How the Workflow Uses the Tracking Issue

The workflow (`.github/workflows/adk-a2a-blog-pipeline.yml`) runs every 6 hours and:

1. **Finds tracking issue** by label `adk-pipeline`
2. **Creates issue if missing** with the standard title and body
3. **Posts run summary** as a comment with:
   - Timestamp (UTC)
   - Trigger type (schedule/manual)
   - Execution mode (simulation/cloud run)
   - Run results
   - Link to workflow run

### Workflow Schedule

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
```

**Run times (UTC):**
- 00:00 - Midnight
- 06:00 - Morning  
- 12:00 - Noon
- 18:00 - Evening

### Manual Triggers

**Basic trigger:**
```bash
gh workflow run adk-a2a-blog-pipeline.yml
```

**With custom topic:**
```bash
gh workflow run adk-a2a-blog-pipeline.yml -f topic_query="AI safety research"
```

**Dry run mode:**
```bash
gh workflow run adk-a2a-blog-pipeline.yml -f dry_run=true
```

**With debug logging:**
```bash
gh workflow run adk-a2a-blog-pipeline.yml -f debug=true
```

## Helper Script Commands

The `tools/adk-pipeline-status.sh` script provides convenient management:

### View Tracking Issue

```bash
./tools/adk-pipeline-status.sh view
```

Shows the complete tracking issue with all comments in your terminal.

### Check Recent Runs

```bash
./tools/adk-pipeline-status.sh recent
```

Displays the last 10 pipeline workflow runs with their status.

### Show Failed Runs

```bash
./tools/adk-pipeline-status.sh failed
```

Lists only failed runs for troubleshooting.

### Trigger New Run

```bash
./tools/adk-pipeline-status.sh trigger
```

Interactively trigger a new pipeline run with options for topic, dry run, and debug mode.

### Check Agent Health

```bash
./tools/adk-pipeline-status.sh health
```

Checks the health status of deployed Cloud Run agents (requires `gcloud` CLI).

### Display Help

```bash
./tools/adk-pipeline-status.sh help
```

Shows usage information and available commands.

## Initialization Scripts

### Welcome Posting Script (✨ Recommended)

**Script:** `tools/post-adk-tracking-welcome.sh`

**What It Does:**

1. **Finds tracking issue** by label (or uses provided issue number)
2. **Posts comprehensive welcome comment** from `docs/issue-comments/ADK_PIPELINE_TRACKING_WELCOME.md` with:
   - Complete system status with component verification
   - Quick command references for all operations
   - A2A pipeline architecture visual diagram
   - Comprehensive documentation links
   - Monitoring & diagnostics commands
   - Pipeline schedule information
   - Expected comment format examples
   - Infrastructure design principles
   - Full @create-botter attribution

**Usage:**

**Auto-detect tracking issue:**
```bash
./tools/post-adk-tracking-welcome.sh
```

**Specify issue number:**
```bash
./tools/post-adk-tracking-welcome.sh 4069
```

**When to Use:**
- **First-time setup** - Initialize new tracking issue (primary use case)
- **After recreation** - Re-initialize if issue was deleted/recreated
- **Documentation update** - Refresh welcome comment with latest info
- **Onboarding** - Help new team members understand the system

### Legacy Initialization Script

**Script:** `tools/initialize-adk-tracking-issue.sh`

**What It Does:**

1. **Finds tracking issue** by label (or uses provided issue number)
2. **Posts welcome comment** with:
   - System status overview
   - Quick command references
   - Pipeline architecture diagram
   - Documentation links
   - Schedule information
   - Monitoring commands

**Usage:**

**Auto-detect tracking issue:**
```bash
./tools/initialize-adk-tracking-issue.sh
```

**Specify issue number:**
```bash
./tools/initialize-adk-tracking-issue.sh 194
```

**Note:** Consider using `post-adk-tracking-welcome.sh` instead for more comprehensive initialization.

## Expected Comment Format

Each pipeline run will post a structured comment:

```markdown
## Pipeline Run: 2025-12-26 12:00:00 UTC

| Property | Value |
|----------|-------|
| Trigger | schedule |
| Mode | simulation |
| Workflow Run | [#1885](https://github.com/enufacas/Chained/actions/runs/1885) |

### Summary

Pipeline executed successfully in simulation mode.

- 🔬 Academic Research: Topics discovered
- 📈 Google Trends: SEO analysis complete
- ✍️ Blog Writer: Content generated

---
*🤖 Created by [ADK A2A Blog Pipeline](https://github.com/enufacas/Chained/actions/runs/1885)*
```

## Troubleshooting

### Issue Not Found

**Problem:** `No tracking issue found with label 'adk-pipeline'`

**Solutions:**
1. Create tracking issue with correct label
2. Verify label spelling (case-sensitive: `adk-pipeline`)
3. Check issue is open (not closed)

### Workflow Not Finding Issue

**Problem:** Workflow creates duplicate issue instead of using existing one

**Solutions:**
1. Verify existing issue has `adk-pipeline` label
2. Check issue state is `open`
3. Ensure only one open issue has the label

### No Comments Posted

**Problem:** Pipeline runs but doesn't post comments

**Solutions:**
1. Check workflow permissions (needs `issues: write`)
2. Verify `GH_TOKEN` secret is configured
3. Review workflow logs for errors
4. Ensure report job completed successfully

### Script Permission Denied

**Problem:** `./tools/initialize-adk-tracking-issue.sh: Permission denied`

**Solution:**
```bash
chmod +x tools/initialize-adk-tracking-issue.sh
```

### GitHub CLI Not Authenticated

**Problem:** `gh: authentication required`

**Solution:**
```bash
gh auth login
```

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│  Tracking Issue (Label: "adk-pipeline")                 │
│  ├─ Title: 🤖 ADK A2A Blog Pipeline Status             │
│  ├─ Body: Tracking issue for pipeline runs             │
│  └─ Comments: Run summaries (posted by workflow)       │
└─────────────────────────────────────────────────────────┘
                           ▲
                           │ posts comment
                           │
┌─────────────────────────────────────────────────────────┐
│  Workflow: adk-a2a-blog-pipeline.yml                    │
│  ├─ Schedule: Every 6 hours                             │
│  ├─ Pre-flight: Check configuration                     │
│  ├─ Pipeline: Run A2A agents                            │
│  └─ Report: Find/create issue, post comment            │
└─────────────────────────────────────────────────────────┘
                           │
                           │ orchestrates
                           ▼
┌─────────────────────────────────────────────────────────┐
│  A2A Agents (ADK-based)                                 │
│  ├─ Academic Research Agent (port 8081)                │
│  ├─ Google Trends Agent (port 8083)                    │
│  └─ Blog Writer Agent (port 8082)                      │
└─────────────────────────────────────────────────────────┘
```

### Label-Based Discovery Flow

```
1. Workflow starts
2. Report job runs
3. Find issue: gh issue list --label "adk-pipeline" --state open
4. If found: Use existing issue
5. If not found: Create new issue with label
6. Post comment with run summary
7. Link to workflow run for details
```

## Best Practices

### Do ✅

- Keep only one open tracking issue with `adk-pipeline` label
- Use the initialization script for consistent welcome comments
- Monitor the tracking issue for pipeline health
- Check failed runs regularly for issues
- Use helper script commands for common tasks

### Don't ❌

- Don't remove the `adk-pipeline` label
- Don't close the tracking issue unless creating a new one
- Don't manually edit workflow-posted comments
- Don't create multiple tracking issues with the same label
- Don't hardcode issue numbers in scripts or docs

## Maintenance

### Regular Tasks

**Weekly:**
- Review recent pipeline runs for failures
- Check agent health status
- Verify comments are posting correctly

**Monthly:**
- Archive old tracking issues if creating new ones
- Update documentation if workflow changes
- Review pipeline success rates

**As Needed:**
- Re-initialize tracking issue after major changes
- Update helper scripts if workflow changes
- Refresh documentation links

### Issue Lifecycle

**Creating:**
1. Use workflow auto-creation OR
2. Manual creation with correct title/labels

**Monitoring:**
1. Watch for new comments from scheduled runs
2. Check workflow runs via `gh run list`
3. Review agent health periodically

**Archiving:**
1. Close old tracking issue
2. Create new tracking issue with same label
3. Initialize new issue with welcome comment
4. Workflow automatically finds new issue

## Documentation Links

### Quick Reference
- [ADK Pipeline Quick Reference](../ADK_PIPELINE_QUICK_REF.md)
- [Helper Script Usage](#helper-script-commands)

### Detailed Guides
- [ADK Pipeline Status Guide](../ADK_PIPELINE_STATUS_GUIDE.md)
- [ADK Pipeline Tracking Guide](../ADK_PIPELINE_TRACKING_GUIDE.md)
- [Complete Implementation Summary](../../ADK_PIPELINE_STATUS_COMPLETE_SUMMARY.md)

### Technical Documentation
- [Workflow File](../../.github/workflows/adk-a2a-blog-pipeline.yml)
- [Helper Script](../../tools/adk-pipeline-status.sh)
- [Welcome Posting Script (Recommended)](../../tools/post-adk-tracking-welcome.sh) ✨
- [Initialization Script (Legacy)](../../tools/initialize-adk-tracking-issue.sh)
- [Welcome Comment Template](../issue-comments/ADK_PIPELINE_TRACKING_WELCOME.md)
- [ADK Agents Directory](../../infrastructure/docker/adk-agents/)
- [Orchestrator](../../infrastructure/docker/adk-agents/orchestrator.py)

### Tests
- [Pipeline Tests](../../tests/test_adk_blog_pipeline.py)

## Success Criteria

A properly configured tracking issue will have:

- ✅ Title: `🤖 ADK A2A Blog Pipeline Status`
- ✅ Label: `adk-pipeline` (required)
- ✅ Label: `automated` (recommended)
- ✅ State: `open`
- ✅ Welcome comment with system overview
- ✅ Regular comments from workflow runs (every 6 hours)
- ✅ Links to workflow runs in comments
- ✅ Clear run summaries with timestamps

## Support

### Getting Help

**For questions about:**
- Tracking issue setup → This document
- Pipeline execution → [ADK Pipeline Status Guide](../ADK_PIPELINE_STATUS_GUIDE.md)
- Helper scripts → Run `./tools/adk-pipeline-status.sh help`
- Workflow issues → Check [workflow logs](../../.github/workflows/adk-a2a-blog-pipeline.yml)
- ADK agents → See [ADK Agents README](../../infrastructure/docker/adk-agents/README.md)

### Reporting Issues

**Create GitHub issue with appropriate label:**
- `workflow-issue` - Workflow execution problems
- `agent-issue` - ADK agent failures
- `documentation` - Documentation gaps or errors
- `bug` - General bugs or unexpected behavior

---

**🏗️ Setup Guide by @create-botter** - _Creating infrastructure that illuminates possibilities._

**Document Version:** 1.0  
**Last Updated:** 2025-12-26  
**Status:** Complete and operational
