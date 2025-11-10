# 🛠️ Micro Projects

This page documents the various micro projects and tools built within the Chained autonomous system.

## 🔍 Visual Code Execution Flow Animator

A visual code execution flow animator that traces and visualizes how code executes step-by-step. Perfect for learning, debugging, and understanding algorithms!

### Features

- 🎯 **Multi-Language Support**: Python (AST-based) and JavaScript
- 📊 **Interactive Visualizations**: Click-through HTML reports with color-coded steps
- 🔄 **Function Call Tracking**: See the execution flow through functions
- 💾 **Multiple Formats**: JSON data and HTML visualizations
- 🎓 **Educational Tool**: Great for learning and teaching programming

### Quick Start

```bash
# Analyze a Python file
python3 tools/code-flow-animator.py -f script.py

# Analyze JavaScript
python3 tools/code-flow-animator.py -f app.js

# View example visualizations
open docs/flow-animator.html
```

### Example Visualizations

The tool comes with example analyses:
- **Factorial Calculator**: Recursive vs iterative approaches (25 steps, 3 functions)
- **Bubble Sort**: Nested loops and conditional swapping (23 steps, 5 control flow)
- **Binary Search**: Divide-and-conquer algorithm (21 steps, JavaScript)

### Live Demo

Visit the [interactive showcase](https://enufacas.github.io/Chained/flow-animator.html) to explore example visualizations.

For complete documentation, see [`tools/CODE_FLOW_ANIMATOR.md`](../tools/CODE_FLOW_ANIMATOR.md)

---

## 🏌️ Code Golf Optimizer

An AI-powered code golf optimizer that minimizes code while preserving functionality. Perfect for code golf challenges and learning how to write concise code!

### Features

- 🎯 **Multi-Language Support**: Python, JavaScript, and Bash
- 🤖 **Smart Optimizations**: Comment removal, whitespace reduction, variable shortening
- 📊 **Detailed Metrics**: Character counts and reduction percentages
- 🔄 **Automated Reports**: Weekly optimization reports via GitHub Actions

### Quick Start

```bash
# Optimize a Python file
python3 tools/code-golf-optimizer.py -f script.py -l python

# Optimize JavaScript from stdin
echo "function test() { return true; }" | python3 tools/code-golf-optimizer.py -l javascript

# View all examples
ls tools/examples/
```

### Example Optimization

Before (283 chars):
```python
def calculate_sum(number_list):
    """Calculate the sum of numbers"""
    # Initialize total
    total = 0
    
    # Loop through each number
    for number in number_list:
        total = total + number
    
    return total
```

After (146 chars, 48.41% reduction):
```python
def calculate_sum(number_list):
 a = 0
 for number in number_list:
 a = a + number
 return a
```

### Workflow Integration

The Code Golf Optimizer runs automatically:
- **Schedule**: Weekly on Mondays at 10 AM UTC
- **Trigger**: Can be manually triggered via GitHub Actions
- **Output**: Generates optimization reports with metrics

For complete documentation, see [`tools/README.md`](../tools/README.md)

---

## 🔍 Self-Improving Code Analyzer

A self-improving code analyzer that learns from each merge, tracking code patterns and their correlation with successful vs. problematic merges.

### Features

- 🧠 **Learning Algorithm**: Updates pattern correlations based on merge outcomes
- 📊 **Pattern Detection**: Identifies both good and bad code patterns
- 📈 **Trend Analysis**: Tracks code quality metrics over time
- 🤖 **Auto-Integration**: Runs on every merge to main branch
- 💬 **PR Comments**: Posts analysis summaries on pull requests
- 🚨 **Quality Alerts**: Creates issues for significant code quality problems

### Pattern Categories

**Good Patterns** (correlated with successful merges):
- Descriptive variable names
- Comprehensive docstrings
- Error handling (try/except)
- Modular functions (<50 lines)
- Type hints

**Bad Patterns** (correlated with issues):
- Long functions (>50 lines)
- Deep nesting (>4 levels)
- Magic numbers
- Unused imports
- Inconsistent naming

### How It Learns

1. **On each merge**: Analyzes code for patterns
2. **Tracks outcomes**: Records whether merge was successful or had issues
3. **Updates correlations**: Uses exponential moving average (10% learning rate)
4. **Improves suggestions**: Pattern weights adjust based on historical data

### Quick Start

```bash
# Analyze current code and learn from it
python3 tools/code-analyzer.py -d . --learn --success

# Analyze a specific directory
python3 tools/code-analyzer.py -d tools -o report.md

# Analyze and mark as problematic merge
python3 tools/code-analyzer.py -d . --learn --failure

# Run tests
python3 tools/test_code_analyzer.py
```

### Analysis Data

All analysis data is stored in [`analysis/`](../analysis/):
- `patterns.json`: The learning database with pattern correlations
- `merge_*.json`: Individual analysis reports for each merge
- `latest_report.md`: Most recent analysis report

### Workflow Integration

The Code Analyzer runs automatically:
- **Trigger**: On every merge to main branch
- **Action**: Analyzes code, posts PR comments, creates issues if needed
- **Learning**: Updates pattern database with merge outcome

For complete documentation, see [`analysis/README.md`](../analysis/README.md)

---

## 🎯 Pattern Matcher

A flexible pattern matching system for code analysis and documentation generation.

### Features

- 🔍 **Multi-Pattern Support**: Detects various code patterns
- 📝 **Documentation Integration**: Auto-generates documentation
- 🔄 **Extensible**: Easy to add new patterns

### Workflow Integration

The Pattern Matcher runs automatically to help identify code patterns and support other automation tools.

---

## 🔮 Future Micro Projects

The autonomous system may generate new micro projects over time. This page will be updated automatically as new tools and features are developed.

---

**Back to [Main README](../README.md) | [Workflows](./WORKFLOWS.md) | [Learning System](./LEARNING_SYSTEM.md)**
