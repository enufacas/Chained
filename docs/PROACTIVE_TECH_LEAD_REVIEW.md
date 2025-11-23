# Proactive Tech Lead Review System

## Overview

The `copilot-pr-assignment.yml` workflow has been enhanced to support **proactive tech lead reviews**. When a PR has a tech lead label but no existing review feedback, the system now creates a Copilot issue to trigger a proactive review by the appropriate tech lead agent.

## Problem Statement

Previously, when the workflow encountered a PR with:
- A `tech-lead:*` label (e.g., `tech-lead:agents-tech-lead`)
- No review comments or change requests

The workflow would skip the PR with: `⚠️ No review feedback found for PR #XXXX`

This meant PRs awaiting tech lead attention were being ignored by the automation system.

## Solution

The workflow now detects this scenario and creates a **proactive review issue** instead of skipping the PR.

## How It Works

### 1. Detection Logic (Lines 213-256)

When no review feedback is found:

```bash
if [ -z "${review_body}" ] || [ "${review_body}" = "null" ]; then
  # Check if tech lead agent is identified from labels
  if [ -n "${tech_lead_agent}" ]; then
    # Create proactive review request
    review_body="## 🔍 Proactive Tech Lead Review Request
    
    This PR has been assigned to **@${tech_lead_agent}** for technical review.
    
    **PR Details:**
    - **Title:** ${pr_title}
    - **Author:** @${pr_author}
    - **Status:** Open and ready for review
    
    **Review Needed:**
    [Instructions for tech lead review...]
    "
  else
    # No tech lead identified, skip PR
    continue
  fi
fi
```

### 2. Review Type Detection (Lines 260-266)

The workflow determines if this is a proactive review or reactive feedback:

```bash
is_proactive_review="false"
if echo "${review_body}" | grep -q "Proactive review request - no prior feedback found"; then
  is_proactive_review="true"
fi
```

### 3. Agent Selection (Lines 268-290)

**For Proactive Reviews:**
- Uses the tech lead agent directly from the label
- No AI matching needed (we know who should review)
- Sets `matched_agent="${tech_lead_agent}"`

**For Reactive Feedback:**
- Uses AI matching to find the best agent to fix the issues
- Calls `match-issue-to-agent.py` with feedback content

### 4. Issue Creation (Lines 291-310)

Creates different issue types based on review mode:

**Proactive Review:**
- Title: `[Tech Lead Review] PR #XXXX - <PR Title>`
- Labels: `tech-lead-review,agent:${matched_agent},linked-to-pr`
- Body: Instructions for tech lead to review the PR

**Reactive Feedback:**
- Title: `[Tech Lead Feedback] PR #XXXX - <PR Title>`
- Labels: `tech-lead-feedback,agent:${matched_agent},linked-to-pr`
- Body: Existing feedback with instructions to fix

## Issue Templates

### Proactive Review Issue

```markdown
> **🤖 Agent Assignment**
> 
> This issue has been assigned to GitHub Copilot with the **🔍 @agents-tech-lead** custom agent profile.
> 
> **@agents-tech-lead** - Please use the specialized approach defined in `.github/agents/agents-tech-lead.md`.
> 
> **IMPORTANT**: Always mention **@agents-tech-lead** by name in all conversations.

---

## 🔍 Tech Lead Review Request for PR #2368

**PR to Review:** #2368 - Example PR Title  
**Author:** @author-name  
**Tech Lead:** @agents-tech-lead  
**Status:** Awaiting tech lead review

### 📋 Review Instructions

[Proactive review request body with detailed instructions]

---

## 🎯 Your Task (@agents-tech-lead)

1. **Review the PR:** Check out PR #2368 and thoroughly review the changes
2. **Assess code quality:** Evaluate according to your tech lead specialization
3. **Provide feedback:**
   - Add review comments on specific lines if needed
   - Identify any issues or concerns
   - Suggest improvements
   - Follow the agents-tech-lead tech lead guidelines
4. **Submit review:** Use GitHub's review system to approve or request changes
5. **Update status:**
   - Comment on this issue with your review summary
   - Close this issue once review is complete

### 🔗 Quick Links

- **PR to review:** [#2368](https://github.com/org/repo/pull/2368)
- **PR files:** [View changes](https://github.com/org/repo/pull/2368/files)
- **Tech lead profile:** [`.github/agents/agents-tech-lead.md`](https://github.com/org/repo/blob/main/.github/agents/agents-tech-lead.md)
```

## PR Comments

When a proactive review issue is created, the workflow adds a comment to the PR:

```markdown
## 🔍 Tech Lead Review Requested

**@agents-tech-lead** has been assigned to review this PR.

**Review Issue:** #XXXX  
**Tech Lead:** 🔍 @agents-tech-lead  
**Specialization:** Tech Lead Review

### What happens next:

1. ✅ **@agents-tech-lead** will review the PR changes
2. 💬 **@agents-tech-lead** will provide feedback and suggestions
3. ✅ **@agents-tech-lead** will approve or request changes
4. 📝 **@agents-tech-lead** will update issue #XXXX when complete

**Timeline:** Review typically starts within a few minutes

---
*🤖 Automated tech lead review request - @agents-tech-lead will review this*
*Created review issue #XXXX*
```

## Tech Lead Agents

The system supports multiple tech lead agents:

- **@workflows-tech-lead** - GitHub Actions and workflows
- **@agents-tech-lead** - Agent system and definitions
- **@docs-tech-lead** - Documentation and markdown files
- **@github-pages-tech-lead** - GitHub Pages web content

Each tech lead agent is identified by labels:
- `tech-lead:workflows-tech-lead`
- `tech-lead:agents-tech-lead`
- `tech-lead:docs-tech-lead`
- `tech-lead:github-pages-tech-lead`

## Workflow Trigger

The workflow runs on a schedule:

```yaml
on:
  schedule:
    - cron: '*/7 * * * *'  # Every 7 minutes
```

It processes all open PRs with:
- `tech-lead-changes-requested` label (reactive feedback)
- `tech-lead:*` labels (proactive review)

## Benefits

1. **No PRs left behind**: Tech leads automatically review PRs in their domain
2. **Proactive oversight**: Reviews happen before problems accumulate
3. **Clear ownership**: Tech lead agent explicitly assigned via issue
4. **Audit trail**: All reviews tracked through GitHub issues
5. **Autonomous operation**: Runs on schedule without manual intervention

## Implementation Details

**File:** `.github/workflows/copilot-pr-assignment.yml`

**Key Lines:**
- 213-256: Detection and proactive review body creation
- 260-266: Review type detection
- 268-290: Conditional agent selection
- 291-310: Conditional issue title and labels
- 316-396: Conditional issue body templates
- 405-430: Issue creation with appropriate labels
- 432-467: Conditional PR comments

**Validation:**
- YAML syntax: ✅ Validated with actionlint
- Bash syntax: ✅ Tested with bash interpreter
- Indentation: ✅ Proper YAML block scalar formatting

## Testing

To test the proactive review system:

1. Create a PR
2. Add a `tech-lead:agents-tech-lead` label
3. Wait for workflow to run (max 7 minutes)
4. Check for created issue with `tech-lead-review` label
5. Verify Copilot is assigned to the issue
6. Observe tech lead agent reviewing the PR

## Related Files

- Workflow: `.github/workflows/copilot-pr-assignment.yml`
- Agent matching: `tools/match-issue-to-agent.py`
- Agent assignment: `tools/assign-copilot-to-issue.sh`
- Agent definitions: `.github/agents/*.md`
