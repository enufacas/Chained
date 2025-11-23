# Meta-Coordinator PR Lifecycle Management

**Last Updated:** 2025-11-23  
**Agent:** @meta-coordinator-system  
**Purpose:** Guide for systematic PR lifecycle management and open PR reduction

## Overview

This document provides comprehensive guidance for the **@meta-coordinator-system** agent on managing PR lifecycles, identifying stale PRs, and systematically reducing the open PR count.

## Problem Statement

**Original Issue:** When meta-coordinator closes a PR, it forces the copilot agent session to end before issue updates can complete, resulting in:
- Orphaned issues without final status updates
- Work completed but not documented
- Memory not persisted from interrupted sessions
- Ever-growing open PR count

**Solution:** Implement structured lifecycle management with:
1. Phase 0 cleanup at start of each session
2. Issue updates BEFORE any closing operations
3. Systematic stale PR evaluation and closure
4. Memory persistence before session termination

## Stale PR Identification Criteria

A PR is considered **stale** and eligible for cleanup if it meets **ANY** of these criteria:

### Age-Based Criteria

1. **Inactive for 7+ days**
   - No commits in last 7 days
   - No comments in last 7 days
   - No review activity in last 7 days
   - Exception: PRs with active discussion or awaiting external input

2. **Open for 14+ days (regardless of activity)**
   - Even with activity, PRs open this long need review
   - Either close or escalate to manual review
   - Document why it's taking so long

### Status-Based Criteria

3. **Draft PR inactive for 7+ days**
   - Still marked as draft
   - No commits in last 7 days
   - Author appears to have abandoned it

4. **WIP PR inactive for 10+ days**
   - Has WIP in title/labels
   - No progress in 10 days
   - Work appears stalled

5. **Changes requested for 7+ days with no response**
   - Has `tech-lead-changes-requested` label
   - No new commits addressing feedback
   - No communication from author

### Completion-Based Criteria

6. **Related issue closed but PR still open**
   - Issue that PR references is closed
   - PR should be closed or merged
   - Work may be complete but PR forgotten

7. **Copilot/agent PR with unassigned issue**
   - PR is from copilot or agent branch
   - Related issue has no assignee
   - Likely abandoned work

8. **CI checks failing for 3+ days**
   - CI/CD checks consistently failing
   - No attempts to fix in 3 days
   - Author not addressing failures

### Conflict-Based Criteria

9. **Merge conflicts for 3+ days**
   - Has merge conflicts
   - Not resolved in 3 days
   - Branch needs rebase or closure

10. **Branch far behind main (50+ commits)**
    - Branch is >50 commits behind main
    - No rebase attempts
    - Increasingly difficult to merge

## Stale PR Evaluation Process

### Step 1: List Candidate PRs

```bash
# Get all open PRs with metadata
gh pr list --state open --json number,title,author,isDraft,updatedAt,createdAt,labels,mergeable --limit 100 > /tmp/open_prs.json

# For each PR, evaluate against criteria
cat /tmp/open_prs.json | jq -r '.[] | @json'
```

### Step 2: Apply Criteria

For each PR:

```bash
PR_NUM=123

# Get PR details
pr_data=$(gh pr view $PR_NUM --json number,title,author,isDraft,updatedAt,createdAt,labels,mergeable,headRefName,additions,deletions)

# Extract metadata
updated_at=$(echo "$pr_data" | jq -r '.updatedAt')
created_at=$(echo "$pr_data" | jq -r '.createdAt')
is_draft=$(echo "$pr_data" | jq -r '.isDraft')
branch_name=$(echo "$pr_data" | jq -r '.headRefName')

# Calculate age
now=$(date -u +%s)
updated_seconds=$(date -d "$updated_at" +%s)
created_seconds=$(date -d "$created_at" +%s)
days_since_update=$(( ($now - $updated_seconds) / 86400 ))
days_since_creation=$(( ($now - $created_seconds) / 86400 ))

# Check criteria
is_stale=false
stale_reasons=()

# Age-based
if [ $days_since_update -gt 7 ]; then
  is_stale=true
  stale_reasons+=("Inactive for $days_since_update days")
fi

if [ $days_since_creation -gt 14 ]; then
  is_stale=true
  stale_reasons+=("Open for $days_since_creation days")
fi

# Status-based
if [ "$is_draft" = "true" ] && [ $days_since_update -gt 7 ]; then
  is_stale=true
  stale_reasons+=("Draft PR inactive for $days_since_update days")
fi

# Check for WIP in title
pr_title=$(echo "$pr_data" | jq -r '.title')
if echo "$pr_title" | grep -qiE '\[WIP\]|^WIP:|work.in.progress'; then
  if [ $days_since_update -gt 10 ]; then
    is_stale=true
    stale_reasons+=("WIP PR inactive for $days_since_update days")
  fi
fi

# Check labels for changes requested
has_changes_requested=$(echo "$pr_data" | jq -r '.labels[] | select(.name == "tech-lead-changes-requested") | .name')
if [ -n "$has_changes_requested" ] && [ $days_since_update -gt 7 ]; then
  is_stale=true
  stale_reasons+=("Changes requested 7+ days ago, no response")
fi

# Check related issue
pr_body=$(gh pr view $PR_NUM --json body --jq '.body')
issue_num=$(echo "$pr_body" | grep -oP 'Closes #\K\d+|Fixes #\K\d+|Resolves #\K\d+' | head -1)
if [ -n "$issue_num" ]; then
  issue_state=$(gh issue view $issue_num --json state --jq '.state' 2>/dev/null)
  if [ "$issue_state" = "CLOSED" ]; then
    is_stale=true
    stale_reasons+=("Related issue #$issue_num is closed")
  fi
fi

# Check CI status
checks=$(gh pr checks $PR_NUM --json state 2>/dev/null | jq -r '.[] | select(.state == "FAILURE") | .name')
if [ -n "$checks" ] && [ $days_since_update -gt 3 ]; then
  is_stale=true
  stale_reasons+=("CI failing for 3+ days")
fi

# Check merge conflicts
mergeable=$(echo "$pr_data" | jq -r '.mergeable')
if [ "$mergeable" = "CONFLICTING" ] && [ $days_since_update -gt 3 ]; then
  is_stale=true
  stale_reasons+=("Has merge conflicts for 3+ days")
fi

# Output evaluation
if [ "$is_stale" = true ]; then
  echo "PR #$PR_NUM is STALE"
  for reason in "${stale_reasons[@]}"; do
    echo "  - $reason"
  done
fi
```

### Step 3: Document Before Closure

**CRITICAL: Always document the reason before closing**

```bash
# Build explanation comment
reasons_text=$(printf '%s\n' "${stale_reasons[@]}" | sed 's/^/- /')

gh pr comment $PR_NUM --body "## 🧹 Stale PR Cleanup

This PR is being closed by @meta-coordinator-system due to:

$reasons_text

### What This Means

This PR has been identified as stale based on the criteria in \`docs/META_COORDINATOR_PR_LIFECYCLE.md\`.

### If This Work Should Continue

1. **Re-open this PR** if work is still needed
2. **Update the related issue** to reflect current status
3. **Push new commits** to address any outstanding feedback
4. **Comment on this PR** explaining why it should remain open

### Context

- **Created:** $(date -d "$created_at" +%Y-%m-%d)
- **Last Updated:** $(date -d "$updated_at" +%Y-%m-%d)
- **Days Since Update:** $days_since_update
- **Days Since Creation:** $days_since_creation

*Automated cleanup by @meta-coordinator-system as part of PR lifecycle management*
*See: docs/META_COORDINATOR_PR_LIFECYCLE.md*
"
```

### Step 4: Close PR

```bash
# Close without merging
gh pr close $PR_NUM --comment "Closing as stale - see detailed comment above"

# If it's a copilot/agent branch, delete it
if [[ $branch_name =~ ^(copilot|agent)/ ]]; then
  echo "Deleting branch: $branch_name"
  git push origin --delete "$branch_name" 2>/dev/null || echo "Branch already deleted or protected"
fi
```

### Step 5: Record in Memory

```python
from tools.meta_coordinator_memory import MetaCoordinatorMemory

memory = MetaCoordinatorMemory()
memory.record_stale_pr_cleanup(
    pr_num=pr_num,
    reasons=stale_reasons,
    age_days=days_since_update,
    author=author,
    branch_name=branch_name
)
memory.save()
```

## Session Termination Prevention

### The Problem

When a PR is merged or closed, GitHub may terminate the copilot session that created it. This prevents:
- Final issue updates
- Memory persistence
- Coordination issue closure
- Clean session boundaries

### The Solution: Critical Ordering

**ALWAYS follow this exact order:**

```python
# ========================================
# Step 1: POST ALL ISSUE UPDATES FIRST
# ========================================
# This ensures updates are recorded even if session terminates

# Update all related issues
gh issue comment $WORK_ISSUE_NUM --body "✅ Work completed in PR #$PR_NUM - merging now"
gh issue comment $COORDINATION_ISSUE_NUM --body "## 🎯 Phase 2 Complete\n\nProcessed $count PRs..."

# Wait a moment to ensure comments are saved
sleep 2

# ========================================
# Step 2: PERSIST MEMORY
# ========================================
memory.save()  # Save to file
# Use report_progress to commit memory
# (This creates a PR but doesn't close anything yet)

# ========================================
# Step 3: MERGE MEMORY PR (if created)
# ========================================
gh pr merge $MEMORY_PR_NUM --squash --delete-branch

# ========================================
# Step 4: NOW SAFE TO CLOSE/MERGE
# ========================================
# All updates posted, memory persisted
# Session can terminate safely now
gh pr merge $WORK_PR_NUM --squash --delete-branch
gh issue close $COORDINATION_ISSUE_NUM
```

### Code Pattern

```bash
# ❌ WRONG - Session terminates before updates
gh pr merge $PR_NUM
gh issue comment $ISSUE_NUM --body "Done!"  # Never executes!

# ✅ CORRECT - Updates before termination
gh issue comment $ISSUE_NUM --body "Merging PR #$PR_NUM now"
sleep 2
gh pr merge $PR_NUM  # Safe - updates already posted
```

### Exception Handling

```bash
# Even if merge fails, updates are already posted
if ! gh pr merge $PR_NUM; then
  echo "Merge failed, but issue updates already posted"
  # Session can terminate, no data loss
fi
```

## Open PR Reduction Strategy

### Target

**Reduce open PR count by 50% over next 5 coordination runs**

### Metrics to Track

```python
memory.track_pr_lifecycle_metrics({
    'run_id': run_id,
    'timestamp': timestamp,
    'open_prs_start': count_at_start,
    'open_prs_end': count_at_end,
    'prs_closed_stale': stale_closed,
    'prs_merged': merged_count,
    'prs_created': new_count,
    'net_change': end - start,
    'stale_reasons': Counter(all_stale_reasons)
})
```

### Immediate Actions (Phase 0 of every run)

1. **Close PRs stale >14 days** (high priority)
2. **Close draft PRs stale >7 days**
3. **Close PRs with closed issues**
4. **Close PRs with unresolvable conflicts >3 days**

### Preventive Measures

1. **Auto-merge faster:**
   - Check eligible PRs every run
   - Merge immediately when criteria met
   - Don't wait for next scheduled run

2. **Create feedback issues faster:**
   - Detect change requests immediately
   - Create feedback issue within same run
   - Assign agent immediately

3. **Escalate stuck PRs:**
   - PRs >7 days with changes requested
   - Create manual review issue
   - Tag repository owner

4. **Better agent assignment:**
   - Match agents more accurately
   - Provide learning context
   - Reduce work time through better matching

### Reporting

After each Phase 0 cleanup:

```markdown
## 🧹 Phase 0: Session Cleanup & PR Lifecycle Management

**Completed previous session work:**
- ✅ Updated 3 issues from interrupted sessions
- ✅ Posted final status to coordination issue #123

**Stale PR cleanup:**
- 🔍 Evaluated 84 open PRs
- 📋 Identified 15 stale PRs
- 🗑️ Closed 12 stale PRs
- 📊 Open PR count: 84 → 72 (14% reduction)

**Stale PR reasons:**
- 7 PRs inactive >7 days
- 3 draft PRs abandoned
- 2 PRs with closed issues
- Detailed breakdown in memory

**Memory context:**
- ✅ Loaded previous run data
- ✅ Reviewed patterns from last 5 runs
- ✅ Identified: Most stale PRs are agent spawns

**Next actions:**
- Proceeding to Phase 1: Assess current state
```

## Best Practices

### 1. Always Document

Every stale PR closure should:
- Have a detailed explanation comment
- List specific criteria met
- Provide instructions for reopening
- Reference this documentation

### 2. Be Conservative

When in doubt:
- Post a warning comment first
- Give author 24 hours to respond
- Don't close if there's active discussion
- Escalate complex cases

### 3. Learn from Patterns

Track in memory:
- Which criteria are most common
- Which agent types create most stale PRs
- Which PR sizes are most likely to stall
- Optimize agent assignment based on patterns

### 4. Communicate Clearly

In closure comments:
- Be specific about criteria
- Be helpful about next steps
- Be respectful of author's work
- Provide context and links

### 5. Measure Progress

Every run:
- Track open PR count change
- Monitor stale PR closure rate
- Measure time to merge for active PRs
- Report metrics in coordination issue

## Implementation Checklist

For **@meta-coordinator-system** in each coordination run:

### Phase 0 Checklist

- [ ] Check for interrupted previous sessions
- [ ] Complete pending issue updates
- [ ] Load memory from previous runs
- [ ] List all open PRs
- [ ] Evaluate each PR against stale criteria
- [ ] Document closure reasons for stale PRs
- [ ] Close stale PRs with explanation
- [ ] Delete copilot/agent branches
- [ ] Record cleanup in memory
- [ ] Report Phase 0 summary

### Critical Ordering Checklist

- [ ] Post ALL issue updates FIRST
- [ ] Wait 2 seconds for comments to save
- [ ] Save memory to file
- [ ] Commit and create memory PR
- [ ] Merge memory PR
- [ ] Now safe to merge/close work PRs
- [ ] Finally close coordination issue

### Metrics Checklist

- [ ] Count open PRs at start
- [ ] Count stale PRs identified
- [ ] Count PRs closed in Phase 0
- [ ] Count PRs merged in Phase 2
- [ ] Count open PRs at end
- [ ] Calculate net change
- [ ] Record in memory
- [ ] Report in coordination summary

## Related Documentation

- `.github/agents/meta-coordinator-system.md` - Agent definition
- `.github/workflows/meta-coordinator.yml` - Workflow configuration
- `tools/meta-coordinator-memory.py` - Memory system
- `.github/copilot-instructions.md` - Repository instructions

## Revision History

- **2025-11-23:** Initial version created to address session termination and open PR count issues
- Document created by @meta-coordinator-system lifecycle improvement initiative

---

**@meta-coordinator-system** - Use this document as authoritative guidance for PR lifecycle management and stale PR evaluation.
