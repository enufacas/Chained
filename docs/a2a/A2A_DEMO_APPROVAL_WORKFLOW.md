# A2A Demo - Fully Autonomous Pipeline

## Overview

The A2A (Agent-to-Agent) Demo is a **fully autonomous pipeline** that:
1. **Dynamically selects agents** based on the `agent_count` parameter
2. Analyzes GitHub issues with multiple specialized agents (with visible reasoning)
3. Generates collaborative recommendations
4. **Automatically implements changes and creates a PR** - no human intervention required

This represents true autonomous AI development where the entire cycle from issue to PR happens without human intervention.

## Workflow Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    A2A Autonomous Pipeline Flow                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Trigger a2a-demo.yml                                                │
│     └─> Specify issue number and agent_count                            │
│     └─> auto_execute: true (default)                                    │
│     └─> show_reasoning: true (see Gemini's thinking)                    │
│                                                                         │
│  2. Dynamic Agent Selection                                             │
│     └─> Reads available agents from .github/agents/                     │
│     └─> Selects diverse agents from different categories                │
│     └─> Categories: Engineering, Security, Organization, Testing, etc.  │
│                                                                         │
│  3. Multi-Agent Analysis via Gemini AI (with visible reasoning)         │
│     ├─> 🤔 REASONING: Why each agent's perspective matters              │
│     ├─> 📋 ANALYSIS: Detailed findings from each agent                  │
│     └─> ✅ RECOMMENDATIONS: Specific actions to take                    │
│                                                                         │
│  4. AUTOMATIC Implementation (no human approval)                        │
│     └─> Gemini CLI implements the recommended changes                   │
│     └─> Creates feature branch (a2a/fix-issue-{number})                 │
│     └─> Commits changes                                                 │
│                                                                         │
│  5. AUTOMATIC PR Creation                                               │
│     └─> Creates PR linked to the issue                                  │
│     └─> Posts completion notification                                   │
│                                                                         │
│  ✅ DONE - Full cycle with zero human intervention                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Usage

### Run the Autonomous Pipeline

1. Go to **Actions** tab in your repository
2. Select **"A2A Demo - Live Multi-Agent Communication"**
3. Click **"Run workflow"**
4. Enter:
   - **Issue number**: The issue to analyze and implement
   - **Agent count**: Number of agents to involve (default: 3)
   - **Agents**: Optional - specific agents (leave empty for auto-selection)
   - **Auto execute**: `true` (default) for fully autonomous
   - **Show reasoning**: `true` (default) to see Gemini's thinking process
5. Click **"Run workflow"**

### What Happens Next

The workflow will:
1. **Select agents** automatically from different specialization categories
2. **Analyze** the issue with each agent showing their reasoning process
3. **Post** analysis summary to the issue with visible reasoning
4. **Implement** the recommended changes automatically
5. **Create** a PR with the changes
6. **Notify** on the issue that the PR is ready

## Input Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `issue_number` | GitHub issue number to analyze | - | Yes |
| `agent_count` | Number of agents to auto-select | `3` | No |
| `agents` | Specific agents (comma-separated) | `''` (auto) | No |
| `auto_execute` | Automatically implement and create PR | `true` | No |
| `show_reasoning` | Show Gemini's reasoning in output | `true` | No |

## Dynamic Agent Selection

When `agents` is left empty, the workflow automatically:

1. **Scans** all agents in `.github/agents/*.md`
2. **Categorizes** agents by specialization
3. **Selects** diverse agents from different categories

### Agent Categories

The selection algorithm prioritizes diversity across these categories:

| Category | Pattern Match | Example Agents |
|----------|---------------|----------------|
| Engineering | `engineer`, `build`, `create`, `develop` | `engineer-master`, `build-wizard` |
| Security | `secure`, `guard`, `monitor`, `validate` | `secure-specialist`, `guardian-master` |
| Code Organization | `organize`, `refactor`, `restructure` | `organize-guru`, `refactor-champion` |
| Testing | `test`, `assert`, `prove`, `verify` | `assert-specialist`, `validator-pro` |
| Documentation | `document`, `clarify`, `communicate` | `document-ninja`, `clarify-champion` |
| Performance | `optimize`, `accelerate`, `enhance` | `accelerate-master`, `optimize-director` |
| Innovation | `pioneer`, `innovate`, `breakthrough` | `pioneer-sage`, `breakthrough-ideas-champion` |
| Integration | `integrate`, `connect`, `bridge` | `bridge-master`, `connector-ninja` |

## Visible Reasoning

When `show_reasoning: true` (default), the Gemini output includes:

### For Each Agent
```markdown
## 🤖 @agent-name

### 🤔 Reasoning
[Why this agent's perspective matters for this issue]

### 📋 Analysis
[Detailed findings from the agent's specialized viewpoint]

### ✅ Recommendations
[Specific, actionable steps to take]
```

### Debug Artifacts

With `show_reasoning: true`, the workflow also:
- Enables Gemini debug mode
- Uploads artifacts with full conversation logs
- Saves telemetry to `.gemini/telemetry.log`

## Examples

### Example 1: Default Configuration (3 agents, auto-selected)

```yaml
issue_number: 3204
agent_count: 3
agents: ''           # Auto-select
auto_execute: true
show_reasoning: true
```

### Example 2: 5 Agents with Full Reasoning

```yaml
issue_number: 3210
agent_count: 5
agents: ''
auto_execute: true
show_reasoning: true
```

### Example 3: Specific Agents

```yaml
issue_number: 3215
agent_count: 3        # Ignored when agents specified
agents: 'secure-specialist,organize-guru,accelerate-master'
auto_execute: true
show_reasoning: true
```

### Example 4: Analysis Only (No Auto-Execute)

```yaml
issue_number: 3220
agent_count: 4
agents: ''
auto_execute: false   # Just analyze, don't create PR
show_reasoning: true
```

## Architecture

The A2A Demo uses:
- **Gemini AI** via `google-github-actions/run-gemini-cli` action
- **GitHub MCP Server** for creating branches, files, and PRs
- **Tier 1 execution**: Same-runner for fast, synchronous execution
- **Dynamic agent discovery** from `.github/agents/*.md` files

## Related Documentation

- [A2A Protocol Overview](./README.md)
- [A2A Status and Roadmap](./A2A_STATUS.md)
- [Three-Tier Architecture](./A2A_GITHUB_RUNNERS_ARCHITECTURE.md)
- [Gemini CLI Integration](../GEMINI_CLI_INTEGRATION.md)

---

**Last Updated**: 2025-11-27
**Status**: Fully Autonomous Pipeline with Dynamic Agent Selection
