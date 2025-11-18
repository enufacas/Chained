---
applyTo:
  - ".github/agents/*.md"
  - "tools/match-issue-to-agent.py"
---

# Agent Definition Synchronization Instructions

## MANDATORY RULE: Keep Agent Definitions and Matching Patterns in Sync

When creating or modifying custom agent definitions in `.github/agents/`, you MUST also update the matching patterns in `tools/match-issue-to-agent.py` to ensure the agent can be discovered and assigned to relevant issues.

### Why This Matters

The agent assignment system has two critical components that must stay synchronized:

1. **Agent Definition** (`.github/agents/{agent-name}.md`): Defines the agent's capabilities, personality, and tools
2. **Matching Patterns** (`tools/match-issue-to-agent.py`): Contains keywords and regex patterns that route issues to this agent

**If patterns are missing**: The agent will never be assigned, even for issues perfectly suited to its specialization. It becomes effectively invisible to the assignment system.

## Required Actions

### When Adding a New Agent

**ALWAYS update both files:**

1. **Create Agent Definition**: `.github/agents/{agent-name}.md`
2. **Add Matching Patterns**: `tools/match-issue-to-agent.py`

### Pattern Definition Template

When adding an agent to `match-issue-to-agent.py`, add an entry to the `AGENT_PATTERNS` dictionary:

```python
AGENT_PATTERNS = {
    # ... existing agents ...
    
    'your-agent-name': {
        'keywords': [
            # List relevant keywords (1 point each when matched)
            'keyword1', 'keyword2', 'related term', 'domain concept',
            'technology', 'tool name', 'file name', 'action verb'
        ],
        'patterns': [
            # List regex patterns (2 points each when matched)
            r'\bkeyword1\b', r'\bkeyword2\b', r'\btechnology\b',
            r'\brelated\s*term\b', r'\bdomain', r'\baction\b'
        ]
    },
    
    # ... more agents ...
}
```

### Pattern Design Guidelines

**Keywords** (simple string matching):
- Lowercase, exact matches within normalized text
- Technology names: `'three.js'`, `'webgl'`, `'react'`, `'python'`
- Domain terms: `'security'`, `'performance'`, `'refactor'`, `'test'`
- Action verbs: `'optimize'`, `'debug'`, `'document'`, `'analyze'`
- File names: `'organism.html'`, `'dockerfile'`, `'package.json'`
- Common variations: `'threejs'` and `'three.js'`, `'3d'` and `'three-dimensional'`

**Patterns** (regex matching, case-insensitive):
- Use `\b` word boundaries for whole word matching: `r'\bapi\b'`
- Use `?` for optional characters: `r'\boptimi[sz]e?\b'` matches optimize/optimise
- Use `\s*` for optional spaces: `r'\b3d\s*rendering\b'`
- Use `|` for alternatives: `r'\b(three\.?js|webgl)\b'`
- Escape special characters: `r'\bthree\.js\b'` (dot is special in regex)

### Example: render-3d-master Agent

**Good Pattern Definition** (comprehensive coverage):

```python
'render-3d-master': {
    'keywords': [
        '3d', 'three.js', 'threejs', 'webgl', 'rendering', 'render',
        'visualization', 'organism.html', 'lifecycle-3d', 'canvas',
        'graphics', 'shader', 'mesh', 'geometry', 'material',
        'camera', 'scene', 'fps', 'particle', 'animation',
        'gpu', 'vertex', 'fragment', 'texture', 'lighting',
        'bloom', 'post-processing', 'orbitcontrols', 'effect',
        'instanced', 'draw call', 'webgl2', 'glsl'
    ],
    'patterns': [
        r'\b3d\b', r'\bthree\.?js\b', r'\bwebgl\b', r'\brendering\b',
        r'\brender', r'\bvisuali[sz]ation\b', r'\borganism\.html\b',
        r'\bcanvas\b', r'\bgraphics\b', r'\bshader\b', r'\bmesh\b',
        r'\bgeometry\b', r'\bcamera\b', r'\bscene\b', r'\bfps\b',
        r'\bparticle', r'\banimation\b', r'\bgpu\b', r'\btexture\b',
        r'\blighting\b', r'\bbloom\b', r'\bpost-process', r'\bglsl\b'
    ]
}
```

**Why this works**:
- Covers technology keywords: `three.js`, `webgl`, `glsl`
- Covers domain terms: `3d`, `rendering`, `visualization`, `graphics`
- Covers specific files: `organism.html`, `lifecycle-3d`
- Covers technical terms: `shader`, `mesh`, `geometry`, `particle`, `gpu`
- Covers performance metrics: `fps`, `draw call`
- Uses word boundaries and optional dots: `r'\bthree\.?js\b'`

### Testing Your Patterns

**ALWAYS test patterns after adding them:**

```bash
# Test that your agent is correctly matched
python3 tools/match-issue-to-agent.py "Issue title with keywords" "Issue body description"

# Should return your agent with a high score
# Example output:
# {
#   "agent": "render-3d-master",
#   "score": 18,
#   "confidence": "high",
#   ...
# }
```

**Test multiple scenarios:**
- Primary keywords (should match with high confidence)
- Related terms (should still match)
- Unrelated issues (should NOT match)

### Pattern Score Calculation

The matching system calculates scores as:
- **Keywords**: 1 point per match
- **Regex patterns**: 2 points per match
- **High confidence**: score ≥ 5
- **Medium confidence**: score ≥ 3
- **Low confidence**: score < 3

Design patterns to achieve **score ≥ 5** for typical issues in your domain.

## Common Mistakes to Avoid

❌ **Creating agent definition without patterns**
```
Created: .github/agents/render-3d-master.md
Forgot: tools/match-issue-to-agent.py update
Result: Agent never gets assigned ⚠️
```

✅ **Correct approach**
```
Created: .github/agents/render-3d-master.md
Updated: tools/match-issue-to-agent.py with patterns
Tested: python3 tools/match-issue-to-agent.py "test issue"
Result: Agent correctly assigned ✅
```

❌ **Using patterns that are too specific**
```python
'keywords': ['exact-file-name-that-rarely-appears.html']
# Agent only matches when this exact file is mentioned
```

✅ **Use patterns with appropriate breadth**
```python
'keywords': ['3d', 'rendering', 'webgl', 'visualization', 'graphics']
# Agent matches various 3D-related issues
```

❌ **Forgetting word boundaries in regex**
```python
r'api'  # Matches "happy", "capital", "erapidly"
```

✅ **Use word boundaries**
```python
r'\bapi\b'  # Only matches "api" as a whole word
```

❌ **Not testing the patterns**
```python
# Added patterns but never tested
# Agent might not match as expected
```

✅ **Always test with realistic issues**
```bash
python3 tools/match-issue-to-agent.py \
  "Fix 3D rendering in organism.html" \
  "The Three.js scene needs optimization"
# Verify your agent is selected with high confidence
```

## Pattern Overlap and Priority

**Multiple agents may match the same issue** - this is expected and healthy!

Example: Issue about "3D performance optimization"
- `render-3d-master`: score 18 (3d, rendering, performance keywords)
- `accelerate-specialist`: score 5 (performance, optimize keywords)
- **Winner**: `render-3d-master` (higher score = more specific match)

The system uses **liberal threshold** (80% of max score) to find top candidates, then randomly selects from them to promote variety. This means:
- Agents with similar scores may both be selected (promotes diversity)
- The agent with the highest score is most likely to be chosen
- Tied agents are all considered viable options

**Design patterns to be MORE specific than general agents** to ensure your specialized agent wins when appropriate.

## Verification Checklist

Before completing work on agent definitions:

- [ ] Agent definition file created: `.github/agents/{agent-name}.md`
- [ ] Patterns added to: `tools/match-issue-to-agent.py`
- [ ] Patterns include 10+ keywords relevant to the agent's domain
- [ ] Patterns include 5+ regex patterns with word boundaries
- [ ] Tested with `python3 tools/match-issue-to-agent.py`
- [ ] Agent scores ≥ 5 for typical issues in its domain
- [ ] Agent scores higher than general agents for specialized issues
- [ ] Verified no conflicts with similar agents

## Finding Missing Patterns

**Audit command** to find agents without patterns:

```bash
# List agents missing from AGENT_PATTERNS
python3 << 'EOF'
import os, re

agent_files = set()
for f in os.listdir('.github/agents'):
    if f.endswith('.md') and f != 'README.md' and not f.startswith('.'):
        agent_files.add(f.replace('.md', ''))

with open('tools/match-issue-to-agent.py', 'r') as f:
    content = f.read()
    
pattern_matches = re.findall(r"'([a-z0-9-]+)':\s*{", content)
patterns = set(pattern_matches)

missing = sorted(agent_files - patterns)
if missing:
    print("⚠️  Agents without patterns:")
    for m in missing:
        print(f"  - {m}")
else:
    print("✅ All agents have patterns defined!")
EOF
```

Run this check before committing changes to agent definitions!

## Integration with Agent System

The patterns you define here directly affect:
- **Issue Assignment**: Which agent gets assigned to new issues
- **Agent Utilization**: How often agents are selected for work
- **Performance Tracking**: Agents without patterns never get opportunities
- **Hall of Fame**: Agents need assignments to accumulate stats

**Missing patterns = Invisible agents** that can never prove their value or accumulate performance stats.

## Summary

**ALWAYS synchronize these files:**

1. `.github/agents/{agent-name}.md` ← Agent definition
2. `tools/match-issue-to-agent.py` ← Matching patterns

**Pattern Requirements:**
- 10+ relevant keywords
- 5+ regex patterns with word boundaries
- Test to achieve score ≥ 5 for domain-specific issues
- Verify agent is selected over general agents

**Testing is Mandatory:**
```bash
python3 tools/match-issue-to-agent.py "test title" "test body"
```

**Remember**: An agent without patterns is an agent that never works. The matching patterns are just as important as the agent definition itself!

---

*🤖 This instruction ensures the agent assignment system remains functional and all agents get fair opportunities to work on relevant issues.*
