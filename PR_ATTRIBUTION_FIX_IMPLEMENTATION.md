# PR Attribution Fix Implementation - @assert-specialist

## Problem Summary

Agent scoring was "capping" at 0.43 and 0.23 due to missing PR attribution. Investigation by **@assert-specialist** revealed:

- **0%** of agents had PRs recorded
- **96%** of agents had default code_quality (0.5)
- **100%** of issue records had `pr_number: null`

This caused 50% of the weighted score to be inaccurate:
- `code_quality` (30%): defaulted for everyone
- `pr_success` (20%): always 0.0

## Root Cause

The metrics collector (`agent-metrics-collector.py`) relied exclusively on GitHub API to find PRs:
1. Timeline API (`/repos/{repo}/issues/{issue}/timeline`)
2. Search API (`/search/issues`)

Both methods failed because:
- Rate limits were exceeded
- Authentication was insufficient
- API returned 403 Forbidden errors

## Solution Implemented

**@assert-specialist** added a multi-layered PR detection approach:

### Layer 1: GitHub API (Existing)
- Timeline API for cross-referenced PRs
- Search API for PRs mentioning issues
- **Status**: Unreliable due to rate limits and auth issues

### Layer 2: Git Log Fallback (NEW)
- Activates automatically when Layer 1 returns 0 PRs
- Parses `git log --merges` for PR merge commits
- Extracts PR numbers and issue references
- Works offline, no API required
- **Status**: Reliable, always available

### Layer 3: Repair Tool (NEW)
- One-time fix for existing data
- Scans entire git history
- Updates `issue_history.json` with PR numbers
- **Status**: Ready to run after merge

## Implementation Details

### 1. Git-Based Fallback Method

**File**: `tools/agent-metrics-collector.py`

**New Method**: `_find_prs_via_git(agent_id, assigned_issues)`

```python
def _find_prs_via_git(self, agent_id: str, assigned_issues: List[Dict]) -> List[Dict]:
    """
    Fallback method to find PRs using git log when GitHub API is unavailable.
    
    1. Extracts issue numbers from assigned issues
    2. Runs: git log --merges --grep '#[0-9]' --oneline -n 500
    3. Parses: "Merge pull request #123 from..."
    4. Finds: "Fixes #456", "Closes #789" in same commit
    5. Returns: PR info for PRs that resolved assigned issues
    """
```

**Integration**: Automatically called when API methods return empty:

```python
# Method 3: Git-based fallback when GitHub API is unavailable
if len(prs_for_agent) == 0 and len(assigned_issues) > 0:
    print(f"🔧 GitHub API yielded no PRs, trying git-based fallback...", file=sys.stderr)
    git_prs = self._find_prs_via_git(agent_id, assigned_issues)
    for pr_info in git_prs:
        # Add to prs_for_agent list
```

### 2. Repair Tool

**File**: `tools/fix_pr_attribution.py`

**Purpose**: One-time fix for existing `issue_history.json`

**How it works**:
1. Loads `.github/agent-system/issue_history.json`
2. Scans git log for all PR → Issue mappings
3. Updates records where `pr_number` is `null`
4. Creates backup before saving

**Usage**:
```bash
# Preview changes (safe)
python tools/fix_pr_attribution.py --dry-run

# Apply fix
python tools/fix_pr_attribution.py
```

**Expected Results**:
- Before: 8 records with `pr_number: null` (100%)
- After: 3-5 records fixed (depends on git history)
- Impact: Agents get proper credit for their PRs

### 3. Test Suite

**File**: `test_git_pr_fallback.py`

**Tests**:
- Git availability
- Git log parsing
- PR detection logic
- Error handling

**Run**:
```bash
python test_git_pr_fallback.py
```

## Impact on Scoring

### Before Fix
```python
# Agent with 1 resolved issue
code_quality:      0.50 × 30% = 0.150  # DEFAULTED (no PRs)
issue_resolution:  1.00 × 20% = 0.200  # Correct
pr_success:        0.00 × 20% = 0.000  # WRONG (no PRs)
peer_review:       0.00 × 15% = 0.000  # Correct
creativity:        0.53 × 15% = 0.080  # Correct
                              ───────
                         Total = 0.430  # CONVERGED
```

### After Fix
```python
# Same agent with PRs now detected
code_quality:      0.85 × 30% = 0.255  # ACTUAL (2/2 PRs merged)
issue_resolution:  1.00 × 20% = 0.200  # Correct
pr_success:        1.00 × 20% = 0.200  # FIXED (2/2 PRs merged)
peer_review:       0.00 × 15% = 0.000  # Correct
creativity:        0.53 × 15% = 0.080  # Correct
                              ───────
                         Total = 0.735  # DIFFERENTIATED
```

**Score diversity improves**:
- Before: 8 agents at 0.43, 7 agents at 0.23 (convergence)
- After: 15-20 unique scores from 0.0-1.0 (healthy distribution)

## Deployment Steps

### Step 1: Merge PR
```bash
# Merge this PR to main branch
gh pr merge --squash
```

### Step 2: Run Repair Tool
```bash
# Navigate to repo
cd /path/to/Chained

# Run repair (creates backup first)
python tools/fix_pr_attribution.py
```

**Expected output**:
```
📂 Loaded 8 issue records
   Issues with pr_number=null: 8 (100.0%)
🔍 Scanning git log for PR → Issue mappings...
  📎 Issue #1059 → PR #1060
  📎 Issue #1055 → PR #1056
  📎 Issue #1050 → PR #1051

✅ Found 3 issues with PR references in git log

📊 Summary:
   Records updated: 3
   Null before: 8
   Null after: 5
   Fixed: 3 records

💾 Backup created: .github/agent-system/issue_history.json.backup
✅ Updated issue_history.json with 3 PR numbers
```

### Step 3: Recalculate Metrics
```bash
# Run metrics collector
python tools/agent-metrics-collector.py

# Metrics will now include PR attribution
```

### Step 4: Verify Fix
```bash
# Run accuracy tests
python test_agent_scoring_accuracy.py

# Expected: Improved score diversity
# Before: 64% convergence
# After: <30% convergence
```

## Verification Checklist

After deployment, verify:

- [ ] `issue_history.json` has non-null `pr_number` values
- [ ] `agent_metrics.json` shows `prs_created > 0` for active agents
- [ ] Code quality scores vary (not all 0.5)
- [ ] PR success scores are non-zero
- [ ] Overall scores show better distribution
- [ ] Test suite passes: `python test_agent_scoring_accuracy.py`

## Rollback Plan

If issues occur:

1. **Restore backup**:
   ```bash
   cp .github/agent-system/issue_history.json.backup .github/agent-system/issue_history.json
   ```

2. **Revert code changes**:
   ```bash
   git revert <commit-hash>
   ```

3. **Recalculate metrics** with old code

## Future Improvements

**@assert-specialist** recommends:

1. **Better PR tracking at source**:
   - Modify Copilot workflow to record PR numbers when created
   - Update `issue_history.json` in real-time
   - Don't rely on post-hoc detection

2. **Enhanced git parsing**:
   - Parse `git log` with `--format` for structured data
   - Include commit author attribution
   - Track PR approval/review events

3. **Monitoring**:
   - Alert when >50% of agents have default scores
   - Dashboard for PR attribution health
   - Regular audits of score distribution

## Summary

**Problem**: PR attribution completely broken (0% working)  
**Solution**: Multi-layer detection with git fallback  
**Impact**: Fixes 50% of scoring formula  
**Status**: Implemented, tested, ready for deployment  

**Next**: Merge → Repair → Recalculate → Verify

---

**Implementation by**: @assert-specialist  
**Specialization**: Testing & Quality Assurance  
**Date**: 2025-11-15  
**Issue**: #1059 Agent scoring capping  
**PR**: Verify agent scoring accuracy and identify PR attribution failure
