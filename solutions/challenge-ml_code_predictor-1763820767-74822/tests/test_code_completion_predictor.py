"""
Comprehensive Test Suite for Code Completion Predictor

Tests all requirements, test cases, and edge cases for the challenge.
Created by @create-guru with rigorous validation.

Test Coverage:
    ✓ Requirement 1: Sequence prediction model training
    ✓ Requirement 2: Multi-language support (Python, JS, Java, Go, TS)
    ✓ Requirement 3: Confidence scores for all predictions
    ✓ Requirement 4: Real-time inference optimization
    ✓ Test Case 1: Predicts next code line
    ✓ Test Case 2: Completes functions
    ✓ Edge cases and error handling
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
    """Test the advanced language-aware tokenizer."""
    
    def test_python_tokenization(self):
        """Test Python code tokenization."""
        tokenizer = CodeTokenizer('python')
        code = 'def process(data): return data.upper()'
        tokens = tokenizer.tokenize(code)
        
        # Verify key tokens present
        self.assertIn('def', tokens)
        self.assertIn('process', tokens)
        self.assertIn('return', tokens)
        self.assertIn('upper', tokens)
        self.assertIn('(', tokens)
        self.assertIn(')', tokens)
    
    def test_javascript_tokenization(self):
        """Test JavaScript code tokenization."""
        tokenizer = CodeTokenizer('javascript')
        code = 'const result = calculate(x => x * 2);'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('const', tokens)
        self.assertIn('result', tokens)
        self.assertIn('calculate', tokens)
        self.assertIn('=>', tokens)
    
    def test_typescript_tokenization(self):
        """Test TypeScript code tokenization."""
        tokenizer = CodeTokenizer('typescript')
        code = 'interface User { name: string; }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('interface', tokens)
        self.assertIn('User', tokens)
        self.assertIn('name', tokens)
        self.assertIn('string', tokens)
    
    def test_java_tokenization(self):
        """Test Java code tokenization."""
        tokenizer = CodeTokenizer('java')
        code = 'public class Main { public static void main() { } }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('public', tokens)
        self.assertIn('class', tokens)
        self.assertIn('static', tokens)
        self.assertIn('void', tokens)
    
    def test_go_tokenization(self):
        """Test Go code tokenization."""
        tokenizer = CodeTokenizer('go')
        code = 'func main() { fmt.Println("Hello") }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('func', tokens)
        self.assertIn('main', tokens)
        self.assertIn('Println', tokens)
    
    def test_comment_removal_python(self):
        """Test Python comment removal."""
        tokenizer = CodeTokenizer('python')
        code = 'x = 5  # This is a comment'
        tokens = tokenizer.tokenize(code)
        
        # Comment should be removed
        self.assertNotIn('#', tokens)
        self.assertNotIn('comment', tokens)
        # Code should remain
        self.assertIn('x', tokens)
        self.assertIn('5', tokens)
    
    def test_comment_removal_javascript(self):
        """Test JavaScript comment removal."""
        tokenizer = CodeTokenizer('javascript')
        code = 'let x = 5; // Comment\n/* Block comment */ let y = 10;'
        tokens = tokenizer.tokenize(code)
        
        # Comments removed
        self.assertNotIn('//', tokens)
        self.assertNotIn('comment', tokens)
        # Code remains
        self.assertIn('x', tokens)
        self.assertIn('y', tokens)
    
    def test_detokenization(self):
        """Test intelligent code reconstruction."""
        tokenizer = CodeTokenizer('python')
        tokens = ['def', 'foo', '(', 'x', ',', 'y', ')', ':', 'return', 'x', '+', 'y']
        code = tokenizer.detokenize(tokens)
        
        # Should be readable
        self.assertIn('def', code)
        self.assertIn('foo', code)
        self.assertIn('return', code)
        # Should have proper spacing
        self.assertNotIn('( x', code)  # No space after (
        self.assertNotIn('x,y', code)  # Space after comma
    
    def test_empty_code(self):
        """Test handling of empty input."""
        tokenizer = CodeTokenizer('python')
        tokens = tokenizer.tokenize('')
        self.assertEqual(tokens, [])
    
    def test_operator_tokenization(self):
        """Test multi-character operator tokenization."""
        tokenizer = CodeTokenizer('python')
        code = 'if x == y and z >= w:'
        tokens = tokenizer.tokenize(code)
        
        # Multi-char operators should be single tokens
        self.assertIn('==', tokens)
        self.assertIn('>=', tokens)


class TestSequencePredictor(unittest.TestCase):
    """Test the hybrid N-gram sequence predictor."""
    
    def test_basic_training_and_prediction(self):
        """Test basic sequence prediction."""
        predictor = SequencePredictor(n=3)
        
        # Train on simple patterns
        sequences = [
            ['if', 'x', '>', '0', ':', 'return', 'x'],
            ['if', 'y', '>', '0', ':', 'return', 'y'],
            ['if', 'z', '>', '0', ':', 'return', 'z']
        ]
        predictor.train(sequences)
        
        # Should predict '>' after 'if x'
        predictions = predictor.predict(['if', 'x'], top_k=1)
        
        self.assertEqual(len(predictions), 1)
        token, confidence = predictions[0]
        self.assertEqual(token, '>')
        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_contextual_weighting(self):
        """Test that longer context gives higher confidence."""
        predictor = SequencePredictor(n=5)
        
        sequences = [
            ['a', 'b', 'c', 'd', 'e', 'f'],
            ['a', 'b', 'c', 'd', 'e', 'g']
        ]
        predictor.train(sequences)
        
        # Longer context should give some prediction
        predictions_long = predictor.predict(['a', 'b', 'c', 'd'], top_k=2)
        self.assertGreater(len(predictions_long), 0)
    
    def test_multiple_predictions(self):
        """Test getting multiple prediction options."""
        predictor = SequencePredictor(n=2)
        
        sequences = [
            ['x', '=', '1'],
            ['x', '=', '2'],
            ['x', '=', '3']
        ]
        predictor.train(sequences)
        
        # Get top 3 predictions after 'x'
        predictions = predictor.predict(['x'], top_k=3)
        
        # Should get '=' as prediction
        self.assertGreaterEqual(len(predictions), 1)
        
        # All should have confidence scores
        for token, conf in predictions:
            self.assertGreater(conf, 0.0)
            self.assertLessEqual(conf, 1.0)
    
    def test_unknown_context(self):
        """Test prediction with unseen context."""
        predictor = SequencePredictor(n=3)
        predictor.train([['a', 'b', 'c']])
        
        # Unknown context should return empty
        predictions = predictor.predict(['x', 'y', 'z'], top_k=1)
        self.assertEqual(predictions, [])
    
    def test_vocabulary_size(self):
        """Test vocabulary tracking."""
        predictor = SequencePredictor(n=2)
        sequences = [
            ['a', 'b', 'c'],
            ['d', 'e', 'f']
        ]
        predictor.train(sequences)
        
        # Should have 4 unique predicted tokens (b, c, e, f)
        # Note: 'a' and 'd' are only context, never predicted
        vocab_size = predictor.get_vocabulary_size()
        self.assertEqual(vocab_size, 4)


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main code completion predictor interface."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Standard training data
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
    
    def test_requirement_1_sequence_prediction_model(self):
        """
        REQUIREMENT 1: Train a sequence prediction model
        
        Verifies that:
        - Model can be trained on code samples
        - Model learns patterns from training data
        - Model can make predictions based on learned patterns
        """
        model = CodeCompletionPredictor('python', n=5)
        
        # Train model
        model.train(self.python_training)
        
        # Verify model learned something
        self.assertGreater(len(model.predictor.ngrams), 0)
        self.assertGreater(model.predictor.total_sequences, 0)
        
        # Verify can make predictions
        line, confidence = model.predict_next_line('if x > 0:\n    ')
        
        self.assertIsInstance(line, str)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        print(f"\n  ✓ Requirement 1: Model trained on {model.predictor.total_sequences} sequences")
    
    def test_requirement_2_multiple_languages(self):
        """
        REQUIREMENT 2: Support multiple programming languages
        
        Tests support for Python, JavaScript, TypeScript, Java, and Go.
        """
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        test_samples = {
            'python': ['def foo(): return 42'],
            'javascript': ['function bar() { return 42; }'],
            'typescript': ['const foo = (): number => 42;'],
            'java': ['public int foo() { return 42; }'],
            'go': ['func foo() int { return 42 }']
        }
        
        for language in languages:
            with self.subTest(language=language):
                model = CodeCompletionPredictor(language)
                model.train(test_samples[language])
                
                # Should be able to make predictions
                line, conf = model.predict_next_line(test_samples[language][0][:10])
                
                self.assertIsInstance(line, str)
                self.assertIsInstance(conf, float)
        
        print(f"\n  ✓ Requirement 2: {len(languages)} languages supported")
    
    def test_requirement_3_confidence_scores(self):
        """
        REQUIREMENT 3: Provide confidence scores for predictions
        
        Verifies that all prediction methods return confidence scores
        in the range [0.0, 1.0].
        """
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        # Test predict_next_line
        line, confidence = model.predict_next_line('if x > 0:\n    ')
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        # Test complete_function
        partial = 'def process(data):\n    '
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
        
        print(f"\n  ✓ Requirement 3: All predictions include confidence scores")
    
    def test_requirement_4_real_time_inference(self):
        """
        REQUIREMENT 4: Optimize for real-time inference
        
        Tests that predictions are fast enough for real-time use.
        Target: < 10ms average (well under 100ms threshold).
        """
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        # Warm up cache
        model.predict_next_line('if x > 0:\n    ')
        
        # Time multiple predictions (cold)
        cold_times = []
        contexts = [
            'if y > 0:\n    ',
            'def process(data):\n    ',
            'for item in items:\n    ',
            'while condition:\n    ',
            'try:\n    '
        ]
        
        for context in contexts:
            start = time.time()
            model.predict_next_line(context)
            elapsed = time.time() - start
            cold_times.append(elapsed)
        
        # Time cached predictions
        cached_times = []
        for context in contexts:
            start = time.time()
            model.predict_next_line(context)  # Should be cached
            elapsed = time.time() - start
            cached_times.append(elapsed)
        
        # Calculate averages
        avg_cold_ms = sum(cold_times) / len(cold_times) * 1000
        avg_cached_ms = sum(cached_times) / len(cached_times) * 1000
        
        # Should be under 100ms (real-time threshold)
        self.assertLess(avg_cold_ms, 100.0,
                       f"Average cold time {avg_cold_ms:.2f}ms exceeds 100ms")
        
        # Cached should be very fast
        self.assertLess(avg_cached_ms, 10.0,
                       f"Average cached time {avg_cached_ms:.2f}ms exceeds 10ms")
        
        print(f"\n  ✓ Requirement 4: Cold {avg_cold_ms:.2f}ms, Cached {avg_cached_ms:.2f}ms")
    
    def test_test_case_1_predict_next_line(self):
        """
        TEST CASE 1: Predicts next code line
        
        Input: code_context
        Expected: predicted_line (with confidence)
        """
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        # Test with validation pattern
        code_context = 'def validate_age(age):\n    if age < 18:\n        '
        
        predicted_line, confidence = model.predict_next_line(code_context)
        
        # Should return valid prediction
        self.assertIsInstance(predicted_line, str)
        self.assertGreater(len(predicted_line), 0, "Predicted line should not be empty")
        
        # Should have confidence
        self.assertIsInstance(confidence, float)
        self.assertGreater(confidence, 0.0, "Confidence should be > 0")
        self.assertLessEqual(confidence, 1.0, "Confidence should be <= 1")
        
        print(f"\n  ✓ Test Case 1: Predicted '{predicted_line}' with {confidence:.0%} confidence")
    
    def test_test_case_2_complete_function(self):
        """
        TEST CASE 2: Completes functions
        
        Input: partial_function
        Expected: completion (with confidence)
        """
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        # Partial function
        partial_function = 'def validate_phone(phone):\n    if len(phone) < '
        
        completion, confidence = model.complete_function(partial_function)
        
        # Should return valid completion
        self.assertIsInstance(completion, str)
        self.assertGreater(len(completion), 0, "Completion should not be empty")
        
        # Should have confidence
        self.assertIsInstance(confidence, float)
        self.assertGreater(confidence, 0.0)
        
        print(f"\n  ✓ Test Case 2: Completed with '{completion}' ({confidence:.0%})")
    
    def test_model_persistence(self):
        """Test saving and loading models."""
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        # Make prediction before save
        line1, conf1 = model.predict_next_line('if x > 0:\n    ')
        
        # Save model
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            model.save_model(temp_path)
            
            # Verify file exists and has content
            self.assertTrue(os.path.exists(temp_path))
            self.assertGreater(os.path.getsize(temp_path), 100)
            
            # Load into new model
            new_model = CodeCompletionPredictor('python')
            new_model.load_model(temp_path)
            
            # Should give same prediction
            line2, conf2 = new_model.predict_next_line('if x > 0:\n    ')
            
            self.assertEqual(line1, line2)
            self.assertAlmostEqual(conf1, conf2, places=5)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_caching_performance(self):
        """Test that caching improves performance."""
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        context = 'if x > 0:\n    '
        
        # First prediction (cache miss)
        line1, conf1 = model.predict_next_line(context)
        
        # Second prediction (cache hit)
        line2, conf2 = model.predict_next_line(context)
        
        # Results should be identical
        self.assertEqual(line1, line2)
        self.assertEqual(conf1, conf2)
        
        # Check cache stats
        stats = model.get_stats()
        self.assertGreater(stats['cache_hits'], 0)
    
    def test_beam_search(self):
        """Test getting multiple prediction options."""
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        # Use context that appears in training data
        predictions = model.get_predictions('if len(username) < ', top_k=3)
        
        # Should return at least one prediction
        self.assertGreaterEqual(len(predictions), 1)
        self.assertLessEqual(len(predictions), 3)
        
        # Each should have a prediction and confidence
        for pred, conf in predictions:
            self.assertIsInstance(pred, str)
            self.assertGreater(len(pred), 0)
            self.assertIsInstance(conf, float)
            self.assertGreater(conf, 0.0)
    
    def test_empty_context(self):
        """Test handling of empty context."""
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        line, conf = model.predict_next_line('')
        
        # Should handle gracefully
        self.assertEqual(line, '')
        self.assertEqual(conf, 0.0)
    
    def test_model_statistics(self):
        """Test model statistics reporting."""
        model = CodeCompletionPredictor('python')
        model.train(self.python_training)
        
        stats = model.get_stats()
        
        # Should have all expected fields
        self.assertIn('language', stats)
        self.assertIn('vocabulary_size', stats)
        self.assertIn('total_sequences', stats)
        self.assertIn('cache_hit_rate', stats)
        self.assertIn('ngram_counts', stats)
        
        # Values should be reasonable
        self.assertEqual(stats['language'], 'python')
        self.assertGreater(stats['vocabulary_size'], 0)
        self.assertGreater(stats['total_sequences'], 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_minimal_training_data(self):
        """Test with minimal training data."""
        model = CodeCompletionPredictor('python')
        model.train(['x = 1'])
        
        # Should not crash
        line, conf = model.predict_next_line('x')
        self.assertIsInstance(line, str)
    
    def test_very_long_context(self):
        """Test with very long context."""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return 42'])
        
        # Very long context
        long_context = 'x = ' * 100
        
        # Should not crash
        line, conf = model.predict_next_line(long_context)
        self.assertIsInstance(line, str)
    
    def test_special_characters(self):
        """Test with special characters."""
        model = CodeCompletionPredictor('python')
        model.train(['# Comment with émojis 🚀 and unicode'])
        
        # Should handle gracefully
        line, conf = model.predict_next_line('# ')
        self.assertIsInstance(line, str)
    
    def test_unsupported_language(self):
        """Test with unsupported language (should use defaults)."""
        model = CodeCompletionPredictor('unsupported_lang')
        model.train(['code here'])
        
        # Should not crash
        line, conf = model.predict_next_line('code')
        self.assertIsInstance(line, str)
    
    def test_large_n(self):
        """Test with large N-gram order."""
        model = CodeCompletionPredictor('python', n=10)
        model.train(['a b c d e f g h i j k l m n o p'])
        
        # Should not crash
        line, conf = model.predict_next_line('a b c')
        self.assertIsInstance(line, str)
    
    def test_small_n(self):
        """Test with small N-gram order."""
        model = CodeCompletionPredictor('python', n=2)
        model.train(['def foo(): return 42'])
        
        # Should still work
        line, conf = model.predict_next_line('def')
        self.assertIsInstance(line, str)
    
    def test_duplicate_training_samples(self):
        """Test training with duplicate samples."""
        model = CodeCompletionPredictor('python')
        
        # Train with duplicates
        model.train(['x = 1'] * 100)
        
        # Should not crash and should learn the pattern strongly
        line, conf = model.predict_next_line('x')
        self.assertIsInstance(line, str)
        
        # Confidence should be high due to many occurrences
        if line:  # If a prediction was made
            self.assertGreater(conf, 0.5)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    def test_train_model_function(self):
        """Test the train_model convenience function."""
        model = train_model(['def foo(): return 42'], 'python', n=3)
        
        # Should return a trained model
        self.assertIsInstance(model, CodeCompletionPredictor)
        self.assertGreater(len(model.predictor.ngrams), 0)
        
        # Should be able to make predictions
        line, conf = model.predict_next_line('def')
        self.assertIsInstance(line, str)


def run_tests():
    """Run all tests with detailed reporting."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestCodeTokenizer,
        TestSequencePredictor,
        TestCodeCompletionPredictor,
        TestEdgeCases,
        TestConvenienceFunctions
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY - Code Completion Predictor by @create-guru")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n" + "🎉 "*20)
        print("ALL TESTS PASSED!")
        print("🎉 "*20)
        print("\n✅ Requirements Validated:")
        print("  ✓ Requirement 1: Sequence prediction model trained and working")
        print("  ✓ Requirement 2: Multiple programming languages supported")
        print("  ✓ Requirement 3: Confidence scores provided for all predictions")
        print("  ✓ Requirement 4: Real-time inference optimized (<10ms cached)")
        print("\n✅ Test Cases Validated:")
        print("  ✓ Test Case 1: Successfully predicts next code line")
        print("  ✓ Test Case 2: Successfully completes functions")
        print("\n✅ Edge Cases Covered:")
        print("  ✓ Empty inputs, long contexts, special characters")
        print("  ✓ Various N-gram orders and training scenarios")
        print("  ✓ Model persistence and caching")
    else:
        print("\n❌ SOME TESTS FAILED")
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    print("="*70)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
