# Intentional Bug Quick Reference Card

## 🎯 Purpose
Test the error_observer A2A agent with a **real runtime error** (not simulated)

## 📍 Bug Location
```
File: infrastructure/docker/adk-agents/code-reviewer/agent.py
Line: 141
Type: ZeroDivisionError (division by zero)
```

## 🔑 Trigger Keyword
```
test_error_observer
```
(Case-insensitive - works with TEST_ERROR_OBSERVER, Test_Error_Observer, etc.)

## ⚡ Quick Trigger Methods

### Method 1: Automated Script (Easiest)
```bash
./scripts/trigger-bug-test.sh https://chained-code-reviewer-XXX.a.run.app
```

### Method 2: A2A UI (Recommended for Visual Testing)
1. Go to: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/
2. Ask: 
```
Please review this code:

```python
# test_error_observer
def test():
    return "hello"
```
```

### Method 3: Direct API (For Advanced Testing)
```bash
curl -X POST "https://chained-code-reviewer-XXX.a.run.app/a2a/tasks" \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","parts":[{"text":"Review: test_error_observer"}]}}'
```

## 📊 Expected Flow
```
Request → code-reviewer
    ↓
Keyword detected
    ↓
ZeroDivisionError
    ↓
report_agent_error()
    ↓
error_observer
    ↓
GitHub Issue
    ↓
A2A UI Display
```

## ✅ Success Indicators

**Agent Response:**
- Task state: "failed"
- Error message: Contains "ZeroDivisionError"

**Error Observer:**
- Status shows recent error
- Last error details visible

**GitHub:**
- New issue created
- Contains error details, stack trace, hash

**A2A UI:**
- Error visible in error observer status

## 🔍 Quick Verification Commands

```bash
# Check code-reviewer health
curl https://chained-code-reviewer-XXX.a.run.app/health

# Check error-observer health
curl https://chained-error-observer-XXX.a.run.app/health

# Check error-observer status
curl https://chained-error-observer-XXX.a.run.app/status

# Check recent logs
gcloud logging read "resource.type=cloud_run_revision" --limit 20

# Check GitHub issues
open https://github.com/enufacas/Chained/issues
```

## 🚀 Deployment

```bash
# Build and deploy
cd infrastructure/docker/adk-agents
gcloud builds submit --tag gcr.io/chained-ai/code-reviewer code-reviewer/
gcloud run deploy chained-code-reviewer \
  --image gcr.io/chained-ai/code-reviewer \
  --region us-central1 \
  --set-env-vars ERROR_OBSERVER_URL=https://[URL]
```

## 🧹 Removal

```bash
# 1. Find the bug
grep -n "INTENTIONAL BUG" infrastructure/docker/adk-agents/code-reviewer/agent.py

# 2. Delete lines 136-143 from agent.py

# 3. Remove test files
rm docs/ERROR_OBSERVER_TESTING.md
rm tests/test_code_reviewer_intentional_bug.py
rm INTENTIONAL_BUG_SUMMARY.md
rm VERIFICATION_CHECKLIST.md
rm scripts/trigger-bug-test.sh
rm QUICK_REFERENCE.md  # This file

# 4. Redeploy
gcloud run deploy chained-code-reviewer \
  --image gcr.io/chained-ai/code-reviewer
```

## 📚 Full Documentation

- **User Guide:** `docs/ERROR_OBSERVER_TESTING.md`
- **Implementation Summary:** `INTENTIONAL_BUG_SUMMARY.md`
- **Verification Checklist:** `VERIFICATION_CHECKLIST.md`

## 🆘 Troubleshooting

**Error not flowing through?**
1. Check ERROR_OBSERVER_URL is set
2. Verify both services are healthy
3. Check Cloud Run logs
4. See INTENTIONAL_BUG_SUMMARY.md "Troubleshooting" section

**GitHub issue not created?**
1. Verify GITHUB_PAT in error-observer
2. Check PAT has `repo` and dispatch permissions
3. Check error-observer logs for GitHub API errors

**Need help?**
- Review `INTENTIONAL_BUG_SUMMARY.md`
- Check Cloud Run logs
- Verify environment variables

---

**Version:** 1.0 | **Created:** 2025-12-04 | **Agent:** @troubleshoot-expert
