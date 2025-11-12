#!/usr/bin/env python3
"""
Test to verify the issue format fix in agent-issue-discussion.yml workflow.

This test verifies that the workflow correctly handles issue numbers that
come in as floating-point format (e.g., "432.0") from GitHub Actions
workflow_dispatch inputs with type: number.
"""

import subprocess
import sys


def test_printf_conversion():
    """Test that printf correctly converts float-formatted numbers to integers."""
    test_cases = [
        ("432", "432"),
        ("432.0", "432"),
        ("1", "1"),
        ("1.0", "1"),
        ("999", "999"),
        ("999.0", "999"),
        ("12345", "12345"),
        ("12345.0", "12345"),
    ]
    
    print("Testing issue number format conversion with printf...")
    passed = 0
    failed = 0
    
    for input_val, expected in test_cases:
        # Simulate the bash printf command used in the workflow
        result = subprocess.run(
            ['bash', '-c', f'printf "%.0f" "{input_val}"'],
            capture_output=True,
            text=True
        )
        
        actual = result.stdout.strip()
        
        if actual == expected:
            print(f"  ✓ PASS: {input_val} -> {actual}")
            passed += 1
        else:
            print(f"  ✗ FAIL: {input_val} -> {actual} (expected {expected})")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_workflow_yaml_valid():
    """Test that the workflow YAML is still valid after changes."""
    import yaml
    from pathlib import Path
    
    workflow_path = Path('.github/workflows/agent-issue-discussion.yml')
    
    if not workflow_path.exists():
        print("❌ Workflow file not found")
        return False
    
    try:
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Verify the workflow has the expected structure
        assert 'name' in workflow, "Workflow missing 'name' field"
        assert 'jobs' in workflow, "Workflow missing 'jobs' field"
        assert 'agent-discussion' in workflow['jobs'], "Workflow missing 'agent-discussion' job"
        
        print("✓ Workflow YAML is valid and has expected structure")
        return True
    except Exception as e:
        print(f"❌ Workflow YAML validation failed: {e}")
        return False


def test_workflow_has_fix():
    """Verify that the fix is present in the workflow."""
    from pathlib import Path
    
    workflow_path = Path('.github/workflows/agent-issue-discussion.yml')
    
    if not workflow_path.exists():
        print("❌ Workflow file not found")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # Check that the fix (printf conversion) is present
    if 'printf "%.0f"' in content or 'printf %.0f' in content:
        print("✓ Fix is present in workflow (printf conversion found)")
        return True
    else:
        print("❌ Fix not found in workflow")
        return False


def main():
    """Run all tests."""
    print("="*70)
    print("🧪 Issue Format Fix Validation Tests")
    print("="*70)
    print()
    
    tests = [
        ("Printf Conversion", test_printf_conversion),
        ("Workflow YAML Valid", test_workflow_yaml_valid),
        ("Fix Present in Workflow", test_workflow_has_fix),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        print("-"*70)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
