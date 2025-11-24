# Tech Lead Assignment Flow

## Overview

This document explains how the meta-coordinator assigns work to tech leads and ensures Copilot sessions start for that work.

## The Problem

Simply creating an issue does NOT start a Copilot session. The issue is just documentation. **Assignment is required** to trigger Copilot to start working.

## The Solution: Two-Step Process

### Step 1: Create Tech Lead Review Issue

```bash
# Create the issue
review_issue_num=$(gh issue create \
  --title "[Tech Lead Review] PR #${pr_num}: ${pr_title}" \
  --body "Tech lead review details..." \
  --label "tech-lead-review,needs-review,linked-to-pr" \
  --json number --jq '.number')
```

**Result:** Issue exists in GitHub, visible to humans
**Status:** ❌ No Copilot session yet - issue is just documentation

### Step 2: Assign Tech Lead Agent to Issue

```bash
# CRITICAL: This starts the Copilot session
export INPUT_ISSUE_NUMBER=$review_issue_num
export FORCE_AGENT="workflows-tech-lead"  # Specific tech lead agent
./tools/assign-copilot-to-issue.sh
```

**Result:** Copilot session starts for the tech lead agent
**Status:** ✅ Tech lead agent (Copilot) is now actively working on the review

## Complete Flow Diagram

```
PR Requires Review
       ↓
Meta-Coordinator Detects Need
       ↓
Step 1: Create Review Issue
       ├─→ Issue visible in GitHub
       ├─→ Links to PR
       └─→ Labels applied
       ↓
       ❌ NOT YET WORKING - Just documentation
       ↓
Step 2: Assign Tech Lead
       ├─→ ./tools/assign-copilot-to-issue.sh
       ├─→ GraphQL API call
       ├─→ Copilot actor assigned to issue
       └─→ Issue body updated with @agent directive
       ↓
       ✅ COPILOT SESSION STARTS
       ↓
Tech Lead Agent (Copilot) Works on Review
       ├─→ Analyzes PR changes
       ├─→ Checks code quality
       ├─→ Makes decision (approve/request changes)
       └─→ Updates PR labels and posts results
       ↓
Meta-Coordinator Detects Outcome
       └─→ Proceeds with next steps (merge, feedback, etc.)
```

## What assign-copilot-to-issue.sh Does

The script performs these critical actions:

### 1. Agent Matching (if not forced)
```bash
agent=$(python3 tools/match-issue-to-agent.py "$issue_title" "$issue_body" --json | jq -r '.agent')
```

### 2. Learning Guidance
```bash
learning=$(python3 tools/agent-learning-api.py query \
  --agent "$agent" \
  --task-description "$issue_title")
```

### 3. Issue Body Update
Prepends agent directive to issue body:
```markdown
<!-- COPILOT_AGENT:workflows-tech-lead -->

> **🤖 Agent Assignment**
> 
> This issue has been assigned to **@workflows-tech-lead**.
> 
> **@workflows-tech-lead** - Please use the specialized approach...
>
> **IMPORTANT**: Always mention **@workflows-tech-lead** by name...
```

### 4. GraphQL Assignment
```bash
# Get Copilot actor ID
actor_id=$(gh api graphql -f query='...' --jq '.data.user.id')

# Assign via mutation
gh api graphql -f query='mutation($issueId: ID!, $actorId: ID!) {
  replaceActorsForAssignable(input: {
    assignableId: $issueId,
    actorIds: [$actorId]
  }) { ... }
}'
```

### 5. Label Management
```bash
gh issue edit $issue_num --add-label "copilot-assigned"
gh issue edit $issue_num --add-label "agent:workflows-tech-lead"
```

### 6. Success Comment
Posts confirmation that assignment completed successfully.

## Environment Variables Required

```bash
# Required for script to work
export GH_TOKEN="${GITHUB_TOKEN}"
export GITHUB_REPOSITORY="owner/repo"
export GITHUB_REPOSITORY_OWNER="owner"
export GITHUB_REPOSITORY_NAME="repo"

# For specific issue
export INPUT_ISSUE_NUMBER="123"

# For forcing specific agent (tech leads, re-reviews)
export FORCE_AGENT="workflows-tech-lead"
```

## Common Patterns

### Pattern 1: Initial Tech Lead Assignment

```bash
# 1. Match tech lead to PR
tech_lead=$(python3 tools/match-pr-to-tech-lead.py "$pr_num" --get-tech-lead)

# 2. Create review issue
review_issue_num=$(gh issue create \
  --title "[Tech Lead Review] PR #${pr_num}" \
  --body "Review request..." \
  --label "tech-lead-review" \
  --json number --jq '.number')

# 3. CRITICAL: Assign tech lead
export INPUT_ISSUE_NUMBER=$review_issue_num
export FORCE_AGENT=$tech_lead
./tools/assign-copilot-to-issue.sh

# 4. Link to PR
gh pr comment $pr_num --body "Review requested in issue #${review_issue_num}"
```

### Pattern 2: Re-Review After Updates

```bash
# PR author pushed updates, need re-review

# 1. Find existing review issue
review_issue_num=$(gh issue list --label "tech-lead-review" \
  --state open --search "PR #${pr_num}" --json number --jq '.[0].number')

# 2. Post re-review request
gh issue comment $review_issue_num --body "Re-review requested - new commits pushed"

# 3. CRITICAL: Re-assign tech lead (in case they unassigned)
export INPUT_ISSUE_NUMBER=$review_issue_num
export FORCE_AGENT=$tech_lead
./tools/assign-copilot-to-issue.sh
```

### Pattern 3: Feedback Issue for Changes Requested

```bash
# Tech lead requested changes, need agent to address feedback

# 1. Match agent for feedback work
agent=$(python3 tools/match-issue-to-agent.py "Address feedback" "$feedback_details" \
  --json | jq -r '.agent')

# 2. Create feedback issue
feedback_issue_num=$(gh issue create \
  --title "[Tech Lead Feedback] PR #${pr_num}" \
  --body "$feedback_details" \
  --label "tech-lead-feedback" \
  --json number --jq '.number')

# 3. CRITICAL: Assign agent to feedback issue
export INPUT_ISSUE_NUMBER=$feedback_issue_num
export FORCE_AGENT=$agent
./tools/assign-copilot-to-issue.sh

# 4. Link to PR
gh pr comment $pr_num --body "Feedback issue created: #${feedback_issue_num}"
```

## Why This Matters

### Without Assignment (Just Creating Issue)
- ❌ Issue exists but sits idle
- ❌ No Copilot session starts
- ❌ Tech lead work doesn't happen
- ❌ PR review cycle stalls
- ❌ System doesn't move forward

### With Assignment (Creating Issue + Calling Script)
- ✅ Copilot session starts immediately
- ✅ Tech lead agent begins work autonomously
- ✅ Review happens automatically
- ✅ PR cycle continues flowing
- ✅ System moves toward desired state

## Testing Assignment

To verify assignment worked:

```bash
# 1. Check issue labels
gh issue view $issue_num --json labels --jq '.labels[].name' | grep copilot-assigned

# 2. Check issue body for agent directive
gh issue view $issue_num --json body --jq '.body' | grep "COPILOT_AGENT:"

# 3. Check issue assignees
gh issue view $issue_num --json assignees --jq '.assignees[].login'

# 4. Monitor for Copilot activity
# Watch for PRs created by copilot[bot] linked to the issue
```

## Troubleshooting

### Issue Created But No Work Happening

**Problem:** Issue exists but tech lead isn't working on it
**Likely Cause:** Assignment step was skipped
**Solution:** Run assignment script:
```bash
export INPUT_ISSUE_NUMBER=$issue_num
export FORCE_AGENT="workflows-tech-lead"
./tools/assign-copilot-to-issue.sh
```

### Assignment Script Fails

**Problem:** Script exits with error
**Likely Causes:**
1. Missing environment variables (GH_TOKEN, GITHUB_REPOSITORY, etc.)
2. Invalid agent name in FORCE_AGENT
3. Issue doesn't exist
4. GitHub API authentication issue

**Solution:** Check environment variables and agent names

### Wrong Agent Assigned

**Problem:** Wrong agent type working on issue
**Cause:** FORCE_AGENT not set or incorrect
**Solution:** Re-assign with correct agent:
```bash
export INPUT_ISSUE_NUMBER=$issue_num
export FORCE_AGENT="correct-agent-name"
./tools/assign-copilot-to-issue.sh
```

## Summary

**Key Takeaway:** Creating an issue is NOT enough. You MUST call `./tools/assign-copilot-to-issue.sh` to actually start a Copilot session for the work to be done.

**Remember:**
1. Create issue = Documentation
2. Assign Copilot = Execution
3. Both steps required = Work gets done

**Always:**
- Create issue first (get issue number)
- Then immediately assign (start Copilot session)
- Never skip the assignment step
- Use FORCE_AGENT for tech leads and specific agents
