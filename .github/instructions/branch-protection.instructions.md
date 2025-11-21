---
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/*.yml"
  - "**/*.yml"
  - "**/*.yaml"
---

# Branch Protection: PR-Based Workflow

## CRITICAL: Main Branch is Protected

**ALL changes MUST go through pull requests. Direct pushes to `main` are not allowed.**

### Required Pattern

❌ **FORBIDDEN:**
```yaml
git push  # Direct push to main
git push origin main  # Explicit push to main
```

✅ **REQUIRED:**
```yaml
- name: Create PR with changes
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    BRANCH_NAME="automated-update/${TIMESTAMP}-${{ github.run_id }}"
    
    git checkout -b "$BRANCH_NAME"
    git add .
    git commit -m "Update files"
    git push origin "$BRANCH_NAME"
    
    gh pr create \
      --title "Automated update - $(date +%Y-%m-%d)" \
      --body "Description of changes" \
      --label "automated" \
      --base main \
      --head "$BRANCH_NAME"
```

### Branch Naming
- Use: `{workflow-name}/YYYYMMDD-HHMMSS-{run_id}`
- Include timestamp to prevent conflicts
- Never reuse branch names

### Check for Changes
Always verify changes exist before creating PR:
```yaml
git add .
if git diff --staged --quiet; then
  echo "No changes to commit"
  exit 0
fi
```

### Agent Attribution
When agent creates PR, include:
- `@agent-name` in title or body
- Label: `agent:agent-name`

### Why This Matters
- **Code Review**: Changes reviewed before merging
- **CI/CD**: Tests run on all changes
- **Audit Trail**: Complete history
- **Rollback**: Easy to revert via PR

## NO EXCEPTIONS
Even for emergency fixes, documentation updates, or data syncs - always use PRs.
