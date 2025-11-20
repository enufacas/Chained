# Enhancement: Complexity-Based Agent Routing

## Overview

This is an optional enhancement that could add complexity-aware agent matching to the Chained autonomous system.

## Current Behavior

Currently, the agent matching system (`tools/match-issue-to-agent.py`) uses:
- **Content analysis**: Keywords and patterns in issue title/body
- **Score-based matching**: Agents score points based on keyword matches
- **No complexity consideration**: All issues treated equally regardless of complexity

## Proposed Enhancement

Add complexity labels that influence agent selection:
- `complexity:low` - Simple, straightforward tasks
- `complexity:medium` - Moderate complexity requiring some planning
- `complexity:high` - Complex tasks requiring significant coordination

## How It Would Work

### Step 1: Add Complexity Labels

Add to `tools/create_labels.py`:

```python
# Complexity labels
("complexity:low", "C5DEF5", "Simple task, quick implementation"),
("complexity:medium", "6DB8F2", "Moderate complexity, requires planning"),
("complexity:high", "2E86C1", "Complex task, significant coordination needed"),
```

Create labels:
```bash
python3 tools/create_labels.py
```

### Step 2: Update Agent Matching Logic

Modify `tools/match-issue-to-agent.py` to:

1. **Detect complexity from labels**:
   ```python
   def get_issue_complexity(issue_labels):
       if 'complexity:high' in issue_labels:
           return 'high'
       elif 'complexity:medium' in issue_labels:
           return 'medium'
       elif 'complexity:low' in issue_labels:
           return 'low'
       return 'unknown'
   ```

2. **Adjust scoring based on complexity**:
   ```python
   def match_agent_with_complexity(content, complexity):
       base_matches = match_agents(content)
       
       if complexity == 'high':
           # Prefer meta-coordinator and orchestrators
           boost_agents(['meta-coordinator', 'orchestrator-guru'], base_matches)
       elif complexity == 'low':
           # Prefer quick-implementation agents
           boost_agents(['create-champion', 'engineer-wizard'], base_matches)
       
       return base_matches
   ```

3. **Update workflow script**:
   Modify `.github/workflows/copilot-graphql-assign.yml` to pass labels to the matching script.

### Step 3: Usage Examples

**Manual Label Addition:**
```bash
gh issue edit 123 --add-label "complexity:high"
```

**In Issue Template:**
```markdown
---
name: Feature Request
about: Suggest a feature
labels: ['enhancement']
---

**Complexity**: <!-- Select: low / medium / high -->

**Description:**
...
```

**Automatic Detection (Advanced):**
Parse complexity indicators from issue text:
```python
def auto_detect_complexity(issue_body):
    indicators = {
        'high': ['complex', 'orchestration', 'multi-system', 'coordination'],
        'medium': ['refactor', 'redesign', 'significant'],
        'low': ['simple', 'quick', 'small', 'minor']
    }
    # Score and assign complexity
```

## Benefits

1. **Better Agent Selection**: Complex tasks routed to experienced coordination agents
2. **Efficiency**: Simple tasks get quick implementations without over-engineering
3. **Resource Optimization**: Right tool for the right job
4. **User Control**: Users can hint at complexity level
5. **Transparency**: Clear indication of task complexity

## Implementation Checklist

If you want to implement this:

- [ ] Add complexity labels via `create_labels.py`
- [ ] Update `match-issue-to-agent.py` to read labels
- [ ] Add complexity-aware scoring logic
- [ ] Update workflow to pass labels to script
- [ ] Test with sample issues of varying complexity
- [ ] Document in `HOW_TO_TRIGGER_AGENTS.md`
- [ ] Create issue templates with complexity selection

## Alternative: Content-Based Detection

Instead of labels, you could detect complexity automatically:

```python
def estimate_complexity(title, body):
    score = 0
    
    # High complexity indicators
    high_keywords = ['orchestration', 'multi-agent', 'coordination', 
                     'distributed', 'complex system']
    score += sum(2 for kw in high_keywords if kw in body.lower())
    
    # Medium complexity indicators
    med_keywords = ['refactor', 'redesign', 'significant change',
                    'multiple components']
    score += sum(1 for kw in med_keywords if kw in body.lower())
    
    # Low complexity indicators
    low_keywords = ['simple', 'quick fix', 'minor', 'small change']
    if any(kw in body.lower() for kw in low_keywords):
        score -= 2
    
    # Length-based heuristic
    if len(body) > 1000:
        score += 1
    
    if score >= 3:
        return 'high'
    elif score >= 1:
        return 'medium'
    else:
        return 'low'
```

## Example Workflow

### Before Enhancement:
```
Issue: "Build intelligent workflow orchestration"
→ Matches @create-guru (default, score: 3)
→ Generic implementation
```

### After Enhancement:
```
Issue: "Build intelligent workflow orchestration"
Label: complexity:high
→ Matches @meta-coordinator (score: 15, complexity boost)
→ Specialized multi-agent approach
```

## Related Files

- `tools/match-issue-to-agent.py` - Main matching logic
- `tools/create_labels.py` - Label definitions
- `.github/workflows/copilot-graphql-assign.yml` - Assignment workflow
- `docs/HOW_TO_TRIGGER_AGENTS.md` - User guide

## Questions?

Create an issue to discuss implementing this enhancement! The system will automatically assign it to the right agent. 😊

---

*This is an optional enhancement. The current system works great without complexity routing!*
