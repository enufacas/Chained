# How Copilot Sessions Interact with A2A Protocol

## Executive Summary

This document explains how multiple Copilot agent sessions interact with the A2A (Agent-to-Agent) protocol framework, particularly focusing on how sessions take input and communicate with each other.

## Key Concepts

### 1. Copilot Session = GitHub Actions Workflow Run

Each Copilot agent execution is a **GitHub Actions workflow run**:
- Triggered by an event (issue creation, PR, workflow_dispatch)
- Runs in an isolated, ephemeral VM (GitHub Actions runner)
- Has no direct network access to other runners
- Can only communicate via GitHub API (outbound HTTPS)

### 2. Two Tiers of Communication

The A2A framework provides **two tiers** of agent-to-agent communication:

#### **Tier 1: Same-Runner (HTTP)** - Multiple agents in ONE Copilot session
- All agents run within a single workflow job
- Traditional A2A HTTP communication over localhost
- Fast (<1ms latency)
- Suitable for quick, coordinated tasks

#### **Tier 2: Cross-Runner (GitHub-mediated)** - Multiple agents in SEPARATE Copilot sessions
- Each agent runs in its own workflow job (separate runner)
- GitHub Issues/Comments act as message bus
- Slower (~5s polling latency)
- Suitable for long-running, parallel tasks

## How Sessions Take Input

### Tier 1: Same-Runner Sessions

**Scenario:** One Copilot session coordinating multiple local agents

```
┌─────────────────────────────────────────────────────────────┐
│              Single GitHub Actions Workflow Run             │
│                   (One Copilot Session)                      │
│                                                              │
│  INPUT: Issue body or workflow_dispatch parameters          │
│                          │                                   │
│                          ▼                                   │
│              ┌───────────────────────┐                       │
│              │  A2A-Coordinator      │                       │
│              │  (Copilot session)    │                       │
│              └───────────┬───────────┘                       │
│                          │                                   │
│           ┌──────────────┼──────────────┐                    │
│           │              │              │                    │
│           ▼              ▼              ▼                    │
│    ┌──────────┐   ┌──────────┐   ┌──────────┐              │
│    │ Agent A  │   │ Agent B  │   │ Agent C  │              │
│    │ HTTP     │◄─►│ HTTP     │◄─►│ HTTP     │              │
│    │ :9001    │   │ :9002    │   │ :9003    │              │
│    └──────────┘   └──────────┘   └──────────┘              │
│         │              │              │                      │
│         └──────────────┴──────────────┘                      │
│                       │                                      │
│                       ▼                                      │
│  OUTPUT: Combined results written to PR/Issue               │
└─────────────────────────────────────────────────────────────┘
```

**How input works:**
1. **Initial trigger**: Issue body contains the main task
2. **Coordinator reads**: Parses task, decomposes into subtasks
3. **Spawns agents**: Starts agent HTTP servers on localhost
4. **HTTP communication**: Agents communicate via localhost HTTP (traditional A2A)
5. **Results**: Coordinator collects results and writes to PR/Issue

**Example workflow:**
```yaml
# .github/workflows/a2a-tier1-orchestration.yml
on:
  issues:
    types: [labeled]  # Triggered when issue gets "a2a-tier1" label

jobs:
  orchestrate:
    runs-on: ubuntu-latest
    steps:
      - name: Parse issue task
        run: |
          # Issue body is INPUT
          issue_body="${{ github.event.issue.body }}"
          echo "Task: $issue_body"
      
      - name: Start discovery service
        run: python -m tools.a2a.discovery &
      
      - name: Start agent servers
        run: |
          # Start multiple agents on localhost
          python -m tools.a2a.agent_server engineer-master &
          python -m tools.a2a.agent_server secure-specialist &
          python -m tools.a2a.agent_server organize-guru &
      
      - name: Execute coordination
        run: |
          # Coordinator sends HTTP requests to agents
          python -m tools.a2a.orchestrate \
            --issue "${{ github.event.issue.number }}"
```

### Tier 2: Cross-Runner Sessions

**Scenario:** Multiple Copilot sessions, each running a different agent

```
┌──────────────────────────────────────────────────────────────┐
│                    GitHub Platform                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │      GitHub Issues = Message Bus                   │     │
│  │                                                     │     │
│  │  Issue #123: "Implement auth system"               │     │
│  │    Status: working                                 │     │
│  │    Assigned: @engineer-master                      │     │
│  │    Body: {A2A task payload}                        │     │
│  │    Comments:                                       │     │
│  │      - Agent started work...                       │     │
│  │      - Progress update...                          │     │
│  │      - Result: {completed}                         │     │
│  └──────────────────▲──────────────────────────────────┘     │
│                     │ GitHub API                             │
└─────────────────────┼────────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│Session 1 │    │Session 2 │    │Session 3 │
│          │    │          │    │          │
│A2A-Coord │    │Engineer  │    │Security  │
│          │    │Master    │    │Specialist│
│          │    │          │    │          │
│Creates   │    │Reads     │    │Reads     │
│Issue #123│    │Issue #123│    │Issue #124│
│          │    │Executes  │    │Executes  │
│Polls for │    │Comments  │    │Comments  │
│completion│    │result    │    │result    │
└──────────┘    └──────────┘    └──────────┘
```

**How input works:**

**1. Coordinator Session (Session 1):**
```python
# INPUT: Original issue or workflow_dispatch
issue_body = github.event.issue.body

# Parse and decompose
task = parse_task(issue_body)
subtasks = decompose(task)
# → ["design auth", "security review", "implement"]

# Create GitHub issues for each subtask (A2A messages)
for subtask in subtasks:
    issue = create_github_issue(
        title=f"A2A Task: {subtask.description}",
        body=json.dumps({
            "method": "tasks/execute",
            "params": {
                "task": subtask.description,
                "context": subtask.context
            }
        }),
        labels=["a2a-task", f"agent:{subtask.agent}"]
    )
    # This triggers the agent worker workflow
```

**2. Agent Session (Session 2 - triggered by issue creation):**
```python
# INPUT: Issue body contains A2A task payload
issue_number = github.event.issue.number
issue_body = get_issue_body(issue_number)

# Parse A2A message from issue body
a2a_message = json.loads(issue_body)
task = a2a_message["params"]["task"]

# Execute task
result = execute_task(task)

# OUTPUT: Post result as comment
post_comment(issue_number, json.dumps({
    "result": result,
    "status": "completed"
}))

# Update labels to signal completion
update_labels(issue_number, ["status:completed"])
```

**3. Coordinator polls for completion:**
```python
# Poll issue for completion
while not is_complete(issue_number):
    time.sleep(5)  # Poll every 5 seconds
    check_labels(issue_number)

# Read result from comments
result = get_latest_comment(issue_number)
```

## Detailed Input Flow Examples

### Example 1: Single Coordinated Task (Tier 1)

**User creates issue:**
```markdown
Title: "Implement user authentication"
Body: "We need a secure authentication system with JWT tokens"
Labels: ["a2a-tier1"]
```

**Workflow triggered:**
1. `a2a-tier1-orchestration.yml` starts
2. One Copilot session reads issue body as INPUT
3. Session starts multiple agent servers locally
4. Agents communicate via HTTP on localhost
5. Session writes final result as OUTPUT to PR

**Input flow:**
```
GitHub Issue Body
    ↓
Single Copilot Session (a2a-coordinator)
    ↓
Parse task → Decompose → Select agents
    ↓
HTTP requests to local agent servers
    ↓
Agents process and return via HTTP responses
    ↓
Coordinator aggregates
    ↓
Write result to PR/Issue
```

### Example 2: Parallel Multi-Agent Task (Tier 2)

**User creates issue:**
```markdown
Title: "Comprehensive security audit"
Body: "Audit all security aspects of the codebase"
Labels: ["a2a-tier2"]
```

**Workflow triggered:**
1. `a2a-orchestration.yml` starts (Session 1: Coordinator)
2. Coordinator reads issue body as INPUT
3. Coordinator creates 4 GitHub issues (sub-tasks)
4. Each sub-task issue triggers `a2a-agent-worker.yml` (Sessions 2-5)
5. Each agent session reads ITS issue body as INPUT
6. Coordinator polls all sub-task issues for completion
7. Coordinator aggregates results and writes to original issue

**Input flow:**
```
GitHub Issue #100 Body
    ↓
Session 1: A2A-Coordinator reads issue #100
    ↓
Creates 4 sub-task issues (#101, #102, #103, #104)
    ↓
Session 2: reads issue #101 → processes → comments result
Session 3: reads issue #102 → processes → comments result
Session 4: reads issue #103 → processes → comments result
Session 5: reads issue #104 → processes → comments result
    ↓
Session 1: polls issues #101-104 for completion
    ↓
Session 1: reads comments (results) from each issue
    ↓
Session 1: aggregates and writes to issue #100
```

## Key Mechanisms for Session Input

### 1. GitHub Event Payloads

Every Copilot session is triggered by a GitHub event:

```yaml
on:
  issues:
    types: [opened, labeled]
  workflow_dispatch:
    inputs:
      task_description:
        required: true
```

**Input sources:**
- `github.event.issue.body` - Issue description
- `github.event.issue.title` - Issue title
- `github.event.inputs.*` - Workflow dispatch parameters
- `github.event.pull_request.body` - PR description

### 2. GitHub Issues as Task Queue

For Tier 2 (cross-runner):

```python
# Agent reads task from issue
issue_body = gh_api.get_issue(issue_number).body

# Parse A2A message (JSON-RPC format)
message = json.loads(issue_body)
method = message["method"]  # e.g., "tasks/execute"
params = message["params"]  # Task parameters

# Execute
result = execute(method, params)

# Write result back as comment
gh_api.create_comment(issue_number, json.dumps(result))
```

### 3. A2A Message Format

All inter-agent communication uses JSON-RPC 2.0 format:

```json
{
  "jsonrpc": "2.0",
  "method": "tasks/execute",
  "params": {
    "task": {
      "id": "auth-design",
      "description": "Design authentication system",
      "requirements": ["JWT", "secure", "scalable"]
    }
  },
  "id": "task-123"
}
```

## Concrete Example: End-to-End Flow

### Scenario: "Implement secure REST API"

**Step 1: User creates issue**
```markdown
Title: "Implement secure REST API"
Body: "Create a REST API with proper authentication and input validation"
Labels: ["a2a-orchestration"]
```

**Step 2: A2A-Coordinator Session Starts**

Triggered by issue label, workflow starts:
```yaml
# .github/workflows/a2a-orchestration.yml triggered
```

Coordinator reads INPUT from issue:
```python
task = github.event.issue.body
# "Create a REST API with proper authentication..."

# Decompose task
subtasks = [
    {"agent": "engineer-master", "task": "Design API endpoints"},
    {"agent": "secure-specialist", "task": "Design authentication"},
    {"agent": "engineer-master", "task": "Implement API"},
    {"agent": "assert-specialist", "task": "Create tests"}
]
```

**Step 3: For Tier 2, create sub-task issues**

```python
# Create GitHub issue for each subtask
issue_101 = create_issue(
    title="A2A Task: Design API endpoints",
    body=json.dumps({
        "method": "tasks/execute",
        "params": {"task": "Design RESTful API endpoints for user management"}
    }),
    labels=["a2a-task", "agent:engineer-master"]
)
# This triggers a2a-agent-worker.yml for engineer-master
```

**Step 4: Agent Worker Session Starts**

```python
# .github/workflows/a2a-agent-worker.yml triggered by issue #101 creation

# Read INPUT from issue
issue_body = get_issue(101).body
task_message = json.loads(issue_body)
task = task_message["params"]["task"]

# Execute using Copilot
result = copilot_execute(task)

# Write OUTPUT as comment
comment(101, json.dumps({"result": result, "status": "completed"}))
update_labels(101, ["status:completed"])
```

**Step 5: Coordinator polls and aggregates**

```python
# Coordinator waits for all subtasks
results = []
for issue_num in [101, 102, 103, 104]:
    while not is_completed(issue_num):
        sleep(5)
    results.append(get_result_from_comments(issue_num))

# Aggregate
final_result = aggregate(results)

# Write to original issue
comment(original_issue, final_result)
```

## Summary: How Sessions Take Input

### Tier 1 (Same-Runner)
- **Input**: GitHub issue body → parsed by coordinator
- **Distribution**: Coordinator makes HTTP calls to local agents
- **Agents receive**: HTTP POST with A2A message payload
- **Agents respond**: HTTP response with result
- **Collection**: Coordinator receives HTTP responses synchronously

### Tier 2 (Cross-Runner)
- **Input**: GitHub issue body → parsed by coordinator
- **Distribution**: Coordinator creates GitHub issues (one per agent)
- **Agents receive**: Each agent workflow triggered by issue creation, reads issue body
- **Agents respond**: Post result as issue comment, update labels
- **Collection**: Coordinator polls issues, reads comments for results

## Key Takeaways

1. **Every Copilot session is isolated** - runs in separate VM
2. **Input is always event-driven** - issue body, workflow_dispatch, PR description
3. **Tier 1 uses HTTP** - fast, synchronous, same runner
4. **Tier 2 uses GitHub Issues** - slower, asynchronous, separate runners
5. **A2A message format is consistent** - JSON-RPC 2.0 across both tiers
6. **Coordinator orchestrates** - decomposes tasks, creates sub-tasks, aggregates results

## Further Reading

- `docs/a2a/A2A_GITHUB_RUNNERS_ARCHITECTURE.md` - Detailed architecture
- `docs/a2a/A2A_TRANSPORT_COMPARISON.md` - Transport layer comparison
- `.github/workflows/a2a-agent-worker.yml` - Agent worker implementation
- `tools/a2a/github_transport.py` - GitHub transport implementation
