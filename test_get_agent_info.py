#!/usr/bin/env python3
"""
Comprehensive test suite for get-agent-info.py tool.
Tests command-line interface, error handling, and edge cases.
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Test data
KNOWN_AGENTS = [
    'bug-hunter',
    'code-poet', 
    'coordinate-wizard',
    'doc-master',
    'feature-architect',
    'integration-specialist',
    'performance-optimizer',
    'refactor-wizard',
    'security-guardian',
    'teach-wizard',
    'test-champion',
    'ux-enhancer',
    'validate-pro',
    'validate-wizard'
]

def run_command(args):
    """Run get-agent-info.py command and return result."""
    try:
        result = subprocess.run(
            ['python3', 'tools/get-agent-info.py'] + args,
            capture_output=True,
            text=True,
            cwd='.',
            timeout=5
        )
        return {
            'returncode': result.returncode,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip()
        }
    except subprocess.TimeoutExpired:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': 'Command timed out'
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }

def test_list_command():
    """Test the list command."""
    print("\n🧪 Testing list command")
    print("-" * 60)
    
    result = run_command(['list'])
    
    if result['returncode'] != 0:
        print(f"❌ FAILED: list command returned non-zero exit code: {result['returncode']}")
        print(f"   stderr: {result['stderr']}")
        return False
    
    agents = result['stdout'].split()
    
    # Verify we got agents
    if len(agents) == 0:
        print("❌ FAILED: No agents returned")
        return False
    
    # Verify known agents are present
    missing = [agent for agent in KNOWN_AGENTS if agent not in agents]
    if missing:
        print(f"❌ FAILED: Missing expected agents: {missing}")
        return False
    
    print(f"✅ PASSED: Found {len(agents)} agents")
    print(f"   Agents: {', '.join(agents[:5])}...")
    return True

def test_info_command():
    """Test the info command."""
    print("\n🧪 Testing info command")
    print("-" * 60)
    
    passed = 0
    failed = 0
    
    # Test a known agent
    result = run_command(['info', 'test-champion'])
    
    if result['returncode'] != 0:
        print(f"❌ FAILED: info command returned non-zero exit code")
        print(f"   stderr: {result['stderr']}")
        failed += 1
    else:
        try:
            data = json.loads(result['stdout'])
            required_keys = ['name', 'description', 'tools', 'emoji', 'mission', 'body']
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                print(f"❌ FAILED: Missing keys in JSON response: {missing_keys}")
                failed += 1
            else:
                print(f"✅ PASSED: info command returns valid JSON with all required keys")
                passed += 1
        except json.JSONDecodeError as e:
            print(f"❌ FAILED: info command did not return valid JSON")
            print(f"   Error: {e}")
            failed += 1
    
    # Test unknown agent
    result = run_command(['info', 'nonexistent-agent'])
    
    if result['returncode'] == 0:
        print(f"❌ FAILED: info command should fail for nonexistent agent")
        failed += 1
    else:
        print(f"✅ PASSED: info command correctly fails for nonexistent agent")
        passed += 1
    
    return failed == 0

def test_emoji_command():
    """Test the emoji command."""
    print("\n🧪 Testing emoji command")
    print("-" * 60)
    
    # Test a known agent
    result = run_command(['emoji', 'test-champion'])
    
    if result['returncode'] != 0:
        print(f"❌ FAILED: emoji command returned non-zero exit code")
        return False
    
    if not result['stdout']:
        print(f"❌ FAILED: emoji command returned empty output")
        return False
    
    print(f"✅ PASSED: emoji command returns emoji: {result['stdout']}")
    return True

def test_mission_command():
    """Test the mission command."""
    print("\n🧪 Testing mission command")
    print("-" * 60)
    
    # Test a known agent
    result = run_command(['mission', 'test-champion'])
    
    if result['returncode'] != 0:
        print(f"❌ FAILED: mission command returned non-zero exit code")
        return False
    
    if not result['stdout']:
        print(f"❌ FAILED: mission command returned empty output")
        return False
    
    print(f"✅ PASSED: mission command returns mission")
    print(f"   Mission: {result['stdout'][:80]}...")
    return True

def test_description_command():
    """Test the description command."""
    print("\n🧪 Testing description command")
    print("-" * 60)
    
    # Test a known agent
    result = run_command(['description', 'test-champion'])
    
    if result['returncode'] != 0:
        print(f"❌ FAILED: description command returned non-zero exit code")
        return False
    
    if not result['stdout']:
        print(f"❌ FAILED: description command returned empty output")
        return False
    
    print(f"✅ PASSED: description command returns description")
    print(f"   Description: {result['stdout'][:80]}...")
    return True

def test_no_arguments():
    """Test running without arguments."""
    print("\n🧪 Testing no arguments")
    print("-" * 60)
    
    result = run_command([])
    
    if result['returncode'] == 0:
        print(f"❌ FAILED: Command should fail without arguments")
        return False
    
    if 'Usage:' not in result['stderr']:
        print(f"❌ FAILED: Should show usage information")
        return False
    
    print(f"✅ PASSED: Correctly shows usage when no arguments provided")
    return True

def test_invalid_command():
    """Test invalid command."""
    print("\n🧪 Testing invalid command")
    print("-" * 60)
    
    result = run_command(['invalid-command'])
    
    if result['returncode'] == 0:
        print(f"❌ FAILED: Command should fail with invalid command")
        return False
    
    if 'Unknown command' not in result['stderr']:
        print(f"❌ FAILED: Should show 'Unknown command' error")
        return False
    
    print(f"✅ PASSED: Correctly rejects invalid command")
    return True

def test_multiple_agents():
    """Test info command for multiple agents."""
    print("\n🧪 Testing multiple agents")
    print("-" * 60)
    
    test_agents = ['bug-hunter', 'doc-master', 'security-guardian']
    passed = 0
    failed = 0
    
    for agent in test_agents:
        result = run_command(['info', agent])
        
        if result['returncode'] != 0:
            print(f"❌ FAILED: Could not get info for {agent}")
            failed += 1
        else:
            try:
                data = json.loads(result['stdout'])
                if data.get('name') == agent:
                    print(f"✅ PASSED: Successfully retrieved info for {agent}")
                    passed += 1
                else:
                    print(f"❌ FAILED: Name mismatch for {agent}")
                    failed += 1
            except json.JSONDecodeError:
                print(f"❌ FAILED: Invalid JSON for {agent}")
                failed += 1
    
    return failed == 0

def test_edge_cases():
    """Test edge cases."""
    print("\n🧪 Testing edge cases")
    print("-" * 60)
    
    test_cases = [
        (['info'], 'Missing agent name for info command'),
        (['emoji'], 'Missing agent name for emoji command'),
        (['mission'], 'Missing agent name for mission command'),
        (['description'], 'Missing agent name for description command'),
    ]
    
    passed = 0
    failed = 0
    
    for args, description in test_cases:
        result = run_command(args)
        
        if result['returncode'] != 0:
            print(f"✅ PASSED: {description} - correctly failed")
            passed += 1
        else:
            print(f"❌ FAILED: {description} - should have failed")
            failed += 1
    
    return failed == 0

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Testing get-agent-info.py Tool")
    print("=" * 60)
    
    # Change to repo root
    repo_root = Path(__file__).parent
    os.chdir(repo_root)
    print(f"Working directory: {os.getcwd()}")
    
    tests = [
        ("List Command", test_list_command),
        ("Info Command", test_info_command),
        ("Emoji Command", test_emoji_command),
        ("Mission Command", test_mission_command),
        ("Description Command", test_description_command),
        ("No Arguments", test_no_arguments),
        ("Invalid Command", test_invalid_command),
        ("Multiple Agents", test_multiple_agents),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
