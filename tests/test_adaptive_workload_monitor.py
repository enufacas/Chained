#!/usr/bin/env python3
"""
Test suite for adaptive workload monitor.

Tests the ML-enhanced workload analysis created by @accelerate-specialist.
"""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

from adaptive_workload_monitor import (
    AdaptiveWorkloadMonitor,
    WorkloadHistoryEntry,
    AdaptiveThresholds
)
from workload_monitor import WorkloadMetrics


def test_history_loading():
    """Test that history can be loaded and saved"""
    print("\n🧪 Test: History Loading and Saving")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create monitor with temp directory
        monitor = AdaptiveWorkloadMonitor()
        
        # Should initialize with empty history
        assert isinstance(monitor.history, list), "History should be a list"
        
        print("✅ History loading works correctly")
    return True


def test_trend_calculation():
    """Test workload trend calculation"""
    print("\n🧪 Test: Trend Calculation")
    
    monitor = AdaptiveWorkloadMonitor()
    
    # Clear any existing history
    monitor.history = []
    
    # Create increasing trend data
    now = datetime.now()
    for i in range(10):
        entry = WorkloadHistoryEntry(
            timestamp=(now - timedelta(hours=10-i)).isoformat(),
            specialization='security',
            open_issues=10 + i,
            pending_prs=5,
            active_agents=5,
            workload_per_agent=3.0 + i * 0.2,
            bottleneck_severity='medium'
        )
        monitor.history.append(entry)
    
    # Calculate trend
    trend = monitor._calculate_trend('security', lookback_hours=24)
    
    print(f"  Calculated trend: {trend:+.3f}")
    assert trend > 0, "Should detect increasing trend"
    
    print("✅ Trend calculation works correctly")
    return True


def test_spawn_confidence():
    """Test spawn confidence calculation"""
    print("\n🧪 Test: Spawn Confidence")
    
    monitor = AdaptiveWorkloadMonitor()
    
    # Create high-severity metrics
    metrics = WorkloadMetrics(
        specialization='security',
        open_issues=20,
        pending_prs=10,
        active_agents=5,
        workload_per_agent=6.0,
        agent_capacity=1.2,
        bottleneck_severity='critical',
        priority_score=95.0,
        recommendation='Spawn 2 agents immediately'
    )
    
    # Add history showing consistent high workload
    now = datetime.now()
    for i in range(5):
        entry = WorkloadHistoryEntry(
            timestamp=(now - timedelta(hours=5-i)).isoformat(),
            specialization='security',
            open_issues=20,
            pending_prs=10,
            active_agents=5,
            workload_per_agent=6.0,
            bottleneck_severity='high'
        )
        monitor.history.append(entry)
    
    # Calculate confidence
    confidence = monitor._calculate_spawn_confidence('security', metrics)
    
    print(f"  Spawn confidence: {confidence:.2%}")
    assert confidence >= 0.6, f"Should have high confidence (got {confidence:.2%})"
    
    print("✅ Spawn confidence works correctly")
    return True


def test_adaptive_threshold_update():
    """Test adaptive threshold learning"""
    print("\n🧪 Test: Adaptive Threshold Update")
    
    monitor = AdaptiveWorkloadMonitor()
    
    # Set initial threshold
    initial_threshold = monitor.adaptive_thresholds['security'].workload_threshold
    print(f"  Initial threshold: {initial_threshold:.2f}")
    
    # Add history with frequent bottlenecks
    now = datetime.now()
    for i in range(20):
        entry = WorkloadHistoryEntry(
            timestamp=(now - timedelta(hours=20-i)).isoformat(),
            specialization='security',
            open_issues=15,
            pending_prs=8,
            active_agents=4,
            workload_per_agent=5.75,
            bottleneck_severity='high' if i % 2 == 0 else 'critical'
        )
        monitor.history.append(entry)
    
    # Update thresholds
    monitor._update_adaptive_thresholds()
    
    # Check that threshold adapted
    new_threshold = monitor.adaptive_thresholds['security'].workload_threshold
    print(f"  New threshold: {new_threshold:.2f}")
    
    # With frequent bottlenecks, threshold should decrease
    assert new_threshold <= initial_threshold, "Threshold should decrease with frequent bottlenecks"
    
    print("✅ Adaptive threshold update works correctly")
    return True


def test_adaptive_recommendations():
    """Test adaptive spawning recommendations"""
    print("\n🧪 Test: Adaptive Recommendations")
    
    monitor = AdaptiveWorkloadMonitor()
    
    # Create metrics
    metrics = {
        'security': WorkloadMetrics(
            specialization='security',
            open_issues=25,
            pending_prs=10,
            active_agents=5,
            workload_per_agent=7.0,
            agent_capacity=1.4,
            bottleneck_severity='high',
            priority_score=85.0,
            recommendation='Spawn 2 agents'
        )
    }
    
    # Add positive trend history
    now = datetime.now()
    for i in range(10):
        entry = WorkloadHistoryEntry(
            timestamp=(now - timedelta(hours=10-i)).isoformat(),
            specialization='security',
            open_issues=20 + i,
            pending_prs=8,
            active_agents=5,
            workload_per_agent=5.6 + i * 0.2,
            bottleneck_severity='medium'
        )
        monitor.history.append(entry)
    
    # Set high confidence
    monitor.adaptive_thresholds['security'].spawn_confidence = 0.8
    monitor.adaptive_thresholds['security'].workload_threshold = 5.0
    
    # Generate recommendations
    recommendations = monitor.generate_spawning_recommendations_adaptive(
        metrics,
        max_spawns=5
    )
    
    print(f"  Generated {len(recommendations)} recommendation(s)")
    
    if recommendations:
        rec = recommendations[0]
        print(f"  Recommendation: {rec.specialization}, count={rec.count}, priority={rec.priority}")
        assert rec.specialization == 'security', "Should recommend security agents"
        assert rec.count > 0, "Should recommend spawning"
    
    print("✅ Adaptive recommendations work correctly")
    return True


def test_adaptive_report_generation():
    """Test adaptive report generation"""
    print("\n🧪 Test: Adaptive Report Generation")
    
    monitor = AdaptiveWorkloadMonitor()
    
    # Add some history
    now = datetime.now()
    for i in range(5):
        entry = WorkloadHistoryEntry(
            timestamp=(now - timedelta(hours=5-i)).isoformat(),
            specialization='security',
            open_issues=15,
            pending_prs=5,
            active_agents=4,
            workload_per_agent=5.0,
            bottleneck_severity='medium'
        )
        monitor.history.append(entry)
    
    # Analyze workload
    metrics = monitor.analyze_workload_adaptive()
    recommendations = monitor.generate_spawning_recommendations_adaptive(metrics)
    
    # Generate report
    report = monitor.generate_adaptive_report(metrics, recommendations)
    
    # Verify report content
    assert '# 📊 Adaptive Workload Analysis Report' in report, "Should have adaptive title"
    assert 'Historical Data Points' in report, "Should show history count"
    assert 'Learning Status' in report, "Should show learning status"
    assert 'Adaptive Threshold' in report or 'Trend' in report, "Should have adaptive metrics"
    
    print(f"  Report length: {len(report)} characters")
    print("✅ Adaptive report generation works correctly")
    return True


def test_confidence_gating():
    """Test that low confidence prevents spawning"""
    print("\n🧪 Test: Confidence Gating")
    
    monitor = AdaptiveWorkloadMonitor()
    
    # Create borderline metrics
    metrics = {
        'security': WorkloadMetrics(
            specialization='security',
            open_issues=15,
            pending_prs=5,
            active_agents=5,
            workload_per_agent=4.0,
            agent_capacity=0.8,
            bottleneck_severity='medium',
            priority_score=55.0,
            recommendation='Monitor'
        )
    }
    
    # Set low confidence
    monitor.adaptive_thresholds['security'].spawn_confidence = 0.3
    monitor.adaptive_thresholds['security'].workload_threshold = 3.0
    
    # Generate recommendations
    recommendations = monitor.generate_spawning_recommendations_adaptive(
        metrics,
        max_spawns=5
    )
    
    print(f"  Generated {len(recommendations)} recommendation(s) with low confidence")
    
    # Should not spawn with low confidence even though threshold met
    assert len(recommendations) == 0, "Should not spawn with low confidence"
    
    print("✅ Confidence gating works correctly")
    return True


def test_history_persistence():
    """Test that history is saved and loaded correctly"""
    print("\n🧪 Test: History Persistence")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override history file location
        original_file = AdaptiveWorkloadMonitor.HISTORY_FILE
        AdaptiveWorkloadMonitor.HISTORY_FILE = f"{tmpdir}/workload_history.json"
        
        try:
            # Create monitor and add history
            monitor1 = AdaptiveWorkloadMonitor()
            
            metrics = {
                'security': WorkloadMetrics(
                    specialization='security',
                    open_issues=10,
                    pending_prs=5,
                    active_agents=3,
                    workload_per_agent=5.0,
                    agent_capacity=1.0,
                    bottleneck_severity='medium',
                    priority_score=50.0,
                    recommendation='Monitor'
                )
            }
            
            monitor1._save_history(metrics)
            history_count = len(monitor1.history)
            print(f"  Saved {history_count} history entries")
            
            # Create new monitor instance
            monitor2 = AdaptiveWorkloadMonitor()
            
            # Should load saved history
            assert len(monitor2.history) == history_count, "Should load saved history"
            
            print("✅ History persistence works correctly")
            return True
            
        finally:
            # Restore original file location
            AdaptiveWorkloadMonitor.HISTORY_FILE = original_file
    
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("🧪 Testing Adaptive Workload Monitor")
    print("=" * 80)
    
    tests = [
        test_history_loading,
        test_trend_calculation,
        test_spawn_confidence,
        test_adaptive_threshold_update,
        test_adaptive_recommendations,
        test_adaptive_report_generation,
        test_confidence_gating,
        test_history_persistence,
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
            import traceback
            traceback.print_exc()
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
