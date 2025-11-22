# Workflow Orchestrator Integration Examples

Created by **@APIs-architect**

This guide shows practical examples of integrating the AI workflow orchestrator into your GitHub Actions workflows.

## Example 1: Recording Workflow Execution Data

Add this to any workflow to feed execution data to the predictor:

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
      
      # Record start time
      - name: Record workflow start
        run: echo "WORKFLOW_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> $GITHUB_ENV
      
      # Your workflow steps
      - name: Run main tasks
        run: |
          echo "Performing work..."
          # Your actual workflow logic here
      
      # Record execution data (always runs)
      - name: Record execution to predictor
        if: always()
        run: |
          WORKFLOW_END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
          DURATION=$(($(date -d "$WORKFLOW_END" +%s) - $(date -d "$WORKFLOW_START" +%s)))
          
          python3 << EOF
          from tools.workflow_orchestrator_api import WorkflowOrchestratorAPI
          from datetime import datetime
          
          api = WorkflowOrchestratorAPI()
          api.record_execution(
              workflow_name="${{ github.workflow }}",
              start_time="$WORKFLOW_START",
              duration_seconds=$DURATION,
              success=${{ job.status == 'success' }},
              resource_usage={
                  'cpu_percent': 50,  # Can be measured during execution
                  'memory_mb': 512,
                  'api_calls': 10
              }
          )
          print("✓ Execution recorded")
          EOF
```

## Example 2: Dynamic Scheduling Based on Predictions

Use predictions to dynamically update workflow schedules:

```yaml
name: Optimize Workflow Schedules

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly optimization
  workflow_dispatch:

permissions:
  contents: write

jobs:
  optimize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Get predictions for all workflows
        id: predictions
        run: |
          python3 << EOF
          from tools.workflow_orchestrator_api import WorkflowOrchestratorAPI
          import json
          
          api = WorkflowOrchestratorAPI()
          
          workflows = ['learn-from-tldr', 'learn-from-hackernews', 'idea-generator']
          response = api.predict_batch(workflows)
          
          if response.success:
              for workflow, pred in response.data['predictions'].items():
                  if pred['confidence'] >= 0.7:
                      print(f"Recommendation for {workflow}:")
                      print(f"  Schedule: {pred['recommended_schedule']}")
                      print(f"  Confidence: {pred['confidence']*100:.0f}%")
                      print(f"  Success Rate: {pred['predicted_success_rate']*100:.0f}%")
                      print()
          EOF
      
      - name: Apply high-confidence recommendations
        run: |
          echo "Apply recommendations with confidence >= 70%"
          # Logic to update workflow files would go here
```

## Example 3: Monitoring Prediction Accuracy

Track how well predictions match reality:

```yaml
name: Monitor Prediction Accuracy

on:
  schedule:
    - cron: '0 0 * * *'  # Daily accuracy check

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Calculate accuracy metrics
        run: |
          python3 << EOF
          from tools.workflow_orchestrator_api import WorkflowOrchestratorAPI
          
          api = WorkflowOrchestratorAPI()
          
          # Overall accuracy
          response = api.get_accuracy_metrics()
          if response.success:
              data = response.data
              print(f"📊 Prediction Accuracy Report")
              print(f"Mean Absolute Error: {data['mean_absolute_error']:.1f}s")
              print(f"Mean Percentage Error: {data['mean_percentage_error']:.1f}%")
              print(f"Accuracy Score: {data['accuracy_score']*100:.0f}%")
              print(f"Total Comparisons: {data['total_comparisons']}")
          
          # Per-workflow accuracy
          workflows = api.get_workflow_list()
          for workflow in workflows:
              response = api.get_accuracy_metrics(workflow)
              if response.success:
                  print(f"\n{workflow}:")
                  print(f"  Accuracy: {response.data['accuracy_score']*100:.0f}%")
          EOF
      
      - name: Alert on low accuracy
        run: |
          python3 << EOF
          from tools.workflow_orchestrator_api import WorkflowOrchestratorAPI
          
          api = WorkflowOrchestratorAPI()
          response = api.get_accuracy_metrics()
          
          if response.success:
              accuracy = response.data['accuracy_score']
              if accuracy < 0.7:
                  print(f"⚠️ WARNING: Prediction accuracy is {accuracy*100:.0f}%")
                  print("Consider collecting more data or reviewing prediction logic")
                  exit(1)
          EOF
```

## Example 4: Workflow Insights Dashboard Update

Generate updated dashboard after executions:

```yaml
name: Update Prediction Dashboard

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-dashboard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate updated dashboard
        run: |
          python3 tools/workflow_prediction_dashboard.py
      
      - name: Commit dashboard updates
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          
          if [[ -n $(git status -s docs/workflow-predictions/) ]]; then
            git add docs/workflow-predictions/
            git commit -m "chore: Update workflow prediction dashboard"
            git push
            echo "✓ Dashboard updated"
          else
            echo "No changes to dashboard"
          fi
```

## Example 5: Conditional Workflow Execution

Run workflows only during predicted optimal times:

```yaml
name: Smart Workflow

on:
  schedule:
    - cron: '0 * * * *'  # Check every hour

jobs:
  check-and-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check if optimal time
        id: check
        run: |
          python3 << EOF
          from tools.workflow_orchestrator_api import WorkflowOrchestratorAPI
          from datetime import datetime
          
          api = WorkflowOrchestratorAPI()
          response = api.predict_execution_time("smart-workflow")
          
          if response.success:
              # Parse cron schedule
              cron = response.data['recommended_schedule']
              hour = int(cron.split()[1])
              current_hour = datetime.utcnow().hour
              
              if hour == current_hour:
                  print("SHOULD_RUN=true")
              else:
                  print("SHOULD_RUN=false")
                  print(f"Current: {current_hour}, Optimal: {hour}")
          EOF
      
      - name: Run workflow
        if: env.SHOULD_RUN == 'true'
        run: |
          echo "Running at optimal time!"
          # Your workflow logic
```

## Example 6: Batch Analysis and Reporting

Analyze multiple workflows and generate report:

```yaml
name: Workflow Analysis Report

on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate comprehensive analysis
        run: |
          python3 << EOF
          from tools.workflow_orchestrator_api import WorkflowOrchestratorAPI
          import json
          
          api = WorkflowOrchestratorAPI()
          
          # Get all workflows
          workflows = api.get_workflow_list()
          
          print("# 🔮 Weekly Workflow Analysis Report")
          print()
          
          # Batch predictions
          predictions = api.predict_batch(workflows)
          
          print("## Predictions")
          for wf, pred in predictions.data['predictions'].items():
              print(f"\n### {wf}")
              print(f"- Schedule: `{pred['recommended_schedule']}`")
              print(f"- Confidence: {pred['confidence']*100:.0f}%")
              print(f"- Expected Duration: {pred['expected_duration_seconds']:.0f}s")
              print(f"- Success Rate: {pred['predicted_success_rate']*100:.0f}%")
          
          # Insights for each workflow
          print("\n## Detailed Insights")
          for wf in workflows:
              response = api.get_workflow_insights(wf)
              if response.success:
                  data = response.data
                  print(f"\n### {wf}")
                  print(f"- Total Executions: {data['total_executions']}")
                  print(f"- Success Rate: {data['success_rate']*100:.0f}%")
                  print(f"- Avg Duration: {data['average_duration']:.0f}s")
                  print(f"- Duration Range: {data['min_duration']:.0f}s - {data['max_duration']:.0f}s")
          
          # Overall accuracy
          accuracy = api.get_accuracy_metrics()
          if accuracy.success:
              print("\n## Prediction Accuracy")
              print(f"- Overall Accuracy: {accuracy.data['accuracy_score']*100:.0f}%")
              print(f"- Mean Error: {accuracy.data['mean_absolute_error']:.0f}s")
              print(f"- Total Comparisons: {accuracy.data['total_comparisons']}")
          
          print("\n---")
          print("Generated by @APIs-architect")
          EOF
      
      - name: Create summary
        run: |
          echo "📊 Analysis complete. Check step output for full report."
```

## Best Practices

### 1. Always Record Executions
Record every workflow execution to improve predictions:
```python
api.record_execution(
    workflow_name=workflow_name,
    start_time=start_time,
    duration_seconds=duration,
    success=success,
    resource_usage=resource_metrics
)
```

### 2. Use Confidence Thresholds
Only apply high-confidence predictions:
```python
if prediction['confidence'] >= 0.7:
    # Apply recommendation
    apply_schedule(prediction['recommended_schedule'])
```

### 3. Monitor Accuracy
Regularly check prediction accuracy:
```python
accuracy = api.get_accuracy_metrics()
if accuracy.data['accuracy_score'] < 0.7:
    # Alert or investigate
```

### 4. Gradual Rollout
Test predictions on non-critical workflows first:
```python
# Start with test workflows
test_workflows = ['non-critical-workflow']
predictions = api.predict_batch(test_workflows)
# Validate before applying to critical workflows
```

### 5. Provide Feedback
Record actual outcomes to improve the system:
```python
# After workflow runs, record what actually happened
api.record_execution(...)
```

## Troubleshooting

### Low Prediction Confidence
If confidence is low (<60%), you need more data:
```bash
# Check execution count
python3 tools/workflow_orchestrator_api.py insights --workflow my-workflow
```

Need at least 20-30 executions for reliable predictions.

### Inaccurate Predictions
If predictions don't match reality:
```bash
# Check accuracy metrics
python3 tools/workflow_orchestrator_api.py accuracy --workflow my-workflow
```

Review resource usage patterns and execution times.

### API Errors
If API returns errors:
```bash
# Check health
python3 tools/workflow_orchestrator_api.py health
```

Ensure history files exist and are readable.

## Additional Resources

- [API Reference](./WORKFLOW_ORCHESTRATOR_API_README.md)
- [AI Predictor Documentation](./AI_WORKFLOW_PREDICTOR_README.md)
- [Execution Tracker Documentation](./WORKFLOW_EXECUTION_TRACKER_README.md)

---

*Created by **@APIs-architect** - Integrating intelligence into your workflows* 🏭
