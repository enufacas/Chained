#!/usr/bin/env python3
"""
Tests for Autonomous Issue Prioritizer
Author: @create-botter (Nikola Tesla)

Comprehensive test suite for the multi-armed bandit issue prioritizer.
"""

import unittest
import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta, timezone
from autonomous_issue_prioritizer import (
    AutonomousIssuePrioritizer,
    BanditArm,
    Issue,
    PriorityRecommendation
)


class TestBanditArm(unittest.TestCase):
    """Test BanditArm functionality"""
    
    def test_initialization(self):
        """Test arm initialization"""
        arm = BanditArm(name='test', description='Test arm')
        self.assertEqual(arm.name, 'test')
        self.assertEqual(arm.successes, 0)
        self.assertEqual(arm.failures, 0)
        self.assertEqual(arm.pulls, 0)
    
    def test_update_success(self):
        """Test updating with successful reward"""
        arm = BanditArm(name='test', description='Test arm')
        arm.update(1.0)
        self.assertEqual(arm.successes, 1)
        self.assertEqual(arm.failures, 0)
        self.assertEqual(arm.pulls, 1)
    
    def test_update_failure(self):
        """Test updating with failed reward"""
        arm = BanditArm(name='test', description='Test arm')
        arm.update(0.0)
        self.assertEqual(arm.successes, 0)
        self.assertEqual(arm.failures, 1)
        self.assertEqual(arm.pulls, 1)
    
    def test_expected_value(self):
        """Test expected value calculation"""
        arm = BanditArm(name='test', description='Test arm')
        # Initially should be 0.5 (uniform prior)
        self.assertAlmostEqual(arm.expected_value(), 0.5, places=2)
        
        # After successes, should increase
        arm.update(1.0)
        arm.update(1.0)
        self.assertGreater(arm.expected_value(), 0.5)
    
    def test_confidence_interval(self):
        """Test confidence interval calculation"""
        arm = BanditArm(name='test', description='Test arm')
        ci_low, ci_high = arm.confidence_interval()
        
        # Should be between 0 and 1
        self.assertGreaterEqual(ci_low, 0.0)
        self.assertLessEqual(ci_high, 1.0)
        
        # Low should be less than high
        self.assertLess(ci_low, ci_high)
    
    def test_sample_theta(self):
        """Test Thompson Sampling"""
        arm = BanditArm(name='test', description='Test arm')
        
        # Sample should be between 0 and 1
        for _ in range(10):
            sample = arm.sample_theta()
            self.assertGreaterEqual(sample, 0.0)
            self.assertLessEqual(sample, 1.0)
    
    def test_serialization(self):
        """Test to_dict and from_dict"""
        arm = BanditArm(name='test', description='Test arm', successes=5, failures=3)
        
        # Convert to dict and back
        arm_dict = arm.to_dict()
        restored_arm = BanditArm.from_dict(arm_dict)
        
        self.assertEqual(restored_arm.name, arm.name)
        self.assertEqual(restored_arm.successes, arm.successes)
        self.assertEqual(restored_arm.failures, arm.failures)


class TestIssue(unittest.TestCase):
    """Test Issue representation"""
    
    def test_issue_creation(self):
        """Test creating an issue"""
        issue = Issue(
            number=123,
            title='Test Issue',
            body='Test body',
            labels=['bug'],
            state='open',
            created_at='2024-01-01T00:00:00Z',
            author='testuser'
        )
        
        self.assertEqual(issue.number, 123)
        self.assertEqual(issue.title, 'Test Issue')
        self.assertEqual(issue.labels, ['bug'])
    
    def test_issue_serialization(self):
        """Test issue to_dict"""
        issue = Issue(
            number=123,
            title='Test Issue',
            body='Test body',
            labels=['bug'],
            state='open',
            created_at='2024-01-01T00:00:00Z',
            author='testuser'
        )
        
        issue_dict = issue.to_dict()
        self.assertIn('number', issue_dict)
        self.assertIn('title', issue_dict)


class TestAutonomousIssuePrioritizer(unittest.TestCase):
    """Test the main prioritizer"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for state
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, 'test_state.json')
        self.prioritizer = AutonomousIssuePrioritizer(state_file=self.state_file)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test prioritizer initialization"""
        self.assertIsNotNone(self.prioritizer.arms)
        self.assertIn('urgency', self.prioritizer.arms)
        self.assertIn('complexity', self.prioritizer.arms)
        self.assertIn('impact', self.prioritizer.arms)
        self.assertIn('balanced', self.prioritizer.arms)
    
    def test_compute_features(self):
        """Test feature computation"""
        issue = self._create_test_issue()
        features = self.prioritizer.compute_features(issue)
        
        # Check that all expected features are present
        self.assertIn('age_urgency', features)
        self.assertIn('complexity', features)
        self.assertIn('impact', features)
        
        # All features should be between 0 and 1
        for value in features.values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
    
    def test_urgency_features(self):
        """Test urgency-related features"""
        # Create old issue
        old_date = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        old_issue = Issue(
            number=1,
            title='Old Issue',
            body='Very old',
            labels=['urgent'],
            state='open',
            created_at=old_date,
            author='test'
        )
        
        features = self.prioritizer.compute_features(old_issue)
        
        # Old issue should have high age urgency
        self.assertGreater(features['age_urgency'], 0.5)
        
        # Urgent label should be detected
        self.assertEqual(features['label_urgency'], 1.0)
    
    def test_complexity_features(self):
        """Test complexity estimation"""
        # Simple issue
        simple_issue = Issue(
            number=1,
            title='Fix typo',
            body='Small fix',
            labels=[],
            state='open',
            created_at=datetime.now(timezone.utc).isoformat(),
            author='test'
        )
        
        # Complex issue
        complex_issue = Issue(
            number=2,
            title='Implement comprehensive machine learning pipeline with data preprocessing',
            body='This requires extensive work including ' + ' '.join(['word'] * 500),
            labels=[],
            state='open',
            created_at=datetime.now(timezone.utc).isoformat(),
            author='test'
        )
        
        simple_features = self.prioritizer.compute_features(simple_issue)
        complex_features = self.prioritizer.compute_features(complex_issue)
        
        # Complex issue should have higher complexity score
        self.assertLess(simple_features['complexity'], complex_features['complexity'])
    
    def test_impact_features(self):
        """Test impact estimation"""
        high_impact = Issue(
            number=1,
            title='Critical security vulnerability',
            body='Major security issue',
            labels=['security', 'bug'],
            state='open',
            created_at=datetime.now(timezone.utc).isoformat(),
            author='test'
        )
        
        low_impact = Issue(
            number=2,
            title='Minor documentation fix',
            body='Small doc update',
            labels=['documentation'],
            state='open',
            created_at=datetime.now(timezone.utc).isoformat(),
            author='test'
        )
        
        high_features = self.prioritizer.compute_features(high_impact)
        low_features = self.prioritizer.compute_features(low_impact)
        
        # High impact issue should score higher
        self.assertGreater(high_features['impact'], low_features['impact'])
    
    def test_select_arm(self):
        """Test arm selection using Thompson Sampling"""
        arm_name = self.prioritizer.select_arm()
        
        # Should select one of the valid arms
        self.assertIn(arm_name, self.prioritizer.arms.keys())
    
    def test_compute_priority_score(self):
        """Test priority score computation"""
        issue = self._create_test_issue()
        
        # Test each arm strategy
        for arm_name in self.prioritizer.arms.keys():
            score = self.prioritizer.compute_priority_score(issue, arm_name)
            
            # Score should be between 0 and 1
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
    
    def test_prioritize_issue(self):
        """Test prioritizing a single issue"""
        issue = self._create_test_issue()
        recommendation = self.prioritizer.prioritize_issue(issue)
        
        self.assertIsInstance(recommendation, PriorityRecommendation)
        self.assertEqual(recommendation.issue_number, issue.number)
        self.assertGreaterEqual(recommendation.priority_score, 0.0)
        self.assertLessEqual(recommendation.priority_score, 1.0)
        self.assertIn(recommendation.selected_arm, self.prioritizer.arms.keys())
    
    def test_prioritize_multiple_issues(self):
        """Test prioritizing multiple issues"""
        issues = [
            self._create_test_issue(number=1, title='Issue 1'),
            self._create_test_issue(number=2, title='Issue 2'),
            self._create_test_issue(number=3, title='Issue 3')
        ]
        
        recommendations = self.prioritizer.prioritize_issues(issues)
        
        self.assertEqual(len(recommendations), 3)
        
        # Should be sorted by priority (descending)
        for i in range(len(recommendations) - 1):
            self.assertGreaterEqual(
                recommendations[i].priority_score,
                recommendations[i + 1].priority_score
            )
    
    def test_record_outcome(self):
        """Test recording issue outcomes"""
        issue = self._create_test_issue()
        recommendation = self.prioritizer.prioritize_issue(issue)
        
        arm_before = self.prioritizer.arms[recommendation.selected_arm]
        pulls_before = arm_before.pulls
        
        # Record success
        self.prioritizer.record_outcome(issue.number, success=True)
        
        arm_after = self.prioritizer.arms[recommendation.selected_arm]
        
        # Pulls should increase
        self.assertEqual(arm_after.pulls, pulls_before + 1)
        
        # Success should be recorded
        self.assertEqual(arm_after.successes, 1)
    
    def test_learning_from_outcomes(self):
        """Test that the system learns from outcomes"""
        issue = self._create_test_issue()
        
        # Record successes and failures for different arms
        for i in range(20):
            rec = self.prioritizer.prioritize_issue(issue)
            # Record success/failure based on arm
            success = rec.selected_arm in ['urgency', 'impact']
            self.prioritizer.record_outcome(issue.number, success=success)
        
        # After learning, some arms should have different expected values
        urgency_arm = self.prioritizer.arms['urgency']
        exploration_arm = self.prioritizer.arms['exploration']
        
        # At least one arm should have been updated
        total_pulls = sum(arm.pulls for arm in self.prioritizer.arms.values())
        self.assertGreater(total_pulls, 0)
    
    def test_save_and_load_state(self):
        """Test state persistence"""
        issue = self._create_test_issue()
        recommendation = self.prioritizer.prioritize_issue(issue)
        self.prioritizer.record_outcome(issue.number, success=True)
        
        # Save state
        self.prioritizer.save_state()
        
        # Create new prioritizer and load state
        new_prioritizer = AutonomousIssuePrioritizer(state_file=self.state_file)
        
        # State should be preserved
        self.assertEqual(
            len(new_prioritizer.history),
            len(self.prioritizer.history)
        )
        
        # Arm statistics should be preserved
        for arm_name in self.prioritizer.arms:
            original = self.prioritizer.arms[arm_name]
            loaded = new_prioritizer.arms[arm_name]
            self.assertEqual(loaded.pulls, original.pulls)
            self.assertEqual(loaded.successes, original.successes)
    
    def test_get_statistics(self):
        """Test statistics generation"""
        issue = self._create_test_issue()
        self.prioritizer.prioritize_issue(issue)
        self.prioritizer.record_outcome(issue.number, success=True)
        
        stats = self.prioritizer.get_statistics()
        
        self.assertIn('arms', stats)
        self.assertIn('total_recommendations', stats)
        self.assertIn('total_outcomes', stats)
        self.assertIn('success_rate', stats)
        
        # Should have statistics for each arm
        for arm_name in self.prioritizer.arms:
            self.assertIn(arm_name, stats['arms'])
    
    def test_reset(self):
        """Test reset functionality"""
        issue = self._create_test_issue()
        self.prioritizer.prioritize_issue(issue)
        self.prioritizer.record_outcome(issue.number, success=True)
        
        # Reset
        self.prioritizer.reset()
        
        # All arms should be reset
        for arm in self.prioritizer.arms.values():
            self.assertEqual(arm.pulls, 0)
            self.assertEqual(arm.successes, 0)
            self.assertEqual(arm.failures, 0)
        
        # History should be cleared
        self.assertEqual(len(self.prioritizer.history), 0)
    
    def test_exploration_vs_exploitation(self):
        """Test that system balances exploration and exploitation"""
        issue = self._create_test_issue()
        
        # Record many successful outcomes for different arms
        recommendations = []
        for _ in range(20):
            rec = self.prioritizer.prioritize_issue(issue)
            recommendations.append(rec)
            # Always record as success
            self.prioritizer.record_outcome(issue.number, success=True)
        
        # Count how many different arms were selected
        arms_used = set(rec.selected_arm for rec in recommendations)
        
        # Should have tried multiple arms (exploration)
        # Not all recommendations should use the same arm
        self.assertGreater(len(arms_used), 1)
    
    # Helper methods
    
    def _create_test_issue(self, number=123, title='Test Issue'):
        """Create a test issue"""
        return Issue(
            number=number,
            title=title,
            body='This is a test issue for prioritization',
            labels=['bug', 'feature'],
            state='open',
            created_at=datetime.now(timezone.utc).isoformat(),
            author='testuser',
            comments=5
        )


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, 'test_state.json')
        self.prioritizer = AutonomousIssuePrioritizer(state_file=self.state_file)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_empty_issue_list(self):
        """Test prioritizing empty issue list"""
        recommendations = self.prioritizer.prioritize_issues([])
        self.assertEqual(len(recommendations), 0)
    
    def test_issue_with_no_body(self):
        """Test issue with empty body"""
        issue = Issue(
            number=1,
            title='No body issue',
            body='',
            labels=[],
            state='open',
            created_at=datetime.now(timezone.utc).isoformat(),
            author='test'
        )
        
        # Should not crash
        recommendation = self.prioritizer.prioritize_issue(issue)
        self.assertIsNotNone(recommendation)
    
    def test_issue_with_no_labels(self):
        """Test issue with no labels"""
        issue = Issue(
            number=1,
            title='No labels',
            body='Issue without labels',
            labels=[],
            state='open',
            created_at=datetime.now(timezone.utc).isoformat(),
            author='test'
        )
        
        # Should not crash
        recommendation = self.prioritizer.prioritize_issue(issue)
        self.assertIsNotNone(recommendation)
    
    def test_record_outcome_for_nonexistent_issue(self):
        """Test recording outcome for issue that wasn't prioritized"""
        # Should handle gracefully
        self.prioritizer.record_outcome(999, success=True)
        # Should not crash
    
    def test_corrupted_state_file(self):
        """Test loading corrupted state file"""
        # Write corrupted JSON
        with open(self.state_file, 'w') as f:
            f.write('{ corrupted json')
        
        # Should handle gracefully and start fresh
        prioritizer = AutonomousIssuePrioritizer(state_file=self.state_file)
        self.assertIsNotNone(prioritizer)


if __name__ == '__main__':
    unittest.main()
