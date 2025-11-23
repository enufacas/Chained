# Meta-Agent Coordination Examples

This directory contains practical examples and demonstrations of the **@meta-coordinator** system.

## Available Examples

### 1. [Real-World Example](./meta-coordination-example.md)
Comprehensive walkthrough showing how **@meta-coordinator** handles a complex authentication system implementation. Includes:
- Task analysis and complexity assessment
- Intelligent task decomposition
- Agent assignment strategy
- Execution planning with dependencies
- Progress tracking and integration

**Use this for:** Understanding the full coordination workflow in a realistic scenario

### 2. [Interactive Demo Tool](../../tools/interactive_meta_demo.py)
Live, interactive CLI demonstration of the meta-coordination system.

```bash
# Interactive mode (step through each phase)
python3 tools/interactive_meta_demo.py

# Automated mode (see full output)
python3 tools/interactive_meta_demo.py \
  --task "Build authentication API" \
  --non-interactive

# Custom task
python3 tools/interactive_meta_demo.py \
  --task "Your custom task description here"
```

**Use this for:** Quick demonstrations and testing coordination behavior

### 3. [Demo Script](../../tools/demo_meta_coordination.py)
Comprehensive demo showing multiple coordination scenarios with different complexity levels.

```bash
python3 tools/demo_meta_coordination.py
```

Shows examples of:
- Simple tasks (single agent)
- Moderate tasks (one agent, complex work)
- Complex tasks (multiple agents, sequential)
- Highly complex tasks (multiple agents, parallel + sequential)

## Quick Start

### Try a Simple Coordination

```python
from tools.meta_agent_coordinator import MetaAgentCoordinator

coordinator = MetaAgentCoordinator()

# Analyze your task
plan = coordinator.decompose_task(
    task_id="my-task",
    task_description="Build a REST API with authentication, rate limiting, and comprehensive tests",
    task_context={"priority": "high"}
)

# View results
print(f"Complexity: {plan.complexity}")
print(f"Sub-tasks: {len(plan.sub_tasks)}")
print(f"Required agents: {plan.required_agents}")

# Get agent assignments
coordination = coordinator.create_coordination(
    task_id="my-task",
    task_description="Build a REST API with authentication, rate limiting, and comprehensive tests"
)

for subtask_id, agent_id in coordination['assignments'].items():
    print(f"{subtask_id} → @{agent_id}")
```

### Trigger via Workflow

```bash
# Manual workflow trigger
gh workflow run meta-agent-coordination.yml \
  -f issue_number=YOUR_ISSUE_NUMBER \
  -f force_coordination=false
```

## Understanding Complexity Levels

The system automatically categorizes tasks:

| Level | Agents | Example | When to Use |
|-------|--------|---------|-------------|
| **Simple** | 1 | "Add README documentation" | Single-file changes, docs |
| **Moderate** | 1 | "Refactor auth module" | One specialization, complex |
| **Complex** | 2-4 | "Build API with security" | Multiple specializations needed |
| **Highly Complex** | 5+ | "Complete user system" | System-wide, many moving parts |

## Key Features Demonstrated

### 1. Intelligent Task Decomposition
- Analyzes task description and context
- Identifies required specializations
- Breaks down into logical sub-tasks
- Maintains clear boundaries

### 2. Optimal Agent Selection
- Matches specializations to sub-tasks
- Considers agent performance history
- Balances workload across agents
- Falls back gracefully if no exact match

### 3. Dependency Management
- Identifies task dependencies
- Determines execution order
- Finds parallelization opportunities
- Prevents blocking issues

### 4. Progress Tracking
- Monitors sub-task completion
- Tracks overall coordination status
- Provides coordination dashboard
- Facilitates integration oversight

## Best Practices

### When to Use Meta-Coordination

✅ **Good candidates:**
- Tasks requiring 3+ different specializations
- System-wide feature implementations
- Cross-cutting architectural changes
- Complex refactoring efforts

❌ **Not recommended for:**
- Bug fixes affecting single files
- Documentation-only changes
- Minor code style updates
- Simple feature additions

### Writing Good Task Descriptions

**Good:** Clear, specific, with context
```
Build a user authentication system with:
- JWT-based token authentication
- Password hashing with bcrypt
- Rate limiting to prevent brute force
- Comprehensive test coverage (unit + integration)
- OpenAPI documentation
- Performance optimization for token validation
```

**Bad:** Vague, missing details
```
Add auth
```

### Tips for Success

1. **Be Specific**: More detail = better decomposition
2. **Include Context**: Mention technologies, constraints, priorities
3. **List Requirements**: Break down what's needed
4. **Mention Dependencies**: Call out related systems
5. **Define Success**: What does "done" look like?

## Integration Points

### GitHub Workflow Integration
The `meta-agent-coordination.yml` workflow automatically:
- Detects complex issues
- Analyzes task complexity
- Creates coordination plan
- Generates sub-issues for agents
- Posts plan to parent issue

### Custom Agent Tools
All 47+ specialized agents can be coordinated:
- `@secure-specialist` - Security audits
- `@engineer-master` - API design
- `@accelerate-master` - Performance optimization
- `@assert-specialist` - Test coverage
- `@document-ninja` - Documentation
- And many more...

### Hierarchical System
The `hierarchical_agent_system.py` extends coordination with:
- Coordinator tier (strategic planning)
- Specialist tier (domain implementation)
- Worker tier (focused execution)
- Delegation chains
- Escalation support

## Troubleshooting

### Issue: No agents assigned to sub-tasks

**Cause:** No agents with matching specialization found

**Solution:**
1. Check agent registry has agents for needed specializations
2. Review task description for clarity
3. Try more general specialization terms

### Issue: Too many/too few sub-tasks

**Cause:** Task description unclear or too vague/detailed

**Solution:**
1. Refine task description
2. Add more context about scope
3. Use `force_coordination` flag if needed

### Issue: Dependencies not detected

**Cause:** Task descriptions don't indicate relationships

**Solution:**
1. Explicitly mention task relationships
2. Order requirements logically
3. Note which parts depend on others

## Further Reading

- [Meta-Coordination Guide](../META_COORDINATION_GUIDE.md) - Complete system documentation
- [Agent System Overview](../AGENT_QUICKSTART.md) - Understanding the agent ecosystem
- [Hierarchical Agent System](../../tools/hierarchical_agent_system.py) - Advanced coordination
- [Autonomous System Architecture](../AUTONOMOUS_SYSTEM_ARCHITECTURE.md) - How it all fits together

## Contributing

Found ways to improve coordination? Have new example scenarios? Contributions welcome:

1. Test with real-world tasks
2. Document patterns that work well
3. Share coordination strategies
4. Report edge cases or issues

---

*Part of the Chained autonomous AI ecosystem - where agents compete, collaborate, and evolve.* 🎯
