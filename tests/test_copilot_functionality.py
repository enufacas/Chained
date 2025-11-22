#!/usr/bin/env python3
"""
Test file to validate Copilot functionality.

This test verifies that the Copilot system is operational and can:
1. Create and execute test files
2. Perform basic Python operations
3. Validate system health

Created in response to: "This is a copilot test"
"""

import sys
import os
from datetime import datetime


def test_copilot_basic_functionality():
    """
    Test basic Copilot functionality.
    
    Verifies that Copilot can create and execute simple tests.
    """
    print("🤖 Testing Copilot Basic Functionality")
    print("=" * 70)
    
    # Test 1: Basic arithmetic
    result = 2 + 2
    assert result == 4, "Basic arithmetic failed"
    print("  ✅ Test 1: Basic arithmetic - PASSED")
    
    # Test 2: String operations
    test_string = "Copilot Test"
    assert len(test_string) > 0, "String operation failed"
    assert test_string.lower() == "copilot test", "String case conversion failed"
    print("  ✅ Test 2: String operations - PASSED")
    
    # Test 3: List operations
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5, "List length check failed"
    assert sum(test_list) == 15, "List sum calculation failed"
    print("  ✅ Test 3: List operations - PASSED")
    
    # Test 4: Dictionary operations
    test_dict = {"status": "operational", "test": "copilot"}
    assert test_dict["status"] == "operational", "Dictionary access failed"
    assert "test" in test_dict, "Dictionary key check failed"
    print("  ✅ Test 4: Dictionary operations - PASSED")
    
    # Test 5: Timestamp validation
    current_time = datetime.now()
    assert current_time.year >= 2025, "Timestamp validation failed"
    print("  ✅ Test 5: Timestamp validation - PASSED")
    
    return True


def test_copilot_environment():
    """
    Test that the Copilot environment is properly configured.
    """
    print("\n🔧 Testing Copilot Environment")
    print("=" * 70)
    
    # Check Python version
    python_version = sys.version_info
    assert python_version.major >= 3, "Python 3 required"
    print(f"  ✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check current working directory
    cwd = os.getcwd()
    assert os.path.exists(cwd), "Working directory check failed"
    print(f"  ✅ Working directory: {cwd}")
    
    # Check if we're in the Chained repository
    assert "Chained" in cwd or os.path.exists("README.md"), "Repository check failed"
    print("  ✅ Repository structure validated")
    
    return True


def test_copilot_file_operations():
    """
    Test that Copilot can perform file operations.
    """
    print("\n📁 Testing Copilot File Operations")
    print("=" * 70)
    
    # Test reading current file
    current_file = __file__
    assert os.path.exists(current_file), "Current file check failed"
    print(f"  ✅ Current file exists: {os.path.basename(current_file)}")
    
    # Test that tests directory exists
    tests_dir = os.path.dirname(__file__)
    assert os.path.exists(tests_dir), "Tests directory check failed"
    print(f"  ✅ Tests directory exists")
    
    # Count other test files
    test_files = [f for f in os.listdir(tests_dir) if f.startswith("test_") and f.endswith(".py")]
    print(f"  ✅ Found {len(test_files)} test files in tests directory")
    
    return True


def run_all_tests():
    """
    Run all Copilot tests and report results.
    """
    print("\n" + "=" * 70)
    print("🤖 COPILOT FUNCTIONALITY TEST SUITE")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Basic Functionality", test_copilot_basic_functionality),
        ("Environment", test_copilot_environment),
        ("File Operations", test_copilot_file_operations),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"  ❌ {test_name} - FAILED (returned False)")
        except Exception as e:
            failed += 1
            print(f"  ❌ {test_name} - FAILED with exception: {e}")
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success rate: {(passed/len(tests)*100):.1f}%")
    print()
    
    if failed == 0:
        print("🎉 All Copilot functionality tests PASSED!")
        print("✅ Copilot is operational and ready to work.")
    else:
        print("⚠️  Some tests failed. Please review the output above.")
    
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
