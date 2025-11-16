# Mission Prompt: Before vs After (Option 3)

This document shows concrete examples of how mission prompts have improved with Option 3 implementation.

## Example Mission: Self-Healing CI Pipelines

**Patterns:** `ci_automation`, `agents`, `devops`, `self_healing`  
**Summary:** OpenAI launches GPT-5 with self-healing CI pipelines that use autonomous agents to auto-fix failures.

---

## BEFORE (Generic Prompt)

```markdown
## 🎯 Agent Mission: Self-Healing CI Pipelines with Autonomous Agents

**Mission ID:** idea:123
**Created:** 2025-11-16 16:00:00 UTC

### 📋 Mission Summary

OpenAI launches GPT-5 with self-healing CI pipelines that use autonomous 
agents to auto-fix failures. GitHub adopts the technology for workflow automation.

### 🌍 Mission Locations

US:San Francisco, US:Redmond

### 🏷️ Patterns & Technologies

ci_automation, agents, devops, self_healing

### 🤖 Assigned Agent

**DevOps Specialist** (@engineer-master) - Match Score: 0.92

This mission was matched to **@engineer-master** based on:
- Location relevance (30%)
- Role/skill match (40%)  
- Performance history (30%)

### 📊 Expected Outputs

- [ ] Documentation related to ci_automation, agents, devops, self_healing
- [ ] Code examples or tools
- [ ] World model updates
- [ ] Learning artifacts

### 🔄 Next Steps

1. **@engineer-master** investigates the mission locations
2. Gathers insights and creates artifacts
3. Reports findings back to world model
4. Agent metrics are updated based on contributions

---

*This mission was automatically created by the Agent Missions workflow and 
assigned to **@engineer-master** based on intelligent matching.*
```

### ❌ Problems with Generic Prompt

1. **No ecosystem context:** Agent doesn't know this is highly relevant to Chained
2. **Vague deliverables:** "Documentation" and "learning artifacts" are too generic
3. **No integration guidance:** No mention of applying to core systems
4. **Missing priority:** Can't distinguish from external tech trends
5. **Unclear success:** What does "success" look like?

---

## AFTER (Option 3: Context-Aware)

```markdown
## ⚙️ Ecosystem Enhancement: Self-Healing CI Pipelines with Autonomous Agents

**Mission ID:** idea:123
**Type:** ⚙️ Ecosystem Enhancement
**Ecosystem Relevance:** 🔴 High (10/10)
**Created:** 2025-11-16 16:00:00 UTC

### 📋 Mission Summary

OpenAI launches GPT-5 with self-healing CI pipelines that use autonomous 
agents to auto-fix failures. GitHub adopts the technology for workflow automation.

### 🔗 Ecosystem Connection (🔴 High: 10/10)

This mission has high relevance to core capabilities:

**Potentially applicable to:**
- Agent System, Autonomous Pipeline

**Integration priority:** High - Consider implementation

**Focus:** This mission has high relevance to Chained. Research thoroughly 
and propose concrete integration approaches.

### 🌍 Mission Locations

US:San Francisco, US:Redmond

### 🏷️ Patterns & Technologies

ci_automation, agents, devops, self_healing

### 🤖 Assigned Agent

**DevOps Specialist** (@engineer-master) - Match Score: 0.92

This mission was matched to **@engineer-master** based on:
- Location relevance (30%)
- Role/skill match (40%)  
- Performance history (30%)

### 📊 Expected Outputs

**Learning Deliverables (Required):**
- [ ] **Research Report** (2-3 pages)
  - Summary of key findings related to ci_automation, agents, devops, self_healing
  - Best practices and lessons learned (3-5 points)
  - Industry trends and patterns
  
- [ ] **Ecosystem Integration Proposal** (Required for high relevance)
  - Specific changes to Chained's components
  - Expected improvements and benefits
  - Implementation complexity estimate (low/medium/high)
  - Risk assessment and mitigation strategies

**Additional Deliverables:**
- [ ] Code examples or proof-of-concept (if applicable)
- [ ] World model updates with geographic/tech data
- [ ] Integration design document or architecture proposal

### 🔄 Next Steps

1. **@engineer-master** researches ci_automation, agents, devops, self_healing thoroughly
2. Analyzes applicability to Chained's core systems
3. **Develops integration proposal** with specific recommendations
4. Documents implementation approach and complexity
5. Creates artifacts (code samples, design docs, etc.)
6. Submits comprehensive findings with clear action items

**Success Criteria:**
- [ ] Clear understanding of technology/patterns
- [ ] Detailed integration proposal for Chained
- [ ] Implementation roadmap with effort estimates
- [ ] Risk assessment completed

---

*This mission was automatically created by the Agent Missions workflow. 
Ecosystem relevance: **🔴 High (10/10)** - Focus on integration opportunities.*
```

### ✅ Improvements with Context-Aware Prompt

1. **Clear type:** "⚙️ Ecosystem Enhancement" vs generic "🎯 Agent Mission"
2. **Visible relevance:** "🔴 High (10/10)" shown prominently
3. **Explicit connection:** New section explaining ecosystem link
4. **Specific deliverables:** Integration proposal required, not optional
5. **Clear success criteria:** Actionable checklist for completion
6. **Appropriate focus:** "Focus on integration" vs generic "investigate"

---

## Comparison Table

| Aspect | Before (Generic) | After (Option 3) | Improvement |
|--------|------------------|-------------------|-------------|
| **Mission Type** | Generic "Mission" | "Ecosystem Enhancement" or "Learning Mission" | ✅ Clear categorization |
| **Relevance Shown** | Not mentioned | "🔴 High (10/10)" in header | ✅ Immediate visibility |
| **Ecosystem Link** | Missing | Dedicated section with components | ✅ Explicit connection |
| **Deliverables** | Generic (4 items) | Context-aware (6-8 items) | ✅ Specific expectations |
| **Integration Focus** | Not mentioned | Required for high relevance | ✅ Clear guidance |
| **Success Criteria** | Implied | Explicit checklist | ✅ Measurable goals |
| **Next Steps** | Generic "investigate" | Context-aware actions | ✅ Clear path forward |
| **Agent Guidance** | Minimal | Comprehensive | ✅ Better direction |

---

## Medium Relevance Example (Score: 6/10)

For missions with medium relevance, the prompt adjusts:

**Key Differences from High:**
- **Type:** "🧠 Learning Mission" (not Ecosystem Enhancement)
- **Deliverables:** Assessment required, integration optional
- **Guidance:** "Evaluate if relevant, propose if score ≥7"
- **Success:** Understanding + honest evaluation

**Example Deliverable Section:**

```markdown
### 📊 Expected Outputs

**Learning Deliverables (Required):**
- [ ] **Research Report** (1-2 pages)
  - Summary of findings related to cloud, security, api
  - Key takeaways (3-5 bullet points)
  
- [ ] **Ecosystem Applicability Assessment**
  - Rate relevance to Chained: __ / 10
  - Specific components that could benefit
  - Integration complexity estimate (low/medium/high)

**Ecosystem Integration (If relevance ≥ 7):**
- [ ] Integration proposal document
  - Specific changes to Chained's workflows/systems
  - Expected benefits and improvements
  - Implementation effort estimate

**Additional:**
- [ ] Code examples or tools (if applicable)
- [ ] World model updates
```

**Note:** Integration proposal is conditional, not required upfront.

---

## Low Relevance Example (Score: 3/10)

For missions with low relevance (primarily external learning):

**Key Differences:**
- **Type:** "🧠 Learning Mission"
- **Relevance:** "🟢 Low" with explanation
- **Deliverables:** Basic research + brief assessment
- **Focus:** "External learning and trend awareness"

**Example Ecosystem Section:**

```markdown
### 🔗 Ecosystem Connection (🟢 Low: 3/10)

This mission is primarily for external learning and trend awareness.

**Focus:** Understand tech trends and document insights for future reference. 
If you discover unexpected applications to Chained's core capabilities, 
note them in your findings.
```

**Note:** No integration pressure, but door left open for discoveries.

---

## Impact Summary

### For Agents

**Before:**
- "Another investigation mission... what should I focus on?"
- "Should I try to apply this to Chained?"
- "What does success look like?"

**After:**
- "High relevance! This needs integration proposal"
- "Clear deliverables: research + integration design"
- "Success = understanding + concrete proposal"

### For Repository Owners

**Before:**
- All missions looked the same
- No way to prioritize
- Unclear if learning → building

**After:**
- Clear categorization (⚙️ vs 🧠)
- Visible relevance scores
- Explicit integration expectations

### For the Autonomous System

**Before:**
- 100% external learning
- 0% ecosystem building
- No connection between phases

**After:**
- Balanced approach (learning + evaluation)
- Clear path to ecosystem work
- Context-aware expectations

---

## Rollout Plan

### Phase 1: Deploy (Immediate)
- Update `tools/create_mission_issues.py`
- Deploy to production workflow
- Monitor first 10 missions

### Phase 2: Observe (Week 1)
- Track score distribution
- Review agent responses
- Validate scoring accuracy

### Phase 3: Iterate (Week 2)
- Adjust thresholds if needed
- Tune pattern values
- Refine deliverables

### Phase 4: Document (Week 3)
- Capture learnings
- Update guidelines
- Share feedback

---

## Success Metrics

After 2 weeks, expect:

**Score Distribution:**
- 20-30% High relevance (7-10)
- 40-50% Medium relevance (4-6)
- 20-30% Low relevance (1-3)

**Agent Behavior:**
- High missions → Integration proposals submitted
- Medium missions → Honest evaluations provided
- Low missions → Learning documented

**Quality Indicators:**
- Agents understand expectations
- Deliverables match relevance level
- Ecosystem connections identified

---

*Option 3 Implementation: Simplest, lowest risk, clear improvement* ✅
