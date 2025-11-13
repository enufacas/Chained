#!/bin/bash

# Chained Workflow State Evaluation Script
# Comprehensive check of all workflows and their health

set -e

# Load shared library
source "$(dirname "$0")/../tools/shell-common.sh"

echo "🔍 Chained Workflow State Evaluation"
echo "====================================="
echo ""

ERRORS=0
WARNINGS=0
INFO=0

# Override print_status to track errors/warnings/info
print_status() {
    local status="$1"
    local message="$2"
    
    case "$status" in
        "OK")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}⚠${NC} $message"
            WARNINGS=$((WARNINGS + 1))
            ;;
        "INFO")
            echo -e "${BLUE}ℹ${NC} $message"
            INFO=$((INFO + 1))
            ;;
        "ERROR"|*)
            echo -e "${RED}✗${NC} $message"
            ERRORS=$((ERRORS + 1))
            ;;
    esac
}

echo "1. Workflow Presence Check"
echo "---------------------------"
echo ""

# All workflows that should exist
declare -A workflows=(
    ["auto-kickoff.yml"]="Auto Kickoff on First Run|push,workflow_dispatch"
    ["system-kickoff.yml"]="System Kickoff|workflow_dispatch"
    ["idea-generator.yml"]="AI Idea Generator|schedule,workflow_dispatch"
    ["smart-idea-generator.yml"]="Smart Idea Generator|schedule,workflow_dispatch"
    ["copilot-assign.yml"]="Copilot Auto-Assign|issues,workflow_dispatch"
    ["issue-to-pr.yml"]="Issue to PR Automator|schedule,workflow_dispatch"
    ["auto-review-merge.yml"]="Auto Review and Merge|pull_request,schedule,workflow_dispatch"
    ["auto-close-issues.yml"]="Auto Close Issues|schedule,workflow_dispatch"
    ["timeline-updater.yml"]="Timeline Updater|schedule,workflow_dispatch"
    ["progress-tracker.yml"]="Progress Tracker|schedule,workflow_dispatch"
    ["learn-from-tldr.yml"]="Learn from TLDR|schedule,workflow_dispatch"
    ["learn-from-hackernews.yml"]="Learn from Hacker News|schedule,workflow_dispatch"
    ["workflow-monitor.yml"]="Workflow Monitor|schedule,workflow_dispatch"
)

total_workflows=${#workflows[@]}
found_workflows=0

for workflow in "${!workflows[@]}"; do
    IFS='|' read -r name expected_triggers <<< "${workflows[$workflow]}"
    
    if [ -f ".github/workflows/$workflow" ]; then
        print_status "OK" "$name exists"
        found_workflows=$((found_workflows + 1))
    else
        print_status "ERROR" "$name is missing"
    fi
done

echo ""
echo "Found $found_workflows out of $total_workflows workflows"
echo ""

echo "2. Workflow Trigger Validation"
echo "-------------------------------"
echo ""

for workflow in "${!workflows[@]}"; do
    if [ ! -f ".github/workflows/$workflow" ]; then
        continue
    fi
    
    IFS='|' read -r name expected_triggers <<< "${workflows[$workflow]}"
    
    # Check if workflow has the expected triggers
    has_valid_trigger=false
    
    for trigger in ${expected_triggers//,/ }; do
        if grep -q "on:" ".github/workflows/$workflow" && grep -q "$trigger:" ".github/workflows/$workflow"; then
            has_valid_trigger=true
            break
        fi
    done
    
    if [ "$has_valid_trigger" = true ]; then
        print_status "OK" "$name has valid triggers"
    else
        print_status "WARN" "$name may be missing expected triggers"
    fi
done

echo ""
echo "3. Workflow Permissions Check"
echo "------------------------------"
echo ""

# Check critical permissions
for workflow in "${!workflows[@]}"; do
    if [ ! -f ".github/workflows/$workflow" ]; then
        continue
    fi
    
    IFS='|' read -r name _ <<< "${workflows[$workflow]}"
    
    # Check if workflow has permissions defined
    if grep -q "permissions:" ".github/workflows/$workflow"; then
        print_status "OK" "$name has permissions defined"
    else
        print_status "INFO" "$name uses default permissions"
    fi
done

echo ""
echo "4. Critical Workflow Dependencies"
echo "----------------------------------"
echo ""

# Check that workflows have their dependencies

# Auto-kickoff depends on system-kickoff
if [ -f ".github/workflows/auto-kickoff.yml" ] && [ -f ".github/workflows/system-kickoff.yml" ]; then
    print_status "OK" "Auto-kickoff can trigger system-kickoff"
    
    # Check if auto-kickoff has actions: write permission (needed to trigger workflows)
    if grep -q "permissions:" ".github/workflows/auto-kickoff.yml" && \
       grep -A 5 "permissions:" ".github/workflows/auto-kickoff.yml" | grep -q "actions: write"; then
        print_status "OK" "Auto-kickoff has actions: write permission"
    else
        print_status "ERROR" "Auto-kickoff missing actions: write permission (needed to trigger workflows)"
    fi
else
    print_status "ERROR" "Auto-kickoff missing system-kickoff dependency"
fi

# Issue-to-PR depends on copilot-assign labels
if [ -f ".github/workflows/issue-to-pr.yml" ] && [ -f ".github/workflows/copilot-assign.yml" ]; then
    print_status "OK" "Issue-to-PR can process copilot-assigned issues"
else
    print_status "ERROR" "Issue-to-PR missing copilot-assign dependency"
fi

# Smart idea generator depends on learning workflows
if [ -f ".github/workflows/smart-idea-generator.yml" ] && \
   [ -f ".github/workflows/learn-from-tldr.yml" ] && \
   [ -f ".github/workflows/learn-from-hackernews.yml" ]; then
    print_status "OK" "Smart idea generator has learning sources"
else
    print_status "ERROR" "Smart idea generator missing learning dependencies"
fi

echo ""
echo "5. Schedule Validation"
echo "----------------------"
echo ""

# Check scheduled workflows have cron expressions
scheduled_workflows=(
    "learn-from-hackernews.yml:3 times daily"
    "learn-from-tldr.yml:2 times daily"
    "smart-idea-generator.yml:daily at 10 AM UTC"
    "idea-generator.yml:daily at 9 AM UTC"
    "auto-review-merge.yml:every 2 hours"
    "issue-to-pr.yml:every 3 hours"
    "auto-close-issues.yml:every 4 hours"
    "timeline-updater.yml:every 6 hours"
    "progress-tracker.yml:every 12 hours"
    "workflow-monitor.yml:every 12 hours"
)

for item in "${scheduled_workflows[@]}"; do
    IFS=':' read -r workflow schedule <<< "$item"
    
    if [ -f ".github/workflows/$workflow" ]; then
        if grep -q "cron:" ".github/workflows/$workflow"; then
            print_status "OK" "$workflow has schedule ($schedule)"
        else
            print_status "ERROR" "$workflow missing cron schedule"
        fi
    fi
done

echo ""
echo "6. Workflow Syntax Check"
echo "------------------------"
echo ""

yaml_errors=0
if command -v yamllint &> /dev/null; then
    for workflow in .github/workflows/*.yml; do
        if yamllint -d "{extends: relaxed, rules: {line-length: {max: 200}}}" "$workflow" >/dev/null 2>&1; then
            : # Valid, no output needed
        else
            print_status "WARN" "$(basename $workflow) has style issues"
            yaml_errors=$((yaml_errors + 1))
        fi
    done
    
    if [ $yaml_errors -eq 0 ]; then
        print_status "OK" "All workflow files have valid YAML syntax"
    else
        print_status "INFO" "$yaml_errors workflow(s) have style issues (not critical)"
    fi
else
    print_status "INFO" "yamllint not available, skipping syntax validation"
fi

echo ""
echo "7. Workflow Chain Validation"
echo "-----------------------------"
echo ""

print_status "INFO" "Workflow execution order:"
echo ""
echo "  First Run:"
echo "    1. auto-kickoff.yml (on push to main)"
echo "       └─> 2. system-kickoff.yml (triggered by auto-kickoff)"
echo "           ├─> Creates labels"
echo "           ├─> Initializes learnings/"
echo "           └─> Triggers initial workflows"
echo ""
echo "  Daily Learning Cycle:"
echo "    07:00 UTC - learn-from-hackernews.yml"
echo "    08:00 UTC - learn-from-tldr.yml"
echo "    09:00 UTC - idea-generator.yml"
echo "    10:00 UTC - smart-idea-generator.yml"
echo "    13:00 UTC - learn-from-hackernews.yml"
echo "    19:00 UTC - learn-from-hackernews.yml"
echo "    20:00 UTC - learn-from-tldr.yml"
echo ""
echo "  Continuous Automation:"
echo "    Every 2h - auto-review-merge.yml"
echo "    Every 3h - issue-to-pr.yml"
echo "    Every 4h - auto-close-issues.yml"
echo "    Every 6h - timeline-updater.yml"
echo "    Every 12h - progress-tracker.yml"
echo "    Every 12h - workflow-monitor.yml"
echo ""
echo "  Event-Driven:"
echo "    On issue created → copilot-assign.yml"
echo "    On PR opened → auto-review-merge.yml"
echo ""

echo "================================================================"
echo "Evaluation Summary"
echo "================================================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All workflow checks passed!${NC}"
    echo ""
    echo "The Chained perpetual motion machine is properly configured."
    echo "All $total_workflows workflows are present and correctly set up."
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Evaluation completed with $WARNINGS warning(s) and $INFO info message(s)${NC}"
    echo ""
    echo "The system should work, but review the warnings above."
    echo ""
    exit 0
else
    echo -e "${RED}✗ Evaluation found $ERRORS error(s), $WARNINGS warning(s), and $INFO info message(s)${NC}"
    echo ""
    echo "Please fix the errors above before starting the system."
    echo ""
    exit 1
fi
