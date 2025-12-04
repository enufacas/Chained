# 🎬 Demo & Deep Dive

This document provides a comprehensive look at the key technical capabilities of this repository, with links to actual implementations.

## 🤖 GitHub Copilot Custom Agents: Complete System

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

## 💬 Copilot Chat vs Agent Tasks: Understanding the Execution Models

GitHub Copilot provides two distinct execution models, each with different capabilities, hosting, and cost implications.

### Copilot Chat on GitHub

**What It Is**: Interactive conversational AI directly in GitHub's web interface

**Where It Runs**:
- Hosted entirely by GitHub
- No local or self-hosted infrastructure required
- Compute provided by Microsoft/GitHub infrastructure

**Access Points**:
- **GitHub.com Web Interface**: Chat panel in issues, PRs, discussions
- **GitHub Mobile App**: Chat available on mobile devices
- **VS Code / IDE**: GitHub Copilot Chat extension

**Capabilities**:
- Answer questions about code, issues, and PRs
- Explain code snippets and suggest improvements
- Generate code based on natural language descriptions
- Search and reference repository context
- Cannot directly modify repository files
- Cannot trigger workflows or create commits

**Cost Model** (as of 2024):
- **GitHub Copilot Individual**: $10/month or $100/year
- **GitHub Copilot Business**: $19/user/month
- **GitHub Copilot Enterprise**: $39/user/month (includes chat + code completion + agent tasks)

**Examples**:
```
User: "Explain how the three-layer instruction architecture works"
Copilot Chat: [Provides explanation based on repository context]

User: "How do I add a new agent?"
Copilot Chat: [References .github/agents/ and provides steps]
```

### Copilot Agent Tasks

**What They Are**: Autonomous coding agents that execute as GitHub Actions workflows

**Where They Run**:
- **GitHub-Hosted Runners**: Free tier + usage-based pricing
- **Self-Hosted Runners**: Your own infrastructure (servers, VMs, containers)
- **Larger Runners**: Premium GitHub-hosted runners with more resources

**Access Points**:

**1. From GitHub.com (Web Interface)**:
- Navigate to issue → Click "Copilot" button → Select "Create task"
- Copilot agent triggers as GitHub Actions workflow
- Agent clones repo, reads instructions, makes changes, creates PR
- Real-time progress visible in Actions tab

**2. From VS Code / IDE**:
- Install GitHub Copilot extension
- Open issue in VS Code GitHub integration
- Click "Assign to Copilot" in issue view
- Task executes on GitHub-hosted or self-hosted runner
- Progress tracked in GitHub Actions

**3. From GitHub Mobile App**:
- Open issue in mobile app
- Tap "..." menu → "Assign to Copilot"
- Task executes on GitHub infrastructure
- Receive notifications when PR is ready

**Capabilities**:
- ✅ Clone entire repository
- ✅ Read all files and context
- ✅ Create new files and modify existing ones
- ✅ Run tests, linters, build tools
- ✅ Create commits and push to branches
- ✅ Open pull requests with changes
- ✅ Execute shell commands (within runner environment)
- ✅ Access secrets via GitHub environments
- ✅ Install dependencies (npm, pip, apt, etc.)

**Execution Flow**:
```
1. User assigns issue to @copilot
   ↓
2. GitHub triggers copilot-agent workflow
   ↓
3. Workflow runs on GitHub Runner (hosted or self-hosted)
   ↓
4. Runner executes copilot-setup-steps.yml (installs dependencies)
   ↓
5. Copilot agent clones repo with full context
   ↓
6. Agent reads instructions (.copilot-instructions.md + path + agent-specific)
   ↓
7. Agent makes code changes, runs tests
   ↓
8. Agent creates PR with changes
   ↓
9. User reviews and merges PR
```

**Real Example**: See this repository's [copilot-setup-steps.yml](../.github/workflows/copilot-setup-steps.yml) for agent task configuration.

### GitHub Runners: Hosting Copilot Compute

#### GitHub-Hosted Runners (Default)

**What They Provide**:
- Pre-configured virtual machines (Ubuntu, Windows, macOS)
- Standard compute resources:
  - **Linux/Windows**: 2-core CPU, 7 GB RAM, 14 GB SSD
  - **macOS**: 3-core CPU, 14 GB RAM, 14 GB SSD
- Auto-scaling based on workflow demand
- Maintained by GitHub (OS updates, security patches)

**Included Free Tier** (per month):
- **Public repositories**: Unlimited minutes
- **GitHub Free**: 2,000 minutes
- **GitHub Pro**: 3,000 minutes
- **GitHub Team**: 3,000 minutes (shared)
- **GitHub Enterprise**: 50,000 minutes (shared)

**Usage-Based Pricing** (beyond free tier):
- **Linux runners**: $0.008/minute
- **Windows runners**: $0.016/minute
- **macOS runners**: $0.08/minute

**Copilot Agent Task Typical Duration**:
- Simple tasks: 5-10 minutes
- Complex refactoring: 15-30 minutes
- Large codebase changes: 30-60 minutes

**Example Cost Calculation**:
```
Scenario: 20 Copilot agent tasks per month on Linux runners
Average duration: 10 minutes per task
Total: 200 minutes/month

If on GitHub Team (3,000 minutes free): $0 (within free tier)
If exceeding free tier by 200 minutes: 200 × $0.008 = $1.60/month
```

#### GitHub Larger Runners (Premium)

**When to Use**: For faster agent execution or resource-intensive tasks

**Specifications**:
- 4-core, 8-core, 16-core, 32-core, 64-core options
- Up to 256 GB RAM
- Up to 2 TB SSD storage
- Linux and Windows available

**Pricing** (examples):
- **4-core, 16 GB RAM**: $0.016/minute
- **8-core, 32 GB RAM**: $0.032/minute
- **16-core, 64 GB RAM**: $0.064/minute

**Use Cases**:
- Large monorepo builds
- Complex multi-language projects
- Parallel test execution
- Heavy computation tasks

#### Self-Hosted Runners

**Why Use Self-Hosted Runners**:
- ✅ Reduce costs for high-volume usage
- ✅ Access to internal/private resources (databases, APIs, VPNs)
- ✅ Custom hardware (GPUs, specialized CPUs)
- ✅ Better control over security and compliance
- ✅ Persistent environment between runs
- ✅ No per-minute charges

**How to Set Up**:

1. **Provision Infrastructure**:
   - Physical server, VM, or container
   - Minimum: 2-core CPU, 4 GB RAM, 20 GB disk
   - Recommended: 4-core CPU, 8 GB RAM, 50 GB disk

2. **Install Runner**:
   ```bash
   # On Ubuntu/Linux
   mkdir actions-runner && cd actions-runner
   curl -o actions-runner-linux-x64.tar.gz -L \
     https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64.tar.gz
   tar xzf actions-runner-linux-x64.tar.gz
   
   # Configure runner (get token from repo settings)
   ./config.sh --url https://github.com/YOUR_ORG/YOUR_REPO --token YOUR_TOKEN
   
   # Install and start as service
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```

3. **Configure for Copilot Agent Tasks**:
   - Label runner: `copilot-agent`
   - Install required tools (Node.js, Python, Docker)
   - Configure secrets/credentials
   - Set up network access to internal resources

4. **Update Workflow**:
   ```yaml
   jobs:
     copilot-setup-steps:
       runs-on: self-hosted  # Use self-hosted instead of ubuntu-latest
       # ... rest of copilot-setup-steps.yml
   ```

**Security Considerations**:
- ⚠️ Self-hosted runners execute arbitrary code from workflows
- ⚠️ Use dedicated, isolated machines (not shared infrastructure)
- ⚠️ Implement network segmentation and firewall rules
- ⚠️ Regularly update runner software and OS
- ✅ Use runner groups to control access
- ✅ Require approval for workflow runs from forks
- ✅ Rotate secrets regularly

**Cost Comparison Example**:

| Scenario | GitHub-Hosted | Self-Hosted (AWS EC2 t3.medium) |
|----------|---------------|----------------------------------|
| **Setup** | $0 (instant) | ~$50-100 (initial setup time) |
| **Monthly Cost** | 1,000 minutes = $8 | ~$30-40/month (24/7 running) |
| **10,000 minutes** | $80/month | ~$30-40/month |
| **100,000 minutes** | $800/month | ~$50-60/month (may need bigger instance) |
| **Breakeven** | ~5,000 minutes/month | |

**Recommendation**:
- **Use GitHub-Hosted Runners** if:
  - Monthly usage < 5,000 minutes
  - Don't need access to internal resources
  - Want zero maintenance
  - Public repositories (unlimited free)

- **Use Self-Hosted Runners** if:
  - Monthly usage > 10,000 minutes
  - Need internal resource access (databases, APIs)
  - Require specific hardware/software
  - Want to optimize costs at scale

### Enterprise Cost Model Summary

**GitHub Copilot Enterprise**: $39/user/month includes:
- Copilot Chat (web, mobile, IDE)
- Copilot code completion
- Copilot agent tasks (workflow execution)
- Knowledge bases (optional)
- Fine-tuned models (optional)

**Additional Runner Costs**:
- GitHub-hosted runners: Usage-based (see pricing above)
- Self-hosted runners: Infrastructure costs only
- Larger runners: Premium per-minute pricing

**Total Cost of Ownership Example** (50-person engineering team):

```
Scenario 1: GitHub-Hosted Only
- Copilot Enterprise: 50 users × $39 = $1,950/month
- Avg 100 agent tasks/month, 15 min each = 1,500 minutes
- Runner cost: 1,500 × $0.008 = $12/month
- Total: ~$1,962/month

Scenario 2: Self-Hosted Runners
- Copilot Enterprise: 50 users × $39 = $1,950/month
- Self-hosted runners: 2 × EC2 t3.large = ~$150/month
- Total: ~$2,100/month (with faster execution + internal access)
```

### Managing Agent Tasks

**From IDE** (VS Code):
1. Install GitHub Copilot extension
2. Open repository in VS Code
3. View GitHub issues in sidebar
4. Right-click issue → "Assign to Copilot"
5. Monitor progress in GitHub Actions tab

**From GitHub.com**:
1. Navigate to issue
2. Click "Copilot" button in issue sidebar
3. Select "Create agent task"
4. Agent begins execution immediately
5. Check Actions tab for real-time logs

**From GitHub Mobile**:
1. Open issue in GitHub mobile app
2. Tap "..." menu
3. Select "Assign to Copilot"
4. Receive notification when PR is created

**Monitoring Execution**:
- **Actions Tab**: Real-time workflow logs
- **Copilot Panel**: High-level progress updates
- **Email Notifications**: Success/failure alerts
- **GitHub Mobile**: Push notifications

**Example Workflow**: See how this repository handles agent tasks in [copilot-setup-steps.yml](../.github/workflows/copilot-setup-steps.yml)

### Real-World Examples from This Repository

**Example 1: Agent Assignment** → [Issue #3520](https://github.com/enufacas/Chained/issues/3520)
- User created issue describing error observer system
- `@troubleshoot-expert` agent was assigned
- Agent executed on GitHub-hosted runner
- Agent created PR #3520 with full implementation
- ~25 minutes of runner time

**Example 2: Copilot Setup Steps** → [copilot-setup-steps.yml](../.github/workflows/copilot-setup-steps.yml)
- Installs Node.js 20+ and Python 3.11
- Configures MCP servers (GCP, GitHub, Playwright)
- Sets up environment variables
- Clones repository with full history
- Executes in ~3-5 minutes on GitHub-hosted runner

**Example 3: Multi-Agent Workflow** → [agent-assignment](../.github/workflows/assign-copilot-to-issue.yml)
- Analyzes issue content
- Matches to specialized agent (100+ options)
- Assigns agent with highest confidence score
- Agent executes autonomously on GitHub runner

### Key Takeaways

| Aspect | Copilot Chat | Copilot Agent Tasks |
|--------|--------------|---------------------|
| **Execution** | GitHub-hosted only | GitHub-hosted or self-hosted runners |
| **Capabilities** | Read-only, advisory | Full read-write, autonomous |
| **Cost** | Included in subscription | Subscription + runner time |
| **Access** | Web, mobile, IDE | Web, mobile, IDE (triggers workflow) |
| **Duration** | Instant responses | Minutes to hours |
| **Output** | Text/code suggestions | Commits, PRs, file changes |
| **Scalability** | Per-user licensing | Add runners as needed |
