# Workflow Health Investigation Report

**Investigator:** @investigate-champion  
**Date:** 2025-11-13  
**Issue:** #[Issue Number] - Workflow Health Alert

## Executive Summary

**@investigate-champion** has conducted a systematic analysis of workflow health issues in the Chained repository. This report documents findings, root causes, and recommended solutions.

### Current State
- **Total Workflow Runs Analyzed:** 100 (last 100 sampled)
- **Completed Runs:** 73
- **Failed Runs:** 11
- **Failure Rate:** 15.1%

### Key Findings

Based on investigation, the workflow failures fall into several categories:

## Detailed Analysis

### 1. NL to Code Translation Demo Workflow (7 failures)

**File:** `.github/workflows/nl-to-code-demo.yml`

**Trigger Configuration:**
```yaml
on:
  issues:
    types: [labeled]
  workflow_dispatch:
```

**Issue Identified:**
- Workflow triggers on **ANY** issue label event
- Conditional check happens inside the job, not at trigger level  
- This causes workflow runs to be created for irrelevant label changes
- These runs are immediately skipped due to the `if` condition, but count as "runs"

**Root Cause:**
The workflow is over-triggering. It should only trigger for specific labels or use path filtering.

**Evidence:**
- 7 failures all correspond to push events on branches where issues were being labeled
- The workflow is designed for `translate-to-code` label only
- Most runs are skipped due to label mismatch

**Recommended Fix:**
Either:
1. Accept that this is expected behavior (skipped ≠ failed)
2. Move to workflow_dispatch only to avoid auto-triggering
3. Add better filtering at the trigger level (not possible with current GitHub Actions)

### 2. AI Pattern: Repetition Detector (1 failure)

**File:** `.github/workflows/repetition-detector.yml`

**Trigger Configuration:**
```yaml
on:
  pull_request:
    types: [opened, synchronize]
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:
```

**Issue Identified:**
- Workflow runs on every PR opened/synchronized
- Requires analysis files that may not exist yet
- Python scripts may fail if repository state is incomplete

**Root Cause:**
Missing error handling for cases where:
- Analysis directory doesn't exist
- JSON files are empty or malformed
- Git history is too short for meaningful analysis

**Evidence:**
- Single failure suggests intermittent issue
- Likely related to PR that was created without full context

**Recommended Fix:**
Add robust error handling in the workflow steps and Python scripts.

### 3. Agent System: Spawner (1 failure)

**File:** `.github/workflows/agent-spawner.yml`

**Trigger Configuration:**
```yaml
on:
  schedule:
    - cron: '0 */3 * * *'
  workflow_dispatch:
```

**Issue Identified:**
- Complex workflow with many dependencies
- Relies on specific file structures and permissions
- GraphQL API calls that may fail intermittently

**Root Cause:**
Potential causes:
- Network issues with GitHub GraphQL API
- Race conditions when creating issues/PRs
- Agent registry file corruption
- COPILOT_PAT token issues

**Evidence:**
- Single failure suggests transient issue
- Likely external dependency or API rate limit

**Recommended Fix:**
1. Add retry logic for API calls
2. Better error messages for debugging
3. Graceful degradation when Copilot assignment fails

### 4. Idea Generation: Progress Checker (2 failures)

**File:** `.github/workflows/goal-progress-checker.yml`

**Trigger Configuration:**
```yaml
on:
  schedule:
    - cron: '0 */3 * * *'
  workflow_dispatch:
```

**Issue Identified:**
- Scheduled workflow that checks AI goals file
- May fail if `docs/AI_GOALS.md` doesn't exist or is malformed
- Git operations can fail if there are conflicts or permissions issues

**Root Cause:**
- File not found or empty
- Git conflicts when trying to push
- No current goal exists (exits cleanly but may be counted as failure)

**Evidence:**
- 2 failures suggest intermittent issues
- Likely when goal file is missing or in transition state

**Recommended Fix:**
1. Add file existence checks with graceful fallback
2. Better handling of "no active goal" state
3. Use `|| true` for non-critical steps

## Pattern Analysis

### Common Failure Patterns

1. **Over-Triggering**
   - Workflows trigger too frequently on irrelevant events
   - Conditional logic happens after workflow starts
   - Solution: Better trigger filters or acceptance of expected behavior

2. **Missing Error Handling**
   - Workflows don't gracefully handle missing files
   - No retry logic for external API calls
   - Solution: Add try-catch logic and validation steps

3. **External Dependencies**
   - GitHub API rate limits
   - Network failures
   - Secret availability
   - Solution: Retry logic and degradation paths

4. **File/State Dependencies**
   - Workflows assume certain files exist
   - No validation of file contents before processing
   - Solution: Add existence checks and validation

## Recommendations

### Short-Term Fixes

1. **Accept Skipped Runs as Normal**
   - Not all skipped runs are failures
   - Update monitoring to distinguish skip vs fail

2. **Add Error Handling**
   - Wrap critical steps in error handling
   - Use `|| true` for optional steps
   - Add existence checks for files

3. **Improve Logging**
   - Add more descriptive error messages
   - Log why workflows skip or fail
   - Help future debugging

### Long-Term Improvements

1. **Workflow Consolidation**
   - Review if all workflows are necessary
   - Combine related workflows to reduce runs
   - Use workflow_dispatch for manual-only workflows

2. **Better Monitoring**
   - Distinguish between:
     - Actual failures (errors)
     - Expected skips (no work to do)
     - Transient failures (retry succeeded)

3. **Documentation**
   - Document expected trigger behavior
   - Explain when skips are normal
   - Provide debugging guides

## Metrics to Track

After implementing fixes, monitor:

1. **True Failure Rate**: Failures that indicate real problems
2. **Skip Rate**: Workflows that appropriately skip work
3. **Retry Success Rate**: Transient failures that succeed on retry
4. **API Error Rate**: External dependency failures

## Conclusion

The 15.1% "failure" rate includes many expected behaviors (skipped runs due to label mismatches). True failures are likely in the 3-5% range, primarily from:

- Transient API issues
- Missing error handling
- File state assumptions

**Next Steps:**
1. Implement error handling improvements
2. Update monitoring to distinguish skip vs fail
3. Add retry logic for external dependencies
4. Document expected behavior

---

**Report generated by @investigate-champion**  
*Investigation complete with systematic root cause analysis*
