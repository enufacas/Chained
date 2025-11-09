#!/usr/bin/env python3
"""
Tests for the Code Golf Optimizer
"""

import sys
import os
import importlib.util

# Load the optimizer module
spec = importlib.util.spec_from_file_location(
    "code_golf_optimizer",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "code-golf-optimizer.py")
)
code_golf_optimizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_golf_optimizer)

CodeGolfOptimizer = code_golf_optimizer.CodeGolfOptimizer
OptimizationResult = code_golf_optimizer.OptimizationResult


def test_python_comment_removal():
    """Test that Python comments are removed"""
    optimizer = CodeGolfOptimizer()
    code = """# This is a comment
x = 5
# Another comment
print(x)"""
    
    result = optimizer.optimize(code, 'python')
    assert '#' not in result.optimized_code
    assert result.optimized_chars < result.original_chars
    print("✓ Python comment removal test passed")


def test_python_docstring_removal():
    """Test that docstrings are removed"""
    optimizer = CodeGolfOptimizer()
    code = '''"""
This is a docstring
"""
def foo():
    """Another docstring"""
    return 42'''
    
    result = optimizer.optimize(code, 'python')
    assert '"""' not in result.optimized_code
    assert result.optimized_chars < result.original_chars
    print("✓ Python docstring removal test passed")


def test_python_blank_line_removal():
    """Test that blank lines are removed"""
    optimizer = CodeGolfOptimizer()
    code = """x = 1

y = 2

z = 3"""
    
    result = optimizer.optimize(code, 'python')
    assert '\n\n' not in result.optimized_code
    print("✓ Python blank line removal test passed")


def test_javascript_comment_removal():
    """Test that JavaScript comments are removed"""
    optimizer = CodeGolfOptimizer()
    code = """// Single line comment
let x = 5;
/* Multi-line
   comment */
console.log(x);"""
    
    result = optimizer.optimize(code, 'javascript')
    assert '//' not in result.optimized_code
    assert '/*' not in result.optimized_code
    print("✓ JavaScript comment removal test passed")


def test_javascript_boolean_optimization():
    """Test that JavaScript booleans are optimized"""
    optimizer = CodeGolfOptimizer()
    code = "let x = true; let y = false;"
    
    result = optimizer.optimize(code, 'javascript')
    assert 'true' not in result.optimized_code
    assert 'false' not in result.optimized_code
    assert '!0' in result.optimized_code or '!1' in result.optimized_code
    print("✓ JavaScript boolean optimization test passed")


def test_bash_comment_removal():
    """Test that Bash comments are removed"""
    optimizer = CodeGolfOptimizer()
    code = """#!/bin/bash
# This is a comment
echo "Hello"
# Another comment
echo "World"
"""
    
    result = optimizer.optimize(code, 'bash')
    # First line might still have shebang
    lines = result.optimized_code.split('\n')
    comment_count = sum(1 for line in lines if line.strip().startswith('#') and not line.startswith('#!'))
    assert comment_count == 0
    print("✓ Bash comment removal test passed")


def test_unsupported_language():
    """Test that unsupported languages raise ValueError"""
    optimizer = CodeGolfOptimizer()
    code = "some code"
    
    try:
        result = optimizer.optimize(code, 'ruby')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unsupported language" in str(e)
        print("✓ Unsupported language test passed")


def test_reduction_percentage():
    """Test that reduction percentage is calculated correctly"""
    optimizer = CodeGolfOptimizer()
    code = """# Comment
x = 1  # Another comment

y = 2
"""
    
    result = optimizer.optimize(code, 'python')
    assert result.reduction_percentage > 0
    assert result.original_chars > result.optimized_chars
    expected_reduction = ((result.original_chars - result.optimized_chars) / result.original_chars) * 100
    assert abs(result.reduction_percentage - expected_reduction) < 0.01
    print("✓ Reduction percentage test passed")


def test_optimization_result_to_dict():
    """Test that OptimizationResult can be converted to dict"""
    optimizer = CodeGolfOptimizer()
    code = "x = 1"
    
    result = optimizer.optimize(code, 'python')
    result_dict = result.to_dict()
    
    assert isinstance(result_dict, dict)
    assert 'original_code' in result_dict
    assert 'optimized_code' in result_dict
    assert 'reduction_percentage' in result_dict
    print("✓ OptimizationResult to_dict test passed")


def test_empty_code():
    """Test handling of empty code"""
    optimizer = CodeGolfOptimizer()
    code = ""
    
    result = optimizer.optimize(code, 'python')
    assert result.original_chars == 0
    assert result.optimized_chars == 0
    print("✓ Empty code test passed")


def test_variable_shortening():
    """Test that long variable names are shortened"""
    optimizer = CodeGolfOptimizer()
    code = """def calculate_sum(number_list):
    total_sum = 0
    for number in number_list:
        total_sum = total_sum + number
        total_sum = total_sum + 1
    return total_sum"""
    
    result = optimizer.optimize(code, 'python')
    # Should be shorter due to variable name shortening
    assert result.optimized_chars < result.original_chars
    # Check that some optimization was applied
    assert "Shortened" in str(result.optimizations_applied) or len(result.optimizations_applied) > 0
    print("✓ Variable shortening test passed")


def run_all_tests():
    """Run all tests"""
    print("Running Code Golf Optimizer tests...\n")
    
    tests = [
        test_python_comment_removal,
        test_python_docstring_removal,
        test_python_blank_line_removal,
        test_javascript_comment_removal,
        test_javascript_boolean_optimization,
        test_bash_comment_removal,
        test_unsupported_language,
        test_reduction_percentage,
        test_optimization_result_to_dict,
        test_empty_code,
        test_variable_shortening,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    if failed == 0:
        print(f"All {len(tests)} tests passed! ✓")
        return 0
    else:
        print(f"{failed}/{len(tests)} tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
