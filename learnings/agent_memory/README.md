# Agent Memory Storage Directory

This directory stores persistent memory files for Chained's autonomous agents.

## Purpose

Each agent maintains a memory file containing:
- Past experiences (context, action, outcome)
- Success/failure patterns
- Metadata about completed work

## File Format

Memory files are named: `{agent-id}_memory.json`

Example: `agent-investigate-champion_memory.json`

## Usage

The memory system is managed by `tools/agent_memory_system.py`:

```python
from tools.agent_memory_system import AgentMemoryEngine

# Create or load memory for an agent
memory = AgentMemoryEngine("agent-investigate-champion")

# Store an experience
memory.store(
    context="Issue description",
    action="What the agent did",
    outcome="Result of the action",
    success=True,
    metadata={"issue_id": "123"}
)

# Retrieve similar past experiences
similar = memory.retrieve_similar("similar issue description")
```

## Directory Structure

```
learnings/agent_memory/
├── README.md (this file)
├── agent-investigate-champion_memory.json
├── agent-create-guru_memory.json
├── agent-secure-specialist_memory.json
└── shared/
    └── best-practices.json
```

## Note

Memory files are excluded from version control via `.gitignore` to prevent repository bloat. Each Chained instance maintains its own agent memories locally.

---

*Created during AI/ML Agents Investigation (Mission idea:17) by @investigate-champion*
