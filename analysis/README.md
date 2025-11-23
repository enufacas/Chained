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

### Universal Truths 🌌 (NEW)
- **universal_truths_insights.json**: Discovered fundamental principles governing the AI ecosystem
- **universal_truths_investigation_*.md**: Deep analysis reports by @investigate-champion
- **universal_truths_action_items.md**: Actionable recommendations derived from truths
- **universal_truths_quickref.md**: Quick reference guide with key metrics and insights

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

## Universal Truths System

### What Are Universal Truths?

The Universal Truth Evaluator discovers fundamental principles that govern the autonomous AI ecosystem by analyzing:
- Agent behavior patterns from world state
- Learning accumulation rates
- Collaboration dynamics
- System-wide patterns and archaeology

Each truth is validated through empirical evidence and repeated observation.

### Current Truths (8 Discovered)

**High Confidence (>0.8)**:
1. **Specialization Diversity (0.90)**: 23 specializations across 43 agents (ratio: 0.53)
2. **Performance Distribution (0.85)**: 55.8% high performers, natural bell curve
3. **Learning Velocity (0.85)**: Consistent 48 learnings/week

**Medium-High Confidence (0.7-0.8)**:
4. **Knowledge Interconnectedness (0.80)**: 4.0 connections per insight
5. **Agent Status Equilibrium (0.70)**: 100% exploring status
6. **Action Patterns (0.70)**: 8 persistent patterns
7. **Archaeology Patterns (0.70)**: 8 distinct patterns
8. **Emergent Creativity (0.70)**: Novel combinations emerging

### Key Insights

- **System Maturity**: All truths are stable with 2-19 evidence points
- **Interconnection**: 7 of 8 truths are interconnected (network density: medium)
- **Self-Organization**: System demonstrates sophisticated emergent behavior
- **Core Properties**: Diversity (0.53 ratio) and learning (48/week) are fundamental

### Investigation Reports

**@investigate-champion** has conducted deep analysis:
- **Full Report**: `universal_truths_investigation_2025-11-23.md` (394 lines)
- **Action Items**: `universal_truths_action_items.md` (8 prioritized recommendations)
- **Quick Reference**: `universal_truths_quickref.md` (summary with metrics)

### Actionable Recommendations

1. **Protect Diversity**: Monitor 0.45-0.65 ratio, alert on violations
2. **Create Dashboard**: Real-time metrics for all 8 truths
3. **Optimize Assignment**: Match agents to issues by performance tier
4. **Document Patterns**: Analyze and document the 8 action patterns
5. **Enhance Knowledge**: Maintain 4.0+ connections per insight

See `universal_truths_action_items.md` for full details.

## Automation

GitHub Actions workflows automatically:
- Run archaeology weekly with active learning
- Generate insights and recommendations
- Create issues with findings
- Commit updated databases
- Track prediction accuracy
- **Discover universal truths daily** (6 AM UTC)
- Generate truth insights and recommendations
- Create discovery issues with findings

See `.github/workflows/code-archaeologist.yml` and `.github/workflows/discover-universal-truths.yml` for details.
