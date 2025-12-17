"""
Usage Examples for Code Completion Predictor

Comprehensive examples demonstrating the capabilities of the
Code Completion Predictor by @create-botter.

Challenge ID: challenge-ml_code_predictor-1765981050-376430

Run this file to see all examples in action:
    python3 examples/usage_examples.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from code_completion_predictor import CodeCompletionPredictor, train_model


def example_1_basic_completion():
    """Example 1: Basic code completion"""
    print("=" * 70)
    print("Example 1: Basic Code Completion")
    print("=" * 70)
    print()
    
    # Train on simple Python functions
    training_data = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b',
    ]
    
    model = train_model(training_data, 'python')
    
    # Predict next line
    context = 'def divide(a, b): '
    prediction, confidence = model.predict_next_line(context)
    
    print(f"Training data: {len(training_data)} samples")
    print(f"Context:    {context}")
    print(f"Prediction: {prediction}")
    print(f"Confidence: {confidence:.0%}")
    print()


def example_2_multi_language():
    """Example 2: Multi-language support"""
    print("=" * 70)
    print("Example 2: Multi-Language Support")
    print("=" * 70)
    print()
    
    examples = {
        'python': {
            'training': ['def validate(x): return x is not None'],
            'context': 'def check(y): '
        },
        'javascript': {
            'training': ['const validate = (x) => x !== null'],
            'context': 'const check = (y) => '
        },
        'java': {
            'training': ['public boolean validate(int x) { return x > 0; }'],
            'context': 'public boolean check(int y) { '
        },
        'go': {
            'training': ['func validate(x int) bool { return x > 0 }'],
            'context': 'func check(y int) bool { '
        }
    }
    
    for lang, data in examples.items():
        model = CodeCompletionPredictor(lang)
        model.train(data['training'])
        
        pred, conf = model.predict_next_line(data['context'])
        
        print(f"Language: {lang.upper()}")
        print(f"Context:    {data['context']}")
        print(f"Prediction: {pred} ({conf:.0%})")
        print()


def example_3_function_completion():
    """Example 3: Function completion"""
    print("=" * 70)
    print("Example 3: Function Completion")
    print("=" * 70)
    print()
    
    training_data = [
        'def process_data(data): if data: return data.strip()',
        'def clean_text(text): if text: return text.lower()',
        'def format_name(name): if name: return name.title()',
    ]
    
    model = train_model(training_data, 'python')
    
    # Complete partial function
    partial = 'def validate_input(value):\n    if value:\n        '
    completion, confidence = model.complete_function(partial)
    
    print("Partial function:")
    print(partial)
    print(f"Completion: {completion} ({confidence:.0%})")
    print()


def example_4_beam_search():
    """Example 4: Beam search (multiple predictions)"""
    print("=" * 70)
    print("Example 4: Beam Search - Multiple Predictions")
    print("=" * 70)
    print()
    
    training_data = [
        'if status == 200: print("OK")',
        'if status == 404: print("Not Found")',
        'if status == 500: print("Error")',
        'if status == 201: print("Created")',
    ]
    
    model = train_model(training_data, 'python')
    
    # Get top 5 predictions
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"Context: {context}")
    print("\nTop predictions:")
    for i, (token, conf) in enumerate(predictions[:5], 1):
        print(f"  {i}. {token:15} (confidence: {conf:.0%})")
    print()


def example_5_model_persistence():
    """Example 5: Save and load model"""
    print("=" * 70)
    print("Example 5: Model Persistence")
    print("=" * 70)
    print()
    
    import tempfile
    import os
    
    # Train a model
    training_data = [
        'def foo(): return 42',
        'def bar(): return 100',
    ]
    
    model = train_model(training_data, 'python')
    
    # Save model
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        filepath = f.name
    
    try:
        model.save_model(filepath)
        print(f"Model saved to: {filepath}")
        
        # Load model in new instance
        new_model = CodeCompletionPredictor('python')
        new_model.load_model(filepath)
        print("Model loaded successfully")
        
        # Use loaded model
        pred, conf = new_model.predict_next_line('def baz(): ')
        print(f"\nPrediction from loaded model: {pred} ({conf:.0%})")
        print()
    finally:
        os.unlink(filepath)


def example_6_real_world_patterns():
    """Example 6: Real-world code patterns"""
    print("=" * 70)
    print("Example 6: Real-World Code Patterns")
    print("=" * 70)
    print()
    
    # Train on realistic Python patterns
    training_data = [
        'def read_file(path): with open(path) as f: return f.read()',
        'def write_file(path, data): with open(path, "w") as f: f.write(data)',
        'def append_file(path, data): with open(path, "a") as f: f.write(data)',
    ]
    
    model = train_model(training_data, 'python')
    
    contexts = [
        'def load_data(filename): ',
        'def save_data(filename, content): ',
    ]
    
    for context in contexts:
        pred, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {pred} ({conf:.0%})")
        print()


def example_7_performance_stats():
    """Example 7: Performance statistics"""
    print("=" * 70)
    print("Example 7: Performance Statistics")
    print("=" * 70)
    print()
    
    import time
    
    # Create and train model
    training_data = [f'def func{i}(): return {i}' for i in range(100)]
    model = train_model(training_data, 'python')
    
    # Measure prediction performance
    context = 'def test(): '
    
    # Cold prediction
    start = time.time()
    model.predict_next_line(context)
    cold_time = (time.time() - start) * 1000
    
    # Cached predictions
    times = []
    for _ in range(100):
        start = time.time()
        model.predict_next_line(context)
        times.append((time.time() - start) * 1000)
    
    cached_avg = sum(times) / len(times)
    
    # Get stats
    stats = model.get_stats()
    
    print(f"Challenge ID: {stats['challenge_id']}")
    print(f"Language: {stats['language']}")
    print(f"Vocabulary size: {stats['vocabulary_size']} tokens")
    print(f"N-gram order: {stats['n']}")
    print(f"N-gram counts: {stats['ngram_counts']}")
    print()
    print("Performance:")
    print(f"  Cold prediction: {cold_time:.3f}ms")
    print(f"  Cached average:  {cached_avg:.3f}ms")
    print(f"  Cache size: {stats['cache_size']}")
    print()


def example_8_typescript_advanced():
    """Example 8: Advanced TypeScript completion"""
    print("=" * 70)
    print("Example 8: Advanced TypeScript Completion")
    print("=" * 70)
    print()
    
    training_data = [
        'interface User { id: number; name: string; }',
        'interface Post { id: number; title: string; }',
        'interface Comment { id: number; text: string; }',
        'const fetchUser = async (id: number): Promise<User> => { return {} as User; }',
        'const fetchPost = async (id: number): Promise<Post> => { return {} as Post; }',
    ]
    
    model = train_model(training_data, 'typescript')
    
    contexts = [
        'interface Product { ',
        'const fetchComment = async (id: number): ',
    ]
    
    for context in contexts:
        pred, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {pred} ({conf:.0%})")
        print()


def main():
    """Run all examples"""
    print()
    print("*" * 70)
    print(" Code Completion Predictor - Usage Examples")
    print(" by @create-botter")
    print(" Challenge ID: challenge-ml_code_predictor-1765981050-376430")
    print("*" * 70)
    print()
    
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
    
    for example in examples:
        example()
    
    print("*" * 70)
    print(" All examples completed successfully!")
    print("*" * 70)
    print()


if __name__ == '__main__':
    main()
