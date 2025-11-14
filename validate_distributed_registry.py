#!/usr/bin/env python3
"""
Validation Test for Distributed Registry System

This script validates that the distributed registry system is working correctly
by testing all major operations.
"""

import sys
import json
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

from registry_manager import RegistryManager


def test_registry_structure():
    """Verify the directory structure exists"""
    print("\n🔍 Testing Registry Structure...")
    
    base_path = Path('.github/agent-system')
    agents_path = base_path / 'agents'
    metadata_path = base_path / 'metadata'
    
    checks = [
        (agents_path.exists(), f"Agents directory exists: {agents_path}"),
        ((base_path / 'config.json').exists(), "Config file exists"),
        ((base_path / 'hall_of_fame.json').exists(), "Hall of fame file exists"),
    ]
    
    # Check for metadata - either single file or distributed
    has_metadata_file = (base_path / 'metadata.json').exists()
    has_metadata_dir = metadata_path.exists() and len(list(metadata_path.glob('*.txt'))) > 0
    
    if has_metadata_dir:
        checks.append((True, f"Distributed metadata directory exists: {metadata_path}"))
        metadata_files = list(metadata_path.glob('*.txt'))
        print(f"   ✅ Distributed metadata directory exists with {len(metadata_files)} field files")
    elif has_metadata_file:
        checks.append((True, "Metadata file exists (single file mode)"))
        print(f"   ⚠️  Using single metadata.json file (consider migrating to distributed)")
    else:
        checks.append((False, "No metadata found"))
    
    for check, msg in checks:
        if check:
            print(f"   ✅ {msg}")
        else:
            print(f"   ❌ {msg}")
            return False
    
    # Count agent files
    agent_files = list(agents_path.glob('agent-*.json'))
    print(f"   ✅ Found {len(agent_files)} agent files")
    
    return True


def test_registry_manager():
    """Test registry manager operations"""
    print("\n🔍 Testing Registry Manager...")
    
    registry = RegistryManager()
    
    # Test list agents
    agents = registry.list_agents()
    print(f"   ✅ Listed {len(agents)} total agents")
    
    active_agents = registry.list_agents(status='active')
    print(f"   ✅ Listed {len(active_agents)} active agents")
    
    # Test get agent
    if active_agents:
        agent_id = active_agents[0]['id']
        agent = registry.get_agent(agent_id)
        if agent:
            print(f"   ✅ Retrieved agent: {agent['name']}")
        else:
            print(f"   ❌ Failed to retrieve agent {agent_id}")
            return False
    
    # Test config
    config = registry.get_config()
    if 'max_active_agents' in config:
        print(f"   ✅ Config loaded: max_agents={config['max_active_agents']}")
    else:
        print("   ❌ Config missing required fields")
        return False
    
    # Test metadata
    metadata = registry.get_metadata()
    if 'version' in metadata:
        print(f"   ✅ Metadata loaded: version={metadata['version']}")
    else:
        print("   ❌ Metadata missing version")
        return False
    
    # Test hall of fame
    hof = registry.get_hall_of_fame()
    print(f"   ✅ Hall of fame loaded: {len(hof)} members")
    
    return True


def test_helper_scripts():
    """Test helper scripts"""
    print("\n🔍 Testing Helper Scripts...")
    
    import subprocess
    
    # Test list agents
    result = subprocess.run(
        ['python3', 'tools/list_agents_from_registry.py', '--status', 'active', '--format', 'count'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        count = int(result.stdout.strip())
        print(f"   ✅ list_agents_from_registry.py: {count} active agents")
    else:
        print(f"   ❌ list_agents_from_registry.py failed")
        return False
    
    return True


def test_no_merge_conflicts():
    """Verify that concurrency controls were removed"""
    print("\n🔍 Testing Concurrency Controls Removed...")
    
    workflows = [
        '.github/workflows/agent-spawner.yml',
        '.github/workflows/learning-based-agent-spawner.yml',
        '.github/workflows/agent-evaluator.yml',
    ]
    
    for workflow in workflows:
        with open(workflow, 'r') as f:
            content = f.read()
            
        if 'concurrency:' in content and 'agent-registry-updates' in content:
            print(f"   ❌ {workflow} still has concurrency control!")
            return False
        else:
            print(f"   ✅ {workflow} - concurrency control removed")
    
    return True


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("🧪 DISTRIBUTED REGISTRY SYSTEM VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Registry Structure", test_registry_structure),
        ("Registry Manager", test_registry_manager),
        ("Helper Scripts", test_helper_scripts),
        ("No Merge Conflicts", test_no_merge_conflicts),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n   ❌ {name} failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("\nThe distributed registry system is working correctly and")
        print("merge conflicts have been eliminated!")
        return 0
    else:
        print("⚠️  SOME VALIDATIONS FAILED")
        print("\nPlease review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
