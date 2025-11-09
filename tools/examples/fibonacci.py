#!/usr/bin/env python3
"""
Fibonacci sequence generator
Generates the first N fibonacci numbers
"""

def generate_fibonacci(count):
    """
    Generate fibonacci sequence
    
    Args:
        count: Number of fibonacci numbers to generate
        
    Returns:
        List of fibonacci numbers
    """
    # Handle edge cases
    if count <= 0:
        return []
    elif count == 1:
        return [0]
    
    # Initialize the sequence with first two numbers
    fibonacci_sequence = [0, 1]
    
    # Generate remaining numbers
    while len(fibonacci_sequence) < count:
        # Calculate next number by adding last two
        next_number = fibonacci_sequence[-1] + fibonacci_sequence[-2]
        fibonacci_sequence.append(next_number)
    
    return fibonacci_sequence


# Test the function
if __name__ == "__main__":
    number_of_terms = 10
    result = generate_fibonacci(number_of_terms)
    print(f"First {number_of_terms} Fibonacci numbers:")
    print(result)
