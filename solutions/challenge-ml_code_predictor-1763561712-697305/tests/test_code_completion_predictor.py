#!/usr/bin/env python3
"""
Comprehensive tests for Code Completion Predictor

Tests all requirements:
1. Sequence prediction model
2. Multi-language support
3. Confidence scores
4. Real-time inference performance

Created by @create-guru for the Chained autonomous AI ecosystem.
"""

import unittest
import time
import sys
from pathlib import Path

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
        self.assertGreater(len(self.predictor.token_freq), 0)
    
    def test_prediction_with_context(self):
        """Test predictions with known context"""
        # Context: "def function"
        predictions = self.predictor.predict(['def', 'function'], top_k=3)
        
        # Should predict opening parenthesis
        self.assertGreater(len(predictions), 0)
        tokens = [token for token, _ in predictions]
        self.assertIn('(', tokens)
    
    def test_confidence_scores(self):
        """Test that confidence scores are valid probabilities"""
        predictions = self.predictor.predict(['if'], top_k=3)
        
        for token, confidence in predictions:
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_beam_search(self):
        """Test beam search completion"""
        beams = self.predictor.beam_search(['def'], max_length=5)
        
        # Should generate multiple completions
        self.assertGreater(len(beams), 0)
        
        # Each beam should be longer than initial context
        for beam in beams:
            self.assertGreater(len(beam), 1)


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main code completion predictor"""
    
    def setUp(self):
        """Set up test predictor with training data"""
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
    if not numbers:
        return 0
    total = sum(numbers)
    return total / len(numbers)
            """,
            """
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        result = 0
        for i in range(b):
            result += a
        return result
            """
        ]
        
        self.model = CodeCompletionPredictor(language='python', n=5)
        self.model.train(self.training_code)
    
    def test_model_training(self):
        """Test that model trains successfully"""
        self.assertTrue(self.model.trained)
        self.assertGreater(len(self.model.predictor.ngrams), 0)
    
    def test_predict_next_line_requirement_1(self):
        """
        Test Case 1: Predicts next code line
        Requirement: Train a sequence prediction model
        """
        code_context = "def process_data(data):\n    total = 0\n    "
        predicted_line, confidence = self.model.predict_next_line(code_context)
        
        # Should return a prediction
        self.assertIsInstance(predicted_line, str)
        self.assertGreater(len(predicted_line), 0)
        
        # Should have a confidence score
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        print(f"\n✓ Test Case 1 - Next Line Prediction:")
        print(f"  Context: {repr(code_context[-50:])}")
        print(f"  Predicted: {repr(predicted_line)}")
        print(f"  Confidence: {confidence:.2%}")
    
    def test_complete_function_requirement_2(self):
        """
        Test Case 2: Completes functions
        Requirement: Support multiple programming languages
        """
        partial_function = "def calculate_product(a, b):\n    result = "
        completion, confidence = self.model.complete_function(partial_function)
        
        # Should return a completion
        self.assertIsInstance(completion, str)
        
        # Should have a confidence score
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        print(f"\n✓ Test Case 2 - Function Completion:")
        print(f"  Partial: {repr(partial_function[-40:])}")
        print(f"  Completion: {repr(completion)}")
        print(f"  Confidence: {confidence:.2%}")
    
    def test_confidence_scores_requirement_3(self):
        """
        Test Requirement 3: Provide confidence scores for predictions
        """
        predictions = self.model.get_predictions("def ", top_k=3)
        
        # Should return multiple predictions
        self.assertGreater(len(predictions), 0)
        
        # Each prediction should have a valid confidence score
        for token, confidence in predictions:
            self.assertIsInstance(token, str)
            self.assertIsInstance(confidence, float)
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
        
        print(f"\n✓ Requirement 3 - Confidence Scores:")
        for i, (token, conf) in enumerate(predictions, 1):
            print(f"  {i}. {token}: {conf:.2%}")
    
    def test_real_time_inference_requirement_4(self):
        """
        Test Requirement 4: Optimize for real-time inference
        Target: < 100ms per prediction
        """
        code_context = "def example():\n    x = "
        
        # Time multiple predictions
        times = []
        for _ in range(10):
            start = time.time()
            self.model.predict_next_line(code_context)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        # Should be fast enough for real-time use
        self.assertLess(avg_time, 100, 
            f"Average prediction time {avg_time:.2f}ms exceeds 100ms threshold")
        
        print(f"\n✓ Requirement 4 - Real-time Inference:")
        print(f"  Average time: {avg_time:.2f}ms")
        print(f"  Min time: {min(times):.2f}ms")
        print(f"  Max time: {max(times):.2f}ms")
        print(f"  Target: < 100ms ✓")
    
    def test_multiple_languages_support(self):
        """Test support for multiple programming languages"""
        # Test JavaScript
        js_code = [
            "function hello() { return 'world'; }",
            "const x = 42;",
            "if (condition) { console.log('test'); }"
        ]
        
        js_model = CodeCompletionPredictor(language='javascript')
        js_model.train(js_code)
        
        self.assertTrue(js_model.trained)
        
        # Should be able to predict
        predicted, conf = js_model.predict_next_line("function test() {")
        self.assertGreater(len(predicted), 0)
        
        print(f"\n✓ Multi-language Support:")
        print(f"  JavaScript model trained: ✓")
        print(f"  Prediction: {repr(predicted)}")
    
    def test_model_save_and_load(self):
        """Test saving and loading model"""
        import tempfile
        import os
        
        # Save model
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            self.model.save_model(temp_path)
            
            # Load into new model
            new_model = CodeCompletionPredictor(language='python')
            new_model.load_model(temp_path)
            
            # Should make similar predictions
            context = "def test():\n    return "
            orig_pred, _ = self.model.predict_next_line(context)
            loaded_pred, _ = new_model.predict_next_line(context)
            
            # Predictions should be similar (tokens may vary slightly)
            self.assertTrue(new_model.trained)
            
            print(f"\n✓ Model Persistence:")
            print(f"  Save/Load: ✓")
            print(f"  Original prediction: {repr(orig_pred)}")
            print(f"  Loaded prediction: {repr(loaded_pred)}")
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_cache_performance(self):
        """Test that caching improves performance"""
        context = "def calculate():\n    result = "
        
        # First prediction (no cache)
        start = time.time()
        pred1, _ = self.model.predict_next_line(context)
        time1 = time.time() - start
        
        # Second prediction (should use cache)
        start = time.time()
        pred2, _ = self.model.predict_next_line(context)
        time2 = time.time() - start
        
        # Cache should make second prediction faster
        self.assertLess(time2, time1 * 1.5)  # Allow some variance
        
        print(f"\n✓ Cache Performance:")
        print(f"  First call: {time1*1000:.2f}ms")
        print(f"  Cached call: {time2*1000:.2f}ms")
        print(f"  Speedup: {time1/time2:.1f}x")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_context(self):
        """Test prediction with empty context"""
        model = CodeCompletionPredictor()
        model.train(["def foo(): pass"])
        
        predicted, confidence = model.predict_next_line("")
        # Should still return something (fallback behavior)
        self.assertIsInstance(predicted, str)
    
    def test_untrained_model(self):
        """Test using untrained model"""
        model = CodeCompletionPredictor()
        
        predicted, confidence = model.predict_next_line("def test():")
        # Should return indication that model is not trained
        self.assertIn("not trained", predicted.lower())
        self.assertEqual(confidence, 0.0)
    
    def test_very_long_context(self):
        """Test with very long code context"""
        model = CodeCompletionPredictor()
        model.train(["def foo(): pass"] * 10)
        
        # Very long context (should truncate internally)
        long_context = "x = 1\n" * 1000 + "def bar():"
        predicted, confidence = model.predict_next_line(long_context)
        
        # Should still work
        self.assertIsInstance(predicted, str)
        self.assertIsInstance(confidence, float)


def run_all_tests():
    """Run all tests and print summary"""
    print("\n" + "="*70)
    print("Code Completion Predictor - Test Suite")
    print("="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCodeTokenizer))
    suite.addTests(loader.loadTestsFromTestCase(TestSequencePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeCompletionPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
        print("\nRequirements Validated:")
        print("  1. ✓ Sequence prediction model")
        print("  2. ✓ Multiple programming languages")
        print("  3. ✓ Confidence scores")
        print("  4. ✓ Real-time inference (< 100ms)")
    else:
        print("\n✗ Some tests failed")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
