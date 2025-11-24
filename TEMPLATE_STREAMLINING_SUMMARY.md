# Meta-Coordinator Issue Template Streamlining

## Problem
The meta-coordinator issue template was excessively verbose (771 lines), repeating detailed instructions that were already in the agent definition file. This made coordination issues long and hard to navigate.

Reference: Issue #2864

## Solution
Streamlined the issue body template from **771 lines to 106 lines (86% reduction)** by:

1. **Removing duplicate instructions** - The detailed agent definition in `.github/agents/meta-coordinator-system.md` (1994 lines) remains unchanged and verbose as requested
2. **Adding clear references** - The issue now references the agent definition instead of repeating it
3. **Keeping essential context** - Retained all workflow-provided metrics and system state data
4. **Maintaining functionality** - All critical information for the agent is still present

## Files Changed

### Modified
- `.github/workflows/templates/meta-coordinator-issue-body.md` - Streamlined from 771 to 106 lines

### Added (for reference)
- `.github/workflows/templates/meta-coordinator-issue-body-BACKUP-verbose.md` - Backup of original verbose version
- `.github/workflows/templates/meta-coordinator-issue-body-streamlined.md` - New streamlined version (source)

### Unchanged
- `.github/agents/meta-coordinator-system.md` - Kept at 1994 lines as requested
- `.github/workflows/meta-coordinator.yml` - No changes needed (uses the same template file)

## What Was Kept

The streamlined template retains:
- ✅ Agent assignment directive (@meta-coordinator-system)
- ✅ Reference to full agent definition
- ✅ Workflow trigger and configuration
- ✅ System state metrics (PRs, issues, cleanup stats)
- ✅ Core responsibilities summary (with reference to details)
- ✅ Focus area and dry run configuration
- ✅ Tools and quick reference
- ✅ Critical execution order
- ✅ Expected output format

## What Was Removed

Removed from the issue template (still in agent definition):
- ❌ Detailed phase-by-phase instructions
- ❌ Code examples and patterns
- ❌ Extensive reasoning frameworks
- ❌ Detailed eligibility criteria
- ❌ Memory system implementation details
- ❌ Extensive proactive problem-solving examples
- ❌ Complete PR lifecycle management documentation

## Benefits

1. **Readability** - Issues are now much easier to scan and understand
2. **Maintainability** - Changes to instructions only need to be made in one place (agent definition)
3. **Consistency** - Agent definition is the single source of truth
4. **Functionality** - Agent still has access to all instructions via the agent definition file
5. **Performance** - Smaller issue bodies may load/process faster

## Testing

Created comprehensive test script (`/tmp/test_template.sh`) that verifies:
- ✅ All template variables are properly substituted
- ✅ No unintended variable substitution in code blocks
- ✅ Agent mention is present
- ✅ Agent definition reference is present
- ✅ Core sections are included

Test results: **All tests passed** ✅

## Implementation Details

The streamlined template follows this structure:

```markdown
1. Agent Assignment (reference to definition)
2. System State (from workflow)
3. Your Mission (summary with reference)
4. Quick Reference (tools and critical order)
5. Expected Output (format guide)
```

Key principle: **Reference, don't repeat**

The issue body now says "see agent definition for details" instead of duplicating the full instructions.

## Migration Notes

- No changes needed to the workflow file
- The agent will read `.github/agents/meta-coordinator-system.md` for detailed instructions
- Future coordination issues will automatically use the streamlined template
- Previous issues with verbose bodies are unchanged (historical record)

## Related Files

- Agent definition: `.github/agents/meta-coordinator-system.md`
- Workflow: `.github/workflows/meta-coordinator.yml`
- Template: `.github/workflows/templates/meta-coordinator-issue-body.md`

---

**Date:** 2025-11-24  
**Author:** GitHub Copilot  
**Issue Reference:** #2864
