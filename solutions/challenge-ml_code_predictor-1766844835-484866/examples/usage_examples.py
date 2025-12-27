"""
Usage Examples for Code Completion Predictor

Demonstrations of the Code Completion Predictor by @create-botter.
Challenge ID: challenge-ml_code_predictor-1766844835-484866

Shows 8 different use cases for the predictor.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.code_completion_predictor import train_model, CodeCompletionPredictor


def example_1_basic_completion():
    """Example 1: Basic code completion"""
    print("=" * 70)
    print("Example 1: Basic Code Completion")
    print("=" * 70)
    
    training_data = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b',
    ]
    
    model = train_model(training_data, language='python', n=5)
    
    context = 'def divide(a, b): '
    line, confidence = model.predict_next_line(context)
    
    print(f"Training data: {len(training_data)} samples")
    print(f"Context: {context}")
    print(f"Prediction: {line}")
    print(f"Confidence: {confidence:.1%}")
    print()


def example_2_multi_language():
    """Example 2: Multi-language support"""
    print("=" * 70)
    print("Example 2: Multi-Language Support")
    print("=" * 70)
    
    # Python
    py_model = train_model(['def greet(): return "Hello"'], 'python')
    line, conf = py_model.predict_next_line('def bye(): ')
    print(f"Python: {line} ({conf:.0%})")
    
    # JavaScript
    js_model = train_model(['const add = (a, b) => a + b'], 'javascript')
    line, conf = js_model.predict_next_line('const sub = (a, b) => ')
    print(f"JavaScript: {line} ({conf:.0%})")
    
    # TypeScript
    ts_model = train_model(['function add(a: number, b: number): number { return a + b; }'], 'typescript')
    line, conf = ts_model.predict_next_line('function sub(a: number, b: number): number { ')
    print(f"TypeScript: {line} ({conf:.0%})")
    
    # Java
    java_model = train_model(['public int add(int a, int b) { return a + b; }'], 'java')
    line, conf = java_model.predict_next_line('public int sub(int a, int b) { ')
    print(f"Java: {line} ({conf:.0%})")
    
    # Go
    go_model = train_model(['func add(a int, b int) int { return a + b }'], 'go')
    line, conf = go_model.predict_next_line('func sub(a int, b int) int { ')
    print(f"Go: {line} ({conf:.0%})")
    print()


def example_3_function_completion():
    """Example 3: Function completion"""
    print("=" * 70)
    print("Example 3: Function Completion")
    print("=" * 70)
    
    training_data = [
        'def validate_email(email):\n    if "@" in email:\n        return True\n    return False',
        'def validate_phone(phone):\n    if len(phone) == 10:\n        return True\n    return False',
    ]
    
    model = train_model(training_data, 'python')
    
    partial = 'def validate_url(url):\n    if '
    completion, confidence = model.complete_function(partial)
    
    print("Training on validation functions...")
    print(f"Partial function:\n{partial}")
    print(f"Completion: {completion}")
    print(f"Confidence: {confidence:.1%}")
    print()


def example_4_beam_search():
    """Example 4: Beam search (multiple predictions)"""
    print("=" * 70)
    print("Example 4: Beam Search (Multiple Predictions)")
    print("=" * 70)
    
    training_data = [
        'if status == 200: print("OK")',
        'if status == 404: print("Not Found")',
        'if status == 500: print("Error")',
        'if status == 201: print("Created")',
    ]
    
    model = train_model(training_data, 'python')
    
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"Context: {context}")
    print(f"Top {len(predictions)} predictions:")
    for i, (token, conf) in enumerate(predictions, 1):
        print(f"  {i}. {token:15} ({conf:.1%})")
    print()


def example_5_model_persistence():
    """Example 5: Save and load model"""
    print("=" * 70)
    print("Example 5: Model Persistence")
    print("=" * 70)
    
    import tempfile
    import os
    
    # Train model
    training_data = [
        'def process(x): return x * 2',
        'def transform(x): return x + 1',
    ]
    model = train_model(training_data, 'python')
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        filepath = f.name
    
    try:
        model.save_model(filepath)
        print(f"✓ Model saved to {filepath}")
        
        # Load into new model
        new_model = CodeCompletionPredictor('python')
        new_model.load_model(filepath)
        print(f"✓ Model loaded from {filepath}")
        
        # Test prediction
        line, conf = new_model.predict_next_line('def compute(x): ')
        print(f"Prediction: {line} ({conf:.1%})")
    finally:
        os.unlink(filepath)
    print()


def example_6_real_world_patterns():
    """Example 6: Real-world code patterns"""
    print("=" * 70)
    print("Example 6: Real-World Code Patterns")
    print("=" * 70)
    
    # Train on realistic Python patterns
    training_data = [
        'try:\n    data = load_file(path)\nexcept FileNotFoundError:\n    return None',
        'try:\n    result = process_data(data)\nexcept ValueError:\n    return None',
        'try:\n    output = transform(input)\nexcept TypeError:\n    return None',
    ]
    
    model = train_model(training_data, 'python')
    
    # Predict error handling
    context = 'try:\n    user = get_user(id)\nexcept '
    line, conf = model.predict_next_line(context)
    
    print("Trained on try-except patterns...")
    print(f"Context: {context}")
    print(f"Prediction: {line}")
    print(f"Confidence: {conf:.1%}")
    print()


def example_7_statistics():
    """Example 7: Model statistics"""
    print("=" * 70)
    print("Example 7: Model Statistics")
    print("=" * 70)
    
    training_data = [
        'def foo(): return 1',
        'def bar(): return 2',
        'def baz(): return 3',
    ] * 3  # Repeat for cache testing
    
    model = train_model(training_data, 'python')
    
    # Make predictions to populate cache
    for i in range(5):
        model.predict_next_line('def test(): ')
    
    stats = model.get_stats()
    
    print("Model Statistics:")
    print(f"  Challenge ID: {stats['challenge_id']}")
    print(f"  Language: {stats['language']}")
    print(f"  N-gram order: {stats['n']}")
    print(f"  Vocabulary size: {stats['vocabulary_size']} tokens")
    print(f"  Cache hit rate: {stats['cache_hit_rate']:.1%}")
    print(f"  Cache size: {stats['cache_size']} entries")
    print(f"  N-gram counts: {stats['ngram_counts']}")
    print()


def example_8_typescript_advanced():
    """Example 8: TypeScript advanced patterns"""
    print("=" * 70)
    print("Example 8: TypeScript Advanced Patterns")
    print("=" * 70)
    
    training_data = [
        'interface User { id: number; name: string; }',
        'interface Product { id: number; price: number; }',
        'interface Order { id: number; total: number; }',
    ]
    
    model = train_model(training_data, 'typescript')
    
    # Predict interface definition
    context = 'interface Customer { id: number; '
    line, conf = model.predict_next_line(context)
    
    print("TypeScript interface definitions...")
    print(f"Context: {context}")
    print(f"Prediction: {line}")
    print(f"Confidence: {conf:.1%}")
    print()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 12 + "Code Completion Predictor by @create-botter" + " " * 13 + "║")
    print("║" + " " * 10 + "Challenge ID: challenge-ml_code_predictor-1766844835-484866" + " " * 0 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    examples = [
        example_1_basic_completion,
        example_2_multi_language,
        example_3_function_completion,
        example_4_beam_search,
        example_5_model_persistence,
        example_6_real_world_patterns,
        example_7_statistics,
        example_8_typescript_advanced,
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"❌ Error in {example_func.__name__}: {e}")
            print()
    
    print("=" * 70)
    print("✨ All examples complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
