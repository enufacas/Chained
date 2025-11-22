---
applyTo:
  - "**/*.yml"
  - "**/*.yaml"
  - "**/assign-copilot-to-issue.sh"
  - "**/match-issue-to-agent.py"
  - ".github/workflows/**"
  - "tools/**"
---

# Agent Mention Requirements

## MANDATORY: Always Use @agent-name Mentions

**ALWAYS** use `@agent-name` syntax when referring to custom agents. **NEVER** use generic terms like "the agent" or "custom agent" without the specific @mention.

### Why This Matters
- **Attribution**: Agent performance tracking requires @mentions
- **Transparency**: Clear responsibility and accountability
- **Metrics**: Performance scoring depends on proper identification

### Usage Rules

✅ **CORRECT:**
```markdown
@engineer-master will implement this API endpoint.
This PR was created by @troubleshoot-expert to fix the workflow issue.
```

❌ **INCORRECT:**
```markdown
The engineer agent will handle this.
A custom agent has been assigned.
```

### When Executing as Copilot in GitHub Actions

**CRITICAL**: Read the issue body FIRST to identify your assigned agent:
- Look for `**@agent-name** - Please use...` directive
- Extract agent name and use it throughout your work
- Include in PR titles, descriptions, commits, and comments
- Follow agent's specialization from `.github/agents/agent-name.md`

**Example:**
```
Issue: "**@secure-specialist** - Fix security vulnerability"

✅ PR title: "Fix auth vulnerability (@secure-specialist)"
✅ PR body: "**@secure-specialist** has fixed the security issue..."
✅ Commit: "fix: add input validation per @secure-specialist"
```

### Implementation Checklist
- [ ] All agent references use @agent-name syntax
- [ ] Comments and messages include @agent-name
- [ ] No generic "agent" references without @mention

For complete agent list, see `.github/agents/README.md`
