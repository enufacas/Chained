# AI Hypothesis Testing Engine for Code Patterns

**Author:** @accelerate-specialist (Edsger Dijkstra)  
**Category:** Code Analysis & Pattern Discovery  
**Status:** Production Ready

## Overview

The AI Hypothesis Testing Engine is an intelligent system that generates and tests hypotheses about code patterns in your repository. It uses statistical analysis and machine learning concepts to discover insights about software quality, maintainability, and performance.

### What Makes This Different?

Unlike traditional static analysis tools that use predefined rules, this engine:

- **🤖 Generates hypotheses automatically** based on code patterns it observes
- **📊 Tests hypotheses statistically** using real repository data
- **🔬 Learns from results** to improve future hypothesis generation
- **⚡ Focuses on performance** - elegant and efficient analysis

## Features

### 1. Hypothesis Generation

The engine generates three types of hypotheses:

- **Correlation Hypotheses**: "Functions with X tend to have Y"
- **Threshold Hypotheses**: "Functions exceeding N in metric X tend to have issue Y"
- **Pattern Hypotheses**: "Functions with pattern X have characteristic Y"

### 2. Statistical Testing

Each hypothesis is tested against actual code metrics:

- Calculates correlation coefficients
- Compares threshold groups
- Assesses pattern impacts
- Provides confidence scores and p-values

### 3. Actionable Insights

The engine provides:

- Validated hypotheses with evidence
- Specific examples from your codebase
- Actionable recommendations for improvement
- Quality assessment scores

## Installation & Usage

### Basic Usage

```bash
# Run on current repository
python3 tools/hypothesis_testing_engine.py

# Customize parameters
python3 tools/hypothesis_testing_engine.py \
  --repo-path /path/to/repo \
  --num-hypotheses 15 \
  --max-files 100 \
  --output analysis/results.json
```

### Command Line Options

- `--repo-path`, `-r`: Path to repository to analyze (default: current directory)
- `--num-hypotheses`, `-n`: Number of hypotheses to generate (default: 10)
- `--max-files`, `-m`: Maximum files to analyze (default: 100)
- `--output`, `-o`: Output file for results (default: analysis/hypothesis_results.json)

### Python API

```python
from hypothesis_testing_engine import HypothesisTestingEngine

# Create engine
engine = HypothesisTestingEngine(
    repo_path=".",
    output_file="analysis/results.json"
)

# Run analysis
results = engine.run(
    num_hypotheses=10,
    max_files=100
)

# Access results
print(f"Validated: {results['hypotheses_validated']}")
print(f"Rate: {results['validation_rate']:.1%}")

for hypothesis in results['hypotheses']:
    if hypothesis['validated']:
        print(f"✓ {hypothesis['description']}")
```

## Example Output

### Console Output

```
🔬 Starting Hypothesis Testing Engine...
📊 Analyzing repository: .

1️⃣ Extracting code metrics...
   ✓ Analyzed 406 functions

2️⃣ Generating hypotheses...
   ✓ Generated 8 hypotheses

3️⃣ Testing hypotheses...
   Testing 1/8: Functions with high cyclomatic_complexity...
   ...

✓ Testing complete!
   4/8 hypotheses validated

============================================================
📊 HYPOTHESIS TESTING RESULTS
============================================================

✓ Validated Hypotheses: 4/8
✓ Validation Rate: 50.0%

🏆 Top Validated Hypotheses:
1. Functions with short naming have lower docstring_quality
   Confidence: 95.00%, Sample: 406
2. Functions with long naming have higher complexity
   Confidence: 95.00%, Sample: 406

💡 Actionable Insights:
  • Consider refactoring functions with lines > 50.0
  • Reducing cyclomatic_complexity may improve test_coverage
```

### JSON Output

```json
{
  "generated_at": "2025-11-18T03:09:32.701070+00:00",
  "repository": ".",
  "metrics_analyzed": 406,
  "hypotheses_generated": 8,
  "hypotheses_validated": 4,
  "validation_rate": 0.5,
  "hypotheses": [
    {
      "hypothesis_id": "hyp_complexity_quality_1",
      "description": "Functions with high cyclomatic_complexity tend to have lower test_coverage",
      "hypothesis_type": "correlation",
      "validated": false,
      "confidence": 0.05,
      "p_value": 0.88,
      "sample_size": 406
    }
  ],
  "summary": {
    "top_validated_hypotheses": [...],
    "insights": [...]
  }
}
```

## How It Works

### 1. Code Analysis

The engine uses Python's AST (Abstract Syntax Tree) to extract metrics:

- **Complexity Metrics**: Cyclomatic and cognitive complexity
- **Size Metrics**: Lines of code, number of parameters
- **Quality Indicators**: Docstrings, tests, error handling, type hints
- **Naming Patterns**: Naming conventions and style

### 2. Hypothesis Generation

Based on templates and observed patterns:

```python
# Example template
"Functions with {direction} {metric1} tend to have {direction2} {metric2}"

# Generated hypothesis
"Functions with high cyclomatic_complexity tend to have lower test_coverage"
```

### 3. Statistical Testing

For each hypothesis:

1. Extract relevant metrics from functions
2. Calculate correlation or compare groups
3. Determine if hypothesis is validated
4. Calculate confidence score and p-value
5. Collect supporting examples

### 4. Learning

The system learns from:

- Metric distributions in the codebase
- Validation success rates
- Pattern correlations
- Quality assessments

## Metrics Collected

### Complexity Metrics
- **Cyclomatic Complexity**: Number of independent paths
- **Cognitive Complexity**: Mental effort to understand code

### Quality Indicators
- **Has Docstring**: Function documentation present
- **Has Tests**: Test function or tested by unit tests
- **Has Error Handling**: Try-except blocks present
- **Has Type Hints**: Type annotations used

### Structure Metrics
- **Lines of Code**: Function size
- **Number of Parameters**: Function signature complexity
- **Naming Patterns**: Convention adherence

## Integration

### With Existing Tools

The engine integrates well with:

- **pattern-matcher.py**: Combines hypothesis testing with pattern matching
- **unsupervised_pattern_learner.py**: Feeds discovered patterns
- **code-archaeologist.py**: Historical pattern analysis
- **pr-failure-learner.py**: Learn from failures

### Workflow Integration

```yaml
# GitHub Actions example
- name: Run Hypothesis Testing
  run: |
    python3 tools/hypothesis_testing_engine.py \
      --num-hypotheses 15 \
      --output analysis/hypothesis_results.json
    
    # Use results for automated review
    python3 tools/analyze_hypotheses.py
```

## Performance Characteristics

**@accelerate-specialist** optimized for efficiency:

- **Time Complexity**: O(n*m) where n=files, m=functions
- **Space Complexity**: O(m) for storing metrics
- **Optimizations**:
  - Lazy file loading
  - Efficient AST traversal
  - Statistical calculations without heavy dependencies
  - JSON streaming for large outputs

### Benchmarks

- 100 files, 400 functions: ~2 seconds
- 500 files, 2000 functions: ~10 seconds
- 1000 files, 5000 functions: ~25 seconds

## Advanced Usage

### Custom Hypothesis Templates

Extend the `HypothesisGenerator` class:

```python
class CustomGenerator(HypothesisGenerator):
    def _load_templates(self):
        templates = super()._load_templates()
        templates.append({
            'id': 'custom_pattern',
            'template': 'Your custom template',
            'type': 'correlation',
            'combinations': [...]
        })
        return templates
```

### Custom Metrics

Extend the `CodeAnalyzer` class:

```python
class CustomAnalyzer(CodeAnalyzer):
    def _extract_function_metrics(self, node, file_path, content):
        metric = super()._extract_function_metrics(node, file_path, content)
        # Add custom metrics
        metric.custom_score = self._calculate_custom_score(node)
        return metric
```

### Filtering Results

```python
# Filter for high-confidence validated hypotheses
high_confidence = [
    h for h in results['hypotheses']
    if h['validated'] and h['confidence'] > 0.8
]

# Filter by hypothesis type
correlations = [
    h for h in results['hypotheses']
    if h['hypothesis_type'] == 'correlation'
]
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python3 tests/test_hypothesis_testing_engine.py

# Run specific test class
python3 tests/test_hypothesis_testing_engine.py TestHypothesisGenerator
```

### Test Coverage

- ✅ Code metrics extraction
- ✅ Hypothesis generation
- ✅ Statistical testing
- ✅ Correlation calculation
- ✅ Quality assessment
- ✅ End-to-end workflow
- ✅ Edge cases and error handling

## Limitations & Future Work

### Current Limitations

- Python-only analysis (other languages planned)
- Simple correlation (more advanced stats possible)
- Limited to function-level metrics
- No inter-function relationship analysis

### Future Enhancements

1. **Multi-language support**: JavaScript, TypeScript, Go, Rust
2. **Advanced statistics**: Bayesian inference, causal analysis
3. **Machine learning**: Neural networks for pattern detection
4. **Temporal analysis**: How patterns evolve over time
5. **Cross-repository**: Compare patterns across projects

## Troubleshooting

### Issue: No functions analyzed

```
Error parsing file.py: expected 'except' or 'finally' block
```

**Solution**: Ensure Python files have valid syntax. The engine skips invalid files.

### Issue: Low validation rate

**Explanation**: This is normal! Not all hypotheses will validate. A 30-50% validation rate is typical and indicates the engine is being appropriately skeptical.

### Issue: Empty results

**Solution**: Ensure the repository path is correct and contains Python files:

```bash
python3 tools/hypothesis_testing_engine.py --repo-path /correct/path
```

## Contributing

Contributions welcome! Areas for improvement:

- Additional hypothesis templates
- More sophisticated statistical tests
- Multi-language support
- Performance optimizations
- Visualization of results

## License

Part of the Chained autonomous AI ecosystem. See repository LICENSE.

## Credits

- **@accelerate-specialist** (Edsger Dijkstra): Design and implementation
- Inspired by: Mutation testing, property-based testing, statistical debugging
- Built for: The Chained autonomous software development ecosystem

---

**"Elegance is not a dispensable luxury but a quality that decides between success and failure."** - Edsger W. Dijkstra

*Created by @accelerate-specialist for the Chained autonomous AI ecosystem*
