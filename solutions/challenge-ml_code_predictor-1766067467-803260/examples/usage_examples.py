"""
Usage Examples for Code Completion Predictor

Demonstrates various features and use cases by @create-botter.
Challenge ID: challenge-ml_code_predictor-1766067467-803260
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
    
    # Training data
    training_code = [
        'def validate_email(email): return "@" in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def validate_username(user): return len(user) > 3'
    ]
    
    # Train model
    model = train_model(training_code, language='python')
    
    # Predict next line
    context = 'def validate_password(pwd): '
    line, confidence = model.predict_next_line(context)
    
    print(f"Context: {context}")
    print(f"Prediction: {line}")
    print(f"Confidence: {confidence:.0%}")
    print()


def example_2_multi_language():
    """Example 2: Multi-language support"""
    print("=" * 70)
    print("Example 2: Multi-Language Support")
    print("=" * 70)
    
    examples = {
        'Python': {
            'training': ['def add(a, b): return a + b'],
            'context': 'def multiply(a, b): '
        },
        'JavaScript': {
            'training': ['const add = (a, b) => a + b'],
            'context': 'const multiply = (a, b) => '
        },
        'Java': {
            'training': ['public int add(int a, int b) { return a + b; }'],
            'context': 'public int multiply(int a, int b) { '
        }
    }
    
    for lang, data in examples.items():
        model = CodeCompletionPredictor(lang.lower())
        model.train(data['training'])
        
        line, conf = model.predict_next_line(data['context'])
        print(f"{lang}: {data['context']}")
        print(f"  → {line} ({conf:.0%})")
    
    print()


def example_3_function_completion():
    """Example 3: Function completion"""
    print("=" * 70)
    print("Example 3: Function Completion")
    print("=" * 70)
    
    training_code = [
        'if x > 0: return True',
        'if x < 0: return False',
        'if x == 0: return None'
    ]
    
    model = train_model(training_code, language='python')
    
    partials = [
        'if status == 200: ',
        'if value > 100: ',
        'if count == 0: '
    ]
    
    for partial in partials:
        completion, confidence = model.complete_function(partial)
        print(f"{partial}")
        print(f"  → {completion} ({confidence:.0%})")
    
    print()


def example_4_beam_search():
    """Example 4: Beam search (multiple predictions)"""
    print("=" * 70)
    print("Example 4: Beam Search (Multiple Predictions)")
    print("=" * 70)
    
    training_code = [
        'if status == 200: print("OK")',
        'if status == 404: print("Not Found")',
        'if status == 500: print("Error")',
        'if status == 403: print("Forbidden")',
        'if status == 401: print("Unauthorized")'
    ]
    
    model = train_model(training_code, language='python')
    
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"Context: {context}")
    print("Top predictions:")
    for i, (pred, conf) in enumerate(predictions, 1):
        print(f"  {i}. {pred:10} ({conf:.0%})")
    
    print()


def example_5_model_persistence():
    """Example 5: Save and load models"""
    print("=" * 70)
    print("Example 5: Model Persistence")
    print("=" * 70)
    
    import tempfile
    import os
    
    # Train model
    training_code = ['def foo(): return 42'] * 5
    model1 = train_model(training_code, language='python')
    
    # Save model
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name
    
    try:
        print("Saving model...")
        model1.save_model(temp_path)
        print(f"✅ Saved to {temp_path}")
        
        # Load model
        print("Loading model...")
        model2 = CodeCompletionPredictor('python')
        model2.load_model(temp_path)
        print("✅ Loaded successfully")
        
        # Test loaded model
        line, conf = model2.predict_next_line('def bar(): ')
        print(f"Prediction from loaded model: {line} ({conf:.0%})")
    finally:
        os.unlink(temp_path)
    
    print()


def example_6_real_world_patterns():
    """Example 6: Real-world coding patterns"""
    print("=" * 70)
    print("Example 6: Real-World Coding Patterns")
    print("=" * 70)
    
    training_code = [
        'try: result = process_data()',
        'try: response = api_call()',
        'except ValueError: return None',
        'except KeyError: return default',
        'except Exception as e: log_error(e)',
        'finally: cleanup()'
    ]
    
    model = train_model(training_code, language='python')
    
    contexts = [
        'try: ',
        'except TypeError: ',
        'finally: '
    ]
    
    for context in contexts:
        line, conf = model.predict_next_line(context)
        print(f"{context}")
        print(f"  → {line} ({conf:.0%})")
    
    print()


def example_7_model_statistics():
    """Example 7: Model statistics"""
    print("=" * 70)
    print("Example 7: Model Statistics")
    print("=" * 70)
    
    # Train on moderate dataset
    training_code = [
        f'def func_{i}(x): return x + {i}'
        for i in range(20)
    ]
    
    model = train_model(training_code, language='python', n=5)
    
    # Get statistics
    stats = model.get_stats()
    
    print("Model Statistics:")
    print(f"  Challenge ID: {stats['challenge_id']}")
    print(f"  Language: {stats['language']}")
    print(f"  N-gram order: {stats['n']}")
    print(f"  Vocabulary size: {stats['vocabulary_size']} tokens")
    print(f"  Cache hit rate: {stats['cache_hit_rate']:.1%}")
    print(f"  N-gram counts:")
    for order, count in sorted(stats['ngram_counts'].items()):
        print(f"    {order}-grams: {count}")
    
    print()


def example_8_typescript_advanced():
    """Example 8: TypeScript with interfaces"""
    print("=" * 70)
    print("Example 8: TypeScript Advanced Features")
    print("=" * 70)
    
    training_code = [
        'interface User { name: string; email: string; }',
        'interface Product { id: number; price: number; }',
        'type Response<T> = { data: T; status: number; }'
    ]
    
    model = train_model(training_code, language='typescript')
    
    contexts = [
        'interface Admin { ',
        'type Error<T> = { '
    ]
    
    for context in contexts:
        line, conf = model.predict_next_line(context)
        print(f"{context}")
        print(f"  → {line} ({conf:.0%})")
    
    print()


def main():
    """Run all examples"""
    print("\n")
    print("*" * 70)
    print("Code Completion Predictor - Usage Examples")
    print("By @create-botter")
    print(f"Challenge ID: challenge-ml_code_predictor-1766067467-803260")
    print("*" * 70)
    print("\n")
    
    examples = [
        example_1_basic_completion,
        example_2_multi_language,
        example_3_function_completion,
        example_4_beam_search,
        example_5_model_persistence,
        example_6_real_world_patterns,
        example_7_model_statistics,
        example_8_typescript_advanced
    ]
    
    for example in examples:
        example()
    
    print("*" * 70)
    print("✅ All examples completed successfully!")
    print("*" * 70)


if __name__ == '__main__':
    main()
