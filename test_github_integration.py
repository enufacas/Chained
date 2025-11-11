#!/usr/bin/env python3
"""
Tests for GitHub Integration Utilities

Tests error handling, retry logic, rate limiting, and other integration features.
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
import urllib.error
import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from github_integration import (
    GitHubAPIClient,
    GitHubAPIError,
    GitHubAPIException,
    RetryConfig,
    RetryStrategy,
    retry_with_backoff,
    validate_response
)


class TestRetryDecorator(unittest.TestCase):
    """Test retry decorator functionality"""
    
    def test_successful_call_no_retry(self):
        """Test that successful calls don't trigger retries"""
        call_count = [0]
        
        @retry_with_backoff(RetryConfig(max_attempts=3))
        def successful_call():
            call_count[0] += 1
            return "success"
        
        result = successful_call()
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 1)
    
    def test_retry_on_transient_error(self):
        """Test that transient errors trigger retries"""
        call_count = [0]
        
        @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=0.01))
        def failing_call():
            call_count[0] += 1
            if call_count[0] < 3:
                error = GitHubAPIError(
                    status_code=500,
                    message="Internal server error",
                    is_rate_limited=False
                )
                raise GitHubAPIException(error)
            return "success"
        
        result = failing_call()
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 3)
    
    def test_no_retry_on_auth_error(self):
        """Test that auth errors don't trigger retries"""
        call_count = [0]
        
        @retry_with_backoff(RetryConfig(max_attempts=3))
        def auth_error_call():
            call_count[0] += 1
            error = GitHubAPIError(
                status_code=401,
                message="Unauthorized",
                is_auth_error=True
            )
            raise GitHubAPIException(error)
        
        with self.assertRaises(GitHubAPIException):
            auth_error_call()
        
        self.assertEqual(call_count[0], 1)
    
    def test_no_retry_on_not_found(self):
        """Test that 404 errors don't trigger retries"""
        call_count = [0]
        
        @retry_with_backoff(RetryConfig(max_attempts=3))
        def not_found_call():
            call_count[0] += 1
            error = GitHubAPIError(
                status_code=404,
                message="Not found",
                is_not_found=True
            )
            raise GitHubAPIException(error)
        
        with self.assertRaises(GitHubAPIException):
            not_found_call()
        
        self.assertEqual(call_count[0], 1)
    
    def test_max_attempts_exceeded(self):
        """Test that max attempts limit is respected"""
        call_count = [0]
        
        @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=0.01))
        def always_failing_call():
            call_count[0] += 1
            error = GitHubAPIError(
                status_code=500,
                message="Internal server error"
            )
            raise GitHubAPIException(error)
        
        with self.assertRaises(GitHubAPIException):
            always_failing_call()
        
        self.assertEqual(call_count[0], 3)
    
    def test_exponential_backoff(self):
        """Test exponential backoff strategy"""
        call_times = []
        
        @retry_with_backoff(RetryConfig(
            max_attempts=3,
            initial_delay=0.1,
            backoff_factor=2.0,
            strategy=RetryStrategy.EXPONENTIAL
        ))
        def timed_failing_call():
            call_times.append(time.time())
            if len(call_times) < 3:
                error = GitHubAPIError(
                    status_code=500,
                    message="Error"
                )
                raise GitHubAPIException(error)
            return "success"
        
        timed_failing_call()
        
        # Check that delays increase exponentially
        self.assertEqual(len(call_times), 3)
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        
        # Second delay should be roughly 2x first delay
        self.assertGreater(delay2, delay1 * 1.5)


class TestGitHubAPIError(unittest.TestCase):
    """Test GitHubAPIError dataclass"""
    
    def test_basic_error(self):
        """Test basic error creation"""
        error = GitHubAPIError(
            status_code=404,
            message="Not found"
        )
        
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.message, "Not found")
        self.assertFalse(error.is_rate_limited)
        self.assertFalse(error.is_auth_error)
        self.assertFalse(error.is_not_found)
    
    def test_rate_limit_error(self):
        """Test rate limit error"""
        error = GitHubAPIError(
            status_code=403,
            message="Rate limit exceeded",
            rate_limit_remaining=0,
            rate_limit_reset=int(time.time()) + 3600,
            is_rate_limited=True
        )
        
        self.assertTrue(error.is_rate_limited)
        self.assertEqual(error.rate_limit_remaining, 0)
        self.assertIsNotNone(error.rate_limit_reset)


class TestGitHubAPIClient(unittest.TestCase):
    """Test GitHubAPIClient functionality"""
    
    def setUp(self):
        """Set up test client"""
        self.client = GitHubAPIClient(
            token="test_token",
            retry_config=RetryConfig(max_attempts=1)  # No retries for simpler tests
        )
    
    def test_client_initialization(self):
        """Test client initialization"""
        self.assertEqual(self.client.base_url, "https://api.github.com")
        self.assertEqual(self.client.token, "test_token")
        self.assertEqual(self.client.timeout, 30)
    
    def test_build_headers(self):
        """Test header building"""
        headers = self.client._build_headers()
        
        self.assertIn('Authorization', headers)
        self.assertIn('Accept', headers)
        self.assertIn('User-Agent', headers)
        self.assertEqual(headers['Authorization'], 'token test_token')
    
    def test_build_headers_with_additional(self):
        """Test header building with additional headers"""
        headers = self.client._build_headers({'X-Custom': 'value'})
        
        self.assertIn('X-Custom', headers)
        self.assertEqual(headers['X-Custom'], 'value')
    
    @patch('urllib.request.urlopen')
    def test_successful_get_request(self, mock_urlopen):
        """Test successful GET request"""
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({'key': 'value'}).encode()
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.client.get('/test')
        
        self.assertEqual(result, {'key': 'value'})
        mock_urlopen.assert_called_once()
    
    @patch('urllib.request.urlopen')
    def test_get_request_with_params(self, mock_urlopen):
        """Test GET request with query parameters"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({'data': []}).encode()
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.client.get('/issues', params={'state': 'open', 'per_page': 10})
        
        # Check that URL contains query parameters
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        self.assertIn('state=open', request.full_url)
        self.assertIn('per_page=10', request.full_url)
    
    @patch('urllib.request.urlopen')
    def test_post_request(self, mock_urlopen):
        """Test POST request"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({'created': True}).encode()
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.client.post('/issues', data={'title': 'Test'})
        
        self.assertEqual(result, {'created': True})
        
        # Check request data
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        self.assertEqual(request.method, 'POST')
    
    @patch('urllib.request.urlopen')
    def test_http_error_handling(self, mock_urlopen):
        """Test HTTP error handling"""
        # Mock error response
        error_response = json.dumps({
            'message': 'Not found',
            'documentation_url': 'https://docs.github.com'
        }).encode()
        
        mock_error = urllib.error.HTTPError(
            url='https://api.github.com/test',
            code=404,
            msg='Not Found',
            hdrs={},
            fp=None
        )
        mock_error.read = Mock(return_value=error_response)
        mock_error.headers = {}
        
        mock_urlopen.side_effect = mock_error
        
        with self.assertRaises(GitHubAPIException) as context:
            self.client.get('/test')
        
        error = context.exception.error
        self.assertEqual(error.status_code, 404)
        self.assertTrue(error.is_not_found)
    
    @patch('urllib.request.urlopen')
    def test_rate_limit_warning(self, mock_urlopen):
        """Test rate limit warning"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({'data': 'test'}).encode()
        mock_response.headers = {'X-RateLimit-Remaining': '5'}
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Should print warning to stderr
        with patch('sys.stderr') as mock_stderr:
            result = self.client.get('/test')
            self.assertEqual(result, {'data': 'test'})
    
    @patch('urllib.request.urlopen')
    def test_graphql_query(self, mock_urlopen):
        """Test GraphQL query"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'data': {'repository': {'name': 'test'}}
        }).encode()
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        query = 'query { repository(owner: "test", name: "repo") { name } }'
        result = self.client.graphql(query)
        
        self.assertEqual(result, {'repository': {'name': 'test'}})
    
    @patch('urllib.request.urlopen')
    def test_graphql_error_handling(self, mock_urlopen):
        """Test GraphQL error handling"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'errors': [{'message': 'Invalid query'}]
        }).encode()
        mock_response.headers = {}
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        query = 'invalid query'
        
        with self.assertRaises(Exception) as context:
            self.client.graphql(query)
        
        self.assertIn('GraphQL errors', str(context.exception))


class TestValidateResponse(unittest.TestCase):
    """Test response validation"""
    
    def test_valid_response(self):
        """Test validation of valid response"""
        response = {'name': 'test', 'id': 123, 'type': 'repo'}
        result = validate_response(response, ['name', 'id'])
        self.assertTrue(result)
    
    def test_missing_fields(self):
        """Test validation with missing fields"""
        response = {'name': 'test'}
        
        with self.assertRaises(ValueError) as context:
            validate_response(response, ['name', 'id', 'type'])
        
        self.assertIn('missing required fields', str(context.exception))
    
    def test_invalid_response_type(self):
        """Test validation with wrong response type"""
        response = "not a dict"
        
        with self.assertRaises(ValueError) as context:
            validate_response(response, ['name'])
        
        self.assertIn('Expected dict', str(context.exception))


class TestIntegration(unittest.TestCase):
    """Integration tests (require network access)"""
    
    @unittest.skipUnless(os.environ.get('RUN_INTEGRATION_TESTS'), 
                        'Set RUN_INTEGRATION_TESTS=1 to run integration tests')
    def test_real_api_call(self):
        """Test real API call to GitHub"""
        client = GitHubAPIClient()
        
        # Test rate limit endpoint (doesn't require auth)
        rate_limit = client.get('/rate_limit')
        
        self.assertIn('resources', rate_limit)
        self.assertIn('core', rate_limit['resources'])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
