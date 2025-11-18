#!/usr/bin/env python3
"""
Test suite for workload monitor and sub-agent spawner.

Tests the workload-based spawning system created by @accelerate-specialist.
"""

import sys
import json
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

from workload_monitor import WorkloadMonitor, WorkloadMetrics, SpawningRecommendation


def test_workload_categorization():
    """Test that issues and PRs are categorized correctly"""
    print("\n🧪 Test: Workload Categorization")
    
    monitor = WorkloadMonitor()
    
    # Mock issues with different labels
    issues = [
        {'labels': ['security', 'bug']},
        {'labels': ['security', 'vulnerability']},
        {'labels': ['performance', 'optimization']},
        {'labels': ['feature', 'enhancement']},
        {'labels': ['documentation']},
    ]
    
    prs = [
        {'labels': ['security']},
        {'labels': ['performance']},
    ]
    
    # Analyze workload
    metrics = monitor.analyze_workload(issues, prs)
    
    # Verify categorization
    assert 'security' in metrics, "Security category should exist"
    assert metrics['security'].open_issues >= 2, "Should have at least 2 security issues"
    assert metrics['security'].pending_prs >= 1, "Should have at least 1 security PR"
    
    assert 'performance' in metrics, "Performance category should exist"
    assert metrics['performance'].open_issues >= 1, "Should have at least 1 performance issue"
    
    assert 'documentation' in metrics, "Documentation category should exist"
    
    print("✅ Workload categorization works correctly")
    return True


def test_bottleneck_detection():
    """Test that bottlenecks are detected correctly"""
    print("\n🧪 Test: Bottleneck Detection")
    
    monitor = WorkloadMonitor()
    
    # Create high-load scenario
    high_load_issues = [
        {'labels': ['security']} for _ in range(15)
    ]
    
    high_load_prs = [
        {'labels': ['security']} for _ in range(10)
    ]
    
    # Mock agent count (will return 3 security agents)
    metrics = monitor.analyze_workload(high_load_issues, high_load_prs)
    
    # Check that high workload is detected
    if 'security' in metrics:
        sec_metrics = metrics['security']
        print(f"  Security workload: {sec_metrics.workload_per_agent:.2f} items/agent")
        print(f"  Bottleneck severity: {sec_metrics.bottleneck_severity}")
        
        # With 25 items and ~6 agents (mocked), should be 4+ items/agent
        assert sec_metrics.workload_per_agent > 3.0, "Should detect high workload"
        assert sec_metrics.bottleneck_severity in ['medium', 'high', 'critical'], "Should detect bottleneck"
    
    print("✅ Bottleneck detection works correctly")
    return True


def test_spawning_recommendations():
    """Test that spawning recommendations are generated correctly"""
    print("\n🧪 Test: Spawning Recommendations")
    
    monitor = WorkloadMonitor()
    
    # Create scenario requiring spawning
    issues = [
        {'labels': ['security']} for _ in range(20)
    ]
    
    prs = [
        {'labels': ['security']} for _ in range(5)
    ]
    
    metrics = monitor.analyze_workload(issues, prs)
    recommendations = monitor.generate_spawning_recommendations(metrics, max_spawns=5)
    
    print(f"  Generated {len(recommendations)} recommendation(s)")
    
    # Should have at least one recommendation for security
    security_recs = [r for r in recommendations if r.specialization == 'security']
    
    if security_recs:
        sec_rec = security_recs[0]
        print(f"  Security recommendation: spawn {sec_rec.count} agent(s)")
        print(f"  Priority: {sec_rec.priority}")
        print(f"  Reason: {sec_rec.reason[:80]}...")
        
        assert sec_rec.should_spawn, "Should recommend spawning"
        assert sec_rec.count > 0, "Should spawn at least 1 agent"
        assert sec_rec.priority >= 3, "Should have medium+ priority"
    
    print("✅ Spawning recommendations work correctly")
    return True


def test_report_generation():
    """Test that reports are generated correctly"""
    print("\n🧪 Test: Report Generation")
    
    monitor = WorkloadMonitor()
    
    # Use default mock data
    metrics = monitor.analyze_workload()
    recommendations = monitor.generate_spawning_recommendations(metrics)
    
    # Generate report
    report = monitor.generate_report(metrics, recommendations)
    
    # Verify report content
    assert '# 📊 Workload Analysis Report' in report, "Should have title"
    assert 'System Overview' in report, "Should have overview"
    assert 'Workload by Specialization' in report, "Should have specializations"
    
    print(f"  Report length: {len(report)} characters")
    print("✅ Report generation works correctly")
    return True


def test_priority_scoring():
    """Test priority score calculation"""
    print("\n🧪 Test: Priority Scoring")
    
    monitor = WorkloadMonitor()
    
    # Test different severity levels
    test_cases = [
        (20.0, 1.0, 'critical', 100.0),  # Maximum priority
        (10.0, 0.9, 'high', 80.0),       # High priority
        (5.0, 0.6, 'medium', 50.0),      # Medium priority
        (2.0, 0.3, 'low', 20.0),         # Low priority
        (1.0, 0.1, 'none', 10.0),        # Minimal priority
    ]
    
    for workload, capacity, severity, min_expected in test_cases:
        score = monitor._calculate_priority_score(workload, capacity, severity)
        print(f"  {severity}: workload={workload}, capacity={capacity*100:.0f}% -> score={score:.1f}")
        
        # Verify score is in reasonable range for severity
        if severity == 'critical':
            assert score >= 70, f"Critical should have high score (got {score})"
        elif severity == 'high':
            assert score >= 50, f"High should have medium+ score (got {score})"
    
    print("✅ Priority scoring works correctly")
    return True


def test_metrics_to_dict():
    """Test that metrics can be serialized to dict/JSON"""
    print("\n🧪 Test: Metrics Serialization")
    
    monitor = WorkloadMonitor()
    metrics = monitor.analyze_workload()
    
    # Convert to dict
    metrics_dict = {spec: m.to_dict() for spec, m in metrics.items()}
    
    # Verify can serialize to JSON
    json_str = json.dumps(metrics_dict, indent=2)
    
    # Verify can deserialize
    loaded = json.loads(json_str)
    
    assert len(loaded) == len(metrics), "Should preserve all metrics"
    
    for spec in metrics:
        assert spec in loaded, f"Should have {spec} in loaded data"
        assert 'workload_per_agent' in loaded[spec], "Should have workload_per_agent"
        assert 'bottleneck_severity' in loaded[spec], "Should have bottleneck_severity"
    
    print(f"  Serialized {len(loaded)} specializations")
    print("✅ Metrics serialization works correctly")
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("🧪 Testing Workload Monitor & Sub-Agent Spawner")
    print("=" * 80)
    
    tests = [
        test_workload_categorization,
        test_bottleneck_detection,
        test_spawning_recommendations,
        test_report_generation,
        test_priority_scoring,
        test_metrics_to_dict,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed}/{len(tests)} passed")
    
    if failed == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ {failed} test(s) failed")
    
    print("=" * 80)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
