# Hierarchical Agent System - Quick Start Guide

Get started with the hierarchical agent system in 5 minutes!

## 🚀 What Is It?

The Hierarchical Agent System organizes AI agents into three tiers:
- **Coordinators**: High-level task management (meta-coordinator, coach-master, support-master)
- **Specialists**: Domain-specific work (engineer-master, secure-specialist, create-guru, etc.)
- **Workers**: Focused execution (accelerate-master, assert-specialist, etc.)

## 📦 Installation

No installation needed! The system is built into Chained.

## 🎯 Quick Commands

### View the Hierarchy

```bash
python3 tools/hierarchical_agent_system.py summary
```

Output shows total agents, breakdown by role, and statistics.

### List Agents by Role

```bash
# List coordinators
python3 tools/hierarchical_agent_system.py list --role coordinator

# List specialists
python3 tools/hierarchical_agent_system.py list --role specialist

# List workers
python3 tools/hierarchical_agent_system.py list --role worker
```

### Create a Hierarchical Plan

```bash
python3 tools/hierarchical_agent_system.py plan \
  --task-id "issue-123" \
  --description "Build authentication API with security and testing"
```

This creates:
- A coordination plan (subtasks, execution order, etc.)
- A delegation chain (coordinator → specialists → workers)

### Delegate a Task

```bash
python3 tools/hierarchical_agent_system.py delegate \
  --from "agent-coord-1" \
  --to "agent-spec-1" \
  --description "Implement secure endpoints"
```

## 🐍 Python API

```python
from hierarchical_agent_system import HierarchicalAgentSystem

# Initialize
system = HierarchicalAgentSystem()

# Create a hierarchical plan
plan, chain = system.create_hierarchical_plan(
    task_id="feature-1",
    task_description="Build user management system"
)

print(f"Coordinator: {chain.coordinator_id}")
print(f"Subtasks: {len(plan.sub_tasks)}")

# Get agents by role
coordinators = system.get_coordinator_agents()
specialists = system.get_specialist_agents()
workers = system.get_worker_agents()

# Delegate task
delegation = system.delegate_task(
    from_agent=coordinators[0],
    to_agent=specialists[0],
    task_description="Design API architecture"
)

# Escalate task
escalation = system.escalate_task(
    from_agent=workers[0],
    task_id="subtask-1",
    reason="Need architectural guidance"
)
```

## 🔄 Typical Workflow

### Scenario: Build Authentication System

**Step 1: Coordinator Receives Task**
```python
plan, chain = system.create_hierarchical_plan(
    "auth-1",
    "Build authentication system with OAuth and 2FA"
)
# Coordinator (meta-coordinator) analyzes and breaks down
```

**Step 2: Delegate to Specialists**
```python
# Delegate API work to engineer-master
delegation_1 = system.delegate_task(
    from_agent=coordinator_id,
    to_agent=engineer_specialist_id,
    task_description="Design and implement OAuth endpoints"
)

# Delegate security audit to secure-specialist
delegation_2 = system.delegate_task(
    from_agent=coordinator_id,
    to_agent=security_specialist_id,
    task_description="Audit authentication security"
)
```

**Step 3: Specialists Delegate to Workers**
```python
# Engineer-master delegates testing to assert-specialist
delegation_3 = system.delegate_task(
    from_agent=engineer_specialist_id,
    to_agent=test_worker_id,
    task_description="Write comprehensive API tests"
)

# Engineer-master delegates performance to accelerate-master
delegation_4 = system.delegate_task(
    from_agent=engineer_specialist_id,
    to_agent=perf_worker_id,
    task_description="Optimize authentication performance"
)
```

**Step 4: Monitor and Integrate**
- Workers complete focused tasks
- Specialists review worker output
- Coordinator oversees overall progress
- All work integrates into complete system

## 📊 Understanding the Output

### Summary Output
```json
{
  "total_agents": 11,
  "by_role": {
    "coordinator": 2,
    "specialist": 4,
    "worker": 5
  },
  "coordinator_agents": [...],
  "specialist_agents": [...],
  "worker_agents": [...]
}
```

### Delegation Chain Output
```json
{
  "hierarchy": [
    {
      "level": 0,
      "role": "coordinator",
      "agent_id": "agent-coord-1",
      "task_id": "issue-123"
    },
    {
      "level": 1,
      "tasks": [
        {
          "subtask_id": "issue-123-subtask-1",
          "role": "specialist",
          "agent_id": "agent-spec-1",
          "description": "Api work..."
        }
      ]
    }
  ]
}
```

## 💡 Key Concepts

### Delegation Rules
- **Coordinators** can delegate to specialists and workers
- **Specialists** can delegate to workers
- **Workers** cannot delegate (execution tier)

### Escalation Path
- **Workers** escalate to specialists
- **Specialists** escalate to coordinators
- System selects best available agent at target tier

### Performance-Based Selection
- Best agents serve as coordinators
- Domain experts serve as specialists
- Focused executors serve as workers

## 🎓 Common Patterns

### Pattern 1: Simple Task (Worker Only)
```
Documentation update → Document-ninja (worker)
No delegation needed
```

### Pattern 2: Medium Task (Specialist + Worker)
```
API feature → Engineer-master (specialist)
           → Assert-specialist (worker) for tests
```

### Pattern 3: Complex Task (All Tiers)
```
Full system → Meta-coordinator (coordinator)
           → Engineer-master (specialist) for API
           → Secure-specialist (specialist) for security
              → Accelerate-master (worker) for performance
              → Assert-specialist (worker) for tests
```

## 🔍 Monitoring

### Check Delegation Statistics
```bash
python3 tools/hierarchical_agent_system.py summary
```

Look at the `statistics` section:
- `total_delegations`: All delegations created
- `successful_delegations`: Completed successfully
- `escalations`: Tasks escalated up

### Configuration Files
- `.github/agent-system/hierarchy.json` - Role assignments and rules
- `.github/agent-system/delegation_log.json` - All delegations and statistics

## 🛠️ Troubleshooting

### "Cannot delegate to..." error
Check delegation rules. Coordinators can delegate to specialists/workers, specialists to workers only.

### "No coordinator agents available"
Ensure meta-coordinator, coach-master, or support-master agents exist in registry.

### Agent not in expected tier
Check `.github/agent-system/hierarchy.json` for role assignments.

## 📚 Next Steps

1. **Read Full Documentation**: `tools/HIERARCHICAL_AGENT_SYSTEM_README.md`
2. **Run Examples**: `python3 tools/examples/hierarchical_agent_system_examples.py`
3. **View Tests**: `tests/test_hierarchical_agent_system.py`
4. **Meta-Coordinator Agent**: `.github/agents/meta-coordinator.md`

## 🤝 Integration with Existing System

The hierarchical system works with:
- ✅ Agent Registry (`.github/agent-system/registry.json`)
- ✅ Meta-Agent Coordinator (`tools/meta_agent_coordinator.py`)
- ✅ Agent Evaluation System
- ✅ Performance Tracking

Use both systems together for maximum effectiveness!

---

*Part of the Chained autonomous AI ecosystem - Building hierarchies that scale.* 🏗️
