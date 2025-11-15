# Hierarchical Agent System

## Overview

The Hierarchical Agent System implements a true multi-tier agent organization for the Chained autonomous AI ecosystem. Instead of all agents operating at the same level, agents are organized into a hierarchy with coordinators, specialists, and workers—each with distinct responsibilities and delegation powers.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COORDINATOR TIER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     Meta     │  │    Coach     │  │   Support    │     │
│  │ Coordinator  │  │    Master    │  │    Master    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    SPECIALIST TIER                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Engineer │ │ Secure   │ │ Create   │ │ Organize │      │
│  │  Master  │ │Specialist│ │   Guru   │ │   Guru   │      │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │
│       │            │            │            │             │
└───────┼────────────┼────────────┼────────────┼─────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      WORKER TIER                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Accelerate│ │  Assert  │ │ Refactor │ │ Document │      │
│  │  Master  │ │Specialist│ │ Champion │ │   Ninja  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Key Concepts

### Agent Roles

#### Coordinator Tier
- **Responsibility**: High-level task analysis and delegation
- **Can delegate to**: Specialists and Workers
- **Reports to**: None (top tier)
- **Agents**:
  - `meta-coordinator`: Overall task coordination
  - `coach-master`: Code review and mentorship coordination
  - `support-master`: Documentation and training coordination

#### Specialist Tier
- **Responsibility**: Domain-specific implementation and design
- **Can delegate to**: Workers
- **Reports to**: Coordinators
- **Agents**:
  - `engineer-master`, `engineer-wizard`: API and infrastructure
  - `secure-specialist`: Security implementation
  - `create-guru`: Feature creation
  - `organize-guru`: Code organization
  - `investigate-champion`: Analysis and investigation
  - `monitor-champion`: System monitoring

#### Worker Tier
- **Responsibility**: Focused execution of specific tasks
- **Can delegate to**: None (execution tier)
- **Reports to**: Specialists
- **Agents**:
  - `accelerate-master`: Performance optimization
  - `assert-specialist`: Test creation
  - `refactor-champion`: Code refactoring
  - `document-ninja`: Documentation writing

### Delegation Chain

A delegation chain tracks work as it flows down the hierarchy:

```
Task → Coordinator → Specialist → Worker
                  ↓                ↓
           (oversight)      (oversight)
```

Each level can:
- **Delegate down**: Break work into smaller pieces
- **Escalate up**: Request help or guidance
- **Oversee down**: Monitor and review delegated work

## 🚀 Usage

### Installation

The hierarchical system is built on top of the existing meta-agent coordinator:

```bash
# No installation needed - part of the Chained tools
cd /path/to/Chained
python3 tools/hierarchical_agent_system.py --help
```

### Command-Line Interface

#### 1. View Hierarchy Summary

```bash
python3 tools/hierarchical_agent_system.py summary
```

Output:
```json
{
  "total_agents": 11,
  "by_role": {
    "coordinator": 2,
    "specialist": 5,
    "worker": 4
  },
  "delegation_chains": 0,
  "coordinator_agents": [...],
  "specialist_agents": [...],
  "worker_agents": [...]
}
```

#### 2. Create Hierarchical Plan

```bash
python3 tools/hierarchical_agent_system.py plan \
  --task-id "issue-123" \
  --description "Build authentication API with security audit and comprehensive testing" \
  --context '{"labels": ["api", "security"]}'
```

Output:
```json
{
  "coordination_plan": {
    "task_id": "issue-123",
    "complexity": "complex",
    "sub_tasks": [...],
    "execution_order": [...]
  },
  "delegation_chain": {
    "chain_id": "chain-issue-123-1234567890",
    "root_task_id": "issue-123",
    "coordinator_id": "agent-12345",
    "hierarchy": [
      {
        "level": 0,
        "role": "coordinator",
        "agent_id": "agent-12345",
        "task_id": "issue-123",
        "status": "pending"
      },
      {
        "level": 1,
        "tasks": [
          {
            "subtask_id": "issue-123-subtask-1",
            "role": "specialist",
            "agent_id": "agent-67890",
            "description": "Api work: Design and implement...",
            "status": "pending"
          }
        ]
      }
    ]
  }
}
```

#### 3. List Agents by Role

```bash
# List all coordinators
python3 tools/hierarchical_agent_system.py list --role coordinator

# List all specialists
python3 tools/hierarchical_agent_system.py list --role specialist

# List all workers
python3 tools/hierarchical_agent_system.py list --role worker

# List all agents
python3 tools/hierarchical_agent_system.py list
```

#### 4. Delegate Task

```bash
python3 tools/hierarchical_agent_system.py delegate \
  --from "agent-12345" \
  --to "agent-67890" \
  --description "Implement secure authentication endpoints"
```

### Python API

```python
from hierarchical_agent_system import HierarchicalAgentSystem, AgentRole

# Initialize the system
system = HierarchicalAgentSystem()

# Get hierarchy summary
summary = system.get_hierarchy_summary()
print(f"Total agents: {summary['total_agents']}")
print(f"Coordinators: {len(summary['coordinator_agents'])}")

# Create a hierarchical plan
plan, chain = system.create_hierarchical_plan(
    task_id="issue-456",
    task_description="Build user profile management system",
    task_context={'labels': ['feature', 'api']}
)

print(f"Complexity: {plan.complexity.value}")
print(f"Coordinator: {chain.coordinator_id}")
print(f"Subtasks: {len(plan.sub_tasks)}")

# Get agents by role
coordinators = system.get_coordinator_agents()
specialists = system.get_specialist_agents('engineer-master')
workers = system.get_worker_agents()

# Delegate a task (with validation)
try:
    delegation = system.delegate_task(
        from_agent="agent-coordinator-1",
        to_agent="agent-specialist-2",
        task_description="Design API architecture",
        context={'priority': 'high'}
    )
    print(f"Delegation created: {delegation['delegation_id']}")
except ValueError as e:
    print(f"Delegation not allowed: {e}")

# Escalate a task
escalation = system.escalate_task(
    from_agent="agent-worker-1",
    task_id="subtask-789",
    reason="Task complexity exceeds worker capability"
)
print(f"Escalated to: {escalation['to_agent']}")
```

## 🔧 Configuration

The hierarchical system is configured in `.github/agent-system/hierarchy.json`:

```json
{
  "version": "1.0.0",
  "enabled": true,
  "role_assignments": {
    "meta-coordinator": "coordinator",
    "engineer-master": "specialist",
    "accelerate-master": "worker"
  },
  "delegation_rules": {
    "coordinator": ["specialist", "worker"],
    "specialist": ["worker"],
    "worker": []
  },
  "oversight_enabled": true,
  "auto_escalation_enabled": true
}
```

### Configuration Options

- **enabled**: Enable/disable hierarchical mode (falls back to flat coordination)
- **role_assignments**: Map specializations to roles
- **delegation_rules**: Define who can delegate to whom
- **oversight_enabled**: Enable coordinator oversight of delegated work
- **auto_escalation_enabled**: Automatically escalate blocked tasks

## 📊 Delegation Tracking

All delegations are logged in `.github/agent-system/delegation_log.json`:

```json
{
  "version": "1.0.0",
  "delegation_chains": [
    {
      "delegation_id": "del-1234567890",
      "from_agent": "agent-coordinator",
      "from_role": "coordinator",
      "to_agent": "agent-specialist",
      "to_role": "specialist",
      "task_description": "Implement feature X",
      "status": "completed",
      "created_at": "2025-11-15T10:00:00Z"
    }
  ],
  "statistics": {
    "total_delegations": 42,
    "successful_delegations": 38,
    "escalations": 3,
    "avg_chain_length": 2.1
  }
}
```

## 🎯 Benefits

### 1. Clear Responsibility Hierarchy
- Each tier has well-defined responsibilities
- No confusion about who handles what
- Natural escalation path when needed

### 2. Efficient Task Decomposition
- Coordinators focus on high-level planning
- Specialists handle domain-specific work
- Workers execute focused tasks

### 3. Quality Oversight
- Higher tiers can review lower tier work
- Built-in quality control mechanism
- Knowledge transfer from experienced to new agents

### 4. Scalability
- Add new agents at appropriate tier
- Distribute workload across hierarchy
- Parallel execution at each level

### 5. Performance Optimization
- Match task complexity to agent capability
- Best agents at coordinator level
- Specialized skills at specialist level
- Fast execution at worker level

## 📈 Metrics and Monitoring

The system tracks:

### Delegation Metrics
- Total delegations
- Successful vs failed delegations
- Average chain length
- Escalation rate

### Agent Utilization
- Tasks per tier
- Agent workload distribution
- Delegation patterns

### Quality Metrics
- Task completion rate by tier
- Code quality scores by tier
- Review outcomes

## 🔄 Integration with Existing System

The hierarchical system integrates seamlessly with existing Chained components:

### 1. Agent Registry
- Reads agent data from `.github/agent-system/registry.json`
- Assigns roles based on specialization
- Uses performance metrics for selection

### 2. Meta-Agent Coordinator
- Built on top of `meta_agent_coordinator.py`
- Reuses task decomposition logic
- Extends with hierarchical delegation

### 3. Agent Spawner
- New agents assigned appropriate tier
- Tier affects initial task assignments
- Performance determines tier promotion

### 4. Evaluation System
- Agents evaluated within their tier
- Tier-specific performance expectations
- Promotion/demotion based on scores

## 🛠️ Advanced Features

### Automatic Escalation

When enabled, tasks are automatically escalated if:
- Worker cannot complete within time limit
- Specialist identifies task is out of scope
- Quality review fails

```python
# Automatic escalation example
if task.blocked_time > threshold:
    system.escalate_task(
        from_agent=current_agent,
        task_id=task.id,
        reason="Task blocked for too long"
    )
```

### Dynamic Tier Assignment

Agents can be promoted or demoted based on performance:

```python
def update_agent_tier(agent_id, performance_score):
    """
    Update agent tier based on performance
    """
    current_tier = system.agent_tiers[agent_id]
    
    if performance_score > 0.85 and current_tier.role == AgentRole.WORKER:
        # Promote to specialist
        promote_to_specialist(agent_id)
    elif performance_score < 0.30 and current_tier.role == AgentRole.SPECIALIST:
        # Demote to worker
        demote_to_worker(agent_id)
```

### Cross-Tier Collaboration

While delegation follows hierarchy, agents can collaborate horizontally:

```python
# Peer collaboration within same tier
specialist_1 = system.get_specialist_agents('engineer-master')[0]
specialist_2 = system.get_specialist_agents('secure-specialist')[0]

# Both can work on same task with different focuses
```

## 📝 Examples

### Example 1: Simple Documentation Task

```python
system = HierarchicalAgentSystem()

# Simple task assigned directly to worker
plan, chain = system.create_hierarchical_plan(
    "doc-1",
    "Update README with installation instructions"
)

# Result:
# - Assigned to: document-ninja (worker)
# - No delegation needed (simple task)
# - Reports to: support-master (coordinator)
```

### Example 2: Complex Feature Development

```python
system = HierarchicalAgentSystem()

plan, chain = system.create_hierarchical_plan(
    "feature-1",
    """
    Implement user authentication system:
    - Security audit
    - API design
    - Database schema
    - Unit tests
    - Integration tests
    - Documentation
    """
)

# Result:
# Level 0 (Coordinator): meta-coordinator receives task
# Level 1 (Specialists):
#   - secure-specialist: Security audit
#   - engineer-master: API design
#   - create-guru: Database schema
# Level 2 (Workers):
#   - assert-specialist: Unit tests (delegated by engineer-master)
#   - assert-specialist: Integration tests (delegated by secure-specialist)
#   - document-ninja: Documentation (delegated by support-master)
```

### Example 3: Task Escalation

```python
# Worker hits a blocker
worker_id = system.get_worker_agents('refactor-champion')[0]

escalation = system.escalate_task(
    from_agent=worker_id,
    task_id="refactor-subtask-1",
    reason="Refactoring requires architectural changes beyond scope"
)

# Result:
# - Escalated to: organize-guru (specialist)
# - Specialist reviews and either:
#   a) Provides guidance to worker
#   b) Takes over the task
#   c) Escalates further to coordinator
```

## 🚧 Future Enhancements

Potential improvements:

1. **Dynamic Rebalancing**: Automatically rebalance workload across tiers
2. **Learning-Based Tier Assignment**: ML-based role assignment
3. **Cross-Repository Hierarchies**: Coordinate across multiple repos
4. **Agent Mentorship**: Senior agents mentor junior agents
5. **Tier-Based Permissions**: Different permissions per tier
6. **Performance-Based Promotion**: Automatic tier promotion
7. **Collaboration Protocols**: Structured inter-tier communication

## 📚 Related Documentation

- [Meta-Agent Coordinator](./META_AGENT_COORDINATOR_README.md)
- [Agent System Overview](../.github/agent-system/README.md)
- [Custom Agents](../.github/agents/README.md)
- [Meta-Coordinator Agent](../.github/agents/meta-coordinator.md)

## 🤝 Contributing

When adding new agents:

1. Determine appropriate tier based on specialization
2. Update `hierarchy.json` if needed
3. Test delegation paths
4. Document tier-specific behaviors

## ⚖️ License

Part of the Chained project - see LICENSE file.

---

*Part of the Chained autonomous AI ecosystem - Building hierarchies that scale.* 🏗️
