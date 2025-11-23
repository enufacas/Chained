"""
Usage Examples for Code Completion Predictor
Created by @create-guru

Comprehensive examples demonstrating all features.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.code_completion_predictor import (
    CodeCompletionPredictor,
    train_model
)


def example_1_basic_completion():
    """Example 1: Basic code completion."""
    print("=" * 70)
    print("Example 1: Basic Code Completion")
    print("=" * 70)
    
    training = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b'
    ]
    
    model = train_model(training, 'python', n=5)
    
    context = 'def divide(a, b): '
    line, confidence = model.predict_next_line(context)
    
    print(f"Context:    {context}")
    print(f"Prediction: {line}")
    print(f"Confidence: {confidence:.0%}")
    print()


def example_2_multi_language():
    """Example 2: Multi-language support."""
    print("=" * 70)
    print("Example 2: Multi-Language Support")
    print("=" * 70)
    
    # Python
    print("\n📘 Python:")
    py_model = train_model([
        'def validate(x): return x > 0',
        'def process(x): return x * 2'
    ], 'python')
    
    py_line, py_conf = py_model.predict_next_line('def transform(x): ')
    print(f"  Prediction: {py_line} ({py_conf:.0%})")
    
    # JavaScript
    print("\n📗 JavaScript:")
    js_model = train_model([
        'const square = x => x * x',
        'const double = x => x * 2'
    ], 'javascript')
    
    js_line, js_conf = js_model.predict_next_line('const triple = x => ')
    print(f"  Prediction: {js_line} ({js_conf:.0%})")
    
    # Java
    print("\n📙 Java:")
    java_model = train_model([
        'public int add(int a, int b) { return a + b; }',
        'public int multiply(int a, int b) { return a * b; }'
    ], 'java')
    
    java_line, java_conf = java_model.predict_next_line('public int subtract(int a, int b) { ')
    print(f"  Prediction: {java_line} ({java_conf:.0%})")
    print()


def example_3_function_completion():
    """Example 3: Function completion."""
    print("=" * 70)
    print("Example 3: Function Completion")
    print("=" * 70)
    
    training = [
        'def validate_email(email):\n    return "@" in email',
        'def validate_phone(phone):\n    return len(phone) == 10',
        'def validate_url(url):\n    return url.startswith("http")'
    ]
    
    model = train_model(training, 'python', n=5)
    
    partial = 'def validate_username(username):\n    '
    completion, confidence = model.complete_function(partial)
    
    print("Partial function:")
    print(partial)
    print("\nPredicted completion:")
    print(f"{completion} (confidence: {confidence:.0%})")
    print()


def example_4_beam_search():
    """Example 4: Beam search for multiple predictions."""
    print("=" * 70)
    print("Example 4: Beam Search (Top-K Predictions)")
    print("=" * 70)
    
    training = [
        'if x == 0: return True',
        'if x == 1: return False',
        'if x > 0: return None',
        'if x < 0: return -1'
    ]
    
    model = train_model(training, 'python', n=5)
    
    context = 'if x '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"Context: {context}")
    print("\nTop predictions:")
    for i, (pred, conf) in enumerate(predictions, 1):
        print(f"  {i}. {pred:15} ({conf:.0%})")
    print()


def example_5_model_persistence():
    """Example 5: Save and load models."""
    print("=" * 70)
    print("Example 5: Model Persistence")
    print("=" * 70)
    
    import tempfile
    
    # Train and save
    print("Training model...")
    model1 = train_model([
        'for i in range(10): print(i)',
        'for j in range(20): print(j)'
    ], 'python')
    
    temp_file = tempfile.mktemp(suffix='.json')
    model1.save_model(temp_file)
    print(f"✓ Model saved to {temp_file}")
    
    # Load and use
    print("Loading model...")
    model2 = CodeCompletionPredictor('python')
    model2.load_model(temp_file)
    print("✓ Model loaded")
    
    line, conf = model2.predict_next_line('for k in range(30): ')
    print(f"\nPrediction: {line} ({conf:.0%})")
    
    # Cleanup
    os.unlink(temp_file)
    print()


def example_6_real_world_patterns():
    """Example 6: Learning real-world coding patterns."""
    print("=" * 70)
    print("Example 6: Real-World Coding Patterns")
    print("=" * 70)
    
    # Common Python patterns
    training = [
        'if data is None: return []',
        'if items is None: return []',
        'if value is None: return {}',
        'if result is None: return None',
        'def process(data): return data.strip().lower()',
        'def validate(item): return item is not None',
        'for item in items: result.append(item)',
        'for value in values: output.append(value)'
    ]
    
    model = train_model(training, 'python', n=5)
    
    test_cases = [
        'if config is None: ',
        'def format(text): ',
        'for element in elements: '
    ]
    
    for test in test_cases:
        line, conf = model.predict_next_line(test)
        print(f"Pattern: {test}")
        print(f"Learned: {line} ({conf:.0%})")
        print()


def example_7_statistics():
    """Example 7: Model statistics and insights."""
    print("=" * 70)
    print("Example 7: Model Statistics")
    print("=" * 70)
    
    model = train_model([
        'def foo(): return 42',
        'def bar(): return 100',
        'def baz(): return 200',
        'class MyClass: pass',
        'class OtherClass: pass'
    ], 'python', n=5)
    
    stats = model.get_stats()
    
    print(f"Language:         {stats['language']}")
    print(f"Vocabulary Size:  {stats['vocabulary_size']} tokens")
    print(f"Total N-grams:    {stats['total_ngrams']}")
    print(f"Cache Hit Rate:   {stats['cache_hit_rate']:.0%}")
    print(f"\nN-gram breakdown:")
    for order, count in sorted(stats['ngram_counts'].items()):
        print(f"  Order {order}: {count} N-grams")
    print()


def example_8_typescript():
    """Example 8: TypeScript support."""
    print("=" * 70)
    print("Example 8: TypeScript Support")
    print("=" * 70)
    
    training = [
        'interface User { name: string; age: number; }',
        'interface Product { id: string; price: number; }',
        'type Status = "active" | "inactive"',
        'function process<T>(item: T): T { return item; }'
    ]
    
    model = train_model(training, 'typescript', n=5)
    
    context = 'interface Order { '
    line, conf = model.predict_next_line(context)
    
    print(f"Context:    {context}")
    print(f"Prediction: {line}")
    print(f"Confidence: {conf:.0%}")
    print()


def run_all_examples():
    """Run all usage examples."""
    print()
    print("█" * 70)
    print("  CODE COMPLETION PREDICTOR - USAGE EXAMPLES")
    print("  Created by @create-guru")
    print("█" * 70)
    print()
    
    examples = [
        example_1_basic_completion,
        example_2_multi_language,
        example_3_function_completion,
        example_4_beam_search,
        example_5_model_persistence,
        example_6_real_world_patterns,
        example_7_statistics,
        example_8_typescript
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in example: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 70)
    print("✅ All examples completed")
    print()
    print("Features demonstrated:")
    print("  ✓ Basic code completion")
    print("  ✓ Multi-language support (Python, JS, Java, TypeScript)")
    print("  ✓ Function completion")
    print("  ✓ Beam search (top-k predictions)")
    print("  ✓ Model persistence (save/load)")
    print("  ✓ Real-world pattern learning")
    print("  ✓ Model statistics and insights")
    print()
    print("=" * 70)
    print("🚀 Built with Tesla-inspired innovation by @create-guru")
    print("=" * 70)


if __name__ == '__main__':
    run_all_examples()
