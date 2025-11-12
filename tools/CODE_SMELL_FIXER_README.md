# Code Smell Fixer Documentation

## Overview

The Code Smell Fixer is an automated tool for detecting and fixing common code smells in Python code. It can analyze single files or entire directories, applying safe transformations to improve code quality while preserving functionality.

## Features

### 🔍 Detection Capabilities

The tool detects the following code smells:

1. **Unused Imports** - Import statements that are never used
2. **Magic Numbers** - Hardcoded numeric literals that should be constants
3. **Missing Docstrings** - Functions and classes without documentation
4. **Poor Variable Names** - Single-letter or generic variable names
5. **Missing Type Hints** - Functions without type annotations
6. **Long Functions** - Functions exceeding 50 lines
7. **Deep Nesting** - Code with nesting depth greater than 4 levels

### 🔧 Auto-Fix Capabilities

The tool can automatically fix:

- ✅ **Unused Imports** - Removes unused import statements
- ✅ **Magic Numbers** - Extracts repeated numbers into named constants
- ✅ **Missing Docstrings** - Adds skeleton docstrings as TODO reminders

The following smells are detected but require manual refactoring:

- ⚠️ **Poor Variable Names** - Suggests improvements (unsafe to auto-rename)
- ⚠️ **Missing Type Hints** - Detects missing hints (requires context to add correctly)
- ⚠️ **Long Functions** - Identifies long functions (requires logic understanding to split)
- ⚠️ **Deep Nesting** - Detects deep nesting (requires refactoring expertise)

## Installation

No installation required. The tool is a standalone Python script that uses only standard library modules.

## Usage

### Basic Usage

```bash
# Analyze and fix a single file
python tools/code-smell-fixer.py -f path/to/file.py

# Analyze and fix all Python files in a directory
python tools/code-smell-fixer.py -d path/to/directory
```

### Command-Line Options

```
-f, --file FILE           Single file to analyze and fix
-d, --directory DIR       Directory to analyze and fix
-o, --output FILE         Output file for report
--format {text,json}      Report format (default: text)
--dry-run                 Preview changes without applying them
--interactive             Ask before applying each fix
--no-backup               Do not create backups before modifying files
```

### Examples

#### Dry-Run Mode (Preview Changes)

```bash
# See what changes would be made without actually making them
python tools/code-smell-fixer.py -f myfile.py --dry-run
```

#### Interactive Mode

```bash
# Review and approve each fix individually
python tools/code-smell-fixer.py -f myfile.py --interactive
```

#### Directory Analysis with Report

```bash
# Analyze entire directory and save report
python tools/code-smell-fixer.py -d src/ -o report.txt

# Generate JSON report
python tools/code-smell-fixer.py -d src/ -o report.json --format json
```

#### Without Backups

```bash
# Skip creating backup files (use with caution)
python tools/code-smell-fixer.py -f myfile.py --no-backup
```

## Safety Features

### 1. Backup System

By default, the tool creates backups before modifying any file:

```
your_project/
├── myfile.py                    # Modified file
└── .smell_fixer_backups/        # Backup directory
    └── myfile.py.20240112_103045.bak  # Timestamped backup
```

To restore from backup:
```bash
cp .smell_fixer_backups/myfile.py.20240112_103045.bak myfile.py
```

### 2. Dry-Run Mode

Preview all changes before applying them:

```bash
python tools/code-smell-fixer.py -d src/ --dry-run
```

This shows what would be changed without modifying any files.

### 3. Interactive Mode

Review and approve each fix individually:

```bash
python tools/code-smell-fixer.py -f myfile.py --interactive
```

For each fix, you can:
- Press `y` to apply the fix
- Press `n` to skip the fix
- Press `q` to quit

### 4. Syntax Validation

The tool validates Python syntax before and after modifications to ensure code remains valid.

## Examples of Fixes

### Example 1: Removing Unused Imports

**Before:**
```python
import os
import sys
import json
import tempfile

def main():
    print(os.path.exists("."))
    sys.exit(0)
```

**After:**
```python
import os
import sys

def main():
    print(os.path.exists("."))
    sys.exit(0)
```

### Example 2: Extracting Magic Numbers

**Before:**
```python
def calculate_discount(price):
    if price > 100:
        return price * 0.85
    return price * 0.95
```

**After:**
```python
# Constants extracted by code-smell-fixer
CONSTANT_100 = 100

def calculate_discount(price):
    if price > CONSTANT_100:
        return price * 0.85
    return price * 0.95
```

### Example 3: Adding Docstrings

**Before:**
```python
def calculate_total(items):
    return sum(item.price for item in items)

class ShoppingCart:
    def __init__(self):
        self.items = []
```

**After:**
```python
def calculate_total(items):
    """TODO: Add function docstring."""
    return sum(item.price for item in items)

class ShoppingCart:
    """TODO: Add class docstring."""
    def __init__(self):
        self.items = []
```

### Example 4: Poor Variable Names (Detection Only)

The tool detects poor names but doesn't auto-fix them (too risky):

```
Detected poor variable names:
- Line 5: 'a' (single_letter)
- Line 7: 'temp' (generic)
- Line 9: 'data' (generic)
```

These require manual review and renaming based on context.

## Report Format

### Text Report

```
# Code Smell Fixer Report

**Generated:** 2024-01-12T10:30:45.123456+00:00

**Directory:** src/

## Summary
- Total files processed: 15
- Files modified: 8
- Total fixes applied: 23

## Details

### src/utils.py
- unused_imports: 2 fix(es)
- magic_numbers: 3 fix(es)
- missing_docstrings: 1 fix(es)

### src/models.py
- unused_imports: 1 fix(es)
- missing_docstrings: 4 fix(es)

## Fixes Applied
Total: 23

## Fixes Skipped
Total: 0
```

### JSON Report

```json
{
  "directory": "src/",
  "timestamp": "2024-01-12T10:30:45.123456+00:00",
  "files": [
    {
      "file": "src/utils.py",
      "fixes": {
        "unused_imports": {
          "success": true,
          "changes": 2,
          "unused_imports": ["json", "tempfile"],
          "backup": ".smell_fixer_backups/utils.py.20240112_103045.bak"
        }
      }
    }
  ],
  "summary": {
    "total_files": 15,
    "files_modified": 8,
    "total_fixes": 23
  }
}
```

## Integration with Existing Tools

The Code Smell Fixer leverages the existing `code-analyzer.py` for detection capabilities:

```python
from code_analyzer import CodeAnalyzer

# Use existing analyzer for consistent detection
analyzer = CodeAnalyzer()
results = analyzer.analyze_python_file("myfile.py")
```

## Best Practices

### 1. Start with Dry-Run

Always preview changes first:
```bash
python tools/code-smell-fixer.py -d src/ --dry-run
```

### 2. Use Version Control

Commit your code before running the fixer:
```bash
git commit -am "Before code smell fixes"
python tools/code-smell-fixer.py -d src/
git diff  # Review changes
```

### 3. Run Tests After Fixes

Always run your test suite after applying fixes:
```bash
python tools/code-smell-fixer.py -d src/
python -m pytest  # Or your test command
```

### 4. Review Generated Constants

Magic number extraction may create generic constant names. Review and rename them for clarity:

```python
# Generated
CONSTANT_100 = 100

# Better
MAX_PRICE_FOR_DISCOUNT = 100
```

### 5. Complete TODO Docstrings

The tool adds skeleton docstrings. Replace them with meaningful documentation:

```python
# Generated
def calculate_total(items):
    """TODO: Add function docstring."""
    return sum(item.price for item in items)

# Better
def calculate_total(items):
    """
    Calculate the total price of all items.
    
    Args:
        items: List of items with price attributes
        
    Returns:
        Total price as a float
    """
    return sum(item.price for item in items)
```

## Limitations

1. **Context-Dependent Fixes**: The tool cannot understand business logic, so some fixes (like variable renaming) require human judgment.

2. **Type Hints**: Adding correct type hints requires understanding data types used at runtime, which the tool cannot determine statically.

3. **Function Splitting**: Breaking down long functions requires understanding the logical flow, which is beyond automated analysis.

4. **Nested Logic**: Reducing nesting depth often requires refactoring patterns like guard clauses or early returns, which require code understanding.

5. **Magic Number Naming**: Generated constant names are generic (e.g., `CONSTANT_100`) and should be renamed to reflect their meaning.

## Troubleshooting

### Issue: "Syntax error" when processing file

**Cause**: The file contains invalid Python syntax.

**Solution**: Fix syntax errors manually before running the fixer.

### Issue: Backups filling up disk space

**Cause**: Multiple runs create many backup files.

**Solution**: Clean up old backups or use `--no-backup` flag.

```bash
# Remove old backups
find . -name ".smell_fixer_backups" -type d -exec rm -rf {} +
```

### Issue: Fix breaks tests

**Cause**: The fix changed behavior (rare but possible).

**Solution**: Restore from backup and review the specific fix:

```bash
cp .smell_fixer_backups/file.py.timestamp.bak file.py
python tools/code-smell-fixer.py -f file.py --interactive
```

### Issue: Too many constants generated

**Cause**: Magic number detection is too aggressive.

**Solution**: Review and consolidate similar constants, or adjust the threshold in the code.

## Performance

The tool is designed for reasonable performance:

- **Single File**: < 1 second for typical files
- **Small Project** (< 100 files): < 10 seconds
- **Large Project** (> 1000 files): 1-2 minutes

For very large codebases, consider:
1. Running on specific directories
2. Using parallel processing (future enhancement)
3. Running as part of CI/CD on changed files only

## Testing

Run the comprehensive test suite:

```bash
python tools/test_code_smell_fixer.py
```

The test suite includes:
- ✅ Unit tests for each fix type
- ✅ Dry-run mode tests
- ✅ Backup functionality tests
- ✅ Error handling tests
- ✅ Edge case tests
- ✅ Integration tests

## Contributing

To add new smell detectors or fixes:

1. Add detection logic in the appropriate method
2. Add auto-fix logic if safe to automate
3. Add comprehensive tests in `test_code_smell_fixer.py`
4. Update this documentation
5. Submit a pull request

## License

This tool is part of the Chained project and follows the same license.

## Support

For issues or questions:
- Check this documentation
- Review the test suite for examples
- Open an issue in the repository

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-12  
**Author:** Feature Architect Agent
