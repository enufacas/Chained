---
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/*.yml"
---

# MANDATORY: Validate Workflows Before Committing

## Critical Requirement

**@troubleshoot-expert** requires that ALL workflow changes be validated BEFORE committing to prevent the #1 recurring problem in this repository: invalid workflow syntax.

## Why This Matters

Invalid workflows cause:
1. **Build Failures**: Workflow won't run at all
2. **Silent Failures**: Runtime errors that are hard to debug
3. **Lost Time**: Hours spent troubleshooting preventable issues
4. **System Instability**: Broken automation pipeline

## Validation Tools Available

### 1. Python YAML Validator (ALWAYS USE)

```bash
# Validate specific workflow(s)
python3 tools/validate-workflows.py .github/workflows/your-workflow.yml

# Validate all workflows
python3 tools/validate-workflows.py --all

# Validate changed files only
git diff --name-only main | python3 tools/validate-workflows.py --changed-files /dev/stdin
```

**What it catches:**
- ✅ YAML syntax errors (malformed YAML)
- ✅ Missing required fields (name, on, jobs)
- ✅ Prohibited patterns (direct push to main)
- ✅ PR workflow pattern violations
- ✅ Script dependency path trigger issues

**What it DOESN'T catch:**
- ❌ GitHub expression syntax errors (`${{ }}`)
- ❌ Invalid action references
- ❌ Runtime logic errors

### 2. yamllint (Secondary Check)

```bash
# Check specific workflow
yamllint .github/workflows/your-workflow.yml

# Check all workflows
yamllint .github/workflows/
```

**What it catches:**
- ✅ YAML syntax errors
- ✅ Style issues (trailing spaces, line length)
- ✅ Indentation problems

### 3. actionlint (GitHub-Specific Validation - Recommended)

```bash
# Install actionlint (if not available)
# See: https://github.com/rhysd/actionlint

# Validate specific workflow
actionlint .github/workflows/your-workflow.yml

# Validate all workflows
actionlint
```

**What it catches:**
- ✅ GitHub expression syntax errors
- ✅ Invalid action references
- ✅ Workflow syntax issues specific to GitHub Actions
- ✅ Type mismatches in expressions
- ✅ Shell command issues

## Common YAML Syntax Errors

### 1. Multi-line Strings with `---` Separator

❌ **WRONG - Causes "multiple documents" error:**
```yaml
run: |
  gh pr create \
    --body "Content here
    
    ---
    
    Footer text" \
    --label "automated"
```

✅ **CORRECT - Use bash string concatenation:**
```yaml
run: |
  gh pr create \
    --body "Content here"$'\n\n'"---"$'\n\n'"Footer text" \
    --label "automated"
```

### 2. Unclosed Multi-line Strings

❌ **WRONG - Missing closing quote:**
```yaml
run: |
  gh pr create \
    --body "Line 1
    Line 2
    Line 3" \  # Quote on wrong line!
    --label "automated"
```

✅ **CORRECT - Proper string concatenation:**
```yaml
run: |
  gh pr create \
    --body "Line 1"$'\n'"Line 2"$'\n'"Line 3" \
    --label "automated"
```

### 3. GitHub Expression Syntax Errors

❌ **WRONG - Missing comma between expressions:**
```yaml
run: |
  URL="${{ github.server_url }}/${{ github.repository }}"  # Wrong!
```

✅ **CORRECT - Proper expression syntax:**
```yaml
run: |
  URL="${{ github.server_url }}/${{ github.repository }}"
```

### 4. Special Characters in Strings

❌ **WRONG - Emoji and special characters can cause issues:**
```yaml
run: |
  CONTENT="
  🤖 Created by workflow
  ---
  More text"
  gh pr create --body "$CONTENT"
```

✅ **CORRECT - Use string concatenation:**
```yaml
run: |
  gh pr create \
    --body "Created by workflow"$'\n\n'"---"$'\n\n'"More text"
```

## Pre-Commit Workflow

**ALWAYS follow this process:**

1. **Make your changes** to the workflow file
2. **Validate immediately:**
   ```bash
   python3 tools/validate-workflows.py .github/workflows/your-workflow.yml
   ```
3. **If validation fails:**
   - Read the error message carefully
   - Fix the syntax error
   - Re-validate until it passes
4. **Run yamllint** for additional checks:
   ```bash
   yamllint .github/workflows/your-workflow.yml
   ```
5. **If actionlint is available, run it:**
   ```bash
   actionlint .github/workflows/your-workflow.yml
   ```
6. **Only AFTER validation passes:**
   - Commit your changes
   - Push to your branch

## Automated Validation

The repository has a workflow validation check:
- **File:** `.github/workflows/workflow-validation.yml`
- **Trigger:** On every PR that changes workflows
- **Action:** Validates all changed workflow files

**However**: Don't rely solely on the automated check!
- It runs AFTER you push
- Catching errors locally is faster
- Prevents polluting PR history with broken commits

## Error Messages and Solutions

### "expected a single document in the stream"

**Cause:** YAML parser found `---` inside a string and interpreted it as document separator

**Solution:** Use bash string concatenation instead of multi-line strings:
```bash
--body "Part 1"$'\n\n'"---"$'\n\n'"Part 2"
```

### "could not find expected ':'"

**Cause:** Unclosed string or malformed YAML structure

**Solution:** Check for:
- Unclosed quotes
- Missing colons after keys
- Incorrect indentation
- Special characters in unquoted strings

### "Unexpected symbol: '{{'"

**Cause:** GitHub expression syntax error (not caught by YAML parsers!)

**Solution:**
- Use actionlint to catch these
- Check for matching braces: `${{ }}`
- Ensure proper expression syntax

## Best Practices

### 1. Keep It Simple
- Use bash variables for complex strings
- Break long strings into parts
- Avoid deeply nested structures

### 2. Use Established Patterns
- Look at other workflows for examples
- Copy-paste tested patterns
- Don't reinvent string handling

### 3. Test Locally First
- ALWAYS validate before pushing
- Run in a local environment when possible
- Use dry-run options if available

### 4. Document Complex Logic
- Add comments explaining tricky syntax
- Reference the pattern source
- Note why specific formatting is needed

## Quick Reference

```bash
# Before committing ANY workflow changes:

# 1. Validate with Python tool
python3 tools/validate-workflows.py .github/workflows/your-workflow.yml

# 2. Check with yamllint
yamllint .github/workflows/your-workflow.yml

# 3. If actionlint is installed
actionlint .github/workflows/your-workflow.yml

# 4. All must pass BEFORE you commit!
```

## Emergency Fix Process

If a workflow is broken in main:

1. **Create a hotfix branch immediately**
2. **Fix the syntax error using proper patterns**
3. **Validate the fix:**
   ```bash
   python3 tools/validate-workflows.py .github/workflows/broken-file.yml
   ```
4. **Create PR with validation results in description**
5. **Merge ASAP to restore system functionality**

## Summary

- ✅ ALWAYS validate workflows before committing
- ✅ Use `python3 tools/validate-workflows.py` as primary tool
- ✅ Use bash string concatenation for multi-line PR bodies
- ✅ Avoid `---` and emojis in multi-line strings
- ✅ Test with yamllint for additional checks
- ❌ NEVER commit without validating first
- ❌ NEVER rely solely on post-push checks

**This is not optional** - workflow validation is MANDATORY for all workflow changes.

---

*🔧 Validation instructions from **@troubleshoot-expert** - preventing the #1 recurring issue in this repository*
