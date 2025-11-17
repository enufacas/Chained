# Workflow Label Fallback Pattern

## Problem

GitHub workflows that create issues or PRs with labels will fail if those labels don't exist in the repository. This causes workflow failures and increases the failure rate.

## Solution: Fallback Pattern

**@troubleshoot-expert** recommends using this fallback pattern for all `gh issue create` and `gh pr create` commands that use labels:

### For Issue Creation

```bash
# Create issue with fallback if labels don't exist
gh issue create \
  --title "Issue Title" \
  --body "$ISSUE_BODY" \
  --label "label1,label2,label3" || {
    echo "⚠️ Issue creation with labels failed, retrying without labels..."
    gh issue create \
      --title "Issue Title" \
      --body "$ISSUE_BODY"
  }
```

### For PR Creation

```bash
# Create PR with fallback if labels don't exist
gh pr create \
  --title "PR Title" \
  --body "PR Description" \
  --label "label1,label2" \
  --base main \
  --head "$BRANCH_NAME" || {
    echo "⚠️ PR creation with labels failed, retrying without labels..."
    gh pr create \
      --title "PR Title" \
      --body "PR Description" \
      --base main \
      --head "$BRANCH_NAME"
  }
```

## Why This Works

1. **Resilient**: Workflow completes even if labels are missing
2. **Informative**: Clear error message indicates when labels are missing
3. **Transparent**: Issue/PR is still created, just without labels
4. **Non-blocking**: Doesn't halt the entire workflow for a label issue

## Anti-Patterns to Avoid

### ❌ BAD: No fallback (workflow fails completely)
```bash
gh issue create \
  --title "Issue Title" \
  --body "$ISSUE_BODY" \
  --label "label1,label2"
```

### ❌ BAD: Silent failure (masks the problem)
```bash
gh issue create \
  --title "Issue Title" \
  --body "$ISSUE_BODY" \
  --label "label1,label2" || true
```

### ✅ GOOD: Explicit fallback with clear messaging
```bash
gh issue create \
  --title "Issue Title" \
  --body "$ISSUE_BODY" \
  --label "label1,label2" || {
    echo "⚠️ Issue creation with labels failed, retrying without labels..."
    gh issue create \
      --title "Issue Title" \
      --body "$ISSUE_BODY"
  }
```

## Label Creation

Before workflows can use labels, they must be created. There are two ways:

### 1. Manual Label Creation (Quick Fix)

```bash
# Create all standard labels
python3 tools/create_labels.py --all

# Or via workflow dispatch
# Go to: Actions → "Maintenance: Ensure Repository Labels Exist" → Run workflow
```

### 2. Add Labels to Definition (Permanent Fix)

Edit `tools/create_labels.py` and add your label to the appropriate section:

```python
SYSTEM_LABELS: List[Tuple[str, str, str]] = [
    # ... existing labels ...
    ("your-label", "COLOR_HEX", "Label description"),
]
```

Then run:
```bash
python3 tools/create_labels.py --all
```

## Workflows Fixed

The following workflows have been updated with fallback logic:

- ✅ `.github/workflows/agent-evolution.yml` - Issue creation (line 168)
- ✅ `.github/workflows/repetition-detector.yml` - Issue creation (line 304)
- ✅ `.github/workflows/repetition-detector.yml` - PR creation (line 352) - already had fallback

## Workflows That May Need Updates

These workflows create issues/PRs with labels but don't have fallback logic yet:

- `.github/workflows/ab-testing-manager.yml`
- `.github/workflows/actions-generator-agent.yml`
- `.github/workflows/ai-friend-daily.yml`
- `.github/workflows/code-analyzer.yml`
- `.github/workflows/code-archaeologist.yml`
- `.github/workflows/combined-learning.yml`
- `.github/workflows/daily-goal-generator.yml`
- `.github/workflows/github-pages-review.yml`
- `.github/workflows/learn-from-copilot.yml`
- `.github/workflows/learn-from-hackernews.yml`
- `.github/workflows/learn-from-tldr.yml`
- `.github/workflows/self-reinforcement.yml`

**Note**: Only update these if they start failing due to missing labels. The principle is "minimal changes" - don't fix what isn't broken.

## Testing

To test the fallback logic:

1. **Without labels in repo**: The workflow will use the fallback path
2. **With labels in repo**: The workflow will use labels normally

Both scenarios should result in successful issue/PR creation.

## Benefits

1. **Reduced failure rate**: Workflows don't fail due to missing labels
2. **Better error messages**: Clear indication when labels are missing
3. **Non-breaking**: Issues/PRs are still created
4. **Easier debugging**: Log messages show exactly what happened

## Related Documentation

- `.github/workflows/TROUBLESHOOTING.md` - General workflow troubleshooting
- `tools/create_labels.py` - Label creation tool
- `.github/workflows/WORKFLOW_ERROR_HANDLING_GUIDE.md` - Error handling patterns

---

*Created by **@troubleshoot-expert** - Preventing workflow failures through resilient patterns* 🔧
