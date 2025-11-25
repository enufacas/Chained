# Simple Guide: Change PR Target to Main

## Current Situation

**Your PR branch:** `copilot/investigate-copilot-error`
- ✅ Contains 4 commits with the HTTP 413 fix
- ✅ All changes committed and pushed
- ❌ Currently targeting wrong base branch (not main)

**Main branch:** Experiencing HTTP 413 errors, needs this fix

## Solution: Change PR Target via GitHub Website

This is the **easiest and safest** method:

### Step 1: Open Your PR
1. Go to: https://github.com/enufacas/Chained/pulls
2. Find the PR from branch `copilot/investigate-copilot-error`
3. Click on it to open

### Step 2: Change Base Branch
1. Near the top of the PR page, you'll see:
   ```
   [base: some-branch] ← [compare: copilot/investigate-copilot-error]
   ```
2. Click **"Edit"** button next to the base branch name
3. Select **`main`** from the dropdown menu
4. Click **"Change base"** button

### Step 3: Verify
- PR should now show: `base: main ← compare: copilot/investigate-copilot-error`
- GitHub will recalculate the diff (may take a few seconds)
- Check that the changes look correct

### Step 4: Merge
- Once the PR targets main, you can merge it
- This will fix the HTTP 413 errors on main branch

## What This PR Does

| Issue | Solution | Result |
|-------|----------|---------|
| HTTP 413 errors | Reduced instruction size 59% | ✅ Fixed |
| Context too large | 122KB → 50KB | ✅ Fixed |
| Too many tokens | ~30K → ~12.5K tokens | ✅ Fixed |
| .copilot-instructions.md | No changes needed | ✅ Preserved |

## After Merging

Main branch will have:
- ✅ Working Copilot (no HTTP 413 errors)
- ✅ All instruction files optimized
- ✅ CI validation to prevent future bloat
- ✅ Documentation and guides
- ✅ `.copilot-instructions.md` preserved unchanged

## If You Can't Change the Base

Alternative: Close the old PR and create a new one:

```bash
# Ensure you're on the fix branch
git checkout copilot/investigate-copilot-error

# Create PR via web UI, making sure to select 'main' as the base branch
# Or use GitHub CLI:
gh pr create \
  --base main \
  --head copilot/investigate-copilot-error \
  --title "Fix GitHub Copilot HTTP 413 errors on main" \
  --body "Fixes HTTP 413 errors by reducing instruction context size from 122KB to 50KB"
```

## Troubleshooting

### "I don't see an Edit button"
- You may need maintainer permissions
- Alternative: Ask a maintainer to change the base branch
- Or: Close and recreate PR with correct base

### "GitHub shows many merge conflicts"
This is unlikely because:
- Our changes are mostly to instruction files
- `.copilot-instructions.md` is identical in both branches
- New files don't conflict with existing ones

If you do see conflicts, you can rebase:
```bash
git checkout copilot/investigate-copilot-error
git fetch origin main
git rebase origin/main
# Resolve any conflicts if they appear
git push --force-with-lease origin copilot/investigate-copilot-error
```

### "What if the changes don't apply cleanly?"
The changes should apply cleanly because:
1. ✅ `.copilot-instructions.md` is identical (verified)
2. ✅ Instruction files are independent
3. ✅ New files don't conflict
4. ✅ Documentation files are new

## Verification After Merge

Test that main is fixed:
```bash
# Pull latest main
git checkout main
git pull origin main

# Check instruction size (should be ~50KB)
find .github/instructions -name "*.md" -exec cat {} \; | wc -c

# Verify .copilot-instructions.md exists
ls -lh .copilot-instructions.md

# Test a Copilot workflow
# Create a test issue → Assign to agent → Watch workflow
# Should complete without HTTP 413 errors
```

## Summary

**What to do:**
1. Open your PR on GitHub
2. Click "Edit" next to base branch
3. Select `main`
4. Click "Change base"
5. Merge the PR

**Result:**
- ✅ Main branch fixed
- ✅ Copilot works again
- ✅ HTTP 413 errors gone
- ✅ All content preserved

**Time required:** < 2 minutes

That's it! The fix is ready to go, it just needs to target the right branch.
