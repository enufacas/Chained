"""
Usage Examples for Code Completion Predictor

Demonstrates the key features of the Code Completion Predictor:
- Basic code completion
- Multi-language support
- Function completion
- Beam search (multiple predictions)
- Model persistence
- Real-world patterns
- Performance statistics

Challenge ID: challenge-ml_code_predictor-1764080154-287095
Created by @create-guru
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.code_completion_predictor import CodeCompletionPredictor, train_model


def example_1_basic_completion():
    """Example 1: Basic Code Completion"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Code Completion")
    print("=" * 60)
    
    # Train model on sample code
    training_code = [
        'def validate_email(email): return "@" in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def validate_name(name): return len(name) > 2',
    ]
    
    model = train_model(training_code, language='python')
    
    # Predict next line
    context = 'def validate_username(user): '
    line, confidence = model.predict_next_line(context)
    
    print(f"Training samples: {len(training_code)}")
    print(f"Context: {context}")
    print(f"Prediction: {line}")
    print(f"Confidence: {confidence:.1%}")


def example_2_multi_language():
    """Example 2: Multi-Language Support"""
    print("\n" + "=" * 60)
    print("Example 2: Multi-Language Support")
    print("=" * 60)
    
    # Python
    py_model = train_model(['def add(a, b): return a + b'], 'python')
    py_line, py_conf = py_model.predict_next_line('def sub(a, b): ')
    print(f"Python: {py_line} ({py_conf:.1%})")
    
    # JavaScript
    js_model = train_model(['const add = (a, b) => a + b'], 'javascript')
    js_line, js_conf = js_model.predict_next_line('const sub = (a, b) => ')
    print(f"JavaScript: {js_line} ({js_conf:.1%})")
    
    # TypeScript
    ts_model = train_model(['const greet = (name: string): string => name'], 'typescript')
    ts_line, ts_conf = ts_model.predict_next_line('const welcome = (user: string): ')
    print(f"TypeScript: {ts_line} ({ts_conf:.1%})")
    
    # Java
    java_model = train_model(['public int add(int a, int b) { return a + b; }'], 'java')
    java_line, java_conf = java_model.predict_next_line('public int sub(int a, int b) { ')
    print(f"Java: {java_line} ({java_conf:.1%})")
    
    # Go
    go_model = train_model(['func add(a, b int) int { return a + b }'], 'go')
    go_line, go_conf = go_model.predict_next_line('func sub(a, b int) int { ')
    print(f"Go: {go_line} ({go_conf:.1%})")


def example_3_function_completion():
    """Example 3: Function Completion"""
    print("\n" + "=" * 60)
    print("Example 3: Function Completion")
    print("=" * 60)
    
    training_code = [
        'def process_data(data):\n    if not data:\n        return None\n    return data.strip()',
        'def validate_input(x):\n    if x < 0:\n        return False\n    return True',
    ]
    
    model = train_model(training_code, language='python')
    
    partial = 'def check_value(val):\n    if val < 0:\n        '
    completion, confidence = model.complete_function(partial)
    
    print(f"Partial function:")
    print(f"  {partial}")
    print(f"Completion: {completion}")
    print(f"Confidence: {confidence:.1%}")


def example_4_beam_search():
    """Example 4: Beam Search (Multiple Predictions)"""
    print("\n" + "=" * 60)
    print("Example 4: Beam Search (Multiple Predictions)")
    print("=" * 60)
    
    training_code = [
        'if status == 200: return True',
        'if status == 404: return None',
        'if status == 500: raise Exception("error")',
        'if status == 301: redirect()',
        'if status == 400: return "bad request"',
    ]
    
    model = train_model(training_code, language='python')
    
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"Context: {context}")
    print("Top 5 predictions:")
    for token, conf in predictions:
        print(f"  {token}: {conf:.1%}")


def example_5_model_persistence():
    """Example 5: Model Persistence"""
    print("\n" + "=" * 60)
    print("Example 5: Model Persistence")
    print("=" * 60)
    
    import tempfile
    
    # Train model
    training_code = ['def foo(): return 42', 'def bar(): return 100']
    model = train_model(training_code, language='python')
    
    # Make prediction before save
    line1, conf1 = model.predict_next_line('def baz(): ')
    print(f"Before save: {line1} ({conf1:.1%})")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        temp_path = f.name
    
    model.save_model(temp_path)
    print(f"Model saved to: {temp_path}")
    
    # Load into new model
    new_model = CodeCompletionPredictor('python')
    new_model.load_model(temp_path)
    
    # Make prediction after load
    line2, conf2 = new_model.predict_next_line('def baz(): ')
    print(f"After load: {line2} ({conf2:.1%})")
    
    # Cleanup
    os.unlink(temp_path)
    print(f"Predictions match: {line1 == line2}")


def example_6_real_world_patterns():
    """Example 6: Real-World Code Patterns"""
    print("\n" + "=" * 60)
    print("Example 6: Real-World Code Patterns")
    print("=" * 60)
    
    # Common Python patterns
    training_code = [
        'def __init__(self, name): self.name = name',
        'def __init__(self, value): self.value = value',
        'def __str__(self): return f"{self.name}"',
        'def __repr__(self): return f"<{self.__class__.__name__}>"',
        'def get_name(self): return self.name',
        'def set_name(self, name): self.name = name',
        'try:\n    result = process()\nexcept Exception as e:\n    log.error(e)',
        'with open(path) as f:\n    data = f.read()',
    ]
    
    model = train_model(training_code, language='python', n=4)
    
    patterns = [
        'def __init__(self, data): ',
        'def get_value(self): ',
        'with open(file) as f:\n    ',
    ]
    
    for context in patterns:
        line, conf = model.predict_next_line(context)
        print(f"Context: {context[:40]}...")
        print(f"  → {line} ({conf:.1%})")


def example_7_statistics():
    """Example 7: Performance Statistics"""
    print("\n" + "=" * 60)
    print("Example 7: Performance Statistics")
    print("=" * 60)
    
    training_code = [
        'def add(a, b): return a + b',
        'def sub(a, b): return a - b',
        'def mul(a, b): return a * b',
        'def div(a, b): return a / b',
    ]
    
    model = train_model(training_code, language='python', n=5)
    
    # Make some predictions to build cache
    for _ in range(5):
        model.predict_next_line('def compute(x, y): ')
    
    # Get statistics
    stats = model.get_stats()
    
    print(f"Challenge ID: {stats['challenge_id']}")
    print(f"Language: {stats['language']}")
    print(f"N-gram order: {stats['n']}")
    print(f"Vocabulary size: {stats['vocabulary_size']} tokens")
    print(f"Training samples: {stats['training_samples']}")
    print(f"Cache size: {stats['cache_size']} entries")
    print(f"Cache hit rate: {stats['cache_hit_rate']:.1%}")
    print(f"N-gram counts: {stats['ngram_counts']}")


def example_8_typescript_advanced():
    """Example 8: TypeScript Advanced"""
    print("\n" + "=" * 60)
    print("Example 8: TypeScript Advanced")
    print("=" * 60)
    
    training_code = [
        'interface User { name: string; age: number; }',
        'interface Product { id: string; price: number; }',
        'const getUser = async (id: string): Promise<User> => fetch(url)',
        'const fetchData = async (): Promise<Data[]> => await api.get()',
        'type Status = "pending" | "active" | "done"',
    ]
    
    model = train_model(training_code, language='typescript', n=4)
    
    contexts = [
        'interface Order { ',
        'const getData = async (key: string): ',
    ]
    
    for context in contexts:
        line, conf = model.predict_next_line(context)
        print(f"Context: {context}")
        print(f"  → {line} ({conf:.1%})")


def main():
    """Run all examples."""
    print("=" * 60)
    print("Code Completion Predictor - Usage Examples")
    print("Challenge ID: challenge-ml_code_predictor-1764080154-287095")
    print("Created by @create-guru")
    print("=" * 60)
    
    example_1_basic_completion()
    example_2_multi_language()
    example_3_function_completion()
    example_4_beam_search()
    example_5_model_persistence()
    example_6_real_world_patterns()
    example_7_statistics()
    example_8_typescript_advanced()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
