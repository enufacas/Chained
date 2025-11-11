#!/usr/bin/env python3
"""
Palindrome Checker

A palindrome is a word, phrase, or sequence that reads the same
backward as forward. A perfect symmetry, a linguistic mirror,
where beginning and end reflect each other in harmony.
"""

import string
from typing import Optional


def is_palindrome(text: str, ignore_case: bool = True, 
                 ignore_spaces: bool = True,
                 ignore_punctuation: bool = True) -> bool:
    """
    Check if the given text is a palindrome.
    
    A palindrome reads identically forwards and backwards.
    Examples: "racecar", "A man a plan a canal Panama"
    
    Args:
        text: String to check for palindrome properties
        ignore_case: Whether to ignore case differences (default: True)
        ignore_spaces: Whether to ignore spaces (default: True)
        ignore_punctuation: Whether to ignore punctuation (default: True)
        
    Returns:
        True if the text is a palindrome, False otherwise
        
    Example:
        >>> is_palindrome("racecar")
        True
        >>> is_palindrome("hello")
        False
    """
    if not text:
        return True  # Empty string is technically a palindrome
    
    # Normalize the text based on parameters
    normalized = text
    
    if ignore_case:
        normalized = normalized.lower()
    
    if ignore_spaces:
        normalized = normalized.replace(" ", "")
    
    if ignore_punctuation:
        normalized = normalized.translate(str.maketrans("", "", string.punctuation))
    
    # Check if the normalized string equals its reverse
    return normalized == normalized[::-1]


def find_longest_palindrome(text: str) -> Optional[str]:
    """
    Find the longest palindromic substring within the given text.
    
    Uses an expanding window approach to discover palindromes
    hidden within larger strings.
    
    Args:
        text: String to search for palindromes
        
    Returns:
        The longest palindromic substring, or None if text is empty
    """
    if not text:
        return None
    
    def expand_around_center(left: int, right: int) -> str:
        """Expand from center to find palindrome."""
        while left >= 0 and right < len(text) and text[left] == text[right]:
            left -= 1
            right += 1
        return text[left + 1:right]
    
    longest = ""
    
    for i in range(len(text)):
        # Check for odd-length palindromes (single center)
        palindrome1 = expand_around_center(i, i)
        # Check for even-length palindromes (double center)
        palindrome2 = expand_around_center(i, i + 1)
        
        # Keep track of the longest palindrome found
        current = palindrome1 if len(palindrome1) > len(palindrome2) else palindrome2
        if len(current) > len(longest):
            longest = current
    
    return longest if longest else None


def reverse_words(text: str) -> str:
    """
    Reverse the order of words in a string.
    
    Args:
        text: String containing words to reverse
        
    Returns:
        String with words in reversed order
        
    Example:
        >>> reverse_words("hello world")
        'world hello'
    """
    return " ".join(text.split()[::-1])


def main():
    """Demonstrate palindrome detection and manipulation."""
    print("🪞 Palindrome Checker\n")
    
    # Test various palindromes
    test_strings = [
        "racecar",
        "hello",
        "A man a plan a canal Panama",
        "Was it a car or a cat I saw",
        "Madam, I'm Adam",
        "python"
    ]
    
    print("Palindrome tests:")
    for text in test_strings:
        status = "✓" if is_palindrome(text) else "✗"
        print(f"  {status} '{text}'")
    
    print()
    
    # Find longest palindrome in a string
    sample = "babad"
    longest = find_longest_palindrome(sample)
    print(f"Longest palindrome in '{sample}': '{longest}'")
    
    # Demonstrate word reversal
    phrase = "Code is poetry"
    reversed_phrase = reverse_words(phrase)
    print(f"\nOriginal: '{phrase}'")
    print(f"Reversed: '{reversed_phrase}'")


if __name__ == "__main__":
    main()
