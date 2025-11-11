#!/usr/bin/env python3
"""
Test script to validate agent deletion and discussion features.
"""

import json
import sys
from pathlib import Path


def test_agent_human_names():
    """Test that all agents have human_name field."""
    registry_path = Path('.github/agent-system/registry.json')
    
    if not registry_path.exists():
        print("❌ .github/agent-system/registry.json not found")
        return False
    
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    agents = registry.get('agents', [])
    if not agents:
        print("⚠️ No agents in registry to test")
        return True
    
    missing_human_name = []
    for agent in agents:
        if 'human_name' not in agent or not agent.get('human_name'):
            missing_human_name.append(agent.get('id', 'unknown'))
    
    if missing_human_name:
        print(f"❌ Agents missing human_name field: {', '.join(missing_human_name)}")
        return False
    
    print(f"✅ All {len(agents)} agents have human_name field")
    return True


def test_agent_personality_fields():
    """Test that all agents have personality and communication_style fields."""
    registry_path = Path('.github/agent-system/registry.json')
    
    if not registry_path.exists():
        print("❌ .github/agent-system/registry.json not found")
        return False
    
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    agents = registry.get('agents', [])
    if not agents:
        print("⚠️ No agents in registry to test")
        return True
    
    missing_fields = []
    for agent in agents:
        agent_id = agent.get('id', 'unknown')
        if 'personality' not in agent:
            missing_fields.append(f"{agent_id}:personality")
        if 'communication_style' not in agent:
            missing_fields.append(f"{agent_id}:communication_style")
    
    if missing_fields:
        print(f"❌ Agents missing fields: {', '.join(missing_fields)}")
        return False
    
    print(f"✅ All {len(agents)} agents have personality and communication_style fields")
    return True


def test_deletion_workflow_inputs():
    """Test that agent-spawner.yml has deletion inputs."""
    workflow_path = Path('.github/workflows/agent-spawner.yml')
    
    if not workflow_path.exists():
        print("❌ agent-spawner.yml not found")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    required_inputs = [
        'delete_mode',
        'delete_agent_ids',
        'respawn_count'
    ]
    
    missing_inputs = []
    for input_name in required_inputs:
        if input_name not in content:
            missing_inputs.append(input_name)
    
    if missing_inputs:
        print(f"❌ Missing workflow inputs: {', '.join(missing_inputs)}")
        return False
    
    # Check for deletion step
    if 'Delete agents if requested' not in content:
        print("❌ Missing deletion step in workflow")
        return False
    
    print("✅ Agent spawner workflow has deletion and respawn inputs")
    return True


def test_discussion_workflow():
    """Test that agent-issue-discussion.yml exists and has correct structure."""
    workflow_path = Path('.github/workflows/agent-issue-discussion.yml')
    
    if not workflow_path.exists():
        print("❌ agent-issue-discussion.yml not found")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    required_elements = [
        'Agent Issue Discussion',
        'workflow_dispatch',
        'issue_number',
        'discussion_rounds',
        'Load active agents',
        'Generate agent discussion',
        'Post assignment decision'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing workflow elements: {', '.join(missing_elements)}")
        return False
    
    # Check for personality-based discussion
    if 'personality' not in content.lower() or 'specialization' not in content.lower():
        print("❌ Discussion workflow missing personality or specialization logic")
        return False
    
    print("✅ Agent discussion workflow exists with correct structure")
    return True


def test_discussion_workflow_label_trigger():
    """Test that discussion workflow can be triggered by label."""
    workflow_path = Path('.github/workflows/agent-issue-discussion.yml')
    
    if not workflow_path.exists():
        print("❌ agent-issue-discussion.yml not found")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # Check for issues trigger with labeled type
    if 'issues:' not in content or 'types: [labeled]' not in content:
        print("❌ Discussion workflow missing issues:labeled trigger")
        return False
    
    # Check for label condition
    if 'agent-discussion' not in content:
        print("❌ Discussion workflow missing agent-discussion label check")
        return False
    
    print("✅ Discussion workflow can be triggered by agent-discussion label")
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("🧪 Testing Agent Deletion and Discussion Features\n")
    
    tests = [
        ("Agent Human Names", test_agent_human_names),
        ("Agent Personality Fields", test_agent_personality_fields),
        ("Deletion Workflow Inputs", test_deletion_workflow_inputs),
        ("Discussion Workflow", test_discussion_workflow),
        ("Discussion Label Trigger", test_discussion_workflow_label_trigger),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"📋 Testing: {test_name}")
        print("-" * 50)
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
