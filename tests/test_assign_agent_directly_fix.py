#!/usr/bin/env python3
"""
Test to verify the fix for assign-agent-directly.sh script.

This test verifies that when assign-agent-directly.sh is called with a specific
agent specialization (e.g., "engineer-master"), it correctly retrieves and uses
that agent's information instead of incorrectly calling match-issue-to-agent.py
with a generic "agent-mission" title.

Bug fixed: The script was calling match-issue-to-agent.py with "agent-mission"
which would return the wrong agent (meta-coordinator) instead of using the
specified agent (e.g., engineer-master).

Fix: Changed line 34 to use get-agent-info.py to directly get the specified
agent's information.
"""

import subprocess
import json
import sys
from pathlib import Path


def test_agent_info_retrieval():
    """
    Test that the script correctly retrieves agent info for the specified agent.
    
    This simulates what happens in assign-agent-directly.sh:
    1. Old behavior: Called match-issue-to-agent.py with "agent-mission" 
       -> Returns meta-coordinator
    2. New behavior: Calls get-agent-info.py with the specified agent
       -> Returns correct agent info
    """
    print("🧪 Testing Agent Info Retrieval Fix")
    print("=" * 70)
    print()
    
    # Test agents to verify
    test_agents = [
        "engineer-master",
        "secure-specialist", 
        "create-guru",
        "assert-specialist",
        "organize-guru"
    ]
    
    passed = 0
    failed = 0
    
    for agent_name in test_agents:
        # Test the NEW fixed behavior (using get-agent-info.py)
        try:
            result = subprocess.run(
                ['python3', 'tools/get-agent-info.py', 'info', agent_name],
                capture_output=True,
                text=True,
                check=True,
                cwd='.'
            )
            agent_info = json.loads(result.stdout)
            
            # Verify the agent name matches what we requested
            if agent_info.get('name') == agent_name:
                print(f"✅ PASSED: {agent_name}")
                print(f"   → Got correct agent info")
                print(f"   → Emoji: {agent_info.get('emoji', 'N/A')}")
                print(f"   → Description: {agent_info.get('description', 'N/A')[:60]}...")
                passed += 1
            else:
                print(f"❌ FAILED: {agent_name}")
                print(f"   → Expected name: {agent_name}")
                print(f"   → Got name: {agent_info.get('name')}")
                failed += 1
                
        except Exception as e:
            print(f"❌ FAILED: {agent_name}")
            print(f"   → Error: {e}")
            failed += 1
        
        print()
    
    print("=" * 70)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print()
    
    return failed == 0


def test_old_vs_new_behavior():
    """
    Test that demonstrates the bug that was fixed.
    
    Old behavior (buggy):
    - Called match-issue-to-agent.py "agent-mission" ""
    - Would return meta-coordinator regardless of the agent we wanted
    
    New behavior (fixed):
    - Calls get-agent-info.py info <agent_name>
    - Returns the correct agent we actually want
    """
    print("🧪 Testing Old vs New Behavior")
    print("=" * 70)
    print()
    
    # Test what OLD buggy code would return
    print("OLD BUGGY BEHAVIOR (calling match-issue-to-agent.py):")
    try:
        result = subprocess.run(
            ['python3', 'tools/match-issue-to-agent.py', 'agent-mission', ''],
            capture_output=True,
            text=True,
            check=True,
            cwd='.'
        )
        old_agent_info = json.loads(result.stdout)
        old_agent = old_agent_info.get('agent')
        print(f"   → Returns: {old_agent}")
        print(f"   ❌ This is WRONG when we want engineer-master")
    except Exception as e:
        print(f"   → Error: {e}")
        return False
    
    print()
    
    # Test what NEW fixed code returns
    print("NEW FIXED BEHAVIOR (calling get-agent-info.py):")
    try:
        result = subprocess.run(
            ['python3', 'tools/get-agent-info.py', 'info', 'engineer-master'],
            capture_output=True,
            text=True,
            check=True,
            cwd='.'
        )
        new_agent_info = json.loads(result.stdout)
        new_agent = new_agent_info.get('name')
        print(f"   → Returns: {new_agent}")
        print(f"   ✅ This is CORRECT - we wanted engineer-master")
    except Exception as e:
        print(f"   → Error: {e}")
        return False
    
    print()
    print("=" * 70)
    
    # Verify the fix works
    if old_agent != 'engineer-master' and new_agent == 'engineer-master':
        print("✅ FIX VERIFIED: The new code returns the correct agent!")
        print()
        return True
    else:
        print("❌ FIX NOT WORKING: The behavior is still incorrect")
        print()
        return False


def main():
    """Run all tests for the assign-agent-directly.sh fix."""
    print()
    print("=" * 70)
    print("🎯 ASSIGN-AGENT-DIRECTLY.SH FIX VERIFICATION")
    print("=" * 70)
    print()
    print("Testing the fix for the direct agent assignment bug where")
    print("the script was calling match-issue-to-agent.py with a generic")
    print("'agent-mission' title instead of getting info for the specified agent.")
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
    
    results.append(("Old vs New Behavior", test_old_vs_new_behavior()))
    results.append(("Agent Info Retrieval", test_agent_info_retrieval()))
    
    # Summary
    print()
    print("=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print()
    
    passed_suites = sum(1 for _, result in results if result)
    total_suites = len(results)
    
    for suite_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {suite_name}")
    
    print()
    print(f"Total: {passed_suites}/{total_suites} test suites passed")
    print()
    
    if passed_suites == total_suites:
        print("✅ All tests passed! The fix is working correctly.")
        print()
        print("Summary of the fix:")
        print("  • Changed assign-agent-directly.sh line 34")
        print("  • OLD: match-issue-to-agent.py 'agent-mission' ''")
        print("  • NEW: get-agent-info.py info $matched_agent")
        print("  • Result: Correct agent info is now retrieved")
        print()
        return 0
    else:
        print(f"❌ {total_suites - passed_suites} test suite(s) failed")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
