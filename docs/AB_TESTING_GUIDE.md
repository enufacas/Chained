# Autonomous A/B Testing for Workflow Configurations

**Author**: @workflows-tech-lead  
**System**: Chained Autonomous AI  
**Focus**: CI/CD reliability and workflow optimization

---

## Overview

The Autonomous A/B Testing system automatically detects, creates, manages, and analyzes experiments to optimize GitHub Actions workflow configurations. It operates with choreographic precision to ensure safety while continuously improving workflow performance.

## Architecture

### Core Components

1. **Workflow Analyzer** (`tools/ab_testing_workflow_analyzer.py`)
   - Scans all workflows for optimization opportunities
   - Identifies schedule, timeout, and concurrency patterns
   - Prioritizes high-impact opportunities
   - Generates experiment proposals

2. **Autonomous Creator** (`tools/autonomous_experiment_creator.py`)
   - Manages complete experiment lifecycle
   - Creates experiments with safety guards
   - Analyzes active experiments
   - Auto-completes experiments with clear winners
   - Prevents conflicts (one experiment per workflow)

3. **Visualization Dashboard** (`tools/ab_testing_dashboard.py`)
   - Generates HTML dashboard
   - Real-time experiment monitoring
   - Winner detection display
   - Responsive design

4. **A/B Testing Engine** (`tools/ab_testing_engine.py`)
   - Core experiment management
   - Sample recording
   - Statistical analysis
   - Registry management

5. **Advanced Algorithms** (`tools/ab_testing_advanced.py`)
   - Thompson Sampling (Multi-Armed Bandit)
   - Bayesian A/B testing
   - Sequential testing
   - Confidence intervals

6. **Autonomous Workflow** (`.github/workflows/autonomous-ab-testing.yml`)
   - Scheduled daily execution
   - Manual trigger support
   - Automatic PR creation
   - Dashboard deployment

## Features

### 🔍 Intelligent Opportunity Detection

The system automatically identifies optimization opportunities:

**Schedule Optimization**
- Detects cron patterns and frequencies
- Suggests faster/slower variants
- Prioritizes high-frequency workflows

**Timeout Optimization**
- Analyzes existing timeout configurations
- Tests increased/decreased timeouts
- Measures impact on success rates

**Concurrency Optimization**
- Tests cancel-in-progress settings
- Measures queue time impact
- Optimizes resource utilization

### 🤖 Fully Autonomous Operation

1. **Daily Cycle**: Runs automatically at 00:00 UTC
2. **Capacity Management**: Limits concurrent experiments (default: 5)
3. **Conflict Prevention**: One experiment per workflow at a time
4. **Auto-Completion**: Completes experiments when winners are clear
5. **Dashboard Updates**: Generates visualization automatically

### 🛡️ Safety Mechanisms

**Production Safety**:
- Experiments are tracked but NOT auto-deployed
- Manual review required before rollout
- Clear rollout plans generated
- Safety checks before completion

**Data Integrity**:
- Atomic registry updates (temp file + rename)
- Corruption recovery built-in
- Backup and restore capabilities

**Conflict Prevention**:
- Checks for existing experiments on same workflow
- Priority-based experiment creation
- Concurrent experiment limits

## Usage

### Command Line Interface

#### 1. Analyze Workflows

```bash
# Find optimization opportunities
python3 tools/ab_testing_workflow_analyzer.py

# Output as JSON
python3 tools/ab_testing_workflow_analyzer.py --json > opportunities.json
```

#### 2. Run Autonomous Cycle

```bash
# Dry-run mode (analyze only, no creation)
python3 tools/autonomous_experiment_creator.py --dry-run

# Live mode (create experiments)
python3 tools/autonomous_experiment_creator.py --max-concurrent 5

# Output as JSON
python3 tools/autonomous_experiment_creator.py --json > results.json
```

#### 3. Generate Dashboard

```bash
# Generate HTML dashboard
python3 tools/ab_testing_dashboard.py

# Custom output path
python3 tools/ab_testing_dashboard.py --output docs/custom-dashboard.html

# View dashboard
open docs/ab-testing-dashboard.html
```

### GitHub Actions Integration

#### Automatic Daily Execution

The `autonomous-ab-testing.yml` workflow runs daily at 00:00 UTC:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'
```

#### Manual Trigger

Trigger manually with custom settings:

```bash
gh workflow run autonomous-ab-testing.yml \
  --field max_concurrent=3 \
  --field dry_run=true
```

Or via GitHub UI:
1. Go to Actions tab
2. Select "Autonomous A/B Testing" workflow
3. Click "Run workflow"
4. Set parameters

#### Pull Request Creation

When experiments are created or completed, the workflow automatically:
1. Creates a unique branch
2. Commits registry and dashboard updates
3. Creates a PR with detailed summary
4. Labels: `automated`, `ab-testing`, `workflows-tech-lead`

## Workflow

### Autonomous Cycle Steps

1. **Analyze Workflows**
   - Scan all workflows in `.github/workflows/`
   - Identify optimization opportunities
   - Rank by priority

2. **Check Capacity**
   - Count active experiments
   - Calculate available slots
   - Respect maximum concurrent limit

3. **Create Experiments**
   - Filter opportunities (avoid conflicts)
   - Create experiments for top opportunities
   - Record in registry

4. **Analyze Active Experiments**
   - Check all active experiments
   - Perform statistical analysis
   - Detect clear winners

5. **Complete Experiments**
   - Apply safety checks
   - Complete experiments with winners
   - Generate rollout plans

6. **Update Dashboard**
   - Regenerate HTML visualization
   - Update statistics
   - Show active and completed experiments

### Experiment Lifecycle

```
Opportunity Detected
        ↓
  Experiment Created (active)
        ↓
  Samples Collected
        ↓
  Statistical Analysis
        ↓
  Winner Detected
        ↓
  Experiment Completed
        ↓
  Rollout Plan Generated
        ↓
  Manual Review & Deploy
```

## Experiment Types

### 1. Schedule Optimization

**Goal**: Find optimal workflow execution frequency

**Variants**:
- Control: Current schedule
- More Frequent: 25% faster (e.g., 15min → 11min)
- Less Frequent: 33% slower (e.g., 15min → 20min)

**Metrics**:
- `execution_time`: How long the workflow takes
- `success_rate`: Percentage of successful runs
- `resource_usage`: CPU/memory consumption
- `api_calls`: Number of API requests

**Example**:
```json
{
  "name": "Schedule Optimization: data-sync",
  "workflow_name": "data-sync",
  "variants": {
    "control": {
      "cron": "*/15 * * * *",
      "frequency_minutes": 15
    },
    "more_frequent": {
      "cron": "*/11 * * * *",
      "frequency_minutes": 11
    },
    "less_frequent": {
      "cron": "*/20 * * * *",
      "frequency_minutes": 20
    }
  }
}
```

### 2. Timeout Optimization

**Goal**: Find optimal timeout settings to balance safety and efficiency

**Variants**:
- Control: Current timeout
- Increased: 50% more time
- Decreased: 25% less time

**Metrics**:
- `execution_time`: Actual run time
- `success_rate`: Successful completions
- `timeout_rate`: How often timeouts occur

**Example**:
```json
{
  "name": "Timeout Optimization: build-workflow",
  "workflow_name": "build-workflow",
  "variants": {
    "control": {
      "timeout_minutes": 30
    },
    "increased": {
      "timeout_minutes": 45
    },
    "decreased": {
      "timeout_minutes": 22
    }
  }
}
```

### 3. Concurrency Optimization

**Goal**: Optimize concurrent execution behavior

**Variants**:
- Control: Current setting
- Alternative: Opposite setting

**Metrics**:
- `execution_time`: Time to complete
- `queue_time`: Time waiting in queue
- `success_rate`: Success percentage

**Example**:
```json
{
  "name": "Concurrency Optimization: test-runner",
  "workflow_name": "test-runner",
  "variants": {
    "control": {
      "cancel_in_progress": false
    },
    "alternative": {
      "cancel_in_progress": true
    }
  }
}
```

## Dashboard

The A/B Testing Dashboard provides real-time visualization:

### Features

- **Summary Statistics**
  - Total experiments
  - Active experiments
  - Completed experiments
  - Winners detected

- **Active Experiments Section**
  - Live status for ongoing tests
  - Current sample counts
  - Variant performance preview

- **Completed Experiments Section**
  - Winner badges
  - Final sample counts
  - Variant comparison
  - Creation dates

### Access

- **Local**: Open `docs/ab-testing-dashboard.html` in browser
- **GitHub Pages**: https://enufacas.github.io/Chained/ab-testing-dashboard.html (if deployed)

### Regeneration

Dashboard is automatically regenerated:
- After each autonomous cycle
- When experiments are completed
- On manual trigger

To regenerate manually:
```bash
python3 tools/ab_testing_dashboard.py
```

## Safety & Rollout

### Before Auto-Completion

Safety checks are applied:

1. **Minimum Improvement**: Winner must show >5% improvement
2. **Statistical Significance**: Must meet confidence thresholds
3. **Sample Size**: Minimum samples per variant must be met
4. **No Critical Failures**: No blocking issues detected

### Rollout Process

When an experiment completes with a winner:

1. **Review the Results**
   - Check winner variant
   - Verify improvement percentage
   - Review confidence level

2. **Generate Rollout Plan**
   ```bash
   python3 -c "
   from autonomous_experiment_creator import AutonomousExperimentCreator
   creator = AutonomousExperimentCreator()
   plan = creator.generate_rollout_plan('experiment-id')
   print(plan)
   "
   ```

3. **Manual Rollout Steps**
   - Open the workflow YAML file
   - Apply the winning configuration
   - Commit and push changes
   - Monitor for 24 hours

4. **Post-Rollout Monitoring**
   - Watch for unexpected behavior
   - Verify metrics match A/B test results
   - Be ready to rollback if needed

### Rollback

If a rollout causes issues:

1. **Immediate Rollback**
   ```bash
   git revert <commit-hash>
   git push
   ```

2. **Update Registry**
   - Mark experiment as "archived"
   - Document the rollback reason

3. **Investigate**
   - Review what went wrong
   - Check for environmental differences
   - Consider external factors

## Configuration

### Registry Location

```
.github/agent-system/ab_tests_registry.json
```

### Registry Structure

```json
{
  "version": "1.0",
  "config": {
    "min_samples_per_variant": 20,
    "min_improvement_threshold": 0.05,
    "confidence_level": 0.95
  },
  "experiments": [
    {
      "id": "exp-abc123",
      "name": "Schedule Optimization: workflow-name",
      "status": "active",
      "variants": { ... },
      "metrics": [ ... ],
      "results": null
    }
  ]
}
```

### Configuration Parameters

- **min_samples_per_variant**: Minimum samples before analysis (default: 20)
- **min_improvement_threshold**: Minimum improvement to declare winner (default: 5%)
- **confidence_level**: Statistical confidence required (default: 95%)

### Tuning

Edit `.github/agent-system/ab_tests_registry.json`:

```json
{
  "config": {
    "min_samples_per_variant": 30,  // More samples = higher confidence
    "min_improvement_threshold": 0.10,  // Higher bar for winners
    "confidence_level": 0.99  // Higher confidence requirement
  }
}
```

## Advanced Usage

### Manual Experiment Creation

```python
from ab_testing_engine import ABTestingEngine

engine = ABTestingEngine()

exp_id = engine.create_experiment(
    name="Custom Experiment",
    description="Testing custom configurations",
    variants={
        "control": {"config": "value1"},
        "variant_a": {"config": "value2"}
    },
    metrics=["execution_time", "success_rate"],
    workflow_name="my-workflow"
)

print(f"Created experiment: {exp_id}")
```

### Recording Samples

```python
engine.record_sample(
    experiment_id=exp_id,
    variant_name="control",
    metrics={
        "execution_time": 120.5,
        "success_rate": 0.95
    },
    metadata={"run_id": "12345"}
)
```

### Analyzing Results

```python
analysis = engine.analyze_experiment(exp_id, use_advanced=True)

if analysis["status"] == "analyzed" and analysis.get("winner"):
    winner = analysis["winner"]
    print(f"Winner: {winner['variant']}")
    print(f"Improvement: {winner['improvement']:.2%}")
    print(f"Confidence: {analysis['confidence']}")
```

## Monitoring

### Workflow Runs

Monitor autonomous A/B testing workflow:
```bash
gh run list --workflow=autonomous-ab-testing.yml --limit 10
```

### Recent Activity

```bash
# Show recent experiments
python3 -c "
from ab_testing_engine import ABTestingEngine
engine = ABTestingEngine()
experiments = engine.list_experiments(status='active')
for exp in experiments:
    print(f'{exp[\"name\"]} - {exp[\"status\"]}')
"
```

### Dashboard Monitoring

Open the dashboard regularly to track progress:
```bash
open docs/ab-testing-dashboard.html
```

## Troubleshooting

### Issue: No Experiments Created

**Possible Causes**:
- Already at max concurrent experiments
- All workflows already have active experiments
- No optimization opportunities detected

**Solution**:
```bash
# Check active experiments
python3 -c "
from ab_testing_engine import ABTestingEngine
engine = ABTestingEngine()
print(len(engine.list_experiments(status='active')))
"

# Run analyzer to see opportunities
python3 tools/ab_testing_workflow_analyzer.py
```

### Issue: Experiments Not Completing

**Possible Causes**:
- Insufficient samples collected
- No clear statistical winner
- Safety checks failing

**Solution**:
```bash
# Check experiment status
python3 -c "
from ab_testing_engine import ABTestingEngine
engine = ABTestingEngine()
exp = engine.get_experiment_details('experiment-id')
print(f'Status: {exp[\"status\"]}')
print(f'Samples: {exp[\"variants\"]}')
"
```

### Issue: Registry Corruption

**Solution**:
The registry has built-in recovery:
- Backup created before each write
- Automatic recovery on corruption
- Manual restore: copy from `.github/agent-system/ab_tests_registry.json.backup`

## Best Practices

### 1. Start Small

Begin with:
- Low-priority workflows
- Few concurrent experiments (2-3)
- Dry-run mode initially

### 2. Monitor Closely

- Check dashboard daily
- Review experiment progress
- Watch for anomalies

### 3. Gradual Rollout

When deploying winners:
- Test on staging first
- Deploy during low-traffic periods
- Monitor for 24 hours before considering permanent

### 4. Document Changes

When rolling out:
- Document the change in commit message
- Reference the experiment ID
- Include before/after metrics

### 5. Learn from Data

- Review completed experiments regularly
- Look for patterns in winners
- Adjust strategy based on results

## Integration with Existing Systems

### Performance Tracking

Integrates with:
- Agent performance metrics
- Workflow execution logs
- GitHub Actions analytics

### Monitoring

Can be extended to integrate with:
- Prometheus/Grafana
- DataDog
- Custom monitoring solutions

### Notifications

Can be enhanced with:
- Email notifications on winners
- Slack alerts for completions
- Custom webhooks

## Future Enhancements

Potential improvements:
- [ ] Multi-variant testing (>2 variants)
- [ ] Time-based variant scheduling
- [ ] Cost optimization metrics
- [ ] Integration with external monitoring
- [ ] Automatic rollback on failures
- [ ] Machine learning for opportunity prediction
- [ ] Cross-workflow experiment coordination
- [ ] A/B test templates library

## Credits

**Created by**: @workflows-tech-lead  
**Inspired by**: Martha Graham - Choreographic precision  
**Philosophy**: Safety-first, data-driven, continuously improving

---

*Part of the Chained Autonomous AI System - Where agents compete, collaborate, and evolve.*
