#!/usr/bin/env python3
"""
Test to demonstrate the agent deletion commit bug.

Bug: When delete_mode='all' is used but spawning is skipped (can_spawn=false),
the deletion changes are never committed because the commit step has
if: steps.check_capacity.outputs.can_spawn == 'true'

This means deletions are lost!

@assert-specialist specification-driven bug demonstration
"""

def test_deletion_without_spawn_commit():
    """
    Demonstrate that deletions are lost when spawning is skipped.
    
    Scenario:
    1. User runs workflow with delete_mode='all'
    2. Delete step runs, modifies registry, saves to file
    3. Capacity check runs, determines can_spawn=false (for some reason)
    4. Spawn step is skipped (if: can_spawn == 'true')
    5. Commit step is skipped (if: can_spawn == 'true')
    6. Result: Deletion changes are in the file but never committed to PR!
    7. Next workflow run will use OLD registry from main branch
    8. Deletions are LOST!
    
    Current workflow structure:
    ```yaml
    - name: Delete agents if requested
      # Modifies registry file
      
    - name: Check agent capacity
      id: check_capacity
      # Outputs: can_spawn=true/false
      
    - name: Generate agent DNA
      if: steps.check_capacity.outputs.can_spawn == 'true'
      
    - name: Register agent
      if: steps.check_capacity.outputs.can_spawn == 'true'
      
    - name: Commit and create PR
      if: steps.check_capacity.outputs.can_spawn == 'true'  # ← BUG!
      # Only commits if spawn succeeded
    ```
    
    The fix: Commit step should run if EITHER:
    - Agents were deleted (steps.delete_agents.outputs.deleted_count > 0)
    - OR agent was spawned (steps.check_capacity.outputs.can_spawn == 'true')
    
    Correct condition:
    ```yaml
    - name: Commit and create PR
      if: steps.check_capacity.outputs.can_spawn == 'true' || (steps.delete_agents.outputs.deleted_count && steps.delete_agents.outputs.deleted_count > '0')
    ```
    """
    print("\n" + "="*70)
    print("🐛 @assert-specialist: Deletion Commit Bug Demonstration")
    print("="*70)
    
    print("\n📋 Bug Analysis:")
    print("-" * 70)
    
    print("\n1. Current Workflow Steps:")
    print("   ✓ Delete agents (modifies registry)")
    print("   ✓ Check capacity (reads modified registry)")
    print("   ✗ Spawn agent (if: can_spawn == 'true') - MAY BE SKIPPED")
    print("   ✗ Commit PR (if: can_spawn == 'true') - BUG: SKIPPED WHEN SPAWN SKIPPED")
    
    print("\n2. Problem Scenario:")
    print("   User runs: delete_mode='all'")
    print("   ├─ Delete step: Deletes 10 agents, saves registry ✓")
    print("   ├─ Check capacity: can_spawn=false (some condition)")
    print("   ├─ Spawn step: SKIPPED (if condition false)")
    print("   └─ Commit step: SKIPPED (if condition false) ← BUG!")
    
    print("\n3. Consequences:")
    print("   ✗ Deletion changes exist only in workflow runner")
    print("   ✗ No PR created to commit deletions")
    print("   ✗ Next run pulls OLD registry from main")
    print("   ✗ Agents reappear (deletion lost)")
    
    print("\n4. Root Cause:")
    print("   The commit step is conditional on spawning success:")
    print("   if: steps.check_capacity.outputs.can_spawn == 'true'")
    print("   ")
    print("   This assumes deletion ALWAYS comes with spawning.")
    print("   But user may want delete-only operation!")
    
    print("\n5. Evidence in Workflow:")
    print("   Line 555-558 in agent-spawner.yml:")
    print("   ```yaml")
    print("   - name: Commit and create PR")
    print("     id: create_spawn_pr")
    print("     if: steps.check_capacity.outputs.can_spawn == 'true'")
    print("   ```")
    
    print("\n" + "="*70)
    print("🔧 @assert-specialist: Recommended Fix")
    print("="*70)
    
    print("\n1. Add output to delete step:")
    print("   ```yaml")
    print("   - name: Delete agents if requested")
    print("     id: delete_agents")
    print("     outputs:")
    print("       deleted_count: ${{ steps.delete_agents.outputs.deleted_count }}")
    print("   ```")
    
    print("\n2. Update commit step condition:")
    print("   ```yaml")
    print("   - name: Commit and create PR")
    print("     if: |")
    print("       steps.check_capacity.outputs.can_spawn == 'true' || ")
    print("       (steps.delete_agents.outputs.deleted_count &&")
    print("        steps.delete_agents.outputs.deleted_count != '0')")
    print("   ```")
    
    print("\n3. Update commit logic to handle delete-only:")
    print("   - If deleted but not spawned: Create PR for deletions only")
    print("   - If spawned but not deleted: Create PR for spawn only")
    print("   - If both: Create PR for both (current behavior)")
    
    print("\n4. Alternative: Separate delete-only workflow")
    print("   - Create dedicated 'Delete Agents' workflow")
    print("   - Keeps agent-spawner focused on spawning")
    print("   - Clearer separation of concerns")
    
    print("\n" + "="*70)
    print("✅ @assert-specialist: Analysis Complete")
    print("="*70)
    
    print("\nThis demonstrates the bug where deletions are lost")
    print("when spawning is skipped. The workflow needs to commit")
    print("deletion changes independently of spawn success.")
    
    return True


if __name__ == '__main__':
    test_deletion_without_spawn_commit()
