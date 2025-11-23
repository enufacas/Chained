# Quick Reference: Evaluating Current Open PRs

**Purpose:** Help identify which of the current open PRs should be evaluated for closure  
**Context:** This repository has 598 copilot/agent branches and many open PRs  
**Action:** Use these criteria to systematically evaluate and reduce open PR count

## Quick Evaluation Command

```bash
# List all open PRs with key metadata
gh pr list --state open \
  --json number,title,author,isDraft,updatedAt,createdAt,labels,headRefName \
  --limit 100 | jq -r '.[] | 
    "PR #\(.number): \(.title) | 
     Author: \(.author.login) | 
     Updated: \(.updatedAt) | 
     Draft: \(.isDraft) | 
     Branch: \(.headRefName)"'
```

## Fast Stale PR Identification

Use these quick checks:

### 1. Inactive PRs (>7 days)

```bash
# Find PRs not updated in last 7 days
NOW=$(date -u +%s)
SEVEN_DAYS_AGO=$(( NOW - (7 * 86400) ))

gh pr list --state open --json number,updatedAt | jq -r --arg cutoff "$SEVEN_DAYS_AGO" '.[] | 
  select((.updatedAt | fromdateiso8601) < ($cutoff | tonumber)) | 
  "PR #\(.number) - Last updated: \(.updatedAt)"'
```

### 2. Old PRs (>14 days)

```bash
# Find PRs open for more than 14 days
FOURTEEN_DAYS_AGO=$(( NOW - (14 * 86400) ))

gh pr list --state open --json number,createdAt,title | jq -r --arg cutoff "$FOURTEEN_DAYS_AGO" '.[] | 
  select((.createdAt | fromdateiso8601) < ($cutoff | tonumber)) | 
  "PR #\(.number) - Created: \(.createdAt) - \(.title)"'
```

### 3. Draft PRs

```bash
# Find draft PRs
gh pr list --state open --json number,isDraft,updatedAt,title | jq -r '.[] | 
  select(.isDraft == true) | 
  "PR #\(.number) - DRAFT - Updated: \(.updatedAt) - \(.title)"'
```

### 4. PRs with Changes Requested

```bash
# Find PRs with changes requested label
gh pr list --state open --label "tech-lead-changes-requested" \
  --json number,updatedAt,title | jq -r '.[] | 
  "PR #\(.number) - Changes Requested - Updated: \(.updatedAt) - \(.title)"'
```

### 5. Copilot/Agent PRs

```bash
# Find PRs from copilot/agent branches
gh pr list --state open --json number,headRefName,title | jq -r '.[] | 
  select(.headRefName | test("^(copilot|agent)/")) | 
  "PR #\(.number) - \(.headRefName) - \(.title)"'
```

## Priority Closure Candidates

Based on the criteria, these PRs should be evaluated FIRST:

### High Priority (Close Immediately)

1. **Draft >7 days + no activity**
   - Clear abandonment signal
   - Low risk to close

2. **PR with closed issue**
   - Work is done or cancelled
   - Should be closed or merged

3. **Conflicts >3 days**
   - Blocking merge
   - Author not addressing

### Medium Priority (Evaluate Carefully)

4. **Inactive >7 days**
   - May just be awaiting review
   - Check for valid reason

5. **Changes requested >7 days + no commits**
   - Feedback not addressed
   - May be stalled

6. **Open >14 days (any status)**
   - Taking too long
   - Escalate or close

### Low Priority (Monitor)

7. **Active but slow progress**
   - Has recent activity
   - Just needs more time

8. **Awaiting external input**
   - Valid reason for delay
   - Keep open with note

## Sample Evaluation Script

```bash
#!/bin/bash
# Quick PR evaluation for meta-coordinator

echo "🔍 Evaluating Open PRs"
echo "======================"
echo ""

# Get all open PRs
PRS=$(gh pr list --state open --json number,title,author,isDraft,updatedAt,createdAt,labels,headRefName --limit 100)

# Count totals
TOTAL=$(echo "$PRS" | jq 'length')
echo "📊 Total Open PRs: $TOTAL"
echo ""

# Check each category
NOW=$(date -u +%s)

# Inactive >7 days
INACTIVE_7D=$(echo "$PRS" | jq --arg cutoff "$((NOW - 7*86400))" '[.[] | select((.updatedAt | fromdateiso8601) < ($cutoff | tonumber))] | length')
echo "⚠️  Inactive >7 days: $INACTIVE_7D"

# Open >14 days
OLD_14D=$(echo "$PRS" | jq --arg cutoff "$((NOW - 14*86400))" '[.[] | select((.createdAt | fromdateiso8601) < ($cutoff | tonumber))] | length')
echo "⚠️  Open >14 days: $OLD_14D"

# Draft PRs
DRAFTS=$(echo "$PRS" | jq '[.[] | select(.isDraft == true)] | length')
echo "📝 Draft PRs: $DRAFTS"

# Changes requested
CHANGES=$(echo "$PRS" | jq '[.[] | select(.labels[]? | .name == "tech-lead-changes-requested")] | length')
echo "🔄 Changes Requested: $CHANGES"

# Copilot/agent PRs
COPILOT=$(echo "$PRS" | jq '[.[] | select(.headRefName | test("^(copilot|agent)/"))] | length')
echo "🤖 Copilot/Agent PRs: $COPILOT"

echo ""
echo "💡 Recommended Actions:"
echo "  - Review $INACTIVE_7D inactive PRs for closure"
echo "  - Evaluate $OLD_14D old PRs for escalation or closure"
echo "  - Check $DRAFTS draft PRs for abandonment"
echo "  - Follow up on $CHANGES PRs with requested changes"

echo ""
echo "📋 Next Steps:"
echo "  1. Review high priority candidates first"
echo "  2. Post explanation comments before closing"
echo "  3. Record closures in memory"
echo "  4. Monitor metrics over next 5 runs"
```

## Manual PR Review Process

For each candidate PR:

### 1. Gather Information

```bash
PR_NUM=123

# Get full PR details
gh pr view $PR_NUM

# Check related issue
gh pr view $PR_NUM --json body | grep -oP 'Closes #\K\d+|Fixes #\K\d+' | while read issue; do
  echo "Related issue #$issue status:"
  gh issue view $issue --json state,closedAt
done

# Check CI status
gh pr checks $PR_NUM

# View recent activity
gh pr view $PR_NUM --comments | tail -20
```

### 2. Make Decision

Use this decision tree:

```
Is PR inactive >7 days?
├─ Yes → Is it draft or has changes requested?
│  ├─ Yes → **CLOSE** (High Priority)
│  └─ No → Check if awaiting external input
│     ├─ Yes → Keep open, add comment
│     └─ No → **CLOSE** (Medium Priority)
└─ No → Is PR open >14 days?
   ├─ Yes → Escalate or close
   └─ No → Monitor, no action yet
```

### 3. Document and Close

```bash
# Post explanation
gh pr comment $PR_NUM --body "## 🧹 Stale PR Evaluation

This PR is being evaluated for closure due to:
- [reason 1]
- [reason 2]

If work should continue, please:
1. Comment with update
2. Push new commits
3. Address any feedback

Will close in 24 hours if no response.

*Evaluating per docs/META_COORDINATOR_PR_LIFECYCLE.md*"

# Wait 24 hours, then close if no response
sleep 86400  # Or do this in next run

gh pr close $PR_NUM --comment "Closing as stale - see evaluation comment above"
```

## Expected Results

After systematic evaluation:

**Before:**
- 598 copilot/agent branches
- 80+ open PRs
- Many stale and forgotten

**After (5 runs):**
- ~300 branches (50% reduction)
- ~40 open PRs (50% reduction)
- All active, none stale

## Metrics to Track

```python
metrics = {
  'evaluation_run': timestamp,
  'total_prs_evaluated': count,
  'stale_identified': count,
  'prs_closed': count,
  'reasons': {
    'inactive_7d': count,
    'draft_abandoned': count,
    'changes_not_addressed': count,
    'issue_closed': count,
    'conflicts': count,
    'ci_failing': count
  },
  'open_pr_count_change': before - after
}
```

## Common Scenarios

### Scenario 1: Agent Spawn PR (stale)

```
PR #456: "Spawn new agent: analyze-master"
- Created 10 days ago
- Draft: true
- No commits in 8 days
- Related issue: closed

→ Action: CLOSE
→ Reason: Draft abandoned, issue closed
```

### Scenario 2: Feature PR (waiting for review)

```
PR #457: "Add new API endpoint"
- Created 5 days ago
- Draft: false
- Last update: 2 days ago (comment from author)
- Tech lead assigned
- Awaiting review

→ Action: KEEP OPEN
→ Reason: Active, awaiting review
```

### Scenario 3: Fix PR (changes requested, no response)

```
PR #458: "Fix workflow bug"
- Created 12 days ago
- Changes requested 9 days ago
- No commits since
- No author response

→ Action: CLOSE
→ Reason: Changes requested >7 days, no response
```

## Integration with Meta-Coordinator

The meta-coordinator should:

1. **Run this evaluation in Phase 0** of every coordination run
2. **Apply criteria systematically** (not subjectively)
3. **Document all decisions** with explanation comments
4. **Track metrics** in memory system
5. **Learn from patterns** to improve criteria

## Quick Tips

✅ **DO:**
- Start conservatively (high priority only)
- Always document reasons
- Give 24-hour warning when possible
- Track metrics for learning
- Review patterns regularly

❌ **DON'T:**
- Close PRs with recent activity
- Close without explanation
- Ignore author responses
- Apply criteria inconsistently
- Rush the cleanup

## Success Indicators

You're doing well if:
- Open PR count decreasing steadily
- No complaints about wrongly closed PRs
- Explanations are clear and helpful
- Metrics show consistent application
- Time to merge for active PRs improving

---

**Use this guide** for systematic, documented, and effective PR lifecycle management.

**Reference:** See `docs/META_COORDINATOR_PR_LIFECYCLE.md` for complete details.
