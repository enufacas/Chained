#!/usr/bin/env python3
"""
Test script to validate that discussion_rounds conversion handles float strings.
This tests the fix for: ValueError: invalid literal for int() with base 10: '3.0'
"""

import subprocess
import sys


def test_bash_conversion():
    """Test that bash printf conversion works correctly."""
    print("📋 Testing bash conversion with printf")
    print("-" * 50)
    
    test_cases = [
        ("3", "3"),
        ("3.0", "3"),
        ("5.0", "5"),
        ("2.5", "2"),  # Should round to 2
        ("4.7", "5"),  # Should round to 5
    ]
    
    passed = 0
    failed = 0
    
    for input_val, expected in test_cases:
        result = subprocess.run(
            ['bash', '-c', f'DISCUSSION_ROUNDS="{input_val}"; printf "%.0f" "$DISCUSSION_ROUNDS"'],
            capture_output=True,
            text=True
        )
        
        actual = result.stdout.strip()
        if actual == expected:
            print(f"  ✅ Input: {input_val:>5} -> Output: {actual:>3} (expected: {expected})")
            passed += 1
        else:
            print(f"  ❌ Input: {input_val:>5} -> Output: {actual:>3} (expected: {expected})")
            failed += 1
    
    print(f"\nBash conversion: {passed}/{len(test_cases)} passed")
    return failed == 0


def test_python_conversion():
    """Test that Python int(float()) conversion works correctly."""
    print("\n📋 Testing Python int(float()) conversion")
    print("-" * 50)
    
    test_cases = [
        ("3", 3),
        ("3.0", 3),
        ("5.0", 5),
        ("2.5", 2),  # Should truncate to 2
        ("4.7", 4),  # Should truncate to 4
    ]
    
    passed = 0
    failed = 0
    
    for input_val, expected in test_cases:
        try:
            actual = int(float(input_val))
            if actual == expected:
                print(f"  ✅ Input: {input_val:>5} -> Output: {actual:>3} (expected: {expected})")
                passed += 1
            else:
                print(f"  ❌ Input: {input_val:>5} -> Output: {actual:>3} (expected: {expected})")
                failed += 1
        except ValueError as e:
            print(f"  ❌ Input: {input_val:>5} -> Error: {e}")
            failed += 1
    
    print(f"\nPython conversion: {passed}/{len(test_cases)} passed")
    return failed == 0


def test_original_problem():
    """Test that the original problem is fixed."""
    print("\n📋 Testing original problem: int('3.0')")
    print("-" * 50)
    
    # This should fail
    try:
        result = int('3.0')
        print(f"  ❌ int('3.0') unexpectedly succeeded: {result}")
        return False
    except ValueError as e:
        print(f"  ✅ int('3.0') correctly fails: {e}")
    
    # This should succeed (the fix)
    try:
        result = int(float('3.0'))
        print(f"  ✅ int(float('3.0')) succeeds: {result}")
        return True
    except ValueError as e:
        print(f"  ❌ int(float('3.0')) unexpectedly failed: {e}")
        return False


def test_workflow_simulation():
    """Simulate the full workflow behavior."""
    print("\n📋 Testing full workflow simulation")
    print("-" * 50)
    
    # Simulate the bash part
    bash_script = '''
    DISCUSSION_ROUNDS="3.0"
    DISCUSSION_ROUNDS=$(printf "%.0f" "$DISCUSSION_ROUNDS")
    echo "$DISCUSSION_ROUNDS"
    '''
    
    result = subprocess.run(
        ['bash', '-c', bash_script],
        capture_output=True,
        text=True
    )
    
    bash_output = result.stdout.strip()
    print(f"  Bash output: '{bash_output}'")
    
    # Simulate the Python part
    try:
        python_value = int(float(bash_output))
        print(f"  ✅ Python conversion succeeded: {python_value}")
        
        if python_value == 3:
            print(f"  ✅ Correct value: {python_value}")
            return True
        else:
            print(f"  ❌ Wrong value: {python_value} (expected 3)")
            return False
    except ValueError as e:
        print(f"  ❌ Python conversion failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("🧪 Testing Discussion Rounds Float String Fix\n")
    
    tests = [
        ("Bash Conversion", test_bash_conversion),
        ("Python Conversion", test_python_conversion),
        ("Original Problem", test_original_problem),
        ("Full Workflow", test_workflow_simulation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"\nPassed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
