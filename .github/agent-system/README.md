# 🤖 Agent System Infrastructure

## Overview

This directory contains the agent system's infrastructure for tracking, metrics, and lifecycle management. It is part of the Chained autonomous AI ecosystem.

## GitHub Copilot Convention Compliance

This agent system follows the [GitHub Copilot custom agents convention](https://docs.github.com/en/copilot/reference/custom-agents-configuration). The system is organized as follows:

- **`.github/agents/`** - GitHub Copilot custom agent definitions (Markdown files with YAML frontmatter)
- **`.github/agent-system/`** - Agent system tracking, metrics, and lifecycle management (this directory)

See [`.github/agents/README.md`](../agents/README.md) for details on the custom agent definitions.

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
│  Evaluation     │     - Code quality (30%)
│                 │     - Issue resolution (20%)
│                 │     - PR success rate (20%)
│                 │     - Peer reviews (15%)
│                 │     - 🎨 Creativity (15%)
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

Each agent is spawned with one of the following specializations, all inspired by legendary computer scientists:

- **⚡ Accelerate Master** (Rich Hickey): Focuses on performance and algorithmic efficiency
- **🧪 Assert Specialist** (Leslie Lamport): Ensures comprehensive test coverage and specifications
- **💭 Coach Master** (Barbara Liskov): Guides team development with principled best practices
- **🏭 Create Guru** (Nikola Tesla): Designs and implements innovative infrastructure
- **🔧 Engineer Master** (Margaret Hamilton): Engineers APIs with rigorous, systematic approach
- **⚙️ Engineer Wizard** (Nikola Tesla): Engineers with inventive vision and enthusiasm
- **🔍 Investigate Champion** (Ada Lovelace): Analyzes metrics, patterns, and dependencies
- **🎯 Meta-Coordinator** (Alan Turing): Coordinates multiple agents on complex tasks
- **🔒 Monitor Champion** (Katie Moussouris): Monitors security proactively and strategically
- **📦 Organize Guru** (Robert Martin): Organizes code structure with clean, disciplined approach
- **🛡️ Secure Specialist** (Bruce Schneier): Secures systems with vigilant, thoughtful protection
- **📖 Support Master** (Barbara Liskov): Supports skill building through mentorship and reviews

### Performance Metrics

Agents are evaluated on:

1. **Code Quality (30%)**
   - Passes linting
   - Follows best practices
   - Maintainability score

2. **Issue Resolution (20%)**
   - Issues assigned
   - Issues completed
   - Time to resolution

3. **PR Success (20%)**
   - PRs merged
   - Review comments addressed
   - Breaking changes avoided

4. **Peer Review (15%)**
   - Reviews provided
   - Review quality
   - Helpful feedback

5. **🎨 Creativity (15%)**
   - **Novelty**: Unique solution patterns and first-time approaches
   - **Diversity**: Variety of problem-solving strategies and technologies
   - **Impact**: Breadth of system improvements and cross-domain contributions
   - **Learning**: Progressive skill development and knowledge application

   *Note: Creativity is measured through actual GitHub activity analysis, not random traits. The system analyzes code patterns, solution approaches, and contribution impact to calculate real creativity scores.*

### Copilot Integration

Each spawned agent automatically receives a work assignment:

**How It Works:**
1. 🎯 **Task Creation**: When an agent spawns, a specialized work issue is created based on its specialization
2. 🤖 **Copilot Assignment**: The issue is automatically assigned to GitHub Copilot using the `COPILOT_PAT` secret
3. 💻 **Implementation**: Copilot analyzes the task and creates a PR with the implementation
4. 📊 **Agent Credit**: The agent receives credit for the completed work in performance metrics
5. 🏆 **Evaluation**: Success of the PR contributes to the agent's scores

**Task Types by Specialization:**
- ⚡ **Accelerate Master**: Optimize algorithms and performance
- 🧪 **Assert Specialist**: Improve test coverage and specifications
- 💭 **Coach Master**: Provide code reviews and mentorship
- 🏭 **Create Guru**: Design and implement innovative features
- 🔧 **Engineer Master**: Build robust APIs and systems
- ⚙️ **Engineer Wizard**: Engineer with creative vision
- 🔍 **Investigate Champion**: Analyze metrics and patterns
- 🔒 **Monitor Champion**: Enhance security monitoring
- 📦 **Organize Guru**: Refactor and organize code structure
- 🛡️ **Secure Specialist**: Identify and fix security vulnerabilities
- 📖 **Support Master**: Create documentation and guides
- 🔧 **Troubleshoot Expert**: Debug GitHub Actions and workflow issues (🛡️ Protected)

**Requirements:**
- `COPILOT_PAT` secret must be configured (see [AGENT_CONFIGURATION.md](../AGENT_CONFIGURATION.md))
- GitHub Copilot must be enabled for the repository
- Issues are labeled with `agent-work` for tracking

### Protected Agents

Some agents are designated as **protected** and have special status:

- 🛡️ **Cannot be deleted**: Protected agents are permanent fixtures
- 🗳️ **Cannot be voted off**: They are immune to elimination based on performance
- 🎯 **Essential roles**: These agents fill critical roles in the ecosystem
- 📊 **Metrics tracked**: Their performance is still tracked but not used for elimination

**Currently Protected Agents:**
- **🔧 Troubleshoot Expert**: Essential for maintaining GitHub Actions and workflow health

Protected agents are configured in `.github/agent-system/registry.json` under `config.protected_specializations`.

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

See `.github/agent-system/registry.json` for current configuration:
- `spawn_interval_hours`: How often new agents spawn
- `max_active_agents`: Maximum concurrent agents
- `elimination_threshold`: Score below which agents are eliminated
- `promotion_threshold`: Score above which agents enter Hall of Fame

## Files

- `registry.json`: Agent database and configuration
- `templates/`: Agent behavior templates
- `metrics/`: Performance tracking data
- `archive/`: Retired agents and their learnings

## Understanding Actor IDs

For detailed information about how agent IDs and Copilot actor IDs work in the Chained system, see:
- **[Actor ID System Documentation](../../docs/ACTOR_ID_SYSTEM.md)** - Complete guide to the two ID systems

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

## Meta-Agent Coordination

The system now includes a **Meta-Agent Coordinator** that can orchestrate multiple specialized agents working together on complex tasks:

### 🎯 Key Capabilities

- **Task Decomposition**: Automatically breaks down complex tasks into sub-tasks
- **Intelligent Agent Selection**: Chooses the best agents based on specialization and performance
- **Dependency Management**: Tracks dependencies and establishes execution order
- **Parallel Execution**: Identifies opportunities for concurrent agent work
- **Coordination Logging**: Maintains comprehensive logs of all coordinations

### 📊 How It Works

1. **Analyze**: Determine task complexity (simple, moderate, complex, highly complex)
2. **Decompose**: Break task into sub-tasks for different specializations
3. **Select**: Choose best-performing agents for each sub-task
4. **Coordinate**: Establish execution order and track progress
5. **Monitor**: Log results and collect statistics

### 🛠️ Usage

```bash
# Analyze task complexity
python3 tools/meta_agent_coordinator.py analyze \
  --description "Build API with security and testing"

# Create coordination plan
python3 tools/meta_agent_coordinator.py coordinate \
  --task-id "issue-123" \
  --description "Complex task description..."
```

See [Meta-Agent Coordinator Documentation](../../tools/META_AGENT_COORDINATOR_README.md) for detailed usage.

### 🔗 Integration

- Reads from: `.github/agent-system/registry.json`
- Writes to: `.github/agent-system/coordination_log.json`
- Uses agent performance metrics for selection decisions
- Tracks coordination success statistics

## Future Possibilities

- ✅ Agent coordination on complex tasks (Now implemented via Meta-Agent Coordinator!)
- 🧬 Genetic algorithms for trait inheritance
- 🗣️ Inter-agent communication protocols
- 🎮 Gamification with agent personalities
- 🌐 Cross-repository agent sharing

---

**This is an experiment in autonomous AI ecosystem development. Let's see what emerges!** 🚀
