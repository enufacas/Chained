# Meta-Coordinator System - Expected Behavior

**Agent:** @meta-coordinator-system  
**Purpose:** Autonomous orchestration of tech lead reviews and agent assignments  
**Frequency:** Every 5 minutes  
**Status:** ⚠️ Waiting for COPILOT_PAT fix

---

## What This System Does

The **@meta-coordinator-system** is the autonomous orchestrator for the entire Chained agent ecosystem. It runs every 5 minutes and performs 7 core responsibilities:

### 1. 🔍 PR Review Orchestration

**What it does:**
- Lists all open, non-draft PRs
- Analyzes changed files in each PR
- Matches PRs to tech leads using `match-pr-to-tech-lead.py`
- Applies `needs-tech-lead-review` label where needed
- Mentions tech leads in PR comments

**Decision logic:**
- Protected paths (`.github/workflows/`, `.github/agents/`, `docs/`) → Requires review
- High complexity (&gt;5 files or &gt;100 lines changed) → Requires review
- Security keywords (auth, token, password, secret) → Requires review
- WIP or draft PRs → Skip

**Example output:**
```
Processed 3 PRs:
- #123: Assigned @workflows-tech-lead (changed workflows)
- #124: Assigned @docs-tech-lead (updated documentation)
- #125: No review needed (simple fix)
```

---

### 2. 📝 Feedback Issue Creation

**What it does:**
- Monitors PRs with `tech-lead-changes-requested` label
- Extracts change request comments from tech lead
- Creates feedback issue with:
  - Title: `[Tech Lead Feedback] PR #X - {title}`
  - Body: PR context + review comments + agent directive
  - Labels: `tech-lead-feedback`, `assigned-agent`
- Matches feedback to agent using `match-issue-to-agent.py`
- Assigns Copilot to the feedback issue
- Links issue ↔ PR bidirectionally

**Prevents duplicates:**
- Searches for existing feedback issues before creating
- Only creates if none exists for that PR

**Example output:**
```
Created feedback issues:
- Issue #456 for PR #123 (@workflows-tech-lead requested changes)
  Assigned to @align-wizard (workflow expertise)
- Issue #457 for PR #124 (@docs-tech-lead requested changes)
  Assigned to @support-master (documentation expertise)
```

---

### 3. 🤖 Agent Assignment

**What it does:**
- Lists all open issues without agent assignment
- Analyzes issue title and body
- Runs pattern matching via `match-issue-to-agent.py`
- Selects best agent based on:
  - Specialization match
  - Keyword score
  - Pattern score
- Assigns Copilot to issue using `assign-copilot-to-issue.sh`
- Posts assignment comment
- Applies `assigned-agent` label

**Agent matching examples:**
- Workflow failures → @troubleshoot-expert
- Security issues → @secure-specialist
- Performance problems → @accelerate-master
- Documentation tasks → @support-master
- Code organization → @organize-guru

**Example output:**
```
Assigned agents to 5 issues:
- #301: @secure-specialist (security vulnerability)
- #302: @accelerate-master (performance optimization)
- #303: @support-master (documentation update)
- #304: @troubleshoot-expert (workflow debugging)
- #305: @organize-guru (code refactoring)
```

---

### 4. 🔄 Review Cycle Management

**What it does:**
- Monitors PRs with `tech-lead-changes-requested`
- Detects new commits after change request
- Requests re-review from tech lead (comment + @mention)
- Tracks review iteration count
- On approval:
  - Removes `tech-lead-changes-requested`
  - Adds `tech-lead-approved`
  - Closes linked feedback issue
- On continued changes:
  - Keeps label
  - Notifies agent in feedback issue

**Iteration tracking:**
- Tracks up to 5 review cycles
- Escalates if stuck in loop

**Example output:**
```
Review cycle updates:
- PR #123: New commits detected, requested re-review from @workflows-tech-lead
- PR #124: Approved! Applied tech-lead-approved label, closed issue #457
- PR #125: Still needs changes (iteration 2/5)
```

---

### 5. ✅ Auto-Merge Execution

**What it does:**
- Checks ALL open PRs for merge eligibility
- **Trust check:** From copilot OR repo owner/maintainer
- **State check:** Open, not draft, no WIP in title
- **Review check:** Has `tech-lead-approved` OR doesn't need review
- **Blocking check:** No `tech-lead-changes-requested` or blocking labels
- **CI check:** All required checks passed
- **Mergeable check:** No merge conflicts
- **If ALL criteria met:**
  - Executes: `gh pr merge $PR_NUM --squash --auto`
  - Posts success comment
  - Records in memory

**Safety guarantees:**
- Only trusted sources (copilot, owner, maintainer)
- Tech lead approval if review was required
- All CI checks must pass
- No merge conflicts
- No blocking labels

**Example output:**
```
Auto-merge operations:
✅ PR #123: Merged (tech-lead-approved, all checks passed)
✅ PR #124: Merged (no review needed, all checks passed)
❌ PR #125: Not eligible (tech-lead-changes-requested)
❌ PR #126: Not eligible (CI checks failing)
```

---

### 6. 🧠 Memory and Learning

**What it does:**
- Loads persistent memory at start:
  ```python
  memory = MetaCoordinatorMemory()
  summary = memory.get_summary()
  ```
- Gets decision context:
  ```python
  context = memory.get_context_for_decision("pr_assignment")
  agent_stats = memory.get_agent_performance("engineer-master")
  ```
- Records ALL actions:
  ```python
  memory.record_pr_assignment(pr_num, tech_lead, complexity, files)
  memory.record_issue_assignment(issue_num, agent, score)
  memory.record_feedback_issue(pr_num, issue_num, tech_lead, agent)
  memory.record_merge(pr_num, reasons)
  ```
- Tracks exceptions and patterns:
  ```python
  memory.record_exception(type, desc, context)
  memory.add_learning(insight, evidence)
  ```
- Saves memory at end

**Learning examples:**
- "PR #X needed review but was initially skipped - pattern updated"
- "@agent-Y handles workflow issues faster than @agent-Z"
- "Tech lead @A approves 90% on first review, @B requires 2 iterations average"

**Example output:**
```
Memory system:
- Recorded 3 PR assignments
- Recorded 5 issue assignments
- Recorded 2 auto-merges
- Added 1 learning insight
- Memory saved to .github/agent-system/meta-coordinator-memory.json
```

---

### 7. ⚠️ Exception Handling

**What it does:**
- Identifies inconsistencies:
  - PRs with conflicting labels
  - Feedback issues without linked PRs
  - Orphaned agent assignments
  - Stale review cycles (&gt;7 days)
  - Missing tech lead assignments
  - Label inconsistencies

- Resolves issues:
  - Fix label conflicts (keep most recent state)
  - Close orphaned issues
  - Ping stale reviews (@mention tech lead)
  - Create coordination issues for complex cases

**Example output:**
```
Exception handling:
⚠️  PR #127: Conflicting labels (tech-lead-approved + tech-lead-changes-requested)
   → Resolved: Removed tech-lead-changes-requested (approved is more recent)
⚠️  Issue #458: Feedback issue with no linked PR
   → Resolved: Closed as orphaned
⚠️  PR #128: Review stale (10 days old)
   → Action: Pinged @workflows-tech-lead for update
```

---

## Expected Output Format

Each coordination run posts a summary issue comment:

```markdown
# 🎯 Meta-Coordinator System Report

**Run:** 2025-11-23 18:31 UTC
**Duration:** 45 seconds
**Status:** ✅ SUCCESS

## System State
- Open PRs: 8 (3 need review, 5 ready)
- Open Issues: 12 (all assigned)
- Pending Reviews: 2
- Ready to Merge: 3

## Actions Taken
1. ✅ PR Review: Assigned 2 tech leads
2. ✅ Feedback Issues: Created 1, closed 1
3. ✅ Agent Assignment: Assigned 3 agents
4. ✅ Review Cycles: 1 re-review requested, 1 approved
5. ✅ Auto-Merge: Merged 2 PRs
6. ✅ Memory: Recorded 8 actions
7. ✅ Exceptions: Resolved 1 inconsistency

## Metrics
- PRs processed: 8
- Tech leads assigned: 2
- Agents assigned: 3
- PRs merged: 2
- Feedback issues: 1 created, 1 closed

## System Health
✅ All systems operational
✅ No blocking issues
✅ Coordination running smoothly

**Next run:** 2025-11-23 18:36 UTC (5 minutes)
```

---

## How It Maintains Autonomy

### Continuous Loop
```
Every 5 minutes:
  1. Assess system state
  2. Identify work needed
  3. Execute prioritized actions
  4. Record outcomes
  5. Learn patterns
  6. Close coordination issue
```

### Self-Correcting
- Detects inconsistencies
- Fixes simple issues automatically
- Escalates complex issues
- Learns from failures

### Zero Manual Intervention
- PRs get reviewed automatically
- Issues get assigned automatically
- Approved PRs merge automatically
- System maintains itself

---

## Current Status: Blocked

**Why it's not working:**
- COPILOT_PAT lacks GitHub API permissions
- Returns `HTTP 403: 403 Forbidden` on all operations
- Cannot list PRs, create issues, assign agents, or merge

**Fix:**
- Generate new PAT with `repo` + `workflow` scopes
- Update `COPILOT_PAT` in `copilot` environment
- See: `ACTION_REQUIRED_COPILOT_PAT_FIX.md`

**After fix:**
- Next run (every 5 minutes) will automatically resume
- All 7 responsibilities will execute
- System becomes fully autonomous

---

## Success Criteria

You'll know the meta-coordinator is working when:

✅ **Coordination issues show activity:**
- "Processed X PRs"
- "Assigned Y agents"
- "Merged Z PRs"

✅ **PRs get tech lead assignments:**
- Comments appear mentioning tech leads
- Labels applied automatically

✅ **Issues get agent assignments:**
- Copilot assigned to issues
- Agent directives posted

✅ **Approved PRs merge automatically:**
- No manual merge needed
- PRs complete within minutes of approval

✅ **System self-maintains:**
- Handles edge cases
- Fixes inconsistencies
- Learns and improves

---

**This document describes the expected behavior once COPILOT_PAT is fixed.**

**Created:** 2025-11-23 18:27 UTC  
**By:** @meta-coordinator-system  
**Status:** Waiting for fix
