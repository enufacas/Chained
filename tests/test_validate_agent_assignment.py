#!/usr/bin/env python3
"""
Tests for the validate-agent-assignment.py tool.

Created by @create-guru to verify the agent assignment validation tool works correctly.
"""

import subprocess
import sys
from pathlib import Path


def test_validate_existing_agent():
    """Test validating an existing agent (create-guru)."""
    print("🧪 Test: Validate existing agent (@create-guru)")
    print("=" * 70)
    
    result = subprocess.run(
        ["python3", "tools/validate-agent-assignment.py", "validate", "create-guru"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    if result.returncode == 0:
        print("✅ PASSED: create-guru validation successful")
        print(f"   Output: {result.stdout.strip()[:100]}...")
        return True
    else:
        print("❌ FAILED: create-guru validation failed")
        print(f"   Error: {result.stderr}")
        return False


def test_validate_nonexistent_agent():
    """Test validating a non-existent agent."""
    print("\n🧪 Test: Validate non-existent agent")
    print("=" * 70)
    
    result = subprocess.run(
        ["python3", "tools/validate-agent-assignment.py", "validate", "nonexistent-agent"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    if result.returncode != 0:
        print("✅ PASSED: Correctly failed for non-existent agent")
        return True
    else:
        print("❌ FAILED: Should have failed for non-existent agent")
        return False


def test_list_agents():
    """Test listing all available agents."""
    print("\n🧪 Test: List all agents")
    print("=" * 70)
    
    result = subprocess.run(
        ["python3", "tools/validate-agent-assignment.py", "list"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    if result.returncode == 0 and "@create-guru" in result.stdout:
        print("✅ PASSED: Agent list contains @create-guru")
        # Count how many agents are listed
        agent_count = result.stdout.count("• @")
        print(f"   Found {agent_count} agents")
        return True
    else:
        print("❌ FAILED: Agent list missing or incomplete")
        return False


def test_multiple_agent_validations():
    """Test validating multiple well-known agents."""
    print("\n🧪 Test: Validate multiple agents")
    print("=" * 70)
    
    test_agents = ["engineer-master", "secure-specialist", "organize-guru"]
    passed = 0
    
    for agent in test_agents:
        result = subprocess.run(
            ["python3", "tools/validate-agent-assignment.py", "validate", agent],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print(f"✅ @{agent}: Valid")
            passed += 1
        else:
            print(f"❌ @{agent}: Invalid")
    
    if passed == len(test_agents):
        print(f"✅ PASSED: All {passed}/{len(test_agents)} agents validated successfully")
        return True
    else:
        print(f"❌ FAILED: Only {passed}/{len(test_agents)} agents validated")
        return False


def main():
    """Run all tests for the validate-agent-assignment tool."""
    print("\n" + "=" * 70)
    print("🎯 VALIDATE-AGENT-ASSIGNMENT TOOL TESTS")
    print("=" * 70)
    print("Testing the agent assignment validation tool created by @create-guru")
    print("=" * 70 + "\n")
    
    # Change to repo root
    repo_root = Path(__file__).parent.parent
    import os
    os.chdir(repo_root)
    
    tests = [
        ("Validate existing agent", test_validate_existing_agent),
        ("Validate non-existent agent", test_validate_nonexistent_agent),
        ("List agents", test_list_agents),
        ("Multiple agent validations", test_multiple_agent_validations),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ EXCEPTION in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Tool is working correctly.")
        print("\n📝 Tool created by @create-guru for validating agent assignments")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
