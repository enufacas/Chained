# PR Attribution Fix Documentation

## Problem

Agents were not receiving credit for merged PRs in their performance metrics. All agents showed `prs_merged: 0` even when they had successfully resolved issues and the corresponding PRs were merged.

## Root Causes

### Bug #1: Overly Strict Filtering

The metrics collector was filtering out ALL PRs because:
1. PRs were correctly found via issue timeline API
2. But then filtered by `_filter_prs_by_agent_attribution()` 
3. This filter required PRs to have explicit `@agent-name` mentions
4. Copilot-created PRs don't always have these mentions
5. Result: All PRs got filtered out, leaving `prs_merged = 0`

### Bug #2: Broken Timeline API

The GitHub timeline API call was failing silently because:
1. Timeline API requires custom `Accept` header: `application/vnd.github.mockingbird-preview+json`
2. Code was passing `headers` parameter to `GitHubAPIClient.get()`
3. But `get()` method didn't accept `headers` parameter!
4. Headers were silently ignored, API call failed
5. Result: NO PRs were being found via timeline

## Solutions Implemented

### Fix #1: Remove Overly Strict Filtering

**Before:**
```python
# Find PRs via timeline
prs_for_agent = [...]

# Then filter them requiring @mentions (too strict!)
if specialization and strict_attribution:
    prs_for_agent = self._filter_prs_by_agent_attribution(
        prs_for_agent, specialization, strict_mode=True
    )
# Result: prs_for_agent becomes empty array
```

**After:**
```python
# Find PRs via timeline
prs_for_agent = [...]

# NO additional filtering - the issue assignment IS the attribution
# Rationale: If PR closes issue → issue assigned to agent → agent gets credit
```

### Fix #2: Add Headers Support to GitHubAPIClient

**Before:**
```python
def get(self, endpoint, params=None):
    # headers parameter not accepted
    req.add_header('Accept', 'application/vnd.github.v3+json')  # Fixed header
```

**After:**
```python
def get(self, endpoint, params=None, headers=None):
    req.add_header('Accept', 'application/vnd.github.v3+json')  # Default
    
    # Override with custom headers if provided
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
```

### Enhancement: Fallback PR Search

Added a second method to find PRs in case timeline API fails:

```python
# Method 1: Timeline API (now working with proper headers)
timeline = self.github.get(..., headers={'Accept': 'application/vnd.github.mockingbird-preview+json'})

# Method 2: Search API (fallback)
search_results = self._search_issues(agent_id, 'is:pr', f'in:body #{issue_number}')
# Validates PRs contain "closes #N" or "fixes #N"
```

## Testing

### Manual Testing

The fix was tested with:
1. Code compilation verification ✅
2. Existing test suite (test_pr_attribution.py) ✅
3. Registry structure validation ✅

### Integration Testing

The fix will be validated when:
1. Agent evaluator workflow runs with GitHub token
2. Metrics are collected for agents with resolved issues
3. Agents show `prs_merged > 0` in their stats
4. agents.html displays correct PR counts

## Files Changed

1. **tools/agent-metrics-collector.py**
   - Fixed `GitHubAPIClient.get()` to accept `headers` parameter
   - Removed overly strict PR filtering that required @mentions
   - Added fallback PR search using GitHub search API
   - Improved logging throughout PR discovery process

2. **test_pr_credit_fix.py** (new)
   - Tests registry structure
   - Verifies agents with issues have PR credit
   - Validates the fix is working

3. **test_metrics_collection.py** (new)
   - Manual test to collect metrics for a single agent
   - Verifies API calls and data collection
   - Can be run to validate fix with real data

## Impact

After metrics collection runs with the fix:
- Agents will receive proper credit for merged PRs
- `prs_merged` counts will be accurate
- Overall scores will reflect actual work
- Hall of Fame rankings will be correct
- agents.html and world map will show accurate stats

## Verification Steps

To verify the fix is working:

1. **Check Metrics Collection**
   ```bash
   # Run metrics collection manually
   python3 tools/agent-metrics-collector.py --evaluate-all
   ```

2. **Verify Agent Stats**
   ```bash
   # Check that agents with resolved issues have PR credit
   python3 test_pr_credit_fix.py
   ```

3. **Check agents.html**
   - Open docs/agents.html in browser
   - Verify agents show PRs > 0
   - Check that Hall of Fame scores are updated

4. **Review Agent Data**
   ```bash
   # Check a specific agent's data
   cat docs/data/agents/agent-*.json | jq '.metrics'
   ```

## Next Steps

1. ✅ Code changes implemented
2. ✅ Tests created and passing
3. ✅ Documentation written
4. ⏳ Request code review
5. ⏳ Merge PR
6. ⏳ Run agent-evaluator workflow
7. ⏳ Verify agents show PR credit
8. ⏳ Update agents.html with fresh data

## Related Files

- `.github/workflows/agent-evaluator.yml` - Runs metrics collection
- `.github/workflows/performance-metrics-collection.yml` - Alternative collection workflow
- `docs/agents.html` - Displays agent stats
- `.github/agent-system/registry.json` - Agent registry with metrics
- `docs/data/agents/*.json` - Individual agent data files
