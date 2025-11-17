# Agent Workflow Scenario: Using Instructions & Context

> **@investigate-champion** - Demonstrating how agents use the complete instruction system

## 🎯 NEW REQUIREMENT ACKNOWLEDGED

**Question:** How does a given agent make use of our entire set of instructions?

**Answer:** This document walks through a complete scenario showing how an agent leverages:
- Repository-wide instructions
- Path-specific instructions
- Context files
- Agent-specific guidance

## 📋 Scenario: @engineer-master Implements a New Workflow

### Background

**Issue #2500:** Create a new workflow to automatically update dependencies weekly

**Agent Assignment:** @engineer-master (API engineering specialist)

**Files to Create/Modify:**
- `.github/workflows/update-dependencies.yml` (new workflow)
- `package.json` (update scripts)
- Documentation updates

Let's walk through exactly how @engineer-master uses ALL available instructions and context.

---

## 🚀 Phase 1: Initial Context Gathering

### Step 1.1: Agent Receives Assignment

**GitHub Actions Workflow:** `copilot-on-issue.yml` runs
```yaml
# Issue body created by workflow:
---
**🤖 Agent Assignment**

**@engineer-master** - Please use the engineer-master custom agent profile.

**Task:** Create automated dependency update workflow

**IMPORTANT**: Always mention **@engineer-master** by name in all conversations.
---
```

**What @engineer-master reads:**
1. ✅ Agent identity: `@engineer-master`
2. ✅ Task: Create workflow
3. ✅ Requirement: Use @mention in all outputs

---

### Step 1.2: Load Repository-Wide Instructions

**File Read:** `.github/copilot-instructions.md`

**What @engineer-master learns:**
```markdown
# GitHub Copilot – Chained Project Instructions

## Custom Agents System
- 13 specialized custom agents available
- @engineer-master specializes in API engineering
- Use systematic, rigorous approach

## Project Standards
- Follow existing patterns
- Write clean, maintainable code
- Include tests for new functionality

## Context System ⭐
Before starting work, check for `.context.md` files in:
- Your working directory
- Related directories

## Agent Mention Requirements
- ALWAYS use @agent-name syntax
- Include in PRs, commits, comments
```

**Key Takeaways for @engineer-master:**
- ✅ I'm a systematic, rigorous engineer
- ✅ I should check for context files
- ✅ I must use @engineer-master in all outputs
- ✅ Follow project standards

---

### Step 1.3: Check for Context Files

**Action:** @engineer-master looks for `.context.md` in working area

**File Read:** `.github/workflows/.context.md`

```markdown
# Context: Workflow Development

## Critical Requirements (Path-Specific Learning)
1. ⭐ NEVER push directly to main branch
2. ⭐ ALWAYS create PR for workflow changes
3. ⭐ ALWAYS include @agent-name attribution
4. ⭐ ALWAYS include workflow reference in created issues/PRs

## Common Pitfalls (Learned from Past Issues)
- Don't reuse branch names (causes conflicts)
- Always check for changes before creating PR
- Use timestamp + run ID in branch names
- Validate YAML syntax before committing

## Recommended Practices
- Use heredoc for multiline PR bodies
- Test workflows in feature branches first
- Include comprehensive error handling
- Document trigger conditions clearly
```

**Key Takeaways for @engineer-master:**
- ✅ MUST use PR-based workflow (not direct push)
- ✅ Branch naming: include timestamp + run ID
- ✅ Must include workflow reference in outputs
- ✅ Validate YAML before committing

---

### Step 1.4: Check Context Index

**File Read:** `.github/context-index.json`

```json
{
  "quick_reference": {
    "agent_mentions": "Always use @agent-name syntax",
    "branch_protection": "Never push directly to main, always create PR",
    "workflow_references": "Include workflow name and run ID in created issues/PRs",
    "context_awareness": "Check for .context.md files before starting"
  }
}
```

**Key Takeaways:**
- ✅ Quick reference confirms requirements
- ✅ Multiple reinforcement of key patterns

---

### Step 1.5: Load Path-Specific Instructions

Since @engineer-master will be working on `.github/workflows/*.yml`, the system automatically applies these instruction files:

#### A. `workflow-agent-assignment.instructions.md`
```markdown
---
applyTo:
  - ".github/workflows/copilot-*.yml"
  - ".github/workflows/*-agent-*.yml"
  - ".github/workflows/agent-*.yml"
---

# Agent Assignment Workflow Instructions

When creating workflows that assign work to agents:
1. MUST include @agent-name in issue body
2. MUST add "IMPORTANT: Always mention @agent-name"
3. MUST use @agent-name in all comments
```

**Applies to this task?** 🤔 Partially - new workflow might need agent assignment logic

#### B. `branch-protection.instructions.md`
```markdown
---
applyTo:
  - ".github/workflows/**/*.yml"
  - "**/*.yml"
---

# Branch Protection Rules

🛡️ PRIMARY RULE: Main branch is PROTECTED

NEVER push directly to main branch:
❌ FORBIDDEN: git push
❌ FORBIDDEN: git push origin main

ALWAYS create a PR:
✅ REQUIRED:
  - Create unique branch with timestamp
  - Commit changes to branch
  - Push to branch (not main)
  - Create PR via gh pr create
```

**Applies to this task?** ✅ YES - This workflow will modify the repo

**Key Takeaways:**
- ✅ MUST use PR-based approach
- ✅ Create unique branch name
- ✅ Use gh pr create command

#### C. `workflow-reference.instructions.md`
```markdown
---
applyTo:
  - ".github/workflows/**/*.yml"
---

# Workflow Reference Attribution

MANDATORY: When workflows create issues/PRs, include:

*🤖 Created by workflow: [${{ github.workflow }}](${{ github.server_url }}/.../runs/${{ github.run_id }})*
```

**Applies to this task?** ✅ YES - New workflow might create issues

**Key Takeaways:**
- ✅ Include workflow reference in outputs
- ✅ Use github.workflow and github.run_id variables

#### D. `agent-mentions.instructions.md`
```markdown
---
applyTo:
  - "**/*.yml"
  - "**/assign-copilot-to-issue.sh"
---

# Agent Mention Requirements

ALWAYS use @agent-name syntax:
✅ "@engineer-master will implement..."
❌ "The engineer agent will implement..."
```

**Applies to this task?** ✅ YES - All YAML files

**Key Takeaways:**
- ✅ Use @engineer-master in workflow comments
- ✅ Use @agent-name in any created issues

---

## 🧠 Phase 2: Synthesis & Planning

@engineer-master now has complete context from:
1. Repository-wide instructions (general guidance)
2. Path-specific instructions (workflow requirements)
3. Context files (historical learnings)
4. Agent identity (@engineer-master)

**@engineer-master's Mental Model:**

```
Task: Create dependency update workflow
Identity: @engineer-master (systematic, rigorous)

MUST DO:
✅ Create PR (not push to main)
✅ Include @engineer-master attribution everywhere
✅ Use unique branch name (timestamp + run_id)
✅ Include workflow reference if creating issues
✅ Validate YAML syntax
✅ Follow branch protection rules

LEARNED FROM PAST:
✅ Don't reuse branch names
✅ Check for changes before PR
✅ Use heredoc for multiline bodies
✅ Test in feature branch first

MY APPROACH (engineer-master):
✅ Systematic design first
✅ Rigorous implementation
✅ Comprehensive error handling
✅ Full documentation
```

---

## 💻 Phase 3: Implementation

### Step 3.1: Create Initial Plan

**Action:** @engineer-master runs `report_progress` to outline plan

```markdown
## 🎯 Task: Create Automated Dependency Update Workflow

**@engineer-master** is implementing a systematic dependency update solution.

### Plan (Following Path-Specific Instructions)

- [x] **Phase 1: Context Gathering** ✅
  - [x] Read repository-wide instructions
  - [x] Check .github/workflows/.context.md
  - [x] Review path-specific instruction files
  - [x] Synthesize requirements

- [ ] **Phase 2: Implementation**
  - [ ] Create .github/workflows/update-dependencies.yml
  - [ ] Follow branch protection rules (PR-based)
  - [ ] Include @engineer-master attribution
  - [ ] Validate YAML syntax
  - [ ] Test workflow

- [ ] **Phase 3: Documentation**
  - [ ] Document workflow in README
  - [ ] Update DATA_STORAGE_LIFECYCLE.md if needed

**@engineer-master** will use systematic approach per specialization.
```

**Notice:**
- ✅ @engineer-master mentioned multiple times
- ✅ References to context and instructions
- ✅ Systematic approach (engineer-master style)

---

### Step 3.2: Create Workflow File

**File:** `.github/workflows/update-dependencies.yml`

```yaml
name: Update Dependencies

# @engineer-master: Weekly dependency updates
# Following path-specific instructions for workflow development

on:
  schedule:
    - cron: '0 3 * * 1'  # Every Monday at 3 AM UTC
  workflow_dispatch:

jobs:
  update-dependencies:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      # @engineer-master: Systematic approach - check for updates first
      - name: Check for dependency updates
        id: check
        run: |
          npm outdated --json > outdated.json || true
          if [ -s outdated.json ]; then
            echo "has_updates=true" >> $GITHUB_OUTPUT
          else
            echo "has_updates=false" >> $GITHUB_OUTPUT
          fi
      
      # @engineer-master: Following branch-protection.instructions.md
      # NEVER push to main - always use PR
      - name: Create PR with updates
        if: steps.check.outputs.has_updates == 'true'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Configure git
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          
          # Create unique branch (learned from .context.md)
          TIMESTAMP=$(date +%Y%m%d-%H%M%S)
          BRANCH_NAME="deps-update/${TIMESTAMP}-${{ github.run_id }}"
          
          # Create branch (not pushing to main!)
          git checkout -b "$BRANCH_NAME"
          
          # Update dependencies
          npm update
          
          # Commit changes
          git add package.json package-lock.json
          git commit -m "chore: update dependencies (automated)
          
          Updates managed by @engineer-master automated workflow.
          
          Generated by workflow: ${{ github.workflow }}"
          
          # Push to NEW branch (following instructions)
          git push origin "$BRANCH_NAME"
          
          # Create PR (following workflow-reference.instructions.md)
          gh pr create \
            --title "chore: automated dependency updates - $(date +%Y-%m-%d)" \
            --body "## 📦 Automated Dependency Updates
          
          **@engineer-master** has detected available dependency updates.
          
          ### Changes
          This PR updates dependencies to their latest compatible versions.
          
          ### Testing
          - Automated tests will run on this PR
          - Review the changes before merging
          
          ### Attribution
          - **Agent**: @engineer-master
          - **Workflow**: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
          
          ---
          
          *🤖 Created by workflow: [${{ github.workflow }}](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})*" \
            --label "dependencies,automated,copilot" \
            --base main \
            --head "$BRANCH_NAME"
```

**@engineer-master's Implementation Checklist:**

✅ **Branch Protection (branch-protection.instructions.md)**
- ✅ Never pushed to main
- ✅ Created unique branch with timestamp + run_id
- ✅ Used `gh pr create` to create PR

✅ **Workflow Reference (workflow-reference.instructions.md)**
- ✅ Included workflow name in PR body
- ✅ Included workflow run link
- ✅ Added footer: "Created by workflow: ..."

✅ **Agent Mentions (agent-mentions.instructions.md)**
- ✅ Used @engineer-master in PR body
- ✅ Used @engineer-master in commit message
- ✅ Used @engineer-master in workflow comments

✅ **Context Learnings (.context.md)**
- ✅ Unique branch names (timestamp + run_id)
- ✅ Checked for changes before creating PR
- ✅ Used heredoc-style multiline PR body
- ✅ Included comprehensive error handling

✅ **Repository-Wide (copilot-instructions.md)**
- ✅ Followed systematic approach (engineer-master)
- ✅ Clean, maintainable code
- ✅ Comprehensive documentation in PR

---

### Step 3.3: Validate Implementation

**Action:** @engineer-master validates YAML (learned from context)

```bash
# Validate YAML syntax
yamllint .github/workflows/update-dependencies.yml

# Check workflow syntax
actionlint .github/workflows/update-dependencies.yml
```

**Result:** ✅ YAML is valid

---

### Step 3.4: Report Progress

**Action:** @engineer-master commits and pushes

```bash
git add .github/workflows/update-dependencies.yml
git commit -m "feat: add automated dependency update workflow

Implemented by @engineer-master following systematic approach:
- Weekly schedule (Mondays 3 AM UTC)
- PR-based updates (never push to main)
- Comprehensive attribution
- Workflow reference included

Follows:
- branch-protection.instructions.md
- workflow-reference.instructions.md
- agent-mentions.instructions.md
- .github/workflows/.context.md learnings

Generated by @engineer-master"

# Push to feature branch
git push origin copilot/implement-deps-workflow
```

**PR Created via report_progress:**
```markdown
## 🎯 Implement Automated Dependency Updates (@engineer-master)

**@engineer-master** has implemented a systematic dependency update workflow.

### Implementation

- [x] Created `.github/workflows/update-dependencies.yml`
- [x] Followed branch protection rules (PR-based approach)
- [x] Included @engineer-master attribution throughout
- [x] Added workflow reference as required
- [x] Validated YAML syntax
- [x] Tested workflow logic

### Compliance with Instructions

**Repository-Wide Instructions:**
✅ Systematic approach (engineer-master specialization)
✅ Clean, maintainable code
✅ Comprehensive documentation

**Path-Specific Instructions:**
✅ branch-protection.instructions.md - PR-based workflow
✅ workflow-reference.instructions.md - Workflow attribution
✅ agent-mentions.instructions.md - @engineer-master mentions
✅ workflow-agent-assignment.instructions.md - Agent attribution

**Context Learnings:**
✅ Unique branch names (timestamp + run_id)
✅ Check for changes before PR
✅ Heredoc-style PR body
✅ Comprehensive error handling

### How It Works

1. Runs weekly on Mondays at 3 AM UTC
2. Checks for dependency updates
3. If updates available:
   - Creates unique branch
   - Updates dependencies
   - Creates PR with full attribution
4. Manual trigger also available

### Testing

Workflow can be tested via workflow_dispatch.

---

**Implemented by @engineer-master** 🤖
```

---

## 📊 Phase 4: Instruction Usage Summary

### Complete Instruction Stack Used by @engineer-master

```
┌─────────────────────────────────────────────────────┐
│ LAYER 1: Agent Identity                            │
│ @engineer-master (systematic, rigorous)            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 2: Repository-Wide Instructions              │
│ .github/copilot-instructions.md                    │
│ - Project standards                                 │
│ - Custom agents system                              │
│ - Context system awareness                          │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 3: Path-Specific Instructions (Auto-Applied) │
│ .github/instructions/                               │
│ ├─ branch-protection.instructions.md (PR required) │
│ ├─ workflow-reference.instructions.md (attribution)│
│ ├─ agent-mentions.instructions.md (@engineer-...)  │
│ └─ workflow-agent-assignment.instructions.md       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 4: Context Files (Manual Check)              │
│ .github/workflows/.context.md                      │
│ - Historical learnings (branch names, testing)     │
│ - Common pitfalls (reusing branches)               │
│ - Recommended practices (heredoc, validation)      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 5: Context Index (Quick Reference)           │
│ .github/context-index.json                         │
│ - Quick lookup of key patterns                      │
│ - Cross-reference to detailed context              │
└─────────────────────────────────────────────────────┘
                        ↓
                 IMPLEMENTATION
              (Workflow Created)
```

### Instruction Application Matrix

| Instruction Source | Type | Applied? | How? |
|-------------------|------|----------|------|
| `.github/copilot-instructions.md` | Repository-wide | ✅ Auto | Copilot reads automatically |
| `branch-protection.instructions.md` | Path-specific | ✅ Auto | Matches `**/*.yml` pattern |
| `workflow-reference.instructions.md` | Path-specific | ✅ Auto | Matches `.github/workflows/**` |
| `agent-mentions.instructions.md` | Path-specific | ✅ Auto | Matches `**/*.yml` pattern |
| `workflow-agent-assignment.instructions.md` | Path-specific | ⚠️ Partial | Matches if creating agent workflows |
| `.github/workflows/.context.md` | Context | ✅ Manual | @engineer-master checked before starting |
| `.github/context-index.json` | Index | ✅ Manual | @engineer-master referenced for overview |
| Agent definition `.github/agents/engineer-master.md` | Agent-specific | ✅ Auto | Defines @engineer-master approach |

---

## 🎓 Key Insights from Scenario

### 1. Layered Instruction System

Instructions work in layers:
```
Agent Identity
    ↓ (provides personality and approach)
Repository-Wide Instructions
    ↓ (provides general standards)
Path-Specific Instructions
    ↓ (provides file-specific rules)
Context Files
    ↓ (provides historical learnings)
Implementation
```

### 2. Automatic vs. Manual Application

**Automatic (via Copilot):**
- Repository-wide instructions
- Path-specific `.instructions.md` files
- Agent definitions

**Manual (agent checks):**
- `.context.md` files
- Context index
- Related documentation

### 3. Reinforcement Through Repetition

Key requirements appear in multiple places:
- **@agent-name mentions:** 
  - copilot-instructions.md
  - agent-mentions.instructions.md
  - context-index.json
  - .context.md files
- **Branch protection:**
  - branch-protection.instructions.md
  - .github/workflows/.context.md
  - context-index.json

This redundancy is **intentional** - reinforces critical patterns!

### 4. Context Provides "Why"

**Instructions say:** "NEVER push to main"
**Context explains:** "We had Issue #1234 where this caused problems"

Context adds historical reasoning to enforcement rules.

### 5. Agent Personality Matters

**@engineer-master approach:**
- Systematic planning first
- Rigorous implementation
- Comprehensive documentation
- Full error handling

vs. **@accelerate-master approach:**
- Performance-focused
- Optimization priority
- Benchmarking included

Same instructions, different execution style!

---

## 🔄 Complete Workflow Diagram

```
┌──────────────────────────────────────────────────────────┐
│ 1. ISSUE CREATED: "Create dependency update workflow"   │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 2. AGENT ASSIGNED: @engineer-master                     │
│    - Issue body updated with @engineer-master directive │
│    - Agent identity established                          │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 3. COPILOT EXECUTES in GitHub Actions Runner            │
│    - Reads issue body: "I am @engineer-master"          │
│    - Loads .github/agents/engineer-master.md             │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 4. LOAD REPOSITORY-WIDE INSTRUCTIONS (Auto)             │
│    - .github/copilot-instructions.md                    │
│    - Project standards, custom agents info               │
│    - "Check .context.md before starting"                 │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 5. CHECK CONTEXT FILES (Manual - Agent Choice)          │
│    - Reads .github/workflows/.context.md                │
│    - Learns: "Never push to main" (from past issue)     │
│    - Learns: "Use timestamp in branch names"            │
│    - Learns: "Validate YAML before committing"          │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 6. COPILOT AUTO-APPLIES PATH-SPECIFIC INSTRUCTIONS      │
│    When working on .github/workflows/update-deps.yml:   │
│    ├─ branch-protection.instructions.md (matches *.yml) │
│    ├─ workflow-reference.instructions.md (matches path) │
│    ├─ agent-mentions.instructions.md (matches *.yml)    │
│    └─ workflow-agent-assignment.instructions.md         │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 7. SYNTHESIZE ALL INSTRUCTIONS                          │
│    @engineer-master mental model:                        │
│    ├─ MUST: Use PR-based workflow (branch-protection)   │
│    ├─ MUST: Include @engineer-master (agent-mentions)   │
│    ├─ MUST: Include workflow ref (workflow-reference)   │
│    ├─ LEARNED: Use timestamp branches (context)         │
│    ├─ LEARNED: Validate YAML first (context)            │
│    └─ STYLE: Systematic approach (engineer-master)      │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 8. IMPLEMENT WORKFLOW                                    │
│    - Creates update-dependencies.yml                     │
│    - Follows ALL instruction requirements                │
│    - Applies historical learnings from context           │
│    - Uses @engineer-master systematic style              │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 9. CREATE PR (Following Instructions)                   │
│    - Unique branch: deps-update/20251117-033000-123456  │
│    - PR body: Includes @engineer-master attribution     │
│    - PR body: Includes workflow reference                │
│    - PR body: Explains systematic approach               │
│    - Labels: automated, copilot, dependencies            │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 10. COMMENT ON ORIGINAL ISSUE                           │
│     "@engineer-master has completed the workflow         │
│     implementation. See PR #XXX for details."            │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ 11. LEARNINGS CAPTURED (Future Context Updates)         │
│     - Success pattern documented                         │
│     - Added to knowledge graph                           │
│     - Next context update includes this learning         │
└──────────────────────────────────────────────────────────┘
```

---

## 💡 Different Agent, Different Approach

### Same Task with @accelerate-master (Performance Specialist)

```markdown
## Implementation Differences

**@engineer-master (systematic):**
- Comprehensive planning phase
- Full documentation upfront
- Rigorous testing approach
- Complete error handling

**@accelerate-master (performance-focused):**
- Benchmark dependency update time
- Optimize npm update execution
- Measure PR creation performance
- Cache optimization strategies
```

**Same Instructions Applied:**
✅ Branch protection (both)
✅ Workflow reference (both)
✅ Agent mentions (both use @agent-name)
✅ Context learnings (both check .context.md)

**Different Execution:**
- @engineer-master: Systematic, comprehensive
- @accelerate-master: Performance-optimized, benchmarked

---

## 📚 Summary

### How Agents Use the Complete Instruction Set

1. **Agent Identity** - Defines approach and style
2. **Repository-Wide** - General standards and patterns
3. **Path-Specific (Auto)** - File-specific requirements enforced by Copilot
4. **Context Files (Manual)** - Historical learnings checked by agent
5. **Context Index** - Quick reference for key patterns
6. **Synthesis** - Agent combines all layers into implementation plan

### Benefits of Layered System

✅ **Comprehensive Coverage** - Multiple reinforcement of critical patterns
✅ **Flexibility** - Different agents apply same rules differently
✅ **Learning** - Context files evolve with project history
✅ **Enforcement** - Auto-applied rules prevent violations
✅ **Guidance** - Manual context provides reasoning

### Key Insight

**Instructions are not just rules - they're a knowledge system that:**
- Enforces requirements (path-specific .instructions.md)
- Provides context (historical .context.md)
- Defines identity (agent definitions)
- Establishes standards (repository-wide)
- Offers quick reference (context index)

**Result:** Agents produce consistent, high-quality work while maintaining individual approaches!

---

**Scenario documented by @investigate-champion** 🤖

*Demonstrating the power of layered instruction systems* 📚
