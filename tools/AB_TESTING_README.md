# A/B Testing System for Workflow Configurations

## Overview

The A/B Testing System enables autonomous experimentation with different workflow configurations in the Chained ecosystem. It provides a rigorous, statistical approach to evaluating and optimizing workflow parameters.

**Author**: @engineer-master  
**Design Philosophy**: Systematic, defensive, and data-driven

## Architecture

### Core Components

1. **A/B Testing Engine** (`ab_testing_engine.py`)
   - Manages experiment lifecycle
   - Tracks variant performance
   - Performs statistical analysis
   - Determines winners

2. **Integration Helper** (`ab_testing_helper.py`)
   - CLI interface for workflows
   - Sample recording
   - Variant selection
   - Experiment creation

3. **Experiment Manager Workflow** (`ab-testing-manager.yml`)
   - Daily experiment analysis
   - Winner detection
   - Results reporting
   - Automated issue creation

### Data Model

Experiments are stored in `.github/agent-system/ab_tests_registry.json` with the following structure:

```json
{
  "version": "1.0.0",
  "experiments": [
    {
      "id": "exp-abc123def456",
      "name": "Auto-Review Schedule Optimization",
      "description": "Testing different schedule frequencies",
      "workflow_name": "auto-review-merge",
      "created_at": "2025-11-14T03:00:00Z",
      "status": "active",
      "variants": {
        "control": {
          "config": {"schedule": "*/15 * * * *"},
          "samples": [],
          "metrics": {
            "execution_time": [],
            "success_rate": []
          },
          "total_samples": 0
        },
        "variant_a": {
          "config": {"schedule": "*/10 * * * *"},
          "samples": [],
          "metrics": {
            "execution_time": [],
            "success_rate": []
          },
          "total_samples": 0
        }
      },
      "metrics": ["execution_time", "success_rate"],
      "results": null
    }
  ],
  "config": {
    "min_samples_per_variant": 10,
    "confidence_threshold": 0.95,
    "min_improvement_threshold": 0.05,
    "max_experiment_duration_days": 14
  }
}
```

## Usage Guide

### Creating an Experiment

#### Via Python API

```python
from ab_testing_engine import ABTestingEngine

engine = ABTestingEngine()

variants = {
    "control": {
        "schedule": "*/15 * * * *",
        "description": "Current 15-minute schedule"
    },
    "variant_a": {
        "schedule": "*/10 * * * *",
        "description": "More frequent 10-minute schedule"
    }
}

exp_id = engine.create_experiment(
    name="Schedule Optimization",
    description="Testing different schedule frequencies",
    variants=variants,
    metrics=["execution_time", "success_rate"],
    workflow_name="auto-review-merge"
)
```

#### Via CLI

```bash
# Create variants JSON file
cat > variants.json << 'EOF'
{
  "control": {"schedule": "*/15 * * * *"},
  "variant_a": {"schedule": "*/10 * * * *"}
}
EOF

# Create experiment
python3 tools/ab_testing_helper.py create \
  "Schedule Optimization" \
  "Testing different schedule frequencies" \
  variants.json \
  --metrics execution_time,success_rate \
  --workflow-name auto-review-merge
```

#### Via Workflow

Trigger the `ab-testing-manager` workflow with action `create_example` to create a sample experiment.

### Recording Samples

Workflows can record performance samples for ongoing experiments:

#### From GitHub Actions Workflow

```yaml
- name: Record A/B Test Sample
  if: always()  # Record even if workflow fails
  run: |
    # Get execution time and success status
    execution_time=${{ steps.some_step.outputs.duration }}
    success_rate=${{ steps.some_step.outputs.success_rate }}
    
    # Record sample
    python3 tools/ab_testing_helper.py record \
      ${{ env.EXPERIMENT_ID }} \
      ${{ env.VARIANT_NAME }} \
      --metric execution_time=${execution_time} \
      --metric success_rate=${success_rate} \
      --metadata run_id=${{ github.run_id }} \
      --metadata workflow=${{ github.workflow }}
```

#### From Python

```python
from ab_testing_engine import ABTestingEngine

engine = ABTestingEngine()

engine.record_sample(
    experiment_id="exp-abc123def456",
    variant_name="variant_a",
    metrics={
        "execution_time": 45.2,
        "success_rate": 0.95
    },
    metadata={
        "run_id": "12345",
        "workflow": "auto-review-merge"
    }
)
```

### Analyzing Experiments

#### Automatic Analysis

The `ab-testing-manager` workflow runs daily to analyze all active experiments. It will:
1. Check if sufficient data has been collected
2. Perform statistical analysis
3. Determine if there's a clear winner
4. Create issues for experiments with winners

#### Manual Analysis

```bash
# Analyze a specific experiment
python3 tools/ab_testing_engine.py analyze exp-abc123def456

# Or via helper
python3 tools/ab_testing_helper.py analyze exp-abc123def456
```

#### Programmatic Analysis

```python
from ab_testing_engine import ABTestingEngine

engine = ABTestingEngine()
analysis = engine.analyze_experiment("exp-abc123def456")

if analysis["status"] == "analyzed" and analysis["winner"]:
    winner = analysis["winner"]
    print(f"Winner: {winner['variant']}")
    print(f"Improvement: {winner['improvement']:.2%}")
    print(f"Confidence: {winner['confidence']}")
```

### Completing an Experiment

Once a winner is determined and you've rolled out the winning configuration:

```python
from ab_testing_engine import ABTestingEngine

engine = ABTestingEngine()

engine.complete_experiment(
    experiment_id="exp-abc123def456",
    winner="variant_a",
    notes="Variant A showed 15% improvement. Rolled out to production."
)
```

## Integration Examples

### Example 1: Testing Workflow Schedule Frequencies

Test different cron schedules for a workflow:

```python
variants = {
    "control": {"schedule": "0 */6 * * *"},  # Every 6 hours
    "variant_a": {"schedule": "0 */4 * * *"},  # Every 4 hours
    "variant_b": {"schedule": "0 */8 * * *"}   # Every 8 hours
}

exp_id = engine.create_experiment(
    name="Learning Workflow Schedule",
    description="Optimize schedule for learning from TLDR",
    variants=variants,
    metrics=["execution_time", "articles_processed", "cpu_usage"],
    workflow_name="learn-from-tldr"
)
```

### Example 2: Testing Agent Selection Algorithms

Test different algorithms for matching issues to agents:

```python
variants = {
    "control": {"algorithm": "keyword_matching", "threshold": 0.7},
    "variant_a": {"algorithm": "ml_classifier", "threshold": 0.8},
    "variant_b": {"algorithm": "hybrid", "threshold": 0.75}
}

exp_id = engine.create_experiment(
    name="Agent Matching Algorithm",
    description="Compare agent selection algorithms",
    variants=variants,
    metrics=["match_quality", "assignment_time", "success_rate"],
    workflow_name="agent-spawner"
)
```

### Example 3: Testing Resource Limits

Test different resource configurations:

```python
variants = {
    "control": {"timeout": 300, "max_retries": 3},
    "variant_a": {"timeout": 600, "max_retries": 2},
    "variant_b": {"timeout": 450, "max_retries": 4}
}

exp_id = engine.create_experiment(
    name="Workflow Resource Limits",
    description="Optimize timeout and retry settings",
    variants=variants,
    metrics=["success_rate", "avg_completion_time", "failure_rate"],
    workflow_name="auto-review-merge"
)
```

## Statistical Analysis

### Metrics

The system tracks multiple metrics per variant:

- **Mean**: Average value across all samples
- **Min**: Minimum observed value
- **Max**: Maximum observed value
- **Count**: Number of samples collected

### Winner Determination

A variant is declared the winner if:

1. **Sufficient Data**: All variants have at least `min_samples_per_variant` samples (default: 10)
2. **Significant Improvement**: Winner shows at least `min_improvement_threshold` improvement (default: 5%)
3. **Statistical Confidence**: Winner has confidence level above threshold (default: 95%)

### Future Enhancements

The current implementation uses simplified statistical analysis. Future versions could include:

- **T-tests**: For comparing means with statistical significance
- **Chi-square tests**: For categorical outcomes
- **Bayesian analysis**: For continuous learning and updating
- **Multi-armed bandit**: For adaptive variant selection
- **Sequential testing**: For early stopping when winner is clear

## Best Practices

### 1. Define Clear Metrics

Choose metrics that directly reflect your optimization goals:

- **Performance**: `execution_time`, `throughput`, `latency`
- **Reliability**: `success_rate`, `error_rate`, `uptime`
- **Resource Usage**: `cpu_usage`, `memory_usage`, `api_calls`
- **Quality**: `code_quality_score`, `review_score`, `bug_rate`

### 2. Start Small

Begin with 2-3 variants. Too many variants require more samples and time.

### 3. Run Experiments Long Enough

Ensure experiments run through different conditions:
- Different times of day
- Weekdays vs weekends
- Various load patterns

The default maximum duration is 14 days.

### 4. Control for External Factors

Document and account for external changes:
- GitHub API rate limits
- Network conditions
- Repository activity levels

### 5. Document Learnings

When completing experiments, include detailed notes:

```python
engine.complete_experiment(
    experiment_id=exp_id,
    winner="variant_a",
    notes="""
    Variant A showed 15% improvement in execution time while maintaining
    same success rate. No increase in API rate limit issues observed.
    Rolled out to production on 2025-11-14.
    
    Key learnings:
    - More frequent execution did not cause rate limit issues
    - Lower latency improved overall system responsiveness
    - Consider testing even more frequent schedules in future
    """
)
```

## Monitoring and Debugging

### List All Experiments

```bash
# List all experiments
python3 tools/ab_testing_engine.py list

# List only active experiments
python3 tools/ab_testing_engine.py list active

# List only completed experiments
python3 tools/ab_testing_engine.py list completed
```

### View Experiment Details

```bash
python3 tools/ab_testing_engine.py details exp-abc123def456
```

### Check Workflow Summary

The `ab-testing-manager` workflow provides a summary in the GitHub Actions UI showing:
- Number of active experiments
- Sample counts per experiment
- Analysis results

## Security Considerations

### Data Privacy

- Experiment data is stored in the repository
- Do not include sensitive data in metrics or metadata
- Variant configurations should not contain secrets

### Access Control

- Only repository collaborators can create experiments
- Workflows use `GITHUB_TOKEN` with appropriate permissions
- Registry file is protected by branch protection rules

### Defensive Programming

Following @engineer-master principles:

- **Atomic Updates**: Registry updates use temp files and atomic rename
- **Input Validation**: All inputs are validated before processing
- **Error Handling**: Comprehensive error handling with clear messages
- **Defensive Defaults**: Safe defaults for all configuration parameters

## Troubleshooting

### Issue: Experiment not collecting data

**Cause**: Workflow not recording samples

**Solution**: Ensure workflow includes sample recording step:

```yaml
- name: Record Sample
  run: |
    python3 tools/ab_testing_helper.py record \
      $EXPERIMENT_ID $VARIANT_NAME \
      --metric your_metric=123
```

### Issue: Analysis shows insufficient data

**Cause**: Not enough samples collected (< 10 per variant by default)

**Solution**: 
- Wait for more workflow runs
- Or lower `min_samples_per_variant` in registry config

### Issue: No clear winner detected

**Cause**: Variants performing similarly

**Solution**:
- Run experiment longer
- Consider if improvement threshold is too high
- Review if metrics are sensitive enough

## Contributing

When enhancing the A/B testing system:

1. **Add Tests**: Include comprehensive tests for new features
2. **Update Documentation**: Keep this README current
3. **Follow Patterns**: Use existing code style and patterns
4. **Defensive Code**: Validate inputs, handle errors, use atomic operations
5. **Mention @engineer-master**: Follow attribution guidelines

## References

- **Agent System**: `.github/agent-system/README.md`
- **Workflow Documentation**: `docs/WORKFLOWS.md`
- **Engineer Master Profile**: `.github/agents/engineer-master.md`

---

*Built by @engineer-master with rigorous engineering principles*  
*Following Margaret Hamilton's legacy of reliable, systematic design*
