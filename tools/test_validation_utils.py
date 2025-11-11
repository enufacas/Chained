#!/usr/bin/env python3
"""
Test suite for validation utilities.

Tests all validation functions to ensure they properly validate inputs
and provide clear error messages.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from validation_utils import (
    ValidationError,
    validate_agent_name,
    validate_file_path,
    validate_json_structure,
    validate_string_length,
    validate_non_empty_string,
    validate_list_of_strings,
    safe_file_read,
    safe_file_write,
    validate_numeric_range,
    validate_url,
    validate_email,
    validate_json_safe,
    validate_list_non_empty,
    sanitize_command_input,
    validate_dict_schema,
    validate_percentage
)


def test_validate_agent_name():
    """Test agent name validation."""
    print("Testing validate_agent_name()...")
    
    # Valid names
    assert validate_agent_name("bug-hunter") == "bug-hunter"
    assert validate_agent_name("test_agent") == "test_agent"
    assert validate_agent_name("Agent123") == "Agent123"
    assert validate_agent_name("  spaced  ") == "spaced"
    
    # Invalid names
    try:
        validate_agent_name("")
        assert False, "Should reject empty string"
    except ValidationError:
        pass
    
    try:
        validate_agent_name("   ")
        assert False, "Should reject whitespace only"
    except ValidationError:
        pass
    
    try:
        validate_agent_name(None)
        assert False, "Should reject None"
    except ValidationError:
        pass
    
    try:
        validate_agent_name(123)
        assert False, "Should reject non-string"
    except ValidationError:
        pass
    
    try:
        validate_agent_name("../etc/passwd")
        assert False, "Should reject path traversal characters"
    except ValidationError:
        pass
    
    try:
        validate_agent_name("agent@name")
        assert False, "Should reject special characters"
    except ValidationError:
        pass
    
    try:
        validate_agent_name("a" * 101)
        assert False, "Should reject too long names"
    except ValidationError:
        pass
    
    try:
        validate_agent_name("a")
        assert False, "Should reject too short names"
    except ValidationError:
        pass
    
    print("✅ validate_agent_name tests passed")


def test_validate_file_path():
    """Test file path validation."""
    print("Testing validate_file_path()...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        test_file = base_dir / "test.txt"
        test_file.write_text("test")
        
        # Valid paths
        validated = validate_file_path(test_file)
        assert validated.exists()
        
        validated = validate_file_path(test_file, base_dir)
        assert validated.exists()
        
        # Invalid paths
        try:
            validate_file_path("")
            assert False, "Should reject empty path"
        except ValidationError:
            pass
        
        try:
            validate_file_path(None)
            assert False, "Should reject None"
        except ValidationError:
            pass
        
        # Path traversal check
        outside_path = Path("/etc/passwd")
        try:
            validate_file_path(outside_path, base_dir)
            assert False, "Should reject path outside base_dir"
        except ValidationError:
            pass
    
    print("✅ validate_file_path tests passed")


def test_validate_json_structure():
    """Test JSON structure validation."""
    print("Testing validate_json_structure()...")
    
    # Valid structure
    data = {"name": "test", "value": 123}
    validate_json_structure(data, ["name", "value"])
    validate_json_structure(data, ["name"])
    
    # Invalid structures
    try:
        validate_json_structure(data, ["name", "missing"])
        assert False, "Should detect missing keys"
    except ValidationError:
        pass
    
    try:
        validate_json_structure("not a dict", ["key"])
        assert False, "Should reject non-dict"
    except ValidationError:
        pass
    
    try:
        validate_json_structure([1, 2, 3], ["key"])
        assert False, "Should reject list"
    except ValidationError:
        pass
    
    print("✅ validate_json_structure tests passed")


def test_validate_string_length():
    """Test string length validation."""
    print("Testing validate_string_length()...")
    
    # Valid lengths
    assert validate_string_length("test", 1, 10) == "test"
    assert validate_string_length("", 0, 10) == ""
    assert validate_string_length("a", 1) == "a"
    
    # Invalid lengths
    try:
        validate_string_length("test", 5, 10)
        assert False, "Should reject too short"
    except ValidationError:
        pass
    
    try:
        validate_string_length("test", 1, 3)
        assert False, "Should reject too long"
    except ValidationError:
        pass
    
    try:
        validate_string_length(123, 1, 10)
        assert False, "Should reject non-string"
    except ValidationError:
        pass
    
    print("✅ validate_string_length tests passed")


def test_validate_non_empty_string():
    """Test non-empty string validation."""
    print("Testing validate_non_empty_string()...")
    
    # Valid strings
    assert validate_non_empty_string("test") == "test"
    assert validate_non_empty_string("  test  ") == "test"
    assert validate_non_empty_string("123") == "123"
    
    # Invalid strings
    try:
        validate_non_empty_string("")
        assert False, "Should reject empty string"
    except ValidationError:
        pass
    
    try:
        validate_non_empty_string("   ")
        assert False, "Should reject whitespace only"
    except ValidationError:
        pass
    
    try:
        validate_non_empty_string(None)
        assert False, "Should reject None"
    except ValidationError:
        pass
    
    try:
        validate_non_empty_string(123)
        assert False, "Should reject non-string"
    except ValidationError:
        pass
    
    print("✅ validate_non_empty_string tests passed")


def test_validate_list_of_strings():
    """Test list of strings validation."""
    print("Testing validate_list_of_strings()...")
    
    # Valid lists
    assert validate_list_of_strings([]) == []
    assert validate_list_of_strings(["a", "b", "c"]) == ["a", "b", "c"]
    assert validate_list_of_strings(["test"]) == ["test"]
    
    # Invalid lists
    try:
        validate_list_of_strings("not a list")
        assert False, "Should reject non-list"
    except ValidationError:
        pass
    
    try:
        validate_list_of_strings([1, 2, 3])
        assert False, "Should reject list of non-strings"
    except ValidationError:
        pass
    
    try:
        validate_list_of_strings(["valid", 123, "string"])
        assert False, "Should reject mixed list"
    except ValidationError:
        pass
    
    print("✅ validate_list_of_strings tests passed")


def test_safe_file_operations():
    """Test safe file read/write operations."""
    print("Testing safe_file_read() and safe_file_write()...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        content = "Hello, World!\n"
        
        # Write file
        safe_file_write(test_file, content)
        assert test_file.exists()
        
        # Read file
        read_content = safe_file_read(test_file)
        assert read_content == content
        
        # Create dirs
        nested_file = Path(tmpdir) / "nested" / "dir" / "file.txt"
        safe_file_write(nested_file, content, create_dirs=True)
        assert nested_file.exists()
        assert safe_file_read(nested_file) == content
        
        # Invalid operations
        try:
            safe_file_read("/nonexistent/file.txt")
            assert False, "Should reject nonexistent file"
        except ValidationError:
            pass
        
        try:
            safe_file_read(tmpdir)  # Directory, not file
            assert False, "Should reject directory"
        except ValidationError:
            pass
    
    print("✅ safe_file_read/write tests passed")


def test_validate_numeric_range():
    """Test numeric range validation."""
    print("Testing validate_numeric_range()...")
    
    # Valid ranges
    assert validate_numeric_range(5, 0, 10) == 5
    assert validate_numeric_range(0, 0, 10) == 0
    assert validate_numeric_range(10, 0, 10) == 10
    assert validate_numeric_range(5.5, 0, 10) == 5.5
    assert validate_numeric_range(100, min_value=0) == 100
    assert validate_numeric_range(-5, max_value=0) == -5
    
    # Invalid ranges
    try:
        validate_numeric_range(-1, 0, 10)
        assert False, "Should reject value below minimum"
    except ValidationError:
        pass
    
    try:
        validate_numeric_range(11, 0, 10)
        assert False, "Should reject value above maximum"
    except ValidationError:
        pass
    
    try:
        validate_numeric_range("5", 0, 10)
        assert False, "Should reject non-numeric"
    except ValidationError:
        pass
    
    try:
        validate_numeric_range(None, 0, 10)
        assert False, "Should reject None"
    except ValidationError:
        pass
    
    print("✅ validate_numeric_range tests passed")


def test_validate_url():
    """Test URL validation."""
    print("Testing validate_url()...")
    
    # Valid URLs
    assert validate_url("http://example.com") == "http://example.com"
    assert validate_url("https://example.com") == "https://example.com"
    assert validate_url("https://example.com/path") == "https://example.com/path"
    assert validate_url("http://localhost:8080") == "http://localhost:8080"
    assert validate_url("https://sub.example.com") == "https://sub.example.com"
    assert validate_url("  https://example.com  ") == "https://example.com"
    
    # Invalid URLs
    try:
        validate_url("")
        assert False, "Should reject empty URL"
    except ValidationError:
        pass
    
    try:
        validate_url("   ")
        assert False, "Should reject whitespace only"
    except ValidationError:
        pass
    
    try:
        validate_url("not-a-url")
        assert False, "Should reject invalid URL"
    except ValidationError:
        pass
    
    try:
        validate_url("ftp://example.com")
        assert False, "Should reject non-http(s) protocol"
    except ValidationError:
        pass
    
    try:
        validate_url(123)
        assert False, "Should reject non-string"
    except ValidationError:
        pass
    
    print("✅ validate_url tests passed")


def test_validate_email():
    """Test email validation."""
    print("Testing validate_email()...")
    
    # Valid emails
    assert validate_email("user@example.com") == "user@example.com"
    assert validate_email("user.name@example.com") == "user.name@example.com"
    assert validate_email("user+tag@example.co.uk") == "user+tag@example.co.uk"
    assert validate_email("  user@example.com  ") == "user@example.com"
    
    # Invalid emails
    try:
        validate_email("")
        assert False, "Should reject empty email"
    except ValidationError:
        pass
    
    try:
        validate_email("   ")
        assert False, "Should reject whitespace only"
    except ValidationError:
        pass
    
    try:
        validate_email("not-an-email")
        assert False, "Should reject invalid format"
    except ValidationError:
        pass
    
    try:
        validate_email("@example.com")
        assert False, "Should reject missing username"
    except ValidationError:
        pass
    
    try:
        validate_email("user@")
        assert False, "Should reject missing domain"
    except ValidationError:
        pass
    
    try:
        validate_email(123)
        assert False, "Should reject non-string"
    except ValidationError:
        pass
    
    print("✅ validate_email tests passed")


def test_validate_json_safe():
    """Test safe JSON validation."""
    print("Testing validate_json_safe()...")
    
    # Valid JSON
    assert validate_json_safe({"key": "value"}) == {"key": "value"}
    assert validate_json_safe('{"key": "value"}') == {"key": "value"}
    assert validate_json_safe('{}') == {}
    
    # Invalid JSON
    try:
        validate_json_safe('[1, 2, 3]')  # Array, not object
        assert False, "Should reject JSON array"
    except ValidationError:
        pass
    
    try:
        validate_json_safe('{"invalid": json}')
        assert False, "Should reject invalid JSON"
    except ValidationError:
        pass
    
    try:
        validate_json_safe(123)
        assert False, "Should reject non-dict/string"
    except ValidationError:
        pass
    
    print("✅ validate_json_safe tests passed")


def test_validate_list_non_empty():
    """Test non-empty list validation."""
    print("Testing validate_list_non_empty()...")
    
    # Valid lists
    assert validate_list_non_empty([1, 2, 3]) == [1, 2, 3]
    assert validate_list_non_empty(["a"]) == ["a"]
    assert validate_list_non_empty([None]) == [None]
    
    # Invalid lists
    try:
        validate_list_non_empty([])
        assert False, "Should reject empty list"
    except ValidationError:
        pass
    
    try:
        validate_list_non_empty("not a list")
        assert False, "Should reject non-list"
    except ValidationError:
        pass
    
    try:
        validate_list_non_empty(None)
        assert False, "Should reject None"
    except ValidationError:
        pass
    
    print("✅ validate_list_non_empty tests passed")


def test_sanitize_command_input():
    """Test command input sanitization."""
    print("Testing sanitize_command_input()...")
    
    # Safe commands
    assert sanitize_command_input("ls -la") == "ls -la"
    assert sanitize_command_input("python script.py") == "python script.py"
    assert sanitize_command_input("echo hello") == "echo hello"
    
    # Dangerous commands
    try:
        sanitize_command_input("ls; rm -rf /")
        assert False, "Should reject command with semicolon"
    except ValidationError:
        pass
    
    try:
        sanitize_command_input("ls | grep test")
        assert False, "Should reject command with pipe"
    except ValidationError:
        pass
    
    try:
        sanitize_command_input("echo `whoami`")
        assert False, "Should reject command substitution"
    except ValidationError:
        pass
    
    try:
        sanitize_command_input("echo $(whoami)")
        assert False, "Should reject command substitution"
    except ValidationError:
        pass
    
    try:
        sanitize_command_input("echo test\nrm file")
        assert False, "Should reject newline injection"
    except ValidationError:
        pass
    
    try:
        sanitize_command_input(123)
        assert False, "Should reject non-string"
    except ValidationError:
        pass
    
    print("✅ sanitize_command_input tests passed")


def test_validate_dict_schema():
    """Test dictionary schema validation."""
    print("Testing validate_dict_schema()...")
    
    # Valid schema
    schema = {'name': str, 'age': int, 'active': bool}
    data = {'name': 'Alice', 'age': 30, 'active': True}
    assert validate_dict_schema(data, schema) == data
    
    # Extra keys are allowed
    data_extra = {'name': 'Bob', 'age': 25, 'active': False, 'extra': 'ignored'}
    assert validate_dict_schema(data_extra, schema) == data_extra
    
    # Invalid schema
    try:
        validate_dict_schema({'name': 'Alice'}, schema)
        assert False, "Should reject missing keys"
    except ValidationError:
        pass
    
    try:
        data_wrong_type = {'name': 123, 'age': 30, 'active': True}
        validate_dict_schema(data_wrong_type, schema)
        assert False, "Should reject wrong type"
    except ValidationError:
        pass
    
    try:
        validate_dict_schema("not a dict", schema)
        assert False, "Should reject non-dict"
    except ValidationError:
        pass
    
    print("✅ validate_dict_schema tests passed")


def test_validate_percentage():
    """Test percentage validation."""
    print("Testing validate_percentage()...")
    
    # Valid percentages
    assert validate_percentage(0) == 0.0
    assert validate_percentage(50) == 50.0
    assert validate_percentage(100) == 100.0
    assert validate_percentage(25.5) == 25.5
    
    # Invalid percentages
    try:
        validate_percentage(-1)
        assert False, "Should reject negative percentage"
    except ValidationError:
        pass
    
    try:
        validate_percentage(101)
        assert False, "Should reject percentage over 100"
    except ValidationError:
        pass
    
    try:
        validate_percentage("50")
        assert False, "Should reject non-numeric"
    except ValidationError:
        pass
    
    print("✅ validate_percentage tests passed")


def main():
    """Run all tests."""
    print("=" * 70)
    print("🧪 Validation Utils Test Suite")
    print("=" * 70)
    print()
    
    try:
        test_validate_agent_name()
        test_validate_file_path()
        test_validate_json_structure()
        test_validate_string_length()
        test_validate_non_empty_string()
        test_validate_list_of_strings()
        test_safe_file_operations()
        test_validate_numeric_range()
        test_validate_url()
        test_validate_email()
        test_validate_json_safe()
        test_validate_list_non_empty()
        test_sanitize_command_input()
        test_validate_dict_schema()
        test_validate_percentage()
        
        print()
        print("=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        return 0
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Test failed: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
