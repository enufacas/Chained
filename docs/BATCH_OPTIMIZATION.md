# Agent Metrics Batch Optimization

## Overview

The agent-metrics-collector uses batch optimization to reduce GitHub API calls when evaluating multiple agents. This document explains how it works and common pitfalls.

## The Optimization

### Before Optimization
When evaluating N agents:
- Each agent triggers a search for "agent-work" issues
- API calls = N (one per agent)
- For 38 agents = 38 API calls

### After Optimization
When evaluating N agents:
- One batch search for ALL "agent-work" issues
- Results distributed to agents based on COPILOT_AGENT comment
- API calls = 1 (total)
- For 38 agents = 1 API call (**97% reduction**)

## Implementation

### Workflow Usage (.github/workflows/agent-evaluator.yml)

```python
# Step 1: Batch fetch all issues once
batch_cache = collector._batch_fetch_all_agent_issues(since_days=7)

# Step 2: Evaluate each agent using the cache
for agent in active_agents:
    metrics = collector.collect_metrics(
        agent_id,
        since_days=7,
        use_batch_cache=(batch_cache is not None),  # ✅ CORRECT
        batch_cache=batch_cache
    )
```

### Common Pitfall: Empty Cache Evaluation

❌ **WRONG**:
```python
use_batch_cache=True if batch_cache else False
```

This fails when `batch_cache = {}` (empty dict), because:
- `bool({})` evaluates to `False`
- Causes fallback to individual searches
- Defeats the optimization

✅ **CORRECT**:
```python
use_batch_cache=(batch_cache is not None)
```

This works because:
- `{} is not None` evaluates to `True`
- Uses batch optimization even with 0 issues
- Always avoids redundant API calls

## Logging

The collector logs different messages based on the code path:

### Using Batch Cache (Optimized)
```
✅ Using batch cache for agent-XXX: N issues (0 API calls)
```

### Using Fallback (Individual Search)
```
🔍 [FALLBACK] Looking for issues assigned to agent XXX
📋 Found N total agent-work issues in timeframe
```

If you see repeated "📋 Found" messages, the batch optimization is NOT being used.

## Testing

To verify the optimization is working:

```python
from agent_metrics_collector import MetricsCollector

collector = MetricsCollector()

# Batch fetch
batch_cache = collector._batch_fetch_all_agent_issues(since_days=7)
api_calls_after_batch = collector._api_call_count

# Evaluate agents
for agent_id in agent_ids:
    issues = collector._find_issues_assigned_to_agent(
        agent_id,
        since_days=7,
        use_batch_cache=True,
        batch_cache=batch_cache
    )

api_calls_per_agent = collector._api_call_count - api_calls_after_batch

# Verify
assert api_calls_per_agent == 0, "Batch optimization not working!"
```

## Performance Impact

For a typical agent evaluation with 38 agents:
- **Without optimization**: 39 API calls (1 batch + 38 individual)
- **With optimization**: 1 API call (batch only)
- **Reduction**: 38 fewer calls = **97% improvement**

This is critical for:
- Staying within GitHub API rate limits
- Faster evaluation cycles
- Reduced latency

## Implementation Details

### Batch Fetch (_batch_fetch_all_agent_issues)

1. Single search for all `label:agent-work` issues in timeframe
2. Search includes issue body to avoid individual fetches
3. Parse COPILOT_AGENT comments to distribute issues
4. Return `Dict[agent_id, List[issues]]`

### Agent Lookup (_find_issues_assigned_to_agent)

1. Check if `use_batch_cache and batch_cache is not None`
2. If yes: return `batch_cache.get(agent_id, [])`
3. If no: fallback to individual search (for single-agent queries)

## Troubleshooting

### "Still seeing repeated API calls"

Check the logic for setting `use_batch_cache`:
```python
# ✅ Correct
use_batch_cache=(batch_cache is not None)

# ❌ Wrong
use_batch_cache=True if batch_cache else False
use_batch_cache=bool(batch_cache)
```

### "Empty batch cache"

This is NORMAL when:
- No agent-work issues exist in the timeframe
- All issues are older than the cutoff
- No issues have COPILOT_AGENT comments

The optimization still works with an empty cache!

### "Fallback messages appearing"

If you see `[FALLBACK]` in logs, check:
1. Is `use_batch_cache=True` being passed?
2. Is `batch_cache` not `None`?
3. Is the batch cache being passed to collect_metrics?

## References

- Issue: #XXX - Rate limit and approach
- Fix: Changed `True if batch_cache else False` to `(batch_cache is not None)`
- File: `.github/workflows/agent-evaluator.yml` line 169
- File: `tools/agent-metrics-collector.py` lines 446-471
