# 🔒 Security Best Practices Checklist

## Overview

This document provides a comprehensive security best practices checklist for the Chained autonomous AI development system. It covers multiple security domains and provides actionable guidance for maintaining secure operations.

**Purpose**: To ensure the autonomous AI system operates securely while maintaining its innovative capabilities.

**Audience**: Developers, security reviewers, AI agents, and contributors to the Chained project.

**Related Documents**:
- [Security Implementation](SECURITY_IMPLEMENTATION.md) - Detailed security architecture
- [Security Summary](../SECURITY_SUMMARY.md) - Security scan results
- [Validation Utils](../tools/validation_utils.py) - Input validation library

---

## 📋 Quick Security Assessment

Before deploying changes, verify these critical security controls:

- [ ] All external contributions require manual review (CODEOWNERS configured)
- [ ] Auto-merge restricted to owner and trusted bots with `copilot` label
- [ ] Input validation applied to all user-provided data
- [ ] No secrets hardcoded in code or configuration files
- [ ] File operations protected against path traversal
- [ ] GitHub Actions workflows use minimum required permissions
- [ ] CodeQL security scanning enabled and passing
- [ ] Dependencies regularly updated and scanned

---

## 🔐 1. Authentication & Authorization

### GitHub Actions & Workflows

#### ✅ Do's
- **Use minimal permissions**: Always specify the minimum `permissions` needed for each workflow
  ```yaml
  permissions:
    contents: read      # Only if reading code
    pull-requests: write # Only if managing PRs
  ```
- **Validate PR authors**: Check if the author is authorized before auto-merging
  ```bash
  # Example from auto-review-merge.yml
  is_repo_owner=0
  if [ "${author}" = "${repo_owner}" ]; then
    is_repo_owner=1
  fi
  ```
- **Use trusted bot list**: Maintain explicit list of allowed bot accounts
  ```bash
  # Match exact bot names with regex
  if echo "${author}" | grep -qiE "^(github-actions\[bot\]|dependabot\[bot\]|app/copilot)"; then
    is_trusted_bot=1
  fi
  ```
- **Require labels for automation**: Use labels like `copilot` to indicate approved automation
- **Implement defense in depth**: Use multiple security layers (CODEOWNERS + workflow checks + branch protection)

#### ❌ Don'ts
- **Don't grant broad permissions**: Avoid `permissions: write-all` or unnecessary scopes
- **Don't trust labels alone**: Always verify PR author in addition to labels
- **Don't allow substring matching**: Use exact regex patterns for bot names
- **Don't bypass CODEOWNERS**: Keep owner review requirement for external PRs
- **Don't auto-merge unverified sources**: Explicitly check author identity

### Branch Protection

#### ✅ Recommended Settings
- [x] Require pull request before merging
- [x] Require approvals (1 approval minimum)
- [x] Require review from Code Owners
- [x] Allow auto-merge (for authorized PRs only)
- [x] Automatically delete head branches
- [x] Allow specified actors to bypass (only `github-actions[bot]`)

#### Authorization Matrix

| PR Author | Has `copilot` Label | Auto-Merge? | Reason |
|-----------|-------------------|-------------|---------|
| Repository Owner | ✅ Yes | ✅ YES | Owner with copilot label |
| Repository Owner | ❌ No | ❌ NO | Missing copilot label |
| github-actions[bot] | ✅ Yes | ✅ YES | Trusted bot with copilot label |
| github-actions[bot] | ❌ No | ❌ NO | Missing copilot label |
| dependabot[bot] | ✅ Yes | ✅ YES | Trusted bot with copilot label |
| app/copilot* | ✅ Yes | ✅ YES | Trusted bot with copilot label |
| External User | ✅ Yes | ❌ NO | Not authorized |
| External User | ❌ No | ❌ NO | Not authorized |
| unknown-bot | ✅ Yes | ❌ NO | Not in trusted bot list |

---

## 🛡️ 2. Input Validation & Sanitization

### General Principles

#### ✅ Do's
- **Validate all inputs**: Never trust user-provided data
- **Use validation utilities**: Leverage `tools/validation_utils.py` for common validations
- **Fail securely**: Return generic error messages for security failures
- **Type check inputs**: Verify data types before processing
- **Sanitize before use**: Clean and normalize inputs

#### ❌ Don'ts
- **Don't assume input format**: Always validate before processing
- **Don't expose internal paths**: Use generic error messages
- **Don't skip validation**: Even for "trusted" sources
- **Don't use raw user input**: Sanitize file paths, names, and commands

### Agent Names

```python
# ✅ CORRECT: Validate agent names
from tools.validation_utils import validate_agent_name

try:
    agent_name = validate_agent_name(user_input)
    # Safe to use agent_name
except ValidationError as e:
    print(f"Invalid agent name: {e}")

# ❌ WRONG: Using unvalidated input
agent_file = f".github/agents/{user_input}.md"  # Path traversal risk!
```

#### Requirements
- [x] Only alphanumeric, hyphens, and underscores
- [x] 2-100 characters in length
- [x] No path traversal characters (`../`, `./`)
- [x] No special characters that could affect file systems

### File Paths

```python
# ✅ CORRECT: Validate file paths
from tools.validation_utils import validate_file_path
from pathlib import Path

base_dir = Path(".github/agents")
try:
    safe_path = validate_file_path(user_path, base_dir)
    # safe_path is guaranteed to be within base_dir
except ValidationError as e:
    print(f"Invalid path: {e}")

# ❌ WRONG: Direct path construction
file_path = base_dir / user_input  # Can escape with ../
```

#### Requirements
- [x] Resolve to absolute path
- [x] Verify within allowed directory (when base_dir specified)
- [x] Prevent path traversal attacks
- [x] Check file existence and type before operations

### JSON/YAML Data

```python
# ✅ CORRECT: Validate JSON structure
from tools.validation_utils import validate_json_structure

data = json.loads(user_json)
validate_json_structure(data, required_keys=["name", "description"])
# Safe to access data["name"] and data["description"]

# ❌ WRONG: Assuming structure
name = data["name"]  # May raise KeyError
```

### String Length & Content

```python
# ✅ CORRECT: Validate string length
from tools.validation_utils import validate_string_length, validate_non_empty_string

description = validate_string_length(
    user_input, 
    min_length=10, 
    max_length=500, 
    field_name="description"
)

title = validate_non_empty_string(user_title, field_name="title")

# ❌ WRONG: No validation
description = user_input  # Could be empty or excessively long
```

---

## 🗂️ 3. File System Security

### Safe File Operations

#### ✅ Do's
- **Use Path objects**: Prefer `pathlib.Path` over string manipulation
- **Validate paths**: Always validate before file operations
- **Use safe read/write**: Use `safe_file_read()` and `safe_file_write()` utilities
- **Handle encoding errors**: Specify and handle encoding properly
- **Atomic writes**: Write to temp file first, then move
- **Clean up on error**: Ensure proper cleanup in exception handlers

```python
# ✅ CORRECT: Safe file operations
from tools.validation_utils import safe_file_read, safe_file_write

try:
    content = safe_file_read("path/to/file.txt")
    # Process content
    safe_file_write("path/to/output.txt", processed_content, create_dirs=True)
except ValidationError as e:
    print(f"File operation failed: {e}")
```

#### ❌ Don'ts
- **Don't use string concatenation**: For building paths
- **Don't ignore exceptions**: Handle or propagate file errors
- **Don't write directly**: Use atomic writes for critical files
- **Don't hardcode paths**: Use configuration or validation

### Path Traversal Prevention

Common attack vectors and mitigations:

| Attack Pattern | Blocked By |
|----------------|------------|
| `../../../etc/passwd` | `validate_agent_name()` - rejects `../` |
| `/etc/passwd` | `validate_file_path()` - checks base_dir |
| `agent/../../../etc/passwd` | Path resolution + relative_to check |
| Symbolic links | `Path.resolve()` follows links then validates |
| `agent\x00name` | Regex validation rejects null bytes |
| `agent@#$%` | Regex validation allows only safe characters |

### Directory Operations

```python
# ✅ CORRECT: Safe directory creation
from pathlib import Path

output_dir = Path("output")
output_dir.mkdir(parents=True, exist_ok=True)

# Validate before accessing subdirectories
safe_subdir = validate_file_path(user_subdir, base_dir=output_dir)

# ❌ WRONG: Unchecked directory access
os.makedirs(f"output/{user_input}")  # Path traversal risk
```

---

## 🔑 4. Secrets Management

### GitHub Secrets

#### ✅ Do's
- **Use GitHub Secrets**: Store sensitive data in repository secrets
- **Reference via environment**: Access secrets through `${{ secrets.NAME }}`
- **Rotate regularly**: Update secrets periodically
- **Use least privilege**: Each secret should have minimum necessary permissions
- **Audit access**: Review who can access secrets

```yaml
# ✅ CORRECT: Using GitHub Secrets
env:
  GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
run: |
  gh pr list --repo ${{ github.repository }}
```

#### ❌ Don'ts
- **Don't hardcode secrets**: Never commit API keys, tokens, or passwords
- **Don't log secrets**: Ensure secrets aren't printed in logs
- **Don't pass in URLs**: Secrets in URLs may be logged
- **Don't commit .env files**: Add to .gitignore

### Secret Detection

```bash
# Check for accidentally committed secrets
git log -p | grep -iE '(api[_-]?key|secret|token|password)\s*=\s*["\'][^"\']{8,}'

# Use GitHub's secret scanning
# Enabled automatically for public repositories
```

### Configuration Files

```python
# ✅ CORRECT: Load from environment
import os

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

# ❌ WRONG: Hardcoded secrets
API_KEY = "sk-1234567890abcdef"  # NEVER DO THIS
```

---

## 🚨 5. Command Injection Prevention

### Subprocess Execution

#### ✅ Do's
- **Use argument arrays**: Pass commands as lists, not strings
- **Avoid shell=True**: Unless absolutely necessary
- **Validate inputs**: Before passing to subprocess
- **Use constants**: For command names when possible
- **Quote properly**: When shell commands are necessary

```python
# ✅ CORRECT: Safe subprocess execution
import subprocess

result = subprocess.run(
    ["gh", "pr", "view", pr_number],
    capture_output=True,
    text=True,
    check=True
)

# ❌ WRONG: Command injection risk
subprocess.run(f"gh pr view {pr_number}", shell=True)  # DANGEROUS!
```

#### ❌ Don'ts
- **Don't use string commands**: With `shell=True`
- **Don't interpolate user input**: Into shell commands
- **Don't trust command output**: Validate before reuse
- **Don't ignore return codes**: Check for success/failure

### GitHub CLI (gh) Usage

```bash
# ✅ CORRECT: Safe gh CLI usage
pr_number="123"  # Validated number
gh pr view "${pr_number}" --json title,author

# ✅ CORRECT: Safe with validation
if [[ "${pr_number}" =~ ^[0-9]+$ ]]; then
  gh pr view "${pr_number}"
fi

# ❌ WRONG: Injection vulnerability
gh pr view $(echo "${user_input}")  # User could inject commands
```

### Bash Script Security

```bash
# ✅ CORRECT: Safe bash practices
#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Quote variables
pr_author="${author}"
if [ "${pr_author}" = "github-actions[bot]" ]; then
  echo "Trusted bot"
fi

# ❌ WRONG: Unquoted variables
if [ $pr_author = "github-actions[bot]" ]; then  # Word splitting risk
  echo "Trusted bot"
fi
```

---

## 🔍 6. Data Exposure & Privacy

### Information Disclosure

#### ✅ Do's
- **Use generic errors**: For security-related failures
- **Log safely**: Avoid logging sensitive data
- **Sanitize outputs**: Before displaying to users
- **Control error detail**: Different messages for different contexts

```python
# ✅ CORRECT: Generic security error
try:
    validate_file_path(user_path, base_dir)
except ValidationError:
    raise ValidationError("Access denied")  # Generic message

# ❌ WRONG: Exposing internal paths
except ValidationError as e:
    raise ValidationError(f"Cannot access {base_dir}/{user_path}: {e}")
```

#### ❌ Don'ts
- **Don't expose stack traces**: To untrusted users
- **Don't reveal file structure**: In error messages
- **Don't log credentials**: Even in debug mode
- **Don't include system info**: In public error messages

### Logging Best Practices

```python
# ✅ CORRECT: Safe logging
import logging

logger.info(f"Processing agent: {agent_name}")
logger.debug(f"File path validated: {safe_path.name}")  # Only filename

# ❌ WRONG: Logging sensitive data
logger.debug(f"API token: {token}")  # NEVER LOG SECRETS
logger.info(f"Full path: {safe_path}")  # Could expose structure
```

---

## 🧪 7. Testing & Validation

### Security Testing

#### ✅ Required Tests
- [x] **Input validation tests**: Test reject invalid inputs
- [x] **Path traversal tests**: Verify path protection
- [x] **Authorization tests**: Check access control logic
- [x] **Injection tests**: Test command/SQL injection prevention
- [x] **Error handling tests**: Verify secure error messages
- [x] **Integration tests**: Test security in real workflows

### CodeQL Security Scanning

```yaml
# Ensure CodeQL is enabled in repository
# .github/workflows/codeql-analysis.yml should exist and run

# Security scan should show:
# ✅ Zero alerts for new code
# ✅ All languages scanned (Python, JavaScript, etc.)
# ✅ Runs on PRs and scheduled
```

### Test Examples

```python
# Example from test_validation_utils.py
def test_path_traversal_attack():
    """Test that path traversal attempts are blocked."""
    base_dir = Path("/safe/directory")
    
    # These should all raise ValidationError
    with pytest.raises(ValidationError):
        validate_file_path("../../../etc/passwd", base_dir)
    
    with pytest.raises(ValidationError):
        validate_file_path("/etc/passwd", base_dir)
    
    with pytest.raises(ValidationError):
        validate_agent_name("../../etc/passwd")
```

### Manual Security Review Checklist

Before merging security-sensitive changes:

- [ ] Review all file operations for path traversal risks
- [ ] Check all subprocess calls for command injection
- [ ] Verify input validation on all user-provided data
- [ ] Ensure no secrets in code or configuration
- [ ] Test error messages don't expose sensitive info
- [ ] Verify proper authentication/authorization checks
- [ ] Run CodeQL scan and address any alerts
- [ ] Test with malicious inputs (fuzzing)
- [ ] Check dependencies for known vulnerabilities

---

## 📦 8. Dependency Management

### Dependency Security

#### ✅ Do's
- **Pin versions**: Use specific versions in requirements.txt
- **Regular updates**: Keep dependencies current
- **Security scanning**: Use Dependabot or similar tools
- **Minimize dependencies**: Only add necessary packages
- **Review before adding**: Check package reputation and maintenance

```txt
# ✅ CORRECT: requirements.txt with pinned versions
requests==2.31.0
pyyaml==6.0.1
pytest==7.4.3
```

#### ❌ Don'ts
- **Don't use wildcards**: Avoid `*` or `^` in versions
- **Don't ignore updates**: Especially security patches
- **Don't add untrusted packages**: Research before installing
- **Don't commit dependencies**: Use .gitignore for node_modules, venv, etc.

### Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

---

## 🤖 9. Autonomous AI System Specific

### AI Agent Security

#### ✅ Do's
- **Validate agent definitions**: Check agent markdown files for safety
- **Limit agent permissions**: Agents should have minimal GitHub token access
- **Monitor agent behavior**: Log and review agent actions
- **Validate agent output**: Don't trust AI-generated code without review
- **Sandbox agent execution**: Limit what agents can modify

#### ❌ Don'ts
- **Don't give unrestricted access**: Even to trusted AI agents
- **Don't skip human review**: For security-critical changes
- **Don't trust agent input**: Validate everything
- **Don't allow arbitrary code execution**: From agent suggestions

### Workflow Automation Safety

```yaml
# ✅ CORRECT: Limited workflow permissions
permissions:
  contents: read
  pull-requests: write
  issues: write

# Validate before acting
run: |
  # Check authorization
  if [ "${is_authorized}" -eq 1 ]; then
    # Perform action
    gh pr merge "${pr_number}"
  else
    echo "Unauthorized"
  fi
```

### Issue & PR Generation

```python
# ✅ CORRECT: Validate AI-generated content
def create_issue_from_ai(title, body):
    # Validate inputs
    title = validate_string_length(title, max_length=200, field_name="title")
    body = validate_string_length(body, max_length=65535, field_name="body")
    
    # Sanitize for Markdown injection
    title = title.replace("[", "\\[").replace("]", "\\]")
    
    # Create issue
    subprocess.run(
        ["gh", "issue", "create", "--title", title, "--body", body],
        check=True
    )
```

---

## 🔄 10. Continuous Security

### Monitoring & Auditing

#### ✅ Do's
- **Enable audit logs**: Track who changed what
- **Monitor workflow runs**: Review automated actions
- **Track failed authentications**: Alert on suspicious activity
- **Regular security reviews**: Periodic assessment of security posture
- **Incident response plan**: Know what to do if compromised

### Security Maintenance Schedule

| Frequency | Task |
|-----------|------|
| **Daily** | Review workflow run logs |
| **Weekly** | Check for dependency updates |
| **Monthly** | Security posture review |
| **Quarterly** | Full security audit |
| **Annually** | Penetration testing |

### Security Alerts & Response

```yaml
# Enable security features:
- Code scanning (CodeQL)
- Secret scanning
- Dependency alerts (Dependabot)
- Security advisories

# Response procedures:
1. Assess severity
2. Isolate affected systems
3. Apply patches/fixes
4. Document incident
5. Review and improve
```

---

## 📚 11. OWASP & Standards Compliance

### OWASP Top 10 Coverage

| OWASP Issue | Chained Mitigation | Status |
|-------------|-------------------|---------|
| **A01: Broken Access Control** | CODEOWNERS + workflow auth checks + branch protection | ✅ |
| **A02: Cryptographic Failures** | GitHub Secrets for sensitive data | ✅ |
| **A03: Injection** | Input validation + parameterized commands | ✅ |
| **A04: Insecure Design** | Security-first architecture + defense in depth | ✅ |
| **A05: Security Misconfiguration** | Minimal permissions + secure defaults | ✅ |
| **A06: Vulnerable Components** | Dependabot + version pinning | ✅ |
| **A07: Authentication Failures** | GitHub authentication + bot verification | ✅ |
| **A08: Software/Data Integrity** | Code review + atomic file operations | ✅ |
| **A09: Logging Failures** | Safe logging + monitoring | ✅ |
| **A10: SSRF** | No external API calls without validation | ✅ |

### CWE Coverage

| CWE | Description | Protection |
|-----|-------------|------------|
| **CWE-22** | Path Traversal | `validate_file_path()` + path resolution |
| **CWE-20** | Improper Input Validation | `validation_utils.py` comprehensive checks |
| **CWE-73** | External Control of File Name | Agent name validation + sanitization |
| **CWE-77** | Command Injection | Argument arrays + no shell=True |
| **CWE-78** | OS Command Injection | Input validation + subprocess safety |
| **CWE-79** | XSS | Markdown escaping (GitHub Pages) |
| **CWE-89** | SQL Injection | N/A (no database) |
| **CWE-209** | Information Exposure | Generic error messages |
| **CWE-502** | Deserialization | Safe JSON/YAML parsing only |
| **CWE-798** | Hardcoded Credentials | GitHub Secrets usage |

---

## 🎯 12. Security Implementation Checklist

### For New Features

Before implementing a new feature:

- [ ] **Threat Model**: Identify potential security risks
- [ ] **Input Validation**: Plan validation strategy
- [ ] **Authentication**: Determine who can use the feature
- [ ] **Authorization**: Define access control requirements
- [ ] **Data Protection**: Identify sensitive data handling needs
- [ ] **Error Handling**: Plan secure error messages
- [ ] **Logging**: Determine what to log (safely)
- [ ] **Testing**: Plan security test cases
- [ ] **Documentation**: Document security considerations

### For Code Review

When reviewing code:

- [ ] **Input Validation**: All user inputs validated?
- [ ] **Path Operations**: Protected against traversal?
- [ ] **Command Execution**: Using safe subprocess methods?
- [ ] **Secrets**: No hardcoded credentials?
- [ ] **Permissions**: Minimal required permissions used?
- [ ] **Error Messages**: No information disclosure?
- [ ] **Dependencies**: New dependencies reviewed and safe?
- [ ] **Tests**: Security test cases included?
- [ ] **Documentation**: Security implications documented?

### For Deployment

Before deploying to production:

- [ ] **CodeQL Scan**: Passing with zero alerts
- [ ] **Dependencies**: All up to date
- [ ] **Secrets**: Properly configured in GitHub
- [ ] **Branch Protection**: Rules enabled and correct
- [ ] **CODEOWNERS**: File present and accurate
- [ ] **Workflows**: Permissions minimized
- [ ] **Monitoring**: Logging and alerts configured
- [ ] **Backup**: Can roll back if needed
- [ ] **Documentation**: Updated security docs

---

## 🚀 Quick Reference

### Most Common Security Issues

1. **Path Traversal** → Use `validate_file_path()`
2. **Command Injection** → Use subprocess with argument arrays
3. **Unauthorized Access** → Check author + label before auto-merge
4. **Secrets in Code** → Use GitHub Secrets
5. **Missing Input Validation** → Use `validation_utils.py`

### Security Utilities Quick Reference

```python
from tools.validation_utils import (
    validate_agent_name,      # Agent name validation
    validate_file_path,        # Path traversal prevention
    validate_json_structure,   # JSON validation
    validate_string_length,    # String length checks
    validate_non_empty_string, # Non-empty string validation
    safe_file_read,           # Safe file reading
    safe_file_write,          # Safe file writing
)
```

### Emergency Contacts

- **Security Issue**: Create a security advisory (GitHub Security tab)
- **Urgent Fix**: Contact repository owner (@enufacas)
- **General Questions**: Open an issue with `security` label

---

## 📖 Additional Resources

### Internal Documentation
- [Security Implementation](SECURITY_IMPLEMENTATION.md) - Architecture details
- [Security Summary](../SECURITY_SUMMARY.md) - Scan results
- [Contributing Guide](CONTRIBUTING.md) - External contribution process
- [Workflows Documentation](WORKFLOWS.md) - Workflow security details

### External Resources
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

### Security Tools
- **CodeQL**: Static analysis security scanning
- **Dependabot**: Dependency vulnerability scanning
- **GitHub Secret Scanning**: Automatic secret detection
- **pytest**: Security test framework

---

## 🤝 Contributing to Security

Found a security issue? Please:

1. **Don't open a public issue** for vulnerabilities
2. **Use GitHub Security Advisories** to report privately
3. **Include details**: Steps to reproduce, impact, suggested fix
4. **Wait for acknowledgment**: Before public disclosure

For non-sensitive security improvements:

1. Open an issue with `security` label
2. Discuss approach with maintainers
3. Submit PR with security tests
4. Document in this checklist

---

## ✅ Conclusion

Security in an autonomous AI system requires:

- 🛡️ **Defense in Depth**: Multiple security layers
- 🔍 **Continuous Monitoring**: Watch for anomalies
- 🔄 **Regular Updates**: Keep dependencies current
- 📝 **Documentation**: Clear security guidelines
- 🧪 **Testing**: Comprehensive security tests
- 🤝 **Collaboration**: Security is everyone's responsibility

**Remember**: Security is not a destination, it's a continuous journey. Stay vigilant, keep learning, and prioritize security in every decision.

---

**Last Updated**: 2025-11-11  
**Document Version**: 1.0  
**Maintainer**: Chained Security Team

---

[← Security Implementation](SECURITY_IMPLEMENTATION.md) | [↑ Back to Docs](../) | [Contributing →](CONTRIBUTING.md)
