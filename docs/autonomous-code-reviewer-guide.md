# 🤖 Autonomous Code Reviewer - User Guide

**Enhanced by @construct-specialist**

## Overview

The Autonomous Code Reviewer is a self-improving system that learns from PR outcomes to continuously enhance its review criteria. It provides automated code quality assessments with confidence scoring and adaptive learning.

## Features

### 🎯 Core Capabilities

1. **Multi-Dimensional Quality Assessment**
   - Code complexity and maintainability
   - Code style and formatting
   - Documentation quality
   - Test coverage
   - Security considerations

2. **Self-Improving Learning**
   - Adapts criteria weights based on outcomes
   - Adjusts thresholds from false positives/negatives
   - Increases accuracy with more data

3. **Confidence Scoring**
   - Tracks prediction reliability
   - Adjusts review strictness based on confidence
   - Shows learning progress

4. **GitHub Integration**
   - Fetches real PR data (files, diffs, metadata)
   - Posts automated review comments
   - Learns from merged/rejected PRs

## How It Works

### Review Process

```mermaid
graph LR
    A[PR Created] --> B[Fetch PR Data]
    B --> C[Evaluate Criteria]
    C --> D[Calculate Score]
    D --> E[Post Review Comment]
    E --> F[PR Closed]
    F --> G[Learn from Outcome]
    G --> H[Update Criteria]
```

### Learning Cycle

1. **Review**: Evaluate PR against current criteria
2. **Outcome**: Track whether PR was merged/rejected
3. **Analyze**: Calculate prediction accuracy
4. **Adapt**: Adjust weights and thresholds
5. **Improve**: Better predictions in future reviews

## Usage

### Automatic Reviews

The system automatically reviews PRs via GitHub Actions workflow:

```yaml
# Triggered on PR events
on:
  pull_request:
    types: [opened, synchronize, ready_for_review]
```

### Manual Review

Review a specific PR:

```bash
python3 tools/autonomous-code-reviewer.py --review PR_NUMBER --verbose
```

### View Statistics

Check system performance:

```bash
python3 tools/autonomous-code-reviewer.py --show-stats
```

### Visualize Learning

Generate learning progress report:

```bash
python3 tools/visualize-reviewer-learning.py
cat reviewer-learning-progress.md
```

### Batch Criteria Update

Update criteria from historical data:

```bash
python3 tools/autonomous-code-reviewer.py --update-criteria --verbose
```

## Understanding Review Results

### Review Comment Format

```markdown
## ✅ Autonomous Code Review

**Status:** PASSED
**Overall Score:** 82.5%
**Confidence:** 🎯 73.2% (High confidence)

### Review Summary
Issues Found: 2
[List of suggestions]

### About This Review
[Explanation of criteria]
```

### Score Interpretation

| Score Range | Meaning | Action |
|-------------|---------|--------|
| 90-100% | Excellent | Ready to merge |
| 80-89% | Good | Minor improvements suggested |
| 70-79% | Acceptable | Review suggestions |
| 60-69% | Needs Work | Address issues before merging |
| < 60% | Significant Issues | Major improvements needed |

### Confidence Levels

| Confidence | Indicator | Meaning |
|------------|-----------|---------|
| > 70% | 🎯 High | System has proven accuracy |
| 50-70% | 📊 Moderate | System is learning |
| < 50% | 🔍 Low | Needs more data |

## Configuration

### Criteria File Location

```
learnings/review_criteria.json
```

### Criteria Structure

```json
{
  "version": "1.0.0",
  "last_updated": "2025-12-24T20:00:00Z",
  "criteria": [
    {
      "name": "code_complexity",
      "weight": 0.25,
      "threshold": 0.6,
      "success_rate": 0.75,
      "patterns": [...],
      "anti_patterns": [...]
    }
  ]
}
```

### Adjusting Criteria

Criteria automatically adapt, but you can manually adjust:

1. Edit `learnings/review_criteria.json`
2. Adjust weights (must sum to 1.0)
3. Adjust thresholds (0.0 to 1.0)
4. Add/remove patterns

⚠️ **Warning**: Manual edits will be overwritten by learning algorithm unless you disable auto-learning.

## Advanced Features

### Adaptive Learning Rate

The system adjusts learning speed based on:
- Prediction error magnitude (larger errors = faster learning)
- Amount of historical data (more data = slower, stable learning)
- Convergence (gradually reduces learning rate)

### File-Type Specific Analysis

Enhanced evaluation for:
- **Python files**: Docstrings, PEP 8, type hints
- **Test files**: Coverage, assertion quality, test structure
- **Documentation**: Comment ratio, PR descriptions
- **Security**: Pattern detection for vulnerabilities

### Pattern Matching

Two types of patterns:
1. **Positive patterns**: Good practices to encourage
2. **Anti-patterns**: Bad practices to discourage

## Performance Metrics

### System Health

Check these metrics:
- **Total Reviews**: More data = better accuracy (target: 50+)
- **Average Criterion Accuracy**: Should be > 70%
- **Confidence**: Should increase over time
- **Outcome Distribution**: Should reflect actual PR patterns

### Expected Performance

| Metric | Initial | After 20 Reviews | After 50 Reviews |
|--------|---------|------------------|------------------|
| Confidence | 20-30% | 50-60% | 70-85% |
| Accuracy | 60-70% | 75-80% | 85-90% |
| Learning Rate | High | Moderate | Low (stable) |

## Troubleshooting

### Low Accuracy

**Symptoms**: Frequent incorrect predictions

**Solutions**:
- Check if enough data collected (need 20+ reviews)
- Review outcome labels are correct
- Consider manual pattern adjustment
- Run batch criteria update

### Low Confidence

**Symptoms**: Confidence remains < 50%

**Solutions**:
- Collect more review data
- Ensure varied outcomes (not all merged/rejected)
- Check criteria consistency

### No Learning

**Symptoms**: Criteria don't update

**Solutions**:
- Verify outcome tracking workflow runs
- Check `learnings/review_history/` for outcome files
- Ensure PRs are properly closed
- Run manual learning: `--learn-from-outcome`

## Best Practices

### For System Administrators

1. **Let it learn**: Avoid manual criteria edits initially
2. **Track metrics**: Monitor confidence and accuracy
3. **Provide feedback**: Label outcomes correctly
4. **Be patient**: Needs 50+ reviews for best performance

### For Developers

1. **Read review comments**: Understand suggestions
2. **Address issues**: Even if you disagree, consider feedback
3. **Report errors**: If review seems wrong, investigate
4. **Trust confidence**: High confidence reviews are reliable

## Integration with Existing Systems

### Tech Lead Reviews

Autonomous reviewer complements (not replaces) tech lead reviews:
- Catches common issues automatically
- Frees tech leads for architectural review
- Provides consistency across PRs

### CI/CD Pipeline

Fits into standard pipeline:
```
Code Push → CI Tests → Autonomous Review → Tech Lead Review → Merge
```

### Agent System

Part of the larger agent ecosystem:
- Uses agent performance data
- Contributes to system learning
- Adapts to repository patterns

## Future Enhancements

Planned improvements:
- [ ] A/B testing for criteria changes
- [ ] Real-time learning (incremental updates)
- [ ] Visualization dashboard
- [ ] Custom criteria per file type
- [ ] Integration with code coverage tools
- [ ] Machine learning model integration

## Support

### Documentation

- **Implementation**: `tools/autonomous-code-reviewer.py`
- **Workflow**: `.github/workflows/autonomous-code-reviewer.yml`
- **Tests**: `tests/test_autonomous_code_reviewer.py`

### Getting Help

1. Check visualization: `tools/visualize-reviewer-learning.py`
2. View stats: `--show-stats`
3. Review logs: GitHub Actions workflow logs
4. Open issue: Tag with `autonomous-reviewer`

## Technical Details

### Architecture

```
┌─────────────────┐
│   PR Created    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Fetch PR Data  │ (gh CLI)
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Evaluate Criteria│
│  - Complexity   │
│  - Style        │
│  - Docs         │
│  - Tests        │
│  - Security     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Calculate Score │ (weighted sum)
│ + Confidence    │ (historical data)
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Post Comment   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   PR Closed     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Learn & Adapt   │ (adaptive rate)
│ - Update weights│
│ - Adjust thresh.│
│ - Track accuracy│
└─────────────────┘
```

### Algorithm Details

**Scoring**: Weighted sum of criterion scores
```
overall_score = Σ (criterion_score_i × weight_i)
```

**Confidence**: Based on data amount and accuracy
```
confidence = 0.4 × (reviews/50) + 0.4 × avg_accuracy + 0.2 × consistency
```

**Learning Rate**: Adaptive based on error and history
```
learning_rate = base_rate × (1 + error) × (1 / (1 + history/20))
```

## Credits

**Original Implementation**: @create-botter (Infrastructure)  
**Enhanced by**: @construct-specialist (Adaptive learning, confidence scoring, GitHub integration)  
**Inspired by**: Self-improving systems, reinforcement learning

---

*Built for the Chained autonomous AI ecosystem*
