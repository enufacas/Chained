#!/bin/bash
#
# Quick Fix Script for Workflow Label Issues
# Created by @troubleshoot-expert
#
# This script helps resolve workflow failures caused by missing repository labels
#

set -e

echo "🔧 Workflow Label Fix Script"
echo "=============================="
echo ""
echo "Created by @troubleshoot-expert"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo ""
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    echo ""
    echo "Please run this script from the Chained repository root"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "⚠️  Warning: Not authenticated with GitHub CLI"
    echo ""
    echo "Attempting to authenticate..."
    gh auth login
fi

echo "✅ Prerequisites check passed"
echo ""

# Option 1: Run the label creation tool locally
echo "Option 1: Run label creation tool locally"
echo "-----------------------------------------"
echo ""

if [ -f "tools/create_labels.py" ]; then
    echo "Found tools/create_labels.py"
    echo ""
    read -p "Run label creation tool now? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🏷️  Creating repository labels..."
        echo ""
        
        python3 tools/create_labels.py --all
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Labels created successfully!"
        else
            echo ""
            echo "⚠️  Some labels may have failed (see output above)"
            echo "   This is usually okay if most labels were created"
        fi
    fi
else
    echo "❌ tools/create_labels.py not found"
    echo "   Make sure you're in the repository root"
fi

echo ""
echo "Option 2: Trigger the workflow via GitHub Actions"
echo "--------------------------------------------------"
echo ""
echo "You can also trigger the 'Maintenance: Ensure Repository Labels Exist' workflow:"
echo ""
echo "1. Go to: https://github.com/enufacas/Chained/actions/workflows/ensure-labels-exist.yml"
echo "2. Click 'Run workflow'"
echo "3. Click 'Run workflow' again to confirm"
echo "4. Wait ~30 seconds for completion"
echo ""

read -p "Open workflow page in browser? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Try different methods to open the browser
    if command -v xdg-open &> /dev/null; then
        xdg-open "https://github.com/enufacas/Chained/actions/workflows/ensure-labels-exist.yml"
    elif command -v open &> /dev/null; then
        open "https://github.com/enufacas/Chained/actions/workflows/ensure-labels-exist.yml"
    elif command -v start &> /dev/null; then
        start "https://github.com/enufacas/Chained/actions/workflows/ensure-labels-exist.yml"
    else
        echo "Could not open browser automatically."
        echo "Please visit: https://github.com/enufacas/Chained/actions/workflows/ensure-labels-exist.yml"
    fi
fi

echo ""
echo "Verification"
echo "------------"
echo ""
echo "To verify labels were created, run:"
echo ""
echo "  gh label list | grep -E \"code-quality|workflow-optimization|investment-tracker\""
echo ""

read -p "Verify labels now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔍 Checking for critical labels..."
    echo ""
    
    CRITICAL_LABELS=("code-quality" "workflow-optimization" "investment-tracker" "agent-system" "automated" "copilot" "learning")
    FOUND=0
    MISSING=0
    
    for label in "${CRITICAL_LABELS[@]}"; do
        if gh label list | grep -q "^${label}"; then
            echo "✅ ${label}"
            ((FOUND++))
        else
            echo "❌ ${label} - MISSING"
            ((MISSING++))
        fi
    done
    
    echo ""
    echo "Summary: ${FOUND}/${#CRITICAL_LABELS[@]} critical labels found"
    
    if [ $MISSING -eq 0 ]; then
        echo ""
        echo "🎉 All critical labels exist!"
        echo ""
        echo "Workflows should now work correctly."
    else
        echo ""
        echo "⚠️  ${MISSING} labels are still missing"
        echo ""
        echo "Recommendation:"
        echo "1. Run the label creation tool again (Option 1)"
        echo "2. Or trigger the workflow (Option 2)"
        echo "3. Or create missing labels manually:"
        echo ""
        echo "   gh label create <name> --description \"Description\" --color \"HEX\""
    fi
fi

echo ""
echo "================================================"
echo "✅ Workflow Label Fix Script Complete"
echo ""
echo "Next Steps:"
echo "1. Verify labels exist (see above)"
echo "2. Re-run any failed workflows"
echo "3. Monitor workflow health for 24-48 hours"
echo ""
echo "Need help? Check .github/workflows/TROUBLESHOOTING.md"
echo ""
echo "Created by @troubleshoot-expert 🔧"
echo "================================================"
