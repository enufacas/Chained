# Agent Evaluator Performance Improvements

**@meta-coordinator** has implemented changes to address issue with missing performance optimization evidence in workflow logs.

## Problem Statement

PR #1343 introduced performance optimizations to the agent evaluator, including:
- Batch fetching of all agent-work issues
- Short-circuit optimizations to skip expensive API calls
- Smart caching to avoid redundant GitHub API requests

However, these optimizations were not visible in the workflow logs at https://github.com/enufacas/Chained/actions/runs/19414806429

## Root Causes Identified

1. **Log Visibility Issue**: Optimization messages were printed to `sys.stderr`, which is not captured when the MetricsCollector is imported and called programmatically in the GitHub Actions workflow.

2. **Batch Optimization Not Being Used**: The workflow was calling `collector.collect_metrics()` individually for each agent instead of using the batch fetch mechanism, so the batch optimization wasn't actually being triggered.

## Changes Implemented

### 1. Log Visibility Fix (`tools/agent-metrics-collector.py`)

Changed key performance messages from `sys.stderr` to stdout (default):

**Optimization Messages:**
- `⚡ Short-circuit: {agent_id} has no assigned issues, skipping PR/review lookups`
- `⚡ Short-circuit: Skipping review lookup (no significant PR activity)`
- `⚡ Short-circuit: Skipping comment lookup (no assigned issues)`

**Progress Messages:**
- `🚀 Starting batch optimization...`
- `🔄 Batch fetching all agent-work issues (last X days)...`
- `📋 Found X total agent-work issues`
- `✅ Distributed issues to X agents`
- `📊 API calls so far: X`
- `✅ Batch fetch complete. Starting agent evaluation...`
- `📊 Collecting metrics for {agent_id}...`
- `📊 Activity summary for {agent_id}:`
- `✅ Evaluation complete! Collected metrics for X agents.`
- `📊 Total API calls used: X`

### 2. Workflow Batch Optimization (`.github/workflows/agent-evaluator.yml`)

Added batch fetch call before the agent evaluation loop:

```python
# OPTIMIZATION: Batch fetch all issues once before evaluating agents
batch_cache = None
if use_real_metrics:
    try:
        print("🚀 Starting batch optimization...")
        batch_cache = collector._batch_fetch_all_agent_issues(since_days=7)
        print("✅ Batch fetch complete. Starting agent evaluation...")
    except Exception as e:
        print(f"⚠️  Batch fetch failed, proceeding without cache: {e}")
```

Updated the `collect_metrics()` call to use the batch cache:

```python
metrics = collector.collect_metrics(
    agent_id, 
    since_days=7,
    use_batch_cache=True if batch_cache else False,
    batch_cache=batch_cache
)
```

## Expected Results in Next Run

When the agent evaluator workflow runs next, you should see these log messages in order:

1. **Initialization:**
   ```
   📊 Evaluating X active agents...
   ✅ Using real GitHub metrics collector
   ```

2. **Batch Optimization Start:**
   ```
   🚀 Starting batch optimization...
   🔄 Batch fetching all agent-work issues (last 7 days)...
   ```

3. **Batch Fetch Results:**
   ```
   📋 Found X total agent-work issues
   ✅ Distributed issues to X agents
   📊 API calls so far: X
   ✅ Batch fetch complete. Starting agent evaluation...
   ```

4. **Per-Agent Evaluation:**
   ```
   📊 Evaluating agent 1/X
   📊 Collecting metrics for agent-name...
   ```

5. **Short-Circuit Optimizations** (when applicable):
   ```
   ⚡ Short-circuit: agent-name has no assigned issues, skipping PR/review lookups
   ```
   OR
   ```
   ⚡ Short-circuit: Skipping review lookup (no significant PR activity)
   ⚡ Short-circuit: Skipping comment lookup (no assigned issues)
   ```

6. **Activity Summary per Agent:**
   ```
   📊 Activity summary for agent-name:
     - Issues assigned: X
     - Issues resolved: X
     - PRs created: X
     - PRs merged: X
     - Reviews given: X
     - Comments made: X
     - API calls used: X
   ```

7. **Completion:**
   ```
   ✅ Evaluation complete! Collected metrics for X agents.
   📊 Total API calls used: X
   ```

## Performance Impact

The optimizations should significantly reduce:
- **API calls**: From ~20-30 per agent to ~5-10 per agent
- **Execution time**: From ~5-10 minutes to ~2-4 minutes
- **Rate limit pressure**: Fewer API calls mean more headroom

## Verification Steps

To verify the improvements are working in a workflow run:

1. Navigate to the workflow run logs
2. Look for the "Evaluate all agents" step
3. Verify you see the batch optimization messages:
   - `🚀 Starting batch optimization...`
   - `✅ Batch fetch complete...`
4. Check for short-circuit messages (should see several for agents with no activity)
5. Look at the final API call count - should be significantly lower than before

## Technical Details

### Batch Fetch Mechanism

The `_batch_fetch_all_agent_issues()` method:
1. Fetches ALL agent-work issues in a single search query
2. Parses each issue to determine which agent it's assigned to
3. Distributes issues to agent-specific buckets
4. Returns a cache that's passed to each agent's evaluation

### Short-Circuit Optimizations

Three short-circuit checks avoid expensive API calls:
1. If an agent has 0 assigned issues → skip all PR/review lookups
2. If an agent has no merged PRs → skip review lookups  
3. If an agent has no assigned issues → skip comment lookups

### Cache Usage

The batch cache is used in `collect_agent_activity()`:
- When `use_batch_cache=True`, it uses pre-fetched issues from cache
- Falls back to individual fetch if cache is unavailable
- Maintains backward compatibility with non-cached calls

## References

- Original PR: #1343
- Issue: Agent evaluator improvements
- Previous workflow run: https://github.com/enufacas/Chained/actions/runs/19414806429

## Author

**@meta-coordinator** - Specialized in multi-agent coordination and system-wide optimizations
