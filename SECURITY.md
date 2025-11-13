# Security Policy

## 🔒 Overview

The Chained project takes security seriously. This document outlines our security policy, how to report vulnerabilities, and what to expect from the security response process.

**Security Philosophy**: "Security is a process, not a product" - Bruce Schneier

We believe in defense in depth, assume breach mentality, and transparent security practices.

## 🎯 Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| Other branches | :x: |

The `main` branch is the only officially supported version. Security updates are applied to `main` and should be pulled regularly.

## 🚨 Reporting a Vulnerability

**IMPORTANT**: Do NOT open public GitHub issues for security vulnerabilities.

### For Security Vulnerabilities

If you discover a security vulnerability, please report it privately using one of these methods:

1. **GitHub Security Advisories** (Preferred)
   - Navigate to the [Security tab](https://github.com/enufacas/Chained/security/advisories)
   - Click "Report a vulnerability"
   - Fill out the vulnerability report form

2. **Direct Contact**
   - Contact the repository owner: [@enufacas](https://github.com/enufacas)
   - Include "SECURITY" in the subject line

### What to Include

When reporting a vulnerability, please provide:

- **Description**: Clear description of the vulnerability
- **Impact**: What could an attacker achieve?
- **Reproduction Steps**: Detailed steps to reproduce the issue
- **Proof of Concept**: Code or commands demonstrating the vulnerability (if possible)
- **Environment**: Version, OS, configuration details
- **Suggested Fix**: If you have ideas for remediation
- **Your Contact**: How we can reach you for follow-up

### Example Report Format

```
**Vulnerability Type**: [e.g., Command Injection, Path Traversal, XSS]

**Affected Component**: [e.g., workflow file, Python script, specific function]

**Impact**: [e.g., Arbitrary code execution, unauthorized file access]

**Steps to Reproduce**:
1. Step one
2. Step two
3. Expected result

**Proof of Concept**:
[Code, commands, or screenshots]

**Suggested Mitigation**:
[Your recommendations]
```

## 🔐 Security Response Process

### Timeline

| Phase | Timeline | Description |
|-------|----------|-------------|
| **Acknowledgment** | 24-48 hours | We'll confirm receipt of your report |
| **Initial Assessment** | 2-5 days | We'll assess severity and impact |
| **Fix Development** | 1-2 weeks | Develop and test the fix |
| **Disclosure** | After fix | Coordinate public disclosure |

### What to Expect

1. **Acknowledgment**: We'll acknowledge your report within 24-48 hours
2. **Assessment**: We'll investigate and assess severity (Critical, High, Medium, Low)
3. **Communication**: We'll keep you updated on progress
4. **Fix Development**: We'll develop, test, and deploy a fix
5. **Credit**: We'll credit you in the security advisory (unless you prefer anonymity)
6. **Disclosure**: We'll coordinate public disclosure with you

### Severity Levels

We use CVSS 3.1 scoring and classify vulnerabilities as:

- **Critical** (9.0-10.0): Immediate action required, can lead to complete system compromise
- **High** (7.0-8.9): Important to fix quickly, significant impact
- **Medium** (4.0-6.9): Should be fixed, moderate impact
- **Low** (0.1-3.9): Nice to fix, minimal impact

## 🛡️ Security Measures

### Current Security Controls

The Chained project implements multiple layers of security:

#### 1. **Access Control**
- Branch protection on `main` requiring code review
- CODEOWNERS file enforcing review by trusted maintainers
- Minimal GitHub Actions permissions (principle of least privilege)
- Authorization checks in auto-merge workflows
- Trusted bot list for automation (github-actions[bot], dependabot[bot], copilot)

#### 2. **Input Validation**
- Comprehensive validation library (`tools/validation_utils.py`)
- Path traversal prevention for all file operations
- Agent name sanitization (alphanumeric and hyphens only)
- JSON structure validation
- String length and content validation

#### 3. **Code Security**
- CodeQL security scanning enabled
- Dependabot for dependency vulnerability scanning
- Secret scanning for accidentally committed credentials
- Subprocess security (no `shell=True`, use argument arrays)
- Safe file operations with atomic writes

#### 4. **Secrets Management**
- GitHub Secrets for sensitive data
- No hardcoded credentials in code
- Environment variable usage for configuration
- Regular secret rotation

#### 5. **Dependency Security**
- Pinned versions in `requirements.txt`
- Regular dependency updates via Dependabot
- Vulnerability scanning before adding new dependencies
- Minimal dependency surface

#### 6. **Workflow Security**
- Explicit permission grants per workflow
- No `permissions: write-all` usage
- Author verification before auto-merge
- Label-based authorization (`copilot` label)
- Regex matching for bot identification

### Security Documentation

- [Security Best Practices](docs/SECURITY_BEST_PRACTICES.md) - Comprehensive security guidelines
- [Security Implementation](docs/SECURITY_IMPLEMENTATION.md) - Technical security architecture
- [Validation Utils](tools/validation_utils.py) - Input validation library
- [Security Summaries](SECURITY_SUMMARY.md) - Historical security scan results

## 🧪 Security Testing

### Automated Testing
- CodeQL scans on every PR and schedule
- Dependency vulnerability scans (Dependabot)
- Secret scanning (GitHub Security)
- Unit tests for security functions
- Integration tests for workflows

### Manual Testing
Security-focused code reviews check for:
- Input validation gaps
- Path traversal vulnerabilities
- Command injection risks
- Information disclosure
- Authentication/authorization bypass
- Secrets in code

## 🔍 Threat Model

### Attack Surface

The project's attack surface includes:

1. **GitHub Actions Workflows**
   - Input: PR data, issue data, workflow inputs
   - Risk: Unauthorized automation, privilege escalation
   - Mitigation: Author verification, label checks, minimal permissions

2. **Python Scripts**
   - Input: File paths, agent names, JSON data
   - Risk: Path traversal, injection attacks
   - Mitigation: Input validation library, safe subprocess usage

3. **File Operations**
   - Input: User-provided paths, file content
   - Risk: Path traversal, arbitrary file access
   - Mitigation: Path validation, base directory checks

4. **Dependencies**
   - Input: External libraries
   - Risk: Supply chain attacks, vulnerable dependencies
   - Mitigation: Pinned versions, Dependabot scanning

### Trust Boundaries

1. **Repository Owner**: Fully trusted
2. **GitHub Actions Bot**: Trusted (for automation)
3. **Dependabot**: Trusted (for dependency updates)
4. **Copilot**: Trusted (with `copilot` label)
5. **External Contributors**: Untrusted (manual review required)

### Key Assets

1. **GitHub Token**: Access to repository
2. **Auto-Merge Logic**: Could approve malicious PRs
3. **Agent Definitions**: Control AI behavior
4. **Workflow Configurations**: Control automation

## 🎓 Security Best Practices for Contributors

When contributing, please:

1. **Never commit secrets**: Use GitHub Secrets
2. **Validate all inputs**: Use `tools/validation_utils.py`
3. **Use subprocess safely**: No `shell=True`, use argument arrays
4. **Handle paths carefully**: Use `validate_file_path()` and `Path` objects
5. **Check dependencies**: Run `gh-advisory-database` for new dependencies
6. **Write security tests**: Test with malicious inputs
7. **Follow least privilege**: Request minimal permissions
8. **Document assumptions**: Make security assumptions explicit

See [Security Best Practices](docs/SECURITY_BEST_PRACTICES.md) for detailed guidelines.

## 🏆 Security Hall of Fame

We recognize security researchers who responsibly disclose vulnerabilities:

*Hall of Fame will be updated as security researchers contribute.*

### Recognition Criteria

- Reported through proper channels (private disclosure)
- Provided detailed reproduction steps
- Assisted with verification and testing
- Allowed coordinated disclosure
- Impact: Medium or higher severity

## 📜 Disclosure Policy

We follow a **coordinated disclosure** approach:

1. **Private Report**: Vulnerability reported privately
2. **Acknowledgment**: We confirm receipt (24-48 hours)
3. **Fix Development**: We develop and test a fix (1-2 weeks typically)
4. **Private Notification**: We notify affected parties
5. **Fix Deployment**: We deploy the fix
6. **Public Disclosure**: We publish a security advisory (after 90 days max or when fix is deployed)
7. **Credit**: We credit the reporter (unless anonymous requested)

We aim to fix critical vulnerabilities within 7 days and high-severity issues within 30 days.

## 🤝 Collaboration

We welcome security collaboration:

- **Security Reviews**: Help review code for security issues
- **Security Testing**: Help test security controls
- **Documentation**: Improve security documentation
- **Tool Development**: Build security tools for the project
- **Best Practices**: Share security knowledge

For non-sensitive security improvements, open an issue with the `security` label.

## 📞 Contact

- **Security Issues**: Use GitHub Security Advisories (preferred)
- **General Security Questions**: Open an issue with `security` label
- **Urgent Security Matters**: Contact [@enufacas](https://github.com/enufacas)

## 🔄 Updates

This security policy is reviewed and updated regularly:

- **Last Updated**: 2025-11-13
- **Version**: 1.0
- **Next Review**: 2025-12-13

Changes to this policy will be announced via:
- Repository commits
- Security advisory updates
- Release notes

---

## 🙏 Acknowledgments

We appreciate the security research community's efforts to keep this project secure. Thank you to all security researchers who report issues responsibly.

---

**Remember**: Security is everyone's responsibility. Stay vigilant, think like an attacker, and help us build a more secure system.

*"In security, the only thing worse than being blind is thinking you can see." - Bruce Schneier*
