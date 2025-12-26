# ADK A2A Blog Pipeline - Quick Reference

**@create-botter** - Quick commands and tips for the ADK A2A Blog Pipeline.

## 🚀 Quick Start

### View Tracking Issue

```bash
# Find and view tracking issue
gh issue list --label "adk-pipeline" --state open

# Using helper script (recommended)
./tools/adk-pipeline-status.sh view
```

### Trigger Pipeline

```bash
# Default run
gh workflow run adk-a2a-blog-pipeline.yml

# Interactive trigger
./tools/adk-pipeline-status.sh trigger
```

### Check Status

```bash
# Recent runs
./tools/adk-pipeline-status.sh recent

# Failed runs
./tools/adk-pipeline-status.sh failed

# Agent health
./tools/adk-pipeline-status.sh health
```

### Initialize Tracking Issue

```bash
# Post welcome comment (recommended)
./tools/post-adk-tracking-welcome.sh

# Or specify issue number
./tools/post-adk-tracking-welcome.sh 4069

# Legacy initialization
./tools/initialize-adk-tracking-issue.sh
```

## 📊 Tracking Issue

**Title:** 🤖 ADK A2A Blog Pipeline Status

- **Label:** `adk-pipeline` (use this to find the current tracking issue)
- **Purpose:** Centralized history of all pipeline runs
- **Updated:** Automatically after each run

**Find current tracking issue:**
```bash
gh issue list --label "adk-pipeline" --state open
```

## 🔗 Key Resources

| Resource | Location |
|----------|----------|
| **Tracking Issue** | Search for label: `adk-pipeline` |
| **Workflow** | `.github/workflows/adk-a2a-blog-pipeline.yml` |
| **Documentation** | `docs/ADK_PIPELINE_TRACKING_GUIDE.md` |
| **Welcome Script** ✨ | `tools/post-adk-tracking-welcome.sh` |
| **Helper Script** | `tools/adk-pipeline-status.sh` |
| **Agents** | `infrastructure/docker/adk-agents/` |

## ⏰ Schedule

Runs every **6 hours**: 00:00, 06:00, 12:00, 18:00 UTC

## 🤖 Agents

1. **Academic Research** (Port 8081) - Discovers topics
2. **Google Trends** (Port 8083) - Analyzes SEO
3. **Blog Writer** (Port 8082) - Writes & publishes

## 💡 Common Commands

### Workflow Management

```bash
# List recent runs
gh run list --workflow=adk-a2a-blog-pipeline.yml --limit 5

# Watch current run
gh run watch

# View run details
gh run view <RUN_ID>

# View run logs
gh run view <RUN_ID> --log
```

### Issue Management

```bash
# Find tracking issue
gh issue list --label "adk-pipeline" --state open

# View with comments
ISSUE_NUMBER=$(gh issue list --label "adk-pipeline" --state open --limit 1 --json number --jq '.[0].number')
gh issue view "$ISSUE_NUMBER" --comments

# Subscribe to updates
ISSUE_NUMBER=$(gh issue list --label "adk-pipeline" --state open --limit 1 --json number --jq '.[0].number')
gh issue view "$ISSUE_NUMBER" --web
```

### Manual Triggers

```bash
# Basic trigger
gh workflow run adk-a2a-blog-pipeline.yml

# With custom topic
gh workflow run adk-a2a-blog-pipeline.yml -f topic_query="AI agents"

# Dry run (no deployment)
gh workflow run adk-a2a-blog-pipeline.yml -f dry_run=true

# Debug mode
gh workflow run adk-a2a-blog-pipeline.yml -f debug=true
```

### Agent Health (requires gcloud)

```bash
# Check health endpoints
curl https://chained-academic-research-<project>.run.app/health
curl https://chained-google-trends-<project>.run.app/health
curl https://chained-blog-writer-<project>.run.app/health

# View logs
gcloud run services logs read chained-academic-research --region=us-central1

# Get service URLs
gcloud run services describe chained-academic-research \
  --region=us-central1 --format='value(status.url)'
```

## 🔧 Troubleshooting

### Issue not updating?

1. Check workflow runs: `gh run list --workflow=adk-a2a-blog-pipeline.yml`
2. View recent logs: `gh run view <RUN_ID> --log`
3. Find and verify tracking issue:
   ```bash
   ISSUE_NUMBER=$(gh issue list --label "adk-pipeline" --state open --limit 1 --json number --jq '.[0].number')
   gh issue view "$ISSUE_NUMBER" --json labels
   ```

### Pipeline failing?

1. Check failed runs: `./tools/adk-pipeline-status.sh failed`
2. View failure logs: `gh run view <RUN_ID> --log-failed`
3. Check agent health: `./tools/adk-pipeline-status.sh health`

### Need help?

- **Full Guide:** `docs/ADK_PIPELINE_TRACKING_GUIDE.md`
- **Implementation:** `docs/ADK_A2A_PIPELINE_IMPLEMENTATION.md`
- **Helper Script:** `./tools/adk-pipeline-status.sh help`

---

**Created by @create-botter** - Quick reference for pipeline tracking.

*For detailed documentation, see: [ADK_PIPELINE_TRACKING_GUIDE.md](./ADK_PIPELINE_TRACKING_GUIDE.md)*
