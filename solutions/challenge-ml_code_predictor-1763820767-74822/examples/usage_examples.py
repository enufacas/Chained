"""
Usage Examples for Code Completion Predictor

Demonstrates various use cases and features of the code completion system.
Created by @create-guru to showcase the model's capabilities.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.code_completion_predictor import (
    CodeCompletionPredictor,
    train_model
)


def example_1_basic_usage():
    """Example 1: Basic code completion."""
    print("="*70)
    print("Example 1: Basic Code Completion")
    print("="*70)
    
    # Training data
    training_code = [
        'def add(a, b): return a + b',
        'def subtract(a, b): return a - b',
        'def multiply(a, b): return a * b',
        'def divide(a, b): return a / b'
    ]
    
    # Train model
    model = train_model(training_code, language='python')
    
    # Predict next line
    context = 'def modulo(a, b): '
    predicted, confidence = model.predict_next_line(context)
    
    print(f"\nContext: {context}")
    print(f"Prediction: {predicted}")
    print(f"Confidence: {confidence:.1%}")
    print()


def example_2_multi_language():
    """Example 2: Multi-language support."""
    print("="*70)
    print("Example 2: Multi-Language Support")
    print("="*70)
    
    # Python
    print("\n📘 Python:")
    python_model = CodeCompletionPredictor('python')
    python_model.train(['def validate(x): return x > 0'])
    line, conf = python_model.predict_next_line('def check(y): ')
    print(f"  Prediction: {line} ({conf:.0%})")
    
    # JavaScript
    print("\n📙 JavaScript:")
    js_model = CodeCompletionPredictor('javascript')
    js_model.train(['const validate = (x) => x > 0'])
    line, conf = js_model.predict_next_line('const check = (y) => ')
    print(f"  Prediction: {line} ({conf:.0%})")
    
    # Java
    print("\n📕 Java:")
    java_model = CodeCompletionPredictor('java')
    java_model.train(['public boolean validate(int x) { return x > 0; }'])
    line, conf = java_model.predict_next_line('public boolean check(int y) { ')
    print(f"  Prediction: {line} ({conf:.0%})")
    
    print()


def example_3_function_completion():
    """Example 3: Complete partial functions."""
    print("="*70)
    print("Example 3: Function Completion")
    print("="*70)
    
    training_data = [
        """
        def process_user(user):
            if user is None:
                return None
            if not user.is_active:
                return None
            return user
        """,
        """
        def process_order(order):
            if order is None:
                return None
            if not order.is_valid:
                return None
            return order
        """
    ]
    
    model = train_model(training_data, 'python')
    
    # Partial function
    partial = "def process_payment(payment):\n    if payment is None:\n        "
    
    completion, confidence = model.complete_function(partial)
    
    print(f"\nPartial function:")
    print(partial)
    print(f"\nCompleted with: {completion}")
    print(f"Confidence: {confidence:.1%}")
    print()


def example_4_beam_search():
    """Example 4: Multiple prediction options (beam search)."""
    print("="*70)
    print("Example 4: Beam Search - Multiple Predictions")
    print("="*70)
    
    training_data = [
        'if status == 200: return success',
        'if status == 404: return not_found',
        'if status == 500: return error',
        'if status == 201: return created',
        'if status == 401: return unauthorized'
    ]
    
    model = train_model(training_data, 'python')
    
    # Get top 5 predictions
    context = 'if status == '
    predictions = model.get_predictions(context, top_k=5)
    
    print(f"\nContext: {context}")
    print("\nTop predictions:")
    for i, (pred, conf) in enumerate(predictions, 1):
        print(f"  {i}. {pred:25} ({conf:.0%})")
    
    print()


def example_5_model_persistence():
    """Example 5: Save and load models."""
    print("="*70)
    print("Example 5: Model Persistence")
    print("="*70)
    
    import tempfile
    
    # Train a model
    training_data = [
        'def calculate_tax(amount): return amount * 0.08',
        'def calculate_discount(amount): return amount * 0.15',
        'def calculate_total(amount): return amount * 1.08'
    ]
    
    model = train_model(training_data, 'python')
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name
    
    print(f"\nSaving model to: {temp_path}")
    model.save_model(temp_path)
    print("✓ Model saved!")
    
    # Load into new model
    print("\nLoading model...")
    new_model = CodeCompletionPredictor('python')
    new_model.load_model(temp_path)
    print("✓ Model loaded!")
    
    # Test prediction
    line, conf = new_model.predict_next_line('def calculate_fee(amount): ')
    print(f"\nPrediction from loaded model: {line} ({conf:.0%})")
    
    # Clean up
    os.remove(temp_path)
    print()


def example_6_real_world_patterns():
    """Example 6: Real-world code patterns."""
    print("="*70)
    print("Example 6: Real-World Code Patterns")
    print("="*70)
    
    # Common web development patterns
    training_data = [
        """
        @app.route('/api/users', methods=['GET'])
        def get_users():
            users = User.query.all()
            return jsonify([u.to_dict() for u in users])
        """,
        """
        @app.route('/api/posts', methods=['GET'])
        def get_posts():
            posts = Post.query.all()
            return jsonify([p.to_dict() for p in posts])
        """,
        """
        @app.route('/api/comments', methods=['GET'])
        def get_comments():
            comments = Comment.query.all()
            return jsonify([c.to_dict() for c in comments])
        """
    ]
    
    model = train_model(training_data, 'python', n=7)
    
    test_cases = [
        ("@app.route('/api/orders', methods=['GET'])\ndef get_orders():\n    orders = Order.query.all()\n    ", "API endpoint pattern"),
        ("users = User.query.", "Query pattern"),
        ("return jsonify([", "JSON response pattern")
    ]
    
    print("\nPredictions for common patterns:")
    for context, description in test_cases:
        pred, conf = model.predict_next_line(context)
        print(f"\n{description}:")
        print(f"  Context: ...{context[-40:]}")
        print(f"  Predicted: {pred} ({conf:.0%})")
    
    print()


def example_7_performance_stats():
    """Example 7: Model statistics and performance."""
    print("="*70)
    print("Example 7: Model Statistics")
    print("="*70)
    
    training_data = [
        'def validate(x): return x > 0',
        'def process(y): return y * 2',
        'def calculate(z): return z + 10'
    ] * 10  # Repeat for more data
    
    model = train_model(training_data, 'python', n=5)
    
    # Make some predictions (for cache stats)
    model.predict_next_line('def test(): ')
    model.predict_next_line('def test(): ')  # Cached
    model.predict_next_line('if x > 0: ')
    
    # Get statistics
    stats = model.get_stats()
    
    print("\nModel Statistics:")
    print(f"  Language: {stats['language']}")
    print(f"  N-gram order: {stats['n']}")
    print(f"  Vocabulary size: {stats['vocabulary_size']} unique tokens")
    print(f"  Training sequences: {stats['total_sequences']}")
    print(f"  Cache hit rate: {stats['cache_hit_rate']:.1%}")
    print(f"  Cache hits: {stats['cache_hits']}")
    print(f"  Cache misses: {stats['cache_misses']}")
    
    print("\nN-gram counts by order:")
    for order, count in sorted(stats['ngram_counts'].items()):
        print(f"  {order}-grams: {count}")
    
    print()


def example_8_typescript_support():
    """Example 8: TypeScript code completion."""
    print("="*70)
    print("Example 8: TypeScript Support")
    print("="*70)
    
    training_data = [
        """
        interface User {
            id: number;
            name: string;
            email: string;
        }
        """,
        """
        interface Post {
            id: number;
            title: string;
            content: string;
        }
        """,
        """
        interface Comment {
            id: number;
            text: string;
            author: string;
        }
        """
    ]
    
    model = train_model(training_data, 'typescript', n=6)
    
    test_cases = [
        ("interface Product {\n    id: ", "Interface definition"),
        ("const user: User = { id: 1, name: ", "Object literal"),
        ("function getUser(id: number): ", "Function signature")
    ]
    
    print("\nTypeScript predictions:")
    for context, description in test_cases:
        pred, conf = model.predict_next_line(context)
        print(f"\n{description}:")
        print(f"  Context: {context}")
        print(f"  Predicted: {pred} ({conf:.0%})")
    
    print()


def main():
    """Run all examples."""
    print("\n" + "🚀 "*25)
    print("Code Completion Predictor - Usage Examples by @create-guru")
    print("🚀 "*25 + "\n")
    
    examples = [
        example_1_basic_usage,
        example_2_multi_language,
        example_3_function_completion,
        example_4_beam_search,
        example_5_model_persistence,
        example_6_real_world_patterns,
        example_7_performance_stats,
        example_8_typescript_support
    ]
    
    for example in examples:
        try:
            example()
            input("Press Enter to continue to next example...")
            print("\n")
        except KeyboardInterrupt:
            print("\n\nExamples interrupted by user.")
            break
    
    print("="*70)
    print("✅ All examples completed!")
    print("="*70)
    print("\nFor more information, see:")
    print("  - README.md: Full documentation")
    print("  - tests/: Comprehensive test suite")
    print("  - src/code_completion_predictor.py: Implementation details")
    print("\nCreated by @create-guru with ⚡ innovative architecture")
    print()


if __name__ == '__main__':
    main()
