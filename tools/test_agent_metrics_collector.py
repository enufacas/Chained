#!/usr/bin/env python3
"""
Comprehensive tests for the Agent Performance Metrics Collector

Test Coverage:
- Activity collection
- Score calculation algorithms
- Metrics storage and retrieval
- Edge cases and error handling
- Integration with registry
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
from unittest.mock import Mock, patch, MagicMock

# Load the metrics collector module
spec = importlib.util.spec_from_file_location(
    "agent_metrics_collector",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent-metrics-collector.py")
)
metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_module)

AgentActivity = metrics_module.AgentActivity
MetricsScore = metrics_module.MetricsScore
AgentMetrics = metrics_module.AgentMetrics
MetricsCollector = metrics_module.MetricsCollector


def test_agent_activity_dataclass():
    """Test AgentActivity dataclass creation and serialization"""
    activity = AgentActivity(
        issues_resolved=5,
        prs_merged=3,
        reviews_given=2
    )
    
    assert activity.issues_resolved == 5
    assert activity.prs_merged == 3
    assert activity.reviews_given == 2
    
    # Test serialization
    data = activity.to_dict()
    assert isinstance(data, dict)
    assert data['issues_resolved'] == 5
    
    print("✓ AgentActivity dataclass test passed")


def test_metrics_score_dataclass():
    """Test MetricsScore dataclass and calculations"""
    score = MetricsScore(
        code_quality=0.8,
        issue_resolution=0.6,
        pr_success=0.9,
        peer_review=0.4,
        overall=0.7
    )
    
    assert score.code_quality == 0.8
    assert score.overall == 0.7
    
    # Test serialization
    data = score.to_dict()
    assert isinstance(data, dict)
    assert data['code_quality'] == 0.8
    
    print("✓ MetricsScore dataclass test passed")


def test_agent_metrics_serialization():
    """Test complete AgentMetrics serialization"""
    activity = AgentActivity(issues_resolved=5, prs_merged=3)
    scores = MetricsScore(overall=0.75)
    
    metrics = AgentMetrics(
        agent_id="agent-test-123",
        timestamp=datetime.now(timezone.utc).isoformat(),
        activity=activity,
        scores=scores,
        metadata={'test': True}
    )
    
    # Test serialization
    data = metrics.to_dict()
    assert data['agent_id'] == "agent-test-123"
    assert 'activity' in data
    assert 'scores' in data
    assert data['metadata']['test'] is True
    
    print("✓ AgentMetrics serialization test passed")


def test_score_calculation_perfect_performance():
    """Test score calculation for perfect performance"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock registry
        registry_file = Path(tmpdir) / "registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(registry_file, 'w') as f:
            json.dump({
                'config': {
                    'metrics_weight': {
                        'code_quality': 0.30,
                        'issue_resolution': 0.25,
                        'pr_success': 0.25,
                        'peer_review': 0.20
                    }
                }
            }, f)
        
        # Temporarily override registry path
        with patch.object(metrics_module, 'REGISTRY_FILE', registry_file):
            collector = MetricsCollector()
            
            # Perfect activity
            activity = AgentActivity(
                issues_created=10,
                issues_resolved=10,
                prs_created=10,
                prs_merged=10,
                reviews_given=5
            )
            
            scores = collector.calculate_scores(activity, "agent-test")
            
            # All components should be high
            assert scores.issue_resolution == 1.0, f"Expected 1.0, got {scores.issue_resolution}"
            assert scores.pr_success == 1.0, f"Expected 1.0, got {scores.pr_success}"
            assert scores.peer_review == 1.0, f"Expected 1.0, got {scores.peer_review}"
            assert scores.overall > 0.9, f"Expected >0.9, got {scores.overall}"
            
            print("✓ Perfect performance score calculation test passed")


def test_score_calculation_no_activity():
    """Test score calculation for new agent with no activity"""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_file = Path(tmpdir) / "registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(registry_file, 'w') as f:
            json.dump({'config': {'metrics_weight': {}}}, f)
        
        with patch.object(metrics_module, 'REGISTRY_FILE', registry_file):
            collector = MetricsCollector()
            
            # No activity
            activity = AgentActivity()
            
            scores = collector.calculate_scores(activity, "agent-new")
            
            # Should have neutral/default scores
            assert scores.code_quality == 0.5, f"Expected 0.5, got {scores.code_quality}"
            assert scores.issue_resolution == 0.0
            assert scores.pr_success == 0.0
            assert scores.peer_review == 0.0
            
            print("✓ No activity score calculation test passed")


def test_score_calculation_partial_activity():
    """Test score calculation for partial activity"""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_file = Path(tmpdir) / "registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(registry_file, 'w') as f:
            json.dump({'config': {'metrics_weight': {
                'code_quality': 0.30,
                'issue_resolution': 0.25,
                'pr_success': 0.25,
                'peer_review': 0.20
            }}}, f)
        
        with patch.object(metrics_module, 'REGISTRY_FILE', registry_file):
            collector = MetricsCollector()
            
            # Partial activity
            activity = AgentActivity(
                prs_created=5,
                prs_merged=3,
                reviews_given=2
            )
            
            scores = collector.calculate_scores(activity, "agent-partial")
            
            # PR success should be 3/5 = 0.6
            assert scores.pr_success == 0.6, f"Expected 0.6, got {scores.pr_success}"
            
            # Peer review should be 2/5 = 0.4
            assert scores.peer_review == 0.4, f"Expected 0.4, got {scores.peer_review}"
            
            print("✓ Partial activity score calculation test passed")


def test_metrics_storage_and_retrieval():
    """Test storing and loading metrics"""
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_dir = Path(tmpdir) / "metrics"
        
        with patch.object(metrics_module, 'METRICS_DIR', metrics_dir):
            collector = MetricsCollector()
            
            # Create test metrics
            activity = AgentActivity(issues_resolved=5)
            scores = MetricsScore(overall=0.75)
            
            metrics = AgentMetrics(
                agent_id="agent-storage-test",
                timestamp=datetime.now(timezone.utc).isoformat(),
                activity=activity,
                scores=scores,
                metadata={}
            )
            
            # Store metrics
            collector.store_metrics(metrics)
            
            # Verify files were created
            agent_dir = metrics_dir / "agent-storage-test"
            assert agent_dir.exists(), "Agent metrics directory not created"
            assert (agent_dir / "latest.json").exists(), "latest.json not created"
            
            # Load metrics back
            loaded_metrics = collector.load_latest_metrics("agent-storage-test")
            
            assert loaded_metrics is not None, "Failed to load metrics"
            assert loaded_metrics.agent_id == "agent-storage-test"
            assert loaded_metrics.activity.issues_resolved == 5
            assert loaded_metrics.scores.overall == 0.75
            
            print("✓ Metrics storage and retrieval test passed")


def test_scoring_weights_loading():
    """Test loading scoring weights from registry"""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_file = Path(tmpdir) / "registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        custom_weights = {
            'code_quality': 0.40,
            'issue_resolution': 0.20,
            'pr_success': 0.30,
            'peer_review': 0.10
        }
        
        with open(registry_file, 'w') as f:
            json.dump({
                'config': {
                    'metrics_weight': custom_weights
                }
            }, f)
        
        with patch.object(metrics_module, 'REGISTRY_FILE', registry_file):
            collector = MetricsCollector()
            
            assert collector.weights == custom_weights
            
            print("✓ Scoring weights loading test passed")


def test_default_weights_fallback():
    """Test fallback to default weights when registry unavailable"""
    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent_file = Path(tmpdir) / "nonexistent.json"
        
        with patch.object(metrics_module, 'REGISTRY_FILE', nonexistent_file):
            collector = MetricsCollector()
            
            # Should have default weights
            assert collector.weights['code_quality'] == 0.30
            assert collector.weights['issue_resolution'] == 0.25
            assert collector.weights['pr_success'] == 0.25
            assert collector.weights['peer_review'] == 0.20
            
            print("✓ Default weights fallback test passed")


def test_weighted_overall_score_calculation():
    """Test that overall score is correctly weighted"""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_file = Path(tmpdir) / "registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        weights = {
            'code_quality': 0.30,
            'issue_resolution': 0.25,
            'pr_success': 0.25,
            'peer_review': 0.20
        }
        
        with open(registry_file, 'w') as f:
            json.dump({'config': {'metrics_weight': weights}}, f)
        
        with patch.object(metrics_module, 'REGISTRY_FILE', registry_file):
            collector = MetricsCollector()
            
            # Activity that produces known scores
            activity = AgentActivity(
                prs_created=10,
                prs_merged=8,  # 0.8 PR success
                reviews_given=5  # 1.0 peer review
            )
            
            scores = collector.calculate_scores(activity, "agent-test")
            
            # Expected: 0.8*0.3 (code quality) + 0*0.25 + 0.8*0.25 + 1.0*0.20
            # But code quality uses merge rate * 1.2, so min(1.0, 0.8*1.2) = 0.96
            expected = 0.96 * 0.30 + 0.0 * 0.25 + 0.8 * 0.25 + 1.0 * 0.20
            
            assert abs(scores.overall - expected) < 0.01, \
                f"Expected {expected}, got {scores.overall}"
            
            print("✓ Weighted overall score calculation test passed")


def test_edge_case_division_by_zero():
    """Test edge cases that could cause division by zero"""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_file = Path(tmpdir) / "registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(registry_file, 'w') as f:
            json.dump({'config': {'metrics_weight': {}}}, f)
        
        with patch.object(metrics_module, 'REGISTRY_FILE', registry_file):
            collector = MetricsCollector()
            
            # Edge case: agent closed PRs but none merged
            activity = AgentActivity(
                prs_created=5,
                prs_merged=0
            )
            
            scores = collector.calculate_scores(activity, "agent-edge")
            
            # Should handle gracefully without division by zero
            assert scores.pr_success == 0.0
            assert scores.overall >= 0.0
            
            print("✓ Division by zero edge case test passed")


def test_resolving_others_issues():
    """Test scoring when agent resolves issues created by others"""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_file = Path(tmpdir) / "registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(registry_file, 'w') as f:
            json.dump({'config': {'metrics_weight': {}}}, f)
        
        with patch.object(metrics_module, 'REGISTRY_FILE', registry_file):
            collector = MetricsCollector()
            
            # Agent resolves issues but didn't create any
            activity = AgentActivity(
                issues_created=0,
                issues_resolved=3
            )
            
            scores = collector.calculate_scores(activity, "agent-helper")
            
            # Should get credit for resolving others' issues
            assert scores.issue_resolution > 0.0
            assert scores.issue_resolution <= 1.0
            
            print("✓ Resolving others' issues test passed")


def test_high_merge_rate_bonus():
    """Test that high PR merge rate gets a bonus in code quality"""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_file = Path(tmpdir) / "registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(registry_file, 'w') as f:
            json.dump({'config': {'metrics_weight': {}}}, f)
        
        with patch.object(metrics_module, 'REGISTRY_FILE', registry_file):
            collector = MetricsCollector()
            
            # 100% merge rate
            activity = AgentActivity(
                prs_created=10,
                prs_merged=10
            )
            
            scores = collector.calculate_scores(activity, "agent-perfect")
            
            # With 1.2x bonus, 1.0 * 1.2 = 1.2, capped at 1.0
            assert scores.code_quality == 1.0
            
            print("✓ High merge rate bonus test passed")


def test_metrics_directory_creation():
    """Test that metrics directory is created if it doesn't exist"""
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_dir = Path(tmpdir) / "nonexistent" / "metrics"
        
        with patch.object(metrics_module, 'METRICS_DIR', metrics_dir):
            collector = MetricsCollector()
            
            # Directory should be created during initialization
            assert metrics_dir.exists(), "Metrics directory was not created"
            
            print("✓ Metrics directory creation test passed")


def test_error_handling_invalid_json():
    """Test error handling when loading corrupted metrics"""
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_dir = Path(tmpdir) / "metrics"
        agent_dir = metrics_dir / "agent-corrupt"
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Write invalid JSON
        with open(agent_dir / "latest.json", 'w') as f:
            f.write("{ invalid json }")
        
        with patch.object(metrics_module, 'METRICS_DIR', metrics_dir):
            collector = MetricsCollector()
            
            # Should handle gracefully and return None
            metrics = collector.load_latest_metrics("agent-corrupt")
            assert metrics is None
            
            print("✓ Invalid JSON error handling test passed")


def run_all_tests():
    """Run all test functions"""
    test_functions = [
        test_agent_activity_dataclass,
        test_metrics_score_dataclass,
        test_agent_metrics_serialization,
        test_score_calculation_perfect_performance,
        test_score_calculation_no_activity,
        test_score_calculation_partial_activity,
        test_metrics_storage_and_retrieval,
        test_scoring_weights_loading,
        test_default_weights_fallback,
        test_weighted_overall_score_calculation,
        test_edge_case_division_by_zero,
        test_resolving_others_issues,
        test_high_merge_rate_bonus,
        test_metrics_directory_creation,
        test_error_handling_invalid_json,
    ]
    
    passed = 0
    failed = 0
    
    print("=" * 70)
    print("🧪 Running Agent Metrics Collector Tests")
    print("=" * 70)
    print()
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed > 0:
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    run_all_tests()
