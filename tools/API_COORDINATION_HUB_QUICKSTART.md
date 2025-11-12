# API Coordination Hub - Quick Reference

## Installation
```bash
# No installation needed - included in Chained tools
cd /path/to/Chained/tools
```

## Quick Start (30 seconds)
```python
from api_coordination_hub import get_hub, APIConfig

# 1. Get hub
hub = get_hub()

# 2. Register API
hub.register_api('myapi', APIConfig(rate_limit=100, time_window=60))

# 3. Use decorator
@hub.coordinate('myapi')
def my_api_call():
    return api_client.get('/data')

# 4. Make call (coordination automatic!)
result = my_api_call()
```

## Common Configurations

### GitHub API
```python
hub.register_api('github', APIConfig(
    rate_limit=5000,
    time_window=3600,
    circuit_breaker_threshold=10
))
```

### Web Scraping (1 req/sec)
```python
hub.register_api('web', APIConfig(
    rate_limit=60,
    time_window=60
))
```

### Critical Service
```python
hub.register_api('critical', APIConfig(
    rate_limit=1000,
    circuit_breaker_threshold=3,
    circuit_breaker_timeout=30
))
```

## Essential Commands

### Check Health
```python
status = hub.get_health_status('myapi')  # HEALTHY/DEGRADED/UNHEALTHY
score = hub.get_health_score('myapi')    # 0.0 - 1.0
```

### Check Rate Limits
```python
tokens = hub.get_available_tokens('myapi')
state = hub.get_circuit_state('myapi')    # CLOSED/OPEN/HALF_OPEN
```

### Get Metrics
```python
metrics = hub.get_metrics('myapi')
print(f"Success rate: {metrics['success_rate']:.2%}")
print(f"Avg latency: {metrics['average_latency']:.3f}s")
```

### Status Dashboard
```python
hub.print_status()  # Shows all APIs
```

### Export Metrics
```python
hub.export_metrics('/tmp/metrics.json')
```

## Exception Handling

```python
from api_coordination_hub import RateLimitExceeded, CircuitBreakerOpen

try:
    result = coordinated_call()
except RateLimitExceeded as e:
    # Wait and retry
    time.sleep(10)
except CircuitBreakerOpen as e:
    # Use fallback
    result = cached_data()
```

## Testing

```bash
# Run tests
python tools/test_api_coordination_hub.py

# Run demo
python tools/api_coordination_hub.py --demo

# Run examples
python tools/examples/api_coordination_hub_examples.py
```

## Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| rate_limit | 1000 | Requests per time window |
| time_window | 3600 | Time window in seconds |
| circuit_breaker_threshold | 5 | Failures before opening |
| circuit_breaker_timeout | 60 | Seconds before recovery test |
| circuit_breaker_success_threshold | 2 | Successes to close circuit |
| timeout | 30 | Request timeout |
| max_retries | 3 | Retry attempts |
| priority | 1 | Priority (1-10) |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Rate limit hit | Increase `rate_limit` or `time_window` |
| Circuit opens | Increase `circuit_breaker_threshold` |
| High latency | Check metrics, optimize calls |
| Low health score | Check error logs in metrics |

## Files

- `tools/api_coordination_hub.py` - Main implementation
- `tools/test_api_coordination_hub.py` - Test suite
- `tools/API_COORDINATION_HUB_README.md` - Full documentation
- `tools/examples/api_coordination_hub_examples.py` - Examples

## Links

- Full Documentation: `tools/API_COORDINATION_HUB_README.md`
- Implementation Summary: `KNUTH_API_COORDINATION_HUB_IMPLEMENTATION.md`
- Test Suite: `tools/test_api_coordination_hub.py`
- Examples: `tools/examples/api_coordination_hub_examples.py`
