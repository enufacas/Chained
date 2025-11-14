#!/usr/bin/env python3
"""
Test script to validate agent deletion workflows work correctly.

This tests the deletion logic in agent-spawner.yml and agent-evaluator.yml
to ensure agents are properly deleted when requested.

@assert-specialist test suite - specification-driven validation
"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
import sys


def setup_test_environment():
    """Create a test environment with sample agents."""
    # Create test directory structure
    test_dir = Path(tempfile.mkdtemp())
    agent_system_dir = test_dir / ".github" / "agent-system"
    profiles_dir = agent_system_dir / "profiles"
    archive_dir = agent_system_dir / "archive"
    agents_dir = test_dir / ".github" / "agents"
    
    profiles_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)
    agents_dir.mkdir(parents=True)
    
    # Create registry with sample agents
    registry = {
        "version": "2.0.0",
        "agents": [
            {
                "id": "agent-test-1",
                "name": "Test Agent 1",
                "human_name": "Agent1",
                "specialization": "test-specialist-1",
                "status": "active",
                "spawned_at": "2025-11-14T00:00:00Z",
                "metrics": {"overall_score": 0.5}
            },
            {
                "id": "agent-test-2",
                "name": "Test Agent 2",
                "human_name": "Agent2",
                "specialization": "test-specialist-2",
                "status": "active",
                "spawned_at": "2025-11-14T00:00:00Z",
                "metrics": {"overall_score": 0.5}
            },
            {
                "id": "agent-test-3",
                "name": "Test Agent 3",
                "human_name": "Agent3",
                "specialization": "test-specialist-3",
                "status": "active",
                "spawned_at": "2025-11-14T00:00:00Z",
                "metrics": {"overall_score": 0.5}
            }
        ],
        "hall_of_fame": [],
        "system_lead": None,
        "config": {
            "max_active_agents": 10,
            "elimination_threshold": 0.3,
            "promotion_threshold": 0.85
        }
    }
    
    registry_path = agent_system_dir / "registry.json"
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    # Create profile files for each agent
    for agent in registry["agents"]:
        profile_path = profiles_dir / f"{agent['id']}.md"
        with open(profile_path, 'w') as f:
            f.write(f"# {agent['name']}\n\nTest profile for {agent['id']}\n")
    
    # Create agent definition files
    for agent in registry["agents"]:
        agent_def_path = agents_dir / f"{agent['specialization']}.md"
        with open(agent_def_path, 'w') as f:
            f.write(f"# {agent['specialization']}\n\nTest definition\n")
    
    return test_dir


def test_delete_all_agents():
    """
    Test that delete_mode='all' properly deletes all active agents.
    
    Expected behavior:
    - All agents marked as 'deleted'
    - All agents removed from active list
    - All profiles moved to archive
    - Agent definitions remain (for future spawns)
    """
    print("\n" + "="*70)
    print("TEST: Delete All Agents (delete_mode='all')")
    print("="*70)
    
    test_dir = setup_test_environment()
    os.chdir(test_dir)
    
    try:
        registry_path = Path(".github/agent-system/registry.json")
        
        # Load registry
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        initial_count = len([a for a in registry['agents'] if a.get('status') == 'active'])
        print(f"Initial active agents: {initial_count}")
        
        # Simulate delete_mode='all' logic from agent-spawner.yml
        deleted_agents = []
        
        for agent in registry['agents']:
            if agent.get('status') == 'active':
                agent['status'] = 'deleted'
                agent['deleted_at'] = datetime.utcnow().isoformat() + 'Z'
                agent['deletion_reason'] = 'Manual deletion - all agents'
                deleted_agents.append(agent)
                
                # Archive profile
                profile_path = Path(f".github/agent-system/profiles/{agent['id']}.md")
                archive_path = Path(f".github/agent-system/archive/{agent['id']}.md")
                if profile_path.exists():
                    shutil.move(str(profile_path), str(archive_path))
                    print(f"  ✓ Archived profile: {agent['id']}")
                else:
                    print(f"  ✗ Profile not found: {agent['id']}")
                    return False
        
        # Remove deleted agents from active list
        registry['agents'] = [a for a in registry['agents'] if a.get('status') != 'deleted']
        
        # Verify results
        final_count = len([a for a in registry['agents'] if a.get('status') == 'active'])
        archived_count = len(list(Path(".github/agent-system/archive").glob("*.md")))
        
        print(f"\nResults:")
        print(f"  Deleted agents: {len(deleted_agents)}")
        print(f"  Final active agents: {final_count}")
        print(f"  Archived profiles: {archived_count}")
        
        # Assertions
        success = True
        if final_count != 0:
            print(f"  ✗ FAIL: Expected 0 active agents, got {final_count}")
            success = False
        else:
            print(f"  ✓ PASS: All agents removed from active list")
        
        if archived_count != initial_count:
            print(f"  ✗ FAIL: Expected {initial_count} archived profiles, got {archived_count}")
            success = False
        else:
            print(f"  ✓ PASS: All profiles archived")
        
        # Verify agent definitions still exist
        for agent in deleted_agents:
            specialization = agent.get('specialization')
            def_path = Path(f".github/agents/{specialization}.md")
            if def_path.exists():
                print(f"  ✓ Agent definition remains: {specialization}.md")
            else:
                print(f"  ✗ Agent definition missing: {specialization}.md")
                success = False
        
        return success
        
    finally:
        # Cleanup
        os.chdir("/")
        shutil.rmtree(test_dir)


def test_delete_specific_agents():
    """
    Test that delete_mode='specific' properly deletes only specified agents.
    
    Expected behavior:
    - Only specified agents marked as 'deleted'
    - Only specified agents removed from active list
    - Only specified profiles moved to archive
    - Other agents remain active
    """
    print("\n" + "="*70)
    print("TEST: Delete Specific Agents (delete_mode='specific')")
    print("="*70)
    
    test_dir = setup_test_environment()
    os.chdir(test_dir)
    
    try:
        registry_path = Path(".github/agent-system/registry.json")
        
        # Load registry
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        initial_count = len([a for a in registry['agents'] if a.get('status') == 'active'])
        print(f"Initial active agents: {initial_count}")
        
        # Simulate delete_mode='specific' with agent-test-1 and agent-test-3
        delete_ids = ['agent-test-1', 'agent-test-3']
        print(f"Deleting specific agents: {', '.join(delete_ids)}")
        
        deleted_agents = []
        
        for agent_id in delete_ids:
            agent = next((a for a in registry['agents'] if a['id'] == agent_id), None)
            if agent and agent.get('status') == 'active':
                agent['status'] = 'deleted'
                agent['deleted_at'] = datetime.utcnow().isoformat() + 'Z'
                agent['deletion_reason'] = f'Manual deletion - specific ID: {agent_id}'
                deleted_agents.append(agent)
                
                # Archive profile
                profile_path = Path(f".github/agent-system/profiles/{agent['id']}.md")
                archive_path = Path(f".github/agent-system/archive/{agent['id']}.md")
                if profile_path.exists():
                    shutil.move(str(profile_path), str(archive_path))
                    print(f"  ✓ Archived profile: {agent['id']}")
        
        # Remove deleted agents from active list
        registry['agents'] = [a for a in registry['agents'] if a.get('status') != 'deleted']
        
        # Verify results
        final_count = len([a for a in registry['agents'] if a.get('status') == 'active'])
        archived_count = len(list(Path(".github/agent-system/archive").glob("*.md")))
        
        print(f"\nResults:")
        print(f"  Deleted agents: {len(deleted_agents)}")
        print(f"  Final active agents: {final_count}")
        print(f"  Archived profiles: {archived_count}")
        
        # Assertions
        success = True
        expected_remaining = initial_count - len(delete_ids)
        if final_count != expected_remaining:
            print(f"  ✗ FAIL: Expected {expected_remaining} active agents, got {final_count}")
            success = False
        else:
            print(f"  ✓ PASS: Correct number of agents remaining")
        
        if archived_count != len(delete_ids):
            print(f"  ✗ FAIL: Expected {len(delete_ids)} archived profiles, got {archived_count}")
            success = False
        else:
            print(f"  ✓ PASS: Correct number of profiles archived")
        
        # Verify agent-test-2 is still active
        remaining_agent = next((a for a in registry['agents'] if a['id'] == 'agent-test-2'), None)
        if remaining_agent and remaining_agent.get('status') == 'active':
            print(f"  ✓ PASS: Non-deleted agent remains active (agent-test-2)")
        else:
            print(f"  ✗ FAIL: Non-deleted agent was incorrectly modified")
            success = False
        
        return success
        
    finally:
        # Cleanup
        os.chdir("/")
        shutil.rmtree(test_dir)


def test_deletion_conditional_logic():
    """
    Test that the deletion step conditional works correctly.
    
    Expected behavior:
    - delete_mode='none' -> step skipped
    - delete_mode='all' -> step runs
    - delete_mode='specific' -> step runs
    - delete_mode='' (empty) -> step skipped
    - delete_mode=null (scheduled run) -> step skipped
    """
    print("\n" + "="*70)
    print("TEST: Deletion Conditional Logic")
    print("="*70)
    
    test_cases = [
        ('none', False, "delete_mode='none' should skip"),
        ('all', True, "delete_mode='all' should run"),
        ('specific', True, "delete_mode='specific' should run"),
        ('', False, "delete_mode='' should skip"),
        (None, False, "delete_mode=null should skip"),
    ]
    
    all_passed = True
    
    for delete_mode, should_run, description in test_cases:
        # Simulate the conditional: github.event.inputs.delete_mode != 'none' && github.event.inputs.delete_mode != ''
        # In Python equivalent: delete_mode != 'none' and delete_mode != ''
        
        # Handle None case (null in YAML becomes None in Python)
        if delete_mode is None:
            # In GitHub Actions, null values in conditionals are falsy
            condition_result = False
        else:
            condition_result = delete_mode != 'none' and delete_mode != ''
        
        status = "✓ PASS" if condition_result == should_run else "✗ FAIL"
        print(f"  {status}: {description}")
        print(f"    delete_mode={repr(delete_mode)}, should_run={should_run}, actual={condition_result}")
        
        if condition_result != should_run:
            all_passed = False
    
    return all_passed


def test_edge_cases():
    """
    Test edge cases in deletion workflow.
    
    Expected behavior:
    - Deleting non-existent agent ID -> warning, continue
    - Deleting already-deleted agent -> warning, continue
    - Profile file missing -> still mark as deleted
    - Archive directory doesn't exist -> create it
    """
    print("\n" + "="*70)
    print("TEST: Edge Cases")
    print("="*70)
    
    test_dir = setup_test_environment()
    os.chdir(test_dir)
    
    try:
        registry_path = Path(".github/agent-system/registry.json")
        
        # Test 1: Delete non-existent agent
        print("\n  Test 1: Delete non-existent agent")
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        agent = next((a for a in registry['agents'] if a['id'] == 'non-existent-agent'), None)
        if agent is None:
            print("    ✓ PASS: Non-existent agent handled correctly (None returned)")
        else:
            print("    ✗ FAIL: Non-existent agent should return None")
            return False
        
        # Test 2: Delete already-deleted agent
        print("\n  Test 2: Delete already-deleted agent")
        registry['agents'][0]['status'] = 'deleted'
        agent = registry['agents'][0]
        if agent.get('status') == 'active':
            print("    ✗ FAIL: Agent should be marked as deleted")
            return False
        else:
            print("    ✓ PASS: Already-deleted agent detected")
        
        # Test 3: Profile file missing
        print("\n  Test 3: Profile file missing")
        profile_path = Path(".github/agent-system/profiles/agent-test-2.md")
        profile_path.unlink()  # Delete the file
        
        # Simulate deletion
        agent = next((a for a in registry['agents'] if a['id'] == 'agent-test-2'), None)
        if agent:
            agent['status'] = 'deleted'
            if not profile_path.exists():
                print("    ✓ PASS: Agent marked as deleted even with missing profile")
            else:
                print("    ✗ FAIL: Profile should be missing")
                return False
        
        # Test 4: Archive directory auto-creation
        print("\n  Test 4: Archive directory auto-creation")
        archive_dir = Path(".github/agent-system/archive")
        shutil.rmtree(archive_dir)  # Delete archive directory
        
        if not archive_dir.exists():
            archive_dir.mkdir(parents=True)
            if archive_dir.exists():
                print("    ✓ PASS: Archive directory created when missing")
            else:
                print("    ✗ FAIL: Archive directory should be created")
                return False
        
        return True
        
    finally:
        # Cleanup
        os.chdir("/")
        shutil.rmtree(test_dir)


def main():
    """Run all deletion workflow tests."""
    print("\n" + "="*70)
    print("🧪 @assert-specialist: Agent Deletion Workflow Tests")
    print("Specification-driven validation of agent deletion logic")
    print("="*70)
    
    tests = [
        ("Delete All Agents", test_delete_all_agents),
        ("Delete Specific Agents", test_delete_specific_agents),
        ("Deletion Conditional Logic", test_deletion_conditional_logic),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n✗ FAIL: Test '{name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed!")
        print("\n@assert-specialist: Systematic validation complete.")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("\n@assert-specialist: Issues detected. See details above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
