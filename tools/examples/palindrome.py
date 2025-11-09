#!/usr/bin/env python3
"""
Palindrome checker
Checks if a string is a palindrome
"""

def is_palindrome(text):
    """
    Check if the given text is a palindrome
    
    Args:
        text: String to check
        
    Returns:
        True if palindrome, False otherwise
    """
    # Remove spaces and convert to lowercase for fair comparison
    cleaned_text = text.replace(" ", "").lower()
    
    # Remove punctuation
    import string
    cleaned_text = cleaned_text.translate(str.maketrans("", "", string.punctuation))
    
    # Check if string equals its reverse
    return cleaned_text == cleaned_text[::-1]


# Test the function
if __name__ == "__main__":
    test_strings = [
        "racecar",
        "hello",
        "A man a plan a canal Panama",
        "Was it a car or a cat I saw"
    ]
    
    for test_string in test_strings:
        result = is_palindrome(test_string)
        print(f"'{test_string}' is palindrome: {result}")
