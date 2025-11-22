---
applyTo:
  - ".github/agents/*.md"
  - "tools/match-issue-to-agent.py"
---

# Agent Definition Synchronization

## MANDATORY: Keep Agent Definitions and Patterns in Sync

When creating/modifying agent definitions in `.github/agents/`, **MUST also update matching patterns in `tools/match-issue-to-agent.py`**.

### Why This Matters
Without patterns, agents will never be assigned to issues - they become invisible to the assignment system.

### Required Actions

**When adding a new agent:**
1. Create `.github/agents/{agent-name}.md`
2. Add patterns to `tools/match-issue-to-agent.py`

### Pattern Template
```python
AGENT_PATTERNS = {
    'your-agent-name': {
        'keywords': [
            # 10+ relevant keywords (1 point each)
            'technology', 'domain-term', 'action-verb', 'file-type'
        ],
        'patterns': [
            # 5+ regex patterns (2 points each)
            r'\btechnology\b', r'\bdomain-term\b', r'\baction\b'
        ]
    }
}
```

### Pattern Guidelines
- **Keywords**: Lowercase, exact matches (e.g., `'three.js'`, `'security'`, `'optimize'`)
- **Patterns**: Use `\b` for word boundaries (e.g., `r'\bapi\b'`)
- **Score target**: Design to achieve score ≥ 5 for typical domain issues

### Testing Required
```bash
# Test that agent matches expected issues
python3 tools/match-issue-to-agent.py "Test title" "Test body"
```

### Verification
- [ ] Agent definition created
- [ ] Patterns added (10+ keywords, 5+ regex)
- [ ] Tested with realistic issues
- [ ] Agent scores ≥ 5 for domain-specific issues

**Missing patterns = Agent never works!**
