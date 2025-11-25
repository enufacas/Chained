# Meta-Coordinator Phase 2: Stale PR Cleanup Implementation

**Status:** Ready for Implementation  
**Prerequisites:** Phase 1 (Memory Tracking) must be merged first  
**Estimated Time:** 1-2 days  
**Risk Level:** Low (only closes stale/problematic PRs)

---

## Overview

Phase 2 adds aggressive stale PR cleanup to the meta-coordinator system. This implements:
- 3-hour conflict abandonment policy
- 7-day no-activity closure policy  
- Orphaned PR detection (closed issue)
- Draft PR cleanup (>7 days old)

**Goal:** Reduce open PR count by 20-50 PRs in first run, then maintain low noise.

---

## Implementation

### 1. Cleanup Script (✅ Created)

**File:** `tools/cleanup-stale-prs.sh`

**Features:**
- Checks all open PRs (up to 200)
- Applies 4 cleanup policies:
  1. Merge conflicts >3 hours → Close
  2. No activity >7 days → Close
  3. Orphaned (closed issue) → Close
  4. Draft >7 days old → Close
- Safe closure with explanation comments
- Automatic branch deletion (copilot/agent branches)
- Dry-run mode for testing
- Detailed summary output

**Usage:**
```bash
# Dry run (test without closing)
./tools/cleanup-stale-prs.sh --dry-run

# Real run
export GH_TOKEN=$COPILOT_PAT
./tools/cleanup-stale-prs.sh
```

### 2. Workflow Integration (TODO)

Add cleanup step to `meta-coordinator.yml` BEFORE creating coordination issue:

```yaml
- name: Phase 0 - Stale PR Cleanup
  if: steps.assess.outputs.skip != 'true'
  env:
    GH_TOKEN: ${{ secrets.COPILOT_PAT || secrets.GITHUB_TOKEN }}
  run: |
    echo "🧹 Running stale PR cleanup..."
    
    # Run cleanup script
    ./tools/cleanup-stale-prs.sh > /tmp/cleanup_summary.txt 2>&1
    
    # Extract counts from summary
    conflicts_closed=$(grep "Merge conflicts" /tmp/cleanup_summary.txt | grep -oP '\d+' | tail -1)
    no_activity_closed=$(grep "No activity" /tmp/cleanup_summary.txt | grep -oP '\d+' | tail -1)
    orphaned_closed=$(grep "Orphaned" /tmp/cleanup_summary.txt | grep -oP '\d+' | tail -1)
    draft_closed=$(grep "Abandoned draft" /tmp/cleanup_summary.txt | grep -oP '\d+' | tail -1)
    total_closed=$((conflicts_closed + no_activity_closed + orphaned_closed + draft_closed))
    
    # Save to environment for coordination issue
    echo "CLEANUP_CONFLICTS=${conflicts_closed}" >> $GITHUB_ENV
    echo "CLEANUP_NO_ACTIVITY=${no_activity_closed}" >> $GITHUB_ENV
    echo "CLEANUP_ORPHANED=${orphaned_closed}" >> $GITHUB_ENV
    echo "CLEANUP_DRAFT=${draft_closed}" >> $GITHUB_ENV
    echo "CLEANUP_TOTAL=${total_closed}" >> $GITHUB_ENV
    
    echo ""
    echo "✅ Cleanup complete: ${total_closed} PRs closed"
    cat /tmp/cleanup_summary.txt
```

**Placement:** After "Quick assessment" step, before "Create and assign coordination request"

### 3. Issue Template Update (TODO)

Update `.github/workflows/templates/meta-coordinator-issue-body.md` to include cleanup stats:

```markdown
### Phase 0 Cleanup Results (Completed by Workflow)

**Stale PRs Closed:** ${CLEANUP_TOTAL}
- Merge conflicts (>3h): ${CLEANUP_CONFLICTS}
- No activity (>7d): ${CLEANUP_NO_ACTIVITY}
- Orphaned (closed issue): ${CLEANUP_ORPHANED}
- Abandoned draft (>7d): ${CLEANUP_DRAFT}

> These PRs were proactively closed by the workflow before your coordination work.
> You don't need to worry about them - they're already handled.

**Your Focus:** Work on the REMAINING active PRs and issues below.
```

### 4. Memory Integration (TODO)

Add memory recording for stale PR closures in coordination agent work:

```python
# When agent sees Phase 0 cleanup happened
import os

cleanup_total = int(os.environ.get('CLEANUP_TOTAL', 0))
cleanup_conflicts = int(os.environ.get('CLEANUP_CONFLICTS', 0))
cleanup_no_activity = int(os.environ.get('CLEANUP_NO_ACTIVITY', 0))
cleanup_orphaned = int(os.environ.get('CLEANUP_ORPHANED', 0))
cleanup_draft = int(os.environ.get('CLEANUP_DRAFT', 0))

# Record in memory (these were closed as stale)
# Note: We don't have created_at for these PRs, but we can record the cleanup
memory.record_proactive_cleanup(
    total=cleanup_total,
    conflicts=cleanup_conflicts,
    no_activity=cleanup_no_activity,
    orphaned=cleanup_orphaned,
    draft=cleanup_draft
)
```

### 5. Memory System Enhancement (TODO)

Add `record_proactive_cleanup` method to `meta-coordinator-memory.py`:

```python
def record_proactive_cleanup(self, total: int, conflicts: int = 0, 
                            no_activity: int = 0, orphaned: int = 0, 
                            draft: int = 0):
    """
    Record proactive cleanup stats from Phase 0.
    
    These PRs were closed as stale, count toward stale_prs_closed metric.
    """
    # Update stale PRs closed count
    self.memory["open_count_metrics"]["stale_prs_closed"] += total
    
    # Track breakdown by reason
    if "proactive_cleanup_breakdown" not in self.memory:
        self.memory["proactive_cleanup_breakdown"] = {
            "conflicts": 0,
            "no_activity": 0,
            "orphaned": 0,
            "draft": 0
        }
    
    self.memory["proactive_cleanup_breakdown"]["conflicts"] += conflicts
    self.memory["proactive_cleanup_breakdown"]["no_activity"] += no_activity
    self.memory["proactive_cleanup_breakdown"]["orphaned"] += orphaned
    self.memory["proactive_cleanup_breakdown"]["draft"] += draft
    
    # Record as decision
    self._record_decision(
        "proactive_cleanup",
        f"Closed {total} stale PRs in Phase 0 cleanup",
        {
            "total": total,
            "conflicts": conflicts,
            "no_activity": no_activity,
            "orphaned": orphaned,
            "draft": draft
        }
    )
```

---

## Testing Plan

### 1. Test Cleanup Script (Local)

```bash
# Terminal 1: Get current PR count
gh pr list --state open --json number --jq 'length'

# Terminal 2: Test dry run
cd /home/runner/work/Chained/Chained
export GH_TOKEN="your_token"
./tools/cleanup-stale-prs.sh --dry-run

# Review output - check which PRs would be closed
# Verify reasoning is sound

# If dry run looks good:
./tools/cleanup-stale-prs.sh

# Terminal 1: Check new PR count
gh pr list --state open --json number --jq 'length'
```

### 2. Test Workflow Integration

After merging Phase 2 changes:

```bash
# Trigger manual run
gh workflow run meta-coordinator.yml

# Check workflow run logs
gh run list --workflow=meta-coordinator.yml --limit 1

# Check coordination issue for cleanup stats
# Should show "Phase 0 Cleanup Results" section
```

### 3. Verify Memory Tracking

```bash
# Check memory file after run
cat .github/agent-system/meta-coordinator-memory.json | jq '.open_count_metrics.stale_prs_closed'

# Should be > 0 if PRs were closed

# Check proactive cleanup score
python3 tools/meta-coordinator-memory.py success | grep "Cleanup Score"

# Should increase with more stale PRs closed
```

---

## Expected Results

### First Run (Initial Cleanup)
- **PRs closed:** 20-50 (depends on current backlog)
- **Open PR count:** Reduced by 20-40%
- **Cleanup score:** 15-25/100 (depends on ratio)
- **Success score:** 50-55/100 (up from 40/100)

### Subsequent Runs (Maintenance)
- **PRs closed:** 2-10 per run
- **Open PR count:** Stays low and stable
- **Cleanup score:** 20-30/100 (sustained)
- **Success score:** Continues improving toward 80/100

---

## Rollback Plan

If Phase 2 causes problems:

1. **Revert workflow changes:**
   ```bash
   git revert <phase2-commit>
   git push origin main
   ```

2. **PRs can be re-opened manually:**
   ```bash
   gh pr reopen <pr-number>
   ```

3. **Cleanup script has no persistent state** - just re-runs clean

---

## Success Criteria

Phase 2 is successful when:

- ✅ Cleanup script runs without errors
- ✅ 20-50 stale PRs closed in first run
- ✅ Open PR count reduced by 20-40%
- ✅ Memory tracks stale closure rate
- ✅ Proactive cleanup score >15/100
- ✅ Success score improves to >50/100
- ✅ No legitimate work closed mistakenly
- ✅ All closed PRs have explanation comments

---

## Timeline

**Day 1:**
- [ ] Test cleanup script locally (dry-run)
- [ ] Verify script logic is sound
- [ ] Run real cleanup (close 20-50 PRs)
- [ ] Monitor for any issues

**Day 2:**
- [ ] Update workflow to integrate script
- [ ] Update issue template with cleanup stats
- [ ] Add memory tracking for cleanup
- [ ] Test workflow integration
- [ ] Verify metrics populating

**Day 3:**
- [ ] Monitor first scheduled run
- [ ] Check success score improvement
- [ ] Validate cleanup continues working
- [ ] Document lessons learned

---

## Next Phase

After Phase 2 succeeds:

**Phase 3: Optimize Tech Lead Assignment**
- Goal: Reduce tech lead assignments by 50%
- Method: More selective assignment criteria
- Timeline: 2-3 days
- Expected impact: Reduce assignment rate from 13-39 to 5-15 per run

---

## Notes

### Why Phase 0 in Workflow (Not Agent)?

Running cleanup in workflow BEFORE creating coordination issue:
- ✅ Faster (no Copilot session needed)
- ✅ Cheaper (no Copilot cost for cleanup)
- ✅ More reliable (scripted, not LLM-based)
- ✅ Consistent (always runs same way)
- ✅ Results available to agent (via environment variables)

### Why Stale PRs Are a Problem

Stale PRs:
- Consume attention (signal-to-noise ratio)
- Block branch names (namespace pollution)
- Confuse contributors (which PRs matter?)
- Increase cycle time (more PRs = longer queue)
- Make metrics worse (open count stays high)

**Solution:** Aggressive cleanup keeps system healthy.

---

**Phase 2 Implementation Ready** ✅  
**Next: Integrate into workflow and test** 🚀
