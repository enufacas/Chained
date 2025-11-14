# Performance Metrics Collection

**Author:** @assert-specialist  
**Category:** Monitoring  
**Status:** Implemented

## Overview

The Performance Metrics Collection system provides comprehensive monitoring and analysis of system performance across the Chained autonomous AI ecosystem. It tracks workflow execution times, API response times, resource utilization, and throughput to enable performance optimization and anomaly detection.

## Architecture

### Components

1. **Performance Collector** (`tools/performance-metrics-collector.py`)
   - Centralized metrics collection engine
   - Time-series data storage
   - Trend analysis
   - Threshold violation detection

2. **Data Models**
   - `WorkflowMetrics`: Workflow execution tracking
   - `APIMetrics`: API response time monitoring
   - `ResourceMetrics`: System resource utilization
   - `ThroughputMetrics`: Operations per second measurements
   - `PerformanceSnapshot`: Complete performance state

3. **Storage System**
   - Date-based directory structure: `.github/agent-system/metrics/performance/YYYY-MM-DD/`
   - Timestamped JSON files for historical data
   - `latest.json` for quick access to most recent snapshot

### Specification-Driven Design

Following **@assert-specialist**'s systematic approach, the system includes:

- **Pre-condition Assertions**: Validate all inputs before processing
- **Post-condition Assertions**: Verify outputs meet specifications
- **Edge Case Handling**: Comprehensive coverage of boundary conditions
- **State Validation**: Ensure data integrity at all transitions

## Features

### Metrics Collection

#### Workflow Metrics
```python
metrics = collector.collect_workflow_metrics(
    workflow_name="agent-evaluator",
    execution_time_ms=1500.5,
    status="success",
    run_id=12345
)
```

**Specifications:**
- `workflow_name` must not be empty
- `execution_time_ms` must be non-negative
- `status` must be one of: `success`, `failure`, `cancelled`

#### API Metrics
```python
metrics = collector.collect_api_metrics(
    endpoint="/api/agents",
    response_time_ms=250.5,
    status_code=200
)
```

**Specifications:**
- `endpoint` must not be empty
- `response_time_ms` must be non-negative
- `status_code` must be valid HTTP status (100-599)

#### Resource Metrics
```python
metrics = collector.collect_resource_metrics()
```

**Post-conditions:**
- All percentage values are between 0 and 100
- All size values are non-negative
- Reflects actual system state

#### Throughput Metrics
```python
metrics = collector.collect_throughput_metrics(
    operation_type="agent_matching",
    operations_count=1000,
    time_window_seconds=10.0
)
```

**Specifications:**
- `operation_type` must not be empty
- `operations_count` must be non-negative
- `time_window_seconds` must be positive

### Performance Snapshots

Create complete performance snapshots combining all metric types:

```python
snapshot = collector.create_snapshot(
    workflow_metrics=[wf_metrics],
    api_metrics=[api_metrics],
    include_resources=True,
    throughput_metrics=[tp_metrics]
)

collector.store_snapshot(snapshot)
```

### Trend Analysis

Analyze performance trends over time:

```python
snapshots = collector.load_snapshots(since_days=7)
trends = collector.analyze_performance_trends(snapshots)

# Access workflow trends
for workflow, stats in trends['workflow_trends'].items():
    print(f"{workflow}: avg={stats['avg_time_ms']:.2f}ms")

# Access resource trends
for resource, stats in trends['resource_trends'].items():
    print(f"{resource}: avg={stats['avg_percent']:.2f}%")

# Check threshold violations
for violation in trends['threshold_violations']:
    print(f"{violation['type']}: {violation['value']} > {violation['threshold']}")
```

### Reporting

Generate human-readable performance reports:

```python
report = collector.generate_report(since_days=7)
print(report)
```

## CLI Usage

### Collect Metrics

```bash
# Collect current performance metrics
python3 tools/performance-metrics-collector.py --collect

# Collect and output as JSON
python3 tools/performance-metrics-collector.py --collect --json
```

### Analyze Performance

```bash
# Analyze performance trends (last 7 days)
python3 tools/performance-metrics-collector.py --analyze

# Analyze specific time period
python3 tools/performance-metrics-collector.py --analyze --since 30

# Get JSON output
python3 tools/performance-metrics-collector.py --analyze --json
```

### Generate Reports

```bash
# Generate performance report
python3 tools/performance-metrics-collector.py --report

# Generate report for specific period
python3 tools/performance-metrics-collector.py --report --since 14
```

## Configuration

Performance thresholds can be configured in `.github/agent-system/config.json`:

```json
{
  "performance_thresholds": {
    "workflow_execution_time_ms": 30000,
    "api_response_time_ms": 5000,
    "memory_usage_mb": 1024,
    "cpu_usage_percent": 80.0,
    "storage_usage_percent": 85.0
  }
}
```

## Integration

### With GitHub Actions

Collect metrics in workflows:

```yaml
- name: Collect Performance Metrics
  run: |
    python3 tools/performance-metrics-collector.py --collect
```

### With Agent Evaluator

Track agent evaluation performance:

```python
from performance_metrics_collector import PerformanceCollector

collector = PerformanceCollector()

# Track evaluation time
start = time.time()
evaluate_agents()
elapsed_ms = (time.time() - start) * 1000

metrics = collector.collect_workflow_metrics(
    workflow_name="agent-evaluation",
    execution_time_ms=elapsed_ms,
    status="success"
)

snapshot = collector.create_snapshot(
    workflow_metrics=[metrics],
    include_resources=True
)
collector.store_snapshot(snapshot)
```

### With API Monitoring

Track API response times:

```python
import time
import requests

start = time.time()
response = requests.get("https://api.github.com/repos/enufacas/Chained")
elapsed_ms = (time.time() - start) * 1000

metrics = collector.collect_api_metrics(
    endpoint="/repos/enufacas/Chained",
    response_time_ms=elapsed_ms,
    status_code=response.status_code
)
```

## Testing

Comprehensive test suite with 100% coverage:

```bash
# Run all tests
python3 tests/test_performance_metrics_collector.py
```

### Test Categories

1. **Data Structure Tests**
   - Dataclass creation and serialization
   - Field validation
   - Type checking

2. **Pre-condition Tests**
   - Input validation
   - Boundary condition checking
   - Error handling

3. **Post-condition Tests**
   - Output validation
   - State verification
   - Consistency checking

4. **Edge Case Tests**
   - Zero operations
   - Very small time windows
   - Empty data sets
   - Concurrent operations

5. **Integration Tests**
   - Storage and retrieval
   - Trend analysis
   - Report generation
   - End-to-end workflows

## Data Format

### Snapshot Structure

```json
{
  "timestamp": "2025-11-14T06:39:54.832940+00:00",
  "workflow_metrics": [
    {
      "workflow_name": "agent-evaluator",
      "execution_time_ms": 1500.5,
      "status": "success",
      "timestamp": "2025-11-14T06:39:54.832917+00:00",
      "run_id": 12345
    }
  ],
  "api_metrics": [
    {
      "endpoint": "/api/agents",
      "response_time_ms": 250.5,
      "status_code": 200,
      "timestamp": "2025-11-14T06:39:54.832917+00:00"
    }
  ],
  "resource_metrics": {
    "memory_used_mb": 1546.19,
    "memory_percent": 9.7,
    "cpu_percent": 0.0,
    "disk_used_gb": 54.41,
    "disk_percent": 76.0,
    "timestamp": "2025-11-14T06:39:54.832917+00:00"
  },
  "throughput_metrics": [
    {
      "operation_type": "agent_matching",
      "operations_count": 1000,
      "time_window_seconds": 10.0,
      "operations_per_second": 100.0,
      "timestamp": "2025-11-14T06:39:54.832917+00:00"
    }
  ],
  "metadata": {
    "collector_version": "1.0.0",
    "thresholds": {
      "workflow_execution_time_ms": 30000,
      "api_response_time_ms": 5000,
      "memory_usage_mb": 1024,
      "cpu_usage_percent": 80.0,
      "storage_usage_percent": 85.0
    }
  }
}
```

## Best Practices

1. **Regular Collection**: Collect metrics at regular intervals (e.g., every workflow run)
2. **Threshold Configuration**: Adjust thresholds based on your specific environment
3. **Trend Monitoring**: Regularly review trend analysis to identify degradation
4. **Violation Alerts**: Set up alerts for threshold violations
5. **Storage Management**: Periodically archive old metrics to manage disk usage

## Troubleshooting

### No metrics collected
- Ensure psutil is installed: `pip install psutil`
- Check write permissions for metrics directory
- Verify configuration is valid

### Threshold violations
- Review actual vs. expected performance
- Adjust thresholds if they're too strict
- Investigate performance degradation causes

### Storage issues
- Check available disk space
- Review retention policies
- Archive old metrics if needed

## Future Enhancements

Potential improvements following **@assert-specialist**'s systematic approach:

- [ ] Automated performance regression detection
- [ ] Real-time alerting integration
- [ ] Performance optimization recommendations
- [ ] Machine learning-based anomaly detection
- [ ] Integration with external monitoring tools
- [ ] Performance baseline establishment
- [ ] Comparative analysis across time periods

## Credits

Implemented by **@assert-specialist** following a specification-driven, test-first approach with comprehensive assertion coverage and edge case handling.

---

**See Also:**
- [Agent Metrics Collector](../tools/agent-metrics-collector.py)
- [Creativity Metrics Analyzer](../tools/creativity-metrics-analyzer.py)
- [Performance Benchmark](../tools/performance_benchmark.py)
