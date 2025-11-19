#!/usr/bin/env python3
"""
Test Agent Scoring System

Verifies that the agent metrics collector properly calculates scores
and that all components are working correctly.
"""

import sys
from pathlib import Path
import importlib.util

# Add tools to path
tools_dir = Path(__file__).parent / 'tools'
sys.path.insert(0, str(tools_dir))

# Load the agent-metrics-collector module (with hyphen in name)
spec = importlib.util.spec_from_file_location(
    "agent_metrics_collector",
    tools_dir / "agent-metrics-collector.py"
)
metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_module)

# Import the classes we need
AgentActivity = metrics_module.AgentActivity
MetricsScore = metrics_module.MetricsScore
MetricsCollector = metrics_module.MetricsCollector


def test_code_quality_scoring():
    """Test code quality score calculation"""
    print("\n🧪 Testing Code Quality Scoring...")
    
    collector = MetricsCollector()
    
    # Test case 1: High merge rate (80%)
    activity = AgentActivity(prs_created=10, prs_merged=8)
    scores = collector.calculate_scores(activity, "test-agent-1")
    assert 0.90 <= scores.code_quality <= 1.0, f"Expected ~0.96, got {scores.code_quality}"
    print(f"   ✅ High merge rate (8/10): {scores.code_quality:.2%}")
    
    # Test case 2: Perfect merge rate
    activity = AgentActivity(prs_created=5, prs_merged=5)
    scores = collector.calculate_scores(activity, "test-agent-2")
    assert scores.code_quality == 1.0, f"Expected 1.0, got {scores.code_quality}"
    print(f"   ✅ Perfect merge rate (5/5): {scores.code_quality:.2%}")
    
    # Test case 3: New agent (no PRs)
    activity = AgentActivity(prs_created=0, prs_merged=0)
    scores = collector.calculate_scores(activity, "test-agent-3")
    assert scores.code_quality == 0.5, f"Expected 0.5, got {scores.code_quality}"
    print(f"   ✅ New agent (no PRs): {scores.code_quality:.2%}")
    
    return True


def test_issue_resolution_scoring():
    """Test issue resolution score calculation"""
    print("\n🧪 Testing Issue Resolution Scoring...")
    
    collector = MetricsCollector()
    
    # Test case 1: Perfect resolution rate
    activity = AgentActivity(issues_created=5, issues_resolved=5)
    scores = collector.calculate_scores(activity, "test-agent-1")
    assert scores.issue_resolution == 1.0, f"Expected 1.0, got {scores.issue_resolution}"
    print(f"   ✅ Perfect resolution (5/5): {scores.issue_resolution:.2%}")
    
    # Test case 2: Resolving others' issues
    activity = AgentActivity(issues_created=0, issues_resolved=3)
    scores = collector.calculate_scores(activity, "test-agent-2")
    assert scores.issue_resolution == 0.6, f"Expected 0.6, got {scores.issue_resolution}"
    print(f"   ✅ Resolving others' issues (3/0): {scores.issue_resolution:.2%}")
    
    # Test case 3: No issues
    activity = AgentActivity(issues_created=0, issues_resolved=0)
    scores = collector.calculate_scores(activity, "test-agent-3")
    assert scores.issue_resolution == 0.0, f"Expected 0.0, got {scores.issue_resolution}"
    print(f"   ✅ No issues: {scores.issue_resolution:.2%}")
    
    return True


def test_pr_success_scoring():
    """Test PR success score calculation"""
    print("\n🧪 Testing PR Success Scoring...")
    
    collector = MetricsCollector()
    
    # Test case 1: 100% success
    activity = AgentActivity(prs_created=10, prs_merged=10)
    scores = collector.calculate_scores(activity, "test-agent-1")
    assert scores.pr_success == 1.0, f"Expected 1.0, got {scores.pr_success}"
    print(f"   ✅ Perfect success (10/10): {scores.pr_success:.2%}")
    
    # Test case 2: 50% success
    activity = AgentActivity(prs_created=10, prs_merged=5)
    scores = collector.calculate_scores(activity, "test-agent-2")
    assert scores.pr_success == 0.5, f"Expected 0.5, got {scores.pr_success}"
    print(f"   ✅ Half success (5/10): {scores.pr_success:.2%}")
    
    # Test case 3: No PRs
    activity = AgentActivity(prs_created=0, prs_merged=0)
    scores = collector.calculate_scores(activity, "test-agent-3")
    assert scores.pr_success == 0.0, f"Expected 0.0, got {scores.pr_success}"
    print(f"   ✅ No PRs: {scores.pr_success:.2%}")
    
    return True


def test_peer_review_scoring():
    """Test peer review score calculation"""
    print("\n🧪 Testing Peer Review Scoring...")
    
    collector = MetricsCollector()
    
    # Test case 1: 5+ reviews (perfect score)
    activity = AgentActivity(reviews_given=10)
    scores = collector.calculate_scores(activity, "test-agent-1")
    assert scores.peer_review == 1.0, f"Expected 1.0, got {scores.peer_review}"
    print(f"   ✅ Many reviews (10): {scores.peer_review:.2%}")
    
    # Test case 2: 2 reviews
    activity = AgentActivity(reviews_given=2)
    scores = collector.calculate_scores(activity, "test-agent-2")
    assert scores.peer_review == 0.4, f"Expected 0.4, got {scores.peer_review}"
    print(f"   ✅ Some reviews (2): {scores.peer_review:.2%}")
    
    # Test case 3: No reviews
    activity = AgentActivity(reviews_given=0)
    scores = collector.calculate_scores(activity, "test-agent-3")
    assert scores.peer_review == 0.0, f"Expected 0.0, got {scores.peer_review}"
    print(f"   ✅ No reviews: {scores.peer_review:.2%}")
    
    return True


def test_overall_scoring():
    """Test overall weighted score calculation"""
    print("\n🧪 Testing Overall Weighted Scoring...")
    
    collector = MetricsCollector()
    
    # Test case: Perfect agent
    activity = AgentActivity(
        prs_created=10, prs_merged=10,
        issues_created=5, issues_resolved=5,
        reviews_given=5
    )
    scores = collector.calculate_scores(activity, "test-agent-perfect")
    
    # Manual calculation with default weights:
    # code_quality=1.0 * 0.30 = 0.30
    # issue_resolution=1.0 * 0.20 = 0.20
    # pr_success=1.0 * 0.20 = 0.20
    # peer_review=1.0 * 0.15 = 0.15
    # creativity=0.5 * 0.15 = 0.075 (default fallback)
    # Total = 0.925
    
    expected = 0.925
    tolerance = 0.05  # Allow some variance for creativity
    assert abs(scores.overall - expected) <= tolerance, \
        f"Expected ~{expected}, got {scores.overall}"
    print(f"   ✅ Perfect agent overall score: {scores.overall:.2%}")
    print(f"      - Code Quality: {scores.code_quality:.2%} (weight: 30%)")
    print(f"      - Issue Resolution: {scores.issue_resolution:.2%} (weight: 20%)")
    print(f"      - PR Success: {scores.pr_success:.2%} (weight: 20%)")
    print(f"      - Peer Review: {scores.peer_review:.2%} (weight: 15%)")
    print(f"      - Creativity: {scores.creativity:.2%} (weight: 15%)")
    
    return True


def test_weights_configuration():
    """Test that scoring weights are properly configured"""
    print("\n🧪 Testing Scoring Weights Configuration...")
    
    collector = MetricsCollector()
    weights = collector.weights
    
    # Check all weights exist
    required_weights = ['code_quality', 'issue_resolution', 'pr_success', 'peer_review', 'creativity']
    for weight in required_weights:
        assert weight in weights, f"Missing weight: {weight}"
        print(f"   ✅ {weight}: {weights[weight]:.0%}")
    
    # Check weights sum to 1.0
    total = sum(weights.values())
    assert abs(total - 1.0) < 0.01, f"Weights should sum to 1.0, got {total}"
    print(f"   ✅ Total weights: {total:.0%}")
    
    return True


def main():
    """Run all scoring system tests"""
    print("=" * 60)
    print("🧪 AGENT SCORING SYSTEM TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Code Quality Scoring", test_code_quality_scoring),
        ("Issue Resolution Scoring", test_issue_resolution_scoring),
        ("PR Success Scoring", test_pr_success_scoring),
        ("Peer Review Scoring", test_peer_review_scoring),
        ("Overall Weighted Scoring", test_overall_scoring),
        ("Weights Configuration", test_weights_configuration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"   ❌ {test_name} failed")
        except AssertionError as e:
            failed += 1
            print(f"   ❌ {test_name} failed: {e}")
        except Exception as e:
            failed += 1
            print(f"   ❌ {test_name} error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL SCORING SYSTEM TESTS PASSED!")
        print("\nThe scoring system is valid and working correctly:")
        print("  ✓ Code quality based on PR merge rate")
        print("  ✓ Issue resolution properly calculated")
        print("  ✓ PR success rate correctly computed")
        print("  ✓ Peer review activity normalized")
        print("  ✓ Weighted overall score accurate")
        print("  ✓ Weights properly configured (sum to 100%)")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
