# A/B Testing Integration Examples

This directory contains examples demonstrating how to integrate A/B testing into workflows and scripts using the new API.

**Author**: @APIs-architect

---

## Examples

### 1. Basic Workflow Integration

**File**: `ab_testing_workflow_example.py`

Demonstrates basic integration of A/B testing into a Python workflow:
- Setup with default configuration
- Automatic experiment participation
- Success/failure metrics recording
- Graceful fallback behavior

**Run it:**
```bash
python3 examples/ab_testing_workflow_example.py
```

**Expected Output:**
```
============================================================
  Workflow with A/B Testing Integration Example
============================================================

📋 Configuration selected:
   {'timeout': 300, 'max_retries': 3, 'batch_size': 100}

🚀 Running workflow task...
✅ Task completed successfully!
   Execution time: 0.238s
   Items processed: 1000
   Resource usage: 54.9%

============================================================
  Workflow completed
============================================================
```

---

### 2. GitHub Actions Integration

**File**: `.github/workflows/example-ab-testing-workflow.yml`

Shows how to integrate A/B testing into a GitHub Actions workflow:
- Participate in experiments via workflow steps
- Record metrics automatically
- Handle both success and failure cases
- Generate workflow summaries

**Trigger it:**
```bash
# Via GitHub UI: Actions tab → Example Workflow with A/B Testing → Run workflow

# Via CLI:
gh workflow run example-ab-testing-workflow.yml
```

---

## Quick Start Guide

### Step 1: Define Your Default Config

```python
default_config = {
    "timeout": 300,
    "max_retries": 3,
    "batch_size": 100
}
```

### Step 2: Setup A/B Testing

```python
from ab_testing_integration import setup_workflow_testing

integration, config = setup_workflow_testing(
    workflow_name="my-workflow",
    default_config=default_config
)
```

### Step 3: Use the Configuration

```python
# The config will be either from an active experiment or your default
result = run_my_task(config)
```

### Step 4: Record Metrics

```python
if result.success:
    integration.record_success(
        execution_time=result.time,
        metrics={"items": result.count}
    )
else:
    integration.record_failure(
        execution_time=result.time,
        error=result.error
    )
```

---

## Creating an Experiment

Before workflows can participate, create an experiment:

```python
from ab_testing_api import ABTestingAPI

api = ABTestingAPI()

# Create experiment
status_code, response = api.create_experiment(
    name="Timeout Optimization",
    description="Testing different timeout values",
    variants={
        "control": {"timeout": 300, "max_retries": 3, "batch_size": 100},
        "increased": {"timeout": 450, "max_retries": 4, "batch_size": 150},
        "aggressive": {"timeout": 600, "max_retries": 5, "batch_size": 200}
    },
    metrics=["execution_time", "success_rate", "resource_usage"],
    workflow_name="example-workflow"
)

print(f"Created experiment: {response['experiment_id']}")
```

Or use the CLI:

```bash
# Discover opportunities
python3 tools/ab_testing_api.py discover

# Auto-create experiments from opportunities
python3 tools/ab_testing_api.py auto-create --max-concurrent 5
```

---

## Best Practices

### 1. Always Provide Defaults

Your workflow should work perfectly fine without any active experiments:

```python
# ✅ Good - provides default
config = integration.participate({"timeout": 300})

# ❌ Bad - no fallback
config = integration.participate()  # Will use empty dict as default
```

### 2. Record Both Success and Failure

Don't only record successful runs:

```python
# ✅ Good - records both outcomes
if success:
    integration.record_success(time, metrics)
else:
    integration.record_failure(time, error)

# ❌ Bad - only success recorded
if success:
    integration.record_success(time, metrics)
```

### 3. Include Relevant Metrics

Record metrics that help evaluate performance:

```python
# ✅ Good - comprehensive metrics
integration.record_success(
    execution_time=time,
    metrics={
        "items_processed": count,
        "resource_usage": cpu_percent,
        "errors_encountered": errors
    }
)

# ❌ Bad - minimal information
integration.record_success(time)
```

### 4. Handle Errors Gracefully

The integration is designed to never break your workflow:

```python
# Even if A/B testing fails, your workflow continues
try:
    integration, config = setup_workflow_testing(name, default)
    # ... workflow logic ...
    integration.record_success(time, metrics)
except Exception as e:
    # Your workflow still completes
    logger.error(f"A/B testing error: {e}")
    # Continue with default behavior
```

### 5. Use Meaningful Workflow Names

Names should be unique and descriptive:

```python
# ✅ Good - clear and unique
integration = WorkflowIntegration("data-processing-pipeline")
integration = WorkflowIntegration("model-training-workflow")

# ❌ Bad - too generic
integration = WorkflowIntegration("workflow")
integration = WorkflowIntegration("task")
```

---

## Advanced Usage

### Custom Variant Selection

Override the default round-robin selection:

```python
class CustomIntegration(WorkflowIntegration):
    def _select_variant(self, experiment):
        # Custom logic - e.g., weighted selection
        # or Thompson Sampling
        return selected_variant_name
```

### Environment-Based Config

Use environment variables for configuration:

```python
from ab_testing_integration import get_config_from_env

# Set via env var: AB_TEST_CONFIG='{"timeout": 450}'
config = get_config_from_env("AB_TEST_CONFIG", default_config)
```

### Conditional Participation

Only participate in experiments under certain conditions:

```python
integration = WorkflowIntegration("my-workflow")

# Only participate in production
if os.environ.get("ENVIRONMENT") == "production":
    config = integration.participate(default_config)
else:
    config = default_config  # Always use default in dev/staging
```

---

## Monitoring

### Check System Status

```bash
python3 tools/ab_testing_api.py status
```

Output:
```json
{
  "success": true,
  "status": "operational",
  "statistics": {
    "total_experiments": 42,
    "active_experiments": 5,
    "completed_experiments": 37
  }
}
```

### List Active Experiments

```bash
python3 tools/ab_testing_api.py list --status active
```

### Analyze Experiment

```bash
python3 tools/ab_testing_api.py analyze exp-abc123
```

---

## Troubleshooting

### Workflow Not Participating

**Symptoms**: Always uses default config, never participates in experiments

**Possible causes**:
1. No active experiment for this workflow name
2. Experiment workflow_name doesn't match
3. Registry file not accessible

**Solution**:
```bash
# Check for active experiments
python3 tools/ab_testing_api.py list --status active --workflow my-workflow

# Verify workflow name matches
# In your code: WorkflowIntegration("my-workflow")
# In experiment: workflow_name="my-workflow"
```

### Metrics Not Recording

**Symptoms**: API call succeeds but no samples appear in experiment

**Possible causes**:
1. Experiment not found
2. Invalid variant name
3. Registry write permissions

**Solution**:
```bash
# Verify experiment exists
python3 tools/ab_testing_api.py get exp-abc123

# Check variant name
python3 tools/ab_testing_api.py get exp-abc123 | grep variants

# Verify registry is writable
ls -la .github/agent-system/ab_tests_registry.json
```

### Import Errors

**Symptoms**: `ModuleNotFoundError: No module named 'ab_testing_api'`

**Solution**:
```python
# Add tools to path before importing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from ab_testing_api import ABTestingAPI
from ab_testing_integration import WorkflowIntegration
```

---

## Further Reading

- **API Documentation**: `docs/AB_TESTING_API.md`
- **A/B Testing Guide**: `docs/AB_TESTING_GUIDE.md`
- **Autonomous System**: `docs/AUTONOMOUS_AB_TESTING.md`
- **Test Suite**: `tests/test_ab_testing_api.py`

---

**Need Help?**

- Review the test suite for more examples
- Check the API documentation for detailed reference
- Consult @APIs-architect for API design questions
- Consult @workflows-tech-lead for workflow integration

---

*Examples created by **@APIs-architect***  
*Following Margaret Hamilton's principles of reliability and clarity*
