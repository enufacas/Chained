#!/usr/bin/env python3
"""
Tests for the Self-Improving Code Analyzer
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
import importlib.util

# Load the analyzer module
spec = importlib.util.spec_from_file_location(
    "code_analyzer",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "code-analyzer.py")
)
code_analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_analyzer)

CodeAnalyzer = code_analyzer.CodeAnalyzer


def test_pattern_initialization():
    """Test that pattern database initializes correctly"""
    with tempfile.TemporaryDirectory() as tmpdir:
        patterns_file = os.path.join(tmpdir, "patterns.json")
        analyzer = CodeAnalyzer(patterns_file=patterns_file)
        
        assert analyzer.patterns_data["version"] == "1.0.0"
        assert analyzer.patterns_data["total_merges_analyzed"] == 0
        assert "good_patterns" in analyzer.patterns_data
        assert "bad_patterns" in analyzer.patterns_data
        print("✓ Pattern initialization test passed")


def test_detect_good_patterns():
    """Test detection of good code patterns"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
def calculate_sum(numbers: list) -> int:
    """Calculate the sum of a list of numbers"""
    try:
        result = sum(numbers)
        return result
    except TypeError:
        return 0
''')
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_python_file(test_file)
        
        # Should detect good patterns
        good_patterns = [p["type"] for p in result["patterns_found"]["good"]]
        assert "comprehensive_docstrings" in good_patterns
        assert "error_handling" in good_patterns
        assert "type_hints" in good_patterns
        assert "modular_functions" in good_patterns
        print("✓ Good pattern detection test passed")


def test_detect_bad_patterns():
    """Test detection of bad code patterns"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
def bad_function():
    x = 42
    if True:
        if True:
            if True:
                if True:
                    if True:
                        print("Deep nesting")
''')
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_python_file(test_file)
        
        # Should detect bad patterns
        bad_patterns = [p["type"] for p in result["patterns_found"]["bad"]]
        assert "deep_nesting" in bad_patterns
        assert "magic_numbers" in bad_patterns
        print("✓ Bad pattern detection test passed")


def test_long_function_detection():
    """Test detection of long functions"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        # Create a function with more than 50 lines
        lines = ["def long_function():"]
        for i in range(60):
            lines.append(f"    x = {i}")
        
        with open(test_file, 'w') as f:
            f.write('\n'.join(lines))
        
        analyzer = CodeAnalyzer()
        result = analyzer.analyze_python_file(test_file)
        
        bad_patterns = [p["type"] for p in result["patterns_found"]["bad"]]
        assert "long_functions" in bad_patterns
        print("✓ Long function detection test passed")


def test_learning_from_successful_merge():
    """Test that analyzer learns from successful merges"""
    with tempfile.TemporaryDirectory() as tmpdir:
        patterns_file = os.path.join(tmpdir, "patterns.json")
        analyzer = CodeAnalyzer(patterns_file=patterns_file)
        
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
def good_function(x: int) -> int:
    """A well-documented function"""
    return x * 2
''')
        
        # Analyze the file
        result = analyzer.analyze_python_file(test_file)
        analysis_results = {
            "timestamp": "2024-01-01T00:00:00",
            "directory": tmpdir,
            "files_analyzed": [result],
            "summary": {
                "total_files": 1,
                "total_good_patterns": len(result["patterns_found"]["good"]),
                "total_bad_patterns": len(result["patterns_found"]["bad"]),
                "pattern_breakdown": {}
            }
        }
        
        # Learn from successful merge
        initial_count = analyzer.patterns_data["total_merges_analyzed"]
        analyzer.learn_from_merge(analysis_results, merge_successful=True)
        
        assert analyzer.patterns_data["total_merges_analyzed"] == initial_count + 1
        assert len(analyzer.patterns_data["merge_history"]) > 0
        
        # Check that good patterns have positive correlation
        for pattern_name, pattern_data in analyzer.patterns_data["good_patterns"].items():
            if pattern_data["count"] > 0:
                assert pattern_data["correlation_with_success"] >= 0
        
        print("✓ Learning from successful merge test passed")


def test_learning_from_failed_merge():
    """Test that analyzer learns from failed merges"""
    with tempfile.TemporaryDirectory() as tmpdir:
        patterns_file = os.path.join(tmpdir, "patterns.json")
        analyzer = CodeAnalyzer(patterns_file=patterns_file)
        
        test_file = os.path.join(tmpdir, "test.py")
        # Create bad code
        lines = ["def bad_function():"]
        for i in range(60):
            lines.append(f"    x = {i}")
        
        with open(test_file, 'w') as f:
            f.write('\n'.join(lines))
        
        result = analyzer.analyze_python_file(test_file)
        analysis_results = {
            "timestamp": "2024-01-01T00:00:00",
            "directory": tmpdir,
            "files_analyzed": [result],
            "summary": {
                "total_files": 1,
                "total_good_patterns": len(result["patterns_found"]["good"]),
                "total_bad_patterns": len(result["patterns_found"]["bad"]),
                "pattern_breakdown": {}
            }
        }
        
        # Learn from failed merge
        analyzer.learn_from_merge(analysis_results, merge_successful=False)
        
        # Check that bad patterns have issue correlation
        for pattern_name, pattern_data in analyzer.patterns_data["bad_patterns"].items():
            if pattern_data["count"] > 0:
                # After a failed merge, correlation should be updated
                assert "correlation_with_issues" in pattern_data
        
        print("✓ Learning from failed merge test passed")


def test_pattern_persistence():
    """Test that patterns are saved and loaded correctly"""
    with tempfile.TemporaryDirectory() as tmpdir:
        patterns_file = os.path.join(tmpdir, "patterns.json")
        
        # Create analyzer and add some data
        analyzer1 = CodeAnalyzer(patterns_file=patterns_file)
        analyzer1.patterns_data["total_merges_analyzed"] = 5
        analyzer1._save_patterns()
        
        # Load with new analyzer instance
        analyzer2 = CodeAnalyzer(patterns_file=patterns_file)
        assert analyzer2.patterns_data["total_merges_analyzed"] == 5
        assert analyzer2.patterns_data["last_updated"] is not None
        
        print("✓ Pattern persistence test passed")


def test_directory_analysis():
    """Test analyzing multiple files in a directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple test files
        for i in range(3):
            test_file = os.path.join(tmpdir, f"test{i}.py")
            with open(test_file, 'w') as f:
                f.write(f'''
def function{i}():
    """Function {i}"""
    return {i}
''')
        
        analyzer = CodeAnalyzer()
        results = analyzer.analyze_directory(tmpdir)
        
        assert results["summary"]["total_files"] == 3
        assert len(results["files_analyzed"]) == 3
        assert results["summary"]["total_good_patterns"] > 0
        
        print("✓ Directory analysis test passed")


def test_report_generation():
    """Test that reports are generated correctly"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
def sample():
    """A sample function"""
    return 42
''')
        
        analyzer = CodeAnalyzer()
        results = analyzer.analyze_directory(tmpdir)
        report = analyzer.generate_report(results)
        
        assert "Code Analysis Report" in report
        assert "Summary" in report
        assert "files analyzed:" in report.lower()
        
        print("✓ Report generation test passed")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_pattern_initialization,
        test_detect_good_patterns,
        test_detect_bad_patterns,
        test_long_function_detection,
        test_learning_from_successful_merge,
        test_learning_from_failed_merge,
        test_pattern_persistence,
        test_directory_analysis,
        test_report_generation
    ]
    
    print("Running Code Analyzer Tests...")
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
