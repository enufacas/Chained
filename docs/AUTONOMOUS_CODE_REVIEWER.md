# Autonomous Code Reviewer System

**@create-botter** has implemented a self-improving code review system that learns from PR outcomes to continuously evolve its review criteria.

## Overview

The Autonomous Code Reviewer is an intelligent code review system that:
- Reviews pull requests automatically
- Learns from successful merges and failed reviews
- Evolves its criteria based on outcomes
- Continuously improves review accuracy over time

## Architecture

### Core Components

1. **Review Criteria System** (`learnings/review_criteria.json`)
   - Dynamic criteria with weights and thresholds
   - Pattern and anti-pattern detection
   - Success rate tracking for each criterion

2. **Review Tool** (`tools/autonomous-code-reviewer.py`)
   - Code analysis engine
   - Criteria-based evaluation
   - Learning and adaptation mechanism
   - Performance metrics tracking

3. **GitHub Actions Workflow** (`.github/workflows/autonomous-code-reviewer.yml`)
   - Automatic PR review
   - Learning from outcomes
   - Batch criteria updates
   - Statistics generation

4. **Review History** (`learnings/review_history/`)
   - Review results
   - Outcome tracking
   - Learning feedback

## Features

### 1. Multi-Dimensional Code Quality Assessment

The system evaluates code across five key criteria:

- **Code Complexity** (25% weight): Measures complexity and maintainability
- **Code Style** (15% weight): Checks formatting and style consistency
- **Documentation** (20% weight): Ensures adequate documentation
- **Test Coverage** (20% weight): Validates test presence
- **Security** (20% weight): Identifies security vulnerabilities

### 2. Self-Improving Criteria

The system learns from every PR outcome:

- **False Positive Detection**: Tightens thresholds when good PRs fail review
- **False Negative Detection**: Loosens thresholds when bad PRs pass review
- **Weight Adjustment**: Increases weight of predictive criteria
- **Pattern Evolution**: Updates pattern matching based on outcomes

### 3. Adaptive Learning

The reviewer adapts in multiple ways:

- **Real-time Learning**: Updates after each PR outcome
- **Batch Updates**: Comprehensive updates from historical data
- **Success Rate Tracking**: Monitors accuracy for each criterion
- **Weight Normalization**: Keeps criteria weights balanced

### 4. Performance Metrics

The system tracks:

- Total reviews performed
- Outcome distribution (merged, rejected, revised, abandoned)
- Criterion accuracy rates
- Prediction success rates
- False positive/negative rates

## Usage

### Command Line Interface

```bash
# Review a pull request
python3 tools/autonomous-code-reviewer.py --review PR_NUMBER

# Learn from PR outcome
python3 tools/autonomous-code-reviewer.py --learn-from-outcome PR_NUMBER --outcome merged

# Batch update criteria from history
python3 tools/autonomous-code-reviewer.py --update-criteria

# Show statistics
python3 tools/autonomous-code-reviewer.py --show-stats
```

### GitHub Actions Integration

The workflow automatically:
- Reviews PRs when opened or updated
- Posts review comments with scores and suggestions
- Learns from PR outcomes when PRs are closed
- Updates criteria via PRs
- Can be manually triggered for stats or batch updates

### Manual Workflow Dispatch

```yaml
# Review specific PR
action: review
pr_number: 123

# Update criteria
action: update-criteria

# Show statistics
action: show-stats
```

## How It Works

### Review Process

1. **Code Analysis**: Extract code from PR diff
2. **Pattern Matching**: Check against patterns and anti-patterns
3. **Scoring**: Calculate weighted score for each criterion
4. **Overall Assessment**: Compute weighted overall score
5. **Pass/Fail**: Compare against threshold
6. **Feedback**: Generate issues and suggestions

### Learning Process

1. **Outcome Recording**: Track PR outcome (merged/rejected/etc.)
2. **Accuracy Analysis**: Compare prediction vs. actual outcome
3. **Criteria Update**:
   - Adjust weights based on predictive power
   - Tighten thresholds for false positives
   - Loosen thresholds for false negatives
4. **Persistence**: Save updated criteria
5. **Continuous Improvement**: Apply learning to future reviews

### Evolution Mechanism

```
Initial Review → PR Outcome → Accuracy Analysis → Criteria Update → Improved Review
     ↑                                                                      ↓
     └──────────────────────── Feedback Loop ───────────────────────────────┘
```

## Data Storage

### Review Criteria

**Location**: `learnings/review_criteria.json`

```json
{
  "version": "1.0.0",
  "last_updated": "2024-11-25T20:00:00Z",
  "criteria": [
    {
      "name": "code_complexity",
      "description": "Measures code complexity",
      "weight": 0.25,
      "threshold": 0.6,
      "patterns": ["..."],
      "anti_patterns": ["..."],
      "success_rate": 0.85,
      "total_evaluations": 42
    }
  ]
}
```

### Review History

**Location**: `learnings/review_history/`

- `review_{pr_number}_{timestamp}.json` - Review results
- `outcome_{pr_number}_{timestamp}.json` - Outcome tracking

## Integration with Existing Systems

### Works With

- **PR Failure Learning**: Complements the PR failure learning system
- **Tech Lead Review**: Provides preliminary assessment before tech lead review
- **Agent System**: Can be invoked by agents for code quality checks
- **Meta-Coordinator**: Integrates with the autonomous coordination system

### Does Not Conflict With

- **Gemini Review**: Operates independently, provides different perspective
- **Auto-Review-Merge**: Works alongside existing merge workflows
- **Manual Reviews**: Augments, doesn't replace human review

## Performance Expectations

### Review Accuracy

- **Initial Accuracy**: ~70% (with default criteria)
- **After 10 PRs**: ~75-80%
- **After 50 PRs**: ~85%+
- **Long-term**: Continues improving with more data

### Resource Usage

- **Review Time**: < 5 seconds per PR
- **Storage**: ~10KB per review
- **Learning Time**: < 1 second per outcome

## Future Enhancements

Potential improvements for **@create-botter** or other agents:

1. **Enhanced Pattern Recognition**
   - Machine learning for pattern detection
   - Language-specific rules
   - Framework-specific patterns

2. **Context Awareness**
   - Repository-specific criteria
   - File type specialization
   - Historical context integration

3. **Advanced Learning**
   - Multi-PR pattern detection
   - Temporal trend analysis
   - Cross-repository learning

4. **Integration Expansion**
   - Direct GitHub API integration
   - Static analysis tool integration
   - CI/CD pipeline hooks

5. **Visualization**
   - Review statistics dashboard
   - Criteria evolution graphs
   - Accuracy tracking charts

## Troubleshooting

### Common Issues

**Issue**: Reviews not being performed
- **Solution**: Check workflow permissions
- **Solution**: Verify PR is not in draft mode
- **Solution**: Check paths-ignore filters

**Issue**: Learning not working
- **Solution**: Ensure review exists for PR
- **Solution**: Check review_history directory permissions
- **Solution**: Verify outcome parameter is valid

**Issue**: Criteria not evolving
- **Solution**: Need minimum 5 outcomes for batch update
- **Solution**: Check that learning PRs are being merged
- **Solution**: Verify criteria file is not read-only

## Testing

Comprehensive test suite included:

```bash
python3 tests/test_autonomous_code_reviewer.py
```

Tests cover:
- Initialization and persistence
- Review execution
- Pattern detection
- Learning from outcomes
- Criteria evolution
- Weight normalization
- Statistics generation

## Credits

**Designed and implemented by:** @create-botter (Infrastructure creation specialist)
**Inspired by:** Nikola Tesla's visionary approach to innovation
**Part of:** Chained Autonomous AI Ecosystem

---

*"The present is theirs; the future, for which I really worked, is mine." - Nikola Tesla*

This system embodies the forward-thinking spirit of continuous improvement and autonomous evolution.
