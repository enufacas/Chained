"""
Usage Examples for Code Completion Predictor

8 comprehensive examples demonstrating the Code Completion Predictor by @create-botter.
Challenge ID: challenge-ml_code_predictor-1766240020-319351

Examples:
    1. Basic code completion
    2. Multi-language support
    3. Function completion
    4. Beam search
    5. Model persistence
    6. Real-world patterns
    7. Performance statistics
    8. TypeScript advanced
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
    
    # Train on simple patterns
    training_data = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b',
    ]
    
    model = train_model(training_data, 'python')
    
    # Predict next line
    context = 'def divide(a, b): '
    line, confidence = model.predict_next_line(context)
    
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
    py_model = CodeCompletionPredictor('python')
    py_model.train(['def greet(name): return f"Hello, {name}"'])
    line, conf = py_model.predict_next_line('def farewell(name): ')
    print(f"Python:     {line} ({conf:.0%})")
    
    # JavaScript
    js_model = CodeCompletionPredictor('javascript')
    js_model.train(['const add = (a, b) => a + b'])
    line, conf = js_model.predict_next_line('const subtract = (a, b) => ')
    print(f"JavaScript: {line} ({conf:.0%})")
    
    # Java
    java_model = CodeCompletionPredictor('java')
    java_model.train(['public int add(int a, int b) { return a + b; }'])
    line, conf = java_model.predict_next_line('public int multiply(int a, int b) { ')
    print(f"Java:       {line} ({conf:.0%})")
    print()


def example_3_function_completion():
    """Example 3: Function completion"""
    print("=" * 70)
    print("Example 3: Function Completion")
    print("=" * 70)
    
    training_data = [
        'def validate_email(email): return "@" in email and "." in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def validate_age(age): return age >= 18',
    ]
    
    model = train_model(training_data, 'python')
    
    # Complete partial function
    partial = 'def validate_username(username):\n    if len(username) < 3:\n        '
    completion, confidence = model.complete_function(partial)
    
    print(f"Partial function:")
    print(partial)
    print(f"\nCompletion: {completion}")
    print(f"Confidence: {confidence:.0%}")
    print()


def example_4_beam_search():
    """Example 4: Beam search (multiple predictions)"""
    print("=" * 70)
    print("Example 4: Beam Search - Multiple Predictions")
    print("=" * 70)
    
    training_data = [
        'if status == 200: return success',
        'if status == 201: return created',
        'if status == 404: return not_found',
        'if status == 500: return server_error',
        'if status == 403: return forbidden',
    ]
    
    model = train_model(training_data, 'python')
    
    # Get top 5 predictions
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"Context: {context}")
    print(f"\nTop {len(predictions)} predictions:")
    for i, (token, conf) in enumerate(predictions, 1):
        print(f"  {i}. {token:20} ({conf:.0%})")
    print()


def example_5_model_persistence():
    """Example 5: Save and load models"""
    print("=" * 70)
    print("Example 5: Model Persistence")
    print("=" * 70)
    
    import tempfile
    import os
    
    # Train model
    training_data = [
        'def calculate_sum(numbers): return sum(numbers)',
        'def calculate_average(numbers): return sum(numbers) / len(numbers)',
        'def calculate_max(numbers): return max(numbers)',
    ]
    
    model = train_model(training_data, 'python')
    print("✅ Model trained")
    
    # Save model
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        model_path = f.name
    
    model.save_model(model_path)
    print(f"✅ Model saved to {model_path}")
    
    # Load model in new instance
    new_model = CodeCompletionPredictor('python')
    new_model.load_model(model_path)
    print("✅ Model loaded in new instance")
    
    # Test prediction
    line, conf = new_model.predict_next_line('def calculate_min(numbers): ')
    print(f"\nPrediction: {line} ({conf:.0%})")
    
    # Cleanup
    os.unlink(model_path)
    print()


def example_6_real_world_patterns():
    """Example 6: Real-world code patterns"""
    print("=" * 70)
    print("Example 6: Real-World Code Patterns")
    print("=" * 70)
    
    # Train on realistic code patterns
    training_data = [
        'try: result = risky_operation()',
        'try: data = fetch_from_api()',
        'try: file = open("data.txt")',
        'except ValueError: logger.error("Invalid value")',
        'except KeyError: logger.error("Missing key")',
        'except Exception: logger.error("Unknown error")',
        'finally: cleanup_resources()',
        'finally: close_connections()',
    ]
    
    model = train_model(training_data, 'python', n=6)
    
    # Test various patterns
    tests = [
        'try: config = load_config() ',
        'except FileNotFoundError: ',
        'finally: ',
    ]
    
    for context in tests:
        line, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {line} ({conf:.0%})")
        print()


def example_7_statistics():
    """Example 7: Model statistics and performance"""
    print("=" * 70)
    print("Example 7: Model Statistics")
    print("=" * 70)
    
    # Train larger model
    training_data = [
        'def process_user_input(data): return data.strip().lower()',
        'def validate_user_input(data): return len(data) > 0',
        'def sanitize_user_input(data): return data.replace("<", "&lt;")',
        'class User: def __init__(self, name): self.name = name',
        'class Admin: def __init__(self, name): self.name = name',
        'if user.is_authenticated(): return dashboard',
        'if user.is_admin(): return admin_panel',
    ]
    
    model = train_model(training_data, 'python', n=5)
    
    # Get statistics
    stats = model.get_stats()
    
    print(f"Challenge ID:      {stats['challenge_id']}")
    print(f"Language:          {stats['language']}")
    print(f"N-gram order:      {stats['n']}")
    print(f"Vocabulary size:   {stats['vocabulary_size']} tokens")
    print(f"Cache size:        {stats['cache_size']} entries")
    print(f"Cache hit rate:    {stats['cache_hit_rate']:.0%}")
    print(f"\nN-gram counts by order:")
    for order, count in sorted(stats['ngram_counts'].items()):
        print(f"  {order}-grams: {count}")
    print()


def example_8_typescript_advanced():
    """Example 8: Advanced TypeScript patterns"""
    print("=" * 70)
    print("Example 8: Advanced TypeScript Patterns")
    print("=" * 70)
    
    # TypeScript-specific patterns
    training_data = [
        'interface User { id: number; name: string; email: string }',
        'interface Product { id: number; title: string; price: number }',
        'type UserRole = "admin" | "user" | "guest"',
        'type Status = "active" | "inactive" | "pending"',
        'const fetchUser = async (id: number): Promise<User> => {}',
        'const fetchProduct = async (id: number): Promise<Product> => {}',
    ]
    
    model = train_model(training_data, 'typescript', n=6)
    
    # Test TypeScript completions
    tests = [
        'interface Admin { ',
        'type Color = ',
        'const fetchOrder = async (id: number): ',
    ]
    
    for context in tests:
        line, conf = model.predict_next_line(context, max_tokens=8)
        print(f"Context:    {context}")
        print(f"Prediction: {line}")
        print(f"Confidence: {conf:.0%}")
        print()


def main():
    """Run all examples"""
    print()
    print("*" * 70)
    print("Code Completion Predictor - Usage Examples by @create-botter")
    print(f"Challenge ID: challenge-ml_code_predictor-1766240020-319351")
    print("*" * 70)
    print()
    
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
    
    for i, example in enumerate(examples, 1):
        example()
        if i < len(examples):
            print()
    
    print("*" * 70)
    print("All examples completed successfully! ✨")
    print("*" * 70)


if __name__ == '__main__':
    main()
