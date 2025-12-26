#!/usr/bin/env bash
#
# ADK A2A Blog Pipeline - Post Welcome Comment to Tracking Issue
# ==============================================================
# 
# This script posts the comprehensive welcome comment to the ADK tracking issue.
# It can be run manually or as part of a workflow to initialize new tracking issues.
#
# Usage:
#   ./tools/post-adk-tracking-welcome.sh [issue_number]
#
# If issue_number is not provided, the script will search for the tracking issue
# using the 'adk-pipeline' label.
#

set -euo pipefail

# Configuration
TRACKING_LABEL="adk-pipeline"
WELCOME_COMMENT_FILE="docs/issue-comments/ADK_PIPELINE_TRACKING_WELCOME.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if gh CLI is available or if we can use the API
check_github_access() {
    if command -v gh &> /dev/null; then
        return 0
    elif [[ -n "${GITHUB_TOKEN:-}" || -n "${GH_TOKEN:-}" ]]; then
        return 0
    else
        print_error "Neither gh CLI nor GITHUB_TOKEN/GH_TOKEN is available"
        print_info "Install gh CLI from: https://cli.github.com/"
        print_info "Or set GITHUB_TOKEN environment variable"
        return 1
    fi
}

# Get issue number from argument or search by label
get_issue_number() {
    local issue_arg="${1:-}"
    
    if [[ -n "$issue_arg" ]]; then
        echo "$issue_arg"
        return 0
    fi
    
    print_info "Searching for tracking issue with label '${TRACKING_LABEL}'..."
    
    # Use gh CLI if available, otherwise use API directly
    if command -v gh &> /dev/null; then
        local issue_num=$(gh issue list \
            --label "$TRACKING_LABEL" \
            --state open \
            --limit 1 \
            --json number \
            --jq 'if length > 0 then .[0].number else empty end' 2>/dev/null || echo "")
    else
        # Use GitHub API directly
        local token="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
        local repo="${GITHUB_REPOSITORY:-enufacas/Chained}"
        
        local issue_num=$(curl -s \
            -H "Authorization: token $token" \
            -H "Accept: application/vnd.github+json" \
            "https://api.github.com/repos/${repo}/issues?labels=${TRACKING_LABEL}&state=open&per_page=1" \
            | jq -r 'if length > 0 then .[0].number else empty end' 2>/dev/null || echo "")
    fi
    
    if [[ -z "$issue_num" ]]; then
        print_error "No tracking issue found with label '${TRACKING_LABEL}'"
        print_info "Create one with: gh issue create --title '🤖 ADK A2A Blog Pipeline Status' --label '${TRACKING_LABEL},automated'"
        return 1
    fi
    
    echo "$issue_num"
    return 0
}

# Post welcome comment to issue
post_welcome_comment() {
    local issue_number="$1"
    
    if [[ ! -f "$WELCOME_COMMENT_FILE" ]]; then
        print_error "Welcome comment file not found: $WELCOME_COMMENT_FILE"
        return 1
    fi
    
    print_info "Reading welcome comment from: $WELCOME_COMMENT_FILE"
    local comment_body=$(cat "$WELCOME_COMMENT_FILE")
    
    print_info "Posting welcome comment to issue #${issue_number}..."
    
    # Use gh CLI if available, otherwise use API directly
    if command -v gh &> /dev/null; then
        gh issue comment "$issue_number" --body "$comment_body"
    else
        # Use GitHub API directly
        local token="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
        local repo="${GITHUB_REPOSITORY:-enufacas/Chained}"
        
        # Create JSON payload (properly escaping the markdown)
        local json_payload=$(jq -n --arg body "$comment_body" '{body: $body}')
        
        local response=$(curl -s -w "\n%{http_code}" \
            -X POST \
            -H "Authorization: token $token" \
            -H "Accept: application/vnd.github+json" \
            -H "Content-Type: application/json" \
            "https://api.github.com/repos/${repo}/issues/${issue_number}/comments" \
            -d "$json_payload")
        
        local http_code=$(echo "$response" | tail -n1)
        
        if [[ "$http_code" =~ ^20 ]]; then
            print_success "Comment posted successfully (HTTP $http_code)"
        else
            print_error "Failed to post comment (HTTP $http_code)"
            echo "$response" | head -n -1
            return 1
        fi
    fi
    
    return 0
}

# Main script
main() {
    echo "================================="
    echo "ADK Pipeline Tracking - Welcome"
    echo "================================="
    echo ""
    
    # Check GitHub access
    if ! check_github_access; then
        exit 1
    fi
    
    # Get issue number
    local issue_number
    if ! issue_number=$(get_issue_number "${1:-}"); then
        exit 1
    fi
    
    print_info "Tracking issue: #${issue_number}"
    echo ""
    
    # Post welcome comment
    if post_welcome_comment "$issue_number"; then
        echo ""
        print_success "Welcome comment posted successfully!"
        echo ""
        print_info "View the issue:"
        echo "  gh issue view $issue_number --comments"
        echo "  ./tools/adk-pipeline-status.sh view"
        echo ""
        print_info "The tracking system is now fully initialized and operational."
    else
        exit 1
    fi
}

# Run main function
main "$@"
