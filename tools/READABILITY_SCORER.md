# Code Readability Scorer

A comprehensive Python code readability analyzer that scores code quality across multiple dimensions and provides actionable improvement suggestions.

## Features

### Multi-Dimensional Analysis

The readability scorer evaluates code across five key categories:

1. **Naming Quality (25%)** - Variable and function naming conventions
   - Descriptive vs. generic names
   - Naming convention compliance (snake_case)
   - Single-character variable usage
   - Name length and clarity

2. **Complexity (25%)** - Code complexity metrics
   - Cyclomatic complexity per function
   - Nesting depth analysis
   - Function length
   - Control flow complexity

3. **Documentation (20%)** - Documentation completeness and quality
   - Module-level docstrings
   - Function and class docstrings
   - Parameter and return documentation
   - Docstring content quality

4. **Formatting (15%)** - Code formatting standards
   - Line length (PEP 8 compliance)
   - Indentation consistency
   - Trailing whitespace
   - Tab vs. space usage

5. **Structure (15%)** - Code organization
   - Import organization
   - Global variable usage
   - Module organization
   - Class vs. function balance

### Scoring System

- **0-100 Scale**: Overall and per-category scores
- **Letter Grades**: A (90+), B (80-89), C (70-79), D (60-69), F (<60)
- **Visual Indicators**: Score bars and emoji indicators
- **Weighted Average**: Category scores combined with appropriate weights

### Actionable Suggestions

Each issue found includes:
- **Priority Level**: High, Medium, or Low
- **Specific Location**: Line number and context
- **Issue Description**: What's wrong
- **Improvement Suggestion**: How to fix it
- **Code Examples**: When applicable

## Usage

### Basic Usage

Analyze a single file:
```bash
./readability-scorer.py -f myfile.py
```

Analyze a directory (recursive):
```bash
./readability-scorer.py -d ./src
```

Analyze current directory:
```bash
./readability-scorer.py
```

### Output Formats

Generate Markdown report (default):
```bash
./readability-scorer.py -f myfile.py --format markdown
```

Generate JSON output for automation:
```bash
./readability-scorer.py -f myfile.py --format json
```

Save report to file:
```bash
./readability-scorer.py -d ./src -o report.md
```

### Quality Gate

Use as a quality gate in CI/CD:
```bash
# Fail if score is below 80
./readability-scorer.py -d ./src --min-score 80
```

Exit codes:
- `0`: Success (score meets minimum)
- `1`: Failure (score below minimum or error)

## Examples

### Example 1: Single File Analysis

```bash
$ ./readability-scorer.py -f examples/palindrome.py
```

Output:
```markdown
# Readability Report: palindrome.py

**Overall Score:** 99.25/100
**Grade:** A (Excellent) 🌟

## Category Scores
- **Naming:** 100.0/100 ██████████
- **Complexity:** 100.0/100 ██████████
- **Documentation:** 100.0/100 ██████████
- **Formatting:** 100.0/100 ██████████
- **Structure:** 95.0/100 █████████░

## Improvement Suggestions

### 🟡 Medium Priority
**Line 21:** Imports are not at the top of the file
- *Suggestion:* Move all imports to the top of the file after the module docstring
```

### Example 2: Directory Analysis with JSON Output

```bash
$ ./readability-scorer.py -d ./src --format json > analysis.json
```

Output structure:
```json
{
  "timestamp": "2025-11-11T12:00:00Z",
  "directory": "./src",
  "summary": {
    "total_files": 10,
    "avg_overall_score": 85.5,
    "avg_scores_by_category": {
      "naming": 90.0,
      "complexity": 82.0,
      "documentation": 88.0,
      "formatting": 85.0,
      "structure": 87.0
    },
    "total_suggestions": 45,
    "suggestions_by_priority": {
      "high": 5,
      "medium": 20,
      "low": 20
    }
  },
  "files_analyzed": [...]
}
```

### Example 3: CI/CD Integration

```bash
#!/bin/bash
# In your CI pipeline

# Analyze code and require minimum score
./tools/readability-scorer.py -d ./src --min-score 75

if [ $? -eq 0 ]; then
    echo "✅ Code quality check passed"
else
    echo "❌ Code quality below acceptable threshold"
    exit 1
fi
```

## Metrics Details

### Naming Metrics
- Functions analyzed
- Variables analyzed
- Good vs. poor names count
- Single-character variables
- Abbreviation usage

### Complexity Metrics
- Average cyclomatic complexity
- Maximum nesting depth
- Long function count
- Complex function count
- Functions per file

### Documentation Metrics
- Functions with docstrings
- Classes with docstrings
- Module docstring presence
- Average docstring length
- Parameter documentation

### Formatting Metrics
- Total lines of code
- Long lines (>88 characters)
- Trailing whitespace occurrences
- Blank line distribution
- Indentation consistency

### Structure Metrics
- Import count and organization
- Global variable count
- Class to function ratio
- Module organization quality

## Integration

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
./tools/readability-scorer.py -d . --min-score 70 --format json > /tmp/readability.json
exit $?
```

### GitHub Actions

```yaml
- name: Check Code Readability
  run: |
    python tools/readability-scorer.py -d ./src --min-score 75
```

### Pre-merge Quality Check

```bash
# Check all modified Python files
git diff --name-only --diff-filter=AM | grep '.py$' | while read file; do
    ./tools/readability-scorer.py -f "$file" --min-score 70 || exit 1
done
```

## Interpreting Results

### Score Ranges

- **90-100 (A)**: Excellent - Well-written, maintainable code
- **80-89 (B)**: Good - Minor improvements possible
- **70-79 (C)**: Fair - Some refactoring recommended
- **60-69 (D)**: Needs Improvement - Significant issues present
- **0-59 (F)**: Poor - Major refactoring required

### Priority Levels

- **🔴 High Priority**: Issues that significantly impact readability or maintainability
  - Complex functions (cyclomatic complexity > 10)
  - Deep nesting (> 4 levels)
  - Long functions (> 50 lines)
  - Missing critical documentation

- **🟡 Medium Priority**: Issues that affect code quality but are manageable
  - Generic naming
  - Moderate complexity
  - Minor documentation gaps
  - Import organization

- **🟢 Low Priority**: Minor improvements and polish
  - Style inconsistencies
  - Minimal documentation
  - Minor naming issues
  - Convention deviations

## Best Practices

### Aim for These Targets

- **Overall Score**: > 85
- **Naming**: > 90 (clear, descriptive names)
- **Complexity**: > 80 (simple, focused functions)
- **Documentation**: > 85 (comprehensive docs)
- **Formatting**: > 90 (consistent style)
- **Structure**: > 85 (well-organized)

### Common Improvements

1. **Break down long functions** into smaller, focused ones
2. **Add comprehensive docstrings** with Args, Returns, and examples
3. **Use descriptive variable names** that explain intent
4. **Reduce nesting depth** with early returns and guard clauses
5. **Keep lines under 88 characters** for readability
6. **Organize imports** at the top of files
7. **Minimize global variables** in favor of parameters or classes

## Testing

Run the test suite:
```bash
python3 test_readability_scorer.py
```

All tests should pass:
```
Running Readability Scorer Tests...
==================================================
✓ Scorer initialization test passed
✓ Good code analysis test passed
✓ Poor naming detection test passed
...
==================================================
Results: 21 passed, 0 failed
```

## Related Tools

- **code-analyzer.py**: Self-improving code analyzer that learns from merges
- **code-archaeologist.py**: Historical code analysis and evolution tracking
- **pattern-matcher.py**: Pattern detection and matching
- **code-golf-optimizer.py**: Code optimization and minification

## License

Part of the Chained autonomous AI development system.
