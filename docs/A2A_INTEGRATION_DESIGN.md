# A2A Protocol Integration Design

## Overview

This document outlines the integration of the Agent2Agent (A2A) Protocol into the Chained autonomous AI ecosystem, enabling true multi-agent collaboration and communication.

## Background

### Current State
- **80+ custom agents** with specialized capabilities
- **Meta-coordinator** assigns agents to issues
- **Independent execution** - agents work in isolation
- **No inter-agent communication** - agents cannot delegate or collaborate

### A2A Protocol
The Agent2Agent (A2A) Protocol (https://github.com/a2aproject/A2A) is an open standard for AI agent communication that provides:
- **Agent Discovery** via Agent Cards (JSON descriptors of capabilities)
- **Task-based Collaboration** with standardized lifecycle (submitted → working → completed/failed)
- **Opaque Execution** - agents don't expose internal state
- **JSON-RPC 2.0** over HTTP(S) for communication
- **Multi-modal Support** - text, forms, media, files
- **Enterprise Ready** - authentication, observability, security

## Goals

1. **Enable Agent-to-Agent Communication**: Allow agents to discover and communicate with each other
2. **Support Task Delegation**: Enable agents to delegate sub-tasks to specialized agents
3. **Maintain Backward Compatibility**: Existing workflows continue to work
4. **Preserve Agent Autonomy**: Agents remain opaque and independent
5. **Use Standard Protocol**: Follow A2A specification for interoperability

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions Runner                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Agent Orchestration Layer                │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │         A2A Discovery Service               │  │  │
│  │  │  - Agent Card Registry                          │  │  │
│  │  │  - Agent Discovery API                          │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │   Agent 1   │  │   Agent 2   │  │   Agent 3   │  │  │
│  │  │             │  │             │  │             │  │  │
│  │  │ A2A Server  │  │ A2A Server  │  │ A2A Server  │  │  │
│  │  │ (Port 9001) │  │ (Port 9002) │  │ (Port 9003) │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │         │                 │                 │         │  │
│  │         └─────────────────┼─────────────────┘         │  │
│  │                           │                           │  │
│  │                    A2A Protocol                       │  │
│  │              (JSON-RPC 2.0 over HTTP)                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. A2A Agent Server (`tools/a2a/`)
Base classes and utilities for running agents as A2A servers:
- `AgentCard` generation from agent definitions
- `AgentExecutor` implementation for Chained agents
- HTTP server setup (FastAPI/Starlette)
- Task lifecycle management

#### 2. A2A Discovery Service (`tools/a2a/discovery.py`)
Registry of available agents and their capabilities:
- Agent card collection and indexing
- Discovery API for agent lookup
- Capability matching (skills, modalities)
- Health checking

#### 3. A2A Client Library (`tools/a2a/client.py`)
Utilities for agents to communicate with each other:
- Task creation and delegation
- Message exchange
- Streaming support
- Error handling

#### 4. Meta-Coordinator A2A Integration
Enhanced meta-coordinator with A2A capabilities:
- Task decomposition with A2A delegation
- Multi-agent collaboration orchestration
- Progress tracking across agents
- Result aggregation

## Implementation Plan

### Phase 1: Foundation (Current)
- [x] Research A2A protocol and specification
- [x] Study Python SDK and samples
- [x] Create integration design document
- [ ] Add a2a-sdk to requirements.txt
- [ ] Create base A2A infrastructure (`tools/a2a/`)
- [ ] Implement Agent Card generation
- [ ] Basic agent server template

### Phase 2: Core Infrastructure
- [ ] Implement A2A Discovery Service
- [ ] Create agent server wrapper for existing agents
- [ ] Build A2A client library
- [ ] Add task lifecycle management
- [ ] Implement basic delegation flow

### Phase 3: Meta-Coordinator Integration
- [ ] Enhance meta-coordinator with A2A support
- [ ] Implement task decomposition with delegation
- [ ] Add multi-agent collaboration patterns
- [ ] Progress tracking and result aggregation
- [ ] Error handling and recovery

### Phase 4: Agent Migration
- [ ] Identify pilot agents for A2A migration
- [ ] Create A2A-enabled agent definitions
- [ ] Test delegation between agents
- [ ] Validate task collaboration
- [ ] Performance benchmarking

### Phase 5: Workflows & Examples
- [ ] Create example multi-agent workflows
- [ ] Document collaboration patterns
- [ ] Add tutorials and guides
- [ ] Integration tests
- [ ] Performance optimization

### Phase 6: Production Readiness
- [ ] Security review (authentication, authorization)
- [ ] Observability (logging, metrics, tracing)
- [ ] Error handling and resilience
- [ ] Documentation completion
- [ ] Production deployment guide

## Agent Card Generation

### From Chained Agent Definition to A2A Agent Card

```python
# Chained agent definition (.github/agents/engineer-master.md)
---
name: engineer-master
description: "Specialized in engineering APIs"
specialization: api-engineering
tools:
  - github-mcp-server
  - bash
  - edit
---

# Converts to A2A Agent Card:
{
  "name": "engineer-master",
  "description": "Specialized in engineering APIs",
  "url": "http://localhost:9001/",
  "version": "1.0.0",
  "default_input_modes": ["text"],
  "default_output_modes": ["text", "artifact"],
  "capabilities": {
    "streaming": true
  },
  "skills": [
    {
      "id": "api_design",
      "name": "API Design",
      "description": "Design RESTful and GraphQL APIs",
      "tags": ["api", "design", "rest", "graphql"],
      "examples": ["Design a user authentication API", "Create GraphQL schema"]
    },
    {
      "id": "api_implementation",
      "name": "API Implementation",
      "description": "Implement API endpoints and handlers",
      "tags": ["api", "implementation", "coding"],
      "examples": ["Implement REST endpoints", "Add middleware"]
    }
  ]
}
```

### Skill Extraction Strategy

Skills can be derived from:
1. **Agent specialization** field → primary skill
2. **Agent description** → skill descriptions
3. **Pattern matching** from `tools/match-issue-to-agent.py` → skill examples
4. **Agent responsibilities** from markdown content → additional skills

## Task Delegation Flow

### Scenario: Multi-Agent API Development

```
Issue: "Implement user authentication API with security review"

┌─────────────────────────────────────────────────────────┐
│  Meta-Coordinator (A2A Client + Server)                 │
│                                                          │
│  1. Receives issue                                       │
│  2. Decomposes into sub-tasks:                          │
│     - API design and implementation                     │
│     - Security review                                   │
│     - Documentation                                     │
│  3. Discovers agents via A2A:                           │
│     - engineer-master (API development)                 │
│     - secure-specialist (security review)               │
│     - document-ninja (documentation)                    │
│  4. Creates A2A tasks for each agent                    │
│  5. Monitors progress                                   │
│  6. Aggregates results                                  │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│ engineer-   │    │ secure-          │    │ document-   │
│ master      │    │ specialist       │    │ ninja       │
│ (A2A Server)│    │ (A2A Server)     │    │ (A2A Server)│
│             │    │                  │    │             │
│ Receives    │    │ Receives         │    │ Receives    │
│ task via    │    │ task via         │    │ task via    │
│ A2A         │    │ A2A              │    │ A2A         │
│             │    │                  │    │             │
│ Executes    │    │ May delegate to  │◄───┤ Can request │
│ API work    │───►│ monitor-champion │    │ API details │
│             │    │ for additional   │    │             │
│ Returns     │    │ security checks  │    │ Returns     │
│ artifacts   │    │                  │    │ docs        │
└─────────────┘    └──────────────────┘    └─────────────┘
```

### A2A Task Lifecycle

```
Client Agent                    Server Agent
     │                               │
     │  1. POST /task/send-message   │
     ├──────────────────────────────►│
     │     (task submission)          │
     │                               │
     │  2. Task created               │
     │◄──────────────────────────────┤
     │     { task_id, status }        │
     │                               │
     │  3. GET /task/{task_id}        │
     ├──────────────────────────────►│
     │     (poll for updates)         │
     │                               │
     │  4. Status update              │
     │◄──────────────────────────────┤
     │     { status: "working" }      │
     │                               │
     │  5. Streaming events (SSE)     │
     │◄──────────────────────────────┤
     │     (progress updates)         │
     │                               │
     │  6. Task completion            │
     │◄──────────────────────────────┤
     │     { status: "completed",     │
     │       artifacts: [...] }       │
     │                               │
```

## Data Model

### Agent Registry Schema

```json
{
  "agents": [
    {
      "id": "engineer-master",
      "name": "engineer-master",
      "card_url": "http://localhost:9001/.well-known/agent-card",
      "endpoint": "http://localhost:9001",
      "port": 9001,
      "status": "active",
      "specialization": "api-engineering",
      "skills": ["api_design", "api_implementation"],
      "last_health_check": "2025-11-26T02:00:00Z"
    }
  ]
}
```

### Task Tracking Schema

```json
{
  "task_id": "uuid",
  "parent_task_id": "uuid",
  "created_by": "meta-coordinator",
  "assigned_to": "engineer-master",
  "status": "working",
  "created_at": "2025-11-26T02:00:00Z",
  "updated_at": "2025-11-26T02:05:00Z",
  "request": {
    "message": "Implement user authentication API",
    "context": {...}
  },
  "artifacts": [],
  "child_tasks": ["uuid1", "uuid2"]
}
```

## Configuration

### Environment Variables

```bash
# A2A Configuration
A2A_DISCOVERY_SERVICE_URL=http://localhost:9000
A2A_BASE_PORT=9001  # Starting port for agent servers
A2A_ENABLE_DISCOVERY=true
A2A_ENABLE_STREAMING=true
A2A_TASK_TIMEOUT=3600  # seconds

# Agent Server Configuration
A2A_AGENT_BASE_URL=http://localhost
A2A_AGENT_VERSION=1.0.0
A2A_ENABLE_HEALTH_CHECK=true
```

### File Structure

```
Chained/
├── tools/
│   └── a2a/
│       ├── __init__.py
│       ├── agent_card.py         # Agent Card generation
│       ├── agent_executor.py     # Base AgentExecutor for Chained
│       ├── agent_server.py       # HTTP server wrapper
│       ├── client.py             # A2A client utilities
│       ├── discovery.py          # Discovery service
│       ├── task_store.py         # Task persistence
│       └── utils.py              # Helper functions
├── .github/
│   ├── agents/
│   │   └── *.md                  # Agent definitions (unchanged)
│   └── workflows/
│       ├── a2a-discovery.yml     # Discovery service workflow
│       └── a2a-agent-server.yml  # Agent server launcher
└── docs/
    ├── A2A_INTEGRATION_DESIGN.md # This document
    ├── A2A_USAGE_GUIDE.md        # User guide (to be created)
    └── A2A_EXAMPLES.md           # Examples (to be created)
```

## Testing Strategy

### Unit Tests
- Agent Card generation from definitions
- Task lifecycle management
- Message serialization/deserialization
- Client library functionality

### Integration Tests
- Agent server startup and health
- Discovery service registration
- Task delegation between agents
- End-to-end multi-agent workflow

### Example Test Scenario

```python
# Test: Engineer delegates security review to secure-specialist
async def test_multi_agent_delegation():
    # 1. Start discovery service
    discovery = A2ADiscoveryService()
    
    # 2. Register agents
    engineer = await register_agent("engineer-master", port=9001)
    security = await register_agent("secure-specialist", port=9002)
    
    # 3. Engineer receives API development task
    task = create_task("Implement secure authentication API")
    
    # 4. Engineer discovers security agent
    agents = await engineer.discover_agents(skill="security_review")
    assert "secure-specialist" in agents
    
    # 5. Engineer delegates security review
    subtask = await engineer.delegate_task(
        agent="secure-specialist",
        task="Review authentication implementation"
    )
    
    # 6. Verify task completion
    result = await engineer.wait_for_task(subtask.id)
    assert result.status == "completed"
    assert "security_report" in result.artifacts
```

## Migration Path

### Backward Compatibility

Existing workflows continue to work:
- Agents without A2A capability work as before
- Meta-coordinator falls back to traditional assignment
- A2A is opt-in for agents

### Gradual Migration

1. **Infrastructure setup** (Phase 1-2)
2. **Pilot agents** (3-5 agents for initial testing)
3. **Meta-coordinator enhancement** (Phase 3)
4. **Expand agent coverage** (Phase 4)
5. **Production rollout** (Phase 6)

## Security Considerations

### Authentication
- Agent-to-agent authentication via tokens
- Discovery service access control
- Task authorization (who can delegate to whom)

### Data Privacy
- Opaque execution preserves agent internals
- Task data encryption in transit
- Audit logging for delegation

### Resource Limits
- Rate limiting on task creation
- Maximum delegation depth
- Task timeout enforcement

## Observability

### Metrics
- Task success/failure rates
- Agent response times
- Delegation patterns
- Resource utilization

### Logging
- Task lifecycle events
- Agent communication
- Errors and exceptions
- Performance bottlenecks

### Tracing
- OpenTelemetry integration
- Distributed tracing for multi-agent tasks
- Correlation IDs across agents

## Success Criteria

1. **Agent Communication**: Agents can discover and message each other
2. **Task Delegation**: Meta-coordinator successfully delegates to multiple agents
3. **Collaboration**: Multi-agent workflows complete end-to-end
4. **Performance**: Delegation overhead < 10% vs direct execution
5. **Reliability**: 99%+ task completion rate
6. **Documentation**: Complete guides and examples
7. **Compatibility**: Existing workflows unaffected

## Future Enhancements

### Beyond Initial Implementation

1. **Advanced Collaboration Patterns**
   - Agent teams and hierarchies
   - Parallel execution and racing
   - Consensus mechanisms

2. **Intelligent Routing**
   - ML-based agent selection
   - Load balancing
   - Cost optimization

3. **Extended Capabilities**
   - Voice/audio modalities
   - Form-based interactions
   - Real-time collaboration

4. **Ecosystem Integration**
   - Integration with external A2A agents
   - Cross-repository collaboration
   - Industry-specific agent libraries

## References

- **A2A Protocol**: https://github.com/a2aproject/A2A
- **A2A Specification**: https://a2a-protocol.org/latest/specification/
- **A2A Python SDK**: https://github.com/a2aproject/a2a-python
- **A2A Samples**: https://github.com/a2aproject/a2a-samples
- **Mission idea28 Research**: learnings/mission_idea28_ai_ml_agents_research_report.md

---

**Status**: Phase 1 - Foundation Design Complete  
**Next**: Implement base A2A infrastructure in `tools/a2a/`  
**Owner**: @meta-coordinator  
**Date**: 2025-11-26
