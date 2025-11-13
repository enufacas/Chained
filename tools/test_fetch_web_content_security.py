#!/usr/bin/env python3
"""
Security tests for fetch-web-content.py URL validation and SSRF protection.

Tests cover:
- URL validation and sanitization
- SSRF attack prevention (localhost, private IPs)
- Malicious URL pattern detection
- Proper error handling for security violations
"""

import sys
import unittest
from pathlib import Path

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from validation_utils import ValidationError
except ImportError:
    class ValidationError(Exception):
        pass

# Import the WebContentFetcher
try:
    import fetch_web_content
    from fetch_web_content import WebContentFetcher
    HAS_FETCHER = True
except ImportError:
    HAS_FETCHER = False
    print("Warning: Could not import fetch_web_content module")


@unittest.skipIf(not HAS_FETCHER, "fetch_web_content module not available")
class TestURLSecurityValidation(unittest.TestCase):
    """Test URL security validation and SSRF protection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fetcher = WebContentFetcher()
    
    def test_valid_http_url(self):
        """Test that valid HTTP URLs pass validation"""
        valid_urls = [
            'http://example.com',
            'https://example.com',
            'https://www.example.com/path',
            'https://api.github.com/repos',
        ]
        
        for url in valid_urls:
            try:
                validated = self.fetcher._validate_url_security(url)
                self.assertEqual(validated, url)
            except ValidationError as e:
                self.fail(f"Valid URL rejected: {url} - {e}")
    
    def test_reject_localhost_urls(self):
        """Test that localhost URLs are rejected (SSRF protection)"""
        localhost_urls = [
            'http://localhost',
            'http://localhost:8080',
            'http://127.0.0.1',
            'http://127.0.0.1:3000',
            'http://0.0.0.0',
            'http://[::1]',
        ]
        
        for url in localhost_urls:
            with self.assertRaises(ValidationError) as context:
                self.fetcher._validate_url_security(url)
            
            error_msg = str(context.exception).lower()
            self.assertTrue(
                'localhost' in error_msg or 'internal' in error_msg or 'private' in error_msg,
                f"Expected security error for {url}, got: {error_msg}"
            )
    
    def test_reject_private_ip_ranges(self):
        """Test that private IP ranges are rejected (SSRF protection)"""
        private_ips = [
            'http://10.0.0.1',           # Private Class A
            'http://172.16.0.1',         # Private Class B
            'http://192.168.1.1',        # Private Class C
            'http://169.254.1.1',        # Link-local
        ]
        
        for url in private_ips:
            with self.assertRaises(ValidationError) as context:
                self.fetcher._validate_url_security(url)
            
            error_msg = str(context.exception).lower()
            self.assertTrue(
                'private' in error_msg or 'internal' in error_msg,
                f"Expected security error for {url}, got: {error_msg}"
            )
    
    def test_reject_invalid_schemes(self):
        """Test that non-HTTP(S) schemes are rejected"""
        invalid_schemes = [
            'file:///etc/passwd',
            'ftp://example.com',
            'javascript:alert(1)',
            'data:text/html,<script>alert(1)</script>',
            'gopher://example.com',
        ]
        
        for url in invalid_schemes:
            with self.assertRaises(ValidationError) as context:
                self.fetcher._validate_url_security(url)
            
            error_msg = str(context.exception).lower()
            self.assertTrue(
                'scheme' in error_msg or 'not allowed' in error_msg,
                f"Expected scheme error for {url}, got: {error_msg}"
            )
    
    def test_reject_empty_urls(self):
        """Test that empty or invalid URLs are rejected"""
        invalid_urls = [
            '',
            '   ',
            None,
        ]
        
        for url in invalid_urls:
            with self.assertRaises((ValidationError, AttributeError, TypeError)):
                self.fetcher._validate_url_security(url)
    
    def test_reject_malformed_urls(self):
        """Test that malformed URLs are rejected"""
        malformed_urls = [
            'not-a-url',
            'http://',
            'http://.',
            'http://..',
        ]
        
        for url in malformed_urls:
            with self.assertRaises(ValidationError):
                self.fetcher._validate_url_security(url)
    
    def test_fetch_with_invalid_url_returns_error(self):
        """Test that fetch() properly handles invalid URLs"""
        result = self.fetcher.fetch('http://localhost:8080/test')
        
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])
        self.assertIn('security', result['error'].lower())
    
    def test_fetch_with_private_ip_returns_error(self):
        """Test that fetch() properly handles private IP addresses"""
        result = self.fetcher.fetch('http://192.168.1.1')
        
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])
        error_lower = result['error'].lower()
        self.assertTrue(
            'security' in error_lower or 'private' in error_lower or 'internal' in error_lower
        )
    
    def test_fetch_batch_security_validation(self):
        """Test that batch fetching validates all URLs"""
        urls = [
            'http://localhost',
            'http://192.168.1.1',
            'file:///etc/passwd'
        ]
        
        results = self.fetcher.fetch_batch(urls, delay=0.1)
        
        # All should fail with security errors
        for result in results:
            self.assertFalse(result['success'])
            self.assertIsNotNone(result['error'])


@unittest.skipIf(not HAS_FETCHER, "fetch_web_content module not available")
class TestWebContentFetcherSecurity(unittest.TestCase):
    """Test overall security of WebContentFetcher"""
    
    def test_user_agent_is_set(self):
        """Test that a proper User-Agent is set"""
        fetcher = WebContentFetcher()
        self.assertIn('ChainedAI', fetcher.user_agent)
        self.assertIn('User-Agent', fetcher.session.headers)
    
    def test_timeout_is_configurable(self):
        """Test that timeout can be configured"""
        fetcher = WebContentFetcher(timeout=5)
        self.assertEqual(fetcher.timeout, 5)
    
    def test_custom_user_agent(self):
        """Test that custom User-Agent can be set"""
        custom_ua = 'Custom/1.0'
        fetcher = WebContentFetcher(user_agent=custom_ua)
        self.assertEqual(fetcher.user_agent, custom_ua)
    
    def test_result_structure(self):
        """Test that result dictionary has expected structure"""
        fetcher = WebContentFetcher()
        result = fetcher.fetch('http://localhost')
        
        # Check all expected keys are present
        expected_keys = ['success', 'url', 'content', 'title', 'error']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # On security error, success should be False and error should be set
        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])


class TestValidationUtilsIntegration(unittest.TestCase):
    """Test integration with validation_utils module"""
    
    def test_validation_error_available(self):
        """Test that ValidationError is available"""
        self.assertTrue(callable(ValidationError))
    
    @unittest.skipIf(not HAS_FETCHER, "fetch_web_content module not available")
    def test_imports_validation_utils(self):
        """Test that fetch_web_content imports validation utilities"""
        # Check that the module has access to validation functions
        self.assertTrue(hasattr(fetch_web_content, 'ValidationError'))
        self.assertTrue(hasattr(fetch_web_content, '_validate_url_basic'))


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
