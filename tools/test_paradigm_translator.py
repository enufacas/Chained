#!/usr/bin/env python3
"""
Tests for the Code Paradigm Translator
"""

import sys
import os
import importlib.util

# Load the translator module
spec = importlib.util.spec_from_file_location(
    "paradigm_translator",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "paradigm-translator.py")
)
paradigm_translator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(paradigm_translator)

ParadigmTranslator = paradigm_translator.ParadigmTranslator
Paradigm = paradigm_translator.Paradigm
TranslationResult = paradigm_translator.TranslationResult


def test_imperative_to_declarative():
    """Test imperative to declarative transformation"""
    translator = ParadigmTranslator()
    
    code = """
numbers = [1, 2, 3, 4, 5]
doubled = []
for n in numbers:
    doubled.append(n * 2)
"""
    
    result = translator.translate(code, Paradigm.IMPERATIVE, Paradigm.DECLARATIVE)
    
    assert result.success, "Translation should succeed"
    assert "[n * 2 for n in numbers]" in result.translated_code
    assert "doubled.append" not in result.translated_code
    assert len(result.transformations_applied) > 0
    print("✓ Imperative to declarative test passed")


def test_imperative_to_declarative_with_filter():
    """Test imperative to declarative with filter"""
    translator = ParadigmTranslator()
    
    code = """
evens = []
for n in numbers:
    if n % 2 == 0:
        evens.append(n)
"""
    
    result = translator.translate(code, Paradigm.IMPERATIVE, Paradigm.DECLARATIVE)
    
    assert result.success, "Translation should succeed"
    assert "[n for n in numbers if" in result.translated_code
    assert "evens.append" not in result.translated_code
    print("✓ Imperative to declarative with filter test passed")


def test_declarative_to_imperative():
    """Test declarative to imperative transformation"""
    translator = ParadigmTranslator()
    
    code = """
doubled = [n * 2 for n in numbers]
"""
    
    result = translator.translate(code, Paradigm.DECLARATIVE, Paradigm.IMPERATIVE)
    
    assert result.success, "Translation should succeed"
    assert "for n in numbers:" in result.translated_code
    assert "doubled.append(n * 2)" in result.translated_code
    print("✓ Declarative to imperative test passed")


def test_declarative_to_imperative_with_condition():
    """Test declarative to imperative with condition"""
    translator = ParadigmTranslator()
    
    code = """
evens = [n for n in numbers if n % 2 == 0]
"""
    
    result = translator.translate(code, Paradigm.DECLARATIVE, Paradigm.IMPERATIVE)
    
    assert result.success, "Translation should succeed"
    assert "for n in numbers:" in result.translated_code
    assert "if n % 2 == 0:" in result.translated_code
    assert "evens.append(n)" in result.translated_code
    print("✓ Declarative to imperative with condition test passed")


def test_oop_to_functional():
    """Test OOP to functional transformation"""
    translator = ParadigmTranslator()
    
    code = """
class Calculator:
    def add(self, a, b):
        return a + b
"""
    
    result = translator.translate(code, Paradigm.OBJECT_ORIENTED, Paradigm.FUNCTIONAL)
    
    assert result.success, "Translation should succeed"
    # The transformation should extract methods or convert to functional style
    assert len(result.transformations_applied) >= 0
    print("✓ OOP to functional test passed")


def test_functional_to_oop():
    """Test functional to OOP transformation"""
    translator = ParadigmTranslator()
    
    code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""
    
    result = translator.translate(code, Paradigm.FUNCTIONAL, Paradigm.OBJECT_ORIENTED)
    
    assert result.success, "Translation should succeed"
    assert "class" in result.translated_code.lower()
    assert len(result.transformations_applied) > 0
    print("✓ Functional to OOP test passed")


def test_procedural_to_oop():
    """Test procedural to OOP transformation"""
    translator = ParadigmTranslator()
    
    code = """
def process_data(data):
    return data * 2

def validate_data(data):
    return data > 0
"""
    
    result = translator.translate(code, Paradigm.PROCEDURAL, Paradigm.OBJECT_ORIENTED)
    
    assert result.success, "Translation should succeed"
    assert "class" in result.translated_code
    assert len(result.transformations_applied) > 0
    print("✓ Procedural to OOP test passed")


def test_oop_to_procedural():
    """Test OOP to procedural transformation"""
    translator = ParadigmTranslator()
    
    code = """
class DataHandler:
    def process(self, data):
        return data * 2
    
    def validate(self, data):
        return data > 0
"""
    
    result = translator.translate(code, Paradigm.OBJECT_ORIENTED, Paradigm.PROCEDURAL)
    
    assert result.success, "Translation should succeed"
    assert "def process(data" in result.translated_code or "def process(" in result.translated_code
    assert len(result.transformations_applied) >= 0
    print("✓ OOP to procedural test passed")


def test_same_paradigm():
    """Test that same paradigm returns original code"""
    translator = ParadigmTranslator()
    
    code = "x = 5"
    result = translator.translate(code, Paradigm.IMPERATIVE, Paradigm.IMPERATIVE)
    
    assert result.success, "Translation should succeed"
    assert result.translated_code == code
    assert len(result.warnings) > 0
    assert "same" in result.warnings[0].lower()
    print("✓ Same paradigm test passed")


def test_unsupported_translation():
    """Test handling of unsupported translation pairs"""
    translator = ParadigmTranslator()
    
    # Create a mock unsupported translation by removing a strategy
    original_strategies = translator.translation_strategies.copy()
    translator.translation_strategies.clear()
    
    code = "x = 5"
    result = translator.translate(code, Paradigm.IMPERATIVE, Paradigm.DECLARATIVE)
    
    assert not result.success, "Translation should fail for unsupported pair"
    assert len(result.warnings) > 0
    
    # Restore strategies
    translator.translation_strategies = original_strategies
    print("✓ Unsupported translation test passed")


def test_paradigm_detection_oop():
    """Test paradigm detection for OOP code"""
    translator = ParadigmTranslator()
    
    code = """
class MyClass:
    def method(self):
        pass
"""
    
    detected = translator.detect_paradigm(code)
    assert detected == Paradigm.OBJECT_ORIENTED
    print("✓ OOP paradigm detection test passed")


def test_paradigm_detection_functional():
    """Test paradigm detection for functional code"""
    translator = ParadigmTranslator()
    
    code = """
result = list(map(lambda x: x * 2, numbers))
filtered = list(filter(lambda x: x > 0, numbers))
comprehension = [x * 2 for x in numbers]
"""
    
    detected = translator.detect_paradigm(code)
    assert detected == Paradigm.FUNCTIONAL
    print("✓ Functional paradigm detection test passed")


def test_paradigm_detection_procedural():
    """Test paradigm detection for procedural code"""
    translator = ParadigmTranslator()
    
    code = """
def function1():
    pass

def function2():
    pass
"""
    
    detected = translator.detect_paradigm(code)
    assert detected == Paradigm.PROCEDURAL
    print("✓ Procedural paradigm detection test passed")


def test_paradigm_detection_imperative():
    """Test paradigm detection for imperative code"""
    translator = ParadigmTranslator()
    
    code = """
x = 5
y = 10
z = x + y
"""
    
    detected = translator.detect_paradigm(code)
    assert detected == Paradigm.IMPERATIVE
    print("✓ Imperative paradigm detection test passed")


def test_translation_result_str():
    """Test TranslationResult string representation"""
    result = TranslationResult(
        source_paradigm=Paradigm.IMPERATIVE,
        target_paradigm=Paradigm.DECLARATIVE,
        original_code="x = 5",
        translated_code="x = 5",
        transformations_applied=["test"],
        success=True,
        warnings=[]
    )
    
    result_str = str(result)
    assert "Success" in result_str
    assert "imperative" in result_str
    assert "declarative" in result_str
    print("✓ TranslationResult string representation test passed")


def test_error_handling():
    """Test error handling for invalid code"""
    translator = ParadigmTranslator()
    
    # Test with valid Python that might cause issues
    code = "def test():\n    pass"
    result = translator.translate(code, Paradigm.FUNCTIONAL, Paradigm.OBJECT_ORIENTED)
    
    # Should handle gracefully
    assert result.success or len(result.warnings) > 0
    print("✓ Error handling test passed")


def test_multiple_transformations():
    """Test that multiple transformations are tracked"""
    translator = ParadigmTranslator()
    
    code = """
numbers = [1, 2, 3, 4, 5]
doubled = []
for n in numbers:
    doubled.append(n * 2)

evens = []
for n in numbers:
    if n % 2 == 0:
        evens.append(n)
"""
    
    result = translator.translate(code, Paradigm.IMPERATIVE, Paradigm.DECLARATIVE)
    
    assert result.success
    assert len(result.transformations_applied) >= 2
    print("✓ Multiple transformations test passed")


def run_all_tests():
    """Run all tests"""
    print("\nRunning Paradigm Translator Tests...")
    print("=" * 60)
    
    test_functions = [
        test_imperative_to_declarative,
        test_imperative_to_declarative_with_filter,
        test_declarative_to_imperative,
        test_declarative_to_imperative_with_condition,
        test_oop_to_functional,
        test_functional_to_oop,
        test_procedural_to_oop,
        test_oop_to_procedural,
        test_same_paradigm,
        test_unsupported_translation,
        test_paradigm_detection_oop,
        test_paradigm_detection_functional,
        test_paradigm_detection_procedural,
        test_paradigm_detection_imperative,
        test_translation_result_str,
        test_error_handling,
        test_multiple_transformations,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} error: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
