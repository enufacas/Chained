# Self-Evolving Neural Architecture System

**Created by @create-botter** - Inspired by Nikola Tesla's visionary approach

## Overview

The Self-Evolving Neural Architecture is an advanced system that automatically adapts workflow configurations based on their success rates. It uses neural network-inspired algorithms to learn from workflow execution outcomes and continuously evolve its structure to improve performance.

## Key Features

### 🧠 Multi-Layer Neural Architecture
- **Input Layer**: Captures workflow context (time of day, execution frequency, success history)
- **Hidden Layers**: Dynamically evolving neurons that learn patterns
- **Output Layer**: Generates optimized workflow parameter recommendations

### 🧬 Self-Evolution Capabilities
- Automatically adds neurons when learning capacity is insufficient
- Prunes underperforming neurons to maintain efficiency
- Adjusts connection weights based on success feedback
- Adapts learning rate based on performance trends

### 📊 Success Rate-Based Learning
- Tracks execution outcomes (success/failure)
- Computes rolling success rates
- Triggers evolution when success drops below threshold (default: 70%)
- Three evolution strategies based on severity:
  - **Fine Tuning**: Minor weight adjustments
  - **Moderate Evolution**: Limited structural changes
  - **Aggressive Evolution**: Significant restructuring

### 🔍 Pattern Recognition
- Identifies time-based patterns (morning, afternoon, etc.)
- Recognizes day-of-week patterns
- Builds confidence in patterns over time
- Uses patterns to improve predictions

## Architecture

```
                    ┌─────────────────────┐
                    │    Input Layer      │
                    │ (5 context features)│
                    └─────────┬───────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │           Hidden Layer(s)               │
        │ (Dynamic: grows/shrinks based on need)  │
        └─────────────────────┬───────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │    Output Layer     │
                    │ (4 parameter outputs)│
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Recommendations    │
                    │ timeout, retries,   │
                    │ concurrency, priority│
                    └─────────────────────┘
```

## Usage

### Python API

```python
from self_evolving_neural_architecture import (
    SelfEvolvingNeuralArchitecture,
    EvolvingArchitectureManager
)

# Create or load architecture for a workflow
arch = SelfEvolvingNeuralArchitecture(
    workflow_name="ci-build",
    repo_root="/path/to/repo"
)

# Record execution outcomes
arch.record_execution(success=True)
arch.record_execution(success=False)

# Get recommendations
recommendations = arch.get_recommendations()
print(f"Recommended timeout: {recommendations['timeout']}")
print(f"Recommended retries: {recommendations['retries']}")

# Force evolution
if arch.get_success_rate() < 0.7:
    arch.evolve()

# Generate report
print(arch.generate_report())
```

### Using the Manager

```python
# Manage multiple workflows
manager = EvolvingArchitectureManager()

# Record executions
manager.record_execution("ci-build", success=True)
manager.record_execution("tests", success=False)

# Get recommendations
recs = manager.get_recommendations("ci-build")

# Evolve all architectures
manager.evolve_all()

# Get system summary
print(manager.generate_full_report())
```

### Command Line Interface

```bash
# Record an execution
python tools/self_evolving_neural_architecture.py \
  --workflow "my-workflow" \
  --record success

# Get recommendations
python tools/self_evolving_neural_architecture.py \
  --workflow "my-workflow" \
  --recommend

# Force evolution
python tools/self_evolving_neural_architecture.py \
  --workflow "my-workflow" \
  --evolve

# Evolve all workflows
python tools/self_evolving_neural_architecture.py --evolve-all

# Get status
python tools/self_evolving_neural_architecture.py \
  --workflow "my-workflow" \
  --status

# Generate reports
python tools/self_evolving_neural_architecture.py --report
python tools/self_evolving_neural_architecture.py --summary --json
```

## GitHub Actions Integration

The system integrates with GitHub Actions through the `neural-architecture-evolution.yml` workflow:

### Automatic Learning
The workflow automatically records execution outcomes when any workflow completes:
- Success → positive feedback
- Failure → negative feedback

### Scheduled Evolution
Every 6 hours, the system:
1. Reviews all tracked workflows
2. Identifies underperforming architectures
3. Triggers evolution for those below threshold
4. Commits updated architecture configurations

### Manual Operations
Use `workflow_dispatch` to:
- Force evolution for specific workflows
- Generate detailed reports
- Get quick summaries

## Configuration

### Evolution Configuration

```python
ArchitectureEvolutionConfig(
    # Learning parameters
    base_learning_rate=0.01,    # Initial learning rate
    min_learning_rate=0.001,    # Minimum learning rate
    max_learning_rate=0.1,      # Maximum learning rate
    learning_rate_decay=0.99,   # Decay factor
    
    # Evolution triggers
    success_rate_threshold=0.7,  # Evolve if below 70%
    evolution_interval=10,       # Min executions between evolutions
    min_data_for_evolution=5,    # Minimum data points needed
    
    # Architecture constraints
    min_hidden_neurons=2,       # Minimum neurons per layer
    max_hidden_neurons=20,      # Maximum neurons per layer
    max_hidden_layers=3,        # Maximum hidden layers
    
    # Pruning parameters
    neuron_prune_threshold=0.1,     # Remove low-contribution neurons
    connection_prune_threshold=0.01, # Remove weak connections
    
    # Growth parameters
    neuron_growth_rate=0.2,     # Probability of adding neurons
    connection_growth_rate=0.3   # Probability of adding connections
)
```

### Storage Location

Architecture configurations are stored in:
```
.github/agent-system/evolving_architectures/{workflow_name}.json
```

## Data Flow

```
1. Workflow Execution
        │
        ▼
2. Outcome Recording (success/failure)
        │
        ▼
3. Pattern Detection
        │
        ▼
4. Success Rate Check
        │
        ├── Above threshold → Wait for more data
        │
        └── Below threshold → Trigger Evolution
                               │
                               ▼
5. Evolution Strategy Selection
        │
        ├── Very low (<30%) → Aggressive
        ├── Low (<50%) → Moderate
        └── Near threshold → Fine-tune
                               │
                               ▼
6. Architecture Modification
        │
        ▼
7. Weight Adjustment & Learning Rate Update
        │
        ▼
8. Save Updated Configuration
        │
        ▼
9. Generate Recommendations for Next Run
```

## Performance Metrics

The system tracks:
- **Success Rate**: Rolling average of execution outcomes
- **Architecture Fitness**: Overall health of the neural network
- **Evolution Count**: Number of evolution cycles completed
- **Pattern Confidence**: Reliability of recognized patterns
- **Learning Rate**: Current adaptive learning rate

## Best Practices

1. **Allow Learning Time**: Give the system at least 10-20 executions before expecting accurate recommendations

2. **Monitor Evolution**: Review evolution reports to understand what changes are being made

3. **Tune Thresholds**: Adjust `success_rate_threshold` based on your workflow's acceptable failure rate

4. **Review Patterns**: Check recognized patterns to ensure they make sense for your workflows

5. **Persist Data**: The system maintains state across runs - don't delete the architecture JSON files

## Troubleshooting

### Architecture Not Evolving
- Check if you have enough data (`min_data_for_evolution`)
- Verify success rate is below threshold
- Check `evolution_interval` hasn't been exceeded

### Poor Recommendations
- Allow more learning time
- Check if patterns are being recognized correctly
- Consider increasing `max_hidden_neurons` for complex workflows

### Performance Issues
- Prune architectures with too many neurons
- Reduce `max_hidden_layers` if architectures grow too complex

## Related Tools

- `neural_workflow_adapter.py` - Original neural adapter (predecessor)
- `workflow_execution_tracker.py` - Tracks workflow execution times
- `ab_testing_engine.py` - A/B testing for workflow configurations
- `agent-evolution-system.py` - Genetic evolution for agents

## Credits

This system was created by **@create-botter**, inspired by Nikola Tesla's visionary and inventive approach to engineering. The self-evolving nature mirrors Tesla's belief that innovation should adapt and improve continuously.

---

*🤖 Part of the Chained autonomous AI ecosystem*
