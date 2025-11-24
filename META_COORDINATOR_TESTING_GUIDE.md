# Meta-Coordinator Issue Creation Fix - Testing Guide

## Automated Test (Recommended)

### Option 1: Manual Workflow Dispatch
1. Go to: https://github.com/enufacas/Chained/actions/workflows/meta-coordinator.yml
2. Click "Run workflow"
3. Select branch: `copilot/fix-meta-coordinator-issue`
4. Set inputs:
   - `focus_area`: all
   - `dry_run`: false (to actually create the issue)
5. Click "Run workflow"
6. Monitor the workflow run
7. Verify:
   - ✅ Step "Create and assign coordination request" succeeds
   - ✅ An issue is created (check Issues tab)
   - ✅ Issue body is complete and properly formatted
   - ✅ Issue has correct labels: `meta-coordination,automated,system-orchestration`

### Option 2: Wait for Scheduled Run
The workflow runs automatically every 15 minutes via cron schedule.
1. Wait for next scheduled run (check Actions tab)
2. Monitor the run
3. Verify issue creation as above

## Manual Test (Alternative)

If you want to test locally without triggering the actual workflow:

```bash
# Set environment variables
export GH_TOKEN="your_github_token"
export GITHUB_REPOSITORY="enufacas/Chained"
export TRIGGER_EVENT="workflow_dispatch"
export FOCUS_AREA="all"
export DRY_RUN="false"

# Create test issue body
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
RUN_ID="test-12345"
ISSUE_TITLE="🎯 Meta-Coordination: Test $(date +%H:%M)"

ISSUE_BODY="## 🎯 Meta-Coordination Request (TEST)

**Trigger:** ${TRIGGER_EVENT}
**Focus:** ${FOCUS_AREA}
**Repository:** ${GITHUB_REPOSITORY}
**Timestamp:** ${TIMESTAMP}
**Run ID:** ${RUN_ID}
**Dry Run:** ${DRY_RUN}

This is a test issue to verify the fix for issue creation.
"

# Write to file (the fix we implemented)
echo "$ISSUE_BODY" > /tmp/issue_body_test.md

# Test issue creation
gh issue create \
  --repo "${GITHUB_REPOSITORY}" \
  --title "${ISSUE_TITLE}" \
  --body-file /tmp/issue_body_test.md \
  --label "test,meta-coordination"

# Verify
echo "✅ If issue was created successfully, the fix works!"
```

## What to Verify

### Issue Creation Success
- ✅ Issue is created in the repository
- ✅ Issue has a valid issue number (e.g., #1234)
- ✅ Workflow step does not fail with "Failed to create coordination issue"

### Issue Body Integrity
- ✅ All sections are present (not truncated)
- ✅ Markdown formatting is correct
- ✅ Code blocks display properly (with backticks)
- ✅ Variables are substituted correctly (TRIGGER_EVENT, FOCUS_AREA, etc.)
- ✅ Emojis display correctly (🎯, 🤖, ✅, etc.)
- ✅ Line breaks and formatting are preserved

### Issue Metadata
- ✅ Title: "🎯 Meta-Coordination: HH:MM"
- ✅ Labels: `meta-coordination`, `automated`, `system-orchestration`
- ✅ State: Open
- ✅ Assignee: Will be assigned by subsequent step

### Workflow Behavior
- ✅ No error messages in workflow logs
- ✅ Issue URL is extracted correctly
- ✅ Issue number is stored in GITHUB_OUTPUT
- ✅ Subsequent step (Assign Copilot) proceeds normally

## Expected Output in Workflow Logs

```
Creating coordination issue...
✅ Created coordination issue #1234
   URL: https://github.com/enufacas/Chained/issues/1234
```

## Rollback Plan

If the fix causes issues:

1. Revert the change:
```bash
git revert 2bc16099
```

2. Or restore original behavior:
```yaml
# Change back to:
issue_url=$(gh issue create \
  --repo "${GITHUB_REPOSITORY}" \
  --title "${ISSUE_TITLE}" \
  --body "${ISSUE_BODY}" \
  --label "meta-coordination,automated,system-orchestration" 2>&1)
```

3. Investigate alternative solutions:
   - Truncate issue body to smaller size
   - Split into multiple issues
   - Use GitHub API directly instead of gh CLI

## Success Criteria

The fix is successful if:
1. ✅ Meta-coordinator workflow completes without errors
2. ✅ Coordination issue is created in every run
3. ✅ Issue body is complete and properly formatted
4. ✅ No regression in other workflow functionality
5. ✅ Pattern can be applied to other workflows if needed

## Additional Notes

- The fix uses `/tmp/issue_body.md` which is available in GitHub Actions runners
- Temp file is automatically cleaned up by the runner after workflow completion
- Pattern is proven to work in `discover-universal-truths.yml`
- No changes to workflow permissions or environment variables needed
- Error handling is preserved (still checks exit code and extracts issue number)
