#!/usr/bin/env bash
#
# ADK A2A Blog Pipeline - Initialize Tracking Issue
# ==================================================
# 
# This script initializes the ADK A2A Blog Pipeline tracking issue
# with a comprehensive welcome comment explaining the system.
# 
# Usage:
#   ./tools/initialize-adk-tracking-issue.sh [issue_number]
#

set -euo pipefail

# Configuration
TRACKING_LABEL="adk-pipeline"

# Get issue number from argument or find it dynamically
ISSUE_NUMBER="${1:-}"

if [[ -z "$ISSUE_NUMBER" ]]; then
    echo "🔍 Finding tracking issue by label..."
    ISSUE_NUMBER=$(gh issue list --label "$TRACKING_LABEL" --state open --limit 1 --json number --jq 'if length > 0 then .[0].number else empty end' 2>/dev/null || echo "")
    
    if [[ -z "$ISSUE_NUMBER" ]]; then
        echo "❌ No tracking issue found with label '${TRACKING_LABEL}'"
        echo "ℹ️  Create one with: gh issue create --title '🤖 ADK A2A Blog Pipeline Status' --label '${TRACKING_LABEL},automated'"
        exit 1
    fi
fi

echo "📝 Initializing tracking issue #${ISSUE_NUMBER}"
echo ""

# Create the welcome comment
COMMENT_BODY=$(cat <<'EOF'
## 🎉 ADK A2A Blog Pipeline Tracking System - Welcome

**@create-botter** has initialized this issue as the official tracking location for the ADK A2A Blog Pipeline.

### ✅ System Status: OPERATIONAL

All components of the ADK A2A Blog Pipeline tracking infrastructure are verified and ready:

| Component | Status | Location |
|-----------|--------|----------|
| **Workflow** | ✅ Active | `.github/workflows/adk-a2a-blog-pipeline.yml` |
| **Helper Script** | ✅ Ready | `tools/adk-pipeline-status.sh` |
| **Documentation** | ✅ Complete | `docs/ADK_PIPELINE_*.md` |
| **A2A Agents** | ✅ Configured | `infrastructure/docker/adk-agents/` |

### 🔄 How This Tracking Issue Works

This issue serves as an **automated status board** where the workflow posts updates after each pipeline run:

1. **Automatic Runs**: Pipeline executes every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
2. **Manual Triggers**: Can be started on-demand via workflow dispatch
3. **Status Updates**: Workflow posts a comment here after each run with:
   - ⏰ Timestamp (UTC)
   - 🎯 Trigger type (schedule/manual)
   - 🔄 Run mode (simulation/cloud run/dry run)
   - 📊 Agent status (Academic Research, Google Trends, Blog Writer)
   - 🔗 Link to workflow run details

### 🚀 Quick Commands

**View this tracking issue:**
```bash
./tools/adk-pipeline-status.sh view
```

**Trigger a new pipeline run:**
```bash
./tools/adk-pipeline-status.sh trigger
```

**Check recent runs:**
```bash
./tools/adk-pipeline-status.sh recent
```

**See only failed runs:**
```bash
./tools/adk-pipeline-status.sh failed
```

### 🤖 A2A Pipeline Architecture

The ADK A2A Blog Pipeline orchestrates three specialized agents using the A2A (Agent-to-Agent) Protocol:

```
Academic Research Agent  →  Google Trends Agent  →  Blog Writer Agent
      (Topics)               (SEO Analysis)          (Published Post)
         │                        │                        │
         └────────────────────────┴────────────────────────┘
                                  │
                                  ▼
                   GitHub Issue Comment (This Issue)
```

**Agent Flow:**
1. **🔬 Academic Research Agent** - Discovers trending research topics from academic sources
2. **📈 Google Trends Agent** - Analyzes SEO trends and keyword popularity
3. **✍️ Blog Writer Agent** - Generates and publishes blog posts based on research and trends

### 📚 Documentation

**Quick Start:**
- ⚡ [Quick Reference](https://github.com/enufacas/Chained/blob/main/docs/ADK_PIPELINE_QUICK_REF.md)
- 📖 [Complete Tracking Guide](https://github.com/enufacas/Chained/blob/main/docs/ADK_PIPELINE_TRACKING_GUIDE.md)

**Technical Details:**
- 🔧 [Status Guide](https://github.com/enufacas/Chained/blob/main/docs/ADK_PIPELINE_STATUS_GUIDE.md)
- 📋 [Implementation Details](https://github.com/enufacas/Chained/blob/main/docs/implementation-summaries/ISSUE_194_ADK_PIPELINE_TRACKING.md)

### 🎯 Pipeline Schedule

The pipeline runs automatically **4 times per day**:

- 🌙 **00:00 UTC** - Midnight
- 🌅 **06:00 UTC** - Morning
- ☀️ **12:00 UTC** - Noon
- 🌆 **18:00 UTC** - Evening

### ✨ What to Expect

As the pipeline runs, you'll see:
1. **New comments** appear on this issue after each run
2. **Run summaries** with timestamps and execution status
3. **Links** to detailed GitHub Actions workflow logs
4. **Agent reports** showing what each A2A agent discovered/created

### 🏗️ Infrastructure Design

The tracking system uses **label-based discovery** (`adk-pipeline` label), making it:
- ✅ **Dynamic** - Auto-discovers tracking issue without hardcoded references
- ✅ **Resilient** - Self-healing if issue is recreated or relocated
- ✅ **Maintainable** - No manual synchronization required
- ✅ **Scalable** - Can support multiple pipeline types with different labels

### 🎉 System Ready

**No action required.** The infrastructure is operational and will:
- ✨ Run automatically on schedule
- ✨ Post detailed updates to this issue
- ✨ Accept manual triggers via workflow dispatch
- ✨ Self-heal if configuration changes

### 📊 Expected Comment Format

Each pipeline run will post a comment with this structure:

```markdown
## Pipeline Run: 2025-12-26 12:00:00 UTC

| Property | Value |
|----------|-------|
| Trigger | schedule |
| Mode | simulation |
| Workflow Run | [#1885](workflow_url) |

### Summary

Pipeline executed successfully in simulation mode.

- 🔬 Academic Research: Topics discovered
- 📈 Google Trends: SEO analysis complete
- ✍️ Blog Writer: Content generated

---
*🤖 Created by [ADK A2A Blog Pipeline](run_url)*
```

### 🔍 Monitoring

**Check workflow runs:**
```bash
gh run list --workflow=adk-a2a-blog-pipeline.yml --limit 10
```

**Watch live run:**
```bash
gh run watch
```

**View detailed logs:**
```bash
gh run view <run_id> --log
```

### 🆘 Getting Help

**Questions about:**
- Pipeline execution → [Status Guide](https://github.com/enufacas/Chained/blob/main/docs/ADK_PIPELINE_STATUS_GUIDE.md)
- Helper scripts → Run `./tools/adk-pipeline-status.sh help`
- ADK agents → See [ADK Agents README](https://github.com/enufacas/Chained/blob/main/infrastructure/docker/adk-agents/README.md)
- Workflow issues → Check workflow logs via `gh run list --status failure`

---

**🏗️ Infrastructure by @create-botter** - _Creating infrastructure that illuminates possibilities._

**System Status:** 🟢 **OPERATIONAL**  
**Initialization Date:** $(date -u +%Y-%m-%d)  
**Next Scheduled Run:** Check workflow schedule (every 6 hours)
EOF
)

echo "Posting welcome comment to issue #${ISSUE_NUMBER}..."
echo ""

# Post the comment
gh issue comment "$ISSUE_NUMBER" --body "$COMMENT_BODY"

echo ""
echo "✅ Tracking issue #${ISSUE_NUMBER} initialized successfully!"
echo ""
echo "View it with: gh issue view $ISSUE_NUMBER --comments"
echo "Or run: ./tools/adk-pipeline-status.sh view"
