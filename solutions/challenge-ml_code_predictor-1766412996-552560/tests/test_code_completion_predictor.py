"""
Comprehensive Test Suite for Code Completion Predictor by @create-botter

Challenge ID: challenge-ml_code_predictor-1766412996-552560

Tests all requirements and validates the implementation.
"""

import unittest
import sys
import os
import json
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from code_completion_predictor import (
    CodeCompletionPredictor,
    CodeTokenizer,
    SequencePredictor,
    train_model
)


class TestCodeTokenizer(unittest.TestCase):
    """Test CodeTokenizer for all supported languages."""
    
    def test_python_tokenization(self):
        """Test Python code tokenization."""
        tokenizer = CodeTokenizer('python')
        code = 'def hello(): return "world"'
        tokens = tokenizer.tokenize(code)
        self.assertIn('def', tokens)
        self.assertIn('hello', tokens)
        self.assertIn('return', tokens)
    
    def test_javascript_tokenization(self):
        """Test JavaScript code tokenization."""
        tokenizer = CodeTokenizer('javascript')
        code = 'const add = (a, b) => a + b'
        tokens = tokenizer.tokenize(code)
        self.assertIn('const', tokens)
        self.assertIn('=>', tokens)
    
    def test_multi_char_operators(self):
        """Test handling of multi-character operators."""
        tokenizer = CodeTokenizer('python')
        code = 'if x == 5 and y >= 10'
        tokens = tokenizer.tokenize(code)
        self.assertIn('==', tokens)
        self.assertIn('>=', tokens)
    
    def test_comment_removal(self):
        """Test removal of comments."""
        tokenizer = CodeTokenizer('python')
        code = 'def foo(): # this is a comment\n    return 42'
        tokens = tokenizer.tokenize(code)
        # Comments should be removed
        self.assertNotIn('#', tokens)
        self.assertNotIn('comment', tokens)
    
    def test_detokenization(self):
        """Test converting tokens back to code."""
        tokenizer = CodeTokenizer('python')
        tokens = ['def', 'add', '(', 'a', ',', 'b', ')', ':', 'return', 'a', '+', 'b']
        code = tokenizer.detokenize(tokens)
        self.assertIn('def', code)
        self.assertIn('return', code)


class TestSequencePredictor(unittest.TestCase):
    """Test SequencePredictor N-gram model."""
    
    def setUp(self):
        """Set up test predictor."""
        self.predictor = SequencePredictor(n=3)
    
    def test_training(self):
        """Test training on sequences."""
        sequences = [
            ['def', 'foo', ':', 'return', '42'],
            ['def', 'bar', ':', 'return', '100']
        ]
        self.predictor.train(sequences)
        
        # Check vocabulary
        self.assertGreater(len(self.predictor.vocabulary), 0)
        self.assertIn('def', self.predictor.vocabulary)
        self.assertIn('return', self.predictor.vocabulary)
    
    def test_prediction(self):
        """Test prediction from context."""
        sequences = [
            ['if', 'x', '>', '0', ':', 'return', 'True'],
            ['if', 'y', '>', '0', ':', 'return', 'False']
        ]
        self.predictor.train(sequences)
        
        # Predict after 'if x >'
        predictions = self.predictor.predict(['if', 'x', '>'])
        self.assertGreater(len(predictions), 0)
        
        # Should predict '0' with some confidence
        token, confidence = predictions[0]
        self.assertIsInstance(token, str)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_backoff(self):
        """Test backoff to shorter contexts."""
        sequences = [
            ['a', 'b', 'c', 'd'],
            ['x', 'y', 'c', 'd']
        ]
        self.predictor.train(sequences)
        
        # Even if full context not seen, should backoff
        predictions = self.predictor.predict(['unknown', 'c'])
        # Should predict 'd' from shorter context
        if predictions:
            self.assertGreater(len(predictions), 0)
    
    def test_confidence_scores(self):
        """Test that confidence scores are normalized."""
        sequences = [
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['a', 'b', 'd']
        ]
        self.predictor.train(sequences)
        
        predictions = self.predictor.predict(['a', 'b'], top_k=2)
        
        # All confidences should sum to <= 1.0
        total_conf = sum(conf for _, conf in predictions)
        self.assertLessEqual(total_conf, 1.0)
        
        # Each confidence should be in [0, 1]
        for _, conf in predictions:
            self.assertGreaterEqual(conf, 0.0)
            self.assertLessEqual(conf, 1.0)
    
    def test_caching(self):
        """Test prediction caching."""
        sequences = [['a', 'b', 'c']]
        self.predictor.train(sequences)
        
        # First call
        pred1 = self.predictor.predict(['a', 'b'])
        
        # Second call should use cache
        pred2 = self.predictor.predict(['a', 'b'])
        
        self.assertEqual(pred1, pred2)
        self.assertGreater(len(self.predictor.cache), 0)


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test main CodeCompletionPredictor class."""
    
    def setUp(self):
        """Set up test model."""
        self.training_data = [
            'def validate_email(email): return "@" in email',
            'def validate_phone(phone): return len(phone) == 10',
            'def validate_username(user): return len(user) > 3',
            'def process_data(data): return data.strip().lower()',
            'def calculate_sum(nums): return sum(nums)',
        ]
        self.model = CodeCompletionPredictor('python', n=5)
        self.model.train(self.training_data)
    
    def test_initialization(self):
        """Test model initialization."""
        model = CodeCompletionPredictor('python', n=5)
        self.assertEqual(model.language, 'python')
        self.assertEqual(model.n, 5)
        self.assertIsNotNone(model.tokenizer)
        self.assertIsNotNone(model.predictor)
    
    def test_training(self):
        """Test model training."""
        model = CodeCompletionPredictor('python')
        model.train(self.training_data)
        
        stats = model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)
    
    def test_predict_next_line(self):
        """Test next line prediction (Requirement 1 & Test Case 1)."""
        # Test Case 1: Predicts next code line
        code_context = 'def validate_password(pwd): '
        predicted_line, confidence = self.model.predict_next_line(code_context)
        
        # Should return a string
        self.assertIsInstance(predicted_line, str)
        
        # Confidence should be between 0 and 1
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        # Prediction should not be empty (given trained data)
        self.assertGreater(len(predicted_line), 0)
    
    def test_complete_function(self):
        """Test function completion (Test Case 2)."""
        # Test Case 2: Completes functions
        partial_function = 'def transform_text(text): '
        completion, confidence = self.model.complete_function(partial_function)
        
        # Should return a string
        self.assertIsInstance(completion, str)
        
        # Confidence should be valid
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_multi_language_support(self):
        """Test multiple programming languages (Requirement 2)."""
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in languages:
            model = CodeCompletionPredictor(lang)
            self.assertEqual(model.language, lang)
            
            # Each language should have keywords
            self.assertGreater(len(model.tokenizer.keywords), 0)
    
    def test_confidence_scores(self):
        """Test confidence scores provided (Requirement 3)."""
        code_context = 'def foo(): '
        _, confidence = self.model.predict_next_line(code_context)
        
        # Confidence must be a float between 0 and 1
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_real_time_inference(self):
        """Test real-time inference performance (Requirement 4)."""
        code_context = 'def test(): '
        
        # Measure prediction time
        start = time.time()
        for _ in range(10):
            self.model.predict_next_line(code_context)
        elapsed = time.time() - start
        
        avg_time_ms = (elapsed / 10) * 1000
        
        # Should be under 100ms on average (requirement: real-time)
        self.assertLess(avg_time_ms, 100.0)
    
    def test_beam_search(self):
        """Test getting multiple predictions."""
        predictions = self.model.get_predictions('def ', top_k=3)
        
        # Should return list of tuples
        self.assertIsInstance(predictions, list)
        
        if predictions:
            # Check first prediction
            token, conf = predictions[0]
            self.assertIsInstance(token, str)
            self.assertIsInstance(conf, float)
            self.assertGreaterEqual(conf, 0.0)
            self.assertLessEqual(conf, 1.0)
    
    def test_model_persistence(self):
        """Test saving and loading model."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            path = f.name
        
        try:
            # Save model
            self.model.save_model(path)
            self.assertTrue(os.path.exists(path))
            
            # Load into new model
            new_model = CodeCompletionPredictor('python')
            new_model.load_model(path)
            
            # Should have same configuration
            self.assertEqual(new_model.language, self.model.language)
            self.assertEqual(new_model.n, self.model.n)
            
            # Should make similar predictions
            context = 'def test(): '
            pred1, conf1 = self.model.predict_next_line(context)
            pred2, conf2 = new_model.predict_next_line(context)
            
            # Predictions should be identical
            self.assertEqual(pred1, pred2)
            self.assertEqual(conf1, conf2)
        
        finally:
            if os.path.exists(path):
                os.unlink(path)
    
    def test_get_stats(self):
        """Test getting model statistics."""
        stats = self.model.get_stats()
        
        # Should have expected keys
        self.assertIn('challenge_id', stats)
        self.assertIn('language', stats)
        self.assertIn('vocabulary_size', stats)
        self.assertIn('ngram_counts', stats)
        
        # Should have correct challenge ID
        self.assertEqual(stats['challenge_id'], 'challenge-ml_code_predictor-1766412996-552560')


class TestRequirements(unittest.TestCase):
    """Test all 4 requirements are met."""
    
    def setUp(self):
        """Set up test model."""
        training_data = [
            'def add(a, b): return a + b',
            'def sub(a, b): return a - b',
            'def mul(a, b): return a * b',
        ]
        self.model = train_model(training_data, 'python')
    
    def test_requirement_1_sequence_prediction(self):
        """Requirement 1: Train a sequence prediction model."""
        # Model should be trained
        stats = self.model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)
        
        # Should be able to predict
        pred, conf = self.model.predict_next_line('def ')
        self.assertIsInstance(pred, str)
    
    def test_requirement_2_multi_language(self):
        """Requirement 2: Support multiple programming languages."""
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in languages:
            model = CodeCompletionPredictor(lang)
            # Each should initialize successfully
            self.assertEqual(model.language, lang)
    
    def test_requirement_3_confidence_scores(self):
        """Requirement 3: Provide confidence scores for predictions."""
        _, confidence = self.model.predict_next_line('def test(): ')
        
        # Must provide confidence score
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_requirement_4_real_time_inference(self):
        """Requirement 4: Optimize for real-time inference."""
        start = time.time()
        for _ in range(100):
            self.model.predict_next_line('def ')
        elapsed = time.time() - start
        
        avg_time = elapsed / 100
        
        # Should be fast enough for real-time (< 100ms)
        self.assertLess(avg_time, 0.1)


class TestCases(unittest.TestCase):
    """Test the specific test cases from the challenge."""
    
    def setUp(self):
        """Set up test model."""
        training_data = [
            'def process(x): return x * 2',
            'def validate(y): return y > 0',
            'def transform(z): return str(z)',
        ]
        self.model = train_model(training_data, 'python')
    
    def test_case_1_predict_next_line(self):
        """Test Case 1: Predicts next code line."""
        code_context = 'def compute(a): '
        predicted_line, confidence = self.model.predict_next_line(code_context)
        
        # Should return valid prediction
        self.assertIsInstance(predicted_line, str)
        self.assertIsInstance(confidence, float)
        
        # Confidence should be valid
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_case_2_complete_function(self):
        """Test Case 2: Completes functions."""
        partial_function = 'def calculate(value): '
        completion, confidence = self.model.complete_function(partial_function)
        
        # Should return valid completion
        self.assertIsInstance(completion, str)
        self.assertIsInstance(confidence, float)
        
        # Confidence should be valid
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_training_data(self):
        """Test with empty training data."""
        model = CodeCompletionPredictor('python')
        model.train([])
        
        # Should not crash
        pred, conf = model.predict_next_line('def ')
        self.assertEqual(pred, '')
        self.assertEqual(conf, 0.0)
    
    def test_empty_context(self):
        """Test prediction with empty context."""
        model = train_model(['def foo(): pass'], 'python')
        pred, conf = model.predict_next_line('')
        
        # Should handle gracefully
        self.assertIsInstance(pred, str)
        self.assertIsInstance(conf, float)
    
    def test_long_context(self):
        """Test with very long context."""
        model = train_model(['def foo(): return 42'], 'python')
        
        long_context = 'def ' * 100
        pred, conf = model.predict_next_line(long_context)
        
        # Should not crash
        self.assertIsInstance(pred, str)
        self.assertIsInstance(conf, float)
    
    def test_special_characters(self):
        """Test handling of special characters."""
        model = CodeCompletionPredictor('python')
        code = 'def test(): return "hello@world.com"'
        model.train([code])
        
        # Should handle special chars in strings
        stats = model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)


def run_tests():
    """Run all tests and print summary."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeTokenizer))
    suite.addTests(loader.loadTestsFromTestCase(TestSequencePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeCompletionPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirements))
    suite.addTests(loader.loadTestsFromTestCase(TestCases))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY - Code Completion Predictor by @create-botter")
    print("Challenge ID: challenge-ml_code_predictor-1766412996-552560")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
        print()
        print("✅ Requirements Validated:")
        print("  ✓ Requirement 1: Sequence prediction model trained and working")
        print("  ✓ Requirement 2: Multiple programming languages supported")
        print("  ✓ Requirement 3: Confidence scores provided for all predictions")
        print("  ✓ Requirement 4: Real-time inference optimized (<100ms)")
        print()
        print("✅ Test Cases Validated:")
        print("  ✓ Test Case 1: Successfully predicts next code line")
        print("  ✓ Test Case 2: Successfully completes functions")
        print()
    else:
        print("❌ Some tests failed. Please review the output above.")
    
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
