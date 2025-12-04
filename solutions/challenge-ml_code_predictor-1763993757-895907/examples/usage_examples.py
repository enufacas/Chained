"""
Usage Examples for Code Completion Predictor

Demonstrates all features and capabilities of the @create-botter code completion system.

Examples:
    1. Basic code completion
    2. Multi-language support
    3. Function completion
    4. Beam search (multiple predictions)
    5. Model persistence
    6. Real-world patterns
    7. Performance statistics
    8. TypeScript support
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.code_completion_predictor import (
    CodeCompletionPredictor,
    train_model
)


def example_1_basic_completion():
    """Example 1: Basic code completion."""
    print("=" * 70)
    print("Example 1: Basic Code Completion")
    print("=" * 70)
    
    # Train on simple patterns
    training_code = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b'
    ]
    
    model = train_model(training_code, language='python')
    
    # Predict next line
    context = 'def divide(a, b): '
    line, confidence = model.predict_next_line(context)
    
    print(f"Context:     {context}")
    print(f"Prediction:  {line}")
    print(f"Confidence:  {confidence:.1%}")
    print()


def example_2_multi_language():
    """Example 2: Multi-language support."""
    print("=" * 70)
    print("Example 2: Multi-Language Support")
    print("=" * 70)
    
    # Python
    py_model = CodeCompletionPredictor('python')
    py_model.train(['def validate(x): return x > 0'])
    line, conf = py_model.predict_next_line('def check(y): ')
    print(f"Python:      {line} ({conf:.1%})")
    
    # JavaScript
    js_model = CodeCompletionPredictor('javascript')
    js_model.train(['const add = (a, b) => a + b'])
    line, conf = js_model.predict_next_line('const sub = (a, b) => ')
    print(f"JavaScript:  {line} ({conf:.1%})")
    
    # Java
    java_model = CodeCompletionPredictor('java')
    java_model.train(['public int add(int a, int b) { return a + b; }'])
    line, conf = java_model.predict_next_line('public int sub(int a, int b) { ')
    print(f"Java:        {line} ({conf:.1%})")
    
    # Go
    go_model = CodeCompletionPredictor('go')
    go_model.train(['func add(a int, b int) int { return a + b }'])
    line, conf = go_model.predict_next_line('func sub(a int, b int) int { ')
    print(f"Go:          {line} ({conf:.1%})")
    print()


def example_3_function_completion():
    """Example 3: Complete function definitions."""
    print("=" * 70)
    print("Example 3: Function Completion")
    print("=" * 70)
    
    training_code = [
        'def validate_email(email):\n    if "@" not in email:\n        return False\n    return True',
        'def validate_phone(phone):\n    if len(phone) != 10:\n        return False\n    return True',
        'def validate_username(user):\n    if len(user) < 3:\n        return False\n    return True'
    ]
    
    model = train_model(training_code, 'python')
    
    # Complete partial function
    partial = 'def validate_password(pwd):\n    if len(pwd) < '
    completion, confidence = model.complete_function(partial)
    
    print("Partial function:")
    print(partial)
    print("\nCompletion:")
    print(completion)
    print(f"\nConfidence: {confidence:.1%}")
    print()


def example_4_beam_search():
    """Example 4: Beam search for multiple predictions."""
    print("=" * 70)
    print("Example 4: Beam Search (Multiple Predictions)")
    print("=" * 70)
    
    training_code = [
        'if status == 200: return True',
        'if status == 404: return None',
        'if status == 500: raise Exception("Error")',
        'if status == 201: return True',
        'if status == 403: return False'
    ]
    
    model = train_model(training_code, 'python')
    
    # Get top 5 predictions
    predictions = model.get_predictions('if status == ', top_k=5)
    
    print("Context: if status == ")
    print("\nTop predictions:")
    for i, (token, confidence) in enumerate(predictions, 1):
        print(f"  {i}. {token:10} ({confidence:.1%})")
    print()


def example_5_model_persistence():
    """Example 5: Save and load models."""
    print("=" * 70)
    print("Example 5: Model Persistence")
    print("=" * 70)
    
    # Train model
    training_code = [
        'def process(data): return data.strip().lower()',
        'def validate(data): return len(data) > 0'
    ]
    model = train_model(training_code, 'python')
    
    # Make prediction
    line1, conf1 = model.predict_next_line('def transform(text): ')
    print(f"Original prediction: {line1} ({conf1:.1%})")
    
    # Save model
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    model.save_model(temp_path)
    print(f"✓ Model saved to {temp_path}")
    
    # Load into new model
    model2 = CodeCompletionPredictor('python')
    model2.load_model(temp_path)
    print("✓ Model loaded")
    
    # Make same prediction
    line2, conf2 = model2.predict_next_line('def transform(text): ')
    print(f"Loaded prediction:   {line2} ({conf2:.1%})")
    
    # Cleanup
    os.unlink(temp_path)
    print()


def example_6_real_world_patterns():
    """Example 6: Real-world code patterns."""
    print("=" * 70)
    print("Example 6: Real-World Code Patterns")
    print("=" * 70)
    
    # Train on realistic Python patterns
    training_code = [
        'import os',
        'import sys',
        'import json',
        'from typing import List, Dict, Optional',
        'from collections import defaultdict',
        'class DataProcessor:\n    def __init__(self):\n        self.data = []',
        'class APIClient:\n    def __init__(self, url):\n        self.url = url',
        'try:\n    result = process_data()\nexcept Exception as e:\n    logger.error(f"Error: {e}")',
        'with open("file.txt", "r") as f:\n    content = f.read()'
    ]
    
    model = train_model(training_code, 'python', n=5)
    
    # Test various contexts
    contexts = [
        'import ',
        'from typing import ',
        'class UserManager:\n    def __init__(self):\n        ',
        'try:\n    data = fetch()\nexcept '
    ]
    
    for context in contexts:
        line, conf = model.predict_next_line(context)
        print(f"Context: {context[:40]}")
        print(f"Predict: {line} ({conf:.1%})")
        print()


def example_7_performance_stats():
    """Example 7: Performance statistics."""
    print("=" * 70)
    print("Example 7: Performance Statistics")
    print("=" * 70)
    
    training_code = [
        'def foo(): return 42',
        'def bar(): return 100',
        'def baz(): return 200',
        'class MyClass: pass',
        'if x > 0: return True'
    ] * 5  # Duplicate for more training data
    
    model = train_model(training_code, 'python', n=5)
    
    # Make some predictions to populate cache
    for i in range(10):
        model.predict_next_line(f'def test{i}(): ')
    
    # Get statistics
    stats = model.get_stats()
    
    print(f"Language:         {stats['language']}")
    print(f"Vocabulary size:  {stats['vocabulary_size']} tokens")
    print(f"Training samples: {stats['training_samples']}")
    print(f"N-gram order:     {stats['n']}")
    print(f"Cache size:       {stats['cache_size']} entries")
    print(f"Cache hit rate:   {stats['cache_hit_rate']:.1%}")
    print()
    
    print("N-gram counts by order:")
    for order, count in sorted(stats['ngram_counts'].items()):
        print(f"  Order {order}: {count} n-grams")
    print()


def example_8_typescript_support():
    """Example 8: TypeScript-specific features."""
    print("=" * 70)
    print("Example 8: TypeScript Support")
    print("=" * 70)
    
    training_code = [
        'interface User { name: string; age: number; }',
        'interface Product { id: number; price: number; }',
        'type Status = "active" | "inactive"',
        'const fetchUser = async (id: number): Promise<User> => { }',
        'class UserService implements IUserService { }'
    ]
    
    model = train_model(training_code, 'typescript', n=5)
    
    contexts = [
        'interface Customer { ',
        'type Role = ',
        'const saveData = async (data: any): Promise<'
    ]
    
    for context in contexts:
        line, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {line}")
        print(f"Confidence: {conf:.1%}")
        print()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Code Completion Predictor - Usage Examples by @create-botter")
    print("=" * 70)
    print("\n")
    
    examples = [
        example_1_basic_completion,
        example_2_multi_language,
        example_3_function_completion,
        example_4_beam_search,
        example_5_model_persistence,
        example_6_real_world_patterns,
        example_7_performance_stats,
        example_8_typescript_support
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()
        print()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == '__main__':
    main()
