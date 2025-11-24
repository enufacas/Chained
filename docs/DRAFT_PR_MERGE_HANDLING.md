# Draft PR Merge Handling - Implementation Guide

## Overview

This document describes how the meta-coordinator handles draft PRs for review and merge eligibility, based on WIP markers in the title rather than draft status alone.

## Problem Statement

Previously, the meta-coordinator would skip ALL draft PRs from review and merge consideration, even when:
1. The PR author removed WIP markers from the title
2. The work was complete and ready for review
3. The draft status was used for organizational purposes only

This created friction in the workflow where authors had to convert PRs from draft to ready-for-review status manually, even when they had already signaled readiness by removing WIP markers.

## Solution

The meta-coordinator now uses **WIP markers in the PR title** as the authoritative signal of readiness, not the GitHub draft status.

### Decision Matrix

| Draft Status | WIP in Title | Action |
|--------------|--------------|--------|
| Draft | Yes (e.g., "[WIP]") | ❌ Skip processing |
| Draft | No | ✅ Process for review/merge |
| Non-draft | Yes (e.g., "[WIP]") | ❌ Skip processing |
| Non-draft | No | ✅ Process for review/merge |

### WIP Markers Detected

The following patterns in PR titles are considered WIP markers (case-insensitive):
- `[WIP]`
- `WIP:` (at start of title)
- `WIP ` (followed by space)
- `work.in.progress` or `work in progress`
- `[do not merge]` or `[do.not.merge]`
- `[DNM]`

### Code Examples

**Bash Implementation (from meta-coordinator-system.md):**

```bash
# Check for WIP markers in title
has_wip=false
if echo "$pr_title" | grep -qiE '\[WIP\]|^WIP:|WIP\s|work[\.\s]in[\.\s]progress|\[do[\.\s]not[\.\s]merge\]|\[dnm\]'; then
  has_wip=true
fi

# Skip if has WIP marker (even if not draft)
if [ "$has_wip" = "true" ]; then
  echo "Not ready (WIP marker in title)"
  exit 0
fi

# Note: Draft PRs WITHOUT WIP markers are considered ready for processing
```

**Python Implementation (from test_draft_pr_wip_handling.py):**

```python
import re

def has_wip_marker(title: str) -> bool:
    """Check if a PR title has WIP markers."""
    # Use [\.\s] to match literal dot or space
    wip_pattern = r'\[WIP\]|^WIP:|WIP\s|work[\.\s]in[\.\s]progress|\[do[\.\s]not[\.\s]merge\]|\[dnm\]'
    return bool(re.search(wip_pattern, title, re.IGNORECASE))

def should_process_pr(is_draft: bool, title: str) -> tuple[bool, str]:
    """Determine if a PR should be processed."""
    if has_wip_marker(title):
        return False, "WIP marker in title"
    return True, "No WIP markers, ready for processing"
```

## Files Changed

### 1. `.github/agents/meta-coordinator-system.md`

**Section: PR Review Orchestration**
- Updated filtering to process all open PRs (including drafts)
- WIP detection now determines skip/process decision
- Draft status alone doesn't block processing

**Section: Auto-Merge Execution**
- Changed eligibility check from `is_draft == true` to WIP marker detection
- Updated complete eligibility check example code
- Added note about draft PRs without WIP being eligible

**Section: Overview**
- Updated bullet point about auto-merge criteria
- Clarified that WIP markers, not draft status, determine readiness

### 2. `.github/workflows/meta-coordinator.yml`

**Monitoring Section (Phase 5)**
- Added separate count for mergeable draft PRs
- Updated reporting to show both draft and non-draft mergeable counts
- Added note explaining that draft PRs without WIP are eligible

**Comment Header**
- Updated to reflect new behavior: "no WIP in title; draft status doesn't block"

### 3. `tests/test_draft_pr_wip_handling.py` (New)

Comprehensive test coverage for all scenarios:
- Draft PRs with WIP markers → Skip ✓
- Draft PRs without WIP markers → Process ✓
- Non-draft PRs with WIP markers → Skip ✓
- Non-draft PRs without WIP markers → Process ✓
- Edge cases (wipe, WIPR, etc.) ✓

## Benefits

### 1. Better User Experience
- Authors can signal readiness by removing WIP from title
- No need to toggle draft status manually
- More intuitive workflow

### 2. Organizational Flexibility
- Draft status can be used for organization without blocking merge
- Teams can use draft status for tracking purposes
- Reduces workflow friction

### 3. Reduced Cycle Time
- PRs ready for merge can proceed immediately
- No extra step to convert from draft to ready
- Aligns with success metrics (cycle time reduction)

### 4. Consistency
- WIP markers are the single source of truth for readiness
- Behavior is consistent across draft and non-draft PRs
- Clear signal for both humans and automation

## Testing

Run the test suite:

```bash
python3 tests/test_draft_pr_wip_handling.py
```

Expected output:
```
============================================================
Running Draft PR WIP Handling Tests
============================================================

✅ test_has_wip_marker_function passed
✅ test_draft_with_wip_markers passed
✅ test_draft_without_wip_markers passed
✅ test_non_draft_with_wip_markers passed
✅ test_non_draft_without_wip_markers passed
✅ test_edge_case_titles passed

============================================================
✅ All tests passed!
============================================================
```

## Migration Guide

For existing workflows and scripts that check draft status:

### Before

```bash
# Old logic - skips all drafts
if [ "${is_draft}" = "true" ]; then
  echo "Skipping draft PR"
  exit 0
fi
```

### After

```bash
# New logic - check WIP markers instead
pr_title=$(gh pr view $PR_NUM --json title --jq '.title')

if echo "$pr_title" | grep -qiE '\[WIP\]|^WIP:|WIP\s|work[\.\s]in[\.\s]progress|\[do[\.\s]not[\.\s]merge\]|\[dnm\]'; then
  echo "Skipping WIP PR"
  exit 0
fi

# Draft status alone doesn't block - continue processing
```

## Edge Cases

### Valid Titles That Are NOT WIP

These titles should NOT trigger WIP detection:
- "Wipe old cache files" (wipe ≠ wip)
- "Update WIPR protocol" (WIPR is different)
- "Work in the new feature" (not "work.in.progress")
- "Add working implementation" (working ≠ wip)

### Valid WIP Markers

These titles SHOULD trigger WIP detection:
- "[WIP] Update feature"
- "WIP: Add tests"
- "WIP Update docs"
- "work.in.progress: experimental"
- "[do.not.merge] testing"
- "[DNM] Draft changes"

## Performance Impact

- **Minimal**: Only adds one regex check per PR
- **No API calls**: Title is already fetched with PR data
- **No database**: Stateless logic, no persistence needed

## Monitoring

The meta-coordinator workflow now reports:
- Mergeable (non-draft): Count of ready non-draft PRs
- Mergeable (draft, may be ready if no WIP): Count of draft PRs that might be eligible
- Draft (total): Total count of draft PRs
- Note explaining that draft PRs without WIP markers are eligible

## Future Enhancements

Potential improvements for the future:
1. Add GitHub label `ready-despite-draft` for explicit signaling
2. Integrate with GitHub's "Ready for review" button automation
3. Add metrics tracking for draft PR merge rates
4. Consider additional readiness signals beyond WIP markers

## References

- **Agent Definition**: `.github/agents/meta-coordinator-system.md`
- **Workflow**: `.github/workflows/meta-coordinator.yml`
- **Test Suite**: `tests/test_draft_pr_wip_handling.py`
- **Issue**: "The meta-coordinator needs to handle merging draft PRs that no longer have WIP in the title"

## Questions?

For questions or issues with this implementation:
1. Check the test suite for expected behavior
2. Review the agent definition for complete logic
3. Open an issue with specific use case details
