# A2A Orchestration Quick Start

**TL;DR**: You already have 3 working patterns for N-agent orchestration. Pick one and go!

## 30-Second Summary

```bash
# 1. Fast parallel execution (recommended for most cases)
gh workflow run a2a-parallel-agents.yml -f issue_number=123 -f agent_count=3

# 2. Branch-based coordination (for long-running tasks)
gh workflow run copilot-a2a-coordinator.yml -f issue_number=123

# 3. Simple sequential (for demos/testing)
gh workflow run a2a-multi-agent.yml -f issue_number=123 -f agent_count=3
```

## Decision Tree (30 seconds)

```
Need parallel execution? → Use a2a-parallel-agents.yml
Need persistent state?   → Use copilot-a2a-coordinator.yml
Need simple/fast demo?   → Use a2a-multi-agent.yml
```

## The Three Patterns

### Pattern 1: Parallel Matrix ⚡ (FASTEST)

**File**: `a2a-parallel-agents.yml`

```yaml
What: N agents run in parallel jobs
Speed: 5-10 minutes total
Best for: Fast analysis, concurrent execution
```

**Example**:
```bash
gh workflow run a2a-parallel-agents.yml \
  -f issue_number=456 \
  -f agent_count=5 \
  -f provider=balanced \
  -f auto_execute=true
```

**Output**: PR created with synthesized recommendations from all agents

---

### Pattern 2: Branch-Based 🌿 (MOST ROBUST)

**File**: `copilot-a2a-coordinator.yml`

```yaml
What: N agents via branch communication
Speed: 10-20 minutes
Best for: Long tasks, persistent state
```

**Example**:
```bash
# Via workflow
gh workflow run copilot-a2a-coordinator.yml -f issue_number=123

# Or via comment on issue
# @copilot-a2a-coordinator
```

**Output**: Coordination summary with aggregated results

---

### Pattern 3: Sequential 🎯 (SIMPLEST)

**File**: `a2a-multi-agent.yml`

```yaml
What: All agents in one job
Speed: 5-10 minutes
Best for: Demos, simple tasks
```

**Example**:
```bash
gh workflow run a2a-multi-agent.yml \
  -f issue_number=789 \
  -f agents="engineer-master,organize-guru" \
  -f auto_execute=true
```

**Output**: PR created from sequential agent analysis

---

## Key Concepts

### File System Context

All patterns use `.a2a/` directory:

```
.a2a/
├── agent-cards/      # Agent definitions
├── artifacts/        # Agent outputs
└── context/          # Prepared contexts for next stage
```

**Access in workflows**:
```yaml
- name: Read context
  run: cat .a2a/context/implementation.md
```

### Branch Communication (Pattern 2 only)

```
a2a-tasks/issue-N-agent-X-uuid/
├── task.json      # Input
├── status.json    # Progress
└── result.json    # Output
```

**Agent workflow**:
1. Fetch branch → Read task.json
2. Execute work
3. Write result.json → Push

### Artifact Passing (Pattern 1)

```yaml
# Upload
- uses: actions/upload-artifact@v4
  with:
    name: a2a-task-agent-1
    path: .a2a/artifacts/agent-1-analysis.json

# Download
- uses: actions/download-artifact@v4
  with:
    pattern: a2a-task-*
    path: .a2a/agent-artifacts/
```

---

## Common Use Cases

### Use Case 1: Quick Issue Analysis

```bash
gh workflow run a2a-parallel-agents.yml \
  -f issue_number=123 \
  -f agent_count=3 \
  -f auto_execute=false  # Don't create PR yet
```

**Result**: Issue comment with 3 agent analyses

### Use Case 2: Auto-Fix with Implementation

```bash
gh workflow run a2a-parallel-agents.yml \
  -f issue_number=456 \
  -f agent_count=5 \
  -f auto_execute=true  # Creates PR automatically
```

**Result**: PR created with fixes

### Use Case 3: Security Review

```bash
gh workflow run copilot-a2a-coordinator.yml -f issue_number=789
# Coordinator auto-selects security-focused agents
```

**Result**: Comprehensive security analysis

### Use Case 4: Demo for Stakeholders

```bash
gh workflow run a2a-multi-agent.yml \
  -f issue_number=101 \
  -f agents="engineer-master,document-ninja" \
  -f show_reasoning=true  # Shows Gemini's thinking
```

**Result**: Visible reasoning process in artifacts

---

## Customization

### Select Specific Agents

```bash
# Instead of agent_count, use agents parameter
gh workflow run a2a-parallel-agents.yml \
  -f issue_number=123 \
  -f agents="engineer-master,secure-specialist,organize-guru"
```

### Change AI Provider

```bash
# Options: balanced, gemini_only, github_only
gh workflow run a2a-parallel-agents.yml \
  -f issue_number=123 \
  -f provider=gemini_only
```

### Adjust Timeout

Edit workflow file:
```yaml
# Pattern 2: copilot-a2a-coordinator.yml
env:
  POLLING_TIMEOUT_MINUTES: '30'  # Default: 30
  POLLING_INTERVAL_SECONDS: '30'  # Default: 30
```

---

## Troubleshooting

### Issue: "No agents found"

**Fix**: Ensure agent definitions exist in `.github/agents/*.md`

### Issue: "Branch not found" (Pattern 2)

**Fix**: Check branch was created: `git branch -r | grep a2a-tasks`

### Issue: "Artifact not found" (Pattern 1)

**Fix**: Verify agent jobs completed: check workflow run page

### Issue: "PR not created"

**Fix**: Check last step logs, may need manual PR creation from branch

---

## Tips

1. **Start with Pattern 1** (Parallel Matrix) - fastest and most reliable
2. **Use auto_execute=true** for full automation
3. **Check issue comments** for progress updates
4. **Review `.a2a/` directory** to understand data flow
5. **Customize agent selection** for domain-specific tasks

---

## What Next?

- ✅ Run one of the examples above
- ✅ Review workflow logs to understand the flow
- ✅ Read [A2A_COPILOT_ORCHESTRATION_GUIDE.md](./A2A_COPILOT_ORCHESTRATION_GUIDE.md) for deep dive
- ✅ Explore agent definitions in `.github/agents/`
- ✅ Customize for your use case

**You have everything you need - the system is already built!** 🎉

---

## Reference Links

- [Full Orchestration Guide](./A2A_COPILOT_ORCHESTRATION_GUIDE.md) - Complete documentation
- [A2A README](./README.md) - A2A system overview
- [Branch Coordination](./A2A_BRANCH_BASED_COORDINATION.md) - Branch protocol details
- [Copilot Sessions](./A2A_COPILOT_SESSIONS_EXPLAINED.md) - How sessions work
