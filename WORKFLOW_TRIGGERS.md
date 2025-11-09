# Workflow Trigger Mechanisms

## Overview

This document explains **how and when workflows execute** in the Chained autonomous system. Understanding these triggers is crucial for trusting that the automation is working.

## The Problem: How Does Copilot Actually Get Work?

When an issue is auto-assigned to Copilot, you might wonder: **"What actually forces the work to happen?"**

The answer: **Scheduled workflows that poll for work on a regular basis.**

## Trigger Types in Chained

### 1. Event Triggers (Immediate)

These workflows run **instantly** when a specific GitHub event occurs:

| Workflow | Event | Description |
|----------|-------|-------------|
| `copilot-assign.yml` | `issues: [opened, labeled]` | Runs immediately when an issue is created or labeled |
| `auto-review-merge.yml` | `pull_request: [opened, synchronize, reopened]` | Runs immediately when a PR is created or updated |
| `auto-kickoff.yml` | `push: branches: [main]` | Runs immediately when code is pushed to main |

**Trust Factor:** ✅ These are highly reliable - GitHub guarantees event triggers fire.

### 2. Schedule Triggers (Cron-based)

These workflows run **on a schedule** using cron expressions:

| Workflow | Schedule | Frequency | Purpose |
|----------|----------|-----------|---------|
| `issue-to-pr.yml` | `*/30 * * * *` | Every 30 minutes | Converts assigned issues to PRs |
| `auto-review-merge.yml` | `*/15 * * * *` | Every 15 minutes | Reviews and merges PRs |
| `auto-close-issues.yml` | `*/30 * * * *` | Every 30 minutes | Closes completed issues |
| `timeline-updater.yml` | `0 */6 * * *` | Every 6 hours | Updates timeline data |
| `progress-tracker.yml` | `0 */12 * * *` | Every 12 hours | Generates progress reports |
| `workflow-monitor.yml` | `0 */12 * * *` | Every 12 hours | Monitors workflow health |
| `idea-generator.yml` | `0 9 * * *` | Daily at 09:00 UTC | Generates basic ideas |
| `smart-idea-generator.yml` | `0 10 * * *` | Daily at 10:00 UTC | Generates smart ideas from learnings |
| `learn-from-tldr.yml` | `0 8,20 * * *` | Daily at 08:00 and 20:00 UTC | Learns from TLDR Tech |
| `learn-from-hackernews.yml` | `0 7,13,19 * * *` | Daily at 07:00, 13:00, 19:00 UTC | Learns from Hacker News |

**Trust Factor:** ⚠️ GitHub Actions scheduled workflows have some known caveats (see below).

### 3. Manual Triggers (workflow_dispatch)

All workflows support manual triggering via the Actions tab or API.

**Trust Factor:** ✅ These work on-demand when you explicitly run them.

## The Complete Automation Flow

Here's exactly how work gets done after an issue is assigned:

```
1. Issue Created (Manual or AI-generated)
   └─> EVENT TRIGGER: copilot-assign.yml runs immediately
       └─> Adds "copilot-assigned" label
       └─> Issue is now in the queue

2. [Wait up to 30 minutes]
   └─> CRON TRIGGER: issue-to-pr.yml runs
       └─> Scans for issues with "copilot-assigned" label
       └─> Creates branch and PR for the issue
       └─> Adds "in-progress" label

3. [Wait up to 15 minutes]
   └─> CRON TRIGGER: auto-review-merge.yml runs
       └─> Finds the new PR
       └─> Reviews and approves it
       └─> Merges to main branch

4. [Wait up to 30 minutes]
   └─> CRON TRIGGER: auto-close-issues.yml runs
       └─> Finds the merged PR
       └─> Closes the related issue
       └─> Adds "completed" label
```

**Key Insight:** The "forcing" mechanism is **passive polling** via scheduled workflows, NOT active dispatching!

## GitHub Actions Schedule Caveats

### Important Limitations to Know

GitHub's documentation warns about scheduled workflow reliability:

1. **Delays During High Load**: Scheduled workflows may run later than scheduled during peak usage times.

2. **Disabled After 60 Days**: In a public repository, scheduled workflows are automatically disabled if there's no activity for 60 days.

3. **Not Guaranteed**: GitHub does not guarantee exact execution times - there can be delays of several minutes.

4. **Minimum Interval**: Some workflows run every 5-15 minutes, which is near the practical limit for reliable scheduling.

### What This Means for Chained

- **Expected behavior**: Most workflows will run close to their scheduled time
- **Possible delays**: During GitHub's peak hours, workflows might run 5-10 minutes late
- **Mitigation**: Multiple workflows check for work, so delays are self-correcting
- **Monitoring**: The `workflow-monitor.yml` tracks execution and alerts on failures

## How to Trust Your Schedules Are Running

### Option 1: Check the Actions Tab

1. Go to your repository's **Actions** tab
2. Filter by workflow name
3. Check the "Last run" timestamp

### Option 2: Use the check-status.sh Script

```bash
./check-status.sh
```

This shows recent workflow runs and timing.

### Option 3: Check Workflow Monitor Issues

The `workflow-monitor.yml` runs every 12 hours and creates issues if:
- Critical workflows are failing frequently
- Error patterns are detected
- Failure rate exceeds thresholds

Check for issues labeled `workflow-monitor`.

### Option 4: Use the New Verification Tool

We provide a new tool to verify schedules are executing:

```bash
./verify-schedules.sh
```

This tool:
- Lists all scheduled workflows
- Shows when they last ran
- Calculates if they're running on schedule
- Warns if any workflow hasn't run when expected
- Shows next expected run time

## Verification Strategies

### Active Monitoring

1. **Enable GitHub Actions notifications** in your repository settings
2. **Watch for workflow-monitor issues** - these indicate problems
3. **Check the timeline** - https://yourusername.github.io/Chained/ shows activity
4. **Review the Actions tab** periodically

### Passive Monitoring

1. **Let the system self-heal** - workflow-monitor detects and reports issues
2. **Trust the event triggers** - these are guaranteed by GitHub
3. **Accept minor delays** - the system is designed to handle them

## Manual Intervention

If you don't trust that schedules are running, you can:

### Trigger Any Workflow Manually

1. Go to **Actions** tab
2. Select the workflow (e.g., "Issue to PR Automator")
3. Click **"Run workflow"**
4. Optionally provide inputs (like issue number)
5. Click **"Run workflow"** button

### Check Why a Workflow Didn't Run

1. Go to **Actions** tab
2. Find the workflow
3. Click on a failed or cancelled run
4. Review the logs
5. Common issues:
   - Permission errors (check workflow permissions)
   - API rate limits (wait and retry)
   - No work to do (expected behavior)

## Improving Schedule Reliability

### What We've Implemented

1. **Multiple polling intervals**: Critical workflows run frequently (every 15-30 minutes)
2. **Event triggers**: Where possible, we use events instead of schedules
3. **Health monitoring**: Automated detection of schedule failures
4. **Manual fallback**: All workflows support manual triggering

### What You Can Do

1. **Keep the repository active**: Push code or create issues regularly to prevent 60-day deactivation
2. **Monitor notifications**: Enable Actions notifications to be alerted of failures
3. **Use manual triggers**: If time-sensitive, trigger workflows manually
4. **Adjust schedules**: If needed, modify cron expressions in workflow files

## Alternative: Event-Based Architecture

If you want **guaranteed** execution without relying on schedules, consider:

### Option A: Webhook-Based Triggers

Set up external webhooks that trigger workflows on specific events.

### Option B: workflow_dispatch Chains

One workflow can trigger another using the GitHub API (requires PAT token with wider permissions).

### Option C: Hybrid Approach

- Keep event triggers for immediate actions (copilot-assign)
- Keep frequent schedules for polling (issue-to-pr, auto-review-merge)
- Add webhook or dispatch fallback for critical operations

## Conclusion

**The process forcing Copilot to work:**
1. Issues get auto-assigned via event trigger (immediate, reliable)
2. Scheduled workflows poll for work every 15-30 minutes (mostly reliable)
3. Work gets done progressively through the automation pipeline
4. Monitoring detects and reports failures

**Trust your schedules by:**
- Using the verification tools provided
- Monitoring the Actions tab and workflow-monitor issues
- Understanding that minor delays are normal and acceptable
- Accepting that GitHub Actions schedules are "best effort" not "guaranteed"

**If schedules concern you:**
- Use manual workflow triggers for time-sensitive operations
- Check the Actions tab regularly
- Enable notifications for workflow failures
- Keep the repository active to prevent 60-day deactivation

The system is designed to be **self-healing** and **delay-tolerant**, so small timing variations don't break the autonomous cycle.
