# Chained Project Context for Gemini CLI

This file provides project-specific context to help Gemini CLI understand the Chained autonomous AI ecosystem when performing code reviews, issue triage, and general assistance.

## 🎯 Project Overview

**Chained** is a fully autonomous software development ecosystem featuring:

- **48+ specialized AI agents** with unique personalities competing for survival
- **Autonomous closed-loop pipeline**: learning → planning → building → reviewing → self-reinforcing
- **External learning** from TLDR, Hacker News, and GitHub Trending
- **Self-learning** from its own discussions and outcomes
- **Self-documenting** on GitHub Pages

**Key Principle**: The system learns from the world, learns from itself, evolves continuously, and documents everything transparently.

## 📂 Repository Structure

```
Chained/
├── .github/
│   ├── workflows/     # GitHub Actions (including Gemini CLI workflows)
│   ├── agents/        # 48+ agent definitions with personalities
│   └── instructions/  # Path-specific instructions
├── docs/              # All documentation
├── tools/             # Python utilities and scripts
├── learnings/         # AI learning
├── world/             # World model data (geographic visualization)
└── tests/             # Test files
```

## 🤖 Agent System

Agents are defined in `.github/agents/*.md` with YAML frontmatter. Each agent has:
- **Specialization**: Focused area of expertise
- **Personality**: Inspired by legendary computer scientists
- **Performance tracking**: Evaluated based on contributions

**Protected agents** (cannot be eliminated):
- `troubleshoot-expert` - Workflow debugging
- `meta-coordinator-system` - System orchestration

## 💻 Coding Standards

### Python
- Follow PEP 8 style guide
- Use type hints for function signatures
- Handle exceptions appropriately
- Use f-strings for formatting

### Workflows (YAML)
- Use clear job and step names
- Include proper error handling
- Add concurrency controls where needed
- Follow branch protection rules (always use PRs)

### Documentation
- Use proper heading hierarchy (h1 → h2 → h3)
- Include code examples with language tags
- Keep markdown files well-structured

## 🔍 Review Priorities

When reviewing code, prioritize in this order:

1. **Security** - Agent system integrity, secret protection
2. **Correctness** - Logic errors, edge cases
3. **Performance** - Workflow efficiency, resource usage
4. **Maintainability** - Clear code, proper documentation
5. **Testing** - Adequate test coverage

## 🏷️ Issue Labels

Common labels for triage:
- `agent:*` - Agent-related issues
- `workflow` - GitHub Actions workflows
- `documentation` - Docs and guides
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `automated` - Created by automation
- `meta-coordination` - System orchestration

## ⚠️ Important Conventions

1. **Branch Protection**: Never push directly to `main` - always use PRs
2. **Agent Mentions**: Always use `@agent-name` format when referencing agents
3. **Workflow Triggers**: Currently configured for manual-only mode
4. **Documentation**: Update relevant docs when making changes

## 🔐 Security Considerations

- **Fork PRs**: Exercise caution with PRs from forks
- **Secrets**: Never expose or log secrets
- **External input**: Treat all external input as untrusted
- **Tool restrictions**: Use minimal required permissions

## 📝 Commit Message Guidelines

Use conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

## 🔗 Related Resources

- [Agent System Quick Start](/docs/AGENT_QUICKSTART.md)
- [Autonomous System Architecture](/docs/AUTONOMOUS_SYSTEM_ARCHITECTURE.md)
- [Workflow Documentation](/docs/WORKFLOWS.md)
- [GitHub Pages Dashboard](https://enufacas.github.io/Chained/)

## Gemini CLI Integration
The Gemini CLI leverages the Vertex AI API for enhanced functionality.