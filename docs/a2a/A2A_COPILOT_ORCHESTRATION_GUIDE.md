# A2A Native Copilot Agent Orchestration Guide

**Last Updated**: 2025-12-06  
**Status**: Production-Ready Patterns Available

## Executive Summary

The Chained repository **already has multiple working patterns** for orchestrating N Copilot sessions using A2A (Agent-to-Agent) protocol. This guide documents the existing capabilities and provides examples for using them.

## Key Finding: It Already Works! 🎉

You asked about exploring A2A with native Copilot agents and mentioned needing:
- ✅ **File system for context** → Implemented via `.a2a/artifacts/` and `.a2a/context/`
- ✅ **Dedicated unprotected branches** → Implemented with `a2a-tasks/` prefix
- ✅ **Harness to evoke N sessions** → Implemented in 3 different workflows

**You have a good reference already** - multiple production workflows demonstrate these patterns!

---

## Table of Contents

1. [Three Orchestration Patterns](#three-orchestration-patterns)
2. [Pattern Selection Guide](#pattern-selection-guide)
3. [Detailed Pattern Breakdown](#detailed-pattern-breakdown)
4. [File System Context Passing](#file-system-context-passing)
5. [Branch-Based Communication](#branch-based-communication)
6. [Complete Examples](#complete-examples)
7. [Tools Reference](#tools-reference)
8. [Best Practices](#best-practices)

---

## Three Orchestration Patterns

The repository implements **three distinct patterns** for multi-agent orchestration:

### 1. Branch-Based Coordination (`copilot-a2a-coordinator.yml`)

**Best for**: Cross-runner tasks requiring persistent state

```yaml
Pattern: Coordinator → Branch Creation → Agent Assignment → Polling → Aggregation
Communication: Git branches as message bus
Agents: N separate Copilot sessions (via agent assignment)
Context: Stored in branch files (task.json, status.json, result.json)
```

**Key Features**:
- Each agent runs in its own GitHub Actions runner
- Branches persist state between runs
- Polling-based result collection
- Supports long-running tasks
- GraphQL agent assignment for native Copilot

**When to use**:
- Tasks that may take >5 minutes per agent
- Need persistent state across workflow runs
- Multiple agents working independently
- Complex coordination with status tracking

### 2. Parallel Matrix Execution (`a2a-parallel-agents.yml`)

**Best for**: True parallel agent execution with bounded contexts

```yaml
Pattern: Setup → Parallel Matrix → Aggregate → Implement
Communication: GitHub Artifacts
Agents: N parallel jobs with matrix strategy
Context: Uploaded/downloaded artifacts between jobs
```

**Key Features**:
- True parallelism via matrix strategy
- Each agent is a separate job with bounded AI call
- Artifact-based result collection (no polling)
- Multi-provider support (Gemini, GitHub Models)
- A2A-compliant task linking

**When to use**:
- Tasks that benefit from parallel execution
- Need strict job boundaries per agent
- Want fast, concurrent analysis
- Multi-provider AI orchestration

### 3. Sequential Multi-Agent (`a2a-multi-agent.yml`)

**Best for**: Single-job orchestration with quick turnaround

```yaml
Pattern: Setup → Analysis → Context Prep → Implementation
Communication: Filesystem (same job)
Agents: All in one Copilot session
Context: In-memory + file-based (.a2a/)
```

**Key Features**:
- Simplest pattern (one job)
- Fast execution (no cross-job overhead)
- Direct file access for context
- A2A protocol compliance for consistency

**When to use**:
- Quick tasks (<10 minutes total)
- Don't need separate runner isolation
- Sequential execution is acceptable
- Simplicity is valued

---

## Pattern Selection Guide

Use this decision tree to choose the right pattern:

```
Do agents need separate runners for isolation or long tasks?
├─ YES → Do tasks run in parallel or sequential?
│  ├─ PARALLEL → Use a2a-parallel-agents.yml (Matrix pattern)
│  └─ SEQUENTIAL → Use copilot-a2a-coordinator.yml (Branch pattern)
└─ NO → Use a2a-multi-agent.yml (Sequential pattern)

Is the task time-sensitive?
├─ YES (need fast) → Use a2a-parallel-agents.yml (true parallelism)
└─ NO → Use copilot-a2a-coordinator.yml (more robust state)

Do you need persistent state across workflow failures?
├─ YES → Use copilot-a2a-coordinator.yml (branches persist)
└─ NO → Use a2a-parallel-agents.yml (ephemeral jobs)

Do you need native Copilot agent assignment via GraphQL?
├─ YES → Use copilot-a2a-coordinator.yml (GraphQL suggestedActors)
└─ NO → Use a2a-parallel-agents.yml (Gemini or GitHub Models)
```

---

## Detailed Pattern Breakdown

### Pattern 1: Branch-Based Coordination

**File**: `.github/workflows/copilot-a2a-coordinator.yml`

#### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Coordinator (Run #1)                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Parse issue task                                  │   │
│  │ 2. Call copilot_task_analyzer.py                     │   │
│  │ 3. Identify required agents                          │   │
│  │ 4. Create a2a-tasks/issue-N-agent-X branches         │   │
│  │ 5. Write task.json to each branch                    │   │
│  │ 6. Assign agents via copilot_agent_assigner.py      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
              ┌───────────────────┐
              │  GitHub Branches  │
              │  a2a-tasks/       │
              │  issue-N-agent-X  │
              └───────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Agent Workers (Runs #2, #3, #4, ...)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Triggered by agent assignment                     │   │
│  │ 2. Fetch branch a2a-tasks/issue-N-agent-X            │   │
│  │ 3. Read task.json                                    │   │
│  │ 4. Execute work (Copilot session)                    │   │
│  │ 5. Write result.json to branch                       │   │
│  │ 6. Update status.json                                │   │
│  │ 7. Push changes                                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Coordinator (Run #1 continued)                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 8. Poll branches for completion                      │   │
│  │    (branch_polling_monitor.py)                       │   │
│  │ 9. Aggregate results                                 │   │
│  │    (branch_result_aggregator.py)                     │   │
│  │ 10. Post summary comment                             │   │
│  │ 11. Cleanup branches (branch_cleanup.py)            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### Key Files and Tools

**Workflow Steps**:
1. `copilot_task_analyzer.py` - Decomposes task, identifies agents
2. `copilot_agent_assigner.py` - Assigns agents via GraphQL suggestedActors
3. `branch_message_bus_setup.py` - Creates branches with task definitions
4. `branch_polling_monitor.py` - Polls for completion (configurable timeout)
5. `branch_result_aggregator.py` - Collects and combines results
6. `branch_cleanup.py` - Removes temporary branches
7. `copilot_coordination_summary.py` - Posts final summary

**Branch Structure**:
```
a2a-tasks/issue-123-agent-engineer-master/
├── task.json              # Input task definition
├── status.json            # Current status (updated by worker)
├── result.json            # Final result (written by worker)
└── artifacts/             # Optional: additional files
```

**Message Format** (JSON-RPC 2.0):
```json
{
  "jsonrpc": "2.0",
  "id": "task-abc123",
  "method": "agent.execute",
  "params": {
    "agent": "engineer-master",
    "task": "implement_feature",
    "context": {
      "issue_number": 123,
      "files_changed": ["src/api.py"]
    }
  }
}
```

#### Triggering

```yaml
# Manual trigger
workflow_dispatch:
  inputs:
    issue_number: 123

# Or via comment
issue_comment:
  types: [created]
  # Comment: @copilot-a2a-coordinator
```

---

### Pattern 2: Parallel Matrix Execution

**File**: `.github/workflows/a2a-parallel-agents.yml`

#### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Setup Job (1 runner)                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Fetch issue details                               │   │
│  │ 2. Select N agents (auto or manual)                  │   │
│  │ 3. Generate AgentCards (agent_card.py)               │   │
│  │ 4. Create agent-provider matrix                      │   │
│  │ 5. Upload AgentCards as artifact                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Agent Jobs (N parallel runners)                            │
│  ┌─────────────────┬─────────────────┬─────────────────┐   │
│  │ Agent 1         │ Agent 2         │ Agent 3         │   │
│  │ (Gemini)        │ (GitHub Models) │ (Gemini)        │   │
│  ├─────────────────┼─────────────────┼─────────────────┤   │
│  │ 1. Download     │ 1. Download     │ 1. Download     │   │
│  │    AgentCards   │    AgentCards   │    AgentCards   │   │
│  │ 2. Read agent   │ 2. Read agent   │ 2. Read agent   │   │
│  │    definition   │    definition   │    definition   │   │
│  │ 3. Execute AI   │ 3. Execute AI   │ 3. Execute AI   │   │
│  │    call         │    call         │    call         │   │
│  │ 4. Generate     │ 4. Generate     │ 4. Generate     │   │
│  │    analysis     │    analysis     │    analysis     │   │
│  │ 5. Package as   │ 5. Package as   │ 5. Package as   │   │
│  │    artifact     │    artifact     │    artifact     │   │
│  │ 6. Upload       │ 6. Upload       │ 6. Upload       │   │
│  └─────────────────┴─────────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Aggregate Job (1 runner)                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Download all agent artifacts                      │   │
│  │ 2. Parse each agent's analysis.json                  │   │
│  │ 3. Combine analyses into aggregated-analysis.json    │   │
│  │ 4. Upload aggregated artifact                        │   │
│  │ 5. Post summary comment to issue                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Implement Job (1 runner)                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Download aggregated analysis                      │   │
│  │ 2. Prepare .a2a/context/implementation.md            │   │
│  │ 3. Run implementing agent (Gemini)                   │   │
│  │ 4. Create PR with changes                            │   │
│  │ 5. Post completion comment                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### Key Features

**Matrix Strategy**:
```yaml
strategy:
  matrix:
    include:
      - agent: engineer-master
        provider: gemini
      - agent: secure-specialist
        provider: github
      - agent: organize-guru
        provider: gemini
  fail-fast: false  # All agents complete even if one fails
```

**A2A Task Linking** (per spec):
```yaml
- contextId: "run-19779887283-issue-123"
- referenceTaskIds: ["task-19779887283-engineer-master", ...]
```

**Artifact Structure**:
```json
{
  "a2a_version": "0.3.0",
  "artifact_type": "agent_analysis",
  "task_id": "task-19779887283-engineer-master",
  "context_id": "run-19779887283-issue-123",
  "agent_name": "engineer-master",
  "provider": "gemini",
  "status": "completed",
  "content": {
    "analysis": "..."
  }
}
```

**Multi-Provider Support**:
- **Gemini**: Via `google-github-actions/run-gemini-cli`
- **GitHub Models**: Via Python script with OpenAI-compatible API
- **Balanced**: Alternates between providers

---

### Pattern 3: Sequential Multi-Agent

**File**: `.github/workflows/a2a-multi-agent.yml`

#### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Single Job (1 runner, sequential steps)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Setup: Install dependencies                       │   │
│  │ 2. Fetch issue details                               │   │
│  │ 3. Select agents                                     │   │
│  │ 4. Generate AgentCards (agent_card.py)               │   │
│  │ 5. Verify A2A SDK integration                        │   │
│  │ 6. Post start notification                           │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 7. Run analysis (Gemini CLI with MCP tools)          │   │
│  │    - Gemini processes all agents sequentially        │   │
│  │    - Outputs to gemini-artifacts/                    │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 8. Complete analysis lifecycle                       │   │
│  │    (workflow_orchestrator.py)                        │   │
│  │    - Reads gemini-artifacts/                         │   │
│  │    - Creates .a2a/artifacts/analysis.json            │   │
│  │ 9. Upload analysis artifact                          │   │
│  │ 10. Post analysis complete notification              │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 11. Prepare execution context                        │   │
│  │     - Creates .a2a/context/implementation.md         │   │
│  │ 12. Auto-execute: Implement changes                  │   │
│  │     (if auto_execute=true)                           │   │
│  │ 13. Verify PR creation                               │   │
│  │ 14. Post completion notification                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### Key Features

**Simplicity**:
- All steps in one job
- No cross-job artifact passing
- Direct file system access
- Fast execution

**A2A Compliance**:
- Still generates AgentCards
- Uses A2A protocol for consistency
- Task lifecycle tracking
- Artifact packaging

**Good for**:
- Demos and testing
- Quick tasks
- Learning A2A patterns

---

## File System Context Passing

All three patterns use the **`.a2a/` directory** for context passing:

### Directory Structure

```
.a2a/
├── agent-cards/           # AgentCard registry (§4.4.1)
│   ├── engineer-master.json
│   ├── secure-specialist.json
│   ├── organize-guru.json
│   └── registry.json      # Combined registry
│
├── artifacts/             # Agent outputs (§4.1.9)
│   ├── analysis.json      # Aggregated analysis
│   ├── engineer-master-analysis.json
│   ├── secure-specialist-analysis.json
│   └── organize-guru-analysis.json
│
└── context/               # Prepared contexts
    ├── implementation.md  # For implementing agent
    └── review.md          # For reviewing agent
```

### Context File Format

**implementation.md** (used by implementing agent):

```markdown
# A2A Implementation Task

## Task Linking
- contextId: `run-19779887283-issue-123`
- referenceTaskIds: ["task-A", "task-B", "task-C"]

## Agent Analysis

### @engineer-master (from referenced task)
- Recommendation 1: Implement feature X
- Recommendation 2: Refactor module Y

### @secure-specialist (from referenced task)
- Recommendation 1: Add input validation
- Recommendation 2: Use parameterized queries

### @organize-guru (from referenced task)
- Recommendation 1: Extract helper functions
- Recommendation 2: Improve naming

## Implementation Instructions
Based on the above analyses, implement the recommended changes...
```

### Artifact Access Patterns

**Same-job access** (Pattern 3):
```yaml
- name: Read context
  run: cat .a2a/context/implementation.md
```

**Cross-job via upload/download** (Pattern 2):
```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4.4.3
  with:
    name: a2a-analysis
    path: .a2a/artifacts/analysis.json

- name: Download artifact
  uses: actions/download-artifact@v4.1.8
  with:
    name: a2a-analysis
    path: .a2a/artifacts/
```

**Cross-runner via branches** (Pattern 1):
```bash
# Agent 1 writes
git checkout a2a-tasks/issue-123-agent-A
echo '{"result": "..."}' > result.json
git add result.json
git commit -m "Agent A result"
git push

# Coordinator reads
git fetch origin a2a-tasks/issue-123-agent-A
git checkout a2a-tasks/issue-123-agent-A
cat result.json
```

---

## Branch-Based Communication

### Branch Naming

```
a2a-tasks/{coordinator}-{task-type}-{short-uuid}
```

Examples:
- `a2a-tasks/a2a-coordinator-security-review-abc123`
- `a2a-tasks/issue-123-engineer-master-def456`

### Branch Lifecycle

1. **Creation** (Coordinator):
   ```python
   # tools/a2a/branch_message_bus_setup.py
   branch_name = f"a2a-tasks/issue-{issue_number}-{agent_name}-{short_uuid}"
   subprocess.run(["git", "checkout", "-b", branch_name])
   with open("task.json", "w") as f:
       json.dump(task_data, f)
   subprocess.run(["git", "add", "task.json"])
   subprocess.run(["git", "commit", "-m", "Create task for agent"])
   subprocess.run(["git", "push", "origin", branch_name])
   ```

2. **Execution** (Agent):
   ```bash
   git fetch origin a2a-tasks/issue-123-agent-X
   git checkout a2a-tasks/issue-123-agent-X
   task=$(cat task.json)
   # Execute work...
   echo "$result" > result.json
   git add result.json status.json
   git commit -m "Agent result"
   git push
   ```

3. **Polling** (Coordinator):
   ```python
   # tools/a2a/branch_polling_monitor.py
   while not timeout:
       result = check_branch_for_result(branch_name)
       if result:
           return result
       time.sleep(polling_interval)
   ```

4. **Aggregation** (Coordinator):
   ```python
   # tools/a2a/branch_result_aggregator.py
   results = []
   for branch in agent_branches:
       git_checkout(branch)
       result = json.load(open("result.json"))
       results.append(result)
   aggregated = combine_results(results)
   ```

5. **Cleanup** (Coordinator):
   ```python
   # tools/a2a/branch_cleanup.py
   for branch in agent_branches:
       subprocess.run(["git", "push", "origin", "--delete", branch])
   ```

---

## Complete Examples

### Example 1: Use Branch-Based Coordination

**Scenario**: Coordinate 3 agents for a security review

```bash
# Trigger via workflow_dispatch
gh workflow run copilot-a2a-coordinator.yml \
  -f issue_number=123

# Or trigger via comment
# Comment on issue #123: @copilot-a2a-coordinator
```

**What happens**:
1. Coordinator analyzes issue #123
2. Identifies 3 agents: secure-specialist, organize-guru, engineer-master
3. Creates 3 branches:
   - `a2a-tasks/issue-123-secure-specialist-abc123`
   - `a2a-tasks/issue-123-organize-guru-def456`
   - `a2a-tasks/issue-123-engineer-master-ghi789`
4. Assigns each agent via GraphQL suggestedActors
5. Each agent runs in separate workflow, reads task from branch, executes
6. Coordinator polls for completion (30s intervals, 30min timeout)
7. Aggregates results
8. Posts summary comment
9. Cleans up branches

**Timeline**:
- Setup: ~30 seconds
- Agent execution: 3-10 minutes per agent (parallel via separate runners)
- Aggregation: ~10 seconds
- Total: ~5-15 minutes depending on task complexity

### Example 2: Use Parallel Matrix

**Scenario**: Fast parallel analysis with 5 agents

```bash
gh workflow run a2a-parallel-agents.yml \
  -f issue_number=456 \
  -f agent_count=5 \
  -f provider=balanced \
  -f auto_execute=true
```

**What happens**:
1. Setup job selects 5 agents (diverse categories)
2. Generates AgentCards
3. Creates matrix with provider assignment:
   - agent-1: Gemini
   - agent-2: GitHub Models
   - agent-3: Gemini
   - agent-4: GitHub Models
   - agent-5: Gemini
4. 5 jobs run in parallel (truly concurrent)
5. Each uploads artifact with analysis
6. Aggregate job downloads all 5 artifacts
7. Combine into single context file
8. Implement job creates PR

**Timeline**:
- Setup: ~20 seconds
- Agent jobs: 2-5 minutes (PARALLEL - fastest)
- Aggregation: ~10 seconds
- Implementation: 3-5 minutes
- Total: ~5-10 minutes (fastest pattern)

### Example 3: Use Sequential Multi-Agent

**Scenario**: Simple demo or quick task

```bash
gh workflow run a2a-multi-agent.yml \
  -f issue_number=789 \
  -f agent_count=3 \
  -f agents="engineer-master,organize-guru,document-ninja" \
  -f auto_execute=true \
  -f show_reasoning=true
```

**What happens**:
1. Single job, all in one runner
2. Generates AgentCards for 3 agents
3. Gemini CLI processes all 3 agents sequentially
4. Outputs to gemini-artifacts/
5. Lifecycle orchestrator packages as A2A artifacts
6. Prepares implementation context
7. Implementing agent creates PR
8. All in one job, no cross-job overhead

**Timeline**:
- Setup: ~15 seconds
- Analysis: 3-5 minutes (sequential, single AI session)
- Implementation: 2-4 minutes
- Total: ~5-10 minutes (simplest, single job)

---

## Tools Reference

### Core Orchestration Tools

| Tool | Purpose | Used In |
|------|---------|---------|
| `agent_card.py` | Generate A2A AgentCards from agent definitions | All patterns |
| `workflow_orchestrator.py` | Manage task lifecycle, artifacts | Pattern 3 |
| `copilot_task_analyzer.py` | Decompose tasks, identify agents | Pattern 1 |
| `copilot_agent_assigner.py` | Assign agents via GraphQL | Pattern 1 |
| `branch_message_bus_setup.py` | Create task branches | Pattern 1 |
| `branch_polling_monitor.py` | Poll for agent completion | Pattern 1 |
| `branch_result_aggregator.py` | Aggregate results from branches | Pattern 1 |
| `branch_cleanup.py` | Remove temporary branches | Pattern 1 |
| `copilot_coordination_summary.py` | Post summary comments | Pattern 1 |

### Usage Examples

**Generate AgentCard**:
```python
from tools.a2a.agent_card import generate_agent_card

card = generate_agent_card("engineer-master")
print(card.model_dump_json(indent=2))
```

**Lifecycle Management**:
```python
from tools.a2a.workflow_orchestrator import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator(
    issue_number=123,
    run_id="19779887283",
    agents=["agent-1", "agent-2", "agent-3"]
)

# Complete analysis phase
orchestrator.complete_analysis_lifecycle(
    gemini_output_dir="gemini-artifacts/",
    output_artifact=".a2a/artifacts/analysis.json"
)

# Prepare implementation context
orchestrator.prepare_execution_context(
    analysis_artifact=".a2a/artifacts/analysis.json",
    context_output=".a2a/context/implementation.md"
)
```

**Branch Operations**:
```python
from tools.a2a import branch_message_bus_setup

# Create task branch
branch_name = branch_message_bus_setup.create_task_branch(
    issue_number=123,
    agent_name="engineer-master",
    task_data={"method": "implement", "params": {...}}
)
```

---

## Best Practices

### 1. Choose the Right Pattern

| Criteria | Recommended Pattern |
|----------|---------------------|
| Fast, parallel execution | Pattern 2 (Parallel Matrix) |
| Long-running tasks | Pattern 1 (Branch-Based) |
| Need persistent state | Pattern 1 (Branch-Based) |
| Simple, quick tasks | Pattern 3 (Sequential) |
| Native Copilot agents | Pattern 1 (Branch-Based) |
| Multi-provider AI | Pattern 2 (Parallel Matrix) |

### 2. Context Passing

- ✅ Always use `.a2a/` directory structure
- ✅ Package as A2A-compliant artifacts
- ✅ Include contextId and referenceTaskIds
- ✅ Use JSON for structured data
- ✅ Use Markdown for agent prompts

### 3. Error Handling

- ✅ Set reasonable timeouts (Pattern 1: 30min, Pattern 2: 10min per job)
- ✅ Use `fail-fast: false` for matrix jobs
- ✅ Implement retry logic for transient errors
- ✅ Post error notifications to issues
- ✅ Clean up branches even on failure

### 4. Agent Selection

- ✅ Use diverse agent categories for coverage
- ✅ Separate implementing agent from analyzing agents (Pattern 2)
- ✅ Auto-select agents when possible
- ✅ Allow manual override for specific expertise

### 5. A2A Protocol Compliance

- ✅ Generate AgentCards using `agent_card.py`
- ✅ Use proper task lifecycle states
- ✅ Include A2A version (0.3.0) in artifacts
- ✅ Link tasks with contextId and referenceTaskIds
- ✅ Package results as Artifacts per spec

---

## FAQ

**Q: Can I mix patterns?**  
A: Yes! You can use Pattern 1 for analysis and Pattern 3 for implementation, or create hybrid workflows.

**Q: How do I add a new agent?**  
A: Create `.github/agents/your-agent.md` with YAML frontmatter. The orchestration workflows auto-detect available agents.

**Q: What's the maximum number of parallel agents?**  
A: Pattern 2 supports up to 256 jobs (GitHub Actions matrix limit). Practical limit is ~20 for performance.

**Q: Can I use Claude instead of Gemini?**  
A: Yes! See `claude-a2a-coordinator.yml` for Claude-specific implementation.

**Q: How do I debug failures?**  
A: Check workflow logs, review branch files (Pattern 1), or download artifacts (Pattern 2). All patterns post progress comments to issues.

**Q: Is this production-ready?**  
A: Yes! All three patterns are actively used in the repository and have been tested extensively.

---

## Related Documentation

- [A2A README](./README.md) - Complete A2A documentation index
- [A2A Status](./A2A_STATUS.md) - Current implementation status
- [Branch-Based Coordination](./A2A_BRANCH_BASED_COORDINATION.md) - Detailed branch protocol
- [Copilot Sessions Explained](./A2A_COPILOT_SESSIONS_EXPLAINED.md) - How Copilot sessions interact
- [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/) - Official A2A spec

---

## Conclusion

You asked if there's a workflow reference for orchestrating N Copilot sessions with A2A. **The answer is yes - you have THREE excellent reference implementations!**

- **Branch-Based**: Most robust for cross-runner coordination
- **Parallel Matrix**: Fastest for concurrent execution
- **Sequential**: Simplest for demos and quick tasks

All three are production-ready and actively used. Choose based on your specific needs using the decision tree above.

**Next Steps**:
1. Try running `a2a-parallel-agents.yml` with a test issue
2. Review the workflow logs to see the orchestration in action
3. Customize one of the patterns for your specific use case
4. Refer to the tools in `tools/a2a/` for reusable components

Happy orchestrating! 🚀
