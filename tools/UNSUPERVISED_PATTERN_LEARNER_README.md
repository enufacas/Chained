# Unsupervised Pattern Learner

**Author:** @engineer-master (Margaret Hamilton)  
**Version:** 1.0.0  
**Status:** Production Ready

## Overview

The Unsupervised Pattern Learner is an advanced machine learning tool that automatically discovers code patterns, anti-patterns, and anomalies in Python codebases without requiring predefined rules. It uses clustering algorithms and statistical analysis to identify common coding patterns and outliers.

### Key Features

- **🤖 Automatic Pattern Discovery**: No manual rule definition required
- **📊 Multiple Clustering Algorithms**: K-means, DBSCAN-inspired anomaly detection
- **🎯 Rich Feature Extraction**: 16+ code features from AST analysis
- **📈 Statistical Analysis**: Confidence scores, support metrics, silhouette scores
- **📝 Comprehensive Reporting**: Markdown and JSON output formats
- **🔍 Anomaly Detection**: Identifies unusual code patterns for review
- **⚡ Fast Processing**: Handles large codebases efficiently

## Installation

The tool is standalone and requires only Python 3.8+ with no external dependencies beyond the standard library.

```bash
# Make executable
chmod +x tools/unsupervised_pattern_learner.py

# Verify installation
python3 tools/unsupervised_pattern_learner.py --help
```

## Quick Start

### Basic Usage

Discover patterns in the current directory:

```bash
python3 tools/unsupervised_pattern_learner.py -d .
```

### Analyze Specific Directory

```bash
python3 tools/unsupervised_pattern_learner.py -d /path/to/repo -k 10
```

### Save Report to File

```bash
python3 tools/unsupervised_pattern_learner.py -d . -o pattern_report.md
```

### Generate JSON Output

```bash
python3 tools/unsupervised_pattern_learner.py -d . --format json > patterns.json
```

## How It Works

### 1. Feature Extraction

The tool analyzes Python code using Abstract Syntax Tree (AST) parsing to extract:

**Structural Features:**
- Nesting depth
- Number of children/siblings
- Node relationships

**Complexity Features:**
- Cyclomatic complexity
- Cognitive complexity
- Lines of code

**Pattern Features:**
- Docstring presence
- Type hint usage
- Error handling
- Recursion detection

**Naming Features:**
- Name length
- Naming conventions (snake_case, camelCase)

### 2. Pattern Discovery

**K-means Clustering:**
- Groups similar code elements
- Uses K-means++ initialization for better results
- Identifies common coding patterns

**Anomaly Detection:**
- Detects outliers (top 5% of distances)
- Flags unusual or potentially problematic code
- Useful for refactoring identification

### 3. Pattern Analysis

For each discovered pattern:
- Generates descriptive name
- Calculates confidence score
- Determines support (frequency)
- Selects representative examples
- Categorizes pattern type

## Command-Line Options

```bash
python3 tools/unsupervised_pattern_learner.py [OPTIONS]

Options:
  -d, --directory DIR      Directory to analyze (default: current directory)
  -k, --clusters N         Number of clusters (default: 10)
  --min-samples N          Minimum samples per pattern (default: 3)
  -o, --output FILE        Output file for report
  --format FORMAT          Output format: markdown or json (default: markdown)
  --save-patterns          Save discovered patterns to JSON file
  -h, --help               Show help message
```

## Output Formats

### Markdown Report

Includes:
- Summary statistics
- Pattern categories
- Detailed pattern descriptions
- Code examples
- Key insights and recommendations

### JSON Output

Structured data with:
- All patterns with full metadata
- Feature vectors
- Confidence scores
- Example locations

## Integration Examples

### Integration with Code Analyzer

```python
from unsupervised_pattern_learner import UnsupervisedPatternLearner

# Create learner
learner = UnsupervisedPatternLearner()

# Extract features
learner.extract_features_from_directory('src')

# Discover patterns
patterns = learner.discover_patterns(n_clusters=10)

# Generate report
report = learner.generate_report('markdown')
print(report)
```

### Automated Pipeline

```bash
#!/bin/bash
# Continuous pattern discovery

cd /path/to/repo

# Discover patterns weekly
python3 tools/unsupervised_pattern_learner.py \
    -d src \
    -k 12 \
    --save-patterns \
    -o "analysis/patterns_$(date +%Y%m%d).md"

# Track pattern evolution over time
```

## Pattern Categories

The tool automatically categorizes discovered patterns:

### Well-Documented
Code with comprehensive docstrings and documentation

### High-Complexity
Functions/classes with high cyclomatic or cognitive complexity

### Simple-Function
Basic, straightforward implementations

### Type-Safe
Code using type hints extensively

### Anomaly
Outliers that deviate significantly from common patterns

## Use Cases

### 1. Code Quality Assessment

Identify patterns of well-documented vs. undocumented code:

```bash
python3 tools/unsupervised_pattern_learner.py -d src -k 15
```

Review the "Well-Documented" vs. "Basic" pattern distribution.

### 2. Refactoring Identification

Find complex or anomalous code patterns:

```bash
python3 tools/unsupervised_pattern_learner.py -d src --min-samples 2
```

Focus on "High-Complexity" and "Anomaly" categories.

### 3. Architecture Understanding

Discover common coding patterns in large codebases:

```bash
python3 tools/unsupervised_pattern_learner.py -d . -k 20 --save-patterns
```

Analyze the saved JSON to understand architectural patterns.

### 4. Code Review Automation

Integrate into CI/CD to track pattern evolution:

```bash
# In CI pipeline
python3 tools/unsupervised_pattern_learner.py \
    -d $SOURCE_DIR \
    --format json \
    > patterns_$(git rev-parse --short HEAD).json
```

### 5. Learning from Best Practices

Identify patterns in high-quality codebases:

```bash
# Analyze well-maintained projects
python3 tools/unsupervised_pattern_learner.py \
    -d /path/to/exemplary/project \
    -k 10 \
    -o best_practices.md
```

## Performance Metrics

### Confidence Score
- Measures how well code elements fit the pattern
- Range: 0.0 to 1.0
- Higher is better (more consistent pattern)

### Support
- Percentage of codebase matching the pattern
- Range: 0.0% to 100%
- Indicates pattern prevalence

### Occurrences
- Absolute count of pattern instances
- Useful for prioritizing refactoring efforts

## Best Practices

### Choosing Number of Clusters

- **Small projects** (&lt;1000 LOC): k=5-8
- **Medium projects** (1000-10000 LOC): k=10-15
- **Large projects** (&gt;10000 LOC): k=15-25

### Minimum Samples

- Use `--min-samples 2` for exploratory analysis
- Use `--min-samples 5` for production analysis
- Higher values reduce noise but may miss rare patterns

### Regular Analysis

Run pattern discovery:
- **Weekly**: For active development
- **Monthly**: For stable codebases
- **After major refactoring**: To validate improvements

## Troubleshooting

### No Patterns Discovered

**Cause**: Not enough code elements or too high min-samples

**Solution**:
```bash
python3 tools/unsupervised_pattern_learner.py -d . -k 5 --min-samples 1
```

### Too Many Patterns

**Cause**: Too many clusters or too low min-samples

**Solution**:
```bash
python3 tools/unsupervised_pattern_learner.py -d . -k 8 --min-samples 5
```

### Anomaly Detection Sensitivity

Anomaly detection uses the top 5% most distant points. This is hardcoded but can be adjusted in the source if needed.

## Testing

Comprehensive test suite included:

```bash
# Run all tests
python3 tools/test_unsupervised_pattern_learner.py

# Tests cover:
# - Feature extraction
# - Clustering algorithms
# - Pattern discovery
# - Anomaly detection
# - Report generation
# - Integration with real code
```

## Future Enhancements

Potential improvements for future versions:

1. **Additional Clustering Algorithms**: DBSCAN, hierarchical clustering
2. **More Languages**: JavaScript, TypeScript, Go support
3. **Interactive Visualization**: Web-based pattern explorer
4. **Temporal Analysis**: Track pattern evolution over time
5. **Pattern Recommendations**: Suggest refactorings based on patterns

## Technical Details

### Algorithm Complexity

- **Feature Extraction**: O(n * m) where n=files, m=avg AST nodes
- **K-means Clustering**: O(i * k * n * d) where i=iterations, k=clusters, n=points, d=dimensions
- **Anomaly Detection**: O(n * k)
- **Overall**: Linear in codebase size for typical cases

### Memory Usage

- Approximately 1MB per 1000 code elements
- Scales well for large codebases
- Feature vectors cached in memory during analysis

### Accuracy

The tool uses unsupervised learning, so "accuracy" is measured by:
- Silhouette scores (higher is better)
- Intra-cluster cohesion (lower distance is better)
- Manual validation of discovered patterns

## Contributing

As part of the Chained autonomous system, this tool follows **@engineer-master** principles:

- ✅ Rigorous testing (12 comprehensive tests)
- ✅ Defensive programming (error handling throughout)
- ✅ Clear documentation (this README)
- ✅ Type hints where beneficial
- ✅ Systematic design (clear separation of concerns)

## Support

For issues or questions:
1. Check this documentation
2. Review test cases for usage examples
3. Examine the source code (well-commented)
4. Open an issue in the repository

## License

Part of the Chained project. See main repository LICENSE.

---

## Example Output

Here's a sample of what the tool produces:

```markdown
# Unsupervised Pattern Discovery Report

**Generated:** 2025-11-15T03:00:00.000000+00:00
**Total Code Elements Analyzed:** 1934
**Patterns Discovered:** 9

## Pattern Categories
- **well-documented**: 6 patterns
- **simple-function**: 2 patterns
- **anomaly**: 1 patterns

## Discovered Patterns

### 1. Well-Documented Moderate Medium FunctionDef
- **Type:** cluster
- **Category:** well-documented
- **Occurrences:** 229
- **Confidence:** 32.67%
- **Support:** 11.84%
- **Description:** Pattern with 229 occurrences. Primarily FunctionDef nodes. 
  Average complexity: 7.3, average size: 48.2 lines. 
  Generally well-documented. Uses type hints.

**Examples:**
- `tools/code-analyzer.py:200` - FunctionDef
- `tools/workflow-orchestrator.py:110` - FunctionDef
```

---

*Built by **@engineer-master** (Margaret Hamilton) with systematic rigor and innovative design.*
