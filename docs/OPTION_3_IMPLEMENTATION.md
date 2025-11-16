# Option 3: Context-Aware Mission Prompts - Implementation Guide

## Overview

This document describes the implementation of **Option 3: Context-Aware Enhanced** mission prompts for the autonomous pipeline. This is the simplest option that adds ecosystem relevance scoring to mission prompts while maintaining a single mission system.

## What Changed

### 1. Added Ecosystem Relevance Calculation

**File:** `tools/create_mission_issues.py`

**New Function:** `calculate_ecosystem_relevance(patterns, summary)`

This function scores missions from 1-10 based on:
- **High relevance patterns** (7-10): AI/ML, agents, autonomous systems, CI/CD, LLMs, code generation, GitHub workflows
- **Medium relevance patterns** (4-6): Cloud, security, APIs, data analytics
- **Low relevance patterns** (1-3): General tech trends

**Scoring Logic:**
- Base score: 3 points (all missions start here)
- High relevance pattern: +2-3 points each
- Medium relevance pattern: +1 point each
- Ecosystem keywords in summary: +1-2 points each
- Maximum score: 10 points

**Output:**
- `score` (1-10): Numeric relevance score
- `relevance_level`: "🔴 High", "🟡 Medium", or "🟢 Low"
- `applicable_components`: List of Chained components (e.g., "Agent System", "Autonomous Pipeline")

### 2. Updated Mission Prompt Template

**Changes to issue body:**

#### A. Added Relevance Indicators
- **Mission Type:** "⚙️ Ecosystem Enhancement" (score ≥7) or "🧠 Learning Mission" (score <7)
- **Ecosystem Relevance:** Shown in header with emoji and score
- **Ecosystem Connection Section:** New section explaining relevance

#### B. Context-Aware Deliverables

**High Relevance (7-10):**
```markdown
- Research report (2-3 pages)
- **Ecosystem Integration Proposal** (Required)
  - Specific changes to components
  - Expected improvements
  - Implementation complexity
  - Risk assessment
- Code examples or proof-of-concept
```

**Medium Relevance (4-6):**
```markdown
- Research report (1-2 pages)
- **Ecosystem Applicability Assessment**
  - Rate relevance to Chained: __ / 10
  - Components that could benefit
  - Integration complexity
- Optional: Integration proposal if relevance ≥7
```

**Low Relevance (1-3):**
```markdown
- Research report (1-2 pages)
- Brief ecosystem assessment
  - Any unexpected applications
  - Relevance rating: __ / 10
```

#### C. Adjusted Next Steps

Next steps now vary based on relevance:
- **High:** Focus on integration planning and implementation roadmap
- **Medium:** Evaluate and propose if relevant
- **Low:** Document learnings, note any unexpected applications

## Example Outputs

### High Relevance Mission (Score: 10/10)

```markdown
## ⚙️ Ecosystem Enhancement: Self-Healing CI Pipelines with Autonomous Agents

**Mission ID:** idea:123
**Type:** ⚙️ Ecosystem Enhancement
**Ecosystem Relevance:** 🔴 High (10/10)

### 🔗 Ecosystem Connection (🔴 High: 10/10)

This mission has high relevance to core capabilities:

**Potentially applicable to:**
- Agent System, Autonomous Pipeline

**Integration priority:** High - Consider implementation

**Focus:** This mission has high relevance to Chained. Research thoroughly 
and propose concrete integration approaches.
```

### Medium Relevance Mission (Score: 6/10)

```markdown
## 🧠 Learning Mission: Cloud Security Best Practices

**Mission ID:** idea:456
**Type:** 🧠 Learning Mission
**Ecosystem Relevance:** 🟡 Medium (6/10)

### 🔗 Ecosystem Connection (🟡 Medium: 6/10)

This mission has medium relevance with potential applications:

**Potentially applicable to:**
- Evaluate during research

**Integration priority:** Medium - Monitor for insights

**Recommended approach:** If you identify strong ecosystem applications 
(7+/10), document specific integration proposals for potential follow-up work.
```

### Low Relevance Mission (Score: 4/10)

```markdown
## 🧠 Learning Mission: New Mobile UI Framework

**Mission ID:** idea:789
**Type:** 🧠 Learning Mission
**Ecosystem Relevance:** 🟡 Medium (4/10)

### 🔗 Ecosystem Connection (🟡 Medium: 4/10)

This mission is primarily for external learning and trend awareness.

**Focus:** Understand tech trends and document insights for future reference. 
If you discover unexpected applications to Chained's core capabilities, 
note them in your findings.
```

## Benefits

### ✅ Achieved Goals

1. **Clear Communication:** Agents immediately see if a mission is learning-focused or ecosystem-focused
2. **Context-Aware Expectations:** Deliverables match the mission's relevance
3. **Preserved Learning:** All missions still start as learning, but with context
4. **Minimal Complexity:** Single mission system, just enhanced with scoring
5. **No Regression Risk:** Existing workflow unchanged, only prompt improved

### ✅ Compared to Current State

| Aspect | Before (Generic) | After (Option 3) |
|--------|------------------|------------------|
| Mission Type | All "Mission" | Learning or Ecosystem |
| Relevance | Not indicated | Clear score (1-10) |
| Deliverables | Generic | Context-aware |
| Ecosystem Link | Missing | Explicit section |
| Agent Guidance | Vague | Clear expectations |

### ✅ Why Option 3?

User chose this option because:
- **Simplest to implement:** ~100 lines of code, 1-2 hours
- **Lowest risk:** No major workflow changes
- **Clear improvement:** Better prompts without complexity
- **Non-disruptive:** Existing missions continue to work

## Scoring Examples

### Patterns That Increase Score

**High Impact (+2-3 points):**
- `agents`, `autonomous`, `ai`, `ai_ml`, `ml`, `llm`, `code_generation` (+3)
- `ci_automation`, `devops`, `github`, `workflow`, `testing`, `self_healing`, `performance`, `monitoring` (+2)

**Medium Impact (+1 point):**
- `api`, `cloud`, `security`, `data`, `analytics`

### Summary Keywords That Increase Score

- `artificial intelligence`, `machine learning`, `llm`, `language model`, `copilot`, `code generation` (+2)
- `agent`, `autonomous`, `workflow`, `ci/cd`, `github actions`, `ai` (+1)
- `world model` (+2)
- `testing`, `learning`, `documentation`, `geographic` (+1)

### Real-World Examples

1. **"OpenAI launches self-healing CI pipelines with autonomous agents"**
   - Patterns: `ci_automation`, `agents`, `devops`, `self_healing`
   - Keywords: "autonomous", "ci", "agent"
   - **Score: 10/10** (High)

2. **"Anthropic releases Claude 3 with advanced reasoning capabilities"**
   - Patterns: `ai`, `llm`, `ml`
   - Keywords: "AI", "language model"
   - **Score: 10/10** (High)

3. **"Cloud security incident at Checkout.com"**
   - Patterns: `cloud`, `security`, `api`
   - Keywords: none
   - **Score: 6/10** (Medium)

4. **"New mobile UI framework for React"**
   - Patterns: `mobile`, `web`, `ui`
   - Keywords: none
   - **Score: 4/10** (Low-Medium)

## Configuration & Tuning

### Adjusting Thresholds

Current thresholds in `calculate_ecosystem_relevance()`:

```python
# Relevance levels
if score >= 7:
    relevance_level = 'High'
elif score >= 4:
    relevance_level = 'Medium'
else:
    relevance_level = 'Low'
```

**To adjust:**
- Lower high threshold (e.g., 6 instead of 7) → More ecosystem missions
- Raise high threshold (e.g., 8 instead of 7) → Fewer ecosystem missions
- Adjust medium threshold to change balance

### Adding New Patterns

To add new patterns to scoring:

```python
# In high_relevance_patterns
'new_pattern': 2,  # Add with point value

# In medium_relevance_patterns
'another_pattern': 1,  # Add with point value
```

### Adding New Components

To track new Chained components:

```python
ecosystem_keywords = {
    'new_component': ('New Component Name', 1),
    # keyword: (component_display_name, points)
}
```

## Testing

### Manual Testing

1. Create test `missions_data.json`:
   ```bash
   python3 << 'EOF'
   import json
   test_missions = [{
       "idea_id": "test:1",
       "idea_title": "Test Mission",
       "idea_summary": "Test with autonomous agents and CI/CD",
       "patterns": ["agents", "ci_automation"],
       "regions": ["US:Seattle"],
       "agent": {
           "agent_name": "Test Agent",
           "specialization": "engineer-master",
           "score": 0.9
       }
   }]
   with open('missions_data.json', 'w') as f:
       json.dump(test_missions, f, indent=2)
   EOF
   ```

2. Test scoring:
   ```bash
   python3 << 'EOF'
   import sys
   sys.path.insert(0, 'tools')
   from create_mission_issues import calculate_ecosystem_relevance
   
   score, level, components = calculate_ecosystem_relevance(
       ['agents', 'ci_automation'],
       'Test with autonomous agents and CI/CD'
   )
   print(f"Score: {score}/10, Level: {level}, Components: {components}")
   EOF
   ```

### Validation Checklist

Before deploying:
- [ ] Python syntax check passes: `python3 -m py_compile tools/create_mission_issues.py`
- [ ] Scoring function works with various inputs
- [ ] High relevance missions show ecosystem deliverables
- [ ] Medium relevance missions show assessment requirement
- [ ] Low relevance missions focus on learning
- [ ] Issue body renders correctly in GitHub

## Monitoring & Iteration

### Metrics to Track

After deployment, monitor:

1. **Score Distribution:**
   - How many missions score 7-10? (Target: ~20-30%)
   - How many score 4-6? (Target: ~40-50%)
   - How many score 1-3? (Target: ~20-30%)

2. **Agent Response:**
   - Do agents understand the relevance indicators?
   - Are ecosystem proposals being submitted for high-relevance missions?
   - Are low-relevance missions still valuable?

3. **Quality:**
   - Are high-scored missions actually relevant?
   - Are any low-scored missions surprisingly applicable?

### Iteration Strategy

**If too many high-relevance missions:**
- Increase threshold from 7 to 8
- Reduce pattern point values
- Tighten keyword matching

**If too few high-relevance missions:**
- Lower threshold from 7 to 6
- Increase pattern point values
- Add more ecosystem keywords

**If scoring seems off:**
- Review actual missions vs. scores
- Adjust pattern classifications
- Add/remove keywords
- Fine-tune point values

## Migration Path

### From Current Generic Prompts

1. **Deploy:** Update `tools/create_mission_issues.py`
2. **Observe:** Monitor first 10 missions created
3. **Validate:** Check if scores align with expectations
4. **Adjust:** Tune thresholds if needed
5. **Document:** Update knowledge base with learnings

### Future Enhancements

Option 3 can evolve into other options:

**→ Option 5 (Two-Phase):**
- Add Phase 2 generation for high scores
- Preserve existing scoring logic
- Natural progression path

**→ Option 4 (Quotas):**
- Add category tracking
- Enforce balance ratios
- Build on relevance classification

## Rollback Plan

If issues arise:

1. **Revert code:**
   ```bash
   git checkout afbe44e~1 -- tools/create_mission_issues.py
   ```

2. **Or comment out scoring:**
   ```python
   # Quick disable: Set all missions to medium
   relevance_score = 5
   relevance_level = "🟡 Medium"
   applicable_components = []
   ```

3. **Issues to watch for:**
   - Incorrect scoring (all high or all low)
   - Syntax errors in issue body
   - Label creation failures
   - Agent confusion about deliverables

## Summary

**Implementation Status:** ✅ Complete

**Changes Made:**
- Added `calculate_ecosystem_relevance()` function
- Updated issue body template with context-aware sections
- Added relevance indicators and adaptive deliverables

**Impact:**
- Better agent guidance (clear expectations)
- Ecosystem connection (explicit relevance)
- Balanced approach (learning + building)
- Minimal risk (no workflow changes)

**Next Steps:**
- Deploy to production
- Monitor first missions
- Iterate based on feedback
- Consider Option 5 if balance needs automation

---

*Implemented: 2025-11-16*  
*Option: 3 (Context-Aware Enhanced)*  
*Complexity: Low (1-2 hours)*  
*Risk: Minimal (no workflow changes)*
