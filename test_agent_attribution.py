#!/usr/bin/env python3
"""
Test Agent Attribution System

Tests that agents can be properly attributed work through COPILOT_AGENT comments.
"""

import json
import re
import sys
from pathlib import Path

def test_copilot_agent_comment_parsing():
    """Test that COPILOT_AGENT comments can be parsed correctly"""
    
    test_cases = [
        {
            'body': '<!-- COPILOT_AGENT:bug-hunter -->\nFix the bug',
            'specialization': 'bug-hunter',
            'should_match': True
        },
        {
            'body': '<!--COPILOT_AGENT:feature-architect-->\nAdd feature',
            'specialization': 'feature-architect',
            'should_match': True
        },
        {
            'body': '<!-- COPILOT_AGENT: doc-master -->\nUpdate docs',
            'specialization': 'doc-master',
            'should_match': True
        },
        {
            'body': 'Just a regular issue without agent assignment',
            'specialization': 'bug-hunter',
            'should_match': False
        },
        {
            'body': '<!-- COPILOT_AGENT:bug-hunter -->\nFix the bug',
            'specialization': 'doc-master',
            'should_match': False
        },
    ]
    
    print("🧪 Testing COPILOT_AGENT comment parsing")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        body = test['body']
        specialization = test['specialization']
        should_match = test['should_match']
        
        # Use the same pattern as in agent-metrics-collector.py
        pattern = rf'<!--\s*COPILOT_AGENT:\s*{re.escape(specialization)}\s*-->'
        matches = re.search(pattern, body, re.IGNORECASE) is not None
        
        if matches == should_match:
            print(f"✅ Test {i}: PASSED")
            passed += 1
        else:
            print(f"❌ Test {i}: FAILED")
            print(f"   Body: {body[:50]}...")
            print(f"   Specialization: {specialization}")
            print(f"   Expected match: {should_match}, Got: {matches}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


def test_agent_specialization_in_registry():
    """Test that agents in registry have specializations"""
    
    print("\n🧪 Testing Agent Registry Specializations")
    print("=" * 60)
    
    registry_path = Path(".github/agent-system/registry.json")
    
    if not registry_path.exists():
        print("⚠️  Registry file not found, skipping test")
        return True
    
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    agents = registry.get('agents', [])
    hall_of_fame = registry.get('hall_of_fame', [])
    
    all_agents = agents + hall_of_fame
    
    if not all_agents:
        print("⚠️  No agents in registry, skipping test")
        return True
    
    passed = 0
    failed = 0
    
    for agent in all_agents:
        agent_id = agent.get('id', 'unknown')
        specialization = agent.get('specialization')
        
        if specialization:
            print(f"✅ Agent {agent_id}: specialization = {specialization}")
            passed += 1
        else:
            print(f"❌ Agent {agent_id}: missing specialization")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} agents with specialization, {failed} without")
    
    return failed == 0


def test_metrics_collector_import():
    """Test that the metrics collector can be imported"""
    
    print("\n🧪 Testing Metrics Collector Import")
    print("=" * 60)
    
    try:
        sys.path.insert(0, 'tools')
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "agent_metrics_collector",
            "tools/agent-metrics-collector.py"
        )
        metrics_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(metrics_module)
        
        # Check that required methods exist
        MetricsCollector = metrics_module.MetricsCollector
        collector = MetricsCollector()
        
        required_methods = [
            '_get_agent_specialization',
            '_find_issues_assigned_to_agent',
            'collect_agent_activity'
        ]
        
        for method in required_methods:
            if hasattr(collector, method):
                print(f"✅ Method exists: {method}")
            else:
                print(f"❌ Method missing: {method}")
                return False
        
        print("=" * 60)
        print("✅ All required methods exist")
        return True
        
    except Exception as e:
        print(f"❌ Failed to import metrics collector: {e}")
        print("=" * 60)
        return False


def main():
    """Run all tests"""
    
    print("=" * 60)
    print("Agent Attribution System Tests")
    print("=" * 60)
    
    tests = [
        ("COPILOT_AGENT Comment Parsing", test_copilot_agent_comment_parsing),
        ("Agent Registry Specializations", test_agent_specialization_in_registry),
        ("Metrics Collector Import", test_metrics_collector_import),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("=" * 60)
    print(f"Overall: {passed} passed, {failed} failed")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
