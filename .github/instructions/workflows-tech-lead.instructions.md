---
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/*.yml"
  - ".github/actions/**"
---

# Workflows Tech Lead Instructions

## Overview

**@workflows-tech-lead** is responsible for all GitHub Actions workflows and automation in the `.github/workflows/` and `.github/actions/` directories.

## When to Consult Workflows Tech Lead

You should consult **@workflows-tech-lead** when:
- Modifying any workflow files
- Adding new GitHub Actions workflows
- Debugging workflow failures
- Optimizing CI/CD pipeline performance
- Implementing new automation patterns

## Key Responsibilities

**@workflows-tech-lead** ensures:

1. **Security**: Proper permission scoping, secret management, action version pinning
2. **Reliability**: Error handling, retries, concurrency controls
3. **Best Practices**: Following GitHub Actions conventions and patterns
4. **Performance**: Efficient workflow execution and resource usage
5. **Maintainability**: Clear documentation and modular design

## Review Focus Areas

When working in workflow files, **@workflows-tech-lead** reviews:

### Security
- Actions pinned to specific SHA (not tags)
- Minimal required permissions granted
- No secrets exposed in logs
- Input validation for workflow_dispatch
- No command injection vulnerabilities

### Reliability
- Proper error handling and retries
- Concurrency controls to prevent races
- Timeout values set appropriately
- Idempotent operations
- Graceful degradation

### Best Practices
- Clear workflow naming and documentation
- Reusable actions for common patterns
- Appropriate triggers (avoid over-triggering)
- Caching for dependencies
- Clean job names and step descriptions

## Common Anti-Patterns to Avoid

❌ **Don't:**
- Hardcode values that should be variables
- Skip error handling
- Use overly broad permissions
- Allow uncontrolled concurrent runs
- Put expensive operations in scheduled workflows

✅ **Do:**
- Use environment variables and secrets properly
- Handle errors and provide meaningful messages
- Grant minimal necessary permissions
- Use concurrency controls where appropriate
- Optimize for cost and performance

## Workflow Best Practices

### Action Version Pinning
```yaml
# ✅ Good - pinned to SHA
- uses: actions/checkout@a81bbbf8298c0fa03ea29cdc473d45769f953675  # v3.0.0

# ❌ Bad - uses tag which can be moved
- uses: actions/checkout@v3
```

### Permission Scoping
```yaml
# ✅ Good - minimal permissions
permissions:
  contents: read
  pull-requests: write

# ❌ Bad - overly broad
permissions: write-all
```

### Error Handling
```yaml
# ✅ Good - handles errors
- name: Run tests
  run: |
    set -e
    npm test || {
      echo "Tests failed"
      exit 1
    }

# ❌ Bad - no error handling
- name: Run tests
  run: npm test
```

## Getting Help

If you're unsure about:
- Workflow security implications
- Best practices for a specific use case
- Debugging a complex workflow failure
- Performance optimization strategies

Mention **@workflows-tech-lead** in your PR or issue for guidance.

## Protected Status

**@workflows-tech-lead** is a protected agent that cannot be eliminated through standard performance evaluation. This ensures consistent workflow oversight and system reliability.

---

*These instructions apply to all files in `.github/workflows/` and `.github/actions/` to ensure **@workflows-tech-lead** maintains high standards for our automation infrastructure.*
