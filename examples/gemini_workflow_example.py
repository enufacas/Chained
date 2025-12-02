#!/usr/bin/env python3
"""
Example: Proper Gemini Consultation Workflow

This example demonstrates the CORRECT way to use gemini-consultant:
1. Gather repository context FIRST
2. Build comprehensive context string
3. Call Gemini with full context
4. Get specific code fixes

Author: @gemini-consultant improvements
Date: 2024-12-02
"""

import sys
sys.path.insert(0, '/home/runner/work/Chained/Chained')

from tools.ask_gemini import ask_gemini, ask_gemini_fix_code


def example_wrong_way():
    """
    ❌ WRONG: No context gathering
    
    This will produce generic advice that doesn't fit the codebase.
    """
    print("=" * 70)
    print("❌ WRONG WAY: No Context")
    print("=" * 70)
    
    # This is what happened in PR #3513
    try:
        response = ask_gemini_fix_code(
            issue_description="Fix authentication bug",
            file_path="tools/auth.py"
            # Missing: code_snippet parameter!
        )
        print("\n⚠️ This will produce generic advice:")
        print(response[:200] + "...")
    except Exception as e:
        print(f"Error (expected): {e}")
    
    print("\n❌ Problem: Gemini has no idea what the code looks like!")
    print()


def example_right_way():
    """
    ✅ CORRECT: Gather context first
    
    This produces specific, actionable code fixes.
    """
    print("=" * 70)
    print("✅ CORRECT WAY: Context Gathering First")
    print("=" * 70)
    
    # Step 1: Read the actual code (simulated)
    print("\n1. Reading code with view()...")
    code = """
def validate_token(token):
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    return decoded.get('user_id')
    """
    print(f"   ✓ Read tools/auth.py ({len(code)} chars)")
    
    # Step 2: Read tests (simulated)
    print("\n2. Reading tests with view()...")
    tests = """
def test_validate_token():
    token = create_token(user_id=123)
    assert validate_token(token) == 123
    """
    print(f"   ✓ Read tests/test_auth.py ({len(tests)} chars)")
    
    # Step 3: Search for patterns (simulated)
    print("\n3. Searching patterns with bash()...")
    patterns = """
tools/auth.py:45:def validate_token(token):
api/handlers.py:78:    user_id = validate_token(request.headers['Authorization'])
    """
    print(f"   ✓ Found usage in 2 files")
    
    # Step 4: Build comprehensive context
    print("\n4. Building comprehensive context...")
    context = f"""
Current Authentication Code (tools/auth.py):
{code}

Tests (tests/test_auth.py):
{tests}

Usage Patterns:
{patterns}
    """
    print(f"   ✓ Context built ({len(context)} chars)")
    
    # Step 5: Call Gemini with full context
    print("\n5. Consulting Gemini WITH full context...")
    print("   (This would call the actual API)")
    
    # Simulated response (what Gemini would return)
    print("\n✅ Gemini's Response (with context):")
    print("""
## Fix: tools/auth.py (Line 45)

**Before:**
```python
def validate_token(token):
    decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    return decoded.get('user_id')
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
```

**Implementation Steps:**
1. Update tools/auth.py line 45
2. Add `import time` at top of file
3. Test: pytest tests/test_auth.py -v

**Why This Works:**
Adds expiration checking that was missing. Handles both manual
check and PyJWT's built-in validation.
""")
    
    print("\n✅ Result: Specific, actionable code fix!")
    print()


def example_context_gathering_checklist():
    """
    Checklist for proper context gathering.
    """
    print("=" * 70)
    print("📋 Context Gathering Checklist")
    print("=" * 70)
    print("""
Before calling Gemini, gather:

Essential Context:
- [x] The actual code with issue (view)
- [x] Error messages if available
- [x] Related function/class definitions

Important Context:
- [x] Test files covering the code
- [x] Import statements and dependencies
- [x] Configuration files if relevant
- [x] Recent git history
- [x] Similar patterns in codebase

Nice-to-Have:
- [ ] Documentation for the code
- [ ] Related issues/PRs
- [ ] Usage examples from codebase
- [ ] Performance metrics if optimizing

Tools to Use:
- view("path/to/file.py") - Read files
- bash("grep -r 'pattern' dir/") - Search patterns
- bash("git log --oneline -5 -- file.py") - Git history
- bash("git grep 'function_name'") - Find usage
    """)


def example_actual_workflow():
    """
    Show the actual Python code workflow.
    """
    print("=" * 70)
    print("💻 Actual Python Code Workflow")
    print("=" * 70)
    print("""
# This is what the gemini-consultant agent should do:

# 1. Gather context
code = view("tools/auth.py")
tests = view("tests/test_auth.py")
history = bash("git log --oneline -5 -- tools/auth.py")
usage = bash("git grep 'validate_token'")

# 2. Build context
context = f'''
Current Code:
{code}

Tests:
{tests}

Recent Changes:
{history}

Usage:
{usage}
'''

# 3. Call Gemini with context
from tools.ask_gemini import ask_gemini_fix_code

fix = ask_gemini_fix_code(
    issue_description="Authentication allows expired JWT tokens",
    file_path="tools/auth.py",
    code_snippet=code  # Actual code included!
)

# 4. Present the fix
print(fix)
    """)


def main():
    """Run all examples."""
    print("\n" + "🎓 GEMINI CONSULTANT WORKFLOW EXAMPLES".center(70))
    print()
    
    example_wrong_way()
    example_right_way()
    example_context_gathering_checklist()
    example_actual_workflow()
    
    print("=" * 70)
    print("📚 Learn More")
    print("=" * 70)
    print("""
Documentation:
- docs/guides/GEMINI_CONTEXT_GATHERING.md - Complete guide
- examples/gemini_code_fixing_examples.md - More examples
- FINAL_SUMMARY.md - Overview of improvements

Key Takeaways:
1. Gemini API has NO repository access
2. Use view() and bash() to gather context FIRST
3. Send actual code, not just file paths
4. Build comprehensive context strings
5. Get specific, actionable code fixes

Remember: You are the bridge between Gemini and the repository!
    """)


if __name__ == "__main__":
    main()
