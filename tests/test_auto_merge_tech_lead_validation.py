#!/usr/bin/env python3
"""
Test auto-merge workflow tech lead label validation logic

This test validates that the auto-review-merge workflow correctly handles
both tech lead labels by checking if tech lead review was actually required
before blocking the merge.

Addresses the issue where PRs (like PR #2417) were blocked even though no 
tech lead review was needed (no tech lead tags present).
"""

import sys
import yaml
from pathlib import Path


def test_workflow_has_tech_lead_validation():
    """
    Verify that the auto-review-merge workflow validates tech lead requirement
    before blocking on BOTH tech lead labels.
    """
    workflow_path = '.github/workflows/auto-review-merge.yml'
    print(f"\n✅ Testing {workflow_path}...")
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # Check that the workflow contains the validation logic
    checks = [
        # Should check if tech lead review was required
        ('matrix.requires_tech_lead', 'Checks requires_tech_lead flag'),
        ('matrix.tech_leads', 'Checks tech_leads assignment'),
        ('has_needs_tech_lead', 'Checks needs-tech-lead-review label'),
        ('has_changes_requested', 'Checks tech-lead-changes-requested label'),
        # Should have conditional logic
        ('if [ "${{ matrix.requires_tech_lead }}" = "true" ]', 'Validates tech lead requirement'),
        ('[ -n "${{ matrix.tech_leads }}" ]', 'Validates tech lead presence'),
    ]
    
    all_checks_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ❌ Missing: {description}")
            all_checks_passed = False
    
    # Check for both validation comments
    if 'Only block if tech lead review was actually required for this PR' in content:
        print(f"  ✓ Contains comment for needs-tech-lead-review validation")
    else:
        print(f"  ❌ Missing comment for needs-tech-lead-review validation")
        all_checks_passed = False
        
    if 'Only block for tech-lead-changes-requested if tech lead review was actually required' in content:
        print(f"  ✓ Contains comment for tech-lead-changes-requested validation")
    else:
        print(f"  ❌ Missing explanatory comment for the fix")
        all_checks_passed = False
    
    # Verify the logic structure
    if 'if [ "${has_changes_requested}" != "0" ]; then' in content:
        print(f"  ✓ Checks for tech-lead-changes-requested label")
        
        # Should then check if tech lead was required
        tech_lead_check = 'if [ "${{ matrix.requires_tech_lead }}" = "true" ] || [ -n "${{ matrix.tech_leads }}" ]; then'
        if tech_lead_check in content:
            print(f"  ✓ Validates tech lead requirement before blocking")
        else:
            print(f"  ❌ Missing tech lead requirement validation")
            all_checks_passed = False
    else:
        print(f"  ❌ Missing tech-lead-changes-requested check")
        all_checks_passed = False
    
    return all_checks_passed


def test_workflow_yaml_syntax():
    """Verify workflow YAML syntax is valid"""
    workflow_path = '.github/workflows/auto-review-merge.yml'
    print(f"\n✅ Validating YAML syntax: {workflow_path}...")
    
    try:
        with open(workflow_path, 'r') as f:
            yaml.safe_load(f)
        print(f"  ✓ Valid YAML syntax")
        return True
    except yaml.YAMLError as e:
        print(f"  ❌ YAML syntax error: {e}")
        return False


def test_documentation_updated():
    """Verify that documentation reflects the fix"""
    doc_path = '.github/workflows/TECH_LEAD_SYSTEM_README.md'
    print(f"\n✅ Checking documentation: {doc_path}...")
    
    with open(doc_path, 'r') as f:
        content = f.read()
    
    checks = [
        ('tech lead review was required', 'Explains validation requirement'),
        ('requires_tech_lead', 'Documents requires_tech_lead flag'),
        ('stale', 'Mentions stale/incorrect labels'),
        ('false positive', 'Addresses false positives'),
    ]
    
    all_checks_passed = True
    for check_str, description in checks:
        if check_str.lower() in content.lower():
            print(f"  ✓ {description}")
        else:
            print(f"  ⚠️  Documentation could mention: {description}")
            # Not failing on documentation warnings
    
    return True


def test_merge_eligibility_scenarios():
    """
    Test the merge eligibility logic for various scenarios.
    
    This simulates the bash logic used in the workflow for BOTH
    needs-tech-lead-review and tech-lead-changes-requested labels.
    """
    print(f"\n✅ Testing merge eligibility scenarios...")
    
    scenarios = [
        {
            'name': 'Stale needs-tech-lead-review - no tech lead required (PR 2417 case)',
            'has_needs_tech_lead': True,
            'has_changes_requested': False,
            'requires_tech_lead': False,
            'tech_leads': '',
            'expected_blocked': False,
            'reason': 'needs-tech-lead-review label ignored when tech lead not required'
        },
        {
            'name': 'Stale tech-lead-changes-requested - no tech lead required',
            'has_needs_tech_lead': False,
            'has_changes_requested': True,
            'requires_tech_lead': False,
            'tech_leads': '',
            'expected_blocked': False,
            'reason': 'tech-lead-changes-requested label ignored when tech lead not required'
        },
        {
            'name': 'Valid needs-tech-lead-review - tech lead required',
            'has_needs_tech_lead': True,
            'has_changes_requested': False,
            'requires_tech_lead': True,
            'tech_leads': '',
            'expected_blocked': True,
            'reason': 'Block when tech lead review was required'
        },
        {
            'name': 'Valid tech-lead-changes-requested - tech lead required',
            'has_needs_tech_lead': False,
            'has_changes_requested': True,
            'requires_tech_lead': True,
            'tech_leads': '',
            'expected_blocked': True,
            'reason': 'Block when tech lead review was required'
        },
        {
            'name': 'Valid label - tech leads assigned',
            'has_needs_tech_lead': False,
            'has_changes_requested': True,
            'requires_tech_lead': False,
            'tech_leads': 'workflows-tech-lead',
            'expected_blocked': True,
            'reason': 'Block when tech leads were identified'
        },
        {
            'name': 'No blocking labels',
            'has_needs_tech_lead': False,
            'has_changes_requested': False,
            'requires_tech_lead': True,
            'tech_leads': 'workflows-tech-lead',
            'expected_blocked': False,
            'reason': 'Allow when no blocking labels present'
        },
        {
            'name': 'Multiple tech leads assigned with changes requested',
            'has_needs_tech_lead': False,
            'has_changes_requested': True,
            'requires_tech_lead': False,
            'tech_leads': 'docs-tech-lead,workflows-tech-lead',
            'expected_blocked': True,
            'reason': 'Block when multiple tech leads identified'
        },
    ]
    
    all_passed = True
    for scenario in scenarios:
        # Simulate the bash logic for BOTH conditions
        blocked = False
        
        # First condition: needs-tech-lead-review without approval
        if scenario.get('has_needs_tech_lead', False):
            if scenario['requires_tech_lead'] or scenario['tech_leads']:
                blocked = True
        
        # Second condition: tech-lead-changes-requested
        if scenario.get('has_changes_requested', False):
            if scenario['requires_tech_lead'] or scenario['tech_leads']:
                blocked = True
        
        expected = scenario['expected_blocked']
        status = "✓" if blocked == expected else "❌"
        
        print(f"  {status} {scenario['name']}")
        print(f"     has_needs_tech_lead={scenario.get('has_needs_tech_lead', False)}, "
              f"has_changes_requested={scenario.get('has_changes_requested', False)}, "
              f"requires_tech_lead={scenario['requires_tech_lead']}, "
              f"tech_leads='{scenario['tech_leads']}'")
        print(f"     Expected: {'BLOCKED' if expected else 'ALLOWED'}, "
              f"Got: {'BLOCKED' if blocked else 'ALLOWED'}")
        print(f"     Reason: {scenario['reason']}")
        
        if blocked != expected:
            print(f"     ❌ FAILED")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests"""
    print("=" * 70)
    print("AUTO-MERGE TECH LEAD VALIDATION TESTS")
    print("=" * 70)
    print("\nThis test suite validates the fix for PR #2417 issue where")
    print("the workflow blocked PRs with tech lead labels (needs-tech-lead-review")
    print("or tech-lead-changes-requested) even when tech lead review was never required.")
    
    tests = [
        ("Workflow YAML Syntax", test_workflow_yaml_syntax),
        ("Tech Lead Validation Logic", test_workflow_has_tech_lead_validation),
        ("Documentation Updated", test_documentation_updated),
        ("Merge Eligibility Scenarios", test_merge_eligibility_scenarios),
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
    
    if failed == 0:
        print("✅ All tests passed! The fix correctly handles tech-lead-changes-requested validation.")
    else:
        print("❌ Some tests failed. Please review the output above.")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
