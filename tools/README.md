# 🏌️ AI Code Golf Optimizer

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
