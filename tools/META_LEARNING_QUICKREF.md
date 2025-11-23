# Meta-Learning Workflow Optimization - Quick Reference

**@create-guru** | Fast access to workflow schedule optimization commands and insights

## 🚀 Quick Commands

### View Dashboard
```bash
# Open in browser
open docs/workflow-optimization.html

# Or visit online
https://enufacas.github.io/Chained/workflow-optimization.html
```

### Generate Reports
```bash
# Full meta-learning report
python3 tools/meta_learning_scheduler.py --report

# Dashboard summary
python3 tools/workflow_schedule_dashboard.py --summary

# Export JSON
python3 tools/workflow_schedule_dashboard.py --json

# Generate HTML
python3 tools/workflow_schedule_dashboard.py --html

# All outputs
python3 tools/workflow_schedule_dashboard.py --all
```

### Optimize Workflows
```bash
# Generate optimized schedule for a workflow
python3 tools/meta_learning_scheduler.py \
  --optimize "workflow-name" \
  --strategy default

# Adapt a strategy
python3 tools/meta_learning_scheduler.py --adapt default

# Evolve strategies (genetic algorithm)
python3 tools/meta_learning_scheduler.py --evolve
```

## 📊 Key Metrics

| Metric | Location | Meaning |
|--------|----------|---------|
| **Accuracy Score** | Dashboard top | Overall prediction accuracy (0-100%) |
| **Best Strategy** | Dashboard top | Currently best-performing approach |
| **Total Strategies** | Dashboard top | Number of learned strategies |
| **Performance** | Strategy table | Strategy effectiveness score |
| **Trend** | Strategy table | 📈 Improving / ➡️ Stable / 📉 Declining |

## 🎯 Understanding Recommendations

### Confidence Levels
- **≥90%**: High confidence - strongly recommended
- **70-89%**: Good confidence - recommended
- **50-69%**: Moderate confidence - consider carefully
- **<50%**: Low confidence - review before applying

### Schedule Format
```
0 6 * * *   = Daily at 6:00 UTC
0 */6 * * * = Every 6 hours
0 0 * * 1   = Weekly on Monday at midnight
```

## 🔄 Automated Workflows

### Meta-Learning Optimizer
- **Runs**: Every 6 hours
- **Does**: Adapts strategies, evolves approaches
- **Output**: PRs with learned strategies

### Dashboard Updater
- **Runs**: Daily at noon UTC
- **Does**: Refreshes dashboard with latest data
- **Output**: Updated HTML and JSON files

## 📈 Performance Targets

After 4 weeks of operation:
- Accuracy Score: **70-85%**
- Excellent Predictions: **40-60%**
- Strategy Count: **5-8**

## 🧪 Quick Tests

```bash
# Test meta-learning scheduler
python3 tools/test_meta_learning_scheduler.py

# Test dashboard
python3 tools/test_workflow_schedule_dashboard.py
```

## 🔍 Troubleshooting

### Dashboard shows no data
**Solution**: Wait for first meta-learning cycle (runs every 6 hours)

### Low accuracy score
**Solution**: System needs 2-4 weeks to accumulate data

### Recommendations not applied
**Solution**: System generates recommendations but doesn't auto-apply. Review and apply manually.

### Strategy not evolving
**Solution**: Evolution runs every 6 hours. Trigger manually: `--evolve`

## 📁 Important Files

| File | Purpose |
|------|---------|
| `tools/meta_learning_scheduler.py` | Core meta-learning engine |
| `tools/workflow_schedule_dashboard.py` | Dashboard generator |
| `docs/workflow-optimization.html` | Interactive dashboard |
| `docs/data/workflow-optimization.json` | Latest optimization data |
| `.github/workflow-history/meta-learning/` | Learned strategies storage |

## 🎨 Dashboard Features

### Strategy Performance Table
- Shows all learned strategies
- 🏆 marks best strategy
- Color coding for trends
- Historical data points

### Optimization Recommendations
- Current vs recommended schedules
- Confidence scores
- Expected durations
- Highlighted changes

### Learning Progress
- Total predictions analyzed
- Error metrics
- Prediction quality breakdown
- Learning event count

## 🚀 Advanced Usage

### Create Custom Strategy
```python
from meta_learning_scheduler import MetaLearningScheduler, SchedulingStrategy, LearningParameters

scheduler = MetaLearningScheduler()

# Define custom parameters
custom_strategy = SchedulingStrategy(
    name='my_strategy',
    parameters=LearningParameters(
        success_weight=0.5,
        duration_weight=0.3,
        learning_rate=0.15
    ),
    performance_history=[],
    last_updated=datetime.now(timezone.utc).isoformat()
)

scheduler.strategies['my_strategy'] = custom_strategy
scheduler.save_strategies()
```

### Export Report for Analysis
```bash
# Export to JSON
python3 tools/meta_learning_scheduler.py \
  --report \
  --export /tmp/analysis-$(date +%Y%m%d).json

# Analyze with jq
cat /tmp/analysis-*.json | jq '.strategies'
```

## 📚 Related Documentation

- [Full README](META_LEARNING_SCHEDULER_README.md) - Complete system documentation
- [AI Workflow Predictor](AI_WORKFLOW_PREDICTOR_README.md) - Base prediction engine
- [Workflow Execution Tracker](WORKFLOW_EXECUTION_TRACKER_README.md) - Execution tracking

## 💡 Tips

1. **Let it learn**: Give system 2+ weeks to accumulate data
2. **Monitor weekly**: Check dashboard once per week
3. **Review PRs**: Understand what the system is learning
4. **Trust the process**: Accuracy improves over time
5. **Report issues**: Unusual recommendations help improve system

## 🎯 Common Use Cases

### Check System Status
```bash
python3 tools/workflow_schedule_dashboard.py --summary
```

### View Latest Recommendations
```bash
cat docs/data/workflow-optimization.json | jq '.recommendations'
```

### Manual Strategy Evolution
```bash
python3 tools/meta_learning_scheduler.py --evolve
```

### Generate Fresh Dashboard
```bash
python3 tools/workflow_schedule_dashboard.py --html
open docs/workflow-optimization.html
```

## 🔗 Quick Links

- **Dashboard**: [workflow-optimization.html](https://enufacas.github.io/Chained/workflow-optimization.html)
- **GitHub**: [Meta-Learning Optimizer Workflow](../.github/workflows/meta-learning-optimizer.yml)
- **Tests**: Run `python3 tools/test_*.py`

---

**Created by @create-guru** | Part of Chained autonomous AI ecosystem | 🎓 Continuous learning, continuous improvement
