"""
Usage Examples for Code Completion Predictor by @create-botter

Challenge ID: challenge-ml_code_predictor-1766412996-552560

Demonstrates various features and use cases.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from code_completion_predictor import CodeCompletionPredictor, train_model


def example_1_basic_completion():
    """Example 1: Basic code completion."""
    print("=" * 70)
    print("Example 1: Basic Code Completion")
    print("=" * 70)
    
    training_code = [
        'def add(a, b): return a + b',
        'def sub(a, b): return a - b',
        'def mul(a, b): return a * b',
    ]
    
    model = train_model(training_code, 'python')
    
    context = 'def div(a, b): '
    line, confidence = model.predict_next_line(context)
    
    print(f"Context:    {context}")
    print(f"Prediction: {line}")
    print(f"Confidence: {confidence:.0%}")
    print()


def example_2_multi_language():
    """Example 2: Multi-language support."""
    print("=" * 70)
    print("Example 2: Multi-Language Support")
    print("=" * 70)
    
    # Python
    py_model = train_model(['def foo(): return 42'], 'python')
    line, conf = py_model.predict_next_line('def bar(): ')
    print(f"Python:     {line} ({conf:.0%})")
    
    # JavaScript
    js_code = ['const add = (a, b) => a + b']
    js_model = train_model(js_code, 'javascript')
    line, conf = js_model.predict_next_line('const mul = (x, y) => ')
    print(f"JavaScript: {line} ({conf:.0%})")
    
    # TypeScript
    ts_code = ['function greet(name: string): string { return "Hello"; }']
    ts_model = train_model(ts_code, 'typescript')
    line, conf = ts_model.predict_next_line('function farewell(name: string): ')
    print(f"TypeScript: {line} ({conf:.0%})")
    print()


def example_3_function_completion():
    """Example 3: Complete function definitions."""
    print("=" * 70)
    print("Example 3: Function Completion")
    print("=" * 70)
    
    training_code = [
        'def validate_email(email):\n    if "@" in email:\n        return True\n    return False',
        'def validate_phone(phone):\n    if len(phone) == 10:\n        return True\n    return False',
    ]
    
    model = train_model(training_code, 'python')
    
    partial = 'def validate_username(user):\n    if '
    completion, confidence = model.complete_function(partial)
    
    print(f"Partial function:")
    print(partial)
    print(f"\nPredicted completion: {completion}")
    print(f"Confidence: {confidence:.0%}")
    print()


def example_4_beam_search():
    """Example 4: Get multiple predictions (beam search)."""
    print("=" * 70)
    print("Example 4: Beam Search - Multiple Predictions")
    print("=" * 70)
    
    training_code = [
        'if status == 200: print("OK")',
        'if status == 404: print("Not Found")',
        'if status == 500: print("Error")',
        'if code == 200: print("Success")',
    ]
    
    model = train_model(training_code, 'python')
    
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=3)
    
    print(f"Context: {context}")
    print("Top predictions:")
    for i, (token, conf) in enumerate(predictions, 1):
        print(f"  {i}. {token:10} ({conf:.0%})")
    print()


def example_5_model_persistence():
    """Example 5: Save and load trained models."""
    print("=" * 70)
    print("Example 5: Model Persistence")
    print("=" * 70)
    
    import tempfile
    import os
    
    training_code = [
        'def process(x): return x * 2',
        'def transform(y): return str(y)',
    ]
    
    model = train_model(training_code, 'python')
    
    # Save model
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        path = f.name
    
    try:
        model.save_model(path)
        print(f"✓ Model saved to: {path}")
        
        # Load into new model
        new_model = CodeCompletionPredictor('python')
        new_model.load_model(path)
        print(f"✓ Model loaded from disk")
        
        # Test prediction
        line, conf = new_model.predict_next_line('def compute(a): ')
        print(f"  Prediction: {line} ({conf:.0%})")
    
    finally:
        if os.path.exists(path):
            os.unlink(path)
    
    print()


def example_6_real_world_patterns():
    """Example 6: Learning real-world code patterns."""
    print("=" * 70)
    print("Example 6: Real-World Code Patterns")
    print("=" * 70)
    
    training_code = [
        'try:\n    result = process_data(input)\nexcept Exception as e:\n    log_error(e)',
        'try:\n    output = transform(value)\nexcept ValueError as e:\n    handle_error(e)',
        'try:\n    data = fetch_remote()\nexcept ConnectionError as e:\n    retry_connection()',
    ]
    
    model = train_model(training_code, 'python')
    
    context = 'try:\n    response = '
    line, conf = model.predict_next_line(context)
    
    print("Learned pattern: try-except blocks")
    print(f"Context: {context}")
    print(f"Next token: {line} ({conf:.0%})")
    print()


def example_7_statistics():
    """Example 7: Model statistics and metrics."""
    print("=" * 70)
    print("Example 7: Model Statistics")
    print("=" * 70)
    
    training_code = [
        'def foo(): return 42',
        'def bar(): return 100',
        'class MyClass: pass',
        'for i in range(10): print(i)',
    ]
    
    model = train_model(training_code, 'python', n=4)
    stats = model.get_stats()
    
    print(f"Challenge ID:    {stats['challenge_id']}")
    print(f"Language:        {stats['language']}")
    print(f"N-gram order:    {stats['n']}")
    print(f"Vocabulary size: {stats['vocabulary_size']} tokens")
    print(f"N-gram counts:   {stats['ngram_counts']}")
    print()


def example_8_advanced_typescript():
    """Example 8: Advanced TypeScript patterns."""
    print("=" * 70)
    print("Example 8: Advanced TypeScript")
    print("=" * 70)
    
    training_code = [
        'interface User { name: string; age: number; }',
        'interface Product { id: string; price: number; }',
        'type Result<T> = { data: T; error: null } | { data: null; error: string }',
    ]
    
    model = train_model(training_code, 'typescript')
    
    context = 'interface Customer { '
    predictions = model.get_predictions(context, top_k=3)
    
    print("TypeScript interface completion:")
    print(f"Context: {context}")
    print("Predictions:")
    for token, conf in predictions:
        print(f"  {token:15} ({conf:.0%})")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("*" * 70)
    print("Code Completion Predictor - Usage Examples by @create-botter")
    print("Challenge ID: challenge-ml_code_predictor-1766412996-552560")
    print("*" * 70)
    print("\n")
    
    examples = [
        example_1_basic_completion,
        example_2_multi_language,
        example_3_function_completion,
        example_4_beam_search,
        example_5_model_persistence,
        example_6_real_world_patterns,
        example_7_statistics,
        example_8_advanced_typescript,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            print()
    
    print("*" * 70)
    print("All examples completed!")
    print("*" * 70)


if __name__ == '__main__':
    main()
