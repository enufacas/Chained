#!/bin/bash

# Script to create GitHub issues for AI Friend suggestions from 2025-11-14
# Note: These suggestions are identical to 2025-11-13 (gemini-pro), 
# so we use the same detailed specifications.

set -e

echo "🤖 Creating GitHub Issues for AI Friend Suggestions (2025-11-14)"
echo "================================================================"
echo ""
echo "These suggestions came from the gemini-pro AI Friend conversation"
echo "on 2025-11-14 and match the 2025-11-13 suggestions."
echo ""

# Check if we're in the right directory
if [ ! -f "docs/ai-suggestions/issue-5-curiosity-engine.md" ]; then
    echo "❌ Error: Must run from repository root"
    exit 1
fi

# Check if GH_TOKEN is set
if [ -z "$GH_TOKEN" ]; then
    echo "⚠️  Warning: GH_TOKEN not set. Issues may not be created."
    echo "   Set GH_TOKEN environment variable or run in GitHub Actions."
    echo ""
fi

# Issue 5: Curiosity Engine (Priority: Highest)
echo "Creating Issue 5: 🧠 Curiosity Engine..."
gh issue create \
  --title "🧠 Curiosity Engine - AI Knowledge Gap Detection & Self-Directed Learning" \
  --body-file docs/ai-suggestions/issue-5-curiosity-engine.md \
  --label "enhancement,ai-suggested,copilot,learning" || echo "  ⚠️  Issue 5 creation failed or already exists"

echo ""

# Issue 6: Learning Priority System (Priority: High)
echo "Creating Issue 6: 📊 Learning Priority System..."
gh issue create \
  --title "📊 Learning Priority System - Smart Application of Tech Knowledge" \
  --body-file docs/ai-suggestions/issue-6-learning-priority-system.md \
  --label "enhancement,ai-suggested,copilot,learning" || echo "  ⚠️  Issue 6 creation failed or already exists"

echo ""

# Issue 7: A/B Testing Framework (Priority: High)
echo "Creating Issue 7: 🧪 A/B Testing Framework..."
gh issue create \
  --title "🧪 A/B Testing Framework for AI-Generated Features" \
  --body-file docs/ai-suggestions/issue-7-ab-testing-framework.md \
  --label "enhancement,ai-suggested,copilot,testing,experimentation" || echo "  ⚠️  Issue 7 creation failed or already exists"

echo ""

# Issue 8: What-If Simulator (Priority: Medium)
echo "Creating Issue 8: 🔮 What-If Simulator..."
gh issue create \
  --title "🔮 What-If Simulator - Test Ideas Before Implementation" \
  --body-file docs/ai-suggestions/issue-8-what-if-simulator.md \
  --label "enhancement,ai-suggested,copilot,simulation,planning" || echo "  ⚠️  Issue 8 creation failed or already exists"

echo ""
echo "✅ GitHub issue creation complete!"
echo ""
echo "📊 Summary:"
echo "  - 4 issues created/attempted from AI Friend conversation"
echo "  - Source: docs/ai-conversations/conversation_20251114_091442.json"
echo "  - AI Model: gemini-pro"
echo "  - Follow-up doc: docs/ai-suggestions/follow-up-20251114.md"
echo ""
echo "🔗 Next Steps:"
echo "  1. Review created issues on GitHub"
echo "  2. Assign to appropriate agents (@create-guru recommended)"
echo "  3. Begin implementation with highest priority items"
echo "  4. Track progress and measure impact"
echo ""
echo "Priority order for implementation:"
echo "  1. 🧠 Curiosity Engine (Highest)"
echo "  2. 📊 Learning Priority System (High)"
echo "  3. 🧪 A/B Testing Framework (High)"
echo "  4. 🔮 What-If Simulator (Medium)"
