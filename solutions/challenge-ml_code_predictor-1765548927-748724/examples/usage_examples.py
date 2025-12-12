#!/usr/bin/env python3
"""
Usage Examples for Code Completion Predictor

Demonstrates various features and use cases.

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
    print("\n" + "="*60)
    print("Example 1: Basic Next Line Prediction")
    print("="*60)
    
    # Training data
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
        """
    ]
    
    # Train model
    print("\n📚 Training model on sample code...")
    model = train_model(training_code, language='python')
    
    # Predict next line
    context = "def calculate_total(items):\n    total = 0\n    "
    print(f"\n💭 Context:\n{context}")
    
    predicted_line, confidence = model.predict_next_line(context)
    print(f"\n🎯 Predicted next line: {predicted_line}")
    print(f"📊 Confidence: {confidence:.1%}")


def example_2_function_completion():
    """Example 2: Function completion"""
    print("\n" + "="*60)
    print("Example 2: Function Completion")
    print("="*60)
    
    # Training data with common patterns
    training_code = [
        """
        def process_data(items):
            result = []
            for item in items:
                if item > 0:
                    result.append(item * 2)
            return result
        """,
        """
        def filter_items(data):
            result = []
            for value in data:
                if value != None:
                    result.append(value)
            return result
        """
    ]
    
    print("\n📚 Training model...")
    model = train_model(training_code, language='python')
    
    # Complete partial function
    partial = "def transform_list(values):\n    result = "
    print(f"\n💭 Partial function:\n{partial}")
    
    completion, confidence = model.complete_function(partial)
    print(f"\n🎯 Suggested completion: {completion}")
    print(f"📊 Confidence: {confidence:.1%}")


def example_3_multiple_predictions():
    """Example 3: Multiple prediction options"""
    print("\n" + "="*60)
    print("Example 3: Multiple Prediction Options")
    print("="*60)
    
    training_code = [
        "if x > 0: print('positive')",
        "if y > 0: return True",
        "if z > 0: continue",
        "for item in items: process(item)",
        "for i in range(10): print(i)",
    ]
    
    print("\n📚 Training model...")
    model = train_model(training_code, language='python')
    
    # Get multiple predictions
    context = "if "
    print(f"\n💭 Context: '{context}'")
    
    predictions = model.get_predictions(context, top_k=5)
    print(f"\n🎯 Top predictions:")
    for i, (token, confidence) in enumerate(predictions, 1):
        print(f"   {i}. {token:20} (confidence: {confidence:.1%})")


def example_4_javascript_support():
    """Example 4: JavaScript support"""
    print("\n" + "="*60)
    print("Example 4: JavaScript Support")
    print("="*60)
    
    # JavaScript training data
    js_code = [
        """
        function processArray(items) {
            const result = [];
            for (const item of items) {
                result.push(item * 2);
            }
            return result;
        }
        """,
        """
        const calculateSum = (numbers) => {
            let total = 0;
            for (const num of numbers) {
                total += num;
            }
            return total;
        }
        """
    ]
    
    print("\n📚 Training JavaScript model...")
    model = train_model(js_code, language='javascript')
    
    # Predict in JavaScript
    context = "function transform(data) {\n    const result = "
    print(f"\n💭 JavaScript context:\n{context}")
    
    predicted_line, confidence = model.predict_next_line(context)
    print(f"\n🎯 Predicted: {predicted_line}")
    print(f"📊 Confidence: {confidence:.1%}")


def example_5_model_persistence():
    """Example 5: Save and load models"""
    print("\n" + "="*60)
    print("Example 5: Model Persistence")
    print("="*60)
    
    import tempfile
    import os
    
    # Train a model
    training_code = [
        "def foo(): return 42",
        "def bar(): return 'hello'"
    ]
    
    print("\n📚 Training original model...")
    model = train_model(training_code, language='python')
    
    # Test prediction
    context = "def test(): "
    original_prediction, _ = model.predict_next_line(context)
    print(f"\n🎯 Original prediction: {original_prediction}")
    
    # Save model
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        model_path = f.name
    
    print(f"\n💾 Saving model to {model_path}...")
    model.save_model(model_path)
    
    # Load into new model
    print(f"📂 Loading model from disk...")
    new_model = CodeCompletionPredictor(language='python')
    new_model.load_model(model_path)
    
    # Test loaded model
    loaded_prediction, _ = new_model.predict_next_line(context)
    print(f"🎯 Loaded model prediction: {loaded_prediction}")
    
    # Clean up
    os.remove(model_path)
    
    # Verify they match
    if original_prediction == loaded_prediction:
        print("✅ Model persistence works correctly!")
    else:
        print("⚠️  Predictions differ (expected with probabilistic models)")


def example_6_real_world_usage():
    """Example 6: Real-world usage pattern"""
    print("\n" + "="*60)
    print("Example 6: Real-World Usage Pattern")
    print("="*60)
    
    # Simulate training on actual codebase
    training_code = [
        """
        class DataProcessor:
            def __init__(self):
                self.data = []
                self.processed = False
            
            def add_item(self, item):
                self.data.append(item)
            
            def process(self):
                result = []
                for item in self.data:
                    if item is not None:
                        result.append(item)
                self.processed = True
                return result
        """,
        """
        class Calculator:
            def __init__(self):
                self.history = []
            
            def add(self, a, b):
                result = a + b
                self.history.append(result)
                return result
            
            def get_history(self):
                return self.history
        """
    ]
    
    print("\n📚 Training on realistic codebase...")
    model = train_model(training_code, language='python')
    
    # Simulate IDE autocomplete scenarios
    scenarios = [
        "class MyClass:\n    def __init__(self):\n        ",
        "def process_items(data):\n    for item in data:\n        ",
        "if value is not None:\n    "
    ]
    
    print("\n🎯 IDE Autocomplete Scenarios:\n")
    for i, scenario in enumerate(scenarios, 1):
        print(f"Scenario {i}:")
        print(f"  Context: {repr(scenario)}")
        prediction, confidence = model.predict_next_line(scenario)
        print(f"  Suggestion: {prediction}")
        print(f"  Confidence: {confidence:.1%}\n")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("🚀 Code Completion Predictor - Usage Examples")
    print("="*60)
    print("\nCreated by @create-botter")
    print("Part of the Chained autonomous AI ecosystem")
    
    examples = [
        example_1_basic_prediction,
        example_2_function_completion,
        example_3_multiple_predictions,
        example_4_javascript_support,
        example_5_model_persistence,
        example_6_real_world_usage
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {example_func.__name__}: {e}")
    
    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
