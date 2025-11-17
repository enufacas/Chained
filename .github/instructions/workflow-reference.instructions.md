---
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/*.yml"
---

# Workflow Reference Attribution in Issues and PRs

## MANDATORY RULE: Reference Workflow Name in Created Issues and PRs

**@troubleshoot-expert** requires that when workflows create issues or PRs, they MUST include a clear reference to the workflow that created them.

### Primary Directive

Any workflow that uses `gh issue create` or `gh pr create` MUST include a reference to the workflow name in the issue or PR body.

### Why This Matters

1. **Traceability**: Easy to identify which workflow created an issue/PR
2. **Debugging**: Simplifies troubleshooting when issues arise
3. **Audit Trail**: Provides clear provenance for all automated content
4. **Transparency**: Users can see the source of automated work
5. **Accountability**: Workflows are responsible for their outputs

## Implementation Requirements

### For Issue Creation

When using `gh issue create`, the issue body MUST include:

1. **At the end of the body**: A footer line referencing the workflow
2. **Format**: `*🤖 Created by workflow: [workflow-name]*`
3. **Placement**: As the last line or in a footer section

#### ✅ CORRECT Example - Issue Creation

```yaml
- name: Create issue
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh issue create \
      --title "Example Issue Title" \
      --body "## Issue Description

    This is the main content of the issue.

    ### Details

    Additional details here.

    ---

    *🤖 Created by workflow: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})*" \
      --label "automated"
```

**Key elements:**
- Uses `${{ github.workflow }}` to get workflow name
- Includes a link to the workflow run using `${{ github.run_id }}`
- Placed at the end after a separator line (`---`)
- Clearly marked with 🤖 emoji for visibility

### For PR Creation

When using `gh pr create`, the PR body MUST include:

1. **At the end of the body**: A footer line referencing the workflow
2. **Format**: `*🤖 Created by workflow: [workflow-name]*`
3. **Placement**: As the last line or in a footer section

#### ✅ CORRECT Example - PR Creation

```yaml
- name: Create pull request
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh pr create \
      --title "Example PR Title" \
      --body "## Changes

    This PR makes the following changes:
    - Change 1
    - Change 2

    ### Testing

    Tests added for all changes.

    ---

    *🤖 Created by workflow: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})*" \
      --label "automated" \
      --base main \
      --head "$BRANCH_NAME"
```

### Alternative Formats (Also Acceptable)

#### Format 1: Inline with Existing Footer

If the workflow already has a footer message, append the workflow reference:

```yaml
--body "## Summary

Content here

---

*🤖 Automated sync workflow*
*Created by: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})*"
```

#### Format 2: Metadata Section

Include in a metadata or context section:

```yaml
--body "## Summary

Content here

### 📋 Metadata

- **Workflow**: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
- **Run ID**: ${{ github.run_id }}
- **Triggered**: $(date -u +'%Y-%m-%d %H:%M:%S UTC')

---

*🤖 Automated*"
```

#### Format 3: Simple Text Reference

Minimal reference without link (less preferred but acceptable):

```yaml
--body "## Summary

Content here

---

*Created by workflow: ${{ github.workflow }}*"
```

## Available GitHub Context Variables

Use these variables to reference workflow information:

| Variable | Description | Example |
|----------|-------------|---------|
| `${{ github.workflow }}` | Workflow name | `"Agent Data Sync"` |
| `${{ github.run_id }}` | Unique run identifier | `12345678` |
| `${{ github.run_number }}` | Run number for this workflow | `42` |
| `${{ github.server_url }}` | GitHub server URL | `https://github.com` |
| `${{ github.repository }}` | Repository name | `owner/repo` |

### Building a Workflow Run Link

Complete URL to the workflow run:

```
${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

Example: `https://github.com/enufacas/Chained/actions/runs/12345678`

## Examples from Existing Workflows

### Good Example: agent-data-sync.yml

```yaml
gh pr create \
  --title "📊 Sync agent data to GitHub Pages - ${PR_DATE}" \
  --body "## Agent Data Sync

This PR syncs agent registry data.

### Changes
- Updated data files

---

*🤖 Automated data sync workflow*" \
  --label "automated"
```

**Improvement needed**: Add specific workflow name and link:

```yaml
--body "## Agent Data Sync

This PR syncs agent registry data.

### Changes
- Updated data files

---

*🤖 Created by workflow: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})*"
```

## ❌ INCORRECT Examples

### Missing Workflow Reference

```yaml
gh issue create \
  --title "Issue Title" \
  --body "Issue description here." \
  --label "automated"
```

**Problem**: No reference to which workflow created this issue.

### Generic Reference Only

```yaml
gh pr create \
  --title "PR Title" \
  --body "PR description

---

*Automated*" \
  --label "automated"
```

**Problem**: Says it's automated but doesn't specify which workflow.

### Incomplete Reference

```yaml
gh issue create \
  --title "Issue Title" \
  --body "Issue description

Created by GitHub Actions" \
  --label "automated"
```

**Problem**: Too vague - which specific workflow created this?

## Multi-line Body Construction

When building complex issue/PR bodies, use heredoc or multi-line string construction:

### Method 1: Heredoc (Recommended)

```yaml
- name: Create issue with heredoc
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    WORKFLOW_LINK="${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
    
    gh issue create \
      --title "Issue Title" \
      --body "$(cat <<EOF
    ## Issue Description
    
    Content here.
    
    ### Details
    
    More content.
    
    ---
    
    *🤖 Created by workflow: [${{ github.workflow }}](${WORKFLOW_LINK})*
    EOF
    )" \
      --label "automated"
```

### Method 2: Body File

```yaml
- name: Create issue body file
  run: |
    WORKFLOW_LINK="${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
    
    cat > /tmp/issue_body.md <<EOF
    ## Issue Description
    
    Content here.
    
    ---
    
    *🤖 Created by workflow: [${{ github.workflow }}](${WORKFLOW_LINK})*
    EOF

- name: Create issue
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh issue create \
      --title "Issue Title" \
      --body-file /tmp/issue_body.md \
      --label "automated"
```

## Testing and Validation

Before committing workflow changes:

### Checklist
- [ ] Workflow reference is included in issue/PR body
- [ ] Reference uses `${{ github.workflow }}` or similar
- [ ] Link to workflow run is provided (if possible)
- [ ] Reference is clearly visible (end of body, footer section)
- [ ] Format is consistent with examples
- [ ] Emoji (🤖) or marker is present for easy identification

### Manual Verification

After workflow runs:
1. Check created issue/PR
2. Scroll to bottom of description
3. Verify workflow name and link are present
4. Click link to confirm it points to correct run

## Migration Guide

### For Existing Workflows

If you're updating an existing workflow that creates issues/PRs:

1. **Locate the creation command**: Find `gh issue create` or `gh pr create`
2. **Identify the body parameter**: Usually `--body` or `--body-file`
3. **Add footer section**: Append workflow reference at the end
4. **Test locally**: Create a test issue/PR to verify format
5. **Commit changes**: Update the workflow file

### Quick Migration Script

For simple workflows, add this line to the end of the body:

```bash
--body "...existing content...

---

*🤖 Created by workflow: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})*"
```

## Integration with Agent System

When combining with agent attribution, include both:

```yaml
--body "## Summary

Content by **@agent-name**

---

**Agent**: @agent-name
**Workflow**: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})

*🤖 Automated*"
```

## Enforcement

This rule is enforced through:
1. **Path-specific instructions**: This file guides Copilot
2. **Code review**: Manual review checks for compliance
3. **Documentation**: Clear examples and requirements

## Non-Compliance Consequences

Workflows without proper workflow references result in:
- ❌ Difficult to trace issue/PR origin
- ❌ Harder to debug workflow problems
- ❌ Loss of audit trail
- ❌ Confusion about automation source
- ❌ Reduced transparency in the system

## Summary

**ALWAYS include workflow reference in issues and PRs created by workflows:**

```
*🤖 Created by workflow: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})*
```

This simple line provides:
✅ Workflow name
✅ Link to exact run
✅ Clear visual marker (🤖)
✅ Complete traceability

---

*🤖 Instruction file for **@troubleshoot-expert** - Ensuring workflow attribution and transparency*
