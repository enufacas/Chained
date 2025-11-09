#!/usr/bin/env python3
"""
Prime number checker
Checks if a number is prime
"""

def is_prime(number):
    """
    Check if a number is prime
    
    Args:
        number: Integer to check
        
    Returns:
        True if prime, False otherwise
    """
    # Numbers less than 2 are not prime
    if number < 2:
        return False
    
    # 2 is the only even prime number
    if number == 2:
        return True
    
    # Even numbers are not prime
    if number % 2 == 0:
        return False
    
    # Check odd divisors up to square root
    import math
    square_root = int(math.sqrt(number))
    
    for divisor in range(3, square_root + 1, 2):
        if number % divisor == 0:
            return False
    
    return True


# Test the function
if __name__ == "__main__":
    test_numbers = [1, 2, 3, 4, 17, 20, 29, 100, 97]
    
    for test_number in test_numbers:
        result = is_prime(test_number)
        print(f"{test_number} is prime: {result}")
