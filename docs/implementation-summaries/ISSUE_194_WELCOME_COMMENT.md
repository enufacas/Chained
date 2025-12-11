# ADK A2A Blog Pipeline - Issue #194 Welcome Comment

This document contains a comprehensive welcome comment that should be posted to Issue #194 to help users understand the tracking issue.

---

## 🎯 Welcome to the ADK A2A Blog Pipeline Tracking Issue!

This issue serves as the **centralized tracking hub** for all ADK A2A Blog Pipeline executions. Every time the pipeline runs (scheduled or manual), it will automatically post a comment here with the results.

### 📊 What Gets Tracked

Each pipeline run comment includes:
- **Timestamp** (UTC) - When the pipeline executed
- **Trigger Type** - Scheduled (every 6 hours) or manual (workflow_dispatch)
- **Run Mode** - Simulation, Cloud Run, or dry run
- **Workflow Link** - Direct link to the GitHub Actions run
- **Pipeline Summary** - Status of each agent step:
  - 🔬 Academic Research Agent - Topics discovered
  - 📈 Google Trends Agent - SEO analysis
  - ✍️ Blog Writer Agent - Content generated

### 🔧 Quick Access Tools

#### View This Issue
```bash
# Find tracking issue by label
gh issue list --label "adk-pipeline" --state open

# View issue with all run comments
gh issue view <issue-number> --comments
```

#### Using the Helper Script
```bash
# View tracking issue with all history
./tools/adk-pipeline-status.sh view

# Check recent pipeline runs
./tools/adk-pipeline-status.sh recent

# Show failed runs only
./tools/adk-pipeline-status.sh failed

# Manually trigger a pipeline run
./tools/adk-pipeline-status.sh trigger

# Check agent health status
./tools/adk-pipeline-status.sh health

# Show help
./tools/adk-pipeline-status.sh help
```

### 🚀 Pipeline Architecture

The ADK A2A Blog Pipeline implements the Agent-to-Agent (A2A) protocol:

```
GitHub Actions (Every 6 hours)
          ↓
┌─────────────────────────────────┐
│     Cloud Run Agents (GCP)       │
│                                  │
│  Academic Research → Google      │
│    Agent (8081)     Trends       │
│                    Agent (8083)  │
│                       ↓          │
│                  Blog Writer     │
│                  Agent (8082)    │
└─────────────────────────────────┘
          ↓
   GitHub Pages Blog
```

### 📚 Documentation

- **Tracking Guide**: [docs/ADK_PIPELINE_TRACKING_GUIDE.md](../docs/ADK_PIPELINE_TRACKING_GUIDE.md) - Complete guide to the tracking system
- **Implementation**: [docs/ADK_A2A_PIPELINE_IMPLEMENTATION.md](../docs/ADK_A2A_PIPELINE_IMPLEMENTATION.md) - Full architecture and design
- **Quick Reference**: [docs/ADK_PIPELINE_QUICK_REF.md](../docs/ADK_PIPELINE_QUICK_REF.md) - Quick commands and tips
- **Helper Script**: [tools/adk-pipeline-status.sh](../tools/adk-pipeline-status.sh) - CLI tool for managing this tracking issue

### 🔄 How It Works

1. **Automatic Discovery**: The workflow searches for issues with label `adk-pipeline`
2. **Auto-Creation**: If no tracking issue exists, the workflow creates one
3. **Run Comments**: After each execution, the workflow posts a comment with results
4. **Historical Record**: All comments remain as a complete history of pipeline runs

### 📅 Schedule

The pipeline runs automatically:
- **00:00 UTC** - First daily run
- **06:00 UTC** - Second daily run
- **12:00 UTC** - Third daily run
- **18:00 UTC** - Fourth daily run

You can also trigger manual runs via workflow_dispatch in GitHub Actions.

### 🎨 A2A Protocol

Each agent implements the A2A protocol specification:
- `/.well-known/agent.json` - Agent discovery endpoint
- `POST /a2a/tasks` - Send messages between agents
- `GET /health` - Health check endpoint

### 🔗 Useful Links

- **Workflow**: [.github/workflows/adk-a2a-blog-pipeline.yml](../.github/workflows/adk-a2a-blog-pipeline.yml)
- **ADK Agents**: [infrastructure/docker/adk-agents/](../infrastructure/docker/adk-agents/)
- **A2A Protocol**: https://a2a-protocol.org/
- **Google ADK Samples**: https://github.com/google/adk-samples

### 💡 Need Help?

- View the [ADK_PIPELINE_TRACKING_GUIDE.md](../docs/ADK_PIPELINE_TRACKING_GUIDE.md) for detailed information
- Run `./tools/adk-pipeline-status.sh help` for available commands
- Check the workflow file for configuration options

---

**Note**: This issue is automatically maintained by the `adk-a2a-blog-pipeline.yml` workflow. Comments are added after each pipeline run. Do not close this issue - it serves as the permanent tracking hub for pipeline history.

**Label**: `adk-pipeline` - Used for automatic discovery by the workflow

---

*🤖 This tracking system was designed by **@create-botter** - Creating infrastructure that illuminates possibilities.*
