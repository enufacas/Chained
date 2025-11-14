#!/usr/bin/env python3
"""
Tests for the A/B Testing Engine

Comprehensive test suite following @engineer-master's rigorous testing principles.
Tests all functionality including edge cases and error conditions.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# Import the module under test
import sys
sys.path.insert(0, os.path.dirname(__file__))
from ab_testing_engine import ABTestingEngine


class TestABTestingEngine(unittest.TestCase):
    """Test suite for ABTestingEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test registry
        self.test_dir = tempfile.mkdtemp()
        self.registry_path = os.path.join(self.test_dir, "test_registry.json")
        self.engine = ABTestingEngine(registry_path=self.registry_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove test directory
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test that engine initializes correctly."""
        # Registry file should be created
        self.assertTrue(os.path.exists(self.registry_path))
        
        # Registry should have proper structure
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        self.assertEqual(registry["version"], "1.0.0")
        self.assertIsInstance(registry["experiments"], list)
        self.assertIn("config", registry)
    
    def test_create_experiment_valid(self):
        """Test creating a valid experiment."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Test Schedule Frequency",
            description="Testing different schedule frequencies",
            variants=variants,
            metrics=["execution_time", "success_rate"],
            workflow_name="auto-review-merge"
        )
        
        # Experiment ID should be generated
        self.assertIsNotNone(exp_id)
        self.assertTrue(exp_id.startswith("exp-"))
        
        # Experiment should be in registry
        details = self.engine.get_experiment_details(exp_id)
        self.assertIsNotNone(details)
        self.assertEqual(details["name"], "Test Schedule Frequency")
        self.assertEqual(details["status"], "active")
        self.assertEqual(len(details["variants"]), 2)
    
    def test_create_experiment_insufficient_variants(self):
        """Test that experiment creation fails with < 2 variants."""
        variants = {
            "control": {"schedule": "*/15 * * * *"}
        }
        
        with self.assertRaises(ValueError) as context:
            self.engine.create_experiment(
                name="Invalid Test",
                description="Test with one variant",
                variants=variants,
                metrics=["execution_time"]
            )
        
        self.assertIn("at least 2 variants", str(context.exception))
    
    def test_create_duplicate_experiment(self):
        """Test that duplicate active experiments are rejected."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        # Create first experiment
        self.engine.create_experiment(
            name="Duplicate Test",
            description="First instance",
            variants=variants,
            metrics=["execution_time"]
        )
        
        # Try to create duplicate
        with self.assertRaises(ValueError) as context:
            self.engine.create_experiment(
                name="Duplicate Test",
                description="Second instance",
                variants=variants,
                metrics=["execution_time"]
            )
        
        self.assertIn("already exists", str(context.exception))
    
    def test_record_sample_valid(self):
        """Test recording a valid sample."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Sample Test",
            description="Testing sample recording",
            variants=variants,
            metrics=["execution_time", "success_rate"]
        )
        
        # Record a sample
        self.engine.record_sample(
            experiment_id=exp_id,
            variant_name="control",
            metrics={
                "execution_time": 45.2,
                "success_rate": 0.95
            },
            metadata={"run_id": "12345"}
        )
        
        # Verify sample was recorded
        details = self.engine.get_experiment_details(exp_id)
        control_variant = details["variants"]["control"]
        
        self.assertEqual(control_variant["total_samples"], 1)
        self.assertEqual(len(control_variant["samples"]), 1)
        self.assertEqual(len(control_variant["metrics"]["execution_time"]), 1)
        self.assertEqual(control_variant["metrics"]["execution_time"][0], 45.2)
    
    def test_record_sample_invalid_experiment(self):
        """Test that recording to non-existent experiment fails."""
        with self.assertRaises(ValueError) as context:
            self.engine.record_sample(
                experiment_id="exp-nonexistent",
                variant_name="control",
                metrics={"execution_time": 45.2}
            )
        
        self.assertIn("not found", str(context.exception))
    
    def test_record_sample_invalid_variant(self):
        """Test that recording to non-existent variant fails."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Variant Test",
            description="Testing variant validation",
            variants=variants,
            metrics=["execution_time"]
        )
        
        with self.assertRaises(ValueError) as context:
            self.engine.record_sample(
                experiment_id=exp_id,
                variant_name="nonexistent_variant",
                metrics={"execution_time": 45.2}
            )
        
        self.assertIn("not found", str(context.exception))
    
    def test_analyze_experiment_insufficient_data(self):
        """Test analysis with insufficient data."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Analysis Test",
            description="Testing analysis",
            variants=variants,
            metrics=["execution_time"]
        )
        
        # Record only a few samples (less than min_samples_per_variant)
        for i in range(3):
            self.engine.record_sample(
                experiment_id=exp_id,
                variant_name="control",
                metrics={"execution_time": 40.0 + i}
            )
        
        analysis = self.engine.analyze_experiment(exp_id)
        
        self.assertEqual(analysis["status"], "insufficient_data")
        self.assertIn("current_samples", analysis)
    
    def test_analyze_experiment_with_sufficient_data(self):
        """Test analysis with sufficient data."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Full Analysis Test",
            description="Testing complete analysis",
            variants=variants,
            metrics=["execution_time", "success_rate"]
        )
        
        # Record enough samples for both variants
        for i in range(15):
            self.engine.record_sample(
                experiment_id=exp_id,
                variant_name="control",
                metrics={
                    "execution_time": 50.0 + i * 0.5,
                    "success_rate": 0.90 + i * 0.005
                }
            )
            
            self.engine.record_sample(
                experiment_id=exp_id,
                variant_name="variant_a",
                metrics={
                    "execution_time": 45.0 + i * 0.5,  # Better performance
                    "success_rate": 0.92 + i * 0.005
                }
            )
        
        analysis = self.engine.analyze_experiment(exp_id)
        
        self.assertEqual(analysis["status"], "analyzed")
        self.assertIn("variant_statistics", analysis)
        self.assertIn("winner", analysis)
        
        # Verify statistics were calculated
        stats = analysis["variant_statistics"]
        self.assertIn("control", stats)
        self.assertIn("variant_a", stats)
        
        # Each variant should have stats for both metrics
        for variant_name in ["control", "variant_a"]:
            variant_stats = stats[variant_name]
            self.assertIn("execution_time", variant_stats)
            self.assertIn("success_rate", variant_stats)
            
            # Each metric should have mean, min, max, count
            for metric_stats in variant_stats.values():
                self.assertIn("mean", metric_stats)
                self.assertIn("min", metric_stats)
                self.assertIn("max", metric_stats)
                self.assertIn("count", metric_stats)
    
    def test_complete_experiment(self):
        """Test completing an experiment."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Completion Test",
            description="Testing experiment completion",
            variants=variants,
            metrics=["execution_time"]
        )
        
        # Complete the experiment
        self.engine.complete_experiment(
            experiment_id=exp_id,
            winner="variant_a",
            notes="Variant A showed better performance"
        )
        
        # Verify experiment is completed
        details = self.engine.get_experiment_details(exp_id)
        self.assertEqual(details["status"], "completed")
        self.assertIn("completed_at", details)
        self.assertIn("results", details)
        self.assertEqual(details["results"]["winner"], "variant_a")
    
    def test_list_experiments_no_filter(self):
        """Test listing all experiments."""
        # Create multiple experiments
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        self.engine.create_experiment(
            name="Experiment 1",
            description="First test",
            variants=variants,
            metrics=["execution_time"]
        )
        
        self.engine.create_experiment(
            name="Experiment 2",
            description="Second test",
            variants=variants,
            metrics=["success_rate"],
            workflow_name="auto-review-merge"
        )
        
        experiments = self.engine.list_experiments()
        
        self.assertEqual(len(experiments), 2)
        self.assertIn("id", experiments[0])
        self.assertIn("name", experiments[0])
        self.assertIn("status", experiments[0])
    
    def test_list_experiments_with_status_filter(self):
        """Test listing experiments filtered by status."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        exp1_id = self.engine.create_experiment(
            name="Active Experiment",
            description="Active test",
            variants=variants,
            metrics=["execution_time"]
        )
        
        exp2_id = self.engine.create_experiment(
            name="To Complete Experiment",
            description="Will be completed",
            variants=variants,
            metrics=["execution_time"]
        )
        
        # Complete one experiment
        self.engine.complete_experiment(exp2_id)
        
        # List only active experiments
        active_experiments = self.engine.list_experiments(status="active")
        self.assertEqual(len(active_experiments), 1)
        self.assertEqual(active_experiments[0]["name"], "Active Experiment")
        
        # List only completed experiments
        completed_experiments = self.engine.list_experiments(status="completed")
        self.assertEqual(len(completed_experiments), 1)
        self.assertEqual(completed_experiments[0]["name"], "To Complete Experiment")
    
    def test_list_experiments_with_workflow_filter(self):
        """Test listing experiments filtered by workflow name."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        self.engine.create_experiment(
            name="Workflow A Experiment",
            description="Test for workflow A",
            variants=variants,
            metrics=["execution_time"],
            workflow_name="workflow-a"
        )
        
        self.engine.create_experiment(
            name="Workflow B Experiment",
            description="Test for workflow B",
            variants=variants,
            metrics=["execution_time"],
            workflow_name="workflow-b"
        )
        
        # List experiments for workflow-a
        workflow_a_experiments = self.engine.list_experiments(workflow_name="workflow-a")
        self.assertEqual(len(workflow_a_experiments), 1)
        self.assertEqual(workflow_a_experiments[0]["name"], "Workflow A Experiment")
    
    def test_experiment_id_uniqueness(self):
        """Test that experiment IDs are unique."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        exp1_id = self.engine.create_experiment(
            name="Uniqueness Test",
            description="First instance",
            variants=variants,
            metrics=["execution_time"]
        )
        
        # Complete first experiment so we can create another with same name
        self.engine.complete_experiment(exp1_id)
        
        exp2_id = self.engine.create_experiment(
            name="Uniqueness Test",
            description="Second instance",
            variants=variants,
            metrics=["execution_time"]
        )
        
        # IDs should be different
        self.assertNotEqual(exp1_id, exp2_id)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.registry_path = os.path.join(self.test_dir, "test_registry.json")
        self.engine = ABTestingEngine(registry_path=self.registry_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_empty_metrics_list(self):
        """Test creating experiment with empty metrics list."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Empty Metrics Test",
            description="Testing empty metrics",
            variants=variants,
            metrics=[]
        )
        
        # Should create successfully
        details = self.engine.get_experiment_details(exp_id)
        self.assertIsNotNone(details)
        self.assertEqual(details["metrics"], [])
    
    def test_record_sample_to_completed_experiment(self):
        """Test that recording to completed experiment fails."""
        variants = {
            "control": {"schedule": "*/15 * * * *"},
            "variant_a": {"schedule": "*/10 * * * *"}
        }
        
        exp_id = self.engine.create_experiment(
            name="Completed Test",
            description="Testing completed state",
            variants=variants,
            metrics=["execution_time"]
        )
        
        # Complete the experiment
        self.engine.complete_experiment(exp_id)
        
        # Try to record a sample
        with self.assertRaises(ValueError) as context:
            self.engine.record_sample(
                experiment_id=exp_id,
                variant_name="control",
                metrics={"execution_time": 45.2}
            )
        
        self.assertIn("not active", str(context.exception))
    
    def test_analyze_nonexistent_experiment(self):
        """Test analyzing non-existent experiment."""
        with self.assertRaises(ValueError) as context:
            self.engine.analyze_experiment("exp-nonexistent")
        
        self.assertIn("not found", str(context.exception))


if __name__ == "__main__":
    unittest.main()
