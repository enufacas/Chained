#!/usr/bin/env python3
"""
Example Usage for Code Completion Predictor

This example demonstrates how to use the Code Completion Predictor
for various code completion tasks.

Created by @create-guru for the Chained autonomous AI ecosystem.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from code_completion_predictor import (
    CodeCompletionPredictor,
    train_model
)


def example_1_basic_prediction():
    """Example 1: Basic next line prediction"""
    print("\n" + "="*70)
    print("Example 1: Basic Next Line Prediction")
    print("="*70)
    
    # Sample training data
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
    if not numbers:
        return 0
    total = sum(numbers)
    count = len(numbers)
    return total / count
        """,
        """
def find_maximum(array):
    if not array:
        return None
    max_value = array[0]
    for value in array:
        if value > max_value:
            max_value = value
    return max_value
        """
    ]
    
    # Train model
    print("\nTraining model...")
    model = train_model(training_code, language='python')
    print("✓ Model trained on 3 code samples")
    
    # Test prediction
    context = """
def calculate_product(numbers):
    result = 1
    """
    
    print(f"\nCode context:")
    print(context)
    
    predicted_line, confidence = model.predict_next_line(context)
    print(f"\nPredicted next line: {repr(predicted_line)}")
    print(f"Confidence: {confidence:.1%}")


def example_2_function_completion():
    """Example 2: Complete a partial function"""
    print("\n" + "="*70)
    print("Example 2: Function Completion")
    print("="*70)
    
    # Training data with similar patterns
    training_code = [
        """
class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        result = []
        for item in self.data:
            if item.is_valid():
                result.append(item.transform())
        return result
        """,
        """
class StringProcessor:
    def __init__(self, text):
        self.text = text
    
    def process(self):
        words = []
        for word in self.text.split():
            if len(word) > 3:
                words.append(word.upper())
        return words
        """
    ]
    
    # Train model
    print("\nTraining model...")
    model = train_model(training_code, language='python')
    print("✓ Model trained")
    
    # Partial function
    partial = """
class NumberProcessor:
    def __init__(self, numbers):
        self.numbers = numbers
    
    def process(self):
        result = []
        for num in self.numbers:
    """
    
    print(f"\nPartial function:")
    print(partial)
    
    completion, confidence = model.complete_function(partial)
    print(f"\nSuggested completion: {repr(completion)}")
    print(f"Confidence: {confidence:.1%}")


def example_3_multiple_predictions():
    """Example 3: Get multiple prediction options"""
    print("\n" + "="*70)
    print("Example 3: Multiple Prediction Options")
    print("="*70)
    
    # Training data
    training_code = [
        "if condition:\n    print('true')\nelse:\n    print('false')",
        "if x > 0:\n    return x\nelse:\n    return -x",
        "if data:\n    process(data)\nelse:\n    return None"
    ]
    
    # Train model
    print("\nTraining model...")
    model = train_model(training_code, language='python')
    print("✓ Model trained")
    
    # Get multiple predictions
    context = "if "
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"\nContext: {repr(context)}")
    print("\nTop 5 predictions:")
    for i, (token, confidence) in enumerate(predictions, 1):
        print(f"  {i}. {token:20s} (confidence: {confidence:.1%})")


def example_4_javascript_support():
    """Example 4: JavaScript code completion"""
    print("\n" + "="*70)
    print("Example 4: JavaScript Support")
    print("="*70)
    
    # JavaScript training data
    js_code = [
        """
function calculateSum(numbers) {
    let total = 0;
    for (const num of numbers) {
        total += num;
    }
    return total;
}
        """,
        """
function findMax(array) {
    if (array.length === 0) {
        return null;
    }
    let max = array[0];
    for (const val of array) {
        if (val > max) {
            max = val;
        }
    }
    return max;
}
        """,
        """
const processData = (data) => {
    const result = [];
    for (const item of data) {
        if (item.isValid()) {
            result.push(item.transform());
        }
    }
    return result;
};
        """
    ]
    
    # Train JavaScript model
    print("\nTraining JavaScript model...")
    model = CodeCompletionPredictor(language='javascript')
    model.train(js_code)
    print("✓ JavaScript model trained")
    
    # Test prediction
    context = """
function calculateAverage(numbers) {
    let total = 0;
    """
    
    print(f"\nJavaScript context:")
    print(context)
    
    predicted, confidence = model.predict_next_line(context)
    print(f"\nPredicted: {repr(predicted)}")
    print(f"Confidence: {confidence:.1%}")


def example_5_model_persistence():
    """Example 5: Save and load model"""
    print("\n" + "="*70)
    print("Example 5: Model Persistence")
    print("="*70)
    
    import tempfile
    import os
    
    # Training data
    training_code = [
        "def foo(): return 42",
        "def bar(): return 'hello'",
        "def baz(): return [1, 2, 3]"
    ]
    
    # Train and save model
    print("\n1. Training model...")
    model = train_model(training_code, language='python')
    print("   ✓ Model trained")
    
    # Save to file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        model_path = f.name
    
    try:
        print(f"\n2. Saving model to {model_path}...")
        model.save_model(model_path)
        print("   ✓ Model saved")
        
        # Load model
        print("\n3. Loading model from disk...")
        new_model = CodeCompletionPredictor(language='python')
        new_model.load_model(model_path)
        print("   ✓ Model loaded")
        
        # Test loaded model
        context = "def test():"
        predicted, confidence = new_model.predict_next_line(context)
        print(f"\n4. Testing loaded model:")
        print(f"   Context: {repr(context)}")
        print(f"   Predicted: {repr(predicted)}")
        print(f"   Confidence: {confidence:.1%}")
        
    finally:
        if os.path.exists(model_path):
            os.unlink(model_path)
            print(f"\n✓ Cleaned up temporary file")


def example_6_real_world_usage():
    """Example 6: Real-world usage pattern"""
    print("\n" + "="*70)
    print("Example 6: Real-World Usage Pattern")
    print("="*70)
    
    # Simulate real-world code repository
    repository_code = [
        # File 1: utils.py
        """
def validate_input(data):
    if not data:
        return False
    if not isinstance(data, dict):
        return False
    required_keys = ['id', 'name', 'value']
    for key in required_keys:
        if key not in data:
            return False
    return True
        """,
        # File 2: processor.py
        """
class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.results = []
    
    def process_item(self, item):
        if validate_input(item):
            transformed = self.transform(item)
            self.results.append(transformed)
            return True
        return False
    
    def transform(self, item):
        return {
            'id': item['id'],
            'processed_name': item['name'].upper(),
            'doubled_value': item['value'] * 2
        }
        """,
        # File 3: api.py
        """
def process_request(request_data):
    processor = DataProcessor(config={'mode': 'production'})
    
    items = request_data.get('items', [])
    for item in items:
        processor.process_item(item)
    
    return {
        'status': 'success',
        'processed': len(processor.results),
        'results': processor.results
    }
        """
    ]
    
    print("\nTraining on repository code...")
    model = train_model(repository_code, language='python')
    print(f"✓ Model trained on {len(repository_code)} files")
    
    # Developer starts writing new code
    print("\nDeveloper starts writing:")
    new_code = """
def validate_and_process(data):
    if not validate_input(data):
    """
    
    print(new_code)
    
    # Get completion
    predicted, confidence = model.predict_next_line(new_code)
    print(f"\nCode completion suggestion: {repr(predicted)}")
    print(f"Confidence: {confidence:.1%}")
    
    # Show alternative predictions
    alternatives = model.get_predictions(new_code, top_k=3)
    print("\nAlternative completions:")
    for i, (token, conf) in enumerate(alternatives, 1):
        print(f"  {i}. {token} ({conf:.1%})")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("Code Completion Predictor - Examples")
    print("Created by @create-guru")
    print("="*70)
    
    examples = [
        example_1_basic_prediction,
        example_2_function_completion,
        example_3_multiple_predictions,
        example_4_javascript_support,
        example_5_model_persistence,
        example_6_real_world_usage
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n✗ Error in {example.__name__}: {e}")
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Try training on your own code samples")
    print("  2. Experiment with different n-gram orders")
    print("  3. Test with different programming languages")
    print("  4. Integrate into your development workflow")
    print("\nFor more information, see README.md")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
