#!/usr/bin/env python3
"""
Test suite for analysis workflow concurrency controls.

This script validates that all workflows updating the analysis/ directory have:
1. Concurrency controls to prevent race conditions
2. Pull-before-push strategy to avoid merge conflicts
3. Proper conflict resolution logic
"""

import os
import re
import sys
import yaml


def load_workflow(filepath):
    """Load and parse a workflow YAML file."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)


def check_concurrency_control(workflow_data, workflow_name):
    """Check if workflow has proper concurrency control."""
    issues = []
    
    if 'concurrency' not in workflow_data:
        issues.append(f"Missing 'concurrency' field")
        return issues
    
    concurrency = workflow_data['concurrency']
    
    if 'group' not in concurrency:
        issues.append(f"Missing 'concurrency.group' field")
    elif not concurrency['group'].startswith('analysis-'):
        issues.append(f"Concurrency group should start with 'analysis-': {concurrency['group']}")
    
    if 'cancel-in-progress' not in concurrency:
        issues.append(f"Missing 'cancel-in-progress' field")
    elif concurrency['cancel-in-progress'] is not False:
        issues.append(f"'cancel-in-progress' should be false to queue runs, not cancel them")
    
    return issues


def check_pull_before_push(filepath, workflow_name):
    """Check if workflow implements pull-before-push strategy."""
    issues = []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for git fetch origin main
    if 'git fetch origin main' not in content:
        issues.append(f"Missing 'git fetch origin main' before push")
    
    # Check for git merge
    if 'git merge origin/main' not in content:
        issues.append(f"Missing 'git merge origin/main' to incorporate latest changes")
    
    # Check for conflict resolution
    if 'git checkout --ours analysis/' not in content:
        issues.append(f"Missing conflict resolution with 'git checkout --ours analysis/'")
    
    return issues


def check_analysis_directory_protection(filepath, workflow_name):
    """Check if workflow protects the analysis/ directory."""
    issues = []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Should add analysis/ directory
    if 'git add analysis/' not in content:
        issues.append(f"Workflow doesn't update analysis/ directory")
    
    # Should create PRs (not direct push to main)
    if 'gh pr create' not in content:
        issues.append(f"Workflow doesn't create PR (might push directly to main)")
    
    return issues


def check_concurrency_group_consistency(workflow_files):
    """Check that concurrency groups are properly scoped."""
    issues = []
    groups = {}
    
    for filepath, name in workflow_files:
        try:
            workflow_data = load_workflow(filepath)
            if 'concurrency' in workflow_data:
                group = workflow_data['concurrency'].get('group', '')
                if group:
                    if group in groups:
                        issues.append(f"Concurrency group '{group}' used by multiple workflows: {groups[group]} and {name}")
                    else:
                        groups[group] = name
        except Exception as e:
            issues.append(f"Error loading {name}: {e}")
    
    return issues


def test_workflow(filepath, workflow_name):
    """Test a single workflow for all requirements."""
    print(f"\nTesting: {workflow_name}")
    print("-" * 70)
    
    all_issues = []
    
    try:
        # Load workflow
        workflow_data = load_workflow(filepath)
        
        # Test 1: Concurrency control
        issues = check_concurrency_control(workflow_data, workflow_name)
        if issues:
            print(f"❌ Concurrency control issues:")
            for issue in issues:
                print(f"   - {issue}")
            all_issues.extend(issues)
        else:
            print(f"✅ Concurrency control properly configured")
        
        # Test 2: Pull-before-push strategy
        issues = check_pull_before_push(filepath, workflow_name)
        if issues:
            print(f"❌ Pull-before-push issues:")
            for issue in issues:
                print(f"   - {issue}")
            all_issues.extend(issues)
        else:
            print(f"✅ Pull-before-push strategy implemented")
        
        # Test 3: Analysis directory protection
        issues = check_analysis_directory_protection(filepath, workflow_name)
        if issues:
            print(f"❌ Analysis directory protection issues:")
            for issue in issues:
                print(f"   - {issue}")
            all_issues.extend(issues)
        else:
            print(f"✅ Analysis directory properly protected")
        
    except Exception as e:
        print(f"❌ Error testing workflow: {e}")
        all_issues.append(str(e))
    
    if not all_issues:
        print(f"✅ All checks passed")
    
    return all_issues


def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing analysis workflow concurrency controls...")
    print("=" * 70)
    
    # Workflows that update analysis/ directory
    workflow_files = [
        ('.github/workflows/code-quality.yml', 'code-quality.yml'),
        ('.github/workflows/repetition-detector.yml', 'repetition-detector.yml'),
        ('.github/workflows/automated-issue-clustering.yml', 'automated-issue-clustering.yml'),
        ('.github/workflows/design-decisions-documenter.yml', 'design-decisions-documenter.yml'),
        ('.github/workflows/architecture-evolution.yml', 'architecture-evolution.yml'),
    ]
    
    all_workflow_issues = {}
    
    for filepath, name in workflow_files:
        issues = test_workflow(filepath, name)
        if issues:
            all_workflow_issues[name] = issues
    
    # Cross-workflow tests
    print("\n" + "=" * 70)
    print("Cross-workflow consistency tests")
    print("-" * 70)
    
    consistency_issues = check_concurrency_group_consistency(workflow_files)
    if consistency_issues:
        print("❌ Concurrency group consistency issues:")
        for issue in consistency_issues:
            print(f"   - {issue}")
        all_workflow_issues['cross-workflow'] = consistency_issues
    else:
        print("✅ Concurrency groups are consistent")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Workflows tested: {len(workflow_files)}")
    print(f"Total issues found: {sum(len(issues) for issues in all_workflow_issues.values())}")
    
    if all_workflow_issues:
        print("\n❌ TESTS FAILED")
        print("\nIssues by workflow:")
        for workflow_name, issues in all_workflow_issues.items():
            print(f"\n{workflow_name}:")
            for issue in issues:
                print(f"  - {issue}")
        return 1
    else:
        print("\n✅ ALL TESTS PASSED")
        print("\nConcurrency controls are properly configured:")
        print("- Analysis workflows have concurrency groups")
        print("- Pull-before-push strategy is implemented")
        print("- Merge conflict resolution is in place")
        print("- Analysis directory is protected from race conditions")
        return 0


if __name__ == '__main__':
    sys.exit(main())
