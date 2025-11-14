# Commit Strategy Learning System - Integration Guide

## Overview

This guide explains how to integrate the Git Commit Strategy Learning System into the Chained autonomous workflow ecosystem.

## Integration Points

### 1. Post-Merge Analysis

After a PR is successfully merged, automatically analyze the commit patterns:

```yaml
# .github/workflows/learn-from-merge.yml (example)
name: Learn From Merge
on:
  pull_request:
    types: [closed]

jobs:
  learn-commit-strategy:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for analysis
      
      - name: Analyze commit patterns
        run: |
          python tools/commit-strategy-learner.py --analyze --verbose
      
      - name: Generate recommendations
        run: |
          python tools/commit-strategy-learner.py --recommend --context general
```

### 2. Pre-Commit Validation

Provide commit recommendations before agents create PRs:

```python
# In agent workflow scripts
from commit_strategy_learner import CommitStrategyLearner

learner = CommitStrategyLearner(verbose=True)
recommendations = learner.generate_recommendations(
    context="feature",  # or "bugfix", "refactor", etc.
    min_confidence=0.8
)

# Share recommendations with agent
for rec in recommendations:
    print(f"💡 {rec.title}")
    print(f"   {rec.description}")
    print(f"   Confidence: {rec.confidence_score:.0%}")
```

### 3. Agent Performance Enhancement

Integrate with agent evaluation system:

```python
# In agent-evaluator workflow
learner = CommitStrategyLearner()

# Get agent-specific commit patterns
agent_commits = get_commits_by_agent(agent_id)

# Analyze if agent follows best practices
for commit in agent_commits:
    metrics = learner._get_commit_metrics(commit.hash)
    if metrics.follows_conventional:
        bonus_points += 0.1
```

### 4. Daily Learning Report

Generate daily insights for the system:

```yaml
# .github/workflows/daily-commit-insights.yml (example)
name: Daily Commit Insights
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  generate-insights:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Analyze recent commits
        run: |
          python tools/commit-strategy-learner.py --analyze --since 7
      
      - name: Generate report
        run: |
          python tools/commit-strategy-learner.py --report \
            --output analysis/weekly_commit_insights.md
      
      - name: Commit report
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add analysis/weekly_commit_insights.md
          git commit -m "chore: update weekly commit insights"
          git push
```

### 5. PR Review Automation

Add commit quality checks to PR reviews:

```python
# In auto-review-merge workflow
learner = CommitStrategyLearner()

# Analyze PR commits
pr_commits = get_pr_commits(pr_number)
issues = []

for commit in pr_commits:
    metrics = learner._get_commit_metrics(commit.sha)
    
    # Check message quality
    if not metrics.follows_conventional:
        issues.append(f"Commit {commit.sha[:7]} doesn't follow conventional format")
    
    # Check commit size
    if metrics.files_changed > 15:
        issues.append(f"Commit {commit.sha[:7]} changes too many files ({metrics.files_changed})")
    
    # Check message length
    if metrics.message_length < 10:
        issues.append(f"Commit {commit.sha[:7]} has too short message")

# Add review comments if issues found
if issues:
    add_review_comment("### Commit Quality Issues\n\n" + "\n".join(f"- {i}" for i in issues))
```

## Data Flow

```
┌─────────────────┐
│   Git Commits   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  CommitMetrics          │
│  Extraction             │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Pattern                │
│  Analysis               │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Learning Database      │
│  (JSON Files)           │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Recommendations        │
│  Generation             │
└────────┬────────────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│  Agent System   │  │  PR Reviews     │
└─────────────────┘  └─────────────────┘
```

## Database Schema

### commit_strategies.json
```json
{
  "version": "1.0.0",
  "last_updated": "2025-11-14T00:00:00Z",
  "repository": "Chained",
  "total_commits_analyzed": 500,
  "successful_merges": 425,
  "failed_merges": 75,
  "patterns_identified": [
    {
      "pattern_name": "conventional_commits",
      "pattern_type": "message",
      "success_rate": 0.85,
      "confidence_score": 0.9
    }
  ],
  "recommendations": [...]
}
```

### commit_patterns.json
```json
{
  "version": "1.0.0",
  "message_patterns": {
    "conventional_commits": {
      "success_rate": 0.85,
      "occurrence_count": 425
    }
  },
  "size_patterns": {...},
  "organization_patterns": {...},
  "success_metrics": {
    "total_commits": 500,
    "successful_commits": 425
  }
}
```

## API Reference

### CommitStrategyLearner

```python
learner = CommitStrategyLearner(
    repo_path=".",      # Repository path
    verbose=False       # Enable logging
)
```

#### Methods

##### analyze_commits()
```python
result = learner.analyze_commits(
    since_days=30,      # Days of history
    max_commits=500     # Max commits to analyze
)
# Returns: {"total_analyzed": int, "successful": int, "failed": int, "patterns_found": int}
```

##### generate_recommendations()
```python
recommendations = learner.generate_recommendations(
    context="general",      # Context: general, feature, bugfix, refactor, docs
    min_confidence=0.7      # Minimum confidence threshold
)
# Returns: List[StrategyRecommendation]
```

##### generate_report()
```python
report_text = learner.generate_report(
    output_file="analysis/report.md"  # Optional output file
)
# Returns: str (markdown report)
```

## Best Practices

### 1. Regular Analysis
Run analysis after each merge to keep the learning current:
```bash
python tools/commit-strategy-learner.py --analyze --since 1
```

### 2. Context-Specific Recommendations
Use appropriate context for different work types:
- Use `feature` context for new features
- Use `bugfix` context for bug fixes
- Use `refactor` context for code improvements
- Use `docs` context for documentation

### 3. Confidence Thresholds
- Use 0.9+ for strict requirements
- Use 0.7+ for general guidance
- Use 0.5+ for experimental insights

### 4. Incremental Learning
The system improves over time. Initial recommendations may be limited, but will become more accurate as more commits are analyzed.

## Monitoring

Track system health:

```bash
# Check database sizes
ls -lh learnings/commit_strategies.json
ls -lh analysis/commit_patterns.json

# View latest recommendations
python tools/commit-strategy-learner.py --recommend | head -20

# Generate status report
python tools/commit-strategy-learner.py --report
```

## Troubleshooting

### No Patterns Found
- Ensure sufficient commit history (analyze at least 30 days)
- Check that commits have proper metadata
- Verify git repository is valid

### Low Confidence Scores
- Increase analysis period (--since)
- Ensure diverse commit types in history
- Wait for more data to accumulate

### Performance Issues
- Limit max_commits for large repositories
- Use shorter time periods (--since)
- Run during off-peak hours

## Future Enhancements

Planned improvements:
1. GitHub API integration for PR data
2. Real-time merge outcome tracking
3. Multi-repository learning
4. Agent-specific pattern tracking
5. Machine learning pattern recognition
6. Temporal pattern analysis
7. Custom pattern definitions

## Contributing

When extending the system:
1. Follow the existing code structure
2. Add comprehensive tests
3. Update documentation
4. Maintain type hints
5. Follow @engineer-master's quality standards

---

*Integration guide by **@engineer-master** - Systematic, thorough, production-ready.*
