#!/usr/bin/env bash
#
# Post welcome comment to Issue #194 (ADK A2A Blog Pipeline Status)
# ==================================================================
#
# This script posts the welcome/onboarding comment to the tracking issue.
# It's designed to be run once to initialize the tracking issue with
# comprehensive information about the pipeline.
#
# Usage:
#   GH_TOKEN=<token> ./tools/post-issue-194-welcome.sh
#
# Requirements:
#   - GitHub CLI (gh) installed and authenticated
#   - GH_TOKEN environment variable set
#   - Issue #194 must exist with label "adk-pipeline"
#

set -euo pipefail

# Configuration
TRACKING_LABEL="adk-pipeline"
WELCOME_COMMENT_FILE="docs/issue-comments/ISSUE_194_WELCOME_COMMENT.md"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Check prerequisites
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

if [[ -z "${GH_TOKEN:-}" ]]; then
    print_error "GH_TOKEN environment variable not set"
    echo "Set it with: export GH_TOKEN=\$(gh auth token)"
    exit 1
fi

if [[ ! -f "$WELCOME_COMMENT_FILE" ]]; then
    print_error "Welcome comment file not found: $WELCOME_COMMENT_FILE"
    exit 1
fi

# Find tracking issue
print_info "Finding tracking issue with label: $TRACKING_LABEL"
ISSUE_NUMBER=$(gh issue list --label "$TRACKING_LABEL" --state open --limit 1 --json number --jq 'if length > 0 then .[0].number else empty end' 2>/dev/null || echo "")

if [[ -z "$ISSUE_NUMBER" ]]; then
    print_error "No tracking issue found with label '$TRACKING_LABEL'"
    echo ""
    print_info "The tracking issue should be created automatically by the pipeline workflow."
    print_info "Or create it manually with:"
    echo "  gh issue create --title '🤖 ADK A2A Blog Pipeline Status' --label '${TRACKING_LABEL},automated'"
    exit 1
fi

print_success "Found tracking issue: #$ISSUE_NUMBER"
echo ""

# Ask for confirmation
print_warning "This will post a welcome comment to issue #$ISSUE_NUMBER"
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Aborted by user"
    exit 0
fi

# Post the comment
print_info "Posting welcome comment to issue #$ISSUE_NUMBER..."

if gh issue comment "$ISSUE_NUMBER" --body-file "$WELCOME_COMMENT_FILE"; then
    print_success "Welcome comment posted successfully!"
    echo ""
    print_info "View the issue: gh issue view $ISSUE_NUMBER --web"
else
    print_error "Failed to post welcome comment"
    exit 1
fi
