# Autonomous Development Cycle

## Overview

The Chained repository operates as a perpetual motion machine for AI-driven development. This document explains how the autonomous cycle works after the workflow dispatch fixes.

## The Complete Cycle

### 1. Learning Phase (Continuous)

**Workflows:**
- `learn-from-tldr.yml` - Runs at 08:00 and 20:00 UTC daily
- `learn-from-hackernews.yml` - Runs at 07:00, 13:00, and 19:00 UTC daily

**Process:**
1. Workflow runs on schedule
2. Fetches latest tech news and trends
3. Extracts key learnings and insights
4. Saves to `learnings/` directory
5. Creates branch: `learning/{source}-YYYYMMDD-HHMMSS`
6. Creates PR with labels: `automated`, `learning`, `copilot`
7. Workflow completes

**Output:** Learning PR ready for auto-merge

### 2. Auto-Review Phase (Every 15 minutes)

**Workflow:**
- `auto-review-merge.yml` - Runs every 15 minutes + on PR events

**Process:**
1. Detects new PR (learning, timeline, or feature)
2. Validates PR author:
   - ✅ Repository owner with `copilot` label, OR
   - ✅ Trusted bot with `copilot` label
3. Handles draft PRs:
   - If draft and no "WIP" in title and from trusted source: convert to ready
   - Adds comment explaining automatic conversion
4. Checks PR state:
   - Must be OPEN
   - Must not be draft (after conversion attempt)
   - Must be MERGEABLE
5. Approves PR with automated review
6. Waits 30 seconds for checks
7. Merges PR (squash merge)
8. Deletes branch
9. Comments on related issue (if exists)

**Output:** Learning data merged to main branch

### 3. Idea Generation Phase (Daily)

**Workflows:**
- `idea-generator.yml` - Runs at 09:00 UTC daily
- `smart-idea-generator.yml` - Runs at 10:00 UTC daily (uses learnings)

**Process:**
1. Workflow runs on schedule
2. Reads learnings from `learnings/` directory (smart generator only)
3. Generates AI-focused project ideas
4. Creates GitHub issue with idea details
5. Labels: `ai-generated`, `enhancement`
6. Workflow completes

**Output:** New issue with project idea

### 4. Issue Assignment Phase (On issue creation)

**Workflow:**
- `copilot-graphql-assign.yml` - Runs on issue creation

**Process:**
1. New issue created (from idea generator or manually logged)
2. Checks for COPILOT_PAT secret
3. If configured: Assigns issue to Copilot via API
4. Adds `copilot-assigned` label
5. Adds tracking comment
6. Marks issue as ready for work
7. Workflow completes

**Output:** Issue ready for implementation (with Copilot assigned if PAT configured)

### 5. Implementation Phase (Every 30 minutes)

**Workflow:**
- `issue-to-pr.yml` - Runs every 30 minutes

**Process:**
1. Finds issues with `copilot-assigned` label
2. Excludes issues with `in-progress` or `completed` labels
3. For each issue:
   - Adds `in-progress` label
   - Creates branch: `copilot/issue-{number}-{timestamp}`
   - Creates implementation file: `implementations/issue-{number}.md`
   - Commits changes
   - Creates PR with `copilot` label
   - Links PR to issue
4. Workflow completes

**Output:** Implementation PR ready for review

### 6. Auto-Merge Phase (Every 15 minutes + on PR events)

**Workflow:**
- `auto-review-merge.yml` - Same as step 2

**Process:** (Same as Auto-Review Phase above)

**Output:** Implementation merged to main branch, associated issues closed

### 7. Timeline Update Phase (Every 6 hours)

**Workflow:**
- `timeline-updater.yml` - Runs every 6 hours + on events

**Process:**
1. Fetches repository activity:
   - Recent issues
   - Recent PRs
   - Workflow runs
2. Calculates metrics:
   - Completion rates
   - Merge rates
   - Autonomous actions
3. Updates `docs/data/` JSON files
4. Creates branch: `timeline/update-YYYYMMDD-HHMMSS`
5. Creates PR with labels: `automated`, `copilot`
6. Workflow completes

**Output:** Timeline update PR ready for auto-merge

### 8. Progress Tracking Phase (Every 12 hours)

**Workflow:**
- `progress-tracker.yml` - Runs every 12 hours

**Process:**
1. Analyzes repository progress
2. Generates statistics
3. Creates progress report issue
4. Tracks autonomous success rates
5. Workflow completes

**Output:** Progress report issue

### 9. Health Monitoring Phase (Every 12 hours)

**Workflow:**
- `workflow-monitor.yml` - Runs every 12 hours

**Process:**
1. Checks last 100 workflow runs
2. Calculates failure rates
3. Analyzes error patterns:
   - HTTP 403 errors
   - Permission errors
   - Merge conflicts
4. If issues detected:
   - Creates/updates monitoring issue
   - Provides recommendations
5. Workflow completes

**Output:** Health monitoring issue (if problems detected)

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    PERPETUAL MOTION CYCLE                    │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   LEARNING   │  08:00, 20:00 UTC (TLDR)
    │   WORKFLOWS  │  07:00, 13:00, 19:00 UTC (HN)
    └──────┬───────┘
           │ Create Learning PR
           ▼
    ┌──────────────┐
    │ AUTO-REVIEW  │  Every 15 minutes + on PR events
    │  & MERGE     │  • Validate author & labels
    └──────┬───────┘  • Approve & merge
           │ Learning merged to main
           ▼
    ┌──────────────┐
    │     IDEA     │  09:00 UTC (basic)
    │  GENERATION  │  10:00 UTC (smart, uses learnings)
    └──────┬───────┘
           │ Create issue
           ▼
    ┌──────────────┐
    │    ISSUE     │  On issue created
    │  ASSIGNMENT  │  • Add copilot-assigned label
    └──────┬───────┘
           │ Issue ready
           ▼
    ┌──────────────┐
    │    ISSUE     │  Every 30 minutes
    │   TO PR      │  • Create branch & PR
    └──────┬───────┘
           │ Implementation PR
           ▼
    ┌──────────────┐
    │ AUTO-REVIEW  │  Every 15 minutes + on PR events
    │  & MERGE     │  • Review & merge
    └──────┬───────┘
           │ Implementation merged
           ▼
    ┌──────────────┐
    │    ISSUE     │  Every 30 minutes
    │   CLOSURE    │  • Mark completed & close
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   TIMELINE   │  Every 6 hours
    │    UPDATE    │  • Update metrics → PR
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   PROGRESS   │  Every 12 hours
    │   TRACKER    │  • Generate reports
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   WORKFLOW   │  Every 12 hours
    │   MONITOR    │  • Health checks
    └──────────────┘

         [CYCLE REPEATS CONTINUOUSLY]
```

## Key Principles

### 1. PR-Based Everything
- All changes go through PRs
- No direct commits to main (except system initialization)
- Enables review, rollback, and audit trail

### 2. Scheduled Triggers
- All workflows run on reliable schedules
- No manual triggering required
- No workflow-to-workflow dispatch (avoids permission issues)

### 3. Label-Based Routing
- `copilot` label enables auto-merge
- `automated` label marks autonomous actions
- `learning` label identifies learning updates
- `in-progress`, `completed` track issue state

### 4. Self-Healing
- Monitoring detects failures
- Issues created for human intervention
- Pattern analysis suggests fixes

### 5. Security First
- Only authorized sources can auto-merge
- Label requirements prevent abuse
- State validation before merge

## Autonomous Success Metrics

The system measures its own success:
- **Learning Rate**: New learnings added per day
- **Idea Generation**: New ideas created per day
- **Implementation Rate**: Issues converted to PRs
- **Merge Rate**: PRs successfully merged
- **Completion Rate**: Issues completed/closed
- **Health Score**: Workflow success rate
- **Cycle Time**: Time from idea to merged implementation

## Human Intervention Points

While fully autonomous, humans can intervene at:
1. **Manual workflow triggers**: Use "Run workflow" in Actions tab
2. **Issue creation**: Create issues manually
3. **PR review**: Review and modify PRs before merge
4. **Monitoring**: Respond to health monitoring issues
5. **Configuration**: Update workflow schedules or logic

## Maintenance

### Regular Checks (Automated)
- ✅ Workflow health monitoring (every 12 hours)
- ✅ Progress tracking (every 12 hours)
- ✅ Evaluation script (`./evaluate-workflows.sh`)

### Manual Checks (As needed)
- Review monitoring issues
- Adjust schedules if needed
- Update learning sources
- Refine idea generation prompts

## Conclusion

The Chained autonomous cycle operates continuously without human intervention:
- ✅ Learns from external sources
- ✅ Generates ideas based on learnings
- ✅ Implements ideas through PRs
- ✅ Reviews and merges automatically
- ✅ Tracks progress and health
- ✅ Course-corrects when issues arise

This creates a true perpetual motion machine for AI-driven development! 🚀
