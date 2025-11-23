#!/usr/bin/env python3
"""
Test suite for explicit agent marker detection in assign-copilot-to-issue.sh

This test validates that issues with explicit agent markers like 
<!-- COPILOT_AGENT:meta-coordinator-system --> are correctly detected
and assigned to the specified agent.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def run_marker_extraction_test(issue_body: str, expected_agent: str = None):
    """
    Test that the agent marker extraction works correctly.
    
    Args:
        issue_body: The issue body content
        expected_agent: Expected agent name to extract (None if no marker expected)
    
    Returns:
        Tuple of (success: bool, actual_agent: str or None)
    """
    # Use the same regex pattern as in the shell script
    result = subprocess.run(
        ['bash', '-c', 'echo "$1" | grep -oP \'<!-- COPILOT_AGENT:\\K[a-zA-Z0-9_-]+\' | head -1', 
         'bash', issue_body],
        capture_output=True,
        text=True,
        cwd='/home/runner/work/Chained/Chained'
    )
    
    actual_agent = result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None
    
    success = actual_agent == expected_agent
    return success, actual_agent

def test_meta_coordinator_marker():
    """Test extraction of meta-coordinator-system marker."""
    print("\n🧪 Test 1: Meta-coordinator explicit marker")
    print("-" * 60)
    
    issue_body = """<!-- COPILOT_AGENT:meta-coordinator-system -->

## 🎯 Meta-Coordination Request

> **🤖 Agent Profile**: This issue requires the **@meta-coordinator-system** agent.
> Please use the specialized approach defined in `.github/agents/meta-coordinator-system.md`
"""
    
    success, actual = run_marker_extraction_test(issue_body, "meta-coordinator-system")
    
    if success:
        print(f"✅ PASSED: Extracted correct agent: {actual}")
        return True
    else:
        print(f"❌ FAILED: Expected 'meta-coordinator-system', got '{actual}'")
        return False

def test_no_marker():
    """Test that absence of marker is correctly detected."""
    print("\n🧪 Test 2: No explicit marker (regular issue)")
    print("-" * 60)
    
    issue_body = """## Feature Request

Please implement user authentication with OAuth2 support.

This will enable users to log in with their GitHub accounts.
"""
    
    success, actual = run_marker_extraction_test(issue_body, None)
    
    if success:
        print(f"✅ PASSED: Correctly detected no marker")
        return True
    else:
        print(f"❌ FAILED: Expected no marker, got '{actual}'")
        return False

def test_different_agent_marker():
    """Test extraction of different agent marker."""
    print("\n🧪 Test 3: Different agent marker")
    print("-" * 60)
    
    issue_body = """<!-- COPILOT_AGENT:troubleshoot-expert -->

## Workflow Failure Investigation

The CI pipeline is failing on step 3. Please investigate.
"""
    
    success, actual = run_marker_extraction_test(issue_body, "troubleshoot-expert")
    
    if success:
        print(f"✅ PASSED: Extracted correct agent: {actual}")
        return True
    else:
        print(f"❌ FAILED: Expected 'troubleshoot-expert', got '{actual}'")
        return False

def test_marker_with_dashes():
    """Test extraction of agent name with multiple dashes."""
    print("\n🧪 Test 4: Agent name with dashes")
    print("-" * 60)
    
    issue_body = """<!-- COPILOT_AGENT:github-pages-tech-lead -->

## GitHub Pages Issue

The site is not rendering correctly on mobile devices.
"""
    
    success, actual = run_marker_extraction_test(issue_body, "github-pages-tech-lead")
    
    if success:
        print(f"✅ PASSED: Extracted correct agent: {actual}")
        return True
    else:
        print(f"❌ FAILED: Expected 'github-pages-tech-lead', got '{actual}'")
        return False

def test_marker_in_middle():
    """Test that only the first marker is extracted when multiple exist."""
    print("\n🧪 Test 5: Multiple markers (should extract first)")
    print("-" * 60)
    
    issue_body = """Some content before

<!-- COPILOT_AGENT:secure-specialist -->

More content

<!-- COPILOT_AGENT:engineer-master -->

Even more content
"""
    
    success, actual = run_marker_extraction_test(issue_body, "secure-specialist")
    
    if success:
        print(f"✅ PASSED: Extracted first marker: {actual}")
        return True
    else:
        print(f"❌ FAILED: Expected 'secure-specialist' (first marker), got '{actual}'")
        return False

def test_agent_file_exists():
    """Test that meta-coordinator-system agent file exists."""
    print("\n🧪 Test 6: Agent definition file exists")
    print("-" * 60)
    
    agent_file = Path("/home/runner/work/Chained/Chained/.github/agents/meta-coordinator-system.md")
    
    if agent_file.exists():
        print(f"✅ PASSED: Agent file exists: {agent_file}")
        
        # Also test extracting description
        result = subprocess.run(
            ['bash', '-c', 'grep \'^description:\' "$1" | sed \'s/^description: "//\' | sed \'s/"$//\'',
             'bash', str(agent_file)],
            capture_output=True,
            text=True
        )
        
        description = result.stdout.strip()
        if description:
            print(f"   Description: {description}")
        
        # Test extracting emoji
        result = subprocess.run(
            ['bash', '-c', 'grep -oP \'^#\\s*\\K\\S+\' "$1" | head -1',
             'bash', str(agent_file)],
            capture_output=True,
            text=True
        )
        
        emoji = result.stdout.strip()
        if emoji:
            print(f"   Emoji: {emoji}")
        
        return True
    else:
        print(f"❌ FAILED: Agent file not found: {agent_file}")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 Explicit Agent Marker Detection Tests")
    print("=" * 60)
    
    tests = [
        test_meta_coordinator_marker,
        test_no_marker,
        test_different_agent_marker,
        test_marker_with_dashes,
        test_marker_in_middle,
        test_agent_file_exists,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
