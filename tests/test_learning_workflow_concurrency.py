#!/usr/bin/env python3
"""
Test suite for learning workflow concurrency control and merge conflict prevention.

This test validates that learning workflows:
1. Have proper concurrency controls to prevent race conditions
2. Implement pull-before-push strategy to avoid conflicts
3. Use consistent concurrency groups
4. Have merge conflict resolution logic

Related to issue: Enhanced learning continue to cause merge conflicts
"""

import sys
import yaml
import re
from pathlib import Path
from typing import Dict, List, Tuple


class ConcurrencyTestError(Exception):
    """Exception raised for concurrency test failures."""
    pass


def load_workflow(filepath: Path) -> Dict:
    """Load and parse a workflow YAML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            workflow = yaml.safe_load(content)
            
            # YAML might interpret 'on:' as True (boolean)
            if workflow and True in workflow and 'on' not in workflow:
                workflow['on'] = workflow.pop(True)
            
            return workflow
    except Exception as e:
        raise ConcurrencyTestError(f"Failed to load {filepath}: {e}")


def test_has_concurrency_control(workflow: Dict, workflow_name: str) -> List[str]:
    """Test that workflow has concurrency control defined."""
    issues = []
    
    if 'concurrency' not in workflow:
        issues.append(f"{workflow_name}: Missing 'concurrency' configuration")
        return issues
    
    concurrency = workflow['concurrency']
    
    # Check required fields
    if 'group' not in concurrency:
        issues.append(f"{workflow_name}: Concurrency missing 'group' field")
    
    if 'cancel-in-progress' not in concurrency:
        issues.append(f"{workflow_name}: Concurrency missing 'cancel-in-progress' field")
    elif concurrency['cancel-in-progress'] is True:
        # For learning workflows, we want queuing, not cancellation
        issues.append(
            f"{workflow_name}: 'cancel-in-progress' should be false to queue runs "
            "instead of canceling them"
        )
    
    return issues


def test_pull_before_push(workflow_content: str, workflow_name: str) -> List[str]:
    """Test that workflow implements pull-before-push strategy."""
    issues = []
    
    # Check if workflow creates PRs (has gh pr create or git push)
    creates_pr = 'gh pr create' in workflow_content or 'git push origin' in workflow_content
    
    if not creates_pr:
        # Workflow doesn't create PRs, no need for pull-before-push
        return issues
    
    # Check for pull before push
    has_fetch = 'git fetch origin main' in workflow_content
    has_merge = 'git merge origin/main' in workflow_content
    
    if not has_fetch:
        issues.append(
            f"{workflow_name}: Missing 'git fetch origin main' before creating PR. "
            "Should pull latest changes to avoid conflicts."
        )
    
    if not has_merge:
        issues.append(
            f"{workflow_name}: Missing 'git merge origin/main' before creating PR. "
            "Should merge latest changes to avoid conflicts."
        )
    
    # Check for conflict resolution
    has_conflict_resolution = 'git checkout --ours' in workflow_content
    
    if has_fetch and has_merge and not has_conflict_resolution:
        issues.append(
            f"{workflow_name}: Has fetch/merge but missing conflict resolution strategy. "
            "Should handle merge conflicts with 'git checkout --ours learnings/'"
        )
    
    return issues


def test_concurrency_group_consistency(workflows: Dict[str, Dict]) -> List[str]:
    """Test that related workflows use consistent concurrency groups."""
    issues = []
    
    # Learning workflows that update same directories should share concurrency group
    learning_workflows = {
        'self-documenting-ai.yml': None,
        'self-documenting-ai-enhanced.yml': None,
    }
    
    for workflow_name, workflow in workflows.items():
        if workflow_name in learning_workflows:
            if 'concurrency' in workflow and 'group' in workflow['concurrency']:
                learning_workflows[workflow_name] = workflow['concurrency']['group']
    
    # Check if both workflows have the same concurrency group
    groups = [g for g in learning_workflows.values() if g is not None]
    
    if len(set(groups)) > 1:
        issues.append(
            f"Learning workflows have different concurrency groups: {learning_workflows}. "
            "They should use the same group to prevent concurrent runs on same files."
        )
    
    if len(groups) == 0:
        issues.append(
            "No concurrency groups defined for learning workflows. "
            "This can cause race conditions and merge conflicts."
        )
    
    return issues


def test_learnings_directory_protection(workflow_content: str, workflow_name: str) -> List[str]:
    """Test that workflow properly handles learnings directory updates."""
    issues = []
    
    # Check if workflow updates learnings directory
    updates_learnings = (
        'learnings/' in workflow_content or 
        'learnings/discussions' in workflow_content
    )
    
    if not updates_learnings:
        # Workflow doesn't update learnings, no need to check
        return issues
    
    # Should have concurrency control
    if 'concurrency:' not in workflow_content:
        issues.append(
            f"{workflow_name}: Updates 'learnings/' directory but has no concurrency control. "
            "Multiple simultaneous runs can cause merge conflicts."
        )
    
    # Should have git config before commits
    if 'git commit' in workflow_content:
        has_git_config = (
            'git config user.name' in workflow_content and
            'git config user.email' in workflow_content
        )
        
        if not has_git_config:
            issues.append(
                f"{workflow_name}: Has 'git commit' but missing git config. "
                "Should configure user.name and user.email."
            )
    
    return issues


def run_all_tests():
    """Run all concurrency and conflict prevention tests."""
    print("Testing learning workflow concurrency controls...")
    print("=" * 70)
    
    workflows_dir = Path('.github/workflows')
    
    if not workflows_dir.exists():
        print(f"ERROR: Workflows directory not found: {workflows_dir}")
        return 1
    
    # Target workflows that handle learning data
    target_workflows = [
        'self-documenting-ai.yml',
        'self-documenting-ai-enhanced.yml',
        'combined-learning.yml',
    ]
    
    all_issues = []
    workflows = {}
    workflow_contents = {}
    
    # Load and test each workflow
    for workflow_file in target_workflows:
        workflow_path = workflows_dir / workflow_file
        
        if not workflow_path.exists():
            print(f"⚠️  WARNING: Workflow not found: {workflow_file}")
            continue
        
        print(f"\nTesting: {workflow_file}")
        print("-" * 70)
        
        try:
            # Load workflow
            workflow = load_workflow(workflow_path)
            workflows[workflow_file] = workflow
            
            # Load raw content for text-based checks
            with open(workflow_path, 'r') as f:
                workflow_content = f.read()
                workflow_contents[workflow_file] = workflow_content
            
            # Run individual workflow tests
            issues = []
            
            # Test 1: Concurrency control
            issues.extend(test_has_concurrency_control(workflow, workflow_file))
            
            # Test 2: Pull-before-push
            issues.extend(test_pull_before_push(workflow_content, workflow_file))
            
            # Test 3: Learnings directory protection
            issues.extend(test_learnings_directory_protection(workflow_content, workflow_file))
            
            if issues:
                print(f"❌ Found {len(issues)} issue(s):")
                for issue in issues:
                    print(f"   - {issue}")
                all_issues.extend(issues)
            else:
                print("✅ All checks passed")
        
        except Exception as e:
            error_msg = f"{workflow_file}: Test error: {e}"
            print(f"❌ {error_msg}")
            all_issues.append(error_msg)
    
    # Run cross-workflow tests
    print("\n" + "=" * 70)
    print("Cross-workflow consistency tests")
    print("-" * 70)
    
    consistency_issues = test_concurrency_group_consistency(workflows)
    
    if consistency_issues:
        print(f"❌ Found {len(consistency_issues)} issue(s):")
        for issue in consistency_issues:
            print(f"   - {issue}")
        all_issues.extend(consistency_issues)
    else:
        print("✅ Concurrency groups are consistent")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Workflows tested: {len(workflows)}")
    print(f"Total issues found: {len(all_issues)}")
    
    if all_issues:
        print("\n❌ TESTS FAILED")
        print("\nAll issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        return 1
    else:
        print("\n✅ ALL TESTS PASSED")
        print("\nConcurrency controls are properly configured:")
        print("- Learning workflows have concurrency groups")
        print("- Pull-before-push strategy is implemented")
        print("- Merge conflict resolution is in place")
        print("- Learnings directory is protected from race conditions")
        return 0


if __name__ == '__main__':
    sys.exit(run_all_tests())
