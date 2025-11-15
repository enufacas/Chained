#!/usr/bin/env python3
"""
Test workflow auto-review integration

This test validates that the agent spawner workflows properly integrate
with the auto-review-merge workflow by triggering it after PR creation.
"""

import yaml
import sys
from pathlib import Path


def test_workflow_has_auto_review_trigger():
    """Verify workflows have auto-review trigger steps"""
    workflows = [
        '.github/workflows/agent-spawner.yml',
        '.github/workflows/learning-based-agent-spawner.yml',
        '.github/workflows/autonomous-pipeline.yml'
    ]
    
    for workflow_path in workflows:
        print(f"\n✅ Testing {workflow_path}...")
        
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Find the job that creates spawn PRs
        found_trigger = False
        found_wait = False
        jobs_with_triggers = []
        
        for job_name, job in workflow['jobs'].items():
            if 'steps' not in job:
                continue
                
            step_names = [step.get('name', '') for step in job['steps']]
            
            # Check for auto-review trigger step
            if any('Trigger Auto Review' in name for name in step_names):
                found_trigger = True
                jobs_with_triggers.append(job_name)
                print(f"  ✓ Found 'Trigger Auto Review and Merge' step in job '{job_name}'")
            
            # Check for wait step
            if any('Wait for PR to be merged' in name for name in step_names):
                found_wait = True
                print(f"  ✓ Found 'Wait for PR to be merged' step in job '{job_name}'")
        
        if not found_trigger:
            print(f"  ❌ ERROR: Missing 'Trigger Auto Review and Merge' step in {workflow_path}")
            return False
            
        if not found_wait:
            print(f"  ❌ ERROR: Missing 'Wait for PR to be merged' step in {workflow_path}")
            return False
        
        # For autonomous-pipeline, verify all merge jobs have the steps
        if 'autonomous-pipeline' in workflow_path:
            merge_jobs = [name for name in workflow['jobs'].keys() if 'merge' in name.lower()]
            if merge_jobs:
                print(f"  ℹ️  Merge jobs in autonomous-pipeline: {', '.join(merge_jobs)}")
                for merge_job in merge_jobs:
                    if merge_job not in jobs_with_triggers:
                        print(f"  ⚠️  Warning: Merge job '{merge_job}' missing auto-review trigger")
    
    return True


def test_workflow_syntax():
    """Verify workflow YAML syntax is valid"""
    workflows = [
        '.github/workflows/agent-spawner.yml',
        '.github/workflows/learning-based-agent-spawner.yml',
        '.github/workflows/autonomous-pipeline.yml'
    ]
    
    for workflow_path in workflows:
        print(f"\n✅ Validating syntax: {workflow_path}...")
        try:
            with open(workflow_path, 'r') as f:
                yaml.safe_load(f)
            print(f"  ✓ Valid YAML syntax")
        except yaml.YAMLError as e:
            print(f"  ❌ YAML syntax error: {e}")
            return False
    
    return True


def test_auto_review_workflow_dispatch():
    """Verify auto-review-merge workflow has workflow_dispatch trigger"""
    workflow_path = '.github/workflows/auto-review-merge.yml'
    print(f"\n✅ Testing {workflow_path}...")
    
    with open(workflow_path, 'r') as f:
        workflow = yaml.safe_load(f)
    
    # GitHub Actions workflows can have 'on' as true or as a dict
    if 'on' not in workflow and True not in workflow:
        print(f"  ❌ ERROR: auto-review-merge.yml missing 'on' trigger configuration")
        return False
    
    triggers = workflow.get('on', workflow.get(True, {}))
    
    if 'workflow_dispatch' not in triggers:
        print(f"  ❌ ERROR: auto-review-merge.yml missing workflow_dispatch trigger")
        return False
    
    print(f"  ✓ Has workflow_dispatch trigger")
    
    # Check if pr_number input exists
    dispatch = triggers['workflow_dispatch']
    if dispatch and 'inputs' in dispatch and 'pr_number' in dispatch['inputs']:
        print(f"  ✓ Has pr_number input parameter")
    else:
        print(f"  ℹ️  Note: pr_number input parameter optional (workflow can process all PRs)")
    
    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("WORKFLOW AUTO-REVIEW INTEGRATION TESTS")
    print("=" * 70)
    
    tests = [
        ("Workflow Syntax Validation", test_workflow_syntax),
        ("Auto-Review Trigger Steps", test_workflow_has_auto_review_trigger),
        ("Auto-Review Workflow Dispatch", test_auto_review_workflow_dispatch),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 70}")
        print(f"TEST: {test_name}")
        print(f"{'=' * 70}")
        
        try:
            if test_func():
                passed += 1
                print(f"\n✅ PASSED: {test_name}")
            else:
                failed += 1
                print(f"\n❌ FAILED: {test_name}")
        except Exception as e:
            failed += 1
            print(f"\n❌ FAILED: {test_name}")
            print(f"   Error: {e}")
    
    print(f"\n{'=' * 70}")
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print(f"{'=' * 70}\n")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
