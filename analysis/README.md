# Code Analysis Data

This directory contains data from multiple self-improving analyzers that learn from repository history.

## Files

### Archaeology & Learning
- **archaeology.json**: Main archaeology database tracking decisions and technical debt from git history
- **archaeology-patterns.json**: **NEW** Active learning patterns database with success/failure patterns and predictions
- **archaeology_*.json**: Timestamped archaeology analysis snapshots
- **archaeology_learning_*.md**: Human-readable learning reports with insights and recommendations

### Pattern Matching
- **patterns.json**: The learning database that tracks good and bad code patterns discovered over time
- **merge_*.json**: Individual analysis reports for each merge, containing detailed metrics and findings

## How It Works

### Code Archaeology with Active Learning

The enhanced archaeology system runs automatically and:

1. **Documents** legacy decisions and architectural evolution from git history
2. **Learns** patterns from successful and failed commits
3. **Predicts** outcomes based on learned patterns
4. **Recommends** proactive actions to improve code quality

See `docs/archaeology-learner.md` for detailed documentation.

### Pattern Matching

The code analyzer runs automatically on each merge and:

1. **Analyzes** the merged code for patterns, complexity, and quality metrics
2. **Compares** findings against historical pattern database
3. **Learns** by updating pattern correlations based on merge outcomes
4. **Reports** findings and suggestions for future improvements

## Active Learning Features (NEW)

The archaeology system now includes:

### 1. Pattern Learning System
- **Success Patterns**: Commits that worked well (e.g., refactorings with tests)
- **Failure Patterns**: Commits that needed fixes (e.g., large changes without tests)
- **Evolution Patterns**: File change frequency and maintenance needs

### 2. Predictive Insights
- Risk assessment for proposed changes
- Success probability calculations
- Confidence scores and reasoning
- Historical pattern matching

### 3. Proactive Recommendations
- High/medium/low priority actions
- Evidence-based suggestions
- Specific implementation guidance
- Links to supporting patterns

### 4. Living Knowledge Base
All patterns stored in `archaeology-patterns.json`:
```json
{
  "patterns": {
    "success": [...],
    "failure": [...],
    "evolution": [...]
  },
  "insights": [...],
  "recommendations": [...],
  "statistics": {
    "total_patterns": 150,
    "prediction_accuracy": 0.85
  }
}
```

## Pattern Learning

### Good Patterns (Code Quality)
Patterns that correlate with successful merges (no issues, no reverts):
- Descriptive variable names
- Comprehensive docstrings
- Error handling
- Modular functions
- Type hints

### Success Patterns (Git History)
Commits that lead to stable code:
- Refactorings with tests
- Incremental feature additions
- Well-documented changes
- Small, focused commits

### Bad Patterns (Code Quality)
Patterns that correlate with issues or problems:
- Long functions (>50 lines)
- Deep nesting (>4 levels)
- Magic numbers
- Unused imports
- Inconsistent naming conventions

### Failure Patterns (Git History)
Commits that often need fixes:
- Large changes without tests
- Quick fixes without documentation
- Missing error handling
- Undocumented architectural changes

## Metrics Tracked

### Code Quality Metrics
- Code complexity (cyclomatic complexity)
- Function length
- Nesting depth
- Comment density
- Import usage
- Naming conventions
- Error handling coverage
- Test coverage patterns

### Historical Metrics (NEW)
- Commit success/failure rates
- File change frequency
- Time between related changes
- Fix turnaround time
- Pattern correlation scores
- Prediction accuracy

## Self-Improvement

### Pattern Matcher
The analyzer improves over time by:
1. Tracking which patterns appear in problematic vs. successful merges
2. Updating correlation scores after each merge
3. Weighting patterns based on historical data
4. Suggesting improvements based on learned patterns

### Archaeology Learner (NEW)
The learner improves by:
1. Analyzing more commit history over time
2. Identifying new patterns as they emerge
3. Updating prediction models with new data
4. Validating recommendations against outcomes
5. Adjusting confidence scores based on accuracy

## Usage

### Run Full Analysis with Learning
```bash
python3 tools/code-archaeologist.py --learn -n 200
```

### Run Learning Only
```bash
python3 tools/archaeology-learner.py -n 200 -o report.md
```

### View Patterns
```bash
cat analysis/archaeology-patterns.json | jq '.patterns.success[:5]'
```

### View Recommendations
```bash
cat analysis/archaeology-patterns.json | jq '.recommendations'
```

## Automation

GitHub Actions workflows automatically:
- Run archaeology weekly with active learning
- Generate insights and recommendations
- Create issues with findings
- Commit updated databases
- Track prediction accuracy

See `.github/workflows/code-archaeologist.yml` for details.
