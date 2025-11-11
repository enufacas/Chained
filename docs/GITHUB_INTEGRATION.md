# GitHub Integration Utilities Documentation

## Overview

The GitHub Integration Utilities provide a robust, production-ready client for interacting with GitHub's REST and GraphQL APIs. Built with reliability and error handling as top priorities, these utilities implement industry-standard integration patterns.

## Features

### Core Features
- **Automatic Retry Logic**: Configurable retry strategies with exponential backoff
- **Rate Limit Handling**: Automatic detection and intelligent waiting
- **Comprehensive Error Handling**: Structured error responses with actionable information
- **Request Timeout Management**: Prevent hanging requests
- **Response Validation**: Ensure API responses contain expected data
- **Authentication**: Automatic token-based authentication
- **Both REST and GraphQL**: Support for both API types

### Integration Patterns Implemented

#### 1. Retry with Exponential Backoff
Automatically retries failed requests with increasing delays between attempts.

```python
from tools.github_integration import GitHubAPIClient, RetryConfig, RetryStrategy

# Configure retry behavior
retry_config = RetryConfig(
    max_attempts=5,
    initial_delay=1.0,
    max_delay=60.0,
    backoff_factor=2.0,
    strategy=RetryStrategy.EXPONENTIAL
)

client = GitHubAPIClient(retry_config=retry_config)
```

#### 2. Rate Limit Awareness
Monitors rate limits and waits when necessary.

```python
# Client automatically handles rate limits
repo = client.get('/repos/owner/repo')

# Warns when approaching rate limit
# Waits and retries when rate limited
```

#### 3. Timeout Management
Prevents requests from hanging indefinitely.

```python
# Set custom timeout (default: 30 seconds)
client = GitHubAPIClient(timeout=60)
```

#### 4. Error Classification
Distinguishes between different error types for appropriate handling.

```python
try:
    repo = client.get('/repos/owner/repo')
except GitHubAPIException as e:
    if e.error.is_rate_limited:
        print("Rate limited, wait and retry")
    elif e.error.is_auth_error:
        print("Authentication failed")
    elif e.error.is_not_found:
        print("Resource not found")
    else:
        print(f"Error: {e.error.message}")
```

## Usage

### Basic Usage

#### Initialize Client

```python
from tools.github_integration import GitHubAPIClient

# With token from environment (GITHUB_TOKEN or GH_TOKEN)
client = GitHubAPIClient()

# With explicit token
client = GitHubAPIClient(token="your_github_token")

# With custom configuration
client = GitHubAPIClient(
    token="your_token",
    timeout=60,
    retry_config=RetryConfig(max_attempts=5)
)
```

#### Make REST API Calls

```python
# GET request
repo = client.get('/repos/owner/repo')
print(f"Stars: {repo['stargazers_count']}")

# GET with query parameters
issues = client.get('/repos/owner/repo/issues', params={
    'state': 'open',
    'per_page': 10
})

# POST request
new_issue = client.post('/repos/owner/repo/issues', data={
    'title': 'Bug report',
    'body': 'Description of the bug'
})

# PATCH request
updated_issue = client.patch('/repos/owner/repo/issues/1', data={
    'state': 'closed'
})

# DELETE request
client.delete('/repos/owner/repo/issues/comments/123')
```

#### Make GraphQL Queries

```python
# Execute GraphQL query
query = '''
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    name
    stargazerCount
    issues(first: 5, states: OPEN) {
      nodes {
        number
        title
      }
    }
  }
}
'''

result = client.graphql(query, variables={
    'owner': 'owner',
    'name': 'repo'
})

repo = result['repository']
print(f"Stars: {repo['stargazerCount']}")
```

### Advanced Usage

#### Custom Retry Decorator

```python
from tools.github_integration import retry_with_backoff, RetryConfig, RetryStrategy

@retry_with_backoff(RetryConfig(
    max_attempts=5,
    initial_delay=2.0,
    backoff_factor=3.0,
    strategy=RetryStrategy.EXPONENTIAL
))
def my_api_operation():
    # Your API call here
    return client.get('/some/endpoint')

result = my_api_operation()
```

#### Response Validation

```python
from tools.github_integration import validate_response

response = client.get('/repos/owner/repo')

# Ensure response has required fields
validate_response(response, ['id', 'name', 'full_name'])
```

#### Error Handling

```python
from tools.github_integration import GitHubAPIClient, GitHubAPIException

client = GitHubAPIClient()

try:
    repo = client.get('/repos/nonexistent/repo')
except GitHubAPIException as e:
    error = e.error
    
    print(f"Status: {error.status_code}")
    print(f"Message: {error.message}")
    
    if error.documentation_url:
        print(f"Docs: {error.documentation_url}")
    
    if error.is_rate_limited:
        print(f"Rate limit resets at: {error.rate_limit_reset}")
```

## API Reference

### GitHubAPIClient

#### Constructor

```python
GitHubAPIClient(
    token: Optional[str] = None,
    base_url: str = "https://api.github.com",
    timeout: int = 30,
    retry_config: Optional[RetryConfig] = None,
    user_agent: str = "Chained-GitHub-Integration/1.0"
)
```

**Parameters:**
- `token`: GitHub token (defaults to GITHUB_TOKEN env var)
- `base_url`: Base URL for GitHub API
- `timeout`: Request timeout in seconds
- `retry_config`: Configuration for retry behavior
- `user_agent`: User agent string for requests

#### Methods

##### get(path, params=None)
Make GET request to GitHub API.

```python
repo = client.get('/repos/owner/repo')
issues = client.get('/repos/owner/repo/issues', params={'state': 'open'})
```

##### post(path, data)
Make POST request to GitHub API.

```python
issue = client.post('/repos/owner/repo/issues', data={'title': 'Bug'})
```

##### patch(path, data)
Make PATCH request to GitHub API.

```python
updated = client.patch('/repos/owner/repo/issues/1', data={'state': 'closed'})
```

##### delete(path)
Make DELETE request to GitHub API.

```python
client.delete('/repos/owner/repo/issues/comments/123')
```

##### graphql(query, variables=None)
Execute GraphQL query.

```python
data = client.graphql('query { viewer { login } }')
```

### RetryConfig

Configuration for retry behavior.

```python
@dataclass
class RetryConfig:
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retry_on_rate_limit: bool = True
```

**Fields:**
- `max_attempts`: Maximum number of retry attempts
- `initial_delay`: Initial delay between retries (seconds)
- `max_delay`: Maximum delay between retries (seconds)
- `backoff_factor`: Multiplier for exponential backoff
- `strategy`: Retry strategy (EXPONENTIAL, LINEAR, or FIXED)
- `retry_on_rate_limit`: Whether to retry on rate limit errors

### RetryStrategy

Enum for retry strategies.

```python
class RetryStrategy(Enum):
    EXPONENTIAL = "exponential"  # Delay doubles each retry
    LINEAR = "linear"            # Delay increases linearly
    FIXED = "fixed"              # Constant delay
```

### GitHubAPIError

Structured error information.

```python
@dataclass
class GitHubAPIError:
    status_code: int
    message: str
    documentation_url: Optional[str] = None
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[int] = None
    is_rate_limited: bool = False
    is_auth_error: bool = False
    is_not_found: bool = False
```

### GitHubAPIException

Exception raised for GitHub API errors.

```python
try:
    client.get('/invalid')
except GitHubAPIException as e:
    print(e.error.message)
```

## Best Practices

### 1. Always Use Retry Logic for Production

```python
# Good
client = GitHubAPIClient(retry_config=RetryConfig(max_attempts=5))

# Not recommended for production
client = GitHubAPIClient(retry_config=RetryConfig(max_attempts=1))
```

### 2. Handle Specific Error Types

```python
try:
    data = client.get('/repos/owner/repo')
except GitHubAPIException as e:
    if e.error.is_not_found:
        # Handle missing resource
        pass
    elif e.error.is_auth_error:
        # Handle authentication issues
        pass
    elif e.error.is_rate_limited:
        # Wait and retry later
        pass
    else:
        # Handle other errors
        raise
```

### 3. Validate Critical Responses

```python
from tools.github_integration import validate_response

repo = client.get('/repos/owner/repo')
validate_response(repo, ['id', 'name', 'owner'])
```

### 4. Use Appropriate Timeouts

```python
# Short timeout for health checks
health_client = GitHubAPIClient(timeout=5)

# Longer timeout for complex operations
data_client = GitHubAPIClient(timeout=60)
```

### 5. Monitor Rate Limits

```python
# Check rate limit status
rate_limit = client.get('/rate_limit')
core = rate_limit['resources']['core']

print(f"Remaining: {core['remaining']}/{core['limit']}")
print(f"Resets at: {time.ctime(core['reset'])}")
```

## Testing

### Run Unit Tests

```bash
python3 test_github_integration.py -v
```

### Run Integration Tests

Integration tests make real API calls and are skipped by default.

```bash
RUN_INTEGRATION_TESTS=1 python3 test_github_integration.py -v
```

### Test with Real API

```bash
python3 tools/github_integration.py --repo owner/repo
```

## Migration Guide

### Migrating from urllib

**Before:**
```python
import urllib.request
import json

url = "https://api.github.com/repos/owner/repo"
headers = {'Authorization': f'token {token}'}
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"Error: {e.code}")
```

**After:**
```python
from tools.github_integration import GitHubAPIClient, GitHubAPIException

client = GitHubAPIClient(token=token)

try:
    data = client.get('/repos/owner/repo')
except GitHubAPIException as e:
    print(f"Error: {e.error.message}")
```

### Migrating from subprocess gh

**Before:**
```bash
gh api /repos/owner/repo --jq '.stargazers_count'
```

**After:**
```python
from tools.github_integration import GitHubAPIClient

client = GitHubAPIClient()
repo = client.get('/repos/owner/repo')
print(repo['stargazers_count'])
```

## Examples

### Example 1: List and Filter Issues

```python
from tools.github_integration import GitHubAPIClient

client = GitHubAPIClient()

# Get open issues
issues = client.get('/repos/owner/repo/issues', params={
    'state': 'open',
    'labels': 'bug',
    'per_page': 100
})

# Filter and process
critical_issues = [
    issue for issue in issues
    if 'critical' in issue['title'].lower()
]

print(f"Found {len(critical_issues)} critical issues")
```

### Example 2: Create Issue with Retry

```python
from tools.github_integration import GitHubAPIClient, RetryConfig

# Configure aggressive retry
client = GitHubAPIClient(retry_config=RetryConfig(
    max_attempts=10,
    initial_delay=1.0,
    max_delay=120.0
))

# Create issue (will retry on transient failures)
issue = client.post('/repos/owner/repo/issues', data={
    'title': 'Important Bug Report',
    'body': 'Description of the issue',
    'labels': ['bug', 'critical']
})

print(f"Created issue #{issue['number']}")
```

### Example 3: Bulk Operations with Rate Limit Handling

```python
from tools.github_integration import GitHubAPIClient

client = GitHubAPIClient()

repos = ['repo1', 'repo2', 'repo3', 'repo4', 'repo5']

for repo in repos:
    try:
        data = client.get(f'/repos/owner/{repo}')
        print(f"{repo}: {data['stargazers_count']} stars")
    except GitHubAPIException as e:
        if e.error.is_rate_limited:
            # Will automatically wait and retry
            print(f"Rate limited, waiting...")
        else:
            print(f"Error fetching {repo}: {e.error.message}")
```

## Troubleshooting

### Problem: Rate Limited Immediately

**Solution:** Ensure you're providing a valid GitHub token.

```python
client = GitHubAPIClient(token="your_token")
```

### Problem: Timeouts on Large Operations

**Solution:** Increase timeout value.

```python
client = GitHubAPIClient(timeout=120)
```

### Problem: Too Many Retries

**Solution:** Adjust retry configuration.

```python
client = GitHubAPIClient(retry_config=RetryConfig(
    max_attempts=3,
    max_delay=30.0
))
```

## Contributing

When adding new integration features:

1. **Add comprehensive error handling**
2. **Include retry logic where appropriate**
3. **Add tests for error scenarios**
4. **Document integration patterns**
5. **Test with real API calls**

## License

Part of the Chained project. See main LICENSE file.
