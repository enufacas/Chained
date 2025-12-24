# Self-Evolving Neural Architectures

This directory contains neural architecture configurations for workflow adaptation, created by **@create-botter**.

## Purpose

Each file represents a self-evolving neural architecture for a specific GitHub Actions workflow. These architectures automatically adapt their structure and parameters based on workflow execution success rates.

## File Format

Each architecture file (`workflow_name.json`) contains:

- **Neural network layers**: Input, hidden, and output layers with neurons
- **Weights and biases**: Connection strengths between neurons
- **Success history**: Recent execution outcomes for learning
- **Evolution metrics**: Tracking of architectural adaptations
- **Pattern recognition**: Detected execution patterns (time of day, etc.)

## How It Works

1. **Monitoring**: System tracks workflow execution outcomes (success/failure)
2. **Learning**: Neural network adjusts weights based on results
3. **Evolution**: When success rate drops below threshold (default 70%), architecture evolves
4. **Adaptation**: Network grows neurons, prunes weak connections, or adjusts learning rate
5. **Recommendations**: Evolved architecture provides optimized parameters (timeout, retries, etc.)

## Evolution Strategies

- **Aggressive**: For success rates < 30% - adds neurons, resets weak connections
- **Moderate**: For success rates 30-50% - selective pruning and growth
- **Fine-tuning**: For success rates 50-70% - weight adjustments only

## Usage

Architectures are automatically managed by the `neural-architecture-evolution.yml` workflow. Manual operations:

```bash
# Record execution
python tools/self_evolving_neural_architecture.py --workflow "Workflow Name" --record success

# Get recommendations
python tools/self_evolving_neural_architecture.py --workflow "Workflow Name" --recommend

# Force evolution
python tools/self_evolving_neural_architecture.py --workflow "Workflow Name" --evolve

# View status
python tools/self_evolving_neural_architecture.py --workflow "Workflow Name" --status

# System-wide report
python tools/self_evolving_neural_architecture.py --report
```

## Architecture Lifecycle

1. **Initialization**: New workflow gets a default 3-layer architecture (5 inputs → 3 hidden → 4 outputs)
2. **Training**: As workflow executes, system records outcomes and adjusts weights
3. **Evolution**: Architecture structure changes when performance drops
4. **Optimization**: Successful patterns emerge and architecture stabilizes
5. **Continuous Learning**: Ongoing adaptation to changing conditions

## Created By

🤖 **@create-botter** - Inventive and visionary infrastructure creation inspired by Nikola Tesla
