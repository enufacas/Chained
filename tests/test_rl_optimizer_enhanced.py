#!/usr/bin/env python3
"""
Tests for Enhanced RL Optimizer
Created by @APIs-architect

Tests for double Q-learning and prioritized experience replay enhancements.
"""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from rl_optimizer_enhanced import (
    EnhancedRLOptimizer,
    PrioritizedExperience
)
from rl_resource_optimizer import (
    ResourceState,
    ResourceAction,
    ResourceExperience
)


class TestEnhancedRLOptimizer(unittest.TestCase):
    """Test enhanced RL optimizer features."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        git_dir = Path(self.test_dir) / '.git'
        git_dir.mkdir()
        
        self.optimizer = EnhancedRLOptimizer(repo_root=self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test enhanced optimizer initialization."""
        self.assertIsInstance(self.optimizer, EnhancedRLOptimizer)
        self.assertTrue(self.optimizer.USE_DOUBLE_Q_LEARNING)
        self.assertEqual(self.optimizer.per_beta, self.optimizer.PER_BETA_START)
        self.assertIsInstance(self.optimizer.q_table_2, dict)
        self.assertIsInstance(self.optimizer.prioritized_buffer, list)

    def test_double_q_table(self):
        """Test double Q-table functionality."""
        state = ResourceState(
            workflow_name="test",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=True,
            parallel_jobs=2,
            avg_duration_seconds=180.0,
            success_rate=0.85,
            resource_utilization=0.6,
            time_of_day_bucket=14,
            day_of_week=3
        )
        
        action = ResourceAction.ENABLE_CACHING
        
        # Set values in both Q-tables
        self.optimizer.set_q_value_double(state, action, 0.5, use_second=False)
        self.optimizer.set_q_value_double(state, action, 0.6, use_second=True)
        
        # Verify values
        q1 = self.optimizer.get_q_value_double(state, action, use_second=False)
        q2 = self.optimizer.get_q_value_double(state, action, use_second=True)
        
        self.assertAlmostEqual(q1, 0.5)
        self.assertAlmostEqual(q2, 0.6)

    def test_prioritized_experience(self):
        """Test prioritized experience creation and comparison."""
        state = ResourceState(
            workflow_name="test",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=200.0,
            success_rate=0.8,
            resource_utilization=0.5,
            time_of_day_bucket=10,
            day_of_week=1
        )
        
        next_state = ResourceState(
            workflow_name="test",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=True,
            parallel_jobs=1,
            avg_duration_seconds=150.0,
            success_rate=0.85,
            resource_utilization=0.6,
            time_of_day_bucket=10,
            day_of_week=1
        )
        
        experience = ResourceExperience(
            state=state,
            action=ResourceAction.ENABLE_CACHING,
            reward=0.5,
            next_state=next_state,
            done=False
        )
        
        # Create prioritized experiences
        pri_exp1 = PrioritizedExperience(experience, priority=0.8)
        pri_exp2 = PrioritizedExperience(experience, priority=0.5)
        
        # Higher priority should be "less than" for max-heap
        self.assertTrue(pri_exp1 < pri_exp2)

    def test_add_experience_prioritized(self):
        """Test adding experience to prioritized buffer."""
        state = ResourceState(
            workflow_name="test",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=200.0,
            success_rate=0.8,
            resource_utilization=0.5,
            time_of_day_bucket=10,
            day_of_week=1
        )
        
        next_state = ResourceState(
            workflow_name="test",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=True,
            parallel_jobs=1,
            avg_duration_seconds=150.0,
            success_rate=0.85,
            resource_utilization=0.6,
            time_of_day_bucket=10,
            day_of_week=1
        )
        
        experience = ResourceExperience(
            state=state,
            action=ResourceAction.ENABLE_CACHING,
            reward=0.5,
            next_state=next_state,
            done=False
        )
        
        initial_size = len(self.optimizer.prioritized_buffer)
        self.optimizer.add_experience_prioritized(experience)
        
        # Buffer should grow
        self.assertEqual(len(self.optimizer.prioritized_buffer), initial_size + 1)
        
        # Should also be in regular buffer
        self.assertGreater(len(self.optimizer.experience_buffer), 0)

    def test_calculate_td_error(self):
        """Test TD error calculation."""
        state = ResourceState(
            workflow_name="test",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=200.0,
            success_rate=0.8,
            resource_utilization=0.5,
            time_of_day_bucket=10,
            day_of_week=1
        )
        
        next_state = ResourceState(
            workflow_name="test",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=True,
            parallel_jobs=1,
            avg_duration_seconds=150.0,
            success_rate=0.85,
            resource_utilization=0.6,
            time_of_day_bucket=10,
            day_of_week=1
        )
        
        experience = ResourceExperience(
            state=state,
            action=ResourceAction.ENABLE_CACHING,
            reward=0.5,
            next_state=next_state,
            done=False
        )
        
        td_error = self.optimizer.calculate_td_error(experience)
        
        # TD error should be non-negative
        self.assertGreaterEqual(td_error, 0.0)

    def test_sample_prioritized_batch(self):
        """Test sampling from prioritized buffer."""
        # Add multiple experiences
        for i in range(10):
            state = ResourceState(
                workflow_name=f"test-{i}",
                concurrency_limit=2,
                timeout_minutes=60,
                caching_enabled=False,
                parallel_jobs=1,
                avg_duration_seconds=200.0 + i * 10,
                success_rate=0.8,
                resource_utilization=0.5,
                time_of_day_bucket=10,
                day_of_week=1
            )
            
            next_state = ResourceState(
                workflow_name=f"test-{i}",
                concurrency_limit=2,
                timeout_minutes=60,
                caching_enabled=True,
                parallel_jobs=1,
                avg_duration_seconds=150.0 + i * 5,
                success_rate=0.85,
                resource_utilization=0.6,
                time_of_day_bucket=10,
                day_of_week=1
            )
            
            experience = ResourceExperience(
                state=state,
                action=ResourceAction.ENABLE_CACHING,
                reward=0.5,
                next_state=next_state,
                done=False
            )
            
            self.optimizer.add_experience_prioritized(experience)
        
        # Sample batch
        batch = self.optimizer.sample_prioritized_batch(batch_size=5)
        
        # Should have 5 samples
        self.assertEqual(len(batch), 5)
        
        # Each sample should be (experience, weight) tuple
        for exp, weight in batch:
            self.assertIsInstance(exp, ResourceExperience)
            self.assertIsInstance(weight, float)
            self.assertGreaterEqual(weight, 0.0)
            self.assertLessEqual(weight, 1.0)

    def test_enhanced_action_selection(self):
        """Test enhanced action selection with double Q-learning."""
        state = ResourceState(
            workflow_name="test",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=200.0,
            success_rate=0.8,
            resource_utilization=0.5,
            time_of_day_bucket=10,
            day_of_week=1
        )
        
        # Set different Q-values in both tables
        for action in ResourceAction:
            self.optimizer.set_q_value_double(state, action, 0.5, use_second=False)
            self.optimizer.set_q_value_double(state, action, 0.3, use_second=True)
        
        # Make one action better
        self.optimizer.set_q_value_double(state, ResourceAction.ENABLE_CACHING, 0.9, use_second=False)
        self.optimizer.set_q_value_double(state, ResourceAction.ENABLE_CACHING, 0.8, use_second=True)
        
        # Should select best action (no exploration)
        action = self.optimizer.select_action_enhanced(state, explore=False)
        self.assertEqual(action, ResourceAction.ENABLE_CACHING)

    def test_update_q_value_double(self):
        """Test double Q-learning update."""
        state = ResourceState(
            workflow_name="test",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=200.0,
            success_rate=0.8,
            resource_utilization=0.5,
            time_of_day_bucket=10,
            day_of_week=1
        )
        
        next_state = ResourceState(
            workflow_name="test",
            concurrency_limit=2,
            timeout_minutes=60,
            caching_enabled=True,
            parallel_jobs=1,
            avg_duration_seconds=150.0,
            success_rate=0.85,
            resource_utilization=0.6,
            time_of_day_bucket=10,
            day_of_week=1
        )
        
        experience = ResourceExperience(
            state=state,
            action=ResourceAction.ENABLE_CACHING,
            reward=0.5,
            next_state=next_state,
            done=False
        )
        
        # Get initial Q-values
        q1_before = self.optimizer.get_q_value_double(state, ResourceAction.ENABLE_CACHING, use_second=False)
        q2_before = self.optimizer.get_q_value_double(state, ResourceAction.ENABLE_CACHING, use_second=True)
        
        # Update
        self.optimizer.update_q_value_double(experience, importance_weight=1.0)
        
        # At least one Q-table should have changed
        q1_after = self.optimizer.get_q_value_double(state, ResourceAction.ENABLE_CACHING, use_second=False)
        q2_after = self.optimizer.get_q_value_double(state, ResourceAction.ENABLE_CACHING, use_second=True)
        
        self.assertTrue(q1_before != q1_after or q2_before != q2_after)

    def test_simulate_training_enhanced(self):
        """Test enhanced training simulation."""
        stats = self.optimizer.simulate_training_enhanced(num_episodes=10)
        
        # Check stats structure
        self.assertIn('total_episodes', stats)
        self.assertIn('total_reward', stats)
        self.assertIn('avg_reward', stats)
        self.assertIn('avg_td_errors', stats)
        self.assertIn('learning_rates', stats)
        self.assertIn('final_learning_rate', stats)
        self.assertIn('final_epsilon', stats)
        
        # Check values
        self.assertEqual(stats['total_episodes'], 10)
        self.assertIsInstance(stats['avg_td_errors'], list)
        self.assertIsInstance(stats['learning_rates'], list)
        
        # Should have learned something (at least one Q-table updated)
        self.assertGreater(len(self.optimizer.q_table), 0)
        # Note: q_table_2 may or may not be updated due to randomness in double Q-learning
        total_q_entries = len(self.optimizer.q_table) + len(self.optimizer.q_table_2)
        self.assertGreater(total_q_entries, 0)

    def test_save_and_load_enhanced_state(self):
        """Test saving and loading enhanced state."""
        # Train a bit
        self.optimizer.simulate_training_enhanced(num_episodes=5)
        
        # Save
        self.optimizer.save_enhanced_state()
        
        # Create new optimizer and load
        new_optimizer = EnhancedRLOptimizer(repo_root=self.test_dir)
        
        # Should have loaded state
        self.assertEqual(len(new_optimizer.q_table_2), len(self.optimizer.q_table_2))


if __name__ == '__main__':
    unittest.main()
