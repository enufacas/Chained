# Tech Lead Review System - Label Reference

**Created by @workflows-tech-lead**

## Overview

The Tech Lead Review System uses a set of labels to manage the review cycle state. These labels control whether a PR can be auto-merged and track the review iteration process.

## Label Categories

### Blocking Labels (Prevent Merge)

These labels block auto-merge until resolved:

#### 🔴 `needs-tech-lead-review`

**Color:** `#D73A4A` (Red)  
**Purpose:** Indicates that Tech Lead review is required before this PR can be merged  
**Applied:** Automatically by `tech-lead-review.yml` when PR meets review criteria  
**Removed:** Automatically when Tech Lead approves the PR  
**Blocks Merge:** ✅ Yes

**When Applied:**
- PR modifies protected paths (`.github/workflows/`, `.github/agents/`, etc.)
- PR exceeds complexity thresholds (>5 files or >100 lines changed)
- PR contains security-related keywords

**Auto-Merge Behavior:**
```bash
if has_label("needs-tech-lead-review") && !has_label("tech-lead-approved"):
    BLOCK_MERGE()
    POST_COMMENT("Tech Lead review required")
```

---

#### 🟡 `tech-lead-changes-requested`

**Color:** `#FBCA04` (Yellow/Orange)  
**Purpose:** Tech Lead has requested changes to this PR  
**Applied:** Automatically when Tech Lead submits a "Request Changes" review  
**Removed:** Automatically when Tech Lead approves the PR  
**Blocks Merge:** ✅ Yes

**When Applied:**
- Tech Lead reviews PR and clicks "Request Changes"
- Specific feedback is provided in review comments
- Indicates iteration is needed

**Auto-Merge Behavior:**
```bash
if has_label("tech-lead-changes-requested"):
    BLOCK_MERGE()
    POST_COMMENT("Address Tech Lead feedback before merge")
```

**Review Cycle:**
1. Label applied when changes requested
2. Agent/Author fixes issues and pushes changes
3. `tech-lead-review.yml` re-triggers and notifies Tech Lead
4. Tech Lead re-reviews
5. If approved, label is removed and `tech-lead-approved` is added
6. If more changes needed, cycle repeats

---

### Approval Label (Enables Merge)

#### 🟢 `tech-lead-approved`

**Color:** `#0E8A16` (Green)  
**Purpose:** Tech Lead has approved this PR for merge  
**Applied:** Automatically when Tech Lead submits an "Approve" review  
**Removed:** Never (remains as permanent approval record)  
**Blocks Merge:** ❌ No (enables merge)

**When Applied:**
- Tech Lead reviews PR and clicks "Approve"
- All requested changes have been addressed
- PR is ready for merge

**Auto-Merge Behavior:**
```bash
if has_label("tech-lead-approved"):
    LOG("Tech Lead approval received")
    PROCEED_WITH_MERGE()
```

**Notes:**
- This label is the "green light" for auto-merge to proceed
- Once applied, it remains even if new commits are pushed
- If significant changes are made after approval, Tech Lead may manually remove it

---

### Tracking Label (Informational)

#### 🔵 `tech-lead-review-cycle`

**Color:** `#1D76DB` (Blue)  
**Purpose:** Indicates this PR is in an active Tech Lead review iteration cycle  
**Applied:** Automatically with `needs-tech-lead-review`  
**Removed:** When PR is merged or closed  
**Blocks Merge:** ℹ️ No (informational only)

**When Applied:**
- PR requires Tech Lead review (alongside `needs-tech-lead-review`)
- Helps track PRs actively in review process

**Uses:**
- Query PRs in active review: `is:pr is:open label:tech-lead-review-cycle`
- Metrics on review cycle times
- Identifying stuck PRs needing attention

---

### Identifier Labels (Assignment)

These labels identify which Tech Lead is responsible for the review:

#### 🟣 `tech-lead:workflows-tech-lead`

**Color:** `#5319E7` (Purple)  
**Purpose:** Assigned to workflows-tech-lead for review  
**Applied:** Automatically when PR modifies workflow-related files  
**Removed:** Never (permanent identifier)  
**Blocks Merge:** ℹ️ No (informational only)

**Responsible For:**
- `.github/workflows/**`
- `.github/actions/**`

**Review Focus:**
- Workflow syntax and logic
- Action version pinning
- Secret handling
- Permission scoping
- Error handling patterns

---

#### 🟣 `tech-lead:agents-tech-lead`

**Color:** `#5319E7` (Purple)  
**Purpose:** Assigned to agents-tech-lead for review  
**Applied:** Automatically when PR modifies agent-related files  
**Removed:** Never (permanent identifier)  
**Blocks Merge:** ℹ️ No (informational only)

**Responsible For:**
- `.github/agents/**`
- `.github/agent-system/**`
- `tools/match-issue-to-agent.py`
- `tools/match-pr-to-tech-lead.py`

**Review Focus:**
- Agent definition consistency
- Pattern matching correctness
- Performance metrics accuracy
- Documentation completeness

---

## Label Combinations and States

### Initial State (Review Required)
```
✅ needs-tech-lead-review
✅ tech-lead:<name>
✅ tech-lead-review-cycle
❌ tech-lead-approved
❌ tech-lead-changes-requested
```
**Status:** Awaiting Tech Lead review  
**Merge:** Blocked

---

### State: Changes Requested
```
✅ needs-tech-lead-review
✅ tech-lead:<name>
✅ tech-lead-review-cycle
✅ tech-lead-changes-requested
❌ tech-lead-approved
```
**Status:** Agent/Author must address feedback  
**Merge:** Blocked

---

### State: Approved
```
✅ tech-lead:<name>
✅ tech-lead-approved
❌ needs-tech-lead-review (removed)
❌ tech-lead-changes-requested (removed if present)
❌ tech-lead-review-cycle (removed)
```
**Status:** Ready for merge  
**Merge:** Allowed

---

### State: Optional Review
```
✅ tech-lead:<name>
❌ needs-tech-lead-review (not applied)
❌ tech-lead-approved (not needed)
❌ tech-lead-changes-requested (not present)
❌ tech-lead-review-cycle (not needed)
```
**Status:** No review required, may proceed  
**Merge:** Allowed

---

## Querying PRs by Label

### Find PRs needing Tech Lead review
```bash
gh pr list --label "needs-tech-lead-review" --state open
```

### Find PRs with changes requested
```bash
gh pr list --label "tech-lead-changes-requested" --state open
```

### Find PRs approved by Tech Lead
```bash
gh pr list --label "tech-lead-approved" --state open
```

### Find all PRs in review cycle
```bash
gh pr list --label "tech-lead-review-cycle" --state open
```

### Find PRs by specific Tech Lead
```bash
gh pr list --label "tech-lead:workflows-tech-lead" --state open
gh pr list --label "tech-lead:agents-tech-lead" --state open
```

---

## Label Management

### Manual Label Application

While labels are primarily managed automatically, they can be manually applied if needed:

```bash
# Add a label
gh pr edit <PR_NUMBER> --add-label "tech-lead-approved"

# Remove a label
gh pr edit <PR_NUMBER> --remove-label "needs-tech-lead-review"
```

### When to Manually Adjust Labels

**Scenarios for manual intervention:**
- Workflow fails to apply labels correctly
- Tech Lead wants to explicitly approve without formal review
- PR needs urgent merge and Tech Lead has already reviewed informally
- Debugging label-related issues

**⚠️ Caution:** Manual label changes can bypass intended review process. Use sparingly.

---

## Metrics and Reporting

Labels enable tracking of:

### Review Cycle Metrics
- Average time from `needs-tech-lead-review` to `tech-lead-approved`
- Number of iteration cycles (changes requested → fixed → re-review)
- Tech Lead workload (number of PRs assigned to each)

### System Health Metrics
- PRs blocked on Tech Lead review
- PRs with outstanding change requests
- Time to first review
- Review approval rate

### Query Examples

```bash
# PRs approved today
gh pr list --label "tech-lead-approved" --state closed --search "closed:>=2025-01-01"

# Count PRs by Tech Lead
gh pr list --label "tech-lead:workflows-tech-lead" --json number | jq 'length'

# PRs stuck in review (open >7 days with needs review)
gh pr list --label "needs-tech-lead-review" --state open --search "created:<=2025-01-01"
```

---

## Creating Labels

Labels are automatically created by the `setup-tech-lead-labels.yml` workflow when:
- The workflow is manually triggered via `workflow_dispatch`
- Changes are pushed to main that affect the tech lead review system

To manually create all labels:
```bash
gh workflow run setup-tech-lead-labels.yml
```

---

## Troubleshooting

### Label not applied automatically
1. Check `tech-lead-review.yml` workflow logs
2. Verify PR meets review criteria
3. Re-run workflow via workflow_dispatch if needed

### Label stuck after approval
1. Check if Tech Lead actually approved (not just commented)
2. Verify `pull_request_review` event triggered workflow
3. Manually remove blocking label if workflow failed

### Multiple Tech Lead labels
- This is expected if PR touches multiple subsystems
- Primary Tech Lead (first in list) is notified
- All assigned Tech Leads can review

### Label colors not matching
- Re-run `setup-tech-lead-labels.yml` to update colors
- Colors standardized: Red (blocking), Green (approval), Yellow (changes), Blue (tracking), Purple (identifier)

---

## Related Documentation

- [Tech Lead Review Cycle](./TECH_LEAD_REVIEW_CYCLE.md) - Complete system documentation
- [Tech Lead Review Flow Diagrams](./TECH_LEAD_REVIEW_FLOW_DIAGRAMS.md) - Visual flow charts
- [Workflows Tech Lead Agent](../.github/agents/workflows-tech-lead.md) - Agent definition
- [Agents Tech Lead Agent](../.github/agents/agents-tech-lead.md) - Agent definition

---

*🏷️ Tech Lead Review System Label Reference - Created by @workflows-tech-lead*  
*Last updated: 2025-11-20*
