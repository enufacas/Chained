#!/usr/bin/env python3
"""
GitHub Integration Utilities

A robust GitHub API client with comprehensive error handling, retry logic,
rate limiting, and timeout management. Designed for reliable integration
with GitHub's REST and GraphQL APIs.

Features:
- Automatic retry with exponential backoff
- Rate limit detection and handling
- Comprehensive error handling with meaningful messages
- Request timeout management
- Response validation
- Logging for debugging
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from typing import Dict, Optional, Any, Callable
from functools import wraps
from dataclasses import dataclass
from enum import Enum


class RetryStrategy(Enum):
    """Retry strategy types"""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retry_on_rate_limit: bool = True


@dataclass
class GitHubAPIError:
    """Structured error information from GitHub API"""
    status_code: int
    message: str
    documentation_url: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[int] = None
    is_rate_limited: bool = False
    is_auth_error: bool = False
    is_not_found: bool = False


class GitHubAPIException(Exception):
    """Exception raised for GitHub API errors"""
    def __init__(self, error: GitHubAPIError):
        self.error = error
        super().__init__(error.message)


def retry_with_backoff(retry_config: Optional[RetryConfig] = None):
    """
    Decorator for retrying functions with configurable backoff strategy.
    
    Args:
        retry_config: Configuration for retry behavior
        
    Example:
        @retry_with_backoff(RetryConfig(max_attempts=5))
        def my_api_call():
            return make_request()
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            delay = retry_config.initial_delay
            
            while attempt < retry_config.max_attempts:
                try:
                    return func(*args, **kwargs)
                except GitHubAPIException as e:
                    attempt += 1
                    
                    # Don't retry on certain errors
                    if e.error.is_auth_error or e.error.is_not_found:
                        raise
                    
                    # Check if we should retry on rate limit
                    if e.error.is_rate_limited and not retry_config.retry_on_rate_limit:
                        raise
                    
                    # If this was the last attempt, raise the exception
                    if attempt >= retry_config.max_attempts:
                        raise
                    
                    # Calculate delay for rate limit
                    if e.error.is_rate_limited and e.error.rate_limit_reset:
                        # Wait until rate limit resets
                        wait_time = max(0, e.error.rate_limit_reset - time.time())
                        delay = min(wait_time + 1, retry_config.max_delay)
                    else:
                        # Calculate backoff delay
                        if retry_config.strategy == RetryStrategy.EXPONENTIAL:
                            delay = min(
                                retry_config.initial_delay * (retry_config.backoff_factor ** (attempt - 1)),
                                retry_config.max_delay
                            )
                        elif retry_config.strategy == RetryStrategy.LINEAR:
                            delay = min(
                                retry_config.initial_delay * attempt,
                                retry_config.max_delay
                            )
                        else:  # FIXED
                            delay = retry_config.initial_delay
                    
                    print(f"Attempt {attempt}/{retry_config.max_attempts} failed: {e.error.message}", file=sys.stderr)
                    print(f"Retrying in {delay:.1f} seconds...", file=sys.stderr)
                    time.sleep(delay)
                except Exception as e:
                    # For non-API errors, retry with backoff
                    attempt += 1
                    if attempt >= retry_config.max_attempts:
                        raise
                    
                    print(f"Attempt {attempt}/{retry_config.max_attempts} failed: {str(e)}", file=sys.stderr)
                    print(f"Retrying in {delay:.1f} seconds...", file=sys.stderr)
                    time.sleep(delay)
            
            # Should never reach here, but just in case
            raise Exception("Maximum retry attempts exceeded")
        
        return wrapper
    return decorator


class GitHubAPIClient:
    """
    Robust GitHub API client with error handling and retry logic.
    
    Features:
    - Automatic authentication
    - Rate limit handling
    - Retry with exponential backoff
    - Comprehensive error handling
    - Request timeout management
    
    Example:
        client = GitHubAPIClient(token="your_token")
        repo = client.get("/repos/owner/repo")
        issues = client.get("/repos/owner/repo/issues", params={"state": "open"})
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://api.github.com",
        timeout: int = 30,
        retry_config: Optional[RetryConfig] = None,
        user_agent: str = "Chained-GitHub-Integration/1.0"
    ):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub token (defaults to GITHUB_TOKEN env var)
            base_url: Base URL for GitHub API
            timeout: Request timeout in seconds
            retry_config: Configuration for retry behavior
            user_agent: User agent string for requests
        """
        self.token = token or os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_config = retry_config or RetryConfig()
        self.user_agent = user_agent
        
        if not self.token:
            print("Warning: No GitHub token provided. API requests will be rate-limited.", file=sys.stderr)
    
    def _build_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build request headers with authentication"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': self.user_agent
        }
        
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _parse_error_response(self, error: urllib.error.HTTPError) -> GitHubAPIError:
        """Parse error response from GitHub API"""
        try:
            error_data = json.loads(error.read().decode())
            message = error_data.get('message', 'Unknown error')
            documentation_url = error_data.get('documentation_url')
        except:
            message = f"HTTP {error.code}: {error.reason}"
            documentation_url = None
        
        # Extract rate limit information from headers
        rate_limit_remaining = error.headers.get('X-RateLimit-Remaining')
        rate_limit_reset = error.headers.get('X-RateLimit-Reset')
        
        return GitHubAPIError(
            status_code=error.code,
            message=message,
            documentation_url=documentation_url,
            rate_limit_remaining=int(rate_limit_remaining) if rate_limit_remaining else None,
            rate_limit_reset=int(rate_limit_reset) if rate_limit_reset else None,
            is_rate_limited=(error.code == 403 and rate_limit_remaining == '0'),
            is_auth_error=(error.code in [401, 403]),
            is_not_found=(error.code == 404)
        )
    
    @retry_with_backoff()
    def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Make HTTP request to GitHub API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            data: Request body data
            headers: Additional headers
            
        Returns:
            Parsed JSON response
            
        Raises:
            GitHubAPIException: On API errors
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        request_headers = self._build_headers(headers)
        
        # Prepare request
        request_data = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=request_data, headers=request_headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                # Check rate limit headers
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
                if rate_limit_remaining and int(rate_limit_remaining) < 10:
                    print(f"Warning: Only {rate_limit_remaining} API requests remaining", file=sys.stderr)
                
                # Parse response
                response_data = response.read().decode()
                if response_data:
                    return json.loads(response_data)
                return None
                
        except urllib.error.HTTPError as e:
            error = self._parse_error_response(e)
            raise GitHubAPIException(error)
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {e.reason}")
        except TimeoutError:
            raise Exception(f"Request timed out after {self.timeout} seconds")
    
    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make GET request to GitHub API.
        
        Args:
            path: API endpoint path
            params: Query parameters
            
        Returns:
            Parsed JSON response
        """
        if params:
            # Build query string
            query_parts = []
            for key, value in params.items():
                if isinstance(value, bool):
                    value = str(value).lower()
                query_parts.append(f"{key}={urllib.parse.quote(str(value))}")
            path = f"{path}?{'&'.join(query_parts)}"
        
        return self._make_request('GET', path)
    
    def post(self, path: str, data: Dict) -> Any:
        """
        Make POST request to GitHub API.
        
        Args:
            path: API endpoint path
            data: Request body data
            
        Returns:
            Parsed JSON response
        """
        return self._make_request('POST', path, data=data)
    
    def patch(self, path: str, data: Dict) -> Any:
        """
        Make PATCH request to GitHub API.
        
        Args:
            path: API endpoint path
            data: Request body data
            
        Returns:
            Parsed JSON response
        """
        return self._make_request('PATCH', path, data=data)
    
    def delete(self, path: str) -> Any:
        """
        Make DELETE request to GitHub API.
        
        Args:
            path: API endpoint path
            
        Returns:
            Parsed JSON response
        """
        return self._make_request('DELETE', path)
    
    def graphql(self, query: str, variables: Optional[Dict] = None) -> Any:
        """
        Execute GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Query variables
            
        Returns:
            Query result data
            
        Raises:
            GitHubAPIException: On API or query errors
        """
        data = {'query': query}
        if variables:
            data['variables'] = variables
        
        result = self.post('/graphql', data)
        
        # Check for GraphQL errors
        if 'errors' in result:
            error_messages = [err.get('message', 'Unknown error') for err in result['errors']]
            raise Exception(f"GraphQL errors: {', '.join(error_messages)}")
        
        return result.get('data')


def validate_response(response: Any, expected_fields: list) -> bool:
    """
    Validate that response contains expected fields.
    
    Args:
        response: API response to validate
        expected_fields: List of field names that should be present
        
    Returns:
        True if all expected fields are present
        
    Raises:
        ValueError: If response is missing expected fields
    """
    if not isinstance(response, dict):
        raise ValueError(f"Expected dict response, got {type(response)}")
    
    missing_fields = [field for field in expected_fields if field not in response]
    
    if missing_fields:
        raise ValueError(f"Response missing required fields: {', '.join(missing_fields)}")
    
    return True


# Example usage and testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test GitHub API integration')
    parser.add_argument('--token', help='GitHub token (or use GITHUB_TOKEN env var)')
    parser.add_argument('--repo', default='enufacas/Chained', help='Repository to test (owner/repo)')
    args = parser.parse_args()
    
    # Initialize client
    client = GitHubAPIClient(token=args.token)
    
    print("Testing GitHub API integration...")
    print(f"Repository: {args.repo}")
    print()
    
    try:
        # Test 1: Get repository info
        print("Test 1: Getting repository information...")
        repo = client.get(f"/repos/{args.repo}")
        print(f"✓ Repository: {repo['full_name']}")
        print(f"  Stars: {repo['stargazers_count']}")
        print(f"  Language: {repo['language']}")
        print()
        
        # Test 2: List issues
        print("Test 2: Listing open issues...")
        issues = client.get(f"/repos/{args.repo}/issues", params={"state": "open", "per_page": 5})
        print(f"✓ Found {len(issues)} open issues")
        for issue in issues[:3]:
            print(f"  #{issue['number']}: {issue['title']}")
        print()
        
        # Test 3: Get rate limit
        print("Test 3: Checking rate limit...")
        rate_limit = client.get("/rate_limit")
        core_limit = rate_limit['resources']['core']
        print(f"✓ Rate limit: {core_limit['remaining']}/{core_limit['limit']}")
        print(f"  Resets at: {time.ctime(core_limit['reset'])}")
        print()
        
        print("✓ All tests passed!")
        
    except GitHubAPIException as e:
        print(f"✗ API Error: {e.error.message}", file=sys.stderr)
        if e.error.documentation_url:
            print(f"  See: {e.error.documentation_url}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
