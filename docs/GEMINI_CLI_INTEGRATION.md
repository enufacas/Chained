# Gemini CLI Integration for Chained

This document describes the Gemini CLI integration in the Chained repository and how to use it.

## 🚀 Quick Start - How to Use

> **Current Mode: Manual Only** - Gemini CLI only responds to explicit `@gemini-cli` commands.

### Available Commands

Use these commands in any issue or pull request comment:

| Command | What It Does | Where to Use |
|---------|--------------|--------------|
| `@gemini-cli /review` | Request a code review with inline suggestions | PR comments |
| `@gemini-cli /triage` | Request automatic issue labeling | Issue comments |
| `@gemini-cli /fix` | Automatically fix an issue and create a PR | Issue comments |
| `@gemini-cli <your request>` | Free-form AI assistance (requires approval for changes) | Issues or PRs |

### Examples

**Request a PR Review:**
```
@gemini-cli /review
```

**Request a PR Review with specific focus:**
```
@gemini-cli /review Please focus on security and performance
```

**Request Issue Triage:**
```
@gemini-cli /triage
```

**Request Automatic Issue Fix:**
```
@gemini-cli /fix
```

**Request Automatic Issue Fix with context:**
```
@gemini-cli /fix Focus on improving performance
```

**Ask for Help (General Assistant):**
```
@gemini-cli Explain what this function does and suggest improvements
```

```
@gemini-cli Write unit tests for the changes in this PR
```

```
@gemini-cli Help me debug why this workflow is failing
```

### Who Can Use It?

Only users with these roles can trigger Gemini CLI:
- **OWNER** - Repository owner
- **MEMBER** - Organization member  
- **COLLABORATOR** - Repository collaborator

### What Happens When You Use It?

1. **Acknowledgment**: Gemini posts a comment confirming it received your request
2. **Processing**: Gemini analyzes the context and performs the requested action
3. **Response**: Gemini posts results (review comments, labels applied, or answers)

### Current Configuration

| Setting | Value |
|---------|-------|
| **Mode** | Manual only (no auto-triggers) |
| **Authentication** | API Key (`GEMINI_API_KEY` secret) |
| **Fork PRs** | Skipped for security |
| **Permissions** | OWNER, MEMBER, COLLABORATOR only |

---

## 📋 Table of Contents

1. [Quick Start - How to Use](#-quick-start---how-to-use)
2. [Overview](#overview)
3. [Prerequisites](#prerequisites)
4. [Available Workflow Types](#available-workflow-types)
5. [Customization Options](#customization-options)
6. [Integration with Chained's Agent System](#integration-with-chaineds-agent-system)
7. [Recommended Configuration](#recommended-configuration)
8. [Security Considerations](#security-considerations)
9. [Enabling Auto-Triggers](#enabling-auto-triggers)

---

## Overview

The `run-gemini-cli` action integrates Google's Gemini AI into GitHub workflows, enabling:
- **Autonomous PR reviews** - Automatic code review on pull requests
- **Issue triage** - Automatic labeling and categorization of issues
- **On-demand assistance** - Conversational AI via `@gemini-cli` mentions
- **Custom workflows** - Extensible for any Gemini-powered automation

### Key Features
- **Tool Calling**: Integrates with GitHub MCP server for repository operations
- **Customizable Prompts**: TOML-based prompt configuration
- **GEMINI.md Support**: Repository-specific context and instructions
- **Multiple Auth Options**: API key, Vertex AI, or Workload Identity Federation

---

## Prerequisites

### Required Setup

1. **Gemini API Key** (simplest option)
   - **IMPORTANT**: Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - **⚠️ DO NOT use API keys from Google Cloud Platform Console** - these are different and will not work
   - The workflows use the `generativelanguage.googleapis.com` API which requires Google AI Studio API keys
   - Store as `GEMINI_API_KEY` secret in repository settings

2. **Update `.gitignore`**
   ```gitignore
   # Gemini CLI settings
   .gemini/
   
   # GitHub App credentials
   gha-creds-*.json
   ```

3. **(Optional) GitHub App** for enhanced identity
   - Create a custom GitHub App for "gemini-cli" identity
   - Provides cleaner audit trail and customizable permissions

---

## Available Workflow Types

### 1. 🔀 Gemini Dispatch (Central Router)

**Purpose**: Routes `@gemini-cli` commands to appropriate workflows.

**Triggers**:
- `pull_request` opened (auto-review)
- `issues` opened/reopened (auto-triage)
- `issue_comment`/`pull_request_review_comment` containing `@gemini-cli`

**Commands Supported**:
| Command | Action |
|---------|--------|
| `@gemini-cli /review` | Trigger PR review |
| `@gemini-cli /triage` | Trigger issue triage |
| `@gemini-cli /fix` | Automatically fix issue and create PR |
| `@gemini-cli <request>` | Free-form AI assistance (requires approval for changes) |

**Customization Points**:
- Author association filter (OWNER, MEMBER, COLLABORATOR)
- Fork PR handling
- Acknowledgment message format

### 2. 🔎 Gemini PR Review

**Purpose**: Comprehensive code review with inline suggestions.

**Key Features**:
- Severity-based feedback (🔴 Critical → 🟢 Low)
- Line-accurate code suggestions
- Security and performance analysis
- GitHub MCP server for pending review creation

**Customization Options**:
- Review criteria prioritization
- Severity thresholds
- Custom review prompts via TOML
- Model selection (`gemini-2.0-flash-exp`, etc.)

### 3. 🏷️ Gemini Issue Triage

**Purpose**: Automatic label assignment based on issue content.

**Key Features**:
- Analyzes issue title and body
- Matches to repository labels
- Supports scheduled bulk triage

**Customization Options**:
- Label matching logic
- Triage criteria
- Scheduled vs. on-demand execution

### 4. ▶️ Gemini Invoke (General Assistant)

**Purpose**: Free-form AI assistance for any task.

**Key Features**:
- Full GitHub MCP server integration
- File creation/modification
- Branch and PR creation
- Plan-Approve-Execute workflow

**Customization Options**:
- Available tools/capabilities
- Approval workflow
- Resource limits

---

## Customization Options

### A. Authentication Options

| Option | Best For | Setup Complexity |
|--------|----------|------------------|
| **API Key** | Quick start, non-sensitive repos | Low |
| **Vertex AI** | Enterprise, billing control | Medium |
| **Workload Identity** | GCP-native, no secrets | High |

**Recommendation for Chained**: Start with API Key for simplicity.

### B. Model Selection and Rate Limits

> **⚠️ Free Tier Rate Limits**: Different Gemini models have different rate limits on the free tier. Choose your model carefully to avoid hitting rate limits.

#### Free Tier Rate Limits by Model

| Model | Requests per Minute (RPM) | Requests per Day (RPD) | Recommended |
|-------|--------------------------|------------------------|-------------|
| `gemini-2.0-flash` | 15 | 200 | ✅ **Default** - Best for high-volume use |
| `gemini-2.5-flash-lite` | 15 | 1,000 | ✅ High daily limit |
| `gemini-2.5-flash` | 10 | 250 | Good balance |
| `gemini-2.5-pro` | 2 | 50 | ❌ Lowest RPM - avoid for frequent triggers |

#### Configuration

The workflows default to `gemini-2.0-flash` for optimal free tier usage. To override:

**Option 1: Set Repository Variable (Recommended)**
1. Go to **Settings > Secrets and variables > Actions > Variables**
2. Create variable `GEMINI_MODEL` with your preferred model name

**Option 2: Edit Workflow Files**
```yaml
# In workflow files:
gemini_model: '${{ vars.GEMINI_MODEL || ''gemini-2.0-flash'' }}'
```

#### Available Models

```yaml
# High RPM (recommended for free tier)
gemini_model: 'gemini-2.0-flash'        # 15 RPM - Default
gemini_model: 'gemini-2.5-flash-lite'   # 15 RPM, 1000 RPD

# Balanced
gemini_model: 'gemini-2.5-flash'        # 10 RPM

# Low RPM (use sparingly)
gemini_model: 'gemini-2.5-pro'          # 2 RPM only!
```

**Reference**: [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)

### C. MCP Server Tools

Control which GitHub operations Gemini can perform:

```json
{
  "mcpServers": {
    "github": {
      "includeTools": [
        // Read-only (safer)
        "get_file_contents",
        "get_issue",
        "pull_request_read",
        
        // Write operations (more powerful)
        "add_issue_comment",
        "create_pull_request",
        "push_files"
      ]
    }
  }
}
```

### D. Custom Prompts via GEMINI.md

Create a `GEMINI.md` file in repository root for project-specific context:

```markdown
# Chained Project Context

## Project Overview
Chained is an autonomous AI ecosystem with 48+ specialized agents...

## Coding Standards
- Follow PEP 8 for Python
- Use type hints for all functions
- Tests required for new features

## Architecture
- Agents are defined in `.github/agents/`
- Workflows in `.github/workflows/`
- Tools in `tools/`

## Review Priorities
1. Security (agent system integrity)
2. Performance (workflow efficiency)
3. Maintainability (clear agent definitions)
```

### E. Settings JSON

Configure CLI behavior directly in workflows:

```json
{
  "model": {
    "maxSessionTurns": 25
  },
  "telemetry": {
    "enabled": true,
    "target": "local"
  },
  "tools": {
    "core": [
      "run_shell_command(cat)",
      "run_shell_command(grep)",
      "run_shell_command(python3)"
    ]
  }
}
```

---

## Integration with Chained's Agent System

### Option 1: Parallel Operation

Run Gemini CLI alongside existing Copilot agents:
- Gemini handles specific tasks (e.g., PR review)
- Copilot agents continue current workflows
- No integration required

**Pros**: Simple, no conflicts
**Cons**: Potential duplication of effort

### Option 2: Gemini as Additional Agent Type

Add a `gemini-agent.md` to the agent system:
- Treat Gemini CLI as another specialized agent
- Route specific issue types to Gemini
- Track performance alongside other agents

**Pros**: Unified agent ecosystem
**Cons**: Requires pattern matcher updates

### Option 3: Gemini for Code Analysis Only

Use Gemini exclusively for:
- PR code review (replace or supplement tech leads)
- Security scanning
- Code quality analysis

**Pros**: Clear separation of concerns
**Cons**: Limited scope

### Option 4: Full Replacement (Not Recommended)

Replace Copilot with Gemini CLI entirely:
- Would require significant workflow rewrites
- Loses Chained's custom agent personalities
- Not recommended for this ecosystem

---

## Recommended Configuration

### Minimal Setup (Quick Start)

```yaml
# .github/workflows/gemini-dispatch.yml
name: '🔀 Gemini Dispatch'

on:
  pull_request:
    types: ['opened']
  issue_comment:
    types: ['created']

jobs:
  dispatch:
    if: |
      github.event_name == 'pull_request' ||
      startsWith(github.event.comment.body, '@gemini-cli')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/run-gemini-cli@v0
        with:
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
          prompt: 'Review this PR and provide feedback.'
```

### Full Integration (Recommended)

Copy all four workflows from `google-github-actions/run-gemini-cli`:
1. `gemini-dispatch.yml` - Central router
2. `gemini-review.yml` - PR review
3. `gemini-triage.yml` - Issue triage
4. `gemini-invoke.yml` - General assistance (requires approval for changes)
5. `gemini-fix.yml` - Automatic issue fixer (creates PRs directly)

Add custom TOML prompts tailored to Chained's ecosystem.

---

## Security Considerations

### 1. Fork PR Handling

By default, workflows skip fork PRs to prevent secret exposure:

```yaml
if: github.event.pull_request.head.repo.fork == false
```

**Options**:
- Keep default (secure but limits external contributions)
- Use pull_request_target with careful input sanitization
- Require fork PR approval before running

### 2. Command Permissions

Restrict who can trigger `@gemini-cli`:

```yaml
contains(fromJSON('["OWNER", "MEMBER", "COLLABORATOR"]'), 
         github.event.comment.author_association)
```

### 3. Tool Restrictions

Limit destructive operations:

```json
{
  "mcpServers": {
    "github": {
      "includeTools": [
        // Exclude: delete_file, push_files (for read-only reviews)
        "get_file_contents",
        "pull_request_read"
      ]
    }
  }
}
```

### 4. Secret Protection

Never expose secrets in logs:

```yaml
gemini_debug: ${{ fromJSON(vars.DEBUG || false) }}
# Only enable for troubleshooting
```

---

## Enabling Auto-Triggers

The current configuration uses **manual-only mode**. To enable automatic triggers in the future:

### Enable Auto-Review on PR Open

Edit `.github/workflows/gemini-dispatch.yml`:

1. **Uncomment the `pull_request` trigger:**
   ```yaml
   on:
     # ... existing triggers ...
     pull_request:
       types:
         - 'opened'
   ```

2. **Update the `if` condition** (see comments in the workflow file)

3. **Update the extract_command script** to handle `pull_request.opened` events

### Enable Auto-Triage on Issue Open

Edit `.github/workflows/gemini-dispatch.yml`:

1. **Uncomment the `issues` trigger:**
   ```yaml
   on:
     # ... existing triggers ...
     issues:
       types:
         - 'opened'
         - 'reopened'
   ```

2. **Update the `if` condition and script** (detailed instructions in the workflow file comments)

### Workflow File Reference

All configuration options are documented with inline comments in:
- `.github/workflows/gemini-dispatch.yml` - Main dispatcher with toggle instructions
- `.github/workflows/gemini-review.yml` - PR review workflow
- `.github/workflows/gemini-triage.yml` - Issue triage workflow
- `.github/workflows/gemini-invoke.yml` - General assistant workflow (requires approval)
- `.github/workflows/gemini-fix.yml` - Automatic issue fixer workflow (creates PRs directly)

---

## Current Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| `GEMINI_API_KEY` secret | ✅ Configured | Authentication ready |
| `gemini-dispatch.yml` | ✅ Implemented | Manual-only mode |
| `gemini-review.yml` | ✅ Implemented | PR code review |
| `gemini-triage.yml` | ✅ Implemented | Issue labeling |
| `gemini-invoke.yml` | ✅ Implemented | General assistant (approval-based) |
| `gemini-fix.yml` | ✅ Implemented | Automatic issue fixer |
| `GEMINI.md` | ✅ Created | Project context |
| `.gitignore` | ✅ Updated | Excludes `.gemini/` |
| Auto-triggers | ⏸️ Disabled | Can enable later |

---

## Troubleshooting

### Error: "API keys are not supported by this API"

**Full Error Message:**
```
API keys are not supported by this API. Expected OAuth2 access token or other authentication credentials that assert a principal.
```

**Cause**: You're using an API key from the wrong source. The Gemini workflows use the Google AI Studio API (`generativelanguage.googleapis.com`), which only accepts Google AI Studio API keys.

**Solution:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key" (NOT from Google Cloud Console)
3. Copy the generated API key (starts with `AIza...`)
4. Update your `GEMINI_API_KEY` secret in repository settings:
   - Go to **Settings > Secrets and variables > Actions > Repository secrets**
   - Edit the `GEMINI_API_KEY` secret
   - Paste the new API key from Google AI Studio
5. Re-run the failed workflow

**Common Mistake**: Creating an API key from `https://console.cloud.google.com/marketplace/product/google/aiplatform.googleapis.com` (GCP Console) instead of Google AI Studio. These are different services with different authentication methods.

### Error: Rate Limit Exceeded

If you see rate limit errors, check the [Model Selection and Rate Limits](#b-model-selection-and-rate-limits) section above. The default model (`gemini-2.0-flash`) has a 15 RPM limit on the free tier.

**Solutions:**
- Wait for rate limit to reset (1 minute)
- Use a different model with higher limits (e.g., `gemini-2.5-flash-lite`)
- Upgrade to a paid Google AI Studio plan

### Workflow Doesn't Respond to @gemini-cli

**Check:**
1. Your user role (must be OWNER, MEMBER, or COLLABORATOR)
2. The `GEMINI_API_KEY` secret is configured correctly
3. The command syntax is correct (e.g., `@gemini-cli /review`, not `@gemini-cli/review`)

### Gemini Creates Plan But Doesn't Execute

This is expected behavior for the `/invoke` command. Gemini requires human approval before making changes:
1. Gemini posts a plan in the issue/PR
2. Human reviews and approves
3. Gemini executes the approved plan

Use `/fix` instead if you want automatic execution without approval.

---

## Related Resources

- [run-gemini-cli Repository](https://github.com/google-github-actions/run-gemini-cli)
- [Gemini CLI Documentation](https://github.com/google-gemini/gemini-cli)
- [Google AI Studio](https://aistudio.google.com/app/apikey) - **Get your API key here**
- [Chained Agent System](/docs/AGENT_QUICKSTART.md)

---

*Gemini CLI integration configured for the Chained autonomous AI ecosystem.*

