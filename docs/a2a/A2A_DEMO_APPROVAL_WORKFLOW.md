# A2A Demo - Fully Autonomous Pipeline

## Overview

The A2A (Agent-to-Agent) Demo is a **fully autonomous pipeline** that:
1. Analyzes GitHub issues with multiple specialized agents
2. Generates collaborative recommendations
3. **Automatically implements changes and creates a PR** - no human approval required

This represents true autonomous AI development where the entire cycle from issue to PR happens without human intervention.

## Workflow Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    A2A Autonomous Pipeline Flow                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Trigger a2a-demo.yml                                                │
│     └─> Specify issue number and agents                                 │
│     └─> auto_execute: true (default)                                    │
│                                                                         │
│  2. Multi-Agent Analysis via Gemini AI                                  │
│     ├─> @engineer-master: Rigorous engineering analysis                 │
│     ├─> @secure-specialist: Security recommendations                    │
│     └─> @organize-guru: Code organization insights                      │
│                                                                         │
│  3. AUTOMATIC Implementation (no human approval)                        │
│     └─> Gemini CLI implements the recommended changes                   │
│     └─> Creates feature branch (a2a/fix-issue-{number})                 │
│     └─> Commits changes                                                 │
│                                                                         │
│  4. AUTOMATIC PR Creation                                               │
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
   - **Agents**: Comma-separated agent names (default: `engineer-master,secure-specialist,organize-guru`)
   - **Auto execute**: `true` (default) for fully autonomous, `false` for analysis-only
5. Click **"Run workflow"**

### What Happens Next

The workflow will:
1. **Analyze** the issue with multiple specialized agents
2. **Post** analysis summary to the issue
3. **Implement** the recommended changes automatically
4. **Create** a PR with the changes
5. **Notify** on the issue that the PR is ready

### Example

For issue #3204 "Add MIT license note to footer":

```yaml
# Workflow inputs
issue_number: 3204
agents: engineer-master,secure-specialist,organize-guru
auto_execute: true
```

Result:
- @engineer-master analyzes: HTML structure, semantic markup, documentation
- @secure-specialist analyzes: External link security (rel="noopener noreferrer")
- @organize-guru analyzes: DRY principle, footer consistency across pages
- **Automatic PR** created with all recommended changes

## Input Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `issue_number` | GitHub issue number to analyze | - | Yes |
| `agents` | Comma-separated list of agents | `engineer-master,secure-specialist,organize-guru` | No |
| `auto_execute` | Automatically implement and create PR | `true` | No |

## Agent Specializations

The default agents cover different perspectives:

| Agent | Specialization | Focus Areas |
|-------|----------------|-------------|
| `@engineer-master` | Rigorous engineering | Reliability, documentation, best practices |
| `@secure-specialist` | Security analysis | Vulnerabilities, attack vectors, secure defaults |
| `@organize-guru` | Code organization | DRY principle, maintainability, refactoring |

You can customize agents based on the issue type. See `.github/agents/` for the full list.

## Output

### Issue Comments

The workflow posts three comments to the issue:

1. **Start notification**: "A2A Demo Starting - LIVE"
2. **Analysis complete**: Summary of multi-agent analysis
3. **PR created**: "A2A Pipeline Complete - PR Created"

### Pull Request

The automatically created PR includes:
- Feature branch: `a2a/fix-issue-{issue_number}`
- Title: Based on issue title
- Body: Links to original issue
- Changes: Implementation of all agent recommendations

## Architecture

The A2A Demo uses:
- **Gemini AI** via `google-github-actions/run-gemini-cli` action
- **GitHub MCP Server** for creating branches, files, and PRs
- **Tier 1 execution**: Same-runner for fast, synchronous execution

## Related Documentation

- [A2A Protocol Overview](./README.md)
- [A2A Status and Roadmap](./A2A_STATUS.md)
- [Three-Tier Architecture](./A2A_GITHUB_RUNNERS_ARCHITECTURE.md)
- [Gemini CLI Integration](../GEMINI_CLI_INTEGRATION.md)

---

**Last Updated**: 2025-11-27
**Status**: Fully Autonomous Pipeline - Production Ready
