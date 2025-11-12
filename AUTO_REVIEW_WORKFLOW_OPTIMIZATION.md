# Auto Review Workflow Optimization

**Latest Update (2025-11-12)**: Reduced scheduled run frequency from every 15 minutes to every hour (75% reduction) to address excessive workflow history. Event triggers still provide immediate response to PR activity.

## Problem Statement
The auto-review-merge workflow was generating numerous warnings (⚠️) and consuming excessive runner resources due to:
1. **Draft PR warnings**: Workflow triggered on draft PRs but immediately skipped, causing "action_required" status
2. **Documentation changes**: Unnecessary runs triggered by markdown and doc updates
3. **Concurrent runs**: Multiple simultaneous runs could occur on the same PR
4. **No cancellation policy**: Superseded runs continued unnecessarily

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

### 2. Improved Draft PR Handling
**Before**: Simple draft check that still triggered workflow
```yaml
if: github.event_name != 'pull_request' || !github.event.pull_request.draft
```

**After**: Enhanced condition that properly handles ready_for_review events
```yaml
if: |
  (github.event_name != 'pull_request' || 
   (github.event.action == 'ready_for_review' || 
    !github.event.pull_request.draft)) &&
  (github.event_name != 'pull_request' || 
   github.event.pull_request.state == 'open')
```

**Impact**: Eliminates "action_required" warnings for draft PRs while allowing ready_for_review transitions

### 3. Smart Concurrency Controls
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

### 4. Optimized Schedule Frequency (Updated 2025-11-12)
**Changed from**: `- cron: '*/15 * * * *'` (every 15 minutes)
**Changed to**: `- cron: '0 * * * *'` (every hour)

**Rationale**: 
- Event triggers (PR opened/synchronize/reopened/ready_for_review) provide immediate response
- Scheduled sweep is now a backup/catch-all mechanism, not the primary trigger
- Reduces workflow history clutter (96 → 24 runs/day = 75% reduction)
- Most scheduled runs were finding no PRs to process
- Hourly is still frequent enough for catch-all purposes (vs every 3 hours like other workflows)

## Expected Results

### Runner Resource Savings
- **Documentation PRs**: ~30-40% reduction in PR-triggered runs
- **Draft PR warnings**: Eliminated completely
- **Scheduled runs**: 75% reduction (96 → 24 runs/day)
- **Superseded runs**: Auto-cancelled, saving compute time
- **Concurrent runs**: Prevented via concurrency groups

### Estimated Monthly Savings
- **Before (original)**: ~3,000+ workflow runs/month with warnings
- **After (initial optimization)**: ~2,000-2,400 workflow runs/month, clean status
- **After (schedule optimization)**: ~900-1,200 workflow runs/month
- **Net savings**: ~60-70% reduction in runs, ~100% reduction in warnings

### Resource Optimization Focus
Instead of just reducing frequency, we implemented multiple optimizations:
1. **Eliminate waste**: Skip documentation-only changes (paths-ignore)
2. **Cancel duplicates**: Auto-cancel superseded runs (concurrency)
3. **Fix warnings**: Proper draft PR handling removes "action_required" status
4. **Optimize schedule**: Reduce from every 15 min to every hour (75% reduction)
5. **Maintain value**: Event triggers provide immediate response; hourly sweep as backup

## Monitoring
After deployment, monitor:
1. Workflow run frequency in Actions tab (expect ~60-70% total reduction)
2. Number of "action_required" conclusions (should be near zero)
3. PR merge latency (should remain < 60 minutes for sweep, immediate for events)
4. Auto-cancelled runs (should see cancelled runs for superseded PR updates)
5. Event-triggered runs still provide immediate response to PR changes

## Rollback Plan
If issues occur:
1. Remove path-ignore filters
2. Remove concurrency controls
3. Simplify draft PR condition back to original

## Date
November 10, 2025

