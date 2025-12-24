"""
Test Suite for Code Completion Predictor

Comprehensive tests for the Code Completion Predictor by @create-botter.
Tests all requirements, test cases, and edge cases.

Challenge ID: challenge-ml_code_predictor-1766585721-41

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
    
    def test_javascript_tokenization(self):
        """Test JavaScript code tokenization"""
        tokenizer = CodeTokenizer('javascript')
        code = 'function add(a, b) { return a + b; }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('function', tokens)
        self.assertIn('add', tokens)
        self.assertIn('return', tokens)
    
    def test_multi_char_operators(self):
        """Test multi-character operator handling"""
        tokenizer = CodeTokenizer('python')
        code = 'if x == 5 && y != 3'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('==', tokens)
        self.assertIn('&&', tokens)
        self.assertIn('!=', tokens)
    
    def test_keyword_detection(self):
        """Test keyword identification"""
        tokenizer = CodeTokenizer('python')
        
        self.assertTrue(tokenizer.is_keyword('def'))
        self.assertTrue(tokenizer.is_keyword('class'))
        self.assertFalse(tokenizer.is_keyword('myvar'))
    
    def test_token_type_classification(self):
        """Test token type classification"""
        tokenizer = CodeTokenizer('python')
        
        self.assertEqual(tokenizer.get_token_type('def'), 'keyword')
        self.assertEqual(tokenizer.get_token_type('123'), 'number')
        self.assertEqual(tokenizer.get_token_type('"hello"'), 'string')
        self.assertEqual(tokenizer.get_token_type('myvar'), 'identifier')
        self.assertEqual(tokenizer.get_token_type('+'), 'operator')
    
    def test_empty_code(self):
        """Test handling of empty code"""
        tokenizer = CodeTokenizer('python')
        tokens = tokenizer.tokenize('')
        self.assertEqual(tokens, [])
    
    def test_language_support(self):
        """Test multiple language support"""
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in languages:
            tokenizer = CodeTokenizer(lang)
            self.assertIsNotNone(tokenizer.keywords)


class TestSequencePredictor(unittest.TestCase):
    """Test the SequencePredictor class"""
    
    def test_training(self):
        """Test basic training"""
        predictor = SequencePredictor(n=2)
        sequences = [
            ['a', 'b', 'c'],
            ['a', 'b', 'd'],
            ['a', 'b', 'c']
        ]
        
        predictor.train(sequences)
        
        self.assertGreater(len(predictor.vocab), 0)
        self.assertGreater(predictor.total_sequences, 0)
    
    def test_prediction(self):
        """Test prediction from trained model"""
        predictor = SequencePredictor(n=2)
        sequences = [
            ['def', 'add', 'return'],
            ['def', 'sub', 'return'],
            ['def', 'add', 'return']
        ]
        
        predictor.train(sequences)
        predictions = predictor.predict(['def'], top_k=2)
        
        self.assertGreater(len(predictions), 0)
        self.assertIsInstance(predictions[0], tuple)
        self.assertEqual(len(predictions[0]), 2)  # (token, confidence)
    
    def test_confidence_scores(self):
        """Test that confidence scores are between 0 and 1"""
        predictor = SequencePredictor(n=2)
        sequences = [
            ['a', 'b', 'c'],
            ['a', 'b', 'c'],
            ['a', 'b', 'd']
        ]
        
        predictor.train(sequences)
        predictions = predictor.predict(['a'], top_k=2)
        
        for token, confidence in predictions:
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_empty_context(self):
        """Test prediction with empty context"""
        predictor = SequencePredictor(n=2)
        predictions = predictor.predict([])
        
        self.assertEqual(predictions, [])
    
    def test_fallback_to_shorter_context(self):
        """Test fallback when exact context not found"""
        predictor = SequencePredictor(n=3)
        sequences = [
            ['a', 'b', 'c', 'd']
        ]
        
        predictor.train(sequences)
        
        # Query with unknown full context
        predictions = predictor.predict(['x', 'b', 'c'], top_k=1)
        
        # Should fallback to shorter context
        self.assertIsInstance(predictions, list)
    
    def test_stats(self):
        """Test model statistics"""
        predictor = SequencePredictor(n=2)
        sequences = [['a', 'b', 'c']]
        
        predictor.train(sequences)
        stats = predictor.get_stats()
        
        self.assertIn('vocab_size', stats)
        self.assertIn('total_sequences', stats)
        self.assertGreater(stats['vocab_size'], 0)


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main CodeCompletionPredictor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.training_code = [
            'def add(a, b): return a + b',
            'def subtract(a, b): return a - b',
            'def multiply(a, b): return a * b',
            'class Calculator: def __init__(self): pass',
            'for i in range(10): print(i)',
        ]
    
    def test_initialization(self):
        """Test model initialization"""
        model = CodeCompletionPredictor(language='python')
        
        self.assertEqual(model.language, 'python')
        self.assertFalse(model.trained)
    
    def test_training(self):
        """Test model training"""
        model = CodeCompletionPredictor(language='python')
        model.train(self.training_code)
        
        self.assertTrue(model.trained)
    
    def test_predict_next_line(self):
        """Test Case 1: Predict next code line from context"""
        model = CodeCompletionPredictor(language='python')
        model.train(self.training_code)
        
        context = 'def add(a, b):'
        predictions = model.predict_next_line(context, top_k=3)
        
        self.assertIsInstance(predictions, list)
        self.assertGreater(len(predictions), 0)
        
        # Verify structure
        for pred in predictions:
            self.assertIsInstance(pred, tuple)
            self.assertEqual(len(pred), 2)
            token, confidence = pred
            self.assertIsInstance(token, str)
            self.assertIsInstance(confidence, float)
    
    def test_complete_function(self):
        """Test Case 2: Complete partial function"""
        model = CodeCompletionPredictor(language='python')
        model.train(self.training_code)
        
        partial = 'def multiply(a, b):'
        completed, confidence = model.complete_function(partial, max_tokens=10)
        
        self.assertIsInstance(completed, str)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        # Completed should contain partial
        self.assertIn('multiply', completed)
    
    def test_confidence_scores_requirement(self):
        """Requirement 3: Test confidence scores are provided"""
        model = CodeCompletionPredictor(language='python')
        model.train(self.training_code)
        
        predictions = model.predict_next_line('def add', top_k=2)
        
        for token, confidence in predictions:
            # Confidence should be between 0 and 1
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_multi_language_support(self):
        """Requirement 2: Test multi-language support"""
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in languages:
            model = CodeCompletionPredictor(language=lang)
            self.assertEqual(model.language, lang)
    
    def test_real_time_inference(self):
        """Requirement 4: Test real-time inference (<100ms)"""
        model = CodeCompletionPredictor(language='python')
        model.train(self.training_code * 10)  # More training data
        
        # Measure inference time
        context = 'def add(a, b):'
        start_time = time.time()
        predictions = model.predict_next_line(context, top_k=3)
        end_time = time.time()
        
        inference_time_ms = (end_time - start_time) * 1000
        
        # Should be faster than 100ms
        self.assertLess(inference_time_ms, 100.0)
        print(f"\nInference time: {inference_time_ms:.2f}ms")
    
    def test_untrained_model_error(self):
        """Test that untrained model raises error"""
        model = CodeCompletionPredictor(language='python')
        
        with self.assertRaises(ValueError):
            model.predict_next_line('def test')
    
    def test_get_model_stats(self):
        """Test model statistics retrieval"""
        model = CodeCompletionPredictor(language='python')
        model.train(self.training_code)
        
        stats = model.get_model_stats()
        
        self.assertIn('language', stats)
        self.assertIn('trained', stats)
        self.assertIn('vocab_size', stats)
        self.assertTrue(stats['trained'])
    
    def test_save_and_load_model(self):
        """Test model persistence"""
        import tempfile
        
        model = CodeCompletionPredictor(language='python')
        model.train(self.training_code)
        
        # Save model
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            model.save_model(filepath)
            
            # Load model
            new_model = CodeCompletionPredictor()
            new_model.load_model(filepath)
            
            self.assertTrue(new_model.trained)
            self.assertEqual(new_model.language, 'python')
        finally:
            os.unlink(filepath)


class TestTrainModelFunction(unittest.TestCase):
    """Test the convenience train_model function"""
    
    def test_train_model_function(self):
        """Test train_model convenience function"""
        code_samples = [
            'def test(): pass',
            'class Example: pass'
        ]
        
        model = train_model(code_samples, language='python')
        
        self.assertTrue(model.trained)
        self.assertEqual(model.language, 'python')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_training_data(self):
        """Test training with empty data"""
        model = CodeCompletionPredictor(language='python')
        model.train([])
        
        self.assertTrue(model.trained)
    
    def test_single_token_context(self):
        """Test prediction with single token"""
        model = CodeCompletionPredictor(language='python')
        model.train(['def add: pass'])
        
        predictions = model.predict_next_line('def')
        self.assertIsInstance(predictions, list)
    
    def test_long_code_samples(self):
        """Test with longer code samples"""
        long_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

class MathUtils:
    @staticmethod
    def factorial(n):
        if n == 0:
            return 1
        return n * MathUtils.factorial(n-1)
'''
        
        model = CodeCompletionPredictor(language='python')
        model.train([long_code])
        
        predictions = model.predict_next_line('def fibonacci')
        self.assertIsInstance(predictions, list)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        code_with_special_chars = 'x = [1, 2, 3]; y = {"a": 1}'
        
        model = CodeCompletionPredictor(language='python')
        model.train([code_with_special_chars])
        
        predictions = model.predict_next_line('x =')
        self.assertIsInstance(predictions, list)


def run_tests():
    """Run all tests and print results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeTokenizer))
    suite.addTests(loader.loadTestsFromTestCase(TestSequencePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeCompletionPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestTrainModelFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
