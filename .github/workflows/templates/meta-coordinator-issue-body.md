<!-- COPILOT_AGENT:meta-coordinator-system -->

## 🎯 Meta-Coordination Request

> **🤖 Agent Assignment**: **@meta-coordinator-system**  
> Use the specialized approach defined in `.github/agents/meta-coordinator-system.md`
>
> **IMPORTANT**: Always mention **@meta-coordinator-system** by name in all work.

**Trigger:** ${TRIGGER_EVENT}  
**Focus:** ${FOCUS_AREA}  
**Repository:** ${GITHUB_REPOSITORY}  
**Timestamp:** ${TIMESTAMP}  
**Run ID:** ${RUN_ID}  
**Dry Run:** ${DRY_RUN}

---

### 📊 System State (From Workflow)

**Auto-Merge Completed (Phase 1):** ${AUTOMERGE_MERGED} PRs merged
- Processed: ${AUTOMERGE_PROCESSED}
- Failed: ${AUTOMERGE_FAILED}

**Stale PRs Closed (Phase 0):** ${CLEANUP_TOTAL}
- Merge conflicts: ${CLEANUP_CONFLICTS}
- No activity: ${CLEANUP_NO_ACTIVITY}
- Orphaned: ${CLEANUP_ORPHANED}
- Abandoned draft: ${CLEANUP_DRAFT}

**Current PR States (after workflow automation):**
- ✅ Mergeable (non-draft): ${MERGEABLE_PRS}
- ❌ Conflicting: ${CONFLICTING_PRS}
- 📝 Draft: ${DRAFT_PRS}
- ❓ Unknown: ${UNKNOWN_PRS}

**Starting Counts:**
- Open PRs: ${OPEN_PRS_START}
- Open Issues: ${OPEN_ISSUES_START}

---

### 🎯 Your Mission

**@meta-coordinator-system** - Orchestrate remaining coordination tasks. **Note:** Cleanup and auto-merge are now handled by the workflow before your session.

**Core Responsibilities:**
1. ~~**Session Lifecycle & Cleanup**~~ - **✅ DONE by workflow Phase 0**
2. **PR Review Orchestration** - Assign reviewers where needed
3. **Feedback Issues** - Create issues for change requests  
4. **Agent Assignment** - Assign agents to open issues
5. **Review Cycles** - Manage re-reviews and approvals
6. ~~**Auto-Merge**~~ - **✅ DONE by workflow Phase 1**
7. **Memory & Learning** - Track metrics and persist insights

**Critical Success Metrics:**
- **Cycle Time**: < 24h for PRs, < 48h for issues
- **Open Count Reduction**: -50% target
- **Proactive Cleanup**: 20%+ of closures

**Focus Area:** ${FOCUS_AREA}
- `all`: Process all 7 responsibilities
- `prs`: Focus on PRs (review, feedback, auto-merge)
- `issues`: Focus on agent assignment
- `reviews`: Focus on review cycles + exceptions

**Dry Run:** ${DRY_RUN}
- `true`: Assess and report only (no changes)
- `false`: Execute all actions

---

### 🔧 Quick Reference

**Tools Available:**
- `gh` CLI for all GitHub operations
- `tools/match-issue-to-agent.py` - Agent matching
- `tools/match-pr-to-review.py` - Reviewer matching
- `tools/assign-copilot-to-issue.sh` - Assignment
- `tools/meta-coordinator-memory.py` - Memory system

**Token Setup:**
```bash
export GH_TOKEN="\$COPILOT_PAT or \$GITHUB_TOKEN"
# See agent definition for full token configuration
```

**Critical Order:**
1. Load memory & track start metrics
2. Execute prioritized actions
3. **Post updates to issues FIRST** (before any closing)
4. Save memory & create PR (do NOT merge)
5. Close coordination issue

---

### 📝 Expected Output

Post a summary with:
- **Phase 0 Cleanup**: Stale PRs closed
- **System State**: Current counts with changes
- **Actions Taken**: Numbered list with ✅
- **Success Score**: From `memory.get_success_summary()`
- **Next Run**: Timing

See agent definition for complete execution instructions and examples.

---

*This coordination request is automatically created every 15 minutes. Complete your assessment, take actions, report results, and close this issue.*
