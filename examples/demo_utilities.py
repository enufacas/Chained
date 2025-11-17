#!/usr/bin/env python3
"""
Example utility functions for demonstrating the AI Test Generator.

This module contains simple utility functions that showcase various
parameter types and edge cases that the AI Test Generator can detect.
"""


def calculate_sum(a: int, b: int) -> int:
    """
    Calculate the sum of two integers.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Sum of a and b
    """
    return a + b


def process_text(text: str, max_length: int = 100) -> str:
    """
    Process text by trimming and cleaning it.
    
    Args:
        text: Input text to process
        max_length: Maximum length of output text
        
    Returns:
        Processed text
    """
    if text is None:
        return ""
    
    # Clean whitespace
    cleaned = text.strip()
    
    # Truncate if needed
    if len(cleaned) > max_length:
        return cleaned[:max_length]
    
    return cleaned


def find_average(numbers: list) -> float:
    """
    Find the average of a list of numbers.
    
    Args:
        numbers: List of numbers
        
    Returns:
        Average value
        
    Raises:
        ValueError: If list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    
    return sum(numbers) / len(numbers)


def merge_dictionaries(dict1: dict, dict2: dict) -> dict:
    """
    Merge two dictionaries, with dict2 values overwriting dict1.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    if dict1 is None:
        dict1 = {}
    if dict2 is None:
        dict2 = {}
    
    result = dict1.copy()
    result.update(dict2)
    return result


def is_valid_email(email: str) -> bool:
    """
    Check if an email address is valid (simple validation).
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Simple validation: contains @ and .
    if '@' not in email or '.' not in email:
        return False
    
    # @ should come before .
    at_index = email.index('@')
    dot_index = email.rindex('.')
    
    return at_index < dot_index


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a decimal value as a percentage string.
    
    Args:
        value: Decimal value (e.g., 0.85 for 85%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "0.00%"
    
    percentage = value * 100
    return f"{percentage:.{decimals}f}%"


if __name__ == "__main__":
    # Example usage
    print(f"Sum: {calculate_sum(5, 10)}")
    print(f"Processed: '{process_text('  hello world  ')}'")
    print(f"Average: {find_average([1, 2, 3, 4, 5])}")
    print(f"Merged: {merge_dictionaries({'a': 1}, {'b': 2})}")
    print(f"Valid email: {is_valid_email('test@example.com')}")
    print(f"Percentage: {format_percentage(0.85)}")
