#!/bin/bash
set -e
# Quick Health Check - Like a medical tricorder scan! 🖖
# Created by @clarify-champion

echo "🔍 CHAINED SYSTEM HEALTH CHECK"
echo "================================"
echo ""

# Check 1: Repository Access
echo "📦 Repository Access..."
if git remote -v &>/dev/null; then
    echo "   ✅ Git repository accessible"
else
    echo "   ❌ CRITICAL: Cannot access git repository"
    exit 1
fi

# Check 2: Recent Workflow Activity
echo ""
echo "⚙️  Recent Workflow Activity (last 24h)..."
RECENT_RUNS=$(gh run list --created ">$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)" --json conclusion --jq '. | length' 2>/dev/null || echo "0")
FAILED_RUNS=$(gh run list --status failure --created ">$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)" --json conclusion --jq '. | length' 2>/dev/null || echo "0")

if [ "$RECENT_RUNS" -eq 0 ]; then
    echo "   ❌ WARNING: No workflows ran in last 24 hours"
elif [ "$FAILED_RUNS" -gt "$((RECENT_RUNS / 4))" ]; then
    echo "   ⚠️  WARNING: High failure rate ($FAILED_RUNS / $RECENT_RUNS failed)"
else
    echo "   ✅ Workflows running normally ($FAILED_RUNS / $RECENT_RUNS failed)"
fi

# Check 3: Copilot Assignment Status
echo ""
echo "🤖 Copilot Assignment Status..."
COPILOT_ISSUES=$(gh issue list --assignee "@me" --json number --jq '. | length' 2>/dev/null || echo "0")
OPEN_AI_ISSUES=$(gh issue list --label "ai-generated" --state open --json number --jq '. | length' 2>/dev/null || echo "0")

if [ "$COPILOT_ISSUES" -gt 0 ]; then
    echo "   ✅ Copilot is assigned to $COPILOT_ISSUES issue(s)"
elif [ "$OPEN_AI_ISSUES" -gt 10 ]; then
    echo "   ⚠️  WARNING: $OPEN_AI_ISSUES AI issues unassigned"
else
    echo "   ✅ Assignment queue clear"
fi

# Check 4: Learning System
echo ""
echo "🧠 Learning System..."
if [ -d "learnings" ]; then
    LEARNING_COUNT=$(find learnings -type f -name "*.json" 2>/dev/null | wc -l)
    RECENT_LEARNINGS=$(find learnings -type f -name "*.json" -mtime -1 2>/dev/null | wc -l)

    if [ "$RECENT_LEARNINGS" -gt 0 ]; then
        echo "   ✅ $RECENT_LEARNINGS new learning(s) in last 24h (Total: $LEARNING_COUNT)"
    elif [ "$LEARNING_COUNT" -gt 50 ]; then
        echo "   ⚠️  No new learnings, but $LEARNING_COUNT total exist"
    else
        echo "   ❌ WARNING: Learning system may not be running"
    fi
else
    echo "   ⚠️  WARNING: learnings directory not found"
fi

# Check 5: GitHub Pages
echo ""
echo "🌐 GitHub Pages Status..."
if [ -f "docs/data/stats.json" ]; then
    LAST_UPDATE=$(jq -r '.last_updated // "unknown"' docs/data/stats.json 2>/dev/null)
    echo "   ✅ GitHub Pages data exists (Updated: $LAST_UPDATE)"
else
    echo "   ⚠️  WARNING: GitHub Pages data files missing"
fi

# Check 6: Agent System
echo ""
echo "🤖 Agent System..."
if [ -f ".github/agent-system/registry.json" ]; then
    AGENT_COUNT=$(jq '.agents | length' .github/agent-system/registry.json 2>/dev/null || echo "0")
    ACTIVE_AGENTS=$(jq '[.agents[] | select(.status == "active")] | length' .github/agent-system/registry.json 2>/dev/null || echo "0")
    echo "   ✅ $ACTIVE_AGENTS active agents (Total: $AGENT_COUNT)"
else
    echo "   ⚠️  WARNING: Agent registry not found"
fi

# Final Verdict
echo ""
echo "================================"
echo "🏁 HEALTH CHECK COMPLETE"
echo ""
echo "Status indicators:"
echo "  ✅ = Healthy"
echo "  ⚠️  = Needs attention"
echo "  ❌ = Critical issue"
echo ""
echo "For detailed troubleshooting, see:"
echo "  docs/COMPREHENSIVE_TROUBLESHOOTING_GUIDE.md"
echo "  docs/TROUBLESHOOTING.md"
