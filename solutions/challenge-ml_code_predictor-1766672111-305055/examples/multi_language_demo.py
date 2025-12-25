"""
Example: Multi-Language Code Completion

Demonstrates code completion across different programming languages.
Challenge ID: challenge-ml_code_predictor-1766672111-305055
By @create-botter
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.code_completion_predictor import CodeCompletionPredictor, train_model


def demo_python():
    """Demo Python code completion"""
    print("=" * 70)
    print("Python Code Completion Demo")
    print("=" * 70)
    
    training_code = [
        'def validate_email(email): return "@" in email and "." in email',
        'def validate_phone(phone): return len(phone) == 10',
        'def validate_username(user): return len(user) >= 3',
        'def process_data(data): return data.strip().lower()',
        'if status == 200: return success',
        'if status == 404: return not_found',
    ]
    
    model = train_model(training_code, 'python')
    
    test_contexts = [
        'def validate_password(pwd): ',
        'if status == ',
        'def clean_input(text): return ',
    ]
    
    for context in test_contexts:
        line, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {line} (confidence: {conf:.0%})")
        print()


def demo_javascript():
    """Demo JavaScript code completion"""
    print("=" * 70)
    print("JavaScript Code Completion Demo")
    print("=" * 70)
    
    training_code = [
        'const add = (a, b) => a + b',
        'const subtract = (a, b) => a - b',
        'const multiply = (a, b) => a * b',
        'const divide = (a, b) => a / b',
        'if (status === 200) { return success; }',
        'if (status === 404) { return notFound; }',
    ]
    
    model = train_model(training_code, 'javascript')
    
    test_contexts = [
        'const modulo = (a, b) => ',
        'if (status === ',
        'const square = (x) => ',
    ]
    
    for context in test_contexts:
        line, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {line} (confidence: {conf:.0%})")
        print()


def demo_typescript():
    """Demo TypeScript code completion"""
    print("=" * 70)
    print("TypeScript Code Completion Demo")
    print("=" * 70)
    
    training_code = [
        'interface User { name: string; email: string; }',
        'interface Product { id: number; name: string; }',
        'interface Order { userId: number; productId: number; }',
        'type Status = "active" | "inactive"',
        'type Role = "admin" | "user"',
    ]
    
    model = train_model(training_code, 'typescript')
    
    test_contexts = [
        'interface Employee { ',
        'type Priority = ',
        'interface Config { ',
    ]
    
    for context in test_contexts:
        line, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {line} (confidence: {conf:.0%})")
        print()


def demo_java():
    """Demo Java code completion"""
    print("=" * 70)
    print("Java Code Completion Demo")
    print("=" * 70)
    
    training_code = [
        'public class User { private String name; }',
        'public class Product { private int id; }',
        'public int add(int a, int b) { return a + b; }',
        'public int subtract(int a, int b) { return a - b; }',
        'if (status == 200) { return success; }',
    ]
    
    model = train_model(training_code, 'java')
    
    test_contexts = [
        'public class Order { ',
        'public int multiply(int a, int b) { ',
        'if (status == ',
    ]
    
    for context in test_contexts:
        line, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {line} (confidence: {conf:.0%})")
        print()


def demo_go():
    """Demo Go code completion"""
    print("=" * 70)
    print("Go Code Completion Demo")
    print("=" * 70)
    
    training_code = [
        'func add(a int, b int) int { return a + b }',
        'func subtract(a int, b int) int { return a - b }',
        'func multiply(a int, b int) int { return a * b }',
        'type User struct { Name string; Email string }',
        'type Product struct { ID int; Name string }',
    ]
    
    model = train_model(training_code, 'go')
    
    test_contexts = [
        'func divide(a int, b int) int { ',
        'type Order struct { ',
        'func square(x int) int { ',
    ]
    
    for context in test_contexts:
        line, conf = model.predict_next_line(context)
        print(f"Context:    {context}")
        print(f"Prediction: {line} (confidence: {conf:.0%})")
        print()


if __name__ == '__main__':
    print("\n")
    print("*" * 70)
    print("Multi-Language Code Completion Demo - @create-botter")
    print(f"Challenge ID: {CodeCompletionPredictor.CHALLENGE_ID}")
    print("*" * 70)
    print("\n")
    
    demo_python()
    demo_javascript()
    demo_typescript()
    demo_java()
    demo_go()
    
    print("*" * 70)
    print("All language demos complete! ✨")
    print("*" * 70)
