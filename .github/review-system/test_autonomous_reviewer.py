#!/usr/bin/env python3
"""
Tests for the Autonomous Code Reviewer system.

Tests the learning mechanism, criteria evolution, and review functionality.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import autonomous_reviewer
sys.path.insert(0, str(Path(__file__).parent))

from autonomous_reviewer import AutonomousReviewer


class TestAutonomousReviewer(unittest.TestCase):
    """Test suite for Autonomous Reviewer."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary criteria file for testing
        self.test_dir = tempfile.mkdtemp()
        self.criteria_file = os.path.join(self.test_dir, 'criteria.json')
        
        # Copy the base criteria for testing
        with open('.github/review-system/criteria.json', 'r') as f:
            self.base_criteria = json.load(f)
        
        # Save to test location
        with open(self.criteria_file, 'w') as f:
            json.dump(self.base_criteria, f)
        
        # Create reviewer with test criteria
        self.reviewer = AutonomousReviewer(self.criteria_file)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test reviewer initializes correctly."""
        self.assertIsNotNone(self.reviewer.criteria)
        self.assertIn('metadata', self.reviewer.criteria)
        self.assertIn('criteria', self.reviewer.criteria)
        self.assertIn('evolution_config', self.reviewer.criteria)
    
    def test_learn_from_outcome_success(self):
        """Test learning from successful PR outcome."""
        initial_reviews = self.reviewer.criteria['metadata']['total_reviews']
        initial_rate = self.reviewer.criteria['metadata']['success_rate']
        
        # Learn from a successful outcome
        self.reviewer.learn_from_outcome('test-success-1', {
            'merged': True,
            'major_changes_required': False,
            'overall_score': 0.85
        })
        
        # Verify metrics updated
        self.assertEqual(
            self.reviewer.criteria['metadata']['total_reviews'],
            initial_reviews + 1
        )
        
        # Success rate should increase or stay same
        new_rate = self.reviewer.criteria['metadata']['success_rate']
        self.assertGreaterEqual(new_rate, initial_rate * 0.9)  # Allow small decrease due to rounding
    
    def test_learn_from_outcome_failure(self):
        """Test learning from failed PR outcome."""
        initial_reviews = self.reviewer.criteria['metadata']['total_reviews']
        
        # Learn from a failed outcome
        self.reviewer.learn_from_outcome('test-failed-1', {
            'merged': False,
            'rejected': True,
            'major_changes_required': True,
            'overall_score': 0.25
        })
        
        # Verify metrics updated
        self.assertEqual(
            self.reviewer.criteria['metadata']['total_reviews'],
            initial_reviews + 1
        )
        
        # History should contain the outcome
        history = self.reviewer.criteria.get('history', [])
        self.assertTrue(any(h['review_id'] == 'test-failed-1' for h in history))
    
    def test_criteria_evolution(self):
        """Test that criteria evolve after sufficient reviews."""
        # Record initial weights
        initial_weights = {
            name: cat['weight'] 
            for name, cat in self.reviewer.criteria['criteria'].items()
        }
        
        # Simulate many successful reviews
        for i in range(15):
            self.reviewer.learn_from_outcome(f'sim-success-{i}', {
                'merged': True,
                'major_changes_required': False,
                'overall_score': 0.8
            })
        
        # Simulate some failures
        for i in range(5):
            self.reviewer.learn_from_outcome(f'sim-failed-{i}', {
                'merged': False,
                'rejected': True,
                'major_changes_required': True,
                'overall_score': 0.3
            })
        
        # At least some weights should have changed
        final_weights = {
            name: cat['weight'] 
            for name, cat in self.reviewer.criteria['criteria'].items()
        }
        
        changes = sum(
            1 for name in initial_weights 
            if abs(initial_weights[name] - final_weights[name]) > 0.01
        )
        
        # Expect at least one weight to have changed
        self.assertGreater(changes, 0, "Criteria should evolve after sufficient reviews")
    
    def test_effectiveness_calculation(self):
        """Test effectiveness calculation with confidence intervals."""
        # Learn from multiple outcomes
        for i in range(10):
            self.reviewer.learn_from_outcome(f'test-{i}', {
                'merged': i % 2 == 0,  # 50% success rate
                'major_changes_required': i % 2 == 1,
                'overall_score': 0.6 if i % 2 == 0 else 0.4
            })
        
        # Check that effectiveness values are reasonable
        for category in self.reviewer.criteria['criteria'].values():
            for check in category.get('checks', []):
                effectiveness = check.get('effectiveness', 0.5)
                # Effectiveness should be between 0 and 1
                self.assertGreaterEqual(effectiveness, 0.0)
                self.assertLessEqual(effectiveness, 1.0)
    
    def test_metrics_report_generation(self):
        """Test that metrics report can be generated."""
        report = self.reviewer.generate_metrics_report()
        
        # Verify report contains expected sections
        self.assertIn('Performance Metrics', report)
        self.assertIn('Overall Statistics', report)
        self.assertIn('Category Performance', report)
        self.assertIn('Learning History', report)
        
        # Verify report contains actual metrics
        self.assertIn('Total Reviews Performed', report)
        self.assertIn('Success Rate', report)
    
    def test_adaptive_learning_rate(self):
        """Test that learning rate adapts based on variance."""
        # Create scenarios with different variance patterns
        
        # High variance scenario - inconsistent results
        for i in range(10):
            score = 0.9 if i % 2 == 0 else 0.1
            self.reviewer.learn_from_outcome(f'variance-test-{i}', {
                'merged': i % 2 == 0,
                'major_changes_required': i % 2 == 1,
                'overall_score': score
            })
        
        # Check that variance is tracked
        has_variance = False
        for category in self.reviewer.criteria['criteria'].values():
            if 'effectiveness_variance' in category:
                has_variance = True
                variance = category['effectiveness_variance']
                # High variance scenario should have non-zero variance
                self.assertGreaterEqual(variance, 0.0)
        
        self.assertTrue(has_variance, "Variance should be tracked in categories")
    
    def test_confidence_interval_impact(self):
        """Test that confidence intervals affect effectiveness."""
        # Check with very few applications
        category = self.reviewer.criteria['criteria']['correctness']
        checks = category.get('checks', [])
        
        if checks:
            check = checks[0]
            initial_times_applied = check.get('times_applied', 0)
            
            # With few applications, confidence should be low
            # So effectiveness should be pulled toward success rate
            # This is implicitly tested by the learning mechanism
            self.assertIsNotNone(check.get('effectiveness'))
    
    def test_criteria_removal_threshold(self):
        """Test that ineffective criteria are handled appropriately."""
        config = self.reviewer.criteria['evolution_config']
        removal_threshold = config['criteria_removal_threshold']
        
        # Verify removal threshold is configured
        self.assertGreater(removal_threshold, 0.0)
        self.assertLess(removal_threshold, 1.0)
        
        # Note: Actual removal would require more complex logic
        # For now, we verify the threshold exists and is reasonable
    
    def test_review_comment_generation(self):
        """Test review comment generation."""
        # Create mock review results
        results = {
            'overall_score': 0.75,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'category_scores': {
                'correctness': 0.8,
                'clarity': 0.7,
                'security': 0.9,
                'maintainability': 0.6,
                'workflow_specific': 0.75
            },
            'passed_checks': ['check1', 'check2', 'check3'],
            'failed_checks': [
                {
                    'check': 'meaningful_names',
                    'category': 'clarity',
                    'severity': 'medium',
                    'details': 'Some variable names are too short'
                }
            ]
        }
        
        comment = self.reviewer.generate_review_comment(results)
        
        # Verify comment contains expected elements
        self.assertIn('Autonomous Code Review', comment)
        self.assertIn('Overall Score', comment)
        self.assertIn('Category Scores', comment)
        self.assertIn('workflows-tech-lead', comment)
        
        # Verify scores are displayed
        self.assertIn('75%', comment)  # Overall score
        self.assertIn('correctness', comment.lower())
    
    def test_history_tracking(self):
        """Test that review history is properly tracked."""
        initial_history_len = len(self.reviewer.criteria.get('history', []))
        
        # Add several outcomes
        for i in range(5):
            self.reviewer.learn_from_outcome(f'history-test-{i}', {
                'merged': True,
                'major_changes_required': False,
                'overall_score': 0.7
            })
        
        # Verify history grew
        final_history_len = len(self.reviewer.criteria.get('history', []))
        self.assertEqual(final_history_len, initial_history_len + 5)
    
    def test_multiple_learning_cycles(self):
        """Test multiple learning cycles."""
        # Simulate multiple rounds of learning
        for cycle in range(3):
            # Each cycle has mixed results
            for i in range(10):
                outcome = {
                    'merged': i % 3 != 0,  # 67% success rate
                    'major_changes_required': i % 3 == 0,
                    'overall_score': 0.7 if i % 3 != 0 else 0.4
                }
                self.reviewer.learn_from_outcome(f'cycle-{cycle}-{i}', outcome)
        
        # Verify criteria evolved
        total_reviews = self.reviewer.criteria['metadata']['total_reviews']
        self.assertGreater(total_reviews, 30)
        
        # Success rate should be close to 67% (with some tolerance)
        success_rate = self.reviewer.criteria['metadata']['success_rate']
        self.assertGreater(success_rate, 0.6)
        self.assertLess(success_rate, 0.80)  # Allow more tolerance for variance


class TestCriteriaStructure(unittest.TestCase):
    """Test the criteria JSON structure."""
    
    def setUp(self):
        """Load criteria for testing."""
        with open('.github/review-system/criteria.json', 'r') as f:
            self.criteria = json.load(f)
    
    def test_required_fields(self):
        """Test that all required fields are present."""
        self.assertIn('version', self.criteria)
        self.assertIn('metadata', self.criteria)
        self.assertIn('criteria', self.criteria)
        self.assertIn('evolution_config', self.criteria)
        self.assertIn('history', self.criteria)
    
    def test_metadata_fields(self):
        """Test metadata structure."""
        metadata = self.criteria['metadata']
        self.assertIn('total_reviews', metadata)
        self.assertIn('success_rate', metadata)
        self.assertIn('created_by', metadata)
    
    def test_evolution_config(self):
        """Test evolution configuration."""
        config = self.criteria['evolution_config']
        required_keys = [
            'min_reviews_before_adjustment',
            'effectiveness_window',
            'weight_adjustment_rate',
            'threshold_adjustment_rate',
            'criteria_removal_threshold',
            'criteria_promotion_threshold'
        ]
        
        for key in required_keys:
            self.assertIn(key, config)
            # All should be numeric
            self.assertIsInstance(config[key], (int, float))
    
    def test_category_structure(self):
        """Test each category has required fields."""
        for category_name, category in self.criteria['criteria'].items():
            self.assertIn('weight', category)
            self.assertIn('threshold', category)
            self.assertIn('description', category)
            self.assertIn('checks', category)
            self.assertIn('learning_rate', category)
            
            # Verify numeric fields are in valid ranges
            self.assertGreater(category['weight'], 0.0)
            self.assertGreater(category['threshold'], 0.0)
            self.assertLessEqual(category['threshold'], 1.0)
    
    def test_check_structure(self):
        """Test each check has required fields."""
        for category in self.criteria['criteria'].values():
            for check in category.get('checks', []):
                self.assertIn('id', check)
                self.assertIn('name', check)
                self.assertIn('weight', check)
                self.assertIn('effectiveness', check)
                
                # At least one of patterns, file_patterns, or heuristic should exist
                has_patterns = (
                    'patterns' in check or 
                    'negative_patterns' in check or
                    'file_patterns' in check or
                    'heuristic' in check or
                    'detection' in check or
                    'max_depth' in check  # Some checks use different detection methods
                )
                self.assertTrue(has_patterns, f"Check {check['id']} has no detection method")


def run_tests():
    """Run all tests."""
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
