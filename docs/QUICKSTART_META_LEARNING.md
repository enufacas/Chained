# Quick Start: Meta-Learning Workflow Scheduler

**@workflows-tech-lead** - Get started in 5 minutes

## What is This?

A self-learning system that automatically optimizes GitHub Actions workflow schedules by learning from execution patterns. No configuration needed - it just gets better over time.

## Quick Start

### 1. Run Tests (Optional)

```bash
python3 tools/test_meta_learning_scheduler.py
```

Expected: All 12 tests pass

### 2. Generate Your First Report

```bash
python3 tools/meta_learning_scheduler.py --report
```

See current strategies and performance.

### 3. Try Manual Workflow Trigger

Go to Actions → Meta-Learning Workflow Optimizer → Run workflow

Options:
- **Force Evolution**: Create new strategy variations
- **Generate Report**: See detailed learning metrics

### 4. Let It Learn

The system runs automatically every 6 hours and:
- Collects execution data from workflows
- Adapts strategies based on accuracy
- Evolves new scheduling approaches
- Generates optimized schedules

## Key Commands

```bash
# Get an optimized schedule for a workflow
python3 tools/meta_learning_scheduler.py --optimize workflow-name

# Adapt a strategy based on feedback
python3 tools/meta_learning_scheduler.py --adapt default

# Force evolution of strategies
python3 tools/meta_learning_scheduler.py --evolve

# Generate comprehensive report
python3 tools/meta_learning_scheduler.py --report

# Export data for analysis
python3 tools/meta_learning_scheduler.py --export output.json
```

## What to Expect

### Day 1-7: Bootstrap Phase
- System collects initial execution data
- Uses default scheduling strategy
- Begins basic parameter adaptation

### Week 2-4: Learning Phase
- Prediction accuracy improves (50% → 70%)
- First strategy evolution occurs
- Repository-specific patterns emerge

### Month 2+: Optimized Phase
- High accuracy (75-90%)
- Multiple specialized strategies
- Continuous refinement

## Monitoring Progress

### View in GitHub Actions

Each run shows:
- ✅ Tests passed
- ✅ Strategies adapted
- ✅ Best strategy and accuracy score

### Check Learning Data

```bash
# View strategies
cat .github/workflow-history/meta-learning/learned_strategies.json | jq

# View learning events
cat .github/workflow-history/meta-learning/learning_log.json | jq '.[-10:]'

# View latest report
cat .github/workflow-history/meta-learning/report_latest.json | jq
```

## How It Works (Simple)

1. **Collects Data**: Watches workflow executions
2. **Learns Patterns**: Identifies optimal scheduling times
3. **Adapts Strategies**: Changes parameters based on accuracy
4. **Evolves New Ideas**: Creates variations of good strategies
5. **Generates Schedules**: Recommends best times to run workflows

## Integration with Other Systems

Works alongside:
- AI Workflow Predictor: Enhanced predictions
- Integrated Orchestrator: Optimized schedules
- Dynamic Orchestrator: Real-time adjustments

## Troubleshooting

**Not seeing improvements?**
- Check you have 50+ workflow executions
- Verify data is being collected
- Try forcing evolution: `--evolve`

**Accuracy seems low?**
- Normal in first 1-2 weeks
- Let system collect more data
- Check for major workflow changes

**Want to reset?**
- Delete: `.github/workflow-history/meta-learning/learned_strategies.json`
- System will recreate with defaults

## Next Steps

1. Read full docs: `docs/META_LEARNING_SCHEDULER.md`
2. Let system run for 2 weeks
3. Check reports to see improvement
4. Enjoy automatically optimized workflows!

## Key Metrics to Watch

- **Accuracy Score**: Should trend upward over time
- **Best Strategy Performance**: Compare to default
- **Prediction Errors**: Should decrease week-over-week

## Philosophy

> "The best scheduler is one that learns from your repository's unique patterns and continuously improves itself."

No manual tuning. No configuration files. Just continuous learning and optimization.

---

*Created by **@workflows-tech-lead** - Meta-learning for autonomous workflow optimization* 🎓
