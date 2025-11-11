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
    safe_file_write
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
