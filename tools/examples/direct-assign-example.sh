#!/bin/bash
# Example: How to use custom agent actor IDs for direct assignment
#
# This script demonstrates the workflow for using custom agent actor IDs
# discovered via the inspection tools to directly assign agents to issues.
#
# Prerequisites:
# 1. Set GH_TOKEN environment variable with a PAT that has 'repo' scope
# 2. Have custom agents configured in .github/agents/
# 3. Know the issue number you want to assign

set -e

# Configuration
OWNER="enufacas"
REPO="Chained"
ISSUE_NUMBER="${1:-}"

if [ -z "$ISSUE_NUMBER" ]; then
  echo "Usage: $0 <issue_number>"
  echo ""
  echo "Example: $0 42"
  echo ""
  echo "This script demonstrates how to:"
  echo "1. Discover available custom agent actor IDs"
  echo "2. Match an issue to the appropriate agent"
  echo "3. Assign the issue directly to that custom agent"
  exit 1
fi

if [ -z "$GH_TOKEN" ]; then
  echo "Error: GH_TOKEN environment variable not set"
  echo "Please set it to a GitHub Personal Access Token with 'repo' scope"
  echo ""
  echo "Example:"
  echo "  export GH_TOKEN='ghp_your_token_here'"
  exit 1
fi

echo "=================================================================="
echo "🎯 Direct Custom Agent Assignment Example"
echo "=================================================================="
echo ""
echo "Repository: $OWNER/$REPO"
echo "Issue: #$ISSUE_NUMBER"
echo ""

# Step 1: Get issue details
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Fetch Issue Details"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

issue_data=$(gh api repos/$OWNER/$REPO/issues/$ISSUE_NUMBER)
issue_title=$(echo "$issue_data" | jq -r '.title')
issue_body=$(echo "$issue_data" | jq -r '.body // ""')

echo "Title: $issue_title"
echo "Body preview: ${issue_body:0:100}..."
echo ""

# Step 2: Match issue to appropriate agent
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Match Issue to Custom Agent"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$(dirname "$0")/.."
agent_match=$(python3 tools/match-issue-to-agent.py "$issue_title" "$issue_body")
matched_agent=$(echo "$agent_match" | jq -r '.agent')
agent_score=$(echo "$agent_match" | jq -r '.score')
agent_confidence=$(echo "$agent_match" | jq -r '.confidence')

echo "Matched Agent: $matched_agent"
echo "Score: $agent_score"
echo "Confidence: $agent_confidence"
echo ""

# Step 3: Query for custom agent actor ID
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Query GitHub API for Custom Agent Actor ID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

actors_data=$(gh api graphql -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      suggestedActors(capabilities: [CAN_BE_ASSIGNED], first: 100) {
        nodes {
          login
          __typename
          ... on Bot { id }
          ... on User { id }
        }
      }
    }
  }' -f owner="$OWNER" -f repo="$REPO")

echo "Available actors:"
echo "$actors_data" | jq -r '.data.repository.suggestedActors.nodes[] | "  - \(.login) (\(.__typename)): \(.id)"'
echo ""

# Try to find custom agent actor ID
custom_agent_actor_id=$(echo "$actors_data" | jq -r ".data.repository.suggestedActors.nodes[] | select(.login == \"$matched_agent\") | .id")

if [ -n "$custom_agent_actor_id" ]; then
  echo "✅ Found custom agent actor ID!"
  echo "   Agent: $matched_agent"
  echo "   Actor ID: $custom_agent_actor_id"
  echo "   Path: .github/agents/${matched_agent}.md"
  echo ""
  assignment_method="direct-custom-agent"
  target_actor_id="$custom_agent_actor_id"
  target_actor_name="$matched_agent"
else
  echo "ℹ️  Custom agent '$matched_agent' not found as separate actor"
  echo "   Falling back to generic Copilot bot"
  echo ""
  
  # Get generic Copilot actor ID
  copilot_actor_id=$(echo "$actors_data" | jq -r '.data.repository.suggestedActors.nodes[] | select(.login | test("copilot"; "i")) | .id' | head -1)
  
  if [ -z "$copilot_actor_id" ]; then
    echo "❌ ERROR: Could not find Copilot actor ID"
    exit 1
  fi
  
  echo "✅ Found generic Copilot actor ID: $copilot_actor_id"
  echo ""
  assignment_method="generic-with-directives"
  target_actor_id="$copilot_actor_id"
  target_actor_name="github-copilot"
fi

# Step 4: Get issue node ID
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Get Issue Node ID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

issue_node_id=$(gh api graphql -f query='
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      issue(number: $number) {
        id
      }
    }
  }' -f owner="$OWNER" -f repo="$REPO" -F number="$ISSUE_NUMBER" | jq -r '.data.repository.issue.id')

echo "Issue Node ID: $issue_node_id"
echo ""

# Step 5: Assign via GraphQL API
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Assign via GraphQL API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Assignment Details:"
echo "  Method: $assignment_method"
echo "  Target Actor: $target_actor_name"
echo "  Actor ID: $target_actor_id"
echo "  Issue Node ID: $issue_node_id"
echo ""

echo "Executing GraphQL mutation..."
mutation_result=$(gh api graphql -f query='
  mutation($issueId: ID!, $actorId: ID!) {
    replaceActorsForAssignable(input: {
      assignableId: $issueId,
      actorIds: [$actorId]
    }) {
      assignable {
        ... on Issue {
          id
          assignees(first: 10) {
            nodes {
              login
            }
          }
        }
      }
    }
  }' -f issueId="$issue_node_id" -f actorId="$target_actor_id")

# Check result
if echo "$mutation_result" | jq -e '.data.replaceActorsForAssignable.assignable' > /dev/null 2>&1; then
  echo "✅ Assignment successful!"
  echo ""
  echo "Assigned actors:"
  echo "$mutation_result" | jq -r '.data.replaceActorsForAssignable.assignable.assignees.nodes[] | "  - \(.login)"'
  echo ""
  
  if [ "$assignment_method" = "direct-custom-agent" ]; then
    echo "🎉 SUCCESS: Direct custom agent assignment worked!"
    echo ""
    echo "This proves that:"
    echo "  - Custom agent '$matched_agent' has a separate actor ID"
    echo "  - Direct API assignment to custom agents is possible"
    echo "  - The workflow can use this method automatically"
  else
    echo "ℹ️  Assigned to generic Copilot bot"
    echo ""
    echo "Note: Custom agent selection will rely on directives in the issue"
  fi
else
  echo "❌ Assignment failed"
  echo ""
  echo "Error details:"
  echo "$mutation_result" | jq '.'
  exit 1
fi

echo ""
echo "=================================================================="
echo "✅ Example Complete"
echo "=================================================================="
echo ""
echo "View the issue: https://github.com/$OWNER/$REPO/issues/$ISSUE_NUMBER"
