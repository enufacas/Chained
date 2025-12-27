#!/usr/bin/env bash
# Install Git Commit Strategy Pre-commit Hook
# Created by @create-botter - Autonomous learning infrastructure
#
# This script installs a pre-commit hook that validates commit messages
# against learned optimal strategies before allowing the commit.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOOKS_DIR="${REPO_ROOT}/.git/hooks"
HOOK_FILE="${HOOKS_DIR}/commit-msg"

echo "⚡ Installing Git Commit Strategy Pre-commit Hook"
echo "   Created by @create-botter"
echo ""

# Check if .git directory exists
if [ ! -d "${REPO_ROOT}/.git" ]; then
    echo "❌ Error: Not a git repository"
    echo "   Run this script from within a git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "${HOOKS_DIR}"

# Check if hook already exists
if [ -f "${HOOK_FILE}" ]; then
    echo "⚠️  Existing commit-msg hook found"
    echo "   Backing up to ${HOOK_FILE}.backup"
    cp "${HOOK_FILE}" "${HOOK_FILE}.backup"
fi

# Create the hook
cat > "${HOOK_FILE}" << 'HOOK_CONTENT'
#!/usr/bin/env bash
# Git Commit Strategy Validation Hook
# Installed by @create-botter's commit strategy learning system
#
# This hook validates commit messages against learned optimal strategies
# and provides actionable suggestions for improvement.

COMMIT_MSG_FILE="$1"
TOOLS_DIR="$(git rev-parse --show-toplevel)/tools"

# Check if the learner tool exists
if [ ! -f "${TOOLS_DIR}/commit-strategy-learner.py" ]; then
    # If tool doesn't exist, allow commit (don't block development)
    exit 0
fi

# Read the commit message
COMMIT_MSG=$(cat "${COMMIT_MSG_FILE}")

# Skip validation for merge commits
if echo "${COMMIT_MSG}" | grep -q "^Merge"; then
    exit 0
fi

# Skip validation for revert commits
if echo "${COMMIT_MSG}" | grep -q "^Revert"; then
    exit 0
fi

# Get files being committed
FILES_CHANGED=$(git diff --cached --name-only | wc -l)
LINES_CHANGED=$(git diff --cached --numstat | awk '{add+=$1; del+=$2} END {print add+del}')

# Validate the commit message
echo ""
echo "🔍 Validating commit message against learned strategies..."

# Run validation (capture exit code but don't fail yet)
VALIDATION_OUTPUT=$(cd "$(git rev-parse --show-toplevel)" && python3 "${TOOLS_DIR}/commit-strategy-learner.py" \
    --validate "${COMMIT_MSG}" \
    --files "${FILES_CHANGED}" \
    --lines "${LINES_CHANGED}" 2>&1) || VALIDATION_FAILED=$?

echo "${VALIDATION_OUTPUT}"

# Check validation result
if echo "${VALIDATION_OUTPUT}" | grep -q "needs_improvement"; then
    echo ""
    echo "⚠️  Your commit could be improved"
    echo ""
    echo "Options:"
    echo "  1. Review suggestions above and update commit message"
    echo "  2. Continue anyway with: git commit --no-verify"
    echo ""
    
    # Ask user if they want to continue
    read -p "Continue with commit? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Commit cancelled. Update your message and try again."
        exit 1
    fi
fi

echo ""
echo "✅ Commit message validated"
exit 0
HOOK_CONTENT

# Make hook executable
chmod +x "${HOOK_FILE}"

echo "✅ Pre-commit hook installed successfully!"
echo ""
echo "📋 What this does:"
echo "   • Validates commit messages before allowing commits"
echo "   • Provides actionable suggestions based on learned patterns"
echo "   • Helps maintain high commit quality standards"
echo ""
echo "🎯 Usage:"
echo "   • Write commits normally: git commit -m 'message'"
echo "   • Hook validates automatically and provides feedback"
echo "   • To skip validation: git commit --no-verify"
echo ""
echo "🔧 Uninstall:"
echo "   • Remove or rename: ${HOOK_FILE}"
if [ -f "${HOOK_FILE}.backup" ]; then
    echo "   • Restore backup: mv ${HOOK_FILE}.backup ${HOOK_FILE}"
fi
echo ""
echo "✨ Infrastructure by @create-botter"
