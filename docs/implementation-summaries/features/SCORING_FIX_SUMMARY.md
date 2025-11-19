# Scoring System Fix - @investigate-champion

## Issue
PR #1060 attempted to fix the scoring system but did not address the root cause. The scoring system was showing score convergence with 96% of agents having identical default scores.

## Root Cause Analysis

**@investigate-champion** identified the bug in `tools/agent-metrics-collector.py` at line 607:

### The Bug
```python
# BEFORE (BROKEN):
prs_merged = [pr for pr in prs_for_agent if pr.get('pull_request', {}).get('merged_at')]
```

**Problem**: This code assumes PRs have a nested `pull_request` object with a `merged_at` field. However, PRs from different GitHub API endpoints have different structures:

1. **Timeline API**: Returns PR data as a nested object in `source.issue` with `pull_request` metadata
2. **Search API**: Returns PR data directly with `merged_at` field at the top level
3. **Git fallback**: Returns PR data with `source: 'git_log'` and assumes merged

The original code only checked for the nested structure, which meant:
- PRs from search API were never counted as merged
- PRs from git fallback were never counted as merged
- Only PRs with the exact nested structure (rare) were detected

This caused:
- `prs_merged` always = 0
- `code_quality` score = 0.5 (default for no PRs)
- `pr_success` score = 0.0 (0 merged / 0 created)
- Overall scores converged around 0.43-0.23 regardless of actual work

## The Fix

**@investigate-champion** implemented two fixes:

### Fix 1: Enhanced PR Merge Detection
```python
# AFTER (FIXED):
prs_merged = []
for pr in prs_for_agent:
    # Check multiple possible structures for merge status
    if pr.get('source') == 'git_log':
        # Git fallback PRs are assumed merged
        prs_merged.append(pr)
    elif pr.get('merged_at'):
        # Direct merged_at field (from search API or fetched PR details)
        prs_merged.append(pr)
    elif pr.get('pull_request', {}).get('merged_at'):
        # Nested pull_request object (from timeline cross-reference)
        prs_merged.append(pr)
    elif pr.get('state') == 'closed' and pr.get('merged', False):
        # Alternative: closed + merged flag
        prs_merged.append(pr)

activity.prs_merged = len(prs_merged)
```

This fix handles all four possible PR data structures from different API sources.

### Fix 2: Fetch Full PR Details from Timeline API
```python
# When finding PRs via timeline API, now fetch full details:
full_pr = self.github.get(f'/repos/{self.repo}/pulls/{pr_number}')
if full_pr:
    prs_for_agent.append(full_pr)  # Full PR object with accurate merge status
    merge_status = "merged" if full_pr.get('merged_at') else "open/closed"
    print(f"  ✅ Found PR #{pr_number} ({merge_status}) via timeline for issue #{issue_number}")
```

This ensures we always have complete PR data including accurate merge status.

## Testing

### Unit Test
Created test to verify merge detection logic handles all formats:
```python
test_prs = [
    {'number': 1, 'merged_at': '2025-11-15T00:00:00Z'},  # Search API format
    {'number': 2, 'state': 'closed', 'merged': True},    # Alternative format
    {'number': 3, 'pull_request': {'merged_at': '2025-11-15T00:00:00Z'}},  # Timeline format
    {'number': 4, 'source': 'git_log'},  # Git fallback format
    {'number': 5, 'state': 'open'},  # Not merged
]
```

**Result**: ✅ PASS - Correctly identifies 4 merged PRs out of 5 total

## Data Recalculation Script

**@investigate-champion** created `recalculate_all_metrics.py` to update historical data:

```bash
# Recalculate metrics for all agents with the fixed logic
python3 recalculate_all_metrics.py
```

This script:
1. Loads all agents from registry
2. Recalculates metrics using the fixed scoring logic
3. Updates `.github/agent-system/metrics/*/latest.json`
4. Reports summary of changes

**Note**: Requires `GITHUB_TOKEN` environment variable for API access.

## Expected Impact

After applying this fix and recalculating metrics:

### Before (Broken)
- ✗ 96% of agents have `prs_created = 0`
- ✗ 100% of agents have `prs_merged = 0`
- ✗ 96% have `code_quality = 0.5` (default)
- ✗ 100% have `pr_success = 0.0`
- ✗ Scores converge at 0.43, 0.23, 0.24 (32%, 28%, 20% of agents)

### After (Fixed)
- ✓ Agents with resolved issues will have `prs_created > 0`
- ✓ Merged PRs will be correctly counted
- ✓ `code_quality` scores will reflect actual merge rates
- ✓ `pr_success` scores will reflect actual PR success rates
- ✓ Overall scores will show proper diversity based on actual work

## Verification Steps

After running the data recalculation:

1. Check agent metrics:
```bash
# Verify PRs are now detected for agents with resolved issues
cat .github/agent-system/metrics/agent-1762960673/latest.json | jq '.activity'
```

2. Run scoring accuracy tests:
```bash
python3 test_agent_scoring_accuracy.py
```

Expected results:
- ✓ Score calculation accuracy: PASS
- ✓ Score diversity: PASS (improved from FAIL)
- ✓ PR attribution: PASS (improved from FAIL)

3. Check score distribution:
```bash
# Should show better diversity, fewer agents at identical scores
for f in .github/agent-system/metrics/*/latest.json; do
  jq -r '.scores.overall' "$f"
done | sort | uniq -c
```

## Files Changed

1. **tools/agent-metrics-collector.py**
   - Fixed PR merge detection logic (line 607)
   - Enhanced timeline API to fetch full PR details (line 556)

2. **recalculate_all_metrics.py** (new)
   - Script to recalculate all historical metrics with fixed logic

## Security Considerations

- ✅ No security vulnerabilities introduced
- ✅ API calls use existing authentication mechanisms
- ✅ Error handling preserves functionality even when APIs fail
- ✅ Fallback mechanisms ensure robustness

## Conclusion

The scoring system bug has been identified and fixed by **@investigate-champion**. The root cause was incorrect PR merge status detection that only worked for one specific data structure. The fix now handles all PR data formats from different GitHub API endpoints.

To complete the fix:
1. ✅ Code fix applied to `tools/agent-metrics-collector.py`
2. ⏳ Run `recalculate_all_metrics.py` to update historical data (requires `GITHUB_TOKEN`)
3. ⏳ Verify scores now show proper diversity
4. ⏳ Merge PR with both code fix and updated historical data

---

**Fixed by**: @investigate-champion  
**Date**: 2025-11-15  
**Status**: Code Fix Complete, Data Recalculation Pending GitHub Token
