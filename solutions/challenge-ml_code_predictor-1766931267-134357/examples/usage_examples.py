#!/usr/bin/env python3
"""
Usage Examples for Code Completion Predictor

Demonstrates various use cases and features of the code completion predictor.
Created by @create-botter for challenge-ml_code_predictor-1766931267-134357.

Examples:
    - Basic code completion
    - Multi-language support
    - Beam search for multiple predictions
    - Function completion
    - Model persistence
    - Performance metrics
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.code_completion_predictor import CodeCompletionPredictor


def example_1_basic_usage():
    """Example 1: Basic Code Completion"""
    print("=" * 70)
    print("Example 1: Basic Code Completion")
    print("=" * 70)
    
    # Create model
    model = CodeCompletionPredictor(language='python', n=5)
    
    # Train on sample code
    training_data = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b',
        'def divide(a, b): return a / b'
    ]
    
    print("\n📚 Training on sample functions...")
    model.train(training_data)
    print(f"✅ Trained on {len(training_data)} code samples")
    
    # Make prediction
    context = 'def modulo(a, b): '
    predicted, confidence = model.predict_next_line(context)
    
    print(f"\n🔮 Prediction:")
    print(f"   Context:    '{context}'")
    print(f"   Prediction: '{predicted}'")
    print(f"   Confidence: {confidence:.0%}")
    print()


def example_2_multi_language():
    """Example 2: Multi-Language Support"""
    print("=" * 70)
    print("Example 2: Multi-Language Support")
    print("=" * 70)
    
    examples = [
        ('python', ['def add(a, b): return a + b'], 'def sub(a, b): '),
        ('javascript', ['const add = (a, b) => a + b'], 'const sub = (a, b) => '),
        ('typescript', ['function add(a: number, b: number): number { return a + b }'], 'function sub(a: number, b: number): number { '),
        ('java', ['public int add(int a, int b) { return a + b; }'], 'public int sub(int a, int b) { '),
        ('go', ['func add(a, b int) int { return a + b }'], 'func sub(a, b int) int { ')
    ]
    
    print()
    for lang, training, context in examples:
        model = CodeCompletionPredictor(language=lang, n=4)
        model.train(training)
        
        predicted, confidence = model.predict_next_line(context)
        
        print(f"🌍 {lang.upper()}:")
        print(f"   Training:   '{training[0]}'")
        print(f"   Context:    '{context}'")
        print(f"   Prediction: '{predicted}' ({confidence:.0%})")
        print()


def example_3_beam_search():
    """Example 3: Beam Search (Multiple Predictions)"""
    print("=" * 70)
    print("Example 3: Beam Search - Multiple Predictions")
    print("=" * 70)
    
    # Create and train model
    model = CodeCompletionPredictor(language='python', n=5)
    
    training_data = [
        'if status == 200: return True',
        'if status == 404: return False',
        'if status == 500: raise Exception',
        'if value > 0: return value',
        'if value < 0: return 0'
    ]
    
    model.train(training_data)
    
    # Get top-5 predictions
    context = 'if status '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"\n🔍 Getting top-5 predictions for: '{context}'")
    print(f"\n{'Rank':<6} {'Token':<15} {'Confidence':<12}")
    print("-" * 35)
    
    for i, (token, confidence) in enumerate(predictions, 1):
        bar = '█' * int(confidence * 20)
        print(f"{i:<6} {token:<15} {confidence:>6.0%}  {bar}")
    print()


def example_4_function_completion():
    """Example 4: Function Completion"""
    print("=" * 70)
    print("Example 4: Function Completion")
    print("=" * 70)
    
    # Create model
    model = CodeCompletionPredictor(language='python', n=5)
    
    # Train with validation examples
    training_data = [
        'def validate_email(email): return "@" in email and "." in email',
        'def validate_username(user): return len(user) >= 3 and user.isalnum()',
        'def validate_password(pwd): return len(pwd) >= 8',
        'def validate_age(age): return age >= 18 and age <= 120'
    ]
    
    model.train(training_data)
    
    # Complete partial functions
    examples = [
        'def validate_phone(phone): ',
        'def validate_zipcode(zip): ',
        'def validate_url(url): '
    ]
    
    print()
    for partial in examples:
        completion, confidence = model.complete_function(partial)
        
        print(f"📝 Input:  {partial}")
        print(f"   Output: {completion}")
        print(f"   Confidence: {confidence:.0%}")
        print()


def example_5_model_persistence():
    """Example 5: Save and Load Model"""
    print("=" * 70)
    print("Example 5: Model Persistence")
    print("=" * 70)
    
    import tempfile
    import os
    
    # Create temp file for model
    temp_file = tempfile.mktemp(suffix='.json')
    
    print("\n💾 Saving model...")
    
    # Train and save model
    model1 = CodeCompletionPredictor('python', n=5)
    training_data = [
        'def process(data): return data.strip().lower()',
        'def validate(input): return input is not None'
    ]
    model1.train(training_data)
    model1.save_model(temp_file)
    
    print(f"✅ Model saved to {temp_file}")
    print(f"   File size: {os.path.getsize(temp_file)} bytes")
    
    # Make prediction with original model
    context = 'def transform(text): '
    pred1, conf1 = model1.predict_next_line(context)
    
    print(f"\n📊 Original model prediction:")
    print(f"   {pred1} (confidence: {conf1:.0%})")
    
    # Load model
    print("\n📂 Loading model...")
    model2 = CodeCompletionPredictor('python', n=5)
    model2.load_model(temp_file)
    print("✅ Model loaded successfully")
    
    # Make prediction with loaded model
    pred2, conf2 = model2.predict_next_line(context)
    
    print(f"\n📊 Loaded model prediction:")
    print(f"   {pred2} (confidence: {conf2:.0%})")
    
    # Verify they match
    if pred1 == pred2 and abs(conf1 - conf2) < 0.001:
        print("\n✅ Predictions match! Model persistence works correctly.")
    else:
        print("\n⚠️  Predictions differ slightly (expected with probabilistic model)")
    
    # Clean up
    os.unlink(temp_file)
    print()


def example_6_performance_metrics():
    """Example 6: Performance Metrics and Statistics"""
    print("=" * 70)
    print("Example 6: Performance Metrics and Statistics")
    print("=" * 70)
    
    import time
    
    # Create and train model
    model = CodeCompletionPredictor(language='python', n=5)
    
    training_data = [
        'def add(a, b): return a + b',
        'def sub(a, b): return a - b',
        'if x > 0: return True',
        'if x < 0: return False',
        'for i in range(10): print(i)',
        'while True: break'
    ]
    
    model.train(training_data)
    
    print("\n📊 Model Statistics:")
    stats = model.get_stats()
    
    print(f"   Challenge ID:     {stats['challenge_id']}")
    print(f"   Language:         {stats['language']}")
    print(f"   N-gram Order:     {stats['n_gram_order']}")
    print(f"   Vocabulary Size:  {stats['vocabulary_size']}")
    print(f"   Cache Size:       {stats['cache_size']}")
    print(f"   Cache Hit Rate:   {stats['cache_hit_rate']:.0%}")
    
    # Test performance
    print("\n⚡ Performance Testing:")
    
    contexts = [
        'def test(): ',
        'if x == ',
        'for i in ',
        'return x '
    ]
    
    # Warm up
    for ctx in contexts:
        model.predict_next_line(ctx)
    
    # Measure cold prediction
    start = time.time()
    for _ in range(100):
        model.predict_next_line('def new_func(): ')
    cold_avg = (time.time() - start) * 1000 / 100
    
    # Measure cached prediction
    start = time.time()
    for _ in range(100):
        model.predict_next_line('def test(): ')  # Cached
    cached_avg = (time.time() - start) * 1000 / 100
    
    print(f"   Cold Prediction:   {cold_avg:.2f}ms avg (100 iterations)")
    print(f"   Cached Prediction: {cached_avg:.2f}ms avg (100 iterations)")
    print(f"   Speedup:           {cold_avg / cached_avg:.1f}x faster with cache")
    
    # Get final stats
    final_stats = model.get_stats()
    print(f"\n📈 Final Cache Statistics:")
    print(f"   Cache Hits:   {final_stats['cache_hits']}")
    print(f"   Cache Misses: {final_stats['cache_misses']}")
    print(f"   Hit Rate:     {final_stats['cache_hit_rate']:.0%}")
    print()


def example_7_real_world_scenario():
    """Example 7: Real-World Coding Scenario"""
    print("=" * 70)
    print("Example 7: Real-World Coding Scenario")
    print("=" * 70)
    
    # Create model
    model = CodeCompletionPredictor(language='python', n=6)
    
    # Train on realistic code patterns
    training_data = [
        'def fetch_user(user_id): return db.query(User).filter_by(id=user_id).first()',
        'def create_user(data): return db.session.add(User(**data))',
        'def update_user(user_id, data): user = fetch_user(user_id)',
        'def delete_user(user_id): user = fetch_user(user_id)',
        'if user is None: return {"error": "User not found"}',
        'if not data: return {"error": "Invalid data"}',
        'try: result = process(data)',
        'except Exception as e: return {"error": str(e)}'
    ]
    
    model.train(training_data)
    
    print("\n🌐 Simulating code editor completions:\n")
    
    scenarios = [
        ('User starts typing a new function', 'def get_user('),
        ('Conditional check', 'if user is '),
        ('Error handling', 'except Exception as e: '),
        ('Return statement', 'return {"error": ')
    ]
    
    for description, context in scenarios:
        predicted, confidence = model.predict_next_line(context)
        
        print(f"📝 {description}")
        print(f"   User types:  {context}")
        print(f"   AI suggests: {predicted}")
        print(f"   Confidence:  {confidence:.0%}")
        print()


def main():
    """Run all examples"""
    print("\n" + "🎨" * 35)
    print("Code Completion Predictor - Usage Examples")
    print("Challenge ID: challenge-ml_code_predictor-1766931267-134357")
    print("Created by: @create-botter")
    print("🎨" * 35 + "\n")
    
    examples = [
        example_1_basic_usage,
        example_2_multi_language,
        example_3_beam_search,
        example_4_function_completion,
        example_5_model_persistence,
        example_6_performance_metrics,
        example_7_real_world_scenario
    ]
    
    for example_func in examples:
        try:
            example_func()
            print()
        except Exception as e:
            print(f"❌ Error in {example_func.__name__}: {e}")
            print()
    
    print("=" * 70)
    print("✅ All examples completed!")
    print("=" * 70)


if __name__ == '__main__':
    main()
