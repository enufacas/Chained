#!/usr/bin/env python3
"""
Tests for Autonomous Issue Prioritizer

Comprehensive test suite for the multi-armed bandit issue prioritization system.

Author: @APIs-architect
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from issue_prioritizer import (
    IssuePrioritizer,
    IssueArm,
    PriorityLevel,
    IssuePriority
)


class TestIssueArm(unittest.TestCase):
    """Test the IssueArm class."""
    
    def test_arm_initialization(self):
        """Test arm initialization with defaults."""
        arm = IssueArm(category="bug")
        self.assertEqual(arm.category, "bug")
        self.assertEqual(arm.successes, 0)
        self.assertEqual(arm.failures, 0)
        self.assertEqual(arm.total_pulls, 0)
        self.assertEqual(arm.avg_resolution_time_hours, 0.0)
    
    def test_arm_update_success(self):
        """Test updating arm with successful outcome."""
        arm = IssueArm(category="bug")
        arm.update(success=True, resolution_time_hours=5.0)
        
        self.assertEqual(arm.successes, 1)
        self.assertEqual(arm.failures, 0)
        self.assertEqual(arm.total_pulls, 1)
        self.assertEqual(arm.avg_resolution_time_hours, 5.0)
        self.assertTrue(arm.last_updated)
    
    def test_arm_update_failure(self):
        """Test updating arm with failed outcome."""
        arm = IssueArm(category="feature")
        arm.update(success=False, resolution_time_hours=10.0)
        
        self.assertEqual(arm.successes, 0)
        self.assertEqual(arm.failures, 1)
        self.assertEqual(arm.total_pulls, 1)
        self.assertEqual(arm.avg_resolution_time_hours, 10.0)
    
    def test_arm_multiple_updates(self):
        """Test arm with multiple updates."""
        arm = IssueArm(category="documentation")
        
        arm.update(success=True, resolution_time_hours=2.0)
        arm.update(success=True, resolution_time_hours=3.0)
        arm.update(success=False, resolution_time_hours=1.0)
        
        self.assertEqual(arm.successes, 2)
        self.assertEqual(arm.failures, 1)
        self.assertEqual(arm.total_pulls, 3)
        # Moving average should be between 1.0 and 3.0
        self.assertGreater(arm.avg_resolution_time_hours, 1.0)
        self.assertLess(arm.avg_resolution_time_hours, 3.0)
    
    def test_arm_success_rate(self):
        """Test success rate calculation."""
        arm = IssueArm(category="bug")
        
        # No data yet - should return prior
        self.assertEqual(arm.success_rate, 0.5)
        
        # After some updates
        arm.update(success=True, resolution_time_hours=5.0)
        arm.update(success=True, resolution_time_hours=5.0)
        arm.update(success=False, resolution_time_hours=5.0)
        
        self.assertAlmostEqual(arm.success_rate, 2.0/3.0, places=2)
    
    def test_thompson_sampling(self):
        """Test Thompson Sampling returns valid probability."""
        arm = IssueArm(category="bug", successes=10, failures=5)
        
        # Sample multiple times
        samples = [arm.sample_thompson() for _ in range(100)]
        
        # All samples should be between 0 and 1
        self.assertTrue(all(0 <= s <= 1 for s in samples))
        
        # Mean should be roughly success_rate with some variance
        mean_sample = sum(samples) / len(samples)
        self.assertGreater(mean_sample, 0.5)  # More successes than failures
        self.assertLess(mean_sample, 0.9)     # But not perfect


class TestIssuePrioritizer(unittest.TestCase):
    """Test the IssuePrioritizer class."""
    
    def setUp(self):
        """Create temporary registry for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = os.path.join(self.temp_dir, "test_prioritizer.json")
        self.prioritizer = IssuePrioritizer(registry_path=self.registry_path)
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    # ==================== Initialization Tests ====================
    
    def test_initialization_creates_registry(self):
        """Test that initialization creates registry file."""
        self.assertTrue(os.path.exists(self.registry_path))
        
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        self.assertIn("version", registry)
        self.assertIn("arms", registry)
        self.assertIn("config", registry)
        self.assertIn("history", registry)
        self.assertIn("stats", registry)
    
    def test_initialization_creates_default_arms(self):
        """Test that default category arms are created."""
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        expected_categories = [
            "bug", "feature", "documentation", "refactoring",
            "security", "performance", "testing", "infrastructure",
            "ai-idea", "other"
        ]
        
        for category in expected_categories:
            self.assertIn(category, registry["arms"])
    
    # ==================== Categorization Tests ====================
    
    def test_categorize_issue_by_label(self):
        """Test issue categorization using labels."""
        result = self.prioritizer._categorize_issue(
            title="Some issue",
            body="",
            labels=["bug"]
        )
        self.assertEqual(result, "bug")
    
    def test_categorize_issue_by_title_bug(self):
        """Test categorization detects bugs from title."""
        result = self.prioritizer._categorize_issue(
            title="Fix critical bug in authentication",
            body=""
        )
        self.assertEqual(result, "bug")
    
    def test_categorize_issue_by_title_feature(self):
        """Test categorization detects features from title."""
        result = self.prioritizer._categorize_issue(
            title="Add new feature for user profiles",
            body=""
        )
        self.assertEqual(result, "feature")
    
    def test_categorize_issue_by_body_security(self):
        """Test categorization detects security issues."""
        result = self.prioritizer._categorize_issue(
            title="Important update",
            body="This is a security vulnerability that needs immediate attention"
        )
        self.assertEqual(result, "security")
    
    def test_categorize_issue_by_ai_idea(self):
        """Test categorization detects AI ideas."""
        result = self.prioritizer._categorize_issue(
            title="AI Idea: Autonomous code optimizer",
            body="AI-generated idea for improving performance"
        )
        self.assertEqual(result, "ai-idea")
    
    def test_categorize_issue_fallback_other(self):
        """Test categorization falls back to 'other' for unknown."""
        result = self.prioritizer._categorize_issue(
            title="Random nonsense xyz123",
            body="More random text that doesn't match patterns"
        )
        self.assertEqual(result, "other")
    
    # ==================== Prioritization Tests ====================
    
    def test_prioritize_issue_basic(self):
        """Test basic issue prioritization."""
        result = self.prioritizer.prioritize_issue(
            issue_number=123,
            title="Fix authentication bug",
            body="Users can't log in"
        )
        
        self.assertIsInstance(result, IssuePriority)
        self.assertEqual(result.issue_number, 123)
        self.assertEqual(result.category, "bug")
        self.assertIsInstance(result.priority, PriorityLevel)
        self.assertGreaterEqual(result.confidence, 0.1)  # At least minimum confidence
        self.assertLessEqual(result.confidence, 1.0)
        self.assertGreater(result.estimated_resolution_hours, 0.0)
        self.assertTrue(result.reasoning)
    
    def test_prioritize_issue_creates_new_category(self):
        """Test prioritization creates new category if needed."""
        result = self.prioritizer.prioritize_issue(
            issue_number=456,
            title="Random xyz nonsense unknown",
            body="More unknown content without patterns",
            labels=[]
        )
        
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        # Should fall back to "other" since no patterns match
        self.assertEqual(result.category, "other")
    
    def test_prioritize_issue_records_history(self):
        """Test that prioritization records decision history."""
        self.prioritizer.prioritize_issue(
            issue_number=789,
            title="Test issue",
            body=""
        )
        
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        self.assertEqual(len(registry["history"]), 1)
        self.assertEqual(registry["history"][0]["issue_number"], 789)
        self.assertEqual(registry["stats"]["total_decisions"], 1)
    
    def test_prioritize_issue_workload_adjustment(self):
        """Test that workload affects prioritization."""
        # With no workload
        result1 = self.prioritizer.prioritize_issue(
            issue_number=100,
            title="Fix bug",
            body="",
            current_open_issues=0
        )
        
        # With high workload
        result2 = self.prioritizer.prioritize_issue(
            issue_number=101,
            title="Fix bug",
            body="",
            current_open_issues=100
        )
        
        # Both should be bugs, but priorities might differ
        self.assertEqual(result1.category, "bug")
        self.assertEqual(result2.category, "bug")
    
    # ==================== Outcome Recording Tests ====================
    
    def test_record_outcome_success(self):
        """Test recording successful outcome."""
        # First prioritize
        result = self.prioritizer.prioritize_issue(
            issue_number=111,
            title="Fix bug",
            body=""
        )
        
        # Record success
        self.prioritizer.record_outcome(
            issue_number=111,
            category=result.category,
            success=True,
            resolution_time_hours=5.0
        )
        
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        arm = registry["arms"][result.category]
        self.assertEqual(arm["successes"], 1)
        self.assertEqual(arm["failures"], 0)
        self.assertEqual(arm["avg_resolution_time_hours"], 5.0)
    
    def test_record_outcome_failure(self):
        """Test recording failed outcome."""
        self.prioritizer.record_outcome(
            issue_number=222,
            category="bug",
            success=False,
            resolution_time_hours=10.0
        )
        
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        arm = registry["arms"]["bug"]
        self.assertEqual(arm["successes"], 0)
        self.assertEqual(arm["failures"], 1)
    
    def test_record_outcome_updates_global_stats(self):
        """Test that recording updates global statistics."""
        self.prioritizer.record_outcome(
            issue_number=333,
            category="feature",
            success=True,
            resolution_time_hours=12.0
        )
        
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        stats = registry["stats"]
        self.assertGreater(stats["total_decisions"], 0)
        self.assertEqual(stats["total_successes"], 1)
        self.assertGreater(stats["avg_resolution_time_hours"], 0)
    
    # ==================== Statistics Tests ====================
    
    def test_get_stats_empty(self):
        """Test getting stats with no data."""
        stats = self.prioritizer.get_stats()
        
        self.assertIn("overall", stats)
        self.assertIn("categories", stats)
        self.assertEqual(stats["overall"]["total_decisions"], 0)
    
    def test_get_stats_with_data(self):
        """Test getting stats after recording outcomes."""
        # Record several outcomes
        self.prioritizer.record_outcome(
            issue_number=1, category="bug",
            success=True, resolution_time_hours=5.0
        )
        self.prioritizer.record_outcome(
            issue_number=2, category="bug",
            success=True, resolution_time_hours=6.0
        )
        self.prioritizer.record_outcome(
            issue_number=3, category="feature",
            success=False, resolution_time_hours=20.0
        )
        
        stats = self.prioritizer.get_stats()
        
        # Check overall stats
        self.assertGreater(stats["overall"]["total_decisions"], 0)
        self.assertEqual(stats["overall"]["total_successes"], 2)
        self.assertEqual(stats["overall"]["total_failures"], 1)
        
        # Check category stats
        bug_stats = stats["categories"]["bug"]
        self.assertEqual(bug_stats["total_pulls"], 2)
        self.assertGreater(bug_stats["success_rate"], 0.9)  # Both succeeded
        
        feature_stats = stats["categories"]["feature"]
        self.assertEqual(feature_stats["total_pulls"], 1)
        self.assertLess(feature_stats["success_rate"], 0.1)  # Failed
    
    # ==================== Top Priorities Tests ====================
    
    def test_get_top_priorities_empty(self):
        """Test getting top priorities with no data."""
        top = self.prioritizer.get_top_priorities(n=5)
        
        self.assertIsInstance(top, list)
        self.assertGreater(len(top), 0)  # Should have default categories
        
        for item in top:
            self.assertIn("category", item)
            self.assertIn("sampled_priority", item)
            self.assertIn("success_rate", item)
    
    def test_get_top_priorities_with_data(self):
        """Test top priorities after recording outcomes."""
        # Make bugs very successful
        for i in range(10):
            self.prioritizer.record_outcome(
                issue_number=i,
                category="bug",
                success=True,
                resolution_time_hours=5.0
            )
        
        # Make features less successful
        for i in range(10, 15):
            self.prioritizer.record_outcome(
                issue_number=i,
                category="feature",
                success=False,
                resolution_time_hours=20.0
            )
        
        top = self.prioritizer.get_top_priorities(n=10)
        
        # Find bugs and features in results
        bug_idx = next(i for i, x in enumerate(top) if x["category"] == "bug")
        feature_idx = next(i for i, x in enumerate(top) if x["category"] == "feature")
        
        # Bugs should be prioritized higher (but Thompson Sampling adds randomness)
        # We can't guarantee order, but bug should have higher success rate
        bug_item = top[bug_idx]
        feature_item = top[feature_idx]
        
        self.assertGreater(bug_item["success_rate"], feature_item["success_rate"])
    
    def test_get_top_priorities_limit(self):
        """Test that top priorities respects limit."""
        top = self.prioritizer.get_top_priorities(n=3)
        self.assertEqual(len(top), 3)
    
    # ==================== Edge Cases ====================
    
    def test_history_pruning(self):
        """Test that history is pruned to prevent unbounded growth."""
        # Add more than 1000 decisions
        for i in range(1100):
            self.prioritizer.prioritize_issue(
                issue_number=i,
                title=f"Issue {i}",
                body=""
            )
        
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        # Should be pruned to 1000
        self.assertEqual(len(registry["history"]), 1000)
    
    def test_atomic_writes(self):
        """Test that registry writes are atomic."""
        # This is hard to test directly, but we can verify temp file cleanup
        self.prioritizer.prioritize_issue(
            issue_number=999,
            title="Test",
            body=""
        )
        
        temp_path = Path(self.registry_path).with_suffix('.tmp')
        self.assertFalse(temp_path.exists(), "Temp file should be cleaned up")
    
    def test_corrupted_registry_recovery(self):
        """Test recovery from corrupted registry."""
        # Write corrupted JSON
        with open(self.registry_path, 'w') as f:
            f.write("corrupted json {{{")
        
        # Should recover and reinitialize
        prioritizer = IssuePrioritizer(registry_path=self.registry_path)
        result = prioritizer.prioritize_issue(
            issue_number=888,
            title="Test after corruption",
            body=""
        )
        
        self.assertIsInstance(result, IssuePriority)


class TestPriorityLevel(unittest.TestCase):
    """Test PriorityLevel enum."""
    
    def test_priority_to_score(self):
        """Test converting priority levels to scores."""
        self.assertEqual(PriorityLevel.CRITICAL.to_score(), 1.0)
        self.assertEqual(PriorityLevel.HIGH.to_score(), 0.75)
        self.assertEqual(PriorityLevel.MEDIUM.to_score(), 0.5)
        self.assertEqual(PriorityLevel.LOW.to_score(), 0.25)
    
    def test_priority_ordering(self):
        """Test that priority scores are properly ordered."""
        critical = PriorityLevel.CRITICAL.to_score()
        high = PriorityLevel.HIGH.to_score()
        medium = PriorityLevel.MEDIUM.to_score()
        low = PriorityLevel.LOW.to_score()
        
        self.assertGreater(critical, high)
        self.assertGreater(high, medium)
        self.assertGreater(medium, low)


if __name__ == '__main__':
    unittest.main()
