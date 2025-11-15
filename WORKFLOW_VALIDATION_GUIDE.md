# Workflow Validation Guide

## 🔍 Overview

This guide explains the workflow validation system that ensures all GitHub Actions workflows in the Chained repository are valid before being merged to main.

## 🎯 Purpose

The workflow validation system prevents:
- YAML syntax errors in workflows
- Workflows that push directly to protected main branch
- Missing required workflow structure
- Common workflow misconfigurations

## 🛠️ How It Works

### Automatic Validation on PRs

When you create or update a PR that modifies workflow files:

1. **Triggers Automatically**: The validation runs on any PR that changes files in `.github/workflows/`
2. **Validates Changed Files**: Only the modified workflows are checked
3. **Reports Results**: A comment is posted to the PR with validation results
4. **Blocks Merge**: If validation fails, the PR check fails and blocks merge

### Validation Checks

The validation script (`tools/validate-workflows.py`) performs these checks:

#### 1. YAML Syntax
- Ensures the workflow is valid YAML
- Catches parsing errors before they break workflows

#### 2. Required Structure
- **name**: Workflow must have a name field
- **on**: Workflow must have trigger configuration
- **jobs**: Workflow must define at least one job

#### 3. Prohibited Patterns

**❌ Direct Push to Main:**
```yaml
# This is PROHIBITED
- name: Push changes
  run: |
    git push  # Pushes to current branch (may be main)
```

```yaml
# This is PROHIBITED
- name: Push to main
  run: |
    git push origin main  # Direct push to protected branch
```

**✅ Correct Pattern (PR-based workflow):**
```yaml
- name: Create PR with changes
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Create unique branch
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    BRANCH_NAME="update/${TIMESTAMP}-${{ github.run_id }}"
    git checkout -b "$BRANCH_NAME"
    
    # Commit and push to new branch
    git add .
    git commit -m "Update files"
    git push origin "$BRANCH_NAME"
    
    # Create PR
    gh pr create \
      --title "Automated update" \
      --body "Description" \
      --label "automated" \
      --base main \
      --head "$BRANCH_NAME"
```

#### 4. PR-Based Workflow Pattern

When a workflow commits and pushes changes, it should:
- Create a new branch (not push to main)
- Use unique branch names (timestamp + run ID)
- Create a PR for the changes
- Allow automated review and merge processes

## 📋 Using the Validation Tool

### Validate All Workflows

```bash
cd /home/runner/work/Chained/Chained
python3 tools/validate-workflows.py --all
```

### Validate Specific Workflow

```bash
python3 tools/validate-workflows.py .github/workflows/my-workflow.yml
```

### Validate Changed Files (for CI)

```bash
# Create file with changed workflow paths
git diff --name-only main HEAD | grep "^\.github/workflows/.*\.yml$" > changed.txt

# Validate only changed files
python3 tools/validate-workflows.py --changed-files changed.txt
```

## 🔧 Fixing Validation Errors

### YAML Syntax Error

**Error:**
```
YAML syntax error in my-workflow.yml: while scanning a simple key
```

**Fix:**
1. Check indentation - all content must be properly indented
2. Ensure heredoc content in bash scripts is indented
3. Use a YAML validator or linter

### Direct Push to Main

**Error:**
```
my-workflow.yml:45: Direct "git push" without branch specification is prohibited.
```

**Fix:**
Replace direct push with PR-based workflow pattern (see example above).

### Missing Required Fields

**Error:**
```
my-workflow.yml: Missing 'on' trigger field
```

**Fix:**
Add the required field to your workflow:
```yaml
name: "My Workflow"

on:
  workflow_dispatch:  # Or other triggers
  
jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Hello"
```

## 🧪 Testing Your Workflow Changes

### Before Creating a PR

```bash
# Validate your changes locally
python3 tools/validate-workflows.py .github/workflows/your-workflow.yml

# Should see:
# ✅ All validations passed!
# Summary: 1 passed, 0 failed
```

### After Creating a PR

1. The validation check runs automatically
2. Check the "Workflow Validation" check in the PR
3. Review any validation errors in the workflow run logs
4. Fix issues and push again - validation re-runs automatically

## 📚 Best Practices

### 1. Always Use PR-Based Workflow Pattern

When your workflow needs to commit changes:
- ✅ Create a new branch
- ✅ Use unique branch names
- ✅ Create a PR
- ❌ Never push directly to main

### 2. Test Locally First

Before pushing:
```bash
# Validate your workflow
python3 tools/validate-workflows.py .github/workflows/my-workflow.yml

# Test YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/my-workflow.yml'))"
```

### 3. Use yamllint for Style

```bash
# Install yamllint
pip install yamllint

# Check style
yamllint .github/workflows/my-workflow.yml
```

### 4. Follow Naming Conventions

**Good workflow names:**
- `workflow-name.yml`
- `category-workflow-name.yml`
- `feature-workflow-name.yml`

**Avoid:**
- Names with spaces
- Overly generic names like `test.yml`
- Names that don't describe the workflow purpose

## 🚨 Common Issues

### Issue: Validation passes locally but fails in CI

**Cause:** Different YAML parser versions or environment

**Solution:**
- Ensure you're using Python 3.11+ (same as CI)
- Check that all files are committed
- Verify file paths are correct

### Issue: Workflow has complex bash scripts

**Tip:** When using heredocs in workflow bash scripts:
- Ensure heredoc content is indented consistently
- Use unique heredoc delimiters (not just `EOF`)
- Test with Python's yaml.safe_load()

### Issue: False positive for git push warning

**Scenario:** Your workflow uses `git push` in documentation or examples

**Solution:**
- If it's in a string or comment, the validator might flag it
- If it's a false positive warning, you can ignore it
- Errors (not warnings) will block merge

## 🔄 Validation Workflow Updates

If you need to update the validation workflow itself:

1. Modify `.github/workflows/workflow-validation.yml`
2. Test it validates correctly:
   ```bash
   python3 tools/validate-workflows.py .github/workflows/workflow-validation.yml
   ```
3. Create a PR - the workflow will validate itself!

## 📖 Related Documentation

- [Branch Protection Rules](.github/instructions/branch-protection.instructions.md)
- [Workflow Health Investigation Reports](WORKFLOW_HEALTH_INVESTIGATION_REPORT.md)
- [Workflow Fixes Summary](WORKFLOW_FIXES_SUMMARY.md)

## 🎯 Summary

The workflow validation system ensures:
- ✅ All workflows have valid YAML syntax
- ✅ Workflows follow required structure
- ✅ No direct pushes to protected main branch
- ✅ PR-based workflow pattern is used
- ✅ Changes are validated before merge

This prevents workflow failures and maintains repository health!

---

*Built by **@create-guru** - Infrastructure for reliable automation*
