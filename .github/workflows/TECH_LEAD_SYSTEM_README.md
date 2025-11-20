# Tech Lead Review System

## Overview

The Tech Lead Review System is an automated workflow that assigns domain-expert "Tech Lead" agents to review pull requests that touch their areas of responsibility. This ensures that critical changes receive appropriate expert oversight before being merged.

## System Components

### 1. Tech Lead Agents

Tech Lead agents are specialized agents with deep expertise in specific areas of the codebase. They are defined in `.github/agents/` with the suffix `-tech-lead.md`.

**Current Tech Leads:**

| Tech Lead | Specialization | Responsible Paths |
|-----------|----------------|-------------------|
| **workflows-tech-lead** | GitHub Actions & Workflows | `.github/workflows/**`, `.github/actions/**` |
| **agents-tech-lead** | Agent System & Definitions | `.github/agents/**`, `.github/agent-system/**`, `tools/*agent*.py` |
| **docs-tech-lead** | Documentation & Markdown | `docs/**/*.md`, `README.md`, `*.md`, `learnings/**`, `summaries/**` |
| **github-pages-tech-lead** | GitHub Pages Web Content | `docs/**/*.html`, `docs/**/*.css`, `docs/**/*.js`, `docs/data/**`, `docs/assets/**` |

**Key Characteristics:**
- Protected from performance-based elimination
- Have clear path-based responsibilities in their agent definition
- Are automatically assigned to PRs touching their paths
- Provide specialized review criteria for their domains

### 2. Core Workflows

#### `tech-lead-review.yml`

**Purpose:** Analyzes PRs and assigns appropriate Tech Leads

**Triggers:**
- Pull request events: `opened`, `synchronize`, `ready_for_review`, `reopened`
- Pull request review events: `submitted`
- Manual dispatch: `workflow_dispatch`

**What it does:**
1. Checks for WIP markers in PR title (skips review if found)
2. Gets list of changed files from PR
3. Matches files to Tech Lead agents using path patterns
4. Analyzes PR complexity (file count, line changes, protected paths, security keywords)
5. Determines if Tech Lead review is required or optional
6. Applies appropriate labels to the PR
7. Assigns primary Tech Lead for review (via comment mention)
8. Handles review state changes (approved, changes requested)
9. Manages re-review cycles when changes are pushed

**Complexity Thresholds:**
- Small PR (optional review): ≤5 files, ≤100 lines changed
- Protected paths: Always require review
- Security keywords: Always require review (auth, token, password, secret, permission, security)

#### `setup-tech-lead-labels.yml`

**Purpose:** Creates/updates all necessary labels for the system

**Triggers:**
- Manual dispatch: `workflow_dispatch`
- Push to main when tech-lead workflows change

**Labels Created:**

| Label | Color | Purpose | Blocks Merge |
|-------|-------|---------|--------------|
| `needs-tech-lead-review` | 🔴 Red | Tech Lead review required | ✅ Yes |
| `tech-lead-approved` | 🟢 Green | Approved by Tech Lead | ❌ No |
| `tech-lead-changes-requested` | 🟡 Yellow | Changes requested | ✅ Yes |
| `tech-lead-review-cycle` | 🔵 Blue | In review cycle | ℹ️ Info |
| `tech-lead:workflows-tech-lead` | 🟣 Purple | Workflows Tech Lead assigned | ℹ️ Info |
| `tech-lead:agents-tech-lead` | 🟣 Purple | Agents Tech Lead assigned | ℹ️ Info |
| `tech-lead:docs-tech-lead` | 🟣 Purple | Docs Tech Lead assigned | ℹ️ Info |
| `tech-lead:github-pages-tech-lead` | 🟣 Purple | GitHub Pages Tech Lead assigned | ℹ️ Info |

#### `tech-lead-feedback-handler.yml`

**Purpose:** Handles Tech Lead review feedback and updates

**Triggers:**
- Pull request review submitted
- Manual dispatch

**What it does:**
- Processes Tech Lead review submissions
- Updates labels based on review state
- Notifies relevant parties of review status
- Manages review iteration cycles

### 3. Supporting Scripts

#### `tools/match-pr-to-tech-lead.py`

**Purpose:** Matches PR files to Tech Lead agents

**Usage:**
```bash
python3 tools/match-pr-to-tech-lead.py <pr_number>
python3 tools/match-pr-to-tech-lead.py <pr_number> --check-complexity
```

**Output:**
```json
{
  "pr_number": "123",
  "total_files": 5,
  "tech_leads": [
    {
      "name": "workflows-tech-lead",
      "specialization": "workflows",
      "description": "GitHub Actions and workflow orchestration",
      "file_count": 3,
      "files": [".github/workflows/test.yml", ...]
    }
  ],
  "complexity": {
    "total_files": 5,
    "total_changes": 150,
    "touches_protected": true,
    "requires_review": true,
    "recommendation": "required"
  }
}
```

## Review Process Flow

### 1. PR Created/Updated

```
PR Opened/Synchronized
  ↓
tech-lead-review.yml triggered
  ↓
Check WIP markers → If WIP, skip review
  ↓
Get PR files
  ↓
Match files to Tech Leads
  ↓
Analyze complexity
  ↓
Apply labels
  ↓
Assign Tech Lead (if required)
```

### 2. Tech Lead Review States

#### Required Review
```
needs-tech-lead-review label added
  ↓
tech-lead:X label(s) added (identifies which Tech Lead)
  ↓
tech-lead-review-cycle label added
  ↓
Tech Lead assigned via comment mention
  ↓
Auto-merge BLOCKED until approval
```

#### Optional Review
```
tech-lead:X label(s) added
  ↓
No blocking labels
  ↓
Auto-merge can proceed without review
  ↓
Tech Lead notified but review is optional
```

### 3. Review Cycle

#### Approval Path
```
Tech Lead reviews PR
  ↓
Tech Lead approves
  ↓
tech-lead-review.yml triggered (on review submitted)
  ↓
needs-tech-lead-review label removed
  ↓
tech-lead-changes-requested label removed (if present)
  ↓
tech-lead-approved label added
  ↓
Auto-merge unblocked
```

#### Changes Requested Path
```
Tech Lead reviews PR
  ↓
Tech Lead requests changes
  ↓
tech-lead-review.yml triggered (on review submitted)
  ↓
tech-lead-changes-requested label added
  ↓
needs-tech-lead-review label maintained
  ↓
Auto-merge BLOCKED
  ↓
PR author/agent pushes changes
  ↓
tech-lead-review.yml triggered (on synchronize)
  ↓
Re-review request posted
  ↓
Tech Lead reviews again → Cycle continues
```

## Integration with Auto-Merge

The `auto-review-merge.yml` workflow checks Tech Lead labels before allowing merge:

**Blocking Conditions:**
- `needs-tech-lead-review` label present AND `tech-lead-approved` label absent
- `tech-lead-changes-requested` label present

**Merge Allowed:**
- No `needs-tech-lead-review` label (optional review)
- `tech-lead-approved` label present (required review completed)
- No `tech-lead-changes-requested` label

## Adding a New Tech Lead

To add a new Tech Lead agent:

### 1. Create Agent Definition

Create `.github/agents/your-tech-lead.md`:

```yaml
---
name: your-tech-lead
description: "Description of your specialization"
specialization: your-domain
personality: expertise-focused
tech_lead_for_paths:
  - path/pattern/**
  - another/path/**
responsibilities:
  - Review criteria 1
  - Review criteria 2
---

# Your Tech Lead Agent

[Agent description and guidelines]
```

### 2. Add Labels

Update `.github/workflows/setup-tech-lead-labels.yml`:

```yaml
# Add label creation
create_label \
  "tech-lead:your-tech-lead" \
  "Assigned to your-tech-lead for review" \
  "5319E7"
```

Also update the summary outputs to include your new Tech Lead.

### 3. Run Label Setup

Manually trigger the label setup workflow:
```bash
gh workflow run setup-tech-lead-labels.yml --repo owner/repo
```

### 4. Test

Create a test PR that touches your Tech Lead's paths and verify:
- Correct `tech-lead:your-tech-lead` label is applied
- Tech Lead is mentioned in the assignment comment
- Review process works end-to-end

## Verification and Testing

### Check System Status

```bash
# List all tech-lead labels
gh label list --repo owner/repo | grep "tech-lead"

# Check recent tech-lead-review runs
gh run list --workflow="tech-lead-review.yml" --limit 5

# View specific workflow run
gh run view <run_id>
```

### Test Tech Lead Matching

```bash
# Match a specific PR to Tech Leads
python3 tools/match-pr-to-tech-lead.py <pr_number>

# With complexity analysis
python3 tools/match-pr-to-tech-lead.py <pr_number> --check-complexity
```

### Manual Trigger

```bash
# Manually trigger review for a specific PR
gh workflow run tech-lead-review.yml \
  --repo owner/repo \
  --field pr_number=<pr_number>
```

## Troubleshooting

### Labels Not Applied

**Problem:** PR doesn't get tech-lead labels

**Checks:**
1. Does the PR touch paths covered by Tech Leads?
   ```bash
   python3 tools/match-pr-to-tech-lead.py <pr_number>
   ```
2. Are labels created in the repository?
   ```bash
   gh label list | grep "tech-lead"
   ```
3. Is the workflow running?
   ```bash
   gh run list --workflow="tech-lead-review.yml"
   ```

### Tech Lead Not Assigned

**Problem:** Labels applied but Tech Lead not mentioned

**Checks:**
1. Is the PR marked as draft? (Workflow skips draft PRs)
2. Does PR title have WIP marker? (Workflow skips WIP PRs)
3. Check workflow run logs for errors
4. Verify `requires_review` is true in complexity analysis

### Auto-Merge Not Blocked

**Problem:** PR merges without Tech Lead review

**Checks:**
1. Is `needs-tech-lead-review` label present?
2. Check `auto-review-merge.yml` workflow configuration
3. Verify label names match exactly (case-sensitive)

### Review Not Detected

**Problem:** Tech Lead approves but labels don't update

**Checks:**
1. Is Tech Lead reviewer listed in CODEOWNERS or has write access?
2. Check `tech-lead-review.yml` runs for `pull_request_review` trigger
3. Verify workflow has `pull-requests: write` permission

## Best Practices

### For Tech Leads

1. **Review Checklist:** Follow the criteria in your agent definition
2. **Clear Feedback:** Provide actionable, specific comments
3. **Timely Response:** Review within 24-48 hours when possible
4. **Approve or Request Changes:** Use GitHub's review system (not just comments)

### For PR Authors

1. **Remove WIP:** Take PR out of draft and remove WIP markers when ready
2. **Address Feedback:** Respond to all change requests
3. **Request Re-review:** Explicitly request re-review after addressing feedback
4. **Wait for Approval:** Don't bypass Tech Lead review for protected paths

### For System Maintenance

1. **Keep Labels Updated:** Run `setup-tech-lead-labels.yml` after adding Tech Leads
2. **Monitor Workflow Runs:** Check for failures or warnings
3. **Update Documentation:** Keep this README in sync with changes
4. **Test Changes:** Use manual trigger to test before merging workflow updates

## Architecture Decisions

### Why Path-Based Assignment?

Path-based assignment ensures:
- Objective, automatic assignment (no human bias)
- Coverage based on actual expertise areas
- Scalable to many Tech Leads
- Clear ownership of code areas

### Why Label-Based State Management?

Labels provide:
- Visible state in PR UI
- Easy filtering and searching
- Integration with other workflows
- Queryable via API
- Persistent across PR lifecycle

### Why Comment-Based Assignment?

Comment mentions:
- Trigger GitHub notifications
- Are visible in PR timeline
- Don't require GraphQL mutations
- Are simpler to implement
- Work with any GitHub account type

## Future Enhancements

Potential improvements:

1. **GraphQL Assignment:** Use GraphQL API to formally assign Tech Leads as reviewers
2. **Review Time Tracking:** Track time from assignment to review completion
3. **Escalation:** Auto-escalate if review not done within SLA
4. **Review Quality Metrics:** Track Tech Lead review thoroughness
5. **Multi-Tier Review:** Require multiple Tech Leads for complex changes
6. **Review Templates:** Provide Tech Lead-specific review checklists

## Related Documentation

- [Agent System Quick Start](/AGENT_QUICKSTART.md)
- [Workflow Documentation](/docs/WORKFLOWS.md)
- [Custom Agents Directory](/.github/agents/README.md)
- [Auto-Review-Merge Workflow](/docs/AUTO_REVIEW_MERGE.md)

---

*🤖 Maintained by **@workflows-tech-lead***  
*Last Updated: 2025-11-20*
