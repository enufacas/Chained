#!/usr/bin/env python3
"""
Test script to validate the agent registry schema and workflows.
"""

import json
import sys
from pathlib import Path

def test_agent_registry():
    """Test that agent registry has correct schema."""
    registry_path = Path('.github/agent-system/registry.json')
    
    if not registry_path.exists():
        print("❌ .github/agent-system/registry.json not found")
        return False
    
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    # Check required top-level keys (v2.0.0+ uses specializations_note instead of specializations array)
    required_keys = ['version', 'agents', 'hall_of_fame', 'system_lead', 'config']
    for key in required_keys:
        if key not in registry:
            print(f"❌ Missing required key: {key}")
            return False
    
    # Check that either specializations or specializations_note exists
    if 'specializations' not in registry and 'specializations_note' not in registry:
        print("❌ Missing specializations info (need either 'specializations' array or 'specializations_note')")
        return False
    
    # Check config structure (v2.0.0+ includes spawn_mode and new_agent_probability)
    config = registry['config']
    required_config_keys = ['spawn_interval_hours', 'max_active_agents', 'elimination_threshold', 
                   'promotion_threshold', 'metrics_weight']
    for key in required_config_keys:
        if key not in config:
            print(f"❌ Missing config key: {key}")
            return False
    
    # Check metrics weights
    weights = config['metrics_weight']
    expected_weights = ['code_quality', 'issue_resolution', 'pr_success', 'peer_review']
    for weight in expected_weights:
        if weight not in weights:
            print(f"❌ Missing metrics weight: {weight}")
            return False
    
    # Verify weights sum to 1.0
    total_weight = sum(weights.values())
    if abs(total_weight - 1.0) > 0.01:
        print(f"❌ Metrics weights don't sum to 1.0 (got {total_weight})")
        return False
    
    # Check specializations (v2.0+ uses dynamic loading from .github/agents/)
    if 'specializations' in registry:
        if not isinstance(registry['specializations'], list):
            print("❌ specializations must be a list")
            return False
        
        if len(registry['specializations']) == 0:
            print("❌ No specializations defined")
            return False
    
    version = registry.get('version', '1.0.0')
    print(f"✅ Agent registry schema is valid (version {version})")
    return True

def test_workflow_files():
    """Test that required workflow files exist."""
    workflow_dir = Path('.github/workflows')
    
    required_workflows = [
        'agent-spawner.yml',
        'agent-evaluator.yml',
        'agent-data-sync.yml'
    ]
    
    for workflow in required_workflows:
        workflow_path = workflow_dir / workflow
        if not workflow_path.exists():
            print(f"❌ Missing workflow: {workflow}")
            return False
    
    print("✅ All required workflow files exist")
    return True

def test_documentation():
    """Test that documentation files exist."""
    docs = [
        '.github/agent-system/README.md',
        'AGENT_BRAINSTORMING.md',
        'docs/agents.html'
    ]
    
    for doc in docs:
        doc_path = Path(doc)
        if not doc_path.exists():
            print(f"❌ Missing documentation: {doc}")
            return False
    
    print("✅ All required documentation exists")
    return True

def test_directory_structure():
    """Test that required directories exist."""
    dirs = [
        '.github/agent-system',
        '.github/agent-system/templates',
        '.github/agent-system/metrics',
        '.github/agent-system/archive'
    ]
    
    for dir_path in dirs:
        if not Path(dir_path).exists():
            print(f"❌ Missing directory: {dir_path}")
            return False
    
    print("✅ Directory structure is correct")
    return True

def main():
    """Run all tests."""
    print("🧪 Testing Agent System Implementation\n")
    
    tests = [
        ("Agent Registry Schema", test_agent_registry),
        ("Workflow Files", test_workflow_files),
        ("Documentation", test_documentation),
        ("Directory Structure", test_directory_structure)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 Testing: {name}")
        print("-" * 50)
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
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
