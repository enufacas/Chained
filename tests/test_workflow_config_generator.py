#!/usr/bin/env python3
"""
Tests for Workflow Configuration Variant Generator

Tests the automatic generation of workflow configuration variants for A/B testing.

Author: @create-botter
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from workflow_config_generator import WorkflowConfigGenerator


class TestWorkflowConfigGenerator(unittest.TestCase):
    """Test workflow configuration variant generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = WorkflowConfigGenerator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_generate_schedule_variants(self):
        """Test schedule variant generation."""
        current_schedule = "0 */6 * * *"  # Every 6 hours
        workflow_name = "test-workflow"
        
        variants = self.generator.generate_schedule_variants(
            current_schedule,
            workflow_name
        )
        
        # Should have control variant
        self.assertIn("control", variants)
        self.assertEqual(
            variants["control"]["config"]["schedule"],
            current_schedule
        )
        
        # Should have at least 2 variants (control + 1 other)
        self.assertGreaterEqual(len(variants), 2)
    
    def test_generate_timeout_variants(self):
        """Test timeout variant generation."""
        current_timeout = 60  # 60 minutes
        workflow_name = "test-workflow"
        job_name = "test-job"
        
        variants = self.generator.generate_timeout_variants(
            current_timeout,
            workflow_name,
            job_name
        )
        
        # Should have control, conservative, and aggressive variants
        self.assertIn("control", variants)
        self.assertIn("conservative", variants)
        self.assertIn("aggressive", variants)
        
        # Conservative should be longer
        self.assertGreater(
            variants["conservative"]["config"]["timeout-minutes"],
            current_timeout
        )
        
        # Aggressive should be shorter
        self.assertLess(
            variants["aggressive"]["config"]["timeout-minutes"],
            current_timeout
        )
    
    def test_generate_concurrency_variants(self):
        """Test concurrency variant generation."""
        workflow_name = "test-workflow"
        
        variants = self.generator.generate_concurrency_variants(workflow_name)
        
        # Should have control, sequential, and cancel_old variants
        self.assertIn("control", variants)
        self.assertIn("sequential", variants)
        self.assertIn("cancel_old", variants)
        
        # Sequential should have cancel-in-progress = False
        self.assertFalse(
            variants["sequential"]["config"]["cancel-in-progress"]
        )
        
        # Cancel_old should have cancel-in-progress = True
        self.assertTrue(
            variants["cancel_old"]["config"]["cancel-in-progress"]
        )
    
    def test_generate_retry_variants(self):
        """Test retry variant generation."""
        workflow_name = "test-workflow"
        current_retries = 2
        
        variants = self.generator.generate_retry_variants(
            workflow_name,
            current_retries
        )
        
        # Should have multiple retry strategies
        self.assertIn("control", variants)
        self.assertIn("no_retry", variants)
        self.assertIn("moderate_retry", variants)
        self.assertIn("aggressive_retry", variants)
        
        # Verify max_attempts are different
        self.assertEqual(variants["no_retry"]["config"]["max_attempts"], 1)
        self.assertEqual(variants["moderate_retry"]["config"]["max_attempts"], 3)
        self.assertGreater(
            variants["aggressive_retry"]["config"]["max_attempts"],
            variants["moderate_retry"]["config"]["max_attempts"]
        )
    
    def test_adjust_schedule_frequency(self):
        """Test schedule frequency adjustment."""
        # Test doubling interval (less frequent)
        schedule = "0 */4 * * *"  # Every 4 hours
        adjusted = self.generator._adjust_schedule_frequency(schedule, 2.0)
        self.assertIn("*/8", adjusted)  # Should become every 8 hours
        
        # Test halving interval (more frequent)
        adjusted = self.generator._adjust_schedule_frequency(schedule, 0.5)
        self.assertIn("*/2", adjusted)  # Should become every 2 hours
    
    def test_shift_schedule_time(self):
        """Test schedule time shifting."""
        schedule = "0 2 * * *"  # 2 AM
        shifted = self.generator._shift_schedule_time(schedule, 4)
        self.assertIn(" 6 ", shifted)  # Should become 6 AM
        
        # Test wrapping around 24 hours
        schedule = "0 22 * * *"  # 10 PM
        shifted = self.generator._shift_schedule_time(schedule, 4)
        self.assertIn(" 2 ", shifted)  # Should wrap to 2 AM
    
    def test_generate_experiment_from_workflow_schedule(self):
        """Test generating complete experiment from workflow file."""
        # Create temporary workflow file
        workflow_content = """
name: Test Workflow
on:
  schedule:
    - cron: '0 */6 * * *'
jobs:
  test-job:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - name: Test step
        run: echo "test"
"""
        workflow_path = Path(self.temp_dir) / "test-workflow.yml"
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        
        # Generate experiment
        experiment = self.generator.generate_experiment_from_workflow(
            workflow_path,
            "schedule"
        )
        
        # Verify experiment structure
        self.assertIn("name", experiment)
        self.assertIn("description", experiment)
        self.assertIn("variants", experiment)
        self.assertIn("metrics", experiment)
        
        # Should have control variant
        self.assertIn("control", experiment["variants"])
        
        # Metrics should be defined
        self.assertIn("execution_time", experiment["metrics"])
        self.assertIn("success_rate", experiment["metrics"])
    
    def test_generate_experiment_from_workflow_timeout(self):
        """Test generating timeout experiment from workflow."""
        workflow_content = """
name: Test Workflow
on:
  workflow_dispatch:
jobs:
  test-job:
    runs-on: ubuntu-latest
    timeout-minutes: 120
    steps:
      - name: Test step
        run: echo "test"
"""
        workflow_path = Path(self.temp_dir) / "test-workflow.yml"
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        
        experiment = self.generator.generate_experiment_from_workflow(
            workflow_path,
            "timeout"
        )
        
        # Should have timeout-specific variants
        self.assertIn("conservative", experiment["variants"])
        self.assertIn("aggressive", experiment["variants"])
    
    def test_generate_experiment_from_workflow_concurrency(self):
        """Test generating concurrency experiment from workflow."""
        workflow_content = """
name: Test Workflow
on:
  push:
concurrency:
  group: test-group
  cancel-in-progress: false
jobs:
  test-job:
    runs-on: ubuntu-latest
    steps:
      - name: Test step
        run: echo "test"
"""
        workflow_path = Path(self.temp_dir) / "test-workflow.yml"
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        
        experiment = self.generator.generate_experiment_from_workflow(
            workflow_path,
            "concurrency"
        )
        
        # Should have concurrency-specific variants
        self.assertIn("sequential", experiment["variants"])
        self.assertIn("cancel_old", experiment["variants"])
    
    def test_invalid_optimization_type(self):
        """Test handling of invalid optimization type."""
        workflow_content = """
name: Test Workflow
on:
  push:
jobs:
  test-job:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""
        workflow_path = Path(self.temp_dir) / "test-workflow.yml"
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        
        # Should raise ValueError for invalid type
        with self.assertRaises(ValueError):
            self.generator.generate_experiment_from_workflow(
                workflow_path,
                "invalid_type"
            )


class TestWorkflowConfigGeneratorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = WorkflowConfigGenerator()
    
    def test_timeout_variants_no_current_timeout(self):
        """Test timeout generation when no current timeout is set."""
        variants = self.generator.generate_timeout_variants(
            None,  # No current timeout
            "test-workflow",
            "test-job"
        )
        
        # Should use default timeout
        self.assertIn("control", variants)
        control_timeout = variants["control"]["config"]["timeout-minutes"]
        self.assertGreater(control_timeout, 0)
    
    def test_schedule_variants_non_standard_cron(self):
        """Test schedule generation with non-standard cron."""
        # Test with specific time (not interval)
        schedule = "0 14 * * *"  # 2 PM daily
        variants = self.generator.generate_schedule_variants(
            schedule,
            "test-workflow"
        )
        
        # Should at least have control variant
        self.assertIn("control", variants)
    
    def test_concurrency_variants_no_current_config(self):
        """Test concurrency generation with no current config."""
        variants = self.generator.generate_concurrency_variants(
            "test-workflow",
            None  # No current config
        )
        
        # Should still generate variants
        self.assertIn("control", variants)
        self.assertIn("sequential", variants)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowConfigGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowConfigGeneratorEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
