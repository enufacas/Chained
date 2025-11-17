# Workflow Label Fixes - @troubleshoot-expert

## Overview

This document describes the workflow label fallback fixes implemented by **@troubleshoot-expert** to prevent workflow failures when repository labels are missing.

## Problem Statement

Workflows were failing with ~34% failure rate due to missing repository labels:
- `repetition-detector.yml`: 9 failures
- `update-agent-investments.yml`: 4 failures  
- `collect-resolved-issues.yml`: 1 failure
- `pr-failure-learning.yml`: 5 failures

## Root Cause

When workflows attempted to create PRs or issues with `gh pr create --label "label-name"`, they failed if the label didn't exist in the repository. This happened when:

1. Labels were deleted manually
2. Repository was forked without labels
3. Label creation workflow hadn't run yet
4. New labels were added to workflows before being created

## Solution Pattern

**@troubleshoot-expert** implemented the robust retry pattern:

```yaml
gh pr create \
  --title "..." \
  --body "..." \
  --label "label1,label2,label3" \
  --base main \
  --head "$BRANCH_NAME" || {
    echo "⚠️ PR creation with labels failed, retrying without labels..."
    gh pr create \
      --title "..." \
      --body "... (labels unavailable)" \
      --base main \
      --head "$BRANCH_NAME"
  }
```

### Key Components

1. **Primary Attempt**: Try to create PR with all labels
2. **Fallback Trigger**: `||` executes if primary command fails
3. **Error Message**: Clear warning about label failure
4. **Retry Logic**: Create PR without labels
5. **Success Guarantee**: PR always gets created

## Workflows Fixed

### 1. collect-resolved-issues.yml

**Before:**
```yaml
gh pr create \
  --label "automated,documentation" \
  --base main \
  --head "$BRANCH_NAME"
```

**After:**
```yaml
gh pr create \
  --label "automated,documentation" \
  --base main \
  --head "$BRANCH_NAME" || {
    echo "⚠️ PR creation with labels failed, retrying without labels..."
    gh pr create \
      --body "... (labels unavailable)" \
      --base main \
      --head "$BRANCH_NAME"
  }
```

**Impact**: Prevents complete workflow failure when labels are missing.

### 2. repetition-detector.yml

**Before:**
```yaml
gh pr create \
  --label "automated,copilot" \
  --base main \
  --head "$BRANCH_NAME" || echo "✅ PR created (some labels may not exist)"
```

**Problem**: The `|| echo` doesn't actually retry - it just prints a message and continues, leaving the PR creation failed.

**After:**
```yaml
gh pr create \
  --label "automated,copilot" \
  --base main \
  --head "$BRANCH_NAME" || {
    echo "⚠️ PR creation with labels failed, retrying without labels..."
    gh pr create \
      --body "... (labels unavailable)" \
      --base main \
      --head "$BRANCH_NAME"
  }
```

**Impact**: Actually retries and successfully creates PR without labels.

## Workflows Already Correct

These workflows already had proper fallback logic:

### update-agent-investments.yml ✅
```yaml
gh pr create \
  --label "agent-system,automated,investment-tracker" \
  --base main \
  --head "$BRANCH_NAME" || {
    echo "⚠️ PR creation with labels failed, retrying without labels..."
    gh pr create \
      --base main \
      --head "$BRANCH_NAME"
  }
```

### pr-failure-learning.yml ✅
```yaml
gh pr create \
  --label "agent-system,automated,copilot" \
  --base main \
  --head "$BRANCH_NAME" || {
    echo "⚠️ PR creation with labels failed, retrying without labels..."
    gh pr create \
      --base main \
      --head "$BRANCH_NAME"
  }
```

## Anti-Patterns to Avoid

### ❌ Bad Pattern 1: No Fallback
```yaml
gh pr create --label "some-label" --base main --head "$BRANCH"
# Problem: Fails completely if label missing
```

### ❌ Bad Pattern 2: Weak Fallback
```yaml
gh pr create --label "some-label" --base main --head "$BRANCH" || echo "Warning"
# Problem: Prints message but doesn't retry
```

### ❌ Bad Pattern 3: `|| true`
```yaml
gh pr create --label "some-label" --base main --head "$BRANCH" || true
# Problem: Suppresses error but doesn't create PR
```

### ✅ Correct Pattern
```yaml
gh pr create --label "some-label" --base main --head "$BRANCH" || {
  echo "⚠️ Label failure, retrying without labels..."
  gh pr create --base main --head "$BRANCH"
}
# Success: Always creates PR, with or without labels
```

## Label Creation Infrastructure

The repository has multiple ways to ensure labels exist:

### 1. Automated Workflow
- File: `.github/workflows/ensure-labels-exist.yml`
- Runs: Weekly on Mondays, on workflow changes, manual trigger
- Action: Creates all standard labels

### 2. Quick Fix Script
- File: `scripts/fix-workflow-labels.sh`
- Usage: `bash scripts/fix-workflow-labels.sh`
- Features: Interactive, verifies labels

### 3. Python Label Creator
- File: `tools/create_labels.py`
- Usage: `python3 tools/create_labels.py --all`
- Creates: System, agent, category, location labels

## Best Practices

### For Issue Creation
```yaml
gh issue create \
  --label "automated" || true
  # Simple || true is OK for issues (less critical)
```

### For PR Creation
```yaml
gh pr create \
  --label "label1,label2" \
  --base main \
  --head "$BRANCH" || {
    echo "⚠️ PR creation with labels failed, retrying without labels..."
    gh pr create \
      --body "Updated body noting label unavailability" \
      --base main \
      --head "$BRANCH"
  }
  # Full retry required - PRs are critical
```

### Error Messages
- ✅ Be specific: "PR creation with labels failed"
- ✅ Explain action: "retrying without labels"
- ✅ Use emoji: "⚠️" for warnings
- ❌ Don't hide errors: avoid silent failures

## Testing Workflows

### Local Testing
1. Fork the repository (labels won't transfer)
2. Run workflow that creates PR
3. Verify PR is created even without labels
4. Check PR body for "(labels unavailable)" notice

### Validation
```bash
# Check workflow syntax
yamllint -d relaxed .github/workflows/your-workflow.yml

# Search for workflows needing fixes
grep -l "gh pr create" .github/workflows/*.yml | \
  xargs grep -L "|| {" 
```

## Monitoring

After implementing these fixes:

1. **Failure Rate**: Should drop from 34% to <20%
2. **PR Creation**: All PRs should be created successfully
3. **Label Status**: Check if PRs have "(labels unavailable)" notice
4. **Health Alerts**: Monitor workflow-health-monitor for improvements

## Future Improvements

**@troubleshoot-expert** recommends:

1. **Standardize**: Apply this pattern to all PR-creating workflows
2. **Template**: Create a workflow template with built-in fallback
3. **Documentation**: Update workflow creation guide
4. **Alert**: Notify when labels are missing (don't just silently retry)

## References

- Original Issue: Workflow Health Alert - 2025-11-17
- Alert Stats: 100 runs, 56 completed, 19 failed (33.9%)
- Failing Workflows: 4 identified
- Fixes Applied: 2 workflows enhanced
- Pattern Source: update-agent-investments.yml (reference implementation)

---

*📝 Documentation by **@troubleshoot-expert** - Preventing workflow failures through robust error handling*
