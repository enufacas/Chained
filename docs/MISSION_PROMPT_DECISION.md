# 🎯 Mission Prompt Evolution - Quick Decision Guide

**Date:** 2025-11-16  
**Issue:** Improve autonomous pipeline mission prompts  
**Status:** Analysis complete, awaiting decision

---

## 🔴 The Problem (30 seconds)

Current mission prompts are **too generic**:
- All missions treated as "learning" (exploration)
- No clear path to "ecosystem" work (building Chained itself)
- Vague deliverables: "documentation", "insights"
- Result: 100% exploration, 0% core improvements

---

## 🎯 The Goal (30 seconds)

**Balance learning AND building:**
- **Learning missions:** Understand external tech trends (TLDR, HN)
- **Ecosystem missions:** Improve Chained's core capabilities
- **Target balance:** ~70% learning, ~30% ecosystem (your choice)

---

## ⚡ Quick Recommendation (60 seconds)

**Option 5: Two-Phase Pipeline** ⭐

**How it works:**
1. All missions start as **Phase 1 (Learning)**
   - Research topic, document findings
   - Score ecosystem relevance (1-10)
   
2. High-value findings (score ≥7) trigger **Phase 2 (Ecosystem)**
   - Auto-generated integration mission
   - Concrete implementation work
   - Same agent owns both phases

**Why it's best:**
- ✅ Preserves learning (all missions start there)
- ✅ Natural filter (only good ideas → ecosystem)
- ✅ Clear prompts (research OR implement, not both)
- ✅ Balanced automatically (~30% reach Phase 2)

**Implementation:** 4-5 hours

---

## 📊 All 5 Options (2 minutes)

### Option 1: Dual-Track 🔄
- Two separate mission types from start
- Enforce quotas (70% learning / 30% ecosystem)
- **Pro:** Clear separation | **Con:** Need upfront classification

### Option 2: Graduated 📈
- Three levels: Explore → Apply → Integrate
- Progression through quality gates
- **Pro:** Natural advancement | **Con:** Takes longer, complex tracking

### Option 3: Context-Aware 🎯
- Single mission type, add relevance scoring
- Adjust expectations based on score
- **Pro:** Simplest (1-2 hours) | **Con:** Less clear separation

### Option 4: Quota System ⚖️
- Track categories: 60% learn / 30% build / 10% tools
- Show agents balance status
- **Pro:** Enforced balance | **Con:** Might feel rigid

### Option 5: Two-Phase 🔄🔧 ⭐
- All start as learning, valuable ones → ecosystem
- Auto-generation for high scores
- **Pro:** Best of both worlds | **Con:** Two templates needed

---

## 📝 Example: Cloud Security Mission

### Current (Generic)
```
Mission: Cloud Innovation
Expected: Documentation, insights
Next Steps: Investigate and gather
```
**Problem:** Agent doesn't know what to actually do

### After (Option 5 - Phase 1)
```
Mission: Learn About Cloud Security
Expected: 
- Research report (2-3 pages)
- Ecosystem relevance score (1-10)
- Integration proposal (if score ≥7)
Next: If score ≥7, Phase 2 auto-created
```
**Better:** Clear deliverables, honest evaluation

### After (Option 5 - Phase 2, if score ≥7)
```
Mission: Integrate Cloud Security Scanning
Context: {Phase 1 findings}
Expected:
- Security scan workflow implementation
- Tests and documentation
- Performance metrics
Next: Create PR with changes
```
**Best:** Concrete implementation goal

---

## 🤔 Decision Framework (1 minute)

**Choose based on your priority:**

### Want simplest solution?
→ **Option 3** (Context-Aware, 1-2 hours)

### Want strict balance control?
→ **Option 4** (Quota System, 3-4 hours)

### Want natural quality filter?
→ **Option 5** (Two-Phase, 4-5 hours) ⭐ RECOMMENDED

### Want explicit separation?
→ **Option 1** (Dual-Track, 3-4 hours)

### Want progressive refinement?
→ **Option 2** (Graduated, 6-8 hours)

---

## ✅ Quick Questions

**Answer these to help decide:**

1. **Balance preference?**
   - [ ] Natural (emergent from quality) → Option 5
   - [ ] Enforced (quotas) → Option 4
   - [ ] Don't care much → Option 3

2. **Implementation time available?**
   - [ ] 1-2 hours → Option 3
   - [ ] 3-4 hours → Options 1, 4
   - [ ] 4-5 hours → Option 5
   - [ ] 6+ hours → Option 2

3. **Most important feature?**
   - [ ] Learning preserved → Option 5
   - [ ] Simplicity → Option 3
   - [ ] Control → Option 4
   - [ ] Clear separation → Option 1
   - [ ] Quality gates → Option 2

4. **Acceptable complexity?**
   - [ ] Low → Option 3
   - [ ] Medium → Options 1, 4, 5
   - [ ] High → Option 2

---

## 🚀 Next Steps

**Once you decide:**

1. **Tell me which option** (1, 2, 3, 4, or 5)

2. **Answer these (if Option 5):**
   - Target balance? (30% ecosystem seems right)
   - Phase 2 threshold? (7/10 or adjust?)
   - Pilot first? (5-10 missions) or full rollout?

3. **I'll implement:**
   - Update `tools/create_mission_issues.py`
   - Create/modify prompt templates
   - Add necessary tracking/scoring
   - Test with sample data
   - Create PR with changes

**Time estimate:** 1-5 hours depending on option

---

## 📚 Full Documentation

- **Detailed Analysis:** `MISSION_PROMPT_OPTIONS.md` (10 pages)
- **Visual Guide:** `docs/MISSION_PROMPT_COMPARISON.md` (diagrams)
- **Examples:** `docs/MISSION_PROMPT_EXAMPLES.md` (before/after)
- **This Summary:** `docs/MISSION_PROMPT_DECISION.md` (you are here)

---

## 💭 My Personal Take

**I recommend Option 5** because:

1. **Preserves what works** - Your learning loop is powerful
2. **Adds what's missing** - Clear path to ecosystem improvements
3. **Quality over quantity** - Only best ideas reach Phase 2
4. **Agent clarity** - Know if researching or building
5. **Measurable** - Track Phase 2 trigger rate

**Objections addressed:**
- "Too complex?" → Only 2 templates, rest is auto
- "Will it slow down?" → No, Phase 1 completes normally
- "What if agents game it?" → They want to build, high scores are good!
- "Can we adjust?" → Yes, threshold is configurable

**Start conservative:**
- Week 1-2: Phase 1 only (establish baseline)
- Week 3: Add Phase 2 generation (threshold 8/10)
- Week 4+: Lower to 7/10 if needed
- Monitor: Aim for ~30% Phase 2 trigger rate

---

## 🎯 TL;DR

**Current:** Vague learning prompts, no ecosystem work  
**Recommended:** Two-phase (learn → build) with quality filter  
**Result:** ~30% missions become real improvements to Chained  
**Time:** 4-5 hours to implement  
**Next:** Tell me which option you prefer!

---

*Ready to implement when you are!* 🚀
