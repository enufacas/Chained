"""
Example Usage - Code Completion Predictor

Demonstrates various use cases of the Code Completion Predictor by @create-botter.
Challenge ID: challenge-ml_code_predictor-1766499383-908922
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.code_completion_predictor import train_model, CodeCompletionPredictor


def example_1_python_basics():
    """Example 1: Basic Python function completion"""
    print("=" * 70)
    print("Example 1: Python Function Completion")
    print("=" * 70)
    print()
    
    # Training data
    training_code = [
        """
def add(a, b):
    return a + b
        """,
        """
def multiply(x, y):
    return x * y
        """,
        """
def subtract(a, b):
    result = a - b
    return result
        """,
        """
def divide(a, b):
    if b == 0:
        return None
    return a / b
        """
    ]
    
    print("📚 Training model on Python functions...")
    model = train_model(training_code, language='python')
    print("✅ Training complete!")
    print()
    
    # Test Case 1: Predict next line
    print("🧪 Test Case 1: Predict next code line")
    print("-" * 70)
    context = "def modulo(a, b):"
    print(f"Context: {context}")
    print()
    
    predictions = model.predict_next_line(context, top_k=5)
    print("Predictions:")
    for i, (token, conf) in enumerate(predictions, 1):
        print(f"  {i}. {token:<20} confidence: {conf:.3f}")
    print()
    
    # Test Case 2: Complete function
    print("🧪 Test Case 2: Complete function")
    print("-" * 70)
    partial = "def square(x):"
    print(f"Partial: {partial}")
    print()
    
    completions = model.complete_function(partial, top_k=3)
    print("Completions:")
    for i, (comp, conf) in enumerate(completions, 1):
        print(f"  {i}. Confidence: {conf:.3f}")
        print(f"     {partial} {comp}")
        print()


def example_2_javascript_arrow_functions():
    """Example 2: JavaScript arrow functions"""
    print("=" * 70)
    print("Example 2: JavaScript Arrow Functions")
    print("=" * 70)
    print()
    
    # JavaScript training data
    js_code = [
        "const add = (a, b) => a + b;",
        "const multiply = (x, y) => x * y;",
        "const subtract = (a, b) => { return a - b; }",
        "const divide = (a, b) => { if (b === 0) return null; return a / b; }",
        "const greet = (name) => `Hello, ${name}!`;",
        "const square = x => x * x;"
    ]
    
    print("📚 Training model on JavaScript code...")
    model = train_model(js_code, language='javascript', max_n=4)
    print("✅ Training complete!")
    print()
    
    # Predict arrow function body
    context = "const double = x =>"
    print(f"Context: {context}")
    print()
    
    predictions = model.predict_next_line(context, top_k=3)
    print("Predictions:")
    for i, (token, conf) in enumerate(predictions, 1):
        print(f"  {i}. {token:<20} confidence: {conf:.3f}")
    print()


def example_3_multi_language():
    """Example 3: Multi-language support"""
    print("=" * 70)
    print("Example 3: Multi-Language Support")
    print("=" * 70)
    print()
    
    languages = {
        'python': [
            "def fibonacci(n):\n    if n <= 1:\n        return n",
            "class Point:\n    def __init__(self, x, y):\n        self.x = x"
        ],
        'javascript': [
            "function factorial(n) { if (n <= 1) return 1; return n * factorial(n-1); }",
            "const isEmpty = arr => arr.length === 0;"
        ],
        'typescript': [
            "interface User { name: string; age: number; }",
            "type ID = string | number;"
        ]
    }
    
    for lang, code_samples in languages.items():
        print(f"\n📚 Training {lang.upper()} model...")
        model = train_model(code_samples, language=lang, max_n=3)
        
        # Different test contexts per language
        if lang == 'python':
            context = "def process():"
        elif lang == 'javascript':
            context = "const process = () =>"
        else:  # typescript
            context = "interface Product {"
        
        predictions = model.predict_next_line(context, top_k=3)
        
        print(f"Context: {context}")
        print("Top predictions:")
        for i, (token, conf) in enumerate(predictions, 1):
            print(f"  {i}. {token} ({conf:.3f})")


def example_4_class_completion():
    """Example 4: Class definition completion"""
    print("\n" + "=" * 70)
    print("Example 4: Class Definition Completion")
    print("=" * 70)
    print()
    
    # Training with class structures
    training_code = [
        """
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, x):
        self.result += x
        return self.result
    
    def reset(self):
        self.result = 0
        """,
        """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx**2 + dy**2)**0.5
        """,
        """
class BankAccount:
    def __init__(self, balance):
        self.balance = balance
    
    def deposit(self, amount):
        self.balance += amount
        return self.balance
        """
    ]
    
    print("📚 Training model on Python classes...")
    model = train_model(training_code, language='python', max_n=4)
    print("✅ Training complete!")
    print()
    
    # Complete a new class
    partial = """class Counter:
    def __init__(self):"""
    
    print("Partial class definition:")
    print(partial)
    print()
    
    completions = model.complete_function(partial, top_k=2)
    print("Suggested completions:")
    for i, (comp, conf) in enumerate(completions, 1):
        print(f"\n  {i}. Confidence: {conf:.3f}")
        print(f"     {partial} {comp}")


def example_5_control_flow():
    """Example 5: Control flow completion"""
    print("\n" + "=" * 70)
    print("Example 5: Control Flow Completion")
    print("=" * 70)
    print()
    
    training_code = [
        """
for i in range(10):
    if i % 2 == 0:
        print(i)
        """,
        """
while x > 0:
    x -= 1
    if x == 5:
        break
        """,
        """
if score >= 90:
    grade = 'A'
elif score >= 80:
    grade = 'B'
else:
    grade = 'C'
        """,
        """
for item in items:
    if item is None:
        continue
    process(item)
        """
    ]
    
    print("📚 Training model on control flow patterns...")
    model = train_model(training_code, language='python', max_n=4)
    print("✅ Training complete!")
    print()
    
    contexts = [
        "for i in range(20):",
        "if value > threshold:",
        "while running:"
    ]
    
    for context in contexts:
        print(f"Context: {context}")
        predictions = model.predict_next_line(context, top_k=3)
        print("Predictions:")
        for i, (token, conf) in enumerate(predictions, 1):
            print(f"  {i}. {token} ({conf:.3f})")
        print()


def example_6_performance_comparison():
    """Example 6: Performance and caching demonstration"""
    print("\n" + "=" * 70)
    print("Example 6: Performance & Caching")
    print("=" * 70)
    print()
    
    import time
    
    # Train model
    training_code = [
        "def add(a, b): return a + b" for _ in range(20)
    ] + [
        "def multiply(x, y): return x * y" for _ in range(20)
    ]
    
    print("📚 Training model...")
    model = train_model(training_code, language='python', max_n=4)
    print("✅ Training complete!")
    print()
    
    context = "def process(data):"
    
    # First call (cold)
    start = time.time()
    predictions = model.predict_next_line(context, top_k=5)
    cold_time = (time.time() - start) * 1000
    
    # Subsequent calls (cached)
    times = []
    for _ in range(100):
        start = time.time()
        _ = model.predict_next_line(context, top_k=5)
        times.append((time.time() - start) * 1000)
    
    cached_avg = sum(times) / len(times)
    
    print("⚡ Performance Results:")
    print(f"  Cold prediction:     {cold_time:.3f} ms")
    print(f"  Cached prediction:   {cached_avg:.3f} ms")
    print(f"  Speedup:             {cold_time/cached_avg:.1f}x")
    print()
    
    # Show cache statistics
    stats = model.get_stats()
    cache_stats = stats['cache_stats']
    print("📊 Cache Statistics:")
    print(f"  Cache size:          {cache_stats['cache_size']}")
    print(f"  Cache hits:          {cache_stats['cache_hits']}")
    print(f"  Cache misses:        {cache_stats['cache_misses']}")
    print(f"  Hit rate:            {cache_stats['hit_rate']:.1%}")


def main():
    """Run all examples"""
    print()
    print("🚀 Code Completion Predictor - Example Usage")
    print("Challenge ID: challenge-ml_code_predictor-1766499383-908922")
    print("Created by @create-botter")
    print()
    
    examples = [
        ("Python Basics", example_1_python_basics),
        ("JavaScript Arrow Functions", example_2_javascript_arrow_functions),
        ("Multi-Language Support", example_3_multi_language),
        ("Class Completion", example_4_class_completion),
        ("Control Flow", example_5_control_flow),
        ("Performance & Caching", example_6_performance_comparison)
    ]
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
    
    print("\n" + "=" * 70)
    print("✨ All examples completed!")
    print("=" * 70)
    print()
    print("Requirements demonstrated:")
    print("  ✅ Sequence prediction model")
    print("  ✅ Multi-language support")
    print("  ✅ Confidence scores")
    print("  ✅ Real-time inference")
    print()


if __name__ == '__main__':
    main()
