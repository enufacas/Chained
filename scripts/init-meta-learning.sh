#!/bin/bash
# Meta-Learning Scheduler Initialization Script
# Created by @create-botter
#
# This script initializes the meta-learning workflow scheduler system
# by creating the necessary directory structure and baseline strategies.

set -e

echo "🎓 Initializing Meta-Learning Workflow Scheduler..."
echo ""

# Navigate to repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Create meta-learning directory
echo "📁 Creating meta-learning directory structure..."
mkdir -p .github/workflow-history/meta-learning
echo "✅ Directory created: .github/workflow-history/meta-learning"

# Initialize baseline strategies
echo ""
echo "🧠 Initializing baseline scheduling strategies..."
python3 tools/meta_learning_scheduler.py --adapt default

if [ -f .github/workflow-history/meta-learning/learned_strategies.json ]; then
    echo "✅ Baseline strategies initialized"
else
    echo "❌ Failed to initialize strategies"
    exit 1
fi

# Run tests to verify system
echo ""
echo "🧪 Running test suite..."
if python3 tools/test_meta_learning_scheduler.py > /tmp/meta_learning_test.log 2>&1; then
    echo "✅ All tests passed"
    tail -20 /tmp/meta_learning_test.log
else
    echo "⚠️ Some tests failed - see /tmp/meta_learning_test.log"
    tail -50 /tmp/meta_learning_test.log
    exit 1
fi

# Generate initial report
echo ""
echo "📊 Generating initial report..."
python3 tools/meta_learning_scheduler.py --report

echo ""
echo "============================================"
echo "✨ Meta-Learning Scheduler Initialized!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. The workflow runs automatically every 6 hours"
echo "  2. View progress: python3 tools/meta_learning_scheduler.py --report"
echo "  3. Manual trigger: gh workflow run meta-learning-optimizer.yml"
echo ""
echo "Documentation:"
echo "  • Quick Start: docs/QUICKSTART_META_LEARNING.md"
echo "  • Full Guide: docs/META_LEARNING_SCHEDULER.md"
echo "  • Implementation: META_LEARNING_IMPLEMENTATION.md"
echo ""
echo "@create-botter - System ready for meta-learning! 🏭⚡"
