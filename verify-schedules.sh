#!/bin/bash

# Chained Schedule Verification Tool
# This script verifies that scheduled workflows are actually running

set -e

# Load shared library
source "$(dirname "$0")/tools/shell-common.sh"

echo "🔍 Workflow Schedule Verification"
echo "=================================="
echo ""

# Check GitHub CLI prerequisites
if ! check_gh_cli; then
    exit 1
fi

# Get current UTC time
current_time=$(date -u +%s)
current_time_str=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

echo "Current time: $current_time_str"
echo ""

# Define scheduled workflows with their expected intervals (in seconds)
declare -A workflows
workflows["Issue to PR Automator"]="1800"          # 30 minutes
workflows["Auto Review and Merge"]="900"           # 15 minutes  
workflows["Auto Close Issues"]="1800"              # 30 minutes
workflows["Timeline Updater"]="21600"              # 6 hours
workflows["Progress Tracker"]="43200"              # 12 hours
workflows["Workflow Monitor and Self-Healing"]="43200"  # 12 hours
workflows["AI Idea Generator"]="86400"             # 24 hours
workflows["Smart Idea Generator"]="86400"          # 24 hours
workflows["Learn from TLDR Tech"]="43200"          # 12 hours (runs twice daily)
workflows["Learn from Hacker News"]="21600"        # ~8 hours (runs 3x daily)

echo -e "${BLUE}Checking Scheduled Workflows${NC}"
echo "----------------------------"
echo ""

all_healthy=true
warning_count=0
error_count=0

for workflow_name in "${!workflows[@]}"; do
    interval=${workflows[$workflow_name]}
    
    # Get the most recent run of this workflow
    last_run=$(gh run list --workflow "$workflow_name" --limit 1 --json createdAt,status,conclusion -q '.[0]' 2>/dev/null || echo "{}")
    
    if [ "$last_run" = "{}" ] || [ -z "$last_run" ]; then
        echo -e "${YELLOW}⚠️  $workflow_name${NC}"
        echo "   Status: No runs found"
        echo "   Expected interval: $(($interval / 60)) minutes"
        echo ""
        warning_count=$((warning_count + 1))
        all_healthy=false
        continue
    fi
    
    last_run_time=$(echo "$last_run" | jq -r '.createdAt')
    status=$(echo "$last_run" | jq -r '.status')
    conclusion=$(echo "$last_run" | jq -r '.conclusion // "in_progress"')
    
    # Convert last run time to epoch
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        last_run_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$last_run_time" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "${last_run_time%.*}" +%s 2>/dev/null)
    else
        # Linux
        last_run_epoch=$(date -d "$last_run_time" +%s 2>/dev/null)
    fi
    
    if [ -z "$last_run_epoch" ]; then
        echo -e "${YELLOW}⚠️  $workflow_name${NC}"
        echo "   Status: Could not parse run time"
        echo "   Last run: $last_run_time"
        echo ""
        warning_count=$((warning_count + 1))
        all_healthy=false
        continue
    fi
    
    # Calculate time since last run
    time_since_last_run=$((current_time - last_run_epoch))
    
    # Calculate next expected run (add 10% buffer for GitHub delays)
    expected_max=$((interval + interval / 10))
    
    # Format time since last run
    if [ $time_since_last_run -lt 3600 ]; then
        time_str="$((time_since_last_run / 60)) minutes ago"
    elif [ $time_since_last_run -lt 86400 ]; then
        time_str="$((time_since_last_run / 3600)) hours ago"
    else
        time_str="$((time_since_last_run / 86400)) days ago"
    fi
    
    # Determine status
    if [ $time_since_last_run -gt $expected_max ]; then
        # Overdue
        echo -e "${RED}❌ $workflow_name${NC}"
        echo "   Status: OVERDUE"
        echo "   Last run: $time_str"
        echo "   Expected interval: $(($interval / 60)) minutes"
        echo "   Overdue by: $(((time_since_last_run - expected_max) / 60)) minutes"
        echo "   Last status: $status ($conclusion)"
        echo ""
        error_count=$((error_count + 1))
        all_healthy=false
    elif [ $time_since_last_run -gt $interval ]; then
        # Slightly late but within buffer
        echo -e "${YELLOW}⚠️  $workflow_name${NC}"
        echo "   Status: LATE (within tolerance)"
        echo "   Last run: $time_str"
        echo "   Expected interval: $(($interval / 60)) minutes"
        echo "   Last status: $status ($conclusion)"
        echo ""
        warning_count=$((warning_count + 1))
    else
        # On schedule
        echo -e "${GREEN}✅ $workflow_name${NC}"
        echo "   Status: ON SCHEDULE"
        echo "   Last run: $time_str"
        echo "   Expected interval: $(($interval / 60)) minutes"
        echo "   Last status: $status ($conclusion)"
        echo ""
    fi
done

# Summary
echo "=================================="
echo -e "${BLUE}Summary${NC}"
echo "=================================="
echo ""

total_workflows=${#workflows[@]}
healthy_workflows=$((total_workflows - warning_count - error_count))

echo "Total scheduled workflows: $total_workflows"
echo -e "${GREEN}Healthy (on schedule): $healthy_workflows${NC}"
echo -e "${YELLOW}Warnings (late but tolerable): $warning_count${NC}"
echo -e "${RED}Errors (overdue): $error_count${NC}"
echo ""

if [ $all_healthy = true ]; then
    echo -e "${GREEN}✅ All scheduled workflows are running on time!${NC}"
    echo ""
    echo "Your cron schedules are working properly. The autonomous system"
    echo "is operating as expected."
else
    if [ $error_count -gt 0 ]; then
        echo -e "${RED}⚠️  Some workflows are significantly overdue!${NC}"
        echo ""
        echo "This could indicate:"
        echo "  • GitHub Actions is experiencing delays"
        echo "  • Workflows are disabled (check Actions tab)"
        echo "  • Workflow failures are preventing runs"
        echo "  • Repository has been inactive for 60+ days"
        echo ""
        echo "Actions to take:"
        echo "  1. Check the Actions tab for failed workflows"
        echo "  2. Look for workflow-monitor issues"
        echo "  3. Manually trigger overdue workflows"
        echo "  4. Review workflow logs for errors"
    elif [ $warning_count -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Some workflows are running slightly late${NC}"
        echo ""
        echo "This is normal and expected. GitHub Actions scheduled workflows"
        echo "can experience minor delays during peak hours. As long as they're"
        echo "running within 10-20% of their expected interval, the system will"
        echo "function properly."
    fi
fi

echo ""
echo "=================================="
echo -e "${BLUE}Additional Information${NC}"
echo "=================================="
echo ""

# Check for recent workflow failures
recent_failures=$(gh run list --limit 50 --json conclusion,name | jq '[.[] | select(.conclusion == "failure")] | length')

if [ "$recent_failures" -gt 0 ]; then
    echo -e "${RED}⚠️  Detected $recent_failures failed workflow runs in last 50 runs${NC}"
    echo ""
    echo "Recent failures:"
    gh run list --limit 50 --json conclusion,name,createdAt | jq -r '.[] | select(.conclusion == "failure") | "  • \(.name) - \(.createdAt | split("T")[0] + " " + split("T")[1] | split(".")[0])"' | head -5
    echo ""
    echo "Check workflow-monitor issues for detailed analysis."
else
    echo -e "${GREEN}✅ No recent workflow failures detected${NC}"
fi

echo ""

# Check if repository might be at risk of 60-day deactivation
last_commit=$(git log -1 --format=%ct 2>/dev/null)
if [ -n "$last_commit" ]; then
    days_since_commit=$(( (current_time - last_commit) / 86400 ))
    
    if [ $days_since_commit -gt 60 ]; then
        echo -e "${RED}⚠️  Last commit was $days_since_commit days ago${NC}"
        echo "   Scheduled workflows are disabled after 60 days of inactivity!"
        echo "   Make a commit or create activity to re-enable them."
    elif [ $days_since_commit -gt 45 ]; then
        echo -e "${YELLOW}⚠️  Last commit was $days_since_commit days ago${NC}"
        echo "   Warning: Approaching the 60-day inactivity limit."
        echo "   Scheduled workflows will be disabled if no activity occurs."
    else
        echo -e "${GREEN}✅ Repository is active (last commit $days_since_commit days ago)${NC}"
        echo "   Scheduled workflows will remain enabled."
    fi
fi

echo ""
echo "For more information about workflow triggers, see WORKFLOW_TRIGGERS.md"
echo ""
