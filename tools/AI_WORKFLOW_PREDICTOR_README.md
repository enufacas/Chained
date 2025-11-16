# AI-Powered Workflow Orchestrator

Created by **@coordinate-wizard** 🎹

An intelligent workflow execution time predictor that uses machine learning to optimize GitHub Actions workflow scheduling based on historical patterns.

## 🎯 Purpose

The AI-Powered Workflow Orchestrator extends the existing `workflow-orchestrator.py` with ML-based prediction capabilities to:

- **Predict optimal execution times** based on historical success patterns
- **Reduce resource contention** by analyzing workflow conflicts
- **Learn from past failures** to avoid problematic time slots
- **Optimize API usage** by scheduling workflows during off-peak hours
- **Provide confidence scores** for each recommendation

## 🧠 How It Works

### Machine Learning Approach

The predictor uses historical execution data to learn patterns:

1. **Pattern Recognition**: Analyzes success rates by time of day and day of week
2. **Conflict Detection**: Identifies workflows that frequently run simultaneously
3. **Duration Prediction**: Estimates expected runtime based on past executions
4. **Success Rate Prediction**: Forecasts likelihood of successful completion
5. **Resource Impact Assessment**: Categorizes workflows by their resource usage

### Data Collection

The system tracks:
- Workflow execution start times
- Duration of each run
- Success/failure outcomes
- Resource usage (CPU, memory, API calls)
- Day of week and hour patterns

## 🚀 Usage

### Basic Commands

```bash
# Simulate execution data for testing
python3 tools/ai_workflow_predictor.py --simulate

# Generate comprehensive recommendations report
python3 tools/ai_workflow_predictor.py --report

# Get prediction for specific workflow
python3 tools/ai_workflow_predictor.py --workflow "learn-from-tldr"

# Combine simulation with report
python3 tools/ai_workflow_predictor.py --simulate --report
```

### Recording Real Execution Data

```python
from ai_workflow_predictor import AIWorkflowPredictor

predictor = AIWorkflowPredictor()

# Record a workflow execution
predictor.record_execution(
    workflow_name="my-workflow",
    start_time=datetime.now(timezone.utc),
    duration_seconds=245.5,
    success=True,
    resource_usage={
        'cpu_percent': 45.2,
        'memory_mb': 512,
        'api_calls': 23
    }
)
```

### Getting Predictions

```python
from ai_workflow_predictor import AIWorkflowPredictor

predictor = AIWorkflowPredictor()

# Get prediction for a single workflow
prediction = predictor.predict_optimal_time("my-workflow")

print(f"Recommended Schedule: {prediction.recommended_time}")
print(f"Confidence: {prediction.confidence * 100:.0f}%")
print(f"Expected Duration: {prediction.expected_duration}s")
print(f"Success Rate: {prediction.predicted_success_rate * 100:.0f}%")

# Get predictions for multiple workflows
predictions = predictor.predict_batch(["workflow-1", "workflow-2", "workflow-3"])
```

## 📊 Prediction Output

Each prediction includes:

- **Recommended Schedule**: Cron expression for optimal execution time
- **Confidence Level**: 0-100% based on amount of historical data
- **Expected Duration**: Predicted runtime in seconds
- **Success Rate**: Likelihood of successful completion (0-100%)
- **Resource Impact**: low/medium/high classification
- **Reasoning**: List of factors influencing the recommendation

### Example Output

```
Workflow: learn-from-tldr
Recommended Schedule: 0 3 * * *
Confidence: 85%
Expected Duration: 245s
Predicted Success Rate: 92%
Resource Impact: low

Reasoning:
  • Hour 3 has 92% success rate
  • Scheduled during off-peak hours
  • Often conflicts with: agent-spawner, idea-generator
```

## 🎨 Integration with Existing Tools

### With workflow-orchestrator.py

The AI predictor complements the existing orchestrator:

```python
from workflow_orchestrator import WorkflowOrchestrator
from ai_workflow_predictor import AIWorkflowPredictor

# Use orchestrator for dynamic scheduling based on API usage
orchestrator = WorkflowOrchestrator()
orchestrator.update_all_workflows(mode='conservative')

# Use AI predictor for intelligent timing recommendations
predictor = AIWorkflowPredictor()
predictions = predictor.predict_batch(['workflow-1', 'workflow-2'])

# Apply AI recommendations to workflows
for workflow_name, prediction in predictions.items():
    if prediction.confidence > 0.7:  # Only apply high-confidence predictions
        print(f"Applying AI recommendation for {workflow_name}")
        # Update workflow schedule based on prediction
```

### With workflow_harmonizer.py

The predictor enhances harmonizer's conflict detection:

```python
from workflow_harmonizer import WorkflowHarmonizer
from ai_workflow_predictor import AIWorkflowPredictor

harmonizer = WorkflowHarmonizer()
harmonizer.load_workflows()

predictor = AIWorkflowPredictor()
report = predictor.generate_recommendations_report()

# Use both tools for comprehensive analysis
conflicts = harmonizer.detect_conflicts()
predictions = report['recommendations']

print("Combining workflow harmony analysis with AI predictions...")
```

## 🏗️ Architecture

### Data Storage

Execution history is stored in:
```
.github/workflow-history/executions.json
```

Format:
```json
{
  "last_updated": "2025-11-16T04:35:00Z",
  "executions": [
    {
      "workflow_name": "learn-from-tldr",
      "start_time": "2025-11-16T03:00:00Z",
      "duration_seconds": 245.5,
      "success": true,
      "resource_usage": {
        "cpu_percent": 45.2,
        "memory_mb": 512,
        "api_calls": 23
      },
      "day_of_week": 5,
      "hour_of_day": 3
    }
  ]
}
```

### Pattern Learning

The system maintains internal pattern maps:
- **Success Patterns**: `Dict[workflow_name, List[(day, hour)]]`
- **Duration Patterns**: `Dict[workflow_name, Dict[time_key, List[durations]]]`
- **Conflict Patterns**: `Dict[workflow_name, List[conflicting_workflows]]`

## 📈 Benefits

1. **Reduced API Usage**: Optimizes scheduling to stay within quotas
2. **Higher Success Rates**: Schedules workflows during proven success windows
3. **Less Contention**: Prevents multiple workflows from running simultaneously
4. **Data-Driven Decisions**: Uses historical patterns instead of guesswork
5. **Continuous Learning**: Improves predictions as more data is collected
6. **Confidence Scoring**: Indicates reliability of each recommendation

## 🧪 Testing with Simulated Data

For testing and demonstration, the predictor can generate realistic simulation data:

```bash
# Generate 200 executions for 15 workflows
python3 tools/ai_workflow_predictor.py --simulate

# Customize simulation parameters
python3 -c "
from tools.ai_workflow_predictor import AIWorkflowPredictor
predictor = AIWorkflowPredictor()
predictor.simulate_execution_data(num_workflows=20, num_executions=500)
"
```

Simulated data includes:
- Realistic workflow duration variations
- Time-dependent success rates
- Preferred execution hours per workflow
- Resource usage patterns
- Conflict scenarios

## 🔮 Future Enhancements

Potential improvements for the AI predictor:

1. **Seasonal Patterns**: Detect weekly/monthly patterns
2. **External Factors**: Consider API quota status, GitHub Actions limits
3. **Cost Optimization**: Factor in GitHub Actions pricing
4. **Multi-Objective Optimization**: Balance success rate, duration, and cost
5. **Reinforcement Learning**: Adapt based on actual outcomes vs predictions
6. **Dependency Analysis**: Account for workflow dependencies
7. **Real-Time Adjustment**: Dynamic rescheduling based on current load

## 📚 Related Tools

- **workflow-orchestrator.py**: Dynamic scheduling based on API usage
- **workflow_harmonizer.py**: Ecosystem health analysis and conflict detection
- **workflow_dependency_graph.py**: Visualize workflow relationships
- **copilot-usage-tracker.py**: Monitor API quota consumption

## 🎼 Philosophy

As **@coordinate-wizard** (Quincy Jones), this tool embodies:
- **Versatility**: Works with any workflow configuration
- **Integration**: Seamlessly combines with existing tools
- **Philosophical**: Learns from patterns to make informed decisions
- **Orchestration**: Coordinates diverse workflows for harmony

---

*Created by **@coordinate-wizard** - Orchestrating workflows with the wisdom of experience* 🎹
