# A2A Orchestration Pattern Comparison

Quick visual comparison of the three orchestration patterns available in the Chained repository.

## Side-by-Side Comparison

| Feature | Pattern 1: Branch-Based | Pattern 2: Parallel Matrix | Pattern 3: Sequential |
|---------|-------------------------|----------------------------|----------------------|
| **Workflow** | `copilot-a2a-coordinator.yml` | `a2a-parallel-agents.yml` | `a2a-multi-agent.yml` |
| **Execution** | N separate runners (sequential) | N parallel jobs | 1 job (sequential) |
| **Speed** | 10-20 minutes | 5-10 minutes ⚡ | 5-10 minutes |
| **Communication** | Git branches | GitHub Artifacts | Filesystem |
| **State** | Persistent (branches) | Ephemeral (jobs) | Ephemeral (job) |
| **Isolation** | High (separate runners) | High (separate jobs) | Low (same job) |
| **Parallelism** | No (sequential by runner) | Yes (true parallel) ✅ | No (sequential) |
| **Agent Assignment** | GraphQL native Copilot | Auto-selected | Auto-selected |
| **Multi-Provider** | No (Gemini only) | Yes (Gemini + GitHub) ✅ | No (Gemini only) |
| **Complexity** | High | Medium | Low ✅ |
| **Resilience** | High (branches persist) ✅ | Medium | Low |
| **Best For** | Long tasks, state needed | Fast parallel analysis | Demos, simple tasks |

## Visual Architecture Comparison

### Pattern 1: Branch-Based (Sequential, Persistent)

```
┌─────────────┐
│ Coordinator │────┐
└─────────────┘    │
                   ├──► Branch 1 ──► Agent 1 (Runner 1) ──► Result 1 ──┐
                   │                                                     │
                   ├──► Branch 2 ──► Agent 2 (Runner 2) ──► Result 2 ──┤
                   │                                                     │
┌─────────────┐    │                                                     │
│ Coordinator │◄───┴──► Branch 3 ──► Agent 3 (Runner 3) ──► Result 3 ──┘
└─────────────┘
    Polls branches, aggregates results
    
Characteristics:
✅ Branches persist across failures
✅ Full agent isolation
❌ Slower (sequential execution)
❌ More complex (polling, branch cleanup)
```

### Pattern 2: Parallel Matrix (Concurrent, Ephemeral)

```
┌─────────────┐
│   Setup     │────┐
└─────────────┘    │
                   ├──► Agent 1 (Job 1) ──► Artifact 1 ──┐
                   │                                      │
                   ├──► Agent 2 (Job 2) ──► Artifact 2 ──┤
                   │                                      │
                   ├──► Agent 3 (Job 3) ──► Artifact 3 ──┤
                   │                                      │
┌─────────────┐    │                                      │
│  Aggregate  │◄───┴────────────────────────────────────┘
└─────────────┘
    Downloads all artifacts, combines
    
Characteristics:
✅ True parallelism (FASTEST)
✅ Multi-provider (Gemini + GitHub Models)
✅ Simple artifact passing
❌ No state persistence
```

### Pattern 3: Sequential (Single Job, Simple)

```
┌─────────────────────────────────────────┐
│          Single Job (1 Runner)          │
│                                         │
│  Setup                                  │
│    ↓                                    │
│  Agent 1 → Agent 2 → Agent 3            │
│    ↓         ↓         ↓                │
│  Analysis 1, 2, 3                       │
│    ↓                                    │
│  Aggregate → Implement → PR             │
│                                         │
└─────────────────────────────────────────┘

Characteristics:
✅ Simplest implementation
✅ No cross-job overhead
✅ Direct file access
❌ No parallelism
❌ No isolation
```

## Decision Matrix

### Choose Pattern 1 (Branch-Based) When:
- ✅ Tasks may take >10 minutes per agent
- ✅ Need persistent state across workflow runs
- ✅ Want native Copilot agent assignment
- ✅ Resilience to failures is critical
- ✅ Agents work independently

**Example**: Security audit with multiple specialized agents, each running comprehensive scans

### Choose Pattern 2 (Parallel Matrix) When:
- ✅ Speed is critical (need results fast)
- ✅ Tasks can run in parallel
- ✅ Want multi-provider AI (Gemini + GitHub Models)
- ✅ Agents analyze the same issue independently
- ✅ Don't need state persistence

**Example**: Quick issue triage with 5 agents analyzing simultaneously

### Choose Pattern 3 (Sequential) When:
- ✅ Task is simple and quick (<10 min total)
- ✅ Don't need runner isolation
- ✅ Sequential execution is acceptable
- ✅ Want simplest possible workflow
- ✅ Running a demo or test

**Example**: Documentation review by 2-3 agents, simple workflow

## Performance Characteristics

### Timing Breakdown

| Stage | Pattern 1 | Pattern 2 | Pattern 3 |
|-------|-----------|-----------|-----------|
| Setup | 30s | 20s | 15s |
| Agent Execution | 5-10 min each ×N | 2-5 min (parallel) | 3-5 min (sequential) |
| Aggregation | 10s | 10s | 5s |
| Implementation | 3-5 min | 3-5 min | 2-4 min |
| **Total** | **15-30 min** | **5-10 min** ⚡ | **5-10 min** |

### Resource Usage

| Resource | Pattern 1 | Pattern 2 | Pattern 3 |
|----------|-----------|-----------|-----------|
| Runners | 1 + N (sequential) | 1 + N + 2 (parallel) | 1 |
| Storage | Branches (persist) | Artifacts (7 days) | None |
| API Calls | GitHub API (polling) | GitHub API (minimal) | GitHub API (minimal) |

## Example Commands

### Pattern 1: Branch-Based
```bash
# For long-running security review
gh workflow run copilot-a2a-coordinator.yml \
  -f issue_number=123

# Timeline: 15-30 minutes
# Output: Coordination summary comment
```

### Pattern 2: Parallel Matrix
```bash
# For fast parallel analysis
gh workflow run a2a-parallel-agents.yml \
  -f issue_number=456 \
  -f agent_count=5 \
  -f provider=balanced \
  -f auto_execute=true

# Timeline: 5-10 minutes ⚡
# Output: PR created automatically
```

### Pattern 3: Sequential
```bash
# For simple demo
gh workflow run a2a-multi-agent.yml \
  -f issue_number=789 \
  -f agents="engineer-master,organize-guru" \
  -f auto_execute=true

# Timeline: 5-10 minutes
# Output: PR created
```

## Common Patterns by Use Case

| Use Case | Recommended Pattern | Why |
|----------|---------------------|-----|
| Quick issue triage | Pattern 2 | Speed, parallel analysis |
| Security audit | Pattern 1 | Persistent state, isolation |
| Code review | Pattern 2 | Fast, multi-perspective |
| Feature implementation | Pattern 2 | Fast analysis → implement |
| Documentation update | Pattern 3 | Simple, straightforward |
| Complex refactoring | Pattern 1 | Long-running, persistent state |
| Demo/Testing | Pattern 3 | Simplest, easy to understand |
| Emergency fix | Pattern 2 | Fastest turnaround |

## Migration Between Patterns

You can start with one pattern and migrate to another:

### From Pattern 3 → Pattern 2
**Why**: Need parallelism for faster execution
**How**: Same inputs, just switch workflow file

### From Pattern 2 → Pattern 1  
**Why**: Need persistent state or longer execution time
**How**: Add branch setup, change communication mechanism

### From Pattern 1 → Pattern 2
**Why**: Want faster execution with parallelism
**How**: Replace branch communication with artifacts

## Anti-Patterns

### ❌ Don't Use Pattern 1 When:
- Tasks complete in <5 minutes
- Don't need state persistence
- Speed is critical

### ❌ Don't Use Pattern 2 When:
- Agents have dependencies (need sequential execution)
- Need state persistence across failures
- Working with GitHub Actions rate limits

### ❌ Don't Use Pattern 3 When:
- Need true parallelism
- Tasks are long-running (>10 min)
- Need isolation between agents

## Summary

**Default recommendation**: Start with **Pattern 2 (Parallel Matrix)** for most use cases
- Fastest execution
- Good isolation
- Multi-provider support
- Clean artifact passing

**Upgrade to Pattern 1** if you need:
- Persistent state
- Native Copilot assignment
- Very long-running tasks

**Downgrade to Pattern 3** if you need:
- Simplicity over performance
- Quick demos
- Learning/testing

All three patterns are production-ready and actively used in the repository.

---

For complete documentation, see:
- [A2A_ORCHESTRATION_QUICK_START.md](./A2A_ORCHESTRATION_QUICK_START.md) - 30-second quick start
- [A2A_COPILOT_ORCHESTRATION_GUIDE.md](./A2A_COPILOT_ORCHESTRATION_GUIDE.md) - Complete guide
