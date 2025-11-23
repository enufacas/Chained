# Meta-Coordinator Implementation Guide

**Created by:** @support-master  
**Date:** 2025-11-23  
**Status:** READY FOR DEPLOYMENT

---

## Overview

This guide provides step-by-step instructions for deploying the **meta-coordinator-system** agent to orchestrate the tech lead review and agent assignment system.

## What Was Implemented

### 1. Meta-Coordinator System Agent

**File:** `.github/agents/meta-coordinator-system.md`

**Key Features:**
- ✅ Comprehensive tools and permissions
- ✅ Wide, permissive access as requested
- ✅ Full system orchestration responsibilities
- ✅ All 6 core areas covered:
  - PR review orchestration
  - Feedback issue creation
  - Agent assignment
  - Review cycle management
  - Auto-merge eligibility
  - Exception handling

**Tools & Access:**
- `gh` CLI for all GitHub operations
- `match-issue-to-agent.py` for agent matching
- `match-pr-to-tech-lead.py` for tech lead matching
- `assign-copilot-to-issue.sh` for Copilot assignment
- GitHub API access
- Repository file access (bash, view, edit, create)
- All github-mcp-server tools

**Permissions:**
- `contents: write`
- `issues: write`
- `pull-requests: write`
- `actions: read`

### 2. Meta-Coordinator Workflow

**File:** `.github/workflows/meta-coordinator.yml`

**Key Features:**
- ✅ Runs every 5 minutes (continuous orchestration)
- ✅ Manual dispatch with options (focus area, dry run)
- ✅ Creates coordination issue for agent
- ✅ Comprehensive agent instructions in issue body
- ✅ Monitors and reports progress

**Triggers:**
- **Schedule:** Every 5 minutes (primary)
- **Manual:** `workflow_dispatch` with controls
- **Optional:** Can add event triggers (currently commented)

## Deployment Steps

### Phase 1: Validation (5 minutes)

#### 1.1 Verify Agent Definition

```bash
# Check agent file exists
ls -la .github/agents/meta-coordinator-system.md

# Validate YAML frontmatter
head -20 .github/agents/meta-coordinator-system.md
```

**Expected:** File exists with valid frontmatter

#### 1.2 Verify Workflow

```bash
# Check workflow exists
ls -la .github/workflows/meta-coordinator.yml

# Validate workflow syntax
gh workflow view meta-coordinator.yml --repo enufacas/Chained
```

**Expected:** Workflow file exists and syntax is valid

#### 1.3 Check Prerequisites

```bash
# Verify tools exist
ls -la tools/match-issue-to-agent.py
ls -la tools/match-pr-to-tech-lead.py
ls -la tools/assign-copilot-to-issue.sh

# Check labels exist
gh label list --repo enufacas/Chained | grep -E "needs-tech-lead-review|tech-lead-approved|tech-lead-changes-requested|assigned-agent"
```

**Expected:** All tools and labels exist

### Phase 2: Initial Deployment (10 minutes)

#### 2.1 Merge PR

```bash
# This PR contains the implementation
# Review and merge PR for meta-coordinator implementation
```

#### 2.2 Enable Workflow

The workflow is already enabled when merged. It will start running on the next 5-minute schedule.

#### 2.3 Manual Test Run

```bash
# Trigger a manual test run with dry-run mode
gh workflow run meta-coordinator.yml \
  --repo enufacas/Chained \
  -f focus_area=all \
  -f dry_run=true

# Wait 30 seconds for workflow to start
sleep 30

# Get the run ID
run_id=$(gh run list --workflow=meta-coordinator.yml --limit 1 --json databaseId --jq '.[0].databaseId')

# View the run
gh run view $run_id --repo enufacas/Chained
```

**Expected:** Workflow runs successfully, creates coordination issue

#### 2.4 Monitor First Run

```bash
# Find the coordination issue
issue_number=$(gh issue list --label "meta-coordination" --limit 1 --json number --jq '.[0].number')

# View the issue
gh issue view $issue_number --repo enufacas/Chained

# Watch for agent activity
gh issue view $issue_number --comments --repo enufacas/Chained
```

**Expected:** Agent posts summary comment, closes issue within 10 minutes

### Phase 3: Validation (15 minutes)

#### 3.1 Check System Operations

After first run completes, verify:

```bash
# Check if PRs were processed
gh pr list --repo enufacas/Chained --json number,labels,title | jq '.'

# Check if issues were assigned
gh issue list --repo enufacas/Chained --json number,assignees,labels | jq '.'

# Check coordination issue was closed
gh issue view $issue_number --json state --jq '.state'
```

**Expected:** 
- PRs have appropriate labels
- Issues have agent assignments
- Coordination issue is closed

#### 3.2 Review Agent Summary

```bash
# Get agent's summary comment
gh issue view $issue_number --comments --repo enufacas/Chained | tail -50
```

**Expected:** Detailed summary with:
- System state counts
- Actions taken list
- Metrics
- System health status

#### 3.3 Verify No Errors

```bash
# Check workflow logs for errors
gh run view $run_id --log --repo enufacas/Chained | grep -i error

# Check for failed operations
gh run view $run_id --log --repo enufacas/Chained | grep -i failed
```

**Expected:** No critical errors

### Phase 4: Production Monitoring (Ongoing)

#### 4.1 Monitor Schedule Runs

```bash
# List recent workflow runs
gh run list --workflow=meta-coordinator.yml --limit 10 --repo enufacas/Chained

# Check success rate
gh run list --workflow=meta-coordinator.yml --limit 20 --json conclusion --jq '[.[] | .conclusion] | group_by(.) | map({key: .[0], count: length})'
```

**Expected:** High success rate (>95%)

#### 4.2 Monitor System Metrics

Track these metrics from agent summaries:
- **PRs processed per run**: Should match open PR count
- **Issues assigned per run**: Should decrease as backlog clears
- **Feedback issues created**: Should match change request rate
- **Exceptions handled**: Should be low (<5%)
- **Run duration**: Should stay under 10 minutes

#### 4.3 Monitor System Health

Check for these indicators:
- ✅ All reviewable PRs have tech lead assignment
- ✅ All PRs with changes requested have feedback issues
- ✅ All open issues have agent assignment
- ✅ No conflicting labels
- ✅ No stale reviews (>7 days)

### Phase 5: Optimization (Optional)

#### 5.1 Enable Event Triggers

After validating schedule runs work well, optionally enable event triggers for immediate response:

Edit `.github/workflows/meta-coordinator.yml`:

```yaml
on:
  schedule:
    - cron: '*/5 * * * *'
  
  workflow_dispatch:
    # ... (keep existing)
  
  # Enable for immediate response
  issues:
    types: [opened]
  pull_request:
    types: [opened, synchronize, labeled]
  pull_request_review:
    types: [submitted]
```

**Benefit:** Faster response (<60s vs 5min)  
**Trade-off:** More workflow runs, potential rate limiting

#### 5.2 Adjust Schedule Frequency

If system is stable and traffic is low, can reduce frequency:

```yaml
on:
  schedule:
    - cron: '*/10 * * * *'  # Every 10 minutes instead of 5
```

**Benefit:** Fewer workflow runs, lower cost  
**Trade-off:** Slower response (10min vs 5min)

#### 5.3 Add Monitoring Dashboard

Create a simple dashboard issue to track metrics:

```bash
gh issue create \
  --title "📊 Meta-Coordinator System Dashboard" \
  --body "## System Metrics

Updated automatically by meta-coordinator runs.

### Last 24 Hours
- Total runs: TBD
- PRs processed: TBD
- Issues assigned: TBD
- Feedback issues created: TBD
- Exceptions: TBD

### Success Rate
- Successful runs: TBD%
- Failed runs: TBD%
- Average duration: TBD minutes" \
  --label "dashboard,automated" \
  --repo enufacas/Chained
```

## Configuration Options

### Focus Area

Control what the agent processes:

```bash
# Process everything
gh workflow run meta-coordinator.yml -f focus_area=all

# Focus on PRs only
gh workflow run meta-coordinator.yml -f focus_area=prs

# Focus on issues only
gh workflow run meta-coordinator.yml -f focus_area=issues

# Focus on reviews only
gh workflow run meta-coordinator.yml -f focus_area=reviews
```

### Dry Run

Test without making changes:

```bash
# Dry run - see what would happen
gh workflow run meta-coordinator.yml -f dry_run=true

# Real run - make changes
gh workflow run meta-coordinator.yml -f dry_run=false
```

## Troubleshooting

### Issue: Workflow not running

**Check:**
```bash
# Verify workflow is enabled
gh workflow view meta-coordinator.yml --repo enufacas/Chained

# Check recent runs
gh run list --workflow=meta-coordinator.yml --limit 5
```

**Solution:**
- Ensure workflow file is merged to main
- Check schedule syntax is correct
- Verify workflow permissions

### Issue: Agent not responding

**Check:**
```bash
# Find coordination issue
gh issue list --label "meta-coordination" --state open

# Check if assigned to copilot
gh issue view <issue_number> --json assignees
```

**Solution:**
- Verify issue is assigned to copilot
- Check if agent profile is correct
- Manually trigger via web UI if needed

### Issue: Rate limit errors

**Check:**
```bash
# Check rate limit
gh api rate_limit --jq '.rate'
```

**Solution:**
- Reduce schedule frequency (10min vs 5min)
- Add rate limit checks in agent logic
- Use COPILOT_PAT if available (higher limits)

### Issue: Conflicting with old workflows

**Check:**
```bash
# List all active workflows
gh workflow list --repo enufacas/Chained
```

**Solution:**
- Disable old workflows:
  - `copilot-graphql-assign.yml`
  - `copilot-pr-assignment.yml`
  - Keep `auto-review-merge.yml` but simplify it

```bash
# Disable workflow
gh workflow disable copilot-graphql-assign.yml --repo enufacas/Chained
```

### Issue: Performance degradation

**Check:**
```bash
# Monitor run durations
gh run list --workflow=meta-coordinator.yml --limit 10 --json conclusion,createdAt,updatedAt
```

**Solution:**
- Optimize agent logic (batch operations)
- Increase time limit in workflow
- Split into multiple focused workflows if needed

## Success Criteria

Deployment is successful when:

- ✅ Workflow runs every 5 minutes without errors
- ✅ Agent processes all open PRs and issues
- ✅ Tech leads assigned within 5 minutes of PR opening
- ✅ Feedback issues created within 5 minutes of change request
- ✅ Agents assigned within 5 minutes of issue opening
- ✅ Review cycles managed correctly
- ✅ No conflicting labels or orphaned issues
- ✅ Run duration stays under 10 minutes
- ✅ System health remains at 100%

## Rollback Plan

If issues arise, can rollback:

### Option 1: Disable Workflow

```bash
# Temporarily disable
gh workflow disable meta-coordinator.yml --repo enufacas/Chained

# Re-enable old workflows
gh workflow enable copilot-graphql-assign.yml --repo enufacas/Chained
gh workflow enable copilot-pr-assignment.yml --repo enufacas/Chained
```

### Option 2: Revert Commit

```bash
# Find commit that added meta-coordinator
git log --oneline --grep "meta-coordinator"

# Revert that commit
git revert <commit_hash>
git push origin main
```

### Option 3: Emergency Manual Mode

If automation fails completely:
1. Disable all automatic workflows
2. Manually assign tech leads to PRs
3. Manually create feedback issues
4. Manually assign agents to issues
5. Fix automation, then re-enable

## Next Steps After Deployment

1. **Monitor for 24 hours**: Watch first day of operations
2. **Gather metrics**: Collect performance data
3. **Optimize as needed**: Adjust based on observations
4. **Document learnings**: Update this guide with findings
5. **Consider enhancements**: Event triggers, dashboards, etc.

## Support

For issues or questions:
1. Check workflow logs: `gh run view <run_id> --log`
2. Check coordination issues: `gh issue list --label meta-coordination`
3. Review agent summaries for error messages
4. Create issue with `meta-coordinator-support` label

---

**@support-master** has provided complete implementation of the meta-coordinator approach with comprehensive tools and wide, permissive access as requested.

*Implementation ready for deployment: 2025-11-23*
