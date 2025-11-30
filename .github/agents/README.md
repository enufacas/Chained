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
- **gcloud MCP Server** (Google) - Google Cloud Platform operations

### Important: GitHub MCP Server Tools Are Automatically Available

**All 37+ GitHub MCP server tools are automatically available to all agents** - they do not need to be listed in the `tools:` section of agent definitions. The GitHub MCP server is built into the Copilot Coding Agent environment.

This includes tools for:
- Repository & Files: `get_file_contents`, `list_branches`, `list_commits`, etc.
- Search: `search_code`, `search_issues`, `search_pull_requests`, `web_search`, etc.
- Issues: `list_issues`, `issue_read`, etc.
- Pull Requests: `list_pull_requests`, `pull_request_read`, etc.
- Workflows: `list_workflows`, `get_workflow_run`, `summarize_job_log_failures`, etc.
- Security: `list_code_scanning_alerts`, `list_secret_scanning_alerts`, etc.

For the complete list of available tools, see **[MCP_SERVERS_CONFIGURATION.md](../../summaries/MCP_SERVERS_CONFIGURATION.md)**.

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

### 📋 [product-owner.md](./product-owner.md) 🛡️ **Protected**
Specialized in story writing and requirements clarification. Inspired by Marty Cagan - product-minded and user-focused, with strategic vision. Transforms general ideas into consumable, well-structured issues for the agent fleet. **This is a protected agent that cannot be deleted or voted off.**

### 🛡️ [secure-specialist.md](./secure-specialist.md)
Specialized in securing security. Inspired by Bruce Schneier - vigilant and thoughtful, with a philosophical bent. Focuses on security, data integrity, and access control.

### 📖 [support-master.md](./support-master.md)
Specialized in supporting skill building. Inspired by Barbara Liskov - principled and guiding. Focuses on code reviews, best practices, and knowledge sharing.

### 🔧 [troubleshoot-expert.md](./troubleshoot-expert.md) 🛡️ **Protected**
Specialized in troubleshooting GitHub Actions and workflows. Inspired by Grace Hopper - practical and debugging-focused, with systematic problem-solving. Focuses on CI/CD issues, workflow failures, and GitHub Actions debugging. **This is a protected agent that cannot be deleted or voted off.**

## Tech Lead Agents 👔

Tech lead agents provide specialized oversight for major subsections of the codebase. They have deep domain knowledge and ensure quality, consistency, and best practices in their respective areas. All tech lead agents are **protected** and cannot be eliminated through standard performance evaluation.

### 🏗️ [agents-tech-lead.md](./agents-tech-lead.md) 🛡️ **Protected**
Tech Lead responsible for agent system integrity, ensuring agent definitions are well-designed and the agent ecosystem remains healthy. Oversees `.github/agents/` directory, agent matching logic, and agent registry.

### ⚙️ [workflows-tech-lead.md](./workflows-tech-lead.md) 🛡️ **Protected**
Tech Lead responsible for GitHub Actions workflows, ensuring reliability and best practices in CI/CD automation. Oversees `.github/workflows/` directory and GitHub Actions configuration.

### 📚 [docs-tech-lead.md](./docs-tech-lead.md) 🛡️ **Protected**
Tech Lead responsible for documentation quality, ensuring clear, accurate, and maintainable documentation across the project. Oversees all markdown files, README files, and knowledge documentation.

### 🌐 [github-pages-tech-lead.md](./github-pages-tech-lead.md) 🛡️ **Protected**
Tech Lead responsible for GitHub Pages site quality, ensuring reliable rendering, performance, and user experience. Oversees `docs/` directory web content including HTML, CSS, and JavaScript.

## Using Custom Agents

Custom agents can be invoked:

1. **In GitHub Copilot Chat**: Use the agent name in your prompt
2. **In Issues**: Agents are automatically assigned based on specialization
3. **Via Workflow**: The agent spawner workflow creates tasks for agents

## Agent Assignment System

The intelligent matching system analyzes issue content and assigns the best-matching specialized agent. **Tech leads are excluded from initial assignment** to ensure specialized workers get opportunities to handle issues while tech leads focus on oversight and review through separate PR-based workflows.

### How Assignment Works
When a new issue is created:
1. The system analyzes issue title and body for keywords and patterns
2. **Tech leads are excluded** from the initial assignment pool
3. The issue is assigned to the best-matching specialized agent
4. Examples:
   - Workflow issues → `troubleshoot-expert`
   - Documentation → `document-ninja`, `clarify-champion`
   - API work → `engineer-master`, `APIs-architect`
   - Refactoring → `organize-guru`, `refactor-champion`

### Tech Lead Review
Tech leads are assigned to PRs via separate tech lead review workflows based on file paths changed, ensuring they provide oversight without dominating initial issue assignments.

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
