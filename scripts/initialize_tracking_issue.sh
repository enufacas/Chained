#!/usr/bin/env bash
#
# Initialize ADK A2A Blog Pipeline Tracking Issue
# ===============================================
# 
# This script posts the welcome comment to the tracking issue.
# It's designed to run in GitHub Actions with GITHUB_TOKEN.
#

set -euo pipefail

echo "🔄 Initializing ADK A2A Blog Pipeline Tracking Issue"
echo "===================================================="
echo ""

# Check if we have GitHub token
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "❌ Error: GITHUB_TOKEN not set"
    echo "   This script must run with GitHub token access"
    exit 1
fi

# Export for gh CLI
export GH_TOKEN="${GITHUB_TOKEN}"

# Configuration
TRACKING_LABEL="adk-pipeline"
WELCOME_FILE="docs/issue-comments/ADK_PIPELINE_TRACKING_WELCOME.md"

echo "📋 Configuration:"
echo "   Label: ${TRACKING_LABEL}"
echo "   Welcome file: ${WELCOME_FILE}"
echo ""

# Find or create tracking issue
echo "🔍 Searching for tracking issue..."
ISSUE_NUMBER=$(gh issue list --label "${TRACKING_LABEL}" --state open --limit 1 --json number --jq 'if length > 0 then .[0].number else empty end' 2>/dev/null || echo "")

if [[ -z "$ISSUE_NUMBER" ]]; then
    echo "📝 No tracking issue found, creating one..."
    
    # Create new tracking issue
    ISSUE_URL=$(gh issue create \
        --title "🤖 ADK A2A Blog Pipeline Status" \
        --label "${TRACKING_LABEL},automated" \
        --body "Tracking issue for ADK A2A blog pipeline runs. See comments for run history." 2>&1)
    
    if [[ $? -eq 0 ]]; then
        # Extract issue number from URL
        ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -o '[0-9]*$')
        echo "✅ Created tracking issue #${ISSUE_NUMBER}"
    else
        echo "❌ Failed to create tracking issue"
        echo "   Error: $ISSUE_URL"
        exit 1
    fi
else
    echo "✅ Found existing tracking issue #${ISSUE_NUMBER}"
fi

echo ""
echo "📝 Checking if welcome comment already exists..."

# Check if welcome comment already posted
WELCOME_MARKER="ADK A2A Blog Pipeline Tracking System - Initialized"
HAS_WELCOME=$(gh issue view "$ISSUE_NUMBER" --json comments --jq '.comments[].body' | grep -c "$WELCOME_MARKER" || echo "0")

if [[ "$HAS_WELCOME" -gt 0 ]]; then
    echo "ℹ️  Welcome comment already exists, skipping..."
    echo ""
    echo "✅ Tracking issue #${ISSUE_NUMBER} already initialized"
    echo ""
    echo "View it: gh issue view $ISSUE_NUMBER --comments"
    exit 0
fi

echo "📤 Posting welcome comment..."

# Read welcome comment
if [[ ! -f "$WELCOME_FILE" ]]; then
    echo "❌ Error: Welcome comment file not found: $WELCOME_FILE"
    exit 1
fi

WELCOME_CONTENT=$(cat "$WELCOME_FILE")

# Update initialization date in welcome comment
INIT_DATE=$(date -u +%Y-%m-%d)
WELCOME_CONTENT="${WELCOME_CONTENT//2025-12-26/$INIT_DATE}"

# Post welcome comment
if gh issue comment "$ISSUE_NUMBER" --body "$WELCOME_CONTENT"; then
    echo "✅ Welcome comment posted successfully!"
else
    echo "❌ Failed to post welcome comment"
    exit 1
fi

echo ""
echo "=" 
echo "🎉 ADK A2A Blog Pipeline Tracking Issue Initialized!"
echo "="
echo ""
echo "📊 Summary:"
echo "   Issue: #${ISSUE_NUMBER}"
echo "   Label: ${TRACKING_LABEL}"
echo "   Status: Initialized and operational"
echo ""
echo "🚀 Next Steps:"
echo "   - Pipeline will post updates automatically (every 6 hours)"
echo "   - View issue: gh issue view $ISSUE_NUMBER --comments"
echo "   - Check status: ./tools/adk-pipeline-status.sh view"
echo "   - Monitor health: python3 tools/adk-pipeline-dashboard.py health"
echo ""
echo "📚 Documentation:"
echo "   - Quick Ref: docs/ADK_PIPELINE_QUICK_REF.md"
echo "   - Full Guide: docs/ADK_PIPELINE_TRACKING_GUIDE.md"
echo ""
