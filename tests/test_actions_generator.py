#!/usr/bin/env python3
"""
Tests for GitHub Actions Pattern Analyzer and Generator

Created by @engineer-master - Comprehensive testing approach.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
import sys

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

# Import using exec to handle hyphenated names
import importlib.util

def load_module(file_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

tools_dir = Path(__file__).parent.parent / 'tools'
analyzer_module = load_module(tools_dir / 'actions-pattern-analyzer.py', 'analyzer')
generator_module = load_module(tools_dir / 'actions-generator.py', 'generator')

ActionsPatternAnalyzer = analyzer_module.ActionsPatternAnalyzer
ActionsGenerator = generator_module.ActionsGenerator


class TestActionsPatternAnalyzer(unittest.TestCase):
    """Test suite for the pattern analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_repo = Path(self.test_dir) / 'test_repo'
        self.test_repo.mkdir(parents=True)
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly."""
        analyzer = ActionsPatternAnalyzer(str(self.test_repo))
        self.assertIsNotNone(analyzer)
        self.assertEqual(analyzer.repo_path, self.test_repo)
    
    def test_analyze_empty_repository(self):
        """Test analyzing an empty repository."""
        analyzer = ActionsPatternAnalyzer(str(self.test_repo))
        results = analyzer.analyze()
        
        self.assertIn('timestamp', results)
        self.assertIn('patterns', results)
        self.assertIn('recommendations', results)
        self.assertEqual(results['existing_workflows_count'], 0)
    
    def test_detect_python_files(self):
        """Test detection of Python files."""
        # Create Python files
        (self.test_repo / 'test.py').write_text('import pytest\n')
        (self.test_repo / 'script.py').write_text('import requests\n')
        
        analyzer = ActionsPatternAnalyzer(str(self.test_repo))
        results = analyzer.analyze()
        
        self.assertIn('.py', results['file_statistics'])
        self.assertEqual(results['file_statistics']['.py'], 2)
    
    def test_detect_testing_framework(self):
        """Test detection of testing frameworks."""
        test_file = self.test_repo / 'test_example.py'
        test_file.write_text('import pytest\n\ndef test_something():\n    pass\n')
        
        analyzer = ActionsPatternAnalyzer(str(self.test_repo))
        results = analyzer.analyze()
        
        # Check that testing patterns were detected
        self.assertIn('test_files_count', results['patterns'])
    
    def test_workflow_analysis(self):
        """Test analysis of existing workflows."""
        workflows_dir = self.test_repo / '.github' / 'workflows'
        workflows_dir.mkdir(parents=True)
        
        workflow_content = """
name: Test Workflow
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python test.py
"""
        (workflows_dir / 'test.yml').write_text(workflow_content)
        
        analyzer = ActionsPatternAnalyzer(str(self.test_repo))
        results = analyzer.analyze()
        
        self.assertEqual(results['existing_workflows_count'], 1)
    
    def test_recommendations_generation(self):
        """Test that recommendations are generated."""
        # Create enough Python files to trigger recommendation
        for i in range(25):
            (self.test_repo / f'file{i}.py').write_text('import os\n')
        
        analyzer = ActionsPatternAnalyzer(str(self.test_repo))
        results = analyzer.analyze()
        
        self.assertGreater(len(results['recommendations']), 0)
        
        # Check recommendation structure
        if results['recommendations']:
            rec = results['recommendations'][0]
            self.assertIn('priority', rec)
            self.assertIn('title', rec)
            self.assertIn('description', rec)
            self.assertIn('pattern', rec)


class TestActionsGenerator(unittest.TestCase):
    """Test suite for the actions generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.test_dir) / 'actions'
        self.output_dir.mkdir(parents=True)
        
        # Sample analysis data
        self.analysis_data = {
            'timestamp': '2025-11-15T00:00:00Z',
            'recommendations': [
                {
                    'priority': 'high',
                    'title': 'Python automation',
                    'description': 'Create Python automation action',
                    'pattern': 'python_automation',
                    'action_type': 'composite'
                },
                {
                    'priority': 'high',
                    'title': 'Abstract repeated testing operation',
                    'description': 'Found testing pattern',
                    'pattern': 'testing',
                    'action_type': 'composite'
                }
            ]
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_generator_initialization(self):
        """Test that generator initializes correctly."""
        generator = ActionsGenerator(self.analysis_data)
        self.assertIsNotNone(generator)
        self.assertEqual(generator.analysis, self.analysis_data)
    
    def test_generate_actions(self):
        """Test action generation."""
        generator = ActionsGenerator(self.analysis_data)
        actions = generator.generate_actions()
        
        self.assertEqual(len(actions), 2)
        
        # Check action structure
        for action in actions:
            self.assertIn('name', action)
            self.assertIn('priority', action)
            self.assertIn('action_yaml', action)
            self.assertIn('description', action)
    
    def test_python_action_generation(self):
        """Test Python automation action generation."""
        generator = ActionsGenerator(self.analysis_data)
        actions = generator.generate_actions()
        
        python_action = next(
            (a for a in actions if 'python' in a['name']),
            None
        )
        
        self.assertIsNotNone(python_action)
        self.assertIn('inputs', python_action['action_yaml'])
        self.assertIn('runs', python_action['action_yaml'])
    
    def test_testing_action_generation(self):
        """Test testing action generation."""
        generator = ActionsGenerator(self.analysis_data)
        actions = generator.generate_actions()
        
        testing_action = next(
            (a for a in actions if 'testing' in a['name']),
            None
        )
        
        self.assertIsNotNone(testing_action)
        self.assertEqual(testing_action['action_yaml']['runs']['using'], 'composite')
    
    def test_save_actions(self):
        """Test saving actions to files."""
        generator = ActionsGenerator(self.analysis_data)
        created_files = generator.save_actions(str(self.output_dir))
        
        self.assertGreater(len(created_files), 0)
        
        # Check that files were created
        for file_path in created_files:
            self.assertTrue(Path(file_path).exists())
    
    def test_action_yaml_validity(self):
        """Test that generated YAML is valid."""
        import yaml
        
        generator = ActionsGenerator(self.analysis_data)
        generator.generate_actions()
        generator.save_actions(str(self.output_dir))
        
        # Find and parse a generated action
        action_files = list(self.output_dir.glob('*/action.yml'))
        self.assertGreater(len(action_files), 0)
        
        for action_file in action_files:
            with open(action_file, 'r') as f:
                yaml_data = yaml.safe_load(f)
            
            # Check required fields
            self.assertIn('name', yaml_data)
            self.assertIn('description', yaml_data)
            self.assertIn('runs', yaml_data)
            self.assertEqual(yaml_data['runs']['using'], 'composite')


class TestIntegration(unittest.TestCase):
    """Integration tests for analyzer and generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_repo = Path(self.test_dir) / 'test_repo'
        self.test_repo.mkdir(parents=True)
        self.output_dir = Path(self.test_dir) / 'actions'
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from analysis to generation."""
        # Create sample repository structure
        for i in range(30):
            (self.test_repo / f'module{i}.py').write_text('import json\nimport requests\n')
        
        (self.test_repo / 'test_suite.py').write_text('import pytest\n')
        
        # Analyze
        analyzer = ActionsPatternAnalyzer(str(self.test_repo))
        analysis_results = analyzer.analyze()
        
        # Generate
        generator = ActionsGenerator(analysis_results)
        actions = generator.generate_actions()
        
        # Verify
        self.assertGreater(len(actions), 0)
        self.assertGreater(len(analysis_results['recommendations']), 0)
        
        # Save
        created_files = generator.save_actions(str(self.output_dir))
        self.assertGreater(len(created_files), 0)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestActionsPatternAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestActionsGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
