
# A2A Orchestration Patterns - Visual Flow

## Pattern 1: Parallel Matrix (FASTEST - 5-10 min)

```mermaid
graph TD
    Setup[Setup Job<br/>Select Agents<br/>Generate AgentCards] --> Matrix{Matrix Strategy}
    Matrix -->|Agent 1| Job1[Job 1<br/>Gemini Analysis]
    Matrix -->|Agent 2| Job2[Job 2<br/>GitHub Models]
    Matrix -->|Agent 3| Job3[Job 3<br/>Gemini Analysis]
    
    Job1 --> Artifact1[Upload Artifact 1]
    Job2 --> Artifact2[Upload Artifact 2]
    Job3 --> Artifact3[Upload Artifact 3]
    
    Artifact1 --> Agg[Aggregate Job<br/>Combine Results]
    Artifact2 --> Agg
    Artifact3 --> Agg
    
    Agg --> Impl[Implement Job<br/>Create PR]
    
    style Matrix fill:#90EE90
    style Agg fill:#FFD700
    style Impl fill:#87CEEB
```

**Characteristics**:
- ✅ TRUE PARALLELISM (3 jobs run simultaneously)
- ✅ Fastest execution (5-10 minutes)
- ✅ Multi-provider (Gemini + GitHub Models)
- ✅ Clean artifact passing

---

## Pattern 2: Branch-Based Coordination (MOST ROBUST - 10-20 min)

```mermaid
graph TD
    Coord1[Coordinator<br/>Parse Issue] --> Analysis[Task Analysis<br/>Identify Agents]
    Analysis --> Branch1[Create Branch 1<br/>Write task.json]
    Analysis --> Branch2[Create Branch 2<br/>Write task.json]
    Analysis --> Branch3[Create Branch 3<br/>Write task.json]
    
    Branch1 --> Assign1[Assign Agent 1<br/>via GraphQL]
    Branch2 --> Assign2[Assign Agent 2<br/>via GraphQL]
    Branch3 --> Assign3[Assign Agent 3<br/>via GraphQL]
    
    Assign1 --> Agent1[Agent 1 Runner<br/>Execute Work<br/>Write result.json]
    Assign2 --> Agent2[Agent 2 Runner<br/>Execute Work<br/>Write result.json]
    Assign3 --> Agent3[Agent 3 Runner<br/>Execute Work<br/>Write result.json]
    
    Agent1 --> Poll[Coordinator Polls<br/>Read Results]
    Agent2 --> Poll
    Agent3 --> Poll
    
    Poll --> Agg[Aggregate Results<br/>Post Summary]
    Agg --> Clean[Cleanup Branches]
    
    style Branch1 fill:#90EE90
    style Branch2 fill:#90EE90
    style Branch3 fill:#90EE90
    style Poll fill:#FFD700
```

**Characteristics**:
- ✅ Persistent state (branches survive failures)
- ✅ Native Copilot agent assignment
- ✅ Full isolation (separate runners)
- ❌ Sequential execution (polling-based)

---

## Pattern 3: Sequential Multi-Agent (SIMPLEST - 5-10 min)

```mermaid
graph TD
    Start[Single Job Start] --> Setup[Setup<br/>Install Dependencies]
    Setup --> Select[Select Agents<br/>Generate AgentCards]
    Select --> Gemini[Gemini CLI<br/>Process All Agents<br/>Sequential Analysis]
    Gemini --> Lifecycle[Lifecycle Orchestrator<br/>Package Artifacts]
    Lifecycle --> Context[Prepare Context<br/>.a2a/context/implementation.md]
    Context --> Implement[Implementing Agent<br/>Create PR]
    Implement --> Done[Done]
    
    style Gemini fill:#90EE90
    style Context fill:#FFD700
    style Implement fill:#87CEEB
```

**Characteristics**:
- ✅ Simplest (all in one job)
- ✅ No cross-job overhead
- ✅ Direct file access
- ❌ No parallelism
- ❌ No isolation

---

## Decision Tree

```mermaid
graph TD
    Q1{Need parallel<br/>execution?}
    Q1 -->|Yes| P1[Pattern 1:<br/>Parallel Matrix]
    Q1 -->|No| Q2{Need persistent<br/>state?}
    
    Q2 -->|Yes| P2[Pattern 2:<br/>Branch-Based]
    Q2 -->|No| Q3{Quick demo or<br/>simple task?}
    
    Q3 -->|Yes| P3[Pattern 3:<br/>Sequential]
    Q3 -->|No| P1B[Pattern 1:<br/>Parallel Matrix<br/>Recommended]
    
    style P1 fill:#90EE90
    style P2 fill:#FFB347
    style P3 fill:#87CEEB
    style P1B fill:#90EE90
```

---

## Performance Comparison

```mermaid
gantt
    title Execution Time Comparison (N=3 agents)
    dateFormat X
    axisFormat %s
    
    section Pattern 1 (Parallel)
    Setup           :p1_setup, 0, 20
    Parallel Exec   :p1_parallel, 20, 180
    Aggregate       :p1_agg, 200, 10
    Implement       :p1_impl, 210, 180
    
    section Pattern 2 (Branch)
    Setup           :p2_setup, 0, 30
    Agent 1         :p2_a1, 30, 300
    Agent 2         :p2_a2, 330, 300
    Agent 3         :p2_a3, 630, 300
    Aggregate       :p2_agg, 930, 10
    
    section Pattern 3 (Sequential)
    Setup           :p3_setup, 0, 15
    Sequential Exec :p3_seq, 15, 180
    Implement       :p3_impl, 195, 180
```

**Legend**:
- Pattern 1: **~6-7 minutes** (fastest due to parallelism)
- Pattern 2: **~15-20 minutes** (sequential, but most robust)
- Pattern 3: **~6-7 minutes** (simple, single job)

---

## Communication Flow Comparison

```mermaid
graph LR
    subgraph Pattern 1: Artifacts
        C1[Coordinator] --> A1[Agent 1]
        C1 --> A2[Agent 2]
        C1 --> A3[Agent 3]
        A1 --> Artifact[(GitHub Artifact)]
        A2 --> Artifact
        A3 --> Artifact
        Artifact --> Agg1[Aggregator]
    end
    
    subgraph Pattern 2: Branches
        C2[Coordinator] --> B1[Branch 1]
        C2 --> B2[Branch 2]
        C2 --> B3[Branch 3]
        B1 --> AG1[Agent 1]
        B2 --> AG2[Agent 2]
        B3 --> AG3[Agent 3]
        AG1 --> B1
        AG2 --> B2
        AG3 --> B3
        B1 --> Poll[Polling]
        B2 --> Poll
        B3 --> Poll
    end
    
    subgraph Pattern 3: Filesystem
        C3[Coordinator] --> FS[.a2a/ Directory]
        FS --> SEQ[Sequential Agents]
        SEQ --> FS
        FS --> Impl[Implement]
    end
```

---

## Use Case Recommendations

| Use Case | Recommended Pattern | Why |
|----------|---------------------|-----|
| 🔥 **Emergency Fix** | Pattern 1 (Parallel) | Fastest turnaround |
| 🔒 **Security Audit** | Pattern 2 (Branch) | Persistent state, isolation |
| 💡 **Quick Triage** | Pattern 1 (Parallel) | Fast parallel analysis |
| 🏗️ **Complex Refactor** | Pattern 2 (Branch) | Long-running, state needed |
| 📝 **Doc Review** | Pattern 3 (Sequential) | Simple, straightforward |
| 🎯 **Demo/Test** | Pattern 3 (Sequential) | Easiest to understand |
| ⚡ **Feature Request** | Pattern 1 (Parallel) | Fast analysis → implement |

---

## Quick Start Commands

### Pattern 1: Fast Parallel
```bash
gh workflow run a2a-parallel-agents.yml \
  -f issue_number=123 \
  -f agent_count=5 \
  -f provider=balanced \
  -f auto_execute=true
```

### Pattern 2: Branch-Based
```bash
gh workflow run copilot-a2a-coordinator.yml \
  -f issue_number=456
```

### Pattern 3: Sequential
```bash
gh workflow run a2a-multi-agent.yml \
  -f issue_number=789 \
  -f agents="engineer-master,organize-guru" \
  -f auto_execute=true
```
