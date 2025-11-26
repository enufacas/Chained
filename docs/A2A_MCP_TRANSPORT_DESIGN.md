# A2A MCP Transport Design

## Overview

This document clarifies the relationship between GitHub MCP Server tools and the A2A transport layer, addressing a common question: "Should we use MCP tools for GitHub API operations?"

## The Question

> "Wouldn't we also use the github mcp server to do the writing and reading? Or is that inherent in the design already?"

## The Answer

**It depends on the execution context.** There are actually **two different execution contexts** where A2A communication happens:

### Context 1: GitHub Actions Workflows

**Environment:**
- Python code running in GitHub Actions runners
- No access to Copilot MCP tools
- Standard Python libraries available (httpx, requests, PyGithub)

**Current Implementation:**
- ✅ `github_transport.py` - Uses httpx for GitHub API calls
- ✅ `github_branch_transport.py` - Uses httpx for GitHub API calls

**Why not MCP?**
- MCP tools are not available in standard Python runtime
- GitHub Actions workflows need portable, dependency-based solutions
- httpx/requests are industry-standard for API access in production

### Context 2: Copilot Agent Environment

**Environment:**
- Copilot agent executing tasks
- MCP tools available via function calling
- Running in Copilot runtime, not GitHub Actions

**Proposed Implementation:**
- 🔜 `mcp_transport.py` - Uses github-mcp-server tools
- Provides Tier 3 communication (agent-to-agent without workflows)

**Why MCP?**
- ✅ Consistent with Copilot ecosystem patterns
- ✅ Built-in authentication via Copilot context
- ✅ Cleaner integration with other Copilot operations
- ✅ No HTTP client management needed

## Three-Tier Architecture (Expanded)

### Tier 1: Same-Runner HTTP
**Use Case:** Multiple agents in one workflow job

```python
# Running in GitHub Actions workflow
from tools.a2a import ChainedA2AClient

# Agents communicate via localhost HTTP
async with ChainedA2AClient() as client:
    result = await client.send_message("agent", "task")
```

**Implementation:** HTTP servers on localhost (uses a2a-sdk)

### Tier 2: GitHub-Mediated (Workflows)
**Use Case:** Cross-runner tasks that trigger workflows

```python
# Running in GitHub Actions workflow
from tools.a2a import send_task_via_github

# Create issue/branch, trigger workflow
issue = await send_task_via_github(agent, message, token, owner, repo)
```

**Implementation:** 
- `github_transport.py` (httpx → GitHub API)
- `github_branch_transport.py` (httpx → GitHub API)

### Tier 3: MCP-Native (Future)
**Use Case:** Copilot agent delegates to another Copilot agent

```python
# Running in Copilot environment (not GitHub Actions)
from tools.a2a import MCPTransport

# Uses MCP tools via function calling
transport = MCPTransport(owner, repo)
task = await transport.create_task(agent, message)
```

**Implementation:**
- `mcp_transport.py` (MCP tools via function calling)
- Not yet fully implemented (placeholder with design notes)

## When to Use Each

| Tier | When | Environment | Tools |
|------|------|-------------|-------|
| 1 | Fast, local multi-agent | GitHub Actions | HTTP (localhost) |
| 2 | Cross-runner workflows | GitHub Actions | httpx → GitHub API |
| 3 | Agent-to-agent direct | Copilot | MCP Server Tools |

## Current Status

**Implemented (Phase 2A):**
- ✅ Tier 1: Same-runner HTTP communication
- ✅ Tier 2: Two transport options (issues and branches)
  - Both use httpx for GitHub API calls
  - Designed for GitHub Actions workflows
  - Production-ready

**Designed but Not Implemented:**
- 🔜 Tier 3: MCP-native transport
  - Conceptual design in `mcp_transport.py`
  - Shows how Copilot agents would use MCP tools
  - Requires running in Copilot environment
  - Would use function calling to invoke github-mcp-server tools

## Why Not Refactor Tier 2 to Use MCP?

The existing Tier 2 transports (`github_transport.py`, `github_branch_transport.py`) are designed to run in **GitHub Actions workflows**, not the Copilot environment. They need to work in standard Python runtime with typical dependencies.

**Keeping httpx for Tier 2 is correct because:**

1. **Portability:** Works in any Python environment
2. **Standard Practice:** httpx/requests are industry-standard for API access
3. **Production Ready:** Well-tested, documented, widely used
4. **Workflow Context:** GitHub Actions don't have MCP tools
5. **Clear Separation:** Different tools for different contexts

## MCP Transport Use Case

The MCP transport would enable a **new capability** not covered by Tier 1 or 2:

**Scenario:** Copilot agent running a task wants to delegate sub-work to another Copilot agent without spinning up a full GitHub Actions workflow.

**Example:**
```
User asks Copilot to "Analyze codebase and fix issues"

Copilot (orchestrator agent):
  1. Uses MCP transport to delegate:
     - "find-issues" task → @investigate-champion
     - "fix-security" task → @secure-specialist
     - "refactor-code" task → @organize-guru
  
  2. Each sub-agent executes in Copilot environment
  
  3. Orchestrator aggregates results
  
All communication via MCP tools, no workflows needed
```

This is different from Tier 2, which creates actual GitHub workflow runs.

## Implementation Roadmap

### Phase 2A (Complete) ✅
- Tier 1 & Tier 2 fully implemented
- httpx-based transports for workflows
- Documentation of architecture

### Phase 2B (Current)
- End-to-end testing of Tier 1 & 2
- Performance benchmarks

### Phase 3 (Future)
- Implement Tier 3 MCP transport
- Enable Copilot agent-to-agent delegation
- No workflow overhead for simple tasks

### Phase 4+ (Future)
- Hybrid strategies (combine tiers)
- Smart transport selection
- Performance optimization

## Conclusion

**Short Answer:**
- **Tier 1 & 2:** Use httpx (GitHub Actions context) ✅ Already implemented
- **Tier 3:** Use MCP tools (Copilot context) 🔜 Designed, not yet implemented

**Key Insight:**
The transport layer choice depends on **where the code runs**, not just what it does:
- GitHub Actions workflows → Standard libraries (httpx)
- Copilot agents → MCP tools (function calling)

Both are correct for their respective contexts. The current implementation is production-ready for its intended use case (GitHub Actions workflows). MCP transport would add a new capability (Copilot-native delegation) when needed.

## References

- **Current Transports:** `tools/a2a/github_transport.py`, `tools/a2a/github_branch_transport.py`
- **MCP Design:** `tools/a2a/mcp_transport.py` (conceptual)
- **Architecture:** `docs/A2A_GITHUB_RUNNERS_ARCHITECTURE.md`
- **Transport Comparison:** `docs/A2A_TRANSPORT_COMPARISON.md`
