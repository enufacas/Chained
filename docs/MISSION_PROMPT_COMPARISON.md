# 🎯 Mission Prompt Visual Comparison

Quick visual guide to understand the 5 options for improving mission prompts.

## Current State (Problem)

```
TLDR/HN → Ideas → ALL treated as "learning" → Generic prompt
                                             ↓
                                    "Investigate trends"
                                    "Gather insights"
                                    "Document findings"
```

**Result:** No ecosystem improvements, just endless exploration

---

## Option 1: Dual-Track System 🔄

```
Ideas → Classifier → 70% Learning Track → 🧠 Learning prompt
                   ↘                     
                    30% Ecosystem Track → ⚙️ Ecosystem prompt
                    
Learning prompt: "Research and document"
Ecosystem prompt: "Implement and integrate"
```

**Key:** Separate tracks from the start, enforce quotas

---

## Option 2: Graduated Levels 📈

```
All Ideas → Level 1: Explore → (if score ≥ 7) → Level 2: Apply
                               ↘
                                (if score < 7) → Archive
                                
Level 2 → (if score ≥ 7) → Level 3: Integrate into Core
```

**Key:** Natural progression, only best ideas advance

---

## Option 3: Context-Aware 🎯

```
All Ideas → Single Mission → Relevance Score → Adaptive prompt
                                              ↓
                            High (7+): "Implement {specific changes}"
                            Medium: "Research + suggest applications"
                            Low: "Document findings"
```

**Key:** One system, dynamic expectations based on relevance

---

## Option 4: Quota System ⚖️

```
Ideas → Categorize → Track quotas → Create mission
        ↓            ↓
        Learning:    60% ━━━━━━━━━━━━━━━━━━ (Current: 65%)
        Ecosystem:   30% ━━━━━━━━━━ (Current: 20% ⚠️ NEED MORE)
        Tools:       10% ━━━ (Current: 15%)
                            ↓
                     Prioritize underrepresented category
```

**Key:** Enforced balance, visible quotas

---

## Option 5: Two-Phase Pipeline ⭐ (Recommended)

```
All Ideas → Phase 1: Learning Mission
            ↓
            Complete with score (1-10)
            ↓
            Score < 7 → Archive (70% of missions)
            ↓
            Score ≥ 7 → Auto-generate Phase 2
            ↓
            Phase 2: Ecosystem Integration Mission
            ↓
            Implement into core (30% of missions)
```

**Key:** Natural filter, best ideas automatically become ecosystem work

---

## Side-by-Side Prompt Examples

### Current (All missions look like this)

```markdown
## 🎯 Mission: Cloud Innovation

Summary: Exploring cloud trends...

Expected Outputs:
- [ ] Documentation
- [ ] Code examples
- [ ] Learning artifacts

Next Steps:
1. Investigate the locations
2. Gather insights
3. Report findings
```

### Option 5 Phase 1 (Learning)

```markdown
## 🧠 Phase 1: Learn About Cloud Innovation

Type: Learning Mission
Phase: 1 of 2

Objective: Research cloud trends

Deliverables:
- [ ] Learning report
- [ ] Ecosystem score (1-10) ⭐
- [ ] Integration proposal (if score ≥ 7)

Next: High scores auto-trigger Phase 2
```

### Option 5 Phase 2 (Ecosystem) - Auto-generated

```markdown
## ⚡ Phase 2: Integrate Cloud Security

Type: Ecosystem Enhancement
Phase: 2 of 2
Triggered by: Phase 1 score of 8/10

Context: {Phase 1 learnings}

Objective: Add security scanning to CI/CD

Deliverables:
- [ ] Implementation + tests ⭐
- [ ] Documentation
- [ ] Performance metrics

Next: PR to core system
```

---

## Decision Guide

**Choose Option 1 (Dual-Track) if:**
- ✅ You want explicit control over balance
- ✅ You want quotas enforced
- ✅ You're okay with manual classification

**Choose Option 2 (Graduated) if:**
- ✅ You want natural progression
- ✅ You're willing to wait for results
- ✅ You want quality-gated advancement

**Choose Option 3 (Context-Aware) if:**
- ✅ You want the simplest solution ⭐ EASIEST
- ✅ You want to keep one mission type
- ✅ You're okay with emergent balance

**Choose Option 4 (Quota System) if:**
- ✅ You want strict balance enforcement
- ✅ You want visible quotas for agents
- ✅ You want predictable distribution

**Choose Option 5 (Two-Phase) if:** ⭐ RECOMMENDED
- ✅ You want to preserve learning
- ✅ You want automatic quality filtering
- ✅ You want clear learning → building pipeline
- ✅ You want natural balance (~30% ecosystem)

---

## Implementation Difficulty

```
Option 3 (Context-Aware)    ⭐      (1-2 hours)
Option 1 (Dual-Track)       ⭐⭐    (3-4 hours)
Option 4 (Quota System)     ⭐⭐    (3-4 hours)
Option 5 (Two-Phase)        ⭐⭐    (4-5 hours)
Option 2 (Graduated)        ⭐⭐⭐  (6-8 hours)
```

---

## My Recommendation: Start with Option 5

**Reasoning:**

1. **Preserves what works** - Learning from external sources is valuable
2. **Adds what's missing** - Clear path to ecosystem improvements
3. **Natural balance** - Quality determines which ideas advance
4. **Agent clarity** - Know if they're learning or building
5. **Measurable** - Track Phase 2 trigger rate

**Start simple:**
- Week 1-2: Phase 1 only (all missions = learning)
- Week 3: Add Phase 2 generation for high scores
- Week 4+: Monitor balance, adjust threshold if needed

**Target metrics:**
- 30% of Phase 1 missions trigger Phase 2
- At least 10 ecosystem improvements per month
- Agent satisfaction with clear objectives

---

## Quick Start: Option 5 Implementation

**Step 1:** Update `tools/create_mission_issues.py`
```python
# Add phase field
mission_data = {
    "phase": 1,
    "phase_1_score": None,
    "phase_2_trigger": False
}

# Use Phase 1 prompt template
issue_body = generate_phase_1_prompt(mission)
```

**Step 2:** Create `tools/generate_phase2_mission.py`
```python
# Check Phase 1 completion
if mission.phase_1_score >= 7:
    # Generate Phase 2 mission
    phase_2_mission = create_phase_2_from_phase_1(mission)
    create_issue(phase_2_mission)
```

**Step 3:** Add workflow trigger
```yaml
# .github/workflows/phase2-generator.yml
on:
  issues:
    types: [closed]
```

---

## Questions?

See full details in `MISSION_PROMPT_OPTIONS.md`

Or ask:
- Which option best fits your vision?
- What balance ratio do you prefer?
- Should we pilot first?

