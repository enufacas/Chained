# Shell Common Library

This library provides shared functions and variables for shell scripts in the Chained project, following the DRY (Don't Repeat Yourself) principle and improving maintainability.

## Usage

Source the library at the beginning of your shell script:

```bash
#!/bin/bash
source "$(dirname "$0")/tools/shell-common.sh"
```

If your script is in a subdirectory:

```bash
#!/bin/bash
source "$(dirname "$0")/../tools/shell-common.sh"
```

## Available Functions

### `check_gh_cli [require_auth]`

Checks if GitHub CLI is available and optionally authenticated.

**Parameters:**
- `require_auth` (optional): Set to "false" to skip authentication check. Default is "true".

**Returns:**
- `0` if ready
- `1` if not available or not authenticated

**Example:**
```bash
if ! check_gh_cli; then
    exit 1
fi
```

### `print_status <status> <message>`

Prints a status message with appropriate color coding.

**Parameters:**
- `status`: One of "OK", "WARN", or "ERROR"
- `message`: The message to display

**Example:**
```bash
print_status "OK" "Configuration is valid"
print_status "WARN" "Optional file missing"
print_status "ERROR" "Required file not found"
```

### `print_header <title>`

Prints a section header with underline.

**Parameters:**
- `title`: The section title

**Example:**
```bash
print_header "System Configuration"
```

## Available Variables

### Color Codes

The library exports these color code variables:

- `GREEN`: Green text color
- `YELLOW`: Yellow text color
- `BLUE`: Blue text color
- `RED`: Red text color
- `NC`: No color (reset)

**Example:**
```bash
echo -e "${GREEN}Success!${NC}"
echo -e "${RED}Error occurred${NC}"
```

## Benefits

1. **Reduced Duplication**: Eliminates ~80 lines of duplicate code across multiple scripts
2. **Consistency**: All scripts use the same color codes and formatting
3. **Maintainability**: Changes to common functions only need to be made once
4. **Testability**: Shared functions can be tested independently
5. **SOLID Principles**: Single Responsibility and DRY principles applied

## Scripts Using This Library

- `check-status.sh`
- `validate-system.sh`
- `kickoff-system.sh`
- `verify-schedules.sh`
- `evaluate-workflows.sh`

## Implementation Notes

The library follows best practices:
- Functions return proper exit codes
- Error messages go to stderr
- Variables are properly exported
- Functions can be overridden if needed
