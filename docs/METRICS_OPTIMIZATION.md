# Agent Metrics Collector Optimization

## Problem

The agent evaluation workflow was making an excessive number of GitHub API calls, causing rate limiting issues during daily evaluations with 51+ active agents.

### Before Optimization

**Complexity**: O(agents × issues × operations)

For each of 51 agents:
- Search ALL agent-work issues (~100+ issues) = 51 searches
- For EACH issue, fetch full details = 51 × 100+ fetches
- For EACH issue, fetch timeline (expensive) = 51 × 100+ timeline calls
- For EACH issue, search for PRs = 51 × 100+ searches
- For EACH PR, fetch comments = additional calls

**Total**: 25,000+ API calls per evaluation
**GitHub Limit**: 5,000 requests/hour for authenticated requests

## Solution

**@engineer-master** implemented a batch optimization strategy:

### Key Optimizations

1. **Batch Fetching**: Pre-fetch ALL agent-work issues once, then distribute to agents
   - Reduces O(n*m) to O(m) for issue fetching
   - Single search query instead of N searches

2. **In-Memory Caching**: Cache issues, PRs, and timeline data
   - `_issue_cache`: Stores fetched issue details
   - `_pr_cache`: Stores fetched PR details  
   - `_timeline_cache`: Stores expensive timeline API results

3. **Smart PR Discovery**: Optimize PR-to-issue linking
   - Check issue body for PR references first (no API call)
   - Use timeline API only as fallback
   - Cache timeline results for reuse

4. **API Call Tracking**: Monitor usage
   - `_api_call_count`: Track total API calls made
   - `get_api_stats()`: Get cache and API usage statistics
   - Rate limit awareness with warnings

### After Optimization

**Complexity**: O(issues + agents)

1. Batch fetch all issues once = 1 search + M fetches
2. Distribute cached issues to agents = 0 API calls
3. Fetch PRs/timelines only when needed, with caching
4. Reuse cached data across agents

**Estimated Total**: ~200-500 API calls per evaluation (95% reduction)

## Usage

### In evaluate_all_agents()

```python
# Automatically uses batch optimization
collector = MetricsCollector()
results = collector.evaluate_all_agents(since_days=7)

# Check API usage
stats = collector.get_api_stats()
print(f"API calls used: {stats['api_calls']}")
```

### In Workflow

The optimization is transparent - no workflow changes needed. The metrics collector automatically:
1. Batch fetches issues on first call to `evaluate_all_agents()`
2. Caches data throughout evaluation
3. Reports API usage in logs

### Monitoring

Check workflow logs for:
```
🚀 Starting batch optimization...
📋 Found 150 total agent-work issues
✅ Distributed issues to 51 agents
📊 API calls so far: 151
```

Compare to rate limit:
```
✅ GitHub API accessible. Rate limit: 4850/5000
```

## Benefits

1. **Avoid Rate Limiting**: Stay well under 5,000/hour limit
2. **Faster Evaluations**: Reduced network round-trips
3. **More Reliable**: Less prone to timeout errors
4. **Scalable**: Can handle 100+ agents efficiently

## Testing

Run the optimization test:
```bash
python3 test_metrics_optimization.py
```

Verifies:
- Batch fetching works correctly
- Caching reduces API calls
- API call counting is accurate
- Cache clearing resets state

## Implementation Details

### MetricsCollector Class Changes

```python
def __init__(self, ...):
    # Add caches
    self._issue_cache: Dict[int, Dict] = {}
    self._pr_cache: Dict[int, Dict] = {}
    self._timeline_cache: Dict[int, List] = {}
    self._api_call_count = 0

def _batch_fetch_all_agent_issues(self, since_days: int) -> Dict[str, List[Dict]]:
    """Pre-fetch ALL issues once and distribute to agents"""
    # Single search + cached issue fetches
    # Returns: {agent_id: [issues]}

def collect_agent_activity(
    self,
    agent_id: str,
    use_batch_cache: bool = False,
    batch_cache: Optional[Dict] = None
):
    """Use batch cache if available"""
    # Check batch cache first
    # Fall back to individual search if needed

def evaluate_all_agents(self, since_days: int):
    """Evaluate all agents with batch optimization"""
    batch_cache = self._batch_fetch_all_agent_issues(since_days)
    for agent in active_agents:
        metrics = self.collect_metrics(
            agent_id,
            use_batch_cache=True,
            batch_cache=batch_cache
        )
```

### Smart PR Discovery

```python
# Method 1: Check issue body for PR refs (fast, no API call)
pr_refs = re.findall(r'#(\d+)', issue_body)

# Method 2: Timeline API only if no PRs found (expensive, cached)
if len(prs_for_agent) == 0:
    timeline = self._timeline_cache.get(issue_number) or self.github.get(...)
    
# Method 3: Search API as fallback
# Method 4: Git log parsing as last resort
```

## Future Enhancements

1. **GraphQL API**: Use GraphQL for more efficient batch queries
2. **Persistent Caching**: Store cache between runs (Redis/file-based)
3. **Incremental Updates**: Only fetch changed issues since last run
4. **Parallel Processing**: Fetch data for multiple agents concurrently

## Related Files

- `tools/agent-metrics-collector.py` - Main implementation
- `.github/workflows/agent-evaluator.yml` - Uses the collector
- `test_metrics_optimization.py` - Test suite

---

*Implemented by **@engineer-master** - Systematic engineering approach to performance optimization*
