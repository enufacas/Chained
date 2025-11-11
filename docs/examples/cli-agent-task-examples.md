# Example: Creating Agent Tasks with Custom Agents via CLI

This document provides practical examples of using the GitHub CLI to create agent tasks with custom agent specifications, following [GitHub's official documentation](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli#use-custom-agents).

## Basic Syntax

The key to specifying a custom agent in the CLI is using the `@agent-name` syntax at the beginning of your task description:

```bash
gh agent-task create "@bug-hunter Please fix the login crash reported in issue #123"
```

## Example 1: Bug Fix with Bug Hunter Agent

```bash
gh agent-task create "@bug-hunter

Please investigate and fix the null pointer exception in the authentication module.

**Issue Details:**
- Users are experiencing crashes when logging in with social accounts
- Stack trace shows NPE in AuthController line 45
- Affects approximately 5% of login attempts

**Expected Fix:**
- Add proper null checking
- Include unit tests for edge cases
- Update error handling to prevent crashes
"
```

## Example 2: Feature Development with Feature Architect

```bash
gh agent-task create "@feature-architect

Design and implement a new user dashboard feature.

**Requirements:**
- Display user statistics and activity
- Include customizable widgets
- Support dark/light theme
- Mobile-responsive design

**Technical Considerations:**
- Use existing component library
- Follow current architecture patterns
- Ensure accessibility compliance
"
```

## Example 3: Using a Task Description File

Create a file `task-description.md`:

```markdown
@doc-master

Please create comprehensive documentation for our new API endpoints.

**Documentation Needed:**
1. API Reference
   - All endpoints with parameters
   - Request/response examples
   - Error codes and handling

2. Getting Started Guide
   - Authentication setup
   - First API call tutorial
   - Common use cases

3. Best Practices
   - Rate limiting
   - Error handling
   - Security considerations

**Target Audience:**
External developers integrating with our API

**Deliverables:**
- Markdown documentation in `/docs/api/`
- OpenAPI/Swagger specification
- Code examples in Python and JavaScript
```

Then use the CLI:

```bash
gh agent-task create -F task-description.md --repo owner/repo
```

## Example 4: Performance Optimization Task

```bash
gh agent-task create "@performance-optimizer

Investigate and resolve slow database query performance in the analytics dashboard.

**Current Performance:**
- Dashboard load time: 8-12 seconds
- Primary bottleneck: user_analytics query
- Affects 1000+ users daily

**Optimization Goals:**
- Reduce load time to < 2 seconds
- Add appropriate database indexes
- Implement query result caching
- Monitor performance improvements

**Success Metrics:**
- Query execution time reduced by 80%+
- Dashboard renders in < 2 seconds
- No impact on data accuracy
"
```

## Automated Workflow Example

The Chained repository automatically uses this syntax in the `copilot-graphql-assign.yml` workflow:

```yaml
# Workflow generates task description like:
task_description="@${matched_agent}

Please use the **${agent_emoji} ${matched_agent}** custom agent to handle this task.

**Custom Agent Profile**: \`.github/agents/${matched_agent}.md\`
**Agent Description**: ${agent_description}

---

## Task Details

**Issue #${issue_number}**: ${issue_title}

${issue_body}
"

# Create the task
gh agent-task create -F task-file.md --repo owner/repo
```

## Best Practices

### 1. Always Start with @agent-name
```bash
# ✅ CORRECT
gh agent-task create "@bug-hunter Fix the login issue"

# ❌ INCORRECT (agent reference not at start)
gh agent-task create "Fix the login issue @bug-hunter"
```

### 2. Use the Exact Agent Name
```bash
# ✅ CORRECT (matches .github/agents/bug-hunter.md)
@bug-hunter

# ❌ INCORRECT (doesn't match filename)
@bug_hunter
@BugHunter
@bug-hunter-agent
```

### 3. Provide Context After Agent Reference
```bash
@security-guardian

[Clear task description with context]
[Security requirements]
[Expected outcomes]
```

### 4. Reference Agent Profile
Always include a reference to the agent's profile:
```bash
@doc-master

**Agent Profile**: `.github/agents/doc-master.md`

[Task description]
```

### 5. Use --follow for Real-time Feedback
```bash
gh agent-task create "@bug-hunter Debug memory leak" --follow
```

This lets you see the agent's progress in real-time.

## Troubleshooting

### Agent Not Recognized

If the custom agent isn't being used:

1. **Check agent name matches file**: The name after `@` must exactly match the `.md` file in `.github/agents/`
2. **Verify agent file exists**: Ensure `.github/agents/agent-name.md` exists
3. **Check agent file format**: Agent definition must follow the required format
4. **Position matters**: The `@agent-name` must be at the very start

### CLI Command Fails

```bash
# Check CLI version
gh --version

# Verify authentication
gh auth status

# Test with simple task first
gh agent-task create "Test task"
```

## References

- [GitHub Docs: Use Custom Agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli#use-custom-agents)
- [GitHub Docs: Create Custom Agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
- [CLI Agent Assignment Documentation](../CLI_AGENT_ASSIGNMENT.md)

---

**Last Updated**: 2025-11-11  
**Status**: Active Examples
