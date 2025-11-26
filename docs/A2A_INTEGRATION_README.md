# A2A (Agent-to-Agent) Protocol Integration

## Overview

The Chained repository now supports the **Agent2Agent (A2A) Protocol**, enabling true multi-agent collaboration and communication. This integration allows the 100+ custom agents in Chained to discover each other, delegate tasks, and collaborate on complex work.

## What is A2A?

The A2A Protocol (https://github.com/a2aproject/A2A) is an open standard for AI agent communication that provides:

- **Agent Discovery**: Agents publish "Agent Cards" describing their capabilities
- **Task-based Collaboration**: Standardized task lifecycle (submitted → working → completed)
- **Opaque Execution**: Agents maintain internal privacy
- **JSON-RPC 2.0**: Standard communication protocol over HTTP(S)
- **Multi-modal Support**: Text, forms, media, files, and artifacts

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs `a2a-sdk[http-server]>=0.2.0` along with other dependencies.

### 2. Generate Agent Cards

```python
from tools.a2a import generate_agent_card

# Generate a card for any Chained agent
card = generate_agent_card("engineer-master")
print(card.model_dump_json(indent=2))
```

Output:
```json
{
  "name": "engineer-master",
  "description": "Specialized in engineering APIs...",
  "url": "http://localhost:9788/",
  "version": "1.0.0",
  "skills": [
    {
      "id": "engineer_master",
      "name": "Engineer Master",
      "description": "Specialized agent for engineering APIs...",
      "tags": ["engineer-master"],
      "examples": ["Help me with APIs"]
    }
  ],
  "capabilities": {
    "streaming": true
  }
}
```

### 3. Generate All Agent Cards

```python
from tools.a2a import generate_all_agent_cards

# Generate cards for all 100+ agents
cards = generate_all_agent_cards()
print(f"Generated {len(cards)} agent cards")

# List available agents
for name, card in cards.items():
    print(f"{name}: {len(card.skills)} skills")
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Chained Repository                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         .github/agents/*.md (100+ agents)            │   │
│  │  - engineer-master.md                                │   │
│  │  - secure-specialist.md                              │   │
│  │  - organize-guru.md                                  │   │
│  │  - troubleshoot-expert.md                            │   │
│  │  - meta-coordinator.md                               │   │
│  │  - ... 95+ more agents ...                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │      tools/a2a/ (A2A Integration)                    │   │
│  │  - agent_card.py: Generate A2A cards                 │   │
│  │  - agent_executor.py: Execute agents via A2A         │   │
│  │  - utils.py: Configuration and helpers               │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           A2A Agent Cards (JSON)                     │   │
│  │  Each agent becomes an A2A-compatible service        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              A2A Protocol Communication
        (Task delegation, message exchange, streaming)
```

## Components

### `tools/a2a/agent_card.py`
Generates A2A Agent Cards from Chained agent definitions:
- Parses YAML frontmatter from `.github/agents/*.md`
- Extracts skills from agent specializations and responsibilities
- Creates A2A-compliant AgentCard objects
- Supports batch generation for all agents

### `tools/a2a/agent_executor.py`
Base executor for running Chained agents via A2A:
- `ChainedAgentExecutor`: Wraps agents for A2A execution
- Handles task lifecycle (execute, cancel)
- Supports event streaming
- Placeholder for actual agent execution integration

### `tools/a2a/utils.py`
Utility functions:
- `get_agent_port()`: Assign consistent ports to agents
- `get_discovery_url()`: Get discovery service URL
- Configuration helpers

## Current Implementation Status

### ✅ Completed (Phase 1)

1. **Design Document**: `docs/A2A_INTEGRATION_DESIGN.md`
   - Comprehensive architecture
   - Implementation plan
   - Data models and workflows

2. **Core Infrastructure**: `tools/a2a/`
   - Agent card generation
   - Base agent executor
   - Utility functions

3. **Agent Card Generation**:
   - Successfully generates cards for 102 agents
   - Extracts skills from agent definitions
   - Assigns consistent ports
   - A2A-compliant format

### 🚧 In Progress (Phase 2)

- [ ] Agent server wrapper (HTTP server for agents)
- [ ] Discovery service (agent registry)
- [ ] A2A client library (agent-to-agent communication)
- [ ] Task store and lifecycle management

### 📋 Planned (Phases 3-6)

- [ ] Meta-coordinator A2A integration
- [ ] Multi-agent collaboration workflows
- [ ] Example multi-agent tasks
- [ ] Production deployment

## Example: Agent Card for engineer-master

```json
{
  "name": "engineer-master",
  "description": "Specialized agent for engineering APIs. Inspired by 'Margaret Hamilton' - rigorous and innovative, with systematic approach. Focuses on features, infrastructure, and tools.",
  "url": "http://localhost:9788/",
  "version": "1.0.0",
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text", "artifact"],
  "capabilities": {
    "streaming": true
  },
  "skills": [
    {
      "id": "engineer_master",
      "name": "Engineer Master",
      "description": "Specialized agent for engineering APIs...",
      "tags": ["engineer-master"],
      "examples": [
        "Help me with specialized agent for engineering apis..."
      ]
    }
  ]
}
```

## Future Capabilities

Once fully implemented, the A2A integration will enable:

1. **Agent Discovery**: Agents can find each other by skill
2. **Task Delegation**: Meta-coordinator can delegate to multiple agents
3. **Multi-Agent Workflows**: Complex tasks handled by agent teams
4. **Real-time Collaboration**: Agents communicate during execution
5. **Standard Protocol**: Interoperate with external A2A agents

## Example Multi-Agent Flow (Future)

```
Issue: "Implement secure authentication API with documentation"

Meta-Coordinator receives issue
    ├─► Discovers agents via A2A
    │   ├─ engineer-master (API development)
    │   ├─ secure-specialist (security review)
    │   └─ document-ninja (documentation)
    │
    ├─► Creates A2A tasks:
    │   ├─ Task 1 → engineer-master: "Implement API"
    │   ├─ Task 2 → secure-specialist: "Security review"
    │   └─ Task 3 → document-ninja: "Document API"
    │
    └─► Monitors and aggregates results
        └─ Returns complete solution with all artifacts
```

## Testing

```bash
# Test agent card generation
python3 -m tools.a2a.agent_card engineer-master

# Test multiple agents
python3 -c "
from tools.a2a import generate_all_agent_cards
cards = generate_all_agent_cards()
print(f'Generated {len(cards)} cards')
"
```

## Configuration

Environment variables for A2A integration:

```bash
# Agent server configuration
A2A_AGENT_BASE_URL=http://localhost  # Base URL for agents
A2A_BASE_PORT=9001                    # Starting port for agents

# Discovery service
A2A_DISCOVERY_SERVICE_URL=http://localhost:9000

# Features
A2A_ENABLED=true
A2A_ENABLE_STREAMING=true
A2A_TASK_TIMEOUT=3600  # seconds
```

## Documentation

- **[Design Document](./A2A_INTEGRATION_DESIGN.md)**: Complete architecture and implementation plan
- **[A2A Protocol](https://a2a-protocol.org)**: Official A2A specification
- **[A2A Python SDK](https://github.com/a2aproject/a2a-python)**: SDK documentation

## Contributing

The A2A integration is under active development. Key areas for contribution:

1. **Agent Server Implementation**: Complete the HTTP server wrapper
2. **Discovery Service**: Implement agent registry and discovery
3. **Testing**: Create integration tests for A2A flows
4. **Examples**: Add multi-agent collaboration examples
5. **Documentation**: Improve guides and tutorials

## References

- **A2A Protocol**: https://github.com/a2aproject/A2A
- **A2A Samples**: https://github.com/a2aproject/a2a-samples
- **Research Report**: `learnings/mission_idea28_ai_ml_agents_research_report.md`

---

**Status**: Phase 1 Complete - Foundation Established  
**Next**: Phase 2 - Implement Server and Discovery Components  
**Branch**: `copilot/implement-agent-orchestration`
