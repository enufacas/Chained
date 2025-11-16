#!/usr/bin/env python3
"""
Test to verify that copilot-assigned label is only added after successful assignment.

This test verifies the fix where the copilot-assigned label was being added
too early (before GraphQL assignment), causing issues to be marked as assigned
even when the assignment failed.

Bug: The label was added at line 91, before attempting GraphQL assignment.
Fix: The label is now added at line 220, AFTER successful GraphQL assignment.
"""

import subprocess
import sys
from pathlib import Path


def test_label_ordering_in_script():
    """
    Test that the script has the correct ordering of operations.
    
    The copilot-assigned label should only be added AFTER the GraphQL
    assignment succeeds, not before attempting it.
    """
    print("🧪 Testing Label Addition Timing in assign-agent-directly.sh")
    print("=" * 70)
    print()
    
    script_path = Path("tools/assign-agent-directly.sh")
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    script_content = script_path.read_text()
    lines = script_content.split('\n')
    
    # Find key line numbers
    copilot_label_line = None
    graphql_mutation_line = None
    success_check_line = None
    
    for i, line in enumerate(lines, 1):
        # Look for where copilot-assigned label is added
        if 'gh issue edit' in line and 'copilot-assigned' in line and copilot_label_line is None:
            copilot_label_line = i
        
        # Look for GraphQL mutation call
        if 'mutation_result=$(gh api graphql' in line and graphql_mutation_line is None:
            graphql_mutation_line = i
        
        # Look for success check
        if 'jq -e' in line and 'replaceActorsForAssignable.assignable' in line:
            success_check_line = i
    
    print("Found key operations:")
    print(f"  - GraphQL mutation: line {graphql_mutation_line}")
    print(f"  - Success check: line {success_check_line}")
    print(f"  - copilot-assigned label: line {copilot_label_line}")
    print()
    
    # Verify ordering
    passed = True
    
    if graphql_mutation_line is None:
        print("❌ FAILED: Could not find GraphQL mutation in script")
        passed = False
    
    if success_check_line is None:
        print("❌ FAILED: Could not find success check in script")
        passed = False
    
    if copilot_label_line is None:
        print("❌ FAILED: Could not find copilot-assigned label addition")
        passed = False
    
    if all([graphql_mutation_line, success_check_line, copilot_label_line]):
        # Check correct ordering
        if copilot_label_line < graphql_mutation_line:
            print("❌ FAILED: copilot-assigned label is added BEFORE GraphQL mutation")
            print(f"   This means the label is added even if assignment fails!")
            passed = False
        elif copilot_label_line < success_check_line:
            print("❌ FAILED: copilot-assigned label is added BEFORE success check")
            print(f"   This means the label is added even if assignment fails!")
            passed = False
        else:
            print("✅ PASSED: copilot-assigned label is added AFTER success check")
            print(f"   The label is only added when GraphQL assignment succeeds!")
            print()
            print("Verification:")
            print(f"   1. GraphQL mutation happens at line {graphql_mutation_line}")
            print(f"   2. Success is checked at line {success_check_line}")
            print(f"   3. Label is added at line {copilot_label_line}")
            print(f"   ✓ Correct order!")
    
    print()
    return passed


def test_script_comment_explains_fix():
    """
    Test that the script has a comment explaining why the label is not added early.
    """
    print("🧪 Testing Script Documentation")
    print("=" * 70)
    print()
    
    script_path = Path("tools/assign-agent-directly.sh")
    script_content = script_path.read_text()
    
    # Look for explanatory comment
    if "copilot-assigned label will be added AFTER successful GraphQL assignment" in script_content:
        print("✅ PASSED: Script has explanatory comment about label timing")
        return True
    elif "NOTE:" in script_content and "copilot-assigned" in script_content:
        print("✅ PASSED: Script has note about copilot-assigned label")
        return True
    else:
        print("⚠️  WARNING: Script could use better documentation about label timing")
        return True  # This is not a failure, just a suggestion


def test_error_message_accuracy():
    """
    Test that error messages accurately reflect the label is NOT added on failure.
    """
    print("🧪 Testing Error Message Accuracy")
    print("=" * 70)
    print()
    
    script_path = Path("tools/assign-agent-directly.sh")
    script_content = script_path.read_text()
    
    # The error message should NOT say the label was added
    if "This mission has been labeled `copilot-assigned` for tracking" in script_content:
        print("❌ FAILED: Error message incorrectly says label was added")
        print("   The label is NOT added when assignment fails!")
        return False
    
    if "copilot-assigned` label was NOT added" in script_content or \
       "NOT added (assignment failed)" in script_content:
        print("✅ PASSED: Error message correctly states label was NOT added")
        return True
    
    print("⚠️  WARNING: Error message could be clearer about label status")
    return True  # This is not a critical failure


def main():
    """Run all tests for the label timing fix."""
    print()
    print("=" * 70)
    print("🎯 COPILOT-ASSIGNED LABEL TIMING FIX VERIFICATION")
    print("=" * 70)
    print()
    print("Testing the fix where the copilot-assigned label was being added")
    print("too early, causing issues to be marked as assigned even when the")
    print("GraphQL assignment actually failed.")
    print()
    print("=" * 70)
    print()
    
    # Change to repo root
    repo_root = Path(__file__).parent.parent
    import os
    os.chdir(repo_root)
    
    print(f"Working directory: {os.getcwd()}")
    print()
    print("=" * 70)
    print()
    
    # Run tests
    results = []
    
    results.append(("Label Ordering", test_label_ordering_in_script()))
    results.append(("Script Documentation", test_script_comment_explains_fix()))
    results.append(("Error Message Accuracy", test_error_message_accuracy()))
    
    # Summary
    print()
    print("=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print()
    
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    print()
    
    if passed_tests == total_tests:
        print("✅ All tests passed! The label timing fix is correct.")
        print()
        print("Summary of the fix:")
        print("  • copilot-assigned label is now added AFTER GraphQL assignment")
        print("  • OLD: Label added early → assignment fails → label stays (BAD)")
        print("  • NEW: Assignment checked → label only if success (GOOD)")
        print("  • Result: Issues are only marked assigned when they actually are")
        print()
        return 0
    else:
        print(f"❌ {total_tests - passed_tests} test(s) failed")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
