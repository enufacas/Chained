# Copilot PR Labeling Fix

## Problem Summary
Draft PRs created by Copilot were not being automatically converted to "ready for review" status because they were missing the `copilot` label. The auto-review-merge workflow requires both:
1. ✅ PR from trusted bot (Copilot)
2. ❌ PR has `copilot` label (was missing)

## Solution
Added a new workflow `.github/workflows/auto-label-copilot-prs.yml` that automatically labels PRs from Copilot.

## How to Fix Existing Draft PRs

### Option 1: Manual Trigger (Recommended)
1. Go to **Actions** tab in GitHub
2. Click on **"Auto Label Copilot PRs"** workflow in the left sidebar
3. Click **"Run workflow"** button
4. Check the box for **"Label all existing Copilot PRs"**
5. Click **"Run workflow"** to start
6. Wait for completion (usually <1 minute)

This will add the `copilot` label to all existing open PRs from Copilot (#80, #79, #78, #77, #76, #75, #74, #73, #72).

### Option 2: Wait for Next PR
The workflow will automatically label any new PRs created by Copilot going forward.

## What Happens After Labeling?

Once the `copilot` label is added:
1. The **auto-review-merge workflow** (runs every 15 minutes) will detect the draft PRs
2. It will check if the title contains "WIP" markers
3. If no WIP markers found:
   - Convert draft to "ready for review"
   - Add a comment explaining the conversion
4. On next cycle (another 15 minutes):
   - Auto-approve and merge if all checks pass
   - Delete the branch automatically

## Expected Timeline

```
Time +0:00 - User triggers "Auto Label Copilot PRs" workflow
Time +0:01 - Labels added to all Copilot PRs
Time +0:15 - Auto-review workflow runs, converts drafts to ready
Time +0:30 - Auto-review workflow runs again, merges ready PRs
```

## Verification

After triggering the workflow, you can verify it worked by:
1. Check the workflow run status in Actions tab
2. Visit any draft PR (e.g., #80) and verify it has the `copilot` label
3. Wait for next auto-review cycle (check scheduled runs every 15 minutes)
4. Draft PRs should be converted to "ready for review" with a comment

## Current Draft PRs to be Processed
- PR #80 - Implement workflow triggering in system-kickoff
- PR #79 - Document Hacker News learning cycle
- PR #78 - Add missing issue-to-pr and auto-close-issues workflows
- PR #77 - Add comprehensive analysis for HN learning data
- PR #76 - Grid timeline layout and workflow run status
- PR #75 - Add self-improving code analyzer
- PR #74 - Add cross-language code translator
- PR #73 - Add cross-repository pattern matcher
- PR #72 - Document HN learning collection

All are from Copilot and need the `copilot` label to be processed by automation.
