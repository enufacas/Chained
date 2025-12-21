"""
Test Suite for Code Completion Predictor by @create-botter

Comprehensive tests validating all requirements and test cases.
Challenge ID: challenge-ml_code_predictor-1766326453-402640

Requirements being tested:
    1. Train a sequence prediction model ✅
    2. Support multiple programming languages ✅
    3. Provide confidence scores for predictions ✅
    4. Optimize for real-time inference ✅

Test Cases being validated:
    1. Predicts next code line ✅
    2. Completes functions ✅
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
    """Test the CodeTokenizer class for all supported languages"""
    
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
    
    def test_typescript_tokenization(self):
        """Test TypeScript code tokenization"""
        tokenizer = CodeTokenizer('typescript')
        code = 'interface User { name: string; }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('interface', tokens)
        self.assertIn('User', tokens)
        self.assertIn('string', tokens)
    
    def test_java_tokenization(self):
        """Test Java code tokenization"""
        tokenizer = CodeTokenizer('java')
        code = 'public class Main { public static void main() {} }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('public', tokens)
        self.assertIn('class', tokens)
        self.assertIn('static', tokens)
    
    def test_go_tokenization(self):
        """Test Go code tokenization"""
        tokenizer = CodeTokenizer('go')
        code = 'func main() { fmt.Println("Hello") }'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('func', tokens)
        self.assertIn('main', tokens)
    
    def test_multi_char_operators(self):
        """Test multi-character operator handling"""
        tokenizer = CodeTokenizer('python')
        code = 'if x == 5 and y >= 10'
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('==', tokens)
        self.assertIn('>=', tokens)
    
    def test_comment_removal_python(self):
        """Test Python comment filtering"""
        tokenizer = CodeTokenizer('python')
        code = 'def foo(): # this is a comment\n    return 42'
        tokens = tokenizer.tokenize(code)
        
        # Comment should be removed
        self.assertNotIn('comment', tokens)
        self.assertIn('def', tokens)
        self.assertIn('return', tokens)
    
    def test_comment_removal_javascript(self):
        """Test JavaScript comment filtering"""
        tokenizer = CodeTokenizer('javascript')
        code = 'const x = 5; // comment here'
        tokens = tokenizer.tokenize(code)
        
        self.assertNotIn('comment', tokens)
        self.assertIn('const', tokens)
    
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
    
    def test_basic_prediction(self):
        """Test basic sequence prediction"""
        predictor = SequencePredictor(n=3)
        
        # Train on simple sequences
        sequences = [
            ['a', 'b', 'c'],
            ['a', 'b', 'd'],
            ['a', 'b', 'c']
        ]
        predictor.train(sequences)
        
        # Predict next token after ['a', 'b']
        predictions = predictor.predict(['a', 'b'], top_k=2)
        
        self.assertGreater(len(predictions), 0)
        self.assertEqual(predictions[0][0], 'c')  # 'c' is most common
    
    def test_backoff_strategy(self):
        """Test intelligent backoff with shorter contexts"""
        predictor = SequencePredictor(n=5)
        
        sequences = [
            ['x', 'y', 'z'],
            ['a', 'b', 'x', 'y', 'z']
        ]
        predictor.train(sequences)
        
        # Should find 'z' even with partial context
        predictions = predictor.predict(['y'], top_k=1)
        
        self.assertGreater(len(predictions), 0)
        self.assertEqual(predictions[0][0], 'z')
    
    def test_confidence_scores(self):
        """Test confidence score generation"""
        predictor = SequencePredictor(n=3)
        
        sequences = [
            ['a', 'b', 'c'] for _ in range(10)
        ]
        predictor.train(sequences)
        
        predictions = predictor.predict(['a', 'b'], top_k=1)
        
        self.assertGreater(len(predictions), 0)
        token, confidence = predictions[0]
        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_top_k_predictions(self):
        """Test getting multiple prediction options"""
        predictor = SequencePredictor(n=3)
        
        sequences = [
            ['if', 'x', '>'],
            ['if', 'x', '=='],
            ['if', 'x', '<']
        ]
        predictor.train(sequences)
        
        predictions = predictor.predict(['if', 'x'], top_k=3)
        
        self.assertEqual(len(predictions), 3)
        # All should be operators
        tokens = [pred[0] for pred in predictions]
        self.assertIn('>', tokens)
        self.assertIn('==', tokens)
        self.assertIn('<', tokens)
    
    def test_empty_context(self):
        """Test handling of empty context"""
        predictor = SequencePredictor(n=3)
        predictions = predictor.predict([], top_k=1)
        
        self.assertEqual(len(predictions), 0)


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main CodeCompletionPredictor class"""
    
    def test_basic_training(self):
        """Test model training"""
        model = CodeCompletionPredictor('python', n=5)
        
        training_data = [
            'def foo(): return 42',
            'def bar(): return 100'
        ]
        
        model.train(training_data)
        
        stats = model.get_stats()
        self.assertGreater(stats['vocabulary_size'], 0)
    
    def test_next_line_prediction(self):
        """Test Case 1: Predicts next code line"""
        model = CodeCompletionPredictor('python', n=5)
        
        training_data = [
            'def validate_email(email): return "@" in email',
            'def validate_phone(phone): return len(phone) == 10',
            'def validate_username(user): return len(user) >= 3'
        ]
        
        model.train(training_data)
        
        line, confidence = model.predict_next_line('def validate_password(pwd): ')
        
        # Should predict something
        self.assertIsInstance(line, str)
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        # Should predict 'return' since all training samples use it
        self.assertIn('return', line.lower())
    
    def test_function_completion(self):
        """Test Case 2: Completes functions"""
        model = CodeCompletionPredictor('python', n=5)
        
        training_data = [
            'def add(a, b):\n    return a + b',
            'def multiply(a, b):\n    return a * b',
            'def divide(a, b):\n    return a / b'
        ]
        
        model.train(training_data)
        
        partial_function = 'def subtract(a, b):\n    '
        completion, confidence = model.complete_function(partial_function)
        
        # Should complete the function
        self.assertIsInstance(completion, str)
        self.assertGreater(len(completion), 0)
        self.assertIsInstance(confidence, float)
        
        # Should predict 'return' pattern
        self.assertIn('return', completion.lower())
    
    def test_multi_language_support(self):
        """Requirement 2: Multiple programming language support"""
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in languages:
            model = CodeCompletionPredictor(lang, n=3)
            
            # Each should create successfully
            self.assertEqual(model.language, lang)
            self.assertIsNotNone(model.tokenizer)
    
    def test_confidence_scores(self):
        """Requirement 3: Confidence scores for predictions"""
        model = CodeCompletionPredictor('python', n=5)
        
        training_data = [
            'if x > 0: print("positive")',
            'if x > 0: print("positive")',
            'if x > 0: print("positive")'
        ]
        
        model.train(training_data)
        
        line, confidence = model.predict_next_line('if x > 0: ')
        
        # Should have valid confidence score
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        # High repetition should give high confidence
        self.assertGreater(confidence, 0.5)
    
    def test_real_time_inference(self):
        """Requirement 4: Real-time inference optimization"""
        model = CodeCompletionPredictor('python', n=5)
        
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
        self.assertLess(avg_time_ms, 100)
    
    def test_beam_search(self):
        """Test getting multiple prediction options"""
        model = CodeCompletionPredictor('python', n=5)
        
        training_data = [
            'if status == 200: handle_success()',
            'if status == 404: handle_not_found()',
            'if status == 500: handle_error()'
        ]
        
        model.train(training_data)
        
        predictions = model.get_predictions('if status == ', top_k=3)
        
        self.assertGreater(len(predictions), 0)
        self.assertLessEqual(len(predictions), 3)
        
        # Each prediction should have token and confidence
        for pred, conf in predictions:
            self.assertIsInstance(pred, str)
            self.assertIsInstance(conf, float)
            self.assertGreaterEqual(conf, 0.0)
            self.assertLessEqual(conf, 1.0)
    
    def test_model_persistence(self):
        """Test save and load functionality"""
        model = CodeCompletionPredictor('python', n=5)
        
        training_data = ['def foo(): return 42']
        model.train(training_data)
        
        # Save model
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            path = f.name
        
        try:
            model.save_model(path)
            
            # Load into new model
            new_model = CodeCompletionPredictor('python', n=5)
            new_model.load_model(path)
            
            # Should have same stats
            self.assertEqual(
                model.get_stats()['vocabulary_size'],
                new_model.get_stats()['vocabulary_size']
            )
        finally:
            os.unlink(path)
    
    def test_javascript_support(self):
        """Test JavaScript-specific features"""
        model = CodeCompletionPredictor('javascript', n=5)
        
        training_data = [
            'const add = (a, b) => a + b',
            'const multiply = (a, b) => a * b'
        ]
        
        model.train(training_data)
        
        line, confidence = model.predict_next_line('const subtract = (a, b) => ')
        
        self.assertIsInstance(line, str)
        self.assertGreater(len(line), 0)
    
    def test_edge_case_long_context(self):
        """Test handling of very long context"""
        model = CodeCompletionPredictor('python', n=5)
        
        training_data = ['def foo(): return 42']
        model.train(training_data)
        
        # Very long context
        long_context = ' '.join(['token'] * 100) + ' def bar(): '
        
        # Should not crash
        line, confidence = model.predict_next_line(long_context)
        self.assertIsInstance(line, str)
    
    def test_edge_case_special_characters(self):
        """Test handling of special characters"""
        model = CodeCompletionPredictor('python', n=5)
        
        training_data = ['x = [1, 2, 3]']
        model.train(training_data)
        
        line, confidence = model.predict_next_line('y = ')
        
        # Should handle gracefully
        self.assertIsInstance(line, str)
    
    def test_get_stats(self):
        """Test statistics retrieval"""
        model = CodeCompletionPredictor('python', n=5)
        
        training_data = ['def foo(): return 42']
        model.train(training_data)
        
        stats = model.get_stats()
        
        self.assertIn('challenge_id', stats)
        self.assertEqual(stats['challenge_id'], 'challenge-ml_code_predictor-1766326453-402640')
        self.assertIn('language', stats)
        self.assertIn('vocabulary_size', stats)
        self.assertIn('ngram_counts', stats)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""
    
    def test_train_model_function(self):
        """Test train_model convenience function"""
        training_data = ['def foo(): return 42']
        
        model = train_model(training_data, language='python', n=5)
        
        self.assertIsInstance(model, CodeCompletionPredictor)
        self.assertEqual(model.language, 'python')
        self.assertEqual(model.n, 5)
        
        # Should be ready to predict
        line, conf = model.predict_next_line('def bar(): ')
        self.assertIsInstance(line, str)


class TestRequirements(unittest.TestCase):
    """Validate all challenge requirements"""
    
    def test_requirement_1_sequence_prediction(self):
        """Requirement 1: Train a sequence prediction model"""
        model = CodeCompletionPredictor('python', n=5)
        
        training_data = [
            'def func1(): return 1',
            'def func2(): return 2'
        ]
        
        # Should train successfully
        model.train(training_data)
        
        # Should be able to predict
        line, confidence = model.predict_next_line('def func3(): ')
        
        self.assertIsInstance(line, str)
        self.assertIsInstance(confidence, float)
        print("✅ Requirement 1: Sequence prediction model trained and working")
    
    def test_requirement_2_multi_language(self):
        """Requirement 2: Support multiple programming languages"""
        languages = ['python', 'javascript', 'typescript', 'java', 'go']
        
        for lang in languages:
            model = CodeCompletionPredictor(lang, n=3)
            model.train([f'test code in {lang}'])
            
            # Each should work independently
            self.assertEqual(model.language, lang)
        
        print(f"✅ Requirement 2: {len(languages)} programming languages supported")
    
    def test_requirement_3_confidence_scores(self):
        """Requirement 3: Provide confidence scores"""
        model = CodeCompletionPredictor('python', n=5)
        model.train(['def foo(): return 42'])
        
        line, confidence = model.predict_next_line('def bar(): ')
        
        # Should have valid confidence
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        print(f"✅ Requirement 3: Confidence scores provided (example: {confidence:.1%})")
    
    def test_requirement_4_real_time_inference(self):
        """Requirement 4: Optimize for real-time inference"""
        model = CodeCompletionPredictor('python', n=5)
        
        training_data = [f'def func{i}(): return {i}' for i in range(100)]
        model.train(training_data)
        
        # Measure cold prediction
        start = time.time()
        model.predict_next_line('def test(): ')
        cold_time_ms = (time.time() - start) * 1000
        
        # Should be under 100ms
        self.assertLess(cold_time_ms, 100)
        
        print(f"✅ Requirement 4: Real-time inference optimized ({cold_time_ms:.1f}ms)")


def run_tests():
    """Run all tests and print summary"""
    print("=" * 70)
    print("TEST SUITE - Code Completion Predictor by @create-botter")
    print("Challenge ID: challenge-ml_code_predictor-1766326453-402640")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeTokenizer))
    suite.addTests(loader.loadTestsFromTestCase(TestSequencePredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeCompletionPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestRequirements))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print()
        print("Requirements Validated:")
        print("  ✓ Requirement 1: Sequence prediction model")
        print("  ✓ Requirement 2: Multiple programming languages")
        print("  ✓ Requirement 3: Confidence scores")
        print("  ✓ Requirement 4: Real-time inference")
        print()
        print("Test Cases Validated:")
        print("  ✓ Test Case 1: Predicts next code line")
        print("  ✓ Test Case 2: Completes functions")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the failures above")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
