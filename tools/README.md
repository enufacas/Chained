# 🛠️ Chained Development Tools

A collection of intelligent development tools for the Chained autonomous AI system.

## Available Tools

### 🏭 Agent Definition Validator

A comprehensive validation tool for GitHub Copilot custom agent definitions.

**Purpose:** Ensure all agent definitions in `.github/agents/` follow the GitHub Copilot custom agents convention and maintain consistency across the agent ecosystem.

**Quick Start:**
```bash
# Validate all agent definitions
python3 tools/validate-agent-definition.py

# Validate a single agent file
python3 tools/validate-agent-definition.py -f .github/agents/create-guru.md

# Strict mode (treat warnings as errors)
python3 tools/validate-agent-definition.py --strict

# Quiet mode (only show errors)
python3 tools/validate-agent-definition.py --quiet
```

**What It Validates:**
- YAML frontmatter structure and syntax
- Required fields: `name` and `description`
- Filename matches agent name (kebab-case convention)
- Markdown body structure and recommended sections
- Tool list format and content
- Overall convention compliance

**Use Case:** Run this tool before committing agent definition changes to ensure they follow the GitHub Copilot custom agents convention. Integrate into CI/CD pipelines for automated validation.

**Infrastructure Innovation:** Built by the create-guru agent to demonstrate infrastructure-building capabilities with elegant validation logic and beautiful terminal output.

---

### 🔍 Issue Assignment Inspector

Inspect GitHub issue assignments to discover custom agent actor IDs for direct API assignment.

**Purpose:** When you assign a custom agent via the GitHub UI, this tool examines the assignment through the API to discover the agent's actor ID, which can then be used for programmatic assignment.

**Quick Start:**
```bash
# Inspect a specific issue's assignment history
export GH_TOKEN="your_github_token"
python3 tools/inspect-issue-assignment.py enufacas Chained 42
```

**What It Shows:**
- Current assignees with their actor IDs and types
- Assignment timeline (who assigned what, when)
- Detection of custom agents vs generic Copilot
- Actor IDs that can be used for direct API assignment
- Actionable insights for enabling direct assignment

**Use Case:** You assigned bug-hunter agent via UI to an issue. Run this tool to see the actor ID that was used, then use that ID for future programmatic assignments.

---

### 📋 Agent Actor ID Lister

List all custom agents and their corresponding actor IDs from the GitHub API.

**Purpose:** Query the GitHub API to see which custom agents have separate actor IDs that can be used for direct assignment.

**Quick Start:**
```bash
# List all agents and their actor IDs
export GH_TOKEN="your_github_token"
python3 tools/list-agent-actor-ids.py enufacas Chained
```

**What It Shows:**
- All custom agents found in `.github/agents/`
- Which agents have actor IDs in the GitHub API
- Actor ID mapping for each agent
- Summary of direct assignment capabilities

**Use Case:** Quickly see all available custom agents and which ones can be directly assigned via API.

---

### 📊 Code Readability Scorer

An intelligent code quality analyzer that scores code readability and provides actionable improvement suggestions.

**Purpose:** Analyze Python code to measure readability across multiple dimensions and get specific, prioritized suggestions for improvement.

⚡ **Performance:** Optimized with single-pass AST traversal (2.4x faster) - see [Performance Optimization](./PERFORMANCE_OPTIMIZATION.md)

**Quick Start:**
```bash
# Analyze a single file
python3 tools/readability-scorer.py -f myfile.py

# Analyze a directory
python3 tools/readability-scorer.py -d ./src

# Generate markdown report
python3 tools/readability-scorer.py -d ./src --format markdown -o report.md

# Output JSON for automation
python3 tools/readability-scorer.py -f myfile.py --format json

# Quality gate (exit 1 if score below threshold)
python3 tools/readability-scorer.py -f myfile.py --min-score 80
```

**What It Analyzes:**
- 📝 **Naming Quality (25%)**: Variable/function names, conventions, clarity
- 🧩 **Complexity (25%)**: Cyclomatic complexity, nesting depth, function length
- 📚 **Documentation (20%)**: Docstrings, parameter docs, completeness
- ✨ **Formatting (15%)**: Line length, indentation, whitespace
- 🏗️ **Structure (15%)**: Import organization, global variables

**Features:**
- 0-100 scoring system with letter grades (A-F)
- Category-specific scores with visual progress bars
- Actionable suggestions with priority levels (High, Medium, Low)
- Line-specific feedback with improvement examples
- JSON and Markdown report formats
- Quality gate support for CI/CD integration
- Comprehensive metrics and statistics

**Use Cases:**
- Code reviews - Quickly assess code quality
- CI/CD pipelines - Enforce quality standards
- Pre-commit hooks - Catch issues before commit
- Team standards - Maintain consistent code quality
- Learning - Get feedback on code improvements

[📖 Full Documentation](./READABILITY_SCORER.md)

---

### 🔬 Self-Improving Code Analyzer

An intelligent code pattern analyzer that learns from merge outcomes to continuously improve code quality assessment.

**Purpose:** Analyze code patterns, track correlations with successful merges, and build institutional knowledge about what works.

⚡ **Performance:** Optimized with single-pass AST traversal achieving **2.4x speedup** - see [Performance Optimization](./PERFORMANCE_OPTIMIZATION.md)

**Quick Start:**
```bash
# Analyze a single Python file
python3 tools/code-analyzer.py -f myfile.py

# Analyze entire directory
python3 tools/code-analyzer.py -d ./src

# Learn from a successful merge
python3 tools/code-analyzer.py -d . --learn --success

# Learn from a problematic merge
python3 tools/code-analyzer.py -d . --learn --failure
```

**What It Analyzes:**
- ✅ **Good Patterns**: Descriptive names, docstrings, error handling, type hints
- ⚠️ **Bad Patterns**: Long functions, deep nesting, magic numbers, unused imports
- 📈 **Learning**: Tracks correlation between patterns and merge success
- 🧠 **Adaptive**: Updates pattern database based on outcomes

**Features:**
- Single-pass AST traversal for optimal performance (2.4x faster)
- Pattern correlation tracking with merge outcomes
- Persistent learning database in `analysis/patterns.json`
- Detailed reports with recommendations
- Linear scalability (O(n) complexity)

**Performance Benchmarks:**
```
Small file (10 functions):     2.3 ms  (435 files/sec)
Medium file (50 functions):   11.4 ms  ( 88 files/sec)
Large file (150 functions):   34.6 ms  ( 29 files/sec)
Very large (300 functions):   70.3 ms  ( 14 files/sec)
Scalability factor: 1.02 (near-perfect linear scaling)
```

**Use Cases:**
- CI/CD quality gates - Enforce pattern standards
- Code review automation - Flag anti-patterns
- Team learning - Build knowledge base of effective patterns
- Performance monitoring - Track analyzer efficiency

**Benchmark Tool:**
```bash
# Run comprehensive performance benchmark
python3 tools/benchmark_code_analyzer.py
```

[📖 Performance Documentation](./PERFORMANCE_OPTIMIZATION.md)

---

### 🏛️ AI Code Archaeologist

An intelligent tool that analyzes git history to document legacy decisions, architectural evolution, and technical debt.

**Features:**
- Git history analysis to understand code decisions
- Automatic categorization of commits (architectural, features, bug fixes, debt)
- Decision extraction from commit messages
- Technical debt tracking (TODOs, FIXMEs, workarounds)
- Architectural evolution timeline
- Human-readable markdown reports
- Automated weekly analysis via GitHub Actions

**Quick Start:**
```bash
# Analyze last 100 commits
python3 tools/code-archaeologist.py -n 100

# Analyze commits from last month
python3 tools/code-archaeologist.py --since "1 month ago"

# Generate JSON report
python3 tools/code-archaeologist.py -n 50 --format json

# Save report to file
python3 tools/code-archaeologist.py -n 100 -o archaeology_report.md
```

**What It Does:**
- 📜 **Documents Legacy Decisions**: Extracts "why" from commit messages
- 🏗️ **Tracks Architecture Evolution**: Shows how design changed over time
- ⚠️ **Identifies Technical Debt**: Finds TODOs, FIXMEs, and workarounds
- 📊 **Provides Statistics**: Commits by category, top contributors, most changed files
- 💡 **Gives Recommendations**: Actionable insights for improvement

**Command-Line Options:**
- `-d, --directory`: Repository directory to analyze (default: current)
- `-n, --max-commits`: Maximum commits to analyze (default: 100)
- `--since`: Only analyze commits since date (e.g., "2023-01-01", "1 month ago")
- `-o, --output`: Output file for report (default: stdout)
- `--format`: Output format - text or json (default: text)

**Example Output:**
```markdown
# 🏛️ Code Archaeology Report

## 📊 Summary
- Total commits analyzed: 100
- Architectural decisions found: 12
- Technical debt items found: 8

## 🏗️ Architectural Decisions
1. **Decided to move config to separate file because it improves modularity**
   - Commit: `abc123d`
   - Date: 2024-01-15

## ⚠️ Technical Debt
1. **TODO: Fix this workaround for the database connection**
   - Commit: `def456e`
   - Date: 2024-02-20
   - Files: utils.py
```

---

### 🔍 Cross-Repository Pattern Matcher
An intelligent best practices analyzer that detects anti-patterns, security issues, and code quality problems across multiple programming languages.

**Features:**
- Multi-language support (Python, JavaScript, Bash, YAML)
- Security analysis (hardcoded secrets, SQL injection, unsafe eval)
- Cross-repository analysis via GitHub API
- Automated weekly reports via GitHub Actions
- Detailed categorized findings

**Quick Start:**
```bash
# Scan entire repository
python3 tools/pattern-matcher.py -d .

# Analyze multiple GitHub repositories
python3 tools/cross-repo-analyzer.py --search "language:python topic:ml" --max 5

# Get statistics
python3 tools/pattern-matcher.py -d . --stats
```

[📖 Full Documentation](./PATTERN_MATCHER.md)

---

### 🏌️ AI Code Golf Optimizer

An intelligent code optimizer that minimizes code character count while preserving functionality - perfect for code golf challenges!

## Overview

The AI Code Golf Optimizer analyzes your code and applies various optimization techniques to reduce its size. It supports multiple programming languages and provides detailed reports on the optimizations applied.

## Features

- 🎯 **Multi-Language Support**: Python, JavaScript, and Bash
- 🤖 **AI-Powered Optimizations**: Intelligent pattern recognition
- 📊 **Detailed Metrics**: Character counts, reduction percentages, and applied optimizations
- 🔄 **Multiple Output Formats**: Text and JSON
- 📁 **Batch Processing**: Optimize multiple files at once
- ⚡ **Automated Workflow**: Weekly optimization reports via GitHub Actions

## Installation

The optimizer is a standalone Python script with no external dependencies:

```bash
# Make the script executable
chmod +x tools/code-golf-optimizer.py

# Run directly
./tools/code-golf-optimizer.py --help
```

## Usage

### Basic Usage

```bash
# Optimize a Python file
python3 tools/code-golf-optimizer.py -f script.py -l python

# Optimize JavaScript from stdin
echo "function test() { return true; }" | python3 tools/code-golf-optimizer.py -l javascript

# Optimize a bash script
python3 tools/code-golf-optimizer.py -f deploy.sh -l bash
```

### Advanced Options

```bash
# Output as JSON for programmatic use
python3 tools/code-golf-optimizer.py -f script.py -l python --format json

# Save output to a file
python3 tools/code-golf-optimizer.py -f script.py -l python -o results.txt

# Process all Python files in a directory
for file in examples/*.py; do
    python3 tools/code-golf-optimizer.py -f "$file" -l python
done
```

### Command-Line Options

- `-f, --file`: Input file to optimize
- `-l, --language`: Programming language (python, javascript, js, bash, sh)
- `--format`: Output format (text, json)
- `-o, --output`: Output file (default: stdout)

## Optimization Techniques

### Python Optimizations

1. **Comment Removal**: Removes all `#` comments and docstrings
2. **Whitespace Reduction**: Eliminates unnecessary blank lines and spaces
3. **Boolean Simplification**: Converts `True`/`False` to `1`/`0`
4. **Variable Shortening**: Renames long variables to single characters
5. **Syntax Simplification**: Removes unnecessary parentheses

### JavaScript Optimizations

1. **Comment Removal**: Removes `//` and `/* */` comments
2. **Whitespace Reduction**: Minimizes spaces and blank lines
3. **Boolean Simplification**: Converts `true`/`false` to `!0`/`!1`
4. **Function Optimization**: Suggests arrow function conversions

### Bash Optimizations

1. **Comment Removal**: Removes `#` comments
2. **Whitespace Reduction**: Eliminates unnecessary spaces
3. **Blank Line Removal**: Removes empty lines

## Examples

### Example: Fibonacci Optimization

**Before** (979 characters):
```python
#!/usr/bin/env python3
"""
Fibonacci sequence generator
Generates the first N fibonacci numbers
"""

def generate_fibonacci(count):
    """
    Generate fibonacci sequence
    
    Args:
        count: Number of fibonacci numbers to generate
        
    Returns:
        List of fibonacci numbers
    """
    # Handle edge cases
    if count <= 0:
        return []
    elif count == 1:
        return [0]
    
    # Initialize the sequence with first two numbers
    fibonacci_sequence = [0, 1]
    
    # Generate remaining numbers
    while len(fibonacci_sequence) < count:
        # Calculate next number by adding last two
        next_number = fibonacci_sequence[-1] + fibonacci_sequence[-2]
        fibonacci_sequence.append(next_number)
    
    return fibonacci_sequence


# Test the function
if __name__ == "__main__":
    number_of_terms = 10
    result = generate_fibonacci(number_of_terms)
    print(f"First {number_of_terms} Fibonacci numbers:")
    print(result)
```

**After** (290 characters, 70.38% reduction):
```python
def generate_fibonacci(count):
 if count <= 0:
 return []
 elif count == 1:
 return [0]
 a = [0, 1]
 while len(a) < count:
 b = a[-1] + a[-2]
 a.append(b)
 return a
if __name__ == "__main__":
 c = 10
 result = generate_fibonacci(c)
 print(f"First {c} Fibonacci numbers:")
 print(result)
```

### Example: JavaScript Factorial

**Before** (1068 characters):
```javascript
#!/usr/bin/env node
/**
 * Factorial calculator
 * Calculates the factorial of a number
 */

function factorial(number) {
    /**
     * Calculate factorial of a number
     * 
     * @param {number} number - The number to calculate factorial for
     * @returns {number} The factorial result
     */
    
    // Base case: factorial of 0 or 1 is 1
    if (number <= 1) {
        return 1;
    }
    
    // Recursive case: n! = n * (n-1)!
    return number * factorial(number - 1);
}
```

**After** (544 characters, 49.06% reduction):
```javascript
#!/usr/bin/env node
function factorial(number) {
 if (number <= 1) {
 return 1;
 }
 return number * factorial(number - 1);
}
function factorialIterative(number) {
 let result = 1;
 for (let i = 2; i <= number; i++) {
 result = result * i;
 }
 return result;
}
```

## GitHub Actions Integration

The optimizer runs automatically every Monday at 10 AM UTC, generating optimization reports for all example files.

### Manual Trigger

You can trigger the workflow manually from the Actions tab:

1. Go to **Actions** → **Code Golf Optimizer**
2. Click **Run workflow**
3. Optionally specify a file path and language
4. View the generated optimization report

### Workflow Features

- Optimizes all example files
- Generates detailed reports with metrics
- Creates GitHub issues with optimization results
- Tracks total character savings across all files

## Best Practices

### ✅ Do

- Test optimized code to ensure it still works correctly
- Use for code golf competitions and challenges
- Review suggested optimizations before applying
- Keep original code for reference
- Use version control to track changes

### ⚠️ Don't

- Use optimized code in production without thorough testing
- Apply all optimizations blindly (some may break functionality)
- Forget about code readability for production code
- Rely solely on automatic optimization without manual review

## Tips for Manual Optimization

1. **Remove unnecessary imports**: Only import what you need
2. **Use list comprehensions**: More compact than loops
3. **Leverage built-in functions**: `sum()`, `map()`, `filter()` etc.
4. **Avoid intermediate variables**: Chain operations when possible
5. **Use shorter variable names**: Single letters for code golf
6. **Remove type hints**: Save characters (but lose clarity)
7. **Combine statements**: Use semicolons in Python (carefully!)
8. **Use ternary operators**: Instead of if-else blocks

## Limitations

- **Safety**: Some optimizations may change behavior in edge cases
- **Readability**: Optimized code is harder to understand
- **Maintainability**: Shortened variable names reduce clarity
- **Language Features**: Not all language-specific tricks are implemented
- **Context Awareness**: Cannot understand complex business logic
- **Python Indentation**: Aggressive whitespace reduction may break Python's indentation requirements - optimized code may need manual indentation adjustment for proper execution
- **Testing Required**: Always test optimized code before use, as optimizations are heuristic-based and may not preserve all functionality in complex cases

## Contributing

To add support for a new language or optimization technique:

1. Add a new method to the `CodeGolfOptimizer` class
2. Register it in the `self.optimizations` dictionary
3. Add example files for testing
4. Update documentation

## Testing

Run the optimizer on the provided examples:

```bash
# Test Python optimization
python3 tools/code-golf-optimizer.py -f tools/examples/fibonacci.py -l python

# Test JavaScript optimization
python3 tools/code-golf-optimizer.py -f tools/examples/factorial.js -l javascript

# Test Bash optimization
python3 tools/code-golf-optimizer.py -f tools/examples/backup.sh -l bash
```

## License

Part of the Chained autonomous AI development system.

## Related Resources

- [Code Golf Stack Exchange](https://codegolf.stackexchange.com/)
- [Tips for golfing in Python](https://codegolf.stackexchange.com/questions/54/tips-for-golfing-in-python)
- [Tips for golfing in JavaScript](https://codegolf.stackexchange.com/questions/2682/tips-for-golfing-in-javascript)

---

*Generated by the Chained AI Code Golf Optimizer*
