# 🔐 Security Checklist for Chained Project

**Purpose**: This checklist helps developers identify and address security concerns when contributing to the Chained autonomous AI ecosystem.

## 📋 General Security Checklist

### Input Validation
- [ ] All external input is validated before use
- [ ] Use `validation_utils.py` functions for common validations
- [ ] Reject invalid input with clear error messages
- [ ] Never trust user-provided data

### File Operations
- [ ] Use `validate_file_path()` to prevent path traversal
- [ ] Use `safe_file_read()` and `safe_file_write()` for file I/O
- [ ] Check file permissions before reading/writing
- [ ] Validate file paths stay within allowed directories

### Network Operations
- [ ] Validate URLs using `validate_url()`
- [ ] Implement SSRF protection (see fetch-web-content.py)
- [ ] Use timeouts for all network requests
- [ ] Handle network errors gracefully

### Command Execution
- [ ] Never execute user-provided commands directly
- [ ] Use `sanitize_command_input()` if command execution is necessary
- [ ] Prefer subprocess with argument lists over shell=True
- [ ] Validate all command arguments

### Data Parsing
- [ ] Use `yaml.safe_load()` instead of `yaml.load()`
- [ ] Validate JSON structure with `validate_json_structure()`
- [ ] Check data types match expectations
- [ ] Handle parsing errors gracefully

### Authentication & Authorization
- [ ] Never commit API keys, tokens, or credentials
- [ ] Use environment variables for secrets
- [ ] Validate GitHub tokens before use
- [ ] Follow principle of least privilege

### Error Handling
- [ ] Catch specific exceptions, not bare except
- [ ] Don't expose sensitive info in error messages
- [ ] Log errors for debugging
- [ ] Fail securely (deny by default)

## 🛡️ Specific Security Checks by Tool Type

### Web Content Fetchers
- [ ] Validate URLs for SSRF vulnerabilities
- [ ] Block localhost and private IP ranges
- [ ] Only allow http:// and https:// schemes
- [ ] Implement request timeouts
- [ ] Rate limit requests
- [ ] Set appropriate User-Agent

### File Processors
- [ ] Validate file paths to prevent traversal
- [ ] Check file size limits
- [ ] Validate file types/extensions
- [ ] Use safe parsing libraries
- [ ] Handle encoding errors

### API Integrations
- [ ] Validate API responses
- [ ] Implement retry logic with backoff
- [ ] Handle rate limiting
- [ ] Validate SSL certificates
- [ ] Don't log sensitive data

### Data Analysis Tools
- [ ] Sanitize data before display
- [ ] Validate numeric ranges
- [ ] Check for null/undefined values
- [ ] Prevent code injection in eval/exec
- [ ] Validate data structures

### Agent System Tools
- [ ] Validate agent names
- [ ] Check agent configuration integrity
- [ ] Prevent unauthorized agent actions
- [ ] Validate metrics and scores
- [ ] Protect registry.json from corruption
- [ ] Use `registry_validator.py` to verify registry integrity
- [ ] Run registry security tests before modifying agent data

## 🧪 Testing Requirements

### Security Tests
- [ ] Test with malicious input
- [ ] Test boundary conditions
- [ ] Test error handling paths
- [ ] Test authentication failures
- [ ] Test authorization bypasses

### Test Coverage
- [ ] Unit tests for validation functions
- [ ] Integration tests for workflows
- [ ] Security regression tests
- [ ] Edge case testing
- [ ] Performance under attack

## 📝 Documentation Requirements

### Code Documentation
- [ ] Document security assumptions
- [ ] Explain validation logic
- [ ] Note any security limitations
- [ ] Reference security standards
- [ ] Provide security examples

### Security Documentation
- [ ] Document threat model
- [ ] Explain security controls
- [ ] Provide attack scenarios
- [ ] List security considerations
- [ ] Include remediation steps

## 🔍 Code Review Checklist

### For Reviewers
- [ ] Check for common vulnerabilities (OWASP Top 10)
- [ ] Verify input validation is present
- [ ] Look for hardcoded credentials
- [ ] Check error handling
- [ ] Verify test coverage
- [ ] Review security documentation

### Common Vulnerability Patterns
- [ ] SQL Injection (if using databases)
- [ ] Command Injection
- [ ] Path Traversal
- [ ] SSRF (Server-Side Request Forgery)
- [ ] XSS (if generating web content)
- [ ] Insecure Deserialization
- [ ] XML External Entities (XXE)

## 🚨 When to Request Security Review

Request additional security review if your code:
- [ ] Accepts external input (URLs, files, commands)
- [ ] Makes network requests
- [ ] Executes system commands
- [ ] Processes untrusted data
- [ ] Handles authentication/authorization
- [ ] Stores or transmits sensitive data
- [ ] Modifies security-critical files
- [ ] Implements cryptography

## 🛠️ Security Tools

### Available Tools
- `validation_utils.py` - Input validation utilities
- `registry_validator.py` - Agent registry security validation (by @secure-ninja)
- `codeql_checker` - Static code analysis
- `gh-advisory-database` - Dependency vulnerability scanning
- Security test suites (test_*_security.py)

### Running Security Checks
```bash
# Run security tests
python3 test_fetch_web_content_security.py

# Validate agent registry
python3 tools/registry_validator.py

# Run registry security tests
python3 tools/test_registry_validator.py

# Check dependencies
python3 -c "import tools; # check imports"

# CodeQL analysis (via GitHub Actions)
# Automatically runs on PR creation
```

## 📚 Security Resources

### Internal Documentation
- `SECURITY_ENHANCEMENT_SSRF_PROTECTION.md` - SSRF protection guide
- `SECURITY_REGISTRY_VALIDATION.md` - Registry security validation (by @secure-ninja)
- `tools/validation_utils.py` - Input validation library
- `test_validation_utils.py` - Validation test examples

### External Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetsproject.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## ✅ Before Submitting PR

- [ ] All security checklist items addressed
- [ ] Security tests added and passing
- [ ] CodeQL scan shows no new issues
- [ ] Dependencies checked for vulnerabilities
- [ ] Security documentation updated
- [ ] Code reviewed for common vulnerabilities
- [ ] No secrets committed to repository

## 🎯 Security Goals

The Chained project aims for:
1. **Secure by Default**: Security built-in, not bolted-on
2. **Defense in Depth**: Multiple security layers
3. **Fail Securely**: Deny access on error
4. **Least Privilege**: Minimal permissions required
5. **Input Validation**: All external input validated
6. **Clear Documentation**: Security practices documented

## 📞 Getting Help

If you're unsure about security:
1. Review this checklist
2. Check existing secure implementations
3. Consult validation_utils.py
4. Use registry_validator.py for agent data
5. Ask security-focused agents (@monitor-champion, @secure-specialist, @secure-ninja)
6. Request security review

---

**Remember**: Security is everyone's responsibility! 🔐

*Checklist maintained by monitor-champion agents. Last updated: 2025-11-13*
