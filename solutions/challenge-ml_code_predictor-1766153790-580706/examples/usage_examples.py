"""
Usage Examples for Code Completion Predictor

Practical demonstrations of the Code Completion Predictor by @create-botter.
Challenge ID: challenge-ml_code_predictor-1766153790-580706

This file shows 8 different ways to use the predictor.
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
        'def validate_email(email): return "@" in email and "." in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def validate_username(user): return len(user) >= 3',
    ]
    
    # Train model
    model = train_model(training_code, language='python')
    
    # Predict
    context = 'def validate_password(pwd): '
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
    py_model.train(['def add(a, b): return a + b'])
    line, conf = py_model.predict_next_line('def multiply(a, b): ')
    print(f"Python:     {line} ({conf:.0%})")
    
    # JavaScript
    js_model = CodeCompletionPredictor('javascript')
    js_model.train(['const add = (a, b) => a + b'])
    line, conf = js_model.predict_next_line('const multiply = (a, b) => ')
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
    
    training_code = [
        'def calculate_area(width, height): return width * height',
        'def calculate_volume(w, h, d): return w * h * d',
    ]
    
    model = train_model(training_code, 'python')
    
    partial = 'def calculate_perimeter(width, height):\n    '
    completion, conf = model.complete_function(partial)
    
    print(f"Partial function:\n{partial}")
    print(f"Completion: {completion} ({conf:.0%})")
    print()


def example_4_beam_search():
    """Example 4: Beam search (multiple predictions)"""
    print("=" * 70)
    print("Example 4: Beam Search - Multiple Predictions")
    print("=" * 70)
    
    training_code = [
        'if status == 200: return success',
        'if status == 404: return not_found',
        'if status == 500: return error',
        'if status == 201: return created',
    ]
    
    model = train_model(training_code, 'python')
    
    # Get top 3 predictions
    predictions = model.get_predictions('if status == ', top_k=3)
    
    print("Context: if status == ")
    print("\nTop predictions:")
    for i, (token, conf) in enumerate(predictions, 1):
        print(f"  {i}. {token:10} ({conf:.0%})")
    print()


def example_5_model_persistence():
    """Example 5: Save and load models"""
    print("=" * 70)
    print("Example 5: Model Persistence (Save/Load)")
    print("=" * 70)
    
    import tempfile
    import os
    
    # Train model
    training_code = ['def foo(): return 42', 'def bar(): return 100']
    model = train_model(training_code, 'python')
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        model_path = f.name
    
    try:
        model.save_model(model_path)
        print(f"✅ Model saved to {model_path}")
        
        # Load in new model
        new_model = CodeCompletionPredictor('python')
        new_model.load_model(model_path)
        print(f"✅ Model loaded from {model_path}")
        
        # Test prediction
        line, conf = new_model.predict_next_line('def baz(): ')
        print(f"Prediction: {line} ({conf:.0%})")
    finally:
        os.unlink(model_path)
        print(f"✅ Cleaned up temporary file")
    
    print()


def example_6_real_world_patterns():
    """Example 6: Real-world coding patterns"""
    print("=" * 70)
    print("Example 6: Real-World Coding Patterns")
    print("=" * 70)
    
    # More realistic training data
    training_code = [
        'import json',
        'import os',
        'import sys',
        'from pathlib import Path',
        'from typing import List, Dict',
        'def load_config(path): return json.load(open(path))',
        'def save_data(data, path): json.dump(data, open(path, "w"))',
        'try: result = process_data()',
        'except ValueError: return None',
        'except Exception as e: print(f"Error: {e}")',
    ]
    
    model = train_model(training_code, 'python')
    
    # Test various contexts
    contexts = [
        'import ',
        'from typing import ',
        'try: data = ',
        'except ',
    ]
    
    for context in contexts:
        line, conf = model.predict_next_line(context, max_tokens=3)
        print(f"{context:25} → {line:20} ({conf:.0%})")
    print()


def example_7_performance_stats():
    """Example 7: Performance statistics"""
    print("=" * 70)
    print("Example 7: Model Performance Statistics")
    print("=" * 70)
    
    # Create and train model
    training_code = [
        'def add(a, b): return a + b',
        'def sub(a, b): return a - b',
        'if x > 0: return True',
        'if x < 0: return False',
        'for i in range(10): print(i)',
    ]
    
    model = train_model(training_code, 'python', n=5)
    
    # Get statistics
    stats = model.get_stats()
    
    print(f"Challenge ID:      {stats['challenge_id']}")
    print(f"Language:          {stats['language']}")
    print(f"N-gram order:      {stats['n']}")
    print(f"Vocabulary size:   {stats['vocabulary_size']} tokens")
    print(f"Cache size:        {stats['cache_size']} entries")
    print(f"Cache hit rate:    {stats['cache_hit_rate']:.0%}")
    print(f"N-gram counts:     {stats['ngram_counts']}")
    print()


def example_8_typescript_advanced():
    """Example 8: Advanced TypeScript patterns"""
    print("=" * 70)
    print("Example 8: TypeScript Advanced Patterns")
    print("=" * 70)
    
    training_code = [
        'interface User { name: string; email: string; }',
        'interface Product { id: number; name: string; }',
        'type Result<T> = { success: true; data: T }',
        'type Error = { success: false; error: string }',
        'const fetchUser = async (id: number): Promise<User> => {}',
        'const fetchProduct = async (id: number): Promise<Product> => {}',
    ]
    
    model = train_model(training_code, 'typescript')
    
    # Test TypeScript-specific patterns
    contexts = [
        'interface Order { ',
        'type Status = { ',
        'const fetchOrder = async (id: number): ',
    ]
    
    for context in contexts:
        line, conf = model.predict_next_line(context, max_tokens=5)
        print(f"Context:    {context}")
        print(f"Prediction: {line} ({conf:.0%})")
        print()


def main():
    """Run all examples"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Code Completion Predictor - Usage Examples".center(68) + "║")
    print("║" + "  by @create-botter".center(68) + "║")
    print("║" + f"  Challenge ID: challenge-ml_code_predictor-1766153790-580706".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
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
        input("Press Enter to continue...")
        print("\n")
    
    print("=" * 70)
    print("All examples completed! ✨")
    print("=" * 70)


if __name__ == '__main__':
    main()
