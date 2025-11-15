# Workflow Error Handling Guide

**Author**: @support-master  
**Purpose**: Document best practices for error handling in GitHub Actions workflows  
**Status**: Active guidance for all workflow maintenance

---

## 🎯 Overview

This guide documents the error handling patterns implemented to improve workflow reliability from a 56.1% failure rate to stable operation. All workflow maintainers should follow these patterns.

## 📋 Common Workflow Failures and Solutions

### 1. Workflow Triggering Issues (HTTP 403)

**Problem**: Using `workflow_run` triggers causes HTTP 403 errors when workflows try to trigger other workflows.

**Solution**: Remove `workflow_run` triggers and rely on scheduled triggers instead.

```yaml
# ❌ BAD - Causes HTTP 403 errors
on:
  workflow_run:
    workflows: ["Other Workflow"]
    types: [completed]

# ✅ GOOD - Use scheduled triggers
on:
  schedule:
    - cron: '30 0 * * 0'
  workflow_dispatch:
```

### 2. Missing Files or Directories

**Problem**: Workflows assume files or directories exist, causing failures when they don't.

**Solution**: Check for existence before operations.

```yaml
# ❌ BAD - Fails if directory doesn't exist
- name: Process files
  run: |
    for file in learnings/*.json; do
      process_file "$file"
    done

# ✅ GOOD - Check existence first
- name: Process files
  run: |
    if [ -d "learnings" ]; then
      if ls learnings/*.json 1>/dev/null 2>&1; then
        for file in learnings/*.json; do
          process_file "$file"
        done
      else
        echo "⚠️ No JSON files found (OK)"
      fi
    else
      echo "⚠️ Directory doesn't exist (OK)"
    fi
```

### 3. GitHub CLI Command Failures

**Problem**: `gh` commands fail or return null values, breaking subsequent steps.

**Solution**: Add error handling and null checks.

```yaml
# ❌ BAD - No error handling
- name: Get PR count
  run: |
    PR_COUNT=$(gh pr list --json number | jq 'length')
    echo "Found $PR_COUNT PRs"

# ✅ GOOD - With error handling
- name: Get PR count
  continue-on-error: true
  run: |
    PR_COUNT=$(gh pr list --json number 2>/dev/null | jq 'length' 2>/dev/null || echo "0")
    if [ "$PR_COUNT" == "null" ] || [ -z "$PR_COUNT" ]; then
      PR_COUNT="0"
    fi
    echo "Found $PR_COUNT PRs"
```

### 4. Python Script Failures

**Problem**: Python scripts fail due to missing modules or data, stopping the entire workflow.

**Solution**: Use `continue-on-error` and wrap scripts in error handling.

```yaml
# ❌ BAD - Workflow stops on script failure
- name: Run analysis
  run: |
    python3 tools/analyzer.py --input data.json

# ✅ GOOD - Graceful error handling
- name: Run analysis
  id: analyze
  continue-on-error: true
  run: |
    if python3 tools/analyzer.py --input data.json 2>&1; then
      echo "✅ Analysis completed"
      echo "analyze_success=true" >> $GITHUB_OUTPUT
    else
      echo "⚠️ Analysis failed (OK - continuing)"
      echo "analyze_success=false" >> $GITHUB_OUTPUT
    fi
```

### 5. Dependent Step Execution

**Problem**: Later steps assume earlier steps succeeded, causing cascading failures.

**Solution**: Use conditional execution based on step outputs.

```yaml
# ❌ BAD - Assumes previous step succeeded
- name: Collect data
  id: collect
  run: collect_data.sh

- name: Process data
  run: process_data.sh

# ✅ GOOD - Conditional execution
- name: Collect data
  id: collect
  continue-on-error: true
  run: |
    if collect_data.sh; then
      echo "collect_success=true" >> $GITHUB_OUTPUT
    else
      echo "collect_success=false" >> $GITHUB_OUTPUT
    fi

- name: Process data
  if: steps.collect.outputs.collect_success == 'true'
  run: process_data.sh
```

## 🛠️ Implementation Patterns

### Pattern 1: Defensive File Operations

Always check files exist before reading/processing them:

```yaml
- name: Load configuration
  run: |
    CONFIG_FILE="config.json"
    if [ -f "$CONFIG_FILE" ]; then
      CONFIG=$(cat "$CONFIG_FILE")
      echo "✅ Configuration loaded"
    else
      echo "⚠️ Configuration not found, using defaults"
      CONFIG="{}"
    fi
```

### Pattern 2: Safe Command Chaining

Don't let one command failure stop the entire step:

```yaml
- name: Multiple operations
  continue-on-error: true
  run: |
    success_count=0
    
    if operation1; then
      echo "✅ Operation 1 succeeded"
      ((success_count++))
    else
      echo "⚠️ Operation 1 failed"
    fi
    
    if operation2; then
      echo "✅ Operation 2 succeeded"
      ((success_count++))
    else
      echo "⚠️ Operation 2 failed"
    fi
    
    echo "Completed $success_count operations"
```

### Pattern 3: Graceful Python Error Handling

Wrap Python scripts to capture and handle errors:

```python
# In Python scripts
try:
    # Your main logic
    result = do_work()
    print(f"✅ Success: {result}")
    sys.exit(0)
except FileNotFoundError as e:
    print(f"⚠️ File not found (OK): {e}")
    sys.exit(0)  # Exit successfully
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)  # Only fail for unexpected errors
```

### Pattern 4: Output Validation

Always validate step outputs before using them:

```yaml
- name: Generate data
  id: generate
  run: |
    output=$(generate_data.py)
    if [ -n "$output" ] && [ "$output" != "null" ]; then
      echo "data=$output" >> $GITHUB_OUTPUT
      echo "has_data=true" >> $GITHUB_OUTPUT
    else
      echo "has_data=false" >> $GITHUB_OUTPUT
    fi

- name: Use data
  if: steps.generate.outputs.has_data == 'true'
  run: |
    echo "Using data: ${{ steps.generate.outputs.data }}"
```

## 🎨 Workflow-Specific Patterns

### PR Failure Workflows

Both `pr-failure-learning.yml` and `pr-failure-intelligence.yml` follow this pattern:

1. **Data Collection** - Continue even if collection fails
2. **Analysis** - Only run if data exists
3. **Suggestions** - Only run if analysis succeeded
4. **Commit** - Only commit if there are changes

```yaml
- name: Collect failures
  id: collect
  continue-on-error: true
  # ... collection logic with success flag

- name: Analyze patterns
  if: steps.collect.outputs.collect_success == 'true'
  id: analyze
  continue-on-error: true
  # ... analysis logic with success flag

- name: Generate suggestions
  if: steps.analyze.outputs.analyze_success == 'true'
  # ... suggestion logic

- name: Commit data
  if: success() || steps.analyze.outputs.analyze_success == 'true'
  # ... commit only if there's useful data
```

### Self-Documenting AI Workflows

These workflows handle missing issue data gracefully:

```yaml
- name: Fetch issue data
  id: fetch
  continue-on-error: true
  # ... with has_data output

- name: Analyze discussion
  if: steps.fetch.outputs.has_data == 'true'
  continue-on-error: true
  # ... with analyze_success output

- name: Create PR
  if: steps.analyze.outputs.analyze_success == 'true'
  # ... only if analysis succeeded
```

### World Update Workflows

These allow individual update steps to fail:

```yaml
- name: Sync agents
  continue-on-error: true
  run: |
    if python3 world/sync_agents_to_world.py; then
      echo "✅ Agents synced"
    else
      echo "⚠️ Agent sync failed (continuing)"
    fi

- name: Sync learnings
  continue-on-error: true
  # ... similar pattern

- name: Create PR
  if: success() || steps.check_changes.outputs.has_changes == 'true'
  # ... commit any changes that did succeed
```

## 📊 Error Handling Checklist

When creating or updating a workflow, verify:

- [ ] No `workflow_run` triggers (use schedule/manual instead)
- [ ] Critical steps have `continue-on-error: true`
- [ ] File operations check for existence first
- [ ] `gh` commands have error handling and null checks
- [ ] Python scripts wrapped with error handling
- [ ] Step outputs validated before use
- [ ] Dependent steps use conditional execution
- [ ] PR creation only happens if there are changes
- [ ] Clear error messages for debugging
- [ ] Success/failure flags set in outputs

## 🔍 Testing Workflows

Before merging workflow changes:

```bash
# 1. Test manually
gh workflow run your-workflow.yml

# 2. Check logs
gh run list --workflow=your-workflow.yml --limit 5
gh run view RUN_ID --log

# 3. Test with missing data
# Create conditions where files don't exist
# Verify graceful handling

# 4. Test error paths
# Intentionally cause failures
# Verify continue-on-error works
```

## 📚 References

- [GitHub Actions: Error Handling](https://docs.github.com/en/actions/learn-github-actions/expressions#job-status-check-functions)
- [Workflow Syntax: continue-on-error](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepscontinue-on-error)
- [Branch Protection Rules](.github/instructions/branch-protection.instructions.md)

## 🤝 Contributing

When adding new workflows:

1. Follow the patterns in this guide
2. Test with missing/invalid data
3. Add error handling for all external calls
4. Document any new patterns discovered
5. Update this guide if needed

---

**@support-master** - Systematic approach to workflow reliability through defensive programming and comprehensive error handling.
