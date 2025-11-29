import unittest
import sys
import os

# Ensure we can import predictor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from predictor import CodePredictor

class TestCodePredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = CodePredictor(n=3)
        # Training on a repetitive pattern to ensure deterministic prediction
        self.training_code = """
def hello_world():
    print("Hello")
    return True

def goodbye_world():
    print("Goodbye")
    return False
"""
        self.predictor.train(self.training_code)


    def test_tokenize(self):
        tokens = self.predictor.tokenize("def hello():\n    pass")
        self.assertEqual(tokens, ["def", "hello", "(", ")", ":", "\n", "pass"])


    def test_predict_next_token(self):
        # Context: "def hello_world():\n" -> ["def", "hello_world", "(", ")", ":", "\n"]
        # After "\n", we saw "print" in training (skipping spaces)
        context = ["def", "hello_world", "(", ")", ":", "\n"]
        token, conf = self.predictor.predict_next_token(context)
        self.assertEqual(token, "print")
        self.assertGreater(conf, 0.0)


    def test_predict_next_line(self):
        context = "def hello_world():\n"
        line, conf = self.predictor.predict_next_line(context)
        self.assertIn("print", line)
        self.assertIn("Hello", line)


    def test_complete_function(self):
        context = "def hello_world():\n"
        completion = self.predictor.complete_function(context)
        self.assertIn("return True", completion)


    def test_multiple_languages(self):
        # Simple test to show it can handle JS-like syntax if trained
        js_code = "function test() { return 1; }"
        self.predictor.train(js_code)
        context = "function test() {"
        tokens = self.predictor.tokenize(context)
        token, _ = self.predictor.predict_next_token(tokens)
        self.assertEqual(token, "return")

if __name__ == "__main__":
    unittest.main()

