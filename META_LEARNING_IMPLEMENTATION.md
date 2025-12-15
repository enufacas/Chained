# Meta-Learning Workflow Scheduler Implementation

**@create-botter** - System activation and implementation guide

## What Was Implemented

### 1. Reactivated Meta-Learning Workflow

**File**: `.github/workflows/meta-learning-optimizer.yml`

**Status**: ✅ Moved from archive and activated

**Schedule**: Runs every 6 hours automatically

**Features**:
- Adapts scheduling strategies based on workflow performance
- Evolves new strategies using genetic algorithms
- Generates comprehensive learning reports
- Commits learned strategies via PR-based workflow
- Can be triggered manually for immediate optimization

### 2. Created Data Infrastructure

**Directory**: `.github/workflow-history/meta-learning/`

**Files Created**:
- `learned_strategies.json` - Stores learned scheduling strategies
- `README.md` - Complete documentation for the data directory

**Initial State**:
- Default strategy initialized with baseline parameters
- Performance history tracking started
- Ready to begin collecting execution data

### 3. Verified Existing Tools

**Core Tool**: `tools/meta_learning_scheduler.py`
- ✅ All functionality working correctly
- ✅ Help system operational
- ✅ Report generation functional

**Test Suite**: `tools/test_meta_learning_scheduler.py`
- ✅ All 12 tests passing
- ✅ Comprehensive coverage of all features
- ✅ Validates learning, adaptation, and evolution

## How It Works

### Meta-Learning Approach

This system implements **second-order learning** - it learns how to learn:

```
Traditional Scheduler:
  Fixed rules → Execute workflows → Done

Meta-Learning Scheduler:
  Execute workflows → Measure accuracy → Adjust strategy → Learn from results → Improve predictions → Repeat
```

### Learning Cycle (Every 6 Hours)

1. **Collect Data**: Fetches recent workflow execution history
2. **Evaluate Accuracy**: Compares predictions vs actual outcomes  
3. **Adapt Strategies**: Adjusts parameters based on performance
4. **Evolve Strategies**: Creates new variations via genetic algorithm
5. **Generate Report**: Produces comprehensive metrics
6. **Commit Changes**: Creates PR with updated strategies

### Key Innovations

#### 1. Continuous Adaptation

Strategies automatically adjust their parameters based on:
- Prediction accuracy (how close were we?)
- Execution success rate (did workflows succeed?)
- Resource efficiency (were there conflicts?)

#### 2. Genetic Evolution

Periodically creates new strategy variations:
- Mutates top-performing strategies
- Tests variations against real data
- Keeps successful mutations
- Prunes poor performers

#### 3. Multi-Strategy Portfolio

Maintains multiple strategies simultaneously:
- `default` - Baseline conservative approach
- `evolved_*` - Automatically generated variations
- Custom strategies can be added manually

## Usage

### Automatic Operation

No action needed! The workflow runs every 6 hours and:
- Learns from recent workflow executions
- Improves its scheduling recommendations
- Reports progress in workflow summaries

### Manual Triggers

#### Quick Test
```bash
# Generate current report
python3 tools/meta_learning_scheduler.py --report
```

#### Force Evolution
```bash
# Trigger workflow manually
gh workflow run meta-learning-optimizer.yml -f force_evolution=true
```

#### Get Optimized Schedule
```bash
# Get recommendation for specific workflow
python3 tools/meta_learning_scheduler.py --optimize github-pages-review
```

## Expected Performance

### Week 1: Bootstrap Phase
- System collects initial execution data
- Uses default strategy with baseline parameters
- Accuracy: ~50% (random baseline)

### Week 2-4: Learning Phase
- Patterns begin to emerge from data
- First strategy evolution occurs
- Accuracy improves to 60-70%

### Month 2+: Optimized Phase
- High prediction accuracy (75-90%)
- Multiple specialized strategies
- Continuous refinement and adaptation

## Monitoring Progress

### View Workflow Runs
1. Go to Actions tab in GitHub
2. Select "Meta-Learning Workflow Optimizer"
3. View run summaries for key metrics

### Check Learned Strategies
```bash
cat .github/workflow-history/meta-learning/learned_strategies.json
```

### Review Learning Log
```bash
cat .github/workflow-history/meta-learning/learning_log.json
```

### Generate Detailed Report
```bash
python3 tools/meta_learning_scheduler.py --report --export report.json
```

## Architecture

### Components

```
┌─────────────────────────────────────────────────────┐
│           Meta-Learning Scheduler System             │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────┐                               │
│  │ GitHub Actions   │                               │
│  │ Workflow         │                               │
│  │ (Orchestrator)   │                               │
│  └────────┬─────────┘                               │
│           │                                          │
│           ▼                                          │
│  ┌──────────────────┐      ┌──────────────────┐    │
│  │ meta_learning_   │◄─────┤ Workflow         │    │
│  │ scheduler.py     │      │ Execution Data   │    │
│  │                  │      └──────────────────┘    │
│  │ • Adaptation     │                               │
│  │ • Evolution      │                               │
│  │ • Optimization   │                               │
│  └────────┬─────────┘                               │
│           │                                          │
│           ▼                                          │
│  ┌──────────────────┐                               │
│  │ Learned          │                               │
│  │ Strategies       │                               │
│  │ (JSON Storage)   │                               │
│  └──────────────────┘                               │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input**: Workflow execution history from GitHub API
2. **Processing**: Meta-learning algorithm analyzes patterns
3. **Output**: Optimized scheduling recommendations
4. **Storage**: Learned strategies persisted to JSON
5. **Feedback**: Next execution provides new training data

## Technical Details

### Learning Parameters

Each strategy has adjustable parameters:

- `success_weight` (0.4): How much to value prediction accuracy
- `duration_weight` (0.3): How much to value execution time
- `conflict_weight` (0.3): How much to value conflict avoidance
- `confidence_threshold` (0.6): Minimum confidence for recommendations
- `learning_rate` (0.1): How quickly to adapt (0=never, 1=immediately)
- `exploration_rate` (0.15): Probability of trying new approaches

### Performance Metrics

Strategies evaluated on:
- **Accuracy Score**: 100% - average prediction error
- **Average Performance**: Mean of recent performance history
- **Performance Trend**: Improving/declining/stable classification

### Evolution Algorithm

Genetic algorithm implementation:
1. Select top 3 performing strategies
2. Create mutations (±10% parameter changes)
3. Test mutations against historical data
4. Retain if performance exceeds threshold
5. Prune strategies with &lt;30% performance

## Troubleshooting

### Issue: Low prediction accuracy

**Symptoms**: Accuracy &lt; 40% after 2+ weeks

**Causes**:
- Insufficient execution data
- Highly variable workflow patterns
- Recent changes to workflow schedules

**Solutions**:
1. Wait for more data to accumulate
2. Manually adjust learning rate (increase for faster adaptation)
3. Force evolution to generate new strategy variations

### Issue: No strategy evolution

**Symptoms**: Only "default" strategy exists

**Causes**:
- Evolution only triggers every 12 hours on schedule
- Manual trigger needed for immediate evolution

**Solutions**:
1. Wait for scheduled evolution cycle
2. Use workflow_dispatch with `force_evolution: true`

### Issue: Strategies not being committed

**Symptoms**: No PRs created for learned strategies

**Causes**:
- No changes to commit (strategies unchanged)
- PR creation might have failed

**Solutions**:
1. Check workflow logs for PR creation step
2. Verify GitHub token has required permissions
3. Look for existing PRs with "Meta-Learning" in title

## Future Enhancements

Potential improvements:
- Multi-objective optimization (Pareto frontier)
- Deep reinforcement learning integration
- Workflow dependency graph analysis
- Predictive resource allocation
- Cross-repository learning

## References

- **Documentation**: `docs/META_LEARNING_SCHEDULER.md`
- **Quick Start**: `docs/QUICKSTART_META_LEARNING.md`
- **Tool**: `tools/meta_learning_scheduler.py`
- **Tests**: `tools/test_meta_learning_scheduler.py`
- **Workflow**: `.github/workflows/meta-learning-optimizer.yml`

---

**@create-botter** - Built with vision, powered by continuous learning
