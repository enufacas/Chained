# Autonomous A/B Testing for Workflow Configurations

**Author**: @create-botter  
**Created**: 2025-11-26

## Overview

This system provides autonomous A/B testing capabilities for GitHub Actions workflow configurations. It automatically identifies optimization opportunities, generates configuration variants, and manages experiments to find optimal workflow settings.

## System Components

### 1. Workflow Configuration Generator (`tools/workflow_config_generator.py`)

Automatically generates workflow configuration variants for A/B testing.

**Features:**
- Schedule frequency optimization
- Timeout configuration variants
- Concurrency setting variants
- Retry strategy variants

**Usage:**

```bash
# Generate experiment config for a workflow
python3 tools/workflow_config_generator.py \
  .github/workflows/my-workflow.yml \
  schedule \
  --output experiment-config.json

# Available optimization types: schedule, timeout, concurrency, retry
```

**Example Output:**
```json
{
  "name": "my-workflow - Schedule Optimization",
  "description": "A/B test different schedule configurations",
  "variants": {
    "control": {
      "name": "Current Schedule",
      "config": {"schedule": "0 */6 * * *"}
    },
    "less_frequent": {
      "name": "Less Frequent",
      "config": {"schedule": "0 */12 * * *"}
    },
    "more_frequent": {
      "name": "More Frequent",
      "config": {"schedule": "0 */3 * * *"}
    }
  },
  "metrics": ["execution_time", "success_rate", "resource_usage"]
}
```

### 2. Workflow A/B Testing Integration (`tools/workflow_ab_testing_integration.py`)

Integrates configuration generation with the A/B testing engine.

**Commands:**

#### Create Single Experiment
```bash
python3 tools/workflow_ab_testing_integration.py create \
  .github/workflows/my-workflow.yml \
  timeout
```

#### Auto-Create Multiple Experiments
```bash
# Create up to 5 experiments from high-priority opportunities
python3 tools/workflow_ab_testing_integration.py auto-create \
  --max 5 \
  --priority high
```

#### Get Recommendations
```bash
# Get top 10 experiment recommendations
python3 tools/workflow_ab_testing_integration.py recommend --limit 10
```

**Example Output:**
```
💡 Top 3 Experiment Recommendations:

1. gemini-fix - timeout
   Priority: medium | Impact: medium
   Test different timeout configurations for gemini-fix

2. agent-spawning - timeout
   Priority: medium | Impact: medium
   Test different timeout configurations for agent-spawning

3. gemini-review - timeout
   Priority: medium | Impact: medium
   Test different timeout configurations for gemini-review
```

#### Generate Experiment Report
```bash
# Text format (default)
python3 tools/workflow_ab_testing_integration.py report exp-abc123

# Markdown format
python3 tools/workflow_ab_testing_integration.py report exp-abc123 --format markdown

# JSON format
python3 tools/workflow_ab_testing_integration.py report exp-abc123 --format json
```

### 3. A/B Testing Engine (`tools/ab_testing_engine.py`)

Core engine for managing experiments (already existing).

**Key Features:**
- Experiment lifecycle management
- Sample tracking and storage
- Statistical analysis
- Winner determination

### 4. Workflow Analyzer (`tools/ab_testing_workflow_analyzer.py`)

Analyzes workflows to identify optimization opportunities (already existing).

## Configuration Templates

### Schedule Optimization

**Pre-defined variants:**
- **Less Frequent**: 2x the interval (reduces load)
- **More Frequent**: 0.5x the interval (faster feedback)
- **Off-Peak**: Shift timing by 4 hours

### Timeout Optimization

**Pre-defined variants:**
- **Conservative**: 1.5x current timeout (reliability)
- **Aggressive**: 0.7x current timeout (faster feedback)
- **Adaptive**: Based on historical 95th percentile

### Concurrency Optimization

**Pre-defined variants:**
- **Sequential**: One at a time (safest)
- **Parallel**: Allow parallel execution
- **Cancel Old**: Cancel old runs when new starts

### Retry Strategy

**Pre-defined variants:**
- **No Retry**: Fail fast (max_attempts: 1)
- **Moderate**: 2 retries (max_attempts: 3)
- **Aggressive**: 5 retries (max_attempts: 6)

## Workflow Integration

### Autonomous A/B Testing Workflow

The system runs automatically via `.github/workflows/autonomous-ab-testing.yml`:

- **Schedule**: Daily at 2 AM UTC
- **Trigger**: Manual workflow_dispatch
- **Actions**:
  1. Analyzes all workflows for opportunities
  2. Creates new experiments (up to max_concurrent)
  3. Collects metrics for active experiments
  4. Analyzes results and detects winners
  5. Completes experiments with clear outcomes
  6. Updates dashboard

### Manual Workflow

For manual experimentation:

1. **Identify Opportunity**
   ```bash
   python3 tools/workflow_ab_testing_integration.py recommend --limit 10
   ```

2. **Create Experiment**
   ```bash
   python3 tools/workflow_ab_testing_integration.py create \
     .github/workflows/target-workflow.yml \
     timeout
   ```

3. **Monitor Progress**
   ```bash
   python3 tools/workflow_ab_testing_integration.py report exp-abc123
   ```

4. **Check Dashboard**
   Open `docs/ab-testing-dashboard.html` in browser

## Metrics Tracked

Each experiment tracks:
- **execution_time**: How long the workflow takes
- **success_rate**: Percentage of successful runs
- **resource_usage**: CPU/memory consumption
- **failure_rate**: Percentage of failed runs

## Statistical Analysis

The system uses:
- **Minimum samples**: 10-20 per variant
- **Confidence level**: 95%
- **Minimum improvement**: 5%
- **T-tests** for continuous metrics
- **Chi-squared** for proportions

## Best Practices

### When to A/B Test

✅ **Good candidates:**
- Workflows running frequently (daily or more)
- High-cost workflows (long execution time)
- Workflows with variable success rates
- Critical path workflows

❌ **Avoid testing:**
- Workflows running rarely (weekly or less)
- Protected/security workflows
- Workflows with external dependencies

### Experiment Duration

- **Minimum**: 7 days for statistical significance
- **Maximum**: 14 days to avoid stale configs
- **Sample size**: At least 20 runs per variant

### Priority Levels

- **High**: Critical workflows, high potential impact
- **Medium**: Regular workflows, moderate impact
- **Low**: Minor workflows, small improvements

## Example Scenarios

### Scenario 1: Optimize Scheduled Workflow

```bash
# Step 1: Check current performance
python3 tools/workflow_ab_testing_integration.py recommend --limit 5

# Step 2: Create schedule experiment
python3 tools/workflow_ab_testing_integration.py create \
  .github/workflows/learn-from-tldr.yml \
  schedule

# Step 3: Wait 7 days for data collection

# Step 4: Check results
python3 tools/workflow_ab_testing_integration.py report exp-abc123 --format markdown

# Step 5: If winner detected, update workflow manually
```

### Scenario 2: Batch Create Experiments

```bash
# Auto-create experiments for top opportunities
python3 tools/workflow_ab_testing_integration.py auto-create \
  --max 3 \
  --priority medium

# Monitor all experiments
for exp_id in $(cat .github/agent-system/ab_tests_registry.json | jq -r '.experiments[].id'); do
  python3 tools/workflow_ab_testing_integration.py report $exp_id
done
```

## Testing

Run the test suite:

```bash
# Test workflow config generator
python3 tests/test_workflow_config_generator.py

# Test A/B testing engine
python3 tests/test_autonomous_ab_testing.py

# All tests
python3 -m pytest tests/test_workflow_config_generator.py tests/test_autonomous_ab_testing.py
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         Autonomous A/B Testing System               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐    ┌──────────────────┐    │
│  │  Workflow        │───▶│  Config          │    │
│  │  Analyzer        │    │  Generator       │    │
│  └──────────────────┘    └──────────────────┘    │
│           │                       │                │
│           │                       ▼                │
│           │              ┌──────────────────┐     │
│           └─────────────▶│  Integration     │     │
│                          │  Tool            │     │
│                          └──────────────────┘     │
│                                   │                │
│                                   ▼                │
│                          ┌──────────────────┐     │
│                          │  A/B Testing     │     │
│                          │  Engine          │     │
│                          └──────────────────┘     │
│                                   │                │
│                                   ▼                │
│                          ┌──────────────────┐     │
│                          │  Dashboard       │     │
│                          │  Generator       │     │
│                          └──────────────────┘     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Future Enhancements

- [ ] Integration with RL optimizer for learned insights
- [ ] Real-time metrics collection from GitHub Actions API
- [ ] Multi-armed bandit allocation for faster convergence
- [ ] Bayesian optimization for sequential testing
- [ ] Automated rollout of winning variants
- [ ] Cost-benefit analysis for each experiment
- [ ] Interaction effect testing (multiple parameters)

## References

- [A/B Testing Engine](tools/ab_testing_engine.py)
- [Workflow Config Generator](tools/workflow_config_generator.py)
- [Integration Tool](tools/workflow_ab_testing_integration.py)
- [Workflow Analyzer](tools/ab_testing_workflow_analyzer.py)
- [Test Suite](tests/test_workflow_config_generator.py)

---

**Created by @create-botter** - Inspired by Nikola Tesla's inventive approach to system optimization
