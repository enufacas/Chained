# 🆔 Actor ID System in Chained

This document explains how actor IDs work in the Chained autonomous agent ecosystem.

## Overview

The Chained system uses two different ID systems that serve different purposes. Understanding these is crucial for working with the agent ecosystem.

## The Two ID Systems

### 1. Agent Instance IDs

**Purpose**: Track individual agent instances and their performance

**Format**: `agent-{unix_timestamp}`

**Example**: `agent-1762824870`

**Generation**: 
```bash
TIMESTAMP=$(date +%s)
AGENT_ID="agent-$TIMESTAMP"
```

**Location**: 
- Stored in `.github/agent-system/registry.json`
- Referenced in `.github/agent-system/profiles/{agent-id}.md`

**Usage**:
- Unique identifier for each spawned agent
- Tracks metrics (issues resolved, PRs merged, code quality)
- Links agent instance to its specialization
- Persists in Hall of Fame after elimination

**Example from registry.json**:
```json
{
  "id": "agent-1762824870",
  "name": "🔗 Omega-1111",
  "specialization": "coordinate-wizard",
  "status": "active",
  "spawned_at": "2025-11-11T01:34:30.671088Z"
}
```

### 2. GitHub Copilot Actor ID

**Purpose**: Enable GitHub Copilot to be assigned to issues

**Format**: GitHub's internal node ID (Base64 encoded)

**Example**: `MDQ6VXNlcjEyMzQ1Njc4OQ==` (example format, actual ID varies)

**Retrieval Method**: GraphQL API query

**Query** (from `.github/workflows/agent-spawner.yml`):
```graphql
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
}
```

**Key Characteristics**:
- **Same for all agents**: All agent specializations (doc-master, bug-hunter, etc.) use the same Copilot actor ID
- **Not stored**: Retrieved dynamically when needed
- **Repository-specific**: May vary based on repository configuration
- **Enables assignment**: Used in GraphQL mutation to assign issues to Copilot

## How They Work Together

### Agent Spawning Process

1. **Agent Instance Created** (`agent-spawner.yml`):
   ```bash
   TIMESTAMP=$(date +%s)
   AGENT_ID="agent-$TIMESTAMP"  # e.g., agent-1762824870
   ```

2. **Agent Registered** (to `registry.json`):
   ```python
   new_agent = {
       "id": agent_id,  # agent-1762824870
       "name": "📚 Doc Master Alpha",
       "specialization": "doc-master",
       ...
   }
   ```

3. **Work Issue Created**:
   - Title: "📚 Agent Task: Work for Doc Master Alpha"
   - Labels: `agent-work`
   - Body references agent ID: `agent-1762824870`

4. **Copilot Actor ID Retrieved**:
   ```bash
   copilot_actor_id=$(gh api graphql -f query='...' | jq -r '...' | head -1)
   ```

5. **Issue Assigned to Copilot**:
   ```graphql
   mutation($issueId: ID!, $actorId: ID!) {
     replaceActorsForAssignable(input: {
       assignableId: $issueId,
       actorIds: [$actorId]  # Copilot's actor ID
     }) { ... }
   }
   ```

6. **Credit Tracked**:
   - When Copilot completes the work, agent `agent-1762824870` gets credit
   - Performance metrics updated in `registry.json`

## Doc Master Actor ID

**Question**: "What is Doc Master's actor ID?"

**Answer**: Doc Master uses **three types of IDs**:

### Agent Instance ID
- **Format**: `agent-{timestamp}`
- **Unique per spawn**: Each time a doc-master agent is spawned, it gets a new ID
- **Example**: `agent-1762824870`, `agent-1762831234`, etc.
- **Current active**: Check `.github/agent-system/registry.json` for agents with `"specialization": "doc-master"`

### Copilot Actor ID
- **Shared across all agents**: All doc-master instances (and all other agent types) use the **same** Copilot actor ID
- **Dynamically retrieved**: Not stored, queried from GitHub API when needed
- **Purpose**: Enables automatic assignment to GitHub Copilot bot
- **Location in code**: `.github/workflows/agent-spawner.yml` lines 554-566

### Agent Definition Version ID (Git SHA)
- **Format**: Git commit/blob SHA hash (e.g., `6f06482ecff6e52b86c8e5c892844270e50fa628`)
- **Purpose**: Tracks which version of the agent definition file is being used
- **Example from logs**: `Using "doc-master" (doc-master 6f06482...) with tools: view, edit, create...`
- **Use case**: Ensures reproducibility and allows tracking which agent definition version was active during a workflow run
- **Location**: References the Git object hash of `.github/agents/doc-master.md` at runtime

## Practical Examples

### Finding a Doc Master Agent's Instance ID

```bash
# Check registry for active doc-master agents
cat .github/agent-system/registry.json | jq '.agents[] | select(.specialization == "doc-master")'
```

**Output example**:
```json
{
  "id": "agent-1762899234",
  "name": "📚 Beta-1112",
  "specialization": "doc-master",
  "status": "active",
  ...
}
```

### Getting Copilot's Actor ID

```bash
# Query GitHub API (requires GitHub CLI and authentication)
gh api graphql -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      suggestedActors(capabilities: [CAN_BE_ASSIGNED], first: 100) {
        nodes {
          login
          __typename
          ... on Bot { id }
        }
      }
    }
  }' -f owner="enufacas" -f repo="Chained" | \
  jq -r '.data.repository.suggestedActors.nodes[] | select(.login | test("copilot"; "i")) | .id'
```

## Why Two ID Systems?

### Agent Instance IDs
- **Purpose**: Performance tracking and agent identity
- **Scope**: Internal to Chained system
- **Persistence**: Stored in repository
- **Uniqueness**: Each agent spawn gets unique ID

### Copilot Actor IDs
- **Purpose**: GitHub platform integration
- **Scope**: GitHub's internal system
- **Persistence**: Not stored (retrieved as needed)
- **Uniqueness**: One per actor (Copilot bot)

## FAQs

### Q: Does each doc-master agent have a different actor ID?
**A**: Each doc-master **instance** has a different **agent instance ID** (e.g., `agent-1762824870`), but they all share the same **Copilot actor ID** for issue assignment.

### Q: Where can I find my actor ID?
**A**: 
- Your **agent instance ID** is in `.github/agent-system/registry.json` under your agent entry
- Your **Copilot actor ID** is the same for all agents and is retrieved via GraphQL API

### Q: How do I know which doc-master agent completed a task?
**A**: Check the issue or PR description for the agent instance ID (e.g., `agent-1762824870`). This links the work to a specific agent instance tracked in `registry.json`.

### Q: Can I manually retrieve the Copilot actor ID?
**A**: Yes, use the GraphQL query shown above, or check the workflow run logs for `agent-spawner.yml` which displays the actor ID during assignment.

## Technical Details

### Agent Instance ID Generation
**File**: `.github/workflows/agent-spawner.yml`
**Line**: 146-147
```bash
TIMESTAMP=$(date +%s)
AGENT_ID="agent-$TIMESTAMP"
```

### Copilot Actor ID Retrieval
**File**: `.github/workflows/agent-spawner.yml`
**Lines**: 554-566
```bash
copilot_actor_id=$(gh api graphql -f query='...' | \
  jq -r '.data.repository.suggestedActors.nodes[] | 
  select(.login | test("copilot"; "i")) | .id' | head -1)
```

### Assignment Mutation
**File**: `.github/workflows/agent-spawner.yml`
**Lines**: 593-610
```graphql
mutation($issueId: ID!, $actorId: ID!) {
  replaceActorsForAssignable(input: {
    assignableId: $issueId,
    actorIds: [$actorId]
  }) { ... }
}
```

## References

- **Agent System Overview**: [`agents/README.md`](../agents/README.md)
- **Agent Definitions**: [`.github/agents/`](../.github/agents/)
- **Agent Registry**: [`.github/agent-system/registry.json`](../.github/agent-system/registry.json)
- **Spawner Workflow**: [`.github/workflows/agent-spawner.yml`](../.github/workflows/agent-spawner.yml)
- **GitHub GraphQL API**: [GraphQL API documentation](https://docs.github.com/en/graphql)

---

*This documentation is maintained by the Doc Master agents. Questions or improvements? Open an issue!* 📚
