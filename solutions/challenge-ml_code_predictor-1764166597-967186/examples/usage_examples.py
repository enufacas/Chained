"""
Usage Examples for Code Completion Predictor

Demonstrates various ways to use the code completion predictor
across different programming languages and use cases.

Created by @create-guru
Challenge ID: challenge-ml_code_predictor-1764166597-967186
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.code_completion_predictor import (
    CodeCompletionPredictor,
    train_model
)


def example_1_basic_usage():
    """Example 1: Basic Python code completion."""
    print("=" * 70)
    print("Example 1: Basic Python Code Completion")
    print("=" * 70)
    
    # Create and train model
    model = CodeCompletionPredictor('python')
    
    training_code = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b',
        'def divide(a, b): return a / b'
    ]
    
    model.train(training_code)
    print(f"✓ Trained on {len(training_code)} samples\n")
    
    # Predict next line
    context = 'def modulo(a, b): '
    line, confidence = model.predict_next_line(context)
    
    print(f"Context:     {context}")
    print(f"Prediction:  {line}")
    print(f"Confidence:  {confidence:.1%}\n")


def example_2_multi_language():
    """Example 2: Multi-language support."""
    print("=" * 70)
    print("Example 2: Multi-Language Support")
    print("=" * 70)
    
    languages = {
        'Python': {
            'lang': 'python',
            'training': [
                'def process(data): return data.strip()',
                'def validate(input): return len(input) > 0'
            ],
            'context': 'def transform(text): '
        },
        'JavaScript': {
            'lang': 'javascript',
            'training': [
                'const process = (data) => data.trim()',
                'const validate = (input) => input.length > 0'
            ],
            'context': 'const transform = (text) => '
        },
        'Java': {
            'lang': 'java',
            'training': [
                'public int add(int a, int b) { return a + b; }',
                'public int multiply(int a, int b) { return a * b; }'
            ],
            'context': 'public int subtract(int a, int b) { '
        }
    }
    
    for name, config in languages.items():
        model = CodeCompletionPredictor(config['lang'])
        model.train(config['training'])
        
        line, confidence = model.predict_next_line(config['context'])
        
        print(f"\n{name}:")
        print(f"  Context:     {config['context']}")
        print(f"  Prediction:  {line}")
        print(f"  Confidence:  {confidence:.1%}")
    
    print()


def example_3_function_completion():
    """Example 3: Function completion."""
    print("=" * 70)
    print("Example 3: Function Completion")
    print("=" * 70)
    
    model = CodeCompletionPredictor('python')
    
    training_code = [
        'def validate_email(email): return "@" in email and "." in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def validate_username(user): return len(user) >= 3'
    ]
    
    model.train(training_code)
    
    # Complete partial function
    partial = 'def validate_password(pwd): '
    completion, confidence = model.complete_function(partial)
    
    print(f"Partial function:\n  {partial}\n")
    print(f"Completion:\n  {completion}\n")
    print(f"Confidence: {confidence:.1%}\n")


def example_4_beam_search():
    """Example 4: Beam search (multiple predictions)."""
    print("=" * 70)
    print("Example 4: Beam Search (Multiple Predictions)")
    print("=" * 70)
    
    model = CodeCompletionPredictor('python')
    
    training_code = [
        'if status == 200: return True',
        'if status == 404: return None',
        'if status == 500: raise Exception("Server error")',
        'if status == 401: return False',
        'if status == 403: return False'
    ]
    
    model.train(training_code)
    
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"Context: {context}\n")
    print("Top predictions:")
    for i, (token, confidence) in enumerate(predictions, 1):
        print(f"  {i}. {token:10s} (confidence: {confidence:.1%})")
    
    print()


def example_5_model_persistence():
    """Example 5: Save and load models."""
    print("=" * 70)
    print("Example 5: Model Persistence (Save/Load)")
    print("=" * 70)
    
    # Train and save model
    model = train_model(['def foo(): return 42'], language='python')
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        model_path = f.name
    
    model.save_model(model_path)
    print(f"✓ Model saved to {model_path}")
    
    # Load model
    model2 = CodeCompletionPredictor('python')
    model2.load_model(model_path)
    print(f"✓ Model loaded from {model_path}\n")
    
    # Make prediction with loaded model
    line, confidence = model2.predict_next_line('def bar(): ')
    print(f"Prediction from loaded model: {line}")
    print(f"Confidence: {confidence:.1%}\n")
    
    # Cleanup
    os.unlink(model_path)


def example_6_performance_stats():
    """Example 6: Model statistics and performance."""
    print("=" * 70)
    print("Example 6: Model Statistics and Performance")
    print("=" * 70)
    
    model = CodeCompletionPredictor('python', n=5)
    
    training_code = [
        'def validate_email(email): return "@" in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def process_data(data): return data.strip().lower()',
        'def calculate_sum(numbers): return sum(numbers)'
    ]
    
    model.train(training_code)
    
    # Make some predictions to populate cache
    for _ in range(3):
        model.predict_next_line('def test(): ')
    
    # Get statistics
    stats = model.get_stats()
    
    print(f"Challenge ID:      {stats['challenge_id']}")
    print(f"Language:          {stats['language']}")
    print(f"N-gram order:      {stats['n']}")
    print(f"Vocabulary size:   {stats['vocabulary_size']} tokens")
    print(f"Training samples:  {stats['training_samples']}")
    print(f"Cache size:        {stats['cache_size']}")
    print(f"Cache hit rate:    {stats['cache_hit_rate']:.1%}\n")
    
    print("N-gram counts by order:")
    for order, count in sorted(stats['ngram_counts'].items()):
        print(f"  Order {order}: {count} n-grams")
    
    print()


def example_7_realtime_performance():
    """Example 7: Real-time inference performance."""
    print("=" * 70)
    print("Example 7: Real-Time Inference Performance")
    print("=" * 70)
    
    import time
    
    model = CodeCompletionPredictor('python')
    
    training_code = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b'
    ]
    
    model.train(training_code)
    
    # Measure cold prediction time
    context = 'def divide(a, b): '
    start = time.time()
    line, confidence = model.predict_next_line(context)
    cold_time = (time.time() - start) * 1000
    
    print(f"Cold prediction:")
    print(f"  Time:       {cold_time:.2f}ms")
    print(f"  Prediction: {line}")
    print(f"  Target:     <100ms")
    print(f"  Status:     {'✓ PASS' if cold_time < 100 else '✗ FAIL'}\n")
    
    # Measure cached prediction time
    start = time.time()
    line2, confidence2 = model.predict_next_line(context)
    cached_time = (time.time() - start) * 1000
    
    print(f"Cached prediction (same context):")
    print(f"  Time:       {cached_time:.2f}ms")
    print(f"  Prediction: {line2}")
    print(f"  Target:     <50ms")
    print(f"  Status:     {'✓ PASS' if cached_time < 50 else '✗ FAIL'}\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("CODE COMPLETION PREDICTOR - USAGE EXAMPLES")
    print("Created by @create-guru")
    print("Challenge ID: challenge-ml_code_predictor-1764166597-967186")
    print("=" * 70 + "\n")
    
    examples = [
        example_1_basic_usage,
        example_2_multi_language,
        example_3_function_completion,
        example_4_beam_search,
        example_5_model_persistence,
        example_6_performance_stats,
        example_7_realtime_performance
    ]
    
    for example in examples:
        example()
        input("Press Enter to continue to next example...")
        print()


if __name__ == '__main__':
    main()
