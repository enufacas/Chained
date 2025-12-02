# Gemini Context Gathering Guide

## ⚠️ Critical Understanding: Gemini Has No Repository Access

The Gemini API is **just an API call**. It does NOT have access to:
- ❌ Your repository files
- ❌ Git history
- ❌ GitHub MCP server
- ❌ Copilot tools (view, bash, etc.)
- ❌ Code search capabilities
- ❌ Any other context unless you explicitly send it

**You must gather and send context manually.**

## The Problem

When you ask gemini-consultant for help without providing code context:

```python
# ❌ BAD - Gemini has no idea what the code looks like
ask_gemini_fix_code(
    issue_description="Fix authentication bug",
    file_path="tools/auth.py"
)
```

Gemini receives:
```
Issue: Fix authentication bug
File: tools/auth.py
Code: <NOTHING>
```

Result: Generic advice that doesn't fit your codebase.

## The Solution: Context Gathering

The gemini-consultant agent has two tools to gather context:
1. **view** - Read files from the repository
2. **bash** - Execute shell commands to search, analyze, etc.

### Context Gathering Workflow

```python
# Step 1: Read the problematic code
code = view("tools/auth.py")

# Step 2: Read related files
tests = view("tests/test_auth.py")
config = view("config/security.yml")

# Step 3: Search for patterns
imports = bash("grep -r 'import jwt' tools/")
usage = bash("git grep 'validate_token'")

# Step 4: Check recent changes
history = bash("git log --oneline -10 -- tools/auth.py")

# Step 5: Build comprehensive context
context = f"""
Current Code (tools/auth.py):
{code}

Tests (tests/test_auth.py):
{tests}

JWT usage in codebase:
{imports}

Where validate_token is called:
{usage}

Recent changes:
{history}
"""

# Step 6: NOW consult Gemini with full context
response = ask_gemini(
    question="How to add expiration checking to token validation?",
    context=context
)
```

## Context Gathering Checklist

Before consulting Gemini, gather:

### Essential Context
- [ ] **The actual code** with the issue (use `view`)
- [ ] **Error messages** if available
- [ ] **Related function/class** definitions

### Important Context
- [ ] **Test files** that cover the code
- [ ] **Import statements** and dependencies
- [ ] **Configuration files** if relevant
- [ ] **Recent git history** for the file
- [ ] **Similar patterns** elsewhere in codebase

### Nice-to-Have Context
- [ ] **Documentation** for the code
- [ ] **Related issues** or PR descriptions
- [ ] **Usage examples** from the codebase
- [ ] **Performance metrics** if optimizing

## Common Bash Commands for Context Gathering

```bash
# Search for patterns
bash("grep -r 'pattern' directory/")
bash("git grep 'function_name'")

# Find files
bash("find . -name '*.py' -path '*/tests/*'")

# Git history
bash("git log --oneline -10 -- path/to/file.py")
bash("git log --all --grep='keyword'")

# File metadata
bash("wc -l path/to/file.py")  # Line count
bash("git blame path/to/file.py | head -20")  # Who wrote it

# Dependencies
bash("grep 'import' path/to/file.py")
bash("pip show package-name")

# Running state
bash("python3 -c 'import module; print(module.__version__)'")
```

## Real-World Examples

### Example 1: Fix Authentication Bug

```python
# Gather comprehensive context
code = view("tools/auth.py")
tests = view("tests/test_auth.py")
jwt_usage = bash("git grep 'jwt.decode' | head -20")
config = view("config/security.yml")

# Build rich context
context = f"""
Current Authentication Code:
---
{code}
---

Existing Tests:
---
{tests}
---

JWT Usage Patterns in Codebase:
---
{jwt_usage}
---

Security Configuration:
---
{config}
---
"""

# NOW ask Gemini with full context
fix = ask_gemini_fix_code(
    issue_description="Authentication allows expired JWT tokens",
    file_path="tools/auth.py",
    code_snippet=code  # Send actual code
)
```

### Example 2: Performance Optimization

```python
# Gather performance context
code = view("api/handlers.py")
profiling = bash("python3 -m cProfile api/handlers.py 2>&1 | head -30")
db_queries = bash("grep 'query' api/handlers.py")
tests = view("tests/test_handlers.py")

context = f"""
Current Handler Code:
{code}

Profiling Output (top 30 slowest):
{profiling}

Database Queries:
{db_queries}

Performance Tests:
{tests}
"""

response = ask_gemini(
    question="How to optimize the slow database queries?",
    context=context
)
```

### Example 3: Architecture Decision

```python
# Gather architectural context
structure = bash("tree -L 3 -I '__pycache__|*.pyc'")
modules = bash("ls -la src/")
imports = bash("grep -r 'from src' . | head -20")
config = view("pyproject.toml")

context = f"""
Current Project Structure:
{structure}

Main Modules:
{modules}

Import Patterns:
{imports}

Project Config:
{config}
"""

response = ask_gemini(
    question="Should we split this into microservices?",
    context=context
)
```

## Anti-Patterns to Avoid

### ❌ Bad: No Context
```python
ask_gemini("How to fix the bug in auth.py?")
# Gemini has no idea what auth.py contains
```

### ❌ Bad: Just File Path
```python
ask_gemini_fix_code(
    issue_description="Fix bug",
    file_path="tools/auth.py"  # No actual code
)
# Gemini can't read the file
```

### ❌ Bad: Generic Description
```python
context = "The auth code has issues"
ask_gemini("Fix it", context=context)
# No actual code, no specifics
```

### ✅ Good: Rich Context
```python
code = view("tools/auth.py")
tests = view("tests/test_auth.py")
context = f"Code:\n{code}\n\nTests:\n{tests}"
ask_gemini_fix_code(
    issue_description="JWT tokens not validated for expiration",
    file_path="tools/auth.py",
    code_snippet=code
)
```

## Tips for Effective Context Gathering

### 1. Start with the Core
Always include the actual code file first:
```python
code = view("path/to/file.py")
```

### 2. Add Tests
Tests show expected behavior:
```python
tests = view("tests/test_file.py")
```

### 3. Search for Patterns
Find similar code:
```python
similar = bash("git grep 'similar_function'")
```

### 4. Check Dependencies
Understand what's imported:
```python
imports = bash("grep '^import\\|^from' path/to/file.py")
```

### 5. Review History
See recent changes:
```python
history = bash("git log --oneline -5 -- path/to/file.py")
```

### 6. Combine Everything
Build comprehensive context:
```python
context = f"""
Code:
{code}

Tests:
{tests}

Similar Patterns:
{similar}

Dependencies:
{imports}

Recent Changes:
{history}
"""
```

## Token Limits

Gemini has a context limit (typically 4096-8192 tokens). If your context is too large:

1. **Prioritize:** Include only relevant code sections
2. **Summarize:** Use bash to extract key lines:
   ```python
   key_functions = bash("grep -A 10 'def validate_token' tools/auth.py")
   ```
3. **Focus:** Send just the problematic function, not entire file
4. **Split:** Make multiple smaller queries instead of one large one

## Measuring Context Quality

Good context includes:
- ✅ Actual source code (not descriptions)
- ✅ Relevant test cases
- ✅ Error messages or symptoms
- ✅ Related code patterns
- ✅ Configuration if relevant

Bad context is:
- ❌ Just file paths
- ❌ Generic descriptions
- ❌ No actual code
- ❌ Irrelevant information

## Summary

**The Golden Rule:** Gemini only knows what you tell it.

1. **Before calling** `ask_gemini()` or `ask_gemini_fix_code()`:
   - Use `view()` to read files
   - Use `bash()` to search and analyze
   - Build comprehensive context string

2. **Pass context explicitly**:
   - Include actual code in `code_snippet` parameter
   - Include related context in `context` parameter
   - Don't assume Gemini can see your repository

3. **The agent's job** is to:
   - Gather context from the repository
   - Format it for Gemini
   - Send it in the API call
   - Interpret Gemini's response with repository knowledge

**Remember:** You are the bridge between Gemini and the repository. Gather context first, then consult.
