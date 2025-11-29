# GitHub AI Services Guide

> A comprehensive guide to understanding GitHub's AI services, their rate limits, usage patterns, and when to use each service.

## Overview

GitHub offers multiple AI services that serve different purposes. Understanding the differences is crucial for:
- Choosing the right service for your use case
- Managing rate limits effectively
- Building automation workflows
- Planning A2A (Agent-to-Agent) orchestration

---

## Visual Overview: GitHub AI Services Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        GITHUB AI SERVICES ECOSYSTEM                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                     REQUEST TYPES & BILLING                              │    │
│  ├──────────────────┬───────────────────┬───────────────────────────────────┤    │
│  │  BASE REQUESTS   │ PREMIUM REQUESTS  │    GITHUB MODELS API              │    │
│  │  (Unlimited*)    │ (Capped Monthly)  │    (Separate Billing)             │    │
│  ├──────────────────┼───────────────────┼───────────────────────────────────┤    │
│  │ • Code completions│ • Chat (advanced) │ • REST API calls                  │    │
│  │ • Inline suggest │ • Agent Mode      │ • Per-model limits                │    │
│  │ • GPT-4o/4.1     │ • Coding Agent    │ • Pay-as-you-go option            │    │
│  │   default models │ • Code Review     │ • Fine-grained PAT                │    │
│  │                  │ • Copilot CLI     │                                   │    │
│  │                  │ • Premium models  │                                   │    │
│  └──────────────────┴───────────────────┴───────────────────────────────────┘    │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                     SERVICES & INTERFACES                                │    │
│  ├─────────────────┬─────────────────┬─────────────────┬────────────────────┤    │
│  │ COPILOT CHAT    │ CODING AGENT    │ COPILOT CLI     │ MODELS API         │    │
│  │ (IDE)           │ (Issues)        │ (Terminal)      │ (REST)             │    │
│  ├─────────────────┼─────────────────┼─────────────────┼────────────────────┤    │
│  │ OAuth only      │ OAuth/GraphQL   │ OAuth only      │ PAT (models:read)  │    │
│  │ ❌ No headless  │ ⚠️ Via GraphQL  │ ❌ No headless  │ ✅ Full headless   │    │
│  │ Premium req.    │ Premium + Mins  │ Premium req.    │ API rate limits    │    │
│  └─────────────────┴─────────────────┴─────────────────┴────────────────────┘    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

  *Unlimited for paid plans with default GPT-4o/GPT-4.1 models
```

---

## Service Comparison

| Service | Interface | Authentication | Headless Support | Use Case |
|---------|-----------|----------------|------------------|----------|
| **GitHub Models API** | REST API | PAT with `models:read` | ✅ Yes | Programmatic LLM access |
| **Copilot Chat** | IDE Extension | OAuth Device Flow | ❌ No | Interactive coding assistance |
| **Copilot Coding Agent** | GitHub Issues | OAuth Device Flow | ⚠️ Via GraphQL assignment | Autonomous issue resolution |
| **Copilot CLI** | Terminal | OAuth Device Flow | ❌ No | Command-line assistance |

---

## GitHub Copilot Plans & Premium Requests

### Plan Comparison

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                         GITHUB COPILOT PLANS                                    │
├────────────┬────────────┬─────────────┬────────────────┬───────────────────────┤
│   PLAN     │   PRICE    │  PREMIUM    │  BASE REQ.     │  KEY FEATURES         │
│            │            │  REQ/MONTH  │                │                       │
├────────────┼────────────┼─────────────┼────────────────┼───────────────────────┤
│   Free     │    $0      │     50      │  2,000 inline  │ Limited completions   │
│            │            │             │  suggestions   │ Basic chat            │
├────────────┼────────────┼─────────────┼────────────────┼───────────────────────┤
│   Pro      │  $10/mo    │    300      │  Unlimited     │ All features          │
│            │            │             │                │ Premium models        │
├────────────┼────────────┼─────────────┼────────────────┼───────────────────────┤
│   Pro+     │  $39/mo    │   1,500     │  Unlimited     │ Higher premium quota  │
│            │            │             │                │ Advanced models       │
├────────────┼────────────┼─────────────┼────────────────┼───────────────────────┤
│  Business  │ $19/user   │  300/user   │  Unlimited     │ Team management       │
│            │            │             │                │ Policy controls       │
├────────────┼────────────┼─────────────┼────────────────┼───────────────────────┤
│ Enterprise │ $39/user   │ 1,000/user  │  Unlimited     │ SSO, private AI       │
│            │            │             │                │ Codebase indexing     │
└────────────┴────────────┴─────────────┴────────────────┴───────────────────────┘
```

### What Counts as Premium Requests?

| Feature | Premium Request Cost | Notes |
|---------|---------------------|-------|
| Chat (default model) | 0 | GPT-4o/GPT-4.1 are free |
| Chat (advanced model) | 1+ | Depends on model multiplier |
| Agent Mode (IDE) | 5-20 | Multi-step operations |
| Coding Agent (Issue) | **1 per session** | As of July 2025 |
| Code Review | 1+ | Per review action |
| Copilot CLI | 1 | Per command |

### Model Multipliers (Premium Request Cost)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AI MODEL PREMIUM REQUEST MULTIPLIERS                  │
├─────────────────────────────┬─────────────┬─────────────────────────────┤
│         MODEL               │ MULTIPLIER  │  COST PER PROMPT            │
├─────────────────────────────┼─────────────┼─────────────────────────────┤
│ GPT-4o / GPT-4.1 (default)  │     0×      │  FREE (unlimited*)          │
│ Google Gemini 2.0 Flash     │   0.25×     │  0.25 premium requests      │
│ GPT-4o-mini                 │     1×      │  1 premium request          │
│ Claude Sonnet 3.5           │     1×      │  1 premium request          │
│ Claude Opus 4               │    10×      │  10 premium requests        │
│ GPT-4.5                     │    50×      │  50 premium requests        │
└─────────────────────────────┴─────────────┴─────────────────────────────┘
                              *Unlimited for paid plans
```

### Premium Request Reset

- **Reset Date**: 1st of each month at 00:00 UTC
- **Overage**: Can purchase more at ~$0.04/request (if enabled)
- **Organization Control**: Admins can set spending caps

---

## 1. GitHub Models API

### What It Is
A REST API that provides direct access to AI models (GPT-4, GPT-4o, GPT-4o-mini, Llama, DeepSeek, etc.) for programmatic use. **This is separate from Copilot premium requests.**

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

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GITHUB MODELS API RATE LIMITS                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  FREE TIER (per model, per day)                                         │
│  ┌────────────────────┬──────────────┬────────────────────────┐         │
│  │ Model              │ Requests/day │ Tokens/request         │         │
│  ├────────────────────┼──────────────┼────────────────────────┤         │
│  │ GPT-4o             │     50       │ ~8,000 in / 4,000 out  │         │
│  │ GPT-4o-mini        │    150       │ ~8,000 in / 4,000 out  │         │
│  │ Other models       │   varies     │ Model-specific         │         │
│  └────────────────────┴──────────────┴────────────────────────┘         │
│                                                                          │
│  PAID TIER (pay-as-you-go billing enabled)                              │
│  ┌────────────────────┬──────────────┬────────────────────────┐         │
│  │ Model              │ Requests     │ Billing                │         │
│  ├────────────────────┼──────────────┼────────────────────────┤         │
│  │ All models         │ Unlimited*   │ Per token (~$0.00001)  │         │
│  │                    │              │ varies by model        │         │
│  └────────────────────┴──────────────┴────────────────────────┘         │
│                                                                          │
│  *Practical limits still apply (requests/minute, concurrent)            │
│                                                                          │
│  COPILOT+ SUBSCRIPTION (observed in testing)                            │
│  ┌────────────────────┬──────────────────┬──────────────────┐           │
│  │ Model              │ Requests/period  │ Tokens/period    │           │
│  ├────────────────────┼──────────────────┼──────────────────┤           │
│  │ GPT-4o-mini        │     20,000       │   2,000,000      │           │
│  │ GPT-4o             │     10,000       │  10,000,000      │           │
│  │ GPT-4.1            │      1,000       │   1,000,000      │           │
│  └────────────────────┴──────────────────┴──────────────────┘           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

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
| Mode | Description | Premium Request Usage |
|------|-------------|----------------------|
| **Ask Mode** | Answer questions about code | 0 (default model) to 1+ (premium models) |
| **Edit Mode** | Make targeted code changes | 0-3 depending on model |
| **Agent Mode** | Multi-step autonomous tasks | 5-20+ (multiple LLM calls) |

### Authentication
- OAuth Device Flow only
- Cannot be automated headlessly
- Requires interactive login

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

### Resource Consumption

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CODING AGENT RESOURCE USAGE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PREMIUM REQUESTS                                                        │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ As of July 2025: 1 premium request per session                 │     │
│  │                                                                 │     │
│  │ A "session" = one issue assignment to @copilot                  │     │
│  │ Complex tasks no longer cost more premium requests!            │     │
│  │                                                                 │     │
│  │ Exception: Real-time steering comments during active session   │     │
│  │            may consume additional premium requests             │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                          │
│  GITHUB ACTIONS MINUTES                                                  │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ Typical session: 10-30 minutes of compute                      │     │
│  │ Complex tasks: May use more Actions minutes                    │     │
│  │ Counted against your plan's monthly Actions allocation         │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

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
- Consumes premium requests

### Best For
- ✅ Terminal command suggestions
- ❌ NOT for automation

---

## Rate Limit Comparison Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     REQUEST TYPES & HOW THEY'RE COUNTED                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐         │
│   │  GitHub Models  │      │    Copilot      │      │ Actions Minutes │         │
│   │   API Requests  │      │Premium Requests │      │                 │         │
│   ├─────────────────┤      ├─────────────────┤      ├─────────────────┤         │
│   │ • REST API calls│      │ • Chat (premium)│      │ • Coding Agent  │         │
│   │ • Per-model cap │      │ • Agent Mode    │      │ • Compute time  │         │
│   │ • Daily/hourly  │      │ • Coding Agent  │      │ • Monthly pool  │         │
│   │ • Separate bill │      │ • CLI commands  │      │ • Per-plan      │         │
│   └────────┬────────┘      └────────┬────────┘      └────────┬────────┘         │
│            │                        │                        │                   │
│            ▼                        ▼                        ▼                   │
│   ┌─────────────────────────────────────────────────────────────────────┐       │
│   │                        ACTIVITY CONSUMPTION                          │       │
│   ├─────────────────┬─────────────┬─────────────┬──────────────────────┤        │
│   │ Activity        │ Models API  │ Premium Req │ Actions Mins         │        │
│   ├─────────────────┼─────────────┼─────────────┼──────────────────────┤        │
│   │ Simple LLM call │ 1 request   │ -           │ -                    │        │
│   │ Chat (default)  │ -           │ 0           │ -                    │        │
│   │ Chat (premium)  │ -           │ 1-50*       │ -                    │        │
│   │ Agent Mode      │ -           │ 5-20        │ -                    │        │
│   │ Coding Agent    │ -           │ 1/session   │ 10-30 min/session    │        │
│   │ Code Review     │ -           │ 1+          │ -                    │        │
│   └─────────────────┴─────────────┴─────────────┴──────────────────────┘        │
│   *Depends on model multiplier (see Model Multipliers section)                  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Reset Periods
- **Models API**: Hourly/daily (varies by tier)
- **Copilot Premium**: Monthly (1st of each month, 00:00 UTC)
- **Actions Minutes**: Monthly (per plan)

---

## Choosing the Right Service

### Decision Flowchart

```
                    ┌─────────────────────────────┐
                    │   What do you need?         │
                    └─────────────┬───────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ Headless LLM    │ │ Autonomous code │ │ Interactive     │
    │ access          │ │ changes         │ │ coding help     │
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ GitHub Models   │ │ Coding Agent    │ │ In IDE?         │
    │ API             │ │ via GraphQL     │ │                 │
    │                 │ │                 │ │ YES → Chat      │
    │ ✅ PAT auth     │ │ ✅ Headless     │ │ NO  → CLI       │
    │ ✅ Full control │ │ ⚠️ Actions mins │ │      (limited)  │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### For Headless Automation

| Need | Solution | Authentication |
|------|----------|----------------|
| LLM reasoning | GitHub Models API | PAT with `models:read` |
| Code changes | Coding Agent | GraphQL assignment |
| Issue analysis | Models API | PAT with `models:read` |
| PR automation | GitHub API + Models API | PAT |

### For Interactive Development

| Need | Solution | Notes |
|------|----------|-------|
| IDE assistance | Copilot Chat | Premium requests for advanced models |
| Terminal help | Copilot CLI | Requires device flow |
| Complex tasks | Agent Mode | Higher premium request cost |

---

## A2A Orchestration Recommendations

### Viable Approaches

1. **GitHub Models API** for LLM reasoning
   - Analyze issues, generate suggestions
   - Multi-turn conversations
   - Full headless support
   - Separate rate limits from Copilot

2. **GraphQL Assignment** for Copilot Coding Agent
   - Assign issues to `@copilot`
   - Only 1 premium request per session!
   - Monitor PR creation
   - Review and merge automation

3. **GitHub Actions** for orchestration
   - Trigger on issue events
   - Call Models API for analysis
   - Assign to coding agent for implementation

### Cost Optimization Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    A2A COST OPTIMIZATION                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Use Models API for analysis (separate rate limits)                  │
│     └─ GPT-4o-mini has highest free quota (150/day)                     │
│                                                                          │
│  2. Use Coding Agent for implementation (1 premium req/session)         │
│     └─ Complex tasks are now "cheap" in premium requests!               │
│                                                                          │
│  3. Use default models in Chat when possible (0 premium req)            │
│     └─ GPT-4o/GPT-4.1 are free on paid plans                            │
│                                                                          │
│  4. Avoid high-multiplier models for routine tasks                      │
│     └─ GPT-4.5 (50×) and Claude Opus (10×) drain quota fast             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### NOT Viable for Headless Use

1. **Copilot CLI** - Requires device flow
2. **Copilot Chat API** - No headless access
3. **api.githubcopilot.com** - Rejects PATs

---

## Documentation References

### Official GitHub Docs
- [Requests in GitHub Copilot](https://docs.github.com/en/copilot/concepts/billing/copilot-requests)
- [Plans for GitHub Copilot](https://docs.github.com/en/copilot/get-started/plans)
- [About GitHub Copilot Coding Agent](https://docs.github.com/en/copilot/using-github-copilot/using-copilot-coding-agent-to-work-on-tasks/about-assigning-tasks-to-copilot)
- [GitHub Copilot Features](https://docs.github.com/en/copilot/about-github-copilot/github-copilot-features)
- [GitHub Models Quickstart](https://docs.github.com/en/github-models/quickstart)
- [GitHub Models API Reference](https://docs.github.com/en/rest/models/inference)
- [GitHub Models Billing](https://docs.github.com/en/billing/concepts/product-billing/github-models)

### Changelogs
- [Coding Agent now uses 1 premium request per session](https://github.blog/changelog/2025-07-10-github-copilot-coding-agent-now-uses-one-premium-request-per-session/)
- [GitHub Models beyond free limits](https://github.blog/changelog/2025-06-24-github-models-now-supports-moving-beyond-free-limits/)

---

## Tested Findings (Nov 2024)

### Key Discoveries

1. **Authorization Format**
   - Documentation says `Bearer`, but `token` format actually works
   - Always use: `Authorization: token $PAT`

2. **Rate Limits Vary by Subscription**
   - Free tier: 50-150 requests/day per model
   - Copilot+: 1,000-20,000 requests/period (much higher!)

3. **Copilot APIs Reject PATs**
   - `api.githubcopilot.com` returns "PATs not supported"
   - `copilot-proxy.githubusercontent.com` returns "invalid token format"

4. **Language Server SDK**
   - `@github/copilot-language-server` requires device flow
   - No method to inject PAT programmatically

5. **Coding Agent Efficiency**
   - As of July 2025: 1 premium request per session (regardless of complexity)
   - Makes A2A orchestration much more cost-effective

---

*Last updated: November 2024*
*Based on live testing in GitHub Actions environment and official GitHub documentation*
*Note: Some features (e.g., Coding Agent 1-request-per-session) reference planned July 2025 changes per GitHub changelog*
