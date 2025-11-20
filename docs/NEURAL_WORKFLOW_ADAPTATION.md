# 🧠 Neural Workflow Adaptation System

**Created by @workflows-tech-lead**

A self-evolving neural architecture that automatically adapts workflow configurations based on success rates. This system uses neural network-inspired learning algorithms to optimize workflow parameters for maximum reliability.

## 🎯 Overview

The Neural Workflow Adapter monitors workflow execution patterns and automatically adjusts configuration parameters to achieve optimal performance. It uses concepts from neural networks including:

- **Neural Weights**: Each workflow parameter has an associated weight
- **Gradient Descent**: Weights are adjusted based on success/failure feedback
- **Momentum**: Smooth learning prevents oscillations
- **Backpropagation**: Success rates propagate back to adjust parameters

## 🏗️ Architecture

### Input Layer
- Workflow execution results (success/failure)
- Historical performance metrics
- Success rate trends
- Variance and stability measures

### Hidden Layer (Neural Weights)
Each workflow has neural weights for parameters:
- **timeout_minutes**: Workflow execution timeout
- **max_retries**: Number of retry attempts
- **concurrency_limit**: Maximum concurrent executions
- **cache_enabled**: Whether to use caching (0.0-1.0)

Each weight has:
- `weight`: Neural weight value (0.0-1.0)
- `bias`: Neural bias (-1.0 to 1.0)
- `gradient`: Current gradient for learning
- `momentum`: Exponential moving average of gradients

### Output Layer
Optimized parameter values computed as:
```python
optimized_value = max(0.1, current_value * weight + bias)
```

### Learning Algorithm
Uses gradient descent with momentum:
```python
error = target_success_rate - actual_success_rate
gradient = error * direction
momentum = momentum_factor * prev_momentum + (1 - momentum_factor) * gradient
weight = weight - learning_rate * momentum
```

## 🚀 Usage

### Command Line Interface

```bash
# Generate report on current neural architectures
python3 tools/neural_workflow_adapter.py --report

# Register a new workflow for adaptation
python3 tools/neural_workflow_adapter.py \
  --register "My Workflow" \
  --params '{"timeout_minutes": 30, "max_retries": 3}'

# Record an execution result
python3 tools/neural_workflow_adapter.py \
  --record "My Workflow" \
  --success

# Adapt a specific workflow
python3 tools/neural_workflow_adapter.py \
  --adapt "My Workflow"

# Adapt all workflows that need it
python3 tools/neural_workflow_adapter.py --adapt-all

# Get workflow status
python3 tools/neural_workflow_adapter.py \
  --status "My Workflow" \
  --json
```

### Python API

```python
from neural_workflow_adapter import NeuralWorkflowAdapter

# Initialize adapter
adapter = NeuralWorkflowAdapter()

# Register a workflow
adapter.register_workflow('My Workflow', {
    'timeout_minutes': 30.0,
    'max_retries': 3.0,
    'concurrency_limit': 5.0
})

# Record executions
adapter.record_execution('My Workflow', success=True)
adapter.record_execution('My Workflow', success=False)

# Adapt based on performance
optimized_params = adapter.adapt_workflow('My Workflow')

# Get status
status = adapter.get_workflow_status('My Workflow')
print(f"Success rate: {status['success_rate']:.1%}")
print(f"Needs adaptation: {status['needs_adaptation']}")

# Generate report
report = adapter.generate_report()
print(report)

# Save configuration
adapter._save_config()
```

## ⚙️ Configuration

Neural configuration is stored in `.github/agent-system/neural_config.json`:

```json
{
  "version": "1.0.0",
  "global_learning_rate": 0.01,
  "adaptation_threshold": 0.7,
  "architectures": [
    {
      "workflow_name": "Example Workflow",
      "weights": {
        "timeout_minutes": {
          "parameter_name": "timeout_minutes",
          "current_value": 30.0,
          "weight": 0.8,
          "bias": 0.1,
          "gradient": 0.0,
          "momentum": 0.0,
          "learning_history": []
        }
      },
      "success_history": [1.0, 1.0, 0.0, 1.0],
      "adaptation_count": 2,
      "confidence": 0.85
    }
  ]
}
```

### Key Parameters

- **global_learning_rate** (default: 0.01): How quickly weights adapt
  - Higher = faster learning but more instability
  - Lower = slower learning but more stable
  
- **adaptation_threshold** (default: 0.7): Success rate below which to adapt
  - Workflows below this threshold trigger adaptation
  - Set to 0.95 for very high reliability requirements
  
- **momentum** (default: 0.9): Smoothing factor for weight updates
  - Prevents oscillations in learning
  - Higher = smoother but slower adaptation

## 🔄 Automatic Adaptation

The `neural-workflow-adaptation.yml` workflow runs automatically:

- **After metrics collection**: Triggered by Performance Metrics Collection workflow
- **Every 6 hours**: Periodic scheduled adaptation
- **Manual trigger**: Via workflow_dispatch for testing

### Adaptation Process

1. **Collect Data**: Fetch recent workflow runs from GitHub API
2. **Initialize**: Register new workflows, load existing neural architectures
3. **Record**: Update success/failure history for each workflow
4. **Adapt**: Apply neural adaptation to workflows below threshold
5. **Commit**: Create PR with updated neural configuration
6. **Report**: Generate and upload adaptation report

### Adaptation Criteria

A workflow needs adaptation when:
- Success rate < 70% (configurable threshold)
- Variance > 0.3 (instability in results)
- Minimum 5 executions recorded

## 📊 Monitoring

### Reports

Generate comprehensive adaptation reports:

```bash
python3 tools/neural_workflow_adapter.py --report
```

Report includes:
- Overall success rate statistics
- Per-workflow neural architecture status
- Parameter values (current, computed, optimized)
- Adaptation history and confidence levels
- Recommendations for workflows needing attention

### Artifacts

Each adaptation cycle uploads artifacts:
- `neural_report.txt`: Full adaptation report
- `adaptation_results.json`: Structured results data
- `workflow_stats.json`: Aggregated workflow statistics

Access in GitHub Actions:
```
Actions → Neural Workflow Adaptation → Run → Artifacts
```

## 🎓 Neural Network Concepts

### Why Neural-Inspired?

Traditional workflow optimization uses fixed thresholds and rules. Neural adaptation offers:

- **Continuous Learning**: Weights evolve based on feedback
- **Non-linear Optimization**: Complex parameter interactions
- **Adaptive Thresholds**: Learning rate adjusts automatically
- **Generalization**: Patterns learned from one workflow can inform others

### Gradient Descent

The system uses gradient descent to minimize the error function:

```
Error = |target_success_rate - actual_success_rate|
```

Weights are updated to reduce this error over time.

### Momentum

Momentum prevents oscillations by smoothing weight updates:

```
momentum[t] = β * momentum[t-1] + (1-β) * gradient[t]
weight[t+1] = weight[t] - α * momentum[t]
```

Where:
- `β` = momentum factor (default 0.9)
- `α` = learning rate (default 0.01)

### Activation Function

Uses ReLU-like activation to ensure positive values:

```python
output = max(0.1, weighted_sum + bias)
```

Prevents parameters from becoming zero or negative.

## 🔍 Example Scenarios

### Scenario 1: Low Success Rate

Workflow has 50% success rate:
1. System detects need for adaptation (below 70% threshold)
2. Computes error: `0.95 - 0.50 = 0.45`
3. Adjusts weights using gradient descent
4. Increases timeout, retries, or other parameters
5. Monitors next executions for improvement

### Scenario 2: High Variance

Workflow alternates between success and failure:
1. System detects instability (variance > 0.3)
2. Reduces learning rate for this workflow
3. Applies smaller, more conservative adjustments
4. Stabilizes configuration over multiple iterations

### Scenario 3: Optimal Performance

Workflow has 95%+ success rate:
1. System recognizes optimal state
2. No adaptation performed
3. Weights remain stable
4. Continues monitoring for regression

## 🚀 Integration with Agent System

Neural adaptation integrates with the existing agent evolution system:

- **Agent Performance**: Agent success rates influence workflow parameters
- **Genetic Algorithms**: Neural weights can be considered "genes"
- **Evolution**: Successful configurations propagate to similar workflows
- **Fitness**: Neural confidence is a fitness metric

Future enhancements:
- Cross-workflow learning (transfer learning)
- Multi-objective optimization (speed vs. reliability)
- Meta-learning (learning to learn)

## 🎯 Best Practices

### Registering Workflows

Register workflows with realistic initial parameters:

```python
# Good: Realistic defaults
adapter.register_workflow('CI Build', {
    'timeout_minutes': 30.0,  # Typical build time
    'max_retries': 3.0,       # Reasonable retry count
    'concurrency_limit': 5.0  # Safe concurrency
})

# Avoid: Extreme values
adapter.register_workflow('CI Build', {
    'timeout_minutes': 300.0,  # Too long
    'max_retries': 10.0,       # Too many
    'concurrency_limit': 100.0 # Unsafe
})
```

### Recording Executions

Record executions consistently:

```python
# Good: Record all executions
for run in workflow_runs:
    adapter.record_execution(
        workflow_name=run.name,
        success=(run.conclusion == 'success')
    )

# Avoid: Selective recording
# Only recording failures biases the data
```

### Adaptation Frequency

Balance between responsiveness and stability:

- **Too frequent** (every run): Noisy, unstable learning
- **Too infrequent** (weekly): Slow to adapt to problems
- **Recommended**: After metrics collection + every 6 hours

### Learning Rate

Adjust learning rate based on confidence:

```python
# High confidence: Smaller adjustments
if confidence > 0.8:
    learning_rate = 0.005
# Low confidence: Faster learning
else:
    learning_rate = 0.02
```

## 🐛 Troubleshooting

### Workflow Not Adapting

**Problem**: Workflow never triggers adaptation

**Solutions**:
1. Check if workflow is registered:
   ```bash
   python3 tools/neural_workflow_adapter.py --status "My Workflow"
   ```

2. Verify execution history:
   - Needs minimum 5 recorded executions
   - Check `success_history` in neural_config.json

3. Review threshold:
   - Default threshold is 70%
   - Workflow may be above threshold

### Unstable Adaptations

**Problem**: Parameters oscillate between values

**Solutions**:
1. Increase momentum factor (e.g., 0.95)
2. Decrease learning rate (e.g., 0.005)
3. Add more execution history before adapting

### Configuration Not Saving

**Problem**: Changes don't persist

**Solutions**:
1. Check file permissions on `.github/agent-system/`
2. Verify `adapter._save_config()` is called
3. Look for errors in workflow logs

## 📚 References

Neural network concepts used:
- **Gradient Descent**: Optimization algorithm for minimizing loss
- **Momentum**: Acceleration method for faster convergence
- **Backpropagation**: Error feedback mechanism
- **ReLU Activation**: Non-linear activation function

Related systems:
- [Agent Evolution System](./agent-evolution-system.py)
- [Workflow Execution Tracker](./workflow_execution_tracker.py)
- [AI Workflow Predictor](./ai_workflow_predictor.py)

## 🤖 Created by @workflows-tech-lead

This self-evolving neural architecture represents a significant advancement in autonomous workflow optimization. By applying neural network principles to infrastructure management, we enable truly adaptive and intelligent automation.

**The system that learns from itself becomes exponentially more capable.**

---

*Part of the Chained autonomous AI ecosystem - Where AI agents compete, learn, and evolve to build software autonomously.*
