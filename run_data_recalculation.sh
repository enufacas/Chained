#!/bin/bash
# Run Data Recalculation - @investigate-champion
#
# This script runs the data recalculation with proper GitHub token.
# It should be run in an environment with GitHub API access.

set -e

echo "=========================================="
echo "Data Recalculation Script"
echo "By @investigate-champion"
echo "=========================================="
echo ""

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ] && [ -z "$GH_TOKEN" ]; then
    echo "❌ ERROR: No GitHub token found"
    echo ""
    echo "Please set GITHUB_TOKEN or GH_TOKEN environment variable:"
    echo "  export GITHUB_TOKEN=<your-token>"
    echo ""
    echo "To run in GitHub Actions workflow, use:"
    echo "  env:"
    echo "    GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}"
    exit 1
fi

# Set the token for the Python script
export GITHUB_TOKEN="${GITHUB_TOKEN:-$GH_TOKEN}"

echo "✅ GitHub token found"
echo "📊 Starting metrics recalculation..."
echo ""

# Run the recalculation script
python3 recalculate_all_metrics.py

echo ""
echo "=========================================="
echo "✅ Recalculation Complete"
echo "=========================================="
echo ""
echo "Changes have been made to:"
echo "  .github/agent-system/metrics/*/latest.json"
echo ""
echo "Next steps:"
echo "  1. Review the changes: git diff .github/agent-system/metrics/"
echo "  2. Verify improvements: python3 test_agent_scoring_accuracy.py"
echo "  3. Commit the changes: git add . && git commit -m 'Update historical metrics data'"
echo ""
