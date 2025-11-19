# Agent Metrics Storage-First Optimization

## Overview

The agent evaluation system has been optimized to significantly reduce GitHub API calls by using already-stored metrics data instead of re-fetching from the API on every evaluation.

**Impact**: ~2,000+ API calls saved per daily evaluation cycle

## Problem Statement

Previously, the agent evaluator workflow would:
1. Load the agent registry (in-memory)
2. Make 50+ GitHub API calls per agent to collect metrics
3. Evaluate agents based on collected data
4. Store metrics to disk for historical tracking

**Issue**: Metrics were stored but never reused, resulting in redundant API calls during frequent evaluations.

## Solution

Implemented a **storage-first approach** that:
1. Checks if stored metrics exist and are fresh (< 12 hours old)
2. Uses stored metrics when available (0 API calls)
3. Only collects fresh metrics when needed (stale or missing)
4. Falls back to API collection with batch optimization

## Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ Agent Evaluator Workflow                                │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ evaluate_all_agents()                                   │
│  - Load agent registry                                  │
│  - Check each agent's stored metrics                    │
└─────────────────────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
┌──────────────────┐         ┌──────────────────┐
│ Metrics Fresh?   │         │ Metrics Stale?   │
│  (< 12 hours)    │         │  (> 12 hours)    │
└──────────────────┘         └──────────────────┘
        │                             │
        ▼                             ▼
┌──────────────────┐         ┌──────────────────┐
│ Load from        │         │ Collect fresh    │
│ Storage          │         │ from API         │
│ (0 API calls)    │         │ (~50 API calls)  │
└──────────────────┘         └──────────────────┘
        │                             │
        └──────────────┬──────────────┘
                       ▼
              ┌─────────────────┐
              │ Evaluate Agent  │
              │ Performance     │
              └─────────────────┘
```

### Storage Structure

Metrics are stored in:
```
.github/agent-system/metrics/{agent-id}/
  ├── latest.json              # Symlink to most recent metrics
  └── YYYY-MM-DD_HH-MM-SS.json # Timestamped snapshots
```

Each metrics file contains:
```json
{
  "agent_id": "agent-123456789",
  "timestamp": "2025-11-19T01:00:00+00:00",
  "activity": {
    "issues_resolved": 5,
    "issues_created": 2,
    "prs_created": 4,
    "prs_merged": 3,
    "reviews_given": 7,
    "comments_made": 15
  },
  "scores": {
    "code_quality": 0.85,
    "issue_resolution": 0.75,
    "pr_success": 0.80,
    "peer_review": 0.90,
    "creativity": 0.70,
    "overall": 0.80
  },
  "metadata": {
    "lookback_days": 7,
    "api_calls_made": 52
  }
}
```

## Implementation Details

### Key Methods

#### `is_metrics_fresh(agent_id, max_age_hours=12.0)`
Checks if stored metrics are recent enough to use.

**Returns**: `True` if metrics exist and are < 12 hours old, `False` otherwise

```python
metrics = collector.load_latest_metrics(agent_id)
age = datetime.now(timezone.utc) - timestamp
return age_hours < max_age_hours
```

#### `get_or_collect_metrics(agent_id, max_age_hours=12.0, force_refresh=False)`
Retrieves metrics, preferring storage over API.

**Strategy**:
1. If `force_refresh=True`: Skip storage, always use API
2. If stored metrics are fresh: Use storage (0 API calls)
3. Otherwise: Collect fresh from API (~50 API calls)

```python
if not force_refresh and is_metrics_fresh(agent_id, max_age_hours):
    return load_latest_metrics(agent_id)  # Storage
else:
    return collect_metrics(agent_id)  # API
```

#### `evaluate_all_agents(max_age_hours=12.0, force_refresh=False)`
Evaluates all agents using storage-first approach.

**Optimization**:
1. Load all agents from registry
2. Check each for fresh stored metrics
3. Load from storage when possible
4. Batch collect for remaining agents
5. Report API savings

**Output**:
```
✅ Evaluation complete! Metrics for 47 agents:
   📂 From storage: 42 agents (0 API calls)
   🔄 Fresh collection: 5 agents (250 API calls)
   💰 Estimated API calls saved: ~2100
```

### CLI Interface

The `agent-metrics-collector.py` script now supports:

```bash
# Use storage when fresh (default)
python3 tools/agent-metrics-collector.py agent-123456789

# Force fresh collection from API
python3 tools/agent-metrics-collector.py agent-123456789 --force-refresh

# Adjust freshness threshold
python3 tools/agent-metrics-collector.py agent-123456789 --max-age-hours 24

# Evaluate all agents (storage-first)
python3 tools/agent-metrics-collector.py --evaluate-all
```

### Workflow Integration

The `.github/workflows/agent-evaluator.yml` workflow now:

```yaml
- name: Evaluate all agents
  run: |
    # Uses evaluate_all_agents() with storage-first approach
    metrics_results = collector.evaluate_all_agents(
        since_days=7,
        max_age_hours=12.0,  # Use metrics stored within last 12 hours
        force_refresh=False  # Prefer stored data when available
    )
```

## Performance Metrics

### Before Optimization

**Per agent evaluation**:
- API calls: ~50 (search, issues, PRs, reviews)
- Time: ~5-10 seconds (API latency)
- Rate limit cost: 50 requests

**Daily evaluation (47 agents)**:
- Total API calls: ~2,350
- Total time: ~5 minutes
- Rate limit impact: High

### After Optimization

**Per agent evaluation (fresh storage)**:
- API calls: 0
- Time: < 1 second (disk read)
- Rate limit cost: 0

**Per agent evaluation (stale/missing storage)**:
- API calls: ~50 (same as before)
- Time: ~5-10 seconds
- Rate limit cost: 50 requests

**Daily evaluation (47 agents with 90% storage hit rate)**:
- API calls from storage: 42 agents × 0 = 0
- API calls from fresh: 5 agents × 50 = 250
- **Total API calls: ~250** (89% reduction!)
- Total time: ~1 minute
- Rate limit impact: Low

### Expected Savings

Assuming:
- Daily evaluations (1x per day)
- Metrics collector runs (hourly for active agents)
- 90% storage hit rate

**Monthly savings**:
- API calls saved: ~60,000+
- Evaluation time saved: ~2 hours
- Rate limit headroom gained: Significant

## Configuration

### Freshness Threshold

The default threshold is **12 hours**, which balances:
- **Freshness**: Metrics are recent enough for accurate evaluation
- **Efficiency**: Most evaluations use storage (daily cycle is 24h)
- **Accuracy**: Real-time changes reflected within reasonable time

Adjust via:
```python
collector.evaluate_all_agents(max_age_hours=6.0)  # More frequent refresh
collector.evaluate_all_agents(max_age_hours=24.0)  # Less frequent refresh
```

### Force Refresh

Use when:
- Testing new metrics logic
- Debugging discrepancies
- Forcing re-collection after registry changes

```python
collector.evaluate_all_agents(force_refresh=True)
```

## Fallback Behavior

The system gracefully handles:

1. **Missing storage**: Falls back to API collection
2. **Corrupted files**: Skips bad data, collects fresh
3. **Stale metrics**: Re-collects when beyond threshold
4. **API failures**: Uses last known good metrics if available

## Monitoring

### Success Indicators

Watch for these in workflow logs:

```
✅ Evaluation complete! Metrics for 47 agents:
   📂 From storage: 42 agents (0 API calls)
   🔄 Fresh collection: 5 agents (250 API calls)
   💰 Estimated API calls saved: ~2100
```

**Good**: High "from storage" count
**Needs attention**: High "fresh collection" count

### Debugging

If storage isn't being used:

1. Check metric file timestamps:
   ```bash
   find .github/agent-system/metrics -name "latest.json" -exec stat -f "%Sm %N" {} \;
   ```

2. Verify freshness calculation:
   ```python
   python3 tools/agent-metrics-collector.py agent-ID --verbose
   ```

3. Check for corrupted files:
   ```bash
   find .github/agent-system/metrics -name "*.json" -exec python3 -m json.tool {} \; > /dev/null
   ```

## Best Practices

### For Workflows

1. **Use storage-first by default**: Let the system decide when to refresh
2. **Set appropriate thresholds**: 12h for daily evaluations, 1h for hourly
3. **Don't force-refresh unnecessarily**: Wastes API quota
4. **Monitor API usage**: Track the "saved" vs "made" metrics

### For Development

1. **Preserve timestamps**: Don't modify `latest.json` timestamps manually
2. **Test with storage**: Verify logic works with cached data
3. **Handle staleness**: Always have API fallback path
4. **Document changes**: Update this file when modifying metrics

### For Operations

1. **Keep metrics directory**: Don't delete stored metrics unnecessarily
2. **Monitor disk usage**: Old metrics can accumulate (consider cleanup)
3. **Backup strategy**: Metrics can be regenerated, but historical data is useful
4. **Rate limit awareness**: Watch for API quota exhaustion

## Future Improvements

### Potential Enhancements

1. **Adaptive thresholds**: Adjust freshness based on agent activity level
2. **Parallel collection**: Speed up fresh collection with async requests
3. **Compressed storage**: Reduce disk usage for historical metrics
4. **Incremental updates**: Only update changed data, not full re-collection
5. **Metric versioning**: Handle schema changes gracefully

### Monitoring Additions

1. **API savings dashboard**: Visualize storage effectiveness
2. **Staleness alerts**: Notify when too many metrics are stale
3. **Storage health**: Monitor file integrity and disk usage
4. **Performance tracking**: Graph evaluation time over time

## Conclusion

The storage-first optimization represents a **significant improvement** in:
- **Efficiency**: 89% reduction in API calls
- **Speed**: 80% faster evaluation time
- **Sustainability**: Better rate limit management
- **Reliability**: Graceful degradation with fallbacks

**Impact**: This change enables more frequent evaluations without hitting API limits, making the agent system more responsive and sustainable.

---

**Implementation**: @APIs-architect  
**Date**: 2025-11-19  
**Status**: ✅ Production Ready
