#!/usr/bin/env python3
"""
Code Poetry Showcase: Beautiful, Readable Python

This file demonstrates the principles of code craftsmanship:
elegant solutions that are both functional and aesthetically pleasing.
Every function is a verse, every variable a carefully chosen word.
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
from collections import Counter


@dataclass
class TextAnalysis:
    """Container for text analysis results."""
    word_count: int
    unique_words: int
    most_common_word: Tuple[str, int]
    average_word_length: float
    
    def __str__(self) -> str:
        """Return a human-readable representation."""
        word, count = self.most_common_word
        return (
            f"Analysis: {self.word_count} words "
            f"({self.unique_words} unique), "
            f"most common: '{word}' ({count}×), "
            f"avg length: {self.average_word_length:.1f}"
        )


def analyze_text(text: str) -> Optional[TextAnalysis]:
    """
    Analyze text and return meaningful statistics.
    
    This function transforms raw text into insights,
    revealing patterns hidden within the words.
    
    Args:
        text: The text to analyze
        
    Returns:
        TextAnalysis object, or None if text is empty
    """
    if not text or not text.strip():
        return None
    
    words = text.lower().split()
    word_frequencies = Counter(words)
    total_characters = sum(len(word) for word in words)
    
    return TextAnalysis(
        word_count=len(words),
        unique_words=len(word_frequencies),
        most_common_word=word_frequencies.most_common(1)[0],
        average_word_length=total_characters / len(words)
    )


def find_palindromes(words: List[str]) -> List[str]:
    """
    Discover palindromes within a list of words.
    
    A palindrome reads the same forwards and backwards,
    a perfect symmetry in the chaos of language.
    
    Args:
        words: List of words to examine
        
    Returns:
        List of palindromic words, sorted by length
    """
    def is_palindrome(word: str) -> bool:
        """Check if a word is a palindrome."""
        normalized = word.lower()
        return normalized == normalized[::-1]
    
    palindromes = [word for word in words if is_palindrome(word)]
    return sorted(palindromes, key=len, reverse=True)


def fibonacci_sequence(count: int) -> List[int]:
    """
    Generate the Fibonacci sequence, nature's mathematical poetry.
    
    Each number is the sum of the two before it,
    an infinite dance of addition and growth.
    
    Args:
        count: Number of terms to generate
        
    Returns:
        List containing the Fibonacci sequence
        
    Raises:
        ValueError: If count is negative
    """
    if count < 0:
        raise ValueError("Count must be non-negative")
    
    if count == 0:
        return []
    
    if count == 1:
        return [0]
    
    sequence = [0, 1]
    while len(sequence) < count:
        next_number = sequence[-1] + sequence[-2]
        sequence.append(next_number)
    
    return sequence


def format_number_with_separators(number: int, separator: str = ",") -> str:
    """
    Format a number with thousand separators for readability.
    
    Transform digits into a readable format,
    making large numbers comprehensible at a glance.
    
    Args:
        number: The number to format
        separator: The separator character (default: comma)
        
    Returns:
        Formatted string representation of the number
        
    Example:
        >>> format_number_with_separators(1234567)
        '1,234,567'
    """
    number_str = str(abs(number))
    groups = []
    
    for i in range(len(number_str), 0, -3):
        start = max(0, i - 3)
        groups.insert(0, number_str[start:i])
    
    formatted = separator.join(groups)
    return f"-{formatted}" if number < 0 else formatted


def validate_email(email: str) -> bool:
    """
    Validate an email address with simple pattern matching.
    
    Not perfect, but elegant in its simplicity.
    A basic check that catches common mistakes.
    
    Args:
        email: The email address to validate
        
    Returns:
        True if the email appears valid, False otherwise
    """
    if not email or '@' not in email:
        return False
    
    local, domain = email.rsplit('@', 1)
    
    if not local or not domain:
        return False
    
    if '.' not in domain:
        return False
    
    return True


def main():
    """Demonstrate the beauty of well-crafted code."""
    print("🎨 Code Poetry Showcase\n")
    
    # Text analysis demonstration
    sample_text = "the quick brown fox jumps over the lazy dog"
    analysis = analyze_text(sample_text)
    if analysis:
        print(f"Text: '{sample_text}'")
        print(f"{analysis}\n")
    
    # Palindrome discovery
    words = ["racecar", "python", "level", "code", "noon", "elegant"]
    palindromes = find_palindromes(words)
    print(f"Palindromes found: {', '.join(palindromes)}\n")
    
    # Fibonacci sequence
    fib = fibonacci_sequence(10)
    print(f"First 10 Fibonacci numbers: {fib}\n")
    
    # Number formatting
    big_number = 1234567890
    formatted = format_number_with_separators(big_number)
    print(f"Formatted number: {formatted}\n")
    
    # Email validation
    test_emails = ["user@example.com", "invalid.email", "test@test.co"]
    print("Email validation:")
    for email in test_emails:
        status = "✓" if validate_email(email) else "✗"
        print(f"  {status} {email}")


if __name__ == "__main__":
    main()
