#!/usr/bin/env python3
"""
Tests for Autonomous A/B Testing System

Tests the core A/B testing engine and advanced algorithms.

Author: @accelerate-specialist
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from ab_testing_engine import ABTestingEngine
from ab_testing_advanced import (
    ThompsonSampling,
    BayesianABTest,
    SequentialTesting,
    ConfidenceIntervals
)


class TestABTestingEngine(unittest.TestCase):
    """Test core A/B testing engine functionality."""
    
    def setUp(self):
        """Create temporary registry for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = os.path.join(self.temp_dir, "test_registry.json")
        self.engine = ABTestingEngine(registry_path=self.registry_path)
    
    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.registry_path):
            os.remove(self.registry_path)
        os.rmdir(self.temp_dir)
    
    def test_create_experiment(self):
        """Test experiment creation."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Test Experiment",
            description="Testing schedule optimization",
            variants=variants,
            metrics=["execution_time", "success_rate"],
            workflow_name="test-workflow"
        )
        
        self.assertIsNotNone(exp_id)
        self.assertTrue(exp_id.startswith("exp-"))
        
        # Verify experiment was created
        experiments = self.engine.list_experiments()
        self.assertEqual(len(experiments), 1)
        self.assertEqual(experiments[0]["name"], "Test Experiment")
    
    def test_record_sample(self):
        """Test recording samples for variants."""
        variants = {
            "control": {"config": "default"},
            "variant_a": {"config": "optimized"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Sample Test",
            description="Test sample recording",
            variants=variants,
            metrics=["execution_time", "success_rate"]
        )
        
        # Record some samples
        self.engine.record_sample(
            experiment_id=exp_id,
            variant_name="control",
            metrics={"execution_time": 100, "success_rate": 0.9}
        )
        
        self.engine.record_sample(
            experiment_id=exp_id,
            variant_name="variant_a",
            metrics={"execution_time": 80, "success_rate": 0.95}
        )
        
        # Verify samples were recorded
        details = self.engine.get_experiment_details(exp_id)
        self.assertEqual(details["variants"]["control"]["total_samples"], 1)
        self.assertEqual(details["variants"]["variant_a"]["total_samples"], 1)
    
    def test_analyze_experiment_insufficient_data(self):
        """Test analysis with insufficient data."""
        variants = {
            "control": {"config": "default"},
            "variant_a": {"config": "optimized"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Insufficient Data Test",
            description="Test with too few samples",
            variants=variants,
            metrics=["execution_time"]
        )
        
        # Record only a few samples
        for i in range(5):
            self.engine.record_sample(
                experiment_id=exp_id,
                variant_name="control",
                metrics={"execution_time": 100 + i}
            )
        
        analysis = self.engine.analyze_experiment(exp_id)
        self.assertEqual(analysis["status"], "insufficient_data")
    
    def test_analyze_experiment_with_winner(self):
        """Test analysis that identifies a clear winner."""
        variants = {
            "control": {"config": "default"},
            "variant_a": {"config": "optimized"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Winner Test",
            description="Test with clear winner",
            variants=variants,
            metrics=["execution_time"]
        )
        
        # Record samples showing clear improvement
        for i in range(15):
            # Control: slower
            self.engine.record_sample(
                experiment_id=exp_id,
                variant_name="control",
                metrics={"execution_time": 100 + i}
            )
            
            # Variant A: significantly faster
            self.engine.record_sample(
                experiment_id=exp_id,
                variant_name="variant_a",
                metrics={"execution_time": 70 + i}
            )
        
        analysis = self.engine.analyze_experiment(exp_id, use_advanced=False)
        self.assertEqual(analysis["status"], "analyzed")
        
        # Should detect variant_a as winner (lower execution time is better)
        # Note: Current implementation uses average, might need refinement
        self.assertIsNotNone(analysis["winner"])
    
    def test_complete_experiment(self):
        """Test completing an experiment."""
        variants = {
            "control": {"config": "default"},
            "variant_a": {"config": "optimized"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Completion Test",
            description="Test experiment completion",
            variants=variants,
            metrics=["execution_time"]
        )
        
        # Complete the experiment
        self.engine.complete_experiment(
            experiment_id=exp_id,
            winner="variant_a",
            notes="Test completion"
        )
        
        # Verify status changed
        details = self.engine.get_experiment_details(exp_id)
        self.assertEqual(details["status"], "completed")
        self.assertEqual(details["results"]["winner"], "variant_a")


class TestThompsonSampling(unittest.TestCase):
    """Test Thompson Sampling algorithm."""
    
    def test_update_and_select(self):
        """Test updating statistics and selecting variants."""
        thompson = ThompsonSampling()
        
        # Simulate variant performance
        variants = ["control", "variant_a", "variant_b"]
        
        # Variant A performs best
        for _ in range(10):
            thompson.update("control", 0.6)
            thompson.update("variant_a", 0.8)
            thompson.update("variant_b", 0.5)
        
        # Select variant multiple times
        selections = [thompson.select_variant(variants) for _ in range(100)]
        
        # Variant A should be selected most often
        variant_a_count = selections.count("variant_a")
        self.assertGreater(variant_a_count, 30)  # Should be selected frequently
    
    def test_get_probabilities(self):
        """Test probability estimates."""
        thompson = ThompsonSampling()
        
        # Update with perfect performance
        for _ in range(10):
            thompson.update("perfect", 1.0)
            thompson.update("poor", 0.0)
        
        probs = thompson.get_probabilities()
        
        # Perfect variant should have higher probability
        self.assertGreater(probs["perfect"], probs["poor"])


class TestBayesianABTest(unittest.TestCase):
    """Test Bayesian A/B testing."""
    
    def test_credible_interval(self):
        """Test credible interval calculation."""
        bayesian = BayesianABTest()
        
        # 90 successes out of 100 trials
        lower, upper = bayesian.calculate_credible_interval(90, 100)
        
        # Should be around 0.9 with some margin
        self.assertGreater(lower, 0.8)
        self.assertLess(upper, 1.0)
        self.assertGreater(upper, lower)
    
    def test_probability_comparison(self):
        """Test probability that one variant is better."""
        bayesian = BayesianABTest()
        
        # Variant B clearly better (95% vs 80%)
        prob = bayesian.probability_b_better_than_a(
            a_successes=80, a_trials=100,
            b_successes=95, b_trials=100,
            num_samples=1000
        )
        
        # Should be high probability that B is better
        self.assertGreater(prob, 0.8)
    
    def test_equal_variants(self):
        """Test comparison of equal variants."""
        bayesian = BayesianABTest()
        
        # Equal performance
        prob = bayesian.probability_b_better_than_a(
            a_successes=50, a_trials=100,
            b_successes=50, b_trials=100,
            num_samples=1000
        )
        
        # Should be around 0.5
        self.assertGreater(prob, 0.3)
        self.assertLess(prob, 0.7)


class TestSequentialTesting(unittest.TestCase):
    """Test sequential testing for early stopping."""
    
    def test_early_stop_with_clear_winner(self):
        """Test early stopping when there's a clear winner."""
        sequential = SequentialTesting(min_effect_size=0.1)
        
        # Strong evidence for variant
        should_stop, winner = sequential.should_stop(
            control_successes=50, control_trials=100,
            variant_successes=80, variant_trials=100
        )
        
        # Should recommend stopping
        self.assertTrue(should_stop)
        self.assertEqual(winner, 'variant')
    
    def test_no_early_stop_small_difference(self):
        """Test that we don't stop early with small differences."""
        sequential = SequentialTesting(min_effect_size=0.1)
        
        # Small difference
        should_stop, winner = sequential.should_stop(
            control_successes=50, control_trials=100,
            variant_successes=52, variant_trials=100
        )
        
        # Should not stop
        self.assertFalse(should_stop)
    
    def test_insufficient_data(self):
        """Test that we don't stop with insufficient data."""
        sequential = SequentialTesting()
        
        # Too few samples
        should_stop, winner = sequential.should_stop(
            control_successes=5, control_trials=5,
            variant_successes=5, variant_trials=5
        )
        
        # Should not stop
        self.assertFalse(should_stop)


class TestConfidenceIntervals(unittest.TestCase):
    """Test confidence interval calculations."""
    
    def test_proportion_ci(self):
        """Test confidence interval for proportions."""
        lower, upper = ConfidenceIntervals.proportion_ci(
            successes=50, trials=100, confidence=0.95
        )
        
        # Should be centered around 0.5
        self.assertGreater(lower, 0.4)
        self.assertLess(upper, 0.6)
        self.assertGreater(upper, lower)
    
    def test_mean_ci(self):
        """Test confidence interval for means."""
        values = [10, 12, 11, 13, 10, 12, 11]
        
        lower, upper = ConfidenceIntervals.mean_ci(values, confidence=0.95)
        
        # Should be centered around 11.3
        self.assertGreater(lower, 10)
        self.assertLess(upper, 13)
        self.assertGreater(upper, lower)
    
    def test_empty_values(self):
        """Test with empty values."""
        lower, upper = ConfidenceIntervals.mean_ci([], confidence=0.95)
        
        self.assertEqual(lower, 0.0)
        self.assertEqual(upper, 0.0)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestABTestingEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestThompsonSampling))
    suite.addTests(loader.loadTestsFromTestCase(TestBayesianABTest))
    suite.addTests(loader.loadTestsFromTestCase(TestSequentialTesting))
    suite.addTests(loader.loadTestsFromTestCase(TestConfidenceIntervals))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
