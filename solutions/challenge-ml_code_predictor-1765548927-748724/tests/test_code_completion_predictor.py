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
        code = "public class Test { private int x; }"
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('<KEYWORD:public>', tokens)
        self.assertIn('<KEYWORD:class>', tokens)
        self.assertIn('Test', tokens)
    
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
        
        # Simple training data
        self.predictor.train([
            ['a', 'b', 'c', 'd'],
            ['a', 'b', 'c', 'e'],
            ['a', 'b', 'd', 'e']
        ])
    
    def test_basic_prediction(self):
        """Test basic sequence prediction"""
        predictions = self.predictor.predict(['a', 'b'], top_k=2)
        
        # Should predict 'c' or 'd' as next token
        self.assertTrue(len(predictions) > 0)
        predicted_tokens = [token for token, _ in predictions]
        self.assertTrue('c' in predicted_tokens or 'd' in predicted_tokens)
    
    def test_confidence_scores(self):
        """Test that predictions include confidence scores"""
        predictions = self.predictor.predict(['a', 'b'], top_k=1)
        
        self.assertEqual(len(predictions), 1)
        token, prob = predictions[0]
        self.assertTrue(0.0 <= prob <= 1.0)
    
    def test_beam_search(self):
        """Test beam search generates multiple completions"""
        beams = self.predictor.beam_search(['a'], max_tokens=3)
        
        self.assertTrue(len(beams) > 0)
        # Each beam should have tokens and a score
        for tokens, score in beams:
            self.assertTrue(isinstance(tokens, list))
            self.assertTrue(0.0 <= score <= 1.0)


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main code completion predictor"""
    
    def setUp(self):
        """Set up test model"""
        self.training_data = [
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
                    if item > 0:
                        result.append(item)
                return result
            """
        ]
        
        self.model = train_model(self.training_data, language='python')
    
    def test_training(self):
        """Test model can be trained"""
        # Model should have learned patterns
        self.assertTrue(len(self.model.predictor.ngrams) > 0)
    
    def test_predict_next_line(self):
        """Test Case 1: Predicts next code line"""
        context = "def test_function(values):\n    total = 0\n    "
        predicted_line, confidence = self.model.predict_next_line(context)
        
        # Should return a prediction
        self.assertIsInstance(predicted_line, str)
        self.assertTrue(len(predicted_line) > 0)
        
        # Should have confidence score
        self.assertIsInstance(confidence, float)
        self.assertTrue(0.0 <= confidence <= 1.0)
    
    def test_complete_function(self):
        """Test Case 2: Completes functions"""
        partial = "def sum_values(nums):\n    result = "
        completion, confidence = self.model.complete_function(partial)
        
        # Should return a completion
        self.assertIsInstance(completion, str)
        
        # Should have confidence score
        self.assertIsInstance(confidence, float)
        self.assertTrue(0.0 <= confidence <= 1.0)
    
    def test_multiple_predictions(self):
        """Test getting multiple prediction options"""
        predictions = self.model.get_predictions("for ", top_k=3)
        
        # Should return list of predictions
        self.assertTrue(len(predictions) > 0)
        self.assertTrue(len(predictions) <= 3)
        
        # Each prediction should have token and confidence
        for token, confidence in predictions:
            self.assertIsInstance(token, str)
            self.assertIsInstance(confidence, float)
            self.assertTrue(0.0 <= confidence <= 1.0)
    
    def test_caching(self):
        """Test that predictions are cached"""
        context = "def foo():\n    x = "
        
        # First call
        result1 = self.model.predict_next_line(context)
        
        # Second call should be cached
        result2 = self.model.predict_next_line(context)
        
        # Results should be identical
        self.assertEqual(result1, result2)
        
        # Cache should contain the key
        cache_key = f"next_line:{context}"
        self.assertIn(cache_key, self.model.cache)


class TestMultiLanguageSupport(unittest.TestCase):
    """Test multi-language support requirement"""
    
    def test_python_support(self):
        """Test Python language support"""
        code = ["def hello(): return 'world'"]
        model = train_model(code, language='python')
        
        self.assertEqual(model.language, 'python')
    
    def test_javascript_support(self):
        """Test JavaScript language support"""
        code = ["function test() { return 42; }"]
        model = train_model(code, language='javascript')
        
        self.assertEqual(model.language, 'javascript')
        
        # Test prediction with JavaScript
        context = "function foo() { "
        prediction, _ = model.predict_next_line(context)
        self.assertIsInstance(prediction, str)
    
    def test_java_support(self):
        """Test Java language support"""
        code = ["public class Test { public void run() {} }"]
        model = train_model(code, language='java')
        
        self.assertEqual(model.language, 'java')


class TestPerformance(unittest.TestCase):
    """Test real-time inference performance requirement"""
    
    def setUp(self):
        """Set up performance test model"""
        # Larger training set
        self.training_data = [
            """
            def calculate_sum(numbers):
                total = 0
                for num in numbers:
                    total += num
                return total
            """ for _ in range(10)
        ]
        
        self.model = train_model(self.training_data, language='python')
    
    def test_inference_speed(self):
        """Test inference is under 100ms (real-time requirement)"""
        context = "def test():\n    x = "
        
        # Measure prediction time
        start_time = time.time()
        self.model.predict_next_line(context)
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Should be under 100ms
        self.assertLess(elapsed_ms, 100, 
                       f"Inference took {elapsed_ms:.2f}ms, should be < 100ms")
    
    def test_multiple_predictions_speed(self):
        """Test multiple predictions are fast"""
        start_time = time.time()
        self.model.get_predictions("if ", top_k=5)
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Should be very fast
        self.assertLess(elapsed_ms, 50, 
                       f"Multiple predictions took {elapsed_ms:.2f}ms")
    
    def test_cached_speed(self):
        """Test cached predictions are instant"""
        context = "def cached_test():\n    y = "
        
        # First call to populate cache
        self.model.predict_next_line(context)
        
        # Second call should be cached and very fast
        start_time = time.time()
        self.model.predict_next_line(context)
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Cached should be < 1ms
        self.assertLess(elapsed_ms, 1,
                       f"Cached lookup took {elapsed_ms:.2f}ms, should be < 1ms")


class TestModelPersistence(unittest.TestCase):
    """Test model save/load functionality"""
    
    def test_save_and_load(self):
        """Test saving and loading model"""
        # Train a model
        training_data = ["def foo(): return 42"]
        model = train_model(training_data, language='python')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            model_path = f.name
        
        try:
            # Save model
            model.save_model(model_path)
            
            # Create new model and load
            new_model = CodeCompletionPredictor(language='python')
            new_model.load_model(model_path)
            
            # Should have same language and patterns
            self.assertEqual(new_model.language, 'python')
            self.assertTrue(len(new_model.predictor.ngrams) > 0)
            
        finally:
            # Clean up
            if os.path.exists(model_path):
                os.remove(model_path)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_context(self):
        """Test prediction with empty context"""
        model = train_model(["def foo(): pass"], language='python')
        
        # Should handle empty context gracefully
        prediction, confidence = model.predict_next_line("")
        self.assertIsInstance(prediction, str)
        self.assertIsInstance(confidence, float)
    
    def test_unknown_context(self):
        """Test prediction with unknown context"""
        model = train_model(["def foo(): pass"], language='python')
        
        # Context not in training data
        prediction, confidence = model.predict_next_line("xyz abc def unknown")
        
        # Should still return something (even if low confidence)
        self.assertIsInstance(prediction, str)
        self.assertTrue(0.0 <= confidence <= 1.0)
    
    def test_short_training_data(self):
        """Test with minimal training data"""
        model = train_model(["x"], language='python')
        
        # Should not crash
        prediction, _ = model.predict_next_line("x")
        self.assertIsInstance(prediction, str)


def run_validation_summary():
    """Print validation summary for requirements"""
    print("\n" + "="*60)
    print("REQUIREMENTS VALIDATION SUMMARY")
    print("="*60)
    
    print("\n✅ Requirement 1: Train a Sequence Prediction Model")
    print("   Implemented: N-gram based sequence prediction")
    print("   Features: Context-aware, pattern learning")
    
    print("\n✅ Requirement 2: Support Multiple Programming Languages")
    print("   Implemented: Python, JavaScript, Java support")
    print("   Features: Language-specific tokenization")
    
    print("\n✅ Requirement 3: Provide Confidence Scores")
    print("   Implemented: Probabilistic confidence scoring")
    print("   Features: Normalized scores [0, 1]")
    
    print("\n✅ Requirement 4: Optimize for Real-Time Inference")
    print("   Implemented: < 100ms inference time")
    print("   Features: Result caching, efficient lookups")
    
    print("\n" + "="*60)
    print("ALL REQUIREMENTS VALIDATED ✓")
    print("="*60 + "\n")


if __name__ == '__main__':
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print validation summary
    if result.wasSuccessful():
        run_validation_summary()
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
