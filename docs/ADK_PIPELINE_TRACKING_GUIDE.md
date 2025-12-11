# ADK A2A Blog Pipeline - Tracking Issue Guide

**@create-botter** - Infrastructure documentation for the ADK A2A Blog Pipeline tracking system.

## 🎯 Overview

This guide explains how the ADK A2A Blog Pipeline tracking system works and how to use it effectively.

## 📍 Tracking Issue Location

**Title:** 🤖 ADK A2A Blog Pipeline Status  
**Label:** `adk-pipeline`

The tracking issue serves as a centralized history of all ADK A2A Blog Pipeline executions. The workflow automatically creates and maintains this issue.

### Finding the Tracking Issue

```bash
# Method 1: Search by label (recommended - always current)
gh issue list --label "adk-pipeline" --state open

# Method 2: Search by title
gh issue list --search "ADK A2A Blog Pipeline Status" --state open

# Method 3: Using the helper script
./tools/adk-pipeline-status.sh view
```

> **Note:** The issue number may change if tracking issues are closed and recreated. Always search by label to find the current tracking issue.

## 🔄 How the Tracking System Works

### Automatic Issue Management

The workflow (`.github/workflows/adk-a2a-blog-pipeline.yml`) automatically:

1. **Searches for the tracking issue** using the `adk-pipeline` label
2. **Creates the issue** if it doesn't exist (with labels: `adk-pipeline`, `automated`)
3. **Posts a comment** after each pipeline run with detailed results

### What Gets Tracked

Each pipeline run posts a comment containing:

| Information | Details |
|------------|---------|
| **Timestamp** | UTC timestamp of the run |
| **Trigger** | How the workflow was triggered (`schedule`, `workflow_dispatch`) |
| **Mode** | Execution mode (`simulation`, `cloud run`, `dry_run`, `manual`) |
| **Workflow Run** | Direct link to GitHub Actions run |
| **Agent Status** | Status of each A2A agent (Academic Research, Google Trends, Blog Writer) |
| **Summary** | Overall pipeline execution result |

### Pipeline Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Actions Workflow                       │
│                (adk-a2a-blog-pipeline.yml)                       │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ├─► Preflight Checks
                            │
                            ├─► Run Pipeline (Simulation or Cloud Run)
                            │   │
                            │   ├─► Academic Research Agent
                            │   │   (Discover topics)
                            │   │
                            │   ├─► Google Trends Agent
                            │   │   (Analyze SEO trends)
                            │   │
                            │   └─► Blog Writer Agent
                            │       (Generate & publish blog)
                            │
                            └─► Report Results
                                └─► Post comment to tracking issue
```

## 📅 Pipeline Schedule

The pipeline runs automatically on a schedule:

- **00:00 UTC** - Midnight run
- **06:00 UTC** - Morning run
- **12:00 UTC** - Noon run
- **18:00 UTC** - Evening run

**Frequency:** Every 6 hours, 4 times per day

## 🚀 Manual Pipeline Execution

You can manually trigger the pipeline with custom parameters:

### Basic Run

```bash
# Auto-discover topics and run full pipeline
gh workflow run adk-a2a-blog-pipeline.yml
```

### Custom Topic

```bash
# Research a specific topic
gh workflow run adk-a2a-blog-pipeline.yml \
  -f topic_query="Agentic AI frameworks"
```

### Dry Run Mode

```bash
# Run without deploying (testing)
gh workflow run adk-a2a-blog-pipeline.yml \
  -f dry_run=true
```

### Debug Mode

```bash
# Enable detailed logging
gh workflow run adk-a2a-blog-pipeline.yml \
  -f debug=true
```

### Combined Parameters

```bash
# Custom topic + debug mode
gh workflow run adk-a2a-blog-pipeline.yml \
  -f topic_query="Multi-agent systems" \
  -f debug=true
```

## 📊 Viewing Run History

### View All Comments on Tracking Issue

```bash
# Find and view the tracking issue with all comments
ISSUE_NUMBER=$(gh issue list --label "adk-pipeline" --state open --limit 1 --json number --jq '.[0].number')
gh issue view "$ISSUE_NUMBER" --comments

# Or use the helper script
./tools/adk-pipeline-status.sh view
```

### View Recent Workflow Runs

```bash
# List recent pipeline executions
gh run list --workflow=adk-a2a-blog-pipeline.yml --limit 10

# View specific run details
gh run view <RUN_ID>

# View run logs
gh run view <RUN_ID> --log
```

### Filter by Status

```bash
# Only successful runs
gh run list --workflow=adk-a2a-blog-pipeline.yml --status success

# Only failed runs
gh run list --workflow=adk-a2a-blog-pipeline.yml --status failure
```

## 🔍 Pipeline Agents

### Academic Research Agent

**Purpose:** Discovers and analyzes research topics

**Skills:**
- `discover-topics` - Find trending research areas
- `analyze-topic` - Deep dive into specific topic

**Endpoint:** `/a2a/tasks`

### Google Trends Agent

**Purpose:** Analyzes search trends for SEO optimization

**Skills:**
- `analyze-trends` - Get trend data for topics
- `get-keywords` - Extract SEO keywords

**Endpoint:** `/a2a/tasks`

### Blog Writer Agent

**Purpose:** Generates and publishes blog content

**Skills:**
- `write-blog` - Create blog post from research
- `deploy-blog` - Publish to GitHub Pages

**Endpoint:** `/a2a/tasks`

## 🏗️ Infrastructure

### Agent Deployment

Agents are deployed to GCP Cloud Run:

```bash
# Deploy all agents
gh workflow run deploy-adk-agents.yml

# Check agent health
curl https://chained-academic-research-<project>.run.app/health
curl https://chained-google-trends-<project>.run.app/health
curl https://chained-blog-writer-<project>.run.app/health
```

### Agent Discovery

Each agent publishes an A2A agent card:

```bash
# Get agent capabilities
curl https://<agent-url>/.well-known/agent.json
```

### Local Testing

Run agents locally for development:

```bash
cd infrastructure/docker/adk-agents

# Start agents
python academic-research/agent.py &  # Port 8081
python google-trends/agent.py &      # Port 8083
python blog-writer/agent.py &        # Port 8082

# Test orchestrator
python orchestrator.py "AI safety"
```

## 📝 Workflow Configuration

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `GCP_PROJECT_ID` | Google Cloud project ID | Required for Cloud Run |
| `GCP_REGION` | Cloud Run region | `us-central1` |
| `ACADEMIC_RESEARCH_URL` | Research agent endpoint | Auto-discovered |
| `BLOG_WRITER_URL` | Blog writer endpoint | Auto-discovered |
| `GOOGLE_TRENDS_URL` | Trends agent endpoint | Auto-discovered |

### GitHub Secrets

Required secrets for Cloud Run deployment:

- `GCP_PROJECT_ID` - GCP project identifier
- `GCP_SA_KEY` - Service account JSON key
- `GCP_REGION` - Deployment region (optional)

## 🔧 Troubleshooting

### Tracking Issue Not Updated

**Symptom:** No new comments appearing on tracking issue

**Causes:**
1. Workflow authentication failure
2. Issue label missing
3. Network connectivity issues

**Solutions:**
```bash
# Find tracking issue
ISSUE_NUMBER=$(gh issue list --label "adk-pipeline" --state open --limit 1 --json number --jq '.[0].number')

# Verify issue has correct label
gh issue view "$ISSUE_NUMBER" --json labels

# Check recent workflow runs
gh run list --workflow=adk-a2a-blog-pipeline.yml --limit 5

# View workflow logs
gh run view <RUN_ID> --log | grep "tracking issue"
```

### Pipeline Failures

**Check workflow status:**
```bash
# View failed runs
gh run list --workflow=adk-a2a-blog-pipeline.yml --status failure

# View specific failure
gh run view <RUN_ID> --log-failed
```

**Common issues:**
- Agent not deployed or unhealthy
- Authentication failure
- Network timeout
- Missing environment variables

### Agent Health Issues

**Check agent status:**
```bash
# Health check
curl https://<agent-url>/health

# View logs
gcloud run services logs read chained-academic-research --region=us-central1
```

## 📚 Documentation References

- **Implementation:** [`docs/ADK_A2A_PIPELINE_IMPLEMENTATION.md`](./ADK_A2A_PIPELINE_IMPLEMENTATION.md)
- **Workflow:** [`.github/workflows/adk-a2a-blog-pipeline.yml`](../.github/workflows/adk-a2a-blog-pipeline.yml)
- **Agents:** [`infrastructure/docker/adk-agents/`](../infrastructure/docker/adk-agents/)
- **Tracking Fix:** [`docs/implementation-summaries/ADK_PIPELINE_TRACKING_ISSUE_FIX.md`](./implementation-summaries/ADK_PIPELINE_TRACKING_ISSUE_FIX.md)

## 🎯 Best Practices

### For Pipeline Monitoring

1. **Subscribe to the tracking issue** to get notified of all runs
2. **Review comments regularly** to spot patterns or failures
3. **Check workflow runs** for detailed execution logs
4. **Monitor agent health** in Cloud Run console

### For Manual Triggers

1. **Use dry run mode** for testing changes
2. **Enable debug logging** when troubleshooting
3. **Specify topics** for focused content generation
4. **Check agent health** before triggering

### For Development

1. **Test locally first** using simulated agents
2. **Review orchestrator logs** for A2A communication
3. **Verify agent cards** are correctly published
4. **Check blog output** before deploying to production

## 🚀 Future Enhancements

Potential improvements for the tracking system:

1. **Dashboard Integration** - Display tracking issue data on GitHub Pages
2. **Metrics Collection** - Aggregate pipeline success rates over time
3. **Alert Integration** - Notify on pipeline failures via issue mentions
4. **Trend Analysis** - Track pipeline duration trends
5. **Status Badge** - Add badge to README showing last pipeline status

---

**Created by @create-botter** - Infrastructure that illuminates possibilities.

*Last updated: 2025-12-10*
