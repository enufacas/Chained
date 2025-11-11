#!/bin/bash

################################################################################
# Chained System Status Checker
#
# An elegant monitoring tool that provides comprehensive insights into the
# Chained autonomous AI ecosystem's health and activity. This script presents
# system metrics, workflow status, and progress indicators with clarity.
#
# Features:
#   • Recent workflow run analysis
#   • Issue and PR statistics
#   • Learning file tracking
#   • GitHub Pages status
#   • Scheduled workflow overview
#   • Success rate calculations
#
# Usage:
#   ./check-status.sh
#
# Requirements:
#   • GitHub CLI (gh) installed and authenticated
#   • Repository read access
################################################################################

set -e  # Exit on any error

# Terminal color codes for beautiful output
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'  # No Color

################################################################################
# Display Functions
################################################################################

print_header() {
    echo "📊 Chained System Status"
    echo "========================"
    echo ""
}

print_section() {
    local section_number="$1"
    local section_name="$2"
    echo ""
    echo -e "${BLUE}${section_number}. ${section_name}${NC}"
    echo "$(printf '%.0s-' {1..50})"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

################################################################################
# Validation Functions
################################################################################

check_github_cli() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is required but not installed."
        echo "Please install it from: https://cli.github.com/"
        return 1
    fi
    return 0
}

check_authentication() {
    if ! gh auth status &> /dev/null; then
        print_error "GitHub CLI is not authenticated."
        echo "Please run: gh auth login"
        return 1
    fi
    return 0
}

################################################################################
# Data Collection Functions
################################################################################

count_issues_by_label() {
    local label="$1"
    gh issue list --label "$label" --state all --limit 1000 --json number -q 'length' 2>/dev/null || echo "0"
}

################################################################################
# Main Script Logic
################################################################################

main() {
    print_header
    
    # Validate prerequisites
    check_github_cli || exit 1
    check_authentication || exit 1

    
    # Get repository information
    REPO_INFO=$(gh repo view --json owner,name -q '.owner.login + "/" + .name')
    echo "Repository: $REPO_INFO"

    print_section 1 "Recent Workflow Runs"

echo "Last 5 workflow runs:"
gh run list --limit 5 --json name,conclusion,status,createdAt -q '.[] | "\(.createdAt | split("T")[0] + " " + split("T")[1] | split(".")[0]): \(.name) - \(.status) \(if .conclusion then "(\(.conclusion))" else "" end)"' 2>/dev/null || echo "No workflow runs found"

print_section 2 "Issue Statistics"

# Count issues by label
ai_generated=$(count_issues_by_label "ai-generated")
copilot_assigned=$(count_issues_by_label "copilot-assigned")
completed=$(count_issues_by_label "completed")
learning=$(count_issues_by_label "learning")

open_issues=$(gh issue list --state open --limit 1000 --json number -q 'length' 2>/dev/null || echo "0")
closed_issues=$(gh issue list --state closed --limit 1000 --json number -q 'length' 2>/dev/null || echo "0")

echo "Total Issues:"
echo "  Open: $open_issues"
echo "  Closed: $closed_issues"
echo ""
echo "By Label:"
echo "  AI-Generated: $ai_generated"
echo "  Copilot-Assigned: $copilot_assigned"
echo "  Completed: $completed"
echo "  Learning: $learning"

print_section 3 "Recent Issues"
echo "Last 5 issues:"
gh issue list --limit 5 --json number,title,labels,state -q '.[] | "#\(.number): \(.title) [\(.state)] (\(.labels | map(.name) | join(", ")))"' 2>/dev/null || echo "No issues found"

print_section 4 "Pull Request Statistics"

# Count PRs
open_prs=$(gh pr list --state open --limit 1000 --json number -q 'length' 2>/dev/null || echo "0")
closed_prs=$(gh pr list --state closed --limit 1000 --json number -q 'length' 2>/dev/null || echo "0")
merged_prs=$(gh pr list --state merged --limit 1000 --json number -q 'length' 2>/dev/null || echo "0")

echo "Pull Requests:"
echo "  Open: $open_prs"
echo "  Closed: $closed_prs"
echo "  Merged: $merged_prs"

echo ""
echo "Last 5 PRs:"
gh pr list --state all --limit 5 --json number,title,state -q '.[] | "#\(.number): \(.title) [\(.state)]"' 2>/dev/null || echo "No pull requests found"

print_section 5 "Learning Files"

if [ -d "learnings" ]; then
    learning_count=$(find learnings -name "*.json" 2>/dev/null | wc -l)
    echo "Learning files in learnings/: $learning_count"
    
    if [ $learning_count -gt 0 ]; then
        echo ""
        echo "Recent learning files:"
        ls -lt learnings/*.json 2>/dev/null | head -5 | awk '{print "  " $9 " (" $6 " " $7 ")"}'
    fi
else
    echo "Learnings directory not found"
fi

print_section 6 "GitHub Pages Status"

pages_url="https://$(gh repo view --json owner,name -q '.owner.login').github.io/$(gh repo view --json name -q '.name')/"
echo "GitHub Pages URL: $pages_url"
echo ""

# Check if docs directory has been updated recently
if [ -d "docs" ]; then
    last_docs_update=$(git log -1 --format="%ai" -- docs/ 2>/dev/null || echo "Never")
    echo "Last docs/ update: $last_docs_update"
else
    echo "docs/ directory not found"
fi

print_section 7 "Next Scheduled Runs"

# Get current time in UTC
current_hour=$(date -u +%H)
current_minute=$(date -u +%M)

echo "Current UTC time: $(date -u +"%Y-%m-%d %H:%M")"
echo ""
echo "Upcoming workflow schedules:"
echo "  • Learn from HN: 07:00, 13:00, 19:00 UTC"
echo "  • Learn from TLDR: 08:00, 20:00 UTC"
echo "  • Idea Generator: 09:00 UTC"
echo "  • Smart Idea Generator: 10:00 UTC"
echo "  • Auto Review & Merge: Every 15 minutes"
echo "  • Issue to PR: Every 30 minutes"
echo "  • Auto Close Issues: Every 30 minutes"
echo "  • Timeline Updater: Every 6 hours"
echo "  • Progress Tracker: Every 12 hours"
echo "  • Workflow Monitor: Every 12 hours"

echo ""
echo "================================================================"
echo -e "${GREEN}Status Check Complete!${NC}"
echo "================================================================"
echo ""

# Calculate success metrics
if [ "$ai_generated" -gt 0 ]; then
    success_rate=0
    if [ "$completed" -gt 0 ]; then
        success_rate=$((completed * 100 / ai_generated))
    fi
    echo "Autonomous Success Rate: $success_rate% ($completed/$ai_generated completed)"
else
    echo "No AI-generated issues yet. Run './kickoff-system.sh' to start!"
fi

echo ""
echo "Quick Actions:"
echo "  • View actions: gh workflow list"
echo "  • View recent runs: gh run list"
echo "  • Verify schedules: ./verify-schedules.sh"
echo "  • Trigger workflow: gh workflow run <workflow-name>"
echo "  • View issues: gh issue list"
echo "  • View PRs: gh pr list"
echo ""
}

# Execute main function
main
