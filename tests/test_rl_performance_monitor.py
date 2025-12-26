#!/usr/bin/env python3
"""
Tests for RL Performance Monitor
Created by @create-botter
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from rl_performance_monitor import (
    RLPerformanceMonitor,
    PerformanceMetric,
    LearningProgress,
    RecommendationOutcome
)


class TestRLPerformanceMonitor(unittest.TestCase):
    """Test cases for RL Performance Monitor."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.monitor = RLPerformanceMonitor(repo_root=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test monitor initialization."""
        self.assertIsNotNone(self.monitor)
        self.assertTrue(self.monitor.metrics_dir.exists())
    
    def test_record_learning_progress(self):
        """Test recording learning progress."""
        self.monitor.record_learning_progress(
            episode=10,
            total_reward=100.0,
            avg_reward=10.0,
            epsilon=0.5,
            learning_rate=0.1,
            q_table_size=50
        )
        
        self.assertEqual(len(self.monitor.learning_history), 1)
        progress = self.monitor.learning_history[0]
        self.assertEqual(progress.episode, 10)
        self.assertEqual(progress.avg_reward, 10.0)
    
    def test_convergence_score_calculation(self):
        """Test convergence score calculation."""
        # Add multiple progress records
        for i in range(15):
            self.monitor.record_learning_progress(
                episode=i,
                total_reward=100.0 + i,
                avg_reward=10.0 + (i * 0.1),
                epsilon=0.9 - (i * 0.05),
                learning_rate=0.1,
                q_table_size=50 + i
            )
        
        # Latest should have convergence score
        latest = self.monitor.learning_history[-1]
        self.assertGreater(latest.convergence_score, 0.0)
        self.assertLessEqual(latest.convergence_score, 1.0)
    
    def test_record_recommendation_outcome(self):
        """Test recording recommendation outcome."""
        self.monitor.record_recommendation_outcome(
            workflow_name="test-workflow",
            recommendation_id="rec123",
            action_taken="enable_caching",
            before_duration=120.0,
            after_duration=80.0,
            before_success_rate=0.9,
            after_success_rate=0.95
        )
        
        self.assertEqual(len(self.monitor.recommendation_outcomes), 1)
        outcome = self.monitor.recommendation_outcomes[0]
        self.assertEqual(outcome.workflow_name, "test-workflow")
        self.assertGreater(outcome.improvement_percentage, 0)
    
    def test_record_metric(self):
        """Test recording performance metric."""
        self.monitor.record_metric(
            metric_name="duration",
            value=120.5,
            workflow_name="test-workflow"
        )
        
        self.assertEqual(len(self.monitor.performance_metrics), 1)
        metric = self.monitor.performance_metrics[0]
        self.assertEqual(metric.metric_name, "duration")
        self.assertEqual(metric.value, 120.5)
    
    def test_get_convergence_status(self):
        """Test convergence status retrieval."""
        # No data initially
        status = self.monitor.get_convergence_status()
        self.assertEqual(status['status'], 'no_data')
        
        # Add some data
        for i in range(60):
            self.monitor.record_learning_progress(
                episode=i,
                total_reward=100.0,
                avg_reward=10.0,
                epsilon=max(0.05, 1.0 - i * 0.02),
                learning_rate=0.1,
                q_table_size=50
            )
        
        status = self.monitor.get_convergence_status()
        self.assertIn('converged', status)
        self.assertIn('convergence_score', status)
    
    def test_get_recommendation_effectiveness(self):
        """Test recommendation effectiveness calculation."""
        # Add some outcomes
        self.monitor.record_recommendation_outcome(
            "workflow1", "rec1", "enable_caching",
            120.0, 80.0, 0.9, 0.95
        )
        self.monitor.record_recommendation_outcome(
            "workflow2", "rec2", "parallelize",
            180.0, 120.0, 0.85, 0.9
        )
        
        effectiveness = self.monitor.get_recommendation_effectiveness()
        self.assertEqual(effectiveness['total_recommendations'], 2)
        self.assertGreater(effectiveness['avg_improvement'], 0)
        self.assertEqual(effectiveness['workflows_optimized'], 2)
    
    def test_save_and_load(self):
        """Test persistence of monitor data."""
        # Record some data
        self.monitor.record_learning_progress(
            episode=10,
            total_reward=100.0,
            avg_reward=10.0,
            epsilon=0.5,
            learning_rate=0.1,
            q_table_size=50
        )
        
        self.monitor.record_recommendation_outcome(
            "test-workflow", "rec123", "enable_caching",
            120.0, 80.0, 0.9, 0.95
        )
        
        # Save
        self.monitor.save_all()
        
        # Create new monitor and load
        monitor2 = RLPerformanceMonitor(repo_root=self.test_dir)
        self.assertEqual(len(monitor2.learning_history), 1)
        self.assertEqual(len(monitor2.recommendation_outcomes), 1)
    
    def test_generate_report(self):
        """Test report generation."""
        # Add some data
        self.monitor.record_learning_progress(
            episode=10,
            total_reward=100.0,
            avg_reward=10.0,
            epsilon=0.5,
            learning_rate=0.1,
            q_table_size=50
        )
        
        report = self.monitor.generate_report()
        self.assertIsInstance(report, str)
        self.assertIn("RL Performance Monitor Report", report)
        self.assertIn("@create-botter", report)
    
    def test_dashboard_data_generation(self):
        """Test dashboard data generation."""
        dashboard_data = self.monitor.generate_dashboard_data()
        
        self.assertIn('timestamp', dashboard_data)
        self.assertIn('convergence', dashboard_data)
        self.assertIn('effectiveness', dashboard_data)
        self.assertIn('learning_progress', dashboard_data)


if __name__ == '__main__':
    unittest.main()
