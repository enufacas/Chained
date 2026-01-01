#!/usr/bin/env bash
#
# Post welcome comment to the ADK A2A Blog Pipeline tracking issue
# This script is designed to work in GitHub Actions environment
#

set -euo pipefail

# Check for required environment variables
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "❌ Error: GITHUB_TOKEN not set"
    exit 1
fi

if [[ -z "${GITHUB_REPOSITORY:-}" ]]; then
    echo "❌ Error: GITHUB_REPOSITORY not set"
    exit 1
fi

# Get issue number from command line or environment
ISSUE_NUMBER="${1:-${ISSUE_NUMBER:-}}"

if [[ -z "$ISSUE_NUMBER" ]]; then
    echo "❌ Error: Issue number not provided"
    echo "Usage: $0 <issue_number>"
    echo "Or set ISSUE_NUMBER environment variable"
    exit 1
fi

echo "🤖 ADK A2A Blog Pipeline - Welcome Comment Poster"
echo "=================================================="
echo ""
echo "Repository: $GITHUB_REPOSITORY"
echo "Issue: #$ISSUE_NUMBER"
echo ""

# Read the welcome comment template
WELCOME_FILE="docs/issue-comments/ADK_PIPELINE_TRACKING_WELCOME.md"

if [[ ! -f "$WELCOME_FILE" ]]; then
    echo "❌ Error: Welcome comment file not found: $WELCOME_FILE"
    exit 1
fi

echo "📝 Reading welcome comment from: $WELCOME_FILE"

# Read the comment body and update the date
INIT_DATE=$(date -u +%Y-%m-%d)
COMMENT_BODY=$(cat "$WELCOME_FILE" | sed "s/2025-12-26/$INIT_DATE/g")

# Create JSON payload
JSON_PAYLOAD=$(jq -n --arg body "$COMMENT_BODY" '{body: $body}')

echo "📤 Posting welcome comment to issue #$ISSUE_NUMBER..."
echo ""

# Post comment using GitHub API
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    -H "Content-Type: application/json" \
    "https://api.github.com/repos/${GITHUB_REPOSITORY}/issues/${ISSUE_NUMBER}/comments" \
    -d "$JSON_PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n -1)

# Check response
if [[ "$HTTP_CODE" =~ ^(200|201)$ ]]; then
    echo "✅ Welcome comment posted successfully!"
    echo ""
    
    # Extract comment URL
    COMMENT_URL=$(echo "$BODY" | jq -r '.html_url // empty')
    if [[ -n "$COMMENT_URL" ]]; then
        echo "🔗 Comment URL: $COMMENT_URL"
    fi
    
    echo ""
    echo "🎉 ADK A2A Blog Pipeline tracking issue initialized!"
    echo ""
    echo "The tracking system is now operational and ready to receive pipeline updates."
    exit 0
else
    echo "❌ Failed to post comment (HTTP $HTTP_CODE)"
    echo ""
    echo "Response:"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
    exit 1
fi
