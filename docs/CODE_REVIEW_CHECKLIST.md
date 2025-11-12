# Code Review Checklist

**Author**: 💭 Turing (coach-master agent)  
**Purpose**: A practical, actionable checklist for reviewing pull requests  
**Date**: 2025-11-12

## Overview

Think of code reviews like quality checkpoints on an assembly line—each checkpoint catches different types of issues before they reach production. This checklist ensures consistent, thorough reviews that improve code quality while respecting everyone's time.

Good code reviews are:
- **Fast**: Complete within 24 hours
- **Focused**: Address what matters most
- **Clear**: Provide actionable feedback
- **Educational**: Explain the "why" behind suggestions

## Quick Reference

Use this abbreviated checklist for fast reviews:

- [ ] Does it work? (Correctness)
- [ ] Can I understand it? (Clarity)
- [ ] Can we maintain it? (Maintainability)
- [ ] Does it follow best practices? (Standards)
- [ ] Is it tested? (Quality)
- [ ] Is it secure? (Safety)

## Detailed Review Checklist

### 1. Correctness ✓

**Does the code actually work?**

- [ ] **Logic is sound**: No obvious bugs or logical errors
- [ ] **Edge cases handled**: Boundary conditions are addressed
- [ ] **Error handling present**: Failures are caught and handled appropriately
- [ ] **Requirements met**: PR addresses the issue/feature completely
- [ ] **No regressions**: Existing functionality isn't broken

**Red Flags:**
- Off-by-one errors in loops or array access
- Null/undefined/None not handled
- Missing return statements
- Incorrect operator usage (= vs ==, and vs or)

**Example:**
```python
# ❌ Bad - Off-by-one error
for i in range(len(items) + 1):  # Will index out of bounds
    process(items[i])

# ✅ Good - Correct range
for i in range(len(items)):
    process(items[i])
```

### 2. Clarity 📖

**Can others understand this code?**

- [ ] **Meaningful names**: Variables, functions, classes have self-explanatory names
- [ ] **Function size**: Functions do one thing and are reasonably sized (<50 lines)
- [ ] **Clear intent**: Code reads like prose, minimal mental gymnastics required
- [ ] **Comments where needed**: Complex logic explained, not obvious code documented
- [ ] **Consistent style**: Follows project conventions

**Red Flags:**
- Single-letter variables (except loop counters)
- Deeply nested code (>3 levels)
- Functions that do multiple unrelated things
- Comments that explain what instead of why
- Inconsistent naming conventions

**Example:**
```python
# ❌ Bad - Unclear intent
def p(d):
    t = 0
    for x in d:
        if x > 0:
            t += x
    return t

# ✅ Good - Clear intent
def calculate_positive_sum(numbers):
    """Calculate the sum of all positive numbers in the list."""
    total = 0
    for number in numbers:
        if number > 0:
            total += number
    return total
```

### 3. Maintainability 🔧

**Can we work with this code long-term?**

- [ ] **DRY principle**: No unnecessary code duplication
- [ ] **Proper abstractions**: Right level of abstraction for the problem
- [ ] **Separation of concerns**: Different responsibilities in different modules
- [ ] **Dependencies managed**: External dependencies justified and minimal
- [ ] **Configuration externalized**: Magic numbers/strings in constants or config

**Red Flags:**
- Copy-pasted code blocks
- God classes/functions that know too much
- Hardcoded values scattered throughout
- Tight coupling between components
- Mixed concerns (business logic + presentation)

**Example:**
```python
# ❌ Bad - Hardcoded values, duplication
def validate_agent_name(name):
    if len(name) < 2 or len(name) > 100:
        raise ValueError("Invalid name length")
    
def validate_tag(tag):
    if len(tag) < 2 or len(tag) > 100:
        raise ValueError("Invalid tag length")

# ✅ Good - DRY, configurable
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100

def validate_string_length(value, min_len, max_len, field_name):
    """Validate string length with clear error messages."""
    if len(value) < min_len or len(value) > max_len:
        raise ValueError(
            f"{field_name} must be {min_len}-{max_len} chars, got {len(value)}"
        )

def validate_agent_name(name):
    validate_string_length(name, MIN_NAME_LENGTH, MAX_NAME_LENGTH, "Agent name")
```

### 4. Best Practices 🎯

**Does it follow engineering principles?**

- [ ] **SOLID principles**: Single Responsibility, proper abstractions
- [ ] **Error handling**: Fail fast with clear messages
- [ ] **Type safety**: Types used appropriately (type hints in Python, etc.)
- [ ] **Resource management**: Files/connections properly closed
- [ ] **Immutability**: Prefer immutable data where appropriate

**Red Flags:**
- Functions with side effects not indicated by name
- Swallowed exceptions (empty catch blocks)
- Mutable default arguments in Python
- Direct database/file access in business logic
- Missing type hints in new Python code

**Example:**
```python
# ❌ Bad - Mutable default argument
def add_tag(agent_id, tags=[]):
    tags.append(agent_id)  # Modifies shared default list!
    return tags

# ✅ Good - Immutable default
def add_tag(agent_id, tags=None):
    if tags is None:
        tags = []
    return tags + [agent_id]  # Returns new list
```

### 5. Testing 🧪

**Is it adequately tested?**

- [ ] **Tests exist**: New code has corresponding tests
- [ ] **Tests pass**: All tests pass locally and in CI
- [ ] **Coverage adequate**: Critical paths are tested
- [ ] **Edge cases tested**: Boundary conditions covered
- [ ] **Tests are clear**: Test names describe what they test

**Red Flags:**
- No tests for new functionality
- Tests that always pass (testing nothing)
- Tests dependent on execution order
- Tests with unclear names
- Missing assertions

**Example:**
```python
# ❌ Bad - Unclear test, no assertion
def test_agent_registry():
    registry = load_registry()
    # Test passes even if registry is empty!

# ✅ Good - Clear test with assertions
def test_agent_registry_contains_required_keys():
    """Agent registry must have version, agents, and config keys."""
    registry = load_registry()
    
    assert 'version' in registry, "Missing 'version' key"
    assert 'agents' in registry, "Missing 'agents' key"
    assert 'config' in registry, "Missing 'config' key"
```

### 6. Security 🔒

**Are there security vulnerabilities?**

- [ ] **Input validation**: All external input validated
- [ ] **SQL injection prevented**: Parameterized queries used
- [ ] **Path traversal prevented**: File paths validated
- [ ] **Command injection prevented**: Shell commands avoided or sanitized
- [ ] **Secrets protected**: No hardcoded credentials/tokens
- [ ] **Dependencies safe**: No known vulnerabilities in dependencies

**Red Flags:**
- String concatenation for SQL queries
- User input directly in shell commands
- Hardcoded API keys or passwords
- Missing input validation
- Unvalidated file paths

**Example:**
```python
# ❌ Bad - Path traversal vulnerability
def read_agent_file(filename):
    path = f".github/agents/{filename}"  # User could pass "../../../etc/passwd"
    with open(path) as f:
        return f.read()

# ✅ Good - Path validated
def read_agent_file(filename):
    """Read agent file with path validation."""
    from pathlib import Path
    
    base_dir = Path(".github/agents").resolve()
    file_path = (base_dir / filename).resolve()
    
    # Ensure path is within base_dir
    if not file_path.is_relative_to(base_dir):
        raise ValueError(f"Invalid path: {filename}")
    
    with open(file_path) as f:
        return f.read()
```

### 7. Performance ⚡

**Are there obvious performance issues?**

- [ ] **No unnecessary loops**: Efficient algorithms used
- [ ] **Database queries optimized**: N+1 queries avoided
- [ ] **Caching appropriate**: Expensive operations cached when sensible
- [ ] **Resource leaks prevented**: Memory/file handles properly managed
- [ ] **Scalability considered**: Works with expected data volumes

**Red Flags:**
- Nested loops with large datasets
- Loading entire files into memory
- Repeated database queries in loops
- Missing indexes on database queries
- Exponential time complexity

**Example:**
```python
# ❌ Bad - N+1 query problem
def get_agent_metrics(agent_ids):
    metrics = []
    for agent_id in agent_ids:
        # Database query in loop!
        metric = db.query(f"SELECT * FROM metrics WHERE agent_id = {agent_id}")
        metrics.append(metric)
    return metrics

# ✅ Good - Single query
def get_agent_metrics(agent_ids):
    # Fetch all metrics in one query
    metrics = db.query(
        "SELECT * FROM metrics WHERE agent_id IN (?)",
        agent_ids
    )
    return metrics
```

### 8. Documentation 📝

**Is it properly documented?**

- [ ] **Public APIs documented**: Functions/classes have docstrings
- [ ] **Complex logic explained**: Non-obvious code has comments
- [ ] **README updated**: User-facing changes documented
- [ ] **API changes noted**: Breaking changes called out
- [ ] **Examples provided**: Usage examples for new features

**Red Flags:**
- Missing docstrings on public functions
- Outdated documentation
- Breaking changes not mentioned
- No usage examples for new features

**Example:**
```python
# ❌ Bad - No documentation
def validate_agent(data):
    if 'name' not in data or 'spec' not in data:
        return False
    return True

# ✅ Good - Clear documentation
def validate_agent(data: dict) -> bool:
    """
    Validate that agent data contains required fields.
    
    Args:
        data: Dictionary containing agent configuration
        
    Returns:
        True if agent data is valid, False otherwise
        
    Example:
        >>> validate_agent({'name': 'alpha', 'spec': 'code-review'})
        True
        >>> validate_agent({'name': 'beta'})
        False
    """
    required_fields = ['name', 'spec']
    return all(field in data for field in required_fields)
```

## Review Process

### 1. Before You Start (1 minute)

- [ ] Read the PR description and linked issue
- [ ] Understand the goal and context
- [ ] Check CI status (don't review if failing)
- [ ] Note PR size (large PRs need more time)

### 2. First Pass - High Level (5-10 minutes)

- [ ] Does the approach make sense?
- [ ] Is the change in the right place?
- [ ] Are there architectural concerns?
- [ ] Is the scope appropriate (not too large)?

**Stop here if major issues found. Provide feedback and request changes.**

### 3. Second Pass - Details (15-30 minutes)

- [ ] Review each file using the checklist above
- [ ] Check tests thoroughly
- [ ] Verify error handling
- [ ] Look for edge cases
- [ ] Check for security issues

### 4. Final Check (5 minutes)

- [ ] Tests pass locally (for critical changes)
- [ ] Documentation is accurate
- [ ] No obvious issues missed
- [ ] Feedback is clear and actionable

## Providing Feedback

### Structure Your Comments

**For Issues:**
```
[Category] Issue description

Why this is a problem: <explanation>
Suggested fix: <concrete suggestion>

Example:
<code showing the fix>
```

**For Questions:**
```
Question: <your question>
Context: <why you're asking>
```

**For Praise:**
```
✅ Well done: <what was done well>
```

### Tone Guidelines

- **Be respectful**: Code is not the person
- **Be specific**: Point to exact lines
- **Be constructive**: Suggest solutions, not just problems
- **Be clear**: No ambiguity about what to change
- **Be pragmatic**: Focus on what matters

**Example Feedback:**

❌ Bad:
```
This code is messy and hard to read.
```

✅ Good:
```
[Clarity] The function name `process_data` is too generic.

Why this matters: Function names should describe what they do specifically.
Suggested fix: Rename to `validate_agent_configuration` to indicate it validates agent data.

This makes the code self-documenting and easier to navigate.
```

## Priority Levels

Use these to help authors prioritize fixes:

- 🔴 **Blocking**: Must fix before merge (security, correctness)
- 🟡 **Important**: Should fix before merge (maintainability, best practices)
- 🟢 **Nice-to-have**: Consider for future (minor improvements)
- 💬 **Discussion**: Open question, not blocking

## Common Pitfalls to Avoid

### As a Reviewer

1. **Bikeshedding**: Don't argue about style if project has conventions
2. **Perfectionism**: Don't demand perfect code, demand good enough
3. **Scope creep**: Don't ask for unrelated improvements
4. **Late feedback**: Don't wait days to review
5. **Vague comments**: Don't say "this could be better" without specifics

### As an Author

1. **Large PRs**: Keep PRs small and focused (<400 lines)
2. **No description**: Always explain what and why
3. **Arguing**: Accept feedback gracefully, discuss if needed
4. **Ignoring CI**: Fix failing tests before requesting review
5. **No self-review**: Review your own code first

## Chained-Specific Considerations

### Agent System Reviews

- [ ] Agent registry changes maintain backwards compatibility
- [ ] New specializations have clear definitions
- [ ] Metrics weights sum to 1.0
- [ ] Agent spawning logic is safe

### Workflow Reviews

- [ ] Workflow syntax is valid YAML
- [ ] Triggers are appropriate
- [ ] Secrets are properly referenced (not hardcoded)
- [ ] Permissions are minimal required
- [ ] Error handling is present

### Python Code Reviews

- [ ] Type hints used for function signatures
- [ ] Validation utilities used for input validation
- [ ] Tests use pytest, not boolean returns
- [ ] Error messages are actionable
- [ ] Security best practices followed

## Quick Decision Tree

```
Is the code correct?
├─ No → 🔴 Request changes (blocking)
└─ Yes
   ├─ Is it tested?
   │  ├─ No → 🔴 Request changes (blocking)
   │  └─ Yes
   │     ├─ Is it clear/maintainable?
   │     │  ├─ No → 🟡 Request changes (important)
   │     │  └─ Yes
   │     │     ├─ Are there security issues?
   │     │     │  ├─ Yes → 🔴 Request changes (blocking)
   │     │     │  └─ No
   │     │     │     ├─ Minor improvements possible?
   │     │     │     │  ├─ Yes → 🟢 Suggest (nice-to-have)
   │     │     │     │  └─ No → ✅ Approve
```

## Templates

### Approval Comment

```markdown
✅ **Approved**

Great work on this PR! Specifically:
- [What was done well]
- [What was done well]

[Optional minor suggestions for future improvements]
```

### Request Changes Comment

```markdown
🔴 **Changes Requested**

This PR needs the following changes before it can be merged:

**Blocking Issues:**
1. [Issue with explanation and suggested fix]
2. [Issue with explanation and suggested fix]

**Important (Should Fix):**
- [Issue with explanation]

**Nice-to-Have:**
- [Suggestion for improvement]

Happy to discuss any of these points!
```

## Summary

Code reviews are about **improving code quality** while **respecting time**. Focus on:

1. **Correctness**: Does it work?
2. **Clarity**: Can we understand it?
3. **Maintainability**: Can we maintain it?
4. **Testing**: Is it tested?
5. **Security**: Is it safe?

Everything else is secondary. Be direct, be clear, be constructive.

---

*Remember: Every code review is an opportunity to raise the bar and help the team grow. Review code you'd want to maintain at 2am during an outage.*

---

[Related: Best Practices Guide](BEST_PRACTICES.md) | [Related: SOLID Principles](SOLID_PRINCIPLES_GUIDE.md) | [Related: Testing Guide](CODE_REVIEW_GUIDE_TESTING.md)
