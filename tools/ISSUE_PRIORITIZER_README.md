# Autonomous Issue Prioritizer Using Multi-Armed Bandits

## Overview

The **Autonomous Issue Prioritizer** is an intelligent system that uses **Thompson Sampling**, a Bayesian approach to the multi-armed bandit problem, to learn which types of issues should be prioritized for faster resolution.

**Author**: @APIs-architect  
**Inspired by**: Margaret Hamilton - rigorous and innovative

## Key Concepts

### Multi-Armed Bandit Problem

Imagine you're at a casino with multiple slot machines (bandits), each with different unknown payout rates. You want to maximize your winnings, but you don't know which machines are best. The multi-armed bandit problem is about balancing:

- **Exploration**: Trying different machines to learn their payout rates
- **Exploitation**: Playing the machines you know pay well

In our context:
- Each **issue category** (bug, feature, security, etc.) is an "arm"
- The "reward" is successful resolution in reasonable time
- The system learns which categories to prioritize

### Thompson Sampling

Thompson Sampling is a Bayesian approach that:
1. Maintains a probability distribution for each category's success rate
2. Samples from these distributions to make prioritization decisions
3. Updates distributions based on observed outcomes
4. Naturally balances exploration and exploitation

**Why Thompson Sampling?**
- Optimal regret bounds (minimizes mistakes over time)
- Handles uncertainty elegantly
- Simple to implement with Beta distributions
- Proven effectiveness in real-world applications

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                   IssuePrioritizer                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Issue Categories (Arms)                        │  │
│  │  - bug, feature, documentation, security, ...   │  │
│  │  - Each arm tracks: successes, failures, time   │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Thompson Sampling Engine                        │  │
│  │  - Beta distribution per category                │  │
│  │  - Sample → Prioritize → Learn cycle            │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Learning System                                 │  │
│  │  - Records outcomes                              │  │
│  │  - Updates success rates                         │  │
│  │  - Tracks resolution times                       │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Data Structures

**IssueArm**: Represents a category of issues
- `successes`: Number of successful resolutions (Beta α)
- `failures`: Number of failed resolutions (Beta β)
- `total_pulls`: Total times this category was prioritized
- `avg_resolution_time_hours`: Moving average of resolution time

**IssuePriority**: Priority decision for an issue
- `category`: Detected category
- `priority`: CRITICAL, HIGH, MEDIUM, or LOW
- `confidence`: 0.0 to 1.0 based on historical data
- `estimated_resolution_hours`: Expected time to resolve
- `reasoning`: Human-readable explanation

## Usage

### CLI Interface

#### Prioritize an Issue

```bash
python3 tools/issue_prioritizer.py prioritize \
  --title "Fix authentication bug" \
  --body "Users cannot log in after password reset" \
  --issue-number 123 \
  --labels bug security
```

Output:
```
🎯 Issue Priority Decision
━━━━━━━━━━━━━━━━━━━━━━━━
Category:     security
Priority:     HIGH
Confidence:   65.0%
Est. Time:    8.5 hours

💡 Reasoning:
   Category 'security' has 78.0% historical success rate
   (39 successes, 11 failures)
   Average resolution time: 8.5 hours
```

#### Record an Outcome

After an issue is resolved, record the outcome to train the system:

```bash
python3 tools/issue_prioritizer.py record \
  --issue-number 123 \
  --category security \
  --success \
  --resolution-time 7.5
```

#### View Statistics

```bash
python3 tools/issue_prioritizer.py stats
```

Output:
```
📊 Issue Prioritizer Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall:
  Total Decisions:  150
  Successes:        112
  Failures:         38
  Success Rate:     74.7%
  Avg Resolution:   9.3 hours

📁 Categories:
  bug:
    Success Rate:     82.0%
    Samples:          45
    Avg Resolution:   6.2h
  
  security:
    Success Rate:     78.0%
    Samples:          50
    Avg Resolution:   8.5h
```

#### Get Top Priority Categories

```bash
python3 tools/issue_prioritizer.py top -n 5
```

Output:
```
🏆 Top 5 Priority Categories (Thompson Sampling)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SECURITY
   Sampled Priority:  0.823
   Success Rate:      78.0%
   Total Samples:     50
   Avg Resolution:    8.5h

2. BUG
   Sampled Priority:  0.798
   Success Rate:      82.0%
   Total Samples:     45
   Avg Resolution:    6.2h
```

### Python API

```python
from tools.issue_prioritizer import IssuePrioritizer, PriorityLevel

# Initialize
prioritizer = IssuePrioritizer()

# Prioritize an issue
priority = prioritizer.prioritize_issue(
    issue_number=123,
    title="Fix authentication bug",
    body="Users cannot log in",
    labels=["bug", "security"],
    current_open_issues=25
)

print(f"Category: {priority.category}")
print(f"Priority: {priority.priority.value}")
print(f"Confidence: {priority.confidence:.1%}")
print(f"Estimated time: {priority.estimated_resolution_hours:.1f}h")

# Record outcome when resolved
prioritizer.record_outcome(
    issue_number=123,
    category=priority.category,
    success=True,
    resolution_time_hours=7.5
)

# Get statistics
stats = prioritizer.get_stats()
print(f"Overall success rate: {stats['overall']['total_successes']/stats['overall']['total_decisions']:.1%}")

# Get top priorities
top_categories = prioritizer.get_top_priorities(n=5)
for cat in top_categories:
    print(f"{cat['category']}: {cat['sampled_priority']:.3f}")
```

## Issue Categories

The system automatically detects these categories:

| Category | Keywords | Typical Priority |
|----------|----------|------------------|
| `bug` | bug, error, fix, broken, crash, fail | HIGH-CRITICAL |
| `feature` | feature, enhancement, add, new, implement | MEDIUM-HIGH |
| `documentation` | doc, documentation, readme, guide, tutorial | LOW-MEDIUM |
| `refactoring` | refactor, cleanup, reorganize, simplify | MEDIUM |
| `security` | security, vulnerability, cve, exploit, auth | CRITICAL |
| `performance` | performance, slow, optimize, speed | MEDIUM-HIGH |
| `testing` | test, testing, coverage, unit test | MEDIUM |
| `infrastructure` | infrastructure, ci, cd, workflow, pipeline | MEDIUM |
| `ai-idea` | ai idea, ai-generated, autonomous, agent | MEDIUM |
| `other` | (fallback for unknown) | LOW-MEDIUM |

## How Thompson Sampling Works

### 1. Initial State (No Data)

When no data exists, each category starts with a **uniform prior**: Beta(1, 1)

```
All categories have equal probability: ~50% success rate
```

### 2. Sampling for Decision

For each decision, sample from Beta distributions:

```python
for category in categories:
    α = successes + 1  # Beta alpha parameter
    β = failures + 1   # Beta beta parameter
    sampled_value = random.betavariate(α, β)
```

Category with highest sampled value gets prioritized.

### 3. Learning from Outcomes

When an outcome is recorded:

```python
if success:
    successes += 1  # Increase α
else:
    failures += 1   # Increase β
```

The Beta distribution narrows around the true success rate.

### 4. Exploration vs Exploitation

- **Early**: Wide distributions → more exploration
- **Later**: Narrow distributions → more exploitation
- **Thompson Sampling automatically balances this!**

### Example Evolution

```
After 0 samples:  Bug [====????====] 50% ± 50%
After 5 samples:  Bug [======??====] 60% ± 30%
After 20 samples: Bug [=======?====] 65% ± 15%
After 50 samples: Bug [============] 68% ± 8%
```

## Configuration

The prioritizer is configured in the registry file (`.github/agent-system/issue_prioritizer.json`):

```json
{
  "config": {
    "min_samples_for_exploitation": 10,
    "exploration_bonus": 0.1,
    "time_decay_factor": 0.95,
    "categories": [...]
  }
}
```

**Parameters**:
- `min_samples_for_exploitation`: Minimum samples before trusting data
- `exploration_bonus`: Additional weight for unexplored categories
- `time_decay_factor`: Decay for moving average of resolution time

## Integration with Workflows

### Automatic Prioritization Workflow

```yaml
# .github/workflows/auto-prioritize-issues.yml
name: Auto-Prioritize Issues
on:
  issues:
    types: [opened, labeled]

jobs:
  prioritize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Prioritize Issue
        run: |
          PRIORITY=$(python3 tools/issue_prioritizer.py prioritize \
            --title "${{ github.event.issue.title }}" \
            --body "${{ github.event.issue.body }}" \
            --issue-number ${{ github.event.issue.number }} \
            --labels "${{ join(github.event.issue.labels.*.name, ' ') }}")
          
          echo "$PRIORITY" >> $GITHUB_STEP_SUMMARY
```

### Recording Outcomes

```yaml
# When issue is closed via PR
- name: Record Outcome
  if: github.event.issue.closed_at
  run: |
    RESOLUTION_HOURS=$(calculate_hours_between \
      "${{ github.event.issue.created_at }}" \
      "${{ github.event.issue.closed_at }}")
    
    python3 tools/issue_prioritizer.py record \
      --issue-number ${{ github.event.issue.number }} \
      --category "$(detect_category)" \
      --success \
      --resolution-time $RESOLUTION_HOURS
```

## Performance Characteristics

### Time Complexity
- **Prioritization**: O(C) where C = number of categories (~10)
- **Recording outcome**: O(1)
- **Get statistics**: O(C)
- **Get top priorities**: O(C log C)

### Space Complexity
- **Registry file**: O(C + H) where H = history size (max 1000)
- **Memory**: O(C) during operation

### Concurrency
- **Atomic writes**: Uses temp file + rename for crash safety
- **File locking**: Not implemented (assume single writer)
- **Multiple readers**: Safe (reads are atomic)

## Testing

Run the comprehensive test suite:

```bash
# All tests
python3 -m unittest tests.test_issue_prioritizer -v

# Specific test
python3 -m unittest tests.test_issue_prioritizer.TestIssuePrioritizer.test_prioritize_issue_basic -v
```

**Test Coverage**:
- 31 tests covering all functionality
- Unit tests for Thompson Sampling
- Integration tests for full workflow
- Edge cases (corruption, history pruning)
- 100% code coverage of core logic

## Advantages Over Static Prioritization

| Aspect | Static Rules | Thompson Sampling |
|--------|-------------|------------------|
| Adaptation | No | Yes - learns over time |
| Exploration | Manual | Automatic |
| Uncertainty | Ignored | Handled elegantly |
| Category bias | Fixed | Self-correcting |
| Data requirements | None | Improves with data |
| Optimality | Suboptimal | Near-optimal |

## Future Enhancements

1. **Agent-Specific Learning**: Track success per agent-category pair
2. **Time-Based Patterns**: Learn which categories are faster at different times
3. **Context Features**: Use more issue metadata (author, complexity, etc.)
4. **Multi-Objective**: Optimize for both speed and quality
5. **Bandit Variants**: Try UCB, Epsilon-Greedy for comparison

## References

- **Thompson Sampling**: Thompson, W. R. (1933). "On the likelihood that one unknown probability exceeds another"
- **Multi-Armed Bandits**: Sutton & Barto (2018). "Reinforcement Learning: An Introduction"
- **Beta Distribution**: Used for Bayesian inference on Bernoulli trials

## Contributing

When contributing to the issue prioritizer:

1. **Add tests** for new functionality
2. **Maintain atomicity** for file operations
3. **Document** new categories or features
4. **Validate** statistical properties
5. **Benchmark** performance impact

---

**Built by @APIs-architect** - Ensuring reliability through rigorous design and testing.
