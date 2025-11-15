#!/usr/bin/env python3
"""
Test Suite for Autonomous Issue Prioritizer

Tests the multi-armed bandit based issue prioritization system.
Following @accelerate-master principles: efficient, thorough, performance-focused.
"""

import sys
import json
import math
import tempfile
from pathlib import Path
from datetime import datetime, timezone

# Add tools directory to path
tools_dir = Path(__file__).parent.parent / 'tools'
sys.path.insert(0, str(tools_dir))

# Import the module by loading it
import importlib.util
spec = importlib.util.spec_from_file_location(
    "issue_prioritizer",
    tools_dir / "issue-prioritizer.py"
)
issue_prioritizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(issue_prioritizer)

# Import the classes
IssueMetrics = issue_prioritizer.IssueMetrics
IssueType = issue_prioritizer.IssueType
IssuePrioritizer = issue_prioritizer.IssuePrioritizer


def test_issue_metrics_reward_calculation():
    """Test reward calculation from issue metrics"""
    print("Testing IssueMetrics reward calculation...")
    
    # Test perfect outcome
    metrics = IssueMetrics(
        resolution_time_hours=12.0,
        pr_success=True,
        code_quality=1.0,
        agent_score=1.0
    )
    reward = metrics.calculate_reward()
    assert 0.9 <= reward <= 1.0, f"Expected high reward, got {reward}"
    print(f"  ✓ Perfect outcome: {reward:.3f}")
    
    # Test poor outcome
    metrics = IssueMetrics(
        resolution_time_hours=100.0,
        pr_success=False,
        code_quality=0.0,
        agent_score=0.0
    )
    reward = metrics.calculate_reward()
    assert 0.0 <= reward <= 0.2, f"Expected low reward, got {reward}"
    print(f"  ✓ Poor outcome: {reward:.3f}")
    
    # Test medium outcome
    metrics = IssueMetrics(
        resolution_time_hours=24.0,
        pr_success=True,
        code_quality=0.5,
        agent_score=0.5
    )
    reward = metrics.calculate_reward()
    assert 0.4 <= reward <= 0.75, f"Expected medium reward, got {reward}"
    print(f"  ✓ Medium outcome: {reward:.3f}")
    
    print("✅ IssueMetrics tests passed\n")


def test_issue_type_ucb1_calculation():
    """Test UCB1 score calculation for issue types"""
    print("Testing IssueType UCB1 calculation...")
    
    # Test unexplored arm (should have infinite priority)
    issue_type = IssueType(name='bug', keywords=['bug'])
    score = issue_type.ucb1_score(total_attempts=100)
    assert score == float('inf'), "Unexplored arm should have infinite priority"
    print("  ✓ Unexplored arm: infinite priority")
    
    # Test well-explored high-reward arm
    issue_type = IssueType(
        name='performance',
        keywords=['performance'],
        total_attempts=50,
        total_reward=40.0  # 0.8 average
    )
    score = issue_type.ucb1_score(total_attempts=100)
    expected_min = 0.8  # At least the average reward
    assert score >= expected_min, f"Expected UCB1 >= {expected_min}, got {score}"
    print(f"  ✓ High-reward arm: {score:.3f}")
    
    # Test less explored arm (should get exploration bonus)
    explored_type = IssueType(
        name='bug',
        keywords=['bug'],
        total_attempts=50,
        total_reward=35.0  # 0.7 average
    )
    less_explored_type = IssueType(
        name='feature',
        keywords=['feature'],
        total_attempts=10,
        total_reward=7.0  # 0.7 average (same as explored)
    )
    
    explored_score = explored_type.ucb1_score(total_attempts=100)
    less_explored_score = less_explored_type.ucb1_score(total_attempts=100)
    
    # Less explored should have higher score due to exploration bonus
    assert less_explored_score > explored_score, \
        "Less explored arm should have higher UCB1 score"
    print(f"  ✓ Exploration bonus: {less_explored_score:.3f} > {explored_score:.3f}")
    
    print("✅ UCB1 calculation tests passed\n")


def test_issue_classification():
    """Test issue type classification"""
    print("Testing issue classification...")
    
    # Create temporary state file
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "priority_state.json"
        history_file = Path(tmpdir) / "issue_history.json"
        
        prioritizer = IssuePrioritizer(history_file=history_file)
        prioritizer.priority_state_file = state_file
        
        # Test performance issue
        issue_type = prioritizer.classify_issue(
            "Slow database queries",
            "The queries are taking too long to execute",
            ["performance"]
        )
        assert issue_type == "performance", f"Expected 'performance', got '{issue_type}'"
        print(f"  ✓ Performance issue: {issue_type}")
        
        # Test bug
        issue_type = prioritizer.classify_issue(
            "Application crashes on startup",
            "Getting null pointer exception when starting",
            ["bug", "crash"]
        )
        assert issue_type == "bug", f"Expected 'bug', got '{issue_type}'"
        print(f"  ✓ Bug issue: {issue_type}")
        
        # Test security
        issue_type = prioritizer.classify_issue(
            "Authentication bypass vulnerability",
            "Security issue with auth tokens",
            ["security", "vulnerability"]
        )
        assert issue_type == "security", f"Expected 'security', got '{issue_type}'"
        print(f"  ✓ Security issue: {issue_type}")
        
        # Test feature
        issue_type = prioritizer.classify_issue(
            "Add new API endpoint",
            "We need a new feature for user management",
            ["feature", "enhancement"]
        )
        assert issue_type == "feature", f"Expected 'feature', got '{issue_type}'"
        print(f"  ✓ Feature request: {issue_type}")
    
    print("✅ Classification tests passed\n")


def test_priority_calculation():
    """Test priority score calculation"""
    print("Testing priority calculation...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "priority_state.json"
        history_file = Path(tmpdir) / "issue_history.json"
        
        prioritizer = IssuePrioritizer(history_file=history_file)
        prioritizer.priority_state_file = state_file
        
        # Initial state - all types should get equal priority
        priority = prioritizer.calculate_priority('performance')
        assert 0.9 <= priority <= 1.0, f"Initial priority should be ~1.0, got {priority}"
        print(f"  ✓ Initial priority (unexplored): {priority:.3f}")
        
        # Simulate some attempts with rewards
        prioritizer.issue_types['performance'].total_attempts = 20
        prioritizer.issue_types['performance'].total_reward = 16.0  # 0.8 avg
        
        prioritizer.issue_types['bug'].total_attempts = 20
        prioritizer.issue_types['bug'].total_reward = 12.0  # 0.6 avg
        
        perf_priority = prioritizer.calculate_priority('performance')
        bug_priority = prioritizer.calculate_priority('bug')
        
        # Performance should have higher priority due to better reward
        assert perf_priority > bug_priority, \
            f"Performance ({perf_priority:.3f}) should have higher priority than bug ({bug_priority:.3f})"
        print(f"  ✓ Reward-based priority: performance={perf_priority:.3f} > bug={bug_priority:.3f}")
    
    print("✅ Priority calculation tests passed\n")


def test_issue_prioritization():
    """Test full issue prioritization flow"""
    print("Testing full issue prioritization...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "priority_state.json"
        history_file = Path(tmpdir) / "issue_history.json"
        
        prioritizer = IssuePrioritizer(history_file=history_file)
        prioritizer.priority_state_file = state_file
        
        # Prioritize a performance issue
        result = prioritizer.prioritize_issue(
            issue_number=123,
            title="Database queries are slow",
            body="We need to optimize the query performance",
            labels=["performance", "database"]
        )
        
        # Verify result structure
        assert 'issue_number' in result
        assert 'title' in result
        assert 'issue_type' in result
        assert 'priority_score' in result
        assert 'priority_tier' in result
        assert 'recommended_action' in result
        assert 'ucb1_stats' in result
        
        print(f"  ✓ Result structure: {list(result.keys())}")
        print(f"  ✓ Issue #{result['issue_number']}: {result['title']}")
        print(f"  ✓ Type: {result['issue_type']}")
        print(f"  ✓ Priority: {result['priority_score']} ({result['priority_tier']})")
        print(f"  ✓ Action: {result['recommended_action']}")
    
    print("✅ Issue prioritization tests passed\n")


def test_history_update():
    """Test updating from historical data"""
    print("Testing history update...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "priority_state.json"
        history_file = Path(tmpdir) / "issue_history.json"
        
        # Create mock history data
        history = {
            "version": "1.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_issues": 3,
            "issues": [
                {
                    "issue_number": 1,
                    "title": "Slow database queries",
                    "body": "Performance issue",
                    "labels": ["performance"],
                    "agent_assigned": "accelerate-master",
                    "pr_number": 10
                },
                {
                    "issue_number": 2,
                    "title": "API crashes",
                    "body": "Bug in endpoint",
                    "labels": ["bug"],
                    "agent_assigned": "engineer-master",
                    "pr_number": 11
                },
                {
                    "issue_number": 3,
                    "title": "Add new feature",
                    "body": "Enhancement request",
                    "labels": ["feature"],
                    "agent_assigned": "create-guru",
                    "pr_number": None  # Failed
                }
            ]
        }
        
        history_file.write_text(json.dumps(history))
        
        prioritizer = IssuePrioritizer(history_file=history_file)
        prioritizer.priority_state_file = state_file
        
        # Update from history
        prioritizer.update_from_history()
        
        # Check that statistics were updated
        assert prioritizer.issue_types['performance'].total_attempts > 0
        assert prioritizer.issue_types['bug'].total_attempts > 0
        assert prioritizer.issue_types['feature'].total_attempts > 0
        
        print(f"  ✓ Performance: {prioritizer.issue_types['performance'].total_attempts} attempts")
        print(f"  ✓ Bug: {prioritizer.issue_types['bug'].total_attempts} attempts")
        print(f"  ✓ Feature: {prioritizer.issue_types['feature'].total_attempts} attempts")
        
        # Check that state was saved
        assert state_file.exists(), "State file should be created"
        
        # Load state and verify
        with open(state_file) as f:
            saved_state = json.load(f)
        
        assert 'issue_types' in saved_state
        assert 'performance' in saved_state['issue_types']
        
        print("  ✓ State saved successfully")
    
    print("✅ History update tests passed\n")


def test_priority_report_generation():
    """Test priority report generation"""
    print("Testing priority report generation...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "priority_state.json"
        history_file = Path(tmpdir) / "issue_history.json"
        
        prioritizer = IssuePrioritizer(history_file=history_file)
        prioritizer.priority_state_file = state_file
        
        # Create some test issues
        issues = [
            {
                'issue_number': 1,
                'title': 'Critical performance issue',
                'issue_type': 'performance',
                'priority_score': 0.95,
                'priority_tier': 'P0-Critical',
                'recommended_action': 'Implement immediately'
            },
            {
                'issue_number': 2,
                'title': 'Minor bug',
                'issue_type': 'bug',
                'priority_score': 0.45,
                'priority_tier': 'P3-Low',
                'recommended_action': 'Monitor'
            }
        ]
        
        report = prioritizer.generate_priority_report(issues)
        
        # Verify report contains expected sections
        assert '# 🎯 Issue Priority Report' in report
        assert 'Multi-Armed Bandit Statistics' in report
        assert '## 🔥 Priority Tiers' in report
        assert 'P0-Critical' in report
        assert '#1' in report
        assert '#2' in report
        
        print("  ✓ Report structure validated")
        print(f"  ✓ Report length: {len(report)} characters")
    
    print("✅ Report generation tests passed\n")


def test_state_persistence():
    """Test that state persists correctly"""
    print("Testing state persistence...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "priority_state.json"
        history_file = Path(tmpdir) / "issue_history.json"
        
        # Create first prioritizer and update state
        prioritizer1 = IssuePrioritizer(history_file=history_file)
        prioritizer1.priority_state_file = state_file
        
        prioritizer1.issue_types['performance'].total_attempts = 10
        prioritizer1.issue_types['performance'].total_reward = 8.0
        prioritizer1.save_state()
        
        # Create second prioritizer and load state
        prioritizer2 = IssuePrioritizer(history_file=history_file)
        prioritizer2.priority_state_file = state_file
        prioritizer2.load_state()
        
        # Verify state was loaded correctly
        assert prioritizer2.issue_types['performance'].total_attempts == 10
        assert prioritizer2.issue_types['performance'].total_reward == 8.0
        
        print("  ✓ State saved and loaded correctly")
        print(f"  ✓ Performance attempts: {prioritizer2.issue_types['performance'].total_attempts}")
        print(f"  ✓ Performance reward: {prioritizer2.issue_types['performance'].total_reward}")
    
    print("✅ State persistence tests passed\n")


def test_performance_benchmark():
    """Benchmark prioritization performance"""
    print("Testing performance (benchmark)...")
    
    import time
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "priority_state.json"
        history_file = Path(tmpdir) / "issue_history.json"
        
        prioritizer = IssuePrioritizer(history_file=history_file)
        prioritizer.priority_state_file = state_file
        
        # Benchmark single prioritization
        iterations = 1000
        start = time.time()
        
        for i in range(iterations):
            prioritizer.prioritize_issue(
                issue_number=i,
                title=f"Test issue {i}",
                body="Test body",
                labels=["performance"]
            )
        
        elapsed = time.time() - start
        per_issue = (elapsed / iterations) * 1000  # ms
        
        print(f"  ✓ Prioritized {iterations} issues in {elapsed:.3f}s")
        print(f"  ✓ Average: {per_issue:.3f}ms per issue")
        
        # Performance target: < 5ms per issue (for @accelerate-master efficiency)
        assert per_issue < 5.0, f"Prioritization too slow: {per_issue:.3f}ms > 5ms"
        print(f"  ✓ Performance target met: {per_issue:.3f}ms < 5ms")
    
    print("✅ Performance benchmark passed\n")


def run_all_tests():
    """Run all test suites"""
    print("=" * 60)
    print("🧪 Issue Prioritizer Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_issue_metrics_reward_calculation()
        test_issue_type_ucb1_calculation()
        test_issue_classification()
        test_priority_calculation()
        test_issue_prioritization()
        test_history_update()
        test_priority_report_generation()
        test_state_persistence()
        test_performance_benchmark()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
