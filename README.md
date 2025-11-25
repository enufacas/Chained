# Chained: An AI Agent Orchestration Experiment

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://enufacas.github.io/Chained/)

> **An experimental testbed for building custom AI agent systems within GitHub conventions.**

## What is Chained?

Chained is a practical experiment in **AI agent orchestration**. The project explores:

1. **Custom Agent Definitions** - How to define specialized AI agents with distinct roles, personalities, and capabilities using GitHub conventions
2. **Agent Instruction Design** - Patterns for crafting effective agent instructions that work well with GitHub Copilot sessions
3. **Workflow Orchestration** - Techniques for building harnesses around agents using GitHub Actions and other workflow systems
4. **Multi-Agent Coordination** - Methods for assigning, routing, and coordinating work across multiple specialized agents

The repository serves as both a working implementation and a reference for how to structure agent-based automation in GitHub repositories.

**[📖 Documentation](./docs/INDEX.md)** | **[🤖 Agent Definitions](./.github/agents/)** | **[⚙️ Workflows](./.github/workflows/)**

---

## Core Concepts

### Custom Agents

Agents are defined in `.github/agents/` following the [GitHub Copilot custom agents convention](https://docs.github.com/en/copilot/reference/custom-agents-configuration). Each agent is a Markdown file with YAML frontmatter:

```yaml
---
name: engineer-master
description: "Specialized in engineering APIs"
tools:
  - github-mcp-server
  - playwright-browser
---

# Agent Instructions
Detailed instructions for the agent...
```

The repository includes **80+ custom agents** with specializations like:
- `engineer-master` - API engineering (inspired by Margaret Hamilton)
- `troubleshoot-expert` - Workflow debugging (inspired by Grace Hopper)
- `organize-guru` - Code organization (inspired by Robert Martin)
- `secure-specialist` - Security review (inspired by Bruce Schneier)
- `meta-coordinator` - Multi-agent task orchestration

See the [full agent catalog](./.github/agents/README.md) for all available agents.

### Agent Invocation

Agents can be invoked in several ways:

1. **GitHub Copilot Chat** - Reference agents directly in Copilot sessions
2. **Issue Assignment** - The system matches issues to agents based on content analysis
3. **Workflow Dispatch** - Workflows can invoke specific agents programmatically
4. **Copilot Coding Agent** - Agents execute via the GitHub Copilot coding agent runner

### Gemini CLI Integration

The project also experiments with **Google Gemini CLI** for agent-like workflows:

- `gemini-review.yml` - Automated PR code review using Gemini
- `gemini-triage.yml` - Issue labeling and triage using Gemini
- `gemini-fix.yml` - Automated issue fixing with Gemini
- `gemini-invoke.yml` - General Gemini CLI invocation

These workflows demonstrate an alternative approach to agent orchestration using the `google-github-actions/run-gemini-cli` action with custom prompts and MCP server integration.

**[📖 Gemini Context](./GEMINI.md)** - Project context for Gemini CLI

---

## Repository Structure

```
Chained/
├── .github/
│   ├── agents/           # 80+ custom agent definitions
│   ├── workflows/        # GitHub Actions orchestration (100+ workflows)
│   └── instructions/     # Path-specific agent instructions
├── docs/                 # Documentation and GitHub Pages
├── tools/                # Python utilities for agent matching, analysis
├── learnings/            # Data from learning system (see below)
└── world/                # Geographic visualization data
```

---

## Learning System (Experimental)

The repository includes an **experimental learning system** that generates work for agents:

- **External Sources** - Ingests content from TLDR, Hacker News, and GitHub Trending
- **Idea Generation** - Creates issues based on tech trends and patterns
- **Mission Assignment** - Routes generated work to specialized agents

This system provides a continuous stream of tasks but is still experimental. It is not yet reliable at producing novel or high-quality outputs. The primary purpose is to:
- Test agent assignment and matching algorithms
- Exercise the workflow orchestration system
- Generate realistic workloads for agent evaluation

**Note**: The learning outputs require human review before being considered actionable.

---

## Quick Start

### Prerequisites
- GitHub repository with Actions enabled
- Personal Access Token (PAT) with `repo` scope
- (Optional) Gemini API key for Gemini workflows

### Setup

1. **Fork or clone this repository**

2. **Configure secrets:**
   ```
   Repository Settings → Secrets and Variables → Actions
   - COPILOT_PAT: Your personal access token
   - GEMINI_API_KEY: (Optional) For Gemini workflows
   ```

3. **Enable GitHub Pages:**
   ```
   Repository Settings → Pages
   Source: Deploy from branch 'main', folder '/docs'
   ```

4. **Create an issue to test agent assignment:**
   - The system analyzes issue content and assigns an appropriate agent
   - No special labels required

**[📖 Complete Setup Guide](./docs/GETTING_STARTED.md)**

---

## Agent Orchestration Patterns

### Issue-to-Agent Matching

When an issue is created, `tools/match-issue-to-agent.py` analyzes the content and scores each agent based on:
- Keyword matches (specialization terms)
- Pattern matching (regex for domain-specific content)
- Agent availability and workload

The highest-scoring agent is assigned to the issue.

### Tech Lead Review

Tech lead agents (`workflows-tech-lead`, `agents-tech-lead`, `docs-tech-lead`, `github-pages-tech-lead`) provide specialized PR review based on file paths changed.

### Meta-Coordination

For complex tasks, the `meta-coordinator` agent can decompose work across multiple specialized agents.

---

## What This Project Demonstrates

1. **Convention-based agent definitions** - Using standard file formats and locations
2. **Instruction engineering** - Crafting prompts that work with GitHub Copilot
3. **Workflow harnesses** - Building automation around agent invocations
4. **Assignment algorithms** - Matching work to appropriate agents
5. **Multi-agent coordination** - Orchestrating work across specialists
6. **Alternative AI systems** - Integrating Gemini alongside Copilot

---

## Documentation

### Getting Started
- **[Documentation Index](./docs/INDEX.md)** - All docs organized by topic
- **[Architecture Overview](./docs/ARCHITECTURE_OVERVIEW.md)** - System design
- **[Quick Reference](./docs/QUICK_REFERENCE.md)** - Command cheat sheet
- **[FAQ](./docs/FAQ.md)** - Frequently asked questions

### Agent System
- **[Agent Definitions](./.github/agents/README.md)** - How agents are defined
- **[Agent Quickstart](./AGENT_QUICKSTART.md)** - Getting started with agents
- **[Copilot Instructions](./.copilot-instructions.md)** - Repository organization

### Autonomous System (Reference)
- **[Autonomous System Architecture](./docs/AUTONOMOUS_SYSTEM_ARCHITECTURE.md)** - Pipeline design
- **[Data Storage & Lifecycle](./docs/DATA_STORAGE_LIFECYCLE.md)** - Data architecture
- **[Workflows](./docs/WORKFLOWS.md)** - GitHub Actions explained

---

## Status & Monitoring

The repository includes a GitHub Pages dashboard showing:
- Agent activity and assignments
- Workflow execution status
- Learning system outputs (for review)

**[View Dashboard](https://enufacas.github.io/Chained/)**

---

## Contributing

Contributions are welcome. This is an experimental project, so:

- **Agent definitions** - Add or improve agents in `.github/agents/`
- **Workflow improvements** - Enhance orchestration patterns
- **Documentation** - Help clarify how the system works
- **Bug fixes** - Report and fix issues

All external PRs require manual review. See [Security Implementation](./docs/SECURITY_IMPLEMENTATION.md) for details.

---

## Limitations & Known Issues

- **Learning system quality**: Generated work items often lack relevance or novelty. All outputs require human review before acting on them.
- **Agent matching accuracy**: The keyword-based matching sometimes assigns inappropriate agents. Manual reassignment is possible by editing issue labels.
- **Multi-agent coordination**: The meta-coordinator is rudimentary. Complex multi-agent tasks often require manual intervention.
- **Gemini integration**: Requires a separate API key configuration (`GEMINI_API_KEY` secret).

This is an experiment in agent orchestration patterns, not a production-ready system.

---

## License

Open source. See [LICENSE](./LICENSE).

---

## Acknowledgments

- **GitHub Actions** - Workflow orchestration backbone
- **GitHub Copilot** - Custom agent runtime
- **Gemini CLI** - Alternative agent invocation
- **Model Context Protocol (MCP)** - Tool integration

---

*This repository is an experiment in AI agent orchestration. The patterns and conventions documented here are works in progress.*
