#!/bin/bash
#
# Close Stale Issues and Conflicted PRs
#
# This script implements automated cleanup of:
# 1. Issues older than specified hours (default: 2 hours)
# 2. PRs with merge conflicts
#
# Usage:
#   ./tools/close-stale-issues-and-prs.sh [--issue-hours HOURS] [--close-issues] [--close-prs] [--dry-run]
#
# Options:
#   --issue-hours HOURS    Close issues older than HOURS (default: 2)
#   --close-issues         Enable closing stale issues
#   --close-prs            Enable closing PRs with conflicts
#   --dry-run              Show what would be done without actually closing
#   --help                 Show this help message
#
# Exit codes:
#   0 - Success
#   1 - General error
#   2 - Missing dependencies

set -euo pipefail

# Configuration
DRY_RUN=false
ISSUE_HOURS_THRESHOLD=2
CLOSE_ISSUES=false
CLOSE_PRS=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --issue-hours)
      ISSUE_HOURS_THRESHOLD="$2"
      shift 2
      ;;
    --close-issues)
      CLOSE_ISSUES=true
      shift
      ;;
    --close-prs)
      CLOSE_PRS=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --help)
      head -n 20 "$0" | tail -n 19
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Check if at least one action is enabled
if [ "$CLOSE_ISSUES" = false ] && [ "$CLOSE_PRS" = false ]; then
  echo "ERROR: No actions specified. Use --close-issues and/or --close-prs"
  echo "Use --help for usage information"
  exit 1
fi

# Check dependencies
if ! command -v gh &> /dev/null; then
  echo "ERROR: gh CLI is required but not installed"
  exit 2
fi

if ! command -v jq &> /dev/null; then
  echo "ERROR: jq is required but not installed"
  exit 2
fi

if ! command -v python3 &> /dev/null; then
  echo "ERROR: python3 is required but not installed"
  exit 2
fi

# Ensure GH_TOKEN is set
if [ -z "${GH_TOKEN:-}" ]; then
  echo "ERROR: GH_TOKEN environment variable must be set"
  exit 1
fi

# Initialize counters
issues_closed=0
prs_closed=0

echo "========================================="
echo "Close Stale Issues and Conflicted PRs"
echo "========================================="
echo ""
echo "Configuration:"
echo "  - Dry run: ${DRY_RUN}"
echo "  - Close issues: ${CLOSE_ISSUES}"
echo "  - Close PRs: ${CLOSE_PRS}"
if [ "$CLOSE_ISSUES" = true ]; then
  echo "  - Issue hours threshold: ${ISSUE_HOURS_THRESHOLD}"
fi
echo ""

#
# Part 1: Close stale issues
#
if [ "$CLOSE_ISSUES" = true ]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📋 Checking for stale issues..."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Calculate cutoff date
  cutoff_date=$(python3 -c "
from datetime import datetime, timedelta
cutoff = datetime.utcnow() - timedelta(hours=${ISSUE_HOURS_THRESHOLD})
print(cutoff.strftime('%Y-%m-%dT%H:%M:%SZ'))
")
  
  echo "Cutoff time: ${cutoff_date}"
  echo ""
  
  # Get all open issues
  issue_list=$(gh issue list --state open --limit 500 --json number,title,createdAt,author,labels 2>/dev/null || echo "[]")
  
  if [ -z "${issue_list}" ] || [ "${issue_list}" = "[]" ]; then
    echo "ℹ️  No open issues found"
  else
    total_issues=$(echo "${issue_list}" | jq 'length')
    echo "Found ${total_issues} open issues"
    echo ""
    
    # Process each issue
    echo "${issue_list}" | jq -c '.[]' | while read -r issue; do
      issue_num=$(echo "${issue}" | jq -r '.number')
      issue_title=$(echo "${issue}" | jq -r '.title')
      issue_created=$(echo "${issue}" | jq -r '.createdAt')
      issue_author=$(echo "${issue}" | jq -r '.author.login')
      
      # Calculate hours since creation
      hours_old=$(python3 -c "
from datetime import datetime
now = datetime.utcnow()
created = datetime.fromisoformat('${issue_created}'.replace('Z', '+00:00'))
hours = (now - created.replace(tzinfo=None)).total_seconds() / 3600
print(int(hours))
")
      
      # Check if issue is older than threshold
      if [ ${hours_old} -gt ${ISSUE_HOURS_THRESHOLD} ]; then
        echo "🗑️  Issue #${issue_num} is ${hours_old} hours old"
        echo "   Title: ${issue_title}"
        echo "   Author: ${issue_author}"
        
        if [ "$DRY_RUN" = true ]; then
          echo "   [DRY RUN] Would close this issue"
        else
          # Post closing comment
          gh issue comment ${issue_num} --body "## 🧹 Automatic Stale Issue Closure

This issue has been automatically closed because it has been open for more than ${ISSUE_HOURS_THRESHOLD} hours.

**Issue details:**
- **Created:** ${issue_created}
- **Age:** ${hours_old} hours
- **Author:** @${issue_author}

**To resume this work:**
1. If this issue is still relevant, please re-open it
2. Add any new context or updates
3. Ensure the issue has clear requirements

---
*Automated cleanup script*" 2>/dev/null || echo "   ⚠️ Failed to comment"
          
          # Close the issue
          gh issue close ${issue_num} --reason "not planned" 2>/dev/null || {
            echo "   ⚠️ Failed to close issue #${issue_num}"
            continue
          }
          
          echo "   ✅ Closed issue #${issue_num}"
          issues_closed=$((issues_closed + 1))
        fi
        echo ""
      fi
    done
  fi
  
  echo ""
fi

#
# Part 2: Close PRs with merge conflicts
#
if [ "$CLOSE_PRS" = true ]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🔀 Checking for PRs with merge conflicts..."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Get all open PRs
  pr_list=$(gh pr list --state open --limit 200 --json number,title,mergeable,mergeStateStatus,author,headRefName 2>/dev/null || echo "[]")
  
  if [ -z "${pr_list}" ] || [ "${pr_list}" = "[]" ]; then
    echo "ℹ️  No open PRs found"
  else
    total_prs=$(echo "${pr_list}" | jq 'length')
    echo "Found ${total_prs} open PRs"
    echo ""
    
    # Process each PR
    echo "${pr_list}" | jq -c '.[]' | while read -r pr; do
      pr_num=$(echo "${pr}" | jq -r '.number')
      pr_title=$(echo "${pr}" | jq -r '.title')
      mergeable=$(echo "${pr}" | jq -r '.mergeable')
      merge_state=$(echo "${pr}" | jq -r '.mergeStateStatus')
      author=$(echo "${pr}" | jq -r '.author.login')
      head_branch=$(echo "${pr}" | jq -r '.headRefName')
      
      # Check if PR has conflicts
      if [ "${mergeable}" = "CONFLICTING" ] || [ "${merge_state}" = "DIRTY" ]; then
        echo "⚠️  PR #${pr_num} has merge conflicts"
        echo "   Title: ${pr_title}"
        echo "   Author: ${author}"
        echo "   Branch: ${head_branch}"
        
        if [ "$DRY_RUN" = true ]; then
          echo "   [DRY RUN] Would close this PR"
        else
          # Post explanation comment
          gh pr comment ${pr_num} --body "## 🚨 Automatic Closure: Merge Conflicts

This PR has been automatically closed due to unresolved merge conflicts.

**PR details:**
- **Title:** ${pr_title}
- **Branch:** \`${head_branch}\`
- **Author:** @${author}
- **Status:** ${mergeable}

**To resume this work:**
1. Create a new branch from latest \`main\`
2. Reapply your changes
3. Resolve any conflicts
4. Open a new PR referencing #${pr_num}

---
*Automated cleanup script*" 2>/dev/null || echo "   ⚠️ Failed to comment"
          
          # Close the PR
          gh pr close ${pr_num} --comment "Closing due to merge conflicts" 2>/dev/null || {
            echo "   ⚠️ Failed to close PR #${pr_num}"
            continue
          }
          
          echo "   ✅ Closed PR #${pr_num}"
          prs_closed=$((prs_closed + 1))
        fi
        echo ""
      fi
    done
  fi
  
  echo ""
fi

# Summary
echo "========================================="
echo "Summary"
echo "========================================="
echo ""
if [ "$CLOSE_ISSUES" = true ]; then
  echo "Issues closed: ${issues_closed}"
fi
if [ "$CLOSE_PRS" = true ]; then
  echo "PRs closed: ${prs_closed}"
fi
echo ""

if [ "$DRY_RUN" = true ]; then
  echo "ℹ️  This was a dry run - nothing was actually closed"
  echo "   Run without --dry-run to execute cleanup"
fi

echo ""
echo "✅ Cleanup complete"
echo "Timestamp: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"

exit 0
