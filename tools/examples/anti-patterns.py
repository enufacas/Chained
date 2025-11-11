#!/usr/bin/env python3
"""
Anti-Patterns and Their Beautiful Alternatives

This file demonstrates common code anti-patterns alongside
their elegant, readable alternatives. Learn from mistakes,
embrace beauty in your code.
"""

import os
from typing import Any, Optional, List


# ❌ ANTI-PATTERN: Vague naming and bare except
def process_data(data):
    """Process the data"""
    try:
        print("debug: processing data")
        result = None
        try:
            result = data * 2
        except:  # Dangerous: catches all exceptions
            pass
        return result
    except:  # What are we catching here?
        return None


# ✅ ELEGANT ALTERNATIVE: Clear naming and specific exception handling
def double_numbers(numbers: List[int]) -> Optional[List[int]]:
    """
    Double each number in the input list.
    
    Args:
        numbers: List of integers to double
        
    Returns:
        List of doubled numbers, or None if operation fails
    """
    try:
        return [num * 2 for num in numbers]
    except (TypeError, ValueError) as error:
        print(f"Failed to double numbers: {error}")
        return None


# ❌ ANTI-PATTERN: Hardcoded secrets
api_key = "sk_test_1234567890abcdefghijklmnop"


# ✅ ELEGANT ALTERNATIVE: Environment variables for configuration
def get_api_key() -> Optional[str]:
    """
    Retrieve API key from environment variables.
    
    Returns:
        API key if found, None otherwise
    """
    return os.environ.get('API_KEY')


# ❌ ANTI-PATTERN: SQL injection vulnerability
def query_database_unsafe(user_input):
    """Query database - SQL injection risk"""
    query = "SELECT * FROM users WHERE name = '%s'" % user_input
    # execute(query)  # Never use string formatting for SQL!
    pass


# ✅ ELEGANT ALTERNATIVE: Parameterized queries
def query_database_safe(username: str, db_connection) -> Any:
    """
    Query database safely using parameterized queries.
    
    Args:
        username: The username to search for
        db_connection: Database connection object
        
    Returns:
        Query results
        
    Note:
        This prevents SQL injection by using parameter substitution
        instead of string formatting.
    """
    query = "SELECT * FROM users WHERE name = ?"
    # return db_connection.execute(query, (username,))
    pass


# ❌ ANTI-PATTERN: Complex nested conditionals
def check_status(status, role, permissions):
    """Check if action is allowed"""
    if status:
        if role:
            if permissions:
                if 'admin' in permissions:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False


# ✅ ELEGANT ALTERNATIVE: Early returns and clear logic
def is_admin_allowed(status: bool, role: Optional[str], 
                     permissions: Optional[List[str]]) -> bool:
    """
    Check if user has admin permissions.
    
    Args:
        status: Whether the user account is active
        role: User's role
        permissions: List of user permissions
        
    Returns:
        True if user is an admin with active status
    """
    if not status:
        return False
    
    if not role or not permissions:
        return False
    
    return 'admin' in permissions


def demonstrate_patterns():
    """Show the difference between anti-patterns and elegant code."""
    print("🎨 Code Anti-Patterns vs. Elegant Alternatives\n")
    
    # Test data processing
    test_data = [1, 2, 3, 4, 5]
    
    print("Data Processing:")
    print(f"  Input: {test_data}")
    print(f"  Anti-pattern result: {process_data(test_data)}")
    print(f"  Elegant result: {double_numbers(test_data)}\n")
    
    # Test permission checking
    print("Permission Checking:")
    print(f"  Anti-pattern: {check_status(True, 'user', ['admin'])}")
    print(f"  Elegant: {is_admin_allowed(True, 'user', ['admin'])}\n")
    
    print("✨ Remember: Clear code is kind code!")


if __name__ == "__main__":
    demonstrate_patterns()
