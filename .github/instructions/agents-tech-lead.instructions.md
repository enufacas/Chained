---
applyTo:
  - ".github/agents/**"
  - ".github/agent-system/**"
  - "tools/match-issue-to-agent.py"
  - "tools/assign-copilot-to-issue.sh"
---

# Agents Tech Lead Instructions

## Overview

**@agents-tech-lead** is responsible for the agent system integrity, including agent definitions, agent registry, agent matching logic, and the overall health of the agent ecosystem.

## When to Consult Agents Tech Lead

You should consult **@agents-tech-lead** when:
- Creating or modifying agent definitions
- Updating agent matching patterns
- Changing agent registry or metrics
- Modifying agent assignment logic
- Implementing new agent capabilities
- Resolving agent system issues

## Key Responsibilities

**@agents-tech-lead** ensures:

1. **Agent Quality**: All agent definitions are well-designed and purposeful
2. **System Integrity**: Agent assignment and matching work correctly
3. **Pattern Accuracy**: Agent patterns match appropriate issues
4. **Ecosystem Health**: Agent system remains balanced and effective
5. **Documentation**: Agent system is well-documented and understandable

## Review Focus Areas

When working with the agent system, **@agents-tech-lead** reviews:

### Agent Definition Quality
- Clear specialization and purpose
- Appropriate tools and capabilities
- Well-defined personality and communication style
- Frontmatter is valid YAML
- Description is accurate and helpful

### Pattern Matching
- Keywords cover relevant terms for the specialization
- Regex patterns are specific but not too narrow
- Patterns don't overly conflict with other agents
- Score thresholds are appropriate
- Testing confirms expected matching behavior

### System Integration
- Agent registered in registry.json
- Protected status correctly configured if needed
- Agent appears in agent list commands
- Assignment workflows can find the agent
- Performance tracking works correctly

### Documentation
- Agent README updated with new agents
- Instructions explain when to use the agent
- Examples show typical use cases
- Tech lead responsibilities are clear

## Common Anti-Patterns to Avoid

❌ **Don't:**
- Create agents with overlapping specializations
- Skip pattern matching configuration
- Forget to update protected agents list
- Leave agent definitions without descriptions
- Create agents without testing assignment

✅ **Do:**
- Define clear, distinct specializations
- Configure comprehensive pattern matching
- Update all related configuration files
- Provide detailed, helpful descriptions
- Test agent matching with realistic issues

## Agent Definition Best Practices

### Frontmatter Structure
```yaml
---
name: agent-name
description: "Clear, concise description of specialization"
specialization: domain
personality: trait
tools:
  - tool1
  - tool2
tech_lead_for_paths:  # For tech lead agents
  - path/pattern/**
responsibilities:
  - Clear responsibility 1
  - Clear responsibility 2
---
```

### Pattern Configuration
```python
'agent-name': {
    'keywords': [
        # 10+ relevant keywords
        'domain', 'technology', 'concept', 'tool',
        'action', 'file-type', 'related-term'
    ],
    'patterns': [
        # 5+ regex patterns
        r'\bdomain\b', r'\btechnology\b',
        r'\bconcept', r'\btool\b',
        r'\baction\b'
    ]
}
```

### Testing Patterns
```bash
# Test that agent matches expected issues
python3 tools/match-issue-to-agent.py \
  "Test title with keywords" \
  "Body text with domain concepts"

# Should return your agent with high confidence
```

## Protected Tech Lead Agents

Tech lead agents are protected from standard evaluation:

### Current Tech Lead Agents
- **workflows-tech-lead**: GitHub Actions and workflows
- **agents-tech-lead**: Agent system and definitions
- **docs-tech-lead**: Documentation and markdown files
- **github-pages-tech-lead**: GitHub Pages web content

### Protected Agent Criteria
Tech lead agents must:
1. Have clear domain ownership
2. Be essential to system operation
3. Provide specialized knowledge
4. Have distinct, non-overlapping responsibilities
5. Maintain high quality standards

## Agent System Architecture

### Key Files
- `.github/agents/*.md` - Agent definitions
- `.github/agent-system/config.json` - System configuration
- `.github/agent-system/registry.json` - Agent registry
- `tools/match-issue-to-agent.py` - Pattern matching
- `tools/assign-copilot-to-issue.sh` - Assignment logic

### Configuration Parameters
```json
{
  "protected_specializations": [
    "troubleshoot-expert",
    "workflows-tech-lead",
    "agents-tech-lead",
    "docs-tech-lead",
    "github-pages-tech-lead"
  ],
  "elimination_threshold": 0.3,
  "promotion_threshold": 0.65,
  "new_agent_grace_period_hours": 48
}
```

## Creating a New Agent

### Checklist
1. ✅ Define clear specialization and purpose
2. ✅ Create `.github/agents/agent-name.md` with frontmatter
3. ✅ Add patterns to `tools/match-issue-to-agent.py`
4. ✅ Test pattern matching
5. ✅ Update agent README
6. ✅ Add to protected list if tech lead
7. ✅ Create path-specific instructions if needed

### Validation
```bash
# Verify agent file parses correctly
python3 -c "import tools.match_issue_to_agent as m; print(m.parse_agent_file('.github/agents/agent-name.md'))"

# Test pattern matching
python3 tools/match-issue-to-agent.py "test title" "test body"

# List all agents to confirm registration
python3 -c "import tools.match_issue_to_agent as m; print(list(m.list_agents()))"
```

## Modifying Protected Agents

For changes to protected agents (like tech leads):
1. **Extra scrutiny**: Changes affect critical system components
2. **Backward compatibility**: Don't break existing functionality
3. **Documentation updates**: Keep docs in sync with changes
4. **Testing**: Verify changes don't disrupt assignment
5. **Review**: Get explicit approval for significant changes

## Getting Help

If you're unsure about:
- Agent specialization design
- Pattern matching optimization
- System configuration changes
- Agent ecosystem balance

Mention **@agents-tech-lead** in your PR or issue for guidance.

## Protected Status

**@agents-tech-lead** is a protected agent that cannot be eliminated through standard performance evaluation. This ensures consistent oversight of the agent ecosystem and maintains system integrity.

---

*These instructions apply to all agent system files to ensure **@agents-tech-lead** maintains high standards for our autonomous AI ecosystem.*
