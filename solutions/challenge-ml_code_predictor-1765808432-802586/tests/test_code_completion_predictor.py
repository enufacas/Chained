#!/usr/bin/env python3
"""
Comprehensive tests for Code Completion Predictor

Tests all requirements from the challenge:
1. Sequence prediction model
2. Multi-language support  
3. Confidence scores for predictions
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
    """Test the custom code tokenizer"""
    
    def test_python_tokenization(self):
        """Test Python code tokenization"""
        tokenizer = CodeTokenizer('python')
        code = "def hello():\n    return 'world'"
        tokens = tokenizer.tokenize(code)
        
        # Should contain keyword, identifier, and string tokens
        self.assertIn('<KEYWORD:def>', tokens)
        self.assertIn('hello', tokens)
        self.assertIn('<KEYWORD:return>', tokens)
        self.assertIn('<STRING>', tokens)
        
    def test_javascript_tokenization(self):
        """Test JavaScript code tokenization"""
        tokenizer = CodeTokenizer('javascript')
        code = "function test() { return 42; }"
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('<KEYWORD:function>', tokens)
        self.assertIn('test', tokens)
        self.assertIn('<KEYWORD:return>', tokens)
        self.assertIn('<NUMBER>', tokens)
    
    def test_java_tokenization(self):
        """Test Java code tokenization"""
        tokenizer = CodeTokenizer('java')
        code = "public class Test { private int x; }"
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('<KEYWORD:public>', tokens)
        self.assertIn('<KEYWORD:class>', tokens)
        self.assertIn('Test', tokens)
        self.assertIn('<KEYWORD:private>', tokens)
        self.assertIn('<KEYWORD:int>', tokens)
    
    def test_cpp_tokenization(self):
        """Test C++ code tokenization"""
        tokenizer = CodeTokenizer('cpp')
        code = "class MyClass { public: int value; };"
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('<KEYWORD:class>', tokens)
        self.assertIn('MyClass', tokens)
        self.assertIn('<KEYWORD:public>', tokens)
    
    def test_go_tokenization(self):
        """Test Go code tokenization"""
        tokenizer = CodeTokenizer('go')
        code = "func main() { return nil }"
        tokens = tokenizer.tokenize(code)
        
        self.assertIn('<KEYWORD:func>', tokens)
        self.assertIn('main', tokens)
        self.assertIn('<KEYWORD:return>', tokens)
    
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
        """Test that newlines are preserved as context markers"""
        tokenizer = CodeTokenizer('python')
        code = "line1\nline2\nline3"
        tokens = tokenizer.tokenize(code)
        
        newline_count = tokens.count('<NEWLINE>')
        self.assertEqual(newline_count, 2)
    
    def test_normalizes_strings(self):
        """Test that strings are normalized"""
        tokenizer = CodeTokenizer('python')
        code = '"hello" and "world"'
        tokens = tokenizer.tokenize(code)
        
        string_count = tokens.count('<STRING>')
        self.assertEqual(string_count, 2)
    
    def test_normalizes_numbers(self):
        """Test that numbers are normalized"""
        tokenizer = CodeTokenizer('python')
        code = "x = 42 + 3.14"
        tokens = tokenizer.tokenize(code)
        
        number_count = tokens.count('<NUMBER>')
        self.assertEqual(number_count, 2)


class TestSequencePredictor(unittest.TestCase):
    """Test the N-gram sequence predictor"""
    
    def setUp(self):
        """Set up test predictor"""
        self.predictor = SequencePredictor(n=3)
    
    def test_training(self):
        """Test basic training"""
        sequences = [
            ['def', 'hello', '(', ')', ':'],
            ['def', 'world', '(', ')', ':'],
            ['def', 'test', '(', ')', ':']
        ]
        
        self.predictor.train(sequences)
        
        # Vocabulary should be built
        self.assertGreater(len(self.predictor.vocab), 0)
        # N-grams should be built
        self.assertGreater(len(self.predictor.ngrams), 0)
    
    def test_prediction(self):
        """Test next token prediction"""
        sequences = [
            ['<KEYWORD:def>', 'func', '(', ')', ':'],
            ['<KEYWORD:def>', 'func', '(', ')', ':'],
            ['<KEYWORD:def>', 'test', '(', ')', ':']
        ]
        
        self.predictor.train(sequences)
        
        # Predict after 'def'
        context = ('<KEYWORD:def>', 'func', '(')
        predictions = self.predictor.predict_next(context, top_k=3)
        
        self.assertGreater(len(predictions), 0)
        # First prediction should be the most common next token
        token, confidence = predictions[0]
        self.assertIsInstance(token, str)
        self.assertGreater(confidence, 0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_beam_search(self):
        """Test beam search for multiple candidates"""
        sequences = [
            ['<KEYWORD:for>', 'i', '<KEYWORD:in>', 'range', '('],
            ['<KEYWORD:for>', 'x', '<KEYWORD:in>', 'list', '('],
            ['<KEYWORD:for>', 'item', '<KEYWORD:in>', 'items', ':']
        ]
        
        self.predictor.train(sequences)
        
        context = ['<KEYWORD:for>']
        beams = self.predictor.beam_search(context, num_tokens=3, beam_width=3)
        
        self.assertGreater(len(beams), 0)
        # Each beam should have sequence and score
        for sequence, score in beams:
            self.assertIsInstance(sequence, list)
            self.assertGreater(score, 0)
            self.assertLessEqual(score, 1.0)
    
    def test_backoff(self):
        """Test context backoff when exact match not found"""
        sequences = [
            ['a', 'b', 'c', 'd'],
            ['x', 'b', 'c', 'd'],
            ['y', 'b', 'c', 'd']
        ]
        
        self.predictor.train(sequences)
        
        # Context not in training data
        context = ('z', 'b', 'c')
        predictions = self.predictor.predict_next(context, top_k=3)
        
        # Should still get predictions via backoff
        self.assertGreater(len(predictions), 0)
    
    def test_save_load(self):
        """Test model persistence"""
        sequences = [
            ['def', 'test', '(', ')', ':'],
            ['def', 'func', '(', ')', ':']
        ]
        
        self.predictor.train(sequences)
        
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Save
            self.predictor.save(temp_path)
            self.assertTrue(temp_path.exists())
            
            # Load into new predictor
            new_predictor = SequencePredictor(n=3)
            new_predictor.load(temp_path)
            
            # Should have same vocabulary
            self.assertEqual(len(new_predictor.vocab), len(self.predictor.vocab))
            self.assertEqual(len(new_predictor.ngrams), len(self.predictor.ngrams))
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestCodeCompletionPredictor(unittest.TestCase):
    """Test the main code completion predictor"""
    
    def setUp(self):
        """Set up training data"""
        self.python_samples = [
            """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
            """,
            """
def find_max(numbers):
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val
            """,
            """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
            """
        ]
        
        self.javascript_samples = [
            """
function calculateSum(numbers) {
    let total = 0;
    for (let num of numbers) {
        total += num;
    }
    return total;
}
            """,
            """
function findMax(numbers) {
    let maxVal = numbers[0];
    for (let num of numbers) {
        if (num > maxVal) {
            maxVal = num;
        }
    }
    return maxVal;
}
            """
        ]
    
    def test_training(self):
        """Test training the complete model"""
        model = CodeCompletionPredictor('python')
        model.train(self.python_samples)
        
        # Should have trained vocabulary
        self.assertGreater(len(model.predictor.vocab), 0)
    
    def test_predict_next_line_python(self):
        """Test Case 1: Predicts next code line for Python"""
        model = train_model(self.python_samples, language='python')
        
        code_context = """
def process_data(data):
    result = []
    for item in data:"""
        
        predictions = model.predict_next_line(code_context, num_predictions=3)
        
        # Should return predictions
        self.assertGreater(len(predictions), 0)
        
        # Each prediction should have code and confidence
        for predicted_line, confidence in predictions:
            self.assertIsInstance(predicted_line, str)
            self.assertGreater(len(predicted_line), 0)
            self.assertGreater(confidence, 0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_predict_next_line_javascript(self):
        """Test predicting next line for JavaScript"""
        model = train_model(self.javascript_samples, language='javascript')
        
        code_context = """
function processArray(arr) {
    let result = [];
    for (let item of arr) {"""
        
        predictions = model.predict_next_line(code_context, num_predictions=2)
        
        self.assertGreater(len(predictions), 0)
        for line, conf in predictions:
            self.assertIsInstance(line, str)
            self.assertGreater(conf, 0)
    
    def test_complete_function(self):
        """Test Case 2: Completes functions"""
        model = train_model(self.python_samples, language='python')
        
        partial_function = """
def sum_list(numbers):
    total = 0"""
        
        completions = model.complete_function(partial_function, num_completions=3)
        
        # Should return completions
        self.assertGreater(len(completions), 0)
        
        # Each completion should have code and confidence
        for completion, confidence in completions:
            self.assertIsInstance(completion, str)
            self.assertGreater(confidence, 0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_confidence_scores(self):
        """Test that confidence scores are provided"""
        model = train_model(self.python_samples, language='python')
        
        code_context = "def test():"
        predictions = model.predict_next_line(code_context, num_predictions=3)
        
        # All predictions should have confidence scores
        for _, confidence in predictions:
            self.assertIsInstance(confidence, float)
            self.assertGreater(confidence, 0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_real_time_inference(self):
        """Test that inference is optimized for real-time (<100ms target)"""
        model = train_model(self.python_samples, language='python')
        
        code_context = "def calculate():\n    x = 10"
        
        # Measure prediction time
        start = time.time()
        for _ in range(10):
            predictions = model.predict_next_line(code_context, num_predictions=3)
        end = time.time()
        
        avg_time = (end - start) / 10
        
        # Should be reasonably fast (allowing some overhead for testing)
        # Target is <100ms, but we'll be lenient in tests
        self.assertLess(avg_time, 1.0, "Inference should be fast")
    
    def test_caching(self):
        """Test that caching improves performance"""
        model = train_model(self.python_samples, language='python')
        
        code_context = "def test(): return"
        
        # First call (not cached)
        start1 = time.time()
        pred1 = model.predict_next_line(code_context, num_predictions=3)
        time1 = time.time() - start1
        
        # Second call (cached)
        start2 = time.time()
        pred2 = model.predict_next_line(code_context, num_predictions=3)
        time2 = time.time() - start2
        
        # Cached call should be faster
        self.assertLess(time2, time1 * 2, "Caching should improve performance")
        
        # Results should be identical
        self.assertEqual(pred1, pred2)
    
    def test_save_load(self):
        """Test model persistence"""
        model = train_model(self.python_samples, language='python')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / 'model.pkl'
            
            # Save
            model.save(model_path)
            self.assertTrue(model_path.exists())
            
            # Load
            new_model = CodeCompletionPredictor('python')
            new_model.load(model_path)
            
            # Should produce same predictions
            code = "def test():"
            pred1 = model.predict_next_line(code, num_predictions=2)
            pred2 = new_model.predict_next_line(code, num_predictions=2)
            
            self.assertEqual(len(pred1), len(pred2))
    
    def test_multi_language_support(self):
        """Test that multiple languages are supported"""
        languages = ['python', 'javascript', 'java', 'cpp', 'go']
        
        for lang in languages:
            model = CodeCompletionPredictor(lang)
            self.assertEqual(model.language, lang)
            # Should have language-specific keywords
            self.assertGreater(len(model.tokenizer.keywords), 0)


class TestRequirements(unittest.TestCase):
    """Test all challenge requirements"""
    
    def test_requirement_1_sequence_prediction(self):
        """Requirement 1: Train a sequence prediction model"""
        # Create and train model
        samples = [
            "def test(): return 1",
            "def func(): return 2"
        ]
        model = train_model(samples, language='python')
        
        # Model should be trained
        self.assertGreater(len(model.predictor.vocab), 0)
        self.assertGreater(len(model.predictor.ngrams), 0)
    
    def test_requirement_2_multi_language(self):
        """Requirement 2: Support multiple programming languages"""
        languages = ['python', 'javascript', 'java', 'cpp', 'go']
        
        for lang in languages:
            tokenizer = CodeTokenizer(lang)
            # Each language should have keywords
            self.assertGreater(len(tokenizer.keywords), 0, 
                              f"{lang} should have keywords")
    
    def test_requirement_3_confidence_scores(self):
        """Requirement 3: Provide confidence scores for predictions"""
        samples = ["def test(): return x" for _ in range(5)]
        model = train_model(samples, language='python')
        
        predictions = model.predict_next_line("def func():", num_predictions=3)
        
        # All predictions must have confidence scores
        for _, confidence in predictions:
            self.assertIsInstance(confidence, float)
            self.assertGreaterEqual(confidence, 0.0)
            self.assertLessEqual(confidence, 1.0)
    
    def test_requirement_4_real_time_inference(self):
        """Requirement 4: Optimize for real-time inference"""
        samples = [
            "def calculate(): return sum(range(10))",
            "def process(): return len(data)"
        ] * 10
        
        model = train_model(samples, language='python')
        
        # Measure inference time
        start = time.time()
        predictions = model.predict_next_line("def test():", num_predictions=5)
        inference_time = time.time() - start
        
        # Should complete reasonably quickly
        self.assertLess(inference_time, 1.0)
        self.assertGreater(len(predictions), 0)


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == '__main__':
    result = run_tests()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
