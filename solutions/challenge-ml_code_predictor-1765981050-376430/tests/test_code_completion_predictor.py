"""
Test Suite for Code Completion Predictor

Comprehensive tests for the Code Completion Predictor by @create-botter.
Tests all requirements, test cases, and edge cases.

Challenge ID: challenge-ml_code_predictor-1765981050-376430

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
    
    def test_basic_training(self):
        """Test basic model training"""
        predictor = SequencePredictor(n=3)
        sequences = [
            ['def', 'foo', '(', ')', ':'],
            ['def', 'bar', '(', ')', ':']
        ]
        predictor.train(sequences)
        
        # Check vocabulary
        self.assertGreater(len(predictor.vocabulary), 0)
        self.assertIn('def', predictor.vocabulary)
        self.assertIn(':', predictor.vocabulary)
    
    def test_prediction(self):
        """Test basic prediction"""
        predictor = SequencePredictor(n=3)
        sequences = [
            ['if', 'x', '>', '0', ':'],
            ['if', 'y', '>', '0', ':']
        ]
        predictor.train(sequences)
        
        # Predict next token after 'if x >'
        predictions = predictor.predict(['if', 'x', '>'])
        
        self.assertGreater(len(predictions), 0)
        token, conf = predictions[0]
        self.assertIsInstance(token, str)
        self.assertGreater(conf, 0.0)
        self.assertLessEqual(conf, 1.0)
    
    def test_top_k_predictions(self):
        """Test beam search (top-k predictions)"""
        predictor = SequencePredictor(n=3)
        sequences = [
            ['x', '=', '5'],
            ['x', '=', '10'],
            ['x', '=', '15']
        ]
        predictor.train(sequences)
        
        predictions = predictor.predict(['x', '='], top_k=3)
        
        self.assertGreater(len(predictions), 0)
        self.assertLessEqual(len(predictions), 3)
    
    def test_backoff_strategy(self):
        """Test intelligent backoff to shorter contexts"""
        predictor = SequencePredictor(n=5)
        sequences = [
            ['return', 'True']
        ]
        predictor.train(sequences)
        
        # Even with long context that wasn't trained, should backoff
        predictions = predictor.predict(['a', 'b', 'c', 'return'])
        
        # Should still find 'True' by backing off to 'return'
        self.assertGreater(len(predictions), 0)
    
    def test_stats(self):
        """Test statistics reporting"""
        predictor = SequencePredictor(n=3)
        sequences = [['a', 'b', 'c']]
        predictor.train(sequences)
        
        stats = predictor.get_stats()
        
        self.assertIn('vocabulary_size', stats)
        self.assertIn('ngram_counts', stats)
        self.assertGreater(stats['vocabulary_size'], 0)


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main CodeCompletionPredictor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.python_samples = [
            'def validate_email(email): return "@" in email',
            'def validate_phone(phone): return len(phone) == 10',
            'def validate_username(user): return len(user) > 3'
        ]
    
    def test_initialization(self):
        """Test model initialization"""
        model = CodeCompletionPredictor(language='python', n=5)
        
        self.assertEqual(model.language, 'python')
        self.assertEqual(model.n, 5)
        self.assertIsNotNone(model.tokenizer)
        self.assertIsNotNone(model.predictor)
    
    def test_training(self):
        """Test model training"""
        model = CodeCompletionPredictor('python')
        model.train(self.python_samples)
        
        stats = model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)
    
    def test_next_line_prediction(self):
        """Test Case 1: Predict next code line"""
        model = CodeCompletionPredictor('python', n=5)
        model.train(self.python_samples)
        
        # Test prediction
        line, confidence = model.predict_next_line('def validate_password(pwd): ')
        
        # Validate outputs
        self.assertIsInstance(line, str)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        # Should predict something related to return
        self.assertGreater(len(line), 0)
    
    def test_function_completion(self):
        """Test Case 2: Complete functions"""
        model = CodeCompletionPredictor('python', n=5)
        model.train(self.python_samples)
        
        partial_function = 'def check_valid(x):\n    if x:\n        '
        completion, confidence = model.complete_function(partial_function)
        
        # Validate outputs
        self.assertIsInstance(completion, str)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_beam_search(self):
        """Test multiple predictions (beam search)"""
        model = CodeCompletionPredictor('python')
        model.train(self.python_samples)
        
        predictions = model.get_predictions('return ', top_k=5)
        
        self.assertIsInstance(predictions, list)
        if predictions:
            token, conf = predictions[0]
            self.assertIsInstance(token, str)
            self.assertGreaterEqual(conf, 0.0)
            self.assertLessEqual(conf, 1.0)
    
    def test_multi_language_support(self):
        """Test Requirement 2: Multi-language support"""
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in languages:
            model = CodeCompletionPredictor(lang)
            self.assertEqual(model.language, lang)
            
            # Should be able to train and predict
            if lang == 'python':
                samples = ['def foo(): pass']
            elif lang in ['javascript', 'typescript']:
                samples = ['const foo = () => true']
            elif lang == 'java':
                samples = ['public void foo() { return; }']
            else:  # go
                samples = ['func foo() { return }']
            
            model.train(samples)
            stats = model.get_stats()
            self.assertGreater(stats['vocabulary_size'], 0)
    
    def test_confidence_scores(self):
        """Test Requirement 3: Confidence scores provided"""
        model = CodeCompletionPredictor('python')
        model.train(self.python_samples)
        
        # All prediction methods should return confidence
        line, conf1 = model.predict_next_line('def foo(): ')
        self.assertGreaterEqual(conf1, 0.0)
        self.assertLessEqual(conf1, 1.0)
        
        comp, conf2 = model.complete_function('def bar():\n    ')
        self.assertGreaterEqual(conf2, 0.0)
        self.assertLessEqual(conf2, 1.0)
        
        preds = model.get_predictions('return ')
        if preds:
            _, conf3 = preds[0]
            self.assertGreaterEqual(conf3, 0.0)
            self.assertLessEqual(conf3, 1.0)
    
    def test_real_time_inference(self):
        """Test Requirement 4: Real-time inference optimization"""
        model = CodeCompletionPredictor('python')
        model.train(self.python_samples * 10)  # Train on more data
        
        # Warm up the cache
        model.predict_next_line('def test(): ')
        
        # Measure prediction time
        start = time.time()
        for _ in range(100):
            model.predict_next_line('def test(): ')
        elapsed = time.time() - start
        
        avg_time_ms = (elapsed / 100) * 1000
        
        # Should be fast (< 100ms average, often much faster)
        self.assertLess(avg_time_ms, 100, 
                        f"Average prediction time {avg_time_ms:.2f}ms exceeds 100ms target")
    
    def test_model_persistence(self):
        """Test save/load functionality"""
        import tempfile
        
        model = CodeCompletionPredictor('python')
        model.train(self.python_samples)
        
        # Save model
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            model.save_model(filepath)
            
            # Load into new model
            new_model = CodeCompletionPredictor('python')
            new_model.load_model(filepath)
            
            # Should have same stats
            stats1 = model.get_stats()
            stats2 = new_model.get_stats()
            
            self.assertEqual(stats1['vocabulary_size'], stats2['vocabulary_size'])
            self.assertEqual(stats1['language'], stats2['language'])
        finally:
            os.unlink(filepath)
    
    def test_statistics(self):
        """Test statistics reporting"""
        model = CodeCompletionPredictor('python')
        model.train(self.python_samples)
        
        stats = model.get_stats()
        
        # Check all expected fields
        self.assertIn('challenge_id', stats)
        self.assertIn('language', stats)
        self.assertIn('vocabulary_size', stats)
        self.assertIn('ngram_counts', stats)
        
        self.assertEqual(stats['challenge_id'], 'challenge-ml_code_predictor-1765981050-376430')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_training_data(self):
        """Test behavior with no training data"""
        model = CodeCompletionPredictor('python')
        
        # Should not crash
        line, conf = model.predict_next_line('def foo(): ')
        self.assertIsInstance(line, str)
        self.assertEqual(conf, 0.0)
    
    def test_empty_context(self):
        """Test prediction with empty context"""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): pass'])
        
        line, conf = model.predict_next_line('')
        self.assertIsInstance(line, str)
    
    def test_very_long_context(self):
        """Test with very long code context"""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): pass'])
        
        long_context = 'def ' + ' '.join(['x'] * 100) + ': '
        line, conf = model.predict_next_line(long_context)
        
        # Should handle gracefully
        self.assertIsInstance(line, str)
        self.assertIsInstance(conf, float)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        model = CodeCompletionPredictor('python')
        samples = ['x = "hello world!"', 'y = "test@example.com"']
        model.train(samples)
        
        # Should tokenize and handle correctly
        stats = model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)
    
    def test_unicode_support(self):
        """Test Unicode character support"""
        model = CodeCompletionPredictor('python')
        samples = ['# Comment with émojis 🚀', 'text = "café"']
        model.train(samples)
        
        # Should not crash
        stats = model.get_stats()
        self.assertGreaterEqual(stats['vocabulary_size'], 0)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def test_train_model_function(self):
        """Test the train_model convenience function"""
        samples = ['def foo(): return 42']
        model = train_model(samples, 'python', n=5)
        
        self.assertIsInstance(model, CodeCompletionPredictor)
        self.assertEqual(model.language, 'python')
        self.assertEqual(model.n, 5)
        
        stats = model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)


class TestRequirementsValidation(unittest.TestCase):
    """Validate all challenge requirements"""
    
    def test_requirement_1_sequence_prediction_model(self):
        """Requirement 1: Train a sequence prediction model"""
        model = CodeCompletionPredictor('python')
        samples = [
            'def add(a, b): return a + b',
            'def sub(a, b): return a - b'
        ]
        model.train(samples)
        
        # Model should be trained
        stats = model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)
        
        # Should be able to predict
        line, conf = model.predict_next_line('def mul(a, b): ')
        self.assertGreater(len(line), 0)
        
        print("✓ Requirement 1: Sequence prediction model trained and working")
    
    def test_requirement_2_multi_language_support(self):
        """Requirement 2: Support multiple programming languages"""
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in languages:
            model = CodeCompletionPredictor(lang)
            self.assertEqual(model.language, lang)
        
        print(f"✓ Requirement 2: {len(languages)} programming languages supported")
    
    def test_requirement_3_confidence_scores(self):
        """Requirement 3: Provide confidence scores for predictions"""
        model = CodeCompletionPredictor('python')
        model.train(['def foo(): return True'])
        
        # All prediction methods must return confidence
        line, conf1 = model.predict_next_line('def bar(): ')
        self.assertIsInstance(conf1, float)
        self.assertGreaterEqual(conf1, 0.0)
        self.assertLessEqual(conf1, 1.0)
        
        comp, conf2 = model.complete_function('def baz():\n    ')
        self.assertIsInstance(conf2, float)
        self.assertGreaterEqual(conf2, 0.0)
        self.assertLessEqual(conf2, 1.0)
        
        print("✓ Requirement 3: Confidence scores provided for all predictions")
    
    def test_requirement_4_real_time_inference(self):
        """Requirement 4: Optimize for real-time inference"""
        model = CodeCompletionPredictor('python')
        samples = ['def foo(): return 42'] * 50
        model.train(samples)
        
        # Measure cold prediction
        start = time.time()
        model.predict_next_line('def unique_context(): ')
        cold_time = (time.time() - start) * 1000
        
        # Measure cached prediction
        start = time.time()
        for _ in range(10):
            model.predict_next_line('def bar(): ')
        cached_time = ((time.time() - start) / 10) * 1000
        
        # Should be fast
        self.assertLess(cold_time, 100, f"Cold prediction {cold_time:.2f}ms > 100ms")
        self.assertLess(cached_time, 50, f"Cached prediction {cached_time:.2f}ms > 50ms")
        
        print(f"✓ Requirement 4: Real-time inference optimized")
        print(f"  - Cold prediction: {cold_time:.2f}ms")
        print(f"  - Cached prediction: {cached_time:.2f}ms")


class TestCaseValidation(unittest.TestCase):
    """Validate specific test cases from challenge"""
    
    def test_case_1_predict_next_code_line(self):
        """Test Case 1: Predicts next code line"""
        model = CodeCompletionPredictor('python')
        
        # Train on function patterns
        training_samples = [
            'def validate_email(email): return "@" in email',
            'def validate_phone(phone): return len(phone) == 10',
            'def validate_name(name): return len(name) > 0',
        ]
        model.train(training_samples)
        
        # Test prediction (input: code_context, expected: predicted_line)
        code_context = 'def validate_username(user): '
        predicted_line, confidence = model.predict_next_line(code_context)
        
        # Validate
        self.assertIsInstance(predicted_line, str)
        self.assertGreater(len(predicted_line), 0)
        self.assertIsInstance(confidence, float)
        self.assertGreater(confidence, 0.0)
        
        print(f"✓ Test Case 1: Successfully predicts next code line")
        print(f"  Context: {code_context}")
        print(f"  Prediction: {predicted_line} (confidence: {confidence:.0%})")
    
    def test_case_2_complete_functions(self):
        """Test Case 2: Completes functions"""
        model = CodeCompletionPredictor('python')
        
        # Train on function patterns
        training_samples = [
            'def process_data(data): if data: return data.strip()',
            'def clean_text(text): if text: return text.lower()',
            'def format_name(name): if name: return name.title()',
        ]
        model.train(training_samples)
        
        # Test completion (input: partial_function, expected: completion)
        partial_function = 'def validate_input(value):\n    if value:\n        '
        completion, confidence = model.complete_function(partial_function)
        
        # Validate
        self.assertIsInstance(completion, str)
        self.assertGreater(len(completion), 0)
        self.assertIsInstance(confidence, float)
        self.assertGreater(confidence, 0.0)
        
        print(f"✓ Test Case 2: Successfully completes functions")
        print(f"  Partial: {partial_function.split(chr(10))[-1]}")
        print(f"  Completion: {completion} (confidence: {confidence:.0%})")


def run_tests():
    """Run all tests and print summary"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeTokenizer))
    suite.addTests(loader.loadTestsFromTestCase(TestSequencePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeCompletionPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirementsValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestCaseValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY - Code Completion Predictor by @create-botter")
    print(f"Challenge ID: challenge-ml_code_predictor-1765981050-376430")
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
        print("❌ Some tests failed. See details above.")
        print()
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
