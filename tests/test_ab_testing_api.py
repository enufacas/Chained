#!/usr/bin/env python3
"""
Tests for A/B Testing API and Integration

Tests the new API layer and workflow integration helpers.

Author: @APIs-architect
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from http import HTTPStatus

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from ab_testing_api import ABTestingAPI
from ab_testing_integration import WorkflowIntegration, setup_workflow_testing


class TestABTestingAPI(unittest.TestCase):
    """Test A/B Testing API functionality."""
    
    def setUp(self):
        """Create temporary registry for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = os.path.join(self.temp_dir, "test_registry.json")
        self.api = ABTestingAPI(registry_path=self.registry_path)
    
    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.registry_path):
            os.remove(self.registry_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    # ==================== Experiment Management Tests ====================
    
    def test_create_experiment_success(self):
        """Test successful experiment creation via API."""
        status_code, response = self.api.create_experiment(
            name="API Test Experiment",
            description="Testing API experiment creation",
            variants={
                "control": {"timeout": 300},
                "variant_a": {"timeout": 450}
            },
            metrics=["execution_time", "success_rate"],
            workflow_name="test-workflow"
        )
        
        self.assertEqual(status_code, HTTPStatus.CREATED)
        self.assertTrue(response["success"])
        self.assertIn("experiment_id", response)
        self.assertTrue(response["experiment_id"].startswith("exp-"))
    
    def test_create_experiment_invalid_name(self):
        """Test experiment creation with invalid name."""
        status_code, response = self.api.create_experiment(
            name="",  # Empty name
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["time"]
        )
        
        self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response["code"], "INVALID_NAME")
    
    def test_create_experiment_insufficient_variants(self):
        """Test experiment creation with too few variants."""
        status_code, response = self.api.create_experiment(
            name="Test",
            description="Test",
            variants={"only_one": {}},  # Only one variant
            metrics=["time"]
        )
        
        self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response["code"], "INSUFFICIENT_VARIANTS")
    
    def test_create_experiment_no_metrics(self):
        """Test experiment creation without metrics."""
        status_code, response = self.api.create_experiment(
            name="Test",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=[]  # No metrics
        )
        
        self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response["code"], "NO_METRICS")
    
    def test_get_experiment(self):
        """Test retrieving experiment details."""
        # Create an experiment first
        status_code, create_response = self.api.create_experiment(
            name="Get Test",
            description="Test getting experiment",
            variants={"a": {}, "b": {}},
            metrics=["time"]
        )
        exp_id = create_response["experiment_id"]
        
        # Now retrieve it
        status_code, response = self.api.get_experiment(exp_id)
        
        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertTrue(response["success"])
        self.assertIn("experiment", response)
        self.assertEqual(response["experiment"]["name"], "Get Test")
    
    def test_get_nonexistent_experiment(self):
        """Test retrieving a non-existent experiment."""
        status_code, response = self.api.get_experiment("exp-nonexistent")
        
        self.assertEqual(status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response["code"], "EXPERIMENT_NOT_FOUND")
    
    def test_list_experiments(self):
        """Test listing experiments."""
        # Create a couple of experiments
        self.api.create_experiment(
            name="Exp 1",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["time"]
        )
        self.api.create_experiment(
            name="Exp 2",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["time"]
        )
        
        status_code, response = self.api.list_experiments()
        
        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertTrue(response["success"])
        self.assertEqual(len(response["experiments"]), 2)
        self.assertEqual(response["pagination"]["total"], 2)
    
    def test_list_experiments_with_filter(self):
        """Test listing experiments with status filter."""
        # Create and complete one experiment
        status_code, create_response = self.api.create_experiment(
            name="Completed Exp",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["time"]
        )
        exp_id = create_response["experiment_id"]
        self.api.complete_experiment(exp_id, "a", "Test completion")
        
        # Create another active experiment
        self.api.create_experiment(
            name="Active Exp",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["time"]
        )
        
        # List only active
        status_code, response = self.api.list_experiments(status="active")
        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertEqual(len(response["experiments"]), 1)
        self.assertEqual(response["experiments"][0]["name"], "Active Exp")
    
    def test_complete_experiment(self):
        """Test completing an experiment."""
        # Create experiment
        status_code, create_response = self.api.create_experiment(
            name="Complete Test",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["time"]
        )
        exp_id = create_response["experiment_id"]
        
        # Complete it
        status_code, response = self.api.complete_experiment(
            exp_id, "a", "Test completion"
        )
        
        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertTrue(response["success"])
        self.assertEqual(response["winner"], "a")
    
    # ==================== Metrics Tests ====================
    
    def test_record_sample(self):
        """Test recording a sample."""
        # Create experiment
        status_code, create_response = self.api.create_experiment(
            name="Metrics Test",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["execution_time", "success_rate"]
        )
        exp_id = create_response["experiment_id"]
        
        # Record sample
        status_code, response = self.api.record_sample(
            experiment_id=exp_id,
            variant_name="a",
            metrics={"execution_time": 100.5, "success_rate": 0.95}
        )
        
        self.assertEqual(status_code, HTTPStatus.CREATED)
        self.assertTrue(response["success"])
    
    def test_record_sample_invalid_experiment(self):
        """Test recording sample for non-existent experiment."""
        status_code, response = self.api.record_sample(
            experiment_id="exp-nonexistent",
            variant_name="a",
            metrics={"time": 100}
        )
        
        self.assertEqual(status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response["code"], "EXPERIMENT_NOT_FOUND")
    
    def test_record_sample_invalid_variant(self):
        """Test recording sample for invalid variant."""
        # Create experiment
        status_code, create_response = self.api.create_experiment(
            name="Test",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["time"]
        )
        exp_id = create_response["experiment_id"]
        
        # Record with invalid variant
        status_code, response = self.api.record_sample(
            experiment_id=exp_id,
            variant_name="invalid",
            metrics={"time": 100}
        )
        
        self.assertEqual(status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response["code"], "INVALID_VARIANT")
    
    def test_get_metrics(self):
        """Test retrieving metrics."""
        # Create experiment and record samples
        status_code, create_response = self.api.create_experiment(
            name="Metrics Get Test",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["time"]
        )
        exp_id = create_response["experiment_id"]
        
        self.api.record_sample(exp_id, "a", {"time": 100})
        self.api.record_sample(exp_id, "a", {"time": 105})
        
        # Get metrics
        status_code, response = self.api.get_metrics(exp_id)
        
        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertTrue(response["success"])
        self.assertIn("variants", response)
        self.assertEqual(response["variants"]["a"]["sample_count"], 2)
    
    def test_get_metrics_single_variant(self):
        """Test retrieving metrics for specific variant."""
        # Create experiment and record samples
        status_code, create_response = self.api.create_experiment(
            name="Single Variant Test",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["time"]
        )
        exp_id = create_response["experiment_id"]
        
        self.api.record_sample(exp_id, "a", {"time": 100})
        
        # Get metrics for variant a
        status_code, response = self.api.get_metrics(exp_id, "a")
        
        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertEqual(response["variant"], "a")
        self.assertEqual(response["sample_count"], 1)
    
    # ==================== Analysis Tests ====================
    
    def test_analyze_experiment(self):
        """Test analyzing an experiment."""
        # Create experiment with enough samples
        status_code, create_response = self.api.create_experiment(
            name="Analysis Test",
            description="Test",
            variants={"control": {}, "variant": {}},
            metrics=["execution_time"]
        )
        exp_id = create_response["experiment_id"]
        
        # Add samples for both variants
        for i in range(15):
            self.api.record_sample(exp_id, "control", {"execution_time": 100 + i})
            self.api.record_sample(exp_id, "variant", {"execution_time": 90 + i})
        
        # Analyze
        status_code, response = self.api.analyze_experiment(exp_id)
        
        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertTrue(response["success"])
        self.assertIn("analysis", response)
    
    # ==================== System Status Tests ====================
    
    def test_get_system_status(self):
        """Test getting system status."""
        # Create some experiments
        self.api.create_experiment(
            name="Test 1",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["time"]
        )
        
        status_code, response = self.api.get_system_status()
        
        self.assertEqual(status_code, HTTPStatus.OK)
        self.assertTrue(response["success"])
        self.assertEqual(response["status"], "operational")
        self.assertIn("statistics", response)
        self.assertGreaterEqual(response["statistics"]["total_experiments"], 1)


class TestWorkflowIntegration(unittest.TestCase):
    """Test workflow integration helpers."""
    
    def setUp(self):
        """Setup for integration tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = os.path.join(self.temp_dir, "test_registry.json")
        self.api = ABTestingAPI(registry_path=self.registry_path)
    
    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.registry_path):
            os.remove(self.registry_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_participate_no_experiment(self):
        """Test participation when no experiment exists."""
        integration = WorkflowIntegration("test-workflow", registry_path=self.registry_path)
        default_config = {"timeout": 300}
        
        config = integration.participate(default_config)
        
        self.assertEqual(config, default_config)
        self.assertFalse(integration._is_participating)
        self.assertEqual(integration.variant_name, "default")
    
    def test_participate_with_experiment(self):
        """Test participation in an active experiment."""
        # Create experiment
        status_code, response = self.api.create_experiment(
            name="Integration Test",
            description="Test",
            variants={
                "control": {"timeout": 300},
                "variant": {"timeout": 450}
            },
            metrics=["time"],
            workflow_name="test-workflow"
        )
        exp_id = response["experiment_id"]
        
        # Participate - use same registry path
        integration = WorkflowIntegration("test-workflow", registry_path=self.registry_path)
        default_config = {"timeout": 200}
        
        config = integration.participate(default_config)
        
        # Should get experiment config, not default
        self.assertTrue(integration._is_participating)
        self.assertIn(integration.variant_name, ["control", "variant"])
        self.assertIn("timeout", config)
        self.assertIn(config["timeout"], [300, 450])
    
    def test_record_success(self):
        """Test recording successful run."""
        # Create experiment
        status_code, response = self.api.create_experiment(
            name="Record Test",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["execution_time", "success_rate"],
            workflow_name="test-workflow"
        )
        
        # Participate and record
        integration = WorkflowIntegration("test-workflow", registry_path=self.registry_path)
        integration.participate({})
        
        if integration._is_participating:
            result = integration.record_success(100.5, {"custom_metric": 42})
            self.assertTrue(result)
    
    def test_record_failure(self):
        """Test recording failed run."""
        # Create experiment
        status_code, response = self.api.create_experiment(
            name="Failure Test",
            description="Test",
            variants={"a": {}, "b": {}},
            metrics=["execution_time", "success_rate"],
            workflow_name="test-workflow"
        )
        
        # Participate and record failure
        integration = WorkflowIntegration("test-workflow", registry_path=self.registry_path)
        integration.participate({})
        
        if integration._is_participating:
            result = integration.record_failure(50.0, "Test error")
            self.assertTrue(result)
    
    def test_setup_workflow_testing(self):
        """Test quick setup helper."""
        default_config = {"timeout": 300}
        
        integration, config = setup_workflow_testing(
            "test-workflow",
            default_config
        )
        
        self.assertIsInstance(integration, WorkflowIntegration)
        self.assertIsInstance(config, dict)


if __name__ == "__main__":
    unittest.main()
