#!/bin/bash
# gh-issue-create-wrapper.sh
# Robust wrapper for gh issue create with comprehensive logging and error handling
# 
# This script provides a standardized way to create GitHub issues with:
# - Extensive logging for debugging
# - Permission verification
# - Multiple format support (inline body vs file)
# - Robust error handling
# - Consistent output parsing

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Enable debug mode if DEBUG=1
DEBUG="${DEBUG:-0}"

log_debug() {
    if [ "$DEBUG" = "1" ]; then
        echo -e "${BLUE}[DEBUG]${NC} $*" >&2
    fi
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Robust wrapper for gh issue create with logging and error handling.

OPTIONS:
    --title TITLE           Issue title (required)
    --body BODY             Issue body (inline text)
    --body-file FILE        Issue body (from file)
    --label LABELS          Comma-separated labels
    --assignee USER         Assignee (optional)
    --repo REPO             Repository (org/name format)
    --help                  Show this help message

ENVIRONMENT:
    GH_TOKEN or GITHUB_TOKEN    GitHub token for authentication
    DEBUG=1                     Enable debug logging

EXAMPLES:
    # Inline body
    $0 --title "Bug report" --body "Description here" --label "bug"
    
    # Body from file
    $0 --title "Feature request" --body-file /tmp/body.md --label "enhancement"
    
    # With assignee
    $0 --title "Task" --body "Details" --assignee copilot --label "task"

OUTPUT:
    On success: Prints issue URL to stdout
    On error: Exits with non-zero code and error message to stderr

EOF
    exit 0
}

# Check gh CLI is available
check_gh_cli() {
    log_debug "Checking for gh CLI..."
    if ! command -v gh &> /dev/null; then
        log_error "gh CLI not found. Please install it first."
        exit 1
    fi
    
    local gh_version
    gh_version=$(gh --version 2>&1 | head -1 || echo "unknown")
    log_debug "Found gh CLI: $gh_version"
}

# Check authentication
check_auth() {
    log_debug "Checking GitHub authentication..."
    
    # Check if token is set
    if [ -z "${GH_TOKEN:-}" ] && [ -z "${GITHUB_TOKEN:-}" ]; then
        log_error "No GitHub token found. Set GH_TOKEN or GITHUB_TOKEN environment variable."
        exit 1
    fi
    
    # Try to authenticate
    if ! gh auth status &> /dev/null; then
        log_error "GitHub authentication failed. Token may be invalid."
        local token_var="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
        log_debug "Token length: ${#token_var}"
        exit 1
    fi
    
    log_debug "GitHub authentication successful"
    
    # Get and display user info (helpful for debugging permission issues)
    local user_info
    user_info=$(gh api user --jq '.login' 2>/dev/null || echo "unknown")
    log_debug "Authenticated as: $user_info"
}

# Check permissions for repository
check_permissions() {
    local repo="$1"
    log_debug "Checking permissions for repository: $repo"
    
    # Try to get repo info (requires read access)
    if ! gh repo view "$repo" &> /dev/null; then
        log_error "Cannot access repository: $repo"
        log_error "Check that:"
        log_error "  1. Repository exists"
        log_error "  2. Token has access to the repository"
        log_error "  3. Token has 'repo' or 'public_repo' scope"
        exit 1
    fi
    
    log_debug "Repository access confirmed"
    
    # Check if we can list issues (basic permissions check)
    if gh issue list --repo "$repo" --limit 1 &> /dev/null; then
        log_debug "Issue list permission confirmed"
    else
        log_warn "Cannot list issues - may indicate permission issues"
    fi
}

# Validate body content
validate_body() {
    local body="$1"
    local body_file="$2"
    
    if [ -n "$body" ] && [ -n "$body_file" ]; then
        log_error "Cannot specify both --body and --body-file"
        exit 1
    fi
    
    if [ -z "$body" ] && [ -z "$body_file" ]; then
        log_error "Must specify either --body or --body-file"
        exit 1
    fi
    
    if [ -n "$body_file" ]; then
        if [ ! -f "$body_file" ]; then
            log_error "Body file not found: $body_file"
            exit 1
        fi
        
        local file_size
        file_size=$(wc -c < "$body_file")
        log_debug "Body file size: $file_size bytes"
        
        if [ "$file_size" -eq 0 ]; then
            log_error "Body file is empty: $body_file"
            exit 1
        fi
    else
        local body_length=${#body}
        log_debug "Body length: $body_length characters"
        
        if [ "$body_length" -eq 0 ]; then
            log_error "Body is empty"
            exit 1
        fi
    fi
}

# Create the issue
create_issue() {
    local title="$1"
    local body="$2"
    local body_file="$3"
    local labels="$4"
    local assignee="$5"
    local repo="$6"
    
    log_info "Creating GitHub issue..."
    log_debug "  Title: $title"
    log_debug "  Labels: ${labels:-none}"
    log_debug "  Assignee: ${assignee:-none}"
    log_debug "  Repo: $repo"
    
    # Build gh command
    local cmd=(gh issue create --repo "$repo" --title "$title")
    
    # Add body
    if [ -n "$body_file" ]; then
        cmd+=(--body-file "$body_file")
        log_debug "  Body: from file $body_file"
    else
        cmd+=(--body "$body")
        log_debug "  Body: inline (${#body} chars)"
    fi
    
    # Add optional parameters
    if [ -n "$labels" ]; then
        cmd+=(--label "$labels")
    fi
    
    if [ -n "$assignee" ]; then
        cmd+=(--assignee "$assignee")
        log_debug "  Note: --assignee flag may fail for some tokens (use GraphQL API instead)"
    fi
    
    # Execute with error capture
    log_debug "Executing: ${cmd[*]}"
    
    local output
    local exit_code=0
    
    # Capture both stdout and stderr
    output=$("${cmd[@]}" 2>&1) || exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        log_error "gh issue create failed with exit code $exit_code"
        log_error "Output: $output"
        
        # Provide helpful error messages based on common failure patterns
        if echo "$output" | grep -qi "not found"; then
            log_error "Repository not found or no access"
        elif echo "$output" | grep -qi "permission"; then
            log_error "Permission denied - check token scopes"
        elif echo "$output" | grep -qi "assignee"; then
            log_error "Assignee assignment failed - token may lack permissions"
            log_error "Tip: Remove --assignee and use GraphQL API separately"
        elif echo "$output" | grep -qi "label"; then
            log_error "Label not found - ensure labels exist first"
        fi
        
        exit 1
    fi
    
    # Extract issue URL
    local issue_url
    issue_url=$(echo "$output" | grep -oE 'https://github\.com/[^/]+/[^/]+/issues/[0-9]+' | head -1)
    
    if [ -z "$issue_url" ]; then
        log_error "Could not extract issue URL from output"
        log_error "Output: $output"
        exit 1
    fi
    
    # Extract issue number
    local issue_number
    issue_number=$(echo "$issue_url" | grep -oE '[0-9]+$')
    
    log_info "Successfully created issue #$issue_number"
    log_debug "  URL: $issue_url"
    
    # Output to stdout (for capture by caller)
    echo "$issue_url"
}

# Main function
main() {
    local title=""
    local body=""
    local body_file=""
    local labels=""
    local assignee=""
    local repo="${GITHUB_REPOSITORY:-}"
    
    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --title)
                title="$2"
                shift 2
                ;;
            --body)
                body="$2"
                shift 2
                ;;
            --body-file)
                body_file="$2"
                shift 2
                ;;
            --label)
                labels="$2"
                shift 2
                ;;
            --assignee)
                assignee="$2"
                shift 2
                ;;
            --repo)
                repo="$2"
                shift 2
                ;;
            --help|-h)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done
    
    # Validate required arguments
    if [ -z "$title" ]; then
        log_error "Missing required argument: --title"
        exit 1
    fi
    
    if [ -z "$repo" ]; then
        log_error "Missing repository. Specify --repo or set GITHUB_REPOSITORY"
        exit 1
    fi
    
    # Validate body
    validate_body "$body" "$body_file"
    
    # Run checks
    check_gh_cli
    check_auth
    check_permissions "$repo"
    
    # Create issue
    create_issue "$title" "$body" "$body_file" "$labels" "$assignee" "$repo"
}

# Run main
main "$@"
