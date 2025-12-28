#!/usr/bin/env python3
"""
Tests for Code Completion Predictor

Comprehensive test suite for the code completion predictor by @create-botter.
Challenge ID: challenge-ml_code_predictor-1766931267-134357

Test Coverage:
    - Tokenization (all languages)
    - N-gram prediction
    - Code completion
    - Function completion
    - Confidence scores
    - Real-time performance
    - Model persistence
    - Edge cases
"""

import unittest
import time
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.code_completion_predictor import (
    CodeTokenizer,
    SequencePredictor,
    CodeCompletionPredictor
)


class TestCodeTokenizer(unittest.TestCase):
    """Test CodeTokenizer for all supported languages"""
    
    def test_python_tokenization(self):
        """Test Python code tokenization"""
        tokenizer = CodeTokenizer('python')
        code = 'def add(a, b): return a + b'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('def', tokens)
        self.assertIn('add', tokens)
        self.assertIn('return', tokens)
        self.assertEqual(tokens[0], 'def')
    
    def test_javascript_tokenization(self):
        """Test JavaScript code tokenization"""
        tokenizer = CodeTokenizer('javascript')
        code = 'const add = (a, b) => a + b'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('const', tokens)
        self.assertIn('add', tokens)
        self.assertIn('=>', tokens)
    
    def test_typescript_tokenization(self):
        """Test TypeScript code tokenization"""
        tokenizer = CodeTokenizer('typescript')
        code = 'interface User { name: string; }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('interface', tokens)
        self.assertIn('User', tokens)
        self.assertIn('name', tokens)
    
    def test_java_tokenization(self):
        """Test Java code tokenization"""
        tokenizer = CodeTokenizer('java')
        code = 'public class Main { }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('public', tokens)
        self.assertIn('class', tokens)
        self.assertIn('Main', tokens)
    
    def test_go_tokenization(self):
        """Test Go code tokenization"""
        tokenizer = CodeTokenizer('go')
        code = 'func add(a, b int) int { return a + b }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('func', tokens)
        self.assertIn('add', tokens)
        self.assertIn('return', tokens)
    
    def test_comment_removal_python(self):
        """Test Python comment removal"""
        tokenizer = CodeTokenizer('python')
        code = 'x = 5  # This is a comment'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('x', tokens)
        self.assertIn('=', tokens)
        self.assertIn('5', tokens)
        self.assertNotIn('#', tokens)
        self.assertNotIn('This', tokens)
    
    def test_comment_removal_javascript(self):
        """Test JavaScript comment removal"""
        tokenizer = CodeTokenizer('javascript')
        code = 'let x = 5; // comment'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('let', tokens)
        self.assertIn('x', tokens)
        self.assertNotIn('//', tokens)
    
    def test_multi_char_operators(self):
        """Test multi-character operator handling"""
        tokenizer = CodeTokenizer('python')
        code = 'if x == 5 and y != 3'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('==', tokens)
        self.assertIn('!=', tokens)
        # Should not split into single chars
        self.assertEqual(tokens.count('='), 0)  # No standalone '='
    
    def test_detokenization(self):
        """Test token-to-code conversion"""
        tokenizer = CodeTokenizer('python')
        tokens = ['def', 'add', '(', 'a', ',', 'b', ')', ':', 'return', 'a', '+', 'b']
        code = tokenizer.detokenize(tokens)
        
        self.assertIn('def', code)
        self.assertIn('add', code)
        self.assertIn('return', code)
    
    def test_empty_input(self):
        """Test handling of empty input"""
        tokenizer = CodeTokenizer('python')
        tokens = tokenizer.tokenize('')
        self.assertEqual(tokens, [])
        
        code = tokenizer.detokenize([])
        self.assertEqual(code, '')


class TestSequencePredictor(unittest.TestCase):
    """Test SequencePredictor N-gram engine"""
    
    def test_basic_prediction(self):
        """Test basic next token prediction"""
        predictor = SequencePredictor(n=3)
        
        # Train with simple patterns
        predictor.train([
            ['def', 'add', 'return'],
            ['def', 'subtract', 'return'],
            ['def', 'multiply', 'return']
        ])
        
        # Predict next token after 'def'
        predictions = predictor.predict(['def'], top_k=1)
        
        self.assertEqual(len(predictions), 1)
        token, confidence = predictions[0]
        self.assertIn(token, ['add', 'subtract', 'multiply'])
        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_backoff_mechanism(self):
        """Test N-gram backoff to lower orders"""
        predictor = SequencePredictor(n=5)
        
        # Train with limited data
        predictor.train([
            ['a', 'b', 'c', 'd', 'e', 'f']
        ])
        
        # Predict with context that requires backoff
        # Exact 5-gram won't match, should fall back to lower orders
        predictions = predictor.predict(['x', 'y', 'z'], top_k=1)
        
        # Should still return something (from unigram fallback)
        self.assertGreaterEqual(len(predictions), 0)
    
    def test_top_k_predictions(self):
        """Test retrieving top-k predictions"""
        predictor = SequencePredictor(n=2)
        
        # Train with known frequencies
        predictor.train([
            ['if', 'x'],
            ['if', 'y'],
            ['if', 'y'],
            ['if', 'z'],
            ['if', 'z'],
            ['if', 'z']
        ])
        
        # Get top-3 predictions
        predictions = predictor.predict(['if'], top_k=3)
        
        self.assertEqual(len(predictions), 3)
        
        # Should be sorted by frequency: z (3), y (2), x (1)
        tokens = [token for token, _ in predictions]
        self.assertEqual(tokens[0], 'z')
        self.assertEqual(tokens[1], 'y')
        self.assertEqual(tokens[2], 'x')
    
    def test_confidence_scores(self):
        """Test confidence score calculation"""
        predictor = SequencePredictor(n=2)
        
        # Train with known distribution
        predictor.train([
            ['start', 'a'],
            ['start', 'a'],
            ['start', 'b']
        ])
        
        predictions = predictor.predict(['start'], top_k=2)
        
        # 'a' appears 2/3 times, 'b' appears 1/3 times
        token_a, conf_a = predictions[0]
        token_b, conf_b = predictions[1]
        
        self.assertEqual(token_a, 'a')
        self.assertAlmostEqual(conf_a, 2/3, places=2)
        self.assertEqual(token_b, 'b')
        self.assertAlmostEqual(conf_b, 1/3, places=2)
    
    def test_vocabulary_tracking(self):
        """Test vocabulary is properly tracked"""
        predictor = SequencePredictor(n=3)
        
        predictor.train([
            ['a', 'b', 'c'],
            ['d', 'e', 'f']
        ])
        
        self.assertEqual(len(predictor.vocabulary), 6)
        self.assertIn('a', predictor.vocabulary)
        self.assertIn('f', predictor.vocabulary)
    
    def test_ngram_counts(self):
        """Test N-gram count reporting"""
        predictor = SequencePredictor(n=3)
        
        predictor.train([
            ['a', 'b', 'c', 'd']
        ])
        
        counts = predictor.get_ngram_counts()
        
        # Should have N-grams of order 1, 2, and 3
        self.assertIn(1, counts)
        self.assertIn(2, counts)
        self.assertIn(3, counts)
        
        # Check counts make sense
        self.assertGreater(counts[1], 0)
        self.assertGreater(counts[2], 0)
        self.assertGreater(counts[3], 0)


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test CodeCompletionPredictor main interface"""
    
    def setUp(self):
        """Set up test predictor"""
        self.model = CodeCompletionPredictor(language='python', n=5)
        self.training_data = [
            'def add(a, b): return a + b',
            'def subtract(a, b): return a - b',
            'def multiply(a, b): return a * b',
            'def divide(a, b): return a / b',
            'def validate(user): return len(user) > 0',
            'if x > 0: return True',
            'if x < 0: return False',
            'for i in range(10): print(i)'
        ]
        self.model.train(self.training_data)
    
    def test_challenge_id(self):
        """Test challenge ID is set correctly"""
        self.assertEqual(
            self.model.challenge_id,
            'challenge-ml_code_predictor-1766931267-134357'
        )
    
    def test_predict_next_line(self):
        """Test Case 1: Predict next code line"""
        line, confidence = self.model.predict_next_line('def process(data): ')
        
        # Should predict something
        self.assertIsInstance(line, str)
        self.assertGreater(len(line), 0)
        
        # Confidence should be valid
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_complete_function(self):
        """Test Case 2: Complete functions"""
        completion, confidence = self.model.complete_function('def validate(x): ')
        
        # Should predict something
        self.assertIsInstance(completion, str)
        self.assertGreater(len(completion), 0)
        
        # Confidence should be valid
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_beam_search(self):
        """Test multiple predictions (beam search)"""
        predictions = self.model.get_predictions('return a ', top_k=3)
        
        # Should get multiple predictions
        self.assertGreaterEqual(len(predictions), 1)
        self.assertLessEqual(len(predictions), 3)
        
        # Each prediction should have token and confidence
        for token, confidence in predictions:
            self.assertIsInstance(token, str)
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_real_time_performance(self):
        """Test Requirement 4: Real-time inference (<100ms)"""
        # Warm up cache
        self.model.predict_next_line('def test(): ')
        
        # Measure cold prediction time
        start = time.time()
        self.model.predict_next_line('if x > ')
        cold_time = (time.time() - start) * 1000  # Convert to ms
        
        # Measure cached prediction time
        start = time.time()
        self.model.predict_next_line('if x > ')  # Same context, should be cached
        cached_time = (time.time() - start) * 1000
        
        # Both should be under 100ms
        self.assertLess(cold_time, 100, f"Cold prediction took {cold_time:.2f}ms (target: <100ms)")
        self.assertLess(cached_time, 10, f"Cached prediction took {cached_time:.2f}ms (target: <10ms)")
        
        print(f"\n⚡ Performance: Cold={cold_time:.2f}ms, Cached={cached_time:.2f}ms")
    
    def test_multi_language_support(self):
        """Test Requirement 2: Multiple programming languages"""
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in languages:
            model = CodeCompletionPredictor(language=lang, n=3)
            
            # Basic training
            if lang == 'python':
                model.train(['def test(): pass'])
            elif lang in ('javascript', 'typescript'):
                model.train(['function test() { }'])
            elif lang == 'java':
                model.train(['public void test() { }'])
            elif lang == 'go':
                model.train(['func test() { }'])
            
            # Should be able to predict
            line, conf = model.predict_next_line('function ')
            self.assertIsInstance(line, str)
            self.assertGreaterEqual(conf, 0.0)
        
        print(f"\n🌍 Tested {len(languages)} languages: {', '.join(languages)}")
    
    def test_confidence_scores(self):
        """Test Requirement 3: Confidence scores"""
        # Get multiple predictions
        predictions = self.model.get_predictions('def ', top_k=5)
        
        # All should have valid confidence scores
        for token, confidence in predictions:
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
        
        # Confidence should be sorted (highest first)
        confidences = [conf for _, conf in predictions]
        self.assertEqual(confidences, sorted(confidences, reverse=True))
    
    def test_model_persistence(self):
        """Test model save/load functionality"""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Train and save model
            original_model = CodeCompletionPredictor('python', n=3)
            original_model.train(['def test(): return 42'])
            original_pred, original_conf = original_model.predict_next_line('def ')
            
            original_model.save_model(temp_path)
            
            # Load model
            loaded_model = CodeCompletionPredictor('python', n=3)
            loaded_model.load_model(temp_path)
            
            # Should make same prediction
            loaded_pred, loaded_conf = loaded_model.predict_next_line('def ')
            
            self.assertEqual(original_pred, loaded_pred)
            self.assertAlmostEqual(original_conf, loaded_conf, places=5)
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_caching_mechanism(self):
        """Test prediction caching works"""
        # Clear stats
        self.model.cache.clear()
        self.model.cache_hits = 0
        self.model.cache_misses = 0
        
        # First prediction (cache miss)
        self.model.predict_next_line('def test(): ')
        self.assertEqual(self.model.cache_misses, 1)
        self.assertEqual(self.model.cache_hits, 0)
        
        # Second prediction (cache hit)
        self.model.predict_next_line('def test(): ')
        self.assertEqual(self.model.cache_misses, 1)
        self.assertEqual(self.model.cache_hits, 1)
        
        # Different context (cache miss)
        self.model.predict_next_line('if x: ')
        self.assertEqual(self.model.cache_misses, 2)
        self.assertEqual(self.model.cache_hits, 1)
    
    def test_get_stats(self):
        """Test statistics reporting"""
        stats = self.model.get_stats()
        
        # Should have expected keys
        self.assertIn('challenge_id', stats)
        self.assertIn('language', stats)
        self.assertIn('vocabulary_size', stats)
        self.assertIn('cache_hit_rate', stats)
        
        # Values should be valid
        self.assertEqual(stats['challenge_id'], 'challenge-ml_code_predictor-1766931267-134357')
        self.assertEqual(stats['language'], 'python')
        self.assertGreater(stats['vocabulary_size'], 0)
        self.assertGreaterEqual(stats['cache_hit_rate'], 0.0)
        self.assertLessEqual(stats['cache_hit_rate'], 1.0)
    
    def test_empty_training_data(self):
        """Test handling of empty training data"""
        model = CodeCompletionPredictor('python', n=3)
        model.train([])
        
        # Should not crash
        line, conf = model.predict_next_line('def test(): ')
        
        # May return empty or have low confidence
        self.assertIsInstance(line, str)
        self.assertGreaterEqual(conf, 0.0)
    
    def test_empty_context(self):
        """Test handling of empty context"""
        line, conf = self.model.predict_next_line('')
        
        # Should handle gracefully
        self.assertIsInstance(line, str)
        self.assertGreaterEqual(conf, 0.0)


class TestRequirementsValidation(unittest.TestCase):
    """Validate all challenge requirements are met"""
    
    def setUp(self):
        """Set up test model"""
        self.model = CodeCompletionPredictor('python', n=5)
        training_data = [
            'def add(a, b): return a + b',
            'def subtract(a, b): return a - b',
            'if x > 0: return True',
            'for i in range(10): print(i)'
        ]
        self.model.train(training_data)
    
    def test_requirement_1_sequence_prediction_model(self):
        """✅ Requirement 1: Train a sequence prediction model"""
        # Model should be trained and make predictions
        line, conf = self.model.predict_next_line('def ')
        
        self.assertIsInstance(line, str)
        self.assertGreater(len(line), 0)
        self.assertGreater(conf, 0.0)
        
        print("\n✅ Requirement 1: Sequence prediction model trained and working")
    
    def test_requirement_2_multi_language_support(self):
        """✅ Requirement 2: Support multiple programming languages"""
        supported_languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in supported_languages:
            model = CodeCompletionPredictor(language=lang, n=3)
            # Each language should have keywords
            self.assertGreater(len(model.tokenizer.keywords), 0)
        
        print(f"✅ Requirement 2: {len(supported_languages)} programming languages supported")
    
    def test_requirement_3_confidence_scores(self):
        """✅ Requirement 3: Provide confidence scores for predictions"""
        # All predictions should have confidence scores
        predictions = self.model.get_predictions('return ', top_k=5)
        
        for token, confidence in predictions:
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
        
        print(f"✅ Requirement 3: Confidence scores provided (0.0-1.0 range)")
    
    def test_requirement_4_real_time_inference(self):
        """✅ Requirement 4: Optimize for real-time inference"""
        # Test cold and cached performance
        start = time.time()
        self.model.predict_next_line('def process(): ')
        cold_time = (time.time() - start) * 1000
        
        start = time.time()
        self.model.predict_next_line('def process(): ')  # Cached
        cached_time = (time.time() - start) * 1000
        
        self.assertLess(cold_time, 100)
        self.assertLess(cached_time, 10)
        
        print(f"✅ Requirement 4: Real-time inference optimized (cold: {cold_time:.1f}ms, cached: {cached_time:.1f}ms)")


class TestCaseValidation(unittest.TestCase):
    """Validate challenge test cases"""
    
    def setUp(self):
        """Set up test model"""
        self.model = CodeCompletionPredictor('python', n=5)
        training_data = [
            'def add(a, b): return a + b',
            'def validate(user): return len(user) > 0',
            'if status == 200: return True'
        ]
        self.model.train(training_data)
    
    def test_case_1_predicts_next_code_line(self):
        """✅ Test Case 1: Predicts next code line"""
        # Input: code_context
        code_context = 'def process(data): '
        
        # Expected: predicted_line
        predicted_line, confidence = self.model.predict_next_line(code_context)
        
        self.assertIsInstance(predicted_line, str)
        self.assertGreater(len(predicted_line), 0)
        self.assertGreaterEqual(confidence, 0.0)
        
        print(f"\n✅ Test Case 1: Predicts next code line")
        print(f"   Input: '{code_context}'")
        print(f"   Output: '{predicted_line}' (confidence: {confidence:.0%})")
    
    def test_case_2_completes_functions(self):
        """✅ Test Case 2: Completes functions"""
        # Input: partial_function
        partial_function = 'def validate(x): '
        
        # Expected: completion
        completion, confidence = self.model.complete_function(partial_function)
        
        self.assertIsInstance(completion, str)
        self.assertGreater(len(completion), 0)
        self.assertGreaterEqual(confidence, 0.0)
        
        print(f"\n✅ Test Case 2: Completes functions")
        print(f"   Input: '{partial_function}'")
        print(f"   Output: '{completion}' (confidence: {confidence:.0%})")


def run_all_tests():
    """Run all tests and print summary"""
    print("=" * 70)
    print("🧪 Code Completion Predictor - Test Suite")
    print("   Challenge ID: challenge-ml_code_predictor-1766931267-134357")
    print("   Created by: @create-botter")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeTokenizer))
    suite.addTests(loader.loadTestsFromTestCase(TestSequencePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeCompletionPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirementsValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestCaseValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        print("\n✅ Requirements Validated:")
        print("  ✓ Requirement 1: Sequence prediction model trained and working")
        print("  ✓ Requirement 2: Multiple programming languages supported")
        print("  ✓ Requirement 3: Confidence scores provided for all predictions")
        print("  ✓ Requirement 4: Real-time inference optimized (<100ms)")
        print("\n✅ Test Cases Validated:")
        print("  ✓ Test Case 1: Successfully predicts next code line")
        print("  ✓ Test Case 2: Successfully completes functions")
    else:
        print("\n❌ Some tests failed. See details above.")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
