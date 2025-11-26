# A2A (Agent-to-Agent) Protocol Documentation

## Overview

This directory contains all documentation related to the Agent2Agent (A2A) Protocol integration in the Chained autonomous AI ecosystem. The A2A Protocol enables the 100+ custom agents in Chained to discover each other, communicate, delegate tasks, and collaborate on complex work.

## 📚 Documentation Index

### Quick Start
- **[A2A_INTEGRATION_README.md](./A2A_INTEGRATION_README.md)** - Quick start guide, examples, and basic usage

### Architecture & Design
- **[A2A_GITHUB_RUNNERS_ARCHITECTURE.md](./A2A_GITHUB_RUNNERS_ARCHITECTURE.md)** - Core architecture for running A2A on GitHub Actions runners, three-tier design
- **[A2A_INTEGRATION_DESIGN.md](./A2A_INTEGRATION_DESIGN.md)** - Complete integration design, components, and API specifications
- **[A2A_GITHUB_RUNNERS_COMPLIANCE.md](./A2A_GITHUB_RUNNERS_COMPLIANCE.md)** - GitHub Actions runner constraints and compliance analysis

### Transport Layers
- **[A2A_TRANSPORT_COMPARISON.md](./A2A_TRANSPORT_COMPARISON.md)** - Comparison of different transport mechanisms (HTTP, GitHub Issues, GitHub Branches)
- **[A2A_MCP_TRANSPORT_DESIGN.md](./A2A_MCP_TRANSPORT_DESIGN.md)** - MCP (Model Context Protocol) transport design for Copilot agents

### Implementation Status
- **[A2A_STATUS.md](./A2A_STATUS.md)** - **⭐ Current implementation status and roadmap**
- **[A2A_IMPLEMENTATION_SUMMARY.md](./A2A_IMPLEMENTATION_SUMMARY.md)** - Phase 1 implementation summary
- **[A2A_PHASE_2B_TESTING_SUMMARY.md](./A2A_PHASE_2B_TESTING_SUMMARY.md)** - Phase 2B testing results and findings

## 🏗️ Architecture Overview

The A2A implementation uses a **three-tier architecture** to accommodate GitHub Actions runner constraints:

### Tier 1: Same-Runner (HTTP)
- **Use Case**: Multiple agents in single workflow job
- **Communication**: Traditional A2A HTTP protocol (localhost)
- **Performance**: Fast (<1ms latency)
- **Limitation**: All agents must run in same runner

### Tier 2: Cross-Runner (GitHub-Mediated)
- **Use Case**: Long-running tasks, parallel execution
- **Communication**: GitHub Issues or Branches as message bus
- **Performance**: Slower (~5s polling latency)
- **Benefit**: True parallelism across runners

### Tier 3: MCP-Native (Conceptual)
- **Use Case**: Copilot agent-to-agent communication
- **Communication**: Via github-mcp-server tools
- **Benefit**: No workflow overhead
- **Status**: Design phase

## 📂 Project Structure

```
Chained/
├── docs/a2a/                           # This directory - all documentation
├── tools/a2a/                          # Core A2A implementation
│   ├── agent_card.py                   # Agent Card generation
│   ├── agent_executor.py               # Agent execution wrapper
│   ├── agent_server.py                 # HTTP server wrapper
│   ├── client.py                       # A2A client
│   ├── discovery.py                    # Discovery service
│   ├── github_transport.py             # GitHub Issues transport
│   ├── github_branch_transport.py      # GitHub Branches transport
│   ├── mcp_transport.py                # MCP transport (future)
│   └── utils.py                        # Utilities
├── .github/workflows/
│   ├── a2a-agent-worker.yml            # Tier 2 worker
│   ├── a2a-local-orchestration.yml     # Tier 1 example
│   ├── a2a-test-quick-validation.yml   # Quick tests
│   ├── a2a-test-tier1-integration.yml  # Tier 1 tests
│   ├── a2a-test-multi-agent-demo.yml   # Demo workflow
│   ├── a2a-test-full-suite.yml         # Full test suite
│   └── README-A2A-TESTING.md           # Testing guide
├── tests/
│   ├── test_a2a_agent_cards.py         # Agent card tests
│   ├── test_a2a_discovery.py           # Discovery tests
│   ├── test_a2a_tier1.py               # Tier 1 tests
│   └── run_a2a_tests.py                # Test runner
└── examples/
    ├── a2a_agent_server.py             # Server example
    ├── a2a_client.py                   # Client example
    └── a2a_multi_agent_collaboration.py # Multi-agent demo
```

## 🚀 Implementation Status

### ✅ Phase 1: Foundation (Complete)
- Agent Card generation for 102 agents
- Base AgentExecutor class
- Core utilities and examples
- Design documentation

### ✅ Phase 2A: Core Infrastructure (Complete)
- Agent server wrapper (Tier 1)
- Discovery service
- A2A client
- GitHub transports (Tier 2)
- MCP transport design (Tier 3)
- Orchestration workflows

### ✅ Phase 2B: Testing & Integration (Complete)
- Agent card tests (102/102 passing)
- Discovery service tests
- Tier 1 integration tests
- Multi-agent collaboration demo
- Performance benchmarks
- Test workflows with auto-run

### 🔄 Phase 3: Meta-coordinator Integration (In Progress)
- Meta-coordinator A2A support
- Task decomposition and delegation
- Production multi-agent workflows
- Advanced orchestration patterns

### 📋 Future Phases
- Phase 4: Advanced Features (streaming, artifacts, forms)
- Phase 5: Production Hardening (monitoring, error handling, retry logic)
- Phase 6: External Compute (only if GitHub-based approach hits limits)

## 🧪 Testing

All A2A functionality is tested via automated workflows:

- **Quick Validation** (~2-3 min): Agent cards, discovery, imports
- **Tier 1 Integration** (~5-7 min): HTTP servers, communication, performance
- **Multi-Agent Demo** (~3-4 min): 3-agent collaboration scenario
- **Full Suite** (~8-10 min): All tests combined

See [.github/workflows/README-A2A-TESTING.md](../../.github/workflows/README-A2A-TESTING.md) for detailed testing guide.

## 🔑 Key Concepts

### Agent Cards
JSON descriptors of agent capabilities following A2A specification. Each Chained agent (from `.github/agents/*.md`) can generate an A2A-compliant card.

### Discovery Service
In-memory registry of available agents. Agents register on startup and can be discovered by name or skill.

### Task Lifecycle
Tasks follow standard A2A states: `submitted` → `working` → `completed`/`failed`

### Transport Layers
Different communication mechanisms for different contexts:
- **HTTP**: Fast, traditional, same-runner only
- **GitHub Issues**: Cross-runner, visible, tracked
- **GitHub Branches**: Cross-runner, clean workspace
- **MCP**: Native Copilot agent communication (future)

## 📖 Reading Order

If you're new to the A2A implementation, read in this order:

1. **A2A_STATUS.md** - ⭐ Start here for current status and roadmap
2. **A2A_INTEGRATION_README.md** - Quick start guide and examples
3. **A2A_GITHUB_RUNNERS_ARCHITECTURE.md** - Understand the architecture
4. **A2A_INTEGRATION_DESIGN.md** - Detailed component design
5. **A2A_IMPLEMENTATION_SUMMARY.md** - What was built in Phase 1
6. **A2A_PHASE_2B_TESTING_SUMMARY.md** - Testing results
7. **A2A_TRANSPORT_COMPARISON.md** - Transport options
8. **A2A_GITHUB_RUNNERS_COMPLIANCE.md** - Constraints and limitations
9. **A2A_MCP_TRANSPORT_DESIGN.md** - Future MCP integration

## 🔗 External Resources

- **A2A Protocol Specification**: https://github.com/a2aproject/A2A
- **A2A SDK Documentation**: https://pypi.org/project/a2a-sdk/
- **GitHub Actions Documentation**: https://docs.github.com/en/actions
- **MCP Documentation**: https://modelcontextprotocol.io/

## 🤝 Contributing

When working on A2A features:

1. **Read the architecture docs first** to understand constraints
2. **Follow the three-tier pattern** for appropriate contexts
3. **Add tests** for new functionality
4. **Update documentation** to reflect changes
5. **Run test workflows** before submitting PRs

## 📝 Notes

### Known Limitations
- **Port collisions**: 7 out of 102 agents have hash-based port collisions (acceptable for localhost testing)
- **Discovery API**: Some tests need updating to match actual API
- **Integration tests**: Some require real HTTP servers (use workflow tests)

### Performance Characteristics
- Agent card generation: ~1-2ms per card
- Discovery registration: ~5-8ms per agent  
- Tier 1 communication: <1ms latency
- Tier 2 communication: ~5s polling latency
- Setup overhead: ~50ms for 5 agents

## 📞 Support

For questions or issues:
- Check existing documentation in this directory
- Review test workflows and examples
- Open an issue in the repository
- Consult the A2A Protocol specification

---

**Last Updated**: 2025-11-26  
**Status**: Phase 2B Complete, Phase 3 Planning
