# Meta-Learning Workflow Scheduler

**@workflows-tech-lead** - Advanced schedule optimization through meta-learning

## Overview

The Meta-Learning Workflow Scheduler is an innovative system that implements second-order learning for GitHub Actions workflow optimization. Unlike traditional schedulers that use fixed rules, this system **learns how to learn** better scheduling policies by continuously adapting based on execution feedback.

## Key Innovation: Meta-Learning

### What is Meta-Learning?

Meta-learning, or "learning to learn," enables the system to:
- **Discover** optimal scheduling policies from experience
- **Adapt** strategies automatically based on feedback
- **Evolve** new approaches without manual tuning
- **Improve** continuously as more data becomes available

### Why Meta-Learning for Workflows?

Traditional workflow schedulers rely on:
- Fixed heuristics (e.g., "run tests after each commit")
- Manual configuration (cron schedules)
- Static rules that don't adapt to changing patterns

Our meta-learning system:
- **Learns** from historical execution data
- **Adapts** to repository-specific patterns
- **Discovers** non-obvious scheduling optimizations
- **Minimizes** workflow conflicts and resource contention
- **Maximizes** execution efficiency

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Meta-Learning System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌───────────────┐      ┌──────────┐ │
│  │   Strategy   │─────▶│  Performance  │─────▶│ Learning │ │
│  │   Library    │      │   Evaluation  │      │   Loop   │ │
│  └──────────────┘      └───────────────┘      └──────────┘ │
│         │                      │                     │       │
│         │                      ▼                     │       │
│         │              ┌───────────────┐            │       │
│         │              │   Feedback    │            │       │
│         │              │  Collection   │            │       │
│         │              └───────────────┘            │       │
│         │                      │                     │       │
│         │                      ▼                     │       │
│         │              ┌───────────────┐            │       │
│         └─────────────▶│  Parameter    │◀───────────┘       │
│                        │  Adaptation   │                    │
│                        └───────────────┘                    │
│                               │                              │
│                               ▼                              │
│                       ┌───────────────┐                     │
│                       │   Strategy    │                     │
│                       │  Evolution    │                     │
│                       └───────────────┘                     │
│                               │                              │
│                               ▼                              │
│                       ┌───────────────┐                     │
│                       │  Optimized    │                     │
│                       │  Schedules    │                     │
│                       └───────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Scheduling Strategies

Each strategy represents a learned approach to workflow scheduling:

```python
SchedulingStrategy(
    name="strategy_name",
    parameters=LearningParameters(
        success_weight=0.4,      # Weight for successful predictions
        failure_penalty=0.2,     # Penalty for failures
        recency_bias=0.3,        # Emphasis on recent data
        exploration_rate=0.1     # Rate of trying new approaches
    ),
    performance_history=[...],   # Track performance over time
    last_updated="2025-11-20T..."
)
```

#### 2. Learning Parameters

Dynamic parameters that control learning behavior:

- **success_weight**: How much to reward accurate predictions (0.0-1.0)
- **failure_penalty**: How much to penalize inaccurate predictions (0.0-1.0)
- **recency_bias**: Weight given to recent vs. historical data (0.0-1.0)
- **exploration_rate**: Balance between using best strategies vs. trying new ones (0.0-1.0)

#### 3. Performance Tracking

Continuous monitoring of strategy effectiveness:

```python
{
    "total_predictions": 150,
    "mean_error": 12.5,          # Average prediction error
    "accuracy_score": 87.5,       # Overall accuracy %
    "excellent_predictions": 45,  # Error ≤ 10%
    "good_predictions": 60,       # Error 10-25%
    "fair_predictions": 30,       # Error 25-50%
    "poor_predictions": 15        # Error > 50%
}
```

#### 4. Strategy Evolution

Genetic algorithm for discovering new strategies:

1. **Selection**: Choose top-performing strategies
2. **Mutation**: Create variations with modified parameters
3. **Evaluation**: Test new strategies on historical data
4. **Survival**: Keep strategies that outperform baseline

## Usage

### Command-Line Interface

```bash
# Initialize meta-learning scheduler
python3 tools/meta_learning_scheduler.py

# Adapt a strategy based on feedback
python3 tools/meta_learning_scheduler.py --adapt strategy_name

# Evolve strategies using genetic algorithm
python3 tools/meta_learning_scheduler.py --evolve

# Generate optimized schedule for a workflow
python3 tools/meta_learning_scheduler.py --optimize workflow_name

# Generate meta-learning report
python3 tools/meta_learning_scheduler.py --report

# Export learning data
python3 tools/meta_learning_scheduler.py --export output.json
```

### GitHub Actions Integration

The system runs automatically via `meta-learning-optimizer.yml`:

```yaml
# Runs every 6 hours
schedule:
  - cron: '0 */6 * * *'

# Or trigger manually
workflow_dispatch:
  inputs:
    force_evolution: 'true'
    generate_report: 'true'
```

### Programmatic Usage

```python
from meta_learning_scheduler import MetaLearningScheduler

# Initialize scheduler
scheduler = MetaLearningScheduler()

# Record execution feedback
scheduler.record_execution_feedback(
    workflow_name="test-workflow",
    predicted_duration=120,
    actual_duration=115,
    success=True,
    strategy_used="default"
)

# Adapt strategy
scheduler.adapt_strategy("default")

# Generate optimized schedule
schedule = scheduler.generate_optimized_schedule(
    workflow_name="test-workflow",
    strategy_name="default"
)

print(f"Recommended: {schedule['recommended_time']}")
print(f"Confidence: {schedule['confidence_score']}%")
```

## Learning Process

### 1. Data Collection

The system collects:
- Workflow execution times
- Success/failure rates
- Resource utilization patterns
- Scheduling conflicts
- Prediction accuracy

### 2. Performance Evaluation

For each strategy:
- Calculate prediction accuracy
- Track performance trends (improving/declining/stable)
- Identify optimal parameter configurations
- Compare against baseline strategies

### 3. Parameter Adaptation

Based on performance:
- **Success** → Increase success_weight
- **Failure** → Increase failure_penalty
- **Stable performance** → Increase exploration_rate
- **Declining performance** → Increase recency_bias

### 4. Strategy Evolution

Periodically:
- Select top 3 performing strategies
- Create mutations with varied parameters
- Test mutations on historical data
- Retain strategies that improve performance

### 5. Schedule Optimization

When generating schedules:
- Use best-performing strategy
- Consider execution patterns
- Avoid conflict windows
- Balance load across time periods
- Provide confidence scores

## Performance Metrics

### Accuracy Score

Overall prediction accuracy:

```
accuracy_score = 100 - mean_error
```

Where `mean_error` is the average percentage difference between predicted and actual execution times.

### Strategy Performance

Individual strategy effectiveness:

```python
performance = (excellent * 1.0 + good * 0.7 + fair * 0.4 + poor * 0.0) / total
```

### Trend Detection

Determine if strategies are:
- **Improving**: Recent performance > historical performance
- **Declining**: Recent performance < historical performance  
- **Stable**: Performance consistent over time

## Integration Points

### With Existing Systems

The meta-learning scheduler enhances:

1. **AI Workflow Predictor** (`ai_workflow_predictor.py`)
   - Provides learned scheduling policies
   - Improves prediction accuracy over time

2. **Integrated Workflow Orchestrator** (`integrated_workflow_orchestrator.py`)
   - Supplies optimized schedules
   - Adapts to execution patterns

3. **Dynamic Workflow Orchestrator** (`dynamic_workflow_orchestrator.py`)
   - Real-time schedule adjustments
   - Conflict resolution

4. **Workflow Execution Tracker** (existing workflows)
   - Consumes execution data
   - Feeds learning loop

### Data Flow

```
Workflows → Execution Data → Meta-Learning → Optimized Schedules → Orchestrator → Workflows
             ↑                                                                        │
             └────────────────────────────────────────────────────────────────────────┘
                                    Feedback Loop
```

## Configuration

### Storage Locations

```
.github/workflow-history/meta-learning/
├── learned_strategies.json    # Strategy library
├── learning_log.json          # Learning events
└── report_latest.json         # Latest metrics
```

### Default Parameters

```python
DEFAULT_PARAMS = LearningParameters(
    success_weight=0.4,
    failure_penalty=0.2,
    recency_bias=0.3,
    exploration_rate=0.1
)
```

### Evolution Settings

```python
EVOLUTION_CONFIG = {
    "top_strategies": 3,           # Number to evolve from
    "mutations_per_strategy": 2,   # Variations to create
    "mutation_rate": 0.1,          # Parameter change magnitude
    "min_performance": 0.3         # Minimum to keep
}
```

## Example Scenarios

### Scenario 1: New Repository

**Initial State**: No historical data

1. System starts with default strategy
2. Collects execution data from workflow runs
3. Evaluates initial predictions
4. Adapts parameters based on accuracy
5. After 50+ executions, begins evolution

**Result**: Customized scheduling policies for the repository

### Scenario 2: Changing Patterns

**Event**: Team switches from daily to continuous deployment

1. System detects declining performance (predictions less accurate)
2. Increases recency_bias to favor recent patterns
3. Adapts success_weight based on new feedback
4. Evolves strategies to match new execution patterns

**Result**: Automatic adaptation to workflow changes

### Scenario 3: Resource Optimization

**Goal**: Minimize workflow conflicts

1. System identifies conflict patterns in execution data
2. Learns optimal spacing between workflows
3. Generates schedules that avoid peak times
4. Continuously refines timing based on feedback

**Result**: Reduced conflicts and better resource utilization

## Comparison with Other Approaches

### Traditional Schedulers

| Feature | Traditional | Meta-Learning |
|---------|------------|---------------|
| Configuration | Manual | Automatic |
| Adaptation | Static | Dynamic |
| Learning | None | Continuous |
| Optimization | Rule-based | Data-driven |
| Repository-specific | No | Yes |

### Benefits

1. **Zero Configuration**: Works out-of-the-box, improves automatically
2. **Continuous Improvement**: Gets better with more data
3. **Repository-Aware**: Learns unique patterns of each project
4. **Self-Optimizing**: Discovers non-obvious optimizations
5. **Transparent**: Provides reasoning for scheduling decisions

## Monitoring and Debugging

### View Learning Progress

```bash
# Generate comprehensive report
python3 tools/meta_learning_scheduler.py --report
```

Output:
```
🎓 Meta-Learning Scheduler Report
════════════════════════════════════

📊 Overall Prediction Accuracy
  Total Predictions: 150
  Mean Error: 12.5%
  Accuracy Score: 87.5%
  Excellent (≤10%): 45
  Good (10-25%): 60
  Fair (25-50%): 30
  Poor (>50%): 15

🧠 Learned Strategies
  default: 85.0% (📈 improving)
  evolved_1: 88.5% (📈 improving)
  evolved_2: 82.0% (➡️  stable)

🏆 Best Strategy: evolved_1 (88.5%)
```

### Check Learning Log

```bash
# View recent learning events
cat .github/workflow-history/meta-learning/learning_log.json | jq '.[-5:]'
```

### Validate Strategy Performance

```bash
# Test individual strategy
python3 tools/meta_learning_scheduler.py \
  --optimize test-workflow \
  --strategy evolved_1
```

## Testing

### Run Test Suite

```bash
# Comprehensive tests
python3 tools/test_meta_learning_scheduler.py
```

Tests cover:
- Strategy creation and persistence
- Parameter adaptation
- Performance calculation
- Trend detection
- Schedule generation
- Strategy evolution
- Report generation

### Expected Output

```
🧪 Meta-Learning Scheduler Test Suite
══════════════════════════════════════

✅ PASS - learning_parameters
✅ PASS - strategy_creation  
✅ PASS - trend_detection
✅ PASS - scheduler_init
✅ PASS - strategy_persistence
✅ PASS - learning_log
✅ PASS - accuracy_evaluation
✅ PASS - performance_calculation
✅ PASS - parameter_adaptation
✅ PASS - schedule_generation
✅ PASS - strategy_evolution
✅ PASS - meta_report

🎯 Total: 12/12 tests passed
```

## Future Enhancements

### Planned Features

1. **Multi-Repository Learning**
   - Share learned strategies across repositories
   - Collaborative learning from multiple projects

2. **Advanced Evolution**
   - Crossover between strategies
   - Adaptive mutation rates
   - Multi-objective optimization

3. **Real-Time Adaptation**
   - Immediate strategy updates after each execution
   - Online learning algorithms
   - Streaming data processing

4. **Predictive Scheduling**
   - Forecast future resource needs
   - Proactive conflict avoidance
   - Load balancing across time zones

5. **Visual Dashboard**
   - Interactive strategy explorer
   - Performance visualization
   - Learning progress tracking

## Troubleshooting

### Problem: Low Accuracy

**Symptoms**: accuracy_score < 50%

**Solutions**:
1. Increase recency_bias to focus on recent patterns
2. Force strategy evolution: `--evolve`
3. Check if workflow patterns have changed
4. Ensure sufficient historical data (50+ executions)

### Problem: Strategy Not Improving

**Symptoms**: All strategies show "stable" or "declining" trends

**Solutions**:
1. Verify execution data is being collected
2. Check learning_log.json for adaptation events
3. Manually trigger evolution: `--evolve`
4. Review parameter ranges (might be constrained)

### Problem: Conflicts Still Occur

**Symptoms**: Workflows still run concurrently despite optimization

**Solutions**:
1. Check if orchestrator is using meta-learning schedules
2. Verify workflow execution data includes conflict information
3. Increase exploration_rate to try more diverse schedules
4. Review recommended_time vs. actual execution time

## Best Practices

1. **Let It Learn**: Give the system at least 50 workflow executions before evaluating
2. **Monitor Trends**: Check reports regularly to understand learning progress
3. **Trust the Data**: Let the system adapt rather than forcing manual changes
4. **Provide Feedback**: Ensure execution data includes success/failure status
5. **Evolve Periodically**: Run evolution every 100-200 executions

## References

### Meta-Learning Theory

- **MAML (Model-Agnostic Meta-Learning)**: Principles adapted for scheduling
- **Reinforcement Learning**: Reward/penalty feedback loop
- **Genetic Algorithms**: Strategy evolution mechanism
- **Transfer Learning**: Sharing knowledge across workflows

### Implementation Notes

- Uses only Python standard library (no external dependencies)
- JSON-based persistence for portability
- Stateless operations for reliability
- Comprehensive error handling

## License

Part of the Chained autonomous AI ecosystem.

## Authors

**@workflows-tech-lead** - Created 2025-11-20

---

*🎓 Meta-learning: The system that learns how to learn better scheduling policies*
