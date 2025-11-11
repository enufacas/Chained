#!/usr/bin/env python3
"""
Prime Number Checker

Prime numbers are the atoms of mathematics - indivisible,
fundamental building blocks from which all other numbers are composed.
They stand alone, divisible only by themselves and one.
"""

import math
from typing import List, Iterator


def is_prime(number: int) -> bool:
    """
    Determine if a number is prime.
    
    A prime number is a natural number greater than 1 that has
    no positive divisors other than 1 and itself.
    
    Args:
        number: The integer to test for primality
        
    Returns:
        True if the number is prime, False otherwise
        
    Example:
        >>> is_prime(17)
        True
        >>> is_prime(18)
        False
    """
    # Numbers less than 2 are not prime by definition
    if number < 2:
        return False
    
    # Two is the only even prime number
    if number == 2:
        return True
    
    # All other even numbers are not prime
    if number % 2 == 0:
        return False
    
    # Check odd divisors up to the square root
    # If n = a × b, then one of a or b must be ≤ √n
    square_root = int(math.sqrt(number))
    
    for divisor in range(3, square_root + 1, 2):
        if number % divisor == 0:
            return False
    
    return True


def find_primes_up_to(limit: int) -> List[int]:
    """
    Find all prime numbers up to a given limit using the Sieve of Eratosthenes.
    
    This ancient algorithm is both elegant and efficient,
    systematically eliminating composite numbers.
    
    Args:
        limit: The upper bound (inclusive) for finding primes
        
    Returns:
        List of all prime numbers up to and including the limit
    """
    if limit < 2:
        return []
    
    # Create a boolean array "is_prime" and initialize all entries as true
    is_prime_array = [True] * (limit + 1)
    is_prime_array[0] = is_prime_array[1] = False
    
    # Start with the smallest prime number, 2
    for number in range(2, int(math.sqrt(limit)) + 1):
        if is_prime_array[number]:
            # Mark all multiples as not prime
            for multiple in range(number * number, limit + 1, number):
                is_prime_array[multiple] = False
    
    # Collect all numbers marked as prime
    return [num for num, prime in enumerate(is_prime_array) if prime]


def prime_generator() -> Iterator[int]:
    """
    Generate prime numbers infinitely using a generator.
    
    Yields:
        Next prime number in sequence
    """
    yield 2
    candidates = 3
    primes_found = [2]
    
    while True:
        is_prime_candidate = True
        sqrt_candidate = int(math.sqrt(candidates))
        
        for prime in primes_found:
            if prime > sqrt_candidate:
                break
            if candidates % prime == 0:
                is_prime_candidate = False
                break
        
        if is_prime_candidate:
            primes_found.append(candidates)
            yield candidates
        
        candidates += 2


def main():
    """Demonstrate prime number detection."""
    print("🔢 Prime Number Checker\n")
    
    # Test individual numbers
    test_numbers = [1, 2, 3, 4, 17, 20, 29, 100, 97]
    print("Individual prime tests:")
    for number in test_numbers:
        status = "✓ prime" if is_prime(number) else "✗ not prime"
        print(f"  {number:3d}: {status}")
    
    print()
    
    # Find all primes up to a limit
    limit = 50
    primes = find_primes_up_to(limit)
    print(f"Primes up to {limit}:")
    print(f"  {primes}")
    print(f"  Total: {len(primes)} primes found")


if __name__ == "__main__":
    main()
