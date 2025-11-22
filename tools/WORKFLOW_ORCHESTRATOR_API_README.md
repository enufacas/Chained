# AI-Powered Workflow Orchestrator - Predicting Execution Times

Created by **@APIs-architect** 🏭

A comprehensive AI-powered workflow orchestration system that predicts optimal execution times for GitHub Actions workflows using machine learning and provides a REST-like API for real-time predictions.

## 🎯 Overview

This enhanced workflow orchestrator extends the existing prediction capabilities with:

- **🔮 Advanced ML Predictions**: Predicts optimal workflow execution times based on historical patterns
- **📡 REST-like API**: Programmatic access to predictions and metrics
- **📊 Real-time Insights**: Query workflow performance and success rates
- **🎯 Batch Processing**: Predict multiple workflows simultaneously
- **📈 Accuracy Tracking**: Compare predictions vs actual execution times
- **🔄 Continuous Learning**: System improves with each workflow execution

## 🏗️ Architecture

### Components

1. **AI Workflow Predictor** (`ai_workflow_predictor.py`)
   - Core ML-based prediction engine
   - Pattern recognition and learning
   - Historical data analysis

2. **Workflow Execution Tracker** (`workflow_execution_tracker.py`)
   - Tracks actual execution times
   - Calculates prediction accuracy
   - Provides feedback loop for improvement

3. **Orchestrator API** (`workflow_orchestrator_api.py`) ⭐ **NEW**
   - REST-like API interface
   - Real-time predictions
   - Metrics and insights
   - Easy integration with GitHub Actions

4. **Integrated Orchestrator** (`integrated_workflow_orchestrator.py`)
   - Combines all components
   - High-level orchestration
   - Intelligent scheduling recommendations

## 🚀 Quick Start

### Installation

No additional dependencies required beyond what's in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Basic Usage

#### 1. Predict Execution Time for a Workflow

```bash
python3 tools/workflow_orchestrator_api.py predict --workflow learn-from-tldr
```

Output:
```
📡 Workflow Orchestrator API - @APIs-architect
Status: ✅ Success
Message: Prediction generated successfully

Data:
{
  "workflow_name": "learn-from-tldr",
  "recommended_schedule": "0 3 * * *",
  "confidence": 0.85,
  "expected_duration_seconds": 245.0,
  "predicted_success_rate": 0.92,
  "resource_impact": "low",
  "reasoning": [
    "Hour 3 has 92% success rate",
    "Scheduled during off-peak hours",
    "Often conflicts with: agent-spawner"
  ]
}
```

#### 2. Batch Predictions

```bash
python3 tools/workflow_orchestrator_api.py batch --workflows learn-from-tldr learn-from-hackernews idea-generator
```

#### 3. Get Workflow Insights

```bash
python3 tools/workflow_orchestrator_api.py insights --workflow learn-from-tldr
```

#### 4. View Execution History

```bash
python3 tools/workflow_orchestrator_api.py history --workflow learn-from-tldr --limit 50
```

#### 5. Check Accuracy Metrics

```bash
python3 tools/workflow_orchestrator_api.py accuracy --workflow learn-from-tldr
```

#### 6. Health Check

```bash
python3 tools/workflow_orchestrator_api.py health
```

### JSON Output

For programmatic access, use `--json` flag:

```bash
python3 tools/workflow_orchestrator_api.py predict --workflow my-workflow --json
```

## 📡 API Reference

### WorkflowOrchestratorAPI Class

#### Methods

##### `predict_execution_time(workflow_name: str) -> APIResponse`
Predict optimal execution time for a single workflow.

**Returns:**
```python
{
    "workflow_name": str,
    "recommended_schedule": str,  # Cron expression
    "confidence": float,  # 0-1
    "expected_duration_seconds": float,
    "predicted_success_rate": float,  # 0-1
    "resource_impact": str,  # "low", "medium", "high"
    "reasoning": List[str]
}
```

##### `predict_batch(workflow_names: List[str]) -> APIResponse`
Predict optimal times for multiple workflows.

##### `get_execution_history(workflow_name: str, limit: int) -> APIResponse`
Retrieve execution history for analysis.

##### `get_accuracy_metrics(workflow_name: str) -> APIResponse`
Get prediction accuracy statistics.

##### `get_workflow_insights(workflow_name: str) -> APIResponse`
Get comprehensive insights including:
- Total executions
- Success rate
- Duration statistics
- Most common execution hour
- Recommendation confidence

##### `record_execution(...) -> APIResponse`
Record a new workflow execution for learning.

##### `health_check() -> APIResponse`
Check API health status.

## 🔧 Integration Examples

### Python Integration

```python
from tools.workflow_orchestrator_api import WorkflowOrchestratorAPI

# Initialize API
api = WorkflowOrchestratorAPI()

# Get prediction
response = api.predict_execution_time("my-workflow")

if response.success:
    print(f"Recommended schedule: {response.data['recommended_schedule']}")
    print(f"Confidence: {response.data['confidence']*100:.0f}%")
    print(f"Expected duration: {response.data['expected_duration_seconds']}s")

# Get insights
insights = api.get_workflow_insights("my-workflow")
if insights.success:
    print(f"Success rate: {insights.data['success_rate']*100:.0f}%")
    print(f"Average duration: {insights.data['average_duration']}s")
```

### GitHub Actions Integration

Add this to your workflow to record execution data:

```yaml
name: My Workflow
on:
  schedule:
    - cron: '0 * * * *'

jobs:
  main:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Record workflow start
        run: echo "WORKFLOW_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $GITHUB_ENV
      
      - name: Your workflow steps
        run: |
          # Your actual workflow logic
          echo "Doing work..."
      
      - name: Record execution to predictor
        if: always()
        run: |
          DURATION=$(($(date +%s) - $(date -d "$WORKFLOW_START" +%s)))
          python3 tools/workflow_orchestrator_api.py record \
            --workflow "${{ github.workflow }}" \
            --start-time "$WORKFLOW_START" \
            --duration "$DURATION" \
            --success "${{ job.status == 'success' }}"
```

### Bash Script Integration

```bash
#!/bin/bash

# Get prediction for a workflow
predict_workflow() {
    local workflow=$1
    python3 tools/workflow_orchestrator_api.py predict \
        --workflow "$workflow" \
        --json | jq -r '.data.recommended_schedule'
}

# Update workflow schedule based on prediction
SCHEDULE=$(predict_workflow "learn-from-tldr")
echo "Recommended schedule: $SCHEDULE"
```

## 📊 Features

### 1. Machine Learning Predictions

- **Pattern Recognition**: Learns from historical execution patterns
- **Time-based Analysis**: Identifies optimal hours and days
- **Conflict Detection**: Avoids scheduling conflicts
- **Success Rate Prediction**: Forecasts likelihood of success
- **Duration Estimation**: Predicts expected runtime

### 2. Real-time API

- **RESTful Interface**: Easy programmatic access
- **Standard Response Format**: Consistent JSON responses
- **Error Handling**: Graceful error handling and reporting
- **Health Monitoring**: Built-in health check endpoint

### 3. Comprehensive Metrics

- **Execution History**: Full historical tracking
- **Accuracy Metrics**: MAE, MAPE, accuracy score
- **Workflow Insights**: Statistics and trends
- **Resource Impact**: Classification of resource usage

### 4. Integration Ready

- **GitHub Actions**: Easy workflow integration
- **CLI Access**: Command-line interface
- **JSON Output**: Machine-readable format
- **Python API**: Native Python integration

## 🎯 Use Cases

### 1. Optimize Workflow Scheduling

```python
# Get predictions for all workflows
api = WorkflowOrchestratorAPI()
workflows = ['learn-tldr', 'learn-hn', 'idea-generator']
predictions = api.predict_batch(workflows)

# Apply high-confidence recommendations
for workflow, pred in predictions.data['predictions'].items():
    if pred['confidence'] > 0.7:
        print(f"Update {workflow} to {pred['recommended_schedule']}")
```

### 2. Monitor Prediction Accuracy

```python
# Track how well predictions match reality
accuracy = api.get_accuracy_metrics()
if accuracy.success:
    mae = accuracy.data['mean_absolute_error']
    print(f"Average prediction error: {mae}s")
```

### 3. Identify Problem Workflows

```python
# Find workflows with low success rates
insights = api.get_workflow_insights("problematic-workflow")
if insights.success and insights.data['success_rate'] < 0.7:
    print(f"Warning: {workflow} has {insights.data['success_rate']*100}% success rate")
```

### 4. Continuous Learning

```python
# Record each execution to improve predictions
api.record_execution(
    workflow_name="my-workflow",
    start_time=datetime.now(timezone.utc).isoformat(),
    duration_seconds=execution_time,
    success=was_successful,
    resource_usage={
        'cpu_percent': cpu_usage,
        'memory_mb': memory_usage,
        'api_calls': api_calls_made
    }
)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Test the API
python3 tools/test_workflow_orchestrator_api.py

# Test the predictor
python3 tools/test_ai_workflow_predictor.py

# Test execution tracking
python3 tools/test_workflow_execution_tracker.py
```

All tests should pass (100% success rate).

## 📈 Benefits

1. **⏱️ Reduced Execution Time**: Optimize scheduling to avoid conflicts
2. **💰 Cost Savings**: Better resource utilization
3. **✅ Higher Success Rates**: Schedule during proven success windows
4. **📊 Data-Driven Decisions**: Base scheduling on actual patterns
5. **🔄 Continuous Improvement**: System learns and adapts
6. **🎯 Proactive Management**: Identify issues before they occur

## 🔮 Advanced Features

### Confidence-Based Scheduling

Only apply predictions with high confidence:

```python
predictions = api.predict_batch(workflows)
for workflow, pred in predictions.data['predictions'].items():
    if pred['confidence'] >= 0.7:
        # High confidence - apply recommendation
        apply_schedule(workflow, pred['recommended_schedule'])
    else:
        # Low confidence - keep current schedule
        print(f"Need more data for {workflow}")
```

### Trend Analysis

Track prediction accuracy over time:

```python
# Weekly accuracy check
for week in range(4):
    accuracy = api.get_accuracy_metrics()
    print(f"Week {week}: {accuracy.data['accuracy_score']*100:.0f}% accurate")
```

### Resource-Based Scheduling

Schedule heavy workflows during off-peak:

```python
prediction = api.predict_execution_time("heavy-workflow")
if prediction.data['resource_impact'] == 'high':
    # Ensure scheduled during off-peak
    assert int(prediction.data['recommended_schedule'].split()[1]) < 6
```

## 📚 Related Documentation

- [AI Workflow Predictor README](./AI_WORKFLOW_PREDICTOR_README.md) - Core ML predictor
- [Workflow Execution Tracker README](./WORKFLOW_EXECUTION_TRACKER_README.md) - Tracking system
- [Workflow Harmonizer README](./WORKFLOW_HARMONIZER_README.md) - Conflict detection
- [Integrated Orchestrator](./AI_WORKFLOW_ORCHESTRATOR_README.md) - Combined system

## 🎼 Philosophy

As **@APIs-architect** (inspired by Margaret Hamilton), this system embodies:

- **Rigor**: Thoroughly tested and validated
- **Innovation**: ML-based predictions for workflow optimization
- **Reliability**: Ensures workflows run at optimal times
- **Directness**: Clear API interface and actionable recommendations

## 🚀 Future Enhancements

Potential improvements:

1. **Real-time Adaptation**: Dynamic rescheduling based on current load
2. **Cost Optimization**: Factor in GitHub Actions pricing
3. **Multi-objective Optimization**: Balance success rate, duration, and cost
4. **Dependency Analysis**: Account for workflow dependencies
5. **Seasonal Patterns**: Detect weekly/monthly patterns
6. **External Factors**: Consider API quotas and service status
7. **Reinforcement Learning**: Learn from prediction outcomes

## 🤝 Contributing

When contributing to the workflow orchestrator:

1. **Maintain API Compatibility**: Don't break existing integrations
2. **Add Tests**: All new features must have tests
3. **Document Changes**: Update this README
4. **Follow Patterns**: Match existing code style
5. **Validate Accuracy**: Ensure predictions remain accurate

## 📝 License

Part of the Chained autonomous AI ecosystem.

---

*Created by **@APIs-architect** - Building robust, intelligent systems for workflow optimization* 🏭

**Reliability first. Innovation always.**
