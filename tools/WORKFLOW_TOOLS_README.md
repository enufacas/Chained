# Workflow Management Tools

This directory contains scripts for managing GitHub Actions workflows in the Chained repository.

## Overview

These tools allow you to inventory, disable, and re-enable GitHub workflows while preserving their original configurations for future restoration.

## Tools

### 1. inventory_workflows.py
**Purpose**: Create a comprehensive inventory of all workflows in the repository.

**Usage**:
```bash
python3 tools/inventory_workflows.py
```

**Output**:
- `workflow_inventory.json` - Machine-readable inventory
- `workflow_inventory_report.txt` - Human-readable report

**What it does**:
- Scans all `.yml` and `.yaml` files in `.github/workflows/`
- Identifies enabled vs disabled workflows
- Extracts workflow names and trigger types
- Categorizes workflows by status

### 2. disable_workflows.py
**Purpose**: Disable all enabled workflows while preserving their original state.

**Usage**:
```bash
python3 tools/disable_workflows.py
```

**What it does**:
1. Creates timestamped backup of all enabled workflows
2. Adds metadata header to each workflow with:
   - Disable date
   - Original workflow name
   - Original triggers
   - Re-enable instructions
3. Modifies workflows to keep only `workflow_dispatch` trigger
4. Saves metadata for restoration in `workflow_disable_metadata.json`
5. Generates report in `workflow_disable_report.txt`

**Output Files**:
- `workflow_backups/backup_YYYYMMDD_HHMMSS/` - Complete backup
- `workflow_disable_metadata.json` - Restoration metadata
- `workflow_disable_report.txt` - Human-readable report

**Safety**:
- Non-destructive operation
- Complete backup before modifications
- Workflows can still be triggered manually
- Full restoration possible

### 3. enable_workflows.py
**Purpose**: Re-enable previously disabled workflows using saved metadata.

**Usage**:
```bash
# Re-enable all workflows
python3 tools/enable_workflows.py

# Re-enable specific workflow
python3 tools/enable_workflows.py --workflow .github/workflows/agent-spawning.yml

# List all disabled workflows
python3 tools/enable_workflows.py --list
```

**What it does**:
1. Reads restoration metadata from `workflow_disable_metadata.json`
2. Locates original workflows in backup directory
3. Restores complete original workflow files
4. Removes disable metadata headers
5. Restores all original triggers and configurations

**Options**:
- No arguments: Re-enable all workflows
- `--workflow <path>`: Re-enable specific workflow
- `--list`: Show all disabled workflows

## Typical Workflow

### Disabling Workflows

```bash
# 1. Create inventory (optional, for reference)
python3 tools/inventory_workflows.py

# 2. Disable all workflows
python3 tools/disable_workflows.py
```

Result: All enabled workflows now only respond to manual `workflow_dispatch` trigger.

### Re-enabling Workflows

```bash
# Option 1: Re-enable all workflows at once
python3 tools/enable_workflows.py

# Option 2: Re-enable selectively
python3 tools/enable_workflows.py --list  # See what's disabled
python3 tools/enable_workflows.py --workflow .github/workflows/specific-workflow.yml
```

## Files Created

| File | Purpose |
|------|---------|
| `workflow_inventory.json` | Complete workflow inventory (machine-readable) |
| `workflow_inventory_report.txt` | Complete workflow inventory (human-readable) |
| `workflow_disable_metadata.json` | Metadata for restoring disabled workflows |
| `workflow_disable_report.txt` | Report of disable operation |
| `workflow_backups/backup_YYYYMMDD_HHMMSS/` | Complete backup of original workflows |

## Metadata Format

### workflow_disable_metadata.json

```json
{
  "disable_date": "2025-12-29T02:43:14.994388",
  "backup_location": "workflow_backups/backup_20251229_024314",
  "total_enabled": 85,
  "workflows": [
    {
      "file": ".github/workflows/agent-spawning.yml",
      "name": "Agent System: Spawning",
      "original_triggers": ["schedule", "workflow_dispatch"],
      "disabled_date": "2025-12-29T02:43:14.994388"
    }
  ]
}
```

## Workflow Metadata Header

Each disabled workflow gets a metadata header:

```yaml
# ============================================================================
# WORKFLOW DISABLED
# Disabled on: 2025-12-29T02:43:14.994388
# Original workflow name: Agent System: Spawning
# Original triggers: schedule, workflow_dispatch
# 
# To re-enable: Use the tools/enable_workflows.py script with the
# workflow_disable_metadata.json file to restore original triggers.
# ============================================================================
```

## Use Cases

### 1. Maintenance Period
Disable all workflows during system maintenance:
```bash
python3 tools/disable_workflows.py
# Perform maintenance
python3 tools/enable_workflows.py  # When done
```

### 2. Reduce Workflow Costs
Temporarily stop automated workflows to reduce GitHub Actions usage:
```bash
python3 tools/disable_workflows.py
```

### 3. Testing Changes
Disable workflows before making repository-wide changes:
```bash
python3 tools/disable_workflows.py
# Make and test changes
python3 tools/enable_workflows.py
```

### 4. Selective Restoration
Re-enable workflows gradually:
```bash
# Re-enable critical workflows first
python3 tools/enable_workflows.py --workflow .github/workflows/deploy-gcp-infrastructure.yml

# Then less critical ones
python3 tools/enable_workflows.py --workflow .github/workflows/agent-spawning.yml
```

## Safety Features

1. **Complete Backup**: All workflows backed up before modification
2. **Metadata Preservation**: Complete restoration information saved
3. **Non-Destructive**: Original files preserved in backup
4. **Manual Trigger**: Disabled workflows can still be triggered manually
5. **Tested Restore**: Restoration process validated and working

## Troubleshooting

### Issue: "Backup not found"
**Solution**: Verify `workflow_disable_metadata.json` has correct backup location.

### Issue: "Workflow file not found"
**Solution**: Ensure you're running from repository root directory.

### Issue: "Permission denied"
**Solution**: Make scripts executable: `chmod +x tools/*.py`

## Current Status (as of 2025-12-29)

- ✅ **85 workflows disabled**
- ✅ **Disable date captured**: 2025-12-29T02:43:14
- ✅ **Backup location**: `workflow_backups/backup_20251229_024314/`
- ✅ **Metadata saved**: `workflow_disable_metadata.json`
- ✅ **Restore tested**: ✅ Working correctly

## Dependencies

- Python 3.x
- PyYAML (`pip install pyyaml`)

## Author & Maintenance

These tools were created to manage the large number of automated workflows in the Chained repository while preserving the ability to restore them at any time.

For issues or questions, see:
- `WORKFLOW_DISABLE_PLAN.md` - Planning document
- `WORKFLOW_DISABLE_COMPLETE_SUMMARY.md` - Comprehensive summary
- `workflow_disable_report.txt` - Disable operation report
