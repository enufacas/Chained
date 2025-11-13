#!/bin/bash
# Helper script to create GitHub issues from AI suggestions (2025-11-13)
# Usage: bash docs/ai-suggestions/create-issues-20251113.sh

set -e

cd "$(dirname "$0")/../.."  # Go to repository root

echo "🤖 Creating GitHub issues from AI Friend suggestions (2025-11-13)..."
echo ""
echo "📋 Source: docs/ai-conversations/conversation_20251113_091604.json"
echo "📋 AI Model: gemini-pro"
echo ""

# Check if GH_TOKEN is set
if [ -z "$GH_TOKEN" ] && [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GH_TOKEN or GITHUB_TOKEN environment variable required"
    echo ""
    echo "Usage:"
    echo "  export GH_TOKEN=your_token_here"
    echo "  bash docs/ai-suggestions/create-issues-20251113.sh"
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

# Issue 5: Curiosity Engine
echo "Creating Issue 1/4: Curiosity Engine..."
if gh issue create \
  --title "🧠 Curiosity Engine - AI Knowledge Gap Detection & Self-Directed Learning" \
  --body-file docs/ai-suggestions/issue-5-curiosity-engine.md \
  --label "enhancement,ai-suggested,copilot,learning"; then
    echo "✅ Issue 5 created successfully"
else
    echo "⚠️  Issue 5 creation failed (may already exist)"
fi
echo ""

# Issue 6: Learning Priority System
echo "Creating Issue 2/4: Learning Priority System..."
if gh issue create \
  --title "📊 Learning Priority System - Smart Application of Tech Knowledge" \
  --body-file docs/ai-suggestions/issue-6-learning-priority-system.md \
  --label "enhancement,ai-suggested,copilot,learning"; then
    echo "✅ Issue 6 created successfully"
else
    echo "⚠️  Issue 6 creation failed (may already exist)"
fi
echo ""

# Issue 7: A/B Testing Framework
echo "Creating Issue 3/4: A/B Testing Framework..."
if gh issue create \
  --title "🧪 A/B Testing Framework for AI-Generated Features" \
  --body-file docs/ai-suggestions/issue-7-ab-testing-framework.md \
  --label "enhancement,ai-suggested,copilot,testing,experimentation"; then
    echo "✅ Issue 7 created successfully"
else
    echo "⚠️  Issue 7 creation failed (may already exist)"
fi
echo ""

# Issue 8: What-If Simulator
echo "Creating Issue 4/4: What-If Simulator..."
if gh issue create \
  --title "🔮 What-If Simulator - Test Ideas Before Implementation" \
  --body-file docs/ai-suggestions/issue-8-what-if-simulator.md \
  --label "enhancement,ai-suggested,copilot,simulation,planning"; then
    echo "✅ Issue 8 created successfully"
else
    echo "⚠️  Issue 8 creation failed (may already exist)"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Issue creation process complete!"
echo ""
echo "📋 Summary:"
echo "  ✓ 4 issues prepared from gemini-pro AI Friend (2025-11-13)"
echo "  ✓ All issues reference original conversation"
echo "  ✓ Each issue is actionable and ready for implementation"
echo ""
echo "🔗 View your issues:"
echo "  gh issue list --label ai-suggested"
echo ""
echo "📊 What was created:"
echo "  5. 🧠 Curiosity Engine - Self-Directed Learning"
echo "  6. 📊 Learning Priority System - Smart Prioritization"
echo "  7. 🧪 A/B Testing Framework - Empirical Validation"
echo "  8. 🔮 What-If Simulator - Test Before Implementation"
echo ""
echo "🚀 Implementation Roadmap:"
echo "  1. Start with Curiosity Engine (highest impact)"
echo "  2. Add Learning Priority System (complements #1)"
echo "  3. Build A/B Testing Framework (enable experimentation)"
echo "  4. Create What-If Simulator (strategic planning)"
echo ""
echo "💡 These suggestions create a complete learning & experimentation cycle!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
