# API Call Batcher - Quick Start Guide

**Created by:** @accelerate-specialist  
**Purpose:** Reduce rate limit usage through intelligent request batching

## 🚀 Overview

The API Call Batcher is a high-performance tool that reduces API rate limit usage by:

- **Batching**: Grouping requests together to reduce total API calls
- **Deduplication**: Eliminating identical requests within a time window
- **Priority Queuing**: Ensuring critical requests are processed first
- **Auto-flushing**: Smart batching based on size and time thresholds

## 📦 Installation

```bash
# No additional dependencies needed - uses Python standard library
cd tools/
```

## 🎯 Quick Start

### Basic Usage

```python
from api_call_batcher import BatchedAPIClient, BatchConfig

# Create and start batcher
batcher = BatchedAPIClient()
batcher.start()

# Add requests
future = batcher.add_request('GET', '/api/users/123')

# Get result (blocks until ready)
result = future.result(timeout=5.0)

# Stop batcher when done
batcher.stop()
```

### With Configuration

```python
from api_call_batcher import BatchedAPIClient, BatchConfig

config = BatchConfig(
    batch_size=20,              # Max 20 requests per batch
    flush_interval=2.0,         # Auto-flush every 2 seconds
    enable_deduplication=True,  # Deduplicate identical requests
    dedup_window=60.0,          # 60-second dedup window
)

batcher = BatchedAPIClient(config)
batcher.start()
```

### Priority Requests

```python
# Higher priority requests are processed first
urgent = batcher.add_request('POST', '/api/alerts', priority=10)
normal = batcher.add_request('GET', '/api/data', priority=5)
background = batcher.add_request('GET', '/api/logs', priority=1)

# All will be batched, but urgent processed first
urgent_result = urgent.result()
```

### Custom Executor

```python
import requests

def github_api_executor(api_requests):
    """Execute requests against GitHub API"""
    results = []
    for req in api_requests:
        url = f"https://api.github.com{req.endpoint}"
        response = requests.request(
            req.method,
            url,
            params=req.params,
            headers=req.headers
        )
        results.append(response.json())
    return results

batcher = BatchedAPIClient(
    config=BatchConfig(batch_size=10),
    executor=github_api_executor
)
batcher.start()

# Now requests use real GitHub API
future = batcher.add_request('GET', '/users/octocat')
user_data = future.result()
```

## 📊 Monitoring

### Get Statistics

```python
stats = batcher.get_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Deduplicated: {stats['deduplicated_requests']}")
print(f"Reduction rate: {stats['reduction_rate']:.1%}")

# Or print formatted report
batcher.print_stats()
```

### Example Output

```
======================================================================
📦 API Call Batcher Statistics
======================================================================
Total Requests:        1000
Batched Requests:      1000
Deduplicated:          250
Batches Flushed:       50
Reduction Rate:        25.0%
Current Batch Size:    0
Pending Requests:      0
Cache Size:            150
======================================================================
```

## 🔧 Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `batch_size` | 10 | Maximum requests per batch |
| `flush_interval` | 5.0 | Auto-flush interval (seconds) |
| `enable_deduplication` | True | Enable request deduplication |
| `dedup_window` | 60.0 | Dedup cache window (seconds) |
| `max_queue_size` | 1000 | Maximum queued requests |
| `strategy` | ADAPTIVE | Batching strategy |

## 💡 Use Cases

### 1. GitHub API Rate Limiting

```python
# GitHub has 5000 requests/hour limit
# Batching can reduce this significantly

config = BatchConfig(batch_size=50, flush_interval=10.0)
batcher = BatchedAPIClient(config, executor=github_executor)
batcher.start()

# Fetch user data
users = ['user1', 'user2', 'user3']
futures = [batcher.add_request('GET', f'/users/{u}') for u in users]

# Wait for all results
results = [f.result() for f in futures]
```

### 2. Parallel Issue Processing

```python
# Process multiple issues efficiently
issues = [101, 102, 103, 104, 105]

futures = []
for issue_num in issues:
    future = batcher.add_request(
        'GET',
        f'/repos/owner/repo/issues/{issue_num}',
        priority=5
    )
    futures.append(future)

# Process results as they become available
for future in futures:
    issue_data = future.result()
    process_issue(issue_data)
```

### 3. Background Data Collection

```python
# Low-priority background tasks
for endpoint in background_endpoints:
    batcher.add_request(
        'GET',
        endpoint,
        priority=1  # Low priority
    )

# High-priority user request
user_future = batcher.add_request(
    'GET',
    f'/users/{current_user}',
    priority=10  # High priority - processed first
)
```

## 🎨 Integration with API Coordination Hub

```python
from api_coordination_hub import APICoordinationHub, APIConfig
from api_call_batcher import BatchedAPIClient, BatchConfig

# Set up coordination hub for rate limiting
hub = APICoordinationHub()
hub.register_api('github', APIConfig(rate_limit=5000, time_window=3600))

# Set up batcher for request optimization
batcher = BatchedAPIClient(BatchConfig(batch_size=20))
batcher.start()

@hub.coordinate('github', tokens=1)
def execute_github_batch(requests):
    """Execute batch with rate limit protection"""
    results = []
    for req in requests:
        # Make actual API call here
        results.append(make_api_call(req))
    return results

batcher = BatchedAPIClient(executor=execute_github_batch)
```

## 📈 Performance Tips

1. **Tune batch size**: Larger batches = fewer API calls but higher latency
2. **Adjust flush interval**: Shorter intervals = lower latency but more API calls
3. **Enable deduplication**: Massive savings for duplicate requests
4. **Use priorities**: Ensure critical requests aren't delayed
5. **Monitor stats**: Track reduction rate and adjust accordingly

## 🔍 Debugging

```python
# Check if requests are being processed
stats = batcher.get_stats()
if stats['pending_requests'] > 100:
    print("Warning: Queue is backing up!")

# Force immediate flush for debugging
batcher.flush()

# Check deduplication effectiveness
reduction = stats['deduplicated_requests'] / stats['total_requests']
if reduction < 0.1:
    print("Low deduplication - consider increasing dedup_window")
```

## 🚨 Common Pitfalls

1. **Forgetting to start**: Call `batcher.start()` before adding requests
2. **Not stopping**: Always call `batcher.stop()` to flush pending requests
3. **Too large batch_size**: Can cause memory issues with large payloads
4. **Too short dedup_window**: Reduces deduplication effectiveness
5. **Blocking main thread**: Use threading/async for result retrieval

## 🧪 Testing

```bash
# Run full test suite
python3 tools/test_api_call_batcher.py -v

# Run demo
python3 tools/api_call_batcher.py --demo --requests 100 --batch-size 10
```

## 📚 See Also

- [API Coordination Hub](API_COORDINATION_HUB_README.md) - Rate limiting & circuit breakers
- [API Performance Monitor](tools/api_performance_monitor.py) - Performance tracking
- [API Contract Validator](tools/api_contract_validator.py) - API validation

## 🤝 Contributing

This tool is part of the Chained autonomous AI ecosystem. Contributions and improvements are welcome!

---

**@accelerate-specialist** - Making APIs faster, one batch at a time! 🚀
