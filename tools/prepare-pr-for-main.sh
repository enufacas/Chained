#!/bin/bash
# Script to help prepare PR for targeting main branch

set -e

echo "============================================"
echo "PR Target Branch Verification & Preparation"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "copilot/investigate-copilot-error" ]; then
    echo -e "${RED}ERROR: Not on copilot/investigate-copilot-error branch${NC}"
    echo "Run: git checkout copilot/investigate-copilot-error"
    exit 1
fi

# Fetch latest from origin
echo ""
echo "Fetching latest from origin..."
git fetch origin main

# Check if main exists
if ! git rev-parse origin/main >/dev/null 2>&1; then
    echo -e "${RED}ERROR: origin/main branch not found${NC}"
    exit 1
fi

# Show branch divergence
echo ""
echo "Branch Analysis:"
echo "---------------"

MERGE_BASE=$(git merge-base HEAD origin/main)
echo "Common ancestor: $MERGE_BASE"

AHEAD=$(git rev-list --count $MERGE_BASE..HEAD)
echo "Commits ahead of main: $AHEAD"

BEHIND=$(git rev-list --count HEAD..$MERGE_BASE)
echo "Commits behind main: $BEHIND"

# Show commit log
echo ""
echo "Commits in this PR:"
echo "-------------------"
git log --oneline $MERGE_BASE..HEAD

# Check for conflicts
echo ""
echo "Checking for potential merge conflicts..."
if git merge-tree $MERGE_BASE HEAD origin/main | grep -q '^changed in both'; then
    echo -e "${YELLOW}WARNING: Potential merge conflicts detected${NC}"
    echo "Review conflicts before changing PR target"
else
    echo -e "${GREEN}✅ No obvious conflicts detected${NC}"
fi

# Show instruction file sizes
echo ""
echo "Current instruction file sizes:"
echo "-------------------------------"
if [ -d .github/instructions ]; then
    TOTAL_SIZE=$(find .github/instructions -name "*.md" -type f -exec cat {} \; | wc -c)
    TOTAL_KB=$((TOTAL_SIZE / 1024))
    echo "Total: ${TOTAL_SIZE} bytes (${TOTAL_KB} KB)"
    
    if [ -f .copilot-instructions.md ]; then
        ROOT_SIZE=$(wc -c < .copilot-instructions.md)
        TOTAL_WITH_ROOT=$((TOTAL_SIZE + ROOT_SIZE))
        echo "With .copilot-instructions.md: ${TOTAL_WITH_ROOT} bytes ($((TOTAL_WITH_ROOT / 1024)) KB)"
    fi
    
    if [ $TOTAL_SIZE -gt 60000 ]; then
        echo -e "${RED}⚠️  WARNING: Instruction size exceeds 60KB limit!${NC}"
    else
        echo -e "${GREEN}✅ Instruction size within limits${NC}"
    fi
fi

# Check if .copilot-instructions.md exists
echo ""
echo "File verification:"
echo "------------------"
if [ -f .copilot-instructions.md ]; then
    LINES=$(wc -l < .copilot-instructions.md)
    SIZE=$(wc -c < .copilot-instructions.md)
    echo -e "${GREEN}✅ .copilot-instructions.md exists${NC}"
    echo "   Lines: $LINES"
    echo "   Size: $SIZE bytes"
else
    echo -e "${RED}❌ .copilot-instructions.md NOT FOUND${NC}"
fi

# Show what's different from main
echo ""
echo "Files changed compared to main:"
echo "--------------------------------"
git diff --name-status origin/main..HEAD | head -20

# Recommendations
echo ""
echo "============================================"
echo "Recommendations:"
echo "============================================"
echo ""
echo "1. Change PR target branch to 'main' via GitHub web UI"
echo "   https://github.com/enufacas/Chained/pulls"
echo ""
echo "2. Or use GitHub CLI (if authenticated):"
echo "   gh pr list --head copilot/investigate-copilot-error"
echo "   gh pr edit <PR_NUMBER> --base main"
echo ""
echo "3. After changing target, verify the PR shows correct diff"
echo ""

# Optional: Offer to rebase
echo ""
read -p "Do you want to rebase on latest main now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Rebasing on origin/main..."
    git rebase origin/main
    echo ""
    echo -e "${GREEN}✅ Rebase completed${NC}"
    echo ""
    echo "Push with: git push --force-with-lease origin copilot/investigate-copilot-error"
else
    echo ""
    echo "Skipping rebase. You can rebase later with:"
    echo "  git rebase origin/main"
    echo "  git push --force-with-lease origin copilot/investigate-copilot-error"
fi

echo ""
echo "============================================"
echo "Next Steps:"
echo "============================================"
echo "1. Change PR base to 'main' on GitHub"
echo "2. Verify PR shows correct changes"
echo "3. Merge PR to fix main branch"
echo "4. Test Copilot workflow on main"
echo ""
