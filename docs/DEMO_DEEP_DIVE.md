# 🎬 Demo & Deep Dive

This document provides a comprehensive look at the key technical capabilities of this repository, with links to actual implementations.

## 🤖 GitHub Copilot Custom Agents: Complete System

**🔗 Quick Links for Demo**:
- **[.copilot-instructions.md](../.copilot-instructions.md)** - Repository-wide instructions (root level)
- **[.github/instructions/](../.github/instructions/)** - Path-specific instructions directory
- **[.github/agents/](../.github/agents/)** - 100+ agent definitions
- **[copilot-setup-steps.yml](../.github/workflows/copilot-setup-steps.yml)** - Copilot environment configuration
- **[mcp.json](../.github/copilot/mcp.json)** - MCP server setup (includes custom GCP server)
- **[PR #3218](https://github.com/enufacas/Chained/pull/3218)** - Real agent task example (A2A implementation)

---

The repository demonstrates **GitHub Copilot's custom agent capabilities** through an agent system with over 100 specialized agents for testing and demonstration.

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

**Real Example**: See [PR #3218](https://github.com/enufacas/Chained/pull/3218) where the A2A protocol was implemented with GeminiAgentExecutor and task lifecycle management.

---

## 🔮 Gemini Workflows: Multi-Model Support

**🔗 Quick Links for Demo**:
- **[gemini-review.yml](../.github/workflows/gemini-review.yml)** - PR code review with Gemini
- **[gemini-triage.yml](../.github/workflows/gemini-triage.yml)** - Issue triage automation
- **[gemini-fix.yml](../.github/workflows/gemini-fix.yml)** - Automated bug fixes
- **[gemini-invoke.yml](../.github/workflows/gemini-invoke.yml)** - Manual Gemini invocation
- **[gemini-dispatch.yml](../.github/workflows/gemini-dispatch.yml)** - Webhook-triggered Gemini tasks

---

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

## 🔗 A2A Protocol on GCP: Testing Implementation

**🔗 Quick Links for Demo**:
- **[AG-UI Frontend](https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/)** - Live chat interface for testing A2A pipelines
- **[Academic Research Agent](https://chained-academic-research-sguacxy5gq-uc.a.run.app)** - Research paper analysis
- **[Google Trends Agent](https://chained-google-trends-sguacxy5gq-uc.a.run.app)** - Trend data collection
- **[Blog Writer Agent](https://chained-blog-writer-sguacxy5gq-uc.a.run.app)** - Content generation
- **[docs/a2a/README.md](../docs/a2a/README.md)** - Complete A2A documentation
- **[PR #3218](https://github.com/enufacas/Chained/pull/3218)** - A2A implementation with GeminiAgentExecutor

---

The repository includes an **A2A (Agent-to-Agent) implementation** deployed to Google Cloud Run for testing agent collaboration patterns.

### Live A2A System

**Chat Interface**: [AG-UI Frontend](https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/)
- Test research and blog pipelines via chat
- Monitor agent execution
- View A2A task IDs, artifacts, and timing
- Powered by CopilotKit + Vertex AI (Gemini 2.0 Flash)

**Deployed on GCP Cloud Run**: 6 test agents ([Academic Research](https://chained-academic-research-sguacxy5gq-uc.a.run.app), [Google Trends](https://chained-google-trends-sguacxy5gq-uc.a.run.app), [Blog Writer](https://chained-blog-writer-sguacxy5gq-uc.a.run.app), [Code Reviewer](https://chained-code-reviewer-sguacxy5gq-uc.a.run.app), [Data Analyst](https://chained-data-analyst-sguacxy5gq-uc.a.run.app), [Image Generator](https://chained-image-generator-sguacxy5gq-uc.a.run.app))

### Key Features

**A2A Protocol Compliant**: Implements [A2A specification](https://github.com/a2aproject/A2A)
- AgentCards for discovery (`.well-known/agent.json`)
- Standard task message format
- Artifact-based results

**Built with GCP MCP Server**: Used custom GCP MCP server to:
- Troubleshoot deployment errors
- Configure Cloud Run services
- Set up Vertex AI integration
- Debug infrastructure issues

**Prompt Engineered**: All agents built using natural language prompts rather than hand-coded logic

### Documentation

Complete technical details:
- **[A2A Documentation](./a2a/README.md)** - Full A2A guide
- **[A2A Success History](./a2a/A2A_SUCCESS_HISTORY.md)** - Chat conversation and milestones
- **[A2A Architecture](./a2a/A2A_GITHUB_RUNNERS_ARCHITECTURE.md)** - Three-tier design
- **[ADK Pipeline Implementation](./ADK_A2A_PIPELINE_IMPLEMENTATION.md)** - GCP deployment details

**Implementation Example**: See [PR #3218](https://github.com/enufacas/Chained/pull/3218) for GeminiAgentExecutor and task lifecycle.

---

## 💬 Copilot Chat vs Agent Tasks: Demonstration Guide

**🔗 Quick Links for Demo**:
- **[PR #3218](https://github.com/enufacas/Chained/pull/3218)** - Use Copilot Chat on this PR for read-only Q&A
- **[PR #3548](https://github.com/enufacas/Chained/pull/3548)** - Another great PR for Copilot Chat demos
- **[Actions Tab](https://github.com/enufacas/Chained/actions)** - View agent task runners in action
- **[copilot-setup-steps.yml](../.github/workflows/copilot-setup-steps.yml)** - Agent task configuration
- **[Workflow Runs](https://github.com/enufacas/Chained/actions/workflows/copilot-setup-steps.yml)** - History of agent executions

---

This section demonstrates GitHub Copilot's two execution models through live examples and use cases.

### Example 1: Copilot Chat - Interactive Code Questions

**🔗 Demo Links**:
- **Try on [PR #3218](https://github.com/enufacas/Chained/pull/3218)** - Click Copilot Chat button in PR
- **Try on [PR #3548](https://github.com/enufacas/Chained/pull/3548)** - Another example PR
- **Try on [any open issue](https://github.com/enufacas/Chained/issues)** - Ask questions about issues

**What It Demonstrates**:
- Conversational AI directly in GitHub's web interface
- Instant answers about code, issues, and repository context
- Available in GitHub.com, mobile app, and VS Code

**Example Questions to Ask Copilot Chat**:
```
On PR #3218:
"What does this PR implement?"
"Explain the GeminiAgentExecutor class"
"How does the A2A task lifecycle work?"

On PR #3548:
"What errors were fixed in this PR?"
"Explain the localStorage quota handling"
"How does the error observer system work?"
```

**Why It Matters**:
- Zero setup required - hosted entirely by GitHub
- Read-only advisory capabilities
- Included in subscription ($10-$39/user/month)
- Perfect for questions, code explanations, and guidance

**Key Limitation**: Cannot modify files or create PRs

---

### Example 2: Copilot Agent Tasks - Autonomous Code Changes

**🔗 Demo Links**:
- **[PR #3218](https://github.com/enufacas/Chained/pull/3218)** - A2A protocol implementation by agent
- **[PR #3548](https://github.com/enufacas/Chained/pull/3548)** - Error observer fixes by agent
- **[Actions Tab](https://github.com/enufacas/Chained/actions)** - See runners executing agent tasks
- **[Workflow Runs](https://github.com/enufacas/Chained/actions/workflows/copilot-setup-steps.yml)** - History of all agent executions
- **[copilot-setup-steps.yml](../.github/workflows/copilot-setup-steps.yml)** - Agent environment setup

**What It Demonstrates**:
- Autonomous coding agent executing as GitHub Actions workflow
- Full read-write capabilities: clones repo, modifies files, runs tests, creates PR
- Triggered from GitHub.com, VS Code, or mobile app

**How It Works**:
1. User assigns issue to @copilot (or clicks "Copilot" button)
2. GitHub triggers [copilot-setup-steps.yml](../.github/workflows/copilot-setup-steps.yml)
3. Workflow runs on GitHub Runner (hosted or self-hosted)
4. Agent installs dependencies, clones repo with full context
5. Agent reads all applicable instructions
6. Agent makes code changes and runs tests
7. Agent creates PR with complete implementation

**Why It Matters**:
- Actual code contributions, not just suggestions
- Runs complete development workflow (build, test, lint)
- Scales from simple fixes to complex features
- Executes in isolated runner environment

**Key Difference**: Creates commits and PRs vs. providing advice

---

### Example 3: GitHub Runners - Where Agent Tasks Execute

**🔗 Demo Links**:
- **[Actions Tab](https://github.com/enufacas/Chained/actions)** - Live view of runners executing tasks
- **[copilot-setup-steps.yml](../.github/workflows/copilot-setup-steps.yml)** - Runner configuration
- **[Workflow Runs](https://github.com/enufacas/Chained/actions/workflows/copilot-setup-steps.yml)** - Execution history
- **[Settings → Actions → Runners](https://github.com/enufacas/Chained/settings/actions/runners)** - Runner management (org/repo admins)

**What It Demonstrates**:
- Agent task execution environment setup
- Tool installation (Node.js 20+, Python 3.11)
- MCP server configuration (GCP, GitHub, Playwright)
- Repository cloning with full history

**Three Hosting Options**:

**Option 1: GitHub-Hosted Runners** (Default)
- Pre-configured VMs: 2-core CPU, 7 GB RAM, 14 GB SSD
- Free tier: 2,000-50,000 minutes/month (based on plan)
- Pricing: $0.008/min (Linux), $0.016/min (Windows), $0.08/min (macOS)
- Example: Most Copilot tasks run in 5-15 minutes = $0.04-$0.12 per task

**Option 2: GitHub Larger Runners** (Premium)
- 4-64 cores, up to 256 GB RAM
- Faster execution for complex builds
- Pricing: $0.016-$0.064/min
- Example: Large codebase with 30 min build = $0.48-$1.92

**Option 3: Self-Hosted Runners** (Your Infrastructure)
- Your own servers, VMs, or containers
- Zero per-minute charges (infrastructure costs only)
- Access to internal resources (databases, VPNs)
- Breakeven: ~5,000 minutes/month vs. GitHub-hosted

**Why It Matters**:
- Understand where your compute runs
- Cost optimization for high-volume usage
- Security and compliance requirements
- Internal resource access needs

**Setup Example**: See [Self-Hosted Runner Setup](#self-hosted-runner-setup) below for installation steps

---

### Example 4: Managing Agent Tasks From Multiple Interfaces

**🔗 Demo Links**:
- **[GitHub.com Issues](https://github.com/enufacas/Chained/issues)** - Click "Copilot" button on any issue
- **[Actions Tab](https://github.com/enufacas/Chained/actions)** - Monitor agent task execution
- **[VS Code GitHub Extension](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-pull-request-github)** - IDE integration
- **[GitHub Mobile App](https://github.com/mobile)** - iOS/Android trigger

**Access Points**:
- **GitHub.com**: Issue → "Copilot" button → "Create task"
- **VS Code**: GitHub extension → Issue → "Assign to Copilot"
- **Mobile**: GitHub app → Issue → "..." menu → "Assign to Copilot"

**What It Demonstrates**:
- Unified agent task system accessible from anywhere
- Real-time progress in Actions tab
- Email/push notifications on completion

**Monitoring Example**:
1. Trigger agent task from any interface
2. Navigate to Actions tab to watch live logs
3. Receive notification when PR is created
4. Review PR and merge

**Why It Matters**:
- Flexibility to trigger from IDE, web, or mobile
- Consistent experience across platforms
- Visibility into agent progress

---

### Example 5: Enterprise Cost Planning

**🔗 Calculate Your Costs**: Use these scenarios

**Scenario 1: Small Team (10 developers)**
```
Copilot Enterprise: 10 × $39 = $390/month
Agent tasks: ~50 tasks/month × 10 min avg × $0.008 = $4/month
Total: ~$394/month
```

**Scenario 2: Medium Team (50 developers)**
```
Copilot Enterprise: 50 × $39 = $1,950/month
Agent tasks: ~200 tasks/month × 15 min avg × $0.008 = $24/month
Total: ~$1,974/month

Alternative with self-hosted runners:
Copilot Enterprise: $1,950/month
2 × EC2 t3.large runners: ~$150/month
Total: ~$2,100/month (with faster execution + internal access)
```

**What It Demonstrates**:
- Runner costs are typically small vs. subscription
- Self-hosted makes sense at higher volumes
- Cost-per-task decreases with scale

**Why It Matters**:
- Budget planning for adoption
- ROI calculation
- Infrastructure decision making

---

### Self-Hosted Runner Setup

**🔗 Installation Steps**:

```bash
# 1. Provision infrastructure (Ubuntu VM)
# Minimum: 2-core CPU, 4 GB RAM, 20 GB disk
# Recommended: 4-core CPU, 8 GB RAM, 50 GB disk

# 2. Download and install runner
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64.tar.gz
tar xzf actions-runner-linux-x64.tar.gz

# 3. Configure (get token from repo settings → Actions → Runners)
./config.sh --url https://github.com/YOUR_ORG/YOUR_REPO --token YOUR_TOKEN

# 4. Install and start as service
sudo ./svc.sh install
sudo ./svc.sh start

# 5. Update workflow to use self-hosted
# In .github/workflows/copilot-setup-steps.yml:
# runs-on: self-hosted  # instead of ubuntu-latest
```

**What It Demonstrates**:
- Complete self-hosted runner setup
- Service installation for 24/7 availability
- Integration with existing workflows

**Why It Matters**:
- Cost reduction at scale
- Internal resource access
- Custom hardware requirements
- Security and compliance control

**Security Considerations**:
- Use dedicated, isolated machines
- Implement network segmentation
- Regular OS and runner updates
- Rotate secrets frequently

---

### Comparison Table: Chat vs Agent Tasks

| Aspect | Copilot Chat | Copilot Agent Tasks |
|--------|--------------|---------------------|
| **Execution** | GitHub-hosted only | GitHub-hosted or self-hosted runners |
| **Capabilities** | Read-only, advisory | Full read-write, autonomous |
| **Output** | Text/code suggestions | Commits, PRs, file changes |
| **Duration** | Instant responses | 5-60 minutes |
| **Access** | Web, mobile, IDE | Web, mobile, IDE (triggers workflow) |
| **Cost** | Included in subscription | Subscription + runner time |
| **Use Case** | Questions, explanations | Feature implementation, refactoring |
| **Example** | "How does this work?" | [PR #3218](https://github.com/enufacas/Chained/pull/3218) |

---

### Quick Reference: When to Use What

**Use Copilot Chat when**:
- Asking questions about code
- Getting implementation guidance
- Understanding existing functionality
- Quick code suggestions

**Use Copilot Agent Tasks when**:
- Need actual code changes
- Implementing features from issues
- Refactoring or cleanup work
- Running tests and builds

**Use Self-Hosted Runners when**:
- High task volume (>10,000 min/month)
- Need internal resource access
- Custom hardware requirements
- Cost optimization priority
