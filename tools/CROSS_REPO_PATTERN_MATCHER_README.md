# 🎯 Cross-Repository Pattern Matcher

> **Created by @investigate-champion** - An analytical tool for identifying best practices across repositories

## Overview

The Cross-Repository Pattern Matcher is a powerful tool that analyzes code repositories to identify, score, and track best practices. Inspired by Ada Lovelace's analytical rigor, it provides actionable insights to improve code quality, security, and maintainability.

## Features

- **Multi-Category Analysis**: Detects patterns in code, workflows, documentation, and security
- **Extensible Pattern Library**: 20+ built-in patterns across multiple categories
- **Smart Scoring**: Calculates a comprehensive best practices score (0-100)
- **Actionable Recommendations**: Provides specific guidance for improvements
- **Detailed Reporting**: Generates both human-readable and JSON reports
- **High Confidence**: Uses confidence scores to minimize false positives

## Installation

No additional dependencies required beyond the base repository requirements:

```bash
pip install -r requirements.txt
```

The tool uses only Python standard library plus PyYAML (already in requirements.txt).

## Quick Start

### Basic Usage

Analyze the current repository:

```bash
python3 tools/cross-repo-pattern-matcher.py
```

### Analyze a Specific Repository

```bash
python3 tools/cross-repo-pattern-matcher.py --repo /path/to/repository
```

### Generate JSON Report

```bash
python3 tools/cross-repo-pattern-matcher.py -o report.json
```

### Verbose Output with Details

```bash
python3 tools/cross-repo-pattern-matcher.py --verbose
```

### List Available Patterns

```bash
python3 tools/cross-repo-pattern-matcher.py --patterns
```

## Pattern Categories

### 🐍 Code Patterns (8 patterns)

Analyzes Python code for best practices:

- **CP001**: Type Hints Present - Functions with type annotations
- **CP002**: Comprehensive Docstrings - Detailed documentation
- **CP003**: Error Handling - Proper try/except blocks
- **CP004**: Long Functions - Functions exceeding 50 lines (anti-pattern)
- **CP005**: Magic Numbers - Undocumented numeric literals (anti-pattern)
- **CP006**: Deep Nesting - Excessive indentation depth (anti-pattern)
- **CP007**: Dataclass Usage - Modern Python data structures
- **CP008**: Context Managers - Proper resource management

### ⚙️ Workflow Patterns (8 patterns)

Analyzes GitHub Actions workflows:

- **WF001**: Error Handling in Workflows - Resilient workflow steps
- **WF002**: Secrets Management - Proper secrets usage
- **WF003**: Pinned Action Versions - Stable, reproducible workflows
- **WF004**: Workflow Documentation - Clear naming and comments
- **WF005**: Timeout Configuration - Resource management
- **WF006**: Unpinned Action Version - Unstable references (anti-pattern)
- **WF007**: Hardcoded Credentials - Security risk (anti-pattern)
- **WF008**: Reusable Workflow - Modular workflow design

### 🔒 Security Patterns (4 patterns)

Identifies security-related issues:

- **SEC001**: Input Validation - External input checking
- **SEC002**: SQL Injection Risk - Unsafe query construction (anti-pattern)
- **SEC003**: Hardcoded Secrets - Embedded credentials (anti-pattern)
- **SEC004**: Secure Random - Cryptographic randomness

## Output Format

### Console Report

```
================================================================================
📊 PATTERN ANALYSIS REPORT: repository-name
================================================================================
Generated: 2025-11-14T10:28:51.716999+00:00
Score: 87.5/100

📈 SUMMARY
--------------------------------------------------------------------------------
Total patterns matched:    245
Good practices:            210
Anti-patterns:             35
Files analyzed:            42
Average confidence:        89.84%

📋 BY CATEGORY
--------------------------------------------------------------------------------
  code                 200
  workflow             38
  security             7

⚠️  BY SEVERITY
--------------------------------------------------------------------------------
  🔴 critical        2
  🟠 high            45
  🟡 medium          150
  🟢 low             40
  🔵 info            8

💡 RECOMMENDATIONS
================================================================================
1. 🔴 CRITICAL: 2 critical security issues detected...
2. ⚠️  35 anti-patterns detected. Most common: Long Functions (20)...
3. ✅ 210 good practices found. Keep up the excellent work!
...
```

### JSON Report

```json
{
  "repository_name": "Chained",
  "timestamp": "2025-11-14T10:28:51.716999+00:00",
  "patterns_matched": [
    {
      "pattern_id": "CP001",
      "pattern_name": "Type Hints Present",
      "category": "code",
      "file_path": "tools/analyzer.py",
      "line_number": 42,
      "matched_content": "def analyze(data: Dict) -> bool:",
      "context": "Function has type hints",
      "confidence": 0.95,
      "metadata": {}
    }
  ],
  "summary": {
    "total_patterns": 245,
    "good_practices": 210,
    "anti_patterns": 35,
    "by_category": {...},
    "by_severity": {...}
  },
  "recommendations": [...],
  "score": 87.5
}
```

## Scoring Algorithm

The best practices score (0-100) is calculated as follows:

1. **Baseline**: Start at 50 points
2. **Good Practices**: Add points weighted by severity
   - Critical: +10 points
   - High: +5 points
   - Medium: +2 points
   - Low: +1 point
   - Info: +0.5 points
3. **Anti-Patterns**: Subtract points weighted by severity (same weights)
4. **Confidence**: All adjustments multiplied by pattern confidence (0.0-1.0)
5. **Normalization**: Final score clamped to 0-100 range

### Score Interpretation

- **85-100**: Excellent - Strong best practices
- **70-84**: Good - Minor improvements possible
- **50-69**: Fair - Several improvements needed
- **30-49**: Poor - Significant refactoring required
- **0-29**: Critical - Major issues detected

## Advanced Usage

### Integration with CI/CD

Add to GitHub Actions workflow:

```yaml
- name: Run Pattern Analysis
  run: |
    python3 tools/cross-repo-pattern-matcher.py \
      --repo . \
      -o pattern-report.json

- name: Upload Report
  uses: actions/upload-artifact@v4
  with:
    name: pattern-analysis
    path: pattern-report.json
```

### Custom Pattern Detection

Extend the tool by creating custom detector classes:

```python
from cross_repo_pattern_matcher import PatternDetector, Pattern, PatternMatch

class CustomDetector(PatternDetector):
    def __init__(self):
        self.patterns = [
            Pattern(
                id='CUSTOM001',
                name='Custom Pattern',
                category='custom',
                description='Your pattern description',
                severity='medium',
                type='good_practice',
                tags=['custom', 'example']
            )
        ]
    
    def detect(self, file_path, content):
        # Your detection logic
        matches = []
        # ... analyze content ...
        return matches
    
    def get_patterns(self):
        return self.patterns
```

### Cross-Repository Comparison

Compare multiple repositories:

```bash
# Analyze multiple repos
for repo in repo1 repo2 repo3; do
    python3 tools/cross-repo-pattern-matcher.py \
        --repo ../$repo \
        -o analysis-$repo.json
done

# Compare scores
python3 -c "
import json, glob
for f in glob.glob('analysis-*.json'):
    data = json.load(open(f))
    print(f\"{data['repository_name']:20s} {data['score']:5.1f}/100\")
"
```

## Testing

Run the comprehensive test suite:

```bash
python3 tools/test_cross_repo_pattern_matcher.py
```

Tests cover:
- Pattern detection accuracy
- Scoring algorithm correctness
- Report generation
- Confidence calculations
- Pattern definitions
- Integration scenarios

## Performance

- **Speed**: Analyzes ~150 files in under 10 seconds
- **Memory**: Minimal memory footprint (< 100MB for typical repos)
- **Scalability**: Tested on repositories with 1000+ files

## Integration with Existing Tools

### Code Analyzer

The Pattern Matcher complements the existing code-analyzer.py:

- **Code Analyzer**: Learns from merge outcomes, tracks patterns over time
- **Pattern Matcher**: One-time analysis, cross-repo comparison, broader scope

### Dependency Flow Analyzer

Use together for comprehensive insights:

```bash
# Analyze patterns
python3 tools/cross-repo-pattern-matcher.py -o patterns.json

# Analyze dependencies
python3 tools/dependency-flow-analyzer.py -o dependencies.json

# Combine insights for complete picture
```

## Best Practices

1. **Run Regularly**: Integrate into CI/CD for continuous monitoring
2. **Track Over Time**: Compare reports to measure improvement
3. **Prioritize Critical**: Address critical security issues first
4. **Set Goals**: Aim for 85+ score for production code
5. **Share Reports**: Use JSON output for automated dashboards

## Troubleshooting

### No Patterns Detected

- Ensure you're analyzing the correct directory
- Check file extensions (.py, .yml, .yaml)
- Verify files contain actual code (not empty)

### Low Confidence Scores

- Some patterns are naturally lower confidence (e.g., security heuristics)
- Focus on high-severity, high-confidence matches first

### Performance Issues

- Use `.gitignore` patterns to skip large directories
- Consider analyzing specific subdirectories
- Increase system resources for very large repositories

## Roadmap

Future enhancements planned by @investigate-champion:

- [ ] Support for more languages (JavaScript, Go, Rust)
- [ ] Machine learning-based pattern detection
- [ ] Historical trend analysis
- [ ] Interactive HTML reports
- [ ] IDE integration (VS Code extension)
- [ ] Custom pattern DSL for easy pattern definition
- [ ] Pattern marketplace for sharing patterns

## Contributing

To add new patterns:

1. Define pattern in appropriate detector class
2. Add detection logic in `detect()` method
3. Add test cases in test file
4. Update this documentation
5. Submit PR with @investigate-champion

## License

Part of the Chained autonomous AI ecosystem.

---

**Created by @investigate-champion** - Illuminating best practices through analytical rigor 🔍

For questions or improvements, mention @investigate-champion in issues or PRs.
