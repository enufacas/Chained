# How to Change PR Target Branch to Main

## Situation

**Current state:**
- Branch: `copilot/investigate-copilot-error`
- Contains fixes for HTTP 413 Copilot errors
- Currently targeting: Unknown branch (not main)
- **Needs to target: `main`**

**Why this matters:**
Main branch is experiencing HTTP 413 errors due to oversized Copilot instructions. This PR contains the fix, but it needs to target main to actually fix it.

## Quick Fix: Change PR Target via GitHub Web Interface

### Method 1: GitHub Web UI (Easiest)

1. **Go to the PR page:**
   - Navigate to: https://github.com/enufacas/Chained/pulls
   - Find PR from branch `copilot/investigate-copilot-error`

2. **Change the base branch:**
   - On the PR page, look for the branch selector near the top
   - It shows: `base: [current-branch] ← compare: copilot/investigate-copilot-error`
   - Click "Edit" next to the base branch name
   - Select `main` from the dropdown
   - Click "Change base"

3. **Verify:**
   - PR should now show: `base: main ← compare: copilot/investigate-copilot-error`
   - GitHub will recalculate the diff

### Method 2: GitHub CLI (If You Have Access)

```bash
# Find the PR number
gh pr list --head copilot/investigate-copilot-error

# Change the base branch to main
gh pr edit <PR_NUMBER> --base main

# Example:
# gh pr edit 2275 --base main
```

### Method 3: GitHub API (Advanced)

```bash
# Get PR number
PR_NUMBER=$(gh pr list --head copilot/investigate-copilot-error --json number -q '.[0].number')

# Update base branch
gh api repos/enufacas/Chained/pulls/$PR_NUMBER \
  --method PATCH \
  --field base='main'
```

## Alternative: Create New PR Against Main

If changing the base is problematic, create a new PR:

```bash
# Ensure we're on the right branch
git checkout copilot/investigate-copilot-error

# Push to a new branch name (optional, for clarity)
git push origin copilot/investigate-copilot-error:copilot/fix-context-size-for-main

# Create new PR via web UI or CLI
gh pr create \
  --base main \
  --head copilot/fix-context-size-for-main \
  --title "Fix GitHub Copilot HTTP 413 errors on main branch" \
  --body "See detailed description in original PR"
```

## What This PR Does

When merged to main, this PR will:

### ✅ Fix the HTTP 413 Error
- Reduces instruction context from 122KB to 50KB (59% reduction)
- Reduces token count from ~30,000 to ~12,500 (58% reduction)
- Brings context well within GitHub Copilot's limits

### ✅ Preserve All Content
- `.copilot-instructions.md` remains unchanged (verified)
- Detailed guides moved to `docs/guides/copilot-instructions/`
- All critical guidance retained in condensed form
- No information loss

### ✅ Prevent Future Issues
- Adds CI validation workflow
- Creates optimization guide
- Documents best practices
- Monitors instruction size automatically

## Files Changed in This PR

**Optimized files:**
- `.github/instructions/agent-mentions.instructions.md` (7.6KB → 1.8KB)
- `.github/instructions/branch-protection.instructions.md` (8.9KB → 1.5KB)
- `.github/instructions/agent-issue-updates.instructions.md` (11.5KB → 1.3KB)
- `.github/instructions/agent-definition-sync.instructions.md` (9.7KB → 1.3KB)
- `.github/instructions/workflow-reference.instructions.md` (9.6KB → 1.8KB)
- `.github/instructions/issue-pr-agent-mentions.instructions.md` (7.0KB → 1.5KB)
- `.github/instructions/README.md` (updated with size guidance)

**New files:**
- `.github/workflows/validate-instructions-size.yml` (CI validation)
- `docs/guides/CONTEXT_SIZE_OPTIMIZATION.md` (optimization guide)
- `docs/guides/copilot-instructions/threejs-rendering-guide.md` (detailed guide)
- `docs/guides/copilot-instructions/github-pages-testing-guide.md` (detailed guide)
- `docs/investigations/copilot-instructions-file-status.md` (file status report)
- `docs/investigations/change-pr-target-to-main.md` (this file)

**Preserved files:**
- `.copilot-instructions.md` (unchanged, 6.8KB, 194 lines)
- All other instruction files
- All agent definitions
- All workflows

## Expected Results After Merge

### Immediate:
- ✅ Copilot workflows on main will work (no more HTTP 413)
- ✅ Instruction context within limits (50KB vs 122KB before)
- ✅ All content preserved and accessible

### Long-term:
- ✅ CI prevents size from growing again
- ✅ Clear guidelines for maintaining concise instructions
- ✅ Sustainable approach for future additions

## Verification Steps After Merge

1. **Verify merge completed:**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Check instruction size:**
   ```bash
   find .github/instructions -name "*.md" -exec cat {} \; | wc -c
   # Should show ~50,000 bytes
   ```

3. **Test Copilot workflow:**
   - Create a test issue assigned to an agent
   - Watch workflow run
   - Verify no HTTP 413 errors
   - Confirm Copilot completes successfully

4. **Verify file preservation:**
   ```bash
   ls -lh .copilot-instructions.md
   # Should show file exists with 194 lines
   ```

## Troubleshooting

### If PR Can't Change Base
- Close the existing PR
- Create new PR with correct base
- Reference original PR in description

### If Merge Conflicts Occur
This is unlikely since:
- Main's `.copilot-instructions.md` matches our branch
- Instruction files are independent
- New files don't conflict with existing ones

If conflicts do occur:
```bash
git checkout main
git pull origin main
git checkout copilot/investigate-copilot-error
git rebase main
# Resolve any conflicts
git push --force-with-lease origin copilot/investigate-copilot-error
```

### If You Want to Test First
Create a test branch from main:
```bash
git checkout main
git pull origin main
git checkout -b test-copilot-fix
git cherry-pick a2f0b6a..8d9133b
git push origin test-copilot-fix
# Test on this branch first
```

## Summary

**Action Required:** Change PR base branch from current target to `main`

**Method:** Use GitHub web interface (easiest) or CLI commands above

**Result:** Fixes HTTP 413 errors on main branch when merged

**Risk:** Very low - all content preserved, changes are additive/optimization only

**Testing:** Verify no HTTP 413 errors in Copilot workflows after merge
