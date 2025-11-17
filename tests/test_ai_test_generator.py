#!/usr/bin/env python3
"""
Test suite for the AI Test Generator itself.

Created by @investigate-champion to ensure the test generator
works correctly and produces valid test code.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.ai_test_generator import (
    AITestGenerator,
    CodeAnalyzer,
    EdgeCaseDetector,
    TestableFunction,
    EdgeCase
)


def test_edge_case_detector():
    """Test that EdgeCaseDetector generates appropriate edge cases."""
    print("\n📋 Testing EdgeCaseDetector")
    print("-" * 70)
    
    detector = EdgeCaseDetector()
    
    # Test string edge cases
    string_cases = detector.detect_edge_cases_for_param('text', 'str')
    assert len(string_cases) > 0, "Should generate string edge cases"
    
    case_names = [case.name for case in string_cases]
    assert 'empty_string' in case_names, "Should include empty string case"
    assert 'text_none' in case_names, "Should include None case for non-Optional"
    
    print("  ✅ String edge cases generated correctly")
    
    # Test int edge cases
    int_cases = detector.detect_edge_cases_for_param('count', 'int')
    assert len(int_cases) > 0, "Should generate int edge cases"
    
    case_names = [case.name for case in int_cases]
    assert 'zero' in case_names, "Should include zero case"
    assert 'negative' in case_names, "Should include negative case"
    
    print("  ✅ Integer edge cases generated correctly")
    
    # Test list edge cases
    list_cases = detector.detect_edge_cases_for_param('items', 'list')
    assert len(list_cases) > 0, "Should generate list edge cases"
    
    case_names = [case.name for case in list_cases]
    assert 'empty_list' in case_names, "Should include empty list case"
    
    print("  ✅ List edge cases generated correctly")
    
    return True


def test_code_analyzer():
    """Test that CodeAnalyzer correctly parses Python files."""
    print("\n📋 Testing CodeAnalyzer")
    print("-" * 70)
    
    analyzer = CodeAnalyzer()
    
    # Create a temporary Python file to analyze
    test_code = '''
def simple_function(a: int, b: str) -> str:
    """A simple test function."""
    return f"{b}: {a}"

def _private_function():
    """Should be skipped."""
    pass

def test_function():
    """Should be skipped (test function)."""
    pass

def complex_function(text: str, max_len: int = 100, items: list = None) -> dict:
    """Function with multiple parameters and types."""
    return {"text": text, "items": items or []}
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_file = Path(f.name)
    
    try:
        # Analyze the file
        functions = analyzer.analyze_file(temp_file)
        
        # Check results
        assert len(functions) == 2, f"Should find 2 testable functions, found {len(functions)}"
        
        func_names = [f.name for f in functions]
        assert 'simple_function' in func_names, "Should find simple_function"
        assert 'complex_function' in func_names, "Should find complex_function"
        assert '_private_function' not in func_names, "Should skip private functions"
        assert 'test_function' not in func_names, "Should skip test functions"
        
        print(f"  ✅ Found {len(functions)} testable functions")
        
        # Check parameter extraction
        simple_func = [f for f in functions if f.name == 'simple_function'][0]
        assert len(simple_func.parameters) == 2, "Should extract 2 parameters"
        
        param_names = [p[0] for p in simple_func.parameters]
        assert 'a' in param_names and 'b' in param_names, "Should extract parameter names"
        
        print("  ✅ Parameters extracted correctly")
        
        # Check type extraction
        param_types = {p[0]: p[1] for p in simple_func.parameters}
        assert param_types['a'] == 'int', "Should extract int type"
        assert param_types['b'] == 'str', "Should extract str type"
        
        print("  ✅ Types extracted correctly")
        
    finally:
        # Clean up
        temp_file.unlink()
    
    return True


def test_test_generation():
    """Test that AITestGenerator creates valid test code."""
    print("\n📋 Testing AITestGenerator")
    print("-" * 70)
    
    generator = AITestGenerator()
    
    # Create a simple test source file
    test_source = '''
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"
'''
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as src:
        src.write(test_source)
        source_file = Path(src.name)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as out:
        output_file = Path(out.name)
    
    try:
        # Generate tests
        tests = generator.generate_test_suite(source_file, output_file)
        
        # Check that tests were generated
        assert len(tests) > 0, "Should generate tests"
        print(f"  ✅ Generated {len(tests)} test cases")
        
        # Check that test file was created
        assert output_file.exists(), "Test file should be created"
        print("  ✅ Test file created")
        
        # Check that test file is valid Python
        with open(output_file, 'r') as f:
            test_content = f.read()
        
        try:
            compile(test_content, str(output_file), 'exec')
            print("  ✅ Generated test file has valid syntax")
        except SyntaxError as e:
            print(f"  ❌ Generated test file has syntax error: {e}")
            return False
        
        # Check for required components
        assert 'def run_all_tests()' in test_content, "Should have run_all_tests function"
        assert 'if __name__ == "__main__"' in test_content, "Should have main block"
        assert 'test_add_numbers' in test_content, "Should have tests for add_numbers"
        assert 'test_greet' in test_content, "Should have tests for greet"
        
        print("  ✅ Test file contains required components")
        
        # Check for edge case tests
        assert 'happy_path' in test_content, "Should have happy path tests"
        assert 'empty_string' in test_content or 'zero' in test_content, "Should have edge case tests"
        
        print("  ✅ Test file includes edge case tests")
        
    finally:
        # Clean up
        source_file.unlink()
        if output_file.exists():
            output_file.unlink()
    
    return True


def test_edge_case_categories():
    """Test that edge cases are properly categorized."""
    print("\n📋 Testing Edge Case Categories")
    print("-" * 70)
    
    detector = EdgeCaseDetector()
    
    # Check that categories exist
    categories = set()
    for type_name, cases in detector.edge_case_patterns.items():
        for case in cases:
            categories.add(case.category)
    
    expected_categories = {'empty', 'boundary', 'special_char', 'null', 'security', 'complex', 'special_value'}
    
    assert len(categories) > 0, "Should have edge case categories"
    print(f"  ✅ Found {len(categories)} edge case categories: {sorted(categories)}")
    
    # Check for security-related edge cases
    security_cases = []
    for type_name, cases in detector.edge_case_patterns.items():
        for case in cases:
            if case.category == 'security':
                security_cases.append(case.name)
    
    assert len(security_cases) > 0, "Should have security edge cases"
    assert 'sql_injection' in security_cases, "Should have SQL injection test"
    assert 'script_tag' in security_cases, "Should have XSS test"
    
    print(f"  ✅ Security edge cases included: {security_cases}")
    
    return True


def test_special_value_handling():
    """Test that special values like infinity and NaN are handled correctly."""
    print("\n📋 Testing Special Value Handling")
    print("-" * 70)
    
    detector = EdgeCaseDetector()
    
    # Get float edge cases
    float_cases = detector.detect_edge_cases_for_param('value', 'float')
    
    case_values = {case.name: case.input_value for case in float_cases}
    
    # Check for special float values
    assert 'infinity' in case_values, "Should have infinity case"
    assert 'neg_infinity' in case_values, "Should have negative infinity case"
    assert 'nan' in case_values, "Should have NaN case"
    
    # Verify the values are correct
    import math
    assert case_values['infinity'] == float('inf'), "Infinity should be float('inf')"
    assert case_values['neg_infinity'] == float('-inf'), "Neg infinity should be float('-inf')"
    assert math.isnan(case_values['nan']), "NaN should be float('nan')"
    
    print("  ✅ Special float values (inf, -inf, nan) handled correctly")
    
    return True


def run_all_tests():
    """Run all tests for the AI Test Generator."""
    print("=" * 70)
    print("🧪 AI Test Generator - Self Test Suite")
    print("   by @investigate-champion")
    print("=" * 70)
    
    tests = [
        ("Edge Case Detector", test_edge_case_detector),
        ("Code Analyzer", test_code_analyzer),
        ("Test Generation", test_test_generation),
        ("Edge Case Categories", test_edge_case_categories),
        ("Special Value Handling", test_special_value_handling),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED\n")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: FAILED - {e}\n")
    
    print("=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print(f"Total tests: {passed + failed}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    if passed + failed > 0:
        print(f"Success rate: {(passed/(passed+failed)*100):.1f}%")
    print()
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
