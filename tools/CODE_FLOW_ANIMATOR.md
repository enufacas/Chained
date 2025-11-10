# 🔍 Code Flow Animator

A visual code execution flow animator that traces and visualizes how code executes step-by-step. Part of the Chained autonomous AI development system.

## Overview

The Code Flow Animator analyzes source code and generates interactive visualizations showing:
- Function call sequences
- Variable state changes
- Control flow (conditionals, loops)
- Execution timeline
- Code statistics

## Features

### 🎯 Multi-Language Support
- **Python**: Deep AST-based analysis with full support for functions, classes, variables, loops, and conditionals
- **JavaScript**: Pattern-based analysis detecting functions, control flow, and variable assignments

### 📊 Analysis Capabilities
- Function definitions and calls tracking
- Variable assignment and state changes
- Conditional statements (if/else)
- Loop structures (for/while)
- Return statement tracking
- Control flow path analysis

### 🎨 Visualization
- Interactive HTML reports with clickable elements
- Step-by-step execution display
- Source code highlighting
- Real-time statistics
- Beautiful, responsive design

### 💾 Output Formats
- **JSON**: Machine-readable flow data for programmatic use
- **HTML**: Interactive web-based visualization

## Installation

No installation required! The Code Flow Animator is a standalone Python 3 script with no external dependencies.

```bash
git clone https://github.com/enufacas/Chained.git
cd Chained/tools
```

## Usage

### Basic Usage

```bash
# Analyze a Python file (auto-detects language)
python3 code-flow-animator.py -f script.py

# Analyze JavaScript file
python3 code-flow-animator.py -f app.js -l javascript

# Specify language explicitly
python3 code-flow-animator.py -f code.txt -l python
```

### Output Control

```bash
# Generate both JSON and HTML (default)
python3 code-flow-animator.py -f script.py

# Generate only JSON
python3 code-flow-animator.py -f script.py --format json

# Generate only HTML
python3 code-flow-animator.py -f script.py --format html

# Custom output paths
python3 code-flow-animator.py -f script.py --json data.json --html report.html
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `-f, --file` | Code file to analyze (required) |
| `-l, --language` | Programming language (python, javascript, js) - auto-detected from extension if not specified |
| `--json` | Output JSON file path (default: `{filename}_flow.json`) |
| `--html` | Output HTML report path (default: `{filename}_flow.html`) |
| `--format` | Output format: `json`, `html`, or `both` (default: `both`) |

## Examples

### Example 1: Factorial Calculator

Analyze a Python factorial implementation:

```bash
python3 code-flow-animator.py -f examples/flow_factorial.py
```

**Output:**
- `flow_factorial_flow.json` - Flow data
- `flow_factorial_flow.html` - Interactive visualization

**Sample Analysis:**
- Language: Python
- Total Lines: 45
- Execution Steps: 25
- Functions: 3 (factorial, factorial_iterative, main)
- Control Flow: 4 statements

### Example 2: Bubble Sort

Visualize the bubble sort algorithm:

```bash
python3 code-flow-animator.py -f examples/flow_bubblesort.py
```

Shows nested loop structure and conditional swapping logic.

### Example 3: Binary Search (JavaScript)

Analyze JavaScript code:

```bash
python3 code-flow-animator.py -f examples/flow_binarysearch.js
```

Demonstrates divide-and-conquer approach with conditionals.

## Output Format

### JSON Output

The JSON output contains:

```json
{
  "language": "python",
  "source_lines": ["line1", "line2", ...],
  "steps": [
    {
      "type": "call|assign|condition|loop|return",
      "line": 10,
      "description": "Function 'factorial' defined",
      "variables": {"n": "5"},
      "function": "factorial"
    }
  ],
  "function_calls": [
    {
      "name": "factorial",
      "line": 5,
      "params": ["n"]
    }
  ],
  "control_flow": [
    {
      "type": "if|for|while",
      "line": 7,
      "condition": "n <= 1"
    }
  ],
  "statistics": {
    "total_steps": 25,
    "function_definitions": 3,
    "control_flow_statements": 4,
    "assignments": 10,
    "function_calls": 5,
    "returns": 3
  },
  "metadata": {
    "total_lines": 45,
    "language": "python",
    "analyzer": "CodeFlowAnimator"
  }
}
```

### HTML Output

The HTML report includes:
- Source code panel with line numbers
- Execution steps panel with descriptions
- Interactive elements (click code lines to see related steps)
- Statistics dashboard
- Beautiful, responsive design
- No external dependencies (all CSS/JS embedded)

## How It Works

### Python Analysis

1. **AST Parsing**: Uses Python's built-in `ast` module to parse source code
2. **Tree Walking**: Implements `ast.NodeVisitor` to traverse the abstract syntax tree
3. **Step Extraction**: Captures function definitions, assignments, conditionals, loops, and returns
4. **Flow Building**: Constructs a sequential execution flow with line numbers and context

**Detected Patterns:**
- `FunctionDef` → Function definitions
- `Assign` → Variable assignments
- `If` → Conditional statements
- `For`, `While` → Loop structures
- `Return` → Return statements
- `Call` → Function calls

### JavaScript Analysis

1. **Line-by-Line Parsing**: Reads source code line by line
2. **Pattern Matching**: Uses regular expressions and keyword detection
3. **Context Building**: Extracts function names, variables, and control flow
4. **Flow Assembly**: Constructs execution flow with descriptions

**Detected Patterns:**
- `function`, `=>` → Function definitions
- `const`, `let`, `var`, `=` → Variable assignments
- `if`, `else` → Conditional statements
- `for`, `while` → Loop structures
- `return` → Return statements

## Educational Use Cases

### 1. Learning Programming
Perfect for beginners to understand:
- How code executes sequentially
- Function call and return flow
- Variable state changes
- Control flow logic

### 2. Algorithm Visualization
Great for teaching:
- Sorting algorithms (bubble sort, quick sort)
- Search algorithms (binary search, DFS/BFS)
- Recursive algorithms (factorial, Fibonacci)
- Dynamic programming solutions

### 3. Debugging
Helps identify:
- Logic errors in control flow
- Unexpected variable states
- Missing return statements
- Infinite loop conditions

### 4. Code Review
Assists in:
- Understanding complex code
- Verifying execution paths
- Documenting code behavior
- Explaining algorithms to team members

### 5. Documentation
Generate:
- Interactive code examples
- Execution flow diagrams
- Step-by-step walkthroughs
- Tutorial materials

## Integration

### GitHub Pages

The Code Flow Animator includes a dedicated GitHub Pages site at `docs/flow-animator.html` featuring:
- Feature showcase
- Example visualizations
- Usage documentation
- Interactive examples

Access it at: `https://enufacas.github.io/Chained/flow-animator.html`

### GitHub Actions

Can be integrated into CI/CD workflows:

```yaml
- name: Analyze Code Flow
  run: |
    python3 tools/code-flow-animator.py -f src/main.py
    mv *_flow.html docs/
```

### Programmatic Usage

Use as a Python module:

```python
from code_flow_animator import CodeFlowAnimator

animator = CodeFlowAnimator()

# Analyze code string
flow_data = animator.analyze_code(source_code, 'python')

# Analyze file
flow_data = animator.analyze_file('script.py')

# Generate outputs
animator.save_flow_data(flow_data, 'output.json')
animator.generate_html_report(flow_data, 'report.html')
```

## Limitations

### Current Limitations

1. **Python Indentation**: Generated Python code visualizations use simplified indentation
2. **Dynamic Behavior**: Cannot trace actual runtime execution, only static analysis
3. **Complex Expressions**: Very complex expressions may be simplified in descriptions
4. **Language Coverage**: JavaScript support is pattern-based and may miss edge cases
5. **No Imports**: Import statements are not fully traced
6. **Class Methods**: Limited support for class-based code (focuses on functions)

### Future Enhancements

Potential improvements:
- [ ] Additional language support (Java, C++, Go)
- [ ] Runtime execution tracing
- [ ] Interactive step-through debugging
- [ ] Side-by-side comparison mode
- [ ] Export to other formats (PDF, PNG)
- [ ] Integration with debuggers
- [ ] Performance metrics
- [ ] Memory usage tracking

## Testing

Run the test suite:

```bash
python3 test_code_flow_animator.py
```

Tests cover:
- ExecutionStep creation and serialization
- Python AST analysis
- JavaScript pattern matching
- Control flow detection
- Statistics calculation
- JSON/HTML generation
- Error handling

**Current Test Results:**
```
Running Code Flow Animator Tests...
==================================================
✓ ExecutionStep test passed
✓ Python simple analysis test passed
✓ Python control flow test passed
✓ JavaScript analysis test passed
✓ CodeFlowAnimator test passed
✓ File analysis test passed
✓ JSON output test passed
✓ HTML generation test passed
✓ Statistics calculation test passed
✓ Error handling test passed
==================================================
Results: 10 passed, 0 failed
```

## Contributing

Contributions welcome! Areas for improvement:
- Additional language support
- Enhanced visualization features
- Performance optimizations
- Better error messages
- More examples

## Related Tools

Part of the Chained development toolkit:
- **Code Analyzer**: Self-improving code quality analysis
- **Pattern Matcher**: Cross-repository pattern detection
- **Code Golf Optimizer**: Code size minimization

## License

Part of the Chained autonomous AI development system.

## Resources

- [Live Demo](https://enufacas.github.io/Chained/flow-animator.html)
- [GitHub Repository](https://github.com/enufacas/Chained)
- [Example Visualizations](https://enufacas.github.io/Chained/flow-animator.html#examples)
- [Full Documentation](https://github.com/enufacas/Chained/blob/main/tools/README.md)

---

**Generated by the Chained Perpetual AI Motion Machine** 🤖
