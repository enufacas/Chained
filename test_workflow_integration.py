#!/usr/bin/env python3
"""
Integration tests for Chained workflow components.
Tests how different parts of the system work together.
"""

import sys
import os
import json
import subprocess
from pathlib import Path

def run_command(cmd, **kwargs):
    """Run a command and return result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            **kwargs
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

def test_agent_matching_to_info_pipeline():
    """Test that matched agents can be queried for info."""
    print("\n🧪 Testing agent matching → info pipeline")
    print("-" * 60)
    
    # Step 1: Match an issue to an agent
    match_result = run_command([
        'python3', 'tools/match-issue-to-agent.py',
        'Fix security vulnerability in authentication',
        'We need to patch the XSS vulnerability in the login form'
    ], cwd='.')
    
    if match_result['returncode'] != 0:
        print(f"❌ FAILED: Agent matching failed")
        print(f"   stderr: {match_result['stderr']}")
        return False
    
    try:
        match_data = json.loads(match_result['stdout'])
        agent_name = match_data.get('agent')
        
        if not agent_name:
            print(f"❌ FAILED: No agent returned from matching")
            return False
        
        print(f"   Matched agent: {agent_name}")
        
        # Step 2: Get info about the matched agent
        info_result = run_command([
            'python3', 'tools/get-agent-info.py',
            'info', agent_name
        ], cwd='.')
        
        if info_result['returncode'] != 0:
            print(f"❌ FAILED: Could not get info for matched agent {agent_name}")
            print(f"   stderr: {info_result['stderr']}")
            return False
        
        info_data = json.loads(info_result['stdout'])
        
        if info_data.get('name') != agent_name:
            print(f"❌ FAILED: Agent name mismatch")
            return False
        
        print(f"✅ PASSED: Successfully matched and retrieved agent info")
        print(f"   Agent: {agent_name}")
        print(f"   Description: {info_data.get('description', '')[:60]}...")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: Invalid JSON response")
        print(f"   Error: {e}")
        return False

def test_all_agents_have_valid_definitions():
    """Test that all matched agents have valid definitions."""
    print("\n🧪 Testing all agents have valid definitions")
    print("-" * 60)
    
    # Get list of all agents
    list_result = run_command([
        'python3', 'tools/get-agent-info.py', 'list'
    ], cwd='.')
    
    if list_result['returncode'] != 0:
        print(f"❌ FAILED: Could not list agents")
        return False
    
    agents = list_result['stdout'].split()
    
    if len(agents) == 0:
        print(f"❌ FAILED: No agents found")
        return False
    
    print(f"   Testing {len(agents)} agents...")
    
    failed = []
    for agent in agents:
        info_result = run_command([
            'python3', 'tools/get-agent-info.py',
            'info', agent
        ], cwd='.')
        
        if info_result['returncode'] != 0:
            failed.append(agent)
            continue
        
        try:
            data = json.loads(info_result['stdout'])
            required = ['name', 'description', 'tools']
            missing = [k for k in required if not data.get(k)]
            if missing:
                failed.append(f"{agent} (missing: {missing})")
        except json.JSONDecodeError:
            failed.append(f"{agent} (invalid JSON)")
    
    if failed:
        print(f"❌ FAILED: {len(failed)} agents have issues:")
        for f in failed:
            print(f"   - {f}")
        return False
    
    print(f"✅ PASSED: All {len(agents)} agents have valid definitions")
    return True

def test_matching_consistency():
    """Test that matching is consistent for the same input."""
    print("\n🧪 Testing matching consistency")
    print("-" * 60)
    
    test_cases = [
        ("Fix bug in login", "Authentication is broken"),
        ("Add new feature", "We need user profiles"),
        ("Write documentation", "API docs are missing"),
    ]
    
    passed = 0
    failed = 0
    
    for title, body in test_cases:
        # Run matching twice
        result1 = run_command([
            'python3', 'tools/match-issue-to-agent.py',
            title, body
        ], cwd='.')
        
        result2 = run_command([
            'python3', 'tools/match-issue-to-agent.py',
            title, body
        ], cwd='.')
        
        if result1['returncode'] != 0 or result2['returncode'] != 0:
            print(f"❌ FAILED: Matching failed for '{title}'")
            failed += 1
            continue
        
        try:
            data1 = json.loads(result1['stdout'])
            data2 = json.loads(result2['stdout'])
            
            if data1.get('agent') != data2.get('agent'):
                print(f"❌ FAILED: Inconsistent matching for '{title}'")
                print(f"   First: {data1.get('agent')}, Second: {data2.get('agent')}")
                failed += 1
            else:
                print(f"✅ PASSED: Consistent matching for '{title}' → {data1.get('agent')}")
                passed += 1
        except json.JSONDecodeError:
            print(f"❌ FAILED: Invalid JSON for '{title}'")
            failed += 1
    
    return failed == 0

def test_agent_specialization_coverage():
    """Test that we have agents for common issue types."""
    print("\n🧪 Testing agent specialization coverage")
    print("-" * 60)
    
    required_specializations = [
        ('Bug fixing', ['bug-hunter']),
        ('Security issues', ['security-guardian']),
        ('Documentation', ['doc-master']),
        ('Testing', ['test-champion']),
        ('Performance', ['performance-optimizer']),
        ('Features', ['feature-architect']),
        ('Integration', ['integration-specialist']),
        ('UX/UI', ['ux-enhancer']),
    ]
    
    # Get all agents
    list_result = run_command([
        'python3', 'tools/get-agent-info.py', 'list'
    ], cwd='.')
    
    if list_result['returncode'] != 0:
        print(f"❌ FAILED: Could not list agents")
        return False
    
    agents = set(list_result['stdout'].split())
    
    passed = 0
    failed = 0
    
    for category, expected_agents in required_specializations:
        found = [agent for agent in expected_agents if agent in agents]
        
        if found:
            print(f"✅ PASSED: {category} covered by {', '.join(found)}")
            passed += 1
        else:
            print(f"❌ FAILED: {category} not covered (expected one of: {', '.join(expected_agents)})")
            failed += 1
    
    return failed == 0

def test_error_handling_robustness():
    """Test that tools handle errors gracefully."""
    print("\n🧪 Testing error handling robustness")
    print("-" * 60)
    
    test_cases = [
        {
            'name': 'Empty input to matcher',
            'cmd': ['python3', 'tools/match-issue-to-agent.py', '', ''],
            'should_succeed': True  # Should default to feature-architect
        },
        {
            'name': 'Nonexistent agent info',
            'cmd': ['python3', 'tools/get-agent-info.py', 'info', 'nonexistent-agent-xyz'],
            'should_succeed': False
        },
        {
            'name': 'Very long input to matcher',
            'cmd': ['python3', 'tools/match-issue-to-agent.py', 'A' * 10000, 'B' * 10000],
            'should_succeed': True
        },
        {
            'name': 'Special characters in input',
            'cmd': ['python3', 'tools/match-issue-to-agent.py', 'Fix <script>alert(1)</script>', 'Body'],
            'should_succeed': True
        },
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = run_command(test['cmd'], cwd='.')
        success = result['returncode'] == 0
        
        if success == test['should_succeed']:
            print(f"✅ PASSED: {test['name']}")
            passed += 1
        else:
            print(f"❌ FAILED: {test['name']}")
            print(f"   Expected {'success' if test['should_succeed'] else 'failure'}, got {'success' if success else 'failure'}")
            failed += 1
    
    return failed == 0

def test_json_output_format():
    """Test that tools output valid JSON."""
    print("\n🧪 Testing JSON output format")
    print("-" * 60)
    
    test_commands = [
        ['python3', 'tools/match-issue-to-agent.py', 'Test issue', 'Test body'],
        ['python3', 'tools/get-agent-info.py', 'info', 'test-champion'],
    ]
    
    passed = 0
    failed = 0
    
    for cmd in test_commands:
        result = run_command(cmd, cwd='.')
        
        if result['returncode'] != 0:
            print(f"❌ FAILED: Command failed: {' '.join(cmd[2:4])}")
            failed += 1
            continue
        
        try:
            data = json.loads(result['stdout'])
            if isinstance(data, dict):
                print(f"✅ PASSED: Valid JSON from {cmd[1].split('/')[-1]}")
                passed += 1
            else:
                print(f"❌ FAILED: JSON is not a dict from {cmd[1].split('/')[-1]}")
                failed += 1
        except json.JSONDecodeError as e:
            print(f"❌ FAILED: Invalid JSON from {cmd[1].split('/')[-1]}")
            failed += 1
    
    return failed == 0

def main():
    """Run all integration tests."""
    print("=" * 60)
    print("🧪 Chained Workflow Integration Tests")
    print("=" * 60)
    
    # Change to repo root
    repo_root = Path(__file__).parent
    os.chdir(repo_root)
    print(f"Working directory: {os.getcwd()}")
    
    tests = [
        ("Agent Matching → Info Pipeline", test_agent_matching_to_info_pipeline),
        ("All Agents Have Valid Definitions", test_all_agents_have_valid_definitions),
        ("Matching Consistency", test_matching_consistency),
        ("Agent Specialization Coverage", test_agent_specialization_coverage),
        ("Error Handling Robustness", test_error_handling_robustness),
        ("JSON Output Format", test_json_output_format),
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
    print("📊 Integration Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All integration tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
