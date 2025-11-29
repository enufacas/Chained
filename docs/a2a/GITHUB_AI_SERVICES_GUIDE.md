# GitHub AI Services Guide

> A comprehensive guide to understanding GitHub's AI services, their rate limits, usage patterns, and when to use each service.

## Overview

GitHub offers multiple AI services that serve different purposes. Understanding the differences is crucial for:
- Choosing the right service for your use case
- Managing rate limits effectively
- Building automation workflows
- Planning A2A (Agent-to-Agent) orchestration

## Service Comparison

| Service | Interface | Authentication | Headless Support | Use Case |
|---------|-----------|----------------|------------------|----------|
| **GitHub Models API** | REST API | PAT with `models:read` | ✅ Yes | Programmatic LLM access |
| **Copilot Chat** | IDE Extension | OAuth Device Flow | ❌ No | Interactive coding assistance |
| **Copilot Coding Agent** | GitHub Issues | OAuth Device Flow | ⚠️ Via GraphQL assignment | Autonomous issue resolution |
| **Copilot CLI** | Terminal | OAuth Device Flow | ❌ No | Command-line assistance |

---

## 1. GitHub Models API

### What It Is
A REST API that provides direct access to AI models (GPT-4, GPT-4o, GPT-4o-mini, Llama, DeepSeek, etc.) for programmatic use.

### Authentication
```bash
# ✅ Works (discovered through testing)
curl -X POST https://models.github.ai/inference/chat/completions \
  -H "Authorization: token $PAT" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d '{"model":"openai/gpt-4o-mini","messages":[{"role":"user","content":"Hello"}]}'

# ❌ Does NOT work (despite documentation)
curl -H "Authorization: Bearer $PAT" ...
```

**Required PAT Scope**: `models:read` (fine-grained PAT)

### Rate Limits

#### Free Tier
| Model | Requests/day | Tokens/request |
|-------|-------------|----------------|
| GPT-4o | 50 | ~8,000 in / 4,000 out |
| GPT-4o-mini | 150 | ~8,000 in / 4,000 out |

#### Copilot+ Subscription
| Model | Requests/period | Tokens/period |
|-------|-----------------|---------------|
| GPT-4o-mini | 20,000 | 2,000,000 |
| GPT-4o | 10,000 | 10,000,000 |
| GPT-4.1 | 1,000 | 1,000,000 |

### Usage Tracking
Each response includes:
```json
{
  "usage": {
    "prompt_tokens": 14,
    "completion_tokens": 50,
    "total_tokens": 64
  }
}
```

Rate limit headers:
- `X-Ratelimit-Limit-Requests`: Total requests allowed
- `X-Ratelimit-Remaining-Requests`: Requests remaining
- `X-Ratelimit-Limit-Tokens`: Total tokens allowed
- `X-Ratelimit-Remaining-Tokens`: Tokens remaining

### Best For
- ✅ Automated workflows (GitHub Actions)
- ✅ Headless/programmatic LLM access
- ✅ Multi-turn conversations
- ✅ Issue analysis automation
- ❌ NOT for code-aware Copilot features

---

## 2. Copilot Chat

### What It Is
Interactive AI coding assistance within IDEs (VS Code, JetBrains, etc.).

### Modes
| Mode | Description | Request Usage |
|------|-------------|---------------|
| **Ask Mode** | Answer questions about code | Low |
| **Edit Mode** | Make targeted code changes | Medium |
| **Agent Mode** | Multi-step autonomous tasks | High |

### Authentication
- OAuth Device Flow only
- Cannot be automated headlessly
- Requires interactive login

### Rate Limits
- Uses "premium requests" for advanced models
- Agent mode consumes requests quickly (multi-step actions)
- Auto-model selection can mitigate rate limits

### Best For
- ✅ Interactive coding in IDE
- ✅ Code explanations and refactoring
- ✅ Test generation
- ❌ NOT for automation/headless use

---

## 3. Copilot Coding Agent

### What It Is
Autonomous cloud-based agent that picks up GitHub Issues, writes code, runs tests, and creates PRs.

### How It Works
1. Assign issue to `@copilot` (via GraphQL mutation)
2. Agent runs in GitHub Actions environment
3. Creates branch, makes changes, runs tests
4. Submits PR for review

### Authentication
- OAuth Device Flow for direct CLI access
- GraphQL assignment for headless orchestration

### Rate Limits
**Dual consumption:**
1. **Premium Requests** - LLM API calls
2. **Actions Minutes** - Compute time

| Resource | Consumption |
|----------|-------------|
| Premium Requests | Multiple per task (complex issues use more) |
| Actions Minutes | ~10-30 min per issue |

### GraphQL Assignment (Headless)
```graphql
mutation AssignCopilotToIssue($issueId: ID!) {
  updateIssue(input: {
    id: $issueId,
    assigneeIds: ["COPILOT_USER_ID"]
  }) {
    issue { id }
  }
}
```

### Best For
- ✅ Autonomous issue resolution
- ✅ A2A orchestration (via GraphQL)
- ✅ Complex multi-file changes
- ⚠️ Limited by Actions minutes

---

## 4. Copilot CLI

### What It Is
Command-line interface for Copilot assistance in terminal.

### Status
- `gh-copilot` extension: **Deprecated** (v1.2.0)
- `@githubnext/github-copilot-cli`: Requires device flow

### Authentication
- OAuth Device Flow only
- **Cannot be used headlessly**

### Best For
- ✅ Terminal command suggestions
- ❌ NOT for automation

---

## Rate Limit Comparison

### Request Types

| Type | Description | Services |
|------|-------------|----------|
| **API Requests** | Direct REST/GraphQL calls | Models API, GitHub API |
| **Premium Requests** | LLM model invocations | Copilot Chat, Coding Agent |
| **Actions Minutes** | Compute time | Coding Agent |

### Consumption Patterns

| Activity | Models API | Copilot Chat | Coding Agent |
|----------|------------|--------------|--------------|
| Simple query | 1 request | 1 premium | N/A |
| Multi-turn chat | N requests | N premium | N/A |
| Code edit | 1 request | 1-3 premium | N/A |
| Agent task | N/A | 5-20 premium | 10-50 premium + Actions |
| Issue resolution | N/A | N/A | 20-100+ premium + Actions |

### Reset Periods
- **Models API**: Hourly/daily (varies by tier)
- **Copilot Premium**: Hourly/daily
- **Actions Minutes**: Monthly (per plan)

---

## Choosing the Right Service

### For Headless Automation
```
┌─────────────────────────────────────────────────────┐
│ Need headless LLM access?                           │
│                                                     │
│   YES → GitHub Models API                           │
│         • Use PAT with models:read                  │
│         • Authorization: token $PAT                 │
│         • Multi-turn supported                      │
│                                                     │
│ Need autonomous code changes?                       │
│                                                     │
│   YES → Copilot Coding Agent (via GraphQL)          │
│         • Assign @copilot to issues                 │
│         • Monitor via GitHub API                    │
│         • Consumes Actions minutes                  │
└─────────────────────────────────────────────────────┘
```

### For Interactive Development
```
┌─────────────────────────────────────────────────────┐
│ Working in IDE?                                     │
│                                                     │
│   YES → Copilot Chat                                │
│         • Ask/Edit/Agent modes                      │
│         • Context-aware suggestions                 │
│         • Premium request consumption               │
│                                                     │
│ Working in terminal?                                │
│                                                     │
│   YES → Copilot CLI (limited)                       │
│         • Requires device flow auth                 │
│         • Not recommended for automation            │
└─────────────────────────────────────────────────────┘
```

---

## A2A Orchestration Recommendations

For building Agent-to-Agent systems:

### Viable Approaches

1. **GitHub Models API** for LLM reasoning
   - Analyze issues, generate suggestions
   - Multi-turn conversations
   - Full headless support

2. **GraphQL Assignment** for Copilot Coding Agent
   - Assign issues to `@copilot`
   - Monitor PR creation
   - Review and merge automation

3. **GitHub Actions** for orchestration
   - Trigger on issue events
   - Call Models API for analysis
   - Assign to coding agent for implementation

### NOT Viable

1. **Copilot CLI** - Requires device flow
2. **Copilot Chat API** - No headless access
3. **api.githubcopilot.com** - Rejects PATs

---

## Documentation References

- [GitHub Models Quickstart](https://docs.github.com/en/github-models/quickstart)
- [GitHub Models API Reference](https://docs.github.com/en/rest/models/inference)
- [Copilot Rate Limits](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/rate-limits)
- [AI Model Comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison)
- [Coding Agent vs Agent Mode](https://github.blog/developer-skills/github/less-todo-more-done-the-difference-between-coding-agent-and-agent-mode-in-github-copilot/)

---

## Tested Findings (Nov 2024)

### Key Discoveries

1. **Authorization Format**
   - Documentation says `Bearer`, but `token` format actually works
   - Always use: `Authorization: token $PAT`

2. **Rate Limits Vary by Subscription**
   - Free tier: 50-150 requests/day
   - Copilot+: 1,000-20,000 requests/period

3. **Copilot APIs Reject PATs**
   - `api.githubcopilot.com` returns "PATs not supported"
   - `copilot-proxy.githubusercontent.com` returns "invalid token format"

4. **Language Server SDK**
   - `@github/copilot-language-server` requires device flow
   - No method to inject PAT programmatically

---

*Last updated: November 2024*
*Based on live testing in GitHub Actions environment*
