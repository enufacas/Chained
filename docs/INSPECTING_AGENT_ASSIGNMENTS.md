# Inspecting Custom Agent Assignments

This guide explains how to use the API to inspect issue assignments and discover custom agent actor IDs for direct programmatic assignment.

## Background

When you assign a custom agent to an issue via the GitHub UI, that assignment is recorded in the GitHub API. By inspecting the assignment history, we can discover:

1. Whether custom agents have separate actor IDs
2. The exact actor ID for each custom agent
3. How to use those IDs for direct API assignment

**Related Documentation:**
- [Custom Agent API Invocation](./CUSTOM_AGENT_API_INVOCATION.md) - Deep dive into how agents are invoked via API based on actual log analysis
- [Custom Agent Assignment Investigation](../CUSTOM_AGENT_ASSIGNMENT_INVESTIGATION.md) - Complete investigation history
- [Actor ID System](./ACTOR_ID_SYSTEM.md) - Explanation of agent ID systems

## Tools

### 1. Inspect Issue Assignment Tool

**Purpose**: Examines a specific issue's assignment history to detect custom agent assignments.

**Usage**:
```bash
export GH_TOKEN="your_github_token"
python3 tools/inspect-issue-assignment.py <owner> <repo> <issue_number>
```

**Example**:
```bash
python3 tools/inspect-issue-assignment.py enufacas Chained 42
```

**What it shows**:
- Current assignees with their actor IDs
- Assignment timeline (who assigned what, when)
- Detection of custom agents vs generic Copilot
- Actor IDs that can be used for API assignment

### 2. List Agent Actor IDs Tool

**Purpose**: Lists all custom agents and their corresponding actor IDs (if they exist).

**Usage**:
```bash
export GH_TOKEN="your_github_token"
python3 tools/list-agent-actor-ids.py <owner> <repo>
```

**Example**:
```bash
python3 tools/list-agent-actor-ids.py enufacas Chained
```

**What it shows**:
- All custom agents found in `.github/agents/`
- Which agents have actor IDs in the GitHub API
- Ready-to-use actor IDs for direct assignment

### 3. Inspect Issue Assignment Workflow

**Purpose**: GitHub Actions workflow for inspecting assignments without local setup.

**Usage**:
1. Go to repository Actions tab
2. Select "Inspect Issue Assignment" workflow
3. Click "Run workflow"
4. Enter the issue number
5. View the results in the workflow logs

**What it shows**:
- Full assignment history
- Raw API responses
- Custom agent detection
- Recommendations for next steps

## How to Use This to Enable Direct Assignment

### Step 1: Assign a Custom Agent via UI

1. Open an issue in the repository
2. Click "Assignees" in the right sidebar
3. Select a custom agent (e.g., "bug-hunter")
4. The agent is now assigned

### Step 2: Inspect the Assignment

Run one of the inspection tools to see how GitHub recorded the assignment:

```bash
# Using the Python tool
export GH_TOKEN="your_token"
python3 tools/inspect-issue-assignment.py enufacas Chained <issue_number>
```

Or use the GitHub Actions workflow (no local setup needed).

### Step 3: Capture the Actor ID

The tool will show you something like:

```
✅ bug-hunter
   Type: Bot
   Actor ID: MDQ6VXNlcjE2NTI4NDU5
   URL: https://github.com/bug-hunter
   🎯 CUSTOM AGENT DETECTED!
```

This proves:
- The custom agent has a separate actor ID: `MDQ6VXNlcjE2NTI4NDU5`
- The login name matches the agent name: `bug-hunter`
- It's identified as a Bot type in the API

### Step 4: Use for Direct Assignment

Now you can assign directly via API using this actor ID:

```bash
gh api graphql -f query='
  mutation {
    replaceActorsForAssignable(input: {
      assignableId: "<ISSUE_NODE_ID>",
      actorIds: ["MDQ6VXNlcjE2NTI4NDU5"]
    }) {
      assignable {
        ... on Issue {
          assignees(first: 10) {
            nodes {
              login
            }
          }
        }
      }
    }
  }'
```

The workflow (`copilot-graphql-assign.yml`) already implements this logic:
1. It first tries to find the custom agent actor ID
2. If found, it assigns directly to that actor
3. If not found, it falls back to generic Copilot with directives

## What We Can Learn

By inspecting UI assignments, we can discover:

### If Custom Agents Have Actor IDs

**Scenario A**: Custom agent appears as assignee with unique actor ID
- ✅ Custom agents have separate actor IDs
- ✅ Direct API assignment is possible
- ✅ The workflow will use direct assignment

**Scenario B**: Only "github-copilot" appears as assignee
- ❌ Custom agents don't have separate actor IDs
- ❌ They are profiles/configurations, not actors
- ℹ️ The workflow will use directive-based assignment

### Actor ID Format

Custom agent actor IDs follow GitHub's node ID format:
- Format: Base64-encoded string (e.g., `MDQ6VXNlcjE2NTI4NDU5`)
- Type: Usually appears as "Bot" in the API
- Stable: The ID remains constant across API calls

### Assignment Timeline

The timeline shows:
- When the agent was assigned
- Who performed the assignment
- Previous assignment changes

This helps understand:
- Whether manual UI assignments work differently than API assignments
- If agent reassignment affects behavior
- Historical context for troubleshooting

## Example Output

When a custom agent is detected:

```
================================================================
🔍 Issue Assignment History Inspector
================================================================

Current Assignees:
✅ bug-hunter
   Type: Bot
   Actor ID: MDQ6VXNlcjE2NTI4NDU5
   URL: https://github.com/bug-hunter
   🎯 CUSTOM AGENT DETECTED!

Assignment History:
#1 ✅ ASSIGNED
   When: 2025-11-11 02:45:30 UTC
   By: enufacas
   Assignee: bug-hunter
   Assignee Type: Bot
   Assignee ID: MDQ6VXNlcjE2NTI4NDU5
   🎯 CUSTOM AGENT INDICATOR!

Analysis:
🎉 CUSTOM AGENT ASSIGNMENT DETECTED!

Custom agent(s) found as assignees:
  Agent: bug-hunter
  Actor ID: MDQ6VXNlcjE2NTI4NDU5

💡 KEY INSIGHTS:
1. Custom agents HAVE separate actor IDs in the GitHub API
2. When assigned via UI, they appear as Bot type assignees
3. Their login matches the agent name (e.g., 'bug-hunter')
4. We CAN use these actor IDs for programmatic assignment!
```

## Integration with the Workflow

The `copilot-graphql-assign.yml` workflow already uses this information:

1. **Step 1**: Query all available actors
2. **Step 2**: Try to match custom agent name to actor login
3. **Step 3**: If match found, use custom agent actor ID
4. **Step 4**: If not found, fallback to generic Copilot + directives

This means:
- If custom agents have actor IDs, direct assignment works automatically
- If not, the workflow gracefully falls back to directives
- The logs show which method was used for transparency

## Troubleshooting

### No Custom Agent Detected

If the tool shows no custom agent even though you assigned one:

1. **Check agent configuration**: Verify `.github/agents/<name>.md` exists
2. **Verify UI assignment**: Ensure the agent shows in the issue's assignees
3. **Check token permissions**: Use a PAT with `repo` scope
4. **Wait for sync**: GitHub API might take a moment to reflect changes

### Actor ID Not Found

If the agent shows as assignee but no actor ID is found:

1. **API limitation**: Custom agents might not have actor IDs in your setup
2. **Check agent type**: Verify the assignee type is "Bot"
3. **GitHub configuration**: Custom agents might not be fully enabled

### Wrong Agent Assigned

If a different agent than expected is assigned:

1. **Check name matching**: Agent name must exactly match file name
2. **Review logs**: The workflow logs show which agent was matched
3. **Verify directives**: Check if issue body contains agent directives

## Related Documentation

- [Custom Agent Assignment](./CUSTOM_AGENT_ASSIGNMENT_LIMITATIONS.md) - How assignment works
- [Intelligent Agent Matching](./INTELLIGENT_AGENT_MATCHING.md) - How agents are matched
- [Custom Agents Conventions](./CUSTOM_AGENTS_CONVENTIONS.md) - Agent structure and format

## Conclusion

By inspecting UI assignments via the API, we can:
1. ✅ Discover if custom agents have actor IDs
2. ✅ Capture those actor IDs for programmatic use
3. ✅ Enable direct assignment without workarounds
4. ✅ Build a reliable automated assignment system

The workflow is designed to automatically adapt based on what it discovers in the API.
