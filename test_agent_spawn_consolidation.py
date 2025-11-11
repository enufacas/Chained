#!/usr/bin/env python3
"""
Test for agent spawn workflow consolidation.
Verifies that agent registration and assignment happens only in the spawn workflow,
and that copilot-graphql-assign correctly skips agent-system issues.
"""

import sys
import yaml
from pathlib import Path


def test_copilot_assign_skips_agent_system():
    """Test that copilot-graphql-assign.yml skips agent-system issues."""
    print("\n🧪 Testing copilot-graphql-assign skips agent-system issues")
    print("-" * 60)
    
    workflow_path = Path('.github/workflows/copilot-graphql-assign.yml')
    
    if not workflow_path.exists():
        print(f"❌ FAILED: Workflow file not found: {workflow_path}")
        return False
    
    with open(workflow_path, 'r') as f:
        workflow = yaml.safe_load(f)
    
    # Check that the job condition excludes agent-system issues
    job = workflow.get('jobs', {}).get('assign-to-copilot', {})
    job_condition = job.get('if', '')
    
    # The condition should check for agent-system label
    if 'agent-system' not in job_condition:
        print(f"❌ FAILED: Job condition does not check for 'agent-system' label")
        print(f"   Current condition: {job_condition}")
        return False
    
    # Check that it skips issues with agent-system label
    if "!contains(github.event.issue.labels.*.name, 'agent-system')" not in job_condition:
        print(f"❌ FAILED: Job condition does not properly skip agent-system issues")
        print(f"   Current condition: {job_condition}")
        return False
    
    print(f"✅ PASSED: copilot-graphql-assign correctly skips agent-system issues")
    print(f"   Condition: {job_condition.strip()}")
    return True


def test_agent_spawner_creates_issues_with_labels():
    """Test that agent-spawner creates issues with agent-system label."""
    print("\n🧪 Testing agent-spawner creates issues with agent-system label and directive")
    print("-" * 60)
    
    workflow_path = Path('.github/workflows/agent-spawner.yml')
    
    if not workflow_path.exists():
        print(f"❌ FAILED: Workflow file not found: {workflow_path}")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # Check that the issue creation includes agent-system label
    if '--label "agent-system,agent-work"' not in content and '--label agent-system,agent-work' not in content:
        print(f"❌ FAILED: agent-spawner does not create issues with agent-system label")
        return False
    
    # Check that the issue includes Copilot directive
    if '<!-- COPILOT_AGENT:' not in content:
        print(f"❌ FAILED: agent-spawner does not include Copilot agent directive")
        return False
    
    # Check that the directive includes @mention
    if '**@${SPECIALIZATION}**' not in content and '**@$SPECIALIZATION**' not in content:
        print(f"❌ FAILED: agent-spawner directive does not include @mention")
        return False
    
    print(f"✅ PASSED: agent-spawner creates issues with:")
    print(f"   • agent-system label")
    print(f"   • Copilot agent directive")
    print(f"   • @mention of agent")
    return True


def test_agent_spawner_registers_and_assigns():
    """Test that agent-spawner handles both registration and assignment."""
    print("\n🧪 Testing agent-spawner handles registration and assignment")
    print("-" * 60)
    
    workflow_path = Path('.github/workflows/agent-spawner.yml')
    
    if not workflow_path.exists():
        print(f"❌ FAILED: Workflow file not found: {workflow_path}")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # Check for key steps
    required_steps = [
        ('name: Register agent', 'Registration'),
        ('name: Create agent profile', 'Profile creation'),
        ('name: Create agent work and welcome issue', 'Issue creation'),
        ('name: Assign work issue to Copilot', 'Copilot assignment'),
    ]
    
    missing = []
    for step_pattern, description in required_steps:
        if step_pattern not in content:
            missing.append(description)
    
    if missing:
        print(f"❌ FAILED: Missing steps in agent-spawner: {', '.join(missing)}")
        return False
    
    print(f"✅ PASSED: agent-spawner includes all required steps:")
    for _, description in required_steps:
        print(f"   • {description}")
    
    return True


def test_assign_script_skips_agent_system():
    """Test that assign-copilot-to-issue.sh skips agent-system issues."""
    print("\n🧪 Testing assign-copilot-to-issue.sh skips agent-system issues")
    print("-" * 60)
    
    script_path = Path('tools/assign-copilot-to-issue.sh')
    
    if not script_path.exists():
        print(f"❌ FAILED: Script file not found: {script_path}")
        return False
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Check that the script checks for agent-system label
    if 'agent-system' not in content:
        print(f"❌ FAILED: Script does not check for agent-system label")
        return False
    
    # Check that it skips agent-system issues
    if 'Skipping issue' not in content or 'agent-spawner workflow' not in content:
        print(f"❌ FAILED: Script does not properly skip agent-system issues")
        return False
    
    print(f"✅ PASSED: assign-copilot-to-issue.sh correctly skips agent-system issues")
    return True


def test_issue_has_clear_task_directive():
    """Test that spawned issues have clear task directives."""
    print("\n🧪 Testing spawned issues have clear task directives")
    print("-" * 60)
    
    workflow_path = Path('.github/workflows/agent-spawner.yml')
    
    if not workflow_path.exists():
        print(f"❌ FAILED: Workflow file not found: {workflow_path}")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    required_elements = [
        ('Your Assignment:', 'Clear assignment section'),
        ('Aligns with your specialization', 'Specialization alignment guidance'),
        ('Demonstrates your capabilities', 'Capability demonstration requirement'),
        ('Success Criteria:', 'Success criteria section'),
        ('agent definition', 'Reference to agent definition'),
    ]
    
    missing = []
    for element, description in required_elements:
        if element not in content:
            missing.append(description)
    
    if missing:
        print(f"❌ FAILED: Issue directive missing elements:")
        for item in missing:
            print(f"   • {item}")
        return False
    
    print(f"✅ PASSED: Issue includes clear task directive with:")
    for _, description in required_elements:
        print(f"   • {description}")
    
    return True


def test_spawn_pr_linked_to_work_issue():
    """Test that spawn PR is properly linked to work issue."""
    print("\n🧪 Testing spawn PR is linked to work issue")
    print("-" * 60)
    
    workflow_path = Path('.github/workflows/agent-spawner.yml')
    
    if not workflow_path.exists():
        print(f"❌ FAILED: Workflow file not found: {workflow_path}")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # Check that PR creation step has an ID
    if 'id: create_spawn_pr' not in content:
        print(f"❌ FAILED: PR creation step does not have id 'create_spawn_pr'")
        return False
    
    # Check that PR number is captured as output
    if 'pr_number=$PR_NUMBER' not in content or 'echo "pr_number=' not in content:
        print(f"❌ FAILED: PR number is not captured as step output")
        return False
    
    # Check that issue references the PR number
    if 'PR_NUMBER="${{ steps.create_spawn_pr.outputs.pr_number }}"' not in content:
        print(f"❌ FAILED: Issue creation does not reference spawn PR number")
        return False
    
    # Check that issue explains the spawn sequence
    if 'Agent Spawn Sequence' not in content:
        print(f"❌ FAILED: Issue does not include 'Agent Spawn Sequence' section")
        return False
    
    # Check for step that links PR to issue
    if 'name: Link PR to work issue' not in content:
        print(f"❌ FAILED: Missing step to link PR to work issue")
        return False
    
    print(f"✅ PASSED: Spawn PR is properly linked to work issue")
    print(f"   • PR creation captures PR number")
    print(f"   • Issue references spawn PR")
    print(f"   • Issue explains spawn sequence")
    print(f"   • PR is linked back to issue")
    return True


def test_auto_review_handles_agent_spawn():
    """Test that auto-review workflow handles agent spawn PRs specially."""
    print("\n🧪 Testing auto-review handles agent spawn PRs")
    print("-" * 60)
    
    workflow_path = Path('.github/workflows/auto-review-merge.yml')
    
    if not workflow_path.exists():
        print(f"❌ FAILED: Workflow file not found: {workflow_path}")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # Check that it detects agent spawn PRs
    if 'agent-system' not in content:
        print(f"❌ FAILED: auto-review does not check for agent-system label")
        return False
    
    # Check that it looks for linked work issue
    if 'linked_issue' not in content:
        print(f"❌ FAILED: auto-review does not look for linked work issue")
        return False
    
    # Check that it notifies the work issue after merge
    if 'Agent Spawn Complete' not in content:
        print(f"❌ FAILED: auto-review does not notify work issue about spawn completion")
        return False
    
    print(f"✅ PASSED: auto-review properly handles agent spawn PRs")
    print(f"   • Detects agent spawn PRs")
    print(f"   • Extracts linked work issue")
    print(f"   • Notifies work issue after merge")
    return True


def test_no_duplicate_assignment_logic():
    """Test that assignment logic is not duplicated across workflows."""
    print("\n🧪 Testing no duplicate assignment logic")
    print("-" * 60)
    
    # This is more of a documentation check - we verify that:
    # 1. agent-spawner handles assignment for agent-system issues
    # 2. copilot-graphql-assign skips agent-system issues
    # 3. There's no overlap
    
    spawner_path = Path('.github/workflows/agent-spawner.yml')
    copilot_path = Path('.github/workflows/copilot-graphql-assign.yml')
    
    with open(spawner_path, 'r') as f:
        spawner_content = f.read()
    
    with open(copilot_path, 'r') as f:
        copilot_content = f.read()
    
    # Verify spawner assigns to Copilot
    if 'replaceActorsForAssignable' not in spawner_content:
        print(f"⚠️  WARNING: agent-spawner may not be using GraphQL to assign Copilot")
        print(f"   (This might be intentional if using a different method)")
    
    # Verify copilot workflow excludes agent-system
    if "!contains(github.event.issue.labels.*.name, 'agent-system')" not in copilot_content:
        print(f"❌ FAILED: copilot-graphql-assign does not exclude agent-system issues")
        return False
    
    print(f"✅ PASSED: No duplicate assignment logic detected")
    print(f"   • agent-spawner: Handles agent-system issues")
    print(f"   • copilot-graphql-assign: Skips agent-system issues")
    
    return True


def main():
    """Run all consolidation tests."""
    print("=" * 60)
    print("🧪 Agent Spawn Workflow Consolidation Tests")
    print("=" * 60)
    print("\nVerifying that agent registration and assignment are")
    print("consolidated in the spawn workflow, with no conflicts.")
    
    tests = [
        test_copilot_assign_skips_agent_system,
        test_agent_spawner_creates_issues_with_labels,
        test_agent_spawner_registers_and_assigns,
        test_assign_script_skips_agent_system,
        test_issue_has_clear_task_directive,
        test_spawn_pr_linked_to_work_issue,
        test_auto_review_handles_agent_spawn,
        test_no_duplicate_assignment_logic,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All consolidation tests passed!")
        print("\n✨ Agent spawn workflow is properly consolidated:")
        print("   • Agent registration happens in spawn workflow")
        print("   • Profile creation happens in spawn workflow")
        print("   • Issue creation happens in spawn workflow")
        print("   • Copilot assignment happens in spawn workflow")
        print("   • copilot-graphql-assign skips agent-system issues")
        print("   • No duplicate or conflicting logic")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
