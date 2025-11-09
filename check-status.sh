#!/bin/bash

# Chained System Status Checker
# This script checks the status of the autonomous system

set -e

echo "📊 Chained System Status"
echo "========================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is required but not installed.${NC}"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if gh is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI is not authenticated.${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

# Get repository info
REPO_INFO=$(gh repo view --json owner,name -q '.owner.login + "/" + .name')
echo "Repository: $REPO_INFO"
echo ""

echo -e "${BLUE}1. Recent Workflow Runs${NC}"
echo "----------------------"
echo ""

# Get recent workflow runs
echo "Last 5 workflow runs:"
gh run list --limit 5 --json name,conclusion,status,createdAt -q '.[] | "\(.createdAt | split("T")[0] + " " + split("T")[1] | split(".")[0]): \(.name) - \(.status) \(if .conclusion then "(\(.conclusion))" else "" end)"' 2>/dev/null || echo "No workflow runs found"

echo ""
echo -e "${BLUE}2. Issue Statistics${NC}"
echo "-------------------"
echo ""

# Count issues by label
ai_generated=$(gh issue list --label "ai-generated" --state all --limit 1000 --json number -q 'length' 2>/dev/null || echo "0")
copilot_assigned=$(gh issue list --label "copilot-assigned" --state all --limit 1000 --json number -q 'length' 2>/dev/null || echo "0")
completed=$(gh issue list --label "completed" --state closed --limit 1000 --json number -q 'length' 2>/dev/null || echo "0")
learning=$(gh issue list --label "learning" --state all --limit 1000 --json number -q 'length' 2>/dev/null || echo "0")

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

echo ""
echo -e "${BLUE}3. Recent Issues${NC}"
echo "---------------"
echo ""
echo "Last 5 issues:"
gh issue list --limit 5 --json number,title,labels,state -q '.[] | "#\(.number): \(.title) [\(.state)] (\(.labels | map(.name) | join(", ")))"' 2>/dev/null || echo "No issues found"

echo ""
echo -e "${BLUE}4. Pull Request Statistics${NC}"
echo "--------------------------"
echo ""

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

echo ""
echo -e "${BLUE}5. Learning Files${NC}"
echo "----------------"
echo ""

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

echo ""
echo -e "${BLUE}6. GitHub Pages Status${NC}"
echo "---------------------"
echo ""

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

echo ""
echo -e "${BLUE}7. Next Scheduled Runs${NC}"
echo "---------------------"
echo ""

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

# Calculate some metrics
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
