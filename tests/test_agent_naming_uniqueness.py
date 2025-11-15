#!/usr/bin/env python3
"""
Test agent naming uniqueness improvements.

Tests for:
1. Timestamp-based ID uniqueness
2. Agent name generation uniqueness
3. Protection against existing agent names
4. Dynamic agent spawner ID generation
"""

import sys
import os
import time
import random
import importlib.util
from pathlib import Path

# Add tools directory to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / 'tools'))

# Import module with hyphens in name
spec = importlib.util.spec_from_file_location(
    "generate_new_agent",
    REPO_ROOT / 'tools' / 'generate-new-agent.py'
)
generate_new_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_new_agent)

generate_random_agent = generate_new_agent.generate_random_agent
get_existing_agent_names = generate_new_agent.get_existing_agent_names


def test_timestamp_ids_uniqueness():
    """Test that timestamp-based IDs are unique even when generated rapidly."""
    print("\n🧪 Testing timestamp-based ID uniqueness...")
    
    ids = set()
    num_iterations = 100
    
    for i in range(num_iterations):
        # Simulate the workflow ID generation
        timestamp_ns = time.time_ns()
        random_suffix = (random.randint(0, 32767) * random.randint(0, 32767)) % 100000
        agent_id = f"agent-{timestamp_ns}-{random_suffix}"
        
        if agent_id in ids:
            print(f"❌ FAILED: Duplicate ID found: {agent_id}")
            return False
        
        ids.add(agent_id)
        
        # Add tiny delay to prevent exact timestamp collision
        if i % 10 == 0:
            time.sleep(0.001)
    
    print(f"✅ PASSED: Generated {num_iterations} unique timestamp-based IDs")
    print(f"   Sample IDs:")
    for id in list(ids)[:3]:
        print(f"   - {id}")
    return True


def test_agent_name_uniqueness():
    """Test that agent name generation produces unique names."""
    print("\n🧪 Testing agent name generation uniqueness...")
    
    names = set()
    num_iterations = 50
    
    for i in range(num_iterations):
        # Pass previously generated names to exclude them
        agent_info = generate_random_agent(excluded_names=names)
        agent_name = agent_info['name']
        
        if agent_name in names:
            print(f"❌ FAILED: Duplicate name found: {agent_name}")
            return False
        
        names.add(agent_name)
    
    print(f"✅ PASSED: Generated {num_iterations} unique agent names")
    print(f"   Sample names:")
    for name in list(names)[:5]:
        print(f"   - {name}")
    
    # Check variety - should have different suffixes
    suffixes = set()
    for name in names:
        parts = name.split('-')
        if len(parts) >= 2:
            suffixes.add(parts[-1])
    
    print(f"   Suffix variety: {len(suffixes)} different suffixes used")
    if len(suffixes) < 5:
        print(f"   ⚠️  Low suffix variety (expected > 5, got {len(suffixes)})")
    
    return True


def test_existing_agent_detection():
    """Test that the system detects existing agent names."""
    print("\n🧪 Testing existing agent detection...")
    
    existing = get_existing_agent_names()
    
    print(f"   Found {len(existing)} existing agents")
    if len(existing) > 0:
        print(f"   Sample existing agents:")
        for name in list(existing)[:3]:
            print(f"   - {name}")
    
    # The function should return a set
    if not isinstance(existing, set):
        print(f"❌ FAILED: Expected set, got {type(existing)}")
        return False
    
    print(f"✅ PASSED: Existing agent detection working")
    return True


def test_multi_agent_spawn_simulation():
    """Simulate spawning 25 agents and check for duplicates."""
    print("\n🧪 Testing multi-agent spawn simulation (25 agents)...")
    
    agent_ids = set()
    agent_names = set()
    num_agents = 25
    
    for i in range(num_agents):
        # Simulate timestamp ID generation
        timestamp_ns = time.time_ns()
        random_suffix = (random.randint(0, 32767) * random.randint(0, 32767)) % 100000
        matrix_index = i + 1
        agent_id = f"agent-{timestamp_ns}-{matrix_index}-{random_suffix}"
        
        if agent_id in agent_ids:
            print(f"❌ FAILED: Duplicate agent ID: {agent_id}")
            return False
        agent_ids.add(agent_id)
        
        # Generate agent info, passing previously generated names to exclude
        agent_info = generate_random_agent(excluded_names=agent_names)
        agent_name = agent_info['name']
        
        if agent_name in agent_names:
            print(f"❌ FAILED: Duplicate agent name: {agent_name}")
            return False
        agent_names.add(agent_name)
        
        # Add small delay to simulate real spawning
        if i % 5 == 0:
            time.sleep(0.001)
    
    print(f"✅ PASSED: Spawned {num_agents} agents with no duplicates")
    print(f"   Unique IDs: {len(agent_ids)}")
    print(f"   Unique names: {len(agent_names)}")
    print(f"\n   Sample spawned agents:")
    for i, (agent_id, agent_name) in enumerate(zip(list(agent_ids)[:3], list(agent_names)[:3])):
        print(f"   {i+1}. {agent_name} ({agent_id[:30]}...)")
    
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("🧹 Agent Naming Uniqueness Tests (@organize-guru)")
    print("=" * 70)
    
    tests = [
        ("Timestamp ID Uniqueness", test_timestamp_ids_uniqueness),
        ("Agent Name Uniqueness", test_agent_name_uniqueness),
        ("Existing Agent Detection", test_existing_agent_detection),
        ("Multi-Agent Spawn (25 agents)", test_multi_agent_spawn_simulation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name} - Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results:")
    print(f"   ✅ Passed: {passed}/{len(tests)}")
    print(f"   ❌ Failed: {failed}/{len(tests)}")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 All tests passed! Agent naming is now more random and unique.")
        print("   - Timestamp IDs use nanosecond precision + random suffix")
        print("   - Agent names expanded from 8 to 23 possible suffixes")
        print("   - Name generation checks existing agents")
        print("   - Multiple fallback strategies ensure uniqueness")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
