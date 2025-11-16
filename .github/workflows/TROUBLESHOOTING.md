# Workflow Troubleshooting Guide

Created by **@troubleshoot-expert** to help resolve common workflow issues.

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
4. **Create an issue** with:
   - Workflow name and run ID
   - Error message
   - What you've tried

---

*Created by **@troubleshoot-expert** - Making troubleshooting systematic and efficient* 🔧
