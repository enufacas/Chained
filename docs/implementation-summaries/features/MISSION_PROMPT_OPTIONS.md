# 🎯 Mission Prompt Evolution Options

## 📊 Current State Analysis

### The Problem
The autonomous pipeline's mission prompts (`tools/create_mission_issues.py`) currently treat **ALL missions as external learning tasks**, even when work could directly improve Chained's core ecosystem.

**Current prompt characteristics:**
- Generic "investigate and gather insights" instructions
- Focus on exploration and documentation
- No clear connection to improving Chained itself
- Same template for all mission types

### The Balance Challenge

You identified a critical tension:
> "There is a line between learning and building semi related features versus building features more strongly within our core ecosystem"

### Mission Type Examples

**🧠 LEARNING Mission (External Focus):**
- "Explore cloud trends from tech news"
- "Investigate new AI frameworks mentioned in HN"
- Goal: Understand what's happening in the tech world

**🔧 SEMI-RELATED Mission (Tangential):**
- "Build a cloud deployment tool" (inspired by trends)
- "Create an AI benchmarking system" (inspired by news)
- Goal: Build something related to learnings, but not core to Chained

**⚡ CORE ECOSYSTEM Mission (Internal Focus):**
- "Improve agent spawning algorithm diversity"
- "Enhance world model geographic accuracy"
- "Optimize autonomous pipeline PR merge timing"
- Goal: Make Chained itself better, stronger, more capable

**Core Ecosystem Components:**
- 🤖 Agent system (spawning, evaluation, competition)
- 🧠 Learning system (from external sources)
- 🌍 World model (geographic mapping, state)
- 🔄 Autonomous pipeline (workflows, PR creation/merge)
- 📊 Self-documentation and metrics
- 🏆 Performance tracking and Hall of Fame

---

## 🎨 Five Evolution Options

### Option 1: Dual-Track Mission System 🔄

**Concept:** Create two distinct mission types with different prompts.

**Learning Track:**
```markdown
## 🧠 Learning Mission: {title}
**Type:** External Exploration
- Research and document tech trends
- Identify potential applications to Chained
- Deliverable: Learning report + ecosystem suggestions
```

**Ecosystem Track:**
```markdown
## ⚙️ Ecosystem Mission: {title}
**Type:** Core System Enhancement
- Implement direct improvements to Chained
- Deliverable: Code, tests, documentation, metrics
```

**Balance:** Set quotas (e.g., 70% learning / 30% ecosystem)

**Pros:**
- ✅ Clear separation of concerns
- ✅ Agents know exactly what to expect
- ✅ Easy to balance (track mission counts)
- ✅ Can enforce quotas

**Cons:**
- ❌ Requires upfront idea classification
- ❌ More complex routing
- ❌ Less connection between learning and building

**Implementation Effort:** Medium (~250 lines)

---

### Option 2: Graduated Mission System 📈

**Concept:** Three-level progression from learning to integration.

**Levels:**
1. **Level 1 - Explore:** Research and learn (all missions start here)
2. **Level 2 - Apply:** Build proof-of-concept (if relevance ≥ 7)
3. **Level 3 - Integrate:** Merge into core (if integration score ≥ 7)

**Pros:**
- ✅ Natural progression
- ✅ Self-regulating (only good ideas advance)
- ✅ Agents see full journey

**Cons:**
- ❌ Longer time to ecosystem improvements
- ❌ Complex state tracking
- ❌ Might lose momentum between levels

**Implementation Effort:** High (~400 lines)

---

### Option 3: Context-Aware Prompt Enhancement 🎯

**Concept:** Single mission type with ecosystem relevance scoring.

**Enhanced Prompt:**
```markdown
## 🎯 Agent Mission: {title}
**Type:** {Learning | Ecosystem}
**Ecosystem Relevance:** {Low | Medium | High | Critical}

{IF High/Critical:}
  Ecosystem Connection: Could improve {components}
  Expected: Implementation + tests + metrics
  
{ELSE:}
  Focus: External learning
  Expected: Research report + insights
```

**Pros:**
- ✅ Single mission system (simpler)
- ✅ Clear communication of intent
- ✅ Easy to implement
- ✅ Flexible expectations

**Cons:**
- ❌ Still need relevance scoring logic
- ❌ Variable expectations might confuse
- ❌ Harder to enforce balance

**Implementation Effort:** Low (~100 lines) ⭐ EASIEST

---

### Option 4: Explicit Quota Balancing System ⚖️

**Concept:** Add metadata to categorize missions and enforce quotas.

**Mission Categories:**
- 🧠 Learning: 60%
- ⚙️ Ecosystem: 30%
- 🔧 Tool Building: 10%

**Enhanced Prompt:**
```markdown
## {icon} {category} Mission: {title}
**Category:** {Learning | Ecosystem | Tools}
**Quarter Goal:** Learning: 60% | Ecosystem: 30% | Tools: 10%
**Balance Status:** Need {X} more ecosystem missions this quarter
```

**Pros:**
- ✅ Enforced balance automatically
- ✅ Transparent quotas
- ✅ Agents see bigger picture
- ✅ Easy to adjust ratios

**Cons:**
- ❌ Requires classification logic
- ❌ Might constrain good ideas artificially
- ❌ Quota system could feel rigid

**Implementation Effort:** Medium (~250 lines)

---

### Option 5: Two-Phase Learning → Ecosystem Pipeline 🔄🔧 ⭐ RECOMMENDED

**Concept:** All missions start as learning, valuable ones auto-generate ecosystem follow-ups.

**Phase 1 - Learning (All missions):**
```markdown
## 🧠 Phase 1: Learn About {topic}
**Phase:** 1 of 2 (Exploration)

### Required Deliverables:
- Learning report
- **Ecosystem relevance score (1-10)**
- Integration suggestions (if relevant)

### Phase 2 Trigger:
Score ≥ 7 → Automatically creates ecosystem mission
```

**Phase 2 - Ecosystem (Auto-generated for high scores):**
```markdown
## ⚡ Phase 2: Integrate {topic} into Chained
**Phase:** 2 of 2 (Integration)
**Triggered by:** Phase 1 score of {X}/10

### Context from Phase 1:
{Key learnings and insights}

### Implementation Requirements:
- Core system integration
- Tests and validation
- Performance measurement
```

**Pros:**
- ✅ Best of both worlds (learning + building)
- ✅ Natural progression for valuable ideas
- ✅ Clear connection between phases
- ✅ Quality filtering (only good ideas → core)
- ✅ Agent ownership (same agent both phases)
- ✅ Preserves learning strength

**Cons:**
- ❌ More complex pipeline
- ❌ Need scoring mechanism
- ❌ Two prompt templates

**Balance:** ~30% of missions reach Phase 2 (emergent from quality)

**Implementation Effort:** Medium (~300 lines)

---

## 📊 Comparison Matrix

| Option | Complexity | Balance Control | Agent Clarity | Effort | Learning Preserved |
|--------|------------|-----------------|---------------|--------|-------------------|
| 1. Dual-Track | Medium | High (Quotas) | Excellent | Medium | Separate |
| 2. Graduated | High | Self-regulating | Good | High | Yes |
| 3. Context-Aware | Low | Medium | Good | Low ⭐ | Yes |
| 4. Quota System | Medium | Excellent | Excellent | Medium | Yes |
| 5. Two-Phase ⭐ | Medium | Natural | Excellent | Medium | Yes + Enhanced |

---

## 💡 My Recommendation: Option 5 (Two-Phase Pipeline)

### Why Option 5?

1. **Preserves your learning strength** - All missions start as learning
2. **Natural progression** - Agents learn first, then build
3. **Quality filtering** - Only valuable findings reach ecosystem phase
4. **Clear connection** - Phase 2 explicitly references Phase 1 learnings
5. **Balanced automatically** - ~30% reach Phase 2 (emergent from quality)
6. **Agent ownership** - Same agent completes both phases
7. **Minimal disruption** - Builds on existing flow

### Implementation Overview

**Step 1: Update mission creation**
- All missions labeled as "Phase 1 - Learning"
- Add ecosystem scoring requirement
- Template emphasizes research + evaluation

**Step 2: Add Phase 2 generation**
- On Phase 1 completion, check score
- If score ≥ 7: Auto-generate Phase 2 mission
- Phase 2 inherits context from Phase 1
- Assign to same agent

**Step 3: Track metrics**
- Phase 1 completion rate
- Phase 2 trigger rate (target ~30%)
- Ecosystem improvement velocity

**Changes Required:**
1. `tools/create_mission_issues.py` - Two prompt templates
2. New script: `tools/generate_phase2_mission.py`
3. Workflow trigger for Phase 2 generation
4. Mission data: Add phase and scoring fields

---

## 🤔 Discussion Questions

Before implementing, I'd like your input on:

1. **Which option resonates with you most?**
   - Option 5 (Two-Phase) is my recommendation
   - But Option 3 (Context-Aware) is simplest
   - Or do you prefer a different approach?

2. **What's your target balance?**
   - How much should be learning vs ecosystem?
   - 70/30? 80/20? Let it emerge naturally?

3. **Scoring threshold?**
   - For Phase 2 trigger, is 7/10 right?
   - Should it be higher (8/10) or lower (6/10)?

4. **Should we pilot with one option first?**
   - Test with 5-10 missions before full rollout?
   - Or implement system-wide immediately?

5. **Any other considerations?**
   - Other mission types to consider?
   - Different categorization needed?

---

## 🚀 Next Steps

Once you choose an option, I'll:

1. ✅ Implement the chosen approach
2. ✅ Update prompt templates
3. ✅ Modify mission creation logic
4. ✅ Add any necessary tracking
5. ✅ Update documentation
6. ✅ Test with sample missions
7. ✅ Create PR with changes

Let me know which direction you'd like to go!

---

## 📎 Detailed Examples

See complete prompt examples in `/tmp/prompt_examples.md` (local) showing:
- Current baseline prompt
- Option 3 enhanced prompt
- Option 5 Phase 1 and Phase 2 prompts
- Option 1 dual-track prompts

**Quick Preview - Option 5 Phase 1:**
```markdown
## 🧠 Phase 1: Learn About Cloud Innovation

**Phase:** 1 of 2 (Exploration)
**Type:** Learning Mission

### 🎓 Learning Objective
Research cloud security trends from tech news...

### 📊 Phase 1 Deliverables
- [ ] Learning Report (1-2 pages)
- [ ] Ecosystem Applicability Assessment (1-10 score)
- [ ] Phase 2 Recommendation (Yes/No + proposal)

### ⚡ Phase 2 Trigger
Score ≥ 7/10 → Auto-creates integration mission
```

**Option 5 Phase 2 (Auto-generated):**
```markdown
## ⚡ Phase 2: Integrate Cloud Security into Chained

**Phase:** 2 of 2 (Ecosystem Integration)
**Triggered by:** Phase 1 score of 8/10

### 🔗 Context from Phase 1
{Summary of Phase 1 learnings}

### 🎯 Integration Objective
Apply learnings to enhance Chained's {component}...

### 📊 Deliverables
- [ ] Implementation with tests
- [ ] Documentation updates
- [ ] Performance measurement
```

---

*Created: 2025-11-16*
*Issue: Improving autonomous pipeline mission prompts*
*Goal: Balance learning vs core ecosystem building*
