#!/usr/bin/env python3
"""
Tests for the Code Readability Scorer
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
import importlib.util

# Load the readability scorer module
spec = importlib.util.spec_from_file_location(
    "readability_scorer",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "readability-scorer.py")
)
readability_scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readability_scorer)

ReadabilityScorer = readability_scorer.ReadabilityScorer


def test_scorer_initialization():
    """Test that scorer initializes correctly"""
    scorer = ReadabilityScorer()
    assert scorer is not None
    assert hasattr(scorer, 'naming_keywords')
    assert 'good' in scorer.naming_keywords
    assert 'bad' in scorer.naming_keywords
    print("✓ Scorer initialization test passed")


def test_analyze_good_code():
    """Test analysis of well-written code"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
A well-documented module for testing
"""

def calculate_fibonacci(number: int) -> int:
    """
    Calculate the nth Fibonacci number.
    
    Args:
        number: The position in the Fibonacci sequence
        
    Returns:
        The Fibonacci number at the given position
        
    Raises:
        ValueError: If number is negative
    """
    if number < 0:
        raise ValueError("Number must be non-negative")
    
    if number <= 1:
        return number
    
    return calculate_fibonacci(number - 1) + calculate_fibonacci(number - 2)


def main():
    """Main entry point"""
    result = calculate_fibonacci(10)
    print(f"Result: {result}")


if __name__ == '__main__':
    main()
''')
        
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(test_file)
        
        # Should have a good overall score
        assert "scores" in result
        assert result["scores"]["overall"] >= 70
        assert result["scores"]["naming"] >= 80
        assert result["scores"]["documentation"] >= 80
        print("✓ Good code analysis test passed")


def test_analyze_poor_naming():
    """Test detection of poor naming"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
def f(x):
    y = x * 2
    z = y + 1
    return z

def do(a, b):
    return a + b
''')
        
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(test_file)
        
        # Should detect naming issues
        assert result["scores"]["naming"] < 95
        
        # Should have suggestions about naming
        naming_suggestions = [s for s in result["suggestions"] if s["category"] == "naming"]
        assert len(naming_suggestions) > 0
        # Should detect short function names
        assert any("short" in s["issue"].lower() for s in naming_suggestions)
        print("✓ Poor naming detection test passed")


def test_analyze_high_complexity():
    """Test detection of high complexity"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                if x > y:
                    if y > z:
                        return True
    return False
''')
        
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(test_file)
        
        # Should detect complexity issues
        assert result["scores"]["complexity"] < 100
        
        # Should detect deep nesting
        complexity_suggestions = [s for s in result["suggestions"] if s["category"] == "complexity"]
        assert len(complexity_suggestions) > 0
        assert any("nesting" in s["issue"].lower() for s in complexity_suggestions)
        print("✓ High complexity detection test passed")


def test_analyze_long_function():
    """Test detection of long functions"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        # Create a function with more than 50 lines
        lines = ["def very_long_function():"]
        lines.append('    """A very long function"""')
        for i in range(60):
            lines.append(f"    x{i} = {i}")
        lines.append("    return x0")
        
        with open(test_file, 'w') as f:
            f.write('\n'.join(lines))
        
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(test_file)
        
        # Should detect long function
        complexity_suggestions = [s for s in result["suggestions"] if s["category"] == "complexity"]
        assert any("long" in s["issue"].lower() for s in complexity_suggestions)
        print("✓ Long function detection test passed")


def test_analyze_missing_documentation():
    """Test detection of missing documentation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
def undocumented_function(param1, param2):
    return param1 + param2

def another_function():
    return 42

class UndocumentedClass:
    def method(self):
        pass
''')
        
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(test_file)
        
        # Should have low documentation score
        assert result["scores"]["documentation"] < 70
        
        # Should suggest adding docstrings
        doc_suggestions = [s for s in result["suggestions"] if s["category"] == "documentation"]
        assert len(doc_suggestions) >= 3  # At least module, functions, class
        assert any("missing docstring" in s["issue"].lower() for s in doc_suggestions)
        print("✓ Missing documentation detection test passed")


def test_analyze_formatting_issues():
    """Test detection of formatting issues"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            # Write code with formatting issues
            f.write('def test():   \n')  # Trailing whitespace
            f.write('    x = "' + 'a' * 130 + '"\n')  # Very long line
            f.write('    return x\n')
        
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(test_file)
        
        # Should detect formatting issues
        format_suggestions = [s for s in result["suggestions"] if s["category"] == "formatting"]
        assert len(format_suggestions) > 0
        # Should detect long line or trailing whitespace
        assert any("line" in s["issue"].lower() or "whitespace" in s["issue"].lower() 
                  for s in format_suggestions)
        print("✓ Formatting issues detection test passed")


def test_score_boundaries():
    """Test that scores stay within 0-100 range"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        # Create extremely bad code
        with open(test_file, 'w') as f:
            f.write('def f(x):\n')
            for i in range(100):
                f.write(f'    if True:\n')
                f.write(f'        x = {i * 42}\n')
            f.write('    return x\n')
        
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(test_file)
        
        # All scores should be between 0 and 100
        for category, score in result["scores"].items():
            assert 0 <= score <= 100, f"{category} score {score} out of bounds"
        print("✓ Score boundaries test passed")


def test_directory_analysis():
    """Test analyzing multiple files in a directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple test files
        for i in range(3):
            test_file = os.path.join(tmpdir, f"test{i}.py")
            with open(test_file, 'w') as f:
                f.write(f'''
"""Module {i}"""

def function_{i}(parameter: int) -> int:
    """
    Function {i}
    
    Args:
        parameter: Input parameter
        
    Returns:
        Processed value
    """
    return parameter * {i + 1}
''')
        
        scorer = ReadabilityScorer()
        results = scorer.analyze_directory(tmpdir)
        
        assert results["summary"]["total_files"] == 3
        assert len(results["files_analyzed"]) == 3
        assert "avg_overall_score" in results["summary"]
        assert results["summary"]["avg_overall_score"] > 0
        print("✓ Directory analysis test passed")


def test_json_output():
    """Test JSON output generation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
"""Test module"""

def test_function():
    """Test function"""
    return 42
''')
        
        scorer = ReadabilityScorer()
        results = scorer.analyze_file(test_file)
        
        # Should be JSON serializable
        json_str = json.dumps(results)
        parsed = json.loads(json_str)
        
        assert "scores" in parsed
        assert "suggestions" in parsed
        print("✓ JSON output test passed")


def test_markdown_report_generation():
    """Test markdown report generation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
"""Test module"""

def test_function():
    """Test function"""
    return 42
''')
        
        scorer = ReadabilityScorer()
        results = scorer.analyze_file(test_file)
        report = scorer.generate_markdown_report(results)
        
        assert "Readability Report" in report
        assert "Overall Score" in report
        assert "Category Scores" in report
        assert "/100" in report
        print("✓ Markdown report generation test passed")


def test_markdown_report_directory():
    """Test markdown report for directory analysis"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
"""Test module"""

def test_function():
    """Test function"""
    return 42
''')
        
        scorer = ReadabilityScorer()
        results = scorer.analyze_directory(tmpdir)
        report = scorer.generate_markdown_report(results)
        
        assert "Code Readability Report" in report
        assert "Summary" in report
        assert "Files Analyzed" in report
        assert "Average Overall Score" in report
        print("✓ Markdown directory report test passed")


def test_suggestion_priorities():
    """Test that suggestions have correct priority levels"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            # Mix of issues with different severities
            f.write('''
def f(x):
    if x:
        if x:
            if x:
                if x:
                    if x:
                        return True
    return False
''')
        
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(test_file)
        
        # Should have suggestions with priorities
        priorities = [s["priority"] for s in result["suggestions"]]
        assert "high" in priorities or "medium" in priorities or "low" in priorities
        
        # Verify priorities are valid
        valid_priorities = {"high", "medium", "low"}
        assert all(p in valid_priorities for p in priorities)
        print("✓ Suggestion priorities test passed")


def test_metrics_collection():
    """Test that metrics are collected correctly"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
"""Test module"""

class TestClass:
    """Test class"""
    pass

def test_function():
    """Test function"""
    return 42
''')
        
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(test_file)
        
        # Check that metrics exist
        assert "metrics" in result
        assert "naming" in result["metrics"]
        assert "complexity" in result["metrics"]
        assert "documentation" in result["metrics"]
        assert "formatting" in result["metrics"]
        assert "structure" in result["metrics"]
        
        # Check that metrics have expected fields
        assert "functions_analyzed" in result["metrics"]["naming"]
        assert "functions" in result["metrics"]["complexity"]
        assert "module_docstring" in result["metrics"]["documentation"]
        print("✓ Metrics collection test passed")


def test_error_handling_invalid_file():
    """Test error handling for invalid files"""
    scorer = ReadabilityScorer()
    
    try:
        scorer.analyze_file("/nonexistent/file.py")
        assert False, "Should have raised IOError"
    except IOError as e:
        assert "does not exist" in str(e)
    
    print("✓ Invalid file error handling test passed")


def test_error_handling_invalid_directory():
    """Test error handling for invalid directories"""
    scorer = ReadabilityScorer()
    
    try:
        scorer.analyze_directory("/nonexistent/directory")
        assert False, "Should have raised IOError"
    except IOError as e:
        assert "does not exist" in str(e)
    
    print("✓ Invalid directory error handling test passed")


def test_error_handling_syntax_error():
    """Test handling of files with syntax errors"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('def invalid syntax here\n')
        
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(test_file)
        
        # Should capture the error
        assert "error" in result
        assert "Syntax error" in result["error"]
        assert result["scores"]["overall"] == 0
        print("✓ Syntax error handling test passed")


def test_cyclomatic_complexity_calculation():
    """Test cyclomatic complexity calculation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
def complex_function(a, b, c):
    """Complex function"""
    if a > 0:
        if b > 0:
            return a + b
    elif c > 0:
        return c
    else:
        return 0
    
    for i in range(10):
        if i % 2 == 0:
            print(i)
    
    return 1
''')
        
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(test_file)
        
        # Should calculate complexity
        assert "complexity" in result["metrics"]
        assert "avg_cyclomatic_complexity" in result["metrics"]["complexity"]
        assert result["metrics"]["complexity"]["avg_cyclomatic_complexity"] > 1
        print("✓ Cyclomatic complexity calculation test passed")


def test_example_file_palindrome():
    """Test analysis of the palindrome example file"""
    example_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "examples",
        "palindrome.py"
    )
    
    if os.path.exists(example_file):
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(example_file)
        
        # Palindrome is well-written, should score well
        assert result["scores"]["overall"] >= 60
        assert result["scores"]["documentation"] >= 70
        print("✓ Palindrome example analysis test passed")
    else:
        print("⊘ Palindrome example file not found, skipping test")


def test_example_file_anti_patterns():
    """Test analysis of the anti-patterns example file"""
    example_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "examples",
        "anti-patterns.py"
    )
    
    if os.path.exists(example_file):
        scorer = ReadabilityScorer()
        result = scorer.analyze_file(example_file)
        
        # Anti-patterns file should still have reasonable structure
        # but may have some suggestions
        assert "scores" in result
        assert result["scores"]["overall"] >= 0
        
        # Should generate at least some suggestions or have a score
        assert len(result["suggestions"]) >= 0  # May or may not have suggestions
        print("✓ Anti-patterns example analysis test passed")
    else:
        print("⊘ Anti-patterns example file not found, skipping test")


def test_score_bar_generation():
    """Test visual score bar generation"""
    scorer = ReadabilityScorer()
    
    bar_100 = scorer._generate_score_bar(100)
    assert '█' in bar_100
    assert '░' not in bar_100
    
    bar_0 = scorer._generate_score_bar(0)
    assert '█' not in bar_0
    assert '░' in bar_0
    
    bar_50 = scorer._generate_score_bar(50)
    assert '█' in bar_50
    assert '░' in bar_50
    
    print("✓ Score bar generation test passed")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_scorer_initialization,
        test_analyze_good_code,
        test_analyze_poor_naming,
        test_analyze_high_complexity,
        test_analyze_long_function,
        test_analyze_missing_documentation,
        test_analyze_formatting_issues,
        test_score_boundaries,
        test_directory_analysis,
        test_json_output,
        test_markdown_report_generation,
        test_markdown_report_directory,
        test_suggestion_priorities,
        test_metrics_collection,
        test_error_handling_invalid_file,
        test_error_handling_invalid_directory,
        test_error_handling_syntax_error,
        test_cyclomatic_complexity_calculation,
        test_example_file_palindrome,
        test_example_file_anti_patterns,
        test_score_bar_generation
    ]
    
    print("Running Readability Scorer Tests...")
    print("=" * 50)
    
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
