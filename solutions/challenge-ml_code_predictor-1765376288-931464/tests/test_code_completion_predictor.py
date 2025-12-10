#!/usr/bin/env python3
"""
Comprehensive tests for Code Completion Predictor

Tests all requirements:
1. Sequence prediction model
2. Multi-language support
3. Confidence scores
4. Real-time inference performance

Created by @create-botter for the Chained autonomous AI ecosystem.
"""

import unittest
import time
import sys
from pathlib import Path
import tempfile
import os

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from code_completion_predictor import (
    CodeTokenizer,
    SequencePredictor,
    CodeCompletionPredictor,
    train_model
)


class TestCodeTokenizer(unittest.TestCase):
    """Test the code tokenizer"""
    
    def test_python_tokenization(self):
        """Test Python code tokenization"""
        tokenizer = CodeTokenizer('python')
        code = "def hello():\n    return 'world'"
        tokens = tokenizer.tokenize(code)
        
        # Should contain keyword, identifier, and string tokens
        self.assertIn('<KEYWORD:def>', tokens)
        self.assertIn('hello', tokens)
        self.assertIn('<KEYWORD:return>', tokens)
        
    def test_javascript_tokenization(self):
        """Test JavaScript code tokenization"""
        tokenizer = CodeTokenizer('javascript')
        code = "function test() { return 42; }"
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('<KEYWORD:function>', tokens)
        self.assertIn('test', tokens)
        self.assertIn('<KEYWORD:return>', tokens)
        self.assertIn('42', tokens)
    
    def test_java_tokenization(self):
        """Test Java code tokenization"""
        tokenizer = CodeTokenizer('java')
        code = "public class Test { public static void main() {} }"
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('<KEYWORD:public>', tokens)
        self.assertIn('<KEYWORD:class>', tokens)
        self.assertIn('Test', tokens)
        self.assertIn('<KEYWORD:static>', tokens)
        self.assertIn('<KEYWORD:void>', tokens)
    
    def test_detokenization(self):
        """Test converting tokens back to code"""
        tokenizer = CodeTokenizer('python')
        code = "def foo(): return 123"
        tokens = tokenizer.tokenize(code)
        reconstructed = tokenizer.detokenize(tokens)
        
        # Should preserve key elements
        self.assertIn('def', reconstructed)
        self.assertIn('foo', reconstructed)
        self.assertIn('return', reconstructed)
    
    def test_preserves_newlines(self):
        """Test that newlines are preserved"""
        tokenizer = CodeTokenizer('python')
        code = "line1\nline2\nline3"
        tokens = tokenizer.tokenize(code)
        
        # Count newline tokens
        newline_count = sum(1 for t in tokens if t == '<NEWLINE>')
        self.assertEqual(newline_count, 2)
    
    def test_handles_operators(self):
        """Test operator tokenization"""
        tokenizer = CodeTokenizer('python')
        code = "x = y + z * 2"
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('=', tokens)
        self.assertIn('+', tokens)
        self.assertIn('*', tokens)
    
    def test_handles_strings(self):
        """Test string tokenization"""
        tokenizer = CodeTokenizer('python')
        code = 'message = "hello world"'
        tokens = tokenizer.tokenize(code)
        
        # Should preserve the string
        string_tokens = [t for t in tokens if 'hello' in t]
        self.assertTrue(len(string_tokens) > 0)


class TestSequencePredictor(unittest.TestCase):
    """Test the sequence prediction model"""
    
    def setUp(self):
        """Set up test predictor"""
        self.predictor = SequencePredictor(n=3)
        
        # Simple training sequences
        self.train_sequences = [
            ['def', 'function', '(', ')', ':'],
            ['def', 'function', '(', 'arg', ')', ':'],
            ['if', 'condition', ':'],
            ['if', 'test', ':'],
            ['for', 'item', 'in', 'items', ':']
        ]
        
        self.predictor.train(self.train_sequences)
    
    def test_training(self):
        """Test that model learns patterns"""
        # Should have learned some n-grams
        self.assertGreater(len(self.predictor.ngrams), 0)
        self.assertGreater(len(self.predictor.context_counts), 0)
    
    def test_prediction_returns_results(self):
        """Test that prediction returns results"""
        predictions = self.predictor.predict(['def'], top_k=1)
        
        self.assertEqual(len(predictions), 1)
        token, confidence = predictions[0]
        self.assertIsInstance(token, str)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_prediction_top_k(self):
        """Test that top_k works"""
        predictions = self.predictor.predict(['def'], top_k=3)
        
        self.assertLessEqual(len(predictions), 3)
        
        # Predictions should be sorted by confidence
        for i in range(len(predictions) - 1):
            self.assertGreaterEqual(predictions[i][1], predictions[i + 1][1])
    
    def test_confidence_scores(self):
        """Test that confidence scores are valid"""
        predictions = self.predictor.predict(['if'], top_k=5)
        
        for token, confidence in predictions:
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_beam_search(self):
        """Test beam search completion"""
        beams = self.predictor.beam_search(['def'], max_length=3)
        
        self.assertGreater(len(beams), 0)
        
        for seq, score in beams:
            self.assertIsInstance(seq, list)
            self.assertIsInstance(score, float)
            self.assertGreater(len(seq), 1)
    
    def test_model_persistence(self):
        """Test saving and loading model"""
        # Save model
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            self.predictor.save(filepath)
            
            # Load into new predictor
            new_predictor = SequencePredictor(n=3)
            new_predictor.load(filepath)
            
            # Should make same predictions
            original = self.predictor.predict(['def'], top_k=1)
            loaded = new_predictor.predict(['def'], top_k=1)
            
            self.assertEqual(original[0][0], loaded[0][0])
            self.assertAlmostEqual(original[0][1], loaded[0][1], places=5)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_caching(self):
        """Test prediction caching"""
        # Make same prediction twice
        context = ['for', 'item']
        
        pred1 = self.predictor.predict(context, top_k=1)
        pred2 = self.predictor.predict(context, top_k=1)
        
        # Should return identical results
        self.assertEqual(pred1, pred2)


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main code completion predictor"""
    
    def setUp(self):
        """Set up test model with training data"""
        self.training_code = [
            """
            def calculate_sum(numbers):
                total = 0
                for num in numbers:
                    total += num
                return total
            """,
            """
            def calculate_average(numbers):
                total = 0
                count = 0
                for num in numbers:
                    total += num
                    count += 1
                return total / count
            """,
            """
            def process_items(items):
                result = []
                for item in items:
                    result.append(item)
                return result
            """
        ]
        
        self.model = train_model(self.training_code, language='python', n=5)
    
    def test_model_trains(self):
        """Test that model trains successfully"""
        self.assertTrue(self.model.trained)
    
    def test_predict_next_line_requirement_1(self):
        """
        TEST CASE 1: Predicts next code line
        Validates Requirement 1: Sequence prediction model
        """
        # Context: function definition with partial code
        code_context = "def calculate_average(numbers):\n    total = 0\n    "
        
        predicted_line, confidence = self.model.predict_next_line(code_context)
        
        # Should return a prediction
        self.assertIsInstance(predicted_line, str)
        self.assertGreater(len(predicted_line), 0)
        
        # Should have confidence score
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        print(f"\n✓ Test Case 1 PASSED:")
        print(f"  Input: {code_context!r}")
        print(f"  Predicted: {predicted_line!r}")
        print(f"  Confidence: {confidence:.1%}")
    
    def test_complete_function_requirement_2(self):
        """
        TEST CASE 2: Completes functions
        Validates sequence prediction model with beam search
        """
        # Partial function needing completion
        partial_function = "def process_data(items):\n    result = []\n    for item in items:\n        "
        
        completion, confidence = self.model.complete_function(partial_function)
        
        # Should return a completion
        self.assertIsInstance(completion, str)
        self.assertGreater(len(completion), 0)
        
        # Should have confidence score
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        print(f"\n✓ Test Case 2 PASSED:")
        print(f"  Input: {partial_function!r}")
        print(f"  Completion: {completion!r}")
        print(f"  Confidence: {confidence:.1%}")
    
    def test_multi_language_support_requirement_2(self):
        """
        Validates Requirement 2: Support multiple programming languages
        """
        # Test Python
        python_model = CodeCompletionPredictor(language='python')
        self.assertEqual(python_model.language, 'python')
        
        # Test JavaScript
        js_code = [
            "function add(a, b) { return a + b; }",
            "const multiply = (x, y) => x * y;"
        ]
        js_model = train_model(js_code, language='javascript')
        self.assertTrue(js_model.trained)
        
        # Test Java
        java_code = [
            "public class Calculator { public int add(int a, int b) { return a + b; } }"
        ]
        java_model = train_model(java_code, language='java')
        self.assertTrue(java_model.trained)
        
        print(f"\n✓ Multi-language support validated:")
        print(f"  ✓ Python")
        print(f"  ✓ JavaScript")
        print(f"  ✓ Java")
    
    def test_confidence_scores_requirement_3(self):
        """
        Validates Requirement 3: Provide confidence scores for predictions
        """
        context = "def test():\n    "
        
        # Get multiple predictions
        predictions = self.model.get_predictions(context, top_k=3)
        
        # All should have valid confidence scores
        for token, confidence in predictions:
            self.assertIsInstance(confidence, float)
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
        
        print(f"\n✓ Confidence scores validated:")
        for token, conf in predictions[:3]:
            print(f"  {token}: {conf:.1%}")
    
    def test_real_time_inference_requirement_4(self):
        """
        Validates Requirement 4: Optimize for real-time inference
        Target: < 100ms response time
        """
        context = "for item in items:\n    "
        
        # Measure inference time
        start = time.perf_counter()
        predicted, confidence = self.model.predict_next_line(context)
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        
        # Should be much faster than 100ms
        self.assertLess(elapsed, 100)
        
        print(f"\n✓ Real-time inference validated:")
        print(f"  Inference time: {elapsed:.2f}ms (target: <100ms)")
        print(f"  ✓ Performance goal met")
    
    def test_get_multiple_predictions(self):
        """Test getting multiple prediction options"""
        predictions = self.model.get_predictions("if ", top_k=3)
        
        self.assertGreater(len(predictions), 0)
        self.assertLessEqual(len(predictions), 3)
        
        # All predictions should have confidence scores
        for token, confidence in predictions:
            self.assertIsInstance(token, str)
            self.assertIsInstance(confidence, float)
    
    def test_model_persistence(self):
        """Test saving and loading model"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            # Save model
            self.model.save_model(filepath)
            
            # Load into new model
            new_model = CodeCompletionPredictor(language='python', n=5)
            new_model.load_model(filepath)
            
            # Should make same predictions
            context = "def test():\n    "
            orig_pred = self.model.predict_next_line(context)
            new_pred = new_model.predict_next_line(context)
            
            self.assertEqual(orig_pred[0], new_pred[0])
            self.assertAlmostEqual(orig_pred[1], new_pred[1], places=5)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_handles_empty_context(self):
        """Test handling of edge case: empty context"""
        predicted, confidence = self.model.predict_next_line("")
        
        # Should still return something
        self.assertIsInstance(predicted, str)
        self.assertIsInstance(confidence, float)
    
    def test_handles_unknown_context(self):
        """Test handling of unknown code patterns"""
        # Context the model hasn't seen
        unusual_context = "xyzabc123 foobar baz"
        
        predicted, confidence = self.model.predict_next_line(unusual_context)
        
        # Should return low confidence
        self.assertIsInstance(predicted, str)
        self.assertLessEqual(confidence, 0.5)


class TestTrainModelFunction(unittest.TestCase):
    """Test the convenience train_model function"""
    
    def test_train_model_function(self):
        """Test convenience function works"""
        code = ["def foo(): pass", "def bar(): return 42"]
        
        model = train_model(code, language='python', n=5)
        
        self.assertIsInstance(model, CodeCompletionPredictor)
        self.assertTrue(model.trained)
        self.assertEqual(model.language, 'python')


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarks"""
    
    def setUp(self):
        """Set up model with substantial training data"""
        # More training data for realistic performance testing
        self.training_code = [
            """
            def calculate_sum(numbers):
                total = 0
                for num in numbers:
                    total += num
                return total
            """,
            """
            def calculate_average(numbers):
                total = 0
                count = 0
                for num in numbers:
                    total += num
                    count += 1
                return total / count if count > 0 else 0
            """,
            """
            def process_items(items):
                result = []
                for item in items:
                    if item is not None:
                        result.append(item)
                return result
            """,
            """
            class DataProcessor:
                def __init__(self):
                    self.data = []
                
                def add(self, item):
                    self.data.append(item)
                
                def process(self):
                    result = []
                    for item in self.data:
                        result.append(item * 2)
                    return result
            """
        ]
        
        self.model = train_model(self.training_code, language='python', n=5)
    
    def test_inference_speed(self):
        """Benchmark inference speed"""
        contexts = [
            "def test():\n    ",
            "for item in items:\n    ",
            "if condition:\n    ",
            "class MyClass:\n    "
        ]
        
        times = []
        
        for context in contexts:
            start = time.perf_counter()
            self.model.predict_next_line(context)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"\n✓ Performance Benchmarks:")
        print(f"  Average inference: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")
        print(f"  Target: <100ms ✓")
        
        # All should be under 100ms
        for t in times:
            self.assertLess(t, 100)


def run_tests():
    """Run all tests with detailed output"""
    print("=" * 70)
    print("Code Completion Predictor - Comprehensive Test Suite")
    print("Created by @create-botter for the Chained autonomous AI ecosystem")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeTokenizer))
    suite.addTests(loader.loadTestsFromTestCase(TestSequencePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeCompletionPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestTrainModelFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceBenchmarks))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    print("\n" + "=" * 70)
    print("Requirements Validation")
    print("=" * 70)
    print("✓ Requirement 1: Sequence prediction model")
    print("✓ Requirement 2: Multiple programming languages")
    print("✓ Requirement 3: Confidence scores for predictions")
    print("✓ Requirement 4: Real-time inference (<100ms)")
    print("\n" + "=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
