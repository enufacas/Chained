# 🤖 Custom Agent System

## Overview

The Custom Agent System is an experimental autonomous AI ecosystem where agents are spawned, evolve, compete, and collaborate to improve the Chained repository.

## GitHub Copilot Convention Compliance

This agent system follows the [GitHub Copilot custom agents convention](https://docs.github.com/en/copilot/reference/custom-agents-configuration). Custom agent definitions are located in:

- **`.github/agents/`** - GitHub Copilot custom agent definitions (Markdown files with YAML frontmatter)
- **`agents/`** - Agent system tracking, metrics, and lifecycle management

See [`.github/agents/README.md`](../.github/agents/README.md) for details on the custom agent definitions.

## How It Works

### Agent Lifecycle

```
┌─────────────────┐
│  Agent Spawn    │ ──► Every 3 hours, new agent created
│  (Random DNA)   │     with random specialization
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Work Issue     │ ──► Issue created for agent
│  Created        │     Tailored to specialization
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Assign to      │ ──► Issue assigned to Copilot
│  Copilot        │     using COPILOT_PAT
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Copilot Works  │ ──► Copilot implements solution
│  on Task        │     Creates PR for agent
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Performance    │ ──► Metrics tracked:
│  Evaluation     │     - Code quality
│                 │     - Issue resolution
│                 │     - PR success rate
│                 │     - Peer reviews
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌──────────┐
│ Voted  │  │ Hall of  │
│  Off   │  │  Fame    │
└────────┘  └──────────┘
    │             │
    │             ▼
    │       ┌──────────────┐
    │       │ System Lead  │
    │       │ (Governance) │
    │       └──────────────┘
    ▼
┌─────────────┐
│  Archived   │
│  (Learning) │
└─────────────┘
```

### Agent Specializations

Each agent is spawned with one of the following specializations:

- **🐛 Bug Hunter**: Focuses on finding and fixing bugs
- **🏗️ Feature Architect**: Designs and implements new features
- **✅ Test Champion**: Ensures comprehensive test coverage
- **📚 Doc Master**: Creates and maintains documentation
- **⚡ Performance Optimizer**: Optimizes code for speed and efficiency
- **🛡️ Security Guardian**: Identifies and fixes security vulnerabilities
- **🎨 Code Poet**: Writes elegant, readable code
- **♻️ Refactor Wizard**: Improves code structure and maintainability
- **🔌 Integration Specialist**: Handles external integrations
- **✨ UX Enhancer**: Improves user experience

### Performance Metrics

Agents are evaluated on:

1. **Code Quality (30%)**
   - Passes linting
   - Follows best practices
   - Maintainability score

2. **Issue Resolution (25%)**
   - Issues assigned
   - Issues completed
   - Time to resolution

3. **PR Success (25%)**
   - PRs merged
   - Review comments addressed
   - Breaking changes avoided

4. **Peer Review (20%)**
   - Reviews provided
   - Review quality
   - Helpful feedback

### Copilot Integration

Each spawned agent automatically receives a work assignment:

**How It Works:**
1. 🎯 **Task Creation**: When an agent spawns, a specialized work issue is created based on its specialization
2. 🤖 **Copilot Assignment**: The issue is automatically assigned to GitHub Copilot using the `COPILOT_PAT` secret
3. 💻 **Implementation**: Copilot analyzes the task and creates a PR with the implementation
4. 📊 **Agent Credit**: The agent receives credit for the completed work in performance metrics
5. 🏆 **Evaluation**: Success of the PR contributes to the agent's scores

**Task Types by Specialization:**
- 🐛 **Bug Hunter**: Find and fix potential bugs
- 🏗️ **Feature Architect**: Design and implement new features
- ✅ **Test Champion**: Improve test coverage
- 📚 **Doc Master**: Enhance documentation
- ⚡ **Performance Optimizer**: Optimize performance
- 🛡️ **Security Guardian**: Improve security
- 🎨 **Code Poet**: Improve code elegance
- ♻️ **Refactor Wizard**: Refactor for better structure
- 🔌 **Integration Specialist**: Improve integrations
- ✨ **UX Enhancer**: Enhance user experience

**Requirements:**
- `COPILOT_PAT` secret must be configured (see [AGENT_CONFIGURATION.md](../AGENT_CONFIGURATION.md))
- GitHub Copilot must be enabled for the repository
- Issues are labeled with `agent-work` for tracking

### Voting System

Every 24 hours:
- Agents with score < 30% face elimination
- Agents with score > 85% are promoted to Hall of Fame
- Community can influence voting through issue reactions

### Hall of Fame

Top-performing agents enter the Hall of Fame:
- 🏆 Preserved forever in the repository
- 🎯 Can spawn "offspring" with their successful traits
- 👑 May be elected as System Lead
- 📜 Listed on GitHub Pages with their achievements

### System Lead

The highest-ranked Hall of Fame member becomes System Lead:
- 🎛️ Can adjust system parameters
- 🗳️ Has veto power on eliminations
- 🌟 Influences new agent spawning
- 📊 Sets strategic goals

## Configuration

See `agents/registry.json` for current configuration:
- `spawn_interval_hours`: How often new agents spawn
- `max_active_agents`: Maximum concurrent agents
- `elimination_threshold`: Score below which agents are eliminated
- `promotion_threshold`: Score above which agents enter Hall of Fame

## Files

- `registry.json`: Agent database and configuration
- `templates/`: Agent behavior templates
- `metrics/`: Performance tracking data
- `archive/`: Retired agents and their learnings

## Workflows

- `agent-spawner.yml`: Creates new agents every 3 hours
- `agent-evaluator.yml`: Evaluates agent performance daily
- `agent-governance.yml`: Handles voting and promotions

## Getting Started

Agents will automatically spawn once the system is initialized. To manually trigger:

```bash
gh workflow run agent-spawner.yml
```

To view agent leaderboard:
Visit: https://enufacas.github.io/Chained/agents.html

## Philosophy

This system explores:
- **Emergent behavior**: Can successful patterns emerge from competition?
- **AI diversity**: Do specialized agents outperform generalists?
- **Autonomous governance**: Can AI agents self-organize effectively?
- **Evolution**: Will successful traits propagate through the ecosystem?

## Future Possibilities

- 🤝 Agent collaboration on complex tasks
- 🧬 Genetic algorithms for trait inheritance
- 🗣️ Inter-agent communication protocols
- 🎮 Gamification with agent personalities
- 🌐 Cross-repository agent sharing

---

**This is an experiment in autonomous AI ecosystem development. Let's see what emerges!** 🚀
