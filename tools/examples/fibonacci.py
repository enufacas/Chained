#!/usr/bin/env python3
"""
Fibonacci Sequence Generator

The Fibonacci sequence is nature's mathematical poetry,
where each number is born from the sum of its two predecessors.
A recursive pattern found in spirals, flowers, and growth.
"""

from typing import List


def generate_fibonacci(count: int) -> List[int]:
    """
    Generate the Fibonacci sequence.
    
    The sequence begins: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34...
    where each term is the sum of the two preceding ones.
    
    Args:
        count: Number of Fibonacci numbers to generate
        
    Returns:
        List of Fibonacci numbers
        
    Raises:
        ValueError: If count is negative
        
    Example:
        >>> generate_fibonacci(5)
        [0, 1, 1, 2, 3]
    """
    if count < 0:
        raise ValueError("Count must be non-negative")
    
    if count == 0:
        return []
    
    if count == 1:
        return [0]
    
    # Initialize with the first two numbers of the sequence
    sequence = [0, 1]
    
    # Generate each subsequent number from the previous two
    while len(sequence) < count:
        next_number = sequence[-1] + sequence[-2]
        sequence.append(next_number)
    
    return sequence


def fibonacci_generator(max_count: int):
    """
    Generate Fibonacci numbers lazily using a generator.
    
    Memory-efficient for large sequences, yielding one number at a time.
    
    Args:
        max_count: Maximum number of terms to generate
        
    Yields:
        Next Fibonacci number in the sequence
    """
    if max_count <= 0:
        return
    
    current, next_value = 0, 1
    for _ in range(max_count):
        yield current
        current, next_value = next_value, current + next_value


def main():
    """Demonstrate Fibonacci sequence generation."""
    print("🌀 Fibonacci Sequence Generator\n")
    
    # Generate and display the sequence
    number_of_terms = 10
    sequence = generate_fibonacci(number_of_terms)
    
    print(f"First {number_of_terms} Fibonacci numbers:")
    print(sequence)
    print()
    
    # Show the golden ratio approximation
    if len(sequence) >= 2:
        ratio = sequence[-1] / sequence[-2] if sequence[-2] != 0 else 0
        golden_ratio = 1.618033988749
        print(f"Ratio of last two terms: {ratio:.9f}")
        print(f"Golden ratio (φ):        {golden_ratio:.9f}")
        print(f"Difference:              {abs(ratio - golden_ratio):.9f}")


if __name__ == "__main__":
    main()
