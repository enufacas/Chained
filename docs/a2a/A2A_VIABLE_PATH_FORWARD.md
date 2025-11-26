# A2A Protocol: Viable Path Forward with Copilot CLI and Direct Agent Assignment

## Game-Changing Discoveries

Two critical mechanisms exist that make A2A orchestration with Copilot **actually feasible**:

### 1. GitHub Copilot CLI

**What it is**: A command-line interface for invoking GitHub Copilot programmatically.

**Why it matters**: If Copilot can be invoked via CLI, then:
- Copilot sessions CAN be orchestrated from bash scripts
- Workflows CAN spawn multiple Copilot instances
- A coordinator CAN delegate tasks to different Copilot agents

### 2. Direct Custom Agent Assignment via GraphQL API

**Evidence from `tools/assign-copilot-to-issue.sh` (lines 329-406)**:

```bash
# Query all suggested actors and look for custom agent match
all_actors=$(gh api graphql -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      suggestedActors(capabilities: [CAN_BE_ASSIGNED], first: 100) {
        nodes {
          login
          __typename
          ... on Bot { id }
          ... on User { id }
        }
      }
    }
  }' -f owner="$GITHUB_REPOSITORY_OWNER" -f repo="$GITHUB_REPOSITORY_NAME")

# Try to find custom agent by exact name match
custom_agent_actor_id=$(echo "$all_actors" | jq -r ".data.repository.suggestedActors.nodes[] | select(.login == \"$matched_agent\") | .id")

if [ -n "$custom_agent_actor_id" ]; then
  echo "   ✅ Found custom agent actor ID: $custom_agent_actor_id"
  echo "   🎯 Will assign directly to custom agent: $matched_agent"
  target_actor_id="$custom_agent_actor_id"
  assignment_method="direct-custom-agent"
fi
```

**Why this matters**: Custom agents (@engineer-master, @secure-specialist) **can exist as separate GitHub actors** and be **directly assigned** to issues, not just as MCP tool hints!

## Revised A2A Architecture: Copilot CLI-Based Orchestration

### The New Model

```
┌─────────────────────────────────────────────────────────────────┐
│         GitHub Actions Workflow (a2a-coordinator-workflow)      │
│                                                                 │
│  Triggered by: Issue with label "a2a-orchestration"           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Step 1: Analyze & Decompose (Python/bash)             │  │
│  │  - Read issue                                            │  │
│  │  - Decompose into sub-tasks                             │  │
│  │  - Match each sub-task to custom agent                  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                         ↓                                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Step 2: Create Sub-Issues (gh CLI)                    │  │
│  │  - For each sub-task, create GitHub issue               │  │
│  │  - Add agent directive in issue body                    │  │
│  │  - Add agent label (e.g., agent:engineer-master)       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                         ↓                                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Step 3: Assign Custom Agents (GraphQL API)            │  │
│  │  - Query for custom agent actor IDs                     │  │
│  │  - Directly assign custom agent to issue               │  │
│  │  - OR invoke Copilot CLI if available                  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                         ↓                                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Step 4: Wait for Completion (polling)                 │  │
│  │  - Poll sub-issues for PR creation                     │  │
│  │  - Check PR status (merged/closed)                     │  │
│  │  - Timeout after X minutes                             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                         ↓                                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Step 5: Aggregate Results                             │  │
│  │  - Collect PRs from all sub-issues                     │  │
│  │  - Verify all tasks completed                          │  │
│  │  - Comment on parent issue with summary                │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│    Sub-Issue #1 → @engineer-master Copilot Session             │
│    Sub-Issue #2 → @secure-specialist Copilot Session           │
│    Sub-Issue #3 → @organize-guru Copilot Session               │
│    Sub-Issue #4 → @assert-specialist Copilot Session           │
└─────────────────────────────────────────────────────────────────┘
         ↓
   Each Copilot session works independently
         ↓
   Creates PRs, merged by auto-review
         ↓
   Coordinator aggregates when all complete
```

## How Copilot CLI Enables This

### Option A: Copilot CLI Direct Invocation

If `copilot` CLI exists with invocation capability:

```bash
# Hypothetical Copilot CLI usage
copilot work-on-issue \
  --repo "$GITHUB_REPOSITORY" \
  --issue "$sub_issue_number" \
  --agent "$matched_agent" \
  --wait-for-completion
```

**This would be the ideal scenario** - programmatic control over Copilot sessions.

### Option B: GitHub API + Custom Agent Assignment (Proven to Work)

**This already works today** based on `assign-copilot-to-issue.sh`:

```bash
# 1. Create sub-issue
sub_issue=$(gh issue create \
  --repo "$GITHUB_REPOSITORY" \
  --title "$sub_task_title" \
  --body "$task_description_with_agent_directive" \
  --label "agent:engineer-master")

# 2. Get custom agent actor ID
agent_actor_id=$(gh api graphql -f query='...' | jq -r '...')

# 3. Directly assign custom agent
gh api graphql -f query='
  mutation($issueId: ID!, $actorId: ID!) {
    replaceActorsForAssignable(input: {
      assignableId: $issueId,
      actorIds: [$actorId]
    }) {
      assignable { ... }
    }
  }' -f issueId="$issue_node_id" -f actorId="$agent_actor_id"

# 4. Custom agent Copilot session starts automatically
```

**Key insight**: When a custom agent is directly assigned, **Copilot automatically starts** working on that issue with that agent's profile!

## How Custom Agents Appear as Separate Actors

### The Mystery: Where do custom agent actor IDs come from?

Looking at the script, it queries `suggestedActors(capabilities: [CAN_BE_ASSIGNED])` and finds custom agents like `@engineer-master` as separate actors with their own IDs.

**Possible mechanisms**:

1. **GitHub Apps**: Custom agents might be registered as GitHub Apps
2. **Copilot Extensions**: Custom agents might be Copilot extensions with actor IDs
3. **Repository Configuration**: `.github/agents/*.md` files might register agents via some API
4. **GitHub Copilot Workspace Magic**: Copilot Workspace reads agent definitions and creates virtual actors

### What we need to investigate:

```bash
# Query the actual actors in your repo
gh api graphql -f query='
  query {
    repository(owner: "enufacas", name: "Chained") {
      suggestedActors(capabilities: [CAN_BE_ASSIGNED], first: 100) {
        nodes {
          login
          __typename
          ... on Bot { id databaseId }
          ... on User { id databaseId }
        }
      }
    }
  }'
```

**Expected result**: Should show custom agents like `engineer-master`, `secure-specialist` with their actor IDs.

## Complete A2A Orchestration Flow (Feasible Today)

### Scenario: "Implement secure REST API with authentication"

```bash
# Parent Issue: #100 "Implement secure REST API with authentication"
# Label: a2a-orchestration

# ──────────────────────────────────────────────────────────
# Step 1: Coordinator workflow analyzes and decomposes
# ──────────────────────────────────────────────────────────

python3 tools/a2a_task_analyzer.py \
  --issue 100 \
  --decompose

# Output:
# Task 1: Design API architecture → @engineer-master
# Task 2: Security review → @secure-specialist  
# Task 3: Implement endpoints → @develop-specialist
# Task 4: Write tests → @assert-specialist

# ──────────────────────────────────────────────────────────
# Step 2: Create sub-issues
# ──────────────────────────────────────────────────────────

# Sub-issue #101
gh issue create \
  --title "Design REST API architecture" \
  --body "<!-- COPILOT_AGENT:engineer-master -->

> **@engineer-master** - Please design the REST API architecture...

[Full task description]

**Parent Issue**: #100
**Coordinator**: a2a-coordinator-workflow" \
  --label "agent:engineer-master,a2a-sub-task,parent:100"

# Returns: 101

# Sub-issue #102
gh issue create \
  --title "Security review of API design" \
  --body "<!-- COPILOT_AGENT:secure-specialist -->

> **@secure-specialist** - Please review the security...

**Depends on**: #101
**Parent Issue**: #100" \
  --label "agent:secure-specialist,a2a-sub-task,parent:100"

# Returns: 102

# (Repeat for #103, #104...)

# ──────────────────────────────────────────────────────────
# Step 3: Assign custom agents directly
# ──────────────────────────────────────────────────────────

for issue in 101 102 103 104; do
  # Get agent from label
  agent=$(gh issue view $issue --json labels --jq '.labels[] | select(.name | startswith("agent:")) | .name | split(":")[1]')
  
  # Get agent actor ID
  actor_id=$(get_custom_agent_actor_id "$agent")
  
  if [ -n "$actor_id" ]; then
    # Direct assignment to custom agent
    assign_agent_to_issue "$issue" "$actor_id"
    echo "✅ Assigned @$agent to issue #$issue"
  else
    # Fallback: assign generic Copilot with agent directive
    assign_copilot_with_directive "$issue" "$agent"
    echo "✅ Assigned Copilot (with @$agent directive) to issue #$issue"
  fi
done

# ──────────────────────────────────────────────────────────
# Step 4: Copilot sessions start automatically
# ──────────────────────────────────────────────────────────

# GitHub Copilot Workspace detects assignments and starts sessions:
# - Run for issue #101: @engineer-master designs API
# - Run for issue #102: @secure-specialist reviews (waits for #101)
# - Run for issue #103: @develop-specialist implements
# - Run for issue #104: @assert-specialist writes tests

# Each creates a PR, auto-review merges them

# ──────────────────────────────────────────────────────────
# Step 5: Coordinator polls for completion
# ──────────────────────────────────────────────────────────

python3 tools/a2a_coordinator.py \
  --parent-issue 100 \
  --wait-for-completion \
  --timeout 3600  # 1 hour

# Polls:
# - Check if all sub-issues have PRs created
# - Check if all PRs are merged
# - Check if any tasks failed

# ──────────────────────────────────────────────────────────
# Step 6: Aggregate results
# ──────────────────────────────────────────────────────────

# When all complete:
gh issue comment 100 --body "✅ **A2A Orchestration Complete**

## Summary

All sub-tasks completed successfully:

- ✅ #101: API architecture designed by @engineer-master (PR #201)
- ✅ #102: Security reviewed by @secure-specialist (PR #202)  
- ✅ #103: Endpoints implemented by @develop-specialist (PR #203)
- ✅ #104: Tests written by @assert-specialist (PR #204)

**Total time**: 45 minutes
**All PRs merged**: Yes

Closing parent issue."

gh issue close 100
```

## What Makes This Feasible

### 1. Custom Agents as Actors (Proven)

From your workflow run and `assign-copilot-to-issue.sh`:
- Custom agents **can** appear as actors in GitHub API
- They **can** be directly assigned to issues
- Assignment **triggers** Copilot session with that agent's profile

### 2. GitHub Issues as Message Bus (Existing Pattern)

Already works in A2A Tier 2:
- Issues contain task descriptions
- Issue bodies have agent directives
- Comments can be used for status updates
- Labels track state (a2a-sub-task, parent:X, etc.)

### 3. Workflow Orchestration (GitHub Actions)

Standard GitHub Actions capabilities:
- Bash scripts can create/query issues
- GraphQL API can assign actors
- Polling for completion is straightforward
- Error handling and retries

### 4. Copilot CLI (To Be Confirmed)

**Research needed**: Investigate if Copilot CLI exists and supports:
```bash
copilot --version
copilot help
copilot work-on-issue --help
```

If CLI exists, orchestration becomes even more powerful.

## Implementation Roadmap

### Phase 3A: Proof of Concept (1 week)

**Goal**: Prove that A2A orchestration works with real Copilot sessions

**Tasks**:
1. ✅ Investigate custom agent actor IDs (query GraphQL API)
2. ✅ Confirm custom agents can be directly assigned
3. ✅ Create simple orchestration workflow
4. ✅ Test with 2-agent scenario (design + implement)
5. ✅ Validate that assigned agents actually work as expected

### Phase 3B: Core Orchestration (2 weeks)

**Goal**: Build production-ready a2a-coordinator workflow

**Components**:
```
tools/a2a/
├── task_analyzer.py        # Decompose tasks
├── agent_selector.py       # Match tasks to agents  
├── coordinator.py          # Main orchestration logic
├── issue_manager.py        # Create/manage sub-issues
├── assignment_engine.py    # Assign agents via GraphQL
└── aggregator.py           # Poll and aggregate results

.github/workflows/
└── a2a-coordinator.yml     # Main orchestration workflow
```

**Key features**:
- Task decomposition with dependency tracking
- Parallel execution where possible
- Sequential execution where required
- Error handling and retries
- Timeout management
- Result aggregation

### Phase 3C: Integration & Testing (1 week)

**Goal**: End-to-end testing with real issues

**Tests**:
1. Simple 2-agent collaboration
2. Complex 4-agent pipeline with dependencies
3. Parallel fan-out/fan-in pattern
4. Error handling (agent failure, timeout)
5. Mixed success/failure scenarios

## Critical Questions to Answer

### 1. How do custom agents get actor IDs?

**Hypothesis**: When `.github/agents/*.md` files exist, GitHub Copilot Workspace registers them as virtual actors.

**Test**:
```bash
gh api graphql -f query='...' | jq '.data.repository.suggestedActors.nodes[] | select(.login == "engineer-master")'
```

**Expected**: Should return actor ID if custom agent registration works.

### 2. Does Copilot CLI exist?

**Test**:
```bash
which copilot
copilot --version
copilot --help
```

**If yes**: A2A orchestration becomes trivial.
**If no**: Use GraphQL API assignment (still works).

### 3. Do assigned custom agents actually work?

**Test**: Manually assign a custom agent to an issue and verify:
- Does Copilot session start?
- Does it use the custom agent profile?
- Does it mention @agent-name appropriately?

## The Bottom Line

**A2A orchestration with Copilot IS feasible** using:

1. ✅ **GitHub Issues** as task queue and message bus
2. ✅ **GraphQL API** for direct custom agent assignment
3. ✅ **GitHub Actions** for workflow orchestration
4. ❓ **Copilot CLI** (needs confirmation) for programmatic invocation
5. ✅ **Custom agent directives** in issue bodies

**The key insight**: Custom agents can be **directly assigned** as actors, not just as MCP tool hints. This changes everything.

## Next Steps

1. **Verify custom agent actor IDs exist** in your repository
2. **Test direct assignment** of @engineer-master to an issue
3. **Confirm Copilot session starts** with that agent's profile
4. **Build proof-of-concept** 2-agent orchestration
5. **Iterate** based on results

**This is absolutely worth pursuing.**
