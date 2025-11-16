#!/usr/bin/env python3
"""
Test script to verify cloud-architect agent matching works correctly
"""

import json
import sys

def test_cloud_architect_in_registry():
    """Test that cloud-architect exists in the registry"""
    print("Testing cloud-architect in registry...")
    
    with open('.github/agent-system/registry.json', 'r') as f:
        registry = json.load(f)
    
    cloud_agents = [
        agent for agent in registry['agents']
        if agent['specialization'] == 'cloud-architect'
    ]
    
    if not cloud_agents:
        print("❌ FAIL: cloud-architect not found in registry")
        return False
    
    agent = cloud_agents[0]
    print(f"✅ PASS: Found cloud-architect in registry")
    print(f"   Name: {agent['name']}")
    print(f"   ID: {agent['id']}")
    print(f"   Status: {agent['status']}")
    
    if agent['status'] != 'active':
        print("❌ FAIL: Agent is not active")
        return False
    
    print("✅ PASS: Agent is active")
    return True

def test_cloud_architect_in_world_state():
    """Test that cloud-architect exists in world state"""
    print("\nTesting cloud-architect in world state...")
    
    with open('world/world_state.json', 'r') as f:
        world_state = json.load(f)
    
    cloud_agents = [
        agent for agent in world_state['agents']
        if agent['specialization'] == 'cloud-architect'
    ]
    
    if not cloud_agents:
        print("❌ FAIL: cloud-architect not found in world state")
        return False
    
    agent = cloud_agents[0]
    print(f"✅ PASS: Found cloud-architect in world state")
    print(f"   Label: {agent['label']}")
    print(f"   Location: {agent['location_region_id']}")
    print(f"   Mission: {agent.get('current_idea_id', 'None')}")
    print(f"   Status: {agent['status']}")
    
    return True

def test_pattern_matching():
    """Test that cloud patterns map to cloud-architect"""
    print("\nTesting pattern matching...")
    
    with open('.github/workflows/agent-missions.yml', 'r') as f:
        workflow_content = f.read()
    
    # Check if cloud-architect is first in cloud pattern
    test_patterns = [
        ("'cloud':", "cloud-architect"),
        ("'aws':", "cloud-architect"),
        ("'devops':", "cloud-architect"),
    ]
    
    all_passed = True
    for pattern, expected_agent in test_patterns:
        if pattern in workflow_content:
            # Find the line with the pattern
            for line in workflow_content.split('\n'):
                if pattern in line:
                    if expected_agent in line:
                        # Check if it's first
                        start = line.find('[')
                        end = line.find(']')
                        if start > 0 and end > start:
                            agents_list = line[start+1:end]
                            first_agent = agents_list.split(',')[0].strip().strip("'\"")
                            if first_agent == expected_agent:
                                print(f"✅ PASS: Pattern {pattern} prioritizes {expected_agent}")
                            else:
                                print(f"❌ FAIL: Pattern {pattern} does not prioritize {expected_agent}")
                                print(f"   First agent: {first_agent}")
                                all_passed = False
                    else:
                        print(f"❌ FAIL: Pattern {pattern} does not include {expected_agent}")
                        all_passed = False
                    break
        else:
            print(f"❌ FAIL: Pattern {pattern} not found in workflow")
            all_passed = False
    
    return all_passed

def test_agent_definition_exists():
    """Test that cloud-architect.md exists"""
    print("\nTesting agent definition file...")
    
    import os
    agent_file = '.github/agents/cloud-architect.md'
    
    if not os.path.exists(agent_file):
        print(f"❌ FAIL: Agent definition file not found: {agent_file}")
        return False
    
    print(f"✅ PASS: Agent definition file exists: {agent_file}")
    
    # Read and verify it has correct name
    with open(agent_file, 'r') as f:
        content = f.read()
        if 'cloud-architect' in content.lower():
            print("✅ PASS: File contains cloud-architect reference")
            return True
        else:
            print("❌ FAIL: File does not contain cloud-architect reference")
            return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Cloud Architect Agent Integration Tests")
    print("=" * 60)
    
    tests = [
        test_agent_definition_exists,
        test_cloud_architect_in_registry,
        test_cloud_architect_in_world_state,
        test_pattern_matching,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ EXCEPTION in {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
