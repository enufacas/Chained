# 🛡️ Validation Best Practices for Chained

This document provides comprehensive guidelines for implementing robust input validation, data integrity checks, and error handling throughout the Chained codebase.

## Table of Contents

- [Overview](#overview)
- [Core Principles](#core-principles)
- [Validation Utilities](#validation-utilities)
- [Common Validation Patterns](#common-validation-patterns)
- [Security Considerations](#security-considerations)
- [Testing Validation](#testing-validation)
- [Error Messages](#error-messages)

## Overview

Validation is critical for:
- **Security**: Preventing injection attacks and unauthorized access
- **Data Integrity**: Ensuring data remains consistent and correct
- **User Experience**: Providing clear, actionable error messages
- **System Stability**: Catching errors early before they cause crashes

## Core Principles

### 1. Validate Early
Check inputs at system boundaries before they propagate through your code:

```python
from validation_utils import validate_agent_name, ValidationError

def process_agent(agent_name):
    # Validate immediately at the boundary
    agent_name = validate_agent_name(agent_name)
    
    # Now safe to use
    return do_work_with(agent_name)
```

### 2. Validate Often
Apply multiple layers of validation for defense in depth:

```python
# Layer 1: Type and basic format
validate_non_empty_string(url, "URL")

# Layer 2: Specific format validation
validate_url(url)

# Layer 3: Business logic validation
if not is_allowed_domain(url):
    raise ValidationError("URL domain not in allowlist")
```

### 3. Fail Safely
When validation fails, handle it gracefully:

```python
try:
    data = validate_json_safe(user_input)
    process_data(data)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    return {"error": str(e), "status": "invalid"}
```

### 4. Clear Error Messages
Provide actionable error messages that help fix the problem:

```python
# ❌ Bad
raise ValidationError("Invalid input")

# ✅ Good
raise ValidationError(
    f"Agent name '{name}' contains invalid characters. "
    "Only alphanumeric, hyphens, and underscores are allowed"
)
```

## Validation Utilities

The `validation_utils.py` module provides reusable validation functions:

### String Validation

```python
from validation_utils import (
    validate_non_empty_string,
    validate_string_length,
    validate_agent_name
)

# Basic non-empty string
name = validate_non_empty_string(user_input, "name")

# String with length constraints
description = validate_string_length(desc, min_length=10, max_length=500)

# Agent names (alphanumeric, hyphens, underscores only)
agent = validate_agent_name(agent_input)
```

### Numeric Validation

```python
from validation_utils import validate_numeric_range, validate_percentage

# Numeric range
age = validate_numeric_range(user_age, min_value=0, max_value=120)

# Percentages (0-100)
score = validate_percentage(test_score)
```

### Collection Validation

```python
from validation_utils import (
    validate_list_of_strings,
    validate_list_non_empty
)

# List of strings
tags = validate_list_of_strings(user_tags, "tags")

# Non-empty list
items = validate_list_non_empty(item_list, "items")
```

### Data Structure Validation

```python
from validation_utils import (
    validate_json_structure,
    validate_dict_schema,
    validate_json_safe
)

# Check for required keys
validate_json_structure(data, ['name', 'age', 'email'])

# Validate against a schema
schema = {'name': str, 'age': int, 'active': bool}
validate_dict_schema(data, schema)

# Safely parse JSON
data = validate_json_safe(json_string)
```

### Format Validation

```python
from validation_utils import validate_url, validate_email

# URL validation
url = validate_url(user_url)

# Email validation
email = validate_email(user_email)
```

### File Operations

```python
from validation_utils import (
    validate_file_path,
    safe_file_read,
    safe_file_write
)

# Validate file path (prevents directory traversal)
safe_path = validate_file_path(user_path, base_dir=Path("/safe/dir"))

# Safe file operations
content = safe_file_read(safe_path)
safe_file_write(output_path, content, create_dirs=True)
```

## Common Validation Patterns

### Pattern 1: Validating Function Arguments

```python
from validation_utils import (
    validate_non_empty_string,
    validate_numeric_range,
    ValidationError
)

def create_user(username, age, email):
    """Create a new user with validated inputs."""
    try:
        # Validate all inputs
        username = validate_non_empty_string(username, "username")
        age = validate_numeric_range(age, 0, 150, "age")
        email = validate_email(email)
        
        # Proceed with validated data
        return User(username=username, age=age, email=email)
        
    except ValidationError as e:
        logger.error(f"User creation failed: {e}")
        raise
```

### Pattern 2: Validating Configuration Files

```python
from validation_utils import (
    safe_file_read,
    validate_json_safe,
    validate_dict_schema
)

def load_config(config_path):
    """Load and validate configuration file."""
    # Read file safely
    content = safe_file_read(config_path)
    
    # Parse JSON
    config = validate_json_safe(content)
    
    # Validate schema
    schema = {
        'api_key': str,
        'timeout': int,
        'max_retries': int,
        'enabled': bool
    }
    config = validate_dict_schema(config, schema)
    
    # Additional business logic validation
    if config['timeout'] < 1:
        raise ValidationError("timeout must be at least 1")
    
    return config
```

### Pattern 3: Validating API Inputs

```python
def handle_api_request(request_data):
    """Handle API request with comprehensive validation."""
    try:
        # Parse and validate JSON
        data = validate_json_safe(request_data)
        
        # Validate required fields
        validate_json_structure(data, ['action', 'params'])
        
        # Validate specific fields
        action = validate_non_empty_string(data['action'], "action")
        
        # Validate based on action type
        if action == 'create_agent':
            validate_dict_schema(data['params'], {
                'name': str,
                'description': str,
                'tools': list
            })
        
        return process_action(action, data['params'])
        
    except ValidationError as e:
        return {
            'error': str(e),
            'status': 'validation_failed'
        }
```

## Security Considerations

### 1. Prevent Path Traversal

Always validate file paths to prevent directory traversal attacks:

```python
from validation_utils import validate_file_path
from pathlib import Path

# ❌ Dangerous - user can access any file
def read_user_file(filename):
    with open(filename) as f:
        return f.read()

# ✅ Safe - restricted to allowed directory
def read_user_file(filename):
    safe_dir = Path("/app/user_files")
    safe_path = validate_file_path(filename, safe_dir)
    return safe_file_read(safe_path)
```

### 2. Prevent Command Injection

Sanitize command inputs to prevent injection:

```python
from validation_utils import sanitize_command_input

# ❌ Dangerous - allows command injection
def run_command(user_input):
    os.system(f"echo {user_input}")

# ✅ Better - validates command
def run_command(user_input):
    safe_input = sanitize_command_input(user_input)
    # Still prefer subprocess with list args
    subprocess.run(["echo", safe_input])
```

**Best Practice**: Always use parameterized commands:
```python
# ✅ Best - use list arguments
subprocess.run(["python", script_name, arg1, arg2])
```

### 3. Validate JSON Safely

Prevent JSON injection and ensure proper structure:

```python
from validation_utils import validate_json_safe

# ❌ Dangerous - no validation
data = json.loads(user_input)

# ✅ Safe - validates structure
data = validate_json_safe(user_input)
```

### 4. Input Sanitization

Always sanitize user inputs:

```python
from validation_utils import validate_agent_name

# ❌ Dangerous - no sanitization
agent_file = f".github/agents/{user_input}.md"

# ✅ Safe - validates and sanitizes
agent_name = validate_agent_name(user_input)
agent_file = f".github/agents/{agent_name}.md"
```

## Testing Validation

### Test Valid Inputs
```python
def test_valid_inputs():
    assert validate_agent_name("test-agent") == "test-agent"
    assert validate_email("user@example.com") == "user@example.com"
```

### Test Invalid Inputs
```python
def test_invalid_inputs():
    # Test empty inputs
    with pytest.raises(ValidationError):
        validate_agent_name("")
    
    # Test wrong types
    with pytest.raises(ValidationError):
        validate_agent_name(123)
    
    # Test invalid formats
    with pytest.raises(ValidationError):
        validate_email("not-an-email")
```

### Test Boundary Values
```python
def test_boundaries():
    # Test min/max values
    assert validate_numeric_range(0, 0, 100) == 0
    assert validate_numeric_range(100, 0, 100) == 100
    
    with pytest.raises(ValidationError):
        validate_numeric_range(-1, 0, 100)
```

### Test Edge Cases
```python
def test_edge_cases():
    # Test whitespace handling
    assert validate_non_empty_string("  test  ") == "test"
    
    # Test special characters
    with pytest.raises(ValidationError):
        validate_agent_name("../etc/passwd")
```

## Error Messages

### Guidelines for Error Messages

1. **Be Specific**: Clearly state what's wrong
2. **Be Actionable**: Explain how to fix it
3. **Be Consistent**: Use similar patterns across codebase
4. **Include Context**: Show the invalid value (when safe)

### Examples

```python
# ❌ Bad - vague
raise ValidationError("Invalid input")

# ✅ Good - specific and actionable
raise ValidationError(
    f"Agent name '{name}' is too long ({len(name)} chars). "
    f"Maximum length is 100 characters"
)

# ❌ Bad - no context
raise ValidationError("Field missing")

# ✅ Good - includes context
raise ValidationError(
    f"Configuration is missing required keys: {', '.join(missing_keys)}"
)

# ❌ Bad - technical jargon
raise ValidationError("Regex match failed")

# ✅ Good - user-friendly
raise ValidationError(
    f"URL '{url}' is not valid. URLs must start with http:// or https://"
)
```

## Integration Examples

### Example: Enhancing an Existing Tool

Before:
```python
def process_agent(agent_name):
    agent_file = f".github/agents/{agent_name}.md"
    with open(agent_file) as f:
        return f.read()
```

After:
```python
from validation_utils import (
    validate_agent_name,
    validate_file_path,
    safe_file_read,
    ValidationError
)

def process_agent(agent_name):
    try:
        # Validate agent name
        agent_name = validate_agent_name(agent_name)
        
        # Construct and validate path
        agents_dir = Path(".github/agents")
        agent_file = agents_dir / f"{agent_name}.md"
        agent_file = validate_file_path(agent_file, agents_dir)
        
        # Read file safely
        return safe_file_read(agent_file)
        
    except ValidationError as e:
        logger.error(f"Failed to process agent '{agent_name}': {e}")
        raise
```

## Summary

✅ **DO**:
- Validate at system boundaries
- Use provided validation utilities
- Provide clear error messages
- Test with invalid inputs
- Handle validation errors gracefully

❌ **DON'T**:
- Trust user input without validation
- Skip validation for "internal" code
- Silently ignore validation errors
- Use vague error messages
- Forget to test edge cases

---

**Need Help?** Check the `validation_utils.py` module for available validation functions, or see `test_validation_utils.py` for comprehensive usage examples.
