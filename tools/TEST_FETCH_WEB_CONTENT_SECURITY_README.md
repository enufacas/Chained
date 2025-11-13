# Security Test Suite for fetch-web-content.py

This test suite validates the SSRF (Server-Side Request Forgery) protection implemented in `fetch-web-content.py`.

## Purpose

The web content fetcher tool accepts URLs from users to fetch external content. Without proper validation, this could be exploited for:
- Accessing internal services (localhost, private IPs)
- Port scanning internal networks
- Protocol abuse (file://, ftp://, etc.)

This test suite ensures all security controls are working correctly.

## Test Coverage

### 1. Valid URL Tests
Ensures legitimate URLs are accepted:
- http://example.com
- https://example.com
- https://www.example.com/path
- https://api.github.com/repos

### 2. Localhost Protection Tests
Blocks access to localhost:
- http://localhost
- http://localhost:8080
- http://127.0.0.1
- http://127.0.0.1:3000
- http://0.0.0.0
- http://[::1] (IPv6 localhost)

### 3. Private IP Range Tests
Blocks RFC 1918 private networks:
- http://10.0.0.1 (Class A private)
- http://172.16.0.1 (Class B private)
- http://192.168.1.1 (Class C private)
- http://169.254.1.1 (Link-local)

### 4. Invalid Scheme Tests
Only allows http:// and https://:
- file:///etc/passwd
- ftp://example.com
- javascript:alert(1)
- data:text/html,<script>alert(1)</script>
- gopher://example.com

### 5. Malformed URL Tests
Rejects invalid URL formats:
- Empty strings
- Whitespace only
- Invalid URL structures

### 6. Integration Tests
- Error handling in fetch()
- Batch operation security
- Result structure validation

## Running the Tests

From the tools directory:
```bash
cd tools
python3 test_fetch_web_content_security.py
```

Expected output:
```
test_custom_user_agent (__main__.TestWebContentFetcherSecurity) ... ok
test_fetch_batch_security_validation (__main__.TestURLSecurityValidation) ... ok
test_fetch_with_invalid_url_returns_error (__main__.TestURLSecurityValidation) ... ok
...
----------------------------------------------------------------------
Ran 15 tests in X.XXXs

OK
```

## Test Classes

### TestURLSecurityValidation
Tests the core URL security validation logic:
- `_validate_url_security()` method
- Direct validation tests
- fetch() integration tests

### TestWebContentFetcherSecurity
Tests overall security of the WebContentFetcher:
- Configuration options
- User-Agent handling
- Result structure

### TestValidationUtilsIntegration
Tests integration with validation_utils module:
- Import validation
- ValidationError availability

## Adding New Tests

To add a new security test:

1. Identify the attack vector or edge case
2. Add a test method to the appropriate class
3. Use descriptive test names (test_reject_XYZ or test_valid_XYZ)
4. Assert both the exception and error message content

Example:
```python
def test_reject_new_attack_vector(self):
    """Test that new attack vector is blocked"""
    malicious_url = 'http://...'
    
    with self.assertRaises(ValidationError) as context:
        self.fetcher._validate_url_security(malicious_url)
    
    error_msg = str(context.exception).lower()
    self.assertIn('expected_keyword', error_msg)
```

## Security Best Practices

1. **Test Attack Scenarios**: Every test represents a real attack vector
2. **Positive and Negative Tests**: Test both valid and invalid inputs
3. **Error Message Validation**: Ensure errors are informative but not revealing
4. **Comprehensive Coverage**: Cover all code paths in security functions
5. **Continuous Testing**: Run tests after any changes to fetch-web-content.py

## References

- **OWASP SSRF Cheat Sheet**: https://cheatsheetsproject.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **CWE-918 SSRF**: https://cwe.mitre.org/data/definitions/918.html
- **RFC 1918 Private Address Space**: https://tools.ietf.org/html/rfc1918

## Maintenance

Run this test suite:
- After modifying fetch-web-content.py
- After updating validation_utils.py
- As part of CI/CD pipeline
- Before releasing new versions

## Contact

For questions about these security tests:
- Review SECURITY_ENHANCEMENT_SSRF_PROTECTION.md
- Check the Chained project security documentation
- Consult with the security team or monitor-champion agents

---

*Security testing is not optional. It's essential.* 🔒
