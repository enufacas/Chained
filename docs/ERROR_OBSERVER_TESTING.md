# Error Observer Testing - Intentional Bug

## Overview

An **intentional bug** has been introduced in the `code-reviewer` A2A agent to test the error observer system. This is a **real** runtime error (not simulated) that allows testing the complete error reporting and handling flow.

## Bug Details

**Location:** `infrastructure/docker/adk-agents/code-reviewer/agent.py` (line ~141)

**Type:** `ZeroDivisionError` (division by zero)

**Trigger:** The bug activates when code submitted for review contains the keyword `test_error_observer` (case-insensitive)

**Implementation:**
```python
if "test_error_observer" in code.lower():
    _ = 1 / 0  # This will raise ZeroDivisionError
```

## Error Flow

```
User/Workflow sends code review request
    ↓
code-reviewer agent receives request via A2A protocol
    ↓
Checks if code contains "test_error_observer"
    ↓ (YES)
Intentional ZeroDivisionError is raised
    ↓
Exception caught in send_message() handler (agent.py:335)
    ↓
report_agent_error() called (agent.py:338)
    ↓
ErrorEvent created from exception
    ↓
Error sent to error_observer agent via A2A
    ↓
error_observer receives error event
    ↓
error_observer dispatches to GitHub API (repository_dispatch)
    ↓
GitHub issue created automatically
    ↓
Error visible in A2A UI error observer status
```

## How to Trigger the Bug

### Method 1: Via A2A UI (Recommended)

1. Navigate to https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/
2. Use the chat interface to ask for a code review
3. Include the following code snippet:

```python
# test_error_observer
def hello():
    print("This code will trigger the error observer test")
```

**Example prompt:**
```
Please review this code:

```python
# test_error_observer
def example_function():
    return "testing"
```
```

### Method 2: Via Direct API Call

```bash
# Get the code-reviewer agent URL
CODE_REVIEWER_URL="https://chained-code-reviewer-XXX.a.run.app"

# Send a review request
curl -X POST "$CODE_REVIEWER_URL/a2a/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "parts": [
        {
          "text": "Review this code:\n```python\n# test_error_observer\ndef test():\n    pass\n```"
        }
      ]
    }
  }'
```

### Method 3: Via Workflow

Create a GitHub workflow that uses the autonomous code reviewer on a test PR containing the keyword.

## Expected Behavior

When the bug is triggered:

1. **Agent Response:** The code-reviewer agent will return a task with `state: "failed"`
2. **Error Message:** The error message will mention `ZeroDivisionError`
3. **Error Observer:** An error event will be sent to the error_observer agent
4. **GitHub Issue:** A new issue should be created in the repository with:
   - Title indicating a Cloud Run error
   - Error details from the code-reviewer agent
   - Stack trace showing the division by zero
   - Labels: likely `cloudrun-error` or similar
5. **A2A UI:** The error observer status endpoint should show the error was processed

## Verification Checklist

After triggering the bug:

- [ ] Code-reviewer agent returns failed task
- [ ] Error observer receives the error event
- [ ] GitHub issue is created automatically
- [ ] Issue contains:
  - [ ] Service name: `code-reviewer`
  - [ ] Error message mentioning `ZeroDivisionError`
  - [ ] Stack trace
  - [ ] Error hash for deduplication
- [ ] A2A UI shows error in error observer agent

## Debugging

If the error doesn't flow through as expected:

1. **Check error_observer URL configuration:**
   ```bash
   # In code-reviewer Cloud Run service
   echo $ERROR_OBSERVER_URL
   ```

2. **Check error_observer logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chained-error-observer" \
     --limit 50 --format json
   ```

3. **Check code-reviewer logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chained-code-reviewer" \
     --limit 50 --format json
   ```

4. **Verify error_observer agent card:**
   ```bash
   curl https://chained-error-observer-XXX.a.run.app/.well-known/agent.json
   ```

## Removing the Bug

Once testing is complete, remove the intentional bug:

1. Open `infrastructure/docker/adk-agents/code-reviewer/agent.py`
2. Find lines ~136-143 (marked with `INTENTIONAL BUG FOR ERROR OBSERVER TESTING`)
3. Delete the entire block:
   ```python
   # INTENTIONAL BUG FOR ERROR OBSERVER TESTING
   # ... (delete lines 136-143)
   ```
4. Commit and redeploy the code-reviewer agent

**Command to find the bug:**
```bash
grep -n "INTENTIONAL BUG" infrastructure/docker/adk-agents/code-reviewer/agent.py
```

## Why This Approach

This intentional bug approach provides:

1. **Real Error:** Actual Python exception (not simulated)
2. **Controlled:** Only triggers with specific keyword
3. **Observable:** Flows through entire A2A error handling system
4. **Safe:** Doesn't affect normal code review operations
5. **Removable:** Easy to locate and remove with clear comments
6. **Testable:** Can be repeatedly triggered for testing

## Related Documentation

- [Error Observer Overview](./error_observer_overview.md)
- [Error Observer Schema](./error_observer_schema.md)
- [A2A Protocol Documentation](./a2a/)

## Support

If you encounter issues:

1. Check Cloud Run logs for both services
2. Verify ERROR_OBSERVER_URL environment variable
3. Verify GitHub PAT permissions in error_observer
4. Check A2A UI error observer status endpoint
5. Review error_observer agent health endpoint

---

**Created:** 2025-12-04  
**Purpose:** Test error_observer A2A agent functionality  
**Status:** Active - Bug is intentionally present in code-reviewer agent
