---
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/*.yml"
  - "tools/**/*.py"
  - "tools/**/*.sh"
---

# Agent Issue Update Requirements

## MANDATORY: Comment on Issue Before Removing WIP

When an agent works on an issue, the agent **MUST post a progress update comment to the issue BEFORE removing WIP status from the PR.**

### Required Timing
1. **When work is complete** (before removing WIP)
2. **When encountering blockers** (before requesting help)
3. **When ready for review** (before marking PR ready)

### Comment Pattern
```yaml
- name: Update issue with completion
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh issue comment ${{ github.event.issue.number }} --body \
      "## ✅ Work Complete - @agent-name"$'\n\n'\
      "**@agent-name** has completed the work."$'\n\n'\
      "### Accomplished:"$'\n'\
      "- ✅ Feature X"$'\n'\
      "- ✅ Tests added"$'\n\n'\
      "PR #$PR_NUMBER is ready for review."
```

### Required Content
1. **Agent Attribution**: `@agent-name` mention
2. **Status**: Clear completion indicator
3. **Accomplishments**: Bulleted list of work done
4. **PR Link**: Reference to the PR

### Workflow Order
```yaml
1. Create Draft PR (WIP)
2. Perform work
3. Update issue with completion  # REQUIRED BEFORE NEXT STEP
4. Mark PR ready for review
```

### Why This Matters
- **Transparency**: Stakeholders know when work is done
- **Communication**: Clear progress updates
- **Accountability**: Agent work is documented
- **Process**: Proper workflow sequence
