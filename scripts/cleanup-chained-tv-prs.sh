#!/bin/bash
# Chained TV PR Cleanup Script
# This script adds the copilot label to existing Chained TV PRs and closes stale ones
# Run this manually with: GH_TOKEN=<your_token> bash scripts/cleanup-chained-tv-prs.sh

set -e

echo "🧹 Chained TV PR Cleanup"
echo "========================"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

# Get all open Chained TV PRs
echo "📋 Fetching open Chained TV PRs..."
PR_NUMBERS=$(gh pr list --label chained-tv --state open --json number --jq '.[].number')

if [ -z "$PR_NUMBERS" ]; then
    echo "✅ No open Chained TV PRs found"
    exit 0
fi

echo "Found PRs: $PR_NUMBERS"
echo ""

# Process each PR
for PR_NUM in $PR_NUMBERS; do
    echo "Processing PR #$PR_NUM..."
    
    # Check if PR already has copilot label
    HAS_COPILOT=$(gh pr view $PR_NUM --json labels --jq '.labels[] | select(.name == "copilot") | .name' || true)
    
    if [ -z "$HAS_COPILOT" ]; then
        echo "  ➕ Adding copilot label to PR #$PR_NUM"
        gh pr edit $PR_NUM --add-label "copilot" || echo "  ⚠️  Failed to add label"
    else
        echo "  ✅ PR #$PR_NUM already has copilot label"
    fi
    
    # Check PR age
    CREATED_AT=$(gh pr view $PR_NUM --json createdAt --jq '.createdAt')
    CREATED_TIMESTAMP=$(date -d "$CREATED_AT" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$CREATED_AT" +%s 2>/dev/null || echo "0")
    NOW_TIMESTAMP=$(date +%s)
    AGE_HOURS=$(( (NOW_TIMESTAMP - CREATED_TIMESTAMP) / 3600 ))
    
    echo "  📅 PR age: $AGE_HOURS hours"
    
    # If PR is older than 24 hours and hasn't been merged, close it
    if [ "$AGE_HOURS" -gt 24 ]; then
        echo "  🗑️  PR is stale (>24 hours old), closing..."
        gh pr close $PR_NUM --comment "🧹 **Automated Cleanup**

This Chained TV PR is being closed as it's more than 24 hours old and was created before the auto-merge fix.

**Why this happened:**
- This PR was missing the \`copilot\` label required for auto-merge
- The workflow has been fixed to add the label for future PRs
- Newer episodes will now merge automatically

**What's next:**
- Newer Chained TV episodes will merge automatically
- You can view all episodes at: https://enufacas.github.io/Chained/episodes.html

---
*Automated cleanup by @engineer-master*" || echo "  ⚠️  Failed to close PR"
    else
        echo "  ⏳ PR is recent, leaving open for auto-merge system"
    fi
    
    echo ""
done

echo "========================"
echo "✅ Cleanup complete!"
echo ""
echo "📺 View all episodes at: https://enufacas.github.io/Chained/episodes.html"
