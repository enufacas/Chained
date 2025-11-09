#!/bin/bash

# Chained System Pre-Flight Validation Script
# This script validates that the perpetual AI motion machine is properly configured

set -e

echo "🤖 Chained System Validation"
echo "============================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to print status
print_status() {
    if [ "$1" = "OK" ]; then
        echo -e "${GREEN}✓${NC} $2"
    elif [ "$1" = "WARN" ]; then
        echo -e "${YELLOW}⚠${NC} $2"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${RED}✗${NC} $2"
        ERRORS=$((ERRORS + 1))
    fi
}

echo "1. Checking Repository Structure..."
echo "-----------------------------------"

# Check if essential directories exist
if [ -d ".github/workflows" ]; then
    print_status "OK" "Workflows directory exists"
else
    print_status "ERROR" "Workflows directory missing"
fi

if [ -d "docs" ]; then
    print_status "OK" "Documentation directory exists"
else
    print_status "ERROR" "Documentation directory missing"
fi

if [ -d "learnings" ]; then
    print_status "OK" "Learnings directory exists"
else
    print_status "WARN" "Learnings directory missing (will be created by workflows)"
fi

echo ""
echo "2. Checking Workflow Files..."
echo "------------------------------"

# Essential workflows
declare -A workflows=(
    ["idea-generator.yml"]="AI Idea Generator"
    ["smart-idea-generator.yml"]="Smart Idea Generator"
    ["copilot-assign.yml"]="Copilot Auto-Assign"
    ["issue-to-pr.yml"]="Issue to PR Automator"
    ["auto-review-merge.yml"]="Auto Review and Merge"
    ["auto-close-issues.yml"]="Auto Close Issues"
    ["timeline-updater.yml"]="Timeline Updater"
    ["progress-tracker.yml"]="Progress Tracker"
    ["learn-from-tldr.yml"]="Learn from TLDR"
    ["learn-from-hackernews.yml"]="Learn from Hacker News"
    ["system-kickoff.yml"]="System Kickoff"
    ["auto-kickoff.yml"]="Auto Kickoff on First Run"
)

for workflow in "${!workflows[@]}"; do
    if [ -f ".github/workflows/$workflow" ]; then
        print_status "OK" "${workflows[$workflow]} workflow exists"
    else
        print_status "ERROR" "${workflows[$workflow]} workflow missing"
    fi
done

echo ""
echo "3. Checking Documentation Files..."
echo "----------------------------------"

docs=("README.md" "QUICKSTART.md" "CONFIGURATION.md" "COPILOT_VISION.md" "IMPLEMENTATION_COMPLETE.md")
for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        print_status "OK" "$doc exists"
    else
        print_status "WARN" "$doc missing"
    fi
done

echo ""
echo "4. Checking GitHub Pages Configuration..."
echo "-----------------------------------------"

if [ -f "docs/index.html" ]; then
    print_status "OK" "GitHub Pages index.html exists"
else
    print_status "ERROR" "GitHub Pages index.html missing"
fi

if [ -f "docs/style.css" ]; then
    print_status "OK" "GitHub Pages stylesheet exists"
else
    print_status "ERROR" "GitHub Pages stylesheet missing"
fi

if [ -f "docs/script.js" ]; then
    print_status "OK" "GitHub Pages JavaScript exists"
else
    print_status "ERROR" "GitHub Pages JavaScript missing"
fi

echo ""
echo "5. Checking Git Configuration..."
echo "--------------------------------"

# Check if git is configured
if git config user.email >/dev/null 2>&1; then
    print_status "OK" "Git user email configured"
else
    print_status "WARN" "Git user email not configured (needed for commits)"
fi

if git config user.name >/dev/null 2>&1; then
    print_status "OK" "Git user name configured"
else
    print_status "WARN" "Git user name not configured (needed for commits)"
fi

echo ""
echo "6. Checking GitHub CLI (if available)..."
echo "----------------------------------------"

if command -v gh &> /dev/null; then
    print_status "OK" "GitHub CLI (gh) is installed"
    
    # Check if gh is authenticated
    if gh auth status &> /dev/null; then
        print_status "OK" "GitHub CLI is authenticated"
    else
        print_status "WARN" "GitHub CLI not authenticated (run 'gh auth login')"
    fi
else
    print_status "WARN" "GitHub CLI (gh) not installed (needed for manual testing)"
fi

echo ""
echo "7. Workflow Syntax Validation..."
echo "--------------------------------"

# Validate YAML syntax if yamllint is available
if command -v yamllint &> /dev/null; then
    yaml_errors=0
    for workflow in .github/workflows/*.yml; do
        # Use relaxed yamllint config to avoid false positives
        if yamllint -d "{extends: relaxed, rules: {line-length: {max: 200}}}" "$workflow" >/dev/null 2>&1; then
            print_status "OK" "$(basename $workflow) has valid syntax"
        else
            print_status "WARN" "$(basename $workflow) has style issues (not critical)"
            # Don't count style issues as errors
        fi
    done
else
    print_status "WARN" "yamllint not available (skipping YAML validation)"
fi

echo ""
echo "8. Checking Python (for learning workflows)..."
echo "----------------------------------------------"

if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1)
    print_status "OK" "Python 3 is installed: $python_version"
else
    print_status "ERROR" "Python 3 not installed (required for learning workflows)"
fi

echo ""
echo "================================================================"
echo "Validation Summary"
echo "================================================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Your Chained system is ready to go! 🚀"
    echo ""
    echo "Next steps:"
    echo "  1. Run './kickoff-system.sh' to start the autonomous system"
    echo "  2. Or manually trigger workflows in the GitHub Actions tab"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validation completed with $WARNINGS warning(s)${NC}"
    echo ""
    echo "Your system should work, but review the warnings above."
    echo "You can proceed with './kickoff-system.sh' if warnings are acceptable."
    echo ""
    exit 0
else
    echo -e "${RED}✗ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo ""
    echo "Please fix the errors above before starting the system."
    echo ""
    exit 1
fi
