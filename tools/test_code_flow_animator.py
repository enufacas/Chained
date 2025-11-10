#!/usr/bin/env python3
"""
Tests for Code Flow Animator

Validates the code flow analysis and visualization generation.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import with proper module name
import importlib.util
spec = importlib.util.spec_from_file_location(
    "code_flow_animator",
    Path(__file__).parent / "code-flow-animator.py"
)
code_flow_animator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_flow_animator)

CodeFlowAnimator = code_flow_animator.CodeFlowAnimator
PythonFlowAnalyzer = code_flow_animator.PythonFlowAnalyzer
JavaScriptFlowAnalyzer = code_flow_animator.JavaScriptFlowAnalyzer
ExecutionStep = code_flow_animator.ExecutionStep


def test_execution_step():
    """Test ExecutionStep creation and serialization"""
    step = ExecutionStep(
        step_type='assign',
        line_number=10,
        description='x = 5',
        variables={'x': '5'},
        function_name='main'
    )
    
    data = step.to_dict()
    assert data['type'] == 'assign'
    assert data['line'] == 10
    assert data['description'] == 'x = 5'
    assert data['variables'] == {'x': '5'}
    assert data['function'] == 'main'
    print("✓ ExecutionStep test passed")


def test_python_simple_analysis():
    """Test Python code analysis with simple code"""
    code = """
def add(a, b):
    result = a + b
    return result

x = add(5, 3)
"""
    
    analyzer = PythonFlowAnalyzer(code)
    flow_data = analyzer.analyze()
    
    assert flow_data['language'] == 'python'
    assert len(flow_data['steps']) > 0
    assert len(flow_data['function_calls']) > 0
    
    # Check for function definition
    func_steps = [s for s in flow_data['steps'] if s['type'] == 'call']
    assert len(func_steps) > 0
    
    # Check for assignment
    assign_steps = [s for s in flow_data['steps'] if s['type'] == 'assign']
    assert len(assign_steps) > 0
    
    # Check for return
    return_steps = [s for s in flow_data['steps'] if s['type'] == 'return']
    assert len(return_steps) > 0
    
    print("✓ Python simple analysis test passed")


def test_python_control_flow():
    """Test Python control flow detection"""
    code = """
def check_number(n):
    if n > 0:
        result = "positive"
    else:
        result = "negative"
    
    for i in range(n):
        print(i)
    
    while n > 0:
        n = n - 1
    
    return result
"""
    
    analyzer = PythonFlowAnalyzer(code)
    flow_data = analyzer.analyze()
    
    # Check control flow detection
    assert len(flow_data['control_flow']) > 0
    
    # Check for if statement
    if_flows = [f for f in flow_data['control_flow'] if f['type'] == 'if']
    assert len(if_flows) > 0
    
    # Check for for loop
    for_flows = [f for f in flow_data['control_flow'] if f['type'] == 'for']
    assert len(for_flows) > 0
    
    # Check for while loop
    while_flows = [f for f in flow_data['control_flow'] if f['type'] == 'while']
    assert len(while_flows) > 0
    
    print("✓ Python control flow test passed")


def test_javascript_analysis():
    """Test JavaScript code analysis"""
    code = """
function multiply(a, b) {
    const result = a * b;
    return result;
}

const x = multiply(4, 5);

if (x > 10) {
    console.log("Large number");
}

for (let i = 0; i < 5; i++) {
    console.log(i);
}
"""
    
    analyzer = JavaScriptFlowAnalyzer(code)
    flow_data = analyzer.analyze()
    
    assert flow_data['language'] == 'javascript'
    assert len(flow_data['steps']) > 0
    
    # Check for function definitions
    func_calls = flow_data['function_calls']
    assert len(func_calls) > 0
    
    # Check for control flow
    assert len(flow_data['control_flow']) > 0
    
    print("✓ JavaScript analysis test passed")


def test_code_flow_animator():
    """Test main CodeFlowAnimator class"""
    animator = CodeFlowAnimator()
    
    # Test supported languages
    assert 'python' in animator.supported_languages
    assert 'javascript' in animator.supported_languages
    
    # Test analyze_code with Python
    python_code = """
def test():
    x = 1
    return x
"""
    flow_data = animator.analyze_code(python_code, 'python')
    assert flow_data['language'] == 'python'
    assert 'steps' in flow_data
    assert 'metadata' in flow_data
    assert 'statistics' in flow_data
    
    print("✓ CodeFlowAnimator test passed")


def test_file_analysis():
    """Test analyzing a file"""
    # Create a temporary Python file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
""")
        temp_path = f.name
    
    try:
        animator = CodeFlowAnimator()
        flow_data = animator.analyze_file(temp_path)
        
        assert flow_data['language'] == 'python'
        assert len(flow_data['steps']) > 0
        assert flow_data['statistics']['function_definitions'] > 0
        
        print("✓ File analysis test passed")
    finally:
        Path(temp_path).unlink()


def test_json_output():
    """Test JSON output generation"""
    animator = CodeFlowAnimator()
    
    code = """
def simple():
    x = 1
    return x
"""
    flow_data = animator.analyze_code(code, 'python')
    
    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        animator.save_flow_data(flow_data, temp_path)
        
        # Read back and verify
        with open(temp_path, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data['language'] == 'python'
        assert 'steps' in loaded_data
        
        print("✓ JSON output test passed")
    finally:
        Path(temp_path).unlink()


def test_html_generation():
    """Test HTML report generation"""
    animator = CodeFlowAnimator()
    
    code = """
def greet(name):
    message = "Hello, " + name
    return message

result = greet("World")
"""
    flow_data = animator.analyze_code(code, 'python')
    
    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        temp_path = f.name
    
    try:
        animator.generate_html_report(flow_data, temp_path)
        
        # Read and verify HTML contains expected elements
        with open(temp_path, 'r') as f:
            html_content = f.read()
        
        assert '<!DOCTYPE html>' in html_content
        assert 'Code Execution Flow' in html_content
        assert 'python' in html_content.lower()
        assert 'greet' in html_content
        
        print("✓ HTML generation test passed")
    finally:
        Path(temp_path).unlink()


def test_statistics_calculation():
    """Test statistics calculation"""
    code = """
def complex_function(n):
    total = 0
    
    if n > 0:
        for i in range(n):
            total = total + i
    
    while total > 100:
        total = total - 10
    
    return total

result = complex_function(10)
"""
    
    analyzer = PythonFlowAnalyzer(code)
    flow_data = analyzer.analyze()
    
    stats = flow_data['statistics']
    
    assert stats['total_steps'] > 0
    assert stats['function_definitions'] > 0
    assert stats['control_flow_statements'] > 0
    assert stats['assignments'] > 0
    
    # Verify specific counts
    assert stats['function_definitions'] >= 1
    assert stats['control_flow_statements'] >= 2  # if and for/while
    
    print("✓ Statistics calculation test passed")


def test_error_handling():
    """Test error handling for invalid inputs"""
    animator = CodeFlowAnimator()
    
    # Test unsupported language
    try:
        animator.analyze_code("code", "unsupported")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unsupported language" in str(e)
    
    # Test non-existent file
    try:
        animator.analyze_file("/nonexistent/file.py")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass
    
    print("✓ Error handling test passed")


def run_all_tests():
    """Run all tests"""
    print("\nRunning Code Flow Animator Tests...")
    print("=" * 50)
    
    tests = [
        test_execution_step,
        test_python_simple_analysis,
        test_python_control_flow,
        test_javascript_analysis,
        test_code_flow_animator,
        test_file_analysis,
        test_json_output,
        test_html_generation,
        test_statistics_calculation,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
