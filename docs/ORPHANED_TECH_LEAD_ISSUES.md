# Orphaned Tech Lead Issue Handling

## Overview

This document describes how the meta-coordinator detects and fixes tech lead review issues that have assignment labels but no actual work being done.

## The Problem

Tech lead review issues can become "effectively orphaned" in several ways:

### 1. Never Assigned (Most Critical)
```
Issue created with tech-lead-review label
    ↓
Assignment step skipped or failed
    ↓
Issue sits idle - no Copilot session ever starts
    ↓
PR blocked indefinitely
```

### 2. Stale with No Activity
```
Issue assigned to tech lead
    ↓
Tech lead never comments or works on it
    ↓
5+ days pass with no activity
    ↓
PR blocked, no progress
```

### 3. Linked PR Closed
```
Tech lead review issue still open
    ↓
Linked PR was merged or closed
    ↓
Issue no longer needed but still consuming attention
```

### 4. General Staleness
```
Issue open >7 days
    ↓
No comments from anyone
    ↓
No updates, no activity
    ↓
Dead work item
```

## Detection Criteria

The meta-coordinator checks for orphaned tech lead issues using these criteria:

### Criterion 1: Never Assigned (CRITICAL)

**Detection:**
```bash
has_tech_lead_label=$(gh issue view $issue_num --json labels --jq '.labels[] | select(.name == "tech-lead-review")')
has_copilot_label=$(gh issue view $issue_num --json labels --jq '.labels[] | select(.name == "copilot-assigned")')

if [ -n "$has_tech_lead_label" ] && [ -z "$has_copilot_label" ]; then
  echo "ORPHANED: Never assigned!"
fi
```

**Why This Happens:**
- Issue creation succeeded but assignment step failed
- Assignment script not called after creating issue
- Environment variables missing during assignment
- Race condition or workflow interruption

**Impact:**
- 🚨 **BLOCKING**: PR cannot proceed without review
- ⏰ **CYCLE TIME**: Every hour this sits adds to PR cycle time
- 📊 **METRICS**: Increases open issue count without progress

### Criterion 2: Stale (>5 Days, No Tech Lead Comments)

**Detection:**
```bash
issue_age_days=$(calculate_days_since "$created_at")
tech_lead_comments=$(gh issue view $issue_num --json comments \
  --jq '.comments[] | select(.author.login | contains("copilot")) | .id' | wc -l)

if [ $issue_age_days -gt 5 ] && [ $tech_lead_comments -eq 0 ]; then
  echo "ORPHANED: Stale, no tech lead activity"
fi
```

**Why This Happens:**
- Tech lead was assigned but never picked up the work
- Copilot session started but terminated early
- Work deprioritized or forgotten
- Tech lead agent needs escalation

**Impact:**
- ⏰ **CYCLE TIME**: PR waiting 5+ days for review
- 🔄 **THROUGHPUT**: Blocking PR from merging
- 📊 **METRICS**: Both PR and issue aging

### Criterion 3: Linked PR Closed/Merged

**Detection:**
```bash
pr_num=$(gh issue view $issue_num --json body --jq '.body' | grep -oP 'PR #\K\d+' | head -1)
pr_state=$(gh pr view $pr_num --json state --jq '.state' 2>/dev/null || echo "UNKNOWN")

if [ "$pr_state" = "MERGED" ] || [ "$pr_state" = "CLOSED" ]; then
  echo "ORPHANED: PR ${pr_state} but issue still open"
fi
```

**Why This Happens:**
- PR merged/closed but issue close step skipped
- Copilot session terminated before cleanup
- Manual PR closure without closing issue
- Review completed elsewhere

**Impact:**
- 📊 **METRICS**: Inflates open issue count
- 🗑️ **CLUTTER**: Dead work item in issue list
- 🔍 **CONFUSION**: Looks like active work

### Criterion 4: No Activity (>7 Days)

**Detection:**
```bash
last_updated=$(gh issue view $issue_num --json updatedAt --jq '.updatedAt')
days_stale=$(calculate_days_since "$last_updated")

if [ $days_stale -gt 7 ]; then
  echo "ORPHANED: No activity for $days_stale days"
fi
```

**Why This Happens:**
- Issue completely forgotten
- Work deprioritized without closing
- Systemic issue preventing progress
- May need manual intervention

**Impact:**
- ⏰ **CYCLE TIME**: Week+ delay with zero progress
- 📊 **METRICS**: Significant drag on all metrics
- 🚨 **SIGNAL**: Something fundamentally wrong

## Resolution Actions

The meta-coordinator takes different actions based on the type of orphaning:

### Action 1: Re-Assign (Never Assigned or Stale)

```bash
# Get tech lead for the PR
tech_lead=$(python3 tools/match-pr-to-tech-lead.py "$pr_num" --get-tech-lead)

# Check if PR still open
pr_state=$(gh pr view $pr_num --json state --jq '.state' 2>/dev/null || echo "CLOSED")

if [ "$pr_state" = "OPEN" ]; then
  # Re-assign tech lead to fix orphaned issue
  export INPUT_ISSUE_NUMBER=$issue_num
  export FORCE_AGENT=$tech_lead
  ./tools/assign-copilot-to-issue.sh
  
  gh issue comment $issue_num --body "🔧 **Assignment Gap Fixed**

This review issue was created but never assigned. Now assigning @${tech_lead}.

*Automated fix by @meta-coordinator-system*"
  
  echo "✅ Re-assigned issue #${issue_num} to @${tech_lead}"
fi
```

**When Used:**
- Issue has `tech-lead-review` but no `copilot-assigned`
- Issue is stale (>5 days, no tech lead comments)

**Result:**
- ✅ Copilot session starts
- ✅ Tech lead begins working
- ✅ PR unblocked

### Action 2: Close (Linked PR Closed/Merged)

```bash
if [ "$pr_state" = "MERGED" ]; then
  gh issue close $issue_num --comment "✅ PR #${pr_num} was merged. Closing review issue.

*Automated cleanup by @meta-coordinator-system*"
  echo "✅ Closed issue #${issue_num} (PR merged)"
  
elif [ "$pr_state" = "CLOSED" ]; then
  gh issue close $issue_num --comment "🚫 PR #${pr_num} was closed. Closing review issue.

*Automated cleanup by @meta-coordinator-system*"
  echo "✅ Closed issue #${issue_num} (PR closed)"
fi
```

**When Used:**
- Issue still open but linked PR is MERGED or CLOSED

**Result:**
- ✅ Reduces open issue count
- ✅ Removes dead work item
- ✅ Cleans up issue list

### Action 3: Escalate (Very Stale)

```bash
if [ $issue_age_days -gt 5 ] && [ "$tech_lead_comments" = "0" ]; then
  # Re-assign to potentially trigger work
  export INPUT_ISSUE_NUMBER=$issue_num
  export FORCE_AGENT=$tech_lead
  ./tools/assign-copilot-to-issue.sh
  
  gh issue comment $issue_num --body "## ⚠️ Stale Review Escalation

This tech lead review has been open for ${issue_age_days} days with no activity.

**Re-assigning:** @${tech_lead}

**If this review is still needed:**
- Tech lead should complete review within 48 hours
- Add \`tech-lead-approved\` or \`tech-lead-changes-requested\` label to PR

**If no longer needed:**
- Close this issue with explanation
- Update PR status accordingly

*Automated escalation by @meta-coordinator-system*"
  
  echo "✅ Escalated stale issue #${issue_num}, re-assigned"
fi
```

**When Used:**
- Issue >5 days old with no tech lead activity

**Result:**
- ✅ Re-triggers assignment (may have been lost)
- ✅ Escalates with 48-hour deadline
- ✅ Forces decision: complete or close

## Integration in Meta-Coordinator Flow

### Phase 1: Assessment
```bash
# Count orphaned tech lead issues
orphaned_count=$(gh issue list --label "tech-lead-review,-copilot-assigned" \
  --state open --json number --jq 'length')

echo "Found ${orphaned_count} orphaned tech lead review issues"
```

### Priority 1: Reduce Cycle Time & Counts
```bash
# Step 8: Fix orphaned tech lead review issues
for issue_num in $(gh issue list --label "tech-lead-review,-copilot-assigned" \
  --state open --json number --jq '.[].number'); do
  # ... resolution logic ...
done
```

### Priority 4: Exception Handling
```bash
# Section 7: Handle all types of orphaned issues
# - Never assigned
# - Stale (>5 days)
# - Linked PR closed
# - No activity (>7 days)
```

## Metrics Tracking

Track orphaned issue fixes in memory:

```python
# Record orphaned issue fixed
memory.record_action(
    action="orphaned_tech_lead_issue_fixed",
    issue_number=issue_num,
    reason="never_assigned",
    resolution="re_assigned"
)

# Record orphaned issue closed
memory.record_action(
    action="orphaned_tech_lead_issue_closed",
    issue_number=issue_num,
    reason="pr_closed",
    resolution="closed"
)
```

## Success Indicators

Effective orphaned issue handling shows:

✅ **Reduced Orphan Rate**
- Target: <5% of tech-lead-review issues orphaned
- Measure: (orphaned / total tech-lead-review) * 100

✅ **Fast Fix Time**
- Target: Orphaned issues fixed within 1 run (15 minutes)
- Measure: Time from orphaned → fixed

✅ **Improved Cycle Time**
- Effect: PRs no longer stuck waiting for "ghost reviews"
- Measure: Average PR cycle time decreases

✅ **Reduced Open Count**
- Effect: Closing orphaned issues for closed PRs
- Measure: Open issue count decreases

## Common Patterns

### Pattern 1: Batch Fix Never-Assigned Issues
```bash
# Fix all tech lead issues that were never assigned
gh issue list --label "tech-lead-review,-copilot-assigned" --state open \
  --json number --jq '.[].number' | while read issue_num; do
  pr_num=$(gh issue view $issue_num --json body --jq '.body' | grep -oP 'PR #\K\d+')
  tech_lead=$(python3 tools/match-pr-to-tech-lead.py "$pr_num" --get-tech-lead)
  
  export INPUT_ISSUE_NUMBER=$issue_num
  export FORCE_AGENT=$tech_lead
  ./tools/assign-copilot-to-issue.sh
done
```

### Pattern 2: Cleanup Issues for Closed PRs
```bash
# Close all review issues where PR is closed/merged
gh issue list --label "tech-lead-review" --state open --json number,body | \
  jq -r '.[] | "\(.number)|\(.body)"' | while IFS='|' read issue_num body; do
  pr_num=$(echo "$body" | grep -oP 'PR #\K\d+' | head -1)
  pr_state=$(gh pr view $pr_num --json state --jq '.state' 2>/dev/null || echo "UNKNOWN")
  
  if [ "$pr_state" != "OPEN" ]; then
    gh issue close $issue_num --comment "PR ${pr_state}, closing review issue."
  fi
done
```

### Pattern 3: Escalate Stale Reviews
```bash
# Escalate reviews >5 days old with no activity
gh issue list --label "tech-lead-review" --state open \
  --json number,createdAt,comments | jq -c '.[]' | while read issue_data; do
  issue_num=$(echo "$issue_data" | jq -r '.number')
  created_at=$(echo "$issue_data" | jq -r '.createdAt')
  age_days=$(calculate_days_since "$created_at")
  tech_lead_comments=$(echo "$issue_data" | jq '[.comments[] | select(.author.login | contains("copilot"))] | length')
  
  if [ $age_days -gt 5 ] && [ $tech_lead_comments -eq 0 ]; then
    # Re-assign and escalate
    tech_lead=$(get_tech_lead_from_issue $issue_num)
    export INPUT_ISSUE_NUMBER=$issue_num
    export FORCE_AGENT=$tech_lead
    ./tools/assign-copilot-to-issue.sh
    
    gh issue comment $issue_num --body "⚠️ Escalated: ${age_days} days with no activity"
  fi
done
```

## Troubleshooting

### Issue Re-Assigned But Still No Activity

**Symptom:** Issue re-assigned but tech lead still not working
**Possible Causes:**
1. Assignment script succeeded but Copilot session failed
2. Tech lead agent profile has issues
3. Issue body malformed, preventing directive parsing
4. GitHub API delays

**Solution:**
1. Check if `copilot-assigned` label applied
2. Verify issue body has `<!-- COPILOT_AGENT:tech-lead-name -->`
3. Check for Copilot errors in GitHub Actions logs
4. May need manual intervention

### False Positives: Not Actually Orphaned

**Symptom:** Issue flagged as orphaned but work is happening
**Possible Causes:**
1. Tech lead working but not commenting yet
2. Comments from human, not Copilot bot
3. Work happening in PR, not issue

**Solution:**
- Check PR for tech lead activity
- Look for recent PR comments/reviews
- May need to adjust staleness threshold (>5 days)

### Too Many Orphaned Issues

**Symptom:** High percentage of tech lead issues orphaned
**Root Causes:**
1. Assignment step consistently failing
2. Workflow interruptions during creation
3. Environment variable issues
4. Tech lead agents not responding

**Solution:**
- Audit workflow execution logs
- Check environment variable configuration
- Verify tech lead agent definitions
- May need systematic fix, not just patching

## Summary

**Key Takeaways:**

1. **Detection is automatic** - Meta-coordinator checks every run
2. **Fix is immediate** - Re-assign or close within 15 minutes
3. **Impact is significant** - Unblocks PRs, reduces cycle time
4. **Metrics improve** - Open counts down, cycle time down

**Remember:**
- Orphaned = Has label but no work happening
- Most critical: Never assigned (no copilot-assigned label)
- Quick fix: Re-assign using FORCE_AGENT
- Always check if PR still open before re-assigning
- Close issues for closed/merged PRs immediately

**Always:**
- Check tech-lead-review issues for copilot-assigned label
- Re-assign if missing (don't just add label)
- Close orphaned issues for closed PRs
- Escalate stale reviews with deadlines
- Track orphaned issue metrics
