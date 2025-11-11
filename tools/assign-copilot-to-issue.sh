#!/bin/bash
# Script to discover and process GitHub issues for Copilot assignment
# This script is called by .github/workflows/copilot-graphql-assign.yml
#
# Environment variables required:
# - GH_TOKEN: GitHub token for API access
# - GITHUB_EVENT_NAME: The event that triggered the workflow
# - GITHUB_REPOSITORY: The repository name (owner/repo)
# - GITHUB_REPOSITORY_OWNER: The repository owner
# - GITHUB_REPOSITORY_NAME: The repository name
# - INPUT_ISSUE_NUMBER: (optional) Specific issue number to process
# - INPUT_ASSIGNMENT_METHOD: (optional) Assignment method (cli, graphql, auto)
# - ISSUE_NUMBER: (optional, for issue events) The issue number from the event

set -e  # Exit on error

echo "🔍 Determining which issues to process..."

# If workflow_dispatch with specific issue number, process only that issue
if [ "$GITHUB_EVENT_NAME" = "workflow_dispatch" ] && [ -n "$INPUT_ISSUE_NUMBER" ]; then
  echo "Processing specific issue #$INPUT_ISSUE_NUMBER"
  issue_numbers="$INPUT_ISSUE_NUMBER"
# If triggered by issue opened event, process only that issue
elif [ "$GITHUB_EVENT_NAME" = "issues" ]; then
  issue_numbers="$ISSUE_NUMBER"
  echo "Processing newly opened issue #$issue_numbers"
else
  # For scheduled runs or manual dispatch without issue number, get all open issues
  echo "Processing all open issues (scheduled or manual run)"
  issue_numbers=$(gh issue list --repo "$GITHUB_REPOSITORY" --state open --limit 1000 --json number --jq '.[].number')
fi

if [ -z "$issue_numbers" ]; then
  echo "ℹ️ No open issues found"
  exit 0
fi

echo "Found issues to check: $issue_numbers"

success_count=0
already_assigned_count=0
failed_count=0

# Process each issue
for issue_number in $issue_numbers; do
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Processing issue #$issue_number"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # Get current assignees
  assignees=$(gh issue view "$issue_number" --repo "$GITHUB_REPOSITORY" --json assignees --jq '.assignees[].login')
  
  # Check if any assignee matches Copilot patterns
  if echo "$assignees" | grep -qE 'copilot|github-copilot'; then
    echo "✓ Issue #$issue_number already assigned to Copilot"
    already_assigned_count=$((already_assigned_count + 1))
    continue
  fi
  
  echo "📝 Issue #$issue_number not yet assigned to Copilot"
  
  # Check if we've already commented on this issue to avoid duplicate comments
  existing_comments=$(gh issue view "$issue_number" --repo "$GITHUB_REPOSITORY" --json comments --jq '.comments[].body')
  if echo "$existing_comments" | grep -q "🤖 **Copilot"; then
    echo "✓ Issue #$issue_number already has assignment comment, skipping to avoid duplicates"
    already_assigned_count=$((already_assigned_count + 1))
    continue
  fi
  
  # ✨ Intelligent Agent Matching ✨
  echo "🧠 Analyzing issue content to match with appropriate agent..."
  issue_title=$(gh issue view "$issue_number" --repo "$GITHUB_REPOSITORY" --json title --jq '.title')
  issue_body=$(gh issue view "$issue_number" --repo "$GITHUB_REPOSITORY" --json body --jq '.body // ""')
  
  # Use intelligent matching to determine best agent
  agent_match=$(python3 tools/match-issue-to-agent.py "$issue_title" "$issue_body" 2>/dev/null || echo '{"agent":"feature-architect","score":0,"confidence":"low"}')
  matched_agent=$(echo "$agent_match" | jq -r '.agent')
  agent_score=$(echo "$agent_match" | jq -r '.score')
  agent_confidence=$(echo "$agent_match" | jq -r '.confidence')
  agent_emoji=$(echo "$agent_match" | jq -r '.emoji')
  agent_description=$(echo "$agent_match" | jq -r '.description')
  
  echo "✅ Matched to agent: $agent_emoji $matched_agent"
  echo "   Score: $agent_score | Confidence: $agent_confidence"
  echo "   Description: $agent_description"
  
  # Add copilot-assigned label and agent-specific label
  labels=$(gh issue view "$issue_number" --repo "$GITHUB_REPOSITORY" --json labels --jq '.labels[].name')
  if ! echo "$labels" | grep -q "copilot-assigned"; then
    gh issue edit "$issue_number" --repo "$GITHUB_REPOSITORY" --add-label "copilot-assigned"
    echo "✓ Added copilot-assigned label to issue #$issue_number"
  fi
  
  # Add agent-specific label to help Copilot identify which custom agent to use
  agent_label="agent:$matched_agent"
  if ! echo "$labels" | grep -q "$agent_label"; then
    # Create label if it doesn't exist (will fail silently if it already exists)
    gh label create "$agent_label" --repo "$GITHUB_REPOSITORY" --description "Custom agent: $matched_agent" --color "0E8A16" 2>/dev/null || true
    gh issue edit "$issue_number" --repo "$GITHUB_REPOSITORY" --add-label "$agent_label"
    echo "✓ Added $agent_label label to issue #$issue_number"
  fi
  
  # Add agent directive to issue body so Copilot knows which custom agent to use
  # This is crucial: Copilot reads the issue body when assigned to understand context
  echo "📝 Adding agent directive with @mention to issue body..."
  issue_body_original=$(gh issue view "$issue_number" --repo "$GITHUB_REPOSITORY" --json body --jq '.body // ""')
  
  # Check if agent directive already exists in the issue body
  if ! echo "$issue_body_original" | grep -q "<!-- COPILOT_AGENT:"; then
    # Prepend agent directive to issue body with @agent-name mention
    agent_directive="<!-- COPILOT_AGENT:$matched_agent -->

> **🤖 Agent Assignment**
> 
> This issue has been assigned to GitHub Copilot with the **$agent_emoji $matched_agent** custom agent profile.
> 
> **@$matched_agent** - Please use the specialized approach and tools defined in [\`.github/agents/${matched_agent}.md\`](https://github.com/$GITHUB_REPOSITORY/blob/main/.github/agents/${matched_agent}.md).

---

"
    # Combine directive with original body
    new_body="${agent_directive}${issue_body_original}"
    
    # Update issue body using gh issue edit
    echo "$new_body" | gh issue edit "$issue_number" --repo "$GITHUB_REPOSITORY" --body-file -
    echo "✓ Added agent directive with @$matched_agent mention to issue #$issue_number body"
  else
    echo "✓ Agent directive already exists in issue #$issue_number body"
  fi
  
  # Get the issue node ID (required for GraphQL mutation)
  echo "🔍 Fetching issue node ID for issue #$issue_number..."
  issue_node_id=$(gh issue view "$issue_number" --repo "$GITHUB_REPOSITORY" --json id --jq '.id')
  
  if [ -z "$issue_node_id" ]; then
    echo "❌ Failed to get issue node ID for issue #$issue_number"
    failed_count=$((failed_count + 1))
    continue
  fi
  
  echo "📍 Issue node ID: $issue_node_id"
  
  # 🎯 NEW: Try to find custom agent actor ID first
  echo ""
  echo "🔍 Step 1: Searching for custom agent actor ID..."
  echo "   Agent: $matched_agent"
  echo "   Path: .github/agents/${matched_agent}.md"
  
  # Query all suggested actors and look for custom agent match
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
  
  # Log all actors for debugging
  echo "   Available actors in repository:"
  echo "$all_actors" | jq -r '.data.repository.suggestedActors.nodes[] | "     - \(.login) (\(.__typename)): \(.id)"'
  
  # Try to find custom agent by exact name match
  custom_agent_actor_id=$(echo "$all_actors" | jq -r ".data.repository.suggestedActors.nodes[] | select(.login == \"$matched_agent\") | .id")
  
  if [ -n "$custom_agent_actor_id" ]; then
    echo "   ✅ Found custom agent actor ID: $custom_agent_actor_id"
    echo "   🎯 Will assign directly to custom agent: $matched_agent"
    target_actor_id="$custom_agent_actor_id"
    target_actor_name="$matched_agent"
    assignment_method="direct-custom-agent"
  else
    echo "   ℹ️  Custom agent '$matched_agent' not found as separate actor"
    echo ""
    echo "🔍 Step 2: Falling back to generic Copilot actor..."
    
    # Get Copilot's actor ID from the repository's suggested actors
    copilot_actor_id=$(echo "$all_actors" | jq -r '.data.repository.suggestedActors.nodes[] | select(.login | test("copilot"; "i")) | .id' | head -1)
    
    if [ -z "$copilot_actor_id" ]; then
      echo "   ❌ Could not find Copilot actor ID in suggested actors"
      echo "   ℹ️  Copilot may not be enabled for this repository"
      failed_count=$((failed_count + 1))
    
      gh issue comment "$issue_number" --repo "$GITHUB_REPOSITORY" --body "⚠️ **Copilot Not Available**

Could not find GitHub Copilot in the list of available assignees for this repository.

**This means:**
- GitHub Copilot is not enabled for this repository, OR
- The workflow is not using a Personal Access Token (PAT) with proper permissions

**To fix this:**
1. **Enable Copilot:** Go to repository Settings → Copilot and enable GitHub Copilot
2. **Set up PAT:** Create a Personal Access Token with \`repo\` scope at https://github.com/settings/tokens
3. **Add Secret:** Add the PAT as a repository secret named \`COPILOT_PAT\`
4. **Verify Subscription:** Ensure your account has a Copilot subscription (Individual, Business, or Enterprise)

**Note:** The default \`GITHUB_TOKEN\` cannot assign Copilot due to licensing restrictions. A PAT is required.

**For now:**
- This issue has been labeled \`copilot-assigned\` for tracking
- You can manually assign Copilot from the GitHub UI, or assign a developer

---
*🤖 Automated check via GitHub GraphQL API - See https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-a-pr*"
      continue
    fi
    
    echo "   ✅ Found generic Copilot actor ID: $copilot_actor_id"
    echo "   ℹ️  Will assign to Copilot (agent selection via directives)"
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
  
  # Determine which assignment method to use
  PREFERRED_METHOD="${INPUT_ASSIGNMENT_METHOD:-auto}"
  
  echo ""
  echo "   Preferred Assignment Method: $PREFERRED_METHOD"
  
  assignment_successful=false
  
  # Try CLI-based assignment if requested or in auto mode
  if [ "$PREFERRED_METHOD" = "cli" ] || [ "$PREFERRED_METHOD" = "auto" ]; then
    echo ""
    echo "🔧 Attempting CLI-based assignment using 'gh agent-task create'..."
    
    # Authenticate gh CLI for OAuth operations required by agent-task
    # The COPILOT_PAT token is already set as GH_TOKEN in the workflow
    # GitHub CLI will automatically use GH_TOKEN for authentication
    echo "   Setting up gh CLI authentication..."
    
    # Verify we have a token available
    if [ -z "$GH_TOKEN" ]; then
      echo "   ⚠️ No GH_TOKEN available, CLI assignment will likely fail"
    else
      echo "   ✅ GH_TOKEN is set (will be used automatically by gh CLI)"
      
      # Use --with-token to explicitly authenticate with the token
      # This creates a stored credential that gh agent-task can use
      if echo "$GH_TOKEN" | gh auth login --with-token --hostname github.com 2>&1; then
        echo "   ✅ gh CLI authenticated successfully with COPILOT_PAT"
        # Verify authentication status
        if gh auth status 2>&1 | grep -q "Logged in"; then
          echo "   ✅ gh auth status confirmed"
        fi
      else
        echo "   ⚠️ gh auth login failed, CLI assignment may not work"
      fi
    fi
    
    # Build task description with custom agent directive
    # Following GitHub's documentation for custom agent specification in CLI
    # See: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli#use-custom-agents
    task_description="@${matched_agent}

Please use the **${agent_emoji} ${matched_agent}** custom agent to handle this task.

**Custom Agent Profile**: \`.github/agents/${matched_agent}.md\`
**Agent Description**: ${agent_description}
**Specialization**: ${matched_agent}

---

## Task Details

**Issue #${issue_number}**: ${issue_title}

${issue_body}

---

**Instructions for ${matched_agent} agent:**
- Follow the specialized approach defined in \`.github/agents/${matched_agent}.md\`
- Apply your domain-specific expertise and tools
- Ensure the solution aligns with your agent specialization
- Include appropriate tests and documentation as per your agent guidelines"
    
    # Create a temporary file for the task description
    task_file="/tmp/agent-task-${issue_number}.md"
    echo "$task_description" > "$task_file"
    
    # Try to create agent task via CLI
    echo "   Creating agent task from issue #${issue_number}..."
    echo "   Using @${matched_agent} agent directive in task description..."
    cli_result=$(gh agent-task create -F "$task_file" --repo "$GITHUB_REPOSITORY" 2>&1 || echo "CLI_FAILED")
    
    if echo "$cli_result" | grep -qE "(created|session|task)"; then
      echo "   ✅ CLI-based task created successfully!"
      echo "   Result: $cli_result"
      
      # Extract PR or session info if available
      if echo "$cli_result" | grep -qE "pull|PR"; then
        pr_info=$(echo "$cli_result" | grep -oE "https://github.com/[^/]+/[^/]+/pull/[0-9]+" || echo "")
        if [ -n "$pr_info" ]; then
          echo "   🔗 PR created: $pr_info"
        fi
      fi
      
      assignment_successful=true
      actual_method="cli"
      success_count=$((success_count + 1))
      
      # Comment on the issue about CLI assignment
      gh issue comment "$issue_number" --repo "$GITHUB_REPOSITORY" --body "🤖 **Copilot Agent Task Created via CLI**

GitHub Copilot has been assigned to this issue using the **\`gh agent-task create\`** CLI method.

## 🧠 Intelligent Agent Matching

- **Agent**: $agent_emoji $matched_agent
- **Match Confidence**: $agent_confidence
- **Description**: $agent_description
- **Agent Definition**: [\`.github/agents/${matched_agent}.md\`](https://github.com/$GITHUB_REPOSITORY/blob/main/.github/agents/${matched_agent}.md)
- **Assignment Method**: CLI-based (\`gh agent-task create\`)

## 🎯 Custom Agent Directive

The task description includes a directive for Copilot to use the **${matched_agent}** custom agent profile. This approach leverages the GitHub CLI's agent task system.

**What happens next:**
1. ✅ Copilot will analyze the issue using the ${matched_agent} specialization
2. 💻 Copilot will create a branch and implement the solution
3. 📝 Copilot will open a PR with the implementation
4. 🔍 Auto-review workflow will validate and merge
5. ✅ Issue will be automatically closed when complete

**CLI Result:**
\`\`\`
$cli_result
\`\`\`

---
*🤖 Automated via \`gh agent-task create\` CLI with intelligent agent matching*"
      
      rm -f "$task_file"
    else
      echo "   ⚠️ CLI-based assignment failed or not available"
      echo "   Error: $cli_result"
      rm -f "$task_file"
      
      if [ "$PREFERRED_METHOD" = "cli" ]; then
        # CLI was explicitly requested but failed
        echo "   ❌ CLI assignment was required but failed"
        failed_count=$((failed_count + 1))
        
        gh issue comment "$issue_number" --repo "$GITHUB_REPOSITORY" --body "⚠️ **CLI-Based Assignment Failed**

Attempted to assign this issue to GitHub Copilot using \`gh agent-task create\` CLI, but the command failed.

**Error:**
\`\`\`
$cli_result
\`\`\`

**Possible reasons:**
- The \`gh agent-task\` command requires an OAuth token, not a regular PAT
- The COPILOT_PAT may not have the required permissions or token type
- The \`gh agent-task\` feature may not be available in this environment
- Feature may still be in preview/limited availability

**Note about authentication:**
The \`gh agent-task create\` command has stricter authentication requirements than other GitHub CLI commands. It requires an OAuth token obtained through interactive login, which is challenging to automate in CI/CD environments. The workflow will automatically fall back to GraphQL API assignment.

**Matched Agent:** $agent_emoji $matched_agent

The system will automatically attempt GraphQL-based assignment as a fallback."
        
        continue
      fi
      # If auto mode, we'll fall through to GraphQL method
    fi
  fi
  
  # Use GraphQL API assignment if CLI wasn't used or failed
  if [ "$assignment_successful" = false ] && [ "$PREFERRED_METHOD" != "cli" ]; then
    # Assign issue using GraphQL API
    echo ""
    echo "🤖 Assigning issue #$issue_number via GraphQL API..."
  
    # Use GraphQL mutation to assign (this is the official method per GitHub docs)
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
      success_count=$((success_count + 1))
      actual_method="graphql"
      
      # Build success message based on assignment method
      if [ "$assignment_method" = "direct-custom-agent" ]; then
        assignment_details="
## 🎯 Direct Custom Agent Assignment

**SUCCESS!** This issue was assigned directly to the custom agent actor:

- **Custom Agent**: $agent_emoji $matched_agent
- **Actor ID**: \`$target_actor_id\`
- **Agent Path**: [\`.github/agents/${matched_agent}.md\`](https://github.com/$GITHUB_REPOSITORY/blob/main/.github/agents/${matched_agent}.md)
- **Assignment Method**: Direct API assignment to custom agent actor

The custom agent has its own actor ID in the GitHub API, allowing direct assignment without directives."
      else
        assignment_details="
## 🧠 Intelligent Agent Matching

This issue has been analyzed and matched to the **$agent_emoji $matched_agent** specialization:

- **Agent**: $matched_agent
- **Match Confidence**: $agent_confidence
- **Match Score**: $agent_score
- **Description**: $agent_description
- **Agent Path**: [\`.github/agents/${matched_agent}.md\`](https://github.com/$GITHUB_REPOSITORY/blob/main/.github/agents/${matched_agent}.md)
- **Assignment Method**: Generic Copilot with agent directives

## 🎯 Copilot Agent Directive

@copilot please use the **$matched_agent** custom agent profile from \`.github/agents/${matched_agent}.md\` when working on this issue. Follow the specialized approach, tools, and best practices defined in that agent's configuration.

The implementation should align with the [$matched_agent agent definition](https://github.com/$GITHUB_REPOSITORY/blob/main/.github/agents/${matched_agent}.md) and its specialized capabilities."
      fi
      
      # Add success comment with agent matching info
      gh issue comment "$issue_number" --repo "$GITHUB_REPOSITORY" --body "🤖 **Copilot Assigned Successfully**

GitHub Copilot has been automatically assigned to this issue via the official GitHub GraphQL API.
$assignment_details

**What happens next:**
1. ✅ Copilot will analyze the issue requirements using the $matched_agent specialization
2. 💻 Copilot will create a branch and implement the solution following the $matched_agent approach
3. 📝 Copilot will open a PR with the implementation
4. 🔍 Auto-review workflow will validate and merge
5. ✅ Issue will be automatically closed when complete

**Estimated time:** Copilot typically starts work within a few minutes
**Assigned at:** $(date -u +'%Y-%m-%d %H:%M:%S UTC')

---
*🤖 Automated via intelligent agent matching + GitHub GraphQL API with direct custom agent support*"
    else
      echo "❌ Failed to assign issue #$issue_number"
      echo "Error details: $mutation_result"
      failed_count=$((failed_count + 1))
      
      # Add error comment with details
      gh issue comment "$issue_number" --repo "$GITHUB_REPOSITORY" --body "⚠️ **Failed to Assign Copilot via GraphQL API**

The workflow attempted to assign GitHub Copilot to this issue using the official GraphQL API method, but the assignment failed.

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

**Other Possible Reasons:**
- GitHub Copilot is not enabled for this repository
- Copilot coding agent is not activated for your organization
- You need a GitHub Copilot subscription (Individual, Business, or Enterprise)
- The repository lacks necessary Copilot permissions

**For now:**
- This issue has been labeled \`copilot-assigned\` for tracking
- You can manually assign Copilot from the GitHub UI
- Or assign a developer to implement this manually

**To manually assign Copilot:**
- Click on \"Assignees\" in the right sidebar
- Select \"Copilot\" from the dropdown
- Copilot should automatically pick up the issue

---
*🤖 Automated via the official GitHub GraphQL API as documented at https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-a-pr*"
    fi
  fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Successfully assigned: $success_count"
echo "✓ Already assigned: $already_assigned_count"
echo "❌ Failed: $failed_count"
echo "Timestamp: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
