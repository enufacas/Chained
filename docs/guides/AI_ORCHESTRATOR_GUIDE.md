# 🎹 AI-Powered Workflow Orchestrator

## Implementation Guide by @coordinate-wizard

This guide explains how to use and integrate the AI-powered workflow orchestrator created for the Chained autonomous AI ecosystem.

## 🎯 What Was Built

An intelligent workflow execution time predictor that uses machine learning to optimize GitHub Actions scheduling based on:

- **Historical Execution Patterns**: Learns from past runs
- **Success Rate Analysis**: Identifies optimal execution times
- **Conflict Detection**: Prevents simultaneous workflow runs
- **Resource Optimization**: Balances load across time slots
- **Confidence Scoring**: Indicates reliability of predictions

## 🚀 Quick Start

### 1. Basic Usage

```bash
# Generate a comprehensive report
python3 tools/integrated_workflow_orchestrator.py --report

# Simulate execution data for testing
python3 tools/ai_workflow_predictor.py --simulate --report

# Get prediction for a specific workflow
python3 tools/ai_workflow_predictor.py --workflow "my-workflow"

# Export recommendations to JSON
python3 tools/integrated_workflow_orchestrator.py --export recommendations.json
```

### 2. Run Tests

```bash
# Run comprehensive test suite
python3 tools/test_ai_workflow_predictor.py

# Expected output: 10/10 tests passed (100%)
```

### 3. Use the Workflow

Trigger the demo workflow:
- Go to Actions → "AI Workflow Orchestrator Demo"
- Click "Run workflow"
- Select mode: `report`, `simulate`, or `export`

## 📚 Components

### 1. **AI Workflow Predictor** (`ai_workflow_predictor.py`)

Core machine learning engine that:
- Tracks workflow execution history
- Analyzes patterns and trends
- Predicts optimal execution times
- Provides confidence scores
- Detects conflicts

**Key Classes:**
- `WorkflowExecutionData`: Stores execution information
- `PredictionResult`: Contains prediction output
- `AIWorkflowPredictor`: Main prediction engine

### 2. **Integrated Orchestrator** (`integrated_workflow_orchestrator.py`)

Integration layer that:
- Combines AI predictions with existing tools
- Generates comprehensive reports
- Exports recommendations
- Applies changes (with dry-run mode)

**Key Features:**
- Confidence-based filtering
- Visual distribution charts
- JSON export capabilities
- Safe dry-run mode

### 3. **Test Suite** (`test_ai_workflow_predictor.py`)

Comprehensive testing:
- 10 test cases covering all functionality
- Pattern analysis validation
- Prediction accuracy checks
- Conflict detection tests
- Resource impact classification

### 4. **Demo Workflow** (`ai-workflow-orchestrator-demo.yml`)

GitHub Actions workflow demonstrating:
- Automated report generation
- Recommendation export
- PR creation with results
- Integration with issue tracking

## 🔧 Integration Guide

### Collecting Real Execution Data

To get accurate predictions, collect real workflow execution data:

```python
from datetime import datetime, timezone
from tools.ai_workflow_predictor import AIWorkflowPredictor

# Initialize predictor
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

### Adding to Existing Workflows

Add this step to your workflows to collect data:

```yaml
- name: Record execution data
  if: always()  # Run even if workflow fails
  run: |
    python3 << 'EOF'
    from datetime import datetime, timezone
    from tools.ai_workflow_predictor import AIWorkflowPredictor
    import os
    
    predictor = AIWorkflowPredictor()
    
    # Workflow info from GitHub Actions
    workflow_name = "${{ github.workflow }}"
    started_at = "${{ github.event.workflow_run.created_at }}"
    # ... record execution
    EOF
```

### Integrating with Existing Orchestrator

The AI predictor complements `workflow-orchestrator.py`:

```python
from workflow_orchestrator import WorkflowOrchestrator
from ai_workflow_predictor import AIWorkflowPredictor

# Use orchestrator for API-based scheduling
orchestrator = WorkflowOrchestrator()
orchestrator.update_all_workflows(mode='conservative')

# Use AI predictor for intelligent timing
predictor = AIWorkflowPredictor()
predictions = predictor.predict_batch(['workflow-1', 'workflow-2'])

# Apply high-confidence recommendations
for workflow_name, prediction in predictions.items():
    if prediction.confidence > 0.7:
        print(f"Recommended: {workflow_name} at {prediction.recommended_time}")
```

## 📊 Understanding Predictions

### Prediction Output Structure

```python
PredictionResult(
    workflow_name="learn-from-tldr",
    recommended_time="0 3 * * *",  # Cron expression
    confidence=0.85,               # 0-1 scale
    reasoning=[                    # Explanation
        "Hour 3 has 92% success rate",
        "Scheduled during off-peak hours"
    ],
    expected_duration=245.0,       # Seconds
    predicted_success_rate=0.92,   # 0-1 scale
    resource_impact="low"          # low/medium/high
)
```

### Confidence Levels

- **>0.7**: High confidence - safe to apply automatically
- **0.5-0.7**: Medium confidence - review recommended
- **<0.5**: Low confidence - needs more data

### Resource Impact

- **Low**: < 3 minutes duration
- **Medium**: 3-10 minutes duration
- **High**: > 10 minutes duration

## 🎨 Use Cases

### 1. Optimize Scheduled Workflows

```bash
# Get recommendations for all workflows
python3 tools/integrated_workflow_orchestrator.py --report

# Review high-confidence recommendations
# Apply to workflow files manually or via orchestrator
```

### 2. Identify Workflow Conflicts

The predictor detects workflows that frequently run simultaneously:

```python
predictor = AIWorkflowPredictor()
predictor.load_history()

# Check conflict patterns
conflicts = predictor.conflict_patterns
for workflow, conflicting in conflicts.items():
    print(f"{workflow} often conflicts with: {conflicting[:3]}")
```

### 3. Performance Analysis

Track workflow performance over time:

```bash
# Generate report with historical trends
python3 tools/ai_workflow_predictor.py --report

# Review success rates by time of day
# Identify patterns in duration
# Spot degradation trends
```

### 4. Resource Planning

Understand resource usage patterns:

```python
report = predictor.generate_recommendations_report()

# Check resource impact distribution
impact_counts = {'low': 0, 'medium': 0, 'high': 0}
for rec in report['recommendations']:
    impact_counts[rec['resource_impact']] += 1

print(f"High impact workflows: {impact_counts['high']}")
```

## 🔮 Advanced Features

### Custom Prediction Logic

Extend the predictor with custom logic:

```python
class CustomPredictor(AIWorkflowPredictor):
    def predict_optimal_time(self, workflow_name, current_schedule=None):
        # Get base prediction
        prediction = super().predict_optimal_time(workflow_name, current_schedule)
        
        # Add custom logic (e.g., prefer weekends)
        if workflow_name.startswith('maintenance'):
            # Override to run on weekends
            prediction.recommended_time = "0 3 * * 6"  # Saturday 3 AM
            prediction.reasoning.append("Maintenance scheduled for weekend")
        
        return prediction
```

### Batch Optimization

Optimize multiple workflows together:

```python
predictor = AIWorkflowPredictor()

# Get predictions for all workflows
workflows = ['wf-1', 'wf-2', 'wf-3', 'wf-4', 'wf-5']
predictions = predictor.predict_batch(workflows)

# The predictor automatically staggers schedules to avoid conflicts
for wf, pred in predictions.items():
    print(f"{wf}: {pred.recommended_time}")
```

### Historical Analysis

Analyze trends over time:

```python
predictor = AIWorkflowPredictor()

# Get success rates by hour
success_by_hour = defaultdict(lambda: {'success': 0, 'total': 0})
for exec_data in predictor.execution_history:
    hour = exec_data.hour_of_day
    success_by_hour[hour]['total'] += 1
    if exec_data.success:
        success_by_hour[hour]['success'] += 1

# Identify best and worst hours
for hour, stats in sorted(success_by_hour.items()):
    if stats['total'] > 0:
        rate = stats['success'] / stats['total']
        print(f"Hour {hour}: {rate*100:.0f}% success rate")
```

## 🐛 Troubleshooting

### No Predictions Available

**Problem**: All confidence scores are low (< 0.5)

**Solution**: Collect more historical data
```bash
# Simulate data for testing
python3 tools/ai_workflow_predictor.py --simulate

# In production, let workflows run and collect real data
```

### Predictions Don't Match Expected

**Problem**: Predictor recommends unexpected times

**Reason**: The predictor optimizes for:
1. Success rate (highest priority)
2. Least resource contention
3. Off-peak hours

**Solution**: Review the reasoning in the prediction output

### History File Not Loading

**Problem**: New predictor instance doesn't see previous data

**Check**: History file location
```bash
# Default location
ls -la .github/workflow-history/executions.json

# Verify JSON is valid
cat .github/workflow-history/executions.json | python3 -m json.tool
```

## 📈 Monitoring & Improvement

### Track Prediction Accuracy

Compare predictions with actual outcomes:

```python
# Record prediction
prediction = predictor.predict_optimal_time("my-workflow")

# Later, record actual execution
predictor.record_execution(
    workflow_name="my-workflow",
    start_time=actual_start,
    duration_seconds=actual_duration,
    success=actual_success
)

# Compare predicted vs actual
if abs(prediction.expected_duration - actual_duration) < 60:
    print("✓ Duration prediction was accurate")
```

### Continuous Improvement

The predictor gets better over time:

1. **Week 1**: Low confidence (< 50%) - needs more data
2. **Week 2-3**: Medium confidence (50-70%) - patterns emerging
3. **Week 4+**: High confidence (> 70%) - reliable predictions

### Best Practices

1. **Collect Diverse Data**: Run workflows at different times
2. **Include Metadata**: Track resource usage, API calls, etc.
3. **Regular Reviews**: Check predictions weekly
4. **Incremental Adoption**: Start with high-confidence recommendations
5. **Monitor Results**: Track actual vs predicted outcomes

## 🎼 Philosophy (@coordinate-wizard)

Following Quincy Jones' approach:

- **Versatile**: Works with any workflow configuration
- **Integrative**: Complements existing tools
- **Philosophical**: Learns from patterns rather than rigid rules
- **Orchestrative**: Coordinates diverse workflows for harmony

The system embodies continuous learning and adaptation, improving with every execution it observes.

## 📞 Support & Contribution

### Getting Help

- Review `AI_WORKFLOW_PREDICTOR_README.md` for detailed API docs
- Check test cases in `test_ai_workflow_predictor.py` for examples
- Run `--help` on any command for usage information

### Contributing Improvements

Ideas for enhancements:
- Seasonal pattern detection (monthly/quarterly trends)
- External factor integration (API quotas, GitHub status)
- Cost optimization (GitHub Actions pricing)
- Real-time adjustment based on current load
- Reinforcement learning for adaptive predictions

---

**Created by @coordinate-wizard** 🎹  
*Orchestrating workflows with intelligence and insight*
