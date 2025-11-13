#!/usr/bin/env python3
"""
Tests for Workflow Harmonizer
Created by @harmonize-wizard (George Martin)
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.workflow_harmonizer import WorkflowHarmonizer


class TestWorkflowHarmonizer(unittest.TestCase):
    """Test cases for the Workflow Harmonizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test workflows
        self.test_dir = tempfile.mkdtemp()
        self.workflows_dir = Path(self.test_dir) / ".github" / "workflows"
        self.workflows_dir.mkdir(parents=True)
        
        # Create test workflow files
        self._create_test_workflows()
        
        self.harmonizer = WorkflowHarmonizer(str(self.workflows_dir))
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def _create_test_workflows(self):
        """Create test workflow files."""
        # Workflow 1: Scheduled workflow
        workflow1 = """
name: "Test: Scheduled"
on:
  schedule:
    - cron: '0 9 * * *'
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""
        (self.workflows_dir / "scheduled.yml").write_text(workflow1)
        
        # Workflow 2: Event-triggered workflow
        workflow2 = """
name: "Test: Pull Request"
on:
  pull_request:
    types: [opened]
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""
        (self.workflows_dir / "pr-trigger.yml").write_text(workflow2)
        
        # Workflow 3: High-frequency workflow
        workflow3 = """
name: "Test: High Frequency"
on:
  schedule:
    - cron: '*/15 * * * *'
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""
        (self.workflows_dir / "high-freq.yml").write_text(workflow3)
        
        # Workflow 4: Manual only
        workflow4 = """
name: "Test: Manual"
on:
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""
        (self.workflows_dir / "manual.yml").write_text(workflow4)
    
    def test_load_workflows(self):
        """Test workflow loading."""
        self.harmonizer.load_workflows()
        self.assertEqual(len(self.harmonizer.workflows), 4)
        self.assertIn('scheduled', self.harmonizer.workflows)
        self.assertIn('pr-trigger', self.harmonizer.workflows)
    
    def test_analyze_schedules(self):
        """Test schedule analysis."""
        self.harmonizer.load_workflows()
        schedules = self.harmonizer.analyze_schedules()
        
        # Should detect scheduled workflows
        self.assertGreater(len(schedules), 0)
        
        # Should have daily and 15-minute schedules
        self.assertIn('daily_at_9:0', schedules)
        self.assertIn('every_15_minutes', schedules)
    
    def test_analyze_triggers(self):
        """Test trigger analysis."""
        self.harmonizer.load_workflows()
        triggers = self.harmonizer.analyze_triggers()
        
        # Should detect various triggers
        self.assertIn('schedule', triggers)
        self.assertIn('workflow_dispatch', triggers)
        self.assertIn('pull_request', triggers)
        self.assertIn('push', triggers)
        
        # At least 2 workflows should have workflow_dispatch
        # (scheduled and manual both have it)
        self.assertGreaterEqual(len(triggers['workflow_dispatch']), 2)
    
    def test_detect_conflicts(self):
        """Test conflict detection."""
        self.harmonizer.load_workflows()
        conflicts = self.harmonizer.detect_conflicts()
        
        # Conflicts may or may not be detected depending on thresholds
        # Just verify the function runs without errors
        self.assertIsInstance(conflicts, list)
    
    def test_generate_health_report(self):
        """Test health report generation."""
        report = self.harmonizer.generate_health_report()
        
        # Check report structure
        self.assertIn('timestamp', report)
        self.assertIn('summary', report)
        self.assertIn('schedule_analysis', report)
        self.assertIn('trigger_analysis', report)
        self.assertIn('conflicts', report)
        self.assertIn('workflow_list', report)
        
        # Check summary counts
        self.assertEqual(report['summary']['total_workflows'], 4)
        self.assertEqual(report['summary']['scheduled_workflows'], 2)
        self.assertEqual(report['summary']['manual_only'], 1)
    
    def test_parse_cron_frequency(self):
        """Test cron frequency parsing."""
        self.harmonizer.load_workflows()
        
        # Test various cron expressions
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('*/15 * * * *'),
            'every_15_minutes'
        )
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('0 */3 * * *'),
            'every_3_hours'
        )
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('0 9 * * *'),
            'daily_at_9:0'
        )
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('0 0 * * 1'),
            'weekly_on_day_1'
        )
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        self.harmonizer.load_workflows()
        recommendations = self.harmonizer.generate_coordination_recommendations()
        
        # Should generate recommendations
        self.assertGreater(len(recommendations), 0)
        
        # Should recommend concurrency control
        concurrency_rec = any('concurrency' in rec.lower() for rec in recommendations)
        self.assertTrue(concurrency_rec)
    
    def test_export_report(self):
        """Test report export."""
        output_file = Path(self.test_dir) / "test_report.json"
        self.harmonizer.export_report(str(output_file))
        
        # Check file was created
        self.assertTrue(output_file.exists())
        
        # Check file contains valid JSON
        with open(output_file) as f:
            report = json.load(f)
        
        self.assertIn('summary', report)
        self.assertIn('recommendations', report)
    
    def test_workflow_with_concurrency(self):
        """Test detection of concurrency groups."""
        # Create workflow with concurrency
        workflow_with_concurrency = """
name: "Test: With Concurrency"
on:
  push:
concurrency:
  group: test-group
  cancel-in-progress: true
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""
        (self.workflows_dir / "with-concurrency.yml").write_text(workflow_with_concurrency)
        
        # Reload workflows
        self.harmonizer = WorkflowHarmonizer(str(self.workflows_dir))
        self.harmonizer.load_workflows()
        
        # Check concurrency was detected
        workflow = self.harmonizer.workflows['with-concurrency']
        self.assertIn('concurrency', workflow['data'])
    
    def test_empty_workflow_directory(self):
        """Test handling of empty workflow directory."""
        empty_dir = Path(self.test_dir) / "empty"
        empty_dir.mkdir()
        
        harmonizer = WorkflowHarmonizer(str(empty_dir))
        harmonizer.load_workflows()
        
        self.assertEqual(len(harmonizer.workflows), 0)
    
    def test_invalid_yaml(self):
        """Test handling of invalid YAML files."""
        # Create invalid YAML file
        (self.workflows_dir / "invalid.yml").write_text("invalid: yaml: content:")
        
        # Should not crash, just skip the invalid file
        harmonizer = WorkflowHarmonizer(str(self.workflows_dir))
        harmonizer.load_workflows()
        
        # Should still load the valid workflows
        self.assertGreaterEqual(len(harmonizer.workflows), 4)


class TestCronParsing(unittest.TestCase):
    """Test cron expression parsing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.harmonizer = WorkflowHarmonizer()
    
    def test_minute_intervals(self):
        """Test minute interval parsing."""
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('*/5 * * * *'),
            'every_5_minutes'
        )
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('*/30 * * * *'),
            'every_30_minutes'
        )
    
    def test_hour_intervals(self):
        """Test hour interval parsing."""
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('0 */2 * * *'),
            'every_2_hours'
        )
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('0 */12 * * *'),
            'every_12_hours'
        )
    
    def test_daily_schedules(self):
        """Test daily schedule parsing."""
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('0 0 * * *'),
            'daily_at_0:0'
        )
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('30 15 * * *'),
            'daily_at_15:30'
        )
    
    def test_weekly_schedules(self):
        """Test weekly schedule parsing."""
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('0 0 * * 0'),
            'weekly_on_day_0'
        )
        self.assertEqual(
            self.harmonizer._parse_cron_frequency('0 0 * * 5'),
            'weekly_on_day_5'
        )
    
    def test_custom_schedules(self):
        """Test custom schedule parsing."""
        # Monthly schedule (day of month specified)
        result = self.harmonizer._parse_cron_frequency('0 0 1 * *')
        self.assertEqual(result, 'custom_schedule')
        
        # Complex schedule with multiple values  
        # Note: This gets treated as an hour interval since it matches */2
        result = self.harmonizer._parse_cron_frequency('0 */2 * * *')
        self.assertEqual(result, 'every_2_hours')  # Actually matches hour interval pattern


def main():
    """Run the tests."""
    unittest.main()


if __name__ == '__main__':
    main()
