#!/usr/bin/env python3
"""
Tests for RL Resource Optimizer
Created by @create-botter

Comprehensive test suite for the reinforcement learning-based
GitHub Actions resource optimizer.
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from rl_resource_optimizer import (
    RLResourceOptimizer,
    ResourceState,
    ResourceAction,
    ResourceExperience,
    OptimizationRecommendation
)


class TestResourceState(unittest.TestCase):
    """Test ResourceState class."""

    def test_state_creation(self):
        """Test creating a ResourceState."""
        state = ResourceState(
            workflow_name="test-workflow",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=True,
            parallel_jobs=2,
            avg_duration_seconds=180.5,
            success_rate=0.85,
            resource_utilization=0.6,
            time_of_day_bucket=14,
            day_of_week=3
        )

        self.assertEqual(state.workflow_name, "test-workflow")
        self.assertEqual(state.concurrency_limit, 2)
        self.assertEqual(state.timeout_minutes, 60)
        self.assertTrue(state.caching_enabled)
        self.assertEqual(state.parallel_jobs, 2)
        self.assertAlmostEqual(state.avg_duration_seconds, 180.5)
        self.assertAlmostEqual(state.success_rate, 0.85)
        self.assertAlmostEqual(state.resource_utilization, 0.6)
        self.assertEqual(state.time_of_day_bucket, 14)
        self.assertEqual(state.day_of_week, 3)

    def test_state_key_generation(self):
        """Test state key generation for Q-table lookup."""
        state = ResourceState(
            workflow_name="test-workflow",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=True,
            parallel_jobs=2,
            avg_duration_seconds=180,
            success_rate=0.9,
            resource_utilization=0.5,
            time_of_day_bucket=14,
            day_of_week=3
        )

        state_key = state.to_state_key()

        # Key should be a string
        self.assertIsInstance(state_key, str)

        # Key should contain underscore-separated values
        parts = state_key.split('_')
        self.assertTrue(len(parts) >= 8)

        # Same state should produce same key
        self.assertEqual(state.to_state_key(), state.to_state_key())

    def test_different_states_different_keys(self):
        """Test that different states produce different keys."""
        state1 = ResourceState(
            workflow_name="workflow-1",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=True,
            parallel_jobs=2,
            avg_duration_seconds=180,
            success_rate=0.9,
            resource_utilization=0.5,
            time_of_day_bucket=14,
            day_of_week=3
        )

        state2 = ResourceState(
            workflow_name="workflow-2",
            concurrency_limit=5,  # Different
            timeout_minutes=120,  # Different
            caching_enabled=False,  # Different
            parallel_jobs=4,  # Different
            avg_duration_seconds=360,  # Different
            success_rate=0.7,  # Different
            resource_utilization=0.8,  # Different
            time_of_day_bucket=8,  # Different
            day_of_week=1  # Different
        )

        self.assertNotEqual(state1.to_state_key(), state2.to_state_key())


class TestRLResourceOptimizer(unittest.TestCase):
    """Test RLResourceOptimizer class."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.optimizer = RLResourceOptimizer(repo_root=self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test optimizer initialization."""
        self.assertIsNotNone(self.optimizer)
        self.assertEqual(self.optimizer.repo_root, Path(self.temp_dir))
        self.assertIsInstance(self.optimizer.q_table, dict)
        self.assertIsInstance(self.optimizer.experience_buffer, list)
        self.assertGreater(self.optimizer.epsilon, 0)

    def test_q_value_operations(self):
        """Test getting and setting Q-values."""
        state = ResourceState(
            workflow_name="test-wf",
            concurrency_limit=1,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=100,
            success_rate=0.8,
            resource_utilization=0.5,
            time_of_day_bucket=12,
            day_of_week=2
        )

        action = ResourceAction.ENABLE_CACHING

        # Initially should be 0
        q_value = self.optimizer.get_q_value(state, action)
        self.assertEqual(q_value, 0.0)

        # Set a value
        self.optimizer.set_q_value(state, action, 0.5)

        # Should return the set value
        q_value = self.optimizer.get_q_value(state, action)
        self.assertEqual(q_value, 0.5)

    def test_select_action_exploration(self):
        """Test action selection with exploration."""
        state = ResourceState(
            workflow_name="test-wf",
            concurrency_limit=1,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=100,
            success_rate=0.8,
            resource_utilization=0.5,
            time_of_day_bucket=12,
            day_of_week=2
        )

        # With high epsilon, should explore (random actions)
        self.optimizer.epsilon = 1.0
        actions = set()
        for _ in range(50):
            action = self.optimizer.select_action(state, explore=True)
            actions.add(action)

        # Should get multiple different actions due to exploration
        self.assertGreater(len(actions), 1)

    def test_select_action_exploitation(self):
        """Test action selection with exploitation."""
        state = ResourceState(
            workflow_name="test-wf",
            concurrency_limit=1,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=100,
            success_rate=0.8,
            resource_utilization=0.5,
            time_of_day_bucket=12,
            day_of_week=2
        )

        # Set Q-values to prefer one action
        self.optimizer.set_q_value(state, ResourceAction.ENABLE_CACHING, 0.9)
        self.optimizer.set_q_value(state, ResourceAction.NO_CHANGE, 0.1)

        # With exploitation (explore=False), should choose best action
        action = self.optimizer.select_action(state, explore=False)
        self.assertEqual(action, ResourceAction.ENABLE_CACHING)

    def test_calculate_reward(self):
        """Test reward calculation."""
        state = ResourceState(
            workflow_name="test-wf",
            concurrency_limit=1,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=300,
            success_rate=0.7,
            resource_utilization=0.4,
            time_of_day_bucket=12,
            day_of_week=2
        )

        # Improved next state
        better_state = ResourceState(
            workflow_name="test-wf",
            concurrency_limit=1,
            timeout_minutes=60,
            caching_enabled=True,
            parallel_jobs=1,
            avg_duration_seconds=200,  # Faster
            success_rate=0.85,  # Higher success
            resource_utilization=0.6,  # Better utilization
            time_of_day_bucket=12,
            day_of_week=2
        )

        reward = self.optimizer.calculate_reward(
            state, better_state, ResourceAction.ENABLE_CACHING
        )

        # Improvement should yield positive reward
        self.assertGreater(reward, 0)

    def test_calculate_reward_degradation(self):
        """Test reward calculation for degraded state."""
        state = ResourceState(
            workflow_name="test-wf",
            concurrency_limit=1,
            timeout_minutes=60,
            caching_enabled=True,
            parallel_jobs=1,
            avg_duration_seconds=200,
            success_rate=0.9,
            resource_utilization=0.7,
            time_of_day_bucket=12,
            day_of_week=2
        )

        # Worse next state
        worse_state = ResourceState(
            workflow_name="test-wf",
            concurrency_limit=1,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=400,  # Slower
            success_rate=0.6,  # Lower success
            resource_utilization=0.3,  # Worse utilization
            time_of_day_bucket=12,
            day_of_week=2
        )

        reward = self.optimizer.calculate_reward(
            state, worse_state, ResourceAction.DISABLE_CACHING
        )

        # Degradation should yield negative reward
        self.assertLess(reward, 0)

    def test_learn_from_experience(self):
        """Test learning from experience."""
        state = ResourceState(
            workflow_name="test-wf",
            concurrency_limit=1,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=300,
            success_rate=0.7,
            resource_utilization=0.4,
            time_of_day_bucket=12,
            day_of_week=2
        )

        next_state = ResourceState(
            workflow_name="test-wf",
            concurrency_limit=1,
            timeout_minutes=60,
            caching_enabled=True,
            parallel_jobs=1,
            avg_duration_seconds=200,
            success_rate=0.85,
            resource_utilization=0.6,
            time_of_day_bucket=12,
            day_of_week=2
        )

        initial_epsilon = self.optimizer.epsilon

        reward = self.optimizer.learn_from_experience(
            state, ResourceAction.ENABLE_CACHING, next_state
        )

        # Reward should be returned
        self.assertIsInstance(reward, float)

        # Experience should be added to buffer
        self.assertGreater(len(self.optimizer.experience_buffer), 0)

        # Q-value should be updated
        q_value = self.optimizer.get_q_value(state, ResourceAction.ENABLE_CACHING)
        self.assertNotEqual(q_value, 0.0)

        # Epsilon should decay
        self.assertLessEqual(self.optimizer.epsilon, initial_epsilon)

    def test_get_current_state_default(self):
        """Test getting current state with no history."""
        state = self.optimizer.get_current_state("new-workflow")

        self.assertEqual(state.workflow_name, "new-workflow")
        self.assertGreaterEqual(state.concurrency_limit, 1)
        self.assertGreaterEqual(state.timeout_minutes, 1)
        self.assertGreaterEqual(state.success_rate, 0)
        self.assertLessEqual(state.success_rate, 1)

    def test_get_current_state_with_history(self):
        """Test getting current state with execution history."""
        history = [
            {
                'duration_seconds': 150,
                'success': True,
                'resource_usage': {'estimated_cpu_percent': 40}
            },
            {
                'duration_seconds': 180,
                'success': True,
                'resource_usage': {'estimated_cpu_percent': 45}
            },
            {
                'duration_seconds': 160,
                'success': False,
                'resource_usage': {'estimated_cpu_percent': 50}
            }
        ]

        state = self.optimizer.get_current_state("test-workflow", history)

        self.assertEqual(state.workflow_name, "test-workflow")
        # Average duration should be around 163
        self.assertAlmostEqual(state.avg_duration_seconds, 163.33, delta=1)
        # Success rate should be 2/3
        self.assertAlmostEqual(state.success_rate, 0.666, delta=0.01)

    def test_get_recommendation(self):
        """Test getting optimization recommendation."""
        # Train a bit first
        self.optimizer.simulate_training(num_episodes=20)

        rec = self.optimizer.get_recommendation("test-workflow")

        self.assertIsInstance(rec, OptimizationRecommendation)
        self.assertEqual(rec.workflow_name, "test-workflow")
        self.assertIn(rec.recommended_action, [a.value for a in ResourceAction])
        self.assertGreaterEqual(rec.confidence, 0)
        self.assertLessEqual(rec.confidence, 1)
        self.assertIsInstance(rec.reasoning, list)
        self.assertIsInstance(rec.current_state, dict)

    def test_apply_action_to_state(self):
        """Test applying actions to states."""
        state = ResourceState(
            workflow_name="test-wf",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=2,
            avg_duration_seconds=300,
            success_rate=0.8,
            resource_utilization=0.5,
            time_of_day_bucket=12,
            day_of_week=2
        )

        # Test ENABLE_CACHING
        new_state = self.optimizer.apply_action_to_state(state, ResourceAction.ENABLE_CACHING)
        self.assertTrue(new_state.caching_enabled)
        self.assertLess(new_state.avg_duration_seconds, state.avg_duration_seconds)

        # Test INCREASE_CONCURRENCY
        new_state = self.optimizer.apply_action_to_state(state, ResourceAction.INCREASE_CONCURRENCY)
        self.assertEqual(new_state.concurrency_limit, 3)

        # Test DECREASE_CONCURRENCY
        new_state = self.optimizer.apply_action_to_state(state, ResourceAction.DECREASE_CONCURRENCY)
        self.assertEqual(new_state.concurrency_limit, 1)

        # Test EXTEND_TIMEOUT
        new_state = self.optimizer.apply_action_to_state(state, ResourceAction.EXTEND_TIMEOUT)
        self.assertGreater(new_state.timeout_minutes, state.timeout_minutes)

        # Test PARALLELIZE_JOBS
        new_state = self.optimizer.apply_action_to_state(state, ResourceAction.PARALLELIZE_JOBS)
        self.assertEqual(new_state.parallel_jobs, 3)

    def test_simulate_training(self):
        """Test training simulation."""
        stats = self.optimizer.simulate_training(num_episodes=30)

        self.assertEqual(stats['total_episodes'], 30)
        self.assertIn('total_reward', stats)
        self.assertIn('avg_reward', stats)
        self.assertIn('states_explored', stats)
        self.assertIn('action_counts', stats)

        # Q-table should have entries
        self.assertGreater(len(self.optimizer.q_table), 0)

        # Experience buffer should have entries
        self.assertGreater(len(self.optimizer.experience_buffer), 0)

    def test_persistence(self):
        """Test saving and loading state."""
        # Train and get some state
        self.optimizer.simulate_training(num_episodes=20)
        original_q_table_size = len(self.optimizer.q_table)
        original_epsilon = self.optimizer.epsilon

        # Create new optimizer with same directory
        new_optimizer = RLResourceOptimizer(repo_root=self.temp_dir)

        # Should have loaded the saved state
        self.assertEqual(len(new_optimizer.q_table), original_q_table_size)
        self.assertAlmostEqual(new_optimizer.epsilon, original_epsilon, places=5)

    def test_generate_report(self):
        """Test report generation."""
        # Train first
        self.optimizer.simulate_training(num_episodes=20)

        report = self.optimizer.generate_report()

        self.assertIn('timestamp', report)
        self.assertIn('model_stats', report)
        self.assertIn('metrics', report)
        self.assertIn('workflow_recommendations', report)

        model_stats = report['model_stats']
        self.assertIn('total_episodes', model_stats)
        self.assertIn('epsilon', model_stats)
        self.assertIn('q_table_size', model_stats)
        self.assertIn('experience_buffer_size', model_stats)

    def test_experience_buffer_limit(self):
        """Test experience buffer size limit."""
        # Generate many experiences
        for _ in range(self.optimizer.REPLAY_BUFFER_SIZE + 100):
            state = ResourceState(
                workflow_name="test-wf",
                concurrency_limit=1,
                timeout_minutes=60,
                caching_enabled=False,
                parallel_jobs=1,
                avg_duration_seconds=100,
                success_rate=0.8,
                resource_utilization=0.5,
                time_of_day_bucket=12,
                day_of_week=2
            )
            next_state = self.optimizer.apply_action_to_state(state, ResourceAction.NO_CHANGE)
            self.optimizer.learn_from_experience(state, ResourceAction.NO_CHANGE, next_state)

        # Buffer should not exceed limit
        self.assertLessEqual(
            len(self.optimizer.experience_buffer),
            self.optimizer.REPLAY_BUFFER_SIZE
        )

    def test_epsilon_decay(self):
        """Test epsilon decays over time."""
        initial_epsilon = 1.0
        self.optimizer.epsilon = initial_epsilon

        # Simulate some learning
        for _ in range(50):
            state = ResourceState(
                workflow_name="test-wf",
                concurrency_limit=1,
                timeout_minutes=60,
                caching_enabled=False,
                parallel_jobs=1,
                avg_duration_seconds=100,
                success_rate=0.8,
                resource_utilization=0.5,
                time_of_day_bucket=12,
                day_of_week=2
            )
            next_state = self.optimizer.apply_action_to_state(state, ResourceAction.ENABLE_CACHING)
            self.optimizer.learn_from_experience(state, ResourceAction.ENABLE_CACHING, next_state)

        # Epsilon should have decayed
        self.assertLess(self.optimizer.epsilon, initial_epsilon)
        # But should not go below minimum
        self.assertGreaterEqual(self.optimizer.epsilon, self.optimizer.MIN_EPSILON)


class TestResourceAction(unittest.TestCase):
    """Test ResourceAction enum."""

    def test_all_actions_exist(self):
        """Test all expected actions exist."""
        expected_actions = [
            'INCREASE_CONCURRENCY',
            'DECREASE_CONCURRENCY',
            'EXTEND_TIMEOUT',
            'REDUCE_TIMEOUT',
            'ENABLE_CACHING',
            'DISABLE_CACHING',
            'PARALLELIZE_JOBS',
            'SERIALIZE_JOBS',
            'NO_CHANGE'
        ]

        for action_name in expected_actions:
            self.assertTrue(hasattr(ResourceAction, action_name))

    def test_action_values(self):
        """Test action enum values."""
        self.assertEqual(ResourceAction.ENABLE_CACHING.value, "enable_caching")
        self.assertEqual(ResourceAction.NO_CHANGE.value, "no_change")
        self.assertEqual(ResourceAction.INCREASE_CONCURRENCY.value, "increase_concurrency")


class TestIntegration(unittest.TestCase):
    """Integration tests for RL Resource Optimizer."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.optimizer = RLResourceOptimizer(repo_root=self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_full_learning_cycle(self):
        """Test a complete learning cycle."""
        # 1. Start with a workflow state
        history = [
            {'duration_seconds': 300, 'success': True, 'resource_usage': {'estimated_cpu_percent': 40}},
            {'duration_seconds': 320, 'success': True, 'resource_usage': {'estimated_cpu_percent': 45}},
            {'duration_seconds': 350, 'success': False, 'resource_usage': {'estimated_cpu_percent': 50}},
            {'duration_seconds': 280, 'success': True, 'resource_usage': {'estimated_cpu_percent': 35}},
        ]

        state = self.optimizer.get_current_state("my-workflow", history)

        # 2. Get initial recommendation
        initial_rec = self.optimizer.get_recommendation("my-workflow", history)

        # 3. Simulate applying the recommendation
        action = ResourceAction(initial_rec.recommended_action)
        next_state = self.optimizer.apply_action_to_state(state, action)

        # 4. Learn from the experience
        reward = self.optimizer.learn_from_experience(state, action, next_state)

        # 5. Get new recommendation (should be informed by learning)
        final_rec = self.optimizer.get_recommendation("my-workflow", history)

        # Verify the learning happened
        self.assertGreater(len(self.optimizer.experience_buffer), 0)
        self.assertGreater(len(self.optimizer.q_table), 0)

    def test_multiple_workflows(self):
        """Test optimizer with multiple workflows."""
        workflows = ["build", "test", "deploy", "lint", "security-scan"]

        # Train on multiple workflows
        for wf in workflows:
            self.optimizer.get_current_state(wf)

        self.optimizer.simulate_training(num_episodes=50)

        # Get recommendations for each
        recommendations = []
        for wf in workflows:
            rec = self.optimizer.get_recommendation(wf)
            recommendations.append(rec)
            self.assertEqual(rec.workflow_name, wf)

        # Should have various recommendations (not all the same)
        actions = [r.recommended_action for r in recommendations]
        # Due to exploration, we might get various actions
        self.assertTrue(all(isinstance(a, str) for a in actions))


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestResourceState))
    suite.addTests(loader.loadTestsFromTestCase(TestRLResourceOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestResourceAction))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
