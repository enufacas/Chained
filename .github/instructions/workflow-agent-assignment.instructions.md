---
applyTo:
  - ".github/workflows/copilot-*.yml"
  - ".github/workflows/*-agent-*.yml"
  - ".github/workflows/agent-*.yml"
---

# Agent Assignment Workflow Instructions

## Primary Directive: Agent Name Enforcement

When creating or modifying workflows that assign work to custom agents, enforce explicit agent naming:

### Required Elements in Every Workflow

1. **Issue Body Updates**
   - MUST include `@agent-name` in the directive section
   - MUST add "IMPORTANT: Always mention @agent-name by name" reminder
   - Example:
     ```markdown
     > **@engineer-master** - Please use the engineer-master custom agent profile.
     > 
     > **IMPORTANT**: Always mention **@engineer-master** by name in all conversations.
     ```

2. **Comment Generation**
   - MUST use `@agent-name` in all automated comments
   - MUST bold the @mention: `**@agent-name**`
   - MUST include agent name in action descriptions
   - Example:
     ```markdown
     **@troubleshoot-expert** will analyze the workflow failure.
     ```

3. **Assignment Messages**
   - MUST specify assigned agent with @mention in success messages
   - Format: "Assigned agent: @agent-name (specialization)"
   - Example:
     ```markdown
     **Assigned agent:** @create-guru (infrastructure creation)
     ```

4. **Step-by-Step Instructions**
   - MUST prefix each step with `**@agent-name**`
   - Make it clear WHO is doing WHAT
   - Example:
     ```markdown
     1. ✅ **@assert-specialist** will create comprehensive test cases
     2. 💻 **@assert-specialist** will run the test suite
     3. 📝 **@assert-specialist** will document test coverage
     ```

### Shell Script Requirements

For bash/shell scripts in workflows:
- Store agent name in variable: `matched_agent="engineer-master"`
- ALWAYS reference with @: `@$matched_agent` or `@${matched_agent}`
- Include in all echo/comment outputs
- Example:
  ```bash
  echo "Assigning to **@${matched_agent}**"
  gh issue comment "$issue_number" --body "**@${matched_agent}** will handle this"
  ```

### Python Script Requirements

For Python scripts that match or assign agents:
- Return agent names without @ in data structures
- ALWAYS add @ when generating user-facing text
- Example:
  ```python
  agent_name = "organize-guru"
  message = f"**@{agent_name}** has been selected for this refactoring task"
  ```

### Testing Requirements

Before merging workflow changes:
- Verify all outputs include @agent-name
- Check issue body updates have @mentions
- Confirm comments show proper @agent-name format
- Test with multiple agent types
- Validate reminder text is present

### Documentation Requirements

When documenting workflows:
- Show examples with real @agent-name mentions
- Explain WHY @mentions are required
- Link to agent list with proper @mention syntax
- Include troubleshooting for missing mentions
