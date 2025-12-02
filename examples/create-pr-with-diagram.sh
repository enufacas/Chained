#!/bin/bash
# Example script showing how to integrate instruction diagram generation
# into an automated PR creation workflow.
#
# This script demonstrates the pattern for automated workflows that create PRs.

set -e

# Example: Get the issue number from environment or parameter
ISSUE_NUMBER="${1:-$GITHUB_ISSUE_NUMBER}"
if [ -z "$ISSUE_NUMBER" ]; then
    echo "Error: Issue number required"
    echo "Usage: $0 ISSUE_NUMBER"
    exit 1
fi

echo "📝 Preparing PR with instruction diagram for issue #$ISSUE_NUMBER"

# Step 1: Identify modified files
echo "🔍 Detecting modified files..."
MODIFIED_FILES=$(git diff --name-only origin/main 2>/dev/null || git diff --name-only HEAD~1)

if [ -z "$MODIFIED_FILES" ]; then
    echo "⚠️  No modified files detected. Using all staged files..."
    MODIFIED_FILES=$(git diff --name-only --cached)
fi

echo "Modified files:"
echo "$MODIFIED_FILES" | sed 's/^/  - /'

# Step 2: Detect assigned agent (from issue body if available)
echo ""
echo "🤖 Detecting assigned agent..."

# Try to extract agent name from issue body using gh cli
AGENT_NAME=""
if command -v gh >/dev/null 2>&1 && [ -n "$GH_TOKEN" ]; then
    # Extract agent mention from issue body (looks for @agent-name patterns)
    AGENT_NAME=$(gh issue view "$ISSUE_NUMBER" --json body --jq '.body' 2>/dev/null | \
                 grep -oP '@\K[a-z0-9-]+(?=\*\*|\s|$)' | head -1 || echo "")
    
    if [ -n "$AGENT_NAME" ]; then
        echo "  ✓ Found assigned agent: @$AGENT_NAME"
    else
        echo "  ℹ️  No agent detected in issue body"
    fi
else
    echo "  ⚠️  gh CLI not available or GH_TOKEN not set, skipping agent detection"
fi

# Step 3: Generate instruction diagram
echo ""
echo "📊 Generating instruction source diagram..."

DIAGRAM_ARGS="--issue $ISSUE_NUMBER"
if [ -n "$AGENT_NAME" ]; then
    DIAGRAM_ARGS="$DIAGRAM_ARGS --agent $AGENT_NAME"
fi
if [ -n "$MODIFIED_FILES" ]; then
    # Convert newline-separated files to space-separated for --files parameter
    FILES_LIST=$(echo "$MODIFIED_FILES" | tr '\n' ' ')
    DIAGRAM_ARGS="$DIAGRAM_ARGS --files $FILES_LIST"
fi

# Generate the diagram and save to temp file
DIAGRAM_OUTPUT=$(mktemp)
python3 tools/generate-instruction-diagram.py $DIAGRAM_ARGS > "$DIAGRAM_OUTPUT"

echo "  ✓ Diagram generated successfully"

# Step 4: Create PR description with diagram
echo ""
echo "📝 Creating PR description..."

# Build the PR description
PR_DESCRIPTION="## Changes

[Describe your changes here]

## Testing

[Describe how changes were tested]

---

$(cat "$DIAGRAM_OUTPUT")"

# Clean up temp file
rm "$DIAGRAM_OUTPUT"

# Step 5: Create the PR
echo ""
echo "🚀 Creating pull request..."

# Example PR creation (adjust based on your workflow)
if command -v gh >/dev/null 2>&1 && [ -n "$GH_TOKEN" ]; then
    # Get current branch name
    BRANCH_NAME=$(git branch --show-current)
    
    # Create PR with the diagram included
    gh pr create \
        --title "fix: Address issue #$ISSUE_NUMBER" \
        --body "$PR_DESCRIPTION" \
        --label "automated" \
        --base main \
        --head "$BRANCH_NAME"
    
    echo "  ✓ Pull request created successfully"
else
    echo "  ⚠️  gh CLI not available or GH_TOKEN not set"
    echo ""
    echo "Generated PR description:"
    echo "================================"
    echo "$PR_DESCRIPTION"
    echo "================================"
fi

echo ""
echo "✅ Done!"
