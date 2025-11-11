# Custom Agent API Invocation Insights

## Overview

This document captures key insights from analyzing GitHub Actions logs (run 19253915320) about how GitHub Copilot custom agents are invoked via the API. These insights can help configure and troubleshoot custom agent assignment.

## Key Discovery: Agent Specification via Environment Variables

The logs reveal that custom agents are NOT selected via the GraphQL `replaceActorsForAssignable` mutation parameters. Instead, the agent model/type is specified through **environment variables** when the Copilot runtime is invoked.

### Critical Environment Variable: COPILOT_AGENT_MODEL

From the logs:
```bash
COPILOT_AGENT_MODEL: sweagent-capi:claude-sonnet-4.5
```

This environment variable specifies which agent model/runtime to use. The format appears to be:
- `sweagent-capi` - The agent runtime/system
- `claude-sonnet-4.5` - The underlying LLM model

**Insight**: Custom agent selection happens at the runtime invocation level, not at the issue assignment level.

## Environment Variables for Agent Configuration

The logs expose the complete set of environment variables used to configure the Copilot agent:

### Identity & Session
```bash
COPILOT_AGENT_ACTOR: enufacas                    # User who triggered the agent
COPILOT_AGENT_ACTOR_ID: 1485431                  # User's GitHub actor ID
COPILOT_AGENT_SESSION_ID: 20e16a96-0f40-4cff-9080-eddd5c54e418
COPILOT_AGENT_JOB_ID: 1485431-1092617192-e742e379-4adc-43ad-a0fc-80a6435c6528
```

### Task Context
```bash
COPILOT_AGENT_ACTION: fix                        # Type of action (fix, implement, etc.)
COPILOT_AGENT_PROMPT: RG9jIG1hc3RlciB3aGF0IGlzIHlvdXIgYWN0b3JpZD8=  # Base64 encoded
COPILOT_AGENT_ISSUE_NUMBER: 0                    # Issue number (0 if not from issue)
COPILOT_AGENT_PR_NUMBER:                         # PR number (empty if not from PR)
```

**The prompt decodes to**: `"Doc master what is your actorid?"`

### Repository Context
```bash
COPILOT_AGENT_BASE_COMMIT: refs/heads/main
COPILOT_AGENT_BRANCH_NAME: copilot/update-actorid-documentation
COPILOT_AGENT_PR_COMMIT_COUNT: 1
```

### Runtime Configuration
```bash
COPILOT_AGENT_RUNTIME_VERSION: runtime-f3613bf5ec2817b73adf2dd3f90afcf66893ba7a
COPILOT_AGENT_MODEL: sweagent-capi:claude-sonnet-4.5
COPILOT_AGENT_START_TIME_SEC: 1762831566
COPILOT_AGENT_TIMEOUT_MIN: 59
COPILOT_AGENT_CONTENT_FILTER_MODE: hidden_characters
```

### API Endpoints
```bash
COPILOT_API_URL: https://api.githubcopilot.com
COPILOT_AGENT_CALLBACK_URL: https://api.githubcopilot.com/agents/swe/agent
```

### Git Configuration
```bash
COPILOT_AGENT_COMMIT_LOGIN: copilot-swe-agent[bot]
COPILOT_AGENT_COMMIT_EMAIL: 198982749+Copilot@users.noreply.github.com
```

## Tool Restrictions for Custom Agents

**Critical Discovery**: Custom agents have **limited tool access** compared to what's available in the main Copilot runtime.

From the logs, when the agent tried to use `bash`:
```
Tool 'bash' does not exist. Available tools that can be called are view, create, edit, report_progress.
```

### Available Tools
Based on the logs, custom agents in this invocation had access to:
- `view` - View files and directories
- `create` - Create new files
- `edit` - Edit existing files
- `report_progress` - Report progress on tasks

### Tools NOT Available (in this instance)
- `bash` - Execute shell commands
- GitHub API tools (github-mcp-server-*)
- Web search capabilities
- Browser/playwright tools

**Important**: Tool availability may vary based on the agent configuration and runtime version. The specific set of tools should be configured in the `.github/agents/<agent-name>.md` file.

## Agent Response Format Expectations

The logs reveal that GitHub expects specific XML-style tags in agent responses for certain workflows:

### PR Template Response Format
When looking for PR templates, the workflow expects:
```xml
<template_path>path/to/template.md</template_path>
<template_content>
# Template content here
</template_content>
```

From the logs:
```
Agent response did not contain expected template_path and template_content tags
```

This indicates that custom agents should structure their responses with appropriate XML-style tags when the workflow expects specific data formats.

## Custom Agent Selection Mechanism

Based on the investigation documented in `CUSTOM_AGENT_ASSIGNMENT_INVESTIGATION.md` and these log insights, here's how custom agent selection actually works:

### Current Understanding

1. **Issue Assignment** (via GraphQL API)
   - Assigns the issue to "github-copilot" actor (or custom agent actor if available)
   - Uses `replaceActorsForAssignable` mutation
   - Cannot specify agent specialization in this API call

2. **Agent Invocation** (via Copilot runtime)
   - The runtime reads issue metadata (labels, body directives)
   - Determines which agent model to use
   - Sets `COPILOT_AGENT_MODEL` environment variable
   - Launches the agent with specific tool configuration

3. **Agent Execution**
   - Agent receives environment variables with full context
   - Agent has access to configured tools (limited set)
   - Agent reads issue content and directives
   - Agent implements solution following specialization

### The Missing Link

**What we don't know yet**: How does the Copilot runtime map from issue metadata (labels, directives) to the `COPILOT_AGENT_MODEL` environment variable?

Possible mechanisms:
- A. Label-based mapping (e.g., `agent:doc-master` → specific model config)
- B. Issue body directive parsing (e.g., `<!-- COPILOT_AGENT:doc-master -->`)
- C. External configuration file that defines agent-to-model mappings
- D. Manual UI selection that gets stored in GitHub's database

## Practical Implications

### For Workflow Design

1. **Agent Assignment**: Use GraphQL mutation to assign issues
   ```graphql
   mutation {
     replaceActorsForAssignable(input: {
       assignableId: "<ISSUE_ID>",
       actorIds: ["<COPILOT_ACTOR_ID>"]
     }) { ... }
   ```

2. **Agent Metadata**: Add metadata to help runtime select correct agent
   - Label: `agent:doc-master`
   - Body directive: `<!-- COPILOT_AGENT:doc-master -->`
   - Comment directive: `@copilot please use doc-master agent`

3. **Tool Configuration**: Define tools in `.github/agents/<agent-name>.md`
   ```yaml
   ---
   name: doc-master
   tools:
     - view
     - edit
     - create
     - github-mcp-server-get_file_contents
     - github-mcp-server-search_code
   ---
   ```

### For Custom Agent Development

1. **Expect Limited Tools**: Don't assume `bash` or all tools are available
2. **Use Structured Responses**: For workflows expecting specific formats, use XML-style tags
3. **Read Environment Variables**: Agent can access rich context via environment variables
4. **Handle Base64 Prompts**: Prompts may be base64 encoded

### For Debugging

When debugging custom agent invocation:

1. **Check Environment Variables**: Look for `COPILOT_AGENT_*` variables in logs
2. **Verify Tool Availability**: Check error messages about missing tools
3. **Inspect API Calls**: Look for GraphQL mutation logs
4. **Review Response Format**: Check if response tags match expectations

## Example: Custom Agent Invocation Flow

Based on the logs, here's a complete flow:

```bash
# 1. Issue is created
issue_number=123
issue_title="Improve documentation"

# 2. Workflow matches issue to agent
matched_agent="doc-master"

# 3. Workflow adds metadata
gh issue edit $issue_number --add-label "agent:doc-master"
gh issue edit $issue_number --body "<directive>$body</directive>"

# 4. Workflow assigns via GraphQL
gh api graphql -f query='
  mutation($issueId: ID!, $actorId: ID!) {
    replaceActorsForAssignable(input: {
      assignableId: $issueId,
      actorIds: [$actorId]
    }) { ... }
  }' -f issueId="$issue_node_id" -f actorId="$copilot_actor_id"

# 5. Copilot runtime launches (GitHub internal)
# Sets environment variables:
export COPILOT_AGENT_MODEL="sweagent-capi:claude-sonnet-4.5"
export COPILOT_AGENT_ACTOR="enufacas"
export COPILOT_AGENT_ACTION="fix"
export COPILOT_AGENT_PROMPT="$(echo 'Improve documentation' | base64)"
# ... many other variables ...

# 6. Agent executes with limited tools
# - Reads environment variables
# - Analyzes issue content
# - Implements solution using available tools
# - Creates PR with changes
```

## Questions for Future Investigation

1. **Model Selection**: How exactly does GitHub map agent metadata to `COPILOT_AGENT_MODEL`?
2. **Tool Configuration**: How are tool restrictions enforced? Can they be customized per agent?
3. **Actor IDs**: Can custom agents have separate actor IDs, or do they all share the Copilot actor ID?
4. **Response Formats**: What other response format expectations exist beyond PR templates?
5. **Runtime Versions**: How do different `COPILOT_AGENT_RUNTIME_VERSION` values affect behavior?

## Related Documentation

- [Custom Agent Assignment Investigation](../CUSTOM_AGENT_ASSIGNMENT_INVESTIGATION.md) - Complete investigation of assignment mechanism
- [Custom Agent Assignment Limitations](./CUSTOM_AGENT_ASSIGNMENT_LIMITATIONS.md) - Known limitations and workarounds
- [Inspecting Agent Assignments](./INSPECTING_AGENT_ASSIGNMENTS.md) - Tools for debugging assignments
- [Actor ID System](./ACTOR_ID_SYSTEM.md) - Explanation of agent ID systems
- [Copilot GraphQL Assign Workflow](../.github/workflows/copilot-graphql-assign.yml) - Implementation of assignment logic

## References

- GitHub Actions Run: https://github.com/enufacas/Chained/actions/runs/19253915320/job/55044456947
- GitHub Copilot API: https://api.githubcopilot.com
- GitHub Docs: [Creating Custom Agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
- GitHub Docs: [Assigning Issues to Copilot](https://docs.github.com/copilot/how-tos/use-copilot-agents/coding-agent/assign-copilot-to-an-issue)

---

**Last Updated**: 2025-11-11  
**Source**: Analysis of GitHub Actions run 19253915320  
**Status**: Active investigation - mechanisms still being discovered
