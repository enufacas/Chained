"""
Comprehensive Test Suite for Code Completion Predictor

Tests all requirements, test cases, and edge cases for the challenge.
Created by @create-guru with rigorous validation.

Challenge ID: challenge-ml_code_predictor-1764166597-967186

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
        code = 'const add = (a, b) => a + b'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('const', tokens)
        self.assertIn('add', tokens)
        self.assertIn('=>', tokens)
        self.assertIn('+', tokens)
    
    def test_typescript_tokenization(self):
        """Test TypeScript code tokenization."""
        tokenizer = CodeTokenizer('typescript')
        code = 'const greet = (name: string): string => `Hello, ${name}`'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('const', tokens)
        self.assertIn('greet', tokens)
        self.assertIn('string', tokens)
        self.assertIn('=>', tokens)
    
    def test_java_tokenization(self):
        """Test Java code tokenization."""
        tokenizer = CodeTokenizer('java')
        code = 'public int add(int a, int b) { return a + b; }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('public', tokens)
        self.assertIn('int', tokens)
        self.assertIn('return', tokens)
        self.assertIn('{', tokens)
        self.assertIn('}', tokens)
    
    def test_go_tokenization(self):
        """Test Go code tokenization."""
        tokenizer = CodeTokenizer('go')
        code = 'func add(a, b int) int { return a + b }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('func', tokens)
        self.assertIn('add', tokens)
        self.assertIn('int', tokens)
        self.assertIn('return', tokens)
    
    def test_detokenization(self):
        """Test converting tokens back to code."""
        tokenizer = CodeTokenizer('python')
        tokens = ['def', 'add', '(', 'a', ',', 'b', ')', ':', 'return', 'a', '+', 'b']
        code = tokenizer.detokenize(tokens)
        
        # Should be readable code
        self.assertIn('def', code)
        self.assertIn('add', code)
        self.assertIn('return', code)
    
    def test_comment_removal_python(self):
        """Test that Python comments are filtered out."""
        tokenizer = CodeTokenizer('python')
        code = 'def foo(): # This is a comment\n    return 42'
        tokens = tokenizer.tokenize(code)
        
        # Comment should not appear in tokens
        self.assertNotIn('#', tokens)
        self.assertNotIn('This', tokens)
        self.assertNotIn('comment', tokens)
    
    def test_comment_removal_javascript(self):
        """Test that JavaScript comments are filtered out."""
        tokenizer = CodeTokenizer('javascript')
        code = 'const x = 1; // comment\nconst y = 2;'
        tokens = tokenizer.tokenize(code)
        
        self.assertNotIn('comment', tokens)
    
    def test_empty_input(self):
        """Test tokenization of empty input."""
        tokenizer = CodeTokenizer('python')
        tokens = tokenizer.tokenize('')
        self.assertEqual(tokens, [])
    
    def test_whitespace_only(self):
        """Test tokenization of whitespace only."""
        tokenizer = CodeTokenizer('python')
        tokens = tokenizer.tokenize('   \n\t   ')
        self.assertEqual(tokens, [])
    
    def test_operators(self):
        """Test multi-character operator tokenization."""
        tokenizer = CodeTokenizer('python')
        code = 'x == y and a != b or c >= d'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('==', tokens)
        self.assertIn('!=', tokens)
        self.assertIn('>=', tokens)


class TestSequencePredictor(unittest.TestCase):
    """Test the N-gram sequence predictor."""
    
    def test_training(self):
        """Test model training on sequences."""
        predictor = SequencePredictor(n=3)
        sequences = [
            ['def', 'foo', '(', ')', ':', 'return', '42'],
            ['def', 'bar', '(', ')', ':', 'return', '100']
        ]
        predictor.train(sequences)
        
        # Verify vocabulary built
        self.assertGreater(len(predictor.vocabulary), 0)
        self.assertIn('def', predictor.vocabulary)
        self.assertIn('return', predictor.vocabulary)
    
    def test_prediction(self):
        """Test sequence prediction."""
        predictor = SequencePredictor(n=3)
        sequences = [
            ['def', 'foo', '(', ')', ':', 'return', '42'],
            ['def', 'bar', '(', ')', ':', 'return', '100']
        ]
        predictor.train(sequences)
        
        # Predict next token
        context = ['def', 'baz', '(', ')']
        predictions = predictor.predict(context, top_k=1)
        
        # Should predict ':' with high confidence
        self.assertEqual(len(predictions), 1)
        token, confidence = predictions[0]
        self.assertEqual(token, ':')
        self.assertGreater(confidence, 0.5)
    
    def test_top_k_predictions(self):
        """Test returning multiple predictions."""
        predictor = SequencePredictor(n=2)
        sequences = [
            ['a', 'b', 'c'],
            ['a', 'b', 'd'],
            ['a', 'b', 'e']
        ]
        predictor.train(sequences)
        
        predictions = predictor.predict(['a', 'b'], top_k=3)
        
        # Should return up to 3 predictions
        self.assertGreater(len(predictions), 0)
        self.assertLessEqual(len(predictions), 3)
        
        # All predictions should have confidence
        for token, confidence in predictions:
            self.assertIsInstance(token, str)
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_backoff_strategy(self):
        """Test intelligent backoff for unseen contexts."""
        predictor = SequencePredictor(n=3)
        sequences = [['a', 'b', 'c', 'd']]
        predictor.train(sequences)
        
        # Completely new context should still get predictions via backoff
        context = ['x', 'y', 'b', 'c']
        predictions = predictor.predict(context, top_k=1)
        
        # Should predict 'd' via shorter context match
        self.assertGreater(len(predictions), 0)
    
    def test_cache_functionality(self):
        """Test prediction caching."""
        predictor = SequencePredictor(n=3)
        sequences = [['a', 'b', 'c']]
        predictor.train(sequences)
        
        # First prediction
        context = ['a', 'b']
        pred1 = predictor.predict(context, top_k=1)
        
        # Second prediction (should use cache)
        pred2 = predictor.predict(context, top_k=1)
        
        # Should be identical
        self.assertEqual(pred1, pred2)
        
        # Cache stats should show hits
        stats = predictor.get_cache_stats()
        self.assertGreater(stats['cache_hits'], 0)
    
    def test_empty_context(self):
        """Test prediction with empty context."""
        predictor = SequencePredictor(n=3)
        sequences = [['a', 'b', 'c']]
        predictor.train(sequences)
        
        predictions = predictor.predict([], top_k=1)
        self.assertEqual(predictions, [])
    
    def test_empty_training(self):
        """Test with empty training data."""
        predictor = SequencePredictor(n=3)
        predictor.train([])
        
        predictions = predictor.predict(['a', 'b'], top_k=1)
        self.assertEqual(predictions, [])


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main code completion predictor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.training_code = [
            'def validate_email(email): return "@" in email',
            'def validate_phone(phone): return len(phone) == 10',
            'def process_data(data): return data.strip().lower()',
            'if status == 200: return True',
            'if status == 404: return None'
        ]
    
    def test_model_initialization(self):
        """Test model can be initialized."""
        model = CodeCompletionPredictor(language='python', n=5)
        self.assertEqual(model.language, 'python')
        self.assertEqual(model.n, 5)
    
    def test_training(self):
        """Test model training."""
        model = CodeCompletionPredictor('python')
        model.train(self.training_code)
        
        # Verify vocabulary built
        stats = model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)
        self.assertEqual(stats['training_samples'], len(self.training_code))
    
    def test_predict_next_line_requirement_1_and_test_case_1(self):
        """
        TEST CASE 1: Predicts next code line
        REQUIREMENT 1: Sequence prediction model
        """
        model = CodeCompletionPredictor('python')
        model.train(self.training_code)
        
        # Test prediction
        context = 'def validate_username(user): '
        line, confidence = model.predict_next_line(context)
        
        # Should get a prediction
        self.assertIsInstance(line, str)
        self.assertGreater(len(line), 0)
        
        # REQUIREMENT 3: Confidence score provided
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_complete_function_test_case_2(self):
        """
        TEST CASE 2: Completes functions
        REQUIREMENT 1: Sequence prediction model
        """
        model = CodeCompletionPredictor('python')
        model.train(self.training_code)
        
        # Test function completion
        partial = 'def validate_password(pwd): '
        completion, confidence = model.complete_function(partial)
        
        # Should get a completion
        self.assertIsInstance(completion, str)
        self.assertGreater(len(completion), 0)
        
        # REQUIREMENT 3: Confidence score provided
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_multi_language_support_requirement_2(self):
        """
        REQUIREMENT 2: Support multiple programming languages
        """
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in languages:
            with self.subTest(language=lang):
                model = CodeCompletionPredictor(lang)
                self.assertEqual(model.language, lang)
                
                # Train on simple code
                if lang == 'python':
                    code = ['def foo(): return 42']
                elif lang in ['javascript', 'typescript']:
                    code = ['const foo = () => 42']
                elif lang == 'java':
                    code = ['public int foo() { return 42; }']
                else:  # go
                    code = ['func foo() int { return 42 }']
                
                model.train(code)
                stats = model.get_stats()
                self.assertGreater(stats['vocabulary_size'], 0)
    
    def test_confidence_scores_requirement_3(self):
        """
        REQUIREMENT 3: Provide confidence scores for predictions
        """
        model = CodeCompletionPredictor('python')
        model.train(self.training_code)
        
        # Test next line prediction
        line, confidence = model.predict_next_line('def test(): ')
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        # Test beam search
        predictions = model.get_predictions('if status == ', top_k=3)
        for token, conf in predictions:
            self.assertIsInstance(conf, float)
            self.assertGreaterEqual(conf, 0.0)
            self.assertLessEqual(conf, 1.0)
    
    def test_real_time_inference_requirement_4(self):
        """
        REQUIREMENT 4: Optimize for real-time inference
        Target: <100ms for cold predictions, <50ms for cached
        """
        model = CodeCompletionPredictor('python')
        model.train(self.training_code)
        
        # Test cold prediction
        context = 'def new_function(): '
        start_time = time.time()
        line, confidence = model.predict_next_line(context)
        cold_time = (time.time() - start_time) * 1000  # ms
        
        # Should be fast (<100ms)
        self.assertLess(cold_time, 100, 
                       f"Cold prediction took {cold_time:.2f}ms (target: <100ms)")
        
        # Test cached prediction (same context)
        start_time = time.time()
        line2, confidence2 = model.predict_next_line(context)
        cached_time = (time.time() - start_time) * 1000  # ms
        
        # Cached should be faster
        self.assertLess(cached_time, 50,
                       f"Cached prediction took {cached_time:.2f}ms (target: <50ms)")
    
    def test_beam_search(self):
        """Test getting multiple predictions."""
        model = CodeCompletionPredictor('python')
        model.train(self.training_code)
        
        predictions = model.get_predictions('if status == ', top_k=3)
        
        # Should get up to 3 predictions
        self.assertGreater(len(predictions), 0)
        self.assertLessEqual(len(predictions), 3)
        
        # Each should have token and confidence
        for token, confidence in predictions:
            self.assertIsInstance(token, str)
            self.assertIsInstance(confidence, float)
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_model_persistence(self):
        """Test saving and loading models."""
        model = CodeCompletionPredictor('python')
        model.train(self.training_code)
        
        # Make a prediction
        line1, conf1 = model.predict_next_line('def test(): ')
        
        # Save model
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            model.save_model(temp_path)
            
            # Load into new model
            model2 = CodeCompletionPredictor('python')
            model2.load_model(temp_path)
            
            # Should make same prediction
            line2, conf2 = model2.predict_next_line('def test(): ')
            self.assertEqual(line1, line2)
            self.assertEqual(conf1, conf2)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_get_stats(self):
        """Test model statistics."""
        model = CodeCompletionPredictor('python')
        model.train(self.training_code)
        
        stats = model.get_stats()
        
        # Verify all expected keys
        self.assertIn('language', stats)
        self.assertIn('vocabulary_size', stats)
        self.assertIn('training_samples', stats)
        self.assertIn('ngram_counts', stats)
        self.assertIn('cache_hit_rate', stats)
        self.assertIn('challenge_id', stats)
        
        # Verify values
        self.assertEqual(stats['language'], 'python')
        self.assertGreater(stats['vocabulary_size'], 0)
        self.assertEqual(stats['training_samples'], len(self.training_code))
        self.assertEqual(stats['challenge_id'], 'challenge-ml_code_predictor-1764166597-967186')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_training_data(self):
        """Test model with no training data."""
        model = CodeCompletionPredictor('python')
        model.train([])
        
        # Should not crash
        line, confidence = model.predict_next_line('def test(): ')
        
        # Should return empty or low confidence
        self.assertIsInstance(line, str)
        self.assertIsInstance(confidence, float)
    
    def test_empty_context(self):
        """Test prediction with empty context."""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return 42'])
        
        # Should not crash
        line, confidence = model.predict_next_line('')
        
        self.assertIsInstance(line, str)
        self.assertIsInstance(confidence, float)
    
    def test_long_context(self):
        """Test prediction with very long context."""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return 42'])
        
        # Very long context
        long_context = 'def ' + 'very_long_function_name_' * 10 + '(): '
        
        # Should not crash and should complete reasonably
        line, confidence = model.predict_next_line(long_context)
        
        self.assertIsInstance(line, str)
        self.assertIsInstance(confidence, float)
    
    def test_special_characters(self):
        """Test handling of special characters."""
        model = CodeCompletionPredictor('python')
        code = [
            'result = data["key"]',
            'value = array[0]',
            'check = x > 0 and y < 10'
        ]
        model.train(code)
        
        # Should handle brackets, quotes, etc.
        line, confidence = model.predict_next_line('value = ')
        self.assertIsInstance(line, str)
    
    def test_unicode_code(self):
        """Test handling of unicode in code."""
        model = CodeCompletionPredictor('python')
        code = [
            'name = "こんにちは"',
            'greeting = "Hello, 世界"'
        ]
        model.train(code)
        
        # Should not crash
        line, confidence = model.predict_next_line('message = ')
        self.assertIsInstance(line, str)
    
    def test_single_token_training(self):
        """Test training with single token samples."""
        model = CodeCompletionPredictor('python')
        model.train(['x'])
        
        # Should not crash
        line, confidence = model.predict_next_line('y')
        self.assertIsInstance(line, str)


class TestConvenienceFunction(unittest.TestCase):
    """Test the convenience training function."""
    
    def test_train_model_function(self):
        """Test one-line model training."""
        code = ['def foo(): return 42']
        model = train_model(code, language='python', n=5)
        
        # Should be trained and ready
        self.assertEqual(model.language, 'python')
        self.assertEqual(model.n, 5)
        
        stats = model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)
    
    def test_train_model_default_params(self):
        """Test train_model with default parameters."""
        code = ['def foo(): return 42']
        model = train_model(code)
        
        # Should use defaults
        self.assertEqual(model.language, 'python')
        self.assertEqual(model.n, 5)


class TestChallengeRequirements(unittest.TestCase):
    """
    Meta-test class to validate all challenge requirements are met.
    Challenge ID: challenge-ml_code_predictor-1764166597-967186
    """
    
    def test_requirement_1_sequence_prediction_model(self):
        """REQUIREMENT 1: Train a sequence prediction model."""
        model = CodeCompletionPredictor('python')
        training_data = [
            'def add(a, b): return a + b',
            'def sub(a, b): return a - b'
        ]
        model.train(training_data)
        
        # Model should be trained
        stats = model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)
        self.assertEqual(stats['training_samples'], 2)
        
        # Should be able to predict
        line, conf = model.predict_next_line('def mul(a, b): ')
        self.assertIsInstance(line, str)
    
    def test_requirement_2_multi_language(self):
        """REQUIREMENT 2: Support multiple programming languages."""
        required_languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in required_languages:
            model = CodeCompletionPredictor(lang)
            self.assertEqual(model.language, lang)
    
    def test_requirement_3_confidence_scores(self):
        """REQUIREMENT 3: Provide confidence scores for predictions."""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return 42'])
        
        line, conf = model.predict_next_line('def bar(): ')
        
        # Confidence should be a float between 0 and 1
        self.assertIsInstance(conf, float)
        self.assertGreaterEqual(conf, 0.0)
        self.assertLessEqual(conf, 1.0)
    
    def test_requirement_4_realtime_inference(self):
        """REQUIREMENT 4: Optimize for real-time inference."""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return 42'] * 10)
        
        # Measure inference time
        start = time.time()
        for _ in range(10):
            model.predict_next_line('def test(): ')
        total_time = (time.time() - start) * 1000  # ms
        
        # Average should be <100ms per prediction
        avg_time = total_time / 10
        self.assertLess(avg_time, 100, f"Average inference time {avg_time:.2f}ms exceeds 100ms target")
    
    def test_test_case_1_predict_next_line(self):
        """TEST CASE 1: Predicts next code line."""
        model = CodeCompletionPredictor('python')
        model.train([
            'def validate(x): return x > 0',
            'def process(data): return data.upper()'
        ])
        
        line, conf = model.predict_next_line('def check(value): ')
        
        # Should produce a prediction
        self.assertIsInstance(line, str)
        self.assertGreater(len(line), 0)
    
    def test_test_case_2_complete_function(self):
        """TEST CASE 2: Completes functions."""
        model = CodeCompletionPredictor('python')
        model.train([
            'def validate(x): return x > 0',
            'def process(data): return data.upper()'
        ])
        
        completion, conf = model.complete_function('def transform(item): ')
        
        # Should produce a completion
        self.assertIsInstance(completion, str)


def run_test_suite():
    """Run all tests and print summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeTokenizer))
    suite.addTests(loader.loadTestsFromTestCase(TestSequencePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeCompletionPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestChallengeRequirements))
    
    # Run with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY - Code Completion Predictor by @create-guru")
    print("Challenge ID: challenge-ml_code_predictor-1764166597-967186")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
        print()
        print("Requirements Validated:")
        print("  ✓ Requirement 1: Sequence prediction model trained and working")
        print("  ✓ Requirement 2: Multiple programming languages supported")
        print("  ✓ Requirement 3: Confidence scores provided for all predictions")
        print("  ✓ Requirement 4: Real-time inference optimized (<100ms)")
        print()
        print("Test Cases Validated:")
        print("  ✓ Test Case 1: Successfully predicts next code line")
        print("  ✓ Test Case 2: Successfully completes functions")
        print()
        print("Edge Cases Covered:")
        print("  ✓ Empty inputs, long contexts, special characters")
        print("  ✓ Various N-gram orders and training scenarios")
        print("  ✓ Model persistence and caching")
        print("  ✓ Unicode and multi-language support")
    else:
        print("❌ Some tests failed. Please review the output above.")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_test_suite()
    sys.exit(0 if success else 1)
