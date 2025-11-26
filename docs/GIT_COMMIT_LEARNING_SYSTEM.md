# Git Commit Strategy Learning System

**Created by @create-guru** - Infrastructure for continuous learning and improvement of git commit practices

## 🎯 Overview

The Git Commit Strategy Learning System is an autonomous infrastructure that analyzes repository commit history, learns optimal commit patterns from successful merges, and generates actionable recommendations to improve code quality and merge success rates.

## 🌟 Key Features

### 1. **Continuous Learning**
- Analyzes commits after every merge to `main`
- Daily scheduled analysis of recent commit history
- Adapts recommendations based on evolving patterns

### 2. **Comprehensive Pattern Analysis**
- **Message Quality**: Conventional commit format, descriptiveness, clarity
- **Commit Size**: Files changed, lines modified, optimal sizing
- **Organization**: File grouping, logical cohesion, separation of concerns
- **Timing**: Peak activity hours, merge time correlation

### 3. **Actionable Recommendations**
- Priority-based recommendations (CRITICAL, HIGH, MEDIUM, LOW)
- Specific action items for each recommendation
- Confidence scores based on data analysis
- Context-aware guidance

### 4. **Integration with Chained Ecosystem**
- Compatible with existing learning infrastructure
- Integrates with agent performance tracking
- Feeds into autonomous decision-making systems
- Generates timestamped learning files

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   Git Repository History               │
│   (Commits, Merges, PRs)               │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   CommitStrategyLearner                 │
│   - Extract metrics                     │
│   - Analyze patterns                    │
│   - Calculate success rates             │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   Pattern Database                      │
│   analysis/commit_patterns.json         │
│   - Message patterns                    │
│   - Size patterns                       │
│   - Organization patterns               │
│   - Success metrics                     │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   Recommendation Engine                 │
│   - Generate insights                   │
│   - Prioritize actions                  │
│   - Create guidance                     │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   Learning Files                        │
│   learnings/commit_strategies_*.json    │
│   - Timestamped insights                │
│   - Actionable recommendations          │
│   - Metadata for tracking               │
└─────────────────────────────────────────┘
```

## 📋 Components

### 1. Workflow: `learn-commit-strategies.yml`
- **Location**: `.github/workflows/learn-commit-strategies.yml`
- **Triggers**: 
  - Daily at 02:00 UTC (scheduled)
  - After PR merge to main (event-driven)
  - Manual dispatch (on-demand)
- **Permissions**: `contents: write`, `issues: write`, `pull-requests: write`

### 2. Analysis Tool: `commit-strategy-learner.py`
- **Location**: `tools/commit-strategy-learner.py`
- **Purpose**: Core analysis engine
- **Features**:
  - Commit metrics extraction
  - Pattern identification
  - Success correlation
  - Recommendation generation

### 3. Output Files

#### Pattern Database
- **File**: `analysis/commit_patterns.json`
- **Contents**: 
  - Message patterns (conventional formats, prefixes)
  - Size patterns (average files, lines, optimal ranges)
  - Organization patterns (directory frequency, file types)
  - Timing patterns (peak hours, merge times)

#### Learning Files
- **Pattern**: `learnings/commit_strategies_YYYYMMDD_HHMMSS.json`
- **Contents**:
  - Analysis summary
  - Identified patterns
  - Extracted insights
  - Prioritized recommendations
  - Metadata and attribution

## 🚀 Usage

### Manual Execution

Run analysis for last 30 days:
```bash
# Via GitHub Actions UI
# Navigate to: Actions → Learning: Git Commit Strategies → Run workflow
```

Run analysis for custom time period:
```bash
# In workflow dispatch UI:
# - days_to_analyze: 60
# - branch: main
```

### Programmatic Usage

```python
from tools.commit_strategy_learner import CommitStrategyLearner

# Initialize learner
learner = CommitStrategyLearner(
    repo_path='.',
    verbose=True
)

# Analyze commits
summary = learner.analyze_commits(
    since_days=30,
    max_commits=500
)

# Generate recommendations
recommendations = learner.generate_recommendations(
    context='feature',  # or 'bugfix', 'refactor', 'docs'
    min_confidence=0.7
)
```

## 📊 Example Output

### Learning File Structure

```json
{
  "timestamp": "2025-11-26T12:00:00+00:00",
  "source": "Git Commit Analysis",
  "branch": "main",
  "days_analyzed": 30,
  "summary": {
    "total_analyzed": 500,
    "successful": 500,
    "failed": 0,
    "patterns_found": 3
  },
  "patterns": {
    "message_patterns": {...},
    "size_patterns": {...},
    "organization_patterns": {...},
    "timing_patterns": {...}
  },
  "recommendations": [
    {
      "priority": "CRITICAL",
      "title": "Maintain Message Quality Standards",
      "description": "Continue using conventional commit format...",
      "action_items": [
        "Document commit message templates",
        "Consider commit message linters",
        "Share examples of excellent messages"
      ],
      "based_on": "message_patterns analysis"
    }
  ],
  "_metadata": {
    "created_by": "@create-guru",
    "workflow": "learn-commit-strategies.yml",
    "enhanced_recommendations": true
  }
}
```

### Recommendation Priorities

- **CRITICAL**: Essential practices with high impact on merge success
- **HIGH**: Important patterns that significantly improve code quality
- **MEDIUM**: Beneficial practices that enhance reviewability
- **LOW**: Optional optimizations for workflow efficiency

## 🔄 Continuous Learning Loop

```
1. Developer commits code
   ↓
2. PR created and reviewed
   ↓
3. PR merged to main
   ↓
4. Workflow triggers automatically
   ↓
5. System analyzes new commits
   ↓
6. Patterns updated in database
   ↓
7. Recommendations generated
   ↓
8. Learning file created
   ↓
9. PR with updates (or issue if no changes)
   ↓
10. Insights available for agents
```

## 🎓 Learning Insights

The system identifies and tracks:

### Message Quality
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- **Descriptiveness**: Message length, body presence, clarity
- **Consistency**: Format adherence across the team

### Commit Size
- **Optimal Range**: 2-7 files, 20-150 lines
- **Focused Changes**: Single logical change per commit
- **Reviewability**: Maintainable size for effective review

### Organization
- **File Grouping**: Related files changed together
- **Separation**: Avoiding mixed concerns
- **Directory Patterns**: Frequently modified areas

### Success Correlation
- **Merge Rate**: Pattern correlation with successful merges
- **Review Time**: Patterns that speed up review process
- **CI Success**: Patterns associated with passing tests

## 🔧 Configuration

### Workflow Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days_to_analyze` | number | 30 | Days of history to analyze |
| `branch` | string | main | Branch to analyze |

### Analysis Parameters

Configured in `commit-strategy-learner.py`:
- `MIN_MESSAGE_LENGTH`: 10 characters
- `IDEAL_FILES_PER_COMMIT`: 5 files
- `IDEAL_LINES_CHANGED`: 100 lines
- `MAX_COMMITS`: 500 commits per analysis

## 📈 Integration Points

### Agent System
Agents can query learned strategies to improve their commit practices:
```python
# Load latest strategies
with open('learnings/commit_strategies.json', 'r') as f:
    strategies = json.load(f)

# Get recommendations for context
recommendations = [
    r for r in strategies.get('recommendations', [])
    if r['priority'] in ['CRITICAL', 'HIGH']
]
```

### Code Review
Integrate checks into PR review process:
```python
from commit_strategy_learner import CommitStrategyLearner

learner = CommitStrategyLearner()
# Validate PR commits against learned patterns
```

### Agent Evaluation
Include commit quality in agent scoring:
```python
# Bonus points for following learned patterns
if commit_follows_patterns(commit, learned_strategies):
    agent_score += 0.1
```

## 📊 Metrics & Tracking

The system tracks:
- Total commits analyzed
- Success rates by pattern type
- Recommendation adoption
- Pattern evolution over time
- Confidence scores for insights

## 🛡️ Quality Assurance

### Testing
Comprehensive test suite: `tools/test_commit_strategy_learner.py`
- 21 test cases covering all core functionality
- Pattern identification validation
- Recommendation generation testing
- Database persistence verification

### Error Handling
- Graceful failure on analysis errors
- Logging of all operations
- Safe file operations (atomic writes)
- Input validation

## 🔮 Future Enhancements

Planned improvements:
1. **Real-time Feedback**: Pre-commit hooks with recommendations
2. **ML Pattern Recognition**: Advanced pattern detection algorithms
3. **Multi-repo Learning**: Cross-repository insights
4. **Agent-specific Tracking**: Per-agent commit quality metrics
5. **Interactive Dashboard**: Visualization of patterns and trends
6. **Custom Pattern Definition**: User-defined success criteria

## 📚 Documentation

Related documentation:
- `tools/COMMIT_STRATEGY_LEARNER_README.md` - Tool documentation
- `tools/COMMIT_STRATEGY_INTEGRATION.md` - Integration guide
- `tools/test_commit_strategy_learner.py` - Test suite

## 🎯 Success Criteria

The system is successful when:
- ✅ Commits follow learned patterns
- ✅ Merge success rate increases
- ✅ Code review time decreases
- ✅ Team consistency improves
- ✅ Quality metrics rise

## 🙏 Credits

**Infrastructure by @create-guru**
- Visionary design inspired by Nikola Tesla
- Focus on elegant, scalable solutions
- Autonomous learning capabilities
- Integration with Chained ecosystem

Part of the Chained autonomous AI project.

## 📄 License

Part of the Chained project. See main repository LICENSE.

---

*"The present is theirs; the future, for which I really worked, is mine." - Nikola Tesla*

**@create-guru** - Building infrastructure that learns and evolves
