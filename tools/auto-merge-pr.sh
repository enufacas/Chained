#!/bin/bash
# Auto-Merge PR Script (Comprehensive & Deterministic)
#
# This script is the SINGLE SOURCE OF TRUTH for PR auto-merge logic.
# It encapsulates ALL eligibility checks and merge execution in one place.
#
# Usage:
#   ./tools/auto-merge-pr.sh <PR_NUMBER> [--dry-run]
#
# Exit codes:
#   0 - PR was merged successfully
#   1 - PR not eligible (see output for reason)
#   2 - Merge failed (PR was eligible but merge command failed)
#   3 - Usage error
#
# Output:
#   - Human-readable eligibility decision
#   - Structured JSON for programmatic use (optional)

set -euo pipefail

# Configuration
PR_NUM=""
DRY_RUN=false
JSON_OUTPUT=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --json)
      JSON_OUTPUT=true
      shift
      ;;
    -*)
      echo "Unknown option: $1"
      echo "Usage: $0 <PR_NUMBER> [--dry-run] [--json]"
      exit 3
      ;;
    *)
      if [ -z "$PR_NUM" ]; then
        PR_NUM=$1
      else
        echo "Error: Multiple PR numbers provided"
        exit 3
      fi
      shift
      ;;
  esac
done

if [ -z "$PR_NUM" ]; then
  echo "Usage: $0 <PR_NUMBER> [--dry-run] [--json]"
  exit 3
fi

# Ensure GH_TOKEN is set
if [ -z "${GH_TOKEN:-}" ]; then
  echo "ERROR: GH_TOKEN environment variable must be set"
  exit 3
fi

REPO_OWNER="${GITHUB_REPOSITORY_OWNER:-enufacas}"

# Initialize result structure
ELIGIBLE=false
REASON=""
ACTION_TAKEN=""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Auto-Merge PR #${PR_NUM}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
if [ "$DRY_RUN" = true ]; then
  echo "🔍 DRY RUN MODE - No changes will be made"
  echo ""
fi

# Get all PR data in one call
echo "📥 Fetching PR data..."
pr_data=$(gh pr view "$PR_NUM" --json state,isDraft,mergeable,author,title,statusCheckRollup,headRefName,createdAt)

# Extract fields
pr_state=$(echo "$pr_data" | jq -r '.state')
is_draft=$(echo "$pr_data" | jq -r '.isDraft')
pr_title=$(echo "$pr_data" | jq -r '.title')
mergeable=$(echo "$pr_data" | jq -r '.mergeable')
author=$(echo "$pr_data" | jq -r '.author.login')
ci_checks=$(echo "$pr_data" | jq '.statusCheckRollup')
branch_name=$(echo "$pr_data" | jq -r '.headRefName')
created_at=$(echo "$pr_data" | jq -r '.createdAt')

echo "PR Details:"
echo "  Title: ${pr_title:0:60}..."
echo "  Author: $author"
echo "  State: $pr_state"
echo "  Draft: $is_draft"
echo "  Mergeable: $mergeable"
echo "  Branch: $branch_name"
echo ""

# ELIGIBILITY CHECKS (in priority order)

# CHECK 1: PR must be OPEN
echo "✓ Check 1: PR State"
if [ "${pr_state}" != "OPEN" ]; then
  REASON="PR is not open (state: ${pr_state})"
  echo "  ❌ FAIL: ${REASON}"
  ELIGIBLE=false
else
  echo "  ✅ PASS: PR is open"
  
  # CHECK 2: No WIP markers in title (BLOCKS regardless of draft status)
  echo "✓ Check 2: WIP Markers"
  if echo "$pr_title" | grep -qiE '\[WIP\]|^WIP:|WIP\s|work[\.\s]in[\.\s]progress|\[do[\.\s]not[\.\s]merge\]|\[dnm\]'; then
    REASON="PR title contains WIP marker (blocks merge regardless of draft status)"
    echo "  ❌ FAIL: ${REASON}"
    echo "  Note: Remove WIP marker from title to become eligible"
    ELIGIBLE=false
  else
    echo "  ✅ PASS: No WIP markers"
    
    # CHECK 3: Trusted author (security requirement)
    echo "✓ Check 3: Trusted Author"
    is_trusted=false
    
    if [ "${author}" = "${REPO_OWNER}" ]; then
      is_trusted=true
      echo "  ✅ PASS: Repository owner (${author})"
    elif echo "${author}" | grep -qiE "^app/copilot|^copilot|^app/github-actions|^github-actions\[bot\]"; then
      is_trusted=true
      echo "  ✅ PASS: Trusted bot (${author})"
    else
      REASON="Author not trusted (only owner or copilot/github-actions allowed)"
      echo "  ❌ FAIL: ${REASON}"
      ELIGIBLE=false
    fi
    
    if [ "$is_trusted" = true ]; then
      # STEP 4: Handle draft status (mark ready if needed)
      echo "✓ Check 4: Draft Status"
      if [ "${is_draft}" = "true" ]; then
        echo "  ⚠️  PR is draft - marking as ready for merge status calculation..."
        
        if [ "$DRY_RUN" = false ]; then
          if gh pr ready "${PR_NUM}" 2>/dev/null; then
            echo "  → Marked as ready successfully"
            # Wait for GitHub's merge status calculation
            # Give GitHub time to compute merge status after marking ready
            sleep 5
            mergeable=$(gh pr view "$PR_NUM" --json mergeable | jq -r '.mergeable')
            echo "  → Updated mergeable status: ${mergeable}"
            
            # Note: Further UNKNOWN retries happen in Check 5 below
          else
            # Check if already ready
            is_still_draft=$(gh pr view "$PR_NUM" --json isDraft | jq -r '.isDraft')
            if [ "$is_still_draft" = "false" ]; then
              echo "  ℹ️  Already marked ready"
              mergeable=$(gh pr view "$PR_NUM" --json mergeable | jq -r '.mergeable')
            else
              echo "  ⚠️  Could not mark ready (may be permissions issue)"
            fi
          fi
        else
          echo "  → [DRY RUN] Would mark as ready"
        fi
      else
        echo "  ✅ PASS: Not a draft"
      fi
      
      # CHECK 5: Mergeable status (with retry for UNKNOWN)
      echo "✓ Check 5: Mergeable Status"
      
      # Retry logic for UNKNOWN status (GitHub needs time to calculate)
      if [ "${mergeable}" = "UNKNOWN" ]; then
        echo "  ⏳ Status is UNKNOWN - GitHub still calculating"
        echo "     Waiting for merge status to be computed..."
        
        max_retries=4
        retry_count=0
        wait_times=(5 8 12 15)  # Progressive backoff: 5s, 8s, 12s, 15s = 40s total
        
        while [ "${mergeable}" = "UNKNOWN" ] && [ $retry_count -lt $max_retries ]; do
          wait_time=${wait_times[$retry_count]}
          echo "     Attempt $((retry_count + 1))/${max_retries}: Waiting ${wait_time}s..."
          sleep ${wait_time}
          
          # Re-fetch mergeable status
          mergeable=$(gh pr view "$PR_NUM" --json mergeable | jq -r '.mergeable')
          echo "     → Status after wait: ${mergeable}"
          
          retry_count=$((retry_count + 1))
        done
        
        # Final evaluation after retries
        if [ "${mergeable}" = "UNKNOWN" ]; then
          echo "  ⚠️  Status still UNKNOWN after ${max_retries} retries (40s total)"
          echo "     This PR may need more time or manual inspection"
        fi
      fi
      
      # Now check the final mergeable status
      if [ "${mergeable}" = "MERGEABLE" ]; then
        echo "  ✅ PASS: PR is mergeable"
        
        # CHECK 6: CI checks
        echo "✓ Check 6: CI Status"
        if [ "$ci_checks" = "[]" ] || [ "$ci_checks" = "null" ]; then
          echo "  ✅ PASS: No CI checks configured"
          ELIGIBLE=true
        else
          total_checks=$(echo "$ci_checks" | jq 'length')
          failed=$(echo "$ci_checks" | jq '[.[] | select(.state != "SUCCESS")] | length')
          
          if [ "$failed" = "0" ]; then
            echo "  ✅ PASS: All ${total_checks} CI checks passed"
            ELIGIBLE=true
          else
            REASON="CI checks failed (${failed}/${total_checks})"
            echo "  ❌ FAIL: ${REASON}"
            ELIGIBLE=false
          fi
        fi
      elif [ "${mergeable}" = "CONFLICTING" ]; then
        REASON="PR has merge conflicts"
        echo "  ❌ FAIL: ${REASON}"
        ELIGIBLE=false
      elif [ "${mergeable}" = "UNKNOWN" ]; then
        REASON="Mergeable status still UNKNOWN after waiting 40s (GitHub needs more time)"
        echo "  ❌ FAIL: ${REASON}"
        echo "  Note: This PR will be retried in the next run (every 2 hours)"
        echo "        GitHub may need more time to calculate merge status"
        ELIGIBLE=false
      else
        REASON="Unexpected mergeable status: ${mergeable}"
        echo "  ❌ FAIL: ${REASON}"
        ELIGIBLE=false
      fi
    fi
  fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# MERGE EXECUTION
if [ "$ELIGIBLE" = true ]; then
  echo "🎯 ELIGIBLE FOR AUTO-MERGE"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  if [ "$DRY_RUN" = false ]; then
    echo "🔀 Attempting merge..."
    
    # Try immediate merge first
    if gh pr merge "${PR_NUM}" --squash --delete-branch 2>/dev/null; then
      ACTION_TAKEN="merged_immediate"
      echo "✅ Merged successfully (immediate)"
      echo ""
      echo "Branch '${branch_name}' deleted"
    else
      # Fallback to auto-merge (queued)
      echo "⚠️  Immediate merge failed, enabling auto-merge..."
      if gh pr merge "${PR_NUM}" --auto --squash --delete-branch 2>/dev/null; then
        ACTION_TAKEN="merged_queued"
        echo "✅ Auto-merge enabled (queued)"
        echo "   PR will merge automatically when checks complete"
      else
        ACTION_TAKEN="merge_failed"
        echo "❌ Merge failed"
        echo "   Check PR status manually"
        exit 2
      fi
    fi
    
    # Post success comment
    gh pr comment "${PR_NUM}" --body "## ✅ Auto-Merged

This PR met all eligibility criteria and was automatically merged.

**Eligibility Checks:**
- ✅ Open state
- ✅ No WIP markers
- ✅ Trusted author (${author})
- ✅ Mergeable status
- ✅ CI checks passed

**Created:** ${created_at}  
**Merged:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")

*Automated by @meta-coordinator-system*
" || echo "⚠️  Could not post success comment"
    
  else
    echo "[DRY RUN] Would merge PR #${PR_NUM}"
    ACTION_TAKEN="would_merge"
  fi
  
  exit 0
else
  echo "❌ NOT ELIGIBLE FOR AUTO-MERGE"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "Reason: ${REASON}"
  echo ""
  echo "To become eligible:"
  echo "  1. Ensure PR is open"
  echo "  2. Remove any WIP markers from title"
  echo "  3. Resolve any merge conflicts"
  echo "  4. Ensure all CI checks pass"
  ACTION_TAKEN="not_eligible"
  exit 1
fi
