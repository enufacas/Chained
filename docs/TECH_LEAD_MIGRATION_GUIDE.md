# Tech Lead Review System Migration Guide

## Summary of Changes

The tech lead review system has been **simplified from 4 fragile workflows into 1 consolidated workflow**.

### Before (Fragile System)
```
pr-tech-lead-trigger.yml          45 lines   ❌ REMOVED
tech-lead-review.yml             525 lines   ❌ REMOVED
tech-lead-feedback-handler.yml   445 lines   ❌ REMOVED
setup-tech-lead-labels.yml       157 lines   ✅ KEPT
auto-review-merge.yml            468 lines   ✅ REPLACED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:                          1640 lines
```

### After (Simplified System)
```
auto-review-merge.yml            513 lines   ✅ NEW (improved)
setup-tech-lead-labels.yml       157 lines   ✅ KEPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL:                           670 lines   (59% reduction)
```

## What Changed

### Removed Workflows
1. **pr-tech-lead-trigger.yml** - No longer needed (used workflow_run pattern)
2. **tech-lead-review.yml** - Logic integrated into auto-review-merge.yml
3. **tech-lead-feedback-handler.yml** - Logic integrated into auto-review-merge.yml

### Improved Workflow
**auto-review-merge.yml** - Now has 3 clear stages:

1. **Stage 1: analyze-prs** - Analyzes all PRs, determines tech lead requirements
2. **Stage 2: process-pr** - Handles tech lead labels, reviews, feedback (matrix job)
3. **Stage 3: auto-merge** - Merges eligible PRs after approval (matrix job)

### Kept Workflow
**setup-tech-lead-labels.yml** - Still needed for creating tech lead labels

## Functional Changes

### What Stayed the Same ✅
- ✅ Tech lead analysis logic (uses same `tools/match-pr-to-tech-lead.py`)
- ✅ Complexity thresholds (file count, line changes, protected paths)
- ✅ Label-based blocking (`needs-tech-lead-review`, `tech-lead-approved`)
- ✅ Agent follow-up issue creation
- ✅ Review state management (approved, changes requested)
- ✅ WIP detection and skipping
- ✅ Auto-merge criteria (trusted sources, copilot label)

### What Changed 🔄
- 🔄 **Trigger mechanism:** Schedule-based (every 15 min) instead of event-driven
- 🔄 **Workflow structure:** Single workflow with 3 jobs instead of 4 separate workflows
- 🔄 **Error handling:** Better isolation (fail-fast: false on matrix jobs)
- 🔄 **Debugging:** Easier to understand and troubleshoot

### Trade-offs ⚖️
**Slight delay (max 15 min) before detection**
- **Before:** Immediate response to PR events
- **After:** Up to 15 minutes until next scheduled run
- **Impact:** Minimal - tech lead reviews typically take hours/days anyway
- **Benefit:** Much simpler, more reliable system

## Migration Steps

### Automatic Migration (Already Done ✅)
1. ✅ Created new consolidated workflow
2. ✅ Removed old fragile workflows
3. ✅ Replaced auto-review-merge.yml
4. ✅ Documented changes

### What You Need to Do
**Nothing!** The migration is complete and backward-compatible.

### Monitoring (First 24-48 Hours)
1. Watch scheduled workflow runs (every 15 minutes)
2. Verify tech lead labels are applied correctly
3. Check that reviews are processed
4. Confirm auto-merge works as expected

## Testing

### Manual Test
```bash
# Trigger workflow for specific PR
gh workflow run auto-review-merge.yml -f pr_number=123

# Check recent runs
gh run list --workflow=auto-review-merge.yml --limit 5

# View run details
gh run view <run_id> --log
```

### Test Scenarios
Create test PRs to verify:

1. **Tech lead review required:**
   - Modify `.github/workflows/test.yml`
   - Should get `needs-tech-lead-review` label
   - Should get `tech-lead:workflows-tech-lead` label

2. **Tech lead review optional:**
   - Modify `README.md` only
   - Should NOT get tech lead labels
   - Should proceed to auto-merge

3. **Review approval:**
   - Approve a PR that needs tech lead review
   - Should get `tech-lead-approved` label
   - Should remove `needs-tech-lead-review` label
   - Should proceed to auto-merge

4. **Review changes requested:**
   - Request changes on a PR
   - Should get `tech-lead-changes-requested` label
   - Should create follow-up issue for agent
   - Should block auto-merge

5. **WIP PR:**
   - Create PR with `[WIP]` in title
   - Should skip all processing
   - Should not be merged

## Rollback Plan (If Needed)

If critical issues arise, you can rollback:

```bash
# 1. Restore old workflows from git history
git checkout e1a9fbc7 -- .github/workflows/pr-tech-lead-trigger.yml
git checkout e1a9fbc7 -- .github/workflows/tech-lead-review.yml
git checkout e1a9fbc7 -- .github/workflows/tech-lead-feedback-handler.yml
git checkout e1a9fbc7 -- .github/workflows/auto-review-merge.yml

# 2. Commit and push
git add .github/workflows/*.yml
git commit -m "Rollback: Restore old tech lead review system"
git push
```

**Note:** Commit hash `e1a9fbc7` is the last commit before the migration. Adjust if needed.

## Troubleshooting

### Issue: PR not being processed
**Cause:** PR might be draft or have WIP marker  
**Fix:** Remove WIP marker, convert from draft to ready

### Issue: Tech lead review not detected
**Cause:** Scheduled run hasn't occurred yet  
**Fix:** Wait up to 15 minutes, or trigger manually with workflow_dispatch

### Issue: Labels not applied
**Cause:** Label creation workflow hasn't run  
**Fix:** Run `setup-tech-lead-labels.yml` manually

### Issue: Follow-up issue not created
**Cause:** Agent matching failed or review body empty  
**Fix:** Check workflow logs for agent matching errors

## Benefits of New System

✅ **Simpler:** Single workflow instead of 4  
✅ **More Reliable:** No complex workflow_run triggers  
✅ **Easier to Debug:** All logic in one place  
✅ **Better Error Handling:** Isolated matrix jobs  
✅ **More Maintainable:** Clear stages and structure  
✅ **Testable:** Manual trigger for specific PRs  
✅ **Less Code:** 59% reduction in lines of code  

## Documentation

- **Full Documentation:** `docs/SIMPLIFIED_TECH_LEAD_REVIEW.md`
- **Workflow File:** `.github/workflows/auto-review-merge.yml`
- **Label Setup:** `.github/workflows/setup-tech-lead-labels.yml`
- **Tech Lead Matching:** `tools/match-pr-to-tech-lead.py`

## Questions?

If you encounter issues or have questions:
1. Check the workflow logs
2. Read `docs/SIMPLIFIED_TECH_LEAD_REVIEW.md`
3. Open an issue with details
4. Use rollback plan if critical

## Success Criteria

The migration is successful when:
- ✅ All open PRs are processed within 15 minutes
- ✅ Tech lead labels are applied correctly
- ✅ Reviews are processed (approved/changes requested)
- ✅ Follow-up issues created for change requests
- ✅ Auto-merge works for approved PRs
- ✅ No errors in workflow logs

Monitor for 24-48 hours to confirm stability.
