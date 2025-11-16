#!/bin/bash
# Mission Completion Script for idea:15
# Agent: @investigate-champion
# Issue: #1164

set -e

ISSUE_NUMBER=1164
COMMENT_FILE="/tmp/issue_comment.md"

echo "🎯 Mission Completion: Cloud DevOps Innovation (idea:15)"
echo "=================================================="
echo ""
echo "Agent: @investigate-champion (Liskov)"
echo "Issue: #${ISSUE_NUMBER}"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) not found"
    echo "Please install: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI"
    echo "Please run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Post completion comment
echo "📝 Posting mission completion comment to issue #${ISSUE_NUMBER}..."
if gh issue comment "${ISSUE_NUMBER}" --body-file "${COMMENT_FILE}"; then
    echo "✅ Comment posted successfully"
else
    echo "❌ Failed to post comment"
    exit 1
fi

echo ""

# Add completed label
echo "🏷️  Adding 'completed' label..."
if gh issue edit "${ISSUE_NUMBER}" --add-label "completed"; then
    echo "✅ Label added"
else
    echo "⚠️  Warning: Could not add label"
fi

echo ""

# Close the issue
echo "🔒 Closing issue #${ISSUE_NUMBER}..."
if gh issue close "${ISSUE_NUMBER}" --reason "completed" --comment "Mission completed by **@investigate-champion** (Liskov). All deliverables verified and documented."; then
    echo "✅ Issue closed successfully"
else
    echo "❌ Failed to close issue"
    exit 1
fi

echo ""
echo "🎉 Mission completion workflow finished!"
echo ""
echo "Summary:"
echo "--------"
echo "✅ Comment posted with comprehensive mission summary"
echo "✅ Issue #${ISSUE_NUMBER} closed with 'completed' status"
echo "✅ Agent attribution: @investigate-champion (Liskov)"
echo ""
echo "Deliverables:"
echo "-------------"
echo "1. Investigation Report: learnings/cloud_devops_innovation_investigation_20251116.md"
echo "2. Completion Summary: learnings/mission_completion_idea15_20251116.md"
echo "3. Analyzer Tool: tools/cloud_devops_analyzer.py"
echo "4. Investigation Summary: investigation-reports/cloud-devops-innovation-idea-15.md"
echo ""
echo "Mission: idea:15 - Cloud DevOps Innovation"
echo "Status: ✅ COMPLETED"
