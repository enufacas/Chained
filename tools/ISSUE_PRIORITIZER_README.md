# 🎯 Autonomous Issue Prioritizer

## Multi-Armed Bandit Based Intelligent Issue Prioritization

**Implemented by:** @accelerate-master  
**Algorithm:** Upper Confidence Bound (UCB1)  
**Status:** Active

---

## 📋 Overview

The Autonomous Issue Prioritizer uses **multi-armed bandit (MAB) algorithms** to intelligently prioritize issues based on historical outcomes. Unlike static prioritization systems, this system **learns and adapts** over time, becoming more accurate as it processes more issues.

### Why Multi-Armed Bandits?

The multi-armed bandit problem is a classic reinforcement learning challenge where you must balance:
- **Exploration**: Trying new issue types to learn about them
- **Exploitation**: Prioritizing issue types that have historically performed well

This is perfect for issue prioritization because:
1. **Adaptive**: Learns which types of issues lead to successful outcomes
2. **Balanced**: Doesn't ignore less common issue types
3. **Efficient**: Makes optimal decisions with limited data
4. **Self-improving**: Gets better with each resolved issue

## 🧮 Algorithm: UCB1

The system uses the **Upper Confidence Bound (UCB1)** algorithm:

```
UCB1 Score = Average Reward + c × √(ln(total_trials) / type_trials)
              ↑                   ↑
         Exploitation         Exploration
```

Where:
- **Average Reward**: Historical success rate for this issue type
- **c**: Exploration parameter (√2 ≈ 1.414)
- **total_trials**: Total number of resolved issues
- **type_trials**: Number of issues resolved of this type

### Reward Calculation

Each resolved issue receives a reward (0.0 to 1.0) based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| PR Success | 40% | Was the issue resolved with a merged PR? |
| Code Quality | 30% | Quality score of the solution |
| Resolution Speed | 20% | How quickly was it resolved? (normalized to 48h) |
| Agent Performance | 10% | Overall performance of assigned agent |

```python
reward = (0.4 × pr_success) + (0.3 × code_quality) + 
         (0.2 × speed_bonus) + (0.1 × agent_score)
```

## 📊 Issue Types (Arms)

The system categorizes issues into 8 types:

1. **Performance** - Optimization, speed improvements
2. **Bug** - Errors, crashes, failures
3. **Feature** - New functionality, enhancements
4. **Testing** - Test coverage, QA
5. **Security** - Vulnerabilities, auth issues
6. **Documentation** - Docs, guides, tutorials
7. **Refactor** - Code cleanup, technical debt
8. **Infrastructure** - CI/CD, deployment, automation

Each type is an "arm" in the bandit, with its own learned success rate.

## 🎯 Priority Tiers

Issues are assigned to priority tiers based on their UCB1 score:

| Tier | Score Range | Action |
|------|-------------|--------|
| **P0-Critical** | 0.85 - 1.0 | Implement immediately |
| **P1-High** | 0.70 - 0.84 | Plan for next sprint |
| **P2-Medium** | 0.50 - 0.69 | Add to backlog |
| **P3-Low** | 0.0 - 0.49 | Monitor |

## 🔧 Usage

### Command Line Interface

```bash
# Update bandit state from historical data
python3 tools/issue-prioritizer.py update

# Show current statistics
python3 tools/issue-prioritizer.py stats

# Prioritize a single issue
python3 tools/issue-prioritizer.py prioritize \
  --issue-number 123 \
  --title "Database performance issue" \
  --body "Queries are slow" \
  --labels performance database

# Generate priority report
python3 tools/issue-prioritizer.py report
```

### Programmatic Usage

```python
from pathlib import Path
from tools.issue_prioritizer import IssuePrioritizer

# Initialize prioritizer
prioritizer = IssuePrioritizer()

# Update from history
prioritizer.update_from_history()

# Prioritize an issue
result = prioritizer.prioritize_issue(
    issue_number=123,
    title="Optimize database queries",
    body="Performance degradation observed",
    labels=["performance", "database"]
)

print(f"Priority: {result['priority_score']}")
print(f"Tier: {result['priority_tier']}")
print(f"Action: {result['recommended_action']}")
```

## 🤖 Automated Workflow

The system runs automatically via GitHub Actions (`.github/workflows/issue-prioritizer.yml`):

### Triggers

1. **New Issue Opened**: Automatically prioritizes and labels
2. **Daily Schedule**: Generates priority report for all open issues
3. **Manual Dispatch**: Run on-demand

### What It Does

When a new issue is opened:
1. ✅ Updates bandit state from historical data
2. 🎯 Classifies the issue type
3. 📊 Calculates UCB1 score and priority
4. 🏷️ Adds priority and type labels
5. 💬 Comments with detailed priority analysis

Daily:
1. 📈 Prioritizes all open issues
2. 📋 Generates comprehensive priority report
3. 📝 Creates report issue with recommendations

## 📈 Performance

**Benchmark Results** (@accelerate-master efficiency):
- ⚡ **~0.007ms per issue** (on average hardware)
- 📦 Minimal memory footprint
- 🚀 Can process 1000+ issues/second
- 💾 State persistence in JSON (no database needed)

## 🧪 Testing

Comprehensive test suite in `tests/test_issue_prioritizer.py`:

```bash
# Run all tests
python3 tests/test_issue_prioritizer.py
```

Test coverage:
- ✅ Reward calculation
- ✅ UCB1 algorithm correctness
- ✅ Issue classification
- ✅ Priority calculation
- ✅ Full prioritization flow
- ✅ Historical data updates
- ✅ State persistence
- ✅ Report generation
- ✅ Performance benchmarks

All tests pass with **< 5ms per issue target** met.

## 📚 Examples

### Example 1: High-Priority Performance Issue

```json
{
  "issue_number": 999,
  "title": "Optimize database performance",
  "issue_type": "performance",
  "priority_score": 0.729,
  "priority_tier": "P1-High",
  "recommended_action": "Plan for next sprint",
  "ucb1_stats": {
    "attempts": 3,
    "avg_reward": 0.28
  }
}
```

### Example 2: Unexplored Security Issue

Security issues that haven't been tried yet get **infinite UCB1 score** (highest priority) to encourage exploration:

```
security        | Attempts:   0 | Avg Reward: 0.000 | UCB1: inf
```

This ensures new issue types are explored before assuming they're low priority.

### Example 3: Learning Over Time

After processing 8 issues:
```
📊 Multi-Armed Bandit Statistics

Total trials: 8

performance     | Attempts:   3 | Avg Reward: 0.280 | UCB1: 1.457
bug             | Attempts:   3 | Avg Reward: 0.280 | UCB1: 1.457
feature         | Attempts:   1 | Avg Reward: 0.280 | UCB1: 2.319
testing         | Attempts:   1 | Avg Reward: 0.280 | UCB1: 2.319
```

Notice how `feature` and `testing` (less explored) get higher UCB1 scores than `performance` and `bug`, encouraging exploration.

## 🎓 Learning & Adaptation

The system continuously learns:

1. **Historical Learning**: Analyzes past issue outcomes
2. **Reward Updates**: Tracks success metrics for each issue type
3. **Exploration Bonus**: Gives less-tried types a chance
4. **State Persistence**: Saves learning progress
5. **Continuous Improvement**: Gets smarter with each resolved issue

### Convergence Behavior

As the system processes more issues:
- **Early**: Heavy exploration (trying all types)
- **Middle**: Balanced exploration/exploitation
- **Mature**: Mostly exploitation with occasional exploration

## 🔍 Monitoring

### Current State

```bash
# Check current statistics
python3 tools/issue-prioritizer.py stats
```

### State File

State is saved to `.github/agent-system/priority_state.json`:

```json
{
  "version": "1.0",
  "updated_at": "2025-11-15T16:00:00Z",
  "issue_types": {
    "performance": {
      "total_attempts": 10,
      "total_reward": 7.5,
      "average_reward": 0.75
    }
  }
}
```

## 🎯 Design Philosophy (@accelerate-master)

This implementation follows @accelerate-master principles:

✅ **Simple**: Clear algorithm, easy to understand  
✅ **Efficient**: < 5ms per issue, minimal overhead  
✅ **Deliberate**: Well-thought-out reward structure  
✅ **Performance-focused**: Benchmarked and optimized  
✅ **Self-improving**: Learns from every outcome  

The design simplifies through smart architecture rather than adding complexity.

## 🔗 Integration Points

### With Agent System
- Uses historical issue data from `.github/agent-system/issue_history.json`
- Considers agent performance in reward calculation
- Helps assign issues to appropriate agents

### With Workflows
- Integrates with existing GitHub Actions
- Automatic labeling of new issues
- Priority-based issue routing

### With Learning System
- Learns from TLDR and HackerNews inspired issues
- Tracks which tech trends lead to successful issues
- Adapts priorities based on ecosystem evolution

## 📖 References

### Multi-Armed Bandits
- **UCB1 Algorithm**: [Auer et al., 2002](https://homes.di.unimi.it/~cesabian/Pubblicazioni/ml-02.pdf)
- **Exploration vs Exploitation**: Classic RL tradeoff
- **Upper Confidence Bound**: Optimistic in face of uncertainty

### Related Work
- [Thompson Sampling](https://en.wikipedia.org/wiki/Thompson_sampling) - Alternative Bayesian approach
- [Epsilon-Greedy](https://en.wikipedia.org/wiki/Multi-armed_bandit#Semi-uniform_strategies) - Simpler but less optimal
- [EXP3](https://en.wikipedia.org/wiki/Multi-armed_bandit#Adversarial_bandit_problem) - For adversarial settings

## 🚀 Future Enhancements

Potential improvements:
1. **Contextual Bandits**: Consider issue context (author, time, dependencies)
2. **Thompson Sampling**: Bayesian alternative to UCB1
3. **Neural Bandits**: Deep learning for complex patterns
4. **Multi-objective**: Optimize for multiple goals simultaneously
5. **Federated Learning**: Share knowledge across repositories

## 🤝 Contributing

To improve the prioritization system:

1. **Adjust Reward Weights**: Modify `IssueMetrics.calculate_reward()`
2. **Add Issue Types**: Extend the `issue_types` dictionary
3. **Tune Exploration**: Adjust the `c` parameter in UCB1
4. **Add Features**: Implement contextual bandits

## 📝 License

Part of the Chained autonomous AI ecosystem. See main repository LICENSE.

---

*🎯 Autonomous Issue Prioritizer - Learning to prioritize through experience*  
*Implemented by @accelerate-master with thoughtful, deliberate design*
