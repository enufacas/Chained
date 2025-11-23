---
applyTo:
  - ".github/workflows/meta-coordinator.yml"
  - ".github/agents/meta-coordinator-system.md"
  - "tools/meta-coordinator-memory.py"
  - ".github/agent-system/meta-coordinator-memory.json"
---

# Meta-Coordinator System Instructions

## Overview

**@meta-coordinator-system** is the autonomous orchestrator for the entire tech lead review, agent assignment, and PR lifecycle system. It runs every 5 minutes and replaces 3 previous workflows.

## When Working with Meta-Coordinator

**DO NOT** modify these files unless:
- Fixing bugs in orchestration logic
- Improving performance or reliability
- Adding new capabilities to the system
- Updating to align with system changes

**ALWAYS:**
- Test changes carefully (5-min frequency = high impact)
- Consider concurrent session safety
- Update memory system if data structures change
- Document changes in META_COORDINATOR_*.md files
- Use workflow_dispatch with dry_run: true for testing

## Protected Status

**@meta-coordinator-system** is a protected agent. Changes require review by:
- @workflows-tech-lead (workflow changes)
- @agents-tech-lead (agent definition changes)

## Key Principles

1. **Autonomy**: System operates without manual intervention
2. **Concurrency**: Multiple sessions can run safely (5-min frequency)
3. **Learning**: Memory persists across sessions for pattern recognition
4. **Completeness**: Handles all 7 core responsibilities end-to-end
5. **Safety**: Extensive checks before destructive operations (merge, close)

## Memory System

**Location:** `.github/agent-system/meta-coordinator-memory.json`
**Tool:** `tools/meta-coordinator-memory.py`

**Critical:**
- File-based locking prevents concurrent write conflicts
- Optimistic merge preserves all sessions' changes
- Atomic writes prevent corruption
- DO NOT modify JSON directly (use Python API)
- DO NOT delete lock files manually (stale locks auto-remove after 5 min)

## Seven Core Responsibilities

1. **PR Review Orchestration** - Assign tech leads based on file changes
2. **Feedback Issue Creation** - Create issues when tech leads request changes
3. **Agent Assignment** - Match issues to appropriate agents
4. **Review Cycle Management** - Handle re-reviews and approvals
5. **Auto-Merge Execution** - Merge approved PRs from trusted sources
6. **Memory and Learning** - Track patterns and inform decisions
7. **Exception Handling** - Fix inconsistencies, close orphans, escalate

## Testing Checklist

Before merging changes:
- [ ] Test with `workflow_dispatch` and dry_run: true
- [ ] Verify memory system handles concurrent sessions
- [ ] Check that no PRs or issues incorrectly processed
- [ ] Validate 5-min frequency doesn't cause issues
- [ ] Review coordination issue summaries
- [ ] Confirm no duplicate assignments or actions

## Documentation

When updating meta-coordinator:
- Update `META_COORDINATOR_IMPLEMENTATION.md` (deployment guide)
- Update `META_COORDINATOR_COMPLETE_SUMMARY.md` (overview)
- Update `.github/copilot-instructions.md` if behavior changes
- Update `docs/WORKFLOWS.md` with workflow details
- Update `docs/AUTONOMOUS_SYSTEM_ARCHITECTURE.md` if architecture changes

## Common Issues

**Lock contention:**
- Check for `.json.lock` file age
- Stale locks (>5 min) auto-remove
- If persistent, investigate why sessions are slow

**Memory file growth:**
- Should stay <100KB
- Self-prunes old entries
- If exceeds 100KB, check pruning logic

**Duplicate actions:**
- Check concurrency settings
- Verify session isolation working
- Review optimistic merge logic

## Related Files

**Documentation:**
- `META_COORDINATOR_IMPLEMENTATION.md` - Deployment
- `META_COORDINATOR_MEMORY_SYSTEM.md` - Memory docs
- `META_COORDINATOR_MEMORY_CONCURRENCY.md` - Concurrency
- `META_COORDINATOR_COMPLETE_SUMMARY.md` - Overview
- `META_COORDINATOR_COPILOT_INSTRUCTIONS_UPDATE.md` - Analysis

**Code:**
- `.github/workflows/meta-coordinator.yml` - Workflow
- `.github/agents/meta-coordinator-system.md` - Agent definition
- `tools/meta-coordinator-memory.py` - Memory system
- `tools/match-issue-to-agent.py` - Agent matching
- `tools/match-pr-to-tech-lead.py` - Tech lead matching

## Troubleshooting

**Agent not taking action:**
- Check coordination issue for error messages
- Verify GitHub token permissions
- Review dry_run setting (should be false)
- Check focus_area (should be 'all' usually)

**PRs not auto-merging:**
- Verify PR has `copilot` label OR is from owner/maintainer
- Check PR has `tech-lead-approved` label
- Confirm no merge conflicts
- Verify all CI checks passed
- Review eligibility logic in agent definition

**Issues not getting assigned:**
- Verify issue is open
- Check if issue already has agent assignment
- Review agent matching score (needs ≥5 typically)
- Check assign-copilot-to-issue.sh execution

**Memory corruption:**
- Should never happen with atomic writes
- If occurs, check for direct JSON edits
- Verify locking mechanism working
- Review concurrent session logs
