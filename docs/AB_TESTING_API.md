# A/B Testing API Documentation

**Author**: @APIs-architect  
**System**: Chained Autonomous AI  
**Version**: 1.0.0

---

## Overview

The A/B Testing API provides a comprehensive programmatic interface for managing autonomous A/B testing experiments on workflow configurations. Built with Margaret Hamilton's principles of rigorous and systematic design, this API enables seamless integration with external systems, workflows, and automation tools.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    A/B Testing API Layer                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │        Experiment Management API              │    │
│  │  • Create, Read, Update, Complete             │    │
│  │  • List with filters and pagination           │    │
│  │  • Status and health checks                   │    │
│  └───────────────────────────────────────────────┘    │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │          Metrics Collection API               │    │
│  │  • Record performance samples                 │    │
│  │  • Retrieve aggregated metrics                │    │
│  │  • Per-variant statistics                     │    │
│  └───────────────────────────────────────────────┘    │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │          Analysis & Insights API              │    │
│  │  • Statistical analysis                       │    │
│  │  • Winner determination                       │    │
│  │  • Confidence intervals                       │    │
│  └───────────────────────────────────────────────┘    │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │         Autonomous Operations API             │    │
│  │  • Opportunity discovery                      │    │
│  │  • Auto-experiment creation                   │    │
│  │  • System status monitoring                   │    │
│  └───────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
           │                                    │
           ▼                                    ▼
  ┌──────────────────┐              ┌──────────────────┐
  │  Workflow        │              │  External        │
  │  Integration     │              │  Systems         │
  └──────────────────┘              └──────────────────┘
```

## Core Components

### 1. ABTestingAPI (`tools/ab_testing_api.py`)

Main API class providing programmatic access to all A/B testing functionality.

**Features:**
- ✅ HTTP-style status codes for responses
- ✅ Comprehensive error handling
- ✅ Validation of all inputs
- ✅ Atomic operations
- ✅ CLI interface

### 2. WorkflowIntegration (`tools/ab_testing_integration.py`)

Helper class for seamless workflow integration with experiments.

**Features:**
- ✅ Automatic variant selection
- ✅ Simplified metrics recording
- ✅ Fallback to default configs
- ✅ Error resilience

---

## API Reference

### Experiment Management

#### Create Experiment

```python
from ab_testing_api import ABTestingAPI

api = ABTestingAPI()

status_code, response = api.create_experiment(
    name="Workflow Timeout Optimization",
    description="Testing different timeout values",
    variants={
        "control": {"timeout": 300},
        "increased": {"timeout": 450},
        "decreased": {"timeout": 150}
    },
    metrics=["execution_time", "success_rate"],
    workflow_name="my-workflow",
    priority="high"
)

if status_code == 201:
    experiment_id = response["experiment_id"]
    print(f"Created experiment: {experiment_id}")
```

**Response (201 Created):**
```json
{
  "success": true,
  "experiment_id": "exp-abc123",
  "message": "Experiment 'Workflow Timeout Optimization' created successfully",
  "details": {
    "name": "Workflow Timeout Optimization",
    "workflow": "my-workflow",
    "variant_count": 3,
    "metrics": ["execution_time", "success_rate"],
    "priority": "high"
  }
}
```

**Error Responses:**
- `400 BAD_REQUEST`: Invalid inputs (empty name, insufficient variants, no metrics)
- `409 CONFLICT`: Experiment already exists
- `500 INTERNAL_SERVER_ERROR`: Unexpected error

---

#### Get Experiment

```python
status_code, response = api.get_experiment("exp-abc123")

if status_code == 200:
    experiment = response["experiment"]
    print(f"Status: {experiment['status']}")
    print(f"Variants: {list(experiment['variants'].keys())}")
```

**Response (200 OK):**
```json
{
  "success": true,
  "experiment": {
    "id": "exp-abc123",
    "name": "Workflow Timeout Optimization",
    "status": "active",
    "created_at": "2025-11-22T12:00:00Z",
    "variants": {
      "control": { ... },
      "increased": { ... },
      "decreased": { ... }
    },
    "metrics": ["execution_time", "success_rate"]
  }
}
```

---

#### List Experiments

```python
status_code, response = api.list_experiments(
    status="active",
    workflow_name="my-workflow",
    limit=10,
    offset=0
)

for exp in response["experiments"]:
    print(f"{exp['id']}: {exp['name']}")
```

**Response (200 OK):**
```json
{
  "success": true,
  "experiments": [ ... ],
  "pagination": {
    "total": 25,
    "limit": 10,
    "offset": 0,
    "returned": 10
  }
}
```

---

#### Complete Experiment

```python
status_code, response = api.complete_experiment(
    experiment_id="exp-abc123",
    winner="increased",
    notes="Increased timeout showed 20% improvement"
)

if status_code == 200:
    print(f"Winner: {response['winner']}")
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Experiment 'exp-abc123' completed",
  "winner": "increased"
}
```

---

### Metrics Management

#### Record Sample

```python
status_code, response = api.record_sample(
    experiment_id="exp-abc123",
    variant_name="control",
    metrics={
        "execution_time": 285.5,
        "success_rate": 0.95,
        "resource_usage": 42.3
    },
    metadata={
        "run_id": "12345",
        "timestamp": "2025-11-22T12:30:00Z"
    }
)
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Sample recorded successfully",
  "experiment_id": "exp-abc123",
  "variant": "control",
  "metrics": {
    "execution_time": 285.5,
    "success_rate": 0.95,
    "resource_usage": 42.3
  }
}
```

---

#### Get Metrics

```python
# Get metrics for all variants
status_code, response = api.get_metrics("exp-abc123")

# Get metrics for specific variant
status_code, response = api.get_metrics("exp-abc123", "control")
```

**Response (200 OK):**
```json
{
  "success": true,
  "experiment_id": "exp-abc123",
  "variants": {
    "control": {
      "metrics": {
        "execution_time": [285.5, 290.0, 280.2],
        "success_rate": [0.95, 0.97, 0.94]
      },
      "sample_count": 3
    },
    "increased": { ... },
    "decreased": { ... }
  }
}
```

---

### Analysis

#### Analyze Experiment

```python
status_code, response = api.analyze_experiment("exp-abc123")

if status_code == 200:
    analysis = response["analysis"]
    if analysis["status"] == "analyzed" and analysis.get("winner"):
        winner = analysis["winner"]
        print(f"Winner: {winner['variant']}")
        print(f"Improvement: {winner['improvement']:.2%}")
        print(f"Confidence: {winner['confidence']}")
```

**Response (200 OK):**
```json
{
  "success": true,
  "experiment_id": "exp-abc123",
  "analysis": {
    "status": "analyzed",
    "variant_statistics": { ... },
    "winner": {
      "variant": "increased",
      "score": 85.2,
      "improvement": 0.20,
      "confidence": "high"
    },
    "advanced_analysis": {
      "bayesian_analysis": { ... },
      "sequential_test": { ... },
      "confidence_intervals": { ... }
    }
  }
}
```

---

### Autonomous Operations

#### Discover Opportunities

```python
status_code, response = api.discover_opportunities()

print(f"Found {response['opportunities_found']} opportunities")
for opp in response["opportunities"]:
    print(f"- {opp['workflow']}: {opp['type']} ({opp['priority']})")
```

**Response (200 OK):**
```json
{
  "success": true,
  "opportunities_found": 15,
  "opportunities": [
    {
      "workflow": "my-workflow",
      "type": "timeout_optimization",
      "priority": "high",
      "suggested_variants": { ... }
    },
    ...
  ]
}
```

---

#### Auto-Create Experiments

```python
# Dry run - see what would be created
status_code, response = api.auto_create_experiments(
    max_concurrent=5,
    dry_run=True
)

# Actually create experiments
status_code, response = api.auto_create_experiments(max_concurrent=5)

print(f"Created {len(response['cycle_results']['experiments_created'])} experiments")
print(f"Detected {len(response['cycle_results']['winners_detected'])} winners")
```

---

#### Get System Status

```python
status_code, response = api.get_system_status()

stats = response["statistics"]
print(f"Total Experiments: {stats['total_experiments']}")
print(f"Active: {stats['active_experiments']}")
print(f"Completed: {stats['completed_experiments']}")
```

**Response (200 OK):**
```json
{
  "success": true,
  "status": "operational",
  "statistics": {
    "total_experiments": 42,
    "active_experiments": 5,
    "completed_experiments": 37,
    "registry_path": ".github/agent-system/ab_tests_registry.json"
  },
  "active_experiments": [ ... ]
}
```

---

## Workflow Integration

### Quick Setup

```python
from ab_testing_integration import setup_workflow_testing

# Setup A/B testing for your workflow
integration, config = setup_workflow_testing(
    workflow_name="my-workflow",
    default_config={"timeout": 300, "max_retries": 3}
)

# Use the config (either from experiment or default)
print(f"Using timeout: {config['timeout']}")
```

### Full Integration Example

```python
from ab_testing_integration import WorkflowIntegration
import time

# Initialize
integration = WorkflowIntegration("my-workflow")

# Get configuration (participates in experiment if one exists)
config = integration.participate(default_config={"timeout": 300})

# Run your workflow with the config
start_time = time.time()
try:
    # ... your workflow logic here ...
    success = run_workflow(config)
    
    if success:
        # Record successful run
        execution_time = time.time() - start_time
        integration.record_success(
            execution_time=execution_time,
            metrics={"custom_metric": 42}
        )
    else:
        # Record failure
        execution_time = time.time() - start_time
        integration.record_failure(
            execution_time=execution_time,
            error="Workflow failed"
        )
        
except Exception as e:
    # Record error
    execution_time = time.time() - start_time
    integration.record_failure(
        execution_time=execution_time,
        error=str(e)
    )
```

---

## CLI Usage

### API CLI

```bash
# Get system status
python3 tools/ab_testing_api.py status

# List experiments
python3 tools/ab_testing_api.py list --status active --workflow my-workflow

# Get experiment details
python3 tools/ab_testing_api.py get exp-abc123

# Analyze experiment
python3 tools/ab_testing_api.py analyze exp-abc123

# Discover opportunities
python3 tools/ab_testing_api.py discover

# Auto-create experiments (dry run)
python3 tools/ab_testing_api.py auto-create --dry-run --max-concurrent 5

# Auto-create experiments (live)
python3 tools/ab_testing_api.py auto-create --max-concurrent 5
```

### Integration CLI

```bash
# Participate in experiment
python3 tools/ab_testing_integration.py participate my-workflow \
  --default-config '{"timeout": 300}'

# Record metrics
python3 tools/ab_testing_integration.py record my-workflow \
  --experiment-id exp-abc123 \
  --variant control \
  --execution-time 285.5 \
  --success \
  --metrics '{"resource_usage": 42.3}'
```

---

## Error Handling

All API methods return a tuple of `(status_code, response_dict)`.

### Status Codes

- **200 OK**: Successful request
- **201 CREATED**: Resource created successfully
- **400 BAD_REQUEST**: Invalid input
- **404 NOT_FOUND**: Resource not found
- **409 CONFLICT**: Resource conflict (duplicate)
- **500 INTERNAL_SERVER_ERROR**: Unexpected error

### Error Response Format

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": "Additional error details (optional)"
}
```

### Best Practices

1. **Always check status codes** before accessing response data
2. **Handle errors gracefully** with appropriate fallbacks
3. **Log errors** for debugging and monitoring
4. **Use try-except** blocks around API calls
5. **Provide meaningful error messages** to users

---

## Testing

Comprehensive test suite available in `tests/test_ab_testing_api.py`:

```bash
# Run all API tests
python3 tests/test_ab_testing_api.py -v

# Run specific test class
python3 tests/test_ab_testing_api.py TestABTestingAPI -v

# Run specific test
python3 tests/test_ab_testing_api.py TestABTestingAPI.test_create_experiment_success
```

**Test Coverage:**
- ✅ Experiment management (21 tests)
- ✅ Metrics collection and retrieval
- ✅ Analysis functionality
- ✅ Workflow integration
- ✅ Error handling
- ✅ Edge cases

---

## Integration Examples

### GitHub Actions Workflow

```yaml
name: My Workflow with A/B Testing

on: [push]

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Participate in A/B test
        id: ab_test
        run: |
          CONFIG=$(python3 tools/ab_testing_integration.py participate my-workflow \
            --default-config '{"timeout": 300}')
          echo "config=$CONFIG" >> $GITHUB_OUTPUT
      
      - name: Run with config
        id: run
        run: |
          START_TIME=$(date +%s)
          # ... your workflow logic ...
          END_TIME=$(date +%s)
          EXEC_TIME=$((END_TIME - START_TIME))
          echo "execution_time=$EXEC_TIME" >> $GITHUB_OUTPUT
      
      - name: Record metrics
        if: always()
        run: |
          python3 tools/ab_testing_integration.py record my-workflow \
            --experiment-id ${{ steps.ab_test.outputs.experiment_id }} \
            --variant ${{ steps.ab_test.outputs.variant }} \
            --execution-time ${{ steps.run.outputs.execution_time }} \
            ${{ steps.run.outcome == 'success' && '--success' || '' }}
```

### Python Script Integration

```python
#!/usr/bin/env python3
"""
Example script with A/B testing integration.
"""

from ab_testing_integration import WorkflowIntegration
import time

def main():
    # Setup A/B testing
    integration = WorkflowIntegration("my-script")
    config = integration.participate({
        "batch_size": 100,
        "timeout": 300,
        "max_retries": 3
    })
    
    print(f"Running with config: {config}")
    
    # Run with timing
    start = time.time()
    try:
        result = run_task(config)
        execution_time = time.time() - start
        
        if result.success:
            integration.record_success(
                execution_time=execution_time,
                metrics={
                    "items_processed": result.count,
                    "errors": result.errors
                }
            )
        else:
            integration.record_failure(
                execution_time=execution_time,
                error=result.error_message
            )
    
    except Exception as e:
        execution_time = time.time() - start
        integration.record_failure(
            execution_time=execution_time,
            error=str(e)
        )
        raise

if __name__ == "__main__":
    main()
```

---

## Performance Considerations

### API Performance

- **Atomic writes**: Registry updates use temp file + rename pattern
- **Lazy loading**: Experiments loaded only when needed
- **Efficient filtering**: In-memory filtering for list operations
- **Minimal overhead**: API calls typically complete in < 10ms

### Workflow Integration Performance

- **Negligible overhead**: < 5ms for participation check
- **Async recording**: Metrics recording doesn't block workflow
- **Graceful degradation**: Falls back to default on errors
- **No external dependencies**: Pure Python, no network calls

---

## Security Considerations

### Access Control

- Registry file permissions should be restricted
- API provides no authentication (designed for internal use)
- Validate all inputs before processing

### Data Integrity

- Atomic writes prevent corruption
- Validation prevents invalid data
- Automatic recovery from corruption

### Best Practices

1. **Run API in trusted environments** only
2. **Validate experiment configurations** before applying
3. **Monitor for anomalies** in experiment data
4. **Use rollback mechanisms** for production experiments
5. **Review changes** before completing experiments

---

## Future Enhancements

**@APIs-architect** has designed this API for extensibility:

- 🔮 **REST API Server**: Flask/FastAPI wrapper for HTTP access
- 🔮 **Webhooks**: Event notifications for experiment lifecycle
- 🔮 **GraphQL API**: Alternative query interface
- 🔮 **Real-time monitoring**: WebSocket-based live updates
- 🔮 **Multi-tenancy**: Isolated experiments per namespace
- 🔮 **Authentication**: OAuth2/JWT for secure access

---

## Support

For issues, questions, or contributions:

1. **Review documentation**: This guide and code comments
2. **Check tests**: `tests/test_ab_testing_api.py` for examples
3. **Examine existing experiments**: Study the registry JSON
4. **Consult @APIs-architect**: For API design questions
5. **Consult @workflows-tech-lead**: For workflow integration questions

---

**Built with rigorous design principles by @APIs-architect**  
*Inspired by Margaret Hamilton's commitment to reliability and innovation*
