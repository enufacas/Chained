# 🎓 AI Test Generator Tutorial

**by @investigate-champion**

Learn how to use the AI Test Generator to create comprehensive test suites with automatic edge case detection.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding Edge Cases](#understanding-edge-cases)
3. [Interpreting Test Results](#interpreting-test-results)
4. [Customizing Edge Cases](#customizing-edge-cases)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Quick Start

### Generate Tests for a File

```bash
# Basic usage - generates tests in tests/ directory
python tools/ai_test_generator.py tools/my_utility.py

# Custom output location
python tools/ai_test_generator.py tools/my_utility.py tests/test_custom_name.py
```

### Run Generated Tests

```bash
python tests/test_ai_gen_my_utility.py
```

### Example Output

```
======================================================================
🤖 AI-Powered Test Suite Generator
   by @investigate-champion
======================================================================

Source file: tools/my_utility.py
Output file: tests/test_ai_gen_my_utility.py

📚 Learning from existing test patterns...
  ✅ Analyzed 75 test files

🔍 Analyzing my_utility.py...
  ✅ Found 8 testable functions
  ✅ Generated 45 test cases
  📝 Wrote test suite to tests/test_ai_gen_my_utility.py

======================================================================
✨ Test Generation Complete!
======================================================================

Generated 45 test cases
Test file: tests/test_ai_gen_my_utility.py

To run the tests:
  python tests/test_ai_gen_my_utility.py
```

## Understanding Edge Cases

The AI Test Generator detects and tests multiple categories of edge cases:

### 1. Boundary Conditions

Tests values at the limits:

```python
# For integers
test_function_param_zero()       # Value: 0
test_function_param_max_int()    # Value: sys.maxsize
test_function_param_negative()   # Value: -1

# For strings
test_function_param_empty_string()       # Value: ""
test_function_param_very_long_string()   # Value: "x" * 10000
```

### 2. Special Characters

Tests non-standard input:

```python
test_function_param_whitespace_only()    # Value: "   \t\n"
test_function_param_special_characters() # Value: "!@#$%^&*()"
test_function_param_unicode_characters() # Value: "你好世界🌍"
```

### 3. Security Tests

Tests malicious inputs:

```python
test_function_param_sql_injection()  # Value: "'; DROP TABLE users--"
test_function_param_script_tag()     # Value: "<script>alert('xss')</script>"
```

### 4. Null/None Handling

Tests missing values:

```python
test_function_param_param_none()  # Value: None
```

### 5. Special Values (Floats)

Tests mathematical edge cases:

```python
test_function_param_infinity()      # Value: float('inf')
test_function_param_neg_infinity()  # Value: float('-inf')
test_function_param_nan()           # Value: float('nan')
```

### 6. Collection Edge Cases

Tests empty and extreme collections:

```python
# Lists
test_function_param_empty_list()       # Value: []
test_function_param_single_item_list() # Value: [1]
test_function_param_large_list()       # Value: list(range(100000))

# Dictionaries
test_function_param_empty_dict()       # Value: {}
test_function_param_nested_dict()      # Value: {'a': {'b': {'c': 1}}}
```

## Interpreting Test Results

### Success Cases ✅

```
📋 Testing function: process_text
----------------------------------------------------------------------
  ✅ test_process_text_happy_path: PASSED
  ✅ test_process_text_text_empty_string: PASSED
  ✅ test_process_text_text_whitespace_only: PASSED
```

**Meaning**: Your function correctly handles these edge cases!

### Failure Cases ❌

```
📋 Testing function: calculate_sum
----------------------------------------------------------------------
  ❌ test_calculate_sum_a_zero: FAILED - missing 1 required positional argument: 'b'
```

**Meaning**: The generated test has a bug OR your function doesn't handle this edge case correctly.

**Action**: Review the test and decide:
1. Is this a test generation issue? → Fix the test
2. Is this a real edge case your function should handle? → Fix your function

### Mixed Results

```
======================================================================
📊 Test Summary
======================================================================
Total tests: 36
Passed: 20 ✅
Failed: 16 ❌
Success rate: 55.6%
```

**Interpretation**:
- 55.6% success means your function handles many edge cases well
- 44.4% failures identify areas for improvement
- Each failure is a potential bug or unhandled edge case

## Customizing Edge Cases

### Adding New Edge Case Patterns

Edit `tools/ai_test_generator.py`:

```python
class EdgeCaseDetector:
    def __init__(self):
        self.edge_case_patterns = {
            'string': [
                # Add your custom edge case
                EdgeCase(
                    'custom_case',
                    'Description of the case',
                    'test_value',
                    'Expected behavior',
                    'category_name'
                ),
                # ... existing cases
            ]
        }
```

### Adding New Type Support

```python
def detect_edge_cases_for_param(self, param_name: str, param_type: str):
    type_mapping = {
        'str': 'string',
        'CustomType': 'custom',  # Add your type
        # ...
    }
```

## Best Practices

### 1. Review Generated Tests

Always review tests before using them in production:

```python
# Generated test
def test_function_param_empty_string():
    """Test with empty string edge case."""
    text = ''
    result = process_text(text)
    assert result is not None  # Generic assertion
```

**Improve to:**

```python
def test_function_param_empty_string():
    """Test with empty string edge case."""
    text = ''
    result = process_text(text)
    assert result == '', "Empty string should return empty string"  # Specific
```

### 2. Use for Initial Test Coverage

Use AI-generated tests as a starting point:

1. Generate tests ✅
2. Review and fix test logic ✅
3. Add domain-specific tests ✅
4. Add integration tests ✅

### 3. Iterate and Refine

```bash
# Generate initial tests
python tools/ai_test_generator.py tools/my_util.py

# Run and review
python tests/test_ai_gen_my_util.py

# Fix issues in your code
# Regenerate tests
python tools/ai_test_generator.py tools/my_util.py

# Run again to verify
python tests/test_ai_gen_my_util.py
```

### 4. Document Edge Case Decisions

When you decide NOT to handle an edge case:

```python
def process_text(text: str) -> str:
    """
    Process text.
    
    Note: Does not handle None - caller must provide valid string.
    This is by design for performance reasons.
    """
    return text.strip()  # Intentionally not checking for None
```

## Troubleshooting

### Problem: Import Errors

```
Warning: Could not import from my_utility: No module named 'my_utility'
```

**Solution**: The test file needs the correct import path. Edit the generated test:

```python
# If source is in tools/
from tools.my_utility import *

# If source is in examples/
from examples.my_utility import *

# If source is at root
from my_utility import *
```

### Problem: Too Many Test Failures

```
Success rate: 15.2%
```

**Possible causes**:
1. Edge case tests are calling function incorrectly
2. Your function has many unhandled edge cases (good to know!)
3. Test generation needs improvement for your specific code

**Solution**:
1. Review a few failing tests
2. Determine if it's a test issue or code issue
3. Fix accordingly

### Problem: Not All Functions Detected

```
✅ Found 2 testable functions
```

But you have 10 functions!

**Cause**: Generator skips:
- Private functions (`_private`)
- Test functions (`test_*`)
- Class methods (currently)

**Solution**: For class methods, extract them to module-level functions or wait for class support (coming soon).

### Problem: Generated Tests Have Syntax Errors

```
SyntaxError: unterminated f-string literal
```

**Solution**: This is a bug in test generation. Please:
1. Report it to the team
2. Manually fix the generated test file
3. Regenerate after the fix is deployed

## Advanced Usage

### Programmatic API

```python
from pathlib import Path
from tools.ai_test_generator import AITestGenerator, EdgeCaseDetector

# Create generator
generator = AITestGenerator()

# Customize edge cases
custom_detector = EdgeCaseDetector()
# Add custom patterns...
generator.detector = custom_detector

# Generate tests
tests = generator.generate_test_suite(
    Path('tools/my_util.py'),
    Path('tests/test_custom.py')
)

# Analyze results
for test in tests:
    print(f"Generated: {test.test_name}")
    print(f"  Covers: {len(test.edge_cases_covered)} edge cases")
```

### Batch Generation

Generate tests for multiple files:

```bash
#!/bin/bash
# generate_all_tests.sh

for file in tools/*.py; do
    echo "Generating tests for $file"
    python tools/ai_test_generator.py "$file"
done
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test-generation.yml
- name: Generate and run AI tests
  run: |
    python tools/ai_test_generator.py tools/new_feature.py
    python tests/test_ai_gen_new_feature.py
```

## Tips from @investigate-champion

> **"The best tests are those that find bugs before users do."** 🎯

1. **Don't Ignore Failures**: Each failure is a learning opportunity
2. **Edge Cases Matter**: 80% of bugs come from 20% of edge cases
3. **Iterate Continuously**: Regenerate tests as your code evolves
4. **Learn from Patterns**: Look for common edge case patterns in failures
5. **Document Decisions**: Record why you chose to handle (or not handle) edge cases

## Example: Complete Workflow

### Step 1: Write Your Function

```python
# tools/string_utils.py
def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename
```

### Step 2: Generate Tests

```bash
python tools/ai_test_generator.py tools/string_utils.py
```

Output:
```
✅ Found 1 testable function
✅ Generated 7 test cases
```

### Step 3: Run Tests

```bash
python tests/test_ai_gen_string_utils.py
```

Output:
```
📋 Testing function: sanitize_filename
----------------------------------------------------------------------
  ✅ test_sanitize_filename_happy_path: PASSED
  ❌ test_sanitize_filename_filename_empty_string: FAILED
  ✅ test_sanitize_filename_filename_special_characters: PASSED
  ❌ test_sanitize_filename_filename_filename_none: FAILED
```

### Step 4: Fix Issues

```python
def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename."""
    # Handle None
    if filename is None:
        return 'unnamed'
    
    # Handle empty
    if not filename:
        return 'unnamed'
    
    # Sanitize
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename
```

### Step 5: Retest

```bash
python tests/test_ai_gen_string_utils.py
```

Output:
```
Total tests: 7
Passed: 7 ✅
Failed: 0 ❌
Success rate: 100.0%
```

✨ Perfect!

## Learn More

- **Main README**: `tools/AI_TEST_GENERATOR_README.md`
- **Source Code**: `tools/ai_test_generator.py`
- **Examples**: `examples/demo_utilities.py` and `tests/test_ai_gen_demo.py`

---

*Tutorial crafted with analytical rigor by **@investigate-champion*** 🎯
