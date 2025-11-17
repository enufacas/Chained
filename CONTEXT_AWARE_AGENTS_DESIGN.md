# Context-Aware Agent Instructions System - Design Document

> **Prepared by:** @investigate-champion (Ada - Visionary and analytical AI agent)  
> **Date:** 2025-11-17  
> **Status:** Design Proposal

## 🎯 Executive Summary

This document proposes a system for providing custom agents with rich historical context when they receive work assignments, leveraging existing learnings data (discussions, knowledge graph) without overwhelming the context window.

## 🔍 Problem Statement

Currently, when custom agents receive work assignments:
- They have minimal context about past work in similar areas
- They don't easily access historical decisions and patterns
- The valuable learnings data (discussions, knowledge graph) is underutilized
- Agents can't efficiently "look up and around" at their world state

**Challenge:** How do we provide useful historical context without:
- Overwhelming the LLM context window (causing hallucinations/rot)
- Slowing down agent response time
- Creating maintenance burden

## 📊 Available Data Sources

### 1. Discussion Files (`learnings/discussions/`)
- **Format:** JSON files per issue
- **Content:** 
  - Insights (agent_behavior, technical, process)
  - Key decisions
  - Patterns identified
  - Confidence scores
  - Timestamps
- **Size:** ~75 insights across discussions
- **Value:** Historical context about past issues and solutions

### 2. Knowledge Graph (`learnings/discussions/knowledge_graph.json`)
- **Format:** Single JSON file
- **Content:**
  - 75 insights (deduplicated)
  - 133 connections between insights
  - Similarity scores
  - Insight types: agent_behavior, technical, process
- **Value:** Relationships between concepts and patterns

### 3. Learning Files (`learnings/*.json`)
- **Format:** JSON files from external sources
- **Content:** TLDR, Hacker News, GitHub trending, combined analysis
- **Value:** External tech trends and innovations

### 4. Analysis Files (`analysis/*.json`)
- **Format:** JSON files
- **Content:** Code archaeology, patterns, metrics
- **Value:** Historical code patterns and evolution

## 💡 Design Options

### Option 1: Path-Specific Context Summaries (RECOMMENDED)

**Concept:** Create lightweight `.context.md` files in strategic locations that summarize relevant historical insights.

**Implementation:**
```
.github/workflows/.context.md      # Context for workflow changes
.github/agents/.context.md          # Context for agent system
tools/.context.md                   # Context for tooling
learnings/.context.md               # Context for learning system
```

**Pros:**
✅ Lightweight and focused
✅ Easy to maintain
✅ Doesn't overwhelm context window
✅ Can be version controlled
✅ Easy for agents to discover

**Cons:**
❌ Requires manual curation/updates
❌ May become stale

**Mitigation:** Create a workflow to auto-regenerate context summaries weekly

### Option 2: Dynamic Context Injection via Instructions

**Concept:** Extend `.github/instructions/*.instructions.md` files to include historical context relevant to that path scope.

**Example:**
```markdown
---
applyTo:
  - ".github/workflows/**"
---

# Workflow Development Context

## Historical Patterns
- Agents typically need @mention enforcement (see issue #1460)
- Branch protection requires PR-based workflows (see issue #1450)
- Workflow references should include run IDs (see discussion_1486)

## Common Pitfalls
...
```

**Pros:**
✅ Leverages existing instruction file system
✅ Automatically applied when working in scope
✅ Path-specific and targeted
✅ Already integrated with Copilot

**Cons:**
❌ Instructions meant for rules, not historical data
❌ Could make instruction files too large
❌ Mixing concerns (rules vs. history)

### Option 3: Lightweight Context Index

**Concept:** Create a simple index file that agents can query for relevant context.

**File:** `.github/context-index.json`

**Structure:**
```json
{
  "workflow_changes": {
    "summary": "Key patterns and decisions about workflows",
    "insights": ["insight_1460_...", "insight_1461_..."],
    "key_learnings": [
      "Always use PR-based workflow for main branch",
      "Include workflow references in created issues"
    ]
  },
  "agent_system": {
    "summary": "Agent behavior and coordination patterns",
    "insights": [...],
    "key_learnings": [...]
  }
}
```

**Pros:**
✅ Centralized and queryable
✅ Can be programmatically generated
✅ Easy to update
✅ Doesn't pollute instruction files

**Cons:**
❌ Requires agents to actively query it
❌ Not automatically injected
❌ Needs tooling to use effectively

### Option 4: Agent-Specific Context Bundles

**Concept:** Create context bundles tailored to each agent's specialization.

**Example:**
```
.github/agents/context/
  troubleshoot-expert-context.md
  engineer-master-context.md
  support-master-context.md
```

**Content:** Historical insights relevant to that agent's domain

**Pros:**
✅ Highly targeted to agent needs
✅ Can be rich and detailed
✅ Agents automatically get relevant context

**Cons:**
❌ High maintenance burden
❌ Duplication across agents
❌ Not path-aware

## 🎯 Recommended Solution: Hybrid Approach

Combine Options 1 and 3 for maximum effectiveness:

### Phase 1: Path-Specific Context Summaries
1. Create `.context.md` files in key directories
2. Populate with curated historical insights
3. Keep them lightweight (< 500 words each)

### Phase 2: Context Index for Discovery
1. Create `.github/context-index.json` 
2. Link to detailed context files
3. Include quick reference summaries

### Phase 3: Integration with Instructions
1. Add lightweight "context awareness" section to existing instruction files
2. Point to context files for more detail
3. Don't embed full history in instructions

## 📝 Implementation Plan

### Step 1: Create Core Context Files

**Files to create:**
1. `.github/workflows/.context.md` - Workflow development patterns
2. `.github/agents/.context.md` - Agent system insights
3. `.github/instructions/.context.md` - Instruction file patterns
4. `tools/.context.md` - Tooling development insights
5. `learnings/.context.md` - Learning system patterns

**Content template:**
```markdown
# Context: [Area Name]

> Auto-generated from learnings and discussions
> Last updated: [timestamp]

## Key Historical Insights

### Pattern: [Pattern Name]
- **Context:** [Where this applies]
- **Insight:** [What was learned]
- **Source:** [Issue #, Discussion file]
- **Confidence:** [High/Medium/Low]

### Decision: [Decision Name]
- **Context:** [What was decided]
- **Rationale:** [Why]
- **Source:** [Reference]

## Common Pitfalls
- [List of things to avoid]

## Recommended Practices
- [List of recommended approaches]

## Related Resources
- [Links to full discussions]
- [Links to knowledge graph]
```

### Step 2: Create Context Index

**File:** `.github/context-index.json`

**Structure:**
```json
{
  "version": "1.0",
  "last_updated": "2025-11-17T00:00:00Z",
  "contexts": {
    "workflows": {
      "path": ".github/workflows/.context.md",
      "summary": "Workflow development patterns and decisions",
      "key_insights": 12,
      "last_updated": "2025-11-17T00:00:00Z"
    },
    "agents": {
      "path": ".github/agents/.context.md",
      "summary": "Agent system behavior and coordination",
      "key_insights": 15,
      "last_updated": "2025-11-17T00:00:00Z"
    }
  },
  "quick_reference": {
    "agent_mentions": "Always use @agent-name syntax",
    "branch_protection": "Never push directly to main, always create PR",
    "workflow_references": "Include workflow name in created issues/PRs"
  }
}
```

### Step 3: Enhance Main Copilot Instructions

Add section to `.github/copilot-instructions.md`:

```markdown
## 🗺️ Context Awareness System

When working on a task, agents should be aware of relevant historical context:

### Available Context Files

- **`.github/workflows/.context.md`** - Workflow development patterns
- **`.github/agents/.context.md`** - Agent system insights  
- **`tools/.context.md`** - Tooling development best practices
- **`.github/context-index.json`** - Index of all context resources

### How to Use Context

1. **Before starting work:** Check if a `.context.md` file exists in the directory
2. **Reference relevant patterns:** Apply learned patterns from past work
3. **Avoid known pitfalls:** Review common mistakes to avoid
4. **Link to history:** Reference specific discussions when relevant

### Context File Locations

Context files are placed in directories to provide historical insights:
- They summarize key learnings from past issues and discussions
- They highlight common patterns and anti-patterns
- They reference source discussions for deep dives

**Note:** Context files are curated summaries, not comprehensive histories. 
For full details, consult the `learnings/discussions/` directory.
```

### Step 4: Create Context Generation Tool

**File:** `tools/generate-context-summaries.py`

**Purpose:** Auto-generate context files from learnings data

**Features:**
- Parse knowledge graph and discussions
- Group insights by relevant areas (workflows, agents, tools, etc.)
- Generate markdown summaries
- Update context index

**Usage:**
```bash
python tools/generate-context-summaries.py --update-all
```

### Step 5: Add Workflow for Maintenance

**File:** `.github/workflows/update-context-summaries.yml`

**Trigger:** Weekly, or when learnings directory changes

**Actions:**
1. Run context generation tool
2. Create PR with updated context files
3. Auto-merge if no conflicts

## 📏 Success Metrics

### Qualitative
- Agents reference historical patterns in their work
- Fewer repeated mistakes from past issues
- Better decision-making based on prior learnings

### Quantitative
- Context files referenced in PR descriptions
- Reduction in similar issues being filed
- Agent performance scores improve

## 🔒 Constraints and Considerations

### Context Window Management
- Keep each context file under 500 words
- Use summaries, not full transcripts
- Link to detailed sources for deep dives

### Maintenance
- Auto-generate weekly to keep fresh
- Manual curation for quality
- Version control for accountability

### Discovery
- Make context files obvious (naming convention)
- Document in main instructions
- Index for easy lookup

## 🚀 Next Steps

1. ✅ Create design document (this file)
2. ⏭️ Implement context file templates
3. ⏭️ Generate initial context files manually
4. ⏭️ Create context generation tool
5. ⏭️ Update copilot-instructions.md
6. ⏭️ Create maintenance workflow
7. ⏭️ Test with real agent assignments
8. ⏭️ Gather feedback and iterate

## 📚 References

- `learnings/discussions/knowledge_graph.json` - Source data
- `learnings/discussions/*.json` - Discussion insights
- `.github/instructions/README.md` - Instruction file system
- `docs/DATA_STORAGE_LIFECYCLE.md` - Data architecture

---

*Designed by @investigate-champion for the Chained autonomous AI ecosystem* 🤖
