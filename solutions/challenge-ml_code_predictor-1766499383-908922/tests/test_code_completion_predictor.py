"""
Test Suite for Code Completion Predictor

Comprehensive tests for the Code Completion Predictor by @create-botter.
Tests all requirements, test cases, and edge cases.

Challenge ID: challenge-ml_code_predictor-1766499383-908922

Requirements being tested:
    1. Sequence prediction model
    2. Multi-language support
    3. Confidence scores for predictions
    4. Real-time inference optimization

Test Cases being validated:
    1. Predict next code line
    2. Complete functions
"""

import unittest
import sys
import os
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.code_completion_predictor import (
    CodeTokenizer,
    SequencePredictor,
    CodeCompletionPredictor,
    train_model
)


class TestCodeTokenizer(unittest.TestCase):
    """Test the CodeTokenizer class"""
    
    def test_python_tokenization(self):
        """Test Python code tokenization"""
        tokenizer = CodeTokenizer('python')
        code = 'def add(a, b): return a + b'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('def', tokens)
        self.assertIn('add', tokens)
        self.assertIn('return', tokens)
        self.assertIn('+', tokens)
        self.assertGreater(len(tokens), 5)
    
    def test_javascript_tokenization(self):
        """Test JavaScript code tokenization"""
        tokenizer = CodeTokenizer('javascript')
        code = 'const add = (a, b) => a + b'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('const', tokens)
        self.assertIn('add', tokens)
        self.assertIn('=>', tokens)
        self.assertIn('+', tokens)
    
    def test_typescript_tokenization(self):
        """Test TypeScript code tokenization"""
        tokenizer = CodeTokenizer('typescript')
        code = 'interface User { name: string; age: number; }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('interface', tokens)
        self.assertIn('User', tokens)
        self.assertIn(':', tokens)
        self.assertIn('string', tokens)
    
    def test_java_tokenization(self):
        """Test Java code tokenization"""
        tokenizer = CodeTokenizer('java')
        code = 'public class Main { public static void main(String[] args) {} }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('public', tokens)
        self.assertIn('class', tokens)
        self.assertIn('static', tokens)
        self.assertIn('void', tokens)
    
    def test_go_tokenization(self):
        """Test Go code tokenization"""
        tokenizer = CodeTokenizer('go')
        code = 'func add(a int, b int) int { return a + b }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('func', tokens)
        self.assertIn('add', tokens)
        self.assertIn('return', tokens)
    
    def test_multi_char_operators(self):
        """Test multi-character operator handling"""
        tokenizer = CodeTokenizer('python')
        code = 'if x == 5 and y >= 10 or z != 3'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('==', tokens)
        self.assertIn('>=', tokens)
        self.assertIn('!=', tokens)
    
    def test_comment_removal_python(self):
        """Test Python comment filtering"""
        tokenizer = CodeTokenizer('python')
        code = 'def foo(): # this is a comment\n    return 42'
        tokens = tokenizer.tokenize(code)
        
        # Comment content should be removed
        self.assertNotIn('comment', tokens)
        self.assertIn('def', tokens)
        self.assertIn('return', tokens)
        self.assertIn('42', tokens)
    
    def test_comment_removal_javascript(self):
        """Test JavaScript comment filtering"""
        tokenizer = CodeTokenizer('javascript')
        code = 'const x = 5; // comment here'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('const', tokens)
        self.assertIn('x', tokens)
        self.assertNotIn('comment', tokens)
    
    def test_empty_code(self):
        """Test handling of empty code"""
        tokenizer = CodeTokenizer('python')
        tokens = tokenizer.tokenize('')
        self.assertEqual(tokens, [])
    
    def test_context_features(self):
        """Test context feature extraction"""
        tokenizer = CodeTokenizer('python')
        code = 'def foo(x):\n    if x > 0:\n        return x'
        tokens = tokenizer.tokenize(code)
        features = tokenizer.get_context_features(tokens)
        
        self.assertIn('keyword_count', features)
        self.assertIn('has_function_def', features)
        self.assertIn('has_control_flow', features)
        self.assertTrue(features['has_function_def'])
        self.assertTrue(features['has_control_flow'])


class TestSequencePredictor(unittest.TestCase):
    """Test the SequencePredictor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.predictor = SequencePredictor(max_n=3)
        
        # Simple training data
        self.training_sequences = [
            ['def', 'add', '(', 'a', ',', 'b', ')', ':', 'return', 'a', '+', 'b'],
            ['def', 'multiply', '(', 'x', ',', 'y', ')', ':', 'return', 'x', '*', 'y'],
            ['def', 'subtract', '(', 'a', ',', 'b', ')', ':', 'return', 'a', '-', 'b']
        ]
    
    def test_training(self):
        """Test model training"""
        self.predictor.train(self.training_sequences)
        
        # Check that n-grams were created
        for n in range(1, 4):
            self.assertGreater(len(self.predictor.ngrams[n]), 0)
    
    def test_prediction(self):
        """Test basic prediction"""
        self.predictor.train(self.training_sequences)
        
        context = ['def', 'foo', '(', 'a', ',', 'b', ')', ':']
        predictions = self.predictor.predict(context, top_k=3)
        
        self.assertIsInstance(predictions, list)
        self.assertGreater(len(predictions), 0)
        
        # Check prediction format
        for token, conf in predictions:
            self.assertIsInstance(token, str)
            self.assertIsInstance(conf, float)
            self.assertGreaterEqual(conf, 0.0)
            self.assertLessEqual(conf, 1.0)
    
    def test_prediction_with_temperature(self):
        """Test prediction with different temperatures"""
        self.predictor.train(self.training_sequences)
        
        context = ['def', 'test', '(', 'x', ')', ':']
        
        # Low temperature (more focused)
        preds_low = self.predictor.predict(context, top_k=3, temperature=0.5)
        
        # High temperature (more diverse)
        preds_high = self.predictor.predict(context, top_k=3, temperature=2.0)
        
        # Both should return predictions
        self.assertGreater(len(preds_low), 0)
        self.assertGreater(len(preds_high), 0)
    
    def test_cache_functionality(self):
        """Test prediction caching"""
        self.predictor.train(self.training_sequences)
        
        context = ['def', 'bar', '(', 'x', ')', ':']
        
        # First call (cache miss)
        _ = self.predictor.predict(context, top_k=3)
        cache_stats1 = self.predictor.get_cache_stats()
        
        # Second call (cache hit)
        _ = self.predictor.predict(context, top_k=3)
        cache_stats2 = self.predictor.get_cache_stats()
        
        # Cache hits should increase
        self.assertGreater(cache_stats2['cache_hits'], cache_stats1['cache_hits'])
    
    def test_empty_context(self):
        """Test prediction with empty context"""
        self.predictor.train(self.training_sequences)
        
        predictions = self.predictor.predict([], top_k=3)
        
        # Should handle gracefully
        self.assertIsInstance(predictions, list)


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main CodeCompletionPredictor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.training_code = [
            """
def add(a, b):
    return a + b
            """,
            """
def multiply(x, y):
    result = x * y
    return result
            """,
            """
def subtract(a, b):
    return a - b
            """,
            """
class Calculator:
    def __init__(self):
        self.result = 0
    
    def compute(self, x):
        self.result += x
        return self.result
            """,
            """
for i in range(10):
    if i % 2 == 0:
        print(i)
            """
        ]
        
        self.model = CodeCompletionPredictor(language='python', max_n=4)
        self.model.train(self.training_code)
    
    def test_initialization(self):
        """Test model initialization"""
        model = CodeCompletionPredictor(language='python')
        self.assertEqual(model.language, 'python')
        self.assertFalse(model.is_trained)
    
    def test_training(self):
        """Test model training"""
        model = CodeCompletionPredictor(language='python')
        model.train(self.training_code)
        self.assertTrue(model.is_trained)
    
    def test_training_empty_samples(self):
        """Test training with empty samples"""
        model = CodeCompletionPredictor(language='python')
        
        with self.assertRaises(ValueError):
            model.train([])
    
    def test_prediction_before_training(self):
        """Test that prediction fails before training"""
        model = CodeCompletionPredictor(language='python')
        
        with self.assertRaises(RuntimeError):
            model.predict_next_line("def foo():")
    
    def test_case_1_predict_next_line(self):
        """
        TEST CASE 1: Predicts next code line
        
        Requirement: Given code context, predict the next line with confidence
        """
        # Test with function definition context
        context = "def divide(a, b):"
        predictions = self.model.predict_next_line(context, top_k=3)
        
        # Validate predictions
        self.assertIsInstance(predictions, list)
        self.assertGreater(len(predictions), 0)
        self.assertLessEqual(len(predictions), 3)
        
        # Check each prediction has correct format
        for token, confidence in predictions:
            self.assertIsInstance(token, str)
            self.assertIsInstance(confidence, float)
            self.assertGreaterEqual(confidence, 0.0, 
                                  f"Confidence {confidence} is below 0.0")
            self.assertLessEqual(confidence, 1.0,
                               f"Confidence {confidence} is above 1.0")
        
        # Confidences should be sorted (highest first)
        confidences = [conf for _, conf in predictions]
        self.assertEqual(confidences, sorted(confidences, reverse=True))
        
        print(f"\n✅ Test Case 1 PASSED: Predicted next line with {len(predictions)} suggestions")
        for i, (pred, conf) in enumerate(predictions, 1):
            print(f"   {i}. {pred} (confidence: {conf:.3f})")
    
    def test_case_2_complete_function(self):
        """
        TEST CASE 2: Completes functions
        
        Requirement: Given partial function, complete it with confidence
        """
        # Test with partial function
        partial = "def square(x):"
        completions = self.model.complete_function(partial, top_k=2)
        
        # Validate completions
        self.assertIsInstance(completions, list)
        self.assertGreater(len(completions), 0)
        self.assertLessEqual(len(completions), 2)
        
        # Check each completion has correct format
        for completion, confidence in completions:
            self.assertIsInstance(completion, str)
            self.assertIsInstance(confidence, float)
            self.assertGreaterEqual(confidence, 0.0,
                                  f"Confidence {confidence} is below 0.0")
            self.assertLessEqual(confidence, 1.0,
                               f"Confidence {confidence} is above 1.0")
            # Completion should not be empty
            self.assertGreater(len(completion.strip()), 0)
        
        print(f"\n✅ Test Case 2 PASSED: Completed function with {len(completions)} variations")
        for i, (comp, conf) in enumerate(completions, 1):
            print(f"   {i}. Confidence: {conf:.3f}")
            print(f"      {partial} {comp}")
    
    def test_multi_language_support_javascript(self):
        """
        REQUIREMENT: Support multiple programming languages
        Test JavaScript support
        """
        js_code = [
            "const add = (a, b) => a + b",
            "function multiply(x, y) { return x * y; }",
            "const subtract = (a, b) => { return a - b; }"
        ]
        
        js_model = CodeCompletionPredictor(language='javascript', max_n=3)
        js_model.train(js_code)
        
        predictions = js_model.predict_next_line("const divide = (a, b) =>", top_k=2)
        
        self.assertIsInstance(predictions, list)
        self.assertGreater(len(predictions), 0)
        
        print(f"\n✅ JavaScript support validated with {len(predictions)} predictions")
    
    def test_multi_language_support_typescript(self):
        """
        REQUIREMENT: Support multiple programming languages
        Test TypeScript support
        """
        ts_code = [
            "interface User { name: string; age: number; }",
            "type ID = string | number;",
            "function greet(user: User): string { return 'Hello'; }"
        ]
        
        ts_model = CodeCompletionPredictor(language='typescript', max_n=3)
        ts_model.train(ts_code)
        
        predictions = ts_model.predict_next_line("interface Product {", top_k=2)
        
        self.assertIsInstance(predictions, list)
        
        print(f"\n✅ TypeScript support validated")
    
    def test_confidence_scores_range(self):
        """
        REQUIREMENT: Provide confidence scores for predictions
        Test that all confidence scores are in valid range [0.0, 1.0]
        """
        contexts = [
            "def test():",
            "class Foo:",
            "if x > 0:",
            "for i in range(10):"
        ]
        
        all_confidences_valid = True
        
        for context in contexts:
            predictions = self.model.predict_next_line(context, top_k=5)
            
            for token, conf in predictions:
                if not (0.0 <= conf <= 1.0):
                    all_confidences_valid = False
                    print(f"❌ Invalid confidence {conf} for token '{token}'")
        
        self.assertTrue(all_confidences_valid)
        print(f"\n✅ All confidence scores in valid range [0.0, 1.0]")
    
    def test_real_time_inference_performance(self):
        """
        REQUIREMENT: Optimize for real-time inference
        Test that predictions are fast enough for real-time use
        """
        context = "def process_data(data):"
        
        # Warm up cache
        _ = self.model.predict_next_line(context, top_k=5)
        
        # Measure cached performance
        start_time = time.time()
        for _ in range(100):
            _ = self.model.predict_next_line(context, top_k=5)
        elapsed = time.time() - start_time
        
        avg_time_ms = (elapsed / 100) * 1000
        
        # Should be under 100ms per prediction (cached)
        self.assertLess(avg_time_ms, 100.0,
                       f"Average prediction time {avg_time_ms:.2f}ms exceeds 100ms")
        
        print(f"\n✅ Real-time performance validated: {avg_time_ms:.2f}ms per prediction")
        
        # Test cold performance
        start_time = time.time()
        _ = self.model.predict_next_line("def new_function():", top_k=5)
        cold_time_ms = (time.time() - start_time) * 1000
        
        print(f"   Cold prediction: {cold_time_ms:.2f}ms")
    
    def test_statistics(self):
        """Test model statistics retrieval"""
        stats = self.model.get_stats()
        
        self.assertIn('language', stats)
        self.assertIn('max_n', stats)
        self.assertIn('is_trained', stats)
        self.assertIn('ngram_counts', stats)
        self.assertIn('cache_stats', stats)
        
        self.assertEqual(stats['language'], 'python')
        self.assertTrue(stats['is_trained'])
    
    def test_edge_case_empty_context(self):
        """Test edge case: empty context"""
        predictions = self.model.predict_next_line("", top_k=3)
        
        # Should handle gracefully
        self.assertIsInstance(predictions, list)
    
    def test_edge_case_very_long_context(self):
        """Test edge case: very long context"""
        long_context = "\n".join(self.training_code)
        
        predictions = self.model.predict_next_line(long_context, top_k=3)
        
        # Should handle without errors
        self.assertIsInstance(predictions, list)


class TestTrainModelFunction(unittest.TestCase):
    """Test the convenience train_model function"""
    
    def test_train_model_function(self):
        """Test the train_model convenience function"""
        training_code = [
            "def add(a, b): return a + b",
            "def sub(a, b): return a - b"
        ]
        
        model = train_model(training_code, language='python', max_n=3)
        
        self.assertIsInstance(model, CodeCompletionPredictor)
        self.assertTrue(model.is_trained)
        self.assertEqual(model.language, 'python')


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_end_to_end_python(self):
        """Test complete workflow for Python"""
        # Train
        code_samples = [
            "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
            "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
        ]
        
        model = train_model(code_samples, language='python')
        
        # Predict next line
        predictions = model.predict_next_line("def power(base, exp):", top_k=3)
        self.assertGreater(len(predictions), 0)
        
        # Complete function
        completions = model.complete_function("def divide(a, b):", top_k=2)
        self.assertGreater(len(completions), 0)
        
        print("\n✅ End-to-end Python workflow validated")
    
    def test_end_to_end_javascript(self):
        """Test complete workflow for JavaScript"""
        code_samples = [
            "const add = (a, b) => a + b;",
            "function multiply(x, y) { return x * y; }",
            "const subtract = (a, b) => { return a - b; }"
        ]
        
        model = train_model(code_samples, language='javascript')
        
        predictions = model.predict_next_line("const divide = (a, b) =>", top_k=2)
        self.assertGreater(len(predictions), 0)
        
        print("\n✅ End-to-end JavaScript workflow validated")


def run_tests():
    """Run all tests with verbose output"""
    print("=" * 80)
    print("Code Completion Predictor - Test Suite")
    print("Challenge ID: challenge-ml_code_predictor-1766499383-908922")
    print("Created by @create-botter")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeTokenizer))
    suite.addTests(loader.loadTestsFromTestCase(TestSequencePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeCompletionPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestTrainModelFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print()
        print("Requirements validated:")
        print("  ✅ Sequence prediction model")
        print("  ✅ Multi-language support (Python, JS, TS, Java, Go)")
        print("  ✅ Confidence scores (0.0-1.0)")
        print("  ✅ Real-time inference (<100ms)")
        print()
        print("Test cases validated:")
        print("  ✅ Test Case 1: Predict next code line")
        print("  ✅ Test Case 2: Complete functions")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
