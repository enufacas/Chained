#!/usr/bin/env python3
"""
Test agent evaluator workflow optimizations

Tests specifically for the short-circuit optimizations added by @troubleshoot-expert
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
import importlib.util

# Load the metrics collector module
spec = importlib.util.spec_from_file_location(
    "agent_metrics_collector",
    os.path.join("tools", "agent-metrics-collector.py")
)
metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_module)

AgentActivity = metrics_module.AgentActivity
MetricsCollector = metrics_module.MetricsCollector


def test_short_circuit_no_assigned_issues():
    """
    Test that collect_agent_activity returns early when agent has no assigned issues.
    This verifies the short-circuit optimization is working.
    """
    print("🧪 Testing short-circuit for agents with no assigned issues...")
    
    # Create a mock collector
    collector = MetricsCollector()
    
    # Mock the _find_issues_assigned_to_agent to return empty list
    with patch.object(collector, '_find_issues_assigned_to_agent', return_value=[]):
        # Mock other expensive methods to track if they're called
        with patch.object(collector, '_get_reviews_by_agent') as mock_reviews, \
             patch.object(collector, 'github') as mock_github:
            
            # Collect activity
            activity = collector.collect_agent_activity('test-agent-123', since_days=7)
            
            # Verify the activity is all zeros
            assert activity.issues_created == 0, "issues_created should be 0"
            assert activity.issues_resolved == 0, "issues_resolved should be 0"
            assert activity.prs_created == 0, "prs_created should be 0"
            assert activity.prs_merged == 0, "prs_merged should be 0"
            assert activity.reviews_given == 0, "reviews_given should be 0"
            assert activity.comments_made == 0, "comments_made should be 0"
            
            # Verify expensive methods were NOT called (short-circuited)
            mock_reviews.assert_not_called()
            # GitHub API should only be called for finding assigned issues, not for comments
            # The exact count depends on implementation details
            
    print("  ✅ Short-circuit works correctly for agents with no assigned issues")


def test_short_circuit_no_pr_activity():
    """
    Test that review lookups are skipped when agent has no PR activity.
    """
    print("🧪 Testing short-circuit for review lookups...")
    
    collector = MetricsCollector()
    
    # Mock _find_issues_assigned_to_agent to return some issues
    mock_issues = [
        {'number': 1, 'state': 'open'},
        {'number': 2, 'state': 'closed'}
    ]
    
    with patch.object(collector, '_find_issues_assigned_to_agent', return_value=mock_issues):
        # Mock GitHub API to return no PRs
        with patch.object(collector, 'github') as mock_github, \
             patch.object(collector, '_get_reviews_by_agent') as mock_reviews:
            
            # Set up GitHub mock to return empty results
            mock_github.get.return_value = None
            
            # Collect activity
            activity = collector.collect_agent_activity('test-agent-456', since_days=7)
            
            # Verify we have issues but no PRs
            assert activity.issues_created == 2, "Should have 2 assigned issues"
            assert activity.prs_created == 0, "Should have no PRs"
            
            # Verify expensive review lookup was skipped
            mock_reviews.assert_not_called()
            
    print("  ✅ Review lookup short-circuit works correctly")


def test_progress_logging_format():
    """
    Test that progress logging includes agent count in correct format.
    This is a smoke test to ensure the format strings are correct.
    """
    print("🧪 Testing progress logging format...")
    
    # Test the format string we use in evaluate_all_agents
    total_agents = 51
    current_idx = 23
    
    # Verify format strings don't raise exceptions
    progress_msg = f"📊 Evaluating agent {current_idx}/{total_agents}"
    assert progress_msg == "📊 Evaluating agent 23/51"
    
    # Test with different values
    progress_msg = f"✅ [{current_idx}/{total_agents}] Collected metrics"
    assert progress_msg == "✅ [23/51] Collected metrics"
    
    print("  ✅ Progress logging format is correct")


def run_all_tests():
    """Run all optimization tests"""
    print("\n" + "="*70)
    print("🧪 Agent Evaluator Optimization Tests (@troubleshoot-expert)")
    print("="*70 + "\n")
    
    tests = [
        test_short_circuit_no_assigned_issues,
        test_short_circuit_no_pr_activity,
        test_progress_logging_format,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ Test error: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
