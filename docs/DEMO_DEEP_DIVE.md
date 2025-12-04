# 🎬 Demo & Deep Dive

This document provides a comprehensive look at the key technical capabilities of this repository, with links to actual implementations.

## 🤖 GitHub Copilot Custom Agents: Complete System

The repository demonstrates **GitHub Copilot's custom agent capabilities** through a production-ready agent system with over 100 specialized agents.

### Three-Layer Instruction Architecture

The system uses a **hierarchical instruction architecture** where instructions combine from multiple sources:

**Layer 1: GitHub Copilot Built-in Instructions**
- Platform-provided capabilities (code completion, language understanding, tool usage)
- Universal and unchangeable

**Layer 2: Repository-Wide Instructions**
- **File**: `.copilot-instructions.md` (root)
- **Scope**: All agent sessions in this repository
- **Contents**: Agent catalog, selection rules, code standards, PR workflow, communication requirements
- **View**: [.copilot-instructions.md](../.copilot-instructions.md)

**Layer 3A: Path-Specific Instructions** 
- **Location**: `.github/instructions/*.instructions.md`
- **Scope**: Apply to specific file paths based on `applyTo` patterns
- **Examples**:
  - [branch-protection.instructions.md](../.github/instructions/branch-protection.instructions.md) - Applies to all workflow files
  - [agent-mentions.instructions.md](../.github/instructions/agent-mentions.instructions.md) - Enforces @agent-name attribution
  - [terraform-provider-docs.instructions.md](../.github/instructions/terraform-provider-docs.instructions.md) - Terraform-specific guidance
  - [a2a-ui-development.instructions.md](../.github/instructions/a2a-ui-development.instructions.md) - A2A UI development rules

**Layer 3B: Agent-Specific Instructions**
- **Location**: `.github/agents/*.md`
- **Scope**: Individual agent personality, approach, and expertise
- **Format**: Markdown files with YAML frontmatter
- **Examples**:
  - [engineer-master.md](../.github/agents/engineer-master.md) - API engineering (inspired by Margaret Hamilton)
  - [troubleshoot-expert.md](../.github/agents/troubleshoot-expert.md) - Workflow debugging (inspired by Grace Hopper)
  - [secure-specialist.md](../.github/agents/secure-specialist.md) - Security review (inspired by Bruce Schneier)
  - [organize-guru.md](../.github/agents/organize-guru.md) - Code organization (inspired by Robert Martin)

When Copilot executes, it receives **all applicable instructions** (built-in + root + matching path instructions + agent definition), creating the complete instruction set.

### Copilot Environment Setup

The [copilot-setup-steps.yml](../.github/workflows/copilot-setup-steps.yml) workflow configures the Copilot execution environment:

**Key Features:**
- **Environment**: Uses `copilot` environment for secret access (`COPILOT_PAT`)
- **Toolchain**: Installs Node.js 20+ and Python 3.11
- **Dependencies**: Installs from `requirements.txt` and `package.json`
- **Context Optimization**: Sets `COPILOT_LIMIT_CONTEXT=true` and uses `.copilotignore`
- **Full Repository**: Clones with full history for diffs and context

**View the complete setup**: [copilot-setup-steps.yml](../.github/workflows/copilot-setup-steps.yml)

### MCP (Model Context Protocol) Server Configuration

This repository uses **three MCP servers** to extend Copilot's capabilities:

**1. GCP MCP Server** (Custom)
- **Configuration**: `.github/copilot/mcp.json`
- **Provider**: `@google-cloud/gcloud-mcp`
- **Purpose**: Enables gcloud command execution within Copilot
- **Authentication**: Uses `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- **View config**: [mcp.json](../.github/copilot/mcp.json)

**2. GitHub MCP Server** (Standard)
- **Provider**: `github-mcp-server`
- **Purpose**: GitHub API access (issues, PRs, workflows, repositories)
- **Built-in**: Automatically available in Copilot sessions

**3. Playwright MCP Server** (Standard)
- **Provider**: `playwright-browser`
- **Purpose**: Web browser automation and testing
- **Built-in**: Automatically available in Copilot sessions

**Why This Matters**: The MCP server configuration demonstrates how to extend Copilot beyond GitHub operations to include cloud infrastructure management.

### Agent Assignment & Matching

Agents are automatically assigned to issues based on content analysis:

**Matching Algorithm**: `tools/match-issue-to-agent.py`
- Keyword matching (1 point per match)
- Regex pattern matching (2 points per match)
- Minimum score threshold: 5 points
- Highest-scoring agent wins

**Agent Registry**: `.github/agent-system/registry.json`
- Lists all available agents
- Tracks protected agents (cannot be eliminated)
- Records performance metrics

**Example Agent Definitions**:
- 100+ agents covering infrastructure, security, testing, documentation, and more
- Each agent has distinct personality inspired by computing pioneers
- View the full catalog: [.github/agents/README.md](../.github/agents/README.md)

**Real Example**: See [issue #3520](https://github.com/enufacas/Chained/issues/3520) where the error observer system was implemented via agent assignment.

---

## 🔮 Gemini Workflows: Multi-Model Support

The repository demonstrates how **GitHub Actions can orchestrate non-Copilot AI models** through custom workflows, proving that agent orchestration isn't limited to one provider.

### How Gemini Workflows Work

These workflows use the `google-github-actions/run-gemini-cli` action to integrate **Google Gemini** (or other models) directly into GitHub Actions:

**Key Workflows:**

**1. [gemini-review.yml](../.github/workflows/gemini-review.yml)** - Automated PR Code Review
- Analyzes PR diffs and provides inline code suggestions
- Posts review comments directly on PRs
- Supports both Google AI Studio API and Vertex AI

**2. [gemini-triage.yml](../.github/workflows/gemini-triage.yml)** - Issue Labeling & Triage
- Analyzes issue content and assigns appropriate labels
- Prioritizes issues based on content
- Routes issues to relevant team members

**3. [gemini-fix.yml](../.github/workflows/gemini-fix.yml)** - Automated Issue Fixing
- Reads issue description and generates code fixes
- Creates PR with proposed solution
- Includes tests and documentation updates

**4. [gemini-invoke.yml](../.github/workflows/gemini-invoke.yml)** - General-Purpose Invocation
- Flexible workflow for custom Gemini prompts
- Supports file context and custom instructions
- Returns results as workflow artifacts

**5. [gemini-dispatch.yml](../.github/workflows/gemini-dispatch.yml)** - Smart Routing
- Analyzes requests and routes to appropriate Gemini workflow
- Acts as orchestrator for multiple Gemini capabilities

### Authentication Options

**Option 1: Google AI Studio** (Simpler setup)
```bash
# Get API key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your-api-key
```

**Option 2: Vertex AI** (For GCP users)
```bash
# Requires GCP project with Vertex AI enabled
GOOGLE_API_KEY=your-vertex-key
USE_VERTEX_AI=true
GOOGLE_CLOUD_PROJECT=your-project-id
```

### Why This Matters

These workflows prove that **GitHub Actions can orchestrate ANY AI model or provider**:
- ✅ Google Gemini (via gemini-cli)
- ✅ Anthropic Claude (via API or CLI tool)
- ✅ OpenAI GPT (via API integration)
- ✅ AWS Bedrock models (via AWS CLI)
- ✅ Local models (via Ollama or custom endpoints)

The pattern is simple: wrap the model's CLI or API in a GitHub Action, provide authentication, and orchestrate through workflows.

**Context File for Gemini**: The repository provides context optimized for Gemini workflows - see how it's structured in the workflow implementations.

---

## 🔗 A2A Protocol on GCP: Production Implementation

The repository includes a **production A2A (Agent-to-Agent) implementation** deployed to Google Cloud Run, demonstrating real agent collaboration beyond GitHub Actions constraints.

### Live A2A System

**Chat Interface**: [AG-UI Frontend](https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/)
- Create research and blog pipelines via chat
- Monitor real-time agent execution
- View A2A task IDs, artifacts, and timing
- Powered by CopilotKit + Vertex AI (Gemini 2.0 Flash)

**Deployed A2A Agents** (Cloud Run):

| Agent | Live URL | Purpose |
|-------|----------|---------|
| Academic Research | [chained-academic-research](https://chained-academic-research-sguacxy5gq-uc.a.run.app) | Discovers research topics via academic APIs |
| Google Trends | [chained-google-trends](https://chained-google-trends-sguacxy5gq-uc.a.run.app) | Analyzes SEO trends and keywords |
| Blog Writer | [chained-blog-writer](https://chained-blog-writer-sguacxy5gq-uc.a.run.app) | Writes and publishes blog posts |
| Code Reviewer | [chained-code-reviewer](https://chained-code-reviewer-sguacxy5gq-uc.a.run.app) | Reviews code and provides feedback |
| Data Analyst | [chained-data-analyst](https://chained-data-analyst-sguacxy5gq-uc.a.run.app) | Analyzes data and generates insights |
| Image Generator | [chained-image-generator](https://chained-image-generator-sguacxy5gq-uc.a.run.app) | Creates visual assets |

Each agent exposes standard A2A endpoints:
- `/.well-known/agent.json` - AgentCard (discovery metadata)
- `/health` - Health check
- `POST /a2a/tasks` - Send A2A task messages

### A2A Protocol Compliance

The implementation follows the [A2A specification](https://github.com/a2aproject/A2A):

**AgentCard**: Each agent publishes discovery metadata
```json
{
  "name": "Academic Research Agent",
  "capabilities": ["research", "academic-search"],
  "version": "1.0.0",
  "endpoints": {
    "tasks": "https://chained-academic-research-sguacxy5gq-uc.a.run.app/a2a/tasks"
  }
}
```

**A2A Tasks**: Messages follow standard format
```json
{
  "taskId": "unique-id",
  "contextId": "pipeline-123",
  "agentName": "research-agent",
  "capabilities": ["research"],
  "input": { "topic": "AI agents" },
  "referenceTaskIds": ["previous-task-id"]
}
```

**A2A Artifacts**: Results include structured outputs
```json
{
  "taskId": "unique-id",
  "status": "completed",
  "artifacts": [
    { "name": "research.json", "type": "application/json", "data": {...} }
  ]
}
```

### Three-Tier Architecture

The system accommodates GitHub Actions runner constraints:

**Tier 1: Same-Runner (HTTP)**
- Multiple agents in single workflow job
- Traditional A2A HTTP protocol (localhost)
- Fast (<1ms latency)
- Example: [a2a-local-orchestration.yml](../.github/workflows/a2a-local-orchestration.yml)

**Tier 2: Cross-Runner (GitHub-Mediated)**
- Long-running tasks, parallel execution
- Communication via GitHub Artifacts or Branches
- Slower (~5s polling) but enables true parallelism
- Example: [a2a-parallel-agents.yml](../.github/workflows/a2a-parallel-agents.yml)

**Tier 3: Cloud Run (Production)**
- Real HTTP-based A2A agents deployed to Cloud Run
- No runner constraints
- Full A2A protocol support
- Chat interface for human interaction
- Live system: [AG-UI Frontend](https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/)

### Infrastructure

**Deployment**: `infrastructure/terraform/`
- Cloud Run services for each agent
- Vertex AI integration
- Artifact Registry for Docker images
- Secret Manager for credentials

**Agent Implementation**: `infrastructure/docker/adk-agents/`
- Python-based agents using Google ADK patterns
- Dockerfile for each agent
- Shared utilities for A2A protocol handling

**Pipeline Orchestration**: `adk-a2a-blog-pipeline.yml`
- Demonstrates multi-agent coordination
- Research → Trends → Blog Writer flow
- Deploys results to Cloud Storage

### Real A2A Pipeline Example

**Pipeline Flow**:
```
Academic Research Agent → discovers "AI Agent Collaboration" topic
         ↓ (A2A task with referenceTaskIds)
Google Trends Agent → analyzes SEO trends for keywords
         ↓ (A2A task with previous artifacts)
Blog Writer Agent → writes optimized blog post
         ↓ (publishes to Cloud Storage)
https://storage.googleapis.com/chained-blog/posts/ai-agent-collaboration.html
```

**Try it yourself**: Visit the [AG-UI Frontend](https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/) and ask to "create a blog pipeline about quantum computing"

### Documentation

- **[A2A Documentation](./a2a/README.md)** - Complete A2A guide
- **[A2A Success History](./a2a/A2A_SUCCESS_HISTORY.md)** - Working chat conversation and milestones
- **[A2A Architecture](./a2a/A2A_GITHUB_RUNNERS_ARCHITECTURE.md)** - Three-tier design
- **[ADK Pipeline Implementation](./ADK_A2A_PIPELINE_IMPLEMENTATION.md)** - GCP deployment guide

**Real Implementation**: See [PR #3520](https://github.com/enufacas/Chained/pull/3520) for the error observer A2A system implementation.
