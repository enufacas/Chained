---
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/*.yml"
  - ".github/workflows/copilot-*.yml"
  - ".github/workflows/*-agent-*.yml"
  - ".github/workflows/agent-*.yml"
  - "tools/**/*.py"
  - "tools/**/*.sh"
---

# Agent Issue Update Requirements

## 📢 Primary Rule: Communicate Progress to Issues

**MANDATORY**: When an agent (custom or Copilot) is working on an issue, the agent MUST post a progress update comment to the issue BEFORE taking the pull request out of WIP (Work In Progress) status.

## Core Requirements

### 1. **Issue Update Timing**

Agents must comment on the issue at these critical points:

1. **When work is complete** (before removing WIP)
2. **When encountering blockers** (before requesting help)
3. **When work is ready for review** (before marking PR ready)

✅ **REQUIRED Pattern:**
```yaml
- name: Update issue with completion status
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    ISSUE_NUMBER="${{ github.event.issue.number }}"
    
    gh issue comment "$ISSUE_NUMBER" --body \
      "## ✅ Work Complete - @agent-name"$'\n\n'\
      "**@agent-name** has completed the work on this issue."$'\n\n'\
      "### What was accomplished:"$'\n'\
      "- ✅ Implemented feature X"$'\n'\
      "- ✅ Added tests for Y"$'\n'\
      "- ✅ Updated documentation"$'\n\n'\
      "### Pull Request"$'\n'\
      "PR #$PR_NUMBER is ready for review and has been taken out of WIP status."$'\n\n'\
      "---"$'\n'\
      "*🤖 Automated update by **@agent-name***"
```

### 2. **Comment Content Requirements**

Every issue update comment MUST include:

1. **Agent Attribution**: `@agent-name` mention
2. **Status**: Clear indication of completion/progress
3. **Accomplishments**: Bulleted list of what was done
4. **Next Steps**: What happens next (PR ready, needs review, etc.)
5. **PR Link**: Reference to the associated pull request

### 3. **WIP Status Management**

Workflow pattern for managing WIP status:

```yaml
- name: Create Draft PR
  id: create_pr
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Create PR as draft (WIP)
    PR_URL=$(gh pr create \
      --title "WIP: feat: work in progress (@agent-name)" \
      --body "**@agent-name** is working on this..." \
      --label "automated,WIP,agent:agent-name" \
      --draft \
      --base main \
      --head "$BRANCH_NAME")
    
    PR_NUMBER=$(echo "$PR_URL" | grep -oP '\d+$')
    echo "pr_number=$PR_NUMBER" >> $GITHUB_OUTPUT

- name: Do the work
  run: |
    # Agent performs work here
    echo "Working..."

- name: Update issue with completion
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # REQUIRED: Update issue before removing WIP
    gh issue comment ${{ github.event.issue.number }} --body \
      "✅ **@agent-name** has completed the work!"$'\n\n'\
      "PR #${{ steps.create_pr.outputs.pr_number }} is ready for review."

- name: Mark PR ready for review
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Only AFTER issue update, remove WIP and mark ready
    gh pr ready ${{ steps.create_pr.outputs.pr_number }}
    gh pr edit ${{ steps.create_pr.outputs.pr_number }} \
      --title "feat: completed work (@agent-name)" \
      --remove-label "WIP"
```

### 4. **Progress Update Template**

Standard template for issue updates:

```markdown
## 🎯 Progress Update - @agent-name

**@agent-name** reporting on work for this issue.

### ✅ Completed
- [x] Task 1 description
- [x] Task 2 description
- [x] Task 3 description

### 🔧 Implementation Details
Brief description of the approach taken and key changes made.

### 📝 Pull Request
- **PR Number**: #123
- **Status**: Ready for review
- **Link**: [View PR](link)

### 🧪 Testing
Description of tests added or validation performed.

### 📚 Documentation
Any documentation updates or notes.

### ⏭️ Next Steps
This PR is now ready for review and out of WIP status.

---
*🤖 Automated progress update by **@agent-name***
```

## Implementation Patterns

### Pattern 1: Copilot Workflow with Issue Update

```yaml
name: Copilot Work on Issue

on:
  issues:
    types: [assigned, labeled]

jobs:
  copilot-work:
    if: github.event.assignee.login == 'copilot'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Extract agent from issue
        id: agent
        run: |
          # Extract assigned agent from issue body
          AGENT=$(echo "${{ github.event.issue.body }}" | grep -oP '@\K[a-z-]+(?=\*\*)' | head -1)
          echo "agent_name=$AGENT" >> $GITHUB_OUTPUT
      
      - name: Copilot performs work
        run: |
          # Copilot coding agent work here
          echo "Working as @${{ steps.agent.outputs.agent_name }}"
      
      - name: Create PR branch
        run: |
          TIMESTAMP=$(date +%Y%m%d-%H%M%S)
          BRANCH_NAME="copilot-work/${TIMESTAMP}-${{ github.run_id }}"
          git checkout -b "$BRANCH_NAME"
          # ... commit and push
      
      - name: Create draft PR
        id: pr
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          PR_URL=$(gh pr create --draft ...)
          PR_NUMBER=$(echo "$PR_URL" | grep -oP '\d+$')
          echo "number=$PR_NUMBER" >> $GITHUB_OUTPUT
      
      # CRITICAL: Update issue before removing WIP
      - name: Update issue with completion
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue comment ${{ github.event.issue.number }} --body \
            "## ✅ Work Complete - @${{ steps.agent.outputs.agent_name }}"$'\n\n'\
            "**@${{ steps.agent.outputs.agent_name }}** has completed the work!"$'\n\n'\
            "### Accomplishments:"$'\n'\
            "- ✅ Implemented requested changes"$'\n'\
            "- ✅ Added tests"$'\n'\
            "- ✅ Updated docs"$'\n\n'\
            "PR #${{ steps.pr.outputs.number }} is now ready for review."
      
      # ONLY AFTER issue update
      - name: Mark PR ready
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr ready ${{ steps.pr.outputs.number }}
```

### Pattern 2: Agent Direct Work

```yaml
name: Agent Work Flow

on:
  workflow_dispatch:
    inputs:
      issue_number:
        required: true
      agent_name:
        required: true

jobs:
  agent-work:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Agent work
        run: |
          echo "Agent ${{ inputs.agent_name }} working on issue ${{ inputs.issue_number }}"
          # ... work happens here
      
      - name: Post completion to issue
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # REQUIRED: Update issue
          gh issue comment ${{ inputs.issue_number }} --body \
            "**@${{ inputs.agent_name }}** has finished the assigned work."$'\n\n'\
            "Details of changes made..."$'\n\n'\
            "PR is ready for review."
```

### Pattern 3: Progressive Updates

For long-running work, provide multiple updates:

```yaml
- name: Update issue - Starting work
  run: |
    gh issue comment $ISSUE_NUMBER --body \
      "🏁 **@agent-name** is starting work on this issue..."

# ... work steps ...

- name: Update issue - Midpoint progress
  run: |
    gh issue comment $ISSUE_NUMBER --body \
      "⚙️ **@agent-name** progress update:"$'\n'\
      "- Completed step 1"$'\n'\
      "- Working on step 2..."

# ... more work ...

- name: Update issue - Completion
  run: |
    gh issue comment $ISSUE_NUMBER --body \
      "✅ **@agent-name** has completed all work!"
```

## Comment Formatting Best Practices

### Use Markdown Effectively

✅ **Good formatting:**
```markdown
## ✅ Work Complete - @agent-name

**@agent-name** has finished the work!

### Accomplishments
- ✅ Item 1
- ✅ Item 2

### PR Link
- PR #123 is ready

---
*🤖 Update by **@agent-name***
```

❌ **Poor formatting:**
```markdown
@agent-name done. See PR 123.
```

### Include Relevant Details

**What to include:**
- Specific tasks completed
- Tests added
- Documentation updated
- Any issues encountered
- Next steps

**What to avoid:**
- Vague statements like "work done"
- Missing agent attribution
- No PR reference
- Technical jargon without context

## Integration with PR Workflow

### Timeline

```
1. Issue created/assigned
2. Agent starts work → Optional: Post "starting work" comment
3. Agent creates draft PR (WIP status)
4. Agent completes work
5. Agent posts completion comment to issue ← REQUIRED
6. Agent marks PR ready (removes WIP) ← Only after step 5
7. PR gets reviewed and merged
8. Issue auto-closes via PR
```

### Linking PRs to Issues

In PR body, link to issue:
```markdown
Closes #123

**@agent-name** has completed the work requested in #123.
```

In issue comment, link to PR:
```markdown
✅ Work complete! See PR #456 for the implementation.
```

## Why This Rule Exists

### Transparency
- Stakeholders can track progress in the issue thread
- Full conversation history in one place
- Clear communication of what was done

### Collaboration
- Team members can see updates without checking PR
- Allows for issue-level discussion even during PR review
- Keeps context where it started (the issue)

### Audit Trail
- Complete record of work from request to completion
- Agent accountability and attribution
- Historical reference for future work

### User Experience
- Issue authors get notified of progress
- Don't need to hunt for PR status
- Clear closure when work is complete

## Enforcement

This rule is enforced through:

1. **Workflow Design**: Workflows must include issue update step
2. **Code Review**: Copilot flags missing issue updates
3. **Path-Specific Instructions**: This file guides proper patterns
4. **Agent Training**: Custom agents learn to communicate progress

## Common Mistakes to Avoid

❌ **Mistake 1: Marking PR ready without issue update**
```yaml
- name: Mark PR ready
  run: gh pr ready $PR_NUMBER  # No issue update!
```

✅ **Correct:**
```yaml
- name: Update issue
  run: gh issue comment $ISSUE_NUMBER --body "Work done!"
- name: Mark PR ready
  run: gh pr ready $PR_NUMBER
```

---

❌ **Mistake 2: Generic comment without agent attribution**
```yaml
gh issue comment $NUM --body "Work complete"  # Who did this?
```

✅ **Correct:**
```yaml
gh issue comment $NUM --body "**@agent-name** has completed the work"
```

---

❌ **Mistake 3: No PR reference in issue comment**
```yaml
gh issue comment $NUM --body "@agent finished"  # Which PR?
```

✅ **Correct:**
```yaml
gh issue comment $NUM --body "@agent finished. See PR #$PR_NUM"
```

## Testing

Before submitting workflow changes:

```bash
# Verify issue update is present before pr ready
grep -A 10 "gh pr ready" .github/workflows/your-workflow.yml | grep -B 5 "gh issue comment"

# Check that issue number is available
grep "issue.number" .github/workflows/your-workflow.yml
```

## Summary

**Key Requirements:**
- ✅ Always post issue update when work is complete
- ✅ Always include @agent-name attribution
- ✅ Always reference the PR number
- ✅ Always update BEFORE removing WIP status
- ✅ Use clear, formatted markdown
- ❌ Never mark PR ready without issue update
- ❌ Never use generic comments without agent name
- ❌ Never skip this step for any reason

**Remember**: Issue updates are not optional—they're a critical part of transparent, accountable agent work.

---

*📢 Keeping everyone informed ensures the autonomous system stays transparent and trustworthy - **@create-guru***
