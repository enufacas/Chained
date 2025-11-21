---
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/*.yml"
---

# Workflow Reference Attribution

## MANDATORY: Reference Workflow Name in Created Issues/PRs

Workflows that use `gh issue create` or `gh pr create` **MUST include a reference to the workflow that created them**.

### Format
Add at the end of issue/PR body:
```markdown
---

*🤖 Created by workflow: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})*
```

### Implementation

**Issue Creation:**
```yaml
gh issue create \
  --title "Issue Title" \
  --body "## Content"$'\n\n'"Details here."$'\n\n'"---"$'\n\n'"*🤖 Created by workflow: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})*" \
  --label "automated"
```

**PR Creation:**
```yaml
gh pr create \
  --title "PR Title" \
  --body "## Changes"$'\n\n'"List of changes."$'\n\n'"---"$'\n\n'"*🤖 Created by workflow: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})*" \
  --label "automated"
```

### Why This Matters
- **Traceability**: Easy to identify which workflow created an issue/PR
- **Debugging**: Simplifies troubleshooting
- **Audit Trail**: Clear provenance for all automated content
- **Transparency**: Users see the source

### Available Variables
- `${{ github.workflow }}` - Workflow name
- `${{ github.run_id }}` - Unique run identifier
- `${{ github.server_url }}` - GitHub server URL
- `${{ github.repository }}` - Repository name

### Checklist
- [ ] Workflow reference included in issue/PR body
- [ ] Uses `${{ github.workflow }}` or similar
- [ ] Link to workflow run provided
- [ ] Format is consistent with examples
