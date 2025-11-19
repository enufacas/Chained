# Agent Spawning Workflow

This document describes the `agent-spawning.yml` workflow and its usage.

## Overview

The Agent Spawning System consolidates multiple agent spawning workflows into a single, unified workflow with different stages:

1. **standard-spawner** - Standard agent spawning with various options
2. **learning-based-spawner** - Spawn agents inspired by recent learnings
3. **multi-spawner** - Batch spawning of multiple agents
4. **workload-spawner** - Spawn agents based on current workload analysis

## Workflow Inputs

The workflow supports 10 inputs (GitHub Actions maximum for `workflow_dispatch`):

### Core Input
- **stage** (required): Which spawning stage to run
  - Options: `standard-spawner`, `learning-based-spawner`, `multi-spawner`, `workload-spawner`

### Standard Spawner Inputs
- **mode**: Spawning mode (mixed/existing/new)
- **specialization**: Force specific specialization
- **delete_mode**: Delete agents before spawning (none/all/specific)
- **delete_agent_ids**: Agent IDs to delete (comma-separated)
- **respawn_count**: Number of agents to spawn after deletion

### Learning-Based Spawner Inputs
- **force_spawn**: Force spawn even if recent spawns exist

### Multi-Spawner Inputs
- **spawn_count**: Number of agents to spawn
- **batch_mode**: Batch spawning strategy (balanced/existing/new/diverse)

### Workload Spawner Inputs
- **workload_options**: Combined options as string (format: `"max_spawns:5,dry_run:false"`)
  - **max_spawns**: Maximum agents to spawn (default: 5)
  - **dry_run**: Dry run mode without actual spawning (default: false)

## Using Workload Options

The `workload_options` input combines multiple parameters into a single string to stay within GitHub's 10-input limit.

### Format
```
max_spawns:N,dry_run:BOOLEAN
```

### Examples

**Default usage:**
```
max_spawns:5,dry_run:false
```

**Custom max spawns:**
```
max_spawns:10,dry_run:false
```

**Dry run mode:**
```
max_spawns:3,dry_run:true
```

**Only specify max_spawns (dry_run defaults to false):**
```
max_spawns:7
```

**Reversed order (order doesn't matter):**
```
dry_run:true,max_spawns:3
```

## Technical Notes

### Input Limit Resolution

GitHub Actions allows a maximum of 10 `workflow_dispatch` inputs. The original workflow had 11 inputs, which caused a validation error. This was resolved by consolidating the workload spawner's `max_spawns` and `dry_run` inputs into a single `workload_options` string input.

### Parsing Implementation

The `workload-spawner` job includes a "Parse workload options" step that:
1. Takes the `workload_options` input string
2. Extracts individual values using regex pattern matching
3. Provides fallback defaults if values are missing
4. Sets outputs that can be used in subsequent steps

## Troubleshooting

### Issue: Workflow validation fails
**Solution**: Ensure you have no more than 10 inputs defined in the `workflow_dispatch` section.

### Issue: Workload options not parsing correctly
**Solution**: Verify the format is `key:value,key:value` with no spaces and correct key names (`max_spawns` and `dry_run`).

### Issue: Default values not working
**Solution**: The parsing logic includes fallback defaults. If empty string is provided, it defaults to `max_spawns:5,dry_run:false`.

---

*Maintained by **@workflows-tech-lead***
