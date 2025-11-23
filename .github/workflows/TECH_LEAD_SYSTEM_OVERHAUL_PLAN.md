# Tech Lead System Overhaul Plan

**Created by:** @support-master  
**Date:** 2025-11-23  
**Status:** PROPOSAL - Awaiting Review

## Executive Summary

The Tech Lead Review System has evolved into an **overly complex and fragmented** architecture with multiple workflows, conflicting state management, and duplicated functionality. This document proposes a comprehensive overhaul to simplify the system while maintaining its core value: **autonomous tech lead review and agent-based feedback resolution**.

### Key Problems Identified

1. **Workflow Fragmentation**: 3 workflows (`copilot-graphql-assign.yml`, `auto-review-merge.yml`, `copilot-pr-assignment.yml`) with overlapping responsibilities
2. **Label Complexity**: 8+ tech-lead labels creating confusing state management
3. **Schedule-Based Latency**: Multiple scheduled sweeps (7min, 15min) adding unnecessary delays
4. **Duplicate Logic**: Agent matching and assignment duplicated across workflows
5. **Broken Feedback Loop**: Complex cycle between tech lead review → agent assignment → fixes → re-review
6. **Mixed Triggers**: Combination of events, schedules, and manual dispatch creating unpredictable behavior

### Proposed Solution

**Simplify to 2 workflows with clear responsibilities:**

1. **`copilot-agent-assignment.yml`** - Unified agent assignment for both issues and PRs
2. **`auto-review-merge.yml`** - Simplified PR analysis and auto-merge (remove agent assignment logic)

**Reduce labels to essential state indicators:**
- Keep: `needs-tech-lead-review`, `tech-lead-approved`, `tech-lead-changes-requested`
- Remove: `tech-lead-review-cycle`, separate `tech-lead:X` labels
- Simplify: Consolidate agent tracking with single `assigned-agent` label

**Move to event-driven architecture:**
- Replace scheduled sweeps with direct event triggers
- Handle fork PR approvals with proper error handling
- Use fallback manual dispatch for edge cases

---

## Current System Architecture

### Workflow Analysis

#### 1. `copilot-graphql-assign.yml` (Automation: Copilot Assignment)

**Purpose:** Assign Copilot to new and unassigned issues

**Triggers:**
- `issues` (opened)
- `schedule` (every 15 minutes)
- `workflow_dispatch` (manual)
- `workflow_run` (after other workflows)

**What it does:**
- Discovers open, unassigned issues
- Matches issues to custom agents using `match-issue-to-agent.py`
- Assigns Copilot with agent directive
- Posts assignment comment with agent details

**Problems:**
- 15-minute scheduled latency
- Duplicates agent matching logic used in PR assignment
- Doesn't handle PRs (separate workflow needed)
- Over-engineered with multiple trigger types

#### 2. `auto-review-merge.yml` (Automation: Auto Review & Merge)

**Purpose:** Tech lead analysis, review handling, and auto-merge

**Triggers:**
- `pull_request` (opened, synchronize, ready_for_review, reopened)
- `pull_request_review` (submitted)
- `schedule` (every 15 minutes)
- `workflow_dispatch` (manual)

**What it does:**
- Stage 1: Analyze PRs, match to tech leads, apply labels
- Stage 2: Process reviews (approval/changes requested)
- Stage 3: Auto-merge eligible PRs

**Problems:**
- Does TOO MUCH - analysis + review + merge in one workflow
- Complex 3-stage matrix job architecture
- NOTE on line 310 says feedback issue creation handled by other workflow (but still has inline code!)
- 15-minute scheduled sweep adds latency
- Mixing PR analysis with merge logic

#### 3. `copilot-pr-assignment.yml` (Automation: Copilot PR Assignment)

**Purpose:** Create feedback issues for tech lead change requests

**Triggers:**
- `schedule` (every 7 minutes) - PRIMARY
- `workflow_dispatch` (manual)
- **NO pull_request triggers** (to avoid "awaiting approval" on forks)

**What it does:**
- Sweeps PRs with `tech-lead-changes-requested` label
- Gets review comments from tech lead
- Checks for existing feedback issues (prevents duplicates)
- Matches feedback to agent using `match-issue-to-agent.py`
- Creates structured feedback issue
- Assigns Copilot with agent directive
- Links issue to PR via comments

**Problems:**
- 7-minute scheduled latency
- Schedule-only strategy is workaround for fork PR approval issues
- Duplicates agent matching from copilot-graphql-assign
- Complex proactive vs reactive review logic
- Sweeps PRs with `tech-lead:X` labels creating proactive reviews

### Label System

#### State Management Labels

| Label | Color | Purpose | Blocks Merge | Added By | Removed By |
|-------|-------|---------|--------------|----------|------------|
| `needs-tech-lead-review` | 🔴 Red | Review required | ✅ Yes | auto-review-merge | auto-review-merge |
| `tech-lead-approved` | 🟢 Green | Approved | ❌ No | auto-review-merge | - |
| `tech-lead-changes-requested` | 🟡 Yellow | Changes needed | ✅ Yes | auto-review-merge | auto-review-merge |
| `tech-lead-review-cycle` | 🔵 Blue | In review | ℹ️ Info | auto-review-merge | - |

#### Tech Lead Assignment Labels

| Label | Purpose | Problem |
|-------|---------|---------|
| `tech-lead:workflows-tech-lead` | Workflows assigned | Too specific |
| `tech-lead:agents-tech-lead` | Agents assigned | Duplicates info in comments |
| `tech-lead:docs-tech-lead` | Docs assigned | Could use single label |
| `tech-lead:github-pages-tech-lead` | Pages assigned | Creates label sprawl |

#### Agent Tracking Labels

| Label | Purpose | Problem |
|-------|---------|---------|
| `tech-lead-feedback` | Feedback issue created | Overlaps with linked-to-pr |
| `agent:X` | Agent X assigned | Generic, better pattern exists |
| `copilot` | Created by copilot | Useful, keep this |
| `linked-to-pr` | Issue linked to PR | Could be inferred |

### State Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       PR Opened/Updated                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          auto-review-merge.yml (Stage 1: Analyze)              │
│  - Match PR files to tech leads                                │
│  - Check complexity                                             │
│  - Apply labels: needs-tech-lead-review, tech-lead:X, etc.     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Tech Lead Reviews
                    ↙               ↘
                APPROVED        CHANGES REQUESTED
                    ↓                   ↓
        ┌───────────────────┐  ┌────────────────────────────┐
        │ auto-review-merge │  │ auto-review-merge          │
        │ - Remove needs-   │  │ - Add tech-lead-changes-   │
        │   tech-lead       │  │   requested                │
        │ - Add tech-lead-  │  │ - Keep needs-tech-lead     │
        │   approved        │  └────────────────────────────┘
        └───────────────────┘              ↓
                ↓              ┌────────────────────────────┐
        ┌───────────────────┐  │ copilot-pr-assignment      │
        │ auto-review-merge │  │ (7min sweep)               │
        │ (Stage 3: Merge)  │  │ - Create feedback issue    │
        └───────────────────┐  │ - Match to agent           │
                ↓              │ - Assign Copilot           │
            ✅ MERGED          │ - Link to PR               │
                              └────────────────────────────┘
                                          ↓
                              ┌────────────────────────────┐
                              │ copilot-graphql-assign     │
                              │ - Confirm assignment       │
                              │ - Post comment             │
                              └────────────────────────────┘
                                          ↓
                              ┌────────────────────────────┐
                              │ Agent makes fixes          │
                              │ - Pushes to PR branch      │
                              │ - Updates issue            │
                              └────────────────────────────┘
                                          ↓
                              ┌────────────────────────────┐
                              │ auto-review-merge          │
                              │ - Detects synchronize      │
                              │ - Requests re-review       │
                              └────────────────────────────┘
                                          ↓
                                Tech Lead Re-Reviews (loop)
```

### Pain Points

1. **Latency**: 7-15 minute delays between state changes due to scheduled sweeps
2. **Complexity**: Multiple workflows touching same PRs creates race conditions
3. **Label Sprawl**: 8+ labels per PR makes state hard to understand
4. **Duplicate Logic**: Agent matching code duplicated 2x
5. **Broken Links**: Comments link issues to PRs but no structured tracking
6. **Fork PR Issues**: Schedule-only workaround for "awaiting approval" problem
7. **Proactive Reviews**: copilot-pr-assignment creates review requests even when no feedback exists (lines 226-268)
8. **Inline Code**: auto-review-merge says feedback handled elsewhere but has inline issue creation code (commented out?)

---

## Proposed Overhaul

### Goals

1. **Simplify**: Reduce from 3 workflows to 2 with clear separation of concerns
2. **Speed**: Move from scheduled sweeps to event-driven architecture
3. **Unify**: Consolidate agent assignment logic into single workflow
4. **Clarify**: Reduce label count and simplify state management
5. **Reliability**: Handle edge cases (fork PRs, timeouts) gracefully

### New Architecture

#### Workflow 1: `copilot-agent-assignment.yml` (NEW - Unified)

**Purpose:** **Single workflow for all agent assignment** (issues AND PRs)

**Triggers:**
- `issues` (opened, labeled)
- `pull_request` (labeled) - when `tech-lead-changes-requested` added
- `schedule` (every 30 minutes) - safety net for missed events
- `workflow_dispatch` (manual with issue/PR number)

**Responsibilities:**
1. **For Issues:**
   - Match issue to agent using `match-issue-to-agent.py`
   - Assign Copilot with agent directive
   - Post assignment comment
   - Add `agent:X` label

2. **For PRs (tech lead feedback):**
   - Triggered when `tech-lead-changes-requested` label added
   - Get review comments from tech lead
   - Check for existing feedback issue
   - Create feedback issue with PR context
   - Match feedback to agent
   - Assign Copilot with agent directive
   - Link issue to PR
   - Add `agent:X` label to both issue and PR

**Benefits:**
- **Unified logic**: One agent matcher, one assignment flow
- **Event-driven**: No 7-15 minute latency
- **Simpler**: One workflow to maintain
- **Fallback**: Schedule still catches missed events

**Implementation:**
```yaml
name: "Automation: Unified Agent Assignment"

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [labeled]
  schedule:
    - cron: '*/30 * * * *'  # Safety net only
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number'
        required: false
      pr_number:
        description: 'PR number'
        required: false

jobs:
  assign-agent:
    runs-on: ubuntu-latest
    steps:
      - name: Determine assignment type
        id: type
        run: |
          if [ "${{ github.event_name }}" = "issues" ]; then
            echo "type=issue" >> $GITHUB_OUTPUT
            echo "number=${{ github.event.issue.number }}" >> $GITHUB_OUTPUT
          elif [ "${{ github.event_name }}" = "pull_request" ]; then
            echo "type=pr" >> $GITHUB_OUTPUT
            echo "number=${{ github.event.pull_request.number }}" >> $GITHUB_OUTPUT
          elif [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            if [ -n "${{ inputs.issue_number }}" ]; then
              echo "type=issue" >> $GITHUB_OUTPUT
              echo "number=${{ inputs.issue_number }}" >> $GITHUB_OUTPUT
            elif [ -n "${{ inputs.pr_number }}" ]; then
              echo "type=pr" >> $GITHUB_OUTPUT
              echo "number=${{ inputs.pr_number }}" >> $GITHUB_OUTPUT
            fi
          else
            echo "type=sweep" >> $GITHUB_OUTPUT
          fi
      
      - name: Assign to issue
        if: steps.type.outputs.type == 'issue'
        run: |
          # Existing copilot-graphql-assign logic
          ./tools/assign-copilot-to-issue.sh ${{ steps.type.outputs.number }}
      
      - name: Create feedback issue for PR
        if: steps.type.outputs.type == 'pr'
        run: |
          # Existing copilot-pr-assignment logic
          # But triggered by event, not schedule sweep
          ./tools/create-pr-feedback-issue.sh ${{ steps.type.outputs.number }}
      
      - name: Sweep unassigned (safety net)
        if: steps.type.outputs.type == 'sweep'
        run: |
          # Minimal sweep for missed events only
          ./tools/sweep-unassigned.sh
```

#### Workflow 2: `auto-review-merge.yml` (SIMPLIFIED)

**Purpose:** **PR tech lead analysis and auto-merge ONLY**

**Triggers:**
- `pull_request` (opened, synchronize, ready_for_review, reopened)
- `pull_request_review` (submitted)
- `schedule` (every 30 minutes) - for merge sweep only
- `workflow_dispatch` (manual)

**Responsibilities:**
1. **PR Analysis:**
   - Match PR files to tech leads
   - Check complexity thresholds
   - Apply state labels: `needs-tech-lead-review`, `tech-lead:X`
   - Post tech lead assignment comment

2. **Review Handling:**
   - Detect approval → update labels to `tech-lead-approved`
   - Detect changes requested → update labels to `tech-lead-changes-requested`
   - **DO NOT create issues** (delegate to copilot-agent-assignment)
   - Post status update comments

3. **Auto-Merge:**
   - Check merge eligibility
   - Verify tech lead approval status
   - Merge if all criteria met

**Benefits:**
- **Focused**: Does ONE thing well (PR lifecycle management)
- **No agent logic**: Assignment delegated to unified workflow
- **Simpler**: Remove complex issue creation code
- **Reliable**: Still handles core review flow

**Changes from current:**
- **REMOVE**: Lines 313-332 inline feedback issue creation
- **REMOVE**: Stage 2 issue creation logic
- **ADD**: Comment on PR to trigger agent assignment workflow
- **SIMPLIFY**: Remove proactive review logic (copilot-pr-assignment handles this)

#### Workflow 3: `copilot-graphql-assign.yml` (DEPRECATED)

**Status:** **REMOVE** - Functionality moved to unified workflow

**Migration:**
- All issue assignment → `copilot-agent-assignment.yml`
- GraphQL API calls → Moved to shared script
- Schedule sweeps → 30min safety net in unified workflow

### Label Simplification

#### Keep (Essential State)

| Label | Purpose | When Applied |
|-------|---------|--------------|
| `needs-tech-lead-review` | Blocks merge until approved | PR touches protected paths |
| `tech-lead-approved` | Allows merge | Tech lead approves |
| `tech-lead-changes-requested` | Blocks merge, triggers agent | Tech lead requests changes |
| `copilot` | PR created by copilot | PR author is copilot |

#### Consolidate (Tech Lead Assignment)

**REMOVE individual labels:**
- ❌ `tech-lead:workflows-tech-lead`
- ❌ `tech-lead:agents-tech-lead`
- ❌ `tech-lead:docs-tech-lead`
- ❌ `tech-lead:github-pages-tech-lead`

**REPLACE with single label + comment:**
- ✅ `tech-lead-required` (generic label)
- ✅ Comment identifies which tech lead(s): "@workflows-tech-lead please review"

**Rationale:**
- Labels indicate STATE, not IDENTITY
- Comments indicate ASSIGNMENT
- Reduces label sprawl from 4+ to 1
- Tech lead identity still visible in comment

#### Consolidate (Agent Tracking)

**REMOVE specific labels:**
- ❌ `agent:X` (too many possible values)
- ❌ `tech-lead-feedback` (redundant with issue link)
- ❌ `linked-to-pr` (can be inferred)

**REPLACE with:**
- ✅ `assigned-agent` (single label indicating agent assigned)
- ✅ Comment with agent name: "**@engineer-master** has been assigned"
- ✅ Issue link in PR comment

**Rationale:**
- Label indicates STATE (agent assigned), not IDENTITY
- Comment and issue link provide specifics
- Reduces dynamic label creation

#### Remove (Redundant)

- ❌ `tech-lead-review-cycle` - State obvious from other labels

### Event-Driven Architecture

#### Current (Schedule-Based)

```
PR labeled with tech-lead-changes-requested
   ↓
   ⏱️ Wait 7 minutes for copilot-pr-assignment sweep
   ↓
Create feedback issue
   ↓
   ⏱️ Wait 15 minutes for copilot-graphql-assign sweep
   ↓
Assign agent

Total latency: ~22 minutes
```

#### Proposed (Event-Driven)

```
PR labeled with tech-lead-changes-requested
   ↓
   ⚡ Immediate: copilot-agent-assignment triggered
   ↓
Create feedback issue + assign agent in one step

Total latency: ~1 minute
```

#### Handling Fork PRs

**Problem:** Event triggers on fork PRs require maintainer approval ("awaiting approval from maintainer")

**Solution: Graceful degradation**

```yaml
- name: Create feedback issue
  id: create_issue
  continue-on-error: true  # Don't fail workflow if approval needed
  run: |
    # Try to create issue
    issue_number=$(gh issue create ...)
    echo "issue_number=${issue_number}" >> $GITHUB_OUTPUT

- name: Fallback comment if issue creation blocked
  if: steps.create_issue.outcome == 'failure'
  run: |
    gh pr comment ${{ github.event.pull_request.number }} --body \
      "⚠️ **Awaiting Maintainer Approval**
      
      This PR requires changes, but issue creation needs approval.
      A maintainer will need to:
      1. Approve the workflow run
      2. Manually trigger feedback issue creation
      
      Or address the feedback directly in this PR."
```

**Fallback: Schedule still runs every 30min**
- Catches missed events from failed triggers
- Creates issues if approval now granted
- Safety net for edge cases

---

## Migration Plan

### Phase 1: Preparation (Week 1)

#### 1.1 Create Unified Workflow
- [ ] Create `.github/workflows/copilot-agent-assignment.yml`
- [ ] Extract shared logic to `tools/assign-agent.sh`
- [ ] Test issue assignment
- [ ] Test PR feedback assignment
- [ ] Test schedule sweep

#### 1.2 Update Labels
- [ ] Run label cleanup script
- [ ] Remove tech-lead:X labels from existing PRs
- [ ] Add generic `tech-lead-required` label
- [ ] Update label documentation

#### 1.3 Create Shared Tools
- [ ] Consolidate `tools/assign-copilot-to-issue.sh` and PR assignment into `tools/assign-agent.sh`
- [ ] Create `tools/create-pr-feedback-issue.sh`
- [ ] Create `tools/sweep-unassigned.sh`
- [ ] Test all scripts

### Phase 2: Workflow Updates (Week 2)

#### 2.1 Update auto-review-merge.yml
- [ ] Remove inline feedback issue creation (lines 313-332)
- [ ] Update to use generic `tech-lead-required` label
- [ ] Add comment trigger for agent assignment
- [ ] Test review flow end-to-end

#### 2.2 Deploy Unified Workflow
- [ ] Deploy `copilot-agent-assignment.yml`
- [ ] Monitor for 48 hours with both old and new running
- [ ] Verify no issues missed
- [ ] Verify no duplicate assignments

#### 2.3 Deprecate Old Workflows
- [ ] Disable `copilot-graphql-assign.yml` triggers
- [ ] Disable `copilot-pr-assignment.yml` triggers
- [ ] Keep files for 1 week as reference
- [ ] Delete after verification

### Phase 3: Documentation (Week 3)

#### 3.1 Update System Docs
- [ ] Update `TECH_LEAD_SYSTEM_README.md`
- [ ] Update `PR_TECH_LEAD_AGENT_FLOW.md`
- [ ] Create `AGENT_ASSIGNMENT_README.md`
- [ ] Update workflow comments

#### 3.2 Create Migration Guide
- [ ] Document label changes
- [ ] Document workflow changes
- [ ] Create troubleshooting guide
- [ ] Update FAQ

#### 3.3 Announce Changes
- [ ] Create announcement issue
- [ ] Update CHANGELOG
- [ ] Post in discussions
- [ ] Update agent documentation

### Phase 4: Monitoring (Week 4)

#### 4.1 Metrics Collection
- [ ] Track assignment latency
- [ ] Monitor missed assignments
- [ ] Track label accuracy
- [ ] Measure workflow execution time

#### 4.2 Issue Resolution
- [ ] Address any edge cases found
- [ ] Fix label inconsistencies
- [ ] Update documentation gaps
- [ ] Optimize performance

#### 4.3 Finalization
- [ ] Remove deprecated workflows
- [ ] Archive old documentation
- [ ] Update all references
- [ ] Mark migration complete

---

## Testing Strategy

### Unit Tests

#### Test 1: Issue Assignment
```bash
# Create test issue
issue_num=$(gh issue create --title "Test: Issue assignment" --body "Test body")

# Verify agent assigned
sleep 5
gh issue view $issue_num --json labels,assignees

# Expected:
# - Label: assigned-agent
# - Assignee: copilot
# - Comment with agent name
```

#### Test 2: PR Feedback Assignment
```bash
# Create test PR
pr_num=$(gh pr create --title "Test: PR feedback" --body "Test" --label "tech-lead-changes-requested")

# Verify feedback issue created
sleep 5
feedback_issue=$(gh issue list --label "tech-lead-feedback" --search "PR #${pr_num} in:title" --json number --jq '.[0].number')

# Expected:
# - Feedback issue exists
# - Issue has assigned-agent label
# - Issue assigned to copilot
# - PR has comment linking to issue
```

#### Test 3: Fork PR Handling
```bash
# Simulate fork PR (manually)
# 1. Create PR from fork
# 2. Add tech-lead-changes-requested label
# 3. Verify workflow either:
#    a) Creates issue (if approved)
#    b) Posts fallback comment (if needs approval)
#    c) Schedule sweep catches it in 30min
```

### Integration Tests

#### Test 4: End-to-End Review Flow
```bash
# 1. Create PR touching protected path (.github/workflows/)
pr_num=$(gh pr create --title "Test: Update workflow" --body "Changes" --head "test-branch")

# 2. Verify tech lead labels applied
gh pr view $pr_num --json labels

# Expected: needs-tech-lead-review, tech-lead-required

# 3. Manually request changes as tech lead
gh pr review $pr_num --request-changes --body "Test feedback"

# 4. Verify labels updated
gh pr view $pr_num --json labels

# Expected: tech-lead-changes-requested

# 5. Verify feedback issue created
sleep 60  # Wait for workflow
feedback_issue=$(gh issue list --search "PR #${pr_num} in:title" --json number --jq '.[0].number')

# Expected: Issue exists with assigned-agent label

# 6. Close feedback issue (simulate agent completing work)
gh issue close $feedback_issue --comment "Fixes applied"

# 7. Manually approve as tech lead
gh pr review $pr_num --approve

# 8. Verify labels updated
gh pr view $pr_num --json labels

# Expected: tech-lead-approved, no tech-lead-changes-requested

# 9. Verify PR merged
sleep 30
gh pr view $pr_num --json state

# Expected: MERGED
```

### Performance Tests

#### Test 5: Assignment Latency
```bash
# Create 10 test issues
for i in {1..10}; do
  start_time=$(date +%s)
  issue_num=$(gh issue create --title "Latency test $i" --body "Test")
  
  # Poll until assigned
  while [ -z "$(gh issue view $issue_num --json assignees --jq '.assignees[]')" ]; do
    sleep 1
  done
  
  end_time=$(date +%s)
  latency=$((end_time - start_time))
  echo "Issue $i assignment latency: ${latency}s"
done

# Expected: <60 seconds for event-driven (down from 15+ minutes)
```

#### Test 6: Schedule Sweep Performance
```bash
# Create orphan issue (no assignment)
issue_num=$(gh issue create --title "Orphan test" --body "Test" --assignee "")

# Remove automation that would assign it
gh issue edit $issue_num --remove-label "automated"

# Wait for schedule sweep (30min)
sleep 1800

# Verify assigned
gh issue view $issue_num --json assignees

# Expected: Assigned within 30min by safety net sweep
```

---

## Benefits of Overhaul

### Simplification

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Workflows | 3 | 2 | -33% |
| Tech Lead Labels | 8 | 4 | -50% |
| Agent Tracking Labels | 4 | 1 | -75% |
| Scheduled Sweeps | 2 (7min, 15min) | 1 (30min) | -50% |
| Lines of Workflow YAML | ~1200 | ~800 | -33% |

### Performance

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Issue Assignment | 15min (schedule) | <60s (event) | 15x faster |
| PR Feedback Assignment | 7min (schedule) | <60s (event) | 7x faster |
| End-to-end Review Cycle | ~25min | ~3min | 8x faster |

### Maintainability

**Before:**
- 3 workflows with overlapping concerns
- Agent matching logic duplicated 2x
- Complex state management across workflows
- Difficult to trace issue → PR → agent flow

**After:**
- 2 workflows with clear separation
- Agent matching logic centralized 1x
- Simple state management
- Clear flow: Issue/PR → unified assignment → tech lead review → merge

### Reliability

**Before:**
- Race conditions between scheduled sweeps
- Missed assignments due to timing
- Fork PR approval breaks autonomous operation
- Label sprawl creates inconsistencies

**After:**
- Event-driven reduces races
- Fallback schedule catches edge cases
- Graceful degradation for fork PRs
- Minimal labels reduce inconsistencies

---

## Risks and Mitigations

### Risk 1: Fork PR Approval Still Required

**Mitigation:**
- Graceful error handling with fallback comments
- Schedule sweep (30min) as safety net
- Documentation for manual trigger
- Monitor fork PR patterns and adjust strategy

### Risk 2: Event Trigger Failures

**Mitigation:**
- Comprehensive error handling in workflows
- Schedule sweep catches missed events
- Manual dispatch available for critical cases
- Monitoring and alerting for failures

### Risk 3: Migration Breaks Existing PRs

**Mitigation:**
- Keep both old and new workflows running for 48 hours
- Label migration script updates existing PRs
- Thorough testing before cutover
- Rollback plan if issues detected

### Risk 4: Label Changes Confuse Users

**Mitigation:**
- Clear documentation of label changes
- Announcement with migration guide
- Update all documentation references
- Label descriptions explain purpose

### Risk 5: Performance Degrades

**Mitigation:**
- Baseline performance tests before migration
- Monitor latency after deployment
- Fallback to schedule if events unreliable
- Optimize based on metrics

---

## Success Criteria

### Functional Requirements

- [✅] Issues assigned to agents within 60 seconds
- [✅] PR feedback issues created within 60 seconds of changes requested
- [✅] Tech lead review flow works end-to-end
- [✅] Auto-merge only proceeds with proper approvals
- [✅] Fork PRs handled gracefully (even if delayed)
- [✅] No duplicate assignments
- [✅] No missed assignments (caught by schedule sweep)

### Non-Functional Requirements

- [✅] Workflow execution time < 2 minutes
- [✅] Code reduction of 30%+
- [✅] Label count reduction of 50%+
- [✅] Assignment latency reduction of 10x+
- [✅] Zero downtime during migration
- [✅] Complete documentation coverage

### User Experience

- [✅] Clear PR labels indicate state
- [✅] Comments explain next steps
- [✅] Tech leads mentioned explicitly
- [✅] Agent assignments visible and trackable
- [✅] Feedback loop is obvious and fast

---

## Conclusion

The Tech Lead Review System has grown complex through iterative additions. This overhaul proposes a **back-to-basics approach**:

1. **Unify agent assignment** into one workflow
2. **Simplify PR review** to focus on its core purpose
3. **Reduce label sprawl** to essential state indicators
4. **Move to events** for speed and simplicity
5. **Keep schedules** as safety nets only

The result: A **simpler, faster, more maintainable** system that preserves the value of autonomous tech lead review while reducing complexity by 30-50% across all metrics.

### Next Steps

1. **Review this proposal** with stakeholders
2. **Approve migration plan** and timeline
3. **Begin Phase 1** (preparation) implementation
4. **Monitor metrics** and adjust as needed

### Questions for Review

1. Is the 2-workflow architecture acceptable?
2. Are the label simplifications agreeable?
3. Is the event-driven approach with schedule fallback acceptable?
4. Are there additional edge cases to consider?
5. Is the 4-week timeline realistic?

---

**@support-master** recommends proceeding with this overhaul to address the complexity and reliability issues in the current system.

*Document created: 2025-11-23*  
*Status: PROPOSAL - Awaiting stakeholder review*
