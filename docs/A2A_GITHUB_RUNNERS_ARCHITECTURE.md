# A2A Protocol on GitHub Actions Runners - Architecture Analysis

## GitHub Actions Runner Constraints

### What We Know About GitHub Actions Runners

**Environment:**
- Ephemeral VMs that spin up for each job
- Isolated from external network access (no inbound connections)
- Can make outbound HTTP/HTTPS requests
- Can bind to localhost ports within the runner
- No persistent IP addresses
- No way to expose ports to external services
- Multiple concurrent runners are separate VMs

**Key Constraints:**
1. **No Inbound Connections**: Runners cannot receive external HTTP requests
2. **No Cross-Runner Communication**: Runners cannot directly communicate with each other
3. **Ephemeral**: Each job gets a fresh VM, no persistence between jobs
4. **Localhost Only**: Agents can only communicate within the same runner instance

### Traditional A2A Architecture (Not Possible)

```
❌ THIS WON'T WORK ON GITHUB ACTIONS:

Runner 1                Runner 2                Runner 3
┌─────────┐            ┌─────────┐            ┌─────────┐
│ Agent A │◄──HTTP────►│ Agent B │◄──HTTP────►│ Agent C │
│ Port    │            │ Port    │            │ Port    │
│ 9001    │            │ 9002    │            │ 9003    │
└─────────┘            └─────────┘            └─────────┘

Problem: Runners cannot receive inbound HTTP requests from each other
```

## Proposed Architecture: Event-Driven A2A with GitHub as Message Broker

Since we can't have traditional HTTP server-to-server communication, we need to use **GitHub itself** as the message broker.

### Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    GitHub Platform                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │         GitHub Issues/Comments (Message Queue)     │     │
│  │  - Each task = GitHub Issue                        │     │
│  │  - Messages = Issue Comments                       │     │
│  │  - Status tracking = Labels                        │     │
│  └────────────────────────────────────────────────────┘     │
│                          ▲                                   │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │ GitHub API
                           │ (HTTPS - Outbound Only)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Runner 1   │   │   Runner 2   │   │   Runner 3   │
│              │   │              │   │              │
│  Agent A     │   │  Agent B     │   │  Agent C     │
│  (workflow   │   │  (workflow   │   │  (workflow   │
│   dispatch)  │   │   dispatch)  │   │   dispatch)  │
│              │   │              │   │              │
│  Polls for   │   │  Polls for   │   │  Polls for   │
│  new tasks   │   │  new tasks   │   │  new tasks   │
│  via GitHub  │   │  via GitHub  │   │  via GitHub  │
│  API         │   │  API         │   │  API         │
└──────────────┘   └──────────────┘   └──────────────┘
```

### How It Works

#### 1. Task Creation (Agent → GitHub → Agent)

```
Agent A wants to delegate to Agent B:

1. Agent A creates GitHub Issue:
   - Title: "Task for @engineer-master"
   - Body: A2A message payload (JSON-RPC format)
   - Label: "a2a-task", "agent:engineer-master", "status:submitted"

2. GitHub triggers workflow_dispatch for Agent B

3. Agent B (in new runner):
   - Reads issue body (A2A message)
   - Executes task
   - Posts result as comment
   - Updates labels to "status:completed"

4. Agent A polls for completion:
   - Watches issue for "status:completed" label
   - Reads result from comments
```

#### 2. Message Exchange Pattern

```yaml
# .github/workflows/a2a-agent-worker.yml
name: A2A Agent Worker

on:
  issues:
    types: [opened, labeled]
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number containing A2A task'
        required: true

jobs:
  execute-task:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*.name, 'a2a-task')
    
    steps:
      - name: Parse A2A Message
        run: |
          # Extract A2A JSON-RPC from issue body
          # Determine target agent from labels
          
      - name: Execute Agent
        run: |
          # Run agent executor with task
          python3 -m tools.a2a.agent_executor engineer-master
          
      - name: Post Result
        run: |
          # Post A2A response as comment
          # Update issue labels (status:completed)
```

### Hybrid Architecture: Local + GitHub Message Bus

For agents running in the **same runner** (same workflow job), we can use traditional A2A HTTP:

```
Single Runner (Same Workflow Job)
┌─────────────────────────────────────────────────────┐
│  GitHub Actions Runner                              │
│                                                     │
│  ┌──────────┐  HTTP   ┌──────────┐  HTTP  ┌─────┐ │
│  │ Agent A  │◄───────►│ Agent B  │◄──────►│  C  │ │
│  │ :9001    │         │ :9002    │        │:9003│ │
│  └──────────┘         └──────────┘        └─────┘ │
│       │                                             │
│       │ For cross-runner communication              │
│       ▼                                             │
│  ┌─────────────────────────────────────────┐       │
│  │   GitHub API (Issues/Comments)          │       │
│  │   - Create issues for delegation        │       │
│  │   - Poll for responses                  │       │
│  └─────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────┘
```

## Implementation Strategy

### Phase 2A: Local A2A (Within Runner)

**Use Case**: Multi-agent collaboration within a single workflow

```yaml
# Example: API development with security review
jobs:
  multi-agent-task:
    runs-on: ubuntu-latest
    steps:
      - name: Start Discovery Service
        run: python3 -m tools.a2a.discovery_server &
        
      - name: Start Engineer Agent
        run: python3 -m tools.a2a.agent_server engineer-master 9001 &
        
      - name: Start Security Agent
        run: python3 -m tools.a2a.agent_server secure-specialist 9002 &
        
      - name: Coordinate Task
        run: |
          # Meta-coordinator delegates locally
          python3 -m tools.a2a.orchestrate \
            --task "Implement secure API" \
            --agents engineer-master,secure-specialist
```

**Benefits:**
- ✅ True A2A HTTP communication
- ✅ Fast (no GitHub API latency)
- ✅ Real-time streaming
- ✅ Traditional A2A protocol works as-is

**Limitations:**
- ❌ All agents must be in same workflow job
- ❌ Limited parallelism (single runner)
- ❌ No cross-workflow delegation

### Phase 2B: GitHub-Mediated A2A (Cross-Runner)

**Use Case**: Long-running tasks, parallel execution across multiple runners

```python
# tools/a2a/github_transport.py

class GitHubA2ATransport:
    """A2A transport using GitHub Issues as message bus."""
    
    async def send_task(self, agent_name: str, message: dict) -> str:
        """
        Send task to agent via GitHub issue.
        
        Returns task ID (issue number)
        """
        # Create issue with A2A payload
        issue = await self.gh_client.create_issue(
            title=f"Task for @{agent_name}",
            body=json.dumps(message),
            labels=["a2a-task", f"agent:{agent_name}", "status:submitted"]
        )
        
        # Trigger workflow for agent
        await self.gh_client.workflow_dispatch(
            workflow="a2a-agent-worker.yml",
            inputs={"issue_number": issue.number}
        )
        
        return str(issue.number)
    
    async def poll_result(self, task_id: str, timeout: int = 3600) -> dict:
        """Poll issue for completion."""
        start = time.time()
        
        while time.time() - start < timeout:
            issue = await self.gh_client.get_issue(task_id)
            
            if "status:completed" in [l.name for l in issue.labels]:
                # Extract result from comments
                comments = await self.gh_client.get_issue_comments(task_id)
                return json.loads(comments[-1].body)
            
            await asyncio.sleep(5)  # Poll every 5 seconds
        
        raise TimeoutError(f"Task {task_id} did not complete")
```

**Benefits:**
- ✅ Cross-runner communication
- ✅ Parallel execution (multiple runners)
- ✅ Persistent task tracking
- ✅ Audit trail via issues

**Limitations:**
- ❌ Slower (GitHub API latency)
- ❌ Polling overhead
- ❌ Rate limits (5000 requests/hour)

## Recommended Implementation

### Tiered Approach

```
┌──────────────────────────────────────────────────────────┐
│ Tier 1: Same-Runner A2A (Phase 2A)                      │
│ - Fast HTTP communication                                │
│ - Real-time coordination                                 │
│ - Multiple agents in single workflow                     │
└──────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│ Tier 2: GitHub-Mediated A2A (Phase 2B)                  │
│ - Cross-workflow delegation                              │
│ - Long-running tasks                                     │
│ - Issue-based message passing                            │
└──────────────────────────────────────────────────────────┘
                         ▼
┌──────────────────────────────────────────────────────────┐
│ Tier 3: External Compute (Future/Optional)              │
│ - Persistent agent servers                               │
│ - Traditional A2A protocol                               │
│ - Only if hitting runner limits                          │
└──────────────────────────────────────────────────────────┘
```

### Decision Tree

```
Need multi-agent collaboration?
├─ YES: Can all agents run in same workflow job?
│   ├─ YES → Use Tier 1 (Same-Runner A2A)
│   │        ✅ Fast, real-time, full A2A protocol
│   │
│   └─ NO → Need parallel execution or long tasks?
│       ├─ YES → Use Tier 2 (GitHub-Mediated A2A)
│       │        ✅ Cross-runner, persistent, scalable
│       │
│       └─ Hitting rate limits or latency issues?
│           └─ YES → Consider Tier 3 (External Compute)
│                    ⚠️  Only if really needed
│
└─ NO: Single agent execution (current model)
```

## Next Steps for Implementation

### Immediate (Phase 2A)
1. ✅ Keep existing `agent_server.py`, `discovery.py`, `client.py`
2. ✅ Add same-runner orchestration workflow
3. ✅ Test multi-agent local communication
4. ✅ Example: Meta-coordinator with 2-3 local agents

### Near-term (Phase 2B)
1. Create `github_transport.py` - GitHub Issues as message bus
2. Create `a2a-agent-worker.yml` - Worker workflow
3. Implement polling/webhook pattern
4. Rate limit handling
5. Example: Cross-workflow delegation

### Long-term (Phase 3+)
- Evaluate actual usage patterns
- Measure if runner constraints are blocking
- Only then consider external compute

## File Structure Update

```
tools/a2a/
├── __init__.py
├── agent_card.py          ✅ Existing
├── agent_executor.py      ✅ Existing
├── agent_server.py        ✅ Existing (for Tier 1)
├── client.py              ✅ Existing (for Tier 1)
├── discovery.py           ✅ Existing (for Tier 1)
├── utils.py               ✅ Existing
├── github_transport.py    🆕 NEW - GitHub Issues transport
└── orchestrator.py        🆕 NEW - Multi-tier orchestration

.github/workflows/
├── a2a-local-orchestration.yml   🆕 Tier 1 example
└── a2a-agent-worker.yml          🆕 Tier 2 worker
```

## Conclusion

**GitHub Actions runners can support A2A protocol with two tiers:**

1. **Tier 1 (Same-Runner)**: Traditional A2A HTTP within a single workflow job
   - Suitable for: Quick multi-agent tasks, real-time coordination
   - Limitation: All agents in one runner

2. **Tier 2 (GitHub-Mediated)**: Issues/Comments as message bus for cross-runner
   - Suitable for: Long-running tasks, parallel execution
   - Limitation: Slower, polling-based

This architecture respects GitHub Actions constraints while enabling true multi-agent collaboration. We start with Tier 1 (easiest, fastest) and add Tier 2 as needed.

**External compute only if we prove the GitHub-based approach hits fundamental limits.**
