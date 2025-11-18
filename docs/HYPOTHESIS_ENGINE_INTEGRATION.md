# Integration Guide: Hypothesis Testing Engine

**Author:** @accelerate-specialist  
**Purpose:** How to integrate the hypothesis testing engine with existing Chained tools

## Overview

The hypothesis testing engine complements existing analysis tools by automatically discovering patterns rather than relying on predefined rules. This guide shows how to integrate it into your workflow.

## Integration with Existing Tools

### 1. Pattern Matcher Integration

The hypothesis testing engine can validate patterns discovered by `pattern-matcher.py`:

```bash
# Step 1: Run pattern matcher
python3 tools/pattern-matcher.py --repo-path . --output analysis/patterns.json

# Step 2: Run hypothesis testing
python3 tools/hypothesis_testing_engine.py --repo-path . --output analysis/hypothesis_results.json

# Step 3: Compare results
python3 tools/compare_patterns_and_hypotheses.py
```

**Use Case:** Validate that patterns detected by the matcher correlate with quality issues.

### 2. Unsupervised Pattern Learner Integration

Combine unsupervised learning with hypothesis testing:

```python
# First, discover patterns
from unsupervised_pattern_learner import UnsupervisedPatternLearner

learner = UnsupervisedPatternLearner(repo_path=".")
discovered_patterns = learner.discover_patterns()

# Then, test hypotheses about those patterns
from hypothesis_testing_engine import HypothesisTestingEngine

engine = HypothesisTestingEngine(repo_path=".")
results = engine.run(num_hypotheses=15)

# Compare discovered patterns with validated hypotheses
for pattern in discovered_patterns:
    for hypothesis in results['hypotheses']:
        if hypothesis['validated']:
            # Check if they align
            print(f"Pattern {pattern['id']} aligns with {hypothesis['description']}")
```

**Use Case:** Discover novel patterns then test hypotheses about their impact.

### 3. Code Archaeologist Integration

Use hypothesis testing to validate historical patterns:

```bash
# Analyze historical decisions
python3 tools/code-archaeologist.py --analyze-history

# Test hypotheses about evolution
python3 tools/hypothesis_testing_engine.py --repo-path .

# Look for correlations between historical changes and current quality
```

**Use Case:** Understand if past architectural decisions correlate with current code quality.

### 4. PR Failure Learner Integration

Test hypotheses about what causes PR failures:

```python
from pr_failure_learner import PRFailureLearner
from hypothesis_testing_engine import HypothesisTestingEngine

# Learn from failures
learner = PRFailureLearner()
failure_patterns = learner.analyze_failures()

# Generate hypotheses about failure causes
engine = HypothesisTestingEngine(repo_path=".")
results = engine.run(num_hypotheses=10)

# Find hypotheses that explain failure patterns
for hypothesis in results['hypotheses']:
    if hypothesis['validated']:
        # Check if hypothesis explains failures
        print(f"Potential failure cause: {hypothesis['description']}")
```

**Use Case:** Proactively identify code patterns that lead to CI/CD failures.

## Workflow Examples

### Daily Code Quality Check

```bash
#!/bin/bash
# daily-quality-check.sh

echo "Running daily code quality analysis..."

# 1. Pattern matching
python3 tools/pattern-matcher.py --repo-path . --output analysis/patterns.json

# 2. Hypothesis testing
python3 tools/hypothesis_testing_engine.py \
    --repo-path . \
    --num-hypotheses 15 \
    --output analysis/hypothesis_results.json

# 3. Generate report
python3 tools/generate_quality_report.py \
    --patterns analysis/patterns.json \
    --hypotheses analysis/hypothesis_results.json \
    --output reports/daily_quality.md

echo "Report available at: reports/daily_quality.md"
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run hypothesis testing on changed files
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$CHANGED_FILES" ]; then
    echo "Running hypothesis testing on changed files..."
    
    python3 tools/hypothesis_testing_engine.py \
        --max-files 20 \
        --num-hypotheses 8
    
    # Check if any critical hypotheses are violated
    python3 tools/check_hypothesis_violations.py
    
    if [ $? -ne 0 ]; then
        echo "❌ Code quality check failed!"
        exit 1
    fi
fi
```

### CI/CD Pipeline

```yaml
# .github/workflows/code-quality.yml
name: Code Quality Analysis

on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Run hypothesis testing
        run: |
          python3 tools/hypothesis_testing_engine.py \
            --num-hypotheses 12 \
            --max-files 100 \
            --output analysis/hypothesis_results.json
      
      - name: Check for quality regressions
        run: |
          python3 tools/check_quality_regression.py \
            --current analysis/hypothesis_results.json \
            --baseline baseline/hypothesis_results.json
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: hypothesis-results
          path: analysis/hypothesis_results.json
```

## Custom Integration

### Creating a Custom Analyzer

```python
from hypothesis_testing_engine import (
    HypothesisTestingEngine,
    CodeAnalyzer,
    HypothesisGenerator
)

class CustomAnalyzer(CodeAnalyzer):
    """Custom analyzer with domain-specific metrics"""
    
    def _extract_function_metrics(self, node, file_path, content):
        metric = super()._extract_function_metrics(node, file_path, content)
        
        # Add custom metrics
        metric.security_score = self._calculate_security_score(node)
        metric.performance_score = self._calculate_performance_score(node)
        
        return metric
    
    def _calculate_security_score(self, node):
        """Calculate security score"""
        score = 1.0
        
        # Check for security issues
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, 'id'):
                    if child.func.id in ['eval', 'exec']:
                        score -= 0.5
        
        return max(0, score)

# Use custom analyzer
engine = HypothesisTestingEngine(repo_path=".")
engine.analyzer = CustomAnalyzer(repo_path=".")
results = engine.run(num_hypotheses=10)
```

### Creating Custom Hypotheses

```python
class CustomHypothesisGenerator(HypothesisGenerator):
    """Generate domain-specific hypotheses"""
    
    def _load_templates(self):
        templates = super()._load_templates()
        
        # Add custom templates
        templates.append({
            'id': 'security_pattern',
            'template': 'Functions with {security_issue} tend to have {consequence}',
            'type': 'pattern',
            'combinations': [
                ('eval_usage', 'security vulnerabilities'),
                ('hardcoded_secrets', 'data breaches'),
                ('sql_injection_risk', 'database compromise'),
            ]
        })
        
        return templates

# Use custom generator
engine = HypothesisTestingEngine(repo_path=".")
engine.generator = CustomHypothesisGenerator()
results = engine.run(num_hypotheses=15)
```

## Data Flow Diagram

```
┌─────────────────────┐
│  Repository Code    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Code Analyzer      │
│  - Parse AST        │
│  - Extract Metrics  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Hypothesis         │
│  Generator          │
│  - Create           │
│    Hypotheses       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Hypothesis         │
│  Tester             │
│  - Statistical      │
│    Testing          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Results &          │
│  Insights           │
│  - JSON Output      │
│  - Recommendations  │
└─────────────────────┘
```

## Performance Considerations

### Large Repositories

For repositories with 1000+ files:

```bash
# Process in batches
for i in {0..9}; do
    python3 tools/hypothesis_testing_engine.py \
        --max-files 100 \
        --output "analysis/batch_${i}.json" &
done

wait

# Combine results
python3 tools/combine_hypothesis_results.py \
    analysis/batch_*.json \
    --output analysis/combined_results.json
```

### Incremental Analysis

Only analyze changed files:

```bash
# Get changed files
CHANGED=$(git diff --name-only HEAD~1 HEAD | grep '\.py$')

# Create temporary directory with only changed files
mkdir -p /tmp/changed_analysis
for file in $CHANGED; do
    cp --parents "$file" /tmp/changed_analysis/
done

# Analyze only changes
python3 tools/hypothesis_testing_engine.py \
    --repo-path /tmp/changed_analysis \
    --output analysis/incremental_results.json
```

## Best Practices

### 1. Baseline Establishment

```bash
# Create baseline on main branch
git checkout main
python3 tools/hypothesis_testing_engine.py \
    --output baseline/hypothesis_results.json

# Compare branches
git checkout feature-branch
python3 tools/hypothesis_testing_engine.py \
    --output analysis/hypothesis_results.json

python3 tools/compare_with_baseline.py
```

### 2. Regular Monitoring

Set up weekly analysis:

```bash
# crontab entry
0 2 * * 1 cd /path/to/repo && python3 tools/hypothesis_testing_engine.py --num-hypotheses 20
```

### 3. Alert on Regressions

```python
# check_regressions.py
import json

with open('baseline/hypothesis_results.json') as f:
    baseline = json.load(f)

with open('analysis/hypothesis_results.json') as f:
    current = json.load(f)

if current['validation_rate'] < baseline['validation_rate'] * 0.9:
    print("❌ ALERT: Validation rate dropped significantly!")
    exit(1)
```

## Troubleshooting

### Issue: Low validation rate

**Cause:** Small sample size or healthy codebase  
**Solution:** This is often good news! Low validation means anti-patterns aren't present.

### Issue: No functions analyzed

**Cause:** Parsing errors or wrong path  
**Solution:** Check Python syntax and verify repo path:

```bash
python3 -m py_compile *.py  # Check syntax
python3 tools/hypothesis_testing_engine.py --repo-path /correct/path
```

### Issue: Slow analysis

**Cause:** Large repository  
**Solution:** Use `--max-files` to limit scope:

```bash
python3 tools/hypothesis_testing_engine.py --max-files 50
```

## Support & Contribution

For issues or enhancements:

1. Check existing tools documentation
2. Review test cases in `tests/test_hypothesis_testing_engine.py`
3. See examples in `examples/demo_hypothesis_testing.py`
4. Create issue with `[hypothesis-engine]` tag

---

**Created by @accelerate-specialist for the Chained ecosystem**
