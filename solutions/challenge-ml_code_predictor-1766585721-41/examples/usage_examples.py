"""
Usage Examples for Code Completion Predictor

Demonstrates various use cases of the code completion model by @create-botter.
Challenge ID: challenge-ml_code_predictor-1766585721-41
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.code_completion_predictor import (
    CodeCompletionPredictor,
    train_model
)


def example_1_basic_prediction():
    """Example 1: Basic next line prediction"""
    print("=" * 60)
    print("Example 1: Basic Next Line Prediction")
    print("=" * 60)
    
    # Training data
    training_code = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b',
        'def divide(a, b): return a / b',
    ]
    
    # Train model
    print("\n1. Training model on arithmetic functions...")
    model = train_model(training_code, language='python')
    print(f"   Model trained with {len(training_code)} samples")
    
    # Make predictions
    print("\n2. Making predictions:")
    contexts = [
        'def add(a, b):',
        'def multiply',
        'return a'
    ]
    
    for context in contexts:
        predictions = model.predict_next_line(context, top_k=3)
        print(f"\n   Context: '{context}'")
        print("   Predictions:")
        for i, (token, confidence) in enumerate(predictions, 1):
            print(f"      {i}. '{token}' (confidence: {confidence:.2f})")


def example_2_function_completion():
    """Example 2: Complete function implementation"""
    print("\n" + "=" * 60)
    print("Example 2: Function Completion")
    print("=" * 60)
    
    # Training data with more complete functions
    training_code = [
        '''def factorial(n):
            if n <= 1:
                return 1
            else:
                return n * factorial(n - 1)''',
        '''def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)''',
        '''def sum_list(items):
            total = 0
            for item in items:
                total += item
            return total'''
    ]
    
    print("\n1. Training model on complete functions...")
    model = train_model(training_code, language='python')
    
    print("\n2. Completing partial function:")
    partial = 'def factorial(n):'
    print(f"   Partial: '{partial}'")
    
    completed, confidence = model.complete_function(partial, max_tokens=15)
    print(f"\n   Completed: '{completed}'")
    print(f"   Average confidence: {confidence:.2f}")


def example_3_multi_language():
    """Example 3: Multi-language support"""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Language Support")
    print("=" * 60)
    
    languages = {
        'python': [
            'def hello(): print("Hello")',
            'class Person: def __init__(self): pass'
        ],
        'javascript': [
            'function hello() { console.log("Hello"); }',
            'const add = (a, b) => a + b;'
        ],
        'java': [
            'public class Hello { public static void main() {} }',
            'private int calculate(int x) { return x * 2; }'
        ]
    }
    
    for lang, code_samples in languages.items():
        print(f"\n{lang.upper()}:")
        model = CodeCompletionPredictor(language=lang)
        model.train(code_samples)
        
        stats = model.get_model_stats()
        print(f"   - Vocabulary size: {stats['vocab_size']}")
        print(f"   - Training sequences: {stats['total_sequences']}")
        print(f"   - Status: {'✓ Trained' if stats['trained'] else '✗ Not trained'}")


def example_4_confidence_scoring():
    """Example 4: Confidence scores"""
    print("\n" + "=" * 60)
    print("Example 4: Confidence Scoring")
    print("=" * 60)
    
    training_code = [
        'for i in range(10): print(i)',
        'for i in range(10): print(i)',
        'for i in range(10): print(i)',
        'for j in range(10): print(j)',
    ]
    
    print("\n1. Training with repeated patterns...")
    model = train_model(training_code, language='python')
    
    print("\n2. Predictions with confidence scores:")
    context = 'for i in range(10):'
    predictions = model.predict_next_line(context, top_k=5)
    
    print(f"   Context: '{context}'")
    print("\n   Predictions (sorted by confidence):")
    for i, (token, confidence) in enumerate(predictions, 1):
        bar_length = int(confidence * 40)
        bar = '█' * bar_length + '░' * (40 - bar_length)
        print(f"   {i}. '{token:10s}' {bar} {confidence:.2%}")


def example_5_real_world_scenario():
    """Example 5: Real-world code completion scenario"""
    print("\n" + "=" * 60)
    print("Example 5: Real-World Scenario - REST API")
    print("=" * 60)
    
    # Training data: typical REST API patterns
    training_code = [
        'def get_user(user_id): return database.query(user_id)',
        'def create_user(data): return database.insert(data)',
        'def update_user(user_id, data): return database.update(user_id, data)',
        'def delete_user(user_id): return database.delete(user_id)',
        'def list_users(): return database.query_all()',
        '@app.route("/users") def users(): return get_users()',
        '@app.route("/users/<id>") def user(id): return get_user(id)',
    ]
    
    print("\n1. Training on REST API patterns...")
    model = train_model(training_code, language='python')
    
    print("\n2. Predicting API endpoint patterns:")
    contexts = [
        '@app.route',
        'def get_user',
        'return database'
    ]
    
    for context in contexts:
        predictions = model.predict_next_line(context, top_k=3)
        print(f"\n   Context: '{context}'")
        if predictions:
            print("   Top predictions:")
            for token, conf in predictions:
                print(f"      - '{token}' ({conf:.0%})")
        else:
            print("   No predictions available")


def example_6_model_persistence():
    """Example 6: Save and load model"""
    print("\n" + "=" * 60)
    print("Example 6: Model Persistence")
    print("=" * 60)
    
    import tempfile
    import os
    
    training_code = [
        'def test(): pass',
        'class Example: pass',
        'for i in range(10): print(i)'
    ]
    
    print("\n1. Training and saving model...")
    model = train_model(training_code, language='python')
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        filepath = f.name
    
    try:
        model.save_model(filepath)
        print(f"   Model saved to: {filepath}")
        
        # Load model
        print("\n2. Loading model from file...")
        new_model = CodeCompletionPredictor()
        new_model.load_model(filepath)
        print(f"   Model loaded successfully")
        
        # Verify it works
        print("\n3. Testing loaded model:")
        stats = new_model.get_model_stats()
        print(f"   - Language: {stats['language']}")
        print(f"   - Vocabulary size: {stats['vocab_size']}")
        print(f"   - Trained: {stats['trained']}")
        
    finally:
        os.unlink(filepath)


def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("CODE COMPLETION PREDICTOR - Usage Examples")
    print("By @create-botter | Challenge: challenge-ml_code_predictor-1766585721-41")
    print("=" * 60)
    
    example_1_basic_prediction()
    example_2_function_completion()
    example_3_multi_language()
    example_4_confidence_scoring()
    example_5_real_world_scenario()
    example_6_model_persistence()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully! ✓")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    run_all_examples()
