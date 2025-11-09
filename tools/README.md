# 🛠️ Chained Developer Tools

A collection of AI-powered code analysis and transformation tools.

## Tools

1. **🏌️ Code Golf Optimizer** - Minimize code character count
2. **🔄 Cross-Language Code Translator** - Translate and compare code across languages

---

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

---

# 🔄 Cross-Language Code Translator

An intelligent code translator that converts code between different programming languages and provides comparison tools to analyze differences across language implementations.

## Overview

The Cross-Language Code Translator helps developers:
- Translate code between Python, JavaScript, and Bash
- Compare implementations across different languages
- Understand syntax differences between languages
- Migrate code between programming languages

## Features

- 🔄 **Multi-Language Translation**: Python ↔ JavaScript, Python ↔ Bash, JavaScript ↔ Bash
- 📊 **Code Comparison**: Side-by-side comparison with similarity scores
- 📝 **Translation Notes**: Detailed explanations of transformations applied
- 🔄 **Multiple Output Formats**: Text and JSON
- 🎯 **Bidirectional Translation**: Translate in both directions between language pairs

## Installation

The translator is a standalone Python script with no external dependencies:

```bash
# Make the script executable
chmod +x tools/code-translator.py

# Run directly
./tools/code-translator.py --help
```

## Usage

### Translation

#### Basic Translation

```bash
# Translate Python to JavaScript
python3 tools/code-translator.py translate -f script.py -s python -t javascript

# Translate JavaScript to Python
python3 tools/code-translator.py translate -f script.js -s javascript -t python

# Translate from stdin
echo 'print("Hello")' | python3 tools/code-translator.py translate -s python -t javascript

# Translate Python to Bash
python3 tools/code-translator.py translate -f script.py -s python -t bash
```

#### Advanced Translation Options

```bash
# Output as JSON for programmatic use
python3 tools/code-translator.py translate -f script.py -s python -t javascript --format json

# Save output to a file
python3 tools/code-translator.py translate -f script.py -s python -t javascript -o output.js

# Use short language names (js for javascript, sh for bash)
python3 tools/code-translator.py translate -f script.py -s python -t js
```

### Comparison

#### Basic Comparison

```bash
# Compare Python and JavaScript implementations
python3 tools/code-translator.py compare \
  -f1 calculator.py -l1 python \
  -f2 calculator.js -l2 javascript

# Compare with JSON output
python3 tools/code-translator.py compare \
  -f1 script1.py -l1 python \
  -f2 script2.py -l2 python \
  --format json
```

### Command-Line Options

#### translate command

- `-f, --file`: Input file to translate (or use stdin)
- `-s, --source`: Source language (python, javascript/js, bash/sh)
- `-t, --target`: Target language (python, javascript/js, bash/sh)
- `--format`: Output format (text, json)
- `-o, --output`: Output file (default: stdout)

#### compare command

- `-f1, --file1`: First file to compare
- `-l1, --lang1`: Language of first file
- `-f2, --file2`: Second file to compare
- `-l2, --lang2`: Language of second file
- `--format`: Output format (text, json)
- `-o, --output`: Output file (default: stdout)

## Translation Capabilities

### Python to JavaScript

**Supported Conversions:**
- `print()` → `console.log()`
- `def function_name():` → `function functionName() {}`
- `True`/`False` → `true`/`false`
- `None` → `null`
- `elif` → `else if`
- `f"string {var}"` → `` `string ${var}` ``
- `len(list)` → `list.length`
- Python indentation → JavaScript braces

**Example:**

Python:
```python
def greet(name):
    if name:
        print(f"Hello, {name}!")
    else:
        print("Hello, stranger!")
```

JavaScript:
```javascript
function greet(name) {
    if (name) {
        console.log(`Hello, ${name}!`);
    }
    else {
        console.log("Hello, stranger!");
    }
}
```

### JavaScript to Python

**Supported Conversions:**
- `console.log()` → `print()`
- `function functionName() {}` → `def function_name():`
- `true`/`false` → `True`/`False`
- `null`/`undefined` → `None`
- `else if` → `elif`
- `` `string ${var}` `` → `f"string {var}"`
- `list.length` → `len(list)`
- `var`/`let`/`const` removed
- JavaScript braces → Python indentation

**Example:**

JavaScript:
```javascript
function calculate(x, y) {
    let result = x + y;
    if (result > 10) {
        return true;
    }
    return false;
}
```

Python:
```python
def calculate(x, y):
    result = x + y
    if result > 10:
        return True
    return False
```

### Python/JavaScript to Bash

**Supported Conversions:**
- `print()`/`console.log()` → `echo`
- Adds shebang (`#!/bin/bash`)
- Basic variable assignments

**Note:** Python/JavaScript to Bash translation is basic and best suited for simple scripts. Complex logic may require manual adjustment.

### Bash to Python/JavaScript

**Supported Conversions:**
- `echo` → `print()`/`console.log()`
- Removes shebang
- Basic structure conversion

**Note:** Bash to Python/JavaScript translation is basic and best suited for simple scripts.

## Examples

### Example 1: Calculator Translation

**calculator.py:**
```python
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

result = add(5, 3)
print(f"Result: {result}")
```

**Translate to JavaScript:**
```bash
python3 tools/code-translator.py translate -f calculator.py -s python -t javascript
```

**Output (calculator.js equivalent):**
```javascript
function add(a, b) {
    return a + b;
}

function multiply(a, b) {
    return a * b;
}

result = add(5, 3);
console.log(`Result: ${result}`);
```

### Example 2: Code Comparison

**Compare two implementations:**
```bash
python3 tools/code-translator.py compare \
  -f1 tools/examples/calculator.py -l1 python \
  -f2 tools/examples/calculator.js -l2 javascript
```

**Output:**
```
Comparison: python vs javascript
============================================================

Similarity Score: 1.89%

Differences:
------------------------------------------------------------
--- python code
+++ javascript code
@@ -1,5 +1,5 @@
-def add(a, b):
-    return a + b
+function add(a, b) {
+    return a + b;
+}
```

### Example 3: Batch Translation

```bash
# Translate all Python files in examples directory
for file in tools/examples/*.py; do
    output="${file%.py}.js"
    python3 tools/code-translator.py translate -f "$file" -s python -t javascript -o "$output"
done
```

## Translation Notes

The translator provides detailed notes about transformations applied during translation. These notes include:

- Syntax conversions (e.g., "Converted print() to console.log()")
- Structure changes (e.g., "Converted braces to Python indentation")
- Type conversions (e.g., "Converted True/False to true/false")
- Features requiring manual adjustment

Example output:
```
Translation Notes:
------------------------------------------------------------
  • Converted print() to console.log()
  • Converted def to function
  • Converted True/False to true/false
  • Converted None to null
  • Converted f-strings to template literals
```

## Best Practices

### ✅ Do

- Use for learning language syntax differences
- Use for quick prototyping in different languages
- Review generated code before using in production
- Test translated code thoroughly
- Read translation notes carefully
- Use for simple to moderate complexity code

### ⚠️ Don't

- Use translated code in production without review
- Expect perfect translation of complex logic
- Ignore translation notes and warnings
- Assume all language features translate directly
- Forget to test translated code

## Limitations

- **Complexity**: Works best with simple to moderate complexity code
- **Language Features**: Some language-specific features don't have direct equivalents
- **Idioms**: Language-specific idioms may not translate naturally
- **Libraries**: External library calls are not translated
- **Error Handling**: Exception handling may need manual adjustment
- **Advanced Features**: Decorators, generators, async/await may need manual conversion
- **Context**: Cannot understand complex business logic or domain-specific requirements

## Testing

Run the translator test suite:

```bash
# Run all translator tests
python3 tools/test_translator.py
```

Test on provided examples:

```bash
# Test Python to JavaScript translation
python3 tools/code-translator.py translate -f tools/examples/calculator.py -s python -t javascript

# Test comparison
python3 tools/code-translator.py compare \
  -f1 tools/examples/calculator.py -l1 python \
  -f2 tools/examples/calculator.js -l2 javascript
```

## Use Cases

1. **Learning**: Understand how concepts translate between languages
2. **Migration**: Get a starting point when porting code to a new language
3. **Comparison**: Analyze different language approaches to the same problem
4. **Prototyping**: Quickly sketch out code in multiple languages
5. **Documentation**: Generate example code in multiple languages

## Future Enhancements

Potential improvements for future versions:
- Support for more languages (Ruby, Go, Rust, etc.)
- Better handling of language-specific features
- Improved indentation and formatting
- Support for class and object-oriented translations
- Enhanced error handling translation
- Library mapping (e.g., requests → axios)

## License

Part of the Chained autonomous AI development system.

## Related Resources

- [Code Golf Stack Exchange](https://codegolf.stackexchange.com/)
- [Tips for golfing in Python](https://codegolf.stackexchange.com/questions/54/tips-for-golfing-in-python)
- [Tips for golfing in JavaScript](https://codegolf.stackexchange.com/questions/2682/tips-for-golfing-in-javascript)

---

*Generated by the Chained AI Code Golf Optimizer*
