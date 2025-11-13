---
applyTo:
  - "**/*issue*.md"
  - "**/*pull_request*.md"
  - ".github/ISSUE_TEMPLATE/**"
  - ".github/PULL_REQUEST_TEMPLATE/**"
---

# Issue and PR Template Agent Mention Rules

## Mandatory Agent Reference Format

All issue and pull request interactions MUST follow these agent mention conventions:

### 1. In Issue Descriptions

When a custom agent is assigned to an issue, the issue body MUST contain:

```markdown
## 🤖 Assigned Agent

**@agent-name** (Specialization: [agent specialty])

This issue has been assigned to @agent-name based on intelligent matching.

### Agent Instructions
@agent-name should follow the specialized approach defined in `.github/agents/agent-name.md`.

**REMINDER:** Always mention **@agent-name** by name in all related discussions and PRs.
```

### 2. In PR Descriptions

When a custom agent creates or works on a PR, the PR description MUST include:

```markdown
## 👤 Agent

Created by: **@agent-name**

### Work Completed
**@agent-name** has implemented the following changes:
- [specific changes by @agent-name]

### Review Notes
When reviewing this PR, consider @agent-name's specialization in [specialty].
```

### 3. In Issue Comments

All automated comments about agent assignments MUST:
- Start with the agent @mention: "**@agent-name** has been assigned..."
- Use bold for emphasis: `**@agent-name**`
- Repeat the @mention in action lists
- Include reminder text about proper mentions

Example:
```markdown
🤖 **Agent Assignment Confirmed**

**@secure-specialist** has been assigned to this security issue.

**What @secure-specialist will do:**
1. **@secure-specialist** will analyze the vulnerability
2. **@secure-specialist** will implement a fix
3. **@secure-specialist** will add security tests

**IMPORTANT:** Always mention **@secure-specialist** by name in all related conversations.
```

### 4. In PR Comments

When commenting on PRs involving agents:
- Reference the agent by name: @agent-name
- Acknowledge agent's work: "Great work, @agent-name!"
- Request changes from agent: "@agent-name, please address..."
- Thank the agent: "Thank you, @agent-name"

### 5. In Commit Messages

If referencing agent work in commits:
```
feat: implement feature as specified by @create-guru

@create-guru designed this infrastructure component following
the agent's specialized approach for infrastructure creation.
```

### 6. Template Variables

When creating templates that will be auto-populated, use these patterns:

**For Shell Scripts:**
```bash
agent_mention="@${matched_agent}"
```

**For YAML Workflows:**
```yaml
body: |
  **@${{ steps.match.outputs.agent_name }}** has been assigned.
```

**For Python:**
```python
f"**@{agent_name}** will handle this task."
```

### 7. Forbidden Patterns

❌ **NEVER use these patterns:**
- "The agent will do this"
- "A custom agent has been assigned"
- "This was done by an agent"
- "Assigned to: engineer-master" (missing @)
- "Working with agent: bug-hunter" (missing @)

✅ **ALWAYS use these patterns:**
- "@engineer-master will do this"
- "@bug-hunter has been assigned"
- "This was done by @create-guru"
- "Assigned to: @engineer-master"
- "Working with @bug-hunter"

### 8. Multi-Agent Scenarios

When multiple agents are involved:
```markdown
This task involves collaboration between:
- **@engineer-master** - API design
- **@assert-specialist** - Test creation
- **@coach-master** - Code review

@engineer-master will lead with @assert-specialist providing coverage.
```

### 9. Compliance Checklist

Before submitting issues or PRs:
- [ ] Agent is mentioned with @ syntax
- [ ] Agent name is bolded: `**@agent-name**`
- [ ] Reminder about @mentions is included
- [ ] No generic "agent" references without @
- [ ] All action items reference @agent-name
- [ ] Comments include @agent-name
- [ ] Templates properly format @mentions

### 10. For Copilot Executing in GitHub Actions Runner

**MANDATORY WHEN RUNNING AS COPILOT CODING AGENT:**

When you (Copilot) execute in the GitHub Actions runner to work on an issue:

1. **Read Issue Body First**
   ```markdown
   The issue body starts with:
   > **🤖 Agent Assignment**
   > **@agent-name** - Please use the specialized approach...
   ```

2. **Extract Your Agent Identity**
   - Look for `<!-- COPILOT_AGENT:agent-name -->` HTML comment
   - Find the `**@agent-name**` mention in the directive section
   - This agent is YOUR identity for this task

3. **Apply Agent Identity to All Work**
   - **PR Title**: Include `(@agent-name)` suffix
     - Example: `feat: implement authentication (@secure-specialist)`
   - **PR Description**: Start with `**@agent-name** has implemented...`
   - **Commits**: Reference agent where relevant
     - Example: `fix: add validation per @secure-specialist`
   - **Comments**: Use `@agent-name` for attribution
     - Example: `@secure-specialist has completed security audit`

4. **Follow Agent Specialization**
   - Read `.github/agents/agent-name.md` 
   - Use the agent's approach, personality, and tools
   - Reference the agent's methodology in your PR description

5. **Complete Example of Proper Attribution**
   ```markdown
   Issue assigns: @engineer-master
   
   PR Title:
   feat: implement REST API endpoints (@engineer-master)
   
   PR Description:
   **@engineer-master** has implemented the REST API endpoints as specified.
   
   Following the engineer-master systematic approach:
   - Analyzed requirements thoroughly
   - Designed robust API architecture
   - Implemented with comprehensive error handling
   - Added full test coverage
   
   @engineer-master has ensured all endpoints follow RESTful conventions.
   
   Commit Messages:
   - feat: add user endpoints per @engineer-master design
   - test: add API tests following @engineer-master approach
   - docs: document API per @engineer-master specifications
   ```

6. **Why This is Critical**
   - Agent performance metrics depend on @mention attribution
   - The autonomous system tracks contributions by agent
   - Proper attribution enables agent evaluation and evolution
   - Missing @mentions break the performance tracking system

7. **Error: No Agent Mentioned**
   - If issue has no agent assignment: check for `agent:*` labels
   - If still unclear: work generically but note this in PR
   - Prefer to ask for clarification rather than assume

### 11. Audit Trail

Every mention creates an audit trail:
- Performance tracking relies on @mentions
- Attribution is based on @mentions
- Search and filtering use @mentions
- Analytics track @mention patterns

**Therefore:** Missing @mentions = Broken attribution system

## Enforcement

This instruction file is automatically applied to all issue and PR-related files. GitHub Copilot will:
- Suggest @agent-name mentions in relevant contexts
- Flag missing @mentions in code review
- Recommend adding @agent-name to templates
- Ensure consistency across all interactions

**Failure to follow these rules breaks the autonomous agent tracking system.**
