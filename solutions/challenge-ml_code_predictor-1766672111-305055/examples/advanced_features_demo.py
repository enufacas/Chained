"""
Example: Advanced Features Demo

Demonstrates advanced features like beam search, model persistence, and caching.
Challenge ID: challenge-ml_code_predictor-1766672111-305055
By @create-botter
"""

import sys
import time
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.code_completion_predictor import CodeCompletionPredictor, train_model


def demo_beam_search():
    """Demo beam search (multiple predictions)"""
    print("=" * 70)
    print("Beam Search Demo - Multiple Predictions")
    print("=" * 70)
    
    training_code = [
        'if status == 200: return success',
        'if status == 404: return not_found',
        'if status == 500: return error',
        'if status == 403: return forbidden',
        'if status == 401: return unauthorized',
    ]
    
    model = train_model(training_code, 'python')
    
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"Context: {context}")
    print(f"\nTop {len(predictions)} predictions:")
    for i, (token, conf) in enumerate(predictions, 1):
        print(f"  {i}. {token:15s} (confidence: {conf:.0%})")
    print()


def demo_model_persistence():
    """Demo saving and loading models"""
    print("=" * 70)
    print("Model Persistence Demo - Save/Load")
    print("=" * 70)
    
    training_code = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b',
    ]
    
    # Train original model
    print("Training original model...")
    model = train_model(training_code, 'python')
    
    # Test prediction before saving
    context = 'def divide(a, b): '
    original_pred, original_conf = model.predict_next_line(context)
    print(f"Original prediction: {original_pred} (confidence: {original_conf:.0%})")
    
    # Save model
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        model_path = f.name
    
    print(f"Saving model to {model_path}...")
    model.save_model(model_path)
    
    # Load in new model
    print("Loading model...")
    new_model = CodeCompletionPredictor('python')
    new_model.load_model(model_path)
    
    # Test prediction after loading
    loaded_pred, loaded_conf = new_model.predict_next_line(context)
    print(f"Loaded prediction:   {loaded_pred} (confidence: {loaded_conf:.0%})")
    
    # Verify predictions match
    if original_pred == loaded_pred:
        print("✅ Model persistence verified - predictions match!")
    
    # Cleanup
    import os
    os.unlink(model_path)
    print()


def demo_caching_performance():
    """Demo caching performance improvement"""
    print("=" * 70)
    print("Caching Performance Demo")
    print("=" * 70)
    
    training_code = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b',
        'def divide(a, b): return a / b',
        'def modulo(a, b): return a % b',
    ]
    
    model = train_model(training_code, 'python')
    
    context = 'def power(a, b): '
    
    # First prediction (cold - no cache)
    print("First prediction (cold)...")
    start = time.time()
    pred1, conf1 = model.predict_next_line(context)
    cold_time = (time.time() - start) * 1000
    print(f"  Time: {cold_time:.2f}ms")
    print(f"  Result: {pred1} (confidence: {conf1:.0%})")
    
    # Second prediction (cached)
    print("\nSecond prediction (cached)...")
    start = time.time()
    pred2, conf2 = model.predict_next_line(context)
    cached_time = (time.time() - start) * 1000
    print(f"  Time: {cached_time:.2f}ms")
    print(f"  Result: {pred2} (confidence: {conf2:.0%})")
    
    # Calculate speedup
    if cached_time > 0:
        speedup = cold_time / cached_time
        print(f"\n✅ Caching speedup: {speedup:.1f}x faster!")
    
    print()


def demo_model_statistics():
    """Demo model statistics"""
    print("=" * 70)
    print("Model Statistics Demo")
    print("=" * 70)
    
    training_code = [
        'def validate_email(email): return "@" in email and "." in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def validate_username(user): return len(user) >= 3',
        'def process_data(data): return data.strip().lower()',
        'if status == 200: return success',
        'if status == 404: return not_found',
    ]
    
    model = train_model(training_code, 'python', n=5)
    
    # Get detailed statistics
    stats = model.get_stats()
    
    print("Model Configuration:")
    print(f"  Challenge ID:  {stats['challenge_id']}")
    print(f"  Language:      {stats['language']}")
    print(f"  N-gram order:  {stats['n']}")
    print()
    
    print("Training Statistics:")
    print(f"  Vocabulary:    {stats['vocabulary_size']} unique tokens")
    print(f"  Cache size:    {stats['cache_size']} cached predictions")
    print(f"  Cache hit rate: {stats['cache_hit_rate']:.0%}")
    print()
    
    print("N-gram Distribution:")
    for order, count in sorted(stats['ngram_counts'].items()):
        print(f"  {order}-grams: {count} unique contexts")
    print()


def demo_function_completion():
    """Demo function completion with various patterns"""
    print("=" * 70)
    print("Function Completion Demo")
    print("=" * 70)
    
    training_code = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b',
        'def divide(a, b): return a / b',
        'def square(x): return x * x',
        'def cube(x): return x * x * x',
        'def is_even(n): return n % 2 == 0',
        'def is_odd(n): return n % 2 != 0',
    ]
    
    model = train_model(training_code, 'python')
    
    partial_functions = [
        'def modulo(a, b):\n    ',
        'def power(x):\n    ',
        'def is_positive(n):\n    ',
    ]
    
    for partial in partial_functions:
        completion, conf = model.complete_function(partial)
        print(f"Partial function:")
        print(f"  {partial.strip()}")
        print(f"Completion:")
        print(f"  {completion} (confidence: {conf:.0%})")
        print()


if __name__ == '__main__':
    print("\n")
    print("*" * 70)
    print("Advanced Features Demo - @create-botter")
    print(f"Challenge ID: {CodeCompletionPredictor.CHALLENGE_ID}")
    print("*" * 70)
    print("\n")
    
    demo_beam_search()
    demo_model_persistence()
    demo_caching_performance()
    demo_model_statistics()
    demo_function_completion()
    
    print("*" * 70)
    print("All advanced feature demos complete! ✨")
    print("*" * 70)
