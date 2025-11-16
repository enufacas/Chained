#!/usr/bin/env python3
"""
Demonstration of AI Code Golf Optimizer capabilities
"""

# Example 1: Simple function with comments and docstrings
def calculate_factorial(number):
    """
    Calculate the factorial of a given number.
    
    Args:
        number: The input number
        
    Returns:
        The factorial result
    """
    # Initialize result
    result = 1
    
    # Calculate factorial using loop
    for i in range(1, number + 1):
        result = result * i
    
    # Return the final result
    return result


# Example 2: Boolean operations
def check_conditions(value):
    # Check if value is positive
    is_positive = True if value > 0 else False
    
    # Check if value is even
    is_even = True if value % 2 == 0 else False
    
    return is_positive and is_even


# Example 3: List operations
def process_list(input_list):
    # Create result list
    result_list = []
    
    # Process each element
    for element in input_list:
        # Transform element
        transformed = element * 2
        # Add to result
        result_list.append(transformed)
    
    return result_list
