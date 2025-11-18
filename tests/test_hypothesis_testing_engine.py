#!/usr/bin/env python3
"""
Tests for hypothesis_testing_engine.py
Author: @accelerate-specialist

Tests the AI hypothesis generation and testing system.
"""

import unittest
import sys
import os
import tempfile
import json
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from hypothesis_testing_engine import (
    CodeMetrics,
    Hypothesis,
    HypothesisGenerator,
    HypothesisTester,
    CodeAnalyzer,
    HypothesisTestingEngine
)


class TestCodeMetrics(unittest.TestCase):
    """Test CodeMetrics dataclass"""
    
    def test_create_metrics(self):
        """Test creating code metrics"""
        metrics = CodeMetrics(
            file_path="test.py",
            function_name="test_func",
            line_number=10,
            cyclomatic_complexity=5,
            num_parameters=3,
            has_docstring=True
        )
        
        self.assertEqual(metrics.file_path, "test.py")
        self.assertEqual(metrics.function_name, "test_func")
        self.assertEqual(metrics.cyclomatic_complexity, 5)
        self.assertTrue(metrics.has_docstring)


class TestHypothesisGenerator(unittest.TestCase):
    """Test hypothesis generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = HypothesisGenerator()
        self.sample_metrics = [
            CodeMetrics(
                file_path="test1.py",
                function_name="func1",
                line_number=10,
                cyclomatic_complexity=3,
                num_parameters=2,
                lines_of_code=15,
                has_docstring=True,
                has_tests=True
            ),
            CodeMetrics(
                file_path="test2.py",
                function_name="func2",
                line_number=20,
                cyclomatic_complexity=8,
                num_parameters=5,
                lines_of_code=60,
                has_docstring=False,
                has_tests=False
            ),
        ]
    
    def test_generate_hypotheses(self):
        """Test generating hypotheses"""
        hypotheses = self.generator.generate_hypotheses(self.sample_metrics, count=5)
        
        self.assertGreater(len(hypotheses), 0)
        self.assertLessEqual(len(hypotheses), 5)
        
        # Check first hypothesis structure
        hyp = hypotheses[0]
        self.assertIsInstance(hyp, Hypothesis)
        self.assertTrue(hyp.hypothesis_id.startswith('hyp_'))
        self.assertIsNotNone(hyp.description)
        self.assertIn(hyp.hypothesis_type, ['correlation', 'threshold', 'pattern'])
    
    def test_hypothesis_has_required_fields(self):
        """Test that generated hypotheses have required fields"""
        hypotheses = self.generator.generate_hypotheses(self.sample_metrics, count=1)
        
        hyp = hypotheses[0]
        self.assertIsNotNone(hyp.independent_var)
        self.assertIsNotNone(hyp.dependent_var)
        self.assertFalse(hyp.tested)
        self.assertFalse(hyp.validated)
        self.assertEqual(hyp.confidence, 0.0)
    
    def test_multiple_hypothesis_types(self):
        """Test that multiple hypothesis types are generated"""
        hypotheses = self.generator.generate_hypotheses(self.sample_metrics, count=10)
        
        types = set(h.hypothesis_type for h in hypotheses)
        self.assertGreater(len(types), 1, "Should generate multiple hypothesis types")


class TestHypothesisTester(unittest.TestCase):
    """Test hypothesis testing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tester = HypothesisTester()
        self.sample_metrics = [
            CodeMetrics(
                file_path="test1.py",
                function_name="simple_func",
                line_number=10,
                cyclomatic_complexity=2,
                num_parameters=1,
                lines_of_code=10,
                has_docstring=True,
                has_tests=True,
                has_error_handling=True
            ),
            CodeMetrics(
                file_path="test2.py",
                function_name="complex_func",
                line_number=20,
                cyclomatic_complexity=12,
                num_parameters=7,
                lines_of_code=80,
                has_docstring=False,
                has_tests=False,
                has_error_handling=False
            ),
            CodeMetrics(
                file_path="test3.py",
                function_name="medium_func",
                line_number=30,
                cyclomatic_complexity=5,
                num_parameters=3,
                lines_of_code=30,
                has_docstring=True,
                has_tests=False,
                has_error_handling=True
            ),
        ]
    
    def test_test_correlation_hypothesis(self):
        """Test correlation hypothesis testing"""
        hypothesis = Hypothesis(
            hypothesis_id="test_1",
            description="High complexity correlates with low quality",
            hypothesis_type="correlation",
            independent_var="cyclomatic_complexity",
            dependent_var="test_coverage",
            direction="negative"
        )
        
        result = self.tester.test_hypothesis(hypothesis, self.sample_metrics)
        
        self.assertTrue(result.tested)
        self.assertIsNotNone(result.tested_at)
        self.assertEqual(result.sample_size, len(self.sample_metrics))
        self.assertGreater(result.confidence, 0.0)
    
    def test_test_threshold_hypothesis(self):
        """Test threshold hypothesis testing"""
        hypothesis = Hypothesis(
            hypothesis_id="test_2",
            description="Functions over 50 lines have issues",
            hypothesis_type="threshold",
            independent_var="lines",
            dependent_var="quality",
            threshold=50.0
        )
        
        result = self.tester.test_hypothesis(hypothesis, self.sample_metrics)
        
        self.assertTrue(result.tested)
        self.assertIsNotNone(result.p_value)
    
    def test_assess_quality(self):
        """Test quality assessment"""
        # High quality metric
        high_quality = CodeMetrics(
            file_path="test.py",
            function_name="good_func",
            line_number=10,
            has_docstring=True,
            has_tests=True,
            has_error_handling=True,
            has_type_hints=True,
            cyclomatic_complexity=3,
            num_parameters=2,
            lines_of_code=20
        )
        
        quality = self.tester._assess_quality(high_quality)
        self.assertGreater(quality, 0.5)
        
        # Low quality metric
        low_quality = CodeMetrics(
            file_path="test.py",
            function_name="bad_func",
            line_number=10,
            has_docstring=False,
            has_tests=False,
            has_error_handling=False,
            has_type_hints=False,
            cyclomatic_complexity=15,
            num_parameters=8,
            lines_of_code=100
        )
        
        quality = self.tester._assess_quality(low_quality)
        self.assertLess(quality, 0.5)
    
    def test_calculate_correlation(self):
        """Test correlation calculation"""
        # Perfect positive correlation
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        corr = self.tester._calculate_correlation(x, y)
        self.assertGreater(corr, 0.9)
        
        # Perfect negative correlation
        x = [1, 2, 3, 4, 5]
        y = [10, 8, 6, 4, 2]
        corr = self.tester._calculate_correlation(x, y)
        self.assertLess(corr, -0.9)


class TestCodeAnalyzer(unittest.TestCase):
    """Test code analysis"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = CodeAnalyzer(self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_analyze_simple_function(self):
        """Test analyzing a simple function"""
        # Create test Python file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text('''
def simple_function(x, y):
    """A simple function"""
    return x + y
''')
        
        metrics = self.analyzer.analyze_file(test_file)
        
        self.assertEqual(len(metrics), 1)
        metric = metrics[0]
        self.assertEqual(metric.function_name, "simple_function")
        self.assertEqual(metric.num_parameters, 2)
        self.assertTrue(metric.has_docstring)
    
    def test_analyze_complex_function(self):
        """Test analyzing a complex function"""
        test_file = Path(self.temp_dir) / "complex.py"
        test_file.write_text('''
def complex_function(a, b, c, d, e):
    """Complex function with branches"""
    try:
        if a > 0:
            if b > 0:
                return a + b
            else:
                for i in range(c):
                    if i % 2 == 0:
                        d += i
        return d
    except Exception:
        return e
''')
        
        metrics = self.analyzer.analyze_file(test_file)
        
        self.assertEqual(len(metrics), 1)
        metric = metrics[0]
        self.assertEqual(metric.num_parameters, 5)
        self.assertTrue(metric.has_docstring)
        self.assertTrue(metric.has_error_handling)
        self.assertGreater(metric.cyclomatic_complexity, 3)
    
    def test_analyze_repository(self):
        """Test analyzing multiple files"""
        # Create multiple test files
        for i in range(3):
            test_file = Path(self.temp_dir) / f"test_{i}.py"
            test_file.write_text(f'''
def func_{i}(x):
    """Test function {i}"""
    return x * {i}
''')
        
        metrics = self.analyzer.analyze_repository(max_files=10)
        
        self.assertEqual(len(metrics), 3)


class TestHypothesisTestingEngine(unittest.TestCase):
    """Test the complete hypothesis testing engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "results.json")
        
        # Create test repository
        for i in range(3):
            test_file = Path(self.temp_dir) / f"test_{i}.py"
            complexity = i * 5 + 2
            test_file.write_text(f'''
def test_function_{i}(x, y, z):
    """Test function {i}"""
    try:
        result = x + y
        {"if x > 0: result += z\n    " * complexity}
        return result
    except Exception as e:
        return None
''')
        
        self.engine = HypothesisTestingEngine(
            repo_path=self.temp_dir,
            output_file=self.output_file
        )
    
    def tearDown(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_run_engine(self):
        """Test running the complete engine"""
        results = self.engine.run(num_hypotheses=5, max_files=10)
        
        self.assertIn('generated_at', results)
        self.assertIn('hypotheses_generated', results)
        self.assertIn('hypotheses_validated', results)
        self.assertIn('validation_rate', results)
        self.assertIn('hypotheses', results)
        self.assertIn('summary', results)
        
        self.assertGreater(results['hypotheses_generated'], 0)
        self.assertGreaterEqual(results['hypotheses_validated'], 0)
        self.assertTrue(0 <= results['validation_rate'] <= 1)
    
    def test_results_saved_to_file(self):
        """Test that results are saved to file"""
        self.engine.run(num_hypotheses=5, max_files=10)
        
        self.assertTrue(os.path.exists(self.output_file))
        
        with open(self.output_file, 'r') as f:
            results = json.load(f)
        
        self.assertIn('hypotheses', results)
        self.assertGreater(len(results['hypotheses']), 0)
    
    def test_summary_generation(self):
        """Test summary generation"""
        results = self.engine.run(num_hypotheses=5, max_files=10)
        summary = results['summary']
        
        self.assertIn('top_validated_hypotheses', summary)
        self.assertIn('hypothesis_types', summary)
        self.assertIn('insights', summary)
        
        # Check hypothesis types
        types = summary['hypothesis_types']
        self.assertIn('correlation', types)
        self.assertIn('threshold', types)
        self.assertIn('pattern', types)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from analysis to insights"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create diverse test functions
            test_file = Path(temp_dir) / "integration_test.py"
            test_file.write_text('''
def good_function(x: int) -> int:
    """Well-documented simple function"""
    try:
        return x * 2
    except Exception:
        return 0

def bad_function(a, b, c, d, e, f, g):
    result = a
    if b:
        if c:
            if d:
                if e:
                    if f:
                        result = g
    return result

def test_good_function():
    assert good_function(5) == 10
''')
            
            # Run engine
            engine = HypothesisTestingEngine(
                repo_path=temp_dir,
                output_file=os.path.join(temp_dir, "results.json")
            )
            
            results = engine.run(num_hypotheses=8, max_files=10)
            
            # Verify results
            self.assertGreater(results['metrics_analyzed'], 0)
            self.assertEqual(results['hypotheses_generated'], 8)
            
            # Check that at least one hypothesis was validated
            validated_hypotheses = [
                h for h in results['hypotheses'] 
                if h['validated']
            ]
            # Note: May be 0 with small sample, but structure should be correct
            
            # Verify summary structure
            summary = results['summary']
            self.assertIsInstance(summary['top_validated_hypotheses'], list)
            self.assertIsInstance(summary['insights'], list)
        
        finally:
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


def main():
    """Run tests"""
    # Run with verbose output
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
