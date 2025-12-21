"""
Usage Examples for Code Completion Predictor by @create-botter

Demonstrates various features and use cases of the code completion system.
Challenge ID: challenge-ml_code_predictor-1766326453-402640
"""

import sys
from pathlib import Path

# Add parent directory for imports
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
    
    training_code = [
        'def add(a, b): return a + b',
        'def multiply(a, b): return a * b',
        'def divide(a, b): return a / b'
    ]
    
    model = train_model(training_code, language='python')
    
    context = 'def subtract(a, b): '
    line, confidence = model.predict_next_line(context)
    
    print(f"Training samples: {len(training_code)}")
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
    py_model = train_model(['def foo(): return 42'], 'python')
    py_pred, py_conf = py_model.predict_next_line('def bar(): ')
    print(f"Python:     {py_pred:30} ({py_conf:.0%})")
    
    # JavaScript
    js_model = train_model(['const add = (a, b) => a + b'], 'javascript')
    js_pred, js_conf = js_model.predict_next_line('const sub = (a, b) => ')
    print(f"JavaScript: {js_pred:30} ({js_conf:.0%})")
    
    # TypeScript
    ts_model = train_model(['interface User { name: string }'], 'typescript')
    ts_pred, ts_conf = ts_model.predict_next_line('interface Admin { ')
    print(f"TypeScript: {ts_pred:30} ({ts_conf:.0%})")
    
    # Java
    java_model = train_model(['public int add(int a, int b) { return a + b; }'], 'java')
    java_pred, java_conf = java_model.predict_next_line('public int sub(int a, int b) { ')
    print(f"Java:       {java_pred:30} ({java_conf:.0%})")
    
    # Go
    go_model = train_model(['func Add(a, b int) int { return a + b }'], 'go')
    go_pred, go_conf = go_model.predict_next_line('func Sub(a, b int) int { ')
    print(f"Go:         {go_pred:30} ({go_conf:.0%})")
    print()


def example_3_function_completion():
    """Example 3: Function completion"""
    print("=" * 70)
    print("Example 3: Function Completion")
    print("=" * 70)
    
    training_code = [
        'def validate_email(email):\n    return "@" in email',
        'def validate_phone(phone):\n    return len(phone) == 10',
        'def validate_url(url):\n    return url.startswith("http")'
    ]
    
    model = train_model(training_code, 'python')
    
    partial = 'def validate_username(user):\n    '
    completion, confidence = model.complete_function(partial)
    
    print("Partial function:")
    print(partial)
    print("\nPredicted completion:")
    print(completion)
    print(f"\nConfidence: {confidence:.1%}")
    print()


def example_4_beam_search():
    """Example 4: Beam search (multiple predictions)"""
    print("=" * 70)
    print("Example 4: Beam Search - Multiple Predictions")
    print("=" * 70)
    
    training_code = [
        'if status == 200: handle_success()',
        'if status == 404: handle_not_found()',
        'if status == 500: handle_server_error()',
        'if status == 401: handle_unauthorized()',
        'if status == 403: handle_forbidden()'
    ]
    
    model = train_model(training_code, 'python')
    
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"Context: {context}")
    print("\nTop predictions:")
    for i, (pred, conf) in enumerate(predictions, 1):
        print(f"  {i}. {pred:15} ({conf:.1%})")
    print()


def example_5_model_persistence():
    """Example 5: Save and load models"""
    print("=" * 70)
    print("Example 5: Model Persistence")
    print("=" * 70)
    
    # Train model
    training_code = [
        'def process_data(data): return data.strip().lower()',
        'def validate_input(input): return len(input) > 0'
    ]
    
    model = train_model(training_code, 'python')
    
    # Save
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
        model_path = f.name
    
    try:
        model.save_model(model_path)
        print(f"✓ Model saved to: {model_path}")
        print(f"  File size: {os.path.getsize(model_path)} bytes")
        
        # Load into new model
        new_model = CodeCompletionPredictor('python')
        new_model.load_model(model_path)
        print("✓ Model loaded successfully")
        
        # Verify it works
        line, conf = new_model.predict_next_line('def transform_text(text): ')
        print(f"\nPrediction from loaded model: {line}")
        print(f"Confidence: {conf:.1%}")
    finally:
        os.unlink(model_path)
    
    print()


def example_6_real_world_patterns():
    """Example 6: Learning real-world patterns"""
    print("=" * 70)
    print("Example 6: Real-World Code Patterns")
    print("=" * 70)
    
    # Realistic training data
    training_code = [
        'try:\n    result = process(data)\nexcept Exception as e:\n    log_error(e)',
        'try:\n    value = parse(input)\nexcept ValueError as e:\n    handle_error(e)',
        'try:\n    output = transform(raw)\nexcept TypeError as e:\n    return None'
    ]
    
    model = train_model(training_code, 'python', n=5)
    
    # Test pattern recognition
    test_cases = [
        'try:\n    result = ',
        'except Exception as e:\n    ',
        'except ValueError'
    ]
    
    for context in test_cases:
        line, conf = model.predict_next_line(context)
        print(f"Context: {repr(context[:30])}")
        print(f"Prediction: {line}")
        print(f"Confidence: {conf:.1%}")
        print()


def example_7_statistics():
    """Example 7: Model statistics"""
    print("=" * 70)
    print("Example 7: Model Statistics and Metrics")
    print("=" * 70)
    
    training_code = [
        f'def function_{i}(x): return x * {i}'
        for i in range(20)
    ]
    
    model = train_model(training_code, 'python', n=5)
    
    stats = model.get_stats()
    
    print(f"Challenge ID: {stats['challenge_id']}")
    print(f"Language: {stats['language']}")
    print(f"N-gram order: {stats['n']}")
    print(f"Vocabulary size: {stats['vocabulary_size']} tokens")
    print(f"N-gram orders trained: {list(stats['ngram_counts'].keys())}")
    print(f"Total N-grams: {sum(stats['ngram_counts'].values())}")
    print()
    
    # Show N-gram distribution
    print("N-gram distribution:")
    for order, count in sorted(stats['ngram_counts'].items()):
        bar = '█' * (count // 10)
        print(f"  Order {order}: {count:4} {bar}")
    print()


def example_8_advanced_typescript():
    """Example 8: Advanced TypeScript patterns"""
    print("=" * 70)
    print("Example 8: Advanced TypeScript Patterns")
    print("=" * 70)
    
    training_code = [
        'interface User { id: number; name: string; email: string; }',
        'interface Product { id: number; title: string; price: number; }',
        'interface Order { id: number; userId: number; total: number; }',
        'type ApiResponse<T> = { data: T; status: number; }',
        'type Result<T, E> = { ok: true; value: T } | { ok: false; error: E }'
    ]
    
    model = train_model(training_code, 'typescript', n=5)
    
    test_contexts = [
        'interface Admin { id: number; ',
        'type UserResult = ',
        'interface Payment { '
    ]
    
    for context in test_contexts:
        line, conf = model.predict_next_line(context)
        print(f"Context: {context}")
        print(f"Prediction: {line}")
        print(f"Confidence: {conf:.1%}")
        print()


def run_all_examples():
    """Run all usage examples"""
    print("\n")
    print("*" * 70)
    print("* Code Completion Predictor - Usage Examples by @create-botter")
    print("* Challenge ID: challenge-ml_code_predictor-1766326453-402640")
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
        example_8_advanced_typescript
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"❌ Example {i} failed: {e}")
            print()
    
    print("*" * 70)
    print("* All examples completed!")
    print("* Run tests/test_code_completion_predictor.py for full validation")
    print("*" * 70)
    print()


if __name__ == '__main__':
    run_all_examples()
