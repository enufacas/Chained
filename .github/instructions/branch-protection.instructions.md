---
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/*.yml"
  - "**/*.yml"
  - "**/*.yaml"
---

# Branch Protection and PR-Based Workflow Rules

## 🛡️ Primary Rule: Main Branch is Protected

**CRITICAL**: The `main` branch is protected. ALL changes to the repository MUST go through pull requests. Direct pushes to `main` are not allowed.

## Workflow Requirements

### 1. **NEVER Push Directly to Main**

When workflows need to make changes to the repository:

❌ **FORBIDDEN:**
```yaml
- name: Commit changes
  run: |
    git add .
    git commit -m "Update files"
    git push  # This pushes to current branch, which might be main!
```

❌ **FORBIDDEN:**
```yaml
- name: Push to main
  run: |
    git push origin main  # Direct push to main is not allowed!
```

✅ **REQUIRED:**
```yaml
- name: Create PR with changes
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Create unique branch name
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    BRANCH_NAME="automated-update/${TIMESTAMP}-${{ github.run_id }}"
    
    # Checkout new branch
    git checkout -b "$BRANCH_NAME"
    
    # Commit changes
    git add .
    git commit -m "Update files"
    
    # Push to new branch (NOT main)
    git push origin "$BRANCH_NAME"
    
    # Create pull request
    gh pr create \
      --title "Automated update - $(date +%Y-%m-%d)" \
      --body "Description of changes" \
      --label "automated" \
      --base main \
      --head "$BRANCH_NAME"
```

### 2. **Proper Branch Naming**

When creating branches for automated changes:

✅ **Good branch names:**
- `automated-update/YYYYMMDD-HHMMSS-{run_id}`
- `agent-data-sync/YYYYMMDD-HHMMSS-{run_id}`
- `workflow-update/YYYYMMDD-HHMMSS-{run_id}`
- `{workflow-name}/YYYYMMDD-HHMMSS-{run_id}`

❌ **Avoid:**
- Generic names like `update` or `fix`
- Branch names without timestamps (causes conflicts)
- Reusing branch names across runs

### 3. **PR Creation Best Practices**

Every automated PR should:

```yaml
gh pr create \
  --title "Clear, descriptive title - $(date +%Y-%m-%d)" \
  --body "## Purpose"$'\n\n'"Detailed description"$'\n\n'"### Changes"$'\n'"- Change 1"$'\n'"- Change 2"$'\n\n'"---"$'\n'"*🤖 Automated workflow*" \
  --label "automated,copilot" \
  --base main \
  --head "$BRANCH_NAME"
```

Required elements:
- **Title**: Descriptive with date
- **Body**: Explanation of changes with markdown formatting
- **Labels**: Include "automated" label at minimum
- **Base**: Always `main`
- **Head**: The newly created branch

### 4. **Agent Attribution in PRs**

When an agent creates a PR through a workflow:

```yaml
gh pr create \
  --title "feat: implement feature (@agent-name)" \
  --body "**@agent-name** has implemented..."$'\n\n'"Following the agent-name specialization..." \
  --label "automated,agent:agent-name" \
  --base main \
  --head "$BRANCH_NAME"
```

**Required:**
- Mention `@agent-name` in PR title or body
- Include `agent:agent-name` label
- Reference agent's work in the PR description

### 5. **Handling No Changes Scenario**

Always check if there are actual changes before creating a PR:

```yaml
- name: Check for changes
  run: |
    git add .
    if git diff --staged --quiet; then
      echo "No changes to commit"
      exit 0
    else
      echo "Changes detected, proceeding with PR creation"
      # ... PR creation logic
    fi
```

## Common Workflow Patterns

### Pattern 1: Data Sync Workflow

```yaml
jobs:
  sync-data:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Configure git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
      
      - name: Make changes
        run: |
          # Your data sync logic here
          cp source.json destination.json
      
      - name: Create PR
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git add .
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            TIMESTAMP=$(date +%Y%m%d-%H%M%S)
            BRANCH_NAME="data-sync/${TIMESTAMP}-${{ github.run_id }}"
            git checkout -b "$BRANCH_NAME"
            git commit -m "Sync data"
            git push origin "$BRANCH_NAME"
            
            gh pr create \
              --title "Data sync - $(date +%Y-%m-%d)" \
              --body "Automated data synchronization" \
              --label "automated" \
              --base main \
              --head "$BRANCH_NAME"
          fi
```

### Pattern 2: Agent Work Workflow

```yaml
jobs:
  agent-work:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Configure git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
      
      - name: Agent performs work
        run: |
          # Agent work logic
          echo "Agent makes changes"
      
      - name: Create PR with agent attribution
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          AGENT_NAME="create-guru"  # Set appropriately
          git add .
          if ! git diff --staged --quiet; then
            TIMESTAMP=$(date +%Y%m%d-%H%M%S)
            BRANCH_NAME="agent-${AGENT_NAME}/${TIMESTAMP}-${{ github.run_id }}"
            git checkout -b "$BRANCH_NAME"
            git commit -m "Work by @${AGENT_NAME}"
            git push origin "$BRANCH_NAME"
            
            gh pr create \
              --title "feat: agent work (@${AGENT_NAME})" \
              --body "**@${AGENT_NAME}** has completed the assigned work." \
              --label "automated,agent:${AGENT_NAME}" \
              --base main \
              --head "$BRANCH_NAME"
          fi
```

## Migration Guide

### For Existing Workflows That Push to Main

If you find a workflow with:
```yaml
git push
```

Replace with:
```yaml
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BRANCH_NAME="workflow-name/${TIMESTAMP}-${{ github.run_id }}"
git checkout -b "$BRANCH_NAME"
git push origin "$BRANCH_NAME"

gh pr create \
  --title "Workflow update" \
  --body "Changes from workflow" \
  --label "automated" \
  --base main \
  --head "$BRANCH_NAME"
```

### Workflows Currently Needing Updates

The following workflows were identified as pushing directly to main:

1. `.github/workflows/code-archaeologist.yml`
2. `.github/workflows/goal-progress-checker.yml`
3. `.github/workflows/repetition-detector.yml`
4. `.github/workflows/system-kickoff.yml`

These should be updated to follow the PR-based pattern.

## Rationale

### Why PR-Based Workflow?

1. **Code Review**: All changes can be reviewed before merging
2. **CI/CD Validation**: PRs trigger test suites and checks
3. **Audit Trail**: Complete history of all automated changes
4. **Rollback**: Easy to revert via PR revert
5. **Collaboration**: Team members can comment on automated changes
6. **Quality Control**: Automated reviews can catch issues
7. **Branch Protection**: Enforces repository security policies

### Why Not Direct Push?

1. **Bypasses Protection**: Direct pushes skip branch protection rules
2. **No Review**: Changes merge without any validation
3. **Risk**: Automated errors can break the main branch
4. **No Tests**: CI/CD checks don't run on direct pushes
5. **Poor Visibility**: Changes happen silently without notification

## Enforcement

This rule is enforced through:
1. **GitHub Branch Protection**: Technical enforcement at repository level
2. **Code Review**: Copilot code review flags direct pushes
3. **Path-Specific Instructions**: This file guides Copilot to suggest PR-based patterns
4. **Workflow Validation**: Automated checks can validate workflow patterns

## Exceptions

**There are NO exceptions.** Even for:
- ❌ Emergency fixes (create PR, mark urgent, auto-merge if needed)
- ❌ Documentation updates (still need PR)
- ❌ Automated agents (must use PR workflow)
- ❌ Data syncs (use PR-based pattern)

If immediate merge is critical:
1. Create PR
2. Label as `urgent` or `auto-merge`
3. Let auto-review-merge workflow handle it
4. Still maintains audit trail and allows for review

## Testing

Before committing workflow changes:

```bash
# Check for direct pushes to main
grep -n "git push" .github/workflows/*.yml

# Look for problematic patterns
grep -n "git push origin main" .github/workflows/*.yml
```

## Summary

**Remember:**
- ✅ Always create a new branch
- ✅ Always create a PR
- ✅ Always target `main` as base
- ✅ Always include descriptive title and body
- ✅ Always add appropriate labels
- ❌ Never push directly to main
- ❌ Never use `git push` without specifying a branch name
- ❌ Never bypass PR process

---

*🛡️ Protecting the main branch ensures code quality and enables collaborative development - **@create-guru***
