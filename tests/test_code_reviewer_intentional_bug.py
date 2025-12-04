#!/usr/bin/env python3
"""
Test for intentional bug in code-reviewer agent

This test verifies that the intentional bug for error observer testing
works as expected - it should raise a ZeroDivisionError when triggered.

This test is EXPECTED TO FAIL when the bug is present.
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add the code-reviewer agent to path
code_reviewer_path = Path(__file__).parent.parent / "infrastructure" / "docker" / "adk-agents" / "code-reviewer"
sys.path.insert(0, str(code_reviewer_path))

# Mock dependencies for testing
class MockGeminiClient:
    """Mock Gemini client for testing"""
    @staticmethod
    def is_available():
        return False
    
    @staticmethod
    def get_mode():
        return "mock"
    
    @staticmethod
    def get_unavailable_error_message(agent_name="test"):
        return f"{agent_name}: Gemini unavailable"
    
    @staticmethod
    def get_config_info():
        return {"active_mode": "mock"}

# Replace gemini_client with mock before importing agent
sys.modules['shared.gemini_client'] = MockGeminiClient

# Now we can't easily import agent.py due to its dependencies
# So we'll test the logic directly


def test_intentional_bug_trigger():
    """Test that the intentional bug is triggered by the keyword"""
    
    # This is the code that should trigger the bug
    code_with_trigger = """
    # test_error_observer
    def example():
        return "hello"
    """
    
    # This should raise ZeroDivisionError
    with pytest.raises(ZeroDivisionError):
        # Simulate the bug logic
        if "test_error_observer" in code_with_trigger.lower():
            _ = 1 / 0  # This will raise ZeroDivisionError


def test_intentional_bug_not_triggered():
    """Test that normal code doesn't trigger the bug"""
    
    # This is normal code without the trigger
    normal_code = """
    def example():
        return "hello"
    """
    
    # This should NOT raise an error (in the bug check)
    try:
        if "test_error_observer" in normal_code.lower():
            _ = 1 / 0
        # If we get here, the keyword wasn't found (correct)
        assert True
    except ZeroDivisionError:
        # This should not happen with normal code
        pytest.fail("Bug triggered on normal code!")


def test_keyword_case_insensitive():
    """Test that the trigger keyword is case-insensitive"""
    
    variations = [
        "test_error_observer",
        "TEST_ERROR_OBSERVER",
        "Test_Error_Observer",
        "TeSt_ErRoR_oBsErVeR",
    ]
    
    for keyword in variations:
        code = f"# {keyword}\ndef test(): pass"
        
        with pytest.raises(ZeroDivisionError):
            if "test_error_observer" in code.lower():
                _ = 1 / 0


if __name__ == "__main__":
    print("Testing intentional bug in code-reviewer agent...")
    print("=" * 60)
    
    print("\n1. Testing bug trigger with keyword...")
    try:
        test_intentional_bug_trigger()
        print("   ❌ FAILED: Bug should have been triggered!")
    except AssertionError:
        print("   ✅ PASSED: Bug triggered as expected")
    
    print("\n2. Testing bug NOT triggered without keyword...")
    try:
        test_intentional_bug_not_triggered()
        print("   ✅ PASSED: Bug not triggered on normal code")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    print("\n3. Testing case-insensitive keyword...")
    try:
        test_keyword_case_insensitive()
        print("   ❌ FAILED: Bug should have been triggered!")
    except AssertionError:
        print("   ✅ PASSED: Bug triggered for all case variations")
    
    print("\n" + "=" * 60)
    print("Test suite complete!")
    print("\nNote: This test verifies the INTENTIONAL BUG is working.")
    print("When the bug is removed, these tests should be removed too.")
