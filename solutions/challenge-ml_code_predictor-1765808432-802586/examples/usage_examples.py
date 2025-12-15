#!/usr/bin/env python3
"""
Usage Examples for Code Completion Predictor

Demonstrates practical usage of the code completion model.

Created by @create-botter for the Chained autonomous AI ecosystem.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from code_completion_predictor import (
    CodeTokenizer,
    CodeCompletionPredictor,
    train_model
)


def example_1_basic_prediction():
    """Example 1: Basic next line prediction"""
    print("="*70)
    print("Example 1: Basic Next Line Prediction")
    print("="*70)
    
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
    for num in numbers:
        total += num
    return total / len(numbers)
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
    print("\nTraining model on Python code samples...")
    model = train_model(training_code, language='python', n=3)
    print(f"✓ Model trained with {len(model.predictor.vocab)} tokens in vocabulary")
    
    # Predict next line
    code_context = """
def process_list(items):
    result = []
    for item in items:"""
    
    print(f"\nCode context:\n{code_context}")
    print("\nPredictions:")
    
    predictions = model.predict_next_line(code_context, num_predictions=3)
    for i, (line, confidence) in enumerate(predictions, 1):
        print(f"  {i}. [{confidence:.3f}] {line}")
    
    print()


def example_2_function_completion():
    """Example 2: Complete partial function"""
    print("="*70)
    print("Example 2: Function Completion")
    print("="*70)
    
    training_code = [
        """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
        """,
        """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
        """,
        """
def power(base, exp):
    if exp == 0:
        return 1
    return base * power(base, exp - 1)
        """
    ]
    
    print("\nTraining model...")
    model = train_model(training_code, language='python')
    
    partial_function = """
def recursive_sum(n):
    if n <= 0:"""
    
    print(f"\nPartial function:\n{partial_function}")
    print("\nCompletions:")
    
    completions = model.complete_function(partial_function, num_completions=3)
    for i, (completion, confidence) in enumerate(completions, 1):
        print(f"  {i}. [{confidence:.3f}] {completion}")
    
    print()


def example_3_multi_language():
    """Example 3: Multi-language support"""
    print("="*70)
    print("Example 3: Multi-Language Support")
    print("="*70)
    
    # JavaScript training
    js_code = [
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
    
    print("\nTraining JavaScript model...")
    js_model = train_model(js_code, language='javascript')
    
    js_context = """
function processArray(arr) {
    let result = [];
    for (let item of arr) {"""
    
    print(f"\nJavaScript context:\n{js_context}")
    print("\nPredictions:")
    
    predictions = js_model.predict_next_line(js_context, num_predictions=2)
    for i, (line, conf) in enumerate(predictions, 1):
        print(f"  {i}. [{conf:.3f}] {line}")
    
    print()


def example_4_confidence_scores():
    """Example 4: Understanding confidence scores"""
    print("="*70)
    print("Example 4: Confidence Scores")
    print("="*70)
    
    training_code = [
        "def test(): return 1",
        "def test(): return 1",
        "def test(): return 1",  # Repeated for high confidence
        "def func(): return 2",
    ]
    
    print("\nTraining model with repeated patterns...")
    model = train_model(training_code, language='python')
    
    context = "def test():"
    print(f"\nContext: {context}")
    print("\nPredictions with confidence scores:")
    
    predictions = model.predict_next_line(context, num_predictions=5)
    for i, (line, conf) in enumerate(predictions, 1):
        confidence_bar = "█" * int(conf * 50)
        print(f"  {i}. [{conf:.3f}] {confidence_bar} {line}")
    
    print("\n  Note: Higher scores indicate more confident predictions")
    print()


def example_5_model_persistence():
    """Example 5: Save and load models"""
    print("="*70)
    print("Example 5: Model Persistence")
    print("="*70)
    
    import tempfile
    
    training_code = [
        "def add(a, b): return a + b",
        "def sub(a, b): return a - b",
        "def mul(a, b): return a * b",
    ]
    
    print("\nTraining model...")
    model = train_model(training_code, language='python')
    
    # Save model
    with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
        model_path = Path(f.name)
    
    print(f"Saving model to {model_path}...")
    model.save(model_path)
    print("✓ Model saved")
    
    # Load model
    print("\nLoading model...")
    loaded_model = CodeCompletionPredictor('python')
    loaded_model.load(model_path)
    print("✓ Model loaded")
    
    # Test loaded model
    context = "def div(a, b):"
    predictions = loaded_model.predict_next_line(context, num_predictions=2)
    
    print(f"\nPredictions from loaded model:")
    for i, (line, conf) in enumerate(predictions, 1):
        print(f"  {i}. [{conf:.3f}] {line}")
    
    # Cleanup
    model_path.unlink()
    print()


def example_6_tokenizer_details():
    """Example 6: Understanding tokenization"""
    print("="*70)
    print("Example 6: Code Tokenization")
    print("="*70)
    
    code = """
def calculate(x, y):
    result = x + y
    return result
    """
    
    tokenizer = CodeTokenizer('python')
    tokens = tokenizer.tokenize(code)
    
    print(f"\nOriginal code:{code}")
    print(f"\nTokens ({len(tokens)} total):")
    print("  " + " | ".join(tokens[:20]))
    if len(tokens) > 20:
        print(f"  ... and {len(tokens) - 20} more")
    
    # Show keyword detection
    keywords = [t for t in tokens if t.startswith('<KEYWORD:')]
    print(f"\nKeywords detected: {', '.join(keywords)}")
    
    # Show reconstruction
    reconstructed = tokenizer.detokenize(tokens)
    print(f"\nReconstructed:\n{reconstructed}")
    print()


def example_7_performance():
    """Example 7: Real-time performance"""
    print("="*70)
    print("Example 7: Real-Time Inference Performance")
    print("="*70)
    
    import time
    
    # Create larger training set
    training_code = [
        f"def func{i}(x): return x + {i}" for i in range(50)
    ]
    
    print("\nTraining model on 50 code samples...")
    start = time.time()
    model = train_model(training_code, language='python')
    train_time = time.time() - start
    print(f"✓ Training completed in {train_time:.3f}s")
    
    # Test inference speed
    context = "def new_func(x):"
    
    print("\nTesting inference speed (10 predictions)...")
    times = []
    for _ in range(10):
        start = time.time()
        predictions = model.predict_next_line(context, num_predictions=3)
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    print(f"✓ Average inference time: {avg_time*1000:.2f}ms")
    print(f"  Min: {min(times)*1000:.2f}ms")
    print(f"  Max: {max(times)*1000:.2f}ms")
    
    if avg_time < 0.1:
        print("  ✓ Meets real-time target (<100ms)")
    else:
        print(f"  ⚠ Slower than target (target: <100ms)")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("CODE COMPLETION PREDICTOR - USAGE EXAMPLES")
    print("Created by @create-botter")
    print("="*70 + "\n")
    
    examples = [
        ("Basic Prediction", example_1_basic_prediction),
        ("Function Completion", example_2_function_completion),
        ("Multi-Language", example_3_multi_language),
        ("Confidence Scores", example_4_confidence_scores),
        ("Model Persistence", example_5_model_persistence),
        ("Tokenization", example_6_tokenizer_details),
        ("Performance", example_7_performance),
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            print(f"❌ Example {i} ({name}) failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("="*70)
    print("All examples completed!")
    print("="*70)


if __name__ == '__main__':
    main()
