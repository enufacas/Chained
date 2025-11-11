#!/usr/bin/env python3
"""
Validation utilities for the Chained project.

This module provides reusable validation functions to ensure data integrity,
input validation, and error handling across the codebase.
"""

import re
import os
from pathlib import Path
from typing import Any, Optional, Union


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_agent_name(agent_name: Any) -> str:
    """
    Validate and sanitize an agent name.
    
    Ensures the agent name contains only safe characters (alphanumeric, 
    hyphens, and underscores) and meets length requirements.
    
    Args:
        agent_name: The agent name to validate
        
    Returns:
        The validated agent name as a string
        
    Raises:
        ValidationError: If the agent name is invalid
    """
    if not agent_name:
        raise ValidationError("Agent name cannot be empty")
    
    if not isinstance(agent_name, str):
        raise ValidationError(f"Agent name must be a string, got {type(agent_name).__name__}")
    
    # Strip whitespace
    agent_name = agent_name.strip()
    
    if not agent_name:
        raise ValidationError("Agent name cannot be empty or whitespace only")
    
    # Only allow alphanumeric, hyphens, and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', agent_name):
        raise ValidationError(
            f"Agent name '{agent_name}' contains invalid characters. "
            "Only alphanumeric, hyphens, and underscores are allowed"
        )
    
    # Check length constraints
    min_length, max_length = 2, 100
    if len(agent_name) > max_length:
        raise ValidationError(f"Agent name too long ({len(agent_name)} chars), maximum is {max_length}")
    
    if len(agent_name) < min_length:
        raise ValidationError(f"Agent name too short ({len(agent_name)} chars), minimum is {min_length}")
    
    return agent_name


def validate_file_path(filepath: Union[str, Path], base_dir: Optional[Path] = None) -> Path:
    """
    Validate a file path to prevent directory traversal attacks.
    
    Args:
        filepath: The file path to validate
        base_dir: Optional base directory to restrict access to
        
    Returns:
        The validated and resolved Path object
        
    Raises:
        ValidationError: If the path is invalid or outside the allowed directory
    """
    if not filepath:
        raise ValidationError("File path cannot be empty")
    
    try:
        # Convert to Path and resolve
        path = Path(filepath).resolve()
    except (ValueError, OSError) as e:
        raise ValidationError(f"Invalid file path: {e}")
    
    # If base_dir is specified, ensure the path is within it
    if base_dir is not None:
        try:
            base_dir = base_dir.resolve()
            # Check if the path starts with base_dir
            path.relative_to(base_dir)
        except ValueError:
            raise ValidationError(
                f"Path '{filepath}' is outside the allowed directory '{base_dir}'"
            )
    
    return path


def validate_json_structure(data: Any, required_keys: list) -> None:
    """
    Validate that a dictionary has required keys.
    
    Args:
        data: The data to validate (should be a dict)
        required_keys: List of required key names
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(data, dict):
        raise ValidationError(f"Expected dict, got {type(data).__name__}")
    
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise ValidationError(f"Missing required keys: {', '.join(missing_keys)}")


def validate_string_length(
    value: str, 
    min_length: int = 0, 
    max_length: Optional[int] = None,
    field_name: str = "value"
) -> str:
    """
    Validate that a string meets length requirements.
    
    Args:
        value: The string to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length (None for no limit)
        field_name: Name of the field for error messages
        
    Returns:
        The validated string
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string, got {type(value).__name__}")
    
    length = len(value)
    
    if length < min_length:
        raise ValidationError(
            f"{field_name} too short ({length} chars), minimum is {min_length}"
        )
    
    if max_length is not None and length > max_length:
        raise ValidationError(
            f"{field_name} too long ({length} chars), maximum is {max_length}"
        )
    
    return value


def validate_non_empty_string(value: Any, field_name: str = "value") -> str:
    """
    Validate that a value is a non-empty string.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated string (stripped of leading/trailing whitespace)
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string, got {type(value).__name__}")
    
    value = value.strip()
    if not value:
        raise ValidationError(f"{field_name} cannot be empty or whitespace only")
    
    return value


def validate_list_of_strings(value: Any, field_name: str = "value") -> list:
    """
    Validate that a value is a list of strings.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated list
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, list):
        raise ValidationError(f"{field_name} must be a list, got {type(value).__name__}")
    
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(
                f"{field_name}[{i}] must be a string, got {type(item).__name__}"
            )
    
    return value


def safe_file_read(filepath: Union[str, Path], encoding: str = 'utf-8') -> str:
    """
    Safely read a file with proper error handling.
    
    Args:
        filepath: Path to the file to read
        encoding: File encoding (default: utf-8)
        
    Returns:
        The file contents as a string
        
    Raises:
        ValidationError: If the file cannot be read
    """
    try:
        path = Path(filepath)
        if not path.exists():
            raise ValidationError(f"File does not exist: {filepath}")
        
        if not path.is_file():
            raise ValidationError(f"Path is not a file: {filepath}")
        
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except (IOError, OSError, UnicodeDecodeError) as e:
        raise ValidationError(f"Failed to read file '{filepath}': {e}")


def safe_file_write(
    filepath: Union[str, Path], 
    content: str, 
    encoding: str = 'utf-8',
    create_dirs: bool = False
) -> None:
    """
    Safely write content to a file with proper error handling.
    
    Args:
        filepath: Path to the file to write
        content: Content to write
        encoding: File encoding (default: utf-8)
        create_dirs: Whether to create parent directories
        
    Raises:
        ValidationError: If the file cannot be written
    """
    try:
        path = Path(filepath)
        
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
    except (IOError, OSError, UnicodeEncodeError) as e:
        raise ValidationError(f"Failed to write file '{filepath}': {e}")
