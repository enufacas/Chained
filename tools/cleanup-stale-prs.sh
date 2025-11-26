#!/bin/bash
#
# Meta-Coordinator: Stale PR Cleanup Script
#
# This script proactively closes stale PRs that are blocking or abandoned.
# It implements the 3-hour conflict policy and 7-day no-activity policy.
#
# Usage:
#   ./tools/cleanup-stale-prs.sh [--dry-run]
#
# Exit codes:
#   0 - Success
#   1 - General error
#   2 - Missing dependencies

set -euo pipefail

# Configuration
DRY_RUN=false
CONFLICT_HOURS_THRESHOLD=3
NO_ACTIVITY_DAYS_THRESHOLD=7
DRAFT_DAYS_THRESHOLD=7

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--dry-run]"
      exit 1
      ;;
  esac
done

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
total_prs_checked=0
prs_closed_conflicts=0
prs_closed_no_activity=0
prs_closed_orphaned=0
prs_closed_draft=0

echo "========================================="
echo "Meta-Coordinator: Stale PR Cleanup"
echo "========================================="
echo ""
echo "Configuration:"
echo "  - Dry run: ${DRY_RUN}"
echo "  - Conflict threshold: ${CONFLICT_HOURS_THRESHOLD} hours"
echo "  - No activity threshold: ${NO_ACTIVITY_DAYS_THRESHOLD} days"
echo "  - Draft threshold: ${DRAFT_DAYS_THRESHOLD} days"
echo ""

# Get all open PRs
echo "📋 Fetching all open PRs..."
gh pr list --state open --limit 200 \
  --json number,title,isDraft,mergeable,updatedAt,createdAt,author,headRefName \
  > /tmp/all_open_prs.json

total_prs=$(jq 'length' /tmp/all_open_prs.json)
echo "   Found ${total_prs} open PRs"
echo ""

# Function to calculate hours since timestamp
hours_since() {
  local timestamp=$1
  python3 -c "
from datetime import datetime
now = datetime.utcnow()
updated = datetime.fromisoformat('${timestamp}'.replace('Z', '+00:00'))
hours = (now - updated.replace(tzinfo=None)).total_seconds() / 3600
print(int(hours))
"
}

# Function to calculate days since timestamp
days_since() {
  local timestamp=$1
  python3 -c "
from datetime import datetime
now = datetime.utcnow()
updated = datetime.fromisoformat('${timestamp}'.replace('Z', '+00:00'))
days = (now - updated.replace(tzinfo=None)).total_seconds() / 86400
print(int(days))
"
}

# Function to close PR with explanation
close_pr_with_reason() {
  local pr_num=$1
  local reason_title=$2
  local reason_detail=$3
  local is_stale=$4
  
  total_prs_checked=$((total_prs_checked + 1))
  
  if [ "$DRY_RUN" = true ]; then
    echo "   [DRY RUN] Would close PR #${pr_num}: ${reason_title}"
    return 0
  fi
  
  # Post explanation comment
  gh pr comment "${pr_num}" --body "## 🧹 Proactive Stale PR Cleanup

**Reason:** ${reason_title}

${reason_detail}

**To resume this work:**
1. Create a new branch from latest main
2. Reapply your changes (resolve any conflicts)
3. Open a new PR
4. Reference this PR: #${pr_num}

*Automated cleanup by @meta-coordinator-system based on PR lifecycle policies*
" || echo "Warning: Could not post comment to PR #${pr_num}"
  
  # Close PR
  gh pr close "${pr_num}" --comment "Closing as stale - see explanation above" || {
    echo "ERROR: Could not close PR #${pr_num}"
    return 1
  }
  
  # Note: Branch name should be retrieved before closing PR
  # Branch deletion handled separately if needed
  
  echo "   ✅ Closed PR #${pr_num}: ${reason_title}"
}

# 1. Check for PRs with merge conflicts >3 hours
echo "🔍 Checking for PRs with merge conflicts >3 hours..."
conflicting_prs=$(jq -r '.[] | select(.mergeable == "CONFLICTING") | "\(.number)|\(.title)|\(.updatedAt)|\(.author.login)"' /tmp/all_open_prs.json)

if [ -n "$conflicting_prs" ]; then
  while IFS='|' read -r pr_num title updated_at author; do
    hours_stale=$(hours_since "$updated_at")
    
    if [ "$hours_stale" -gt "$CONFLICT_HOURS_THRESHOLD" ]; then
      echo "   🚨 PR #${pr_num} (${author}): ${hours_stale} hours with conflicts"
      close_pr_with_reason \
        "${pr_num}" \
        "Merge conflicts unresolved for ${hours_stale} hours" \
        "This PR has had merge conflicts for more than ${CONFLICT_HOURS_THRESHOLD} hours without resolution.

**Why closing:**
- Merge conflicts indicate PR is critically out of sync with main
- ${CONFLICT_HOURS_THRESHOLD} hours is sufficient time for resolution
- Blocking resources and attention
- Low probability of completion in current form

**What this means:**
- Work in this PR may still be valuable
- Conflicts must be resolved before merging
- Starting fresh from main is often easier than resolving old conflicts" \
        "true"
      prs_closed_conflicts=$((prs_closed_conflicts + 1))
    fi
  done <<< "$conflicting_prs"
fi

echo "   Closed ${prs_closed_conflicts} PRs with conflicts"
echo ""

# 2. Check for PRs with no activity >7 days
echo "🔍 Checking for PRs with no activity >7 days..."
stale_prs=$(jq -r '.[] | select(.isDraft == false) | "\(.number)|\(.title)|\(.updatedAt)|\(.author.login)"' /tmp/all_open_prs.json)

if [ -n "$stale_prs" ]; then
  while IFS='|' read -r pr_num title updated_at author; do
    days_stale=$(days_since "$updated_at")
    
    if [ "$days_stale" -gt "$NO_ACTIVITY_DAYS_THRESHOLD" ]; then
      # Check if it has tech-lead-approved label (if so, skip - it's waiting for merge)
      has_approved=$(gh pr view "${pr_num}" --json labels --jq '.labels[] | select(.name == "tech-lead-approved") | .name' 2>/dev/null || echo "")
      
      if [ -z "$has_approved" ]; then
        echo "   ⏰ PR #${pr_num} (${author}): ${days_stale} days no activity"
        close_pr_with_reason \
          "${pr_num}" \
          "No activity for ${days_stale} days" \
          "This PR has had no commits, comments, or reviews for ${days_stale} days.

**Why closing:**
- No progress or updates for more than ${NO_ACTIVITY_DAYS_THRESHOLD} days
- Likely abandoned or author unavailable
- Consuming attention in PR list
- Signal-to-noise ratio degrading

**What this means:**
- Work may be resumed if still relevant
- May need rebasing on latest main
- Author can re-open if actively working on this" \
          "true"
        prs_closed_no_activity=$((prs_closed_no_activity + 1))
      fi
    fi
  done <<< "$stale_prs"
fi

echo "   Closed ${prs_closed_no_activity} PRs with no activity"
echo ""

# 3. Check for draft PRs >7 days old
echo "🔍 Checking for abandoned draft PRs >7 days..."
draft_prs=$(jq -r '.[] | select(.isDraft == true) | "\(.number)|\(.title)|\(.createdAt)|\(.author.login)"' /tmp/all_open_prs.json)

if [ -n "$draft_prs" ]; then
  while IFS='|' read -r pr_num title created_at author; do
    days_old=$(days_since "$created_at")
    
    if [ "$days_old" -gt "$DRAFT_DAYS_THRESHOLD" ]; then
      echo "   📝 Draft PR #${pr_num} (${author}): ${days_old} days old"
      close_pr_with_reason \
        "${pr_num}" \
        "Draft PR abandoned for ${days_old} days" \
        "This draft PR has been open for ${days_old} days without being marked ready for review.

**Why closing:**
- Draft for more than ${DRAFT_DAYS_THRESHOLD} days
- No indication of active work
- Cluttering PR list
- Work may be obsolete or deprioritized

**What this means:**
- Draft can be re-opened if work resumes
- May need updating with latest main
- Author should mark as ready when complete" \
        "true"
      prs_closed_draft=$((prs_closed_draft + 1))
    fi
  done <<< "$draft_prs"
fi

echo "   Closed ${prs_closed_draft} draft PRs"
echo ""

# 4. Check for orphaned PRs (linked issue closed)
echo "🔍 Checking for orphaned PRs (linked issue closed)..."
# This requires checking PR body for issue references and checking issue state
# Implementation: scan PR body for #\d+ patterns and check if those issues are closed

all_prs=$(jq -r '.[] | "\(.number)"' /tmp/all_open_prs.json)

if [ -n "$all_prs" ]; then
  while read -r pr_num; do
    # Get PR body
    pr_body=$(gh pr view "${pr_num}" --json body --jq '.body' 2>/dev/null || echo "")
    
    # Extract issue numbers (look for #123 patterns or "Fixes #123" or "Closes #123")
    # Using case-insensitive matching
    linked_issues=$(echo "$pr_body" | grep -oiP '(?:Fixes|Closes|Resolves|Fix|Close|Resolve)\s+#\K\d+' | sort -u || echo "")
    
    if [ -n "$linked_issues" ]; then
      while read -r issue_num; do
        issue_state=$(gh issue view "${issue_num}" --json state --jq '.state' 2>/dev/null || echo "")
        
        if [ "$issue_state" = "CLOSED" ]; then
          echo "   🔗 PR #${pr_num}: Linked issue #${issue_num} is closed"
          close_pr_with_reason \
            "${pr_num}" \
            "Linked issue #${issue_num} is closed" \
            "This PR was created to address issue #${issue_num}, which has been closed.

**Why closing:**
- Work may have been completed in another PR
- Issue was closed as won't-fix or duplicate
- PR is no longer needed
- Reduces orphaned PRs

**What this means:**
- If work is still needed, re-open the issue first
- Then create a new PR referencing the issue
- Original work here may be obsolete" \
            "true"
          prs_closed_orphaned=$((prs_closed_orphaned + 1))
          break  # Only need to find one closed issue
        fi
      done <<< "$linked_issues"
    fi
  done <<< "$all_prs"
fi

echo "   Closed ${prs_closed_orphaned} orphaned PRs"
echo ""

# Summary
total_closed=$((prs_closed_conflicts + prs_closed_no_activity + prs_closed_orphaned + prs_closed_draft))

echo "========================================="
echo "Cleanup Summary"
echo "========================================="
echo ""
echo "PRs checked: ${total_prs}"
echo ""
echo "Closed by reason:"
echo "  - Merge conflicts (>3h): ${prs_closed_conflicts}"
echo "  - No activity (>7d): ${prs_closed_no_activity}"
echo "  - Orphaned (closed issue): ${prs_closed_orphaned}"
echo "  - Abandoned draft (>7d): ${prs_closed_draft}"
echo ""
echo "Total closed: ${total_closed}"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo "ℹ️  This was a dry run - no PRs were actually closed"
  echo "   Run without --dry-run to execute cleanup"
fi

echo ""
echo "✅ Cleanup complete"

# Output JSON summary for programmatic consumption
# This enables workflow to extract counts reliably
cat > /tmp/cleanup_summary.json <<EOF
{
  "total_prs_checked": ${total_prs},
  "total_closed": ${total_closed},
  "by_reason": {
    "merge_conflicts": ${prs_closed_conflicts},
    "no_activity": ${prs_closed_no_activity},
    "orphaned": ${prs_closed_orphaned},
    "abandoned_draft": ${prs_closed_draft}
  },
  "dry_run": ${DRY_RUN}
}
EOF

echo ""
echo "📊 JSON summary written to /tmp/cleanup_summary.json"

exit 0
