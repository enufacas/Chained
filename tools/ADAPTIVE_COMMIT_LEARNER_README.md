# Adaptive Commit Learner

## Quick Start

```bash
# Learn from last 7 days of commits
python3 tools/adaptive-commit-learner.py --learn --days 7 --verbose

# Validate previous recommendations
python3 tools/adaptive-commit-learner.py --validate --verbose

# Generate comprehensive report
python3 tools/adaptive-commit-learner.py --report --output analysis/report.md
```

## What It Does

This tool implements an **adaptive learning system** that continuously improves its understanding of optimal git commit strategies. Unlike traditional analysis that reprocesses all history, it:

1. **Learns incrementally** from recent commits
2. **Adapts learning rate** based on confidence
3. **Tracks pattern evolution** over time
4. **Validates recommendations** with feedback loop
5. **Recognizes temporal patterns** in commit activity

## Key Features

### 🧠 Incremental Learning

Analyzes only recent commits (default: 7 days) instead of full history:

```python
learner = AdaptiveCommitLearner(verbose=True)
result = learner.incremental_learn(days_lookback=7)
```

**Benefits**:
- Fast execution (~30-60 seconds)
- Continuous learning without full reanalysis
- Adapts to repository evolution

### 📈 Adaptive Learning Rate

Learning rate automatically adjusts based on session count:

```
learning_rate = 0.1 * (0.95 ^ session_count)
```

**Example progression**:
- Session 1: 0.100 (high responsiveness)
- Session 10: 0.060 (more stable)
- Session 50: 0.008 (very stable, refined)

### 🔄 Pattern Evolution Tracking

Monitors how patterns change over time:

```json
{
  "pattern_name": "message_conventional_commits",
  "confidence_history": [
    {"timestamp": "2025-11-20T10:00:00", "value": 0.75},
    {"timestamp": "2025-11-21T10:00:00", "value": 0.82},
    {"timestamp": "2025-11-22T10:00:00", "value": 0.88}
  ],
  "trend": "improving"
}
```

**Trend Classification**:
- **Improving**: Confidence increasing by 10%+
- **Stable**: Confidence within ±10%
- **Declining**: Confidence decreasing by 10%+

### ✅ Recommendation Validation

Creates feedback loop to validate previous recommendations:

```python
validation = learner.validate_recommendations(validation_window_days=30)
print(f"Validated: {validation['validated']}")
print(f"Invalidated: {validation['invalidated']}")
```

**Validation Logic**:
- **Validated**: Current confidence ≥ 90% of original
- **Invalidated**: Current confidence < 70% of original
- **Active**: Needs more data (between 70-90%)

## CLI Commands

### Learn Mode

```bash
python3 tools/adaptive-commit-learner.py --learn [OPTIONS]

Options:
  --days INT        Days to analyze (default: 7)
  --verbose, -v     Enable verbose logging
```

**Output**:
```
🧠 Performing incremental learning (last 7 days)...
✅ Learning complete!
   Session: #12
   Commits analyzed: 42
   New insights: 5
   Learning velocity: 3.2 insights/session
```

### Validate Mode

```bash
python3 tools/adaptive-commit-learner.py --validate [OPTIONS]

Options:
  --validation-window INT    Days for validation (default: 30)
  --verbose, -v              Enable verbose logging
```

**Output**:
```
✓ Validating recommendations (window: 30 days)...
✅ Validation complete!
   Validated: 3
   Invalidated: 1
   Still active: 8
```

### Report Mode

```bash
python3 tools/adaptive-commit-learner.py --report [OPTIONS]

Options:
  --output FILE     Output file path
  --verbose, -v     Enable verbose logging
```

**Output**: Comprehensive markdown report with:
- System status
- Pattern evolution summary
- Recent learning sessions
- Validated insights

## Programmatic Usage

### Basic Usage

```python
from adaptive_commit_learner import AdaptiveCommitLearner

# Initialize
learner = AdaptiveCommitLearner(repo_path=".", verbose=True)

# Incremental learning
result = learner.incremental_learn(days_lookback=7)

print(f"Session: #{result['session']['session_id']}")
print(f"Insights: {result['session']['new_insights']}")
print(f"Velocity: {result['learning_velocity']}")
```

### Advanced Usage

```python
# Custom learning workflow
learner = AdaptiveCommitLearner(verbose=True)

# 1. Learn from recent activity
learn_result = learner.incremental_learn(days_lookback=14)

# 2. Validate recommendations
validate_result = learner.validate_recommendations(
    validation_window_days=30
)

# 3. Generate report
report = learner.generate_adaptive_report()

# Save report
with open('analysis/custom_report.md', 'w') as f:
    f.write(report)
```

### Accessing Data

```python
# Get adaptive learning data
adaptive_data = learner.adaptive_data

# Learning sessions
sessions = adaptive_data['learning_sessions']
latest_session = sessions[-1]

# Active learnings (not yet validated)
active = adaptive_data['active_learnings']

# Validated patterns
validated = adaptive_data['validated_patterns']

# Get pattern evolution
evolution_data = learner.evolution_data
patterns = evolution_data['patterns']

for name, data in patterns.items():
    trend = data['trend']
    confidence_history = data['confidence_history']
    print(f"{name}: {trend}")
```

## Data Structures

### AdaptiveLearning

```python
@dataclass
class AdaptiveLearning:
    insight_id: str              # Unique identifier
    timestamp: str               # ISO format
    pattern_type: str            # "message", "size", "organization"
    learning_text: str           # Human-readable insight
    confidence: float            # 0.0-1.0
    evidence_count: int          # Number of commits
    validation_status: str       # "unvalidated", "validated", "invalidated"
    learning_rate: float         # Session learning rate
    temporal_context: Dict       # Time-based context
```

### PatternEvolution

```python
@dataclass
class PatternEvolution:
    pattern_name: str                    # Pattern identifier
    first_observed: str                  # ISO timestamp
    last_updated: str                    # ISO timestamp
    confidence_history: List[Dict]       # Historical confidence
    occurrence_history: List[Dict]       # Historical occurrences
    trend: str                           # "improving", "stable", "declining"
```

## Integration with Base Learner

This tool **extends** the base `commit-strategy-learner.py`:

```
Base Learner (commit-strategy-learner.py)
    │
    ├─ Commit metrics extraction
    ├─ Pattern identification
    ├─ Recommendation generation
    └─ Comprehensive analysis
    
Adaptive Learner (adaptive-commit-learner.py)
    │
    ├─ Inherits all base capabilities
    │
    └─ Adds:
       ├─ Incremental learning
       ├─ Learning rate management
       ├─ Pattern evolution tracking
       ├─ Validation feedback
       └─ Temporal awareness
```

**Both can be used independently or together.**

## Configuration

### Constants (in script)

```python
# Learning parameters
LEARNING_RATE_BASE = 0.1         # Initial learning rate
LEARNING_RATE_DECAY = 0.95       # Decay per session
MIN_PATTERN_CONFIDENCE = 0.6     # Minimum to extract insight
PATTERN_EVOLUTION_WINDOW = 90    # Days for trend analysis
```

### File Locations

```python
LEARNINGS_DIR = Path("learnings")
ANALYSIS_DIR = Path("analysis")
ADAPTIVE_LEARNINGS_FILE = LEARNINGS_DIR / "adaptive_commit_learning.json"
PATTERN_EVOLUTION_FILE = ANALYSIS_DIR / "pattern_evolution.json"
```

## Troubleshooting

### No Insights Generated

**Symptoms**: `new_insights: 0` in output

**Possible Causes**:
1. No recent commits in lookback window
2. Patterns below confidence threshold
3. All patterns already learned

**Solutions**:
- Increase `days_lookback`
- Lower `MIN_PATTERN_CONFIDENCE`
- Wait for more commit activity

### High Invalidation Rate

**Symptoms**: Many patterns invalidated during validation

**Possible Causes**:
1. Repository practices changed
2. Previous patterns were false positives
3. Insufficient validation window

**Solutions**:
- Review invalidated patterns
- Increase `validation_window_days`
- Consider full reanalysis with base learner

### Learning Velocity Too High

**Symptoms**: `learning_velocity > 10`

**Possible Causes**:
1. Unstable patterns
2. Confidence threshold too low
3. Too frequent analysis

**Solutions**:
- Increase `MIN_PATTERN_CONFIDENCE`
- Extend days between sessions
- Review pattern stability

## Performance

### Execution Time

- **Incremental Learning**: ~30-60 seconds (7 days, ~100 commits)
- **Validation**: ~10-20 seconds
- **Report Generation**: ~5-10 seconds

**Total**: ~45-90 seconds per session

### Memory Usage

- **Peak RAM**: ~50-100 MB
- **Data Files**: <100 KB total

### Scalability

- Efficient for repos with <10,000 total commits
- Optimized for incremental analysis
- Constant memory usage (doesn't grow with repo size)

## Dependencies

```bash
pip install gitpython
```

**Note**: No additional ML libraries required. Uses statistical methods.

## Examples

### Example 1: Daily Learning Routine

```bash
#!/bin/bash
# Run daily at 6 AM

cd /path/to/repo

# Learn from yesterday
python3 tools/adaptive-commit-learner.py \
  --learn \
  --days 1 \
  --verbose

# Validate weekly
if [ $(date +%u) -eq 1 ]; then
  python3 tools/adaptive-commit-learner.py \
    --validate \
    --validation-window 7 \
    --verbose
fi
```

### Example 2: Custom Analysis Script

```python
#!/usr/bin/env python3
"""Custom adaptive learning script"""

from adaptive_commit_learner import AdaptiveCommitLearner
import json

def main():
    learner = AdaptiveCommitLearner(verbose=True)
    
    # Learn from last 2 weeks
    result = learner.incremental_learn(days_lookback=14)
    
    # Get high-confidence insights
    high_confidence = [
        insight for insight in learner.adaptive_data['active_learnings']
        if insight['confidence'] > 0.8
    ]
    
    # Save high-confidence insights
    with open('high_confidence_insights.json', 'w') as f:
        json.dump(high_confidence, f, indent=2)
    
    print(f"Found {len(high_confidence)} high-confidence insights")

if __name__ == '__main__':
    main()
```

### Example 3: Pattern Trend Monitoring

```python
#!/usr/bin/env python3
"""Monitor pattern trends"""

from adaptive_commit_learner import AdaptiveCommitLearner

def main():
    learner = AdaptiveCommitLearner(verbose=False)
    
    # Get pattern evolution data
    evolution = learner.evolution_data['patterns']
    
    # Find improving patterns
    improving = [
        name for name, data in evolution.items()
        if data['trend'] == 'improving'
    ]
    
    # Find declining patterns
    declining = [
        name for name, data in evolution.items()
        if data['trend'] == 'declining'
    ]
    
    print("📈 Improving Patterns:")
    for pattern in improving:
        print(f"  - {pattern}")
    
    print("\n📉 Declining Patterns:")
    for pattern in declining:
        print(f"  - {pattern}")

if __name__ == '__main__':
    main()
```

## See Also

- [Adaptive Commit Learning System](../docs/ADAPTIVE_COMMIT_LEARNING_SYSTEM.md) - Complete system documentation
- [Base Commit Strategy Learner](./commit-strategy-learner.py) - Foundation tool
- [Commit Learning System](../docs/commit-learning-system.md) - Original system docs

---

**Created by**: @create-guru  
**Version**: 2.0.0  
**Last Updated**: 2025-11-26
