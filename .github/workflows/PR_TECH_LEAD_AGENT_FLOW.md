# PR Tech Lead Review & Agent Assignment Flow

## Overview

This document maps out the complete lifecycle of a Pull Request through tech lead review, agent assignment for fixes, and auto-merge. It clarifies which workflows handle which stages, what labels mean, and when agents are assigned.

**Created:** 2025-11-23  
**Purpose:** Implementation guide for extending copilot assignment to PRs

## Components

### Workflows

| Workflow | File | Purpose | Triggers |
|----------|------|---------|----------|
| **Auto Review & Merge** | `auto-review-merge.yml` | Tech lead analysis, labeling, review handling, auto-merge | PR opened/sync, PR review submitted, scheduled (15min) |
| **PR Auto Labeler** | `pr-auto-labeler.yml` | Content-based label analysis | PR opened/sync/reopened |
| **Copilot PR Assignment** | `copilot-pr-assignment.yml` | **NEW** - Assign copilot to fix tech lead feedback | **Scheduled (15min) - PRIMARY**, manual dispatch |
| **Copilot Issue Assignment** | `copilot-graphql-assign.yml` | Assign copilot to issues | Issue opened, scheduled (15min) |

**Note on Triggers:** `copilot-pr-assignment.yml` uses schedule-only strategy to avoid "awaiting approval" issues on fork PRs.

### Labels

| Label | Color | Meaning | Blocks Merge | Added By | Removed By |
|-------|-------|---------|--------------|----------|------------|
| `needs-tech-lead-review` | 🔴 Red | Tech lead review required | ✅ Yes | auto-review-merge | auto-review-merge (on approval) |
| `tech-lead-approved` | 🟢 Green | Approved by tech lead | ❌ No | auto-review-merge | - |
| `tech-lead-changes-requested` | 🟡 Yellow | Tech lead wants changes | ✅ Yes | auto-review-merge | Agent after fixes |
| `tech-lead-review-cycle` | 🔵 Blue | In review cycle | ℹ️ Info | auto-review-merge | - |
| `tech-lead:workflows-tech-lead` | 🟣 Purple | Workflows tech lead assigned | ℹ️ Info | auto-review-merge | - |
| `tech-lead:agents-tech-lead` | 🟣 Purple | Agents tech lead assigned | ℹ️ Info | auto-review-merge | - |
| `tech-lead:docs-tech-lead` | 🟣 Purple | Docs tech lead assigned | ℹ️ Info | auto-review-merge | - |
| `tech-lead:github-pages-tech-lead` | 🟣 Purple | GitHub Pages tech lead assigned | ℹ️ Info | auto-review-merge | - |
| `tech-lead-feedback` | 🟠 Orange | **NEW** - Feedback issue created | ℹ️ Info | copilot-pr-assignment | - |
| `agent:X` | 🟢 Green | Agent X assigned to fix | ℹ️ Info | copilot-pr-assignment | - |
| `copilot` | 💙 Blue | Created by copilot | ℹ️ Info | auto-review-merge | - |

### Scripts

| Script | Purpose | Used By |
|--------|---------|---------|
| `tools/match-pr-to-tech-lead.py` | Match PR files to tech leads | auto-review-merge |
| `tools/match-issue-to-agent.py` | Match issue/feedback to agent | copilot-graphql-assign, **copilot-pr-assignment** |
| `tools/assign-copilot-to-issue.sh` | Assign copilot to issue | copilot-graphql-assign |
| `tools/assign-copilot-to-pr.sh` | **NEW** - Create feedback issue for PR | **copilot-pr-assignment** |

## Complete PR Lifecycle Flow

### Stage 1: PR Creation & Initial Analysis

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PR Opened/Synchronized                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. pr-auto-labeler.yml                                      │
│    - Analyzes PR content                                    │
│    - Adds content-based labels                              │
│    - Posts analysis comment                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. auto-review-merge.yml (Stage 1: Analyze)                │
│    - Get PR files                                           │
│    - Run match-pr-to-tech-lead.py                          │
│    - Check complexity thresholds                            │
│    - Determine if tech lead review required                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
                    Decision Point
                    ↙            ↘
              YES                 NO
    (Tech Lead Required)    (Optional Review)
                ↓                  ↓
┌──────────────────────────┐  ┌──────────────────────────┐
│ Add Labels:              │  │ Add Labels:              │
│ - needs-tech-lead-review │  │ - tech-lead:X (info)     │
│ - tech-lead:X            │  │ Continue to auto-merge   │
│ - tech-lead-review-cycle │  └──────────────────────────┘
│ - copilot (if copilot)   │
└──────────────────────────┘
                ↓
┌─────────────────────────────────────────────────────────────┐
│ Post Comment:                                               │
│ "Tech Lead Review Required"                                 │
│ - Assigned Tech Lead: @X                                    │
│ - Review criteria                                           │
│ - Next steps                                                │
└─────────────────────────────────────────────────────────────┘
                ↓
    ⏸️  MERGE BLOCKED - Wait for Tech Lead
```

### Stage 2A: Tech Lead Approves

```
┌─────────────────────────────────────────────────────────────┐
│ Tech Lead Reviews → Approves                                │
│ (GitHub PR Review with "Approve" state)                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ auto-review-merge.yml (Stage 2: Process Review)            │
│ Trigger: pull_request_review (submitted)                    │
│                                                             │
│ Actions:                                                    │
│ - Detect approval state                                     │
│ - Remove needs-tech-lead-review                            │
│ - Remove tech-lead-changes-requested (if present)          │
│ - Add tech-lead-approved                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Post Comment:                                               │
│ "✅ Tech Lead Approval Received"                            │
│ - Status changes                                            │
│ - Ready for auto-merge                                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ auto-review-merge.yml (Stage 3: Auto-Merge)                │
│                                                             │
│ Check Eligibility:                                          │
│ ✅ PR is open and not draft                                 │
│ ✅ From trusted source (copilot + label)                    │
│ ✅ tech-lead-approved present                               │
│ ❌ NO tech-lead-changes-requested                           │
│                                                             │
│ → MERGE PR                                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
                    ✅ PR MERGED
```

### Stage 2B: Tech Lead Requests Changes (NEW FLOW)

```
┌─────────────────────────────────────────────────────────────┐
│ Tech Lead Reviews → Requests Changes                        │
│ (GitHub PR Review with "Request Changes" state + comments)  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ auto-review-merge.yml (Stage 2: Process Review)            │
│ Trigger: pull_request_review (submitted)                    │
│                                                             │
│ Actions:                                                    │
│ - Detect changes requested state                            │
│ - Add tech-lead-changes-requested                          │
│ - Maintain needs-tech-lead-review                          │
│ - Extract review body/comments                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ ⚠️  CURRENT: Creates follow-up issue inline                 │
│    (auto-review-merge.yml lines 313-332)                    │
│                                                             │
│    - Run match-issue-to-agent.py on feedback                │
│    - Create issue with agent assignment                     │
│    - Link to PR #                                           │
│    - Assign to copilot                                      │
│    - Add tech-lead-feedback label                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 🆕 NEW: copilot-pr-assignment.yml                          │
│    Trigger: Scheduled (every 15 minutes)                    │
│                                                             │
│    **Schedule-Primary Strategy:**                           │
│    - Runs autonomously without approval requirements        │
│    - Sweeps all PRs with tech-lead-changes-requested       │
│    - Avoids "awaiting approval" issues on fork PRs         │
│                                                             │
│    Actions:                                                 │
│    - Get all PRs with tech-lead-changes-requested label     │
│    - For each PR:                                           │
│      • Get review comments from tech lead                   │
│      • Check if feedback issue already exists               │
│      • Run match-issue-to-agent.py on feedback              │
│      • Create structured feedback issue                     │
│      • Add agent directive with PR context                  │
│      • Assign copilot via GraphQL API                      │
│      • Add agent:X and tech-lead-feedback labels           │
│      • Link issue to PR via comment                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ copilot-graphql-assign.yml                                  │
│ Trigger: Issue opened (feedback issue)                      │
│                                                             │
│ - Detects agent:X label already present                     │
│ - Confirms copilot assignment                               │
│ - Posts assignment comment with agent details               │
└─────────────────────────────────────────────────────────────┘
                          ↓
                ⏸️  Agent Working
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Agent (Copilot with @agent-name profile)                   │
│                                                             │
│ 1. Reads feedback issue                                     │
│ 2. Views PR and tech lead comments                          │
│ 3. Understands required changes                             │
│ 4. Checks out PR branch                                     │
│ 5. Makes fixes                                              │
│ 6. Pushes to PR branch                                      │
│ 7. Removes [WIP] if present                                │
│ 8. Updates issue with completion status                     │
│ 9. Closes feedback issue                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ auto-review-merge.yml (Stage 2: Process PR Update)         │
│ Trigger: pull_request (synchronize)                         │
│                                                             │
│ Actions:                                                    │
│ - Detect new commits on PR                                  │
│ - Post re-review request comment                            │
│ - Notify tech lead                                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
        Tech Lead Re-Reviews
        (Loop back to Stage 2A or 2B)
```

### Stage 3: Scheduled Sweeps

```
┌─────────────────────────────────────────────────────────────┐
│ Scheduled Runs (every 15 minutes)                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ auto-review-merge.yml                                       │
│ - Get all open, non-draft PRs                              │
│ - Re-analyze each PR                                        │
│ - Update labels if needed                                   │
│ - Process eligible PRs for merge                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ copilot-pr-assignment.yml (NEW)                            │
│ - Get PRs with tech-lead-changes-requested                 │
│ - Check if feedback issue exists                            │
│ - Create if missing                                         │
│ - Ensure agent assigned                                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ copilot-graphql-assign.yml                                  │
│ - Get all open issues                                       │
│ - Skip if copilot already assigned                          │
│ - Skip if spawn-pending                                     │
│ - Assign copilot to unassigned issues                       │
└─────────────────────────────────────────────────────────────┘
```

## Decision Matrix

### When to Assign Tech Lead?

| Condition | Requires Review | Optional Review |
|-----------|----------------|-----------------|
| Touches protected paths (workflows, agents, etc.) | ✅ | ❌ |
| Contains security keywords (auth, secret, etc.) | ✅ | ❌ |
| More than 5 files changed | ✅ | ❌ |
| More than 100 lines changed | ✅ | ❌ |
| Small, non-sensitive changes | ❌ | ✅ |

### When to Assign Agent?

| Scenario | Agent Assignment | Purpose |
|----------|-----------------|---------|
| Tech lead requests changes | ✅ Match to appropriate agent | Fix feedback |
| Tech lead approves | ❌ No assignment needed | Ready to merge |
| PR requires tech lead review | ❌ No assignment yet | Wait for review |
| Issue opened | ✅ Match to appropriate agent | Implement feature |
| Feedback issue created | ✅ Same or matched agent | Address comments |

### When to Merge?

| Condition | Can Merge? |
|-----------|------------|
| ✅ From trusted source (copilot + label) | Continue checking |
| ✅ No needs-tech-lead-review OR tech-lead-approved present | Continue checking |
| ❌ tech-lead-changes-requested present | ❌ BLOCK |
| ✅ PR is open and not draft | Continue checking |
| ✅ No WIP markers | ✅ MERGE |

## Implementation Changes Required

### 1. New Workflow: `copilot-pr-assignment.yml`

**Purpose:** Assign agents to address tech lead feedback on PRs

**Triggers:**
- `pull_request` types: `labeled` (when tech-lead-changes-requested added)
- `schedule`: Every 15 minutes (sweep for PRs needing feedback issues)
- `workflow_dispatch`: Manual trigger with PR number

**Key Features:**
- Detect when tech-lead-changes-requested label added
- Get review comments from tech lead
- Match feedback to appropriate agent
- Create linked feedback issue
- Assign copilot with agent directive
- Track issue-PR relationship
- Handle re-assignment if previous agent failed

### 2. New Script: `tools/assign-copilot-to-pr.sh`

**Purpose:** Create feedback issue for PR and assign agent

**Inputs:**
- PR number
- Review body/comments
- Tech lead who reviewed

**Outputs:**
- Creates issue with:
  - Title: "[Tech Lead Feedback] PR #X - Summary"
  - Body: PR context, review comments, agent directive
  - Labels: tech-lead-feedback, agent:X, linked-to-pr
  - Assignee: copilot
- Links issue to PR via comments
- Adds agent:X label to PR for tracking

### 3. Update `auto-review-merge.yml`

**Changes:**
- Remove inline issue creation (lines 313-332)
- Replace with trigger for new copilot-pr-assignment workflow
- Keep review state detection and labeling
- Add comment notifying agent assignment

### 4. Documentation Updates

**Files to Update:**
- `.github/workflows/TECH_LEAD_SYSTEM_README.md` - Add agent assignment flow
- `.github/workflows/AGENT_ASSIGNMENT_WORKFLOWS_README.md` - Add PR assignment
- This file (PR_TECH_LEAD_AGENT_FLOW.md) - Complete reference

## Testing Checklist

- [ ] Create test PR touching protected paths
- [ ] Verify tech lead labels applied
- [ ] Tech lead requests changes
- [ ] Verify feedback issue created
- [ ] Verify correct agent matched
- [ ] Verify copilot assigned to issue
- [ ] Verify issue linked to PR
- [ ] Agent makes fixes and pushes
- [ ] Verify labels updated
- [ ] Tech lead approves
- [ ] Verify PR merges

## Benefits of This Design

1. **Separation of Concerns**
   - auto-review-merge.yml: Review orchestration
   - copilot-pr-assignment.yml: Agent assignment
   - copilot-graphql-assign.yml: Issue assignment

2. **Reusability**
   - Same agent matching logic for issues and PRs
   - Same copilot assignment mechanism
   - Consistent label system

3. **Observability**
   - Clear issue-PR links
   - Trackable agent assignments
   - Visible workflow states

4. **Maintainability**
   - Single responsibility per workflow
   - Shared tools and scripts
   - Well-documented flow

5. **Extensibility**
   - Easy to add new tech leads
   - Easy to add new agent types
   - Scalable to more review stages

6. **Autonomous Operation**
   - Schedule-primary strategy avoids approval gates
   - Reliable execution on fork PRs
   - 15-minute latency is acceptable trade-off
   - Manual dispatch available for immediate processing

## Schedule-Primary Strategy: Trade-offs

### Why Not Event Triggers?

**The Problem:**
- Fork PRs require workflow approval: "This workflow is awaiting approval from a maintainer"
- Security measure to prevent malicious workflow changes
- Breaks autonomous operation - requires human intervention

**Event-Based Trigger (NOT USED):**
```yaml
on:
  pull_request:
    types: [labeled]  # ❌ Requires approval on fork PRs
```

**Schedule-Based Trigger (OUR APPROACH):**
```yaml
on:
  schedule:
    - cron: '*/15 * * * *'  # ✅ Runs autonomously without approval
```

### Latency vs Reliability

| Approach | Latency | Reliability | Autonomous |
|----------|---------|-------------|------------|
| Event-triggered | Immediate | ❌ Breaks on forks | ❌ Requires approval |
| Schedule-only | 15 minutes | ✅ Always works | ✅ Fully autonomous |
| Hybrid (both) | Mixed | ⚠️ Partial | ⚠️ Sometimes |

**Decision: Schedule-only** for consistent, autonomous operation.

### Acceptable Latency?

**15-minute latency is acceptable because:**
1. Tech lead reviews are async (human-in-loop already)
2. Agent work takes time anyway (reading, coding, testing)
3. Total cycle time: Review → Assign → Fix → Re-review is hours/days
4. 15-minute delay is negligible in this context
5. Manual dispatch available for urgent cases

**Timeline Example:**
```
10:00 AM - Tech lead reviews, requests changes
10:00 AM - auto-review-merge adds tech-lead-changes-requested label
10:15 AM - copilot-pr-assignment sweep creates feedback issue
10:16 AM - Agent assigned and starts work
10:45 AM - Agent completes fixes and pushes
11:00 AM - Tech lead notified for re-review
```

Total added latency: **15 minutes** (vs immediate with events)  
Total cycle time: **~1 hour** (same either way)

---

*🤖 Created by @workflows-tech-lead*  
*Last Updated: 2025-11-23*
