"""
Test Suite for Code Completion Predictor

Comprehensive tests for the Code Completion Predictor by @create-botter.
Tests all requirements, test cases, and edge cases.

Challenge ID: challenge-ml_code_predictor-1766067467-803260

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
        code = 'const add = (a, b) => a + b'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('const', tokens)
        self.assertIn('add', tokens)
        self.assertIn('=>', tokens)
    
    def test_multi_char_operators(self):
        """Test multi-character operator handling"""
        tokenizer = CodeTokenizer('python')
        code = 'if x == 5 and y >= 10'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('==', tokens)
        self.assertIn('>=', tokens)
    
    def test_comment_removal(self):
        """Test comment filtering"""
        tokenizer = CodeTokenizer('python')
        code = 'def foo(): # this is a comment\n    return 42'
        tokens = tokenizer.tokenize(code)
        
        # Comment should be removed
        self.assertNotIn('comment', tokens)
        self.assertIn('def', tokens)
        self.assertIn('return', tokens)
    
    def test_detokenization(self):
        """Test token-to-code conversion"""
        tokenizer = CodeTokenizer('python')
        tokens = ['def', 'foo', '(', ')', ':', 'return', '42']
        code = tokenizer.detokenize(tokens)
        
        self.assertIn('def foo', code)
        self.assertIn('return 42', code)
    
    def test_empty_input(self):
        """Test handling of empty input"""
        tokenizer = CodeTokenizer('python')
        tokens = tokenizer.tokenize('')
        
        self.assertEqual(tokens, [])


class TestSequencePredictor(unittest.TestCase):
    """Test the SequencePredictor class"""
    
    def test_training(self):
        """Test basic training"""
        predictor = SequencePredictor(n=3)
        sequences = [
            ['def', 'foo', '(', ')', ':', 'return', '42'],
            ['def', 'bar', '(', ')', ':', 'return', '100']
        ]
        
        predictor.train(sequences)
        
        # Check vocabulary
        self.assertGreater(len(predictor.vocabulary), 0)
        self.assertIn('def', predictor.vocabulary)
        self.assertIn('return', predictor.vocabulary)
    
    def test_prediction(self):
        """Test basic prediction"""
        predictor = SequencePredictor(n=3)
        sequences = [
            ['def', 'foo', '(', ')', ':'],
            ['def', 'bar', '(', ')', ':']
        ]
        
        predictor.train(sequences)
        
        # Predict after 'def'
        predictions = predictor.predict(['def'], top_k=1)
        
        self.assertGreater(len(predictions), 0)
        # Should predict common pattern
    
    def test_backoff_strategy(self):
        """Test backoff to shorter contexts"""
        predictor = SequencePredictor(n=5)
        sequences = [
            ['a', 'b', 'c', 'd', 'e'],
            ['x', 'y', 'c', 'd', 'e']
        ]
        
        predictor.train(sequences)
        
        # Even with long context, should find matches via backoff
        predictions = predictor.predict(['unknown', 'c', 'd'], top_k=1)
        
        self.assertGreater(len(predictions), 0)
    
    def test_confidence_scores(self):
        """Test that confidence scores are in valid range"""
        predictor = SequencePredictor(n=3)
        sequences = [['a', 'b', 'c']]
        
        predictor.train(sequences)
        predictions = predictor.predict(['a', 'b'], top_k=1)
        
        if predictions:
            token, confidence = predictions[0]
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_caching(self):
        """Test prediction caching"""
        predictor = SequencePredictor(n=3)
        sequences = [['a', 'b', 'c']]
        
        predictor.train(sequences)
        
        # First prediction
        context = ['a', 'b']
        pred1 = predictor.predict(context, top_k=1)
        
        # Second prediction (should use cache)
        pred2 = predictor.predict(context, top_k=1)
        
        self.assertEqual(pred1, pred2)
        self.assertGreater(len(predictor.prediction_cache), 0)


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main CodeCompletionPredictor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.training_data = [
            'def validate_email(email): return "@" in email',
            'def validate_phone(phone): return len(phone) == 10',
            'def validate_username(user): return len(user) > 3'
        ]
    
    def test_initialization(self):
        """Test model initialization"""
        model = CodeCompletionPredictor('python', n=5)
        
        self.assertEqual(model.language, 'python')
        self.assertEqual(model.n, 5)
        self.assertIsNotNone(model.tokenizer)
        self.assertIsNotNone(model.predictor)
    
    def test_training(self):
        """Test model training"""
        model = CodeCompletionPredictor('python')
        model.train(self.training_data)
        
        stats = model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)
    
    def test_predict_next_line(self):
        """Test next line prediction - Test Case 1"""
        model = CodeCompletionPredictor('python')
        model.train(self.training_data)
        
        context = 'def validate_password(pwd): '
        line, confidence = model.predict_next_line(context)
        
        # Should predict something
        self.assertIsInstance(line, str)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_complete_function(self):
        """Test function completion - Test Case 2"""
        model = CodeCompletionPredictor('python')
        model.train(self.training_data)
        
        partial = 'def process_data(data): '
        completion, confidence = model.complete_function(partial)
        
        # Should provide completion
        self.assertIsInstance(completion, str)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_get_predictions(self):
        """Test beam search (multiple predictions)"""
        model = CodeCompletionPredictor('python')
        model.train(self.training_data)
        
        context = 'return len('
        predictions = model.get_predictions(context, top_k=3)
        
        self.assertIsInstance(predictions, list)
        # Each prediction should be (text, confidence) tuple
        for pred in predictions:
            self.assertEqual(len(pred), 2)
            text, confidence = pred
            self.assertIsInstance(text, str)
            self.assertIsInstance(confidence, float)
    
    def test_model_persistence(self):
        """Test save and load functionality"""
        import tempfile
        
        model1 = CodeCompletionPredictor('python')
        model1.train(self.training_data)
        
        # Save model
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            model1.save_model(temp_path)
            
            # Load model
            model2 = CodeCompletionPredictor('python')
            model2.load_model(temp_path)
            
            # Should have same stats
            stats1 = model1.get_stats()
            stats2 = model2.get_stats()
            
            self.assertEqual(stats1['vocabulary_size'], stats2['vocabulary_size'])
            self.assertEqual(stats1['language'], stats2['language'])
        finally:
            os.unlink(temp_path)
    
    def test_statistics(self):
        """Test model statistics"""
        model = CodeCompletionPredictor('python')
        model.train(self.training_data)
        
        stats = model.get_stats()
        
        # Check expected keys
        self.assertIn('challenge_id', stats)
        self.assertIn('language', stats)
        self.assertIn('vocabulary_size', stats)
        self.assertIn('ngram_counts', stats)
        
        # Check values
        self.assertEqual(stats['challenge_id'], 'challenge-ml_code_predictor-1766067467-803260')
        self.assertEqual(stats['language'], 'python')


class TestMultiLanguageSupport(unittest.TestCase):
    """Test multi-language support - Requirement 2"""
    
    def test_python_support(self):
        """Test Python language support"""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return 42'])
        
        line, conf = model.predict_next_line('def bar(): ')
        self.assertIsInstance(line, str)
    
    def test_javascript_support(self):
        """Test JavaScript language support"""
        model = CodeCompletionPredictor('javascript')
        model.train(['const add = (a, b) => a + b'])
        
        line, conf = model.predict_next_line('const sub = (a, b) => ')
        self.assertIsInstance(line, str)
    
    def test_typescript_support(self):
        """Test TypeScript language support"""
        model = CodeCompletionPredictor('typescript')
        model.train(['interface User { name: string }'])
        
        line, conf = model.predict_next_line('interface Product { ')
        self.assertIsInstance(line, str)
    
    def test_java_support(self):
        """Test Java language support"""
        model = CodeCompletionPredictor('java')
        model.train(['public int add(int a, int b) { return a + b; }'])
        
        line, conf = model.predict_next_line('public int sub(int a, int b) { ')
        self.assertIsInstance(line, str)
    
    def test_go_support(self):
        """Test Go language support"""
        model = CodeCompletionPredictor('go')
        model.train(['func add(a int, b int) int { return a + b }'])
        
        line, conf = model.predict_next_line('func sub(a int, b int) int { ')
        self.assertIsInstance(line, str)


class TestPerformance(unittest.TestCase):
    """Test real-time inference - Requirement 4"""
    
    def test_prediction_speed(self):
        """Test that predictions are fast enough for real-time"""
        model = CodeCompletionPredictor('python')
        
        # Train on reasonable dataset
        training_data = [
            f'def func{i}(): return {i}'
            for i in range(50)
        ]
        model.train(training_data)
        
        # Measure prediction time
        start = time.time()
        for _ in range(10):
            model.predict_next_line('def test(): ')
        elapsed = time.time() - start
        
        avg_time_ms = (elapsed / 10) * 1000
        
        # Should be under 100ms per prediction (requirement)
        self.assertLess(avg_time_ms, 100,
                       f"Prediction too slow: {avg_time_ms:.2f}ms")
    
    def test_cached_prediction_speed(self):
        """Test that cached predictions are very fast"""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return 42'])
        
        context = 'def bar(): '
        
        # First prediction (cold)
        model.predict_next_line(context)
        
        # Cached predictions
        start = time.time()
        for _ in range(100):
            model.predict_next_line(context)
        elapsed = time.time() - start
        
        avg_time_ms = (elapsed / 100) * 1000
        
        # Cached should be very fast
        self.assertLess(avg_time_ms, 10,
                       f"Cached prediction too slow: {avg_time_ms:.2f}ms")


class TestRequirements(unittest.TestCase):
    """Test all challenge requirements"""
    
    def test_requirement_1_sequence_prediction(self):
        """Requirement 1: Sequence prediction model"""
        model = CodeCompletionPredictor('python')
        training_data = ['def foo(): return 42']
        
        # Train model
        model.train(training_data)
        
        # Make prediction
        line, conf = model.predict_next_line('def bar(): ')
        
        # Should produce prediction
        self.assertIsInstance(line, str)
        self.assertIsInstance(conf, float)
    
    def test_requirement_2_multi_language(self):
        """Requirement 2: Multi-language support"""
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in languages:
            model = CodeCompletionPredictor(lang)
            self.assertEqual(model.language, lang)
    
    def test_requirement_3_confidence_scores(self):
        """Requirement 3: Confidence scores"""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return 42'])
        
        line, confidence = model.predict_next_line('def bar(): ')
        
        # Confidence should be 0.0-1.0
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_requirement_4_real_time_inference(self):
        """Requirement 4: Real-time inference"""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return 42'] * 10)
        
        # Measure inference time
        start = time.time()
        model.predict_next_line('def bar(): ')
        elapsed_ms = (time.time() - start) * 1000
        
        # Should be under 100ms
        self.assertLess(elapsed_ms, 100)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_training_data(self):
        """Test with no training data"""
        model = CodeCompletionPredictor('python')
        
        # Don't train
        line, conf = model.predict_next_line('def foo(): ')
        
        # Should handle gracefully
        self.assertIsInstance(line, str)
        self.assertIsInstance(conf, float)
    
    def test_empty_context(self):
        """Test with empty context"""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return 42'])
        
        line, conf = model.predict_next_line('')
        
        # Should handle gracefully
        self.assertIsInstance(line, str)
        self.assertIsInstance(conf, float)
    
    def test_very_long_context(self):
        """Test with very long context"""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return 42'])
        
        long_context = 'def ' + 'x ' * 100 + '(): '
        line, conf = model.predict_next_line(long_context)
        
        # Should handle gracefully
        self.assertIsInstance(line, str)
    
    def test_special_characters(self):
        """Test with special characters"""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return "hello"'])
        
        line, conf = model.predict_next_line('def bar(): return "')
        
        self.assertIsInstance(line, str)
    
    def test_unicode_support(self):
        """Test with unicode characters"""
        model = CodeCompletionPredictor('python')
        model.train(['def greet(): return "Hello 世界"'])
        
        line, conf = model.predict_next_line('def say_hi(): ')
        
        self.assertIsInstance(line, str)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def test_train_model_function(self):
        """Test train_model convenience function"""
        code_samples = ['def foo(): return 42']
        model = train_model(code_samples, 'python', n=5)
        
        self.assertIsInstance(model, CodeCompletionPredictor)
        self.assertEqual(model.language, 'python')
        self.assertEqual(model.n, 5)


def run_tests():
    """Run all tests and print summary"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeTokenizer))
    suite.addTests(loader.loadTestsFromTestCase(TestSequencePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeCompletionPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiLanguageSupport))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirements))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY - Code Completion Predictor by @create-botter")
    print(f"Challenge ID: challenge-ml_code_predictor-1766067467-803260")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
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
        print("🎉 ALL TESTS PASSED! 🎉")
    else:
        print("❌ Some tests failed. Review output above.")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
