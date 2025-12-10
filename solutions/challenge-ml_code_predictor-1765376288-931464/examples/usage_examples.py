#!/usr/bin/env python3
"""
Usage Examples for Code Completion Predictor

Demonstrates various use cases and features of the code completion system.
Created by @create-botter for the Chained autonomous AI ecosystem.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from code_completion_predictor import train_model, CodeCompletionPredictor


def example_1_basic_prediction():
    """Example 1: Basic next line prediction"""
    print("\n" + "=" * 70)
    print("Example 1: Basic Next Line Prediction")
    print("=" * 70)
    
    # Training data with common Python patterns
    training_code = [
        """
        def calculate_sum(numbers):
            total = 0
            for num in numbers:
                total += num
            return total
        """,
        """
        def calculate_average(numbers):
            total = 0
            count = 0
            for num in numbers:
                total += num
                count += 1
            return total / count
        """,
        """
        def find_maximum(numbers):
            max_val = numbers[0]
            for num in numbers:
                if num > max_val:
                    max_val = num
            return max_val
        """
    ]
    
    # Train model
    print("\nTraining model on sample Python code...")
    model = train_model(training_code, language='python')
    print("✓ Model trained")
    
    # Make prediction
    context = "def calculate_average(numbers):\n    total = 0\n    "
    print(f"\nContext:\n{context}")
    
    predicted_line, confidence = model.predict_next_line(context)
    print(f"\nPredicted next token: {predicted_line}")
    print(f"Confidence: {confidence:.1%}")


def example_2_function_completion():
    """Example 2: Complete partial functions"""
    print("\n" + "=" * 70)
    print("Example 2: Function Completion with Beam Search")
    print("=" * 70)
    
    training_code = [
        """
        def process_items(items):
            result = []
            for item in items:
                result.append(item)
            return result
        """,
        """
        def filter_items(items):
            result = []
            for item in items:
                if item is not None:
                    result.append(item)
            return result
        """,
        """
        def transform_items(items):
            result = []
            for item in items:
                result.append(item * 2)
            return result
        """
    ]
    
    model = train_model(training_code, language='python')
    
    # Complete a partial function
    partial = "def process_data(items):\n    result = []\n    for item in items:\n        "
    print(f"Partial function:\n{partial}")
    
    completion, confidence = model.complete_function(partial)
    print(f"\nCompletion suggestion: {completion}")
    print(f"Confidence: {confidence:.1%}")


def example_3_multiple_predictions():
    """Example 3: Get multiple prediction options"""
    print("\n" + "=" * 70)
    print("Example 3: Multiple Prediction Options")
    print("=" * 70)
    
    training_code = [
        "if x > 0: print('positive')",
        "if x < 0: print('negative')",
        "if x == 0: print('zero')",
        "if condition: return True",
        "if test: break",
        "if value: continue"
    ]
    
    model = train_model(training_code, language='python')
    
    # Get top 5 predictions
    context = "if "
    print(f"Context: '{context}'")
    print("\nTop 5 predictions:")
    
    predictions = model.get_predictions(context, top_k=5)
    for i, (token, confidence) in enumerate(predictions, 1):
        print(f"  {i}. {token:15s} (confidence: {confidence:.1%})")


def example_4_javascript_support():
    """Example 4: JavaScript code completion"""
    print("\n" + "=" * 70)
    print("Example 4: JavaScript Support")
    print("=" * 70)
    
    js_training = [
        "function add(a, b) { return a + b; }",
        "function multiply(x, y) { return x * y; }",
        "const sum = (a, b) => a + b;",
        "const product = (x, y) => x * y;",
        "async function fetchData() { return await fetch(url); }"
    ]
    
    print("\nTraining JavaScript model...")
    model = train_model(js_training, language='javascript')
    print("✓ Model trained")
    
    context = "function calculate(x, y) { "
    print(f"\nContext: {context}")
    
    predicted, confidence = model.predict_next_line(context)
    print(f"Predicted: {predicted}")
    print(f"Confidence: {confidence:.1%}")


def example_5_model_persistence():
    """Example 5: Save and load models"""
    print("\n" + "=" * 70)
    print("Example 5: Model Persistence")
    print("=" * 70)
    
    import tempfile
    import os
    
    training_code = [
        "def foo(): return 42",
        "def bar(): return 'hello'",
        "class MyClass: pass"
    ]
    
    # Train and save
    print("\nTraining model...")
    model = train_model(training_code, language='python')
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        filepath = f.name
    
    try:
        print(f"Saving model to {filepath}...")
        model.save_model(filepath)
        print("✓ Model saved")
        
        # Load into new model
        print("\nLoading model...")
        new_model = CodeCompletionPredictor(language='python')
        new_model.load_model(filepath)
        print("✓ Model loaded")
        
        # Verify it works
        context = "def "
        pred1 = model.predict_next_line(context)
        pred2 = new_model.predict_next_line(context)
        
        print(f"\nOriginal model prediction: {pred1[0]} ({pred1[1]:.1%})")
        print(f"Loaded model prediction: {pred2[0]} ({pred2[1]:.1%})")
        print("✓ Predictions match!" if pred1[0] == pred2[0] else "✗ Predictions differ")
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


def example_6_training_on_real_code():
    """Example 6: Train on a real codebase (simulated)"""
    print("\n" + "=" * 70)
    print("Example 6: Training on Real Codebase")
    print("=" * 70)
    
    # Simulate loading code from multiple files
    print("\nSimulating loading code from repository...")
    
    # Realistic Python code samples
    codebase = [
        """
        class DataProcessor:
            def __init__(self, data):
                self.data = data
                self.results = []
            
            def process(self):
                for item in self.data:
                    if self.validate(item):
                        self.results.append(self.transform(item))
                return self.results
            
            def validate(self, item):
                return item is not None
            
            def transform(self, item):
                return item * 2
        """,
        """
        def read_file(filepath):
            try:
                with open(filepath, 'r') as f:
                    return f.read()
            except FileNotFoundError:
                print(f"File not found: {filepath}")
                return None
            except Exception as e:
                print(f"Error reading file: {e}")
                return None
        """,
        """
        import json
        
        def load_config(config_path):
            data = read_file(config_path)
            if data:
                try:
                    return json.loads(data)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON: {e}")
                    return {}
            return {}
        """
    ]
    
    print(f"✓ Loaded {len(codebase)} code samples")
    
    # Train with larger context window
    print("\nTraining model with n=7 (larger context)...")
    model = CodeCompletionPredictor(language='python', n=7)
    model.train(codebase)
    print("✓ Model trained")
    
    # Test on various contexts
    test_contexts = [
        "class ",
        "def process():\n    for item in items:\n        ",
        "try:\n    ",
        "except "
    ]
    
    print("\nPredictions on various contexts:")
    for context in test_contexts:
        predicted, confidence = model.predict_next_line(context)
        print(f"\n  Context: {context!r}")
        print(f"  Predicted: {predicted!r} ({confidence:.1%})")


def example_7_real_time_performance():
    """Example 7: Demonstrate real-time performance"""
    print("\n" + "=" * 70)
    print("Example 7: Real-Time Performance")
    print("=" * 70)
    
    import time
    
    # Train model
    training_code = [
        "def foo(): pass",
        "def bar(): return 42",
        "if x: print('yes')",
        "for i in range(10): print(i)",
        "while True: break"
    ]
    
    model = train_model(training_code, language='python', n=5)
    
    # Benchmark inference
    contexts = [
        "def ",
        "if ",
        "for ",
        "while ",
        "class "
    ]
    
    print("\nBenchmarking inference speed...")
    print(f"Target: <100ms per prediction\n")
    
    times = []
    for context in contexts:
        start = time.perf_counter()
        predicted, confidence = model.predict_next_line(context)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        times.append(elapsed)
        
        print(f"  '{context}' -> {predicted!r}")
        print(f"    Time: {elapsed:.2f}ms, Confidence: {confidence:.1%}")
    
    avg_time = sum(times) / len(times)
    print(f"\n✓ Average inference time: {avg_time:.2f}ms")
    print(f"✓ All predictions < 100ms: {all(t < 100 for t in times)}")


def main():
    """Run all examples"""
    print("=" * 70)
    print("Code Completion Predictor - Usage Examples")
    print("Created by @create-botter")
    print("Part of the Chained autonomous AI ecosystem")
    print("=" * 70)
    
    examples = [
        example_1_basic_prediction,
        example_2_function_completion,
        example_3_multiple_predictions,
        example_4_javascript_support,
        example_5_model_persistence,
        example_6_training_on_real_code,
        example_7_real_time_performance
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n✗ Error in {example.__name__}: {e}")
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == '__main__':
    main()
