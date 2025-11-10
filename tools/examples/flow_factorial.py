#!/usr/bin/env python3
"""
Example: Factorial Calculator
Demonstrates recursive function calls and return flow
"""

def factorial(n):
    """Calculate factorial of n recursively"""
    if n <= 1:
        return 1
    else:
        result = n * factorial(n - 1)
        return result


def factorial_iterative(n):
    """Calculate factorial of n iteratively"""
    result = 1
    for i in range(2, n + 1):
        result = result * i
    return result


def main():
    """Main function to test factorial calculations"""
    number = 5
    
    # Test recursive version
    recursive_result = factorial(number)
    print(f"Factorial of {number} (recursive): {recursive_result}")
    
    # Test iterative version
    iterative_result = factorial_iterative(number)
    print(f"Factorial of {number} (iterative): {iterative_result}")
    
    # Verify both give same result
    if recursive_result == iterative_result:
        print("Both methods produce the same result!")
    
    return recursive_result


if __name__ == "__main__":
    main()
