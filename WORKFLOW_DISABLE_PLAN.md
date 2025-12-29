# Workflow Disable Operation Plan

## Overview
This document describes the plan to disable all enabled GitHub workflows in the Chained repository.

## Current State (as of 2025-12-29)
- **Total workflows**: 118
- **Enabled workflows**: 85
- **Disabled workflows**: 33 (21 archived, 12 with no active triggers)

## Purpose
Temporarily disable all active workflows to:
1. Reduce workflow execution during maintenance or testing
2. Preserve system resources
3. Allow for systematic re-enablement at a later date

## Methodology

### Backup Strategy
- Create timestamped backup directory: `workflow_backups/backup_YYYYMMDD_HHMMSS/`
- Copy all 85 enabled workflows to backup with full directory structure preserved
- Keep original files in `.github/workflows/` for modification

### Disable Strategy
For each enabled workflow:
1. Add metadata header with:
   - Disable date (ISO 8601 format)
   - Original workflow name
   - Original trigger configuration
   - Re-enable instructions
2. Modify triggers section to keep only `workflow_dispatch`
   - This allows manual execution if needed
   - Removes all automatic triggers (schedule, push, pull_request, etc.)
3. Save modified workflow back to original location

### Metadata Preservation
Create `workflow_disable_metadata.json` containing:
- Disable date and timestamp
- Backup location
- Complete list of disabled workflows with:
  - File path
  - Workflow name
  - Original triggers
  - Disable date

## Re-enabling Process
A companion script `tools/enable_workflows.py` will:
1. Read `workflow_disable_metadata.json`
2. Restore original trigger configurations from backup
3. Remove disable metadata headers
4. Support re-enabling all workflows or specific ones

### Re-enable Commands
```bash
# Re-enable all workflows
python3 tools/enable_workflows.py

# Re-enable specific workflow
python3 tools/enable_workflows.py --workflow .github/workflows/agent-spawning.yml

# List all disabled workflows
python3 tools/enable_workflows.py --list
```

## Safety Measures
1. ✅ Full backup of all workflows before modification
2. ✅ Metadata tracking for reliable restoration
3. ✅ Preserves workflow_dispatch for manual testing
4. ✅ Non-destructive operation (can be reversed)
5. ✅ Validation and error handling in scripts

## Impact Assessment

### Workflows That Will Be Disabled
All 85 enabled workflows, including:
- **Learning & Evolution**: daily-learning-reflection, learn-from-copilot, agent-evolution
- **Agent System**: agent-spawning, agent-missions, agent-evaluator
- **Deployment**: deploy-adk-agents, deploy-gcp-infrastructure
- **Data Collection**: agentops-data-sync, workflow-data-collection
- **Automation**: meta-coordinator, auto-review-merge, pr-auto-labeler
- **Testing**: All a2a-test-* workflows
- **Monitoring**: system-monitor, performance-metrics-collection

### Workflows Already Disabled (Will Not Be Modified)
33 workflows already disabled:
- 21 in `archive/` directory
- 12 with no active triggers

## Execution Steps
1. ✅ Run `tools/inventory_workflows.py` - Complete
2. ⏳ Run `tools/disable_workflows.py` - Pending
3. ⏳ Verify backup created successfully - Pending
4. ⏳ Verify metadata saved correctly - Pending
5. ⏳ Commit changes to repository - Pending

## Post-Disable State
After execution:
- All 85 workflows will retain only `workflow_dispatch` trigger
- No workflows will run automatically on schedule, push, or pull_request
- Manual execution via GitHub UI will still be possible
- Complete restoration possible using `tools/enable_workflows.py`

## Timeline
- **Disable Date**: 2025-12-29 (to be captured at execution time)
- **Re-enable Date**: To be determined (user decision)

## Files Created
1. `workflow_backups/backup_YYYYMMDD_HHMMSS/` - Full backup
2. `workflow_disable_metadata.json` - Restoration metadata
3. `workflow_disable_report.txt` - Human-readable report
4. `tools/disable_workflows.py` - Disable script
5. `tools/enable_workflows.py` - Re-enable script
6. `tools/inventory_workflows.py` - Inventory script

## Validation
After disable operation:
- ✅ Verify backup directory contains all 85 workflows
- ✅ Verify metadata file is complete and valid JSON
- ✅ Verify all workflow files have disable headers
- ✅ Verify all workflows only have workflow_dispatch trigger
- ✅ Test re-enable script on one workflow before committing
