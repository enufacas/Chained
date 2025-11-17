# 🎯 AI Test Generator - Quick Reference

**by @investigate-champion**

One-page reference for the AI-powered test suite generator with edge case detection.

## Installation

```bash
# No installation needed - uses Python standard library only
chmod +x tools/ai_test_generator.py
```

## Basic Commands

```bash
# Generate tests for a file
python tools/ai_test_generator.py <source_file>

# Specify output location
python tools/ai_test_generator.py <source_file> <output_file>

# Example
python tools/ai_test_generator.py tools/my_util.py tests/test_my_util.py

# Run generated tests
python tests/test_ai_gen_my_util.py
```

## Edge Case Categories

| Category | Examples | Count |
|----------|----------|-------|
| **Boundary** | Empty, zero, max/min values | High |
| **Special Char** | Unicode, symbols, whitespace | Medium |
| **Security** | SQL injection, XSS | Critical |
| **Null** | None values | High |
| **Special Value** | Infinity, NaN | Low |
| **Complex** | Nested structures | Medium |
| **Empty** | Empty collections | High |

## Type-Specific Edge Cases

### String Parameters
- ✅ Empty string (`""`)
- ✅ Whitespace only (`"   \t\n"`)
- ✅ Very long (10,000+ chars)
- ✅ Special chars (`!@#$%^&*()`)
- ✅ Unicode (`你好世界🌍`)
- ✅ SQL injection (`'; DROP TABLE--`)
- ✅ XSS attempt (`<script>...</script>`)

### Numeric Parameters
- ✅ Zero (`0`, `0.0`)
- ✅ Negative (`-1`, `-1.5`)
- ✅ Max/Min (`sys.maxsize`, `-sys.maxsize-1`)
- ✅ Infinity (`float('inf')`, `float('-inf')`)
- ✅ NaN (`float('nan')`)

### Collection Parameters
- ✅ Empty (`[]`, `{}`)
- ✅ Single item (`[1]`, `{'k': 'v'}`)
- ✅ Large (100,000+ items)
- ✅ Nested structures

### Boolean Parameters
- ✅ True and False explicitly

### All Parameters
- ✅ None/null value (unless Optional)

## Test Structure

Generated tests follow this pattern:

```python
def test_function_param_edge_case():
    """
    Test <function> with edge case: <description>
    
    Edge case: <expected_behavior>
    Category: <category>
    """
    # Edge case input
    param = <edge_value>
    
    try:
        # Call function
        result = function_name(param)
        
        # Verify
        assert result is not None
        print("  ✅ test_name: PASSED")
        return True
    except Exception as e:
        print("  ❌ test_name: FAILED - {e}")
        return False
```

## Interpreting Results

### Success Rate Guide
- **90-100%**: Excellent edge case handling ✅
- **70-89%**: Good, minor issues 👍
- **50-69%**: Fair, needs improvement ⚠️
- **<50%**: Poor, many edge cases unhandled ❌

### Common Failures
1. **Missing parameters**: Test needs all required args
2. **Type errors**: Function expects different type
3. **ValueError**: Function doesn't handle edge value
4. **AttributeError**: None passed where object expected

## Customization

### Add Custom Edge Cases

Edit `tools/ai_test_generator.py`:

```python
class EdgeCaseDetector:
    def __init__(self):
        self.edge_case_patterns = {
            'string': [
                EdgeCase(
                    name='my_case',
                    description='My custom case',
                    input_value='test',
                    expected_behavior='Should handle gracefully',
                    category='custom'
                ),
                # ... existing cases
            ]
        }
```

### Support New Types

```python
type_mapping = {
    'str': 'string',
    'MyType': 'my_type',  # Add here
    # ...
}

# Then add patterns for 'my_type'
self.edge_case_patterns['my_type'] = [
    # Your edge cases
]
```

## Batch Operations

```bash
# Generate tests for all files in directory
./tools/generate_tests_batch.sh tools/

# Run all generated tests
for f in tests/test_ai_gen_*.py; do python3 $f; done

# Count total tests
grep -r "def test_" tests/test_ai_gen_*.py | wc -l
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Generate AI Tests
  run: python tools/ai_test_generator.py src/new_module.py

- name: Run AI Tests  
  run: python tests/test_ai_gen_new_module.py
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
changed_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
for file in $changed_files; do
    python tools/ai_test_generator.py "$file" || true
done
```

## Best Practices

### ✅ DO
- Review generated tests before committing
- Add domain-specific tests manually
- Regenerate after significant code changes
- Document why edge cases are handled/not handled
- Use as starting point, not final solution

### ❌ DON'T
- Blindly commit generated tests
- Rely only on generated tests
- Ignore test failures without investigation
- Skip reviewing edge case handling
- Generate tests for already well-tested code

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Import errors | Fix import path in generated test |
| Low success rate | Review failing tests, fix code or tests |
| No functions found | Check function naming (no `_` prefix or `test_` prefix) |
| Syntax errors | Report bug, manually fix generated file |
| Too many tests | Reduce edge cases per parameter (edit generator) |

## Command Cheat Sheet

```bash
# Single file
python tools/ai_test_generator.py tools/util.py

# With output
python tools/ai_test_generator.py tools/util.py tests/test_util.py

# Batch generate
./tools/generate_tests_batch.sh tools/

# Run single test
python tests/test_ai_gen_util.py

# Run all AI tests
for f in tests/test_ai_gen_*.py; do python3 $f && echo "---"; done

# Test the generator itself
python tests/test_ai_test_generator.py

# Count generated tests
find tests -name "test_ai_gen_*.py" -exec grep -h "^def test_" {} \; | wc -l
```

## Keyboard Shortcuts (Bash)

```bash
# Add these to ~/.bashrc for convenience

alias aigen='python tools/ai_test_generator.py'
alias aitest='python tests/test_ai_gen_*.py'
alias aibatch='./tools/generate_tests_batch.sh'

# Usage
aigen tools/my_util.py
aitest my_util
```

## File Locations

| File | Purpose |
|------|---------|
| `tools/ai_test_generator.py` | Main generator |
| `tools/AI_TEST_GENERATOR_README.md` | Full documentation |
| `tools/AI_TEST_GENERATOR_TUTORIAL.md` | Step-by-step guide |
| `tools/AI_TEST_GENERATOR_QUICK_REF.md` | This file |
| `tools/generate_tests_batch.sh` | Batch generator |
| `tests/test_ai_test_generator.py` | Generator tests |
| `tests/test_ai_gen_*.py` | Generated tests |
| `examples/demo_utilities.py` | Example code |

## Example Workflow

```bash
# 1. Write your code
vim tools/my_utility.py

# 2. Generate tests
python tools/ai_test_generator.py tools/my_utility.py

# 3. Run tests
python tests/test_ai_gen_my_utility.py

# 4. Review failures
# ... fix code or tests ...

# 5. Rerun
python tests/test_ai_gen_my_utility.py

# 6. Commit when all pass
git add tools/my_utility.py tests/test_ai_gen_my_utility.py
git commit -m "Add my_utility with AI-generated tests"
```

## Support

- **Full docs**: `tools/AI_TEST_GENERATOR_README.md`
- **Tutorial**: `tools/AI_TEST_GENERATOR_TUTORIAL.md`
- **Issues**: Report to @investigate-champion
- **Examples**: `examples/demo_utilities.py`

---

*Quick reference by **@investigate-champion*** 🎯 | *Test smarter, not harder*
