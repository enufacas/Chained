# CLI-Based Custom Agent Assignment

## Overview

This document describes how the Chained repository uses the GitHub CLI (`gh agent-task create`) to assign custom agents to issues, in addition to the traditional GraphQL API method.

## Background

The GitHub Copilot CLI provides an `agent-task` command that allows creating agent tasks directly from the command line. This feature is currently in preview and provides an alternative to the GraphQL API for assigning issues to Copilot.

## Assignment Methods

The `copilot-graphql-assign.yml` workflow now supports three assignment methods:

### 1. Auto Mode (Default)
- **Method**: `auto`
- **Behavior**: Tries CLI-based assignment first, falls back to GraphQL if CLI fails
- **Best for**: Maximum flexibility and resilience

### 2. GraphQL Mode
- **Method**: `graphql`
- **Behavior**: Uses only the GraphQL API mutation (`replaceActorsForAssignable`)
- **Best for**: Proven, stable assignment method

### 3. CLI Mode
- **Method**: `cli`
- **Behavior**: Uses only `gh agent-task create` command
- **Best for**: Testing CLI capabilities, leveraging future CLI features

## How It Works

### CLI-Based Assignment Process

1. **Agent Matching**: The workflow analyzes the issue and matches it to the most appropriate custom agent (e.g., bug-hunter, feature-architect, etc.)

2. **Task Description Generation**: Creates a markdown task description that includes:
   - Custom agent directive: `<!-- COPILOT_AGENT:agent-name -->`
   - Agent profile reference
   - Original issue title and body

3. **CLI Command Execution**:
   ```bash
   gh agent-task create -F task-description.md --repo owner/repo
   ```

4. **Result Handling**:
   - **Success**: Comments on the issue with CLI assignment details
   - **Failure**: Falls back to GraphQL (in auto mode) or reports error (in cli mode)

### GraphQL-Based Assignment Process

When CLI is not used or fails, the workflow uses the GraphQL API:

1. Query for custom agent actor ID
2. If found, assign directly to custom agent
3. If not found, assign to generic Copilot with directives

## Configuration

### Workflow Dispatch Input

You can manually trigger the workflow with a specific assignment method:

```yaml
workflow_dispatch:
  inputs:
    issue_number: "123"
    assignment_method: "auto"  # or "graphql" or "cli"
```

### Using the CLI Method

To use the CLI method for a specific issue:

```bash
gh workflow run copilot-graphql-assign.yml \
  -f issue_number=123 \
  -f assignment_method=cli
```

## Custom Agent Directives

Both methods include custom agent directives to help Copilot understand which specialized agent should handle the task:

### In Issue Body (GraphQL Method)
```markdown
<!-- COPILOT_AGENT:bug-hunter -->

> **🤖 Agent Assignment**
> 
> This issue has been assigned to GitHub Copilot with the **🐛 bug-hunter** custom agent profile.
```

### In Task Description (CLI Method)
```markdown
<!-- COPILOT_AGENT:bug-hunter -->

## Custom Agent Assignment

This task should be handled by the **🐛 bug-hunter** custom agent.

**Agent Profile**: `.github/agents/bug-hunter.md`
```

## Advantages of CLI Method

1. **Simpler Syntax**: Single command vs complex GraphQL mutation
2. **Future-Proof**: May gain flags for custom agent specification
3. **Direct Task Creation**: Creates agent tasks directly without issue-to-PR conversion
4. **Better Integration**: Native GitHub CLI integration

## Current Limitations

1. **Preview Status**: The `gh agent-task` command is in preview and subject to change
2. **No Custom Agent Flag**: Currently no direct flag to specify custom agents
3. **Limited Availability**: May not be available in all environments
4. **Documentation**: Limited official documentation available

## Environment Requirements

The CLI method requires:
- GitHub CLI (`gh`) installed and authenticated
- `GH_TOKEN` environment variable set (PAT recommended for Copilot)
- Repository with Copilot enabled
- Access to preview features

## Troubleshooting

### CLI Assignment Fails

If you see "CLI-based assignment failed":

1. **Check CLI Version**:
   ```bash
   gh --version
   ```
   Ensure you have a recent version with agent-task support.

2. **Verify Authentication**:
   ```bash
   gh auth status
   ```
   Should show authenticated with appropriate scopes.

3. **Test Manually**:
   ```bash
   gh agent-task create "Test task" --repo owner/repo
   ```

4. **Fall Back to GraphQL**: Set `assignment_method: graphql` in workflow inputs

### Custom Agent Not Recognized

If the custom agent directive isn't being respected:

1. Verify agent definition exists in `.github/agents/agent-name.md`
2. Check agent definition follows the correct format
3. Review GitHub Copilot logs for agent selection details
4. Consider using GraphQL method with direct actor ID assignment

## Future Enhancements

Potential improvements as the CLI matures:

1. **Custom Agent Flag**: `gh agent-task create --agent bug-hunter "Fix crash"`
2. **Agent Discovery**: `gh agent-task list-agents` to see available custom agents
3. **Better Feedback**: More detailed success/failure messages
4. **Session Management**: Better tracking of CLI-created tasks

## References

- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub Copilot Agents Documentation](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
- [gh agent-task Command Help](https://cli.github.com/manual/gh_agent-task)
- [Custom Agent Assignment Investigation](../CUSTOM_AGENT_ASSIGNMENT_INVESTIGATION.md)
- [Custom Agent API Insights](../CUSTOM_AGENT_API_INSIGHTS.md)

## Related Documentation

- [Intelligent Agent Matching](./INTELLIGENT_AGENT_MATCHING.md)
- [Custom Agent Assignment Limitations](./CUSTOM_AGENT_ASSIGNMENT_LIMITATIONS.md)
- [Inspecting Agent Assignments](./INSPECTING_AGENT_ASSIGNMENTS.md)
- [Actor ID System](./ACTOR_ID_SYSTEM.md)

---

**Last Updated**: 2025-11-11  
**Status**: Implemented and Available
