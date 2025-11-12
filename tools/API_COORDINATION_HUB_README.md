# API Coordination Hub

## Overview

The API Coordination Hub is a centralized system for managing and coordinating API calls across multiple services in the Chained project. It provides robust patterns for service resilience, rate limiting, and health monitoring.

## Features

### 🔒 Circuit Breaker Pattern
Protects against cascading failures by temporarily blocking calls to failing services.

- **States**: Closed (normal), Open (blocking), Half-Open (testing recovery)
- **Configurable thresholds** for failure counts and recovery attempts
- **Automatic recovery** testing after timeout periods
- **Fail-fast** behavior to prevent resource exhaustion

### 🚦 Rate Limiting
Token bucket algorithm for precise rate limit control.

- **Per-API rate limits** with independent token buckets
- **Automatic token refill** based on configured rates
- **Thread-safe** token consumption
- **Time estimation** for when tokens will be available

### 📊 Health Monitoring
Continuous monitoring of API health based on recent request history.

- **Health statuses**: Healthy, Degraded, Unhealthy, Unknown
- **Success rate tracking** over configurable windows
- **Latency metrics** (min, max, average)
- **Real-time health scoring** (0.0 - 1.0)

### 📈 Metrics Collection
Comprehensive metrics for observability and debugging.

- **Request counts** (total, successful, failed, rate-limited)
- **Latency statistics** (average, min, max)
- **Circuit breaker events** tracking
- **Health scores** and status history
- **JSON export** for integration with monitoring systems

## Installation

The API Coordination Hub is included in the Chained tools directory. No additional installation required.

```bash
# Ensure tools directory is in your Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/Chained/tools"
```

## Quick Start

### Basic Usage

```python
from api_coordination_hub import APICoordinationHub, APIConfig

# Create hub instance
hub = APICoordinationHub()

# Register an API
hub.register_api('github', APIConfig(
    rate_limit=5000,          # 5000 requests
    time_window=3600,         # per hour
    circuit_breaker_threshold=5  # open after 5 failures
))

# Use decorator for automatic coordination
@hub.coordinate('github')
def get_user_repos(username):
    # Your API call here
    return github_client.get(f'/users/{username}/repos')

# Make the call - coordination happens automatically
repos = get_user_repos('octocat')
```

### Manual Execution

```python
# Execute function with coordination
def fetch_data():
    return api_client.get('/data')

result = hub.execute('github', fetch_data)
```

### Singleton Pattern

```python
from api_coordination_hub import get_hub

# Get singleton hub instance (recommended for app-wide use)
hub = get_hub()
hub.register_api('myapi', APIConfig())
```

## Configuration

### APIConfig Parameters

```python
APIConfig(
    rate_limit=1000,              # Requests per time window
    time_window=3600,             # Time window in seconds
    circuit_breaker_threshold=5,  # Failures before opening circuit
    circuit_breaker_timeout=60,   # Seconds before trying recovery
    circuit_breaker_success_threshold=2,  # Successes to close circuit
    timeout=30,                   # Request timeout
    max_retries=3,                # Retry attempts
    priority=1                    # Priority level (1-10)
)
```

### Common Configurations

#### High-Volume API (GitHub)
```python
hub.register_api('github', APIConfig(
    rate_limit=5000,
    time_window=3600,
    circuit_breaker_threshold=10,
    circuit_breaker_timeout=300,
    priority=10
))
```

#### Rate-Limited Web Scraping
```python
hub.register_api('web-scraper', APIConfig(
    rate_limit=60,
    time_window=60,  # 1 request per second
    circuit_breaker_threshold=3,
    timeout=15,
    priority=5
))
```

#### Critical Internal Service
```python
hub.register_api('critical-service', APIConfig(
    rate_limit=10000,
    time_window=60,
    circuit_breaker_threshold=3,
    circuit_breaker_timeout=30,
    max_retries=5,
    priority=10
))
```

## Advanced Usage

### Monitoring Health

```python
# Check health status
status = hub.get_health_status('github')  # Returns HealthStatus enum
score = hub.get_health_score('github')    # Returns 0.0 - 1.0

if status == HealthStatus.UNHEALTHY:
    print("API is unhealthy, consider failover")
```

### Circuit Breaker Management

```python
# Check circuit state
state = hub.get_circuit_state('github')  # Returns CircuitState enum

# Manually reset circuit breaker
if state == CircuitState.OPEN:
    hub.reset_circuit_breaker('github')
```

### Metrics and Monitoring

```python
# Get metrics for specific API
metrics = hub.get_metrics('github')
print(f"Success rate: {metrics['success_rate']:.2%}")
print(f"Average latency: {metrics['average_latency']:.3f}s")

# Get all metrics
all_metrics = hub.get_all_metrics()

# Export to file
hub.export_metrics('/tmp/api_metrics.json')

# Print status dashboard
hub.print_status()
```

### Rate Limit Management

```python
# Check available tokens
available = hub.get_available_tokens('github')
print(f"Available requests: {available}")

# Handle rate limit exceptions
from api_coordination_hub import RateLimitExceeded

try:
    result = api_call()
except RateLimitExceeded as e:
    print(f"Rate limited: {e}")
    # Wait and retry
```

### Exception Handling

```python
from api_coordination_hub import RateLimitExceeded, CircuitBreakerOpen

@hub.coordinate('github')
def risky_call():
    return external_api.call()

try:
    result = risky_call()
except RateLimitExceeded as e:
    # Handle rate limiting
    print(f"Rate limited: {e}")
    # Maybe switch to cached data
except CircuitBreakerOpen as e:
    # Handle circuit breaker
    print(f"Service unavailable: {e}")
    # Use fallback service
except Exception as e:
    # Handle other errors
    print(f"API error: {e}")
```

## Integration Examples

### GitHub API Client Integration

```python
from github_integration import GitHubAPIClient
from api_coordination_hub import get_hub, APIConfig

hub = get_hub()
hub.register_api('github', APIConfig(
    rate_limit=5000,
    time_window=3600
))

client = GitHubAPIClient()

@hub.coordinate('github')
def get_repo_info(owner, repo):
    return client.get(f'/repos/{owner}/{repo}')

# Use with automatic coordination
repo = get_repo_info('enufacas', 'Chained')
```

### Web Content Fetcher Integration

```python
from fetch_web_content import WebContentFetcher
from api_coordination_hub import get_hub, APIConfig

hub = get_hub()
hub.register_api('web', APIConfig(
    rate_limit=60,
    time_window=60
))

fetcher = WebContentFetcher()

@hub.coordinate('web')
def fetch_url(url):
    return fetcher.fetch(url)

# Use with rate limiting
content = fetch_url('https://example.com')
```

### Multiple API Orchestration

```python
from api_coordination_hub import get_hub, APIConfig

hub = get_hub()

# Register multiple APIs
hub.register_api('github', APIConfig(rate_limit=5000, time_window=3600))
hub.register_api('web', APIConfig(rate_limit=60, time_window=60))
hub.register_api('database', APIConfig(rate_limit=1000, time_window=60))

@hub.coordinate('github')
def fetch_github_data():
    return github_client.get('/data')

@hub.coordinate('web')
def fetch_web_data():
    return web_client.get('/data')

@hub.coordinate('database')
def store_data(data):
    return db.insert(data)

# Orchestrate workflow
try:
    gh_data = fetch_github_data()
    web_data = fetch_web_data()
    store_data({**gh_data, **web_data})
except Exception as e:
    print(f"Workflow failed: {e}")
```

## Architecture

### Components

```
APICoordinationHub
├── TokenBucket (Rate Limiting)
│   ├── Token management
│   ├── Refill logic
│   └── Thread-safe operations
├── CircuitBreaker (Resilience)
│   ├── State management
│   ├── Failure detection
│   └── Recovery testing
├── APIHealthMonitor (Monitoring)
│   ├── Success rate tracking
│   ├── Health scoring
│   └── Window-based analysis
└── APIMetrics (Observability)
    ├── Request counting
    ├── Latency tracking
    └── Error recording
```

### Thread Safety

All components are thread-safe:
- Token buckets use locks for consumption
- Circuit breakers use locks for state transitions
- Health monitors use locks for result recording
- Hub-level operations are synchronized

### Performance Characteristics

- **Token consumption**: O(1) with lock contention
- **Circuit breaker check**: O(1) with lock contention
- **Health status**: O(n) where n = window size
- **Metrics collection**: O(1) amortized

## Testing

Run the comprehensive test suite:

```bash
cd /path/to/Chained/tools
python test_api_coordination_hub.py
```

Test coverage includes:
- Token bucket rate limiting
- Circuit breaker state transitions
- Health monitoring and scoring
- Metrics collection
- Concurrent access
- Integration scenarios

## Best Practices

### 1. Register APIs at Startup
```python
# In your application initialization
hub = get_hub()
hub.register_api('github', github_config)
hub.register_api('web', web_config)
```

### 2. Use Decorators for Clean Code
```python
@hub.coordinate('github')
def api_function():
    return client.get('/endpoint')
```

### 3. Monitor Health Regularly
```python
# Periodic health check
if hub.get_health_status('github') == HealthStatus.UNHEALTHY:
    alert_team()
```

### 4. Export Metrics for Monitoring
```python
# Export metrics periodically for monitoring systems
hub.export_metrics('/var/metrics/api_metrics.json')
```

### 5. Handle Exceptions Gracefully
```python
try:
    result = coordinated_call()
except CircuitBreakerOpen:
    # Use fallback
    result = fallback_data()
except RateLimitExceeded:
    # Queue for later
    queue.push(task)
```

### 6. Configure Appropriately
- Set rate limits below actual API limits (safety margin)
- Tune circuit breaker thresholds based on expected failure rates
- Adjust timeouts based on typical API latencies
- Set priorities for resource allocation

## Monitoring Dashboard

Use the built-in status dashboard:

```bash
python -m api_coordination_hub --status
```

Example output:
```
======================================================================
🔗 API Coordination Hub Status
======================================================================

✓ GITHUB
  Health: healthy (100.00%)
  Circuit: closed
  Tokens: 4850
  Requests: 150 (success: 100.00%)
  Latency: avg=0.234s

⚠ WEB
  Health: degraded (87.50%)
  Circuit: closed
  Tokens: 45
  Requests: 80 (success: 87.50%)
  Latency: avg=1.234s

======================================================================
```

## Troubleshooting

### Rate Limit Exceeded
**Problem**: Getting `RateLimitExceeded` exceptions
**Solutions**:
1. Increase `rate_limit` in config
2. Increase `time_window` for lower rate
3. Implement request queuing
4. Use caching to reduce calls

### Circuit Breaker Opens Frequently
**Problem**: Circuit breaker opens too often
**Solutions**:
1. Increase `circuit_breaker_threshold`
2. Check API service health
3. Add retry logic before circuit breaker
4. Increase `circuit_breaker_timeout` for faster recovery

### Poor Health Scores
**Problem**: APIs showing degraded or unhealthy status
**Solutions**:
1. Check network connectivity
2. Verify API credentials
3. Review error logs in metrics
4. Consider increasing timeouts
5. Check rate limiting settings

### High Latency
**Problem**: Metrics show high average latency
**Solutions**:
1. Optimize API calls (reduce payload, use filtering)
2. Increase timeout values
3. Check network conditions
4. Consider regional API endpoints
5. Implement caching

## Future Enhancements

Planned features:
- [ ] Adaptive rate limiting based on API headers
- [ ] Distributed coordination for multi-instance deployments
- [ ] Prometheus metrics export
- [ ] Request prioritization queue
- [ ] Automatic fallback strategies
- [ ] API cost tracking
- [ ] Load shedding during overload

## Contributing

To contribute to the API Coordination Hub:

1. Add tests for new features
2. Update documentation
3. Ensure thread safety
4. Follow existing patterns
5. Add examples for new use cases

## License

Part of the Chained project. See main LICENSE file.

## Support

For issues or questions:
- Open an issue in the Chained repository
- Check test files for usage examples
- Review inline code documentation

---

**Built by the Coordinate Wizard agent for the Chained autonomous AI ecosystem.**
