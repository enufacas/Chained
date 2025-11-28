# Neural Architecture API

**Created by @APIs-architect** - Inspired by Margaret Hamilton's rigorous and reliable approach to software engineering.

## Overview

The Neural Architecture API provides a programmatic REST-style interface for the self-evolving neural architecture system. It enables easy integration with workflows, external systems, and automation pipelines.

## Features

- **Architecture Lifecycle Management**: Create, read, update, and delete neural architectures
- **Execution Recording**: Record workflow success/failure outcomes for learning
- **Evolution Control**: Trigger and manage architecture evolution
- **Recommendations**: Get optimized workflow parameter recommendations
- **Pattern Analysis**: Query recognized execution patterns
- **System Health Monitoring**: Check system health and generate reports
- **Batch Operations**: Efficient bulk recording of executions

## Quick Start

### Python API

```python
from neural_architecture_api import NeuralArchitectureAPI

# Initialize the API
api = NeuralArchitectureAPI()

# Create a new architecture
status, response = api.create_architecture("ci-build")

# Record executions
api.record_execution("ci-build", success=True)
api.record_execution("ci-build", success=False)

# Get recommendations
status, response = api.get_recommendations("ci-build")
print(f"Recommended timeout: {response['recommendations']['timeout']}")

# Trigger evolution
status, response = api.trigger_evolution("ci-build", force=True)

# Check system health
status, response = api.get_health_status()
print(f"System status: {response['status']}")
```

### Command Line Interface

```bash
# Create architecture
python tools/neural_architecture_api.py --create my-workflow

# Record execution
python tools/neural_architecture_api.py --record my-workflow --success

# Get recommendations
python tools/neural_architecture_api.py --recommend my-workflow

# Trigger evolution
python tools/neural_architecture_api.py --evolve my-workflow --force

# Get health status
python tools/neural_architecture_api.py --health

# List all architectures
python tools/neural_architecture_api.py --list

# Generate report
python tools/neural_architecture_api.py --report
```

## API Reference

### Architecture Management

#### `create_architecture(workflow_name, config=None)`
Creates a new neural architecture for a workflow.

**Parameters:**
- `workflow_name`: Name of the workflow to optimize
- `config`: Optional configuration overrides (dict)

**Returns:** `(status_code, response_dict)`

**Example:**
```python
status, response = api.create_architecture("ci-build", config={
    'base_learning_rate': 0.05,
    'success_rate_threshold': 0.8
})
```

#### `get_architecture(workflow_name)`
Gets details of a neural architecture.

**Returns:** Status and architecture details including layers, patterns, and metrics.

#### `delete_architecture(workflow_name)`
Deletes a neural architecture.

#### `list_architectures()`
Lists all neural architectures with their success rates and execution counts.

### Execution Recording

#### `record_execution(workflow_name, success, context=None)`
Records a workflow execution result.

**Parameters:**
- `workflow_name`: Name of the workflow
- `success`: Whether the execution was successful (bool)
- `context`: Optional execution context (dict)

**Example:**
```python
status, response = api.record_execution(
    "ci-build",
    success=True,
    context={'duration': 120, 'memory_usage': 0.8}
)
```

#### `batch_record_executions(executions)`
Records multiple executions in batch.

**Parameters:**
- `executions`: List of execution records with `workflow_name`, `success`, and optional `context`

**Example:**
```python
status, response = api.batch_record_executions([
    {"workflow_name": "ci-build", "success": True},
    {"workflow_name": "tests", "success": False},
])
```

### Evolution Control

#### `trigger_evolution(workflow_name, force=False)`
Triggers evolution for a neural architecture.

**Parameters:**
- `workflow_name`: Name of the workflow
- `force`: Whether to force evolution even if not needed

**Example:**
```python
status, response = api.trigger_evolution("ci-build", force=True)
# response includes before/after architecture state
```

#### `evolve_all()`
Triggers evolution check for all architectures.

### Recommendations

#### `get_recommendations(workflow_name, context=None)`
Gets workflow parameter recommendations from the neural network.

**Returns:**
```json
{
  "workflow_name": "ci-build",
  "recommendations": {
    "timeout": 120.5,
    "retries": 3,
    "concurrency": 5,
    "priority": 75
  },
  "confidence": 0.85,
  "based_on_executions": 50,
  "success_rate": 0.78
}
```

### Pattern Analysis

#### `get_patterns(workflow_name, pattern_type=None)`
Gets recognized patterns for a workflow.

**Parameters:**
- `workflow_name`: Name of the workflow
- `pattern_type`: Optional filter (e.g., "time_of_day", "day_of_week")

### System Health

#### `get_system_summary()`
Gets summary of all neural architectures.

#### `get_health_status()`
Gets health status of the system.

**Returns:**
```json
{
  "status": "healthy",
  "total_architectures": 5,
  "average_success_rate": 0.85,
  "low_performing_count": 0,
  "critical_count": 0,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### `generate_report()`
Generates a comprehensive text report.

## HTTP Status Codes

The API uses standard HTTP status codes:

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error |

## Error Response Format

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "workflow_name": "optional-workflow-name"
}
```

## Integration with Workflows

The API integrates seamlessly with the existing `neural-architecture-evolution.yml` workflow:

```yaml
- name: Record workflow result
  run: |
    python tools/neural_architecture_api.py \
      --record "${{ github.workflow }}" \
      ${{ job.status == 'success' && '--success' || '' }}

- name: Get recommendations
  run: |
    python tools/neural_architecture_api.py \
      --recommend "${{ github.workflow }}"
```

## Configuration

Configuration can be passed when creating architectures:

```python
config = {
    'base_learning_rate': 0.01,      # Initial learning rate
    'success_rate_threshold': 0.7,   # Evolve if below this
    'min_hidden_neurons': 2,          # Minimum neurons per layer
    'max_hidden_neurons': 20          # Maximum neurons per layer
}
```

## Related Tools

- `self_evolving_neural_architecture.py` - Core neural architecture implementation
- `neural_workflow_adapter.py` - Original neural adapter
- `ab_testing_api.py` - A/B testing API (similar pattern)
- `api_coordination_hub.py` - API coordination utilities

## Credits

This API was created by **@APIs-architect**, inspired by Margaret Hamilton's approach to building reliable, well-documented software systems. The design follows the established pattern from `ab_testing_api.py` to maintain consistency across the Chained ecosystem.

---

*🤖 Part of the Chained autonomous AI ecosystem*
