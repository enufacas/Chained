# Gemini Code-Fixing Examples

This document demonstrates the new code-fixing capabilities of the gemini-consultant agent.

## Overview

The gemini-consultant agent has been upgraded to provide **actual code fixes** instead of just analysis. When you ask for help with code issues, you'll receive:

1. ✅ Actual fixed code with before/after examples
2. ✅ Specific file paths and line numbers
3. ✅ Implementation steps
4. ✅ Test commands
5. ✅ Brief explanations (after showing the fix)

## Example 1: Authentication Bug Fix

### Request
```
"ask gemini to fix the authentication bug - tokens not being validated for expiration"
```

### Expected Response Format
```markdown
## 🤔 Gemini Consultation - Code Fix

**Problem:** JWT tokens are not being validated for expiration, allowing expired tokens to authenticate

**Files Affected:**
- `tools/auth.py:45` - Missing expiration check in validate_token()

**Gemini's Solution:**

### Fix: tools/auth.py (Line 45)

**Before:**
```python
def validate_token(token):
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    return decoded.get('user_id')  # ❌ No expiration check
```

**After:**
```python
import time

def validate_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        # Check token expiration
        exp = decoded.get('exp')
        if exp and exp < time.time():
            raise ValueError("Token expired")
        
        return decoded.get('user_id')
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {e}")
```

**What Changed:**
- Added explicit expiration time check using `time.time()`
- Added try/except to catch PyJWT's built-in expiration errors
- Properly raise ValueError for consistency with error handling patterns
- Import time module for timestamp comparison

**Why This Fixes It:**
The original code decoded JWT tokens but never verified the 'exp' claim,
allowing authentication with expired tokens. The fix adds both manual
expiration checking and proper exception handling for PyJWT's validation.

**Implementation Steps:**
1. Open `tools/auth.py`
2. Navigate to line 45
3. Replace the validate_token() function with the fixed version
4. Ensure `import time` is at the top of the file
5. Save the file

**Test Command:**
```bash
# Add test for expired token
pytest tests/test_auth.py::test_expired_token -v

# Run all auth tests
pytest tests/test_auth.py -v
```

**My Analysis:**
This is a security vulnerability (CWE-613: Insufficient Session Expiration).
The fix aligns with our existing error handling patterns and properly handles
both manual checks and PyJWT's built-in validation.
```

## Example 2: Null Pointer Bug Fix

### Request
```
"ask gemini about the bug in src/utils.py where process() crashes on None input"
```

### Expected Response Format
```markdown
## 🤔 Gemini Consultation - Code Fix

**Problem:** Function crashes with AttributeError when receiving None input

**Files Affected:**
- `src/utils.py:78` - No null check in process() function

**Gemini's Solution:**

### Fix: src/utils.py (Line 78)

**Before:**
```python
def process(data):
    return data.split()  # ❌ Crashes if data is None
```

**After:**
```python
def process(data):
    """Process input data by splitting into tokens.
    
    Args:
        data: String data to process
        
    Returns:
        List of tokens
        
    Raises:
        ValueError: If data is None or not a string
    """
    if data is None:
        raise ValueError("Data cannot be None")
    
    if not isinstance(data, str):
        raise TypeError(f"Expected str, got {type(data).__name__}")
    
    return data.split()
```

**What Changed:**
- Added None check with descriptive error message
- Added type check to ensure data is a string
- Added comprehensive docstring
- Proper error types (ValueError for None, TypeError for wrong type)

**Why This Fixes It:**
The original function assumed data would always be a valid string. When
None is passed, calling .split() raises AttributeError. The fix adds
defensive programming with explicit validation and helpful error messages.

**Implementation Steps:**
1. Open `src/utils.py`
2. Find the process() function at line 78
3. Replace with the fixed version above
4. Save the file

**Test Command:**
```bash
# Add tests for edge cases
cat >> tests/test_utils.py << 'EOF'

def test_process_none_input():
    """Test that process raises ValueError for None input."""
    with pytest.raises(ValueError, match="cannot be None"):
        process(None)

def test_process_wrong_type():
    """Test that process raises TypeError for non-string input."""
    with pytest.raises(TypeError, match="Expected str"):
        process(123)
EOF

# Run tests
pytest tests/test_utils.py -v
```

**My Analysis:**
This is a defensive programming fix. The function now explicitly validates
inputs and provides clear error messages, making debugging easier and
preventing silent failures downstream.
```

## Example 3: Performance Optimization

### Request
```
"ask gemini how to optimize the slow database query in api/handlers.py"
```

### Expected Response Format
```markdown
## 🤔 Gemini Consultation - Code Fix

**Problem:** Slow database query causing API timeouts (>5s response time)

**Files Affected:**
- `api/handlers.py:156` - N+1 query problem in get_user_posts()

**Gemini's Solution:**

### Fix: api/handlers.py (Line 156)

**Before:**
```python
def get_user_posts(user_id):
    user = User.query.get(user_id)
    posts = []
    for post_id in user.post_ids:
        post = Post.query.get(post_id)  # ❌ N+1 queries
        posts.append(post)
    return posts
```

**After:**
```python
def get_user_posts(user_id):
    # Use join to fetch all posts in a single query
    user = User.query.get(user_id)
    
    # Single query with IN clause instead of N queries
    posts = Post.query.filter(
        Post.id.in_(user.post_ids)
    ).all()
    
    return posts
```

**Or even better with eager loading:**
```python
def get_user_posts(user_id):
    # Use SQLAlchemy's eager loading with joinedload
    from sqlalchemy.orm import joinedload
    
    user = User.query.options(
        joinedload(User.posts)
    ).get(user_id)
    
    return user.posts
```

**What Changed:**
- Replaced N+1 query loop with single query using IN clause
- Alternative: Use SQLAlchemy's eager loading with joinedload
- Reduces database queries from N+1 to 1-2 queries

**Why This Fixes It:**
The original code made one query per post (N+1 problem). If a user has
100 posts, that's 101 database queries. The fix reduces this to just
1-2 queries regardless of post count.

**Performance Impact:**
- Before: 101 queries for 100 posts ≈ 5.05 seconds
- After: 1-2 queries ≈ 0.05 seconds  
- **100x improvement**

**Implementation Steps:**
1. Open `api/handlers.py`
2. Find get_user_posts() at line 156
3. Replace with optimized version (choose one approach)
4. If using joinedload, add import at top: `from sqlalchemy.orm import joinedload`
5. Save the file

**Test Command:**
```bash
# Test functionality
pytest tests/test_handlers.py::test_get_user_posts -v

# Benchmark performance
python3 -m pytest tests/test_handlers.py::test_get_user_posts_performance \
  --benchmark-only -v

# Expected: <100ms instead of >5000ms
```

**My Analysis:**
Classic N+1 query problem. The fix uses SQLAlchemy's query optimization
features. I recommend the joinedload approach for cleaner code and
automatic relationship management.
```

## Example 4: CLI Usage - Code Fixing Mode

### Command Line
```bash
# Use the new --fix-code flag
python3 tools/ask_gemini.py \
  --fix-code "Authentication function allows expired JWT tokens" \
  --file "tools/auth.py" \
  --code "def validate_token(token): return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])"
```

### Python API
```python
from tools.ask_gemini import ask_gemini_fix_code

# Get code fix
response = ask_gemini_fix_code(
    issue_description="Function crashes when data is None",
    file_path="src/utils.py",
    code_snippet="def process(data): return data.split()"
)

print(response)
```

## Key Differences: Before vs After

### Before (Analysis-Only Pattern) ❌
```
**Problem:** The authentication code has issues.

**Analysis:**
The validate_token function doesn't check for expired tokens. This is a
security vulnerability because...

**Recommendations:**
1. You should add expiration checking
2. Consider using PyJWT's built-in validation
3. Add error handling for edge cases
4. Update documentation
```

### After (Code-First Pattern) ✅
```
**Problem:** Authentication allows expired tokens

**Fix: tools/auth.py (Line 45)**

Before:
def validate_token(token):
    return jwt.decode(token, KEY)

After:
def validate_token(token):
    decoded = jwt.decode(token, KEY, algorithms=['HS256'])
    if decoded.get('exp') < time.time():
        raise ValueError("Token expired")
    return decoded.get('user_id')

Implementation Steps:
1. Update tools/auth.py line 45
2. Test: pytest tests/test_auth.py
```

## When to Use Each Mode

### Code-Fixing Mode (Primary)
Use `ask_gemini_fix_code()` or "ask gemini to fix..." when:
- ✅ You have a specific bug or issue
- ✅ You need actual implementation code
- ✅ You want before/after comparisons
- ✅ You need file:line specifics

### General Mode (Secondary)
Use `ask_gemini()` or "ask gemini about..." when:
- ✅ Architectural decisions (with code examples)
- ✅ Design patterns (with implementations)
- ✅ Technology choices (with sample code)
- ❌ NOT for pure analysis without code

## Summary

The gemini-consultant agent now:
1. **Prioritizes code** over analysis
2. **Shows exact locations** with file:line references
3. **Provides before/after** code comparisons
4. **Includes implementation steps** that can be executed immediately
5. **Gives test commands** to verify fixes work

This transforms gemini-consultant from a "consultant that documents problems" to a "senior engineer that solves problems with working code."
