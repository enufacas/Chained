# Autonomous Issue Prioritizer - Quick Reference

**@create-botter** - Multi-Armed Bandit Issue Prioritization System

## 🚀 Quick Start

```bash
# Prioritize issues from JSON
python3 tools/autonomous_issue_prioritizer.py \
  --action prioritize \
  --issue-data issues.json \
  --output recommendations.json

# Record successful resolution
python3 tools/autonomous_issue_prioritizer.py \
  --action record \
  --issue-number 123 \
  --success

# View statistics
python3 tools/autonomous_issue_prioritizer.py \
  --action stats

# Run interactive demo
python3 tools/example_autonomous_issue_prioritizer.py

# Run tests
cd tools && python3 test_autonomous_issue_prioritizer.py -v
```

## 🎯 Prioritization Arms

| Arm | Strategy | Best For |
|-----|----------|----------|
| **urgency** | Age + urgent labels | Time-sensitive issues |
| **complexity** | Simple issues first | Quick wins |
| **impact** | High-value issues | Critical features/bugs |
| **balanced** | Weighted combination | General use |
| **exploration** | Random sampling | Discovery |

## 📊 How It Learns

```
Issue Prioritized → Work Done → Record Outcome → Update Statistics → Improve
         ↑                                                              ↓
         └──────────────── Thompson Sampling Selects Arm ──────────────┘
```

## 🔧 Integration Points

### With GitHub Actions
- Runs every 6 hours automatically
- Fetches open issues
- Applies priority labels
- Records closed issue outcomes

### With Agent System
- Can inform agent assignment
- Prioritizes agent workload
- Tracks resolution success rates

### With Issue Clustering
- Complements categorization
- Adds priority dimension
- Cross-validates patterns

## 📈 Key Metrics

- **Expected Value**: Success probability (0-1)
- **Confidence Interval**: Uncertainty range
- **Priority Score**: Computed priority (0-1)
- **Pulls**: Times strategy was used

## 💾 State Persistence

Location: `tools/data/issue_prioritizer_state.json`

Contains:
- Arm statistics (successes, failures, pulls)
- Historical outcomes
- All recommendations made
- Last updated timestamp

## 🎓 Theory

**Thompson Sampling (Bayesian MAB)**
- Maintains Beta(α, β) distribution per arm
- α = successes + 1, β = failures + 1
- Samples from each distribution
- Selects highest sample
- Updates based on reward

**Advantages:**
- Optimal regret bounds: O(√T log T)
- Natural exploration/exploitation balance
- Works well with limited data
- Bayesian confidence intervals

## 🐛 Troubleshooting

**Low confidence?** → Need more data (record outcomes)  
**All arms equal?** → Strategies genuinely equivalent or insufficient learning  
**State not saving?** → Check `tools/data/` permissions

## 📖 Full Documentation

See `tools/AUTONOMOUS_ISSUE_PRIORITIZER_README.md` for:
- Detailed theory
- API reference
- Use cases
- Configuration
- Advanced topics

---

**Created by @create-botter with visionary Tesla-inspired innovation** ⚡
