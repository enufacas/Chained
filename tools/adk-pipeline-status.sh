#!/usr/bin/env bash
#
# ADK A2A Blog Pipeline - Tracking Issue Helper
# ==============================================
# 
# This script helps view and manage the ADK A2A Blog Pipeline tracking issue.
# 
# Usage:
#   ./tools/adk-pipeline-status.sh [command]
# 
# Commands:
#   view        View the tracking issue with all comments
#   recent      Show recent pipeline runs
#   failed      Show failed pipeline runs
#   trigger     Manually trigger a pipeline run
#   health      Check agent health status
#   help        Show this help message
# 

set -euo pipefail

# Configuration
TRACKING_LABEL="adk-pipeline"
WORKFLOW_FILE="adk-a2a-blog-pipeline.yml"

# Dynamically find the tracking issue number
get_tracking_issue_number() {
    gh issue list --label "$TRACKING_LABEL" --state open --limit 1 --json number --jq '.[0].number' 2>/dev/null || echo ""
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}=================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if gh CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed"
        echo "Install it from: https://cli.github.com/"
        exit 1
    fi
}

# View tracking issue
view_tracking_issue() {
    TRACKING_ISSUE_NUMBER=$(get_tracking_issue_number)
    
    if [[ -z "$TRACKING_ISSUE_NUMBER" ]]; then
        print_error "No tracking issue found with label '${TRACKING_LABEL}'"
        echo ""
        print_info "The tracking issue will be created automatically on the next pipeline run."
        print_info "Or create one manually with: gh issue create --title '🤖 ADK A2A Blog Pipeline Status' --label '${TRACKING_LABEL},automated'"
        return 1
    fi
    
    print_header "Tracking Issue #${TRACKING_ISSUE_NUMBER}"
    
    echo ""
    print_info "Fetching tracking issue with all comments..."
    echo ""
    
    gh issue view "$TRACKING_ISSUE_NUMBER" --comments
}

# Show recent pipeline runs
show_recent_runs() {
    print_header "Recent Pipeline Runs"
    
    echo ""
    print_info "Fetching last 10 workflow runs..."
    echo ""
    
    gh run list \
        --workflow="$WORKFLOW_FILE" \
        --limit 10 \
        --json number,status,conclusion,event,createdAt,displayTitle \
        --jq '.[] | "\(.number)\t\(.status)\t\(.conclusion // "N/A")\t\(.event)\t\(.createdAt)\t\(.displayTitle)"' \
        | column -t -s $'\t' -N "RUN#,STATUS,CONCLUSION,TRIGGER,CREATED,TITLE"
    
    echo ""
    print_info "To view details: gh run view <RUN#>"
}

# Show failed pipeline runs
show_failed_runs() {
    print_header "Failed Pipeline Runs"
    
    echo ""
    print_info "Fetching failed workflow runs..."
    echo ""
    
    FAILED_RUNS=$(gh run list \
        --workflow="$WORKFLOW_FILE" \
        --status failure \
        --limit 10 \
        --json number,conclusion,createdAt,displayTitle \
        --jq '.[] | "\(.number)\t\(.conclusion)\t\(.createdAt)\t\(.displayTitle)"')
    
    if [[ -z "$FAILED_RUNS" ]]; then
        print_success "No failed runs found! 🎉"
    else
        echo "$FAILED_RUNS" | column -t -s $'\t' -N "RUN#,CONCLUSION,CREATED,TITLE"
        echo ""
        print_info "To view failure logs: gh run view <RUN#> --log-failed"
    fi
}

# Trigger pipeline run
trigger_pipeline() {
    print_header "Trigger Pipeline Run"
    
    echo ""
    echo "Choose run type:"
    echo "  1) Default run (auto-discover topics)"
    echo "  2) Custom topic"
    echo "  3) Dry run (no deployment)"
    echo "  4) Debug mode"
    echo ""
    read -p "Enter choice [1-4]: " choice
    
    case $choice in
        1)
            print_info "Triggering default pipeline run..."
            gh workflow run "$WORKFLOW_FILE"
            ;;
        2)
            read -p "Enter topic: " topic
            print_info "Triggering pipeline with topic: $topic"
            gh workflow run "$WORKFLOW_FILE" -f topic_query="$topic"
            ;;
        3)
            print_info "Triggering dry run (no deployment)..."
            gh workflow run "$WORKFLOW_FILE" -f dry_run=true
            ;;
        4)
            print_info "Triggering pipeline with debug mode..."
            gh workflow run "$WORKFLOW_FILE" -f debug=true
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    echo ""
    print_success "Pipeline triggered!"
    echo ""
    print_info "Monitor progress:"
    echo "  gh run watch"
    echo ""
    print_info "View recent runs:"
    echo "  ./tools/adk-pipeline-status.sh recent"
}

# Check agent health
check_agent_health() {
    print_header "Agent Health Status"
    
    echo ""
    print_info "Checking agent health endpoints..."
    echo ""
    
    # Note: This requires gcloud CLI and proper authentication
    if ! command -v gcloud &> /dev/null; then
        print_warning "gcloud CLI not installed - skipping health checks"
        echo "Install from: https://cloud.google.com/sdk/docs/install"
        return
    fi
    
    # Get GCP region from environment or use default
    GCP_REGION="${GCP_REGION:-us-central1}"
    
    echo "Checking agents in region: $GCP_REGION"
    echo ""
    
    # Agent services
    AGENTS=("chained-academic-research" "chained-google-trends" "chained-blog-writer")
    
    for agent in "${AGENTS[@]}"; do
        echo "Checking: $agent"
        
        # Get service URL
        URL=$(gcloud run services describe "$agent" \
            --region="$GCP_REGION" \
            --format='value(status.url)' 2>/dev/null || echo "")
        
        if [[ -z "$URL" ]]; then
            print_error "$agent: Not deployed"
            continue
        fi
        
        # Check health endpoint
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL/health" || echo "000")
        
        if [[ "$HTTP_CODE" == "200" ]]; then
            print_success "$agent: Healthy (URL: $URL)"
        else
            print_error "$agent: Unhealthy (HTTP $HTTP_CODE, URL: $URL)"
        fi
    done
    
    echo ""
    print_info "To view agent logs:"
    echo "  gcloud run services logs read <service-name> --region=$GCP_REGION"
}

# Show help
show_help() {
    cat << EOF
ADK A2A Blog Pipeline - Tracking Issue Helper
==============================================

This script helps you interact with the ADK A2A Blog Pipeline tracking system.

USAGE:
    ./tools/adk-pipeline-status.sh [command]

COMMANDS:
    view        View the tracking issue with all comments
    recent      Show recent pipeline runs (last 10)
    failed      Show failed pipeline runs
    trigger     Manually trigger a pipeline run (interactive)
    health      Check agent health status (requires gcloud CLI)
    help        Show this help message

EXAMPLES:
    # View tracking issue
    ./tools/adk-pipeline-status.sh view
    
    # Check recent runs
    ./tools/adk-pipeline-status.sh recent
    
    # Find failures
    ./tools/adk-pipeline-status.sh failed
    
    # Trigger a run
    ./tools/adk-pipeline-status.sh trigger
    
    # Check agent health
    ./tools/adk-pipeline-status.sh health

TRACKING ISSUE:
    Label: ${TRACKING_LABEL}
    
    The tracking issue is automatically discovered by searching for the
    '${TRACKING_LABEL}' label. The workflow creates it automatically if
    it doesn't exist. Each pipeline run posts a comment with results.
    
    To manually find the current tracking issue:
    gh issue list --label "${TRACKING_LABEL}" --state open

DOCUMENTATION:
    For detailed information, see:
    - docs/ADK_PIPELINE_TRACKING_GUIDE.md
    - docs/ADK_A2A_PIPELINE_IMPLEMENTATION.md

EOF
}

# Main script
main() {
    check_gh_cli
    
    COMMAND="${1:-help}"
    
    case "$COMMAND" in
        view)
            view_tracking_issue
            ;;
        recent)
            show_recent_runs
            ;;
        failed)
            show_failed_runs
            ;;
        trigger)
            trigger_pipeline
            ;;
        health)
            check_agent_health
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
