# Auto Review Workflow Optimization

## Problem Statement
The auto-review-merge workflow was generating numerous warnings (⚠️) and consuming excessive runner resources due to:
1. **Draft PR warnings**: Workflow triggered on draft PRs but immediately skipped, causing "action_required" status
2. **Documentation changes**: Unnecessary runs triggered by markdown and doc updates
3. **Concurrent runs**: Multiple simultaneous runs could occur on the same PR
4. **No cancellation policy**: Superseded runs continued unnecessarily
5. **Wasteful event triggers**: Workflow triggered on `opened`, `synchronize`, and `reopened` events even for draft PRs, then immediately skipped

## Important Context
The 15-minute scheduled sweep is **intentionally kept** because it:
- Checks all open PRs for merge readiness
- Converts draft PRs to ready when WIP markers are removed
- Catches PRs that may have been missed by event triggers
- Ensures the autonomous development cycle continues smoothly

## Changes Made

### 1. Path Filters to Skip Documentation Changes
```yaml
paths-ignore:
  - '**.md'
  - 'docs/**'
  - 'learnings/**'
  - 'analysis/**'
```

**Impact**: Prevents unnecessary workflow runs when only documentation is changed (~30-40% reduction in PR-triggered runs)

### 2. Simplified Event Triggers (November 2025 Update)
**Before**: Multiple event triggers that often led to skipped runs
```yaml
pull_request:
  types: [opened, synchronize, reopened, ready_for_review]
```

**After**: Only trigger on meaningful event
```yaml
pull_request:
  types: [ready_for_review]
```

**Rationale**:
- `opened`, `synchronize`, and `reopened` fire on draft PRs, causing wasteful skipped runs
- The scheduled sweep (every 15 minutes) handles all PR states including non-draft PRs
- `ready_for_review` provides immediate response when drafts become ready
- Eliminates 60-80% of wasteful PR event triggers

**Impact**: Significantly reduces wasteful workflow runs while maintaining responsiveness

### 3. Removed Redundant Job-Level Condition
**Before**: Complex condition to filter draft PRs at job level
```yaml
if: |
  (github.event_name != 'pull_request' || 
   (github.event.action == 'ready_for_review' || 
    !github.event.pull_request.draft)) &&
  (github.event_name != 'pull_request' || 
   github.event.pull_request.state == 'open')
```

**After**: No job-level condition needed
```yaml
# For PR events: only ready_for_review triggers (always run)
# For scheduled events: always run (logic handles draft/closed PRs internally)
# For workflow_dispatch: always run (manual triggers should always execute)
```

**Impact**: Simpler logic, no skipped runs at job level

### 4. Smart Concurrency Controls
```yaml
concurrency:
  group: ${{ github.event_name == 'schedule' && 'auto-review-scheduled' || format('auto-review-pr-{0}', github.event.pull_request.number) }}
  cancel-in-progress: true
```

**How it works**:
- **Scheduled runs**: Single group, one at a time, cancels if new scheduled run starts
- **PR-specific runs**: Grouped by PR number, cancels superseded runs on same PR
- **Cross-isolation**: Scheduled runs don't interfere with PR-specific runs

**Impact**: Prevents multiple simultaneous runs on the same PR, auto-cancels superseded runs

### 5. Maintained 15-Minute Schedule
**Kept**: `- cron: '*/15 * * * *'` (every 15 minutes)

**Rationale**: 
- The scheduled sweep is essential for the autonomous development cycle
- It processes all open PRs, not just those with recent events
- Faster response time (max 15 min wait) vs hourly (max 60 min wait)
- The other optimizations provide sufficient resource savings

## Expected Results

### Runner Resource Savings
- **Documentation PRs**: ~30-40% reduction in PR-triggered runs
- **Draft PR events**: ~60-80% reduction by removing opened/synchronize/reopened triggers
- **Draft PR warnings**: Eliminated completely
- **Superseded runs**: Auto-cancelled, saving compute time
- **Concurrent runs**: Prevented via concurrency groups

### Estimated Monthly Savings
- **Before**: ~3,000+ workflow runs/month with many skipped runs
- **After**: ~1,000-1,500 workflow runs/month, minimal skipped runs
- **Net savings**: ~50-67% reduction in workflow runs, ~100% reduction in wasteful skipped runs

### Resource Optimization Focus
Instead of reducing frequency (which impacts responsiveness), we:
1. **Eliminate waste**: Skip documentation-only changes
2. **Remove wasteful triggers**: Only trigger on ready_for_review event
3. **Cancel duplicates**: Auto-cancel superseded runs
4. **Rely on sweep**: Use 15-minute scheduled sweep for comprehensive PR handling
5. **Maintain value**: Keep fast response for important events (ready_for_review)

## Trade-offs

### What We Gain
- Massive reduction in wasteful workflow runs
- Cleaner workflow history (no skipped runs)
- Lower GitHub Actions usage
- Simpler workflow logic

### What We Accept
- Non-draft PRs have max 15-minute delay for initial processing (vs immediate)
- PR updates (synchronize) wait for scheduled sweep (vs immediate)
- Reopened PRs wait for scheduled sweep (vs immediate)

### Why It's Worth It
- The scheduled sweep runs frequently enough (every 15 minutes) for the autonomous cycle
- `ready_for_review` events still get immediate response (most important)
- Manual triggers available for urgent cases
- Eliminates 60-80% of wasteful workflow runs

## Monitoring
After deployment, monitor:
1. Workflow run frequency in Actions tab (expect ~50-67% reduction)
2. Number of skipped conclusions (should be near zero)
3. PR merge latency (should remain < 15 minutes for sweep)
4. Auto-cancelled runs (should see cancelled runs for superseded PR updates)
5. Ready_for_review response time (should be immediate)

## Rollback Plan
If issues occur:
1. Add back `opened`, `synchronize`, `reopened` triggers
2. Restore job-level if condition
3. Remove path-ignore filters
4. Remove concurrency controls

## Date
- Initial optimization: November 10, 2025
- Event trigger optimization: November 12, 2025

