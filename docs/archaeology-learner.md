# 🧠 Archaeology Learner - Active Learning from Git History

## Overview

The Archaeology Learner is an advanced tool that learns from your repository's git history to identify patterns, predict outcomes, and provide proactive recommendations. It transforms code archaeology from passive documentation into active learning and prediction.

## Features

### 1. Pattern Learning System

The learner analyzes git history to identify three types of patterns:

#### Success Patterns
- Commits that worked well and didn't require follow-up fixes
- Identifies characteristics that lead to stable, maintainable code
- Examples: Refactorings with tests, incremental features, well-documented changes

#### Failure Patterns
- Commits that needed fixes or corrections shortly after
- Learns what to avoid based on historical issues
- Examples: Large changes without tests, quick fixes, undocumented hacks

#### Evolution Patterns
- Tracks how files and components change over time
- Identifies high-churn files that need attention
- Calculates change frequency: very_frequent, frequent, moderate, rare

### 2. Predictive Insights

Based on learned patterns, the system can:

- **Predict Success Probability**: Estimate likelihood a commit will succeed
- **Assess Risk**: Identify characteristics that historically lead to problems
- **Calculate Confidence**: Provide confidence scores for predictions
- **Explain Reasoning**: Show which patterns influenced the prediction

### 3. Proactive Recommendations

The learner generates actionable recommendations:

- **High Priority**: Critical issues requiring immediate attention
- **Medium Priority**: Important improvements to consider
- **Low Priority**: Nice-to-have enhancements

Each recommendation includes:
- Title and description
- Specific action to take
- Evidence from learned patterns

### 4. Living Knowledge Base

All learned patterns are stored in `analysis/archaeology-patterns.json`:

```json
{
  "version": "1.0",
  "last_updated": "2025-11-12T00:00:00Z",
  "patterns": {
    "success": [...],
    "failure": [...],
    "evolution": [...]
  },
  "insights": [...],
  "recommendations": [...],
  "statistics": {
    "total_patterns": 150,
    "prediction_accuracy": 0.85,
    "recommendations_generated": 12
  }
}
```

## Usage

### Basic Usage

Run the learner on your repository:

```bash
python3 tools/archaeology-learner.py -d /path/to/repo
```

### Command-Line Options

```bash
# Analyze last 500 commits
python3 tools/archaeology-learner.py -n 500

# Save report to file
python3 tools/archaeology-learner.py -o learning_report.md

# Show prediction example
python3 tools/archaeology-learner.py --predict

# Specify repository directory
python3 tools/archaeology-learner.py -d /path/to/repo
```

### Integration with Code Archaeologist

Run the full archaeology with learning enabled:

```bash
python3 tools/code-archaeologist.py --learn -n 200
```

This will:
1. Run standard archaeology analysis
2. Learn patterns from git history
3. Generate insights and recommendations
4. Save both reports and pattern database

### Automated Workflow

The GitHub Actions workflow automatically runs with learning enabled:

```yaml
# .github/workflows/code-archaeologist.yml
- name: Run Code Archaeologist with Active Learning
  run: |
    python3 tools/code-archaeologist.py \
      -n 100 \
      --learn \
      -o archaeology_report.md
```

## Pattern Structure

### Success Pattern Example

```json
{
  "pattern_type": "success",
  "commit_hash": "abc123d",
  "timestamp": "2025-11-12T00:00:00Z",
  "subject": "Refactor authentication module",
  "files_changed": 3,
  "file_types": [".py", ".md"],
  "outcome": {
    "success": true,
    "fixes_needed": [],
    "improvements_made": []
  },
  "characteristics": {
    "is_refactor": true,
    "is_feature": false,
    "is_bug_fix": false,
    "has_tests": true,
    "large_change": false,
    "has_documentation": true
  }
}
```

### Evolution Pattern Example

```json
{
  "pattern_type": "file_evolution",
  "file": "src/core.py",
  "changes_count": 15,
  "first_seen": "2024-01-01T00:00:00Z",
  "last_seen": "2025-11-12T00:00:00Z",
  "change_frequency": "very_frequent",
  "common_change_types": ["bug_fix", "refactor", "feature"]
}
```

## Insights Generated

The system automatically generates insights such as:

### Success Rate Insights
- "Refactorings have high success rate"
- "Commits with tests succeed more often"
- Confidence: high/medium/low

### Risk Insights
- "Large changes have higher failure rate"
- "Quick fixes often need follow-up corrections"
- Includes recommendations to mitigate risks

### Maintenance Insights
- "High churn files need attention"
- "Untested code correlates with bugs"
- Lists specific files requiring action

## Recommendations

Example recommendations generated:

### High Priority

**Require tests for all changes**
- Description: Commits with tests have significantly higher success rates
- Action: Add test coverage checks to CI/CD
- Based on: Testing importance insight

### Medium Priority

**Break down large changes**
- Description: Large commits have higher failure rates
- Action: Use feature flags for incremental delivery
- Based on: Change size risk insight

### Preventive Maintenance

**Review high-churn files**
- Description: Files that change frequently may need refactoring
- Action: Create issues for stabilizing identified files
- Based on: File evolution patterns

## Prediction Example

Predict the outcome of a proposed change:

```python
from archaeology_learner import ArchaeologyLearner

learner = ArchaeologyLearner(repo_path=".")
learner.analyze_and_learn(max_commits=200)

# Characteristics of proposed commit
commit_chars = {
    "is_refactor": True,
    "is_feature": False,
    "is_bug_fix": False,
    "has_tests": True,
    "large_change": False,
    "has_documentation": True
}

prediction = learner.predict_outcome(commit_chars)

print(f"Prediction: {prediction['prediction']}")
print(f"Confidence: {prediction['confidence']:.1%}")
print(f"Success probability: {prediction['success_probability']:.1%}")
print(f"Reasoning: {prediction['reasoning']}")
```

Output:
```
Prediction: success
Confidence: 87.5%
Success probability: 87.5%
Reasoning: Based on 45 success and 12 failure patterns
```

## Best Practices

### 1. Regular Updates
Run the learner weekly to keep patterns up-to-date:
```bash
# In CI/CD or scheduled job
python3 tools/archaeology-learner.py -n 200
```

### 2. Sufficient History
Analyze at least 100-200 commits for meaningful patterns:
```bash
python3 tools/archaeology-learner.py -n 200
```

### 3. Act on Recommendations
Review and implement high-priority recommendations:
- Create issues for high-churn files
- Add test coverage requirements
- Refactor problematic patterns

### 4. Track Accuracy
Monitor prediction accuracy over time:
- Check `statistics.prediction_accuracy` in patterns file
- Adjust learning parameters if accuracy drops
- Increase commit history for better learning

### 5. Share Insights
Use learned patterns in:
- PR reviews: Reference similar successful patterns
- Planning: Estimate based on historical timelines
- Onboarding: Share what works and what doesn't

## Integration Points

### In Pull Requests
Show relevant historical patterns:
```
New PR touches authentication code
→ Archaeology shows 3 past auth bugs
→ Highlights common pitfalls
→ Suggests security testing patterns that worked
```

### In Issue Planning
Provide context from history:
```
New feature request for API endpoint
→ Archaeology finds 10 similar past features
→ Shows average completion time: 2 days
→ Lists common challenges to prepare for
```

### In Agent Spawning
Use patterns to create better agents:
```
Agent needed for database refactoring
→ Load success patterns for refactoring
→ Include common pitfalls in agent prompt
→ Reference proven approaches
```

### In Code Reviews
Reference learned patterns:
```
Reviewer: "Large PR without tests"
→ Show failure pattern statistics
→ Reference similar past issues
→ Suggest incremental approach
```

## Troubleshooting

### Low Pattern Count
**Problem**: Few patterns learned from repository

**Solutions**:
- Increase `-n` parameter to analyze more commits
- Ensure commits have descriptive messages
- Check that repository has sufficient history

### Low Prediction Confidence
**Problem**: Predictions have low confidence scores

**Solutions**:
- Analyze more commits to build larger pattern database
- Ensure commit characteristics are well-defined
- Review pattern quality and diversity

### No Recommendations Generated
**Problem**: System doesn't generate recommendations

**Solutions**:
- Verify insights are being generated first
- Check that insights are marked as actionable
- Review recommendation generation logic

## Performance

- Analyzing 200 commits: ~30-60 seconds
- Analyzing 500 commits: ~2-5 minutes
- Pattern database size: ~100KB-1MB depending on patterns
- Memory usage: ~50-100MB during analysis

## Limitations

1. **Requires Commit History**: Needs well-documented commit messages
2. **Pattern Quality**: Depends on historical data quality
3. **False Positives**: May identify coincidental patterns
4. **Context Sensitivity**: Cannot understand all commit context
5. **Language Agnostic**: Treats all code changes similarly

## Future Enhancements

- [ ] Machine learning integration for better predictions
- [ ] Cross-repository pattern learning
- [ ] Real-time prediction API
- [ ] Pattern visualization dashboard
- [ ] Integration with issue tracking
- [ ] Automated PR comments with predictions
- [ ] Team-specific pattern learning
- [ ] Custom pattern definitions

## Contributing

To improve the archaeology learner:

1. Add new pattern extraction logic
2. Enhance insight generation algorithms
3. Create new recommendation types
4. Improve prediction accuracy
5. Add visualization tools

## License

Same as the main Chained project.
