#!/usr/bin/env python3
"""
Tests for the Cross-Language Code Translator
"""

import sys
import os
import importlib.util

# Load the translator module
spec = importlib.util.spec_from_file_location(
    "code_translator",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "code-translator.py")
)
code_translator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_translator)

CodeTranslator = code_translator.CodeTranslator
TranslationResult = code_translator.TranslationResult
ComparisonResult = code_translator.ComparisonResult


def test_python_to_javascript_print():
    """Test Python to JavaScript print statement translation"""
    translator = CodeTranslator()
    code = 'print("Hello, World!")'
    
    result = translator.translate(code, 'python', 'javascript')
    assert 'console.log' in result.translated_code
    assert 'print(' not in result.translated_code
    print("✓ Python to JavaScript print translation test passed")


def test_python_to_javascript_function():
    """Test Python to JavaScript function translation"""
    translator = CodeTranslator()
    code = """def greet(name):
    return f"Hello, {name}" """
    
    result = translator.translate(code, 'python', 'javascript')
    assert 'function greet' in result.translated_code
    assert 'def ' not in result.translated_code
    print("✓ Python to JavaScript function translation test passed")


def test_python_to_javascript_booleans():
    """Test Python to JavaScript boolean translation"""
    translator = CodeTranslator()
    code = """x = True
y = False
z = None"""
    
    result = translator.translate(code, 'python', 'javascript')
    assert 'true' in result.translated_code
    assert 'false' in result.translated_code
    assert 'null' in result.translated_code
    assert 'True' not in result.translated_code
    assert 'False' not in result.translated_code
    assert 'None' not in result.translated_code
    print("✓ Python to JavaScript boolean translation test passed")


def test_javascript_to_python_console_log():
    """Test JavaScript to Python console.log translation"""
    translator = CodeTranslator()
    code = 'console.log("Hello, World!");'
    
    result = translator.translate(code, 'javascript', 'python')
    assert 'print(' in result.translated_code
    assert 'console.log' not in result.translated_code
    print("✓ JavaScript to Python console.log translation test passed")


def test_javascript_to_python_function():
    """Test JavaScript to Python function translation"""
    translator = CodeTranslator()
    code = """function greet(name) {
    return name;
}"""
    
    result = translator.translate(code, 'javascript', 'python')
    assert 'def greet' in result.translated_code
    assert 'function ' not in result.translated_code
    print("✓ JavaScript to Python function translation test passed")


def test_javascript_to_python_booleans():
    """Test JavaScript to Python boolean translation"""
    translator = CodeTranslator()
    code = """let x = true;
let y = false;
let z = null;"""
    
    result = translator.translate(code, 'javascript', 'python')
    assert 'True' in result.translated_code
    assert 'False' in result.translated_code
    assert 'None' in result.translated_code
    assert 'true' not in result.translated_code
    assert 'false' not in result.translated_code
    assert 'null' not in result.translated_code
    print("✓ JavaScript to Python boolean translation test passed")


def test_python_to_bash():
    """Test Python to Bash translation"""
    translator = CodeTranslator()
    code = 'print("Hello, World!")'
    
    result = translator.translate(code, 'python', 'bash')
    assert 'echo' in result.translated_code
    assert 'print(' not in result.translated_code
    assert result.translated_code.startswith('#!/bin/bash')
    print("✓ Python to Bash translation test passed")


def test_bash_to_python():
    """Test Bash to Python translation"""
    translator = CodeTranslator()
    code = '#!/bin/bash\necho "Hello, World!"'
    
    result = translator.translate(code, 'bash', 'python')
    assert 'print(' in result.translated_code
    assert 'echo ' not in result.translated_code
    assert not result.translated_code.strip().startswith('#!/')
    print("✓ Bash to Python translation test passed")


def test_javascript_to_bash():
    """Test JavaScript to Bash translation"""
    translator = CodeTranslator()
    code = 'console.log("Hello, World!");'
    
    result = translator.translate(code, 'javascript', 'bash')
    assert 'echo' in result.translated_code
    assert 'console.log' not in result.translated_code
    print("✓ JavaScript to Bash translation test passed")


def test_bash_to_javascript():
    """Test Bash to JavaScript translation"""
    translator = CodeTranslator()
    code = '#!/bin/bash\necho "Hello, World!"'
    
    result = translator.translate(code, 'bash', 'javascript')
    assert 'console.log' in result.translated_code
    assert 'echo ' not in result.translated_code
    print("✓ Bash to JavaScript translation test passed")


def test_translation_notes():
    """Test that translation notes are generated"""
    translator = CodeTranslator()
    code = 'print("Hello")'
    
    result = translator.translate(code, 'python', 'javascript')
    assert len(result.translation_notes) > 0
    assert isinstance(result.translation_notes, list)
    print("✓ Translation notes test passed")


def test_translation_result_to_dict():
    """Test TranslationResult to_dict conversion"""
    translator = CodeTranslator()
    code = 'print("Hello")'
    
    result = translator.translate(code, 'python', 'javascript')
    result_dict = result.to_dict()
    
    assert isinstance(result_dict, dict)
    assert 'original_code' in result_dict
    assert 'translated_code' in result_dict
    assert 'source_language' in result_dict
    assert 'target_language' in result_dict
    print("✓ TranslationResult to_dict test passed")


def test_unsupported_language_pair():
    """Test that unsupported language pairs raise ValueError"""
    translator = CodeTranslator()
    code = "some code"
    
    try:
        result = translator.translate(code, 'python', 'ruby')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not supported" in str(e)
        print("✓ Unsupported language pair test passed")


def test_comparison():
    """Test code comparison functionality"""
    translator = CodeTranslator()
    code1 = """print("Hello")
x = 5"""
    code2 = """console.log("Hello");
let x = 5;"""
    
    result = translator.compare(code1, code2, 'python', 'javascript')
    assert isinstance(result, ComparisonResult)
    assert result.language1 == 'python'
    assert result.language2 == 'javascript'
    assert isinstance(result.similarity_score, float)
    print("✓ Comparison test passed")


def test_comparison_identical_code():
    """Test comparison of identical code"""
    translator = CodeTranslator()
    code = "x = 5"
    
    result = translator.compare(code, code, 'python', 'python')
    assert result.similarity_score == 100.0
    print("✓ Identical code comparison test passed")


def test_comparison_result_to_dict():
    """Test ComparisonResult to_dict conversion"""
    translator = CodeTranslator()
    code1 = "x = 5"
    code2 = "let x = 5;"
    
    result = translator.compare(code1, code2, 'python', 'javascript')
    result_dict = result.to_dict()
    
    assert isinstance(result_dict, dict)
    assert 'code1' in result_dict
    assert 'code2' in result_dict
    assert 'language1' in result_dict
    assert 'language2' in result_dict
    assert 'similarity_score' in result_dict
    print("✓ ComparisonResult to_dict test passed")


def test_empty_code_translation():
    """Test translation of empty code"""
    translator = CodeTranslator()
    code = ""
    
    result = translator.translate(code, 'python', 'javascript')
    assert result.translated_code == ""
    print("✓ Empty code translation test passed")


def test_language_normalization():
    """Test that language names are normalized correctly"""
    translator = CodeTranslator()
    code = 'print("test")'
    
    # Test js -> javascript normalization
    result = translator.translate(code, 'python', 'js')
    assert result.target_language == 'javascript'
    
    # Test sh -> bash normalization
    result = translator.translate(code, 'python', 'sh')
    assert result.target_language == 'bash'
    
    print("✓ Language normalization test passed")


def test_python_elif_to_javascript():
    """Test Python elif to JavaScript else if translation"""
    translator = CodeTranslator()
    code = """if x > 5:
    print("big")
elif x > 2:
    print("medium")
else:
    print("small")"""
    
    result = translator.translate(code, 'python', 'javascript')
    assert 'else if' in result.translated_code
    assert 'elif' not in result.translated_code
    print("✓ Python elif to JavaScript else if test passed")


def test_javascript_length_to_python():
    """Test JavaScript .length to Python len() translation"""
    translator = CodeTranslator()
    code = "let size = arr.length;"
    
    result = translator.translate(code, 'javascript', 'python')
    assert 'len(arr)' in result.translated_code
    assert '.length' not in result.translated_code
    print("✓ JavaScript .length to Python len() test passed")


def run_all_tests():
    """Run all tests"""
    print("Running Cross-Language Code Translator tests...\n")
    
    tests = [
        test_python_to_javascript_print,
        test_python_to_javascript_function,
        test_python_to_javascript_booleans,
        test_javascript_to_python_console_log,
        test_javascript_to_python_function,
        test_javascript_to_python_booleans,
        test_python_to_bash,
        test_bash_to_python,
        test_javascript_to_bash,
        test_bash_to_javascript,
        test_translation_notes,
        test_translation_result_to_dict,
        test_unsupported_language_pair,
        test_comparison,
        test_comparison_identical_code,
        test_comparison_result_to_dict,
        test_empty_code_translation,
        test_language_normalization,
        test_python_elif_to_javascript,
        test_javascript_length_to_python,
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
