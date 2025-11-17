#!/bin/bash
#
# Commit Verification Script
# Usage: ./verify_commit.sh <commit_sha>
#
# This script verifies if a commit exists in the repository and which branches contain it.

set -e

COMMIT_SHA=$1

if [ -z "$COMMIT_SHA" ]; then
    echo "Usage: $0 <commit_sha>"
    echo "Example: $0 201c2090c02b819fa5f40b3fb36b2af906903407"
    exit 1
fi

echo "═══════════════════════════════════════════════════════"
echo "Commit Verification Tool"
echo "═══════════════════════════════════════════════════════"
echo "Commit SHA: $COMMIT_SHA"
echo "Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

# Check if commit exists
echo "Checking if commit exists..."
if git cat-file -e "$COMMIT_SHA" 2>/dev/null; then
    echo "✅ COMMIT FOUND"
    echo ""
    
    # Show commit details
    echo "Commit Details:"
    echo "─────────────────────────────────────────────────────"
    git show --no-patch --format="%H%nAuthor: %an <%ae>%nDate: %ad%nSubject: %s" "$COMMIT_SHA"
    echo ""
    
    # Check if in main branch
    echo "Checking if commit is in main branch..."
    if git merge-base --is-ancestor "$COMMIT_SHA" main 2>/dev/null; then
        echo "✅ COMMIT IS IN MAIN BRANCH"
    else
        echo "❌ COMMIT IS NOT IN MAIN BRANCH"
    fi
    echo ""
    
    # List all branches containing this commit
    echo "Branches containing this commit:"
    echo "─────────────────────────────────────────────────────"
    git branch -a --contains "$COMMIT_SHA" 2>/dev/null || echo "No branches found"
    echo ""
    
    # Show commit in log context
    echo "Commit in log context:"
    echo "─────────────────────────────────────────────────────"
    git log --oneline --graph --decorate -n 5 "$COMMIT_SHA"
    
else
    echo "❌ COMMIT NOT FOUND"
    echo ""
    echo "The commit $COMMIT_SHA does not exist in this repository."
    echo ""
    echo "Possible reasons:"
    echo "  1. Commit was removed via force push or rebase"
    echo "  2. Commit is in a different repository or fork"
    echo "  3. Commit SHA is incorrect or contains a typo"
    echo "  4. Repository needs to fetch latest changes (run: git fetch --all)"
    echo ""
    
    # Try to find similar commits
    echo "Searching for similar commit SHAs..."
    PREFIX="${COMMIT_SHA:0:7}"
    SIMILAR=$(git log --all --format="%H" | grep "^$PREFIX" || true)
    if [ -n "$SIMILAR" ]; then
        echo "Found commits with similar prefix ($PREFIX):"
        echo "$SIMILAR"
    else
        echo "No commits found with prefix $PREFIX"
    fi
    
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "Verification Complete"
echo "═══════════════════════════════════════════════════════"
