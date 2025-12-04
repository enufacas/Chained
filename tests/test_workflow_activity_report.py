#!/usr/bin/env python3
"""
Tests for the Workflow Activity Report Generator.
Created by @create-botter

Tests the core functionality of the workflow activity reporter,
including archival score calculation and report generation.
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))


# Cache the loaded module to avoid repeated loading
_cached_module = None


def load_workflow_activity_module():
    """
    Helper function to load the workflow-activity-report module.
    Uses caching to avoid repeated loading across tests.
    """
    global _cached_module
    if _cached_module is not None:
        return _cached_module
    
    from importlib.util import spec_from_loader, module_from_spec
    from importlib.machinery import SourceFileLoader
    
    # Import the module with hyphens in name
    spec = spec_from_loader(
        'workflow_activity_report',
        SourceFileLoader('workflow_activity_report', 
                        str(Path(__file__).parent.parent / 'tools' / 'workflow-activity-report.py'))
    )
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    _cached_module = module
    return module


def test_archival_score_calculation():
    """Test that archival scores are calculated correctly."""
    print("\n🧪 Testing archival score calculation")
    print("-" * 60)
    
    module = load_workflow_activity_module()
    
    reporter = module.WorkflowActivityReporter(
        owner='test',
        repo='repo',
        min_inactive_days=30
    )
    
    test_cases = [
        {
            'name': 'Disabled workflow',
            'params': {
                'state': 'disabled',
                'total_runs': 100,
                'days_since_last_run': 5,
                'success_rate': 90.0,
                'trigger_types': ['push'],
                'avg_runs_per_week': 10.0
            },
            'expected_min_score': 30,  # Should have high score due to disabled state
        },
        {
            'name': 'Never run workflow',
            'params': {
                'state': 'active',
                'total_runs': 0,
                'days_since_last_run': None,
                'success_rate': 0.0,
                'trigger_types': [],
                'avg_runs_per_week': 0.0
            },
            'expected_min_score': 50,  # Should have very high score
        },
        {
            'name': 'Inactive 90+ days',
            'params': {
                'state': 'active',
                'total_runs': 50,
                'days_since_last_run': 100,
                'success_rate': 80.0,
                'trigger_types': ['schedule'],
                'avg_runs_per_week': 0.05
            },
            'expected_min_score': 35,  # High score due to inactivity
        },
        {
            'name': 'Active healthy workflow',
            'params': {
                'state': 'active',
                'total_runs': 500,
                'days_since_last_run': 1,
                'success_rate': 95.0,
                'trigger_types': ['push', 'pull_request'],
                'avg_runs_per_week': 20.0
            },
            'expected_min_score': 0,
            'expected_max_score': 10,  # Should have low score
        },
        {
            'name': 'Low success rate',
            'params': {
                'state': 'active',
                'total_runs': 100,
                'days_since_last_run': 2,
                'success_rate': 15.0,
                'trigger_types': ['schedule'],
                'avg_runs_per_week': 5.0
            },
            'expected_min_score': 15,  # Score from low success rate
        },
        {
            'name': 'Manual-only inactive',
            'params': {
                'state': 'active',
                'total_runs': 10,
                'days_since_last_run': 70,
                'success_rate': 80.0,
                'trigger_types': ['workflow_dispatch'],
                'avg_runs_per_week': 0.1
            },
            'expected_min_score': 25,  # Score from inactivity + manual-only
        },
    ]
    
    passed = 0
    failed = 0
    
    for tc in test_cases:
        score, reasons = reporter._calculate_archival_score(**tc['params'])
        
        # Check minimum expected score
        min_ok = score >= tc.get('expected_min_score', 0)
        max_ok = score <= tc.get('expected_max_score', 100)
        
        if min_ok and max_ok:
            print(f"✅ PASSED: {tc['name']} (score: {score:.1f})")
            passed += 1
        else:
            print(f"❌ FAILED: {tc['name']}")
            print(f"   Score: {score:.1f}")
            print(f"   Expected min: {tc.get('expected_min_score', 0)}, max: {tc.get('expected_max_score', 100)}")
            print(f"   Reasons: {reasons}")
            failed += 1
    
    return failed == 0


def test_workflow_activity_dataclass():
    """Test that WorkflowActivity dataclass works correctly."""
    print("\n🧪 Testing WorkflowActivity dataclass")
    print("-" * 60)
    
    module = load_workflow_activity_module()
    
    try:
        activity = module.WorkflowActivity(
            workflow_id=12345,
            name="Test Workflow",
            path=".github/workflows/test.yml",
            state="active",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-06-01T00:00:00Z",
            total_runs=100,
            last_run_date="2024-06-01T00:00:00Z",
            days_since_last_run=30,
            success_count=90,
            failure_count=10,
            skipped_count=0,
            cancelled_count=0,
            success_rate=90.0,
            trigger_types=["push", "pull_request"],
            avg_runs_per_day=0.5,
            avg_runs_per_week=3.5,
            archival_score=15.0,
            archival_reasons=["Low usage"]
        )
        
        # Test conversion to dict
        data = module.asdict(activity)
        
        if data['workflow_id'] != 12345:
            print(f"❌ FAILED: workflow_id mismatch")
            return False
        
        if data['name'] != "Test Workflow":
            print(f"❌ FAILED: name mismatch")
            return False
        
        if data['archival_score'] != 15.0:
            print(f"❌ FAILED: archival_score mismatch")
            return False
        
        print("✅ PASSED: WorkflowActivity dataclass works correctly")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Exception - {e}")
        return False


def test_report_generation_mock():
    """Test report generation with mock data."""
    print("\n🧪 Testing report generation with mock data")
    print("-" * 60)
    
    module = load_workflow_activity_module()
    
    reporter = module.WorkflowActivityReporter(
        owner='test',
        repo='repo',
        min_inactive_days=30
    )
    
    # Add mock workflows
    reporter.workflows = [
        module.WorkflowActivity(
            workflow_id=1,
            name="Active Workflow",
            path=".github/workflows/active.yml",
            state="active",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-06-01T00:00:00Z",
            total_runs=500,
            last_run_date="2024-11-20T00:00:00Z",
            days_since_last_run=4,
            success_count=450,
            failure_count=50,
            skipped_count=0,
            cancelled_count=0,
            success_rate=90.0,
            trigger_types=["push", "pull_request"],
            avg_runs_per_day=1.5,
            avg_runs_per_week=10.5,
            archival_score=5.0,
            archival_reasons=[]
        ),
        module.WorkflowActivity(
            workflow_id=2,
            name="Inactive Workflow",
            path=".github/workflows/inactive.yml",
            state="active",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-06-01T00:00:00Z",
            total_runs=10,
            last_run_date="2024-01-01T00:00:00Z",
            days_since_last_run=328,
            success_count=8,
            failure_count=2,
            skipped_count=0,
            cancelled_count=0,
            success_rate=80.0,
            trigger_types=["schedule"],
            avg_runs_per_day=0.01,
            avg_runs_per_week=0.07,
            archival_score=75.0,
            archival_reasons=["No runs in 328 days (90+ days)", "Low usage (10 total runs)"]
        ),
        module.WorkflowActivity(
            workflow_id=3,
            name="Disabled Workflow",
            path=".github/workflows/disabled.yml",
            state="disabled",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-06-01T00:00:00Z",
            total_runs=0,
            last_run_date=None,
            days_since_last_run=None,
            success_count=0,
            failure_count=0,
            skipped_count=0,
            cancelled_count=0,
            success_rate=0.0,
            trigger_types=[],
            avg_runs_per_day=0.0,
            avg_runs_per_week=0.0,
            archival_score=90.0,
            archival_reasons=["Workflow is disabled", "Never been run", "Zero total runs"]
        ),
    ]
    
    # Test text report generation
    try:
        text_report = reporter.generate_text_report(top_n=10)
        
        # Verify key elements are in the report
        checks = [
            ('Header', 'WORKFLOW ACTIVITY REPORT' in text_report),
            ('Summary section', 'SUMMARY STATISTICS' in text_report),
            ('Total workflows', 'Total Workflows:' in text_report and '3' in text_report),
            ('Active Workflow name', 'Active Workflow' in text_report),
            ('Inactive Workflow name', 'Inactive Workflow' in text_report),
            ('Archival candidates section', 'ARCHIVAL CANDIDATES' in text_report),
            ('Recommendations', 'ARCHIVAL RECOMMENDATIONS' in text_report),
        ]
        
        all_passed = True
        for check_name, result in checks:
            if result:
                print(f"  ✓ {check_name}")
            else:
                print(f"  ✗ {check_name} - NOT FOUND")
                all_passed = False
        
        if all_passed:
            print("✅ PASSED: Text report generation")
        else:
            print("❌ FAILED: Text report generation")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Text report generation - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test JSON report generation
    try:
        json_report = reporter.generate_json_report()
        
        # Verify key elements
        checks = [
            ('metadata exists', 'metadata' in json_report),
            ('owner correct', json_report.get('metadata', {}).get('owner') == 'test'),
            ('summary exists', 'summary' in json_report),
            ('workflows list', len(json_report.get('workflows', [])) == 3),
            ('archival_candidates', 'archival_candidates' in json_report),
            ('high candidates', len(json_report.get('archival_candidates', {}).get('high', [])) >= 1),
        ]
        
        all_passed = True
        for check_name, result in checks:
            if result:
                print(f"  ✓ {check_name}")
            else:
                print(f"  ✗ {check_name}")
                all_passed = False
        
        if all_passed:
            print("✅ PASSED: JSON report generation")
        else:
            print("❌ FAILED: JSON report generation")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: JSON report generation - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_markdown_report_generation():
    """Test markdown report generation with mock data."""
    print("\n🧪 Testing markdown report generation")
    print("-" * 60)
    
    module = load_workflow_activity_module()
    
    reporter = module.WorkflowActivityReporter(
        owner='test',
        repo='repo',
        min_inactive_days=30
    )
    
    # Add mock workflows
    reporter.workflows = [
        module.WorkflowActivity(
            workflow_id=1,
            name="Active Workflow",
            path=".github/workflows/active.yml",
            state="active",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-06-01T00:00:00Z",
            total_runs=500,
            last_run_date="2024-11-20T00:00:00Z",
            days_since_last_run=4,
            success_count=450,
            failure_count=50,
            skipped_count=0,
            cancelled_count=0,
            success_rate=90.0,
            trigger_types=["push", "pull_request"],
            avg_runs_per_day=1.5,
            avg_runs_per_week=10.5,
            archival_score=5.0,
            archival_reasons=[]
        ),
        module.WorkflowActivity(
            workflow_id=2,
            name="Inactive Workflow",
            path=".github/workflows/inactive.yml",
            state="active",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-06-01T00:00:00Z",
            total_runs=10,
            last_run_date="2024-01-01T00:00:00Z",
            days_since_last_run=328,
            success_count=8,
            failure_count=2,
            skipped_count=0,
            cancelled_count=0,
            success_rate=80.0,
            trigger_types=["schedule"],
            avg_runs_per_day=0.01,
            avg_runs_per_week=0.07,
            archival_score=75.0,
            archival_reasons=["No runs in 328 days (90+ days)", "Low usage (10 total runs)"]
        ),
    ]
    
    try:
        markdown_report = reporter.generate_markdown_report(top_n=10)
        
        # Verify key markdown elements
        checks = [
            ('Header', '# 📊 Workflow Activity Report' in markdown_report),
            ('Repository', '`test/repo`' in markdown_report),
            ('Summary table', '| Metric | Value |' in markdown_report),
            ('Archival candidates table', '| # | Score | Workflow Name |' in markdown_report),
            ('Active Workflow in table', 'Active Workflow' in markdown_report),
            ('Recommendations section', '## 💡 Archival Recommendations' in markdown_report),
            ('Score range table', '| ≥ 70 |' in markdown_report),
            ('Created by attribution', '@create-botter' in markdown_report),
        ]
        
        all_passed = True
        for check_name, result in checks:
            if result:
                print(f"  ✓ {check_name}")
            else:
                print(f"  ✗ {check_name}")
                all_passed = False
        
        if all_passed:
            print("✅ PASSED: Markdown report generation")
            return True
        else:
            print("❌ FAILED: Markdown report generation")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Markdown report generation - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_repo_info():
    """Test repo info extraction from git remote."""
    print("\n🧪 Testing repo info extraction")
    print("-" * 60)
    
    module = load_workflow_activity_module()
    
    try:
        owner, repo = module.get_repo_info()
        
        # In the Chained repo, this should return enufacas/Chained
        if owner and repo:
            print(f"  Detected: {owner}/{repo}")
            print("✅ PASSED: Repo info extraction works")
            return True
        else:
            print("⚠️ WARNING: Could not detect repo info (may be expected in some environments)")
            return True  # Not a failure, just not available
            
    except Exception as e:
        print(f"❌ FAILED: Exception - {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Workflow Activity Report Tests")
    print("   Created by @create-botter")
    print("=" * 60)
    
    # Change to repo root
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)
    
    tests = [
        ("Archival Score Calculation", test_archival_score_calculation),
        ("WorkflowActivity Dataclass", test_workflow_activity_dataclass),
        ("Report Generation (Mock)", test_report_generation_mock),
        ("Markdown Report Generation", test_markdown_report_generation),
        ("Repo Info Extraction", test_get_repo_info),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
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
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
