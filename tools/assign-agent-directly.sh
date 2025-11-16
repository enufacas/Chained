#!/bin/bash
# Reusable script to assign a specific agent to an issue via GraphQL API
# This is called by workflows that create issues and need immediate assignment
#
# Environment variables required:
# - GH_TOKEN: GitHub token for API access
# - GITHUB_REPOSITORY: The repository name (owner/repo)
# - GITHUB_REPOSITORY_OWNER: The repository owner
# - GITHUB_REPOSITORY_NAME: The repository name
#
# Arguments:
# - $1: Issue number to assign
# - $2: Agent specialization (e.g., create-guru, engineer-master)

set -e  # Exit on error

if [ $# -lt 2 ]; then
  echo "Usage: assign-agent-directly.sh <issue_number> <agent_specialization>"
  exit 1
fi

issue_number=$1
matched_agent=$2

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 Direct Agent Assignment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Issue: #$issue_number"
echo "Agent: $matched_agent"
echo ""

# Get agent info using match-issue-to-agent.py
# We use a dummy title/body since we already know the agent
agent_info=$(python3 tools/match-issue-to-agent.py "agent-mission" "" 2>/dev/null || echo '{}')
agent_emoji=$(echo "$agent_info" | jq -r ".emoji // \"🤖\"")
agent_description=$(echo "$agent_info" | jq -r ".description // \"Specialized agent\"")

# Try to get human name for this specialization
agent_human_name=$(python3 << EOF
import json
from pathlib import Path

def get_human_name_for_specialization(specialization):
    """Get a human-readable name for a specialization from the registry."""
    registry_path = Path('.github/agent-system/registry.json')
    if not registry_path.exists():
        return None
    
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        # Find active agents with this specialization
        matching_agents = [
            agent for agent in registry.get('agents', [])
            if agent.get('specialization') == specialization and agent.get('status') == 'active'
        ]
        
        if matching_agents:
            # Return first match's human name
            return matching_agents[0].get('human_name')
    except:
        pass
    
    return None

human_name = get_human_name_for_specialization("$matched_agent")
print(human_name if human_name else "null")
EOF
)

# Build display name
if [ "$agent_human_name" != "null" ] && [ -n "$agent_human_name" ]; then
  agent_display_name="$agent_emoji $agent_human_name (@$matched_agent)"
  agent_name_display="**$agent_emoji $agent_human_name** (@$matched_agent)"
else
  agent_display_name="$agent_emoji $matched_agent"
  agent_name_display="**$agent_emoji $matched_agent**"
fi

echo "Display name: $agent_display_name"

# Add agent-specific label
agent_label="agent:$matched_agent"
echo "🏷️  Adding agent label: $agent_label"
gh label create "$agent_label" --repo "$GITHUB_REPOSITORY" --description "Custom agent: $matched_agent" --color "0E8A16" 2>/dev/null || true
gh issue edit "$issue_number" --repo "$GITHUB_REPOSITORY" --add-label "$agent_label" 2>/dev/null || echo "⚠️  Could not add agent label"

# Add copilot-assigned label to claim the issue
echo "🏷️  Adding copilot-assigned label"
gh issue edit "$issue_number" --repo "$GITHUB_REPOSITORY" --add-label "copilot-assigned" 2>/dev/null || echo "⚠️  Could not add copilot-assigned label"

# Add agent directive to issue body
echo "📝 Adding agent directive with @mention to issue body..."
issue_body_original=$(gh issue view "$issue_number" --repo "$GITHUB_REPOSITORY" --json body --jq '.body // ""')

# Check if agent directive already exists
if ! echo "$issue_body_original" | grep -q "<!-- COPILOT_AGENT:"; then
  # Prepend agent directive to issue body with @agent-name mention
  agent_directive="<!-- COPILOT_AGENT:$matched_agent -->

> **🤖 Agent Assignment**
> 
> This issue has been assigned to GitHub Copilot with the $agent_name_display custom agent profile.
> 
> **@$matched_agent** - Please use the specialized approach and tools defined in [\`.github/agents/${matched_agent}.md\`](https://github.com/$GITHUB_REPOSITORY/blob/main/.github/agents/${matched_agent}.md).
> 
> **IMPORTANT**: Always mention **@$matched_agent** by name in all conversations, comments, and PRs related to this issue.

---

"
  # Combine directive with original body
  new_body="${agent_directive}${issue_body_original}"
  
  # Update issue body using gh issue edit
  echo "$new_body" | gh issue edit "$issue_number" --repo "$GITHUB_REPOSITORY" --body-file -
  echo "✅ Added agent directive with @$matched_agent mention to issue body"
else
  echo "✅ Agent directive already exists in issue body"
fi

# Get the issue node ID (required for GraphQL mutation)
echo "🔍 Fetching issue node ID..."
issue_node_id=$(gh issue view "$issue_number" --repo "$GITHUB_REPOSITORY" --json id --jq '.id')

if [ -z "$issue_node_id" ]; then
  echo "❌ Failed to get issue node ID"
  exit 1
fi

echo "📍 Issue node ID: $issue_node_id"

# Query suggested actors to find Copilot or custom agent
echo ""
echo "🔍 Searching for actor ID (custom agent or Copilot)..."

all_actors=$(gh api graphql -f query='
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
  }' -f owner="$GITHUB_REPOSITORY_OWNER" -f repo="$GITHUB_REPOSITORY_NAME")

# Log available actors for debugging
echo "Available actors:"
echo "$all_actors" | jq -r '.data.repository.suggestedActors.nodes[] | "  - \(.login) (\(.__typename)): \(.id)"'

# Try to find custom agent by exact name match
custom_agent_actor_id=$(echo "$all_actors" | jq -r ".data.repository.suggestedActors.nodes[] | select(.login == \"$matched_agent\") | .id")

if [ -n "$custom_agent_actor_id" ]; then
  echo "✅ Found custom agent actor ID: $custom_agent_actor_id"
  echo "🎯 Will assign directly to custom agent: $matched_agent"
  target_actor_id="$custom_agent_actor_id"
  target_actor_name="$matched_agent"
  assignment_method="direct-custom-agent"
else
  echo "ℹ️  Custom agent '$matched_agent' not found as separate actor"
  echo "🔍 Falling back to generic Copilot actor..."
  
  # Get Copilot's actor ID
  copilot_actor_id=$(echo "$all_actors" | jq -r '.data.repository.suggestedActors.nodes[] | select(.login | test("copilot"; "i")) | .id' | head -1)
  
  if [ -z "$copilot_actor_id" ]; then
    echo "❌ Could not find Copilot actor ID"
    echo "⚠️  Copilot may not be enabled for this repository"
    exit 1
  fi
  
  echo "✅ Found generic Copilot actor ID: $copilot_actor_id"
  echo "ℹ️  Will assign to Copilot (agent selection via directives)"
  target_actor_id="$copilot_actor_id"
  target_actor_name="github-copilot"
  assignment_method="generic-with-directives"
fi

# Log assignment details
echo ""
echo "📋 Assignment Details:"
echo "   Target Actor: $target_actor_name"
echo "   Actor ID: $target_actor_id"
echo "   Method: $assignment_method"
echo "   Agent Path: .github/agents/${matched_agent}.md"

# Assign issue using GraphQL API
echo ""
echo "🤖 Assigning issue #$issue_number via GraphQL API..."

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
  }' -f issueId="$issue_node_id" -f actorId="$target_actor_id" 2>&1)

if echo "$mutation_result" | jq -e '.data.replaceActorsForAssignable.assignable' > /dev/null 2>&1; then
  echo "✅ Successfully assigned issue #$issue_number"
  
  # Build success message based on assignment method
  if [ "$agent_human_name" != "null" ] && [ -n "$agent_human_name" ]; then
    agent_mention="**$agent_human_name** (@$matched_agent)"
  else
    agent_mention="**@$matched_agent**"
  fi
  
  if [ "$assignment_method" = "direct-custom-agent" ]; then
    assignment_details="
## 🎯 Direct Custom Agent Assignment

**SUCCESS!** This mission was assigned directly to the custom agent actor:

- **Custom Agent**: $agent_name_display
- **Actor ID**: \`$target_actor_id\`
- **Agent Path**: [\`.github/agents/${matched_agent}.md\`](https://github.com/$GITHUB_REPOSITORY/blob/main/.github/agents/${matched_agent}.md)
- **Assignment Method**: Direct API assignment to custom agent actor

The custom agent has its own actor ID in the GitHub API, allowing direct assignment without directives.

**IMPORTANT**: Always mention **@$matched_agent** by name in all conversations related to this mission."
  else
    assignment_details="
## 🧠 Intelligent Agent Matching

This mission has been matched to the $agent_name_display specialization:

- **Agent**: $agent_name_display
- **Agent Path**: [\`.github/agents/${matched_agent}.md\`](https://github.com/$GITHUB_REPOSITORY/blob/main/.github/agents/${matched_agent}.md)
- **Assignment Method**: Generic Copilot with agent directives

**IMPORTANT**: Always mention **@$matched_agent** by name in all conversations related to this mission.

## 🎯 Copilot Agent Directive

**@$matched_agent** - Please use the **$matched_agent** custom agent profile from \`.github/agents/${matched_agent}.md\` when working on this mission. Follow the specialized approach, tools, and best practices defined in that agent's configuration.

**IMPORTANT**: Always mention **@$matched_agent** by name in all your conversations, comments, and PRs related to this mission to ensure proper attribution and tracking."
  fi
  
  # Add success comment
  gh issue comment "$issue_number" --repo "$GITHUB_REPOSITORY" --body "🤖 **Mission Agent Assigned Successfully**

GitHub Copilot has been automatically assigned to this mission via the official GitHub GraphQL API.
$assignment_details

**What happens next:**
1. ✅ $agent_mention will analyze the mission requirements using the $matched_agent specialization
2. 💻 $agent_mention will explore the mission locations and gather insights
3. 📝 $agent_mention will create artifacts and documentation
4. 🔄 $agent_mention will update the world model with findings
5. ✅ Mission will be marked complete when all objectives are met

**Estimated time:** Copilot typically starts work within a few minutes
**Assigned agent:** $agent_mention ($matched_agent specialization)
**Assigned at:** $(date -u +'%Y-%m-%d %H:%M:%S UTC')

---
*🎯 Automated mission assignment via Agent Missions workflow + GitHub GraphQL API*"
  
  echo "✅ Assignment complete"
  exit 0
else
  echo "❌ Failed to assign issue #$issue_number"
  echo "Error details: $mutation_result"
  
  # Add error comment
  gh issue comment "$issue_number" --repo "$GITHUB_REPOSITORY" --body "⚠️ **Failed to Assign Mission via GraphQL API**

The workflow attempted to assign GitHub Copilot to this mission using the official GraphQL API method, but the assignment failed.

**API Method Used:**
- GraphQL mutation: \`replaceActorsForAssignable\`
- Target Actor: \`$target_actor_name\`
- Actor ID: \`$target_actor_id\`
- Assignment Method: \`$assignment_method\`
- Agent Path: \`.github/agents/${matched_agent}.md\`

**Most Common Cause:**
This workflow is using the default \`GITHUB_TOKEN\` which cannot assign Copilot due to licensing restrictions. A Personal Access Token (PAT) is required.

**To Fix:**
1. Create a PAT with \`repo\` scope at https://github.com/settings/tokens
2. Add it as a repository secret named \`COPILOT_PAT\`
3. Re-run this workflow

**For now:**
- This mission has been labeled \`copilot-assigned\` for tracking
- You can manually assign Copilot from the GitHub UI
- The scheduled copilot-graphql-assign workflow will attempt assignment again

---
*🤖 Automated via Agent Missions workflow + GitHub GraphQL API*"
  
  exit 1
fi
