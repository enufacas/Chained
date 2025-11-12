# Workflow Health - Quick Reference

## Problem Fixed

**Issue:** 35% workflow failure rate due to HTTP 403 errors when workflows tried to trigger other workflows.

**Solution:** Removed all workflow triggering attempts; rely on scheduled triggers instead.

## What Changed

### 1. Agent Spawn → Assignment Flow
**Before:**
- Spawn PR merges → auto-review-merge tries to trigger copilot-graphql-assign → HTTP 403 error → workflow fails

**After:**
- Spawn PR merges → auto-review-merge removes spawn-pending label → scheduled copilot-graphql-assign picks it up (max 15 min delay)

### 2. System Kickoff
**Before:**
- Tries to trigger learn-from-tldr, learn-from-hackernews, idea-generator → HTTP 403 errors → workflow fails

**After:**
- Displays schedule information and confirms system is ready → no triggering attempts → no failures

### 3. Monitoring
**Before:**
- Simple failure count and percentage

**After:**
- Detailed breakdown of which workflows are failing
- Common causes and solutions
- Actionable recommendations

## Key Schedules

- **copilot-graphql-assign**: Every 15 minutes
- **learn-from-tldr**: 08:00, 20:00 UTC daily
- **learn-from-hackernews**: 07:00, 13:00, 19:00 UTC daily
- **idea-generator**: 09:00 UTC daily
- **agent-spawner**: 06:00, 18:00 UTC daily
- **auto-review-merge**: Every 2 hours
- **system-monitor**: Every 3-6 hours

## Why This Works

1. **GitHub Token Permissions**: The default GITHUB_TOKEN cannot trigger workflows (security feature)
2. **Scheduled Triggers**: More reliable than manual triggering
3. **Label-Based Coordination**: spawn-pending label controls when assignment happens
4. **Self-Sustaining**: No manual intervention needed

## Expected Results

- **Failure Rate**: Down from 35% to <10%
- **Failures Eliminated**: ~21 per 100 runs
- **Delay Impact**: Max 15 minutes for Copilot assignment (avg 7.5 min)
- **System Operation**: Fully autonomous, no breaking changes

## If You See Failures

1. Check the monitoring issue for detailed breakdown
2. Look for patterns (same workflow failing repeatedly)
3. Review common causes:
   - Missing COPILOT_PAT secret
   - External API unavailable
   - Configuration errors
   - Permission issues

## Files Modified

- `.github/workflows/auto-review-merge.yml` - Removed workflow triggering
- `.github/workflows/system-kickoff.yml` - Removed workflow triggering
- `.github/workflows/system-monitor.yml` - Enhanced diagnostics

---

*For detailed analysis, see WORKFLOW_HEALTH_FIX_SUMMARY.md*
