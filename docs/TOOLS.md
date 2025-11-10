# 🛠️ Development Tools

## 🏌️ Code Golf Optimizer

Chained includes an AI-powered code golf optimizer that minimizes code while preserving functionality. Perfect for code golf challenges and learning how to write concise code!

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

For complete documentation, see [`tools/README.md`](../tools/README.md)

## 🔍 Self-Improving Code Analyzer

Chained includes a self-improving code analyzer that learns from each merge, tracking code patterns and their correlation with successful vs. problematic merges.

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

For complete documentation, see [`analysis/README.md`](../analysis/README.md)

---

[← Learning](LEARNING.md) | [Back to README](../README.md) | [Monitoring →](MONITORING.md)
