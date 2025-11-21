---
applyTo:
  - "**/*issue*.md"
  - "**/*pull_request*.md"
  - ".github/ISSUE_TEMPLATE/**"
  - ".github/PULL_REQUEST_TEMPLATE/**"
---

# Issue and PR Template Agent Mention Rules

## Mandatory Agent Reference Format

### In Issue Descriptions
```markdown
## 🤖 Assigned Agent

**@agent-name** (Specialization: [agent specialty])

**REMINDER:** Always mention **@agent-name** by name in all related discussions and PRs.
```

### In PR Descriptions
```markdown
## 👤 Agent

Created by: **@agent-name**

**@agent-name** has implemented the following changes:
- [specific changes]
```

### In Comments
- Start with agent @mention: "**@agent-name** has been assigned..."
- Use bold for emphasis: `**@agent-name**`
- Repeat @mention in action lists

### Forbidden Patterns
❌ "The agent will do this"
❌ "A custom agent has been assigned"
❌ "Assigned to: engineer-master" (missing @)

✅ "@engineer-master will do this"
✅ "@bug-hunter has been assigned"
✅ "Assigned to: @engineer-master"

### For Copilot in GitHub Actions Runner
When executing as Copilot:
1. **Read issue body** for agent assignment: `**@agent-name** - Please use...`
2. **Use that agent name** in PR title, description, commits, comments
3. **Follow agent's specialization** from `.github/agents/agent-name.md`

### Why This Matters
- Agent performance metrics depend on @mention attribution
- Autonomous system tracks contributions by agent
- Proper attribution enables agent evaluation

**Missing @mentions = Broken attribution system**
