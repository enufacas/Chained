# Self-Evolving Neural Architecture for Workflow Adaptation

**Created by @create-botter** - Inventive and visionary infrastructure inspired by Nikola Tesla

## Overview

This system implements a self-evolving neural architecture that automatically adapts GitHub Actions workflows based on their execution success rates. The architecture learns from workflow outcomes and evolves its structure to optimize performance.

## Key Features

### 🧠 Neural Architecture
- **Multi-layer neural network**: Input → Hidden → Output layers
- **Dynamic structure**: Neurons and connections grow/shrink based on performance
- **Adaptive learning**: Learning rate adjusts based on improvement trends
- **Pattern recognition**: Detects temporal patterns (time of day, day of week)

### 🧬 Self-Evolution
- **Automatic structure modification**: Adds/removes neurons when performance drops
- **Smart pruning**: Removes weak connections and low-contribution neurons
- **Growth strategies**: Targeted neuron addition based on performance level
- **Weight adaptation**: Continuous adjustment via gradient descent

### 📊 Success Rate Tracking
- **GitHub API integration**: Fetches workflow execution history
- **Rolling success rates**: Calculates performance over configurable windows
- **Threshold monitoring**: Triggers evolution when performance drops below 70%
- **Execution recording**: Stores outcomes for neural learning

### 🔄 Automated Workflow
- **Scheduled execution**: Runs every 6 hours to check all workflows
- **Real-time learning**: Records executions as workflows complete
- **PR-based updates**: Creates PRs with evolved architectures
- **Comprehensive reporting**: Generates evolution and success rate reports

## Architecture Overview

### Neural Network Structure

```
Input Layer (5 neurons)
    ├── hour_of_day (normalized 0-1)
    ├── day_of_week (normalized 0-1)
    ├── recent_success_rate (0-1)
    ├── execution_frequency (0-1)
    └── avg_duration (normalized 0-1)
         ↓
Hidden Layer (3-20 neurons, evolves)
    ├── hidden1_0
    ├── hidden1_1
    └── hidden1_2 (+ more as needed)
         ↓
Output Layer (4 neurons)
    ├── timeout (scaled to 30-300 minutes)
    ├── retries (scaled to 1-5)
    ├── concurrency (scaled to 1-10)
    └── priority (scaled to 0-100)
```

### Evolution Strategies

#### 1. Aggressive Evolution (Success < 30%)
- **Prune**: Remove underperforming neurons
- **Grow**: Add 2 new neurons with random weights
- **Reset**: Randomize weak connections
- **Learn**: Increase learning rate by 50%

#### 2. Moderate Evolution (Success 30-50%)
- **Prune**: Remove very weak neurons only
- **Grow**: Add 1 new neuron
- **Adjust**: Strengthen successful pathways

#### 3. Fine-Tuning (Success 50-70%)
- **No structure changes**: Keep architecture intact
- **Weight adjustment**: Fine-tune connection strengths
- **Reduce learning rate**: Stabilize for convergence

## File Structure

```
.github/agent-system/evolving_architectures/
├── README.md                    # This file
├── .gitkeep                     # Directory marker
├── workflow_name_1.json         # Architecture for workflow 1
├── workflow_name_2.json         # Architecture for workflow 2
└── ...                          # One file per workflow

tools/
├── self_evolving_neural_architecture.py  # Core neural architecture system
└── workflow_success_tracker.py           # GitHub API integration

.github/workflows/
└── neural-architecture-evolution.yml     # Automation workflow

tests/
└── test_self_evolving_neural_architecture.py  # Comprehensive tests
```

## Usage

### Automatic Operation (Recommended)

The system runs automatically via the `neural-architecture-evolution.yml` workflow:

1. **Every 6 hours**: Checks all workflow success rates
2. **Records executions**: Tracks outcomes for learning
3. **Triggers evolution**: Adapts architectures below 70% success
4. **Creates PRs**: Updates architecture files via pull request

No manual intervention required!

### Manual Operations

#### Track Workflow Success Rates

```bash
# Generate comprehensive report
python tools/workflow_success_tracker.py --report --days 7

# Show statistics
python tools/workflow_success_tracker.py --stats --days 7

# JSON output
python tools/workflow_success_tracker.py --stats --json --days 7
```

#### Record Workflow Executions

```bash
# Record last 7 days of executions
python tools/workflow_success_tracker.py --record --days 7

# Record last 30 days
python tools/workflow_success_tracker.py --record --days 30
```

#### Trigger Evolution

```bash
# Evolve all workflows below threshold
python tools/workflow_success_tracker.py --evolve --days 7

# Evolve specific workflow
python tools/self_evolving_neural_architecture.py \
  --workflow "Workflow Name" --evolve

# Evolve all architectures
python tools/self_evolving_neural_architecture.py --evolve-all
```

#### Get Recommendations

```bash
# Get optimized parameters for a workflow
python tools/self_evolving_neural_architecture.py \
  --workflow "Workflow Name" --recommend

# JSON output
python tools/self_evolving_neural_architecture.py \
  --workflow "Workflow Name" --recommend --json
```

#### View Status and Reports

```bash
# Show architecture status
python tools/self_evolving_neural_architecture.py \
  --workflow "Workflow Name" --status

# Generate full report
python tools/self_evolving_neural_architecture.py --report

# System summary
python tools/self_evolving_neural_architecture.py --summary
```

## Architecture File Format

Each workflow's architecture is stored in JSON format:

```json
{
  "workflow_name": "Example Workflow",
  "version": "1.0.0",
  "last_updated": "2025-12-24T10:00:00Z",
  "config": {
    "base_learning_rate": 0.01,
    "success_rate_threshold": 0.7,
    "min_hidden_neurons": 2,
    "max_hidden_neurons": 20
  },
  "layers": [
    {
      "layer_id": 0,
      "layer_type": "input",
      "neurons": [...]
    },
    {
      "layer_id": 1,
      "layer_type": "hidden",
      "neurons": [...]
    },
    {
      "layer_id": 2,
      "layer_type": "output",
      "neurons": [...]
    }
  ],
  "success_history": [1.0, 1.0, 0.0, 1.0, ...],
  "execution_count": 42,
  "evolution_count": 3,
  "last_evolution_time": "2025-12-24T08:00:00Z",
  "current_learning_rate": 0.009,
  "architecture_fitness": 0.85,
  "patterns": [...]
}
```

## Configuration

### Evolution Parameters

Edit in `self_evolving_neural_architecture.py` → `ArchitectureEvolutionConfig`:

```python
base_learning_rate = 0.01           # Initial learning rate
min_learning_rate = 0.001           # Minimum learning rate
max_learning_rate = 0.1             # Maximum learning rate
success_rate_threshold = 0.7        # Trigger evolution below this
evolution_interval = 10             # Minimum executions between evolutions
min_data_for_evolution = 5          # Minimum data points needed
min_hidden_neurons = 2              # Minimum neurons in hidden layer
max_hidden_neurons = 20             # Maximum neurons in hidden layer
neuron_prune_threshold = 0.1        # Remove neurons with low contribution
```

### Workflow Schedule

Edit in `neural-architecture-evolution.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours (change as needed)
```

## How It Works

### 1. Data Collection

The `workflow_success_tracker.py` module:
- Fetches workflow runs from GitHub API
- Calculates success rates over configurable time windows
- Identifies workflows performing below threshold
- Records execution outcomes in neural architectures

### 2. Neural Learning

The `self_evolving_neural_architecture.py` module:
- Maintains a neural network for each workflow
- Records success/failure for each execution
- Adjusts weights via backpropagation
- Detects temporal patterns in execution

### 3. Evolution Trigger

Evolution occurs when:
- Success rate drops below 70% (configurable)
- Minimum data points available (5+ executions)
- Evolution interval elapsed (10+ executions since last evolution)

### 4. Architecture Adaptation

Based on success rate:
- **< 30%**: Aggressive changes (add neurons, reset weights)
- **30-50%**: Moderate changes (selective growth/pruning)
- **50-70%**: Fine-tuning (weight adjustments only)

### 5. Parameter Recommendations

Evolved architecture generates recommendations:
- **Timeout**: 30-300 minutes
- **Retries**: 1-5 attempts
- **Concurrency**: 1-10 parallel jobs
- **Priority**: 0-100 scheduling priority

## Testing

Comprehensive test suite validates:
- ✅ Neuron activation and weight adjustment
- ✅ Layer forward propagation
- ✅ Architecture initialization
- ✅ Evolution triggers
- ✅ Neuron growth and pruning
- ✅ Success rate tracking
- ✅ Save/load persistence
- ✅ Pattern recognition
- ✅ Multi-workflow isolation

Run tests:

```bash
pytest tests/test_self_evolving_neural_architecture.py -v
```

## Benefits

### 🎯 Automatic Optimization
- **No manual tuning**: System adapts parameters automatically
- **Data-driven decisions**: Based on real execution outcomes
- **Continuous improvement**: Evolves as patterns change

### 🧬 Self-Adaptation
- **Dynamic structure**: Grows/shrinks based on complexity needs
- **Smart pruning**: Removes ineffective components
- **Targeted growth**: Adds neurons where needed most

### 📊 Visibility
- **Comprehensive reports**: Detailed evolution and success metrics
- **Pattern insights**: Shows detected execution patterns
- **Architecture transparency**: Full visibility into neural structure

### 🔄 Automation
- **Scheduled runs**: Automated monitoring and adaptation
- **PR integration**: Changes reviewed before merging
- **No maintenance**: Self-managing system

## Example Report

```
🧠 Self-Evolving Neural Architecture Report
==============================================================
Workflow: CI/CD Pipeline

📊 Performance Metrics:
   Success Rate: 85.0%
   Executions: 42
   Evolutions: 3
   Architecture Fitness: 85.0%
   Current Learning Rate: 0.0095

🏗️ Architecture:
   Structure: 5 -> 4 -> 4
   Layer 0 (input): 5 neurons
   Layer 1 (hidden): 4 neurons
   Layer 2 (output): 4 neurons

🔍 Recognized Patterns:
   time_morning: 12 occurrences (confidence: 88.0%)
   time_afternoon: 15 occurrences (confidence: 82.0%)
   day_monday: 8 occurrences (confidence: 75.0%)

⏰ Last Evolution: 2025-12-24T08:15:30Z

==============================================================
🤖 Report generated by @create-botter
```

## Future Enhancements

Potential improvements:
- **Transfer learning**: Share patterns across similar workflows
- **Multi-objective optimization**: Balance success, speed, and cost
- **Anomaly detection**: Flag unusual execution patterns
- **Reinforcement learning**: Direct policy optimization
- **Explainable AI**: Understand why recommendations are made

## Technical Details

### Neural Activation
- **Function**: Sigmoid (bounded 0-1 output)
- **Weight updates**: Gradient descent with momentum
- **Learning rate**: Adaptive (0.001-0.1 range)
- **Weight clipping**: Prevents explosion (-5 to +5)

### Pattern Recognition
- **Time patterns**: Hour of day, day of week
- **Confidence tracking**: Bayesian-style confidence updates
- **Occurrence counting**: Frequency-based pattern strength

### Persistence
- **Format**: JSON with full architecture state
- **Location**: `.github/agent-system/evolving_architectures/`
- **Versioning**: Each file includes version and timestamps

## Credits

Created by **@create-botter** - Part of the Chained autonomous AI ecosystem.

Inspired by:
- **Nikola Tesla**: Inventive thinking and bold vision
- **Neuroevolution**: Self-adapting neural architectures
- **Gradient Descent**: Classic neural network learning
- **Genetic Algorithms**: Evolution-based optimization

## Related Documentation

- [Self-Evolving Neural Architecture Code](../../tools/self_evolving_neural_architecture.py)
- [Workflow Success Tracker](../../tools/workflow_success_tracker.py)
- [Evolution Workflow](../workflows/neural-architecture-evolution.yml)
- [Test Suite](../../tests/test_self_evolving_neural_architecture.py)

---

*"The present is theirs; the future, for which I really worked, is mine."* - Nikola Tesla
