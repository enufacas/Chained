---
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/**/*.yaml"
---

# Workflow Linting with actionlint

## MANDATORY: Validate Workflows Before Committing

When creating or modifying GitHub Actions workflow files, **ALWAYS use actionlint** to catch syntax errors and workflow issues before committing.

### What is actionlint?

**actionlint** (https://github.com/rhysd/actionlint) is a static checker for GitHub Actions workflow files that:
- ✅ Validates workflow syntax against GitHub Actions schema
- ✅ Type-checks `${{ }}` expressions
- ✅ Validates action inputs/outputs
- ✅ Checks for script injection vulnerabilities
- ✅ Validates runner labels, cron syntax, glob patterns
- ✅ Integrates shellcheck for `run:` scripts
- ✅ Detects hard-coded credentials

### Installation

```bash
# Install via go
go install github.com/rhysd/actionlint/cmd/actionlint@latest

# Or via Homebrew (macOS/Linux)
brew install actionlint

# Or download pre-built binary
# https://github.com/rhysd/actionlint/releases
```

### Usage Pattern

**Before committing workflow changes:**

```bash
# Lint all workflows
actionlint

# Lint specific workflow file
actionlint .github/workflows/my-workflow.yml

# Lint with shellcheck integration (if shellcheck installed)
actionlint -shellcheck=

# Ignore specific rules (use sparingly)
actionlint -ignore 'SC2086:.*'
```

### Common Issues Caught by actionlint

#### ❌ Wrong Key Names
```yaml
on:
  push:
    branch: main  # Should be "branches"
```

#### ❌ Invalid Runner Labels
```yaml
runs-on: linux-latest  # Should be "ubuntu-latest"
```

#### ❌ Script Injection Vulnerabilities
```yaml
- run: echo "${{ github.event.issue.title }}"  # UNSAFE!
```

✅ **Safe Pattern:**
```yaml
- run: echo "$ISSUE_TITLE"
  env:
    ISSUE_TITLE: ${{ github.event.issue.title }}
```

#### ❌ Incorrect Action Inputs
```yaml
- uses: actions/setup-node@v4
  with:
    node_version: 18.x  # Should be "node-version"
```

#### ❌ Invalid Glob Patterns
```yaml
on:
  push:
    tags:
      - 'v\d+'  # Regex not supported, use glob patterns
```

### Workflow Integration

The repository's `workflow-validation.yml` automatically runs actionlint on PR changes. Ensure it's properly configured:

```yaml
- name: Install actionlint
  run: |
    # Install actionlint
    go install github.com/rhysd/actionlint/cmd/actionlint@latest
    # Add to PATH
    echo "$(go env GOPATH)/bin" >> $GITHUB_PATH

- name: Run actionlint
  run: |
    actionlint .github/workflows/**/*.yml
```

### Best Practices

1. **Run locally first**: Catch issues before pushing
   ```bash
   actionlint
   ```

2. **Fix all errors**: Don't ignore actionlint warnings without good reason

3. **Use shellcheck**: Install shellcheck for better validation of run scripts
   ```bash
   brew install shellcheck  # macOS
   apt-get install shellcheck  # Ubuntu
   ```

4. **Test expressions**: Validate `${{ }}` expressions are type-safe

5. **Validate security**: Pay attention to script injection warnings

### Configuration (Optional)

Create `.github/actionlint.yaml` to customize behavior:

```yaml
# Configure custom runner labels
self-hosted-runner:
  labels:
    - my-custom-runner
    - gpu-runner

# Configure shell to validate (default: bash)
shell: 
  - bash

# Ignore specific rules
ignore:
  - 'SC2086:.*'  # Example: ignore specific shellcheck rule
```

### Checklist for Workflow Changes

Before committing workflow changes:
- [ ] Run `actionlint` locally and fix all errors
- [ ] Test workflow with `workflow_dispatch` if applicable
- [ ] Verify all action versions are pinned
- [ ] Check for script injection vulnerabilities
- [ ] Ensure proper error handling in scripts
- [ ] Validate runner labels are correct

### Why This Matters

- **Catch Errors Early**: Find issues before they cause CI/CD failures
- **Security**: Prevent script injection and credential leaks
- **Type Safety**: Avoid runtime errors in expressions
- **Best Practices**: Learn proper GitHub Actions patterns
- **Time Savings**: Fix issues locally vs debugging in CI

## Resources

- **actionlint GitHub**: https://github.com/rhysd/actionlint
- **Online Playground**: https://rhysd.github.io/actionlint/
- **Workflow Syntax**: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- **Security Hardening**: https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions

---

*Always lint before you commit. Your CI/CD will thank you.*
