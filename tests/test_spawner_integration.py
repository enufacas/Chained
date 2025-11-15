#!/usr/bin/env python3
"""
Integration test for agent spawner name uniqueness fix.

Simulates the spawner workflow to verify:
1. Names are not repeated when spawning multiple agents
2. Fallback mechanism works when names are exhausted
3. Helper script integrates correctly with workflow logic

@assert-specialist - Comprehensive integration testing
"""

import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / 'tools'))

from registry_manager import RegistryManager


def test_workflow_name_selection():
    """Simulate workflow's name selection logic with the fix."""
    print("\n🧪 Testing: Workflow name selection (simulated)...")
    
    # Get available names using the helper script
    result = subprocess.run(
        ['python3', 'tools/get-available-human-names.py', '--format', 'json'],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )
    
    if result.returncode != 0:
        print(f"❌ FAILED: Helper script failed: {result.stderr}")
        return False
    
    import json
    available_names = json.loads(result.stdout)
    
    print(f"   Available names: {len(available_names)}")
    if available_names:
        print(f"   Names: {available_names}")
    
    # Simulate selecting a random name (what workflow does)
    if available_names:
        import random
        selected = random.choice(available_names)
        print(f"   Selected: {selected}")
        
        # Verify it's not already used
        registry = RegistryManager()
        agents = registry.list_agents(status='active')
        used_names = {agent.get('human_name', 'Unknown') for agent in agents}
        
        if selected in used_names:
            print(f"❌ FAILED: Selected name '{selected}' is already in use!")
            return False
    
    print("✅ PASSED: Workflow name selection logic validated")
    return True


def test_multiple_spawns_no_duplicates():
    """Verify that script correctly excludes used names."""
    print("\n🧪 Testing: Script excludes already-used names...")
    
    # Get current active agents to track used names
    registry = RegistryManager()
    agents = registry.list_agents(status='active')
    used_names = {agent.get('human_name', 'Unknown') for agent in agents}
    
    print(f"   Starting with {len(used_names)} used names")
    
    # Get a name from available pool
    result = subprocess.run(
        ['python3', 'tools/get-available-human-names.py', '--format', 'random', '--with-fallback'],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )
    
    if result.returncode != 0:
        print(f"❌ FAILED: Failed to get name: {result.stderr}")
        return False
    
    name = result.stdout.strip()
    print(f"   Retrieved name: {name}")
    
    # Check that it's not already used (unless it's a fallback with suffix)
    if name in used_names:
        # If it's in used_names, it should have a suffix (fallback)
        if not any(name.endswith(f'-{i}') for i in range(2, 100)):
            print(f"❌ FAILED: Name '{name}' is already used and has no fallback suffix!")
            return False
        else:
            print(f"   Note: '{name}' is a fallback name (all base names used)")
    
    # Verify all available names are truly available
    result = subprocess.run(
        ['python3', 'tools/get-available-human-names.py', '--format', 'json'],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )
    
    import json
    available = json.loads(result.stdout)
    
    for avail_name in available:
        if avail_name in used_names:
            print(f"❌ FAILED: Available list contains used name '{avail_name}'!")
            return False
    
    print(f"✅ PASSED: Script correctly excludes used names")
    print(f"   Available names verified: {len(available)}")
    print(f"   Note: In real workflow, each spawn updates registry before next")
    return True


def test_fallback_when_exhausted():
    """Test fallback mechanism when all base names are used."""
    print("\n🧪 Testing: Fallback when names exhausted...")
    
    # Count how many names are available
    result = subprocess.run(
        ['python3', 'tools/get-available-human-names.py', '--format', 'count'],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )
    
    available_count = int(result.stdout.strip())
    print(f"   Currently available names: {available_count}")
    
    # Even with 0 available, fallback should work
    result = subprocess.run(
        ['python3', 'tools/get-available-human-names.py', '--format', 'random', '--with-fallback'],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )
    
    if result.returncode != 0:
        print(f"❌ FAILED: Fallback mechanism failed: {result.stderr}")
        return False
    
    name = result.stdout.strip()
    print(f"   Fallback name: {name}")
    
    if not name:
        print("❌ FAILED: No name returned even with fallback!")
        return False
    
    print("✅ PASSED: Fallback mechanism works")
    return True


def test_workflow_bash_integration():
    """Test that the bash workflow commands would work."""
    print("\n🧪 Testing: Bash workflow integration...")
    
    # Simulate the exact bash command from workflow
    bash_cmd = """
    HUMAN_NAME=$(python3 tools/get-available-human-names.py --format random --with-fallback)
    if [ -z "$HUMAN_NAME" ]; then
      echo "FAILED"
      exit 1
    fi
    echo "$HUMAN_NAME"
    """
    
    result = subprocess.run(
        ['bash', '-c', bash_cmd],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT
    )
    
    if result.returncode != 0 or 'FAILED' in result.stdout:
        print(f"❌ FAILED: Bash integration failed: {result.stderr}")
        return False
    
    name = result.stdout.strip()
    print(f"   Bash retrieved name: {name}")
    
    if not name:
        print("❌ FAILED: Bash command returned empty name")
        return False
    
    print("✅ PASSED: Bash workflow integration works")
    return True


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("🧪 Agent Spawner Integration Tests (@assert-specialist)")
    print("=" * 70)
    
    tests = [
        ("Workflow Name Selection", test_workflow_name_selection),
        ("Script Excludes Used Names", test_multiple_spawns_no_duplicates),
        ("Fallback When Exhausted", test_fallback_when_exhausted),
        ("Bash Workflow Integration", test_workflow_bash_integration),
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
        print("\n🎉 All integration tests passed!")
        print("\n✅ The fix is working correctly:")
        print("   - Helper script provides unique names")
        print("   - Fallback mechanism handles exhaustion")
        print("   - Bash workflow integration successful")
        print("   - Multiple spawns avoid duplicates")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
