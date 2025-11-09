# 🔍 Cross-Repository Pattern Matcher

An intelligent best practices analyzer that scans code repositories to detect anti-patterns, security issues, and code quality problems across multiple programming languages.

## Overview

The Cross-Repository Pattern Matcher is a powerful static analysis tool that helps maintain code quality by automatically detecting common issues and suggesting improvements. It's designed to work seamlessly with the Chained autonomous AI system.

## Features

- 🎯 **Multi-Language Support**: Python, JavaScript, Bash, YAML
- 🔒 **Security Analysis**: Detects hardcoded secrets, SQL injection risks, unsafe eval()
- 📊 **Detailed Reports**: Text and JSON output formats with statistics
- 🤖 **Automated Workflow**: Weekly analysis via GitHub Actions
- ⚡ **Fast Scanning**: Efficiently processes entire repositories
- 📈 **Categorized Issues**: Organized by severity and category
- 🔄 **Cross-Repository**: Designed to analyze patterns across multiple projects

## Installation

No installation required! The pattern matcher is a standalone Python script with no external dependencies:

```bash
# Make executable
chmod +x tools/pattern-matcher.py

# Run directly
./tools/pattern-matcher.py --help
```

## Usage

### Basic Usage

```bash
# Scan a single file
python3 tools/pattern-matcher.py -f script.py

# Scan current directory recursively
python3 tools/pattern-matcher.py -d .

# Scan specific directory
python3 tools/pattern-matcher.py -d /path/to/repo

# Save report to file
python3 tools/pattern-matcher.py -d . -o report.txt
```

### Advanced Options

```bash
# Get JSON output for programmatic use
python3 tools/pattern-matcher.py -d . --format json

# Get statistics only
python3 tools/pattern-matcher.py -d . --stats

# Scan non-recursively
python3 tools/pattern-matcher.py -d tools/ --recursive false
```

### Command-Line Options

- `-f, --file`: Scan a single file
- `-d, --directory`: Scan a directory (default: current directory)
- `-r, --recursive`: Scan directories recursively (default: True)
- `--format`: Output format - `text` or `json` (default: text)
- `-o, --output`: Output file (default: stdout)
- `--stats`: Show statistics only

## Pattern Categories

### Python Patterns

#### Security (❌ Error)
- **Hardcoded Secrets**: Detects API keys, passwords, tokens in code
- **SQL Injection**: Identifies string formatting in SQL queries

#### Error Handling (⚠️ Warning)
- **Bare Except Clauses**: Catches all exceptions including system exits

#### Code Quality (ℹ️ Info)
- **Debug Print Statements**: Suggests using logging module
- **Missing Type Hints**: Recommends adding type annotations
- **TODO Comments**: Suggests converting to tracked issues

### JavaScript Patterns

#### Security (❌ Error)
- **eval() Usage**: Dangerous code execution

#### Best Practices (⚠️ Warning)
- **var Keyword**: Suggests using let/const
- **Loose Equality**: Recommends === instead of ==

#### Debugging (ℹ️ Info)
- **console.log**: Production code cleanup
- **TODO Comments**: Issue tracking

### Bash Patterns

#### Best Practices (⚠️ Warning)
- **Unquoted Variables**: Prevents word splitting issues

#### Portability (ℹ️ Info)
- **Missing Shebang**: Ensures correct interpreter
- **Missing set -e**: Exit on error handling

### YAML Patterns

#### Security (❌ Error)
- **Hardcoded Secrets**: Detects secrets in configuration files

## Examples

### Example 1: Scan Python File

```bash
$ python3 tools/pattern-matcher.py -f example.py
```

**Output:**
```
================================================================================
Cross-Repository Pattern Matcher Report
================================================================================

Total Issues Found: 5
  - Errors: 1
  - Warnings: 2
  - Info: 2

--------------------------------------------------------------------------------
❌ ERROR (1)
--------------------------------------------------------------------------------

Category: SECURITY

  [py-hardcoded-secrets] Potential hardcoded secrets
  File: example.py:10
  Code: api_key = "sk_test_1234567890abcdefghijklmnop"
  💡 Use environment variables or secret management

--------------------------------------------------------------------------------
⚠️ WARNING (2)
--------------------------------------------------------------------------------

Category: ERROR-HANDLING

  [py-no-bare-except] Bare except clause
  File: example.py:15
  Code: except:
  💡 Use specific exception types instead of bare except:
```

### Example 2: Get Statistics

```bash
$ python3 tools/pattern-matcher.py -d . --stats
```

**Output:**
```json
{
  "total_issues": 153,
  "by_severity": {
    "error": 2,
    "warning": 24,
    "info": 127
  },
  "by_category": {
    "security": 2,
    "error-handling": 48,
    "type-safety": 24,
    "debugging": 12,
    "maintenance": 2,
    "best-practices": 21
  },
  "by_file": {
    "tools/code-golf-optimizer.py": 3,
    "tools/pattern-matcher.py": 10,
    "src/main.py": 15
  }
}
```

### Example 3: JSON Output

```bash
$ python3 tools/pattern-matcher.py -f script.py --format json
```

**Output:**
```json
[
  {
    "pattern_id": "py-hardcoded-secrets",
    "pattern_name": "Potential hardcoded secrets",
    "severity": "error",
    "file_path": "script.py",
    "line_number": 10,
    "matched_text": "api_key = \"sk_test_1234567890\"",
    "suggestion": "Use environment variables or secret management",
    "category": "security"
  }
]
```

## GitHub Actions Integration

The pattern matcher runs automatically every Monday at 11 AM UTC, generating weekly code quality reports.

### Automatic Workflow

The workflow:
1. Scans the entire repository
2. Generates detailed reports
3. Creates GitHub issues with findings
4. Uploads artifacts for review

### Manual Trigger

You can also run the workflow manually:

1. Go to **Actions** → **Pattern Matcher**
2. Click **Run workflow**
3. Optionally specify:
   - Directory to scan
   - Minimum severity level
4. View the generated issue and artifacts

## Pattern Definitions

Patterns are defined in the `PatternMatcher` class with the following structure:

```python
{
    'id': 'unique-pattern-id',
    'name': 'Human-readable name',
    'pattern': r'regex-pattern',
    'severity': 'error|warning|info',
    'category': 'security|best-practices|etc',
    'suggestion': 'How to fix this issue',
    'description': 'Why this matters'
}
```

## Best Practices

### ✅ Do

- Run pattern analysis regularly (weekly recommended)
- Address errors (❌) immediately - they're security/critical issues
- Review warnings (⚠️) for code quality improvements
- Consider info (ℹ️) suggestions for best practices
- Use in CI/CD pipelines for automated checks
- Customize patterns for your project's needs

### ⚠️ Don't

- Ignore security errors - they need immediate attention
- Treat all warnings equally - prioritize by context
- Disable patterns without understanding them
- Commit known issues without tracking them
- Over-optimize - focus on real problems first

## Extending the Pattern Matcher

### Adding New Patterns

To add a new pattern:

1. Edit `tools/pattern-matcher.py`
2. Add pattern definition to appropriate language in `_load_patterns()`
3. Test with example code
4. Update documentation

Example:

```python
{
    'id': 'py-unused-imports',
    'name': 'Unused imports',
    'pattern': r'^import\s+\w+$',
    'severity': 'info',
    'category': 'code-quality',
    'suggestion': 'Remove unused imports',
    'description': 'Unused imports bloat code'
}
```

### Adding New Languages

To add support for a new language:

1. Add language patterns to `_load_patterns()`
2. Update `detect_language()` with file extensions
3. Add test cases
4. Update documentation

## Testing

Run the test suite:

```bash
# Run all tests
python3 tools/test_pattern_matcher.py

# Run with verbose output
python3 tools/test_pattern_matcher.py -v

# Run specific test
python3 tools/test_pattern_matcher.py TestPatternMatcher.test_python_bare_except
```

## Performance

The pattern matcher is designed for speed:

- **Single File**: < 10ms
- **Small Repo (< 100 files)**: < 1 second
- **Medium Repo (< 1000 files)**: < 10 seconds
- **Large Repo (> 1000 files)**: < 1 minute

Performance characteristics:
- Linear time complexity O(n) where n = lines of code
- Minimal memory footprint
- No external dependencies
- Skips binary files and common ignore patterns

## Limitations

- **False Positives**: Some patterns may trigger incorrectly
- **Context Awareness**: Cannot understand complex business logic
- **Language Coverage**: Only supports Python, JavaScript, Bash, YAML
- **Regex Limitations**: Complex patterns may miss edge cases
- **No Semantic Analysis**: Only pattern matching, not full AST analysis

## Integration with Chained

The pattern matcher integrates seamlessly with the Chained autonomous system:

- **Weekly Reports**: Automatic code quality monitoring
- **Issue Tracking**: Findings automatically become tracked issues
- **Learning Integration**: Patterns can be influenced by external learnings
- **Timeline Updates**: Analysis results appear in GitHub Pages timeline
- **Copilot Integration**: Issues can be assigned to Copilot for fixes

## Comparison with Other Tools

| Feature | Pattern Matcher | ESLint | Pylint | ShellCheck |
|---------|----------------|--------|--------|------------|
| Multi-language | ✅ | ❌ | ❌ | ❌ |
| No dependencies | ✅ | ❌ | ❌ | ❌ |
| Cross-repo analysis | ✅ | ❌ | ❌ | ❌ |
| Custom patterns | ✅ | ✅ | ✅ | ❌ |
| GitHub Actions | ✅ | ✅ | ✅ | ✅ |
| Security focus | ✅ | Partial | Partial | Partial |

## Contributing

To contribute new patterns or improvements:

1. Fork the repository
2. Add your patterns to `pattern-matcher.py`
3. Add test cases to `test_pattern_matcher.py`
4. Update documentation
5. Submit a pull request

## Related Tools

- **Code Golf Optimizer**: Minimizes code character count
- **Smart Idea Generator**: Creates ideas from learnings
- **Auto Review**: AI-powered code review
- **Timeline Updater**: Documents system activity

## FAQ

**Q: Why do I get so many info-level suggestions?**
A: Info suggestions are recommendations, not requirements. Focus on errors and warnings first.

**Q: Can I disable specific patterns?**
A: Yes, edit the pattern definitions in `pattern-matcher.py` or filter by category.

**Q: How accurate are the security detections?**
A: The patterns catch common issues but are not a replacement for comprehensive security audits.

**Q: Can I use this in CI/CD?**
A: Yes! The tool exits with code 1 if errors are found, perfect for CI/CD gates.

**Q: Does it support my language?**
A: Currently supports Python, JavaScript, Bash, and YAML. More languages can be added.

## License

Part of the Chained autonomous AI development system.

## Resources

- [Static Analysis in Practice](https://en.wikipedia.org/wiki/Static_program_analysis)
- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)
- [Python Security Best Practices](https://snyk.io/blog/python-security-best-practices/)
- [JavaScript Security Best Practices](https://www.npmjs.com/package/security-checklist)

---

*Generated by the Chained Cross-Repository Pattern Matcher*
