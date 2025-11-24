#!/usr/bin/env python3
"""
Test suite for AI Code Pattern Hypothesis Testing Workflow

Tests the workflow components and hypothesis testing integration.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from hypothesis_testing_engine import (
    CodeMetrics,
    Hypothesis,
    HypothesisGenerator,
    HypothesisTester,
    CodeAnalyzer,
    HypothesisTestingEngine
)


class TestHypothesisWorkflowIntegration(unittest.TestCase):
    """Test hypothesis testing workflow integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.test_dir, 'results.json')
    
    def test_workflow_basic_execution(self):
        """Test that workflow components can execute successfully"""
        # Create a simple test repo
        test_repo = os.path.join(self.test_dir, 'test_repo')
        os.makedirs(test_repo)
        
        # Create a sample Python file
        sample_file = os.path.join(test_repo, 'sample.py')
        with open(sample_file, 'w') as f:
            f.write('''
def simple_function(x, y):
    """A simple function with docstring"""
    return x + y

def complex_function(a, b, c, d, e):
    """A more complex function"""
    if a > 0:
        if b > 0:
            if c > 0:
                return a + b + c
    return 0

def long_function():
    """A longer function for testing"""
    result = 0
    for i in range(100):
        result += i
        if result > 50:
            result = result // 2
        else:
            result = result * 2
    return result
''')
        
        # Run the engine
        engine = HypothesisTestingEngine(
            repo_path=test_repo,
            output_file=self.output_file
        )
        results = engine.run(num_hypotheses=5, max_files=10)
        
        # Verify results structure
        self.assertIn('generated_at', results)
        self.assertIn('hypotheses_generated', results)
        self.assertIn('hypotheses_validated', results)
        self.assertIn('validation_rate', results)
        self.assertIn('hypotheses', results)
        self.assertGreater(len(results['hypotheses']), 0)
        
        # Verify output file was created
        self.assertTrue(os.path.exists(self.output_file))
        
        # Verify JSON is valid
        with open(self.output_file) as f:
            loaded_results = json.load(f)
            self.assertEqual(loaded_results['hypotheses_generated'], 
                           results['hypotheses_generated'])
    
    def test_hypothesis_validation(self):
        """Test that hypotheses are properly validated"""
        # Create sample metrics that should validate certain hypotheses
        metrics = [
            CodeMetrics(
                file_path='test.py',
                function_name='high_complexity',
                line_number=10,
                cyclomatic_complexity=15,
                lines_of_code=100,
                has_docstring=False,
                has_tests=False
            ),
            CodeMetrics(
                file_path='test.py',
                function_name='low_complexity',
                line_number=50,
                cyclomatic_complexity=2,
                lines_of_code=10,
                has_docstring=True,
                has_tests=True
            ),
        ]
        
        # Generate and test hypotheses
        generator = HypothesisGenerator()
        hypotheses = generator.generate_hypotheses(metrics, count=5)
        
        self.assertEqual(len(hypotheses), 5)
        
        # Test hypotheses
        tester = HypothesisTester()
        for hypothesis in hypotheses:
            tested = tester.test_hypothesis(hypothesis, metrics)
            self.assertTrue(tested.tested)
            self.assertIsNotNone(tested.tested_at)
            self.assertGreater(tested.sample_size, 0)
    
    def test_results_format_for_workflow(self):
        """Test that results are in correct format for workflow consumption"""
        test_repo = os.path.join(self.test_dir, 'test_repo2')
        os.makedirs(test_repo)
        
        # Create a simple file
        with open(os.path.join(test_repo, 'test.py'), 'w') as f:
            f.write('def test(): pass')
        
        engine = HypothesisTestingEngine(
            repo_path=test_repo,
            output_file=self.output_file
        )
        results = engine.run(num_hypotheses=3, max_files=5)
        
        # Check required fields for workflow
        self.assertIsInstance(results['hypotheses_generated'], int)
        self.assertIsInstance(results['hypotheses_validated'], int)
        self.assertIsInstance(results['validation_rate'], (int, float))
        self.assertIsInstance(results['summary'], dict)
        self.assertIn('top_validated_hypotheses', results['summary'])
        self.assertIn('insights', results['summary'])
    
    def test_learning_system_integration(self):
        """Test that results can be integrated with learning system"""
        test_repo = os.path.join(self.test_dir, 'test_repo3')
        os.makedirs(test_repo)
        
        with open(os.path.join(test_repo, 'test.py'), 'w') as f:
            f.write('def test(): pass')
        
        engine = HypothesisTestingEngine(
            repo_path=test_repo,
            output_file=self.output_file
        )
        results = engine.run(num_hypotheses=2, max_files=5)
        
        # Create learning entry format
        learning_entry = {
            'timestamp': results['generated_at'],
            'type': 'hypothesis_testing',
            'metrics': {
                'functions_analyzed': results['metrics_analyzed'],
                'hypotheses_generated': results['hypotheses_generated'],
                'hypotheses_validated': results['hypotheses_validated'],
                'validation_rate': results['validation_rate']
            }
        }
        
        # Verify learning entry is JSON serializable
        json_str = json.dumps(learning_entry)
        self.assertIsInstance(json_str, str)
        
        # Verify we can reload it
        reloaded = json.loads(json_str)
        self.assertEqual(reloaded['type'], 'hypothesis_testing')
    
    def test_issue_creation_data_format(self):
        """Test that validated hypotheses have data needed for issue creation"""
        metrics = [
            CodeMetrics(
                file_path='test.py',
                function_name='test_func',
                line_number=1,
                cyclomatic_complexity=5,
                lines_of_code=20
            )
        ] * 10  # Repeat to get enough samples
        
        generator = HypothesisGenerator()
        hypotheses = generator.generate_hypotheses(metrics, count=3)
        
        tester = HypothesisTester()
        for hypothesis in hypotheses:
            tested = tester.test_hypothesis(hypothesis, metrics)
            
            # Check all fields needed for issue creation
            self.assertIsNotNone(tested.description)
            self.assertIsNotNone(tested.hypothesis_type)
            self.assertIsNotNone(tested.confidence)
            self.assertIsNotNone(tested.sample_size)
            self.assertIsNotNone(tested.validated)
            
            # If validated, should have examples
            if tested.validated:
                # Examples might be empty if no clear pattern found
                self.assertIsInstance(tested.supporting_examples, list)


class TestWorkflowComponents(unittest.TestCase):
    """Test individual workflow components"""
    
    def test_summary_generation(self):
        """Test markdown summary generation"""
        results = {
            'generated_at': '2025-11-24T00:00:00+00:00',
            'repository': '.',
            'metrics_analyzed': 100,
            'hypotheses_generated': 10,
            'hypotheses_validated': 3,
            'validation_rate': 0.3,
            'summary': {
                'top_validated_hypotheses': [
                    {
                        'description': 'Test hypothesis 1',
                        'confidence': 0.85,
                        'sample_size': 50
                    }
                ],
                'insights': ['Insight 1', 'Insight 2']
            }
        }
        
        # Generate summary text (simulating what workflow does)
        summary = f"""## 🔬 AI Code Pattern Hypothesis Testing Results

**Run Date:** {results['generated_at'][:10]}
**Repository:** {results['repository']}

### 📊 Statistics
- **Functions Analyzed:** {results['metrics_analyzed']}
- **Hypotheses Generated:** {results['hypotheses_generated']}
- **Hypotheses Validated:** {results['hypotheses_validated']}
- **Validation Rate:** {results['validation_rate']:.1%}
"""
        
        # Verify summary contains key information
        self.assertIn('2025-11-24', summary)
        self.assertIn('100', summary)
        self.assertIn('10', summary)
        self.assertIn('3', summary)
        self.assertIn('30.0%', summary)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestHypothesisWorkflowIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowComponents))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
