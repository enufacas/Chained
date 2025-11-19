# Workflow Script Dependencies Guide

## Overview

This guide explains how to properly configure GitHub Actions workflows that depend on scripts from the `tools/` or `scripts/` directories.

**@investigate-champion** has implemented enhanced validation to ensure workflows properly track their script dependencies, preventing broken workflows when scripts are updated.

## The Problem

When a workflow uses a script (e.g., `tools/my-script.py`), changes to that script can break the workflow. However, if the workflow doesn't include the script in its path triggers, the CI won't test the workflow when the script changes, leading to broken workflows merged to main.

## The Solution

**Always include your script dependencies in your workflow's path triggers.**

## Required Configuration

### For Workflows with Pull Request Triggers

If your workflow has a `pull_request` trigger and uses scripts, you **must** include those scripts in the path filter.

#### ❌ Bad Example (Missing Script in Paths)

```yaml
name: My Workflow

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run script
        run: python3 tools/my-script.py  # Script not in paths!
```

**Problem:** When `tools/my-script.py` is updated, this workflow won't be tested in CI.

#### ✅ Good Example (Script in Paths)

```yaml
name: My Workflow

on:
  pull_request:
    paths:
      - '.github/workflows/my-workflow.yml'  # The workflow itself
      - 'tools/my-script.py'                 # Script dependency
    types: [opened, synchronize]

jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run script
        run: python3 tools/my-script.py
```

**Benefit:** When either the workflow or the script is updated, CI will test the workflow.

### Multiple Script Dependencies

If your workflow uses multiple scripts, include all of them:

```yaml
on:
  pull_request:
    paths:
      - '.github/workflows/my-workflow.yml'
      - 'tools/script1.py'
      - 'tools/script2.py'
      - 'tools/helper.py'
      - 'scripts/utility.sh'
```

### Using Wildcards

For workflows that use many scripts from a directory, you can use wildcards:

```yaml
on:
  pull_request:
    paths:
      - '.github/workflows/my-workflow.yml'
      - 'tools/**/*.py'    # All Python files in tools/
      - 'scripts/**/*.sh'  # All shell scripts in scripts/
```

**Note:** Wildcards are convenient but less specific. Use them judiciously.

## Validation

The CI system will automatically validate your workflow configuration:

### What Gets Checked

1. **Script Detection**: The validator scans your workflow for script references
2. **Path Trigger Check**: Verifies those scripts are in your path triggers
3. **Clear Error Messages**: Provides examples of how to fix issues

### Example Validation Error

```
❌ my-workflow.yml: Workflow uses scripts ['tools/script.py'] but these are not 
covered by path triggers. Add these to the 'on.pull_request.paths' section:
  Example:
    on:
      pull_request:
        paths:
          - 'tools/script.py'
```

### Example Validation Warning

```
⚠️  my-workflow.yml: Workflow uses scripts ['tools/script.py'] and has pull_request 
trigger but no path filters. Consider adding path triggers to run only when scripts change
```

## Exemptions

Workflows **without** pull_request triggers don't require path configuration:

- Scheduled workflows (`schedule`)
- Manual workflows (`workflow_dispatch`)
- Push-only workflows

These workflows won't be automatically tested in PRs anyway, so path triggers don't apply.

## Common Patterns

### Pattern 1: Simple Script Workflow

```yaml
name: Code Analyzer

on:
  schedule:
    - cron: '0 8 * * *'
  pull_request:  # Also want to test in PRs
    paths:
      - '.github/workflows/code-analyzer.yml'
      - 'tools/code-analyzer.py'

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run analyzer
        run: python3 tools/code-analyzer.py
```

### Pattern 2: Multiple Script Dependencies

```yaml
name: Agent Spawner

on:
  workflow_dispatch:
  pull_request:
    paths:
      - '.github/workflows/agent-spawner.yml'
      - 'tools/generate-new-agent.py'
      - 'tools/add_agent_to_registry.py'
      - 'tools/get-agent-info.py'

jobs:
  spawn:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate agent
        run: python3 tools/generate-new-agent.py
      - name: Register agent
        run: python3 tools/add_agent_to_registry.py
```

### Pattern 3: Embedded Scripts

If your workflow has embedded Python/shell scripts (heredocs), you don't need path triggers for them since they're part of the workflow file itself:

```yaml
name: Learning Workflow

on:
  schedule:
    - cron: '0 8 * * *'

jobs:
  learn:
    runs-on: ubuntu-latest
    steps:
      - name: Fetch and analyze
        run: |
          python3 << 'EOF'
          import json
          # Embedded script - no separate file
          print("Learning...")
          EOF
```

## Troubleshooting

### My workflow failed validation

1. Check the error message for the list of uncovered scripts
2. Add those scripts to your `paths:` section
3. Push the changes - validation will run again

### I use a script but don't want to trigger on changes

If you truly don't want to test your workflow when the script changes:
- Remove the `pull_request` trigger, or
- Accept the validation warning (it's just a warning)

However, this is **not recommended** as it increases the risk of broken workflows.

### My script path is complex

For complex scenarios:
- Use wildcards: `tools/**/*.py`
- Be specific when possible to avoid unnecessary CI runs
- Document why you're using broad wildcards

## Best Practices

1. ✅ **Always include the workflow file itself** in paths
2. ✅ **Include all direct script dependencies**
3. ✅ **Use specific paths** when possible (avoid over-broad wildcards)
4. ✅ **Test locally** before pushing
5. ✅ **Keep scripts stable** - breaking changes should be gradual

## Implementation Details

### How Detection Works

The validator uses regex patterns to find script references:
- `python3 tools/script.py`
- `bash scripts/script.sh`
- `./tools/script.py`
- Direct references in run commands

### How Validation Works

1. Extracts all script references from workflow
2. Checks if workflow has `pull_request` trigger
3. If yes, checks if scripts are in path triggers
4. Reports errors for uncovered scripts
5. Provides example configuration

## Examples from Real Workflows

### workflow-validation.yml

```yaml
on:
  pull_request:
    paths:
      - '.github/workflows/**/*.yml'
      - '.github/workflows/**/*.yaml'
      - 'tools/**/*.py'      # All tools scripts
      - 'tools/**/*.sh'
      - 'scripts/**/*.py'    # All scripts
      - 'scripts/**/*.sh'
```

This workflow validates other workflows and needs to track all scripts since any script change could affect workflow behavior.

## Questions?

If you have questions about workflow script dependencies:
- Review this guide
- Check validation error messages (they include examples)
- Look at `workflow-validation.yml` as a reference
- Open an issue with the `workflow` label

---

*Documentation by **@investigate-champion** - Ensuring workflow reliability through dependency tracking*
