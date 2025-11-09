# Workflow Schedule Investigation - Summary

## Problem Statement

The user wanted to understand:
1. **"What process is forcing Copilot to go do the work?"** - After an issue gets auto-assigned, what actually triggers the work?
2. **"Is there a workflow on a schedule?"** - What's the triggering mechanism?
3. **"I don't trust all my cron schedules are running"** - How to verify schedules are actually executing?

## Investigation Findings

### How the Automation Works

The autonomous system uses **passive polling via scheduled workflows**, not active triggering:

1. **Issue Assignment** (Event Trigger - Immediate)
   - `copilot-graphql-assign.yml` runs instantly when an issue is created
   - Assigns issue to Copilot via API (if COPILOT_PAT configured)
   - Adds "copilot-assigned" label
   - Issue queued for work

2. **Issue to PR** (Cron Schedule - Every 30 minutes)
   - `issue-to-pr.yml` polls for issues with "copilot-assigned" label
   - Creates branch and PR
   - Adds "in-progress" label

3. **Auto Review & Merge** (Cron Schedule - Every 15 minutes)
   - `auto-review-merge.yml` polls for PRs with "copilot" label
   - Reviews, approves, and merges
   - Deletes branch

4. **Issue Closure** (Cron Schedule - Every 30 minutes)
   - `auto-close-issues.yml` polls for merged PRs
   - Closes related issues
   - Adds "completed" label

**Total Time:** 15-75 minutes depending on when scheduled workflows catch the work.

### Schedule Reliability

**GitHub Actions Scheduled Workflows:**
- ✅ Generally reliable and run close to scheduled times
- ⚠️ Can experience 5-10 minute delays during peak hours
- ⚠️ Are "best effort" not "guaranteed" by GitHub
- ⚠️ Automatically disabled after 60 days of repository inactivity
- ⚠️ May experience longer delays during GitHub incidents

**Why This Design:**
- Avoids permission errors (workflow dispatch requires `actions: write`)
- Provides loose coupling between workflows
- Is self-correcting (missed work gets picked up on next run)
- Is delay-tolerant by design
- Easier to monitor and debug

## Solutions Implemented

### 1. Documentation

**WORKFLOW_TRIGGERS.md** (10 KB)
- Complete explanation of all trigger types (event, schedule, manual)
- Detailed automation flow with timing
- GitHub Actions caveats and limitations
- Trust strategies and verification methods
- Visual ASCII diagram of complete flow
- Alternative architectures
- Manual intervention options

**FAQ.md** (15 KB)
- Comprehensive FAQ covering common questions
- Sections on:
  - How automation actually works
  - Trusting cron schedules
  - Troubleshooting issues
  - Manual intervention
  - Configuration options
  - Monitoring and verification
- Real examples and commands

**Updated README.md**
- Added references to new docs
- Enhanced monitoring section
- Added verify-schedules.sh to utilities

### 2. Verification Tool

**verify-schedules.sh** (8.6 KB) - NEW
- Checks when each scheduled workflow last ran
- Compares against expected intervals (with 10% tolerance)
- Color-coded status:
  - ✅ Green: On schedule
  - ⚠️ Yellow: Late but within tolerance
  - ❌ Red: Significantly overdue
- Analyzes recent failures
- Warns about 60-day inactivity deactivation
- Provides actionable recommendations
- Shows summary statistics

**Usage:**
```bash
./verify-schedules.sh
```

**Output includes:**
- Status of each scheduled workflow
- Time since last run
- Whether it's on schedule, late, or overdue
- Recent failure count
- Repository activity status
- Recommended actions

### 3. Enhanced Status Tool

**Updated check-status.sh**
- Fixed incorrect schedule intervals (were way off!)
  - Auto Review & Merge: Every 15 min (was "2 hours")
  - Issue to PR: Every 30 min (was "3 hours")
  - Auto Close Issues: Every 30 min (was "4 hours")
- Added reference to verify-schedules.sh
- Now accurate and useful

## How to Trust Your Schedules

### Primary Method: Use the Verification Tool

```bash
./verify-schedules.sh
```

This shows you exactly:
- When each workflow last ran
- Whether it's running on schedule
- Any overdue workflows
- Recent failures
- Activity status

### Additional Monitoring

1. **Check Actions Tab**
   - View workflow run history
   - See status and timing
   - Review logs for failures

2. **Monitor workflow-monitor Issues**
   - System creates issues when problems detected
   - Look for "workflow-monitor" label
   - Contains diagnostic information

3. **Check GitHub Pages Timeline**
   - https://yourusername.github.io/Chained/
   - Shows recent autonomous activity

4. **Run check-status.sh**
   - Quick overview of system health
   - Issue and PR statistics
   - Recent workflow runs

### Manual Fallback

If schedules aren't running or you need immediate action:

**Via GitHub UI:**
1. Go to Actions tab
2. Select workflow
3. Click "Run workflow"
4. Fill in inputs if needed
5. Click "Run workflow" to confirm

**Via CLI:**
```bash
gh workflow run "workflow-name.yml"
```

## Schedule Frequencies

### Critical Automation Workflows
- `auto-review-merge.yml`: Every 15 minutes
- `issue-to-pr.yml`: Every 30 minutes
- `auto-close-issues.yml`: Every 30 minutes

### Learning Workflows
- `learn-from-hackernews.yml`: 3x daily (07:00, 13:00, 19:00 UTC)
- `learn-from-tldr.yml`: 2x daily (08:00, 20:00 UTC)

### Idea Generation
- `idea-generator.yml`: Daily at 09:00 UTC
- `smart-idea-generator.yml`: Daily at 10:00 UTC

### Monitoring & Reporting
- `timeline-updater.yml`: Every 6 hours
- `progress-tracker.yml`: Every 12 hours
- `workflow-monitor.yml`: Every 12 hours

## Key Takeaways

### For the User

✅ **You CAN trust the schedules** - They're reliable with minor acceptable delays

✅ **You CAN verify execution** - Use `./verify-schedules.sh` to check health

✅ **System is self-healing** - Monitoring detects and reports issues automatically

✅ **Manual fallback exists** - Can always trigger workflows manually if needed

✅ **System is delay-tolerant** - Small timing variations don't break functionality

### Design Philosophy

The autonomous system is built on these principles:

1. **Passive Polling** - Workflows check for work rather than being actively triggered
2. **Loose Coupling** - Workflows are independent and don't call each other
3. **Self-Correcting** - Missed work gets picked up on the next run
4. **Monitored** - Automated health checks detect problems
5. **Transparent** - Easy to verify and debug

### Recommendations

**Daily Use:**
- Let the system run autonomously
- Check GitHub Pages timeline periodically
- Review workflow-monitor issues if they appear

**Weekly Verification:**
```bash
./verify-schedules.sh  # Check schedule health
./check-status.sh      # View overall status
```

**If Concerned:**
- Run verify-schedules.sh to check execution
- Check Actions tab for run history
- Review workflow-monitor issues
- Manually trigger workflows if time-sensitive

**Maintenance:**
- Keep repository active (commit regularly)
- Review workflow-monitor alerts
- Update workflow schedules if needed

## Files Changed

### New Files
- `WORKFLOW_TRIGGERS.md` - Complete trigger documentation (10 KB)
- `FAQ.md` - Comprehensive FAQ (15 KB)
- `verify-schedules.sh` - Schedule verification tool (8.6 KB)
- `SCHEDULE_INVESTIGATION_SUMMARY.md` - This summary (current file)

### Modified Files
- `README.md` - Added references to new docs and tools
- `check-status.sh` - Fixed incorrect schedule intervals

### Lines Changed
- Added: ~1,000 lines of documentation
- Added: ~250 lines of shell script
- Modified: ~20 lines in existing files

## Conclusion

The autonomous system works reliably through **passive scheduled polling**. While GitHub Actions schedules aren't "guaranteed", they're highly reliable in practice. The new verification tool and comprehensive documentation provide the visibility and trust needed to confirm schedules are running properly.

**The system is designed to "just work" with minimal intervention, and now you have the tools to verify that it does.**

---

**Date:** 2025-11-09
**Issue:** Understanding workflow triggers and schedule reliability
**Status:** ✅ Complete
**Artifacts:** 4 new files, 2 modified files, comprehensive documentation and tooling
