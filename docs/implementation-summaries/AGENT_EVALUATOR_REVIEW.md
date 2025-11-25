# Agent Evaluator System Review
## End-to-End Analysis by @support-master

**Date**: 2025-11-22  
**Issue**: Agent evaluator system review - cache lookup and disabled workflows  
**Agent**: @support-master

---

## Executive Summary

The agent evaluator system's cache lookup logic is **working correctly**, but the system is **not running as intended**. All 123 agent metrics are stale (>12-28 hours old), indicating the workflow hasn't executed successfully in over a day despite being scheduled to run daily at midnight UTC.

### Key Findings

1. ✅ **Cache Lookup Logic**: Functioning correctly
2. ❌ **Metrics Freshness**: All metrics are stale (>12h)
3. ⚠️  **Workflow Schedule**: Configured but apparently not triggering
4. ⚠️  **Unused Input**: `force_evaluation` input defined but never used

---

## Detailed Analysis

### 1. Cache Lookup System

**File**: `tools/agent-metrics-collector.py`

The cache lookup system consists of three key methods:

#### `is_metrics_fresh(agent_id, max_age_hours=12.0)` (Lines 1357-1391)
- **Status**: ✅ Working correctly
- **Logic**: 
  1. Loads latest metrics from `.github/agent-system/metrics/{agent_id}/latest.json`
  2. Parses timestamp with proper timezone handling
  3. Calculates age in hours
  4. Returns `True` if age ≤ max_age_hours

**Test Results**:
```
Testing 5 agents:
- agent-176318122315: 28.6h old (STALE)
- agent-176318125320: 28.6h old (STALE)
- agent-1763604149588377518-16542: 28.3h old (STALE)
- agent-1763610423105761116-98104: 28.3h old (STALE)
- agent-1763620733444564165-68520: 28.3h old (STALE)

Result: 0 fresh, 5 stale
```

#### `load_latest_metrics(agent_id)` (Lines 1335-1355)
- **Status**: ✅ Working correctly
- **Logic**: Reads and parses `latest.json` from agent's metrics directory
- Properly handles missing files and parse errors

#### `evaluate_all_agents(since_days, max_age_hours, force_refresh)` (Lines 1435-1536)
- **Status**: ✅ Working correctly
- **Optimization Strategy**:
  1. First pass: Check all agents for fresh cached metrics
  2. Collect agents needing refresh
  3. Batch fetch issues for efficiency
  4. Evaluate only agents needing refresh

**Expected Behavior**: 
- When metrics are fresh (<12h): Use cached data, 0 API calls per agent
- When metrics are stale: Fetch fresh data, ~50-100 API calls per agent

**Current Behavior**:
```
26 active agents total
- From storage: 0 agents (all stale)
- Need refresh: 26 agents (100%)
- Estimated API calls needed: ~1300-2600
```

### 2. Workflow Configuration

**File**: `.github/workflows/agent-evaluator.yml`

#### Schedule Configuration (Lines 4-6)
```yaml
schedule:
  # Run daily at midnight UTC
  - cron: '0 0 * * *'
```

- **Status**: ⚠️ Configured but not executing
- **Expected**: Should run daily at midnight UTC
- **Actual**: Last metrics update was ~28 hours ago

#### Workflow Inputs (Lines 7-13)
```yaml
workflow_dispatch:
  inputs:
    force_evaluation:
      description: 'Force evaluation even if already run today'
      required: false
      type: boolean
      default: false
```

- **Status**: ❌ **BUG - Input defined but never used**
- **Impact**: Manual workflow dispatch cannot force refresh
- **Problem**: The `force_evaluation` input is never referenced in the workflow

#### Evaluation Call (Lines 132-136)
```python
metrics_results = collector.evaluate_all_agents(
    since_days=7,
    max_age_hours=12.0,  # Use metrics stored within last 12 hours
    force_refresh=False  # Prefer stored data when available
)
```

- **Status**: ⚠️ Hardcoded `force_refresh=False`
- **Expected**: Should respect `force_evaluation` input
- **Should be**: 
  ```python
  force_refresh=${{ github.event.inputs.force_evaluation || false }}
  ```

### 3. Metrics Storage

**Directory**: `.github/agent-system/metrics/`

#### Current State
```
Total agent directories: 123
Sample metrics ages:
- agent-1763111986: 172.4h old
- agent-1763604149588377518-16542: 28.3h old
- agent-1763317442: 52.4h old
- agent-176318126822: 100.3h old
- agent-1763258205657852196-3-16512: 52.5h old

Freshness summary: 0 fresh (≤12h), 123 stale (>12h)
```

#### Metrics File Structure
Each agent has:
- `{agent_id}/latest.json` - Most recent metrics
- `{agent_id}/{timestamp}.json` - Historical snapshots

Example `latest.json`:
```json
{
  "agent_id": "agent-1762898916",
  "timestamp": "2025-11-19T01:08:46.193720+00:00",
  "activity": {
    "issues_resolved": 0,
    "issues_created": 0,
    "prs_created": 0,
    "prs_merged": 0,
    "reviews_given": 0,
    "comments_made": 0
  },
  "scores": {
    "code_quality": 0.5,
    "issue_resolution": 0.0,
    "pr_success": 0.0,
    "peer_review": 0.0,
    "creativity": 0.5,
    "overall": 0.225
  },
  "metadata": {
    "lookback_days": 7,
    "repo": "enufacas/Chained",
    "api_calls": 0
  }
}
```

### 4. Optimization Strategy Analysis

The system uses a smart optimization strategy:

#### Storage-First Approach (Lines 1473-1490)
```python
# First, try to use stored metrics where possible
for agent in active_agents:
    if not force_refresh and self.is_metrics_fresh(agent_id, max_age_hours):
        metrics = self.load_latest_metrics(agent_id)
        if metrics:
            results[agent_id] = metrics
            agents_from_storage += 1
            continue
    agents_needing_refresh.append(agent)
```

**Benefits**:
- Avoids redundant API calls
- Fast evaluation when metrics are fresh
- Reduces GitHub API rate limit pressure

**Current Effectiveness**: 0% (all metrics stale)

#### Batch Fetch Optimization (Lines 1495-1499)
```python
if agents_needing_refresh:
    batch_cache = self._batch_fetch_all_agent_issues(since_days)
    # Use batch cache for all agents
```

**Benefits**:
- Single search query for all agent-work issues
- Distributes issues to agents without per-agent searches
- Reduces O(n*m) to O(m) API calls

**Current Effectiveness**: Would work well but runs every time since cache always empty

---

## Root Causes

### Primary Issue: Workflow Not Running on Schedule

**Symptoms**:
- All metrics are 28-172 hours old
- Last evaluation commit was days ago
- Cache system has no fresh data to serve

**Possible Causes**:

1. **GitHub Actions Scheduling Limitations**
   - Scheduled workflows can be delayed or skipped during high load
   - Workflows in repos with low activity may be disabled after 60 days
   - Cron jobs may not trigger if the workflow has errors

2. **Workflow Errors Preventing Completion**
   - Silent failures in the Python script
   - API rate limit exhaustion
   - Permission issues

3. **Repository State**
   - Workflow may be disabled at repository level
   - Branch protection may be preventing commits

### Secondary Issues

1. **Unused Input Parameter** (Line 10, 135)
   - `force_evaluation` input defined but never used
   - Manual workflow dispatch cannot force refresh
   - Should be wired to `force_refresh` parameter

2. **No Freshness Validation** in Workflow
   - Workflow doesn't check if evaluation already ran recently
   - Description says "Force evaluation even if already run today" but no such check exists

---

## Recommendations

### Immediate Actions

1. **Wire Up `force_evaluation` Input**
   ```yaml
   # In workflow file, line ~132
   force_refresh = "${{ github.event.inputs.force_evaluation }}" == "true"
   metrics_results = collector.evaluate_all_agents(
       since_days=7,
       max_age_hours=12.0,
       force_refresh=force_refresh  # Use input parameter
   )
   ```

2. **Add Workflow Execution Monitoring**
   - Add a step that always posts results even on failure
   - Log workflow execution time to a file for tracking

3. **Investigate Why Schedule Isn't Triggering**
   - Check GitHub Actions logs for this workflow
   - Verify repository activity level
   - Check for any repository-level workflow disablement

### Short-Term Improvements

1. **Add Staleness Warning**
   ```python
   # At start of evaluate step
   if all(not collector.is_metrics_fresh(a['id'], 12.0) for a in active_agents):
       print("⚠️  WARNING: ALL metrics are stale! Evaluation hasn't run recently.")
       print("   This will result in high API usage.")
   ```

2. **Implement Progressive Freshness**
   ```python
   # Try multiple freshness thresholds
   if not collector.is_metrics_fresh(agent_id, 12.0):
       if collector.is_metrics_fresh(agent_id, 24.0):
           print(f"⚠️  Using 24h old metrics for {agent_id} to reduce API calls")
           # Use with caveat
   ```

3. **Add Manual Trigger with Force Option**
   - Document how to manually run workflow
   - Fix force_evaluation to actually work

### Long-Term Enhancements

1. **Implement Evaluation Frequency Check**
   ```python
   # Check metadata for last_evaluation
   metadata = registry.get_metadata()
   last_eval = metadata.get('last_evaluation')
   if last_eval and not force_evaluation:
       last_time = datetime.fromisoformat(last_eval.replace('Z', '+00:00'))
       if (datetime.now(timezone.utc) - last_time).total_seconds() < 3600 * 20:
           print("✅ Evaluation already ran recently, skipping")
           exit(0)
   ```

2. **Add Workflow Health Monitoring**
   - Create a separate workflow that checks if evaluator is running
   - Alert if metrics become too stale (>24h)
   - Track evaluation frequency and API usage

3. **Implement Tiered Cache Strategy**
   - Fresh (<12h): Use cached, high confidence
   - Recent (<24h): Use cached with warning, medium confidence
   - Stale (>24h): Refresh required, low confidence

---

## Test Results Summary

### Cache Lookup Tests ✅

All cache lookup logic tests passed:

1. ✅ Registry Manager initialization
2. ✅ Metrics Collector initialization  
3. ✅ Cache freshness checking (logic correct, data stale)
4. ✅ evaluate_all_agents logic (correct optimization flow)

### System State Tests ⚠️

Current system state reveals issues:

1. ⚠️  All 26 active agents have stale metrics (>12h)
2. ⚠️  Cache hit rate: 0% (should be >80% with daily runs)
3. ⚠️  Last evaluation: ~28 hours ago (should be <24h)
4. ❌ force_evaluation input: Defined but not wired up

---

## Conclusion

The agent evaluator system has well-designed cache lookup logic that is functioning correctly. The issue is not with the cache system itself, but with the workflow execution:

1. **Cache Logic**: ✅ Working as designed
2. **Workflow Scheduling**: ❌ Not executing on schedule
3. **Input Handling**: ❌ `force_evaluation` not wired up
4. **Optimization**: ✅ Good design, but ineffective with stale cache

**Priority**: Investigate why the scheduled workflow isn't running and fix the `force_evaluation` input parameter.

---

## Next Steps

1. **Investigate Workflow Execution**: Check GitHub Actions logs to see why cron isn't triggering
2. **Fix Input Parameter**: Wire up `force_evaluation` to `force_refresh`
3. **Add Monitoring**: Implement staleness alerts and execution tracking
4. **Test Manual Trigger**: Verify workflow can be manually triggered successfully
5. **Document**: Update workflow documentation with troubleshooting steps

---

**Review conducted by**: @support-master  
**Specialization**: Documentation and support  
**Repository**: enufacas/Chained  
**Date**: 2025-11-22
