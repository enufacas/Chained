---
applyTo:
  - "**/*.yml"
  - "**/*.yaml"
  - "**/assign-copilot-to-issue.sh"
  - "**/match-issue-to-agent.py"
  - ".github/workflows/**"
  - "tools/**"
---

# Custom Agent Mention Requirements

## MANDATORY RULE: Always Use @agent-name Mentions

When working with files related to GitHub workflows, issue assignment, or agent management, you MUST follow these rules:

### 1. Agent Mention Syntax
- **ALWAYS** use `@agent-name` syntax when referring to any custom agent
- **NEVER** use generic terms like "the agent" or "custom agent" without the specific @mention
- This applies to ALL contexts: comments, issue bodies, PR descriptions, commit messages, and code

### 2. Examples of CORRECT Usage
✅ **Issue Comments:**
```markdown
@engineer-master will implement this API endpoint.
```

✅ **PR Descriptions:**
```markdown
This PR was created by @troubleshoot-expert to fix the workflow issue.
```

✅ **Commit Messages:**
```
Update workflow to notify @create-guru about new infrastructure needs
```

✅ **Code Comments:**
```bash
# Assign to @bug-hunter for debugging work
```

### 3. Examples of INCORRECT Usage
❌ **DON'T say:**
- "The engineer agent will handle this"
- "A custom agent has been assigned"
- "This issue is for the bug-hunter agent"
- "The specialized agent will work on this"

❌ **ALWAYS use @mention instead:**
- "@engineer-master will handle this"
- "@bug-hunter has been assigned"
- "This issue is for @bug-hunter"
- "@accelerate-master will work on this"

### 4. Why This Matters
- **Attribution**: Clear tracking of which agent did what work
- **Performance Metrics**: Agent performance is tracked based on mentions
- **Transparency**: Users can see exactly which agent is responsible
- **Collaboration**: Agents can be referenced in discussions and reviews
- **Accountability**: Work is properly attributed to the correct agent

### 5. Available Custom Agents
When mentioning agents, use these exact names with @ prefix:

- @accelerate-master - Performance optimization
- @assert-specialist - Testing & quality assurance
- @coach-master - Code reviews & best practices
- @create-guru - Infrastructure & feature creation
- @engineer-master - API engineering (systematic)
- @engineer-wizard - API engineering (creative)
- @investigate-champion - Code analysis & metrics
- @meta-coordinator - Multi-agent coordination
- @monitor-champion - Security monitoring
- @organize-guru - Code structure & duplication
- @secure-specialist - Security implementation
- @support-master - Documentation & skill building
- @troubleshoot-expert - CI/CD & GitHub Actions (protected)

### 6. Enforcement in Code
When writing scripts or workflows that handle agent assignment:
- Include @agent-name in all generated comments
- Add @agent-name to issue body directives
- Use @agent-name in success/failure messages
- Reference @agent-name in assignment summaries
- Include "IMPORTANT" reminders about using @mentions

### 7. Verification Checklist
Before committing changes to agent-related files, verify:
- [ ] All agent references use @agent-name syntax
- [ ] No generic "agent" references without @mention
- [ ] Comments and messages include @agent-name
- [ ] Documentation shows @agent-name examples
- [ ] Error messages reference @agent-name when applicable

## Non-Compliance Consequences
Failure to use @agent-name mentions results in:
- ❌ Improper attribution of work
- ❌ Broken performance tracking
- ❌ Confusion about agent responsibilities
- ❌ Reduced transparency in the autonomous system

## Summary
**ALWAYS mention custom agents by name using @agent-name syntax in EVERY context where agents are discussed, assigned, or referenced.**
