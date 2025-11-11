#!/bin/bash
# Helper script to create GitHub issues from AI suggestions
# Usage: bash docs/ai-suggestions/create-issues.sh

set -e

cd "$(dirname "$0")/../.."  # Go to repository root

echo "🤖 Creating GitHub issues from AI Friend suggestions..."
echo ""
echo "📋 Source: docs/ai-conversations/conversation_20251111_091509.json"
echo ""

# Check if GH_TOKEN is set
if [ -z "$GH_TOKEN" ] && [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GH_TOKEN or GITHUB_TOKEN environment variable required"
    echo ""
    echo "Usage:"
    echo "  export GH_TOKEN=your_token_here"
    echo "  bash docs/ai-suggestions/create-issues.sh"
    echo ""
    echo "Or in GitHub Actions:"
    echo "  env:"
    echo "    GH_TOKEN: \${{ secrets.GITHUB_TOKEN }}"
    exit 1
fi

# Use GH_TOKEN if GITHUB_TOKEN is not set
if [ -z "$GH_TOKEN" ]; then
    export GH_TOKEN="$GITHUB_TOKEN"
fi

echo "✅ GitHub CLI configured"
echo ""

# Issue 1: Creativity Metrics
echo "Creating Issue 1/4: Enhanced Creativity Metrics..."
if gh issue create \
  --title "📊 Enhanced Creativity & Innovation Metrics for AI Agents" \
  --body-file docs/ai-suggestions/issue-1-creativity-metrics.md \
  --label "enhancement,ai-suggested,copilot,agent-system"; then
    echo "✅ Issue 1 created successfully"
else
    echo "⚠️  Issue 1 creation failed (may already exist)"
fi
echo ""

# Issue 2: Repetition Detection
echo "Creating Issue 2/4: AI Repetition Detection..."
if gh issue create \
  --title "🔄 AI Pattern Repetition Detection & Prevention System" \
  --body-file docs/ai-suggestions/issue-2-repetition-detection.md \
  --label "enhancement,ai-suggested,copilot,agent-system"; then
    echo "✅ Issue 2 created successfully"
else
    echo "⚠️  Issue 2 creation failed (may already exist)"
fi
echo ""

# Issue 3: Knowledge Graph
echo "Creating Issue 3/4: Enhanced Knowledge Graph..."
if gh issue create \
  --title "🕸️ Enhance AI Knowledge Graph with Deeper Code Relationships" \
  --body-file docs/ai-suggestions/issue-3-knowledge-graph.md \
  --label "enhancement,ai-suggested,copilot,knowledge-graph"; then
    echo "✅ Issue 3 created successfully"
else
    echo "⚠️  Issue 3 creation failed (may already exist)"
fi
echo ""

# Issue 4: Archaeology Learning
echo "Creating Issue 4/4: Enhanced Code Archaeology..."
if gh issue create \
  --title "🏛️ Enhance Code Archaeology to Learn from Historical Patterns" \
  --body-file docs/ai-suggestions/issue-4-archaeology-learning.md \
  --label "enhancement,ai-suggested,copilot,archaeology"; then
    echo "✅ Issue 4 created successfully"
else
    echo "⚠️  Issue 4 creation failed (may already exist)"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Issue creation process complete!"
echo ""
echo "📋 Summary:"
echo "  ✓ 4 issues prepared from AI Friend suggestions"
echo "  ✓ All issues reference original conversation"
echo "  ✓ Each issue is actionable and ready for Copilot"
echo ""
echo "🔗 View your issues:"
echo "  gh issue list --label ai-suggested"
echo ""
echo "📊 What was created:"
echo "  1. 📊 Enhanced Creativity & Innovation Metrics"
echo "  2. 🔄 AI Pattern Repetition Detection & Prevention"
echo "  3. 🕸️ Enhanced Knowledge Graph with Deeper Relationships"
echo "  4. 🏛️ Enhanced Code Archaeology with Pattern Learning"
echo ""
echo "🚀 Next steps:"
echo "  • Review the created issues"
echo "  • Assign to Copilot or appropriate agents"
echo "  • Track implementation progress"
echo "  • Measure impact on system performance"
echo ""
echo "✅ Ready for the perpetual motion machine!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
