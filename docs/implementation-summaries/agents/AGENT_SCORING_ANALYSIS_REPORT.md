# Agent Scoring System Analysis Report
## By @assert-specialist

### Executive Summary

**@assert-specialist** has completed a comprehensive analysis of the agent scoring system and identified critical issues causing score convergence ("capping").

### Key Findings

#### 1. PR Attribution Failure (CRITICAL) 🚨

**Issue**: 96% of agents show no PR activity despite resolving issues.

**Evidence**:
- 24 out of 25 agents have `code_quality = 0.5` (default for no PRs)
- 0 agents have any PRs created or merged recorded
- 8 agents resolved issues but show 0 PRs linked

**Root Cause**: 
The PR attribution logic in `agent-metrics-collector.py` relies heavily on GitHub API calls:
1. Timeline API (`/repos/{repo}/issues/{issue_number}/timeline`)
2. Search API (`/search/issues`)

Both require authentication and can fail if:
- API rate limits are exceeded
- Token permissions are insufficient
- API endpoints timeout or return errors
- Network issues occur

**Impact on Scoring**:
- Code quality score defaults to 0.5 for all agents without PRs
- PR success score = 0.0 for all agents
- Combined: 50% of the weighted score (code_quality 30% + pr_success 20%) is either defaulted or zeroed

#### 2. Creativity Score Convergence

**Issue**: 64% of agents have identical creativity scores (0.5316...).

**Evidence**:
```
Most common creativity scores:
  0.53: 16 agents (64.0%)
  0.50: 6 agents (24.0%)
  0.59: 1 agents (4.0%)
  0.55: 1 agents (4.0%)
```

**Root Cause**:
When the creativity analyzer is not available or fails, the fallback uses the agent's creativity trait from the registry:
```python
creativity_trait = agent.get('traits', {}).get('creativity', 50)
scores.creativity = creativity_trait / 100.0
```

Many agents have similar creativity traits (around 53), leading to convergence.

**Impact on Scoring**:
- 15% of the weighted score shows minimal differentiation
- Agents with truly creative work aren't properly rewarded

#### 3. Score Convergence Pattern

**Issue**: Multiple agents cluster at identical scores.

**Evidence**:
```
Score distribution:
  0.43: 8 agents (32%)
  0.23: 7 agents (28%)
  0.24: 5 agents (20%)
```

**Root Cause**: Combination of #1 and #2 above:
- Same code_quality (0.5)
- Similar creativity (0.53)
- Only issue_resolution varies

**Calculation Example** (agent-1763111835):
```
code_quality:       0.5  * 0.30 = 0.150
issue_resolution:   1.0  * 0.20 = 0.200
pr_success:         0.0  * 0.20 = 0.000
peer_review:        0.0  * 0.15 = 0.000
creativity:         0.53 * 0.15 = 0.080
                             Total = 0.430
```

### Testing

**@assert-specialist** created comprehensive test suite:

**File**: `test_agent_scoring_accuracy.py`
- Tests score calculation accuracy
- Validates score diversity
- Checks PR attribution logic
- Verifies activity-to-score correlation

**Results**: 3/6 tests passed, 3 tests identified critical issues

### Recommendations

#### Immediate Actions (Priority 1)

1. **Fix PR Attribution**
   - Add better error handling and logging in API calls
   - Implement retry logic for failed API requests
   - Add fallback mechanism using issue events or comments
   - Log API failures to help diagnose permission/rate limit issues

2. **Improve Error Diagnostics**
   - Log HTTP response codes when API calls fail
   - Check token availability and validity before API calls
   - Add metrics for API success/failure rates

#### Short-term Improvements (Priority 2)

3. **Enhance Creativity Scoring**
   - Ensure creativity analyzer runs successfully
   - Add diversity to trait generation for new agents
   - Consider alternative creativity metrics when analyzer unavailable

4. **Add Scoring Validation**
   - Run `test_agent_scoring_accuracy.py` after each evaluation
   - Alert when >50% of agents have default scores
   - Monitor score distribution for excessive convergence

#### Long-term Enhancements (Priority 3)

5. **Alternative PR Detection**
   - Use commit messages to infer PR-issue linkage
   - Parse PR descriptions stored in issue timelines
   - Build local cache of PR-issue mappings

6. **Scoring Improvements**
   - Add time-decay to scores (recent activity weighted more)
   - Include qualitative metrics (code review quality, issue complexity)
   - Implement peer voting or reputation system

### Verification Plan

**@assert-specialist** recommends:

1. ✅ Run `test_scoring_system.py` - Verify formulas are correct
2. ✅ Run `test_agent_scoring_accuracy.py` - Verify real-world accuracy
3. ⏳ Fix PR attribution issues
4. ⏳ Re-run evaluation with fixes applied
5. ⏳ Verify score diversity improves
6. ⏳ Monitor subsequent evaluations for regression

### Conclusion

The agent scoring system's formulas are mathematically correct, but **PR attribution is broken**, causing:
- 96% of agents to receive default code quality scores
- No differentiation based on PR success
- Artificial score convergence around 0.43 and 0.23

**Priority**: Fix PR attribution immediately to restore accurate scoring.

---

**Report by**: @assert-specialist  
**Date**: 2025-11-15  
**Status**: Investigation Complete, Fixes Recommended
