#!/usr/bin/env python3
"""
Tests for Meta-Coordinator CLI Tool

Tests the interactive command-line interface for meta-coordination.

Created by @create-guru
Part of the Chained autonomous AI ecosystem.
"""

import unittest
import sys
import json
from pathlib import Path
from io import StringIO

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from meta_coordinator_cli import MetaCoordinatorCLI, Colors


class TestMetaCoordinatorCLI(unittest.TestCase):
    """Test the CLI interface"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cli = MetaCoordinatorCLI()
        # Disable colors for testing
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    def test_cli_initialization(self):
        """Test CLI initializes correctly"""
        self.assertIsNotNone(self.cli.coordinator)
    
    def test_analyze_task_simple(self):
        """Test analyzing a simple task"""
        task = "Fix a typo in the README file"
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        result = self.cli.analyze_task(task)
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Check result structure
        self.assertIn('complexity', result)
        self.assertIn('subtask_count', result)
        self.assertIn('required_agents', result)
        
        # Simple task should have low complexity
        self.assertEqual(result['complexity'], 'simple')
        
    def test_analyze_task_complex(self):
        """Test analyzing a complex task"""
        task = """
        Build a complete authentication system with:
        - Secure API endpoints
        - JWT token handling
        - Rate limiting
        - Comprehensive tests
        - Full documentation
        - Security audit
        """
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        result = self.cli.analyze_task(task)
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Complex task should require multiple agents
        self.assertIn(result['complexity'], ['complex', 'highly_complex'])
        self.assertGreater(result['subtask_count'], 1)
        self.assertGreater(len(result['required_agents']), 1)
    
    def test_create_coordination(self):
        """Test creating a coordination plan"""
        task_id = "test-coordination"
        task_desc = "Build API with tests and documentation"
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        plan = self.cli.create_coordination(task_id, task_desc, auto_assign=True)
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Check plan was created
        self.assertIsNotNone(plan)
        self.assertEqual(plan.task_id, task_id)
        self.assertGreater(len(plan.sub_tasks), 0)
        self.assertGreater(len(plan.required_agents), 0)
    
    def test_show_statistics(self):
        """Test displaying statistics"""
        # Create a coordination first
        self.cli.create_coordination("test-stats", "Test task for statistics")
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        self.cli.show_statistics()
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Check output contains expected sections
        self.assertIn('Total Coordinations', output)
    
    def test_print_methods(self):
        """Test various print methods"""
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        self.cli.print_header("Test Header")
        self.cli.print_success("Success message")
        self.cli.print_warning("Warning message")
        self.cli.print_error("Error message")
        self.cli.print_info("Info message")
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        self.assertIn("Test Header", output)
        self.assertIn("Success message", output)
        self.assertIn("Warning message", output)
        self.assertIn("Error message", output)
        self.assertIn("Info message", output)


class TestCLIColorHandling(unittest.TestCase):
    """Test color handling in CLI"""
    
    def test_colors_defined(self):
        """Test all color codes are defined"""
        colors = ['HEADER', 'BLUE', 'CYAN', 'GREEN', 'YELLOW', 'RED', 'BOLD', 'UNDERLINE', 'END']
        for color in colors:
            self.assertTrue(hasattr(Colors, color))
    
    def test_color_disable(self):
        """Test colors can be disabled"""
        # Save original values
        original_green = Colors.GREEN
        
        # Disable colors
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
        
        self.assertEqual(Colors.GREEN, '')
        
        # Restore
        Colors.GREEN = original_green


class TestCLITaskAnalysis(unittest.TestCase):
    """Test task analysis features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cli = MetaCoordinatorCLI()
        # Disable colors
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    def test_analyze_api_task(self):
        """Test analyzing an API development task"""
        task = "Design and implement REST API endpoints for user management"
        result = self.cli.analyze_task(task)
        
        # Should identify API-related specializations
        self.assertTrue(any('engineer' in agent.lower() for agent in result['required_agents']))
    
    def test_analyze_security_task(self):
        """Test analyzing a security task"""
        task = "Audit the authentication system for security vulnerabilities"
        result = self.cli.analyze_task(task)
        
        # Should identify security-related specializations
        self.assertTrue(any('secure' in agent.lower() or 'security' in agent.lower() 
                          for agent in result['required_agents']))
    
    def test_analyze_testing_task(self):
        """Test analyzing a testing task"""
        task = "Add comprehensive test coverage for the payment module"
        result = self.cli.analyze_task(task)
        
        # Should identify testing-related specializations
        self.assertTrue(any('assert' in agent.lower() or 'test' in agent.lower() 
                          for agent in result['required_agents']))
    
    def test_analyze_refactoring_task(self):
        """Test analyzing a refactoring task"""
        task = "Refactor the legacy code to improve maintainability and organization"
        result = self.cli.analyze_task(task)
        
        # Should identify refactoring-related specializations
        self.assertTrue(any('organize' in agent.lower() or 'refactor' in agent.lower() 
                          for agent in result['required_agents']))


class TestCLICoordination(unittest.TestCase):
    """Test coordination creation and management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cli = MetaCoordinatorCLI()
        # Disable colors
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    def test_coordination_with_auto_assign(self):
        """Test coordination with automatic agent assignment"""
        task_id = "test-auto-assign"
        task_desc = "Build feature with tests"
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        plan = self.cli.create_coordination(task_id, task_desc, auto_assign=True)
        
        sys.stdout = old_stdout
        
        self.assertGreater(len(plan.sub_tasks), 0)
    
    def test_coordination_without_auto_assign(self):
        """Test coordination without automatic agent assignment"""
        task_id = "test-no-assign"
        task_desc = "Build feature with tests"
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        plan = self.cli.create_coordination(task_id, task_desc, auto_assign=False)
        
        sys.stdout = old_stdout
        
        self.assertGreater(len(plan.sub_tasks), 0)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestMetaCoordinatorCLI))
    suite.addTests(loader.loadTestsFromTestCase(TestCLIColorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestCLITaskAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestCLICoordination))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
