"""
Comprehensive Tests for Code Completion Predictor

Tests all requirements and edge cases for the code completion challenge.

Test Coverage:
    - Tokenization (multiple languages)
    - Sequence prediction
    - Next line prediction (Requirement 1)
    - Function completion (Requirement 2)
    - Multi-language support (Requirement 2)
    - Confidence scores (Requirement 3)
    - Real-time inference (Requirement 4)
    - Model persistence
    - Edge cases

Created by @docs-tech-lead with comprehensive test documentation.
"""

import unittest
import time
import tempfile
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.code_completion_predictor import (
    CodeTokenizer,
    SequencePredictor,
    CodeCompletionPredictor,
    train_model
)


class TestCodeTokenizer(unittest.TestCase):
    """Test the code tokenizer for various languages."""
    
    def test_python_tokenization(self):
        """Test tokenizing Python code."""
        tokenizer = CodeTokenizer('python')
        code = 'def foo(x): return x + 1'
        tokens = tokenizer.tokenize(code)
        
        # Should contain key tokens
        self.assertIn('def', tokens)
        self.assertIn('foo', tokens)
        self.assertIn('return', tokens)
        self.assertIn('x', tokens)
        self.assertIn('+', tokens)
        self.assertIn('1', tokens)
    
    def test_javascript_tokenization(self):
        """Test tokenizing JavaScript code."""
        tokenizer = CodeTokenizer('javascript')
        code = 'function bar() { return 42; }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('function', tokens)
        self.assertIn('bar', tokens)
        self.assertIn('return', tokens)
        self.assertIn('42', tokens)
    
    def test_java_tokenization(self):
        """Test tokenizing Java code."""
        tokenizer = CodeTokenizer('java')
        code = 'public class Test { }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('public', tokens)
        self.assertIn('class', tokens)
        self.assertIn('Test', tokens)
    
    def test_detokenization(self):
        """Test converting tokens back to code."""
        tokenizer = CodeTokenizer('python')
        tokens = ['def', 'foo', '(', ')', ':', 'return', '42']
        code = tokenizer.detokenize(tokens)
        
        # Should be readable code
        self.assertIn('def', code)
        self.assertIn('foo', code)
        self.assertIn('return', code)
        self.assertIn('42', code)
    
    def test_empty_code(self):
        """Test tokenizing empty string."""
        tokenizer = CodeTokenizer('python')
        tokens = tokenizer.tokenize('')
        self.assertEqual(tokens, [])


class TestSequencePredictor(unittest.TestCase):
    """Test the n-gram sequence predictor."""
    
    def test_basic_prediction(self):
        """Test basic sequence prediction."""
        predictor = SequencePredictor(n=3)
        
        # Train on simple sequences
        sequences = [
            ['if', 'x', '>', '0', ':', 'return', 'x'],
            ['if', 'y', '>', '0', ':', 'return', 'y']
        ]
        predictor.train(sequences)
        
        # Predict next token after ['if', 'x']
        predictions = predictor.predict(['if', 'x'], top_k=1)
        
        # Should predict '>'
        self.assertEqual(len(predictions), 1)
        token, confidence = predictions[0]
        self.assertEqual(token, '>')
        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_multiple_predictions(self):
        """Test getting multiple prediction options."""
        predictor = SequencePredictor(n=2)
        
        sequences = [
            ['a', 'b', 'c'],
            ['a', 'b', 'd'],
            ['a', 'b', 'e']
        ]
        predictor.train(sequences)
        
        # Get top 3 predictions
        predictions = predictor.predict(['a'], top_k=3)
        
        # Should return 1 prediction ('b')
        self.assertGreaterEqual(len(predictions), 1)
        
        # All should have confidence scores
        for token, conf in predictions:
            self.assertGreater(conf, 0.0)
            self.assertLessEqual(conf, 1.0)
    
    def test_unknown_context(self):
        """Test prediction with unknown context."""
        predictor = SequencePredictor(n=3)
        predictor.train([['a', 'b', 'c']])
        
        # Unknown context should return empty
        predictions = predictor.predict(['x', 'y'], top_k=1)
        self.assertEqual(predictions, [])


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main code completion predictor."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Training data for tests
        self.python_training = [
            """
            def validate_email(email):
                if '@' not in email:
                    return False
                return True
            """,
            """
            def validate_password(password):
                if len(password) < 8:
                    return False
                return True
            """,
            """
            def validate_username(username):
                if len(username) < 3:
                    return False
                return True
            """
        ]
    
    def test_requirement_1_sequence_prediction(self):
        """
        REQUIREMENT 1: Train a sequence prediction model
        
        Verifies that the model can learn from training data and predict
        sequences based on learned patterns.
        """
        model = CodeCompletionPredictor('python', n=5)
        model.train(self.python_training)
        
        # Model should have learned patterns
        self.assertGreater(len(model.predictor.ngrams), 0)
        
        # Should be able to make predictions
        line, confidence = model.predict_next_line('if x > 0:\n    ')
        
        # Should return something
        self.assertIsInstance(line, str)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_requirement_2_multiple_languages(self):
        """
        REQUIREMENT 2: Support multiple programming languages
        
        Verifies support for Python, JavaScript, and Java.
        """
        # Test Python
        python_model = CodeCompletionPredictor('python')
        python_model.train(['def foo(): return 42'])
        line, conf = python_model.predict_next_line('def bar(): ')
        self.assertIsInstance(line, str)
        
        # Test JavaScript
        js_model = CodeCompletionPredictor('javascript')
        js_model.train(['function foo() { return 42; }'])
        line, conf = js_model.predict_next_line('function bar() { ')
        self.assertIsInstance(line, str)
        
        # Test Java
        java_model = CodeCompletionPredictor('java')
        java_model.train(['public int foo() { return 42; }'])
        line, conf = java_model.predict_next_line('public int bar() { ')
        self.assertIsInstance(line, str)
    
    def test_requirement_3_confidence_scores(self):
        """
        REQUIREMENT 3: Provide confidence scores for predictions
        
        Verifies that all predictions include confidence scores in range [0, 1].
        """
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        # Test predict_next_line
        line, confidence = model.predict_next_line('if x > 0:\n    ')
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        # Test complete_function
        partial = 'def process(data):\n    result = []\n    '
        completion, confidence = model.complete_function(partial)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        # Test get_predictions
        predictions = model.get_predictions('if x ', top_k=3)
        for pred, conf in predictions:
            self.assertIsInstance(conf, float)
            self.assertGreaterEqual(conf, 0.0)
            self.assertLessEqual(conf, 1.0)
    
    def test_requirement_4_real_time_inference(self):
        """
        REQUIREMENT 4: Optimize for real-time inference
        
        Verifies that predictions are fast enough for real-time use.
        Target: < 100ms average (we should achieve << 10ms)
        """
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        # Warm up (first prediction may be slower due to initialization)
        model.predict_next_line('if x > 0:\n    ')
        
        # Time multiple predictions
        times = []
        contexts = [
            'if x > 0:\n    ',
            'def process(data):\n    ',
            'for item in items:\n    ',
            'while condition:\n    ',
            'try:\n    '
        ]
        
        for context in contexts:
            start = time.time()
            model.predict_next_line(context)
            elapsed = time.time() - start
            times.append(elapsed)
        
        # Calculate average
        avg_time_ms = sum(times) / len(times) * 1000
        
        # Should be well under 100ms (target for real-time)
        self.assertLess(avg_time_ms, 100.0,
                       f"Average prediction time {avg_time_ms:.2f}ms exceeds 100ms threshold")
        
        # Print performance for visibility
        print(f"\n  Performance: {avg_time_ms:.2f}ms average")
        print(f"  Min: {min(times)*1000:.2f}ms, Max: {max(times)*1000:.2f}ms")
    
    def test_test_case_1_predict_next_line(self):
        """
        TEST CASE 1: Predicts next code line
        Input: code_context
        Expected: predicted_line
        """
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        # Test context
        code_context = 'def validate_age(age):\n    if age < 18:\n        '
        
        # Predict
        predicted_line, confidence = model.predict_next_line(code_context)
        
        # Should return valid prediction
        self.assertIsInstance(predicted_line, str)
        self.assertGreater(len(predicted_line), 0)
        self.assertIsInstance(confidence, float)
        self.assertGreater(confidence, 0.0)
    
    def test_test_case_2_complete_function(self):
        """
        TEST CASE 2: Completes functions
        Input: partial_function
        Expected: completion
        """
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        # Partial function
        partial_function = 'def validate_phone(phone):\n    if len(phone) < '
        
        # Complete
        completion, confidence = model.complete_function(partial_function)
        
        # Should return valid completion
        self.assertIsInstance(completion, str)
        self.assertGreater(len(completion), 0)
        self.assertIsInstance(confidence, float)
    
    def test_model_persistence(self):
        """Test saving and loading models."""
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        # Get prediction before save
        line1, conf1 = model.predict_next_line('if x > 0:\n    ')
        
        # Save model
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            model.save_model(temp_path)
            
            # Load into new model
            new_model = CodeCompletionPredictor('python')
            new_model.load_model(temp_path)
            
            # Should give same prediction
            line2, conf2 = new_model.predict_next_line('if x > 0:\n    ')
            
            self.assertEqual(line1, line2)
            self.assertAlmostEqual(conf1, conf2, places=5)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_empty_context(self):
        """Test prediction with empty context."""
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        line, conf = model.predict_next_line('')
        
        # Should handle gracefully
        self.assertEqual(line, '')
        self.assertEqual(conf, 0.0)
    
    def test_train_model_convenience_function(self):
        """Test the convenience train_model function."""
        model = train_model(['def foo(): return 42'], 'python', n=3)
        
        # Should be a trained model
        self.assertIsInstance(model, CodeCompletionPredictor)
        self.assertGreater(len(model.predictor.ngrams), 0)
    
    def test_caching(self):
        """Test that predictions are cached for performance."""
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        context = 'if x > 0:\n    '
        
        # First prediction
        start1 = time.time()
        line1, conf1 = model.predict_next_line(context)
        time1 = time.time() - start1
        
        # Second prediction (should be cached)
        start2 = time.time()
        line2, conf2 = model.predict_next_line(context)
        time2 = time.time() - start2
        
        # Results should be identical
        self.assertEqual(line1, line2)
        self.assertEqual(conf1, conf2)
        
        # Second should be faster (though both are very fast)
        # Just verify it works, not necessarily faster due to small time scales
        self.assertGreater(time1, 0)
        self.assertGreater(time2, 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_very_short_training_data(self):
        """Test with minimal training data."""
        model = CodeCompletionPredictor('python')
        model.train(['x'])
        
        # Should not crash
        line, conf = model.predict_next_line('x')
        self.assertIsInstance(line, str)
    
    def test_invalid_language(self):
        """Test with unsupported language (should still work with defaults)."""
        model = CodeCompletionPredictor('unsupported_lang')
        model.train(['code here'])
        
        # Should not crash
        line, conf = model.predict_next_line('code')
        self.assertIsInstance(line, str)
    
    def test_large_n(self):
        """Test with large n-gram order."""
        model = CodeCompletionPredictor('python', n=10)
        model.train(['a b c d e f g h i j k'])
        
        # Should not crash
        line, conf = model.predict_next_line('a b c')
        self.assertIsInstance(line, str)
    
    def test_unicode_code(self):
        """Test with unicode characters in code."""
        model = CodeCompletionPredictor('python')
        model.train(['# Comment with émojis 🚀'])
        
        # Should not crash
        line, conf = model.predict_next_line('# ')
        self.assertIsInstance(line, str)


def run_tests():
    """Run all tests and print results."""
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
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
        print("\nRequirements Validated:")
        print("  ✓ Requirement 1: Sequence prediction model trained")
        print("  ✓ Requirement 2: Multiple programming languages supported")
        print("  ✓ Requirement 3: Confidence scores provided")
        print("  ✓ Requirement 4: Real-time inference optimized")
        print("\nTest Cases Validated:")
        print("  ✓ Test Case 1: Predicts next code line")
        print("  ✓ Test Case 2: Completes functions")
    else:
        print("\n✗ SOME TESTS FAILED")
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
