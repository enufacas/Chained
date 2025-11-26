# Adaptive Commit Strategy Learning System

## Overview

**@create-guru** has created an enhanced, Tesla-inspired learning system that continuously improves its understanding of optimal git commit strategies through adaptive learning principles.

## 🎯 What Makes It "Adaptive"?

Unlike traditional learning systems that analyze all history repeatedly, this system:

1. **Incremental Learning**: Learns from recent commits without reprocessing all history
2. **Adaptive Learning Rates**: Adjusts learning speed based on confidence levels (starts at 0.1, decays by 0.95 per session)
3. **Pattern Evolution Tracking**: Monitors how patterns change over time
4. **Recommendation Validation**: Creates a feedback loop to validate previous recommendations
5. **Temporal Awareness**: Recognizes time-based patterns in commit activity

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Adaptive Learning System                       │
│                                                          │
│  ┌────────────────┐    ┌───────────────────────┐       │
│  │ Base Learner   │───▶│ Adaptive Learner      │       │
│  │ (Patterns)     │    │ (Intelligence)        │       │
│  └────────────────┘    └───────────────────────┘       │
│         │                        │                       │
│         │                        ▼                       │
│         │              ┌───────────────────────┐        │
│         │              │ Pattern Evolution     │        │
│         │              │ Tracker               │        │
│         │              └───────────────────────┘        │
│         │                        │                       │
│         ▼                        ▼                       │
│  ┌────────────────────────────────────────┐            │
│  │    Learning Database                    │            │
│  │  • adaptive_commit_learning.json        │            │
│  │  • pattern_evolution.json               │            │
│  │  • commit_patterns.json                 │            │
│  └────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. Adaptive Commit Learner (`tools/adaptive-commit-learner.py`)

**Core Features:**

- **Incremental Learning**: Analyzes only recent commits (default: 7 days)
- **Learning Rate Decay**: Adjusts learning rate: `learning_rate = 0.1 * (0.95^session_count)`
- **Pattern Evolution**: Tracks confidence and occurrence over time
- **Validation Feedback**: Validates previous insights against recent data

**Key Classes:**

```python
@dataclass
class AdaptiveLearning:
    insight_id: str
    timestamp: str
    pattern_type: str
    learning_text: str
    confidence: float
    evidence_count: int
    validation_status: str  # "unvalidated", "validated", "invalidated"
    learning_rate: float
    temporal_context: Dict[str, Any]

@dataclass
class PatternEvolution:
    pattern_name: str
    first_observed: str
    last_updated: str
    confidence_history: List[Dict[str, float]]
    occurrence_history: List[Dict[str, int]]
    trend: str  # "improving", "stable", "declining"
```

### 2. Adaptive Learning Workflow (`.github/workflows/learn-commit-strategies-adaptive.yml`)

**Schedule:**
- Runs twice daily at 06:00 and 18:00 UTC
- Manual trigger with mode selection

**Modes:**
1. **Incremental** (default): Learn from recent commits
2. **Validate**: Validate previous recommendations
3. **Full Report**: Generate comprehensive report

**Workflow Steps:**
1. Checkout with full history
2. Perform incremental learning
3. Validate recommendations
4. Generate adaptive report
5. Create PR with updates
6. Create notification issue (if significant insights)

### 3. Data Files

#### `learnings/adaptive_commit_learning.json`

```json
{
  "version": "2.0.0",
  "last_updated": "ISO timestamp",
  "learning_sessions": [
    {
      "session_id": 1,
      "timestamp": "ISO timestamp",
      "days_analyzed": 7,
      "commits_analyzed": 42,
      "learning_rate": 0.1,
      "new_insights": 5,
      "patterns_updated": 3
    }
  ],
  "active_learnings": [],
  "validated_patterns": [],
  "invalidated_patterns": [],
  "cumulative_insights": 15,
  "learning_velocity": 3.2
}
```

#### `analysis/pattern_evolution.json`

```json
{
  "version": "1.0.0",
  "patterns": {
    "message_conventional_commits": {
      "pattern_name": "message_conventional_commits",
      "first_observed": "ISO timestamp",
      "last_updated": "ISO timestamp",
      "confidence_history": [
        {"timestamp": "ISO timestamp", "value": 0.85}
      ],
      "occurrence_history": [
        {"timestamp": "ISO timestamp", "value": 42}
      ],
      "trend": "improving"
    }
  },
  "last_updated": "ISO timestamp"
}
```

## Usage

### Manual Triggering

1. Go to **Actions** → "Adaptive Learning: Git Commit Strategies"
2. Click **Run workflow**
3. Select mode:
   - **incremental**: Learn from recent commits (default)
   - **validate**: Validate previous recommendations
   - **full-report**: Generate comprehensive report
4. Specify days_lookback (default: 7)

### Command Line

```bash
# Perform incremental learning (last 7 days)
python3 tools/adaptive-commit-learner.py --learn --days 7 --verbose

# Validate recommendations (30-day window)
python3 tools/adaptive-commit-learner.py --validate --validation-window 30

# Generate comprehensive report
python3 tools/adaptive-commit-learner.py --report --output analysis/report.md
```

### Programmatic Usage

```python
from adaptive_commit_learner import AdaptiveCommitLearner

# Initialize learner
learner = AdaptiveCommitLearner(repo_path=".", verbose=True)

# Perform incremental learning
result = learner.incremental_learn(days_lookback=7)
print(f"Session #{result['session']['session_id']}")
print(f"New insights: {result['session']['new_insights']}")

# Validate recommendations
validation = learner.validate_recommendations(validation_window_days=30)
print(f"Validated: {validation['validated']}")
print(f"Invalidated: {validation['invalidated']}")

# Generate report
report = learner.generate_adaptive_report()
print(report)
```

## Learning Metrics

### Learning Velocity

**Definition**: Average number of insights per learning session

**Formula**: `velocity = sum(insights_last_5_sessions) / 5`

**Interpretation**:
- High velocity (>5): Rapidly discovering new patterns
- Medium velocity (2-5): Steady learning progress
- Low velocity (<2): Patterns are stabilizing

### Pattern Trends

**Categories**:
- **Improving**: Recent confidence > previous by 10%+
- **Stable**: Recent confidence within ±10% of previous
- **Declining**: Recent confidence < previous by 10%+

**Calculation**: Compares last 3 observations with previous 3

## Validation Feedback Loop

### How Validation Works

1. For each unvalidated learning:
   - Get current pattern confidence from recent analysis
   - Compare with original confidence when learned
   
2. Validation thresholds:
   - **Validated**: New confidence ≥ 90% of original
   - **Invalidated**: New confidence < 70% of original
   - **Active**: Between 70-90% (needs more data)

3. Validated/invalidated patterns are archived
4. Only active learnings remain in rotation

### Benefits

- **Quality Control**: Filters out false patterns
- **Confidence Refinement**: Adjusts recommendations based on evidence
- **Adaptive Recommendations**: Only promotes proven patterns

## Integration with Existing System

### Relationship to Base Learner

The adaptive system **extends** the base `commit-strategy-learner.py`:

```python
# Base learner provides
- Commit metrics extraction
- Pattern identification
- Recommendation generation
- Comprehensive analysis

# Adaptive learner adds
- Incremental learning
- Learning rate management
- Pattern evolution tracking
- Validation feedback
- Temporal awareness
```

### Backward Compatibility

- Both systems can coexist
- Base learner provides foundation
- Adaptive learner adds intelligence
- Data formats are compatible

## Best Practices

### For Agents Using This System

1. **Check Learning Velocity**: High velocity means patterns are evolving
2. **Trust Validated Patterns**: These have passed validation
3. **Monitor Pattern Trends**: Improving patterns are gaining evidence
4. **Consider Temporal Context**: Some patterns may be time-dependent

### For Maintainers

1. **Review Significant Sessions**: Sessions with >5 insights warrant review
2. **Investigate Declining Patterns**: May indicate repository evolution
3. **Validate Manually**: Cross-check high-confidence patterns
4. **Adjust Parameters**: Tune learning rate if needed

## Performance Characteristics

### Computational Efficiency

- **Incremental Learning**: O(n) where n = recent commits (typically <100)
- **Validation**: O(m) where m = active learnings (typically <50)
- **Pattern Evolution**: O(p) where p = tracked patterns (typically <20)

**Total**: Much faster than full analysis (which is O(N) where N = all commits)

### Storage

- **adaptive_commit_learning.json**: ~10-50 KB
- **pattern_evolution.json**: ~5-20 KB
- **Combined**: <100 KB for typical repositories

### Frequency

- **Scheduled**: 2x daily (06:00, 18:00 UTC)
- **Runtime**: ~30-60 seconds per session
- **PR Creation**: Only when new insights found

## Monitoring

### Success Indicators

✅ **Healthy System**:
- Learning velocity: 2-5 insights/session
- Validation rate: >70% validated
- Pattern trends: Mostly stable/improving
- PR frequency: 1-2 per day

⚠️ **Needs Attention**:
- Learning velocity: <1 or >10 insights/session
- Validation rate: <50% validated
- Pattern trends: Many declining
- PR frequency: >5 per day or 0 for days

### Troubleshooting

**Problem**: No insights generated
- **Cause**: No recent commits or patterns below confidence threshold
- **Solution**: Lower MIN_PATTERN_CONFIDENCE or wait for more commits

**Problem**: All patterns invalidated
- **Cause**: Repository practices changed significantly
- **Solution**: Review and update base patterns, consider full reanalysis

**Problem**: Learning velocity too high
- **Cause**: Unstable patterns or threshold too low
- **Solution**: Increase MIN_PATTERN_CONFIDENCE or extend validation window

## Future Enhancements

Potential improvements:

- [ ] Machine learning models for pattern prediction
- [ ] Cross-repository learning (learn from similar projects)
- [ ] Personalized recommendations per agent
- [ ] Visual dashboards for pattern evolution
- [ ] Automated threshold tuning based on repository characteristics
- [ ] Integration with PR review comments
- [ ] Seasonal pattern detection (e.g., release cycles)

## Credits

**System Design & Implementation**: @create-guru  
**Inspiration**: Nikola Tesla's visionary approach to innovation  
**Philosophy**: Infrastructure that learns and evolves autonomously  
**Integration**: Builds on @workflows-tech-lead's base learning system

---

**Version**: 2.0.0  
**Status**: ✅ Active and operational  
**Last Updated**: 2025-11-26  
**Maintainer**: @create-guru
