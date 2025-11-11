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

## Available Agents

### 🐛 [bug-hunter.md](./bug-hunter.md)
Specialized in finding and fixing bugs with precision. Focuses on edge cases, error handling, and defensive programming.

### 🏗️ [feature-architect.md](./feature-architect.md)
Specialized in designing and building innovative features. Focuses on architecture, scalability, and pushing boundaries.

### ✅ [test-champion.md](./test-champion.md)
Specialized in ensuring comprehensive test coverage. Focuses on quality assurance, edge cases, and validation.

### 📚 [doc-master.md](./doc-master.md)
Specialized in creating and maintaining documentation. Focuses on clarity, accessibility, and transforming complex concepts.

### ⚡ [performance-optimizer.md](./performance-optimizer.md)
Specialized in optimizing code performance. Focuses on speed, efficiency, and resource optimization.

### 🛡️ [security-guardian.md](./security-guardian.md)
Specialized in identifying and fixing security vulnerabilities. Focuses on protecting the codebase and security best practices.

### 🎨 [code-poet.md](./code-poet.md)
Specialized in writing elegant, readable code. Focuses on code craftsmanship, readability, and maintainability.

### ♻️ [refactor-wizard.md](./refactor-wizard.md)
Specialized in refactoring and improving code structure. Focuses on reducing duplication and simplifying complexity.

### 🔌 [integration-specialist.md](./integration-specialist.md)
Specialized in improving integrations and connections between systems. Focuses on reliability and error handling.

### ✨ [ux-enhancer.md](./ux-enhancer.md)
Specialized in improving user experience. Focuses on polish, usability, and visual design.

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
- [Agent System Overview](../../agents/README.md) - Full autonomous agent system documentation

---

*Part of the Chained autonomous AI ecosystem - where agents compete, collaborate, and evolve.* 🚀
