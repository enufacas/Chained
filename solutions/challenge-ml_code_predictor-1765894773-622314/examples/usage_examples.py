"""
Usage Examples for Code Completion Predictor

Comprehensive examples demonstrating all features of the Code Completion
Predictor by @create-botter.

Challenge ID: challenge-ml_code_predictor-1765894773-622314
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.code_completion_predictor import (
    CodeCompletionPredictor,
    train_model
)


def example_1_basic_completion():
    """Example 1: Basic code completion"""
    print("=" * 70)
    print("Example 1: Basic Code Completion")
    print("=" * 70)
    
    # Create and train model
    training_code = [
        'def validate_email(email): return "@" in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def validate_username(user): return len(user) > 3'
    ]
    
    model = train_model(training_code, language='python')
    
    # Predict next line
    context = 'def validate_password(pwd): '
    line, confidence = model.predict_next_line(context)
    
    print(f"Training samples: {len(training_code)}")
    print(f"Context:    {context}")
    print(f"Prediction: {line}")
    print(f"Confidence: {confidence:.0%}")
    print()


def example_2_multi_language():
    """Example 2: Multi-language support"""
    print("=" * 70)
    print("Example 2: Multi-Language Support")
    print("=" * 70)
    
    # Python
    python_code = ['def add(a, b): return a + b']
    python_model = train_model(python_code, 'python')
    line, conf = python_model.predict_next_line('def sub(a, b): ')
    print(f"Python:     {line} (confidence: {conf:.0%})")
    
    # JavaScript
    js_code = ['const add = (a, b) => a + b']
    js_model = train_model(js_code, 'javascript')
    line, conf = js_model.predict_next_line('const sub = (a, b) => ')
    print(f"JavaScript: {line} (confidence: {conf:.0%})")
    
    # TypeScript
    ts_code = ['function add(a: number, b: number): number { return a + b; }']
    ts_model = train_model(ts_code, 'typescript')
    line, conf = ts_model.predict_next_line('function sub(a: number, b: number): number { ')
    print(f"TypeScript: {line} (confidence: {conf:.0%})")
    
    # Java
    java_code = ['public int add(int a, int b) { return a + b; }']
    java_model = train_model(java_code, 'java')
    line, conf = java_model.predict_next_line('public int sub(int a, int b) { ')
    print(f"Java:       {line} (confidence: {conf:.0%})")
    
    # Go
    go_code = ['func add(a int, b int) int { return a + b }']
    go_model = train_model(go_code, 'go')
    line, conf = go_model.predict_next_line('func sub(a int, b int) int { ')
    print(f"Go:         {line} (confidence: {conf:.0%})")
    print()


def example_3_function_completion():
    """Example 3: Function completion"""
    print("=" * 70)
    print("Example 3: Function Completion")
    print("=" * 70)
    
    training_code = [
        'def process_data(data): if data: return data.strip()',
        'def clean_text(text): if text: return text.lower()',
        'def format_name(name): if name: return name.title()'
    ]
    
    model = train_model(training_code, 'python')
    
    partial_functions = [
        'def validate_input(value):\n    if value:\n        ',
        'def check_status(status):\n    if status:\n        '
    ]
    
    for partial in partial_functions:
        completion, conf = model.complete_function(partial)
        print(f"Partial:    {partial.split(chr(10))[-1].strip()}")
        print(f"Completion: {completion} (confidence: {conf:.0%})")
        print()


def example_4_beam_search():
    """Example 4: Beam search (multiple predictions)"""
    print("=" * 70)
    print("Example 4: Beam Search - Top-K Predictions")
    print("=" * 70)
    
    training_code = [
        'if status == 200: return "OK"',
        'if status == 404: return "Not Found"',
        'if status == 500: return "Error"',
        'if status == 401: return "Unauthorized"',
    ]
    
    model = train_model(training_code, 'python')
    
    # Get top 5 predictions
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"Context: {context}")
    print("Top predictions:")
    for i, (token, conf) in enumerate(predictions, 1):
        print(f"  {i}. {token:15} ({conf:.0%})")
    print()


def example_5_model_persistence():
    """Example 5: Save and load model"""
    print("=" * 70)
    print("Example 5: Model Persistence")
    print("=" * 70)
    
    import tempfile
    import os
    
    # Train model
    training_code = [
        'def foo(): return 42',
        'def bar(): return 100'
    ]
    model = train_model(training_code, 'python')
    
    # Save model
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        filepath = f.name
    
    model.save_model(filepath)
    print(f"✓ Model saved to: {filepath}")
    
    # Load into new model
    new_model = CodeCompletionPredictor('python')
    new_model.load_model(filepath)
    print(f"✓ Model loaded from: {filepath}")
    
    # Verify it works
    line, conf = new_model.predict_next_line('def baz(): ')
    print(f"✓ Prediction works: {line} (confidence: {conf:.0%})")
    
    # Cleanup
    os.unlink(filepath)
    print()


def example_6_real_world_patterns():
    """Example 6: Real-world code patterns"""
    print("=" * 70)
    print("Example 6: Real-World Code Patterns")
    print("=" * 70)
    
    # Train on common patterns
    training_code = [
        'try: result = process(data)',
        'try: output = transform(input)',
        'try: value = compute(x)',
        'except Exception as e: print(e)',
        'except ValueError as e: print(e)',
        'except KeyError as e: print(e)',
    ]
    
    model = train_model(training_code, 'python')
    
    # Test predictions
    test_cases = [
        ('try: ', 'Try block'),
        ('except ', 'Except clause'),
        ('except Exception as e: ', 'Exception handling')
    ]
    
    for context, description in test_cases:
        line, conf = model.predict_next_line(context)
        print(f"{description:20} | Context: {context:30} | Prediction: {line} ({conf:.0%})")
    print()


def example_7_performance_stats():
    """Example 7: Performance statistics"""
    print("=" * 70)
    print("Example 7: Performance Statistics")
    print("=" * 70)
    
    import time
    
    # Train on larger dataset
    training_code = []
    for i in range(100):
        training_code.append(f'def function_{i}(x): return x * {i}')
    
    model = train_model(training_code, 'python')
    
    # Measure cold prediction
    start = time.time()
    model.predict_next_line('def unique_function(y): ')
    cold_time = (time.time() - start) * 1000
    
    # Measure cached prediction
    start = time.time()
    for _ in range(100):
        model.predict_next_line('def test(): ')
    cached_time = ((time.time() - start) / 100) * 1000
    
    # Get statistics
    stats = model.get_stats()
    
    print(f"Training samples:   {len(training_code)}")
    print(f"Vocabulary size:    {stats['vocabulary_size']}")
    print(f"N-gram order:       {stats['n']}")
    print(f"Cache size:         {stats['cache_size']}")
    print(f"Cold prediction:    {cold_time:.2f}ms")
    print(f"Cached prediction:  {cached_time:.2f}ms")
    print(f"Speedup factor:     {cold_time/cached_time:.1f}x")
    print()


def example_8_advanced_typescript():
    """Example 8: Advanced TypeScript patterns"""
    print("=" * 70)
    print("Example 8: Advanced TypeScript Patterns")
    print("=" * 70)
    
    training_code = [
        'interface User { id: number; name: string; }',
        'interface Product { id: number; price: number; }',
        'type Result<T> = { data: T; error: null; } | { data: null; error: string; }',
        'const fetchUser = async (id: number): Promise<User> => { return await api.get(id); }',
    ]
    
    model = train_model(training_code, 'typescript')
    
    test_cases = [
        'interface Post { ',
        'type Response<T> = ',
        'const getProduct = async (id: number): '
    ]
    
    for context in test_cases:
        line, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {line} (confidence: {conf:.0%})")
        print()


def run_all_examples():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Code Completion Predictor - Usage Examples".center(68) + "║")
    print("║" + "  by @create-botter".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("║" + "  Challenge ID: challenge-ml_code_predictor-1765894773-622314".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print("\n")
    
    examples = [
        example_1_basic_completion,
        example_2_multi_language,
        example_3_function_completion,
        example_4_beam_search,
        example_5_model_persistence,
        example_6_real_world_patterns,
        example_7_performance_stats,
        example_8_advanced_typescript
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"❌ Error in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 70)
    print("✅ All examples completed!")
    print("=" * 70)
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Basic code completion")
    print("  ✓ Multi-language support (Python, JS, TS, Java, Go)")
    print("  ✓ Function completion")
    print("  ✓ Beam search (top-k predictions)")
    print("  ✓ Model persistence (save/load)")
    print("  ✓ Real-world patterns")
    print("  ✓ Performance optimization")
    print("  ✓ Advanced language features")
    print()


if __name__ == '__main__':
    run_all_examples()
