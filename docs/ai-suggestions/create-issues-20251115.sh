#!/bin/bash
# Script to create GitHub issues for AI Friend suggestions from 2025-11-15

set -e

REPO="enufacas/Chained"
DOCS_DIR="docs/ai-suggestions"

echo "🤖 Creating GitHub issues for AI Friend suggestions (2025-11-15)"
echo "================================================================"
echo ""

# Issue 9: Code Complexity Tracker
echo "📈 Creating Issue 9: Code Complexity Tracker..."
gh issue create \
  --repo "$REPO" \
  --title "📈 Code Complexity Tracker - Monitor Quality Trends Over Time" \
  --body-file "$DOCS_DIR/issue-9-code-complexity-tracker.md" \
  --label "enhancement,ai-suggested,copilot,quality" && echo "✅ Issue 9 created" || echo "❌ Issue 9 failed"

echo ""

# Issue 10: Decision Visualization
echo "🎨 Creating Issue 10: AI Decision Visualization..."
gh issue create \
  --repo "$REPO" \
  --title "🎨 AI Decision-Making Visualization - Show Reasoning Processes" \
  --body-file "$DOCS_DIR/issue-10-decision-visualization.md" \
  --label "enhancement,ai-suggested,copilot,visualization" && echo "✅ Issue 10 created" || echo "❌ Issue 10 failed"

echo ""

# Issue 11: Reflection Feedback Loop
echo "🔄 Creating Issue 11: AI Reflection System..."
gh issue create \
  --repo "$REPO" \
  --title "🔄 AI Reflection System - Self-Assessment & Learning from Past Decisions" \
  --body-file "$DOCS_DIR/issue-11-reflection-feedback-loop.md" \
  --label "enhancement,ai-suggested,copilot,learning" && echo "✅ Issue 11 created" || echo "❌ Issue 11 failed"

echo ""

# Issue 12: Multi-Agent Debate
echo "💬 Creating Issue 12: Multi-Agent Debate System..."
gh issue create \
  --repo "$REPO" \
  --title "💬 Multi-Agent Debate System - Collaborative Intelligence" \
  --body-file "$DOCS_DIR/issue-12-multi-agent-debate.md" \
  --label "enhancement,ai-suggested,copilot,experimental" && echo "✅ Issue 12 created" || echo "❌ Issue 12 failed"

echo ""
echo "================================================================"
echo "✅ Issue creation complete!"
echo ""
echo "Summary:"
echo "  📈 Issue 9:  Code Complexity Tracker (quality)"
echo "  🎨 Issue 10: Decision Visualization (visualization)"
echo "  🔄 Issue 11: Reflection System (learning)"
echo "  💬 Issue 12: Multi-Agent Debate (experimental)"
echo ""
echo "Source: AI Friend conversation from 2025-11-15 (gpt-4.1-nano)"
echo "Analysis: docs/ai-suggestions/issues-to-create-20251115.md"
