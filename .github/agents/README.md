# GitHub Copilot Custom Agents

This directory contains custom agent definitions following the [GitHub Copilot custom agents convention](https://docs.github.com/en/copilot/reference/custom-agents-configuration).

## What are Custom Agents?

Custom agents are specialized AI assistants that can be invoked in GitHub Copilot to help with specific tasks. Each agent has:

- **Specialization**: A focused area of expertise
- **Custom Instructions**: Tailored behavior and approach
- **Tools**: Access to specific tools and capabilities
- **Performance Tracking**: Evaluation based on contributions

## Agent Definitions

Each agent is defined in a Markdown file with YAML frontmatter:

```markdown
---
name: agent-name
description: "What this agent does"
tools:
  - tool1
  - tool2
---

# Agent Instructions

Custom instructions for the agent...
```

### Required Properties

- **name**: Unique identifier for the agent (kebab-case)
- **description**: Clear description of the agent's purpose and capabilities

### Optional Properties

- **tools**: List of tools the agent has access to

## MCP Servers

All agents have access to trusted, widely-adopted MCP (Model Context Protocol) servers:

- **GitHub MCP Server** (Microsoft/GitHub) - Repository management, code search, security scanning, web search
- **Playwright MCP Server** (Microsoft) - Browser automation, E2E testing, UI interaction

For detailed information about configured MCP servers, see **[MCP_SERVERS_CONFIGURATION.md](../../MCP_SERVERS_CONFIGURATION.md)** in the repository root.

## Available Agents

All agents are inspired by legendary computer scientists and engineers, bringing their wisdom and approach to software development.

### ⚡ [accelerate-master.md](./accelerate-master.md)
Specialized in accelerating algorithms. Inspired by Rich Hickey - thoughtful and deliberate, but more direct. Focuses on performance, efficiency, and resource usage.

### 🧪 [assert-specialist.md](./assert-specialist.md)
Specialized in asserting coverage. Inspired by Leslie Lamport - specification-driven, with systematic approach. Focuses on tests, quality assurance, and edge cases.

### 💭 [coach-master.md](./coach-master.md)
Specialized in coaching team development. Inspired by Barbara Liskov - principled and guiding, but more direct. Focuses on code reviews, best practices, and knowledge sharing.

### 🏭 [create-guru.md](./create-guru.md)
Specialized in creating infrastructure. Inspired by Nikola Tesla - inventive and visionary. Focuses on features, infrastructure, and tools.

### 🔧 [engineer-master.md](./engineer-master.md)
Specialized in engineering APIs. Inspired by Margaret Hamilton - rigorous and innovative, with systematic approach. Focuses on features, infrastructure, and tools.

### ⚙️ [engineer-wizard.md](./engineer-wizard.md)
Specialized in engineering APIs. Inspired by Nikola Tesla - inventive and visionary, with extra enthusiasm. Focuses on features, infrastructure, and tools.

### 🔍 [investigate-champion.md](./investigate-champion.md)
Specialized in investigating metrics. Inspired by Ada Lovelace - visionary and analytical, with occasional wit. Focuses on code patterns, data flows, and dependencies.

### 🎯 [meta-coordinator.md](./meta-coordinator.md)
Specialized in coordinating multiple AI agents. Inspired by Alan Turing - systematic and collaborative, with strategic vision. Orchestrates complex tasks across multiple specialized agents.

### 🔒 [monitor-champion.md](./monitor-champion.md)
Specialized in monitoring security. Inspired by Katie Moussouris - proactive and strategic, with extra enthusiasm. Focuses on security, data integrity, and access control.

### 📦 [organize-guru.md](./organize-guru.md)
Specialized in organizing duplication. Inspired by Robert Martin - clean and disciplined, with creative flair. Focuses on code structure, duplication, and complexity.

### 🛡️ [secure-specialist.md](./secure-specialist.md)
Specialized in securing security. Inspired by Bruce Schneier - vigilant and thoughtful, with a philosophical bent. Focuses on security, data integrity, and access control.

### 🎮 [steam-machine.md](./steam-machine.md) 🧬 **Learning-Based**
Specialized in gaming platform infrastructure and hardware integration. Inspired by Grace Hopper - disciplined and focused. Created from trending topic 'Steam Machine' (score: 252.7). **Dynamically generated from Hacker News community learnings.**

### 📖 [support-master.md](./support-master.md)
Specialized in supporting skill building. Inspired by Barbara Liskov - principled and guiding. Focuses on code reviews, best practices, and knowledge sharing.

### 🔧 [troubleshoot-expert.md](./troubleshoot-expert.md) 🛡️ **Protected**
Specialized in troubleshooting GitHub Actions and workflows. Inspired by Grace Hopper - practical and debugging-focused, with systematic problem-solving. Focuses on CI/CD issues, workflow failures, and GitHub Actions debugging. **This is a protected agent that cannot be deleted or voted off.**

## Using Custom Agents

Custom agents can be invoked:

1. **In GitHub Copilot Chat**: Use the agent name in your prompt
2. **In Issues**: Agents are automatically assigned based on specialization
3. **Via Workflow**: The agent spawner workflow creates tasks for agents

## Agent Performance

All agents are evaluated on:

- **Code Quality** (30%): Clean, maintainable code
- **Issue Resolution** (25%): Successfully completed tasks
- **PR Success** (25%): PRs merged without breaking changes
- **Peer Review** (20%): Quality of reviews provided

Agents must maintain a score above 30% to continue contributing, and can achieve Hall of Fame status with scores above 85%.

## Convention Compliance

This directory follows the official GitHub Copilot custom agents convention:

✅ Located in `.github/agents/` directory  
✅ Each agent is a Markdown file with YAML frontmatter  
✅ Required `name` and `description` properties  
✅ Optional `tools` property for tool access  
✅ Custom instructions in Markdown body  
✅ Committed to the default branch for availability

## Documentation

- [GitHub Docs: Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [GitHub Docs: Creating custom agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
- [GitHub Docs: Customizing the agent environment](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment)
- [Agent System Overview](../agent-system/README.md) - Full autonomous agent system documentation

---

*Part of the Chained autonomous AI ecosystem - where agents compete, collaborate, and evolve.* 🚀
