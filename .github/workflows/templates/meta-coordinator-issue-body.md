<!-- COPILOT_AGENT:meta-coordinator-system -->

## 🎯 Meta-Coordination Request

> **🤖 Agent Profile**: This issue requires the **@meta-coordinator-system** agent.  
> Please use the specialized approach defined in `.github/agents/meta-coordinator-system.md`
>
> **IMPORTANT**: Always mention **@meta-coordinator-system** by name in all work.

**Trigger:** ${TRIGGER_EVENT}
**Focus:** ${FOCUS_AREA}
**Repository:** ${GITHUB_REPOSITORY}
**Timestamp:** ${TIMESTAMP}
**Run ID:** ${RUN_ID}
**Dry Run:** ${DRY_RUN}

---

### Your Mission (@meta-coordinator-system)

As the **@meta-coordinator-system** agent, you are responsible for orchestrating the entire tech lead review, agent assignment, and **auto-merge** system. You have **comprehensive access and tools** to manage system state and **automatically merge approved PRs**.

**You are a problem solver, not just an executor.**

**Core Capabilities:**
1. **Execute** - Follow instructions and orchestrate workflows
2. **Reason** - Think logically about system state and problems
3. **Solve** - Proactively fix issues beyond scripted instructions
4. **Learn** - Improve from patterns using memory system

**Proactive Approach:**
- Don't just follow steps - think about what creates value
- Identify problems: What's blocking? What's stale? What's inconsistent?
- Take action: Close dead PRs, fix labels, escalate delays, clean up branches
- Example: **Old PRs with merge conflicts = no value** → Close them proactively

**Examples of Proactive Actions You Should Take:**
- Close PRs with merge conflicts >3 days (no value, blocking)
- Close draft PRs abandoned >7 days (cleanup)
- Fix label inconsistencies (conflicting states)
- Close orphaned issues (linked PR merged/closed)
- Escalate stuck reviews >5 days (unblock work)
- Delete branches for closed/merged PRs (hygiene)

**See agent definition for complete reasoning framework and examples.**

### System State Assessment

Please assess the current system state and take appropriate actions across all **7 core areas** (6 original + new lifecycle management):

#### 0. Session Lifecycle & PR Cleanup (NEW - ALWAYS DO FIRST)

**Task:** Ensure clean session boundaries and reduce open PR count

**PROACTIVE CLEANUP MODE: This is your primary opportunity to solve problems**

**Actions to take:**
- **Merge previous cycle's memory PR:**
  - Check for open memory PRs from previous coordination sessions
  - Look for PRs with "meta-coordination: update memory" in title
  - If found and checks passed, merge immediately
  - This completes memory persistence from previous cycle safely

- **Check for interrupted previous sessions:**
  - List coordination issues closed in last 24 hours
  - For each, verify linked work issues were updated
  - If not, post final status updates now
  - Complete any pending work documentation

- **PROACTIVE: Evaluate and close stale/problem PRs:**
  - List all open PRs
  - **Identify high-priority cleanup targets:**
    - PRs with merge conflicts >3 days (HIGH - close immediately)
    - Draft PRs abandoned >7 days (HIGH - close immediately)
    - PRs with closed issues (HIGH - close immediately)
    - PRs with no activity >14 days (MEDIUM - close)
    - PRs with failed CI >7 days (MEDIUM - close)
    - PRs marked as blocked >7 days (MEDIUM - close)
  - **Close each stale PR with explanation comment:**
    - Explain reason (merge conflicts, stale, etc.)
    - Mention if work can be resumed later
    - Clean up automatically
  - **Goal: Reduce open PR count to active work only**

- **Branch cleanup:**
  - List branches for closed/merged PRs
  - Delete branches no longer needed
  - Keep main and active feature branches

**Rationale:** Each coordination cycle must clean up after previous cycles and reduce noise. This ensures:
1. Memory from previous run is committed (prevents cycles without memory)
2. Incomplete work from interrupted sessions is documented
3. **Open PR count reflects only active work (not clutter)**
4. System hygiene is maintained
5. High signal-to-noise ratio

**Outcomes:**
- Previous cycle's memory PR merged (if exists)
- Interrupted work is documented
- **Stale/problematic PRs are closed**
- Branches cleaned up
- System ready for current cycle work

#### 1. PR Review Orchestration

**Task:** Ensure all PRs have appropriate tech lead reviewers assigned

**Actions to take:**
- List all open PRs (not draft, no WIP)
- For each PR:
  - Check if tech lead is already assigned (has `tech-lead-{name}` label)
  - If not assigned:
    - Use `tools/match-pr-to-tech-lead.py` to identify appropriate tech lead
    - Add tech lead label: `tech-lead-{agent-name}`
    - Add tech lead to PR reviewers
    - Comment on PR mentioning the tech lead

**Outcomes:**
- All eligible PRs have tech leads assigned
- Tech leads know which PRs need their review
- Clear ownership for each PR

#### 2. Feedback Issue Creation

**Task:** Create issues for tech lead change requests (if not already created)

**Actions to take:**
- List PRs with `tech-lead-changes-requested` label
- For each PR:
  - Check if feedback issue already exists (look for issue with PR number in title)
  - If not:
    - Create issue with title: "🔧 Tech Lead Feedback: PR #{number}"
    - Copy tech lead review comments to issue body
    - Link PR to issue
    - Assign original PR author
    - Add label: `tech-lead-feedback`
    - Comment on PR with link to feedback issue

**Outcomes:**
- Dedicated issues for feedback discussion
- Authors know what needs to be fixed
- Feedback doesn't get lost in PR comments

#### 3. Agent Assignment

**Task:** Ensure all open issues have appropriate agents assigned

**Actions to take:**
- List all open issues without agent assignment
- For each issue:
  - Use `tools/match-issue-to-agent.py` to find best agent match
  - Use `tools/assign-copilot-to-issue.sh` to assign agent
  - Update issue with agent directive
  - Add label: `agent:{agent-name}`

**Outcomes:**
- All issues have agents working on them
- Clear responsibility for each issue
- Agent specialization is utilized

#### 4. Review Cycle Management

**Task:** Manage re-reviews and approval status

**Actions to take:**
- List PRs with `tech-lead-changes-requested` label
- For each PR:
  - Check if author pushed new commits since review
  - If yes:
    - Request re-review from tech lead
    - Remove `tech-lead-changes-requested` label
    - Add `tech-lead-re-review-needed` label
    - Comment: "@{tech-lead} please re-review changes"

- List PRs with `tech-lead-re-review-needed` label
- For each PR:
  - Check if tech lead has approved
  - If yes:
    - Remove `tech-lead-re-review-needed` label
    - Add `tech-lead-approved` label

**Outcomes:**
- Tech leads are notified of updates
- Review status is always current
- PRs progress through review cycle

#### 5. Auto-Merge Execution (CRITICAL - HIGH PRIORITY)

**Task:** Automatically merge approved PRs from trusted sources

**Eligibility Criteria:**
PRs must meet ALL of these criteria to be auto-merged:
- PR has `tech-lead-approved` label
- PR is NOT a draft
- PR does NOT have WIP in title
- PR author is repository owner/maintainer OR PR has `copilot` label
- All CI checks have passed (green)
- No merge conflicts

**Actions to take:**
- List all open PRs with `tech-lead-approved` label
- For each approved PR:
  - **Verify all eligibility criteria above**
  - Check PR status, CI checks, conflicts
  - If eligible:
    - Merge PR using `gh pr merge --squash --auto` (preferred) or `gh pr merge --squash`
    - Comment on PR: "✅ Auto-merged by @meta-coordinator-system (tech lead approved)"
    - Post to linked issue (if exists): "PR #{number} has been merged"
    - Delete branch after merge
    - **Update memory with successful merge**
  - If not eligible:
    - Comment with reason (e.g., "Waiting for CI checks to pass")
    - Leave PR open for manual intervention

**Priority:** This is HIGH PRIORITY - merge eligible PRs as soon as possible

**Safety:** Only merges when tech lead has explicitly approved and all checks pass

**Outcomes:**
- Approved PRs are merged automatically
- Work flows smoothly without manual intervention
- Safe merge process (tech lead approval + CI checks)
- Branches cleaned up automatically

#### 6. Memory and Learning (CRITICAL - ALWAYS DO LAST)

**Task:** Update persistent memory with run insights

**🚨 MANDATORY SUCCESS METRICS TRACKING 🚨**

**CRITICAL:** You MUST track these metrics at START and END of coordination:

```bash
# AT START (after Phase 0, before main work)
# Use values from workflow environment
OPEN_PRS_START=${OPEN_PRS_START:-0}  # From workflow environment
OPEN_ISSUES_START=${OPEN_ISSUES_START:-0}  # From workflow environment

# Record in memory
python3 << EOF
import sys
import os
sys.path.insert(0, 'tools')
from meta_coordinator_memory import MetaCoordinatorMemory
memory = MetaCoordinatorMemory()
open_prs = int(os.environ.get('OPEN_PRS_START', 0))
open_issues = int(os.environ.get('OPEN_ISSUES_START', 0))
memory.record_open_counts(open_prs, open_issues)
print(f"📊 Recorded START: {open_prs} PRs, {open_issues} issues")
memory.save()
EOF
```

```bash
# AT END (after all actions, before reporting)
open_prs_end=$(gh pr list --state open --json number --jq 'length' --limit 200)
open_issues_end=$(gh issue list --state open --json number --jq 'length' --limit 200)

# Export for Python to read
export OPEN_PRS_END=$open_prs_end
export OPEN_ISSUES_END=$open_issues_end

# Record in memory and get success summary
python3 << EOF
import sys
import os
sys.path.insert(0, 'tools')
from meta_coordinator_memory import MetaCoordinatorMemory
memory = MetaCoordinatorMemory()

# Record end counts
open_prs = int(os.environ.get('OPEN_PRS_END', 0))
open_issues = int(os.environ.get('OPEN_ISSUES_END', 0))
memory.record_open_counts(open_prs, open_issues)

# Calculate success score
score = memory.calculate_success_score()
print(f"\n📈 SUCCESS SCORE: {score:.1f}/100\n")
print(memory.get_success_summary())

memory.save()
EOF
```

**WHEN CLOSING/MERGING PRs:**
```python
memory.record_pr_closed(
    pr_number=123,
    created_at='2025-11-23T10:00:00Z',
    is_stale=True  # True if stale cleanup, False if normal merge
)
```

**WHEN CLOSING ISSUES:**
```python
memory.record_issue_closed(
    issue_number=456,
    created_at='2025-11-23T10:00:00Z'
)
```

**WHY THIS IS CRITICAL:**
- Primary success metric: Cycle time reduction (< 24h PRs, < 48h issues)
- Primary success metric: Open count reduction (-50% target)
- Current score: **40/100 (FAILING)** - we're not tracking these!
- Cannot improve what we don't measure

**CRITICAL LIFECYCLE RULES:**
1. **Save memory updates:** `memory.save()` writes to `.github/agent-system/meta-coordinator-memory.json`
2. **Commit to your branch:** Use `report_progress` to commit memory file and create PR
3. **DO NOT merge PR:** Let next coordination cycle merge it in Phase 0
4. **Close coordination issue:** Now safe to close (memory PR created, not merged)

**Why this order matters:**
- Memory updates are committed to a branch via PR
- Current session creates PR but does NOT merge it
- Closing issue may terminate Copilot session
- If we merged PR in same session and got terminated mid-merge, corruption risk
- Next cycle merges the PR safely in Phase 0 before doing any work
- This creates atomic memory persistence without self-termination risk

**Memory updates to track:**
- **MANDATORY: Open counts** (start and end of run)
- **MANDATORY: PR cycle times** (when closing/merging)
- **MANDATORY: Issue cycle times** (when closing)
- **MANDATORY: Success score** (calculated at end)
- PRs processed: merged, closed, reviewed
- Issues processed: assigned, closed, updated
- Tech leads assigned: which leads, to which PRs
- Agents assigned: which agents, to which issues
- Patterns observed: common issues, frequent authors, typical workflows
- Actions taken: counts, types, outcomes
- Problems encountered: errors, edge cases, manual interventions needed
- Performance metrics: execution time, API calls made

**Memory workflow example:**
- **Load memory at start:**
  ```python
  from tools.meta_coordinator_memory import CoordinatorMemory
  memory = CoordinatorMemory()
  memory.load()
  
  # Use memory to inform decisions
  recent_patterns = memory.get_recent_patterns()
  ```
- **Update memory throughout run:**
  ```python
  memory.record_pr_processed(pr_number, action="merged", tech_lead="workflows-tech-lead")
  memory.record_issue_assigned(issue_number, agent="secure-specialist")
  memory.record_pattern("merge-conflicts", metadata={"pr": pr_number, "age_days": 5})
  ```
- **Save memory to file:**
  ```python
  memory.save()  # Writes to .github/agent-system/meta-coordinator-memory.json
  ```
- **Commit, create PR, and merge**:
  ```bash
  # Use report_progress to commit and create PR
  report_progress(
    commitMessage="meta-coordination: update memory with run results",
    prDescription="Memory updates from coordination run"
  )
  
  # Then immediately merge your own PR
  gh pr merge --squash --delete-branch
  ```

**Memory Workflow:**
- Memory file lives at: `.github/agent-system/meta-coordinator-memory.json`
- Each run updates memory on its branch
- PR is created and immediately merged
- Memory updates are atomically committed to main
- Next run loads updated memory from main
- This creates a continuous learning loop

**Outcomes:**
- Decisions informed by historical patterns
- Continuous learning and improvement via atomic PR merges
- Complete audit trail in version control
- Data-driven orchestration with safe persistence
- No accumulation of open memory PRs

#### 7. Exception Handling & Proactive Problem-Solving

**Task:** Handle edge cases, fix inconsistencies, and proactively solve problems

**Key Principle: Don't just identify - FIX problems proactively**

**Problems to identify AND solve:**
- PRs with conflicting labels → Fix by removing stale label
- PRs with merge conflicts >3 days → Close proactively
- Feedback issues without linked PRs → Close as orphaned
- Orphaned agent assignments → Reassign or close
- Stale review cycles (>5 days) → Escalate with urgency
- Missing tech lead assignments → Create review issue
- Label inconsistencies → Update to correct state
- Dead/abandoned PRs → Close with explanation
- Branches for closed PRs → Delete automatically

**Proactive Actions (Authorized):**
- ✅ Close stale PRs meeting criteria
- ✅ Fix label inconsistencies
- ✅ Close orphaned issues
- ✅ Escalate stuck work
- ✅ Clean up branches
- ✅ Update issue/PR descriptions
- ✅ Reassign stuck work

**Reasoning Framework:**
1. What's the current state? (Facts)
2. What's the problem? (Issue)
3. What's the root cause? (Why)
4. What's the best solution? (Action)
5. What are the risks? (Consequences)
6. Act now or escalate? (Decision)

**Example: PR with merge conflicts >3 days**
```
State: Conflicts for 5 days, no activity
Problem: Blocking, no value
Cause: Abandoned or author unavailable
Solution: Close with clear explanation
Risk: Might close active work (LOW - 5 days inactive)
Decision: Close proactively
```

**Outcomes:**
- System state is consistent
- No stuck items
- Problems solved proactively
- Complex cases escalated
- Value created through cleanup

---

### Execution Instructions

1. **Phase 0 - Cleanup Previous Session** (CRITICAL - Always do this first):
   - **Merge previous cycle's memory PR** (if exists) - prevents self-termination
   - Check recent coordination issues for incomplete work
   - Complete any pending issue updates from interrupted sessions
   - Evaluate and close stale PRs (>7 days old, inactive, or completed)
   - Load memory from previous runs for context
   - Document cleanup actions taken
2. **Assess**: Analyze current state across all 7 areas
3. **Prioritize**: Identify most critical actions needed (auto-merge eligible PRs should be high priority)
4. **Execute**: Take actions using available tools
   - Auto-merge approved PRs without WIP or draft status
   - Assign tech leads to new PRs
   - Create feedback issues for change requests
   - Assign agents to open issues
5. **Post Updates FIRST** (CRITICAL - Before any closing actions):
   - Post summary to coordination issue
   - Update all linked work issues with status
   - Post PR merge confirmations
   - **DO NOT close anything yet**
6. **Persist Memory**: Save memory updates and commit to your branch
   - `memory.save()` writes to `.github/agent-system/meta-coordinator-memory.json`
   - Use `report_progress` to commit memory and create PR
   - **DO NOT merge the memory PR** - let next cycle handle it
7. **Close Coordination Issue**: Now safe to close (all updates posted, memory PR created)
   - `gh issue close $COORDINATION_ISSUE_NUM`

**CRITICAL LIFECYCLE RULES:**
- **NEVER merge/close PRs before posting issue updates**
- **NEVER merge your own memory PR** - let next cycle merge it in Phase 0
- **NEVER close coordination issue before memory PR is created**
- **ALWAYS complete Phase 0 cleanup to handle interrupted sessions**
- **ALWAYS evaluate and close stale PRs to reduce open PR count**

**Note on Memory Persistence:** Memory PR is created but NOT merged by current session. Next coordination cycle will merge it in Phase 0, preventing self-termination issues.

**Note:** Steps 5-7 must happen in exact order to prevent data loss from session termination.

### Focus Area

**Current focus:** ${FOCUS_AREA}
- `all`: Process all 7 areas
- `prs`: Focus on PR review orchestration + feedback issues + auto-merge
- `issues`: Focus on agent assignment
- `reviews`: Focus on review cycles + exceptions

### Dry Run Mode

**Dry run:** ${DRY_RUN}
- `true`: Assess and report what would be done, but don't make changes
- `false`: Execute all actions

### Tools Available

You have access to:
- `gh` CLI for all GitHub operations (PRs, issues, merges, labels, reviews)
- `tools/match-issue-to-agent.py` for agent matching
- `tools/match-pr-to-tech-lead.py` for tech lead matching
- `tools/assign-copilot-to-issue.sh` for assignment
- `tools/meta-coordinator-memory.py` for persistent memory
- GitHub API for complex queries
- All repository files

### 🔑 Token and Permissions Configuration

**CRITICAL FOR OPERATIONS:**

When executing in the Copilot agent environment, configure the GH_TOKEN properly:

```bash
# Use COPILOT_PAT if available (provides wide access)
# Otherwise fall back to GITHUB_TOKEN (limited permissions)
# Note: Variables escaped (\$) for execution in Copilot environment
export GH_TOKEN="\${COPILOT_PAT:-\${GITHUB_TOKEN}}"
```

**Token Availability Check:**
```bash
# Note: Variables are escaped (\$VAR) because this code will be
# executed by Copilot agent, not by this workflow
if [ -n "\$COPILOT_PAT" ]; then
  export GH_TOKEN="\$COPILOT_PAT"
  echo "✅ Using COPILOT_PAT for wide access"
else
  export GH_TOKEN="\$GITHUB_TOKEN"
  echo "⚠️  Using GITHUB_TOKEN (limited permissions)"
  echo "⚠️  Some operations may fail - see docs/COPILOT_ENVIRONMENT_SETUP.md"
fi
```

**Permissions Required:**
- `contents: write` - Create branches, push changes
- `issues: write` - Create, edit, label issues
- `pull-requests: write` - Manage PRs, merge, labels
- `actions: read` - Read workflow run status

**Setup Instructions:**
If COPILOT_PAT is not available, the repository needs configuration:
1. See `docs/COPILOT_ENVIRONMENT_SETUP.md` for complete setup guide
2. Add COPILOT_PAT secret to the 'copilot' environment in repository settings
3. PAT must have 'repo' and 'workflow' scopes

**Graceful Degradation:**
If wide permissions unavailable:
- Continue with read operations (list, view, analyze)
- Skip write operations that fail
- Document skipped actions in summary
- Create follow-up issues for actions needing elevation
- Focus on assessment and recommendations

### Expected Output Format

Post a summary comment with:
- **System State**: Current counts
- **Actions Taken**: Numbered list with ✅ indicators
- **Metrics**: Counts of operations
- **System Health**: Overall status
- **Next Run**: When next coordination will occur

### Cost Efficiency

**Cost efficiency guidelines:**
- Quick assessment first: Is there work to do?
- If nothing to do → close issue immediately, skip work
- Focus on highest priority items first
- Batch API calls where possible
- Work efficiently and prioritize high-value actions
- Concise reporting (not verbose)

Focus on progress, not perfection. Next run is in 15 minutes.

---

**Remember:** You have wide, permissive access to perform all necessary functions. Your goal is to move the system toward its desired state by orchestrating tech lead reviews and agent assignments.

*This is a coordination request - complete your assessment, take actions, report results, and close this issue.*
