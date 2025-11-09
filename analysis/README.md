# Code Analysis Data

This directory contains data from the self-improving code analyzer that learns from each merge.

## Files

- **patterns.json**: The learning database that tracks good and bad code patterns discovered over time
- **merge_*.json**: Individual analysis reports for each merge, containing detailed metrics and findings

## How It Works

The code analyzer runs automatically on each merge and:

1. **Analyzes** the merged code for patterns, complexity, and quality metrics
2. **Compares** findings against historical pattern database
3. **Learns** by updating pattern correlations based on merge outcomes
4. **Reports** findings and suggestions for future improvements

## Pattern Learning

### Good Patterns
Patterns that correlate with successful merges (no issues, no reverts):
- Descriptive variable names
- Comprehensive docstrings
- Error handling
- Modular functions
- Type hints

### Bad Patterns
Patterns that correlate with issues or problems:
- Long functions (>50 lines)
- Deep nesting (>4 levels)
- Magic numbers
- Unused imports
- Inconsistent naming conventions

## Metrics Tracked

- Code complexity (cyclomatic complexity)
- Function length
- Nesting depth
- Comment density
- Import usage
- Naming conventions
- Error handling coverage
- Test coverage patterns

## Self-Improvement

The analyzer improves over time by:
1. Tracking which patterns appear in problematic vs. successful merges
2. Updating correlation scores after each merge
3. Weighting patterns based on historical data
4. Suggesting improvements based on learned patterns
