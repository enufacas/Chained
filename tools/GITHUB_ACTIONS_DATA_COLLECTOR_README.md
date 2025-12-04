# GitHub Actions Data Collector

**Created by @create-botter** 🏭

An intelligent data collection tool that bridges GitHub Actions with the AI-powered workflow orchestrator by automatically gathering real workflow execution data.

## 🎯 Purpose

The GitHub Actions Data Collector solves a critical gap in the AI workflow prediction system: the need for real execution data. While the existing system could simulate data for testing, this tool enables continuous learning from actual workflow behavior.

### Key Benefits

- **Real Data Learning**: Feed actual execution times to the AI predictor
- **Continuous Improvement**: Automatic daily data collection
- **Trend Detection**: Track workflow performance over time
- **Resource Optimization**: Understand actual resource usage patterns
- **Predictive Accuracy**: Improve prediction confidence with more data

## 🔧 Features

### Core Capabilities

1. **Automatic Data Collection**
   - Fetches workflow runs from GitHub Actions API
   - Extracts execution times, success rates, and resource metrics
   - Records data to the AI predictor's history

2. **Integration with AI Predictor**
   - Direct integration with `ai_workflow_predictor.py`
   - Automatic pattern analysis on new data
   - Confidence score improvements

3. **Scheduled Collection**
   - Daily automatic collection via GitHub Actions
   - Event-triggered collection on workflow completion
   - Manual collection on demand

4. **Comprehensive Reporting**
   - Workflow execution statistics
   - Collection history tracking
   - Performance trend analysis

## 🚀 Usage

### Command Line

```bash
# Collect recent workflow runs
python3 tools/github_actions_data_collector.py --collect

# Collect with custom limit
python3 tools/github_actions_data_collector.py --collect --limit 100

# Filter by specific workflow
python3 tools/github_actions_data_collector.py --collect --workflow "CI Pipeline"

# Show workflow execution statistics
python3 tools/github_actions_data_collector.py --stats

# Generate comprehensive report
python3 tools/github_actions_data_collector.py --report
```

### GitHub Actions Workflow

The tool includes an automated workflow (`.github/workflows/workflow-data-collection.yml`) that:

- Runs daily at 2:00 AM UTC
- Triggers after any workflow completes
- Supports manual dispatch with configurable options

```yaml
# Manual trigger
on:
  workflow_dispatch:
    inputs:
      limit:
        description: 'Maximum runs to collect'
        default: '100'
      mode:
        description: 'Collection mode'
        options:
          - collect
          - stats
          - report
```

### Python API

```python
from github_actions_data_collector import GitHubActionsDataCollector

# Initialize collector
collector = GitHubActionsDataCollector()

# Fetch workflow runs
runs = collector.fetch_workflow_runs(limit=50)

# Record to AI predictor
recorded = collector.record_to_predictor(runs)

# Get statistics
stats = collector.get_workflow_stats()

# Complete collection workflow
result = collector.collect_and_record(limit=100)
```

## 📊 Data Format

### WorkflowRunData Structure

```python
@dataclass
class WorkflowRunData:
    workflow_name: str       # Name of the workflow
    workflow_id: int         # Workflow database ID
    run_id: int             # Unique run ID
    run_number: int         # Sequential run number
    status: str             # Status (completed, in_progress, etc.)
    conclusion: str         # Result (success, failure, etc.)
    start_time: datetime    # When the run started
    end_time: datetime      # When the run ended
    duration_seconds: float # Total execution time
    event: str              # Trigger event (push, pull_request, etc.)
    branch: str             # Branch that triggered the run
    actor: str              # User who triggered the run
```

### Resource Usage Estimation

For each recorded execution:

```python
{
    'duration_seconds': 300,
    'event': 'push',
    'branch': 'main',
    'actor': 'developer',
    'estimated_cpu_percent': 45.0,  # Based on duration
    'estimated_memory_mb': 512     # Based on duration
}
```

## 🏗️ Architecture

### Integration Flow

```
GitHub Actions API
        │
        ▼
┌────────────────────────────────┐
│  GitHub Actions Data Collector │
│  - Fetches workflow runs       │
│  - Parses execution data       │
│  - Estimates resource usage    │
└────────────────────────────────┘
        │
        ▼
┌────────────────────────────────┐
│     AI Workflow Predictor      │
│  - Records execution history   │
│  - Analyzes patterns           │
│  - Updates predictions         │
└────────────────────────────────┘
        │
        ▼
┌────────────────────────────────┐
│  Integrated Workflow Orchestr. │
│  - Generates recommendations   │
│  - Applies scheduling          │
│  - Monitors accuracy           │
└────────────────────────────────┘
```

### Data Storage

```
.github/
└── workflow-history/
    ├── executions.json       # AI predictor's execution history
    └── collection_log.json   # Collection activity log
```

## 📈 Example Output

### Collection Summary

```
🚀 GitHub Actions Data Collector
   @create-botter
==================================================

📥 Fetching workflow runs from GitHub Actions...
✓ Fetched 50 workflow runs
✓ Recorded 48 workflow runs to AI predictor

📊 Collection Summary:
  Status: success
  Runs Fetched: 50
  Runs Recorded: 48
  Workflows: CI Pipeline, Tests, Deploy, Agent Spawning, Learning
```

### Statistics Report

```
📊 Workflow Data Statistics
============================================================

Workflow                            Runs   Success   Avg Duration
----------------------------------------------------------------------
CI Pipeline                           45       91%          180s
Agent Spawning                        32       87%          245s
Learning from TLDR                    28       96%          120s
Meta Coordinator                      25       84%          320s
Workflow Validation                   20      100%           90s
----------------------------------------------------------------------
Total                                150
```

## 🧪 Testing

The tool includes comprehensive tests:

```bash
python3 tests/test_github_actions_data_collector.py
```

Test coverage includes:
- Collector initialization
- Data structure creation
- Collection log persistence
- Recording to AI predictor
- Mocked API responses
- Error handling
- Report generation

## 🔄 Continuous Learning Loop

The data collector enables a continuous improvement loop:

```
1. Collect Data     → Real workflow executions
       ↓
2. Record History   → Feed AI predictor
       ↓
3. Analyze Patterns → Learn success/failure patterns
       ↓
4. Update Predictions → Improve scheduling
       ↓
5. Apply Recommendations → Better execution times
       ↓
6. Track Accuracy   → Monitor prediction quality
       ↓
   [Repeat Daily]
```

## 🔮 Future Enhancements

Planned improvements:

1. **Job-Level Analysis**: Track individual job durations within workflows
2. **Cost Tracking**: Calculate GitHub Actions billing impact
3. **Anomaly Detection**: Alert on unusual execution patterns
4. **Cross-Repository**: Support organization-wide data collection
5. **Webhook Integration**: Real-time data collection via webhooks

## 📚 Related Tools

- **ai_workflow_predictor.py**: ML-based execution time predictor
- **integrated_workflow_orchestrator.py**: Scheduling recommendations
- **workflow_execution_tracker.py**: Prediction accuracy tracking
- **workflow-orchestrator.py**: API usage-based scheduling

## 🎼 Philosophy

As **@create-botter** (inspired by Nikola Tesla), this tool embodies:

- **Innovation**: Novel approach to bridging real data with AI predictions
- **Vision**: See the potential in automated learning from execution patterns
- **Precision**: Careful data collection and integration
- **Automation**: Self-sustaining data collection pipeline
- **Elegance**: Clean integration with existing AI orchestration system

## 🤝 Contributing

### Adding New Features

1. Maintain compatibility with existing tools
2. Follow established patterns
3. Add comprehensive tests
4. Update documentation
5. Mention **@create-botter** in commits

### Reporting Issues

1. Include workflow run details
2. Provide API response examples
3. Share collection logs
4. Suggest improvements

---

*Created by **@create-botter** - Inventive infrastructure for intelligent automation* 🏭
