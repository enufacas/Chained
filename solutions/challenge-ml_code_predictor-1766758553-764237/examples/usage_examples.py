"""
Usage Examples for Code Completion Predictor

Comprehensive examples demonstrating all features by @create-botter.
Challenge ID: challenge-ml_code_predictor-1766758553-764237
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.code_completion_predictor import (
    CodeCompletionPredictor,
    CodeTokenizer,
    train_model
)


def example_1_basic_completion():
    """Example 1: Basic code completion"""
    print("\n" + "=" * 70)
    print("Example 1: Basic Code Completion")
    print("=" * 70)
    
    # Training data
    training_code = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b',
    ]
    
    # Train model
    model = train_model(training_code, language='python')
    
    # Predict next line
    context = 'def divide(a, b): '
    line, confidence = model.predict_next_line(context)
    
    print(f"Context:    {context}")
    print(f"Prediction: {line}")
    print(f"Confidence: {confidence:.0%}")


def example_2_multi_language():
    """Example 2: Multi-language support"""
    print("\n" + "=" * 70)
    print("Example 2: Multi-Language Support")
    print("=" * 70)
    
    examples = [
        ('python', ['def foo(): return 42'], 'def bar(): '),
        ('javascript', ['const add = (a, b) => a + b'], 'const sub = (a, b) => '),
        ('java', ['public int add(int a, int b) { return a + b; }'], 'public int sub(int a, int b) { '),
    ]
    
    for lang, training, context in examples:
        model = CodeCompletionPredictor(lang)
        model.train(training)
        line, conf = model.predict_next_line(context)
        
        print(f"\n{lang.upper()}:")
        print(f"  Context:    {context}")
        print(f"  Prediction: {line} ({conf:.0%})")


def example_3_function_completion():
    """Example 3: Function completion"""
    print("\n" + "=" * 70)
    print("Example 3: Function Completion")
    print("=" * 70)
    
    training_code = [
        'def validate_email(email): return "@" in email and "." in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def validate_username(user): return len(user) >= 3',
    ]
    
    model = train_model(training_code, language='python')
    
    partial = 'def validate_password(pwd):\n    '
    completion, confidence = model.complete_function(partial)
    
    print("Partial function:")
    print(partial)
    print(f"\nCompletion: {completion}")
    print(f"Confidence: {confidence:.0%}")


def example_4_beam_search():
    """Example 4: Beam search (multiple predictions)"""
    print("\n" + "=" * 70)
    print("Example 4: Beam Search - Multiple Predictions")
    print("=" * 70)
    
    training_code = [
        'if status == 200: return success',
        'if status == 404: return not_found',
        'if status == 500: return error',
        'if status == 201: return created',
    ]
    
    model = train_model(training_code, language='python')
    
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"Context: {context}")
    print("\nTop predictions:")
    for i, (token, conf) in enumerate(predictions, 1):
        print(f"  {i}. {token:15} ({conf:.0%})")


def example_5_model_persistence():
    """Example 5: Save and load model"""
    print("\n" + "=" * 70)
    print("Example 5: Model Persistence (Save/Load)")
    print("=" * 70)
    
    import tempfile
    import os
    
    # Train original model
    training_code = [
        'def foo(): return 42',
        'def bar(): return 100',
    ]
    
    original_model = train_model(training_code, language='python')
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        model_path = f.name
    
    try:
        print("Training original model...")
        original_model.save_model(model_path)
        print(f"✅ Model saved to: {model_path}")
        
        # Load in new model
        print("\nLoading model in new instance...")
        loaded_model = CodeCompletionPredictor('python')
        loaded_model.load_model(model_path)
        print("✅ Model loaded successfully")
        
        # Verify same predictions
        context = 'def baz(): '
        line1, conf1 = original_model.predict_next_line(context)
        line2, conf2 = loaded_model.predict_next_line(context)
        
        print(f"\nOriginal: {line1} ({conf1:.0%})")
        print(f"Loaded:   {line2} ({conf2:.0%})")
        print("✅ Predictions match!" if line1 == line2 else "❌ Mismatch")
    finally:
        os.unlink(model_path)


def example_6_real_world_patterns():
    """Example 6: Real-world code patterns"""
    print("\n" + "=" * 70)
    print("Example 6: Real-World Code Patterns")
    print("=" * 70)
    
    # Real-world training data
    training_code = [
        'try: result = process_data(input)',
        'except ValueError: logger.error("Invalid value")',
        'except KeyError: logger.error("Missing key")',
        'except Exception: logger.error("Unknown error")',
        'for item in items: total += item.price',
        'for user in users: send_notification(user)',
        'if user.is_authenticated: return redirect("/dashboard")',
        'if user.is_admin: return render_template("admin.html")',
    ]
    
    model = train_model(training_code, language='python')
    
    test_cases = [
        'try: data = fetch_from_api()',
        'for product in products: ',
        'if user.has_permission: ',
    ]
    
    print("Training on real-world patterns...")
    print(f"Trained on {len(training_code)} code samples\n")
    
    for context in test_cases:
        line, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {line} ({conf:.0%})")
        print()


def example_7_performance_stats():
    """Example 7: Performance and statistics"""
    print("\n" + "=" * 70)
    print("Example 7: Performance Statistics")
    print("=" * 70)
    
    import time
    
    # Train with varied data
    training_code = [
        'def validate_email(email): return "@" in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def validate_username(user): return len(user) >= 3',
        'def process_data(data): return data.strip().lower()',
        'if status == 200: return success',
        'if status == 404: return error',
        'for item in items: total += item.value',
        'while counter < max_value: counter += 1',
    ]
    
    model = train_model(training_code, language='python')
    
    # Get stats
    stats = model.get_stats()
    print("Model Statistics:")
    print(f"  Challenge ID:    {stats['challenge_id']}")
    print(f"  Language:        {stats['language']}")
    print(f"  N-gram order:    {stats['n']}")
    print(f"  Vocabulary size: {stats['vocabulary_size']} tokens")
    print(f"  Cache size:      {stats['cache_size']} entries")
    print(f"  Cache hit rate:  {stats['cache_hit_rate']:.0%}")
    
    # Measure prediction speed
    context = 'def test(): '
    iterations = 100
    
    # Cold predictions
    start = time.time()
    for i in range(iterations):
        model.predict_next_line(f'def test{i}(): ')
    cold_time = time.time() - start
    
    # Cached predictions
    start = time.time()
    for _ in range(iterations):
        model.predict_next_line(context)
    cached_time = time.time() - start
    
    print(f"\nPerformance Metrics ({iterations} predictions):")
    print(f"  Cold predictions:   {(cold_time / iterations) * 1000:.2f}ms avg")
    print(f"  Cached predictions: {(cached_time / iterations) * 1000:.2f}ms avg")


def example_8_typescript_advanced():
    """Example 8: TypeScript with advanced features"""
    print("\n" + "=" * 70)
    print("Example 8: TypeScript Advanced Features")
    print("=" * 70)
    
    training_code = [
        'interface User { name: string; email: string }',
        'interface Product { id: number; price: number }',
        'type AsyncResult = Promise<Response>',
        'type ErrorHandler = (error: Error) => void',
        'const fetchUser = async (): AsyncResult => { }',
        'const handleError: ErrorHandler = (error) => { }',
    ]
    
    model = train_model(training_code, language='typescript')
    
    test_contexts = [
        'interface Admin { ',
        'type UserCallback = ',
        'const loadData = async (): ',
    ]
    
    print("Training on TypeScript patterns...\n")
    
    for context in test_contexts:
        line, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {line} ({conf:.0%})")
        print()


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("Code Completion Predictor - Usage Examples")
    print("By @create-botter")
    print("Challenge ID: challenge-ml_code_predictor-1766758553-764237")
    print("=" * 70)
    
    examples = [
        example_1_basic_completion,
        example_2_multi_language,
        example_3_function_completion,
        example_4_beam_search,
        example_5_model_persistence,
        example_6_real_world_patterns,
        example_7_performance_stats,
        example_8_typescript_advanced,
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Example {i} failed: {e}")
    
    print("\n" + "=" * 70)
    print("All examples completed! ✨")
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()
