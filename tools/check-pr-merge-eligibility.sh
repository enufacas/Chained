#!/bin/bash
# Check PR Auto-Merge Eligibility (Deterministic)
# 
# Usage: check-pr-merge-eligibility.sh <PR_NUMBER>
# Exit codes:
#   0 = ELIGIBLE for auto-merge
#   1 = NOT ELIGIBLE (with reason)
#
# This script implements the deterministic eligibility criteria from
# .github/agents/meta-coordinator-system.md

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <PR_NUMBER>" >&2
    exit 1
fi

PR_NUM=$1
REPO_OWNER="${GITHUB_REPOSITORY_OWNER:-enufacas}"

# Get all PR data in one call
pr_data=$(gh pr view "$PR_NUM" --json state,isDraft,mergeable,author,title,statusCheckRollup)

# Extract fields
pr_state=$(echo "$pr_data" | jq -r '.state')
is_draft=$(echo "$pr_data" | jq -r '.isDraft')
pr_title=$(echo "$pr_data" | jq -r '.title')
mergeable=$(echo "$pr_data" | jq -r '.mergeable')
author=$(echo "$pr_data" | jq -r '.author.login')
ci_checks=$(echo "$pr_data" | jq '.statusCheckRollup')

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PR #${PR_NUM} Eligibility Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Title: ${pr_title:0:60}..."
echo "Author: $author"
echo "Draft: $is_draft"
echo "Mergeable: $mergeable"
echo ""

# STEP 1: Check if PR is open
echo "STEP 1: Check state..."
if [ "${pr_state}" != "OPEN" ]; then
    echo "  ❌ FAIL: Not open (state: ${pr_state})"
    if [ "${is_draft}" = "true" ]; then
        echo "  Note: Closed draft PRs are never eligible (already closed)"
    fi
    exit 1
fi
echo "  ✅ PASS: PR is open"
if [ "${is_draft}" = "true" ]; then
    echo "  Note: Draft PR (will check WIP markers in next step)"
fi
echo ""

# STEP 2: Check for WIP markers in title (CRITICAL - ALWAYS BLOCKS)
echo "STEP 2: Check for WIP markers in title..."
if echo "$pr_title" | grep -qiE '\[WIP\]|^WIP:|WIP\s|work[\.\s]in[\.\s]progress|\[do[\.\s]not[\.\s]merge\]|\[dnm\]'; then
    echo "  ❌ FAIL: Has WIP marker in title"
    if [ "${is_draft}" = "true" ]; then
        echo "  Note: Draft PRs with WIP markers are not eligible"
    else
        echo "  Note: Non-draft PRs with WIP markers are not eligible"
    fi
    echo "  Note: WIP markers block regardless of draft state"
    exit 1
fi
echo "  ✅ PASS: No WIP markers in title"
if [ "${is_draft}" = "true" ]; then
    echo "  Note: Draft PR without WIP marker - eligible for processing"
fi
echo ""

# STEP 3: Verify trusted author (CRITICAL - SECURITY)
echo "STEP 3: Verify trusted author..."
is_trusted=false

if [ "${author}" = "${REPO_OWNER}" ]; then
    is_trusted=true
    echo "  ✅ PASS: Repository owner (${author})"
elif echo "${author}" | grep -qiE "^app/copilot|^copilot|^github-actions"; then
    is_trusted=true
    echo "  ✅ PASS: Trusted bot (${author})"
fi

if [ "${is_trusted}" = "false" ]; then
    echo "  ❌ FAIL: Not from trusted author (${author})"
    echo "  Note: Only owner or copilot/github-actions allowed"
    exit 1
fi
echo ""

# STEP 4: Mark draft PRs as ready (ALWAYS - triggers status calculation)
echo "STEP 4: Handle draft status..."
if [ "${is_draft}" = "true" ]; then
    echo "  ⚠️  PR is draft - marking as ready (required for auto-merge)..."
    echo "  → Original mergeable status: ${mergeable}"
    
    if gh pr ready "${PR_NUM}" 2>/dev/null; then
        echo "  → Marked as ready successfully"
        echo "  → Waiting 2 seconds for GitHub to update merge status..."
        sleep 2
        # Re-fetch mergeable status after marking ready
        mergeable_after=$(gh pr view "$PR_NUM" --json mergeable --jq -r '.mergeable')
        echo "  → Updated mergeable status: ${mergeable_after}"
        
        # Update mergeable variable for next check
        mergeable="$mergeable_after"
    else
        # Verify if it's already ready (expected) or an actual error
        is_still_draft=$(gh pr view "$PR_NUM" --json isDraft --jq -r '.isDraft')
        if [ "$is_still_draft" = "false" ]; then
            echo "  ℹ️  PR was already marked ready (no action needed)"
        else
            echo "  ⚠️  Failed to mark ready - possible network/permission issue"
            echo "  → Continuing with existing status: ${mergeable}"
        fi
    fi
else
    echo "  ✅ PASS: Not a draft (no action needed)"
fi
echo ""

# STEP 5: Check mergeable status
echo "STEP 5: Check mergeable status..."
if [ "${mergeable}" = "MERGEABLE" ]; then
    echo "  ✅ PASS: Mergeable"
elif [ "${mergeable}" = "CONFLICTING" ]; then
    echo "  ❌ FAIL: Has merge conflicts"
    exit 1
elif [ "${mergeable}" = "UNKNOWN" ]; then
    echo "  ❌ FAIL: Status still UNKNOWN"
    echo "  Note: GitHub may still be calculating - try again in a moment"
    exit 1
else
    echo "  ❌ FAIL: Unexpected status (${mergeable})"
    exit 1
fi
echo ""

# STEP 6: Check CI status (optional - unavailable is OK)
echo "STEP 6: Check CI status..."
if [ "$ci_checks" = "[]" ] || [ "$ci_checks" = "null" ]; then
    echo "  ✅ PASS: No CI checks configured (OK)"
else
    total_checks=$(echo "$ci_checks" | jq 'length')
    failed=$(echo "$ci_checks" | jq '[.[] | select(.state != "SUCCESS")] | length')
    
    if [ "$failed" = "0" ]; then
        echo "  ✅ PASS: All $total_checks CI checks passed"
    else
        echo "  ❌ FAIL: $failed/$total_checks CI checks failed"
        exit 1
    fi
fi
echo ""

# ALL CHECKS PASSED
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 RESULT: ELIGIBLE FOR AUTO-MERGE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
exit 0
