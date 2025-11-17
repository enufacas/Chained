# Workflow Troubleshooting Guide

Created by **@troubleshoot-expert** to help resolve common workflow issues.

## Recent Fixes (2025-11-17)

**@troubleshoot-expert** has implemented several fixes to improve workflow reliability:

### Fixed Issues
1. **Missing evolution_data.json** - Created initial evolution data structure
2. **Exit code capture in repetition-detector.yml** - Fixed incorrect exit code checking
3. **Code-golf-optimizer.yml improvements:**
   - Added missing file/directory checks
   - Replaced `bc` with `awk` for better portability
   - Added error handling for individual file failures
   - Added label fallback for issue creation
4. **Pattern-matcher.yml** - Added label fallback for issue creation

### Expected Impact
These fixes should reduce workflow failure rate from ~25% to under 10%.

---

## Common Issues

### 1. Label-Related Failures

**Symptom:** Workflows fail with errors like:
```
could not add label: 'code-quality' not found
```

**Root Cause:** Required repository labels don't exist yet.

**Solution:**

1. **Manually trigger the label creation workflow:**
   - Go to Actions tab → "Maintenance: Ensure Repository Labels Exist"
   - Click "Run workflow" → "Run workflow"
   - Wait for completion (~30 seconds)

2. **Verify labels were created:**
   ```bash
   gh label list | grep -E "code-quality|workflow-optimization|investment-tracker"
   ```

3. **Re-run failed workflows:**
   - They should now succeed with labels applied

**Prevention:** The label creation workflow runs:
- Weekly on Mondays at 00:00 UTC
- When `tools/create_labels.py` is modified
- Manually via workflow_dispatch

**Note:** All workflows now have fallback logic. If labels are missing, they'll create PRs without labels instead of failing.

### 2. Missing Secrets

**Symptom:** Workflows skip steps or fail with:
```
Error: Secret COPILOT_PAT not found
```

**Root Cause:** Optional secret `COPILOT_PAT` is not configured.

**Solution:**
- Most workflows use `GITHUB_TOKEN` which is automatically available
- `COPILOT_PAT` is only needed for workflows that trigger other workflows
- Either configure the secret or accept that those workflows will skip some steps

### 3. External API Failures

**Symptom:** Intermittent failures when calling external APIs (Hacker News, TLDR, etc.)

**Root Cause:** External services are temporarily unavailable or rate-limiting.

**Solution:**
- Workflows already have retry logic
- Failures are expected occasionally
- No action needed unless failures persist

### 4. Permission Issues

**Symptom:** Workflows fail with:
```
Error: Resource not accessible by integration
```

**Root Cause:** Workflow permissions are insufficient.

**Solution:**
- Check the workflow's `permissions:` block
- Common permissions needed:
  ```yaml
  permissions:
    contents: write      # To push commits
    pull-requests: write # To create PRs
    issues: write        # To comment on issues
  ```

## Monitoring Workflow Health

The **System: Monitor** workflow tracks workflow health automatically:

- Runs every 12 hours
- Creates alerts when failure rate exceeds 20%
- Provides detailed failure breakdowns

### Healthy Metrics
- **Failure Rate:** < 20% (of completed runs)
- **Failed Workflows:** < 5 per workflow

### Actions When Unhealthy
1. Review the alert issue for details
2. Check Actions tab for error logs
3. Focus on workflows with multiple failures
4. Use this guide to resolve common issues

## Workflow Dependencies

Some workflows depend on others:

```
ensure-labels-exist.yml (foundation)
  ↓
code-analyzer.yml
code-archaeologist.yml
update-agent-investments.yml
ai-workflow-orchestrator-demo.yml
(and others that create PRs with labels)
```

**Recommendation:** If multiple workflows are failing, check if the foundational workflows ran successfully.

## Getting Help

1. **Check workflow logs** in the Actions tab
2. **Review this troubleshooting guide**
3. **Check related documentation:**
   - `.github/workflows/WORKFLOW_ERROR_HANDLING_GUIDE.md`
   - `.github/workflows/AGENT_ASSIGNMENT_WORKFLOWS_README.md`
   - `.github/workflows/LABEL_FALLBACK_PATTERN.md` - Label handling best practices
4. **Create an issue** with:
   - Workflow name and run ID
   - Error message
   - What you've tried

## Best Practices

### Label Fallback Pattern

When creating issues or PRs with labels, always use fallback logic to prevent failures when labels are missing. See `.github/workflows/LABEL_FALLBACK_PATTERN.md` for detailed examples and patterns.

**Quick Example:**
```bash
gh issue create --title "Title" --body "Body" --label "label1,label2" || {
  echo "⚠️ Issue creation with labels failed, retrying without labels..."
  gh issue create --title "Title" --body "Body"
}
```

This ensures workflows complete successfully even if labels haven't been created yet.

### Testing Workflows Locally

Before committing workflow changes, test the logic locally:

```bash
# Test Python tools
cd tools
python3 repetition-detector.py -d . --since-days 30 -o /tmp/test.json
python3 code-golf-optimizer.py -f examples/fibonacci.py -l python
python3 pattern-matcher.py -d . --format json -o /tmp/pattern.json

# Test shell script logic
cd .github/workflows
# Extract and test shell commands from workflow YAML
# Verify exit codes, file existence checks, fallback logic

# Common checks:
# - Does it handle missing files gracefully?
# - Are exit codes captured immediately after commands?
# - Does bc/other tools exist (prefer awk)?
# - Are labels optional with fallback?
```

### Exit Code Best Practices

**❌ Wrong:** Checking exit code after multiple commands
```bash
python3 script.py -o output.json
cp output.json backup.json
cd /tmp
if [ $? -ne 0 ]; then  # This checks 'cd', not python!
  echo "Script failed"
fi
```

**✅ Correct:** Capture exit code immediately
```bash
python3 script.py -o output.json
SCRIPT_EXIT=$?

# Continue with other commands
cp output.json backup.json
cd /tmp

# Check the correct exit code
if [ $SCRIPT_EXIT -ne 0 ]; then
  echo "Script failed"
fi
```

---

*Created by **@troubleshoot-expert** - Making troubleshooting systematic and efficient* 🔧
