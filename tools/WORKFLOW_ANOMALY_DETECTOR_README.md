# Workflow Anomaly Detector

Created by **@create-botter** 🏭

An intelligent anomaly detection system that identifies unusual workflow execution patterns, helping maintain system health and proactively address potential issues.

## 🎯 Purpose

The Workflow Anomaly Detector enhances the AI-powered workflow orchestrator by:

- **Detecting duration anomalies**: Identifies workflows running significantly longer or shorter than usual
- **Monitoring failure rates**: Alerts when failure rates increase beyond normal thresholds
- **Tracking performance trends**: Detects gradual degradation in workflow performance
- **Calculating health scores**: Provides comprehensive health metrics for each workflow

## 🧠 How It Works

### Anomaly Detection Methods

#### 1. Duration Anomaly Detection
Uses statistical Z-score analysis to detect unusual execution times:
- Calculates mean and standard deviation of historical durations
- Flags executions with Z-score > 2.5 (more than 2.5 standard deviations from mean)
- Severity scales with Z-score (medium → high → critical)

#### 2. Failure Rate Anomaly Detection
Compares recent failure rates against historical baselines:
- Splits execution history into recent and historical periods
- Detects when recent failure rate increases by > 30%
- Severity based on magnitude of increase

#### 3. Trend Anomaly Detection
Uses linear regression to detect gradual performance degradation:
- Analyzes slope of execution times over recent window (10 executions)
- Flags when projected increase exceeds 25% over next 10 runs
- Early warning system for slowly degrading workflows

### Health Score Calculation

Each workflow receives a comprehensive health score (0-100) based on:

| Component | Weight | Description |
|-----------|--------|-------------|
| Success Score | 35% | Based on success/failure rate |
| Duration Score | 25% | Based on execution time consistency |
| Consistency Score | 20% | Based on recent execution variance |
| Trend Score | 20% | Based on improvement/degradation trend |

## 🚀 Usage

### Command Line

```bash
# Generate full anomaly report
python3 tools/workflow_anomaly_detector.py --report

# Check specific workflow
python3 tools/workflow_anomaly_detector.py --check "my-workflow"

# Export results to JSON
python3 tools/workflow_anomaly_detector.py --export anomaly_report.json

# Simulate data for testing
python3 tools/workflow_anomaly_detector.py --simulate --report
```

### Python API

```python
from workflow_anomaly_detector import WorkflowAnomalyDetector

detector = WorkflowAnomalyDetector()

# Check for duration anomaly
alert = detector.detect_duration_anomaly("my-workflow", current_duration=500)
if alert:
    print(f"ALERT: {alert.message}")
    print(f"Severity: {alert.severity}")
    print(f"Action: {alert.recommended_action}")

# Get workflow health score
health = detector.calculate_health_score("my-workflow")
print(f"Health Score: {health.overall_score}")
print(f"Success Rate: {health.success_score}%")

# Run full analysis
results = detector.run_full_analysis()
for workflow, score in results['health_scores'].items():
    print(f"{workflow}: {score['overall_score']}")
```

## 📊 Output Examples

### Anomaly Report

```
======================================================================
🔍 Workflow Anomaly Detection Report
   Created by @create-botter
======================================================================

📊 Summary:
  Total Workflows Analyzed: 15
  Active Alerts: 3
    - Critical: 1
    - High: 1
  Average Health Score: 78.5

⚠️  Active Anomalies:
----------------------------------------------------------------------

🔴 [CRITICAL] learn-from-tldr
   Type: duration
   Message: Execution time is 450% longer than usual
   Action: Investigate why learn-from-tldr is running longer than expected

🟠 [HIGH] agent-spawner
   Type: failure_rate
   Message: Failure rate increased from 5% to 45%
   Action: Investigate recent failures in agent-spawner

🟡 [MEDIUM] ci-pipeline
   Type: trend
   Message: Execution time showing upward trend (+35% projected)
   Action: Monitor ci-pipeline for potential performance degradation

✅ No additional anomalies detected!

🏥 Workflow Health Scores:
----------------------------------------------------------------------
Workflow                       Overall    Success    Duration   Trend     
----------------------------------------------------------------------
workflow-validation            🟢 92      100.0      89.0       95.0      
code-quality                   🟢 88      100.0      82.0       90.0      
learn-from-hackernews          🟢 85      95.0       80.0       88.0      
agent-evolution                🟡 72      85.0       65.0       70.0      
ci-pipeline                    🔴 58      60.0       45.0       55.0      

======================================================================
```

### Health Score JSON Export

```json
{
  "timestamp": "2025-11-27T01:15:00Z",
  "health_scores": {
    "learn-from-tldr": {
      "workflow_name": "learn-from-tldr",
      "overall_score": 85.2,
      "duration_score": 82.0,
      "success_score": 95.0,
      "consistency_score": 80.0,
      "trend_score": 88.0
    }
  },
  "alerts": [
    {
      "workflow_name": "agent-spawner",
      "anomaly_type": "failure_rate",
      "severity": "high",
      "message": "Failure rate increased from 5% to 45%"
    }
  ],
  "summary": {
    "total_workflows": 15,
    "average_health_score": 78.5,
    "critical_alerts": 0,
    "high_alerts": 1
  }
}
```

## 🔧 Configuration

### Detection Thresholds

The detector uses configurable thresholds:

```python
class WorkflowAnomalyDetector:
    DURATION_Z_SCORE_THRESHOLD = 2.5  # Standard deviations from mean
    FAILURE_RATE_THRESHOLD = 0.3      # 30% increase triggers alert
    MIN_SAMPLES_FOR_ANALYSIS = 5      # Minimum data points needed
    TREND_WINDOW_SIZE = 10            # Recent executions to analyze
```

### Severity Levels

| Level | Icon | Description |
|-------|------|-------------|
| Critical | 🔴 | Immediate attention required |
| High | 🟠 | Should be addressed soon |
| Medium | 🟡 | Worth investigating |
| Low | ⚪ | Minor concern |

## 🔄 Integration

### With AI Workflow Orchestrator

The anomaly detector integrates seamlessly with the existing orchestration system:

```python
from ai_workflow_predictor import AIWorkflowPredictor
from workflow_anomaly_detector import WorkflowAnomalyDetector

predictor = AIWorkflowPredictor()
detector = WorkflowAnomalyDetector()

# Use predictions for scheduling
prediction = predictor.predict_optimal_time("my-workflow")

# Use anomaly detection for health monitoring
health = detector.calculate_health_score("my-workflow")

# Combine for informed decisions
if health.overall_score < 60:
    print(f"⚠️ {my-workflow} health is low, consider investigation")
elif prediction.confidence > 0.7:
    print(f"✅ Safe to apply AI scheduling: {prediction.recommended_time}")
```

### With GitHub Actions

The `workflow-execution-tracker.yml` workflow automatically:
1. Triggers on workflow completion
2. Records execution data to the predictor
3. Runs anomaly detection
4. Commits data back to the repository

## 🧪 Testing

Run the test suite:

```bash
python3 tools/test_workflow_anomaly_detector.py
```

Expected output:
```
======================================================================
Total: 9/9 tests passed (100%)
======================================================================
```

## 📁 File Structure

```
tools/
├── workflow_anomaly_detector.py       # Main anomaly detector
├── test_workflow_anomaly_detector.py  # Test suite
├── WORKFLOW_ANOMALY_DETECTOR_README.md # This file
├── ai_workflow_predictor.py           # ML predictor (dependency)
└── integrated_workflow_orchestrator.py # Orchestrator (related)

.github/
├── workflows/
│   ├── workflow-execution-tracker.yml  # Automatic data collection
│   └── ai-workflow-orchestrator-demo.yml # Demo workflow
└── workflow-history/
    ├── executions.json                  # Execution history
    └── anomaly_alerts.json              # Alert history
```

## 🎨 Philosophy

As **@create-botter** (Nikola Tesla), this tool embodies:

- **Visionary Thinking**: Proactive detection before problems escalate
- **Elegant Solutions**: Statistical methods for accurate anomaly detection
- **Innovation First**: ML-inspired health scoring system
- **Scalability**: Works with any number of workflows
- **Automation**: Integrates seamlessly with existing infrastructure

## 📚 Related Tools

- **ai_workflow_predictor.py**: ML-based execution time predictor
- **integrated_workflow_orchestrator.py**: Intelligent scheduling system
- **workflow_execution_tracker.py**: Accuracy tracking
- **workflow-execution-tracker.yml**: Automatic data collection workflow

## 🤝 Contributing

When enhancing the anomaly detector:
1. Add tests for new detection methods
2. Update this README with new features
3. Maintain compatibility with existing tools
4. Mention **@create-botter** in commits

---

*Created by **@create-botter** - Illuminating workflow health with the insight of innovation* 🏭
