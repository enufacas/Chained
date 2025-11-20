# 🤖 Autonomous Code Reviewer with Self-Improving Criteria

> **Created by @workflows-tech-lead**  
> A self-evolving code review system that learns from outcomes and continuously improves its review criteria.

## 🌟 Overview

This autonomous code review system evaluates pull requests against a set of evolving criteria that improve over time based on real-world outcomes. Unlike traditional static linters, this system **learns** from:

- ✅ Successfully merged PRs
- ❌ Rejected PRs
- 🔄 PRs that required significant changes
- 💬 Reviewer feedback patterns

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PR OPENED/UPDATED                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         AUTONOMOUS CODE REVIEWER WORKFLOW                │
│  • Load current criteria (criteria.json)                │
│  • Fetch changed files from PR                          │
│  • Apply pattern matching and heuristics                │
│  • Calculate scores per category                        │
│  • Generate review comment                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           POST REVIEW & STORE RESULTS                    │
│  • Comment on PR with findings                          │
│  • Add quality label                                    │
│  • Save review results to reviews/                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               PR MERGED OR CLOSED                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         LEARNING WORKFLOW (Daily @ 2 AM UTC)             │
│  • Fetch closed PRs from last N days                    │
│  • Match with review results                            │
│  • Calculate outcome success                            │
│  • Adjust criteria weights/thresholds                   │
│  • Update effectiveness metrics                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         CRITERIA EVOLUTION & PR CREATION                 │
│  • Commit updated criteria.json                         │
│  • Generate learning report                             │
│  • Create PR with improvements                          │
└─────────────────────────────────────────────────────────┘
                     │
                     └──────── (Loop Continues) ────────┐
                                                         │
                     ┌───────────────────────────────────┘
                     ▼
            🔄 CONTINUOUS IMPROVEMENT
```

## 📁 File Structure

```
.github/review-system/
├── criteria.json              # The evolving review criteria
├── autonomous_reviewer.py     # Core reviewer logic
├── reviews/                   # Stored review results
│   ├── pr-123-1234567890.json
│   ├── pr-124-1234567891.json
│   └── ...
└── README.md                  # This file
```

## 📊 Criteria Categories

The autonomous reviewer evaluates PRs across multiple categories:

### 1. **Correctness** (Weight: 1.0)
- Error handling present
- Null/undefined checks
- Boundary conditions handled
- Tests present

### 2. **Clarity** (Weight: 0.8)
- Meaningful variable names
- Reasonable function size
- Complex logic explained
- Reasonable nesting depth

### 3. **Security** (Weight: 1.2) ⚡ High Priority
- No hardcoded secrets
- Input validation present
- No SQL injection risks

### 4. **Maintainability** (Weight: 0.7)
- No obvious duplication (DRY)
- Single responsibility principle
- Public APIs documented

### 5. **Workflow-Specific** (Weight: 1.0)
- Actions pinned to SHA
- Minimal permissions granted
- Error handling in workflows
- Concurrency controls

## 🧠 Learning Mechanism

### How It Learns

1. **Data Collection**: Every review is stored with its results
2. **Outcome Tracking**: PR merges/rejections are tracked
3. **Effectiveness Calculation**: Each criterion's correlation with good outcomes is measured
4. **Criteria Adjustment**: Weights and thresholds are adjusted based on effectiveness

### Evolution Parameters

```json
{
  "min_reviews_before_adjustment": 10,
  "effectiveness_window": 30,
  "weight_adjustment_rate": 0.1,
  "threshold_adjustment_rate": 0.05,
  "criteria_removal_threshold": 0.3,
  "criteria_promotion_threshold": 0.85
}
```

### Adaptation Strategy

- **Effective criteria** (>85% correlation): Increase weight, stricter threshold
- **Neutral criteria** (30-85% correlation): Maintain current settings
- **Ineffective criteria** (<30% correlation): Decrease weight, lenient threshold

## 🚀 Usage

### Automatic Review

The system automatically reviews all PRs when:
- PR is opened
- New commits are pushed
- PR is reopened

No configuration needed—it just works!

### Manual Trigger

To manually trigger learning from recent outcomes:

```bash
gh workflow run review-criteria-learning.yml
```

### Check Current Criteria

```bash
jq . .github/review-system/criteria.json
```

### View Learning History

```bash
jq '.history | .[-5:]' .github/review-system/criteria.json
```

## 📈 Metrics Tracked

- **Total Reviews**: Cumulative count of all reviews performed
- **Success Rate**: Percentage of reviews where PR was successfully merged
- **Category Weights**: Dynamic weights for each criteria category
- **Check Effectiveness**: Per-check effectiveness scores
- **Historical Effectiveness**: Trend data for criteria evolution

## 🎯 Goals & Success Criteria

### Short-term Goals (30 days)
- [ ] Review 50+ PRs
- [ ] Achieve 70% success rate correlation
- [ ] Identify top 3 most effective criteria
- [ ] Remove or adjust ineffective criteria

### Long-term Goals (90 days)
- [ ] Review 200+ PRs
- [ ] Achieve 80% success rate correlation
- [ ] Fully automated criteria evolution
- [ ] Integration with agent performance metrics

## 🔧 Configuration

### Adding New Criteria

Edit `criteria.json` and add new checks:

```json
{
  "id": "new_check",
  "name": "New Check Name",
  "weight": 0.3,
  "patterns": ["regex_pattern"],
  "effectiveness": 0.5,
  "times_applied": 0
}
```

### Adjusting Learning Rate

Modify the category's `learning_rate`:

```json
{
  "category_name": {
    "learning_rate": 0.1  // 0.0 = no learning, 1.0 = instant adaptation
  }
}
```

### Changing Evolution Parameters

Edit `evolution_config` in `criteria.json`:

```json
{
  "evolution_config": {
    "min_reviews_before_adjustment": 10,  // Wait for N reviews
    "weight_adjustment_rate": 0.1         // Adjustment magnitude
  }
}
```

## 🧪 Testing

### Test on Sample PR

```bash
python3 .github/review-system/autonomous_reviewer.py \
  --pr-number 123 \
  --comment
```

### Simulate Learning

```bash
# Manually record an outcome
python3 << 'EOF'
import json
from autonomous_reviewer import AutonomousReviewer

reviewer = AutonomousReviewer()
reviewer.learn_from_outcome('test-pr-001', {
    'merged': True,
    'major_changes_required': False
})
EOF
```

## 📊 Performance Dashboard

View current performance:

```bash
python3 << 'EOF'
import json

with open('.github/review-system/criteria.json') as f:
    criteria = json.load(f)

print(f"Total Reviews: {criteria['metadata']['total_reviews']}")
print(f"Success Rate: {criteria['metadata']['success_rate']:.1%}")

for name, cat in criteria['criteria'].items():
    print(f"\n{name}:")
    print(f"  Weight: {cat['weight']:.2f}")
    print(f"  Threshold: {cat['threshold']:.0%}")
    print(f"  Evaluated: {cat.get('times_evaluated', 0)} times")
EOF
```

## 🤝 Integration with Agent System

This autonomous reviewer integrates with the broader Chained agent ecosystem:

- **Metrics Collection**: Review outcomes feed into agent performance metrics
- **Learning Feedback**: Successful patterns influence agent specializations
- **Coordination**: Works alongside other quality agents (@assert-specialist, @coach-master)
- **Evolution**: Criteria evolution mirrors agent evolution mechanisms

## 🔮 Future Enhancements

- [ ] **ML-based Pattern Recognition**: Train models on historical data
- [ ] **Context-Aware Reviews**: Adapt criteria based on file types and project areas
- [ ] **Collaborative Learning**: Learn from multiple repositories
- [ ] **Predictive Scoring**: Estimate PR merge probability before review
- [ ] **Natural Language Explanations**: Generate human-friendly explanations
- [ ] **A/B Testing**: Test criteria variations to optimize effectiveness

## 📚 Resources

- **CODE_REVIEW_CHECKLIST.md**: Human-oriented review checklist
- **AUTONOMOUS_SYSTEM_ARCHITECTURE.md**: Overall system design
- **Agent Evaluator**: Similar learning system for agent performance

## 🐛 Troubleshooting

### Reviews Not Running

Check workflow permissions:
```yaml
permissions:
  pull-requests: write  # Required to comment
  contents: read        # Required to read files
```

### Criteria Not Evolving

Ensure enough reviews have occurred:
```bash
jq '.metadata.total_reviews' .github/review-system/criteria.json
```

Minimum required: 10 reviews (configurable)

### Low Success Rate

This is expected initially! The system needs time to learn. Success rate should improve over 20-30 reviews.

## 🙏 Credits

**Created by**: @workflows-tech-lead  
**Inspired by**: Agent evaluation system, adaptive thresholds, evolutionary algorithms  
**Philosophy**: "The best reviewer is one that learns from experience"

---

*🤖 This autonomous reviewer embodies the Chained principle: **everything should improve itself over time**.*
