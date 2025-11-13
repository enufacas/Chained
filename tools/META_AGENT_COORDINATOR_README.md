# Meta-Agent Coordinator

## Overview

The Meta-Agent Coordinator is a sophisticated system for coordinating multiple specialized AI agents to work together on complex tasks. It provides intelligent task decomposition, agent selection, and collaboration management within the Chained autonomous AI ecosystem.

## Features

- **Task Analysis**: Automatically analyzes task complexity and requirements
- **Task Decomposition**: Breaks down complex tasks into manageable sub-tasks
- **Intelligent Agent Selection**: Chooses the best agents based on specialization and performance
- **Dependency Management**: Tracks dependencies between sub-tasks
- **Parallel Execution**: Identifies opportunities for concurrent agent work
- **Coordination Logging**: Maintains a log of all coordinations and statistics
- **Performance Tracking**: Monitors coordination success rates

## How It Works

### 1. Task Complexity Analysis

The coordinator analyzes task descriptions to determine complexity:

- **Simple**: Single agent, straightforward implementation
- **Moderate**: Single agent, complex implementation
- **Complex**: Multiple agents needed, some dependencies
- **Highly Complex**: Multiple agents, significant dependencies

Complexity is determined by:
- Number of different specializations required
- Presence of complexity keywords (comprehensive, full, system-wide, etc.)
- Task patterns (API, security, testing, documentation, etc.)

### 2. Task Decomposition

Complex tasks are automatically decomposed into sub-tasks:

```python
from meta_agent_coordinator import MetaAgentCoordinator

coordinator = MetaAgentCoordinator()

# Decompose a complex task
plan = coordinator.decompose_task(
    task_id="issue-123",
    task_description="""
    Build a new authentication API:
    - Design secure API endpoints
    - Implement with performance optimization
    - Add comprehensive test coverage
    - Document the API
    """
)

# Plan contains:
# - Sub-tasks for each specialization
# - Execution order
# - Parallel execution opportunities
# - Required agents
# - Estimated duration
```

### 3. Agent Selection

The coordinator selects the best agent for each sub-task based on:

1. **Specialization Match**: Agent's expertise aligns with sub-task requirements
2. **Performance History**: Agent's overall score and code quality
3. **Task Complexity**: Match agent capabilities to task difficulty

```python
# Select agents for the plan
assignments = coordinator.select_agents(plan)

# assignments = {
#   'issue-123-subtask-1': 'agent-1762898916',  # engineer-master
#   'issue-123-subtask-2': 'agent-1762996355',  # secure-specialist
#   'issue-123-subtask-3': 'agent-1762918927',  # assert-specialist
# }
```

### 4. Coordination Creation

Create a full coordination plan:

```python
coordination = coordinator.create_coordination(
    task_id="issue-123",
    task_description="Build authentication API...",
    task_context={'labels': ['api', 'security']}
)

# Coordination includes:
# - Complete decomposition plan
# - Agent assignments
# - Coordination ID for tracking
# - Timestamp and status
```

## Task Patterns

The coordinator recognizes these task patterns:

| Pattern | Keywords | Specialized Agents |
|---------|----------|-------------------|
| **Performance** | optimize, speed, latency, efficient | accelerate-master |
| **Testing** | test, coverage, validate, QA | assert-specialist |
| **Review** | review, feedback, best practices | coach-master, support-master |
| **Infrastructure** | infrastructure, build, pipeline | create-guru, engineer-master |
| **API** | api, endpoint, rest, interface | engineer-master, engineer-wizard |
| **Investigation** | investigate, analyze, debug | investigate-champion |
| **Security** | security, vulnerability, auth | secure-specialist, monitor-champion |
| **Refactor** | refactor, clean, duplication | organize-guru |
| **Documentation** | document, guide, tutorial | support-master |

## Dependency Management

The coordinator automatically establishes dependencies between sub-tasks:

```
investigation → security → infrastructure → api → performance
                                         ↓
                testing → review → documentation
```

Dependencies ensure:
- Investigation happens before implementation
- Security is addressed early
- Testing follows implementation
- Documentation comes after validation

## Command-Line Interface

```bash
# Analyze a task
python3 tools/meta_agent_coordinator.py analyze \
  --description "Build API with auth and testing"

# Create coordination
python3 tools/meta_agent_coordinator.py coordinate \
  --task-id "issue-123" \
  --description "Build API..." \
  --context '{"labels": ["api", "security"]}'

# View coordination summary
python3 tools/meta_agent_coordinator.py summary

# View specific coordination
python3 tools/meta_agent_coordinator.py summary \
  --coordination-id "coord-issue-123-1234567890"
```

## Integration with Agent System

The meta-coordinator integrates with the existing agent system:

1. **Registry Integration**: Reads agent information from `.github/agent-system/registry.json`
2. **Performance-Based Selection**: Uses agent metrics for selection decisions
3. **Coordination Logging**: Logs all coordinations in `.github/agent-system/coordination_log.json`
4. **Statistics Tracking**: Maintains coordination success statistics

## Output Format

### Coordination Plan

```json
{
  "task_id": "issue-123",
  "complexity": "complex",
  "sub_tasks": [
    {
      "id": "issue-123-subtask-1",
      "description": "Api work: Design and implement API endpoints",
      "required_specializations": ["engineer-master", "engineer-wizard"],
      "dependencies": [],
      "priority": 6,
      "estimated_effort": "high",
      "status": "pending",
      "assigned_agent": "agent-1762898916",
      "completion_criteria": [
        "API endpoints implemented",
        "API documentation complete",
        "API tests pass"
      ]
    }
  ],
  "execution_order": ["issue-123-subtask-1", "issue-123-subtask-2"],
  "parallel_groups": [["issue-123-subtask-3", "issue-123-subtask-4"]],
  "estimated_duration": "medium (4-8 hours)",
  "required_agents": ["engineer-master", "secure-specialist"]
}
```

## Statistics

The coordinator tracks these statistics:

- **Total Coordinations**: Number of tasks coordinated
- **Successful Coordinations**: Tasks completed successfully
- **Failed Coordinations**: Tasks that failed
- **Average Agents per Task**: Average number of agents involved

## Testing

Comprehensive test suite available in `tests/test_meta_agent_coordinator.py`:

```bash
python3 tests/test_meta_agent_coordinator.py
```

Tests cover:
- Task complexity analysis
- Task decomposition logic
- Agent selection algorithms
- Dependency tracking
- Execution ordering
- Statistics tracking

## Example Scenarios

### Scenario 1: Simple Documentation Task

```python
coordinator = MetaAgentCoordinator()
plan = coordinator.decompose_task(
    "doc-1",
    "Add README documentation for the project"
)

# Result:
# - Complexity: SIMPLE
# - 1 sub-task for support-master
# - No dependencies
# - Estimated duration: short
```

### Scenario 2: Complex API Development

```python
coordinator = MetaAgentCoordinator()
coordination = coordinator.create_coordination(
    "api-1",
    """
    Build user authentication API:
    - Investigate current auth patterns
    - Design secure endpoints
    - Implement with optimizations
    - Add comprehensive tests
    - Document the API
    """
)

# Result:
# - Complexity: HIGHLY_COMPLEX
# - 5 sub-tasks across multiple agents
# - Dependencies: investigation → api → testing
# - Parallel opportunities: documentation + performance
# - Estimated duration: long (1-3 days)
```

## Best Practices

1. **Clear Task Descriptions**: Provide detailed, specific task descriptions
2. **Include Context**: Add labels, related issues, or other context
3. **Monitor Progress**: Check coordination logs regularly
4. **Review Statistics**: Track coordination success rates
5. **Agent Performance**: Ensure agents have good performance scores

## Architecture

```
┌─────────────────────────────────────────────────┐
│          Meta-Agent Coordinator                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐    ┌──────────────┐          │
│  │   Task       │───▶│  Complexity  │          │
│  │   Analysis   │    │  Assessment  │          │
│  └──────────────┘    └──────────────┘          │
│         │                     │                  │
│         ▼                     ▼                  │
│  ┌──────────────┐    ┌──────────────┐          │
│  │    Task      │───▶│   Agent      │          │
│  │Decomposition │    │  Selection   │          │
│  └──────────────┘    └──────────────┘          │
│         │                     │                  │
│         ▼                     ▼                  │
│  ┌──────────────┐    ┌──────────────┐          │
│  │  Dependency  │───▶│ Coordination │          │
│  │   Tracking   │    │    Plan      │          │
│  └──────────────┘    └──────────────┘          │
│                                                  │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│         Agent System Registry                    │
│  • Active agents                                 │
│  • Specializations                               │
│  • Performance metrics                           │
└─────────────────────────────────────────────────┘
```

## Future Enhancements

Potential future improvements:

- **Real-time Coordination**: Monitor agent progress in real-time
- **Adaptive Scheduling**: Adjust execution order based on agent availability
- **Cross-Repository Coordination**: Coordinate agents across multiple repositories
- **Agent Communication**: Enable direct agent-to-agent communication
- **Machine Learning**: Learn optimal coordination patterns from history
- **Workload Balancing**: Distribute tasks more evenly across agents

## Related Documentation

- [Agent System Overview](../.github/agent-system/README.md)
- [Custom Agents](../.github/agents/README.md)
- [Meta-Coordinator Agent Definition](../.github/agents/meta-coordinator.md)

---

*Part of the Chained autonomous AI ecosystem - Orchestrating brilliant collaborations.* 🎯
