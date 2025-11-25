# RL Resource Optimizer for GitHub Actions

> **Created by @create-guru** - Reinforcement Learning for GitHub Actions Resource Optimization

## Overview

The RL Resource Optimizer uses Q-Learning to intelligently optimize GitHub Actions resource allocation. It learns from workflow execution history to make data-driven decisions about:

- **Concurrency settings** - How many workflows can run in parallel
- **Timeout configurations** - Optimal timeout values for each workflow
- **Caching strategies** - When to enable/disable caching
- **Job parallelization** - Optimal number of parallel jobs

## How It Works

### Q-Learning Algorithm

The optimizer uses Q-Learning, a model-free reinforcement learning algorithm that learns the value of actions in different states:

```
Q(s,a) = Q(s,a) + α * (r + γ * max(Q(s',a')) - Q(s,a))
```

Where:
- `Q(s,a)` = Quality of taking action `a` in state `s`
- `α` (alpha) = Learning rate (how fast to learn)
- `γ` (gamma) = Discount factor (importance of future rewards)
- `r` = Immediate reward
- `s'` = Next state

### State Space

Each workflow's state is characterized by:
- Current concurrency limit (1-10)
- Timeout setting (minutes)
- Caching enabled/disabled
- Number of parallel jobs
- Average execution duration
- Historical success rate
- Resource utilization efficiency
- Time of day and day of week

### Action Space

The optimizer can recommend these actions:

| Action | Description |
|--------|-------------|
| `increase_concurrency` | Allow more concurrent runs |
| `decrease_concurrency` | Reduce concurrent runs for stability |
| `extend_timeout` | Increase timeout to prevent failures |
| `reduce_timeout` | Decrease timeout to free resources |
| `enable_caching` | Turn on caching for faster builds |
| `disable_caching` | Turn off caching for consistency |
| `parallelize_jobs` | Run more jobs in parallel |
| `serialize_jobs` | Run jobs sequentially |
| `no_change` | Current config is optimal |

### Reward Function

The multi-objective reward function optimizes for:

- **Duration improvement** (40%): Reducing execution time
- **Success rate** (35%): Improving reliability
- **Resource utilization** (25%): Efficient resource usage

## Quick Start

### Get Recommendations

```bash
# Get recommendation for a specific workflow
python3 tools/rl_resource_optimizer.py --workflow "my-workflow"
```

### Train the Model

```bash
# Simulate training episodes
python3 tools/rl_resource_optimizer.py --simulate 100

# Generate comprehensive report
python3 tools/rl_resource_optimizer.py --report
```

### Integration Example

```python
from tools.rl_resource_optimizer import RLResourceOptimizer

# Initialize optimizer
optimizer = RLResourceOptimizer()

# Get execution history (from your data source)
history = [
    {
        'duration_seconds': 180,
        'success': True,
        'resource_usage': {'estimated_cpu_percent': 45}
    },
    # ... more executions
]

# Get recommendation
rec = optimizer.get_recommendation("my-workflow", execution_history=history)

print(f"Recommended: {rec.recommended_action}")
print(f"Expected improvement: {rec.expected_improvement:.1f}%")
print(f"Confidence: {rec.confidence * 100:.0f}%")
```

## Integration with Existing Tools

The RL Resource Optimizer integrates with:

- **`github_actions_data_collector.py`**: Collects real execution data
- **`ai_workflow_predictor.py`**: Provides execution history
- **`workflow-data-collection.yml`**: Automated data collection workflow

### Data Flow

```
GitHub Actions API
        ↓
Data Collector (github_actions_data_collector.py)
        ↓
Execution History (.github/workflow-history/executions.json)
        ↓
RL Optimizer (rl_resource_optimizer.py)
        ↓
Optimization Recommendations
```

## Configuration

### Learning Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `LEARNING_RATE` | 0.1 | How fast to update Q-values |
| `DISCOUNT_FACTOR` | 0.95 | Importance of future rewards |
| `INITIAL_EPSILON` | 1.0 | Starting exploration rate |
| `EPSILON_DECAY` | 0.995 | Exploration decay rate |
| `MIN_EPSILON` | 0.05 | Minimum exploration |
| `REPLAY_BUFFER_SIZE` | 1000 | Experience storage limit |
| `BATCH_SIZE` | 32 | Learning batch size |

### Reward Weights

| Weight | Value | Optimizes For |
|--------|-------|---------------|
| Duration | 0.4 | Faster execution |
| Success | 0.35 | Higher reliability |
| Utilization | 0.25 | Better resource efficiency |

## Storage

The optimizer persists its learning in:

```
.github/rl-optimizer/
├── q_table.json       # Learned Q-values
├── experiences.json   # Experience replay buffer
└── metrics.json       # Optimizer performance metrics
```

## Example Output

```
🔍 Analyzing workflow: code-quality

📋 Recommendation for: code-quality
   Current State:
     - concurrency_limit: 2
     - timeout_minutes: 60
     - caching_enabled: False
     - parallel_jobs: 1
     - avg_duration_seconds: 342.5
     - success_rate: 85.0%
     - resource_utilization: 45.0%

   ✨ Recommended Action: enable_caching
   📈 Expected Improvement: 12.5%
   🎯 Confidence: 75%

   💭 Reasoning:
     ⏱️ Long average duration (5.7min) - optimization potential
     💡 Enabling caching can significantly reduce build times
     📈 High confidence action (Q-value: 0.125)

   🔄 Alternative Actions:
     - parallelize_jobs (expected: 8.2%)
     - increase_concurrency (expected: 5.1%)
```

## Testing

Run the test suite:

```bash
python3 tools/test_rl_resource_optimizer.py
```

Or with pytest:

```bash
pytest tests/test_rl_resource_optimizer.py -v
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   RLResourceOptimizer                    │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Q-Table    │  │  Experience  │  │    State     │  │
│  │   Storage    │  │    Replay    │  │   Manager    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │                 Q-Learning Engine                 │   │
│  │  • Epsilon-greedy exploration                    │   │
│  │  • Experience replay learning                    │   │
│  │  • Multi-objective reward calculation            │   │
│  └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │              Recommendation Engine                │   │
│  │  • Action selection                              │   │
│  │  • Confidence estimation                         │   │
│  │  • Reasoning generation                          │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Future Improvements

- [ ] Deep Q-Network (DQN) for continuous state spaces
- [ ] Multi-agent learning for workflow dependencies
- [ ] Automatic hyperparameter tuning
- [ ] Integration with GitHub Actions API for automatic application
- [ ] A/B testing integration for recommendation validation

## Related Tools

- `ai_workflow_predictor.py` - Execution time prediction
- `github_actions_data_collector.py` - Data collection
- `workflow-orchestrator.py` - Workflow coordination

---

*Created by **@create-guru** - Part of the Chained autonomous AI ecosystem 🏭*
