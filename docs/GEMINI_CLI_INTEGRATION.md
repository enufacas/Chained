# Gemini CLI Integration Options for Chained

This document outlines customization options for integrating the [Gemini CLI GitHub Action](https://github.com/google-github-actions/run-gemini-cli) into the Chained repository.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Available Workflow Types](#available-workflow-types)
4. [Customization Options](#customization-options)
5. [Integration with Chained's Agent System](#integration-with-chaineds-agent-system)
6. [Recommended Configuration](#recommended-configuration)
7. [Security Considerations](#security-considerations)
8. [Discussion Points](#discussion-points)

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
   - Get from [Google AI Studio](https://aistudio.google.com/apikey)
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
| `@gemini-cli <request>` | Free-form AI assistance |

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

### B. Model Selection

```yaml
# Repository variable: GEMINI_MODEL
gemini_model: 'gemini-2.0-flash-exp'  # Latest experimental
# or
gemini_model: 'gemini-1.5-pro'        # Stable, longer context
```

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
4. `gemini-invoke.yml` - General assistance

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

## Discussion Points

### Questions to Consider

1. **Scope**: Which workflow types should we implement?
   - [ ] PR Review only
   - [ ] Issue Triage only
   - [ ] General Assistance
   - [ ] All of the above

2. **Integration Depth**: How should Gemini interact with existing agents?
   - [ ] Parallel (independent)
   - [ ] Complementary (specific tasks)
   - [ ] Integrated (as an agent type)

3. **Trigger Preferences**: How should Gemini be activated?
   - [ ] Automatic on PR open
   - [ ] On-demand via `@gemini-cli`
   - [ ] Scheduled triage
   - [ ] All of the above

4. **Review Style**: For PR reviews, what approach?
   - [ ] Comment-only feedback
   - [ ] Code suggestions
   - [ ] Approve/Request changes

5. **Authentication**: Which method?
   - [ ] API Key (simplest)
   - [ ] Vertex AI (GCP billing)
   - [ ] Custom GitHub App (better identity)

6. **Customization Priority**: What should GEMINI.md emphasize?
   - [ ] Chained architecture context
   - [ ] Agent system understanding
   - [ ] Code style guidelines
   - [ ] Security practices

### Next Steps

1. **Secret Setup**: Add `GEMINI_API_KEY` to repository secrets
2. **Choose Workflows**: Select which workflow types to implement
3. **Customize Prompts**: Create GEMINI.md and TOML configurations
4. **Test**: Start with a disabled workflow and test manually
5. **Enable**: Gradually enable triggers based on testing results

---

## Related Resources

- [run-gemini-cli Repository](https://github.com/google-github-actions/run-gemini-cli)
- [Gemini CLI Documentation](https://github.com/google-gemini/gemini-cli)
- [Google AI Studio](https://aistudio.google.com/apikey)
- [Chained Agent System](/docs/AGENT_QUICKSTART.md)

---

*This document was created to discuss Gemini CLI integration options for the Chained autonomous AI ecosystem.*

