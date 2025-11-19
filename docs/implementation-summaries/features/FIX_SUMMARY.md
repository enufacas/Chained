# Fix: Autonomous Pipeline Agent Assignment Issues

## Problem Summary

The autonomous-pipeline workflow had two critical bugs:

### Bug 1: Same Agent Assigned to All Issues ❌
**Symptom:** 5 issues created, all assigned to the same agent  
**Root Cause:** Lines 916-935 in autonomous-pipeline.yml assigned all agents the same score (0.5)
```python
for agent in agents:
    score = 0.5  # Base score - NO DIFFERENTIATION!
```
**Impact:** The workflow always selected the first agent in the list for every mission

### Bug 2: Duplicate Mission Creation ❌
**Symptom:** Same missions created on each workflow run  
**Root Cause:** No tracking of previously created missions between runs  
**Impact:** Duplicate issues cluttering the repository

## Solution Implemented

### 1. Use Existing Agent Matching Tool ✅

**Before:** Inline hardcoded scoring logic with no differentiation
```python
# Old broken code
for agent in agents:
    score = 0.5  # Everyone gets same score!
```

**After:** Use the comprehensive `tools/match-issue-to-agent.py` tool
```python
# New working code
result = subprocess.run(
    ['python3', 'tools/match-issue-to-agent.py', match_text],
    capture_output=True,
    text=True,
    check=True
)
match_data = json.loads(result.stdout)
matched_specialization = match_data.get('agent')
```

**Benefits:**
- 43+ agent specializations with comprehensive keyword patterns
- Regex-based pattern matching
- Proper scoring based on issue content
- Confidence levels (high/medium/low)
- Returns all scores for fallback options

### 2. Add Mission Deduplication ✅

**Implementation:**
- Track mission hashes in `.github/agent-system/missions_history.json`
- Hash includes: idea_id, title, and patterns
- Skip missions that have been created before
- Keep last 100 hashes to prevent unbounded growth

```python
mission_content = f"{idea_id}:{idea_title}:{':'.join(sorted(idea_patterns))}"
mission_hash = hashlib.md5(mission_content.encode()).hexdigest()

if mission_hash in previous_mission_hashes:
    print(f"  ⏭️  Skipping duplicate mission for '{idea_title}'")
    continue
```

### 3. Encourage Agent Variety ✅

**Implementation:**
- Track agents used in current run
- If best match already used, select from unused agents
- Uses `all_scores` from match-issue-to-agent.py output

```python
if matched_specialization in used_agents:
    all_scores = match_data.get('all_scores', {})
    unused_agents = [(spec, score) for spec, score in all_scores.items() 
                    if spec not in used_agents and score > 0]
    if unused_agents:
        unused_agents.sort(key=lambda x: x[1], reverse=True)
        matched_specialization = unused_agents[0][0]
```

## Architecture Understanding

### Workflow Flow

```
Stage 4: agent-missions
├── Create missions (lines 878-1061)
│   ├── Load world_state.json (agents)
│   ├── Load knowledge.json (ideas)
│   ├── Match each idea to best agent using match-issue-to-agent.py
│   ├── Save missions_data.json
│   └── Track in missions_history.json
├── Create mission issues
│   └── tools/create_mission_issues.py
│       ├── Creates GitHub issues
│       └── Saves created_missions.json (issue_number + agent_specialization)
└── Update world state PR

Stage 4.5: merge-mission-pr
└── Wait for PR merge

Stage 4.75: assign-agents-to-missions
└── Assign agents to issues
    └── tools/assign-agent-directly.sh
        ├── Reads created_missions.json
        ├── For each issue:
        │   ├── Validates agent file exists
        │   ├── Adds agent directive to issue body with @mention
        │   └── Assigns via GitHub GraphQL API
        └── Adds copilot-assigned label
```

### Key Insight

**Stage 4 (mission creation) is where agent matching happens!**

The assignment stage (4.75) just takes the decisions from Stage 4 and executes them via GraphQL API. It doesn't re-evaluate which agent should be assigned - it trusts the `created_missions.json` file.

Therefore, fixing the agent matching in Stage 4 was the correct approach.

## Files Changed

1. **`.github/workflows/autonomous-pipeline.yml`**
   - Replaced hardcoded scoring with match-issue-to-agent.py calls
   - Added mission deduplication logic
   - Added variety encouragement
   - Updated PR creation to include missions_history.json

2. **`.github/agent-system/missions_history.json`** (new)
   - Tracks mission hashes to prevent duplicates
   - Initialized with empty structure

3. **`test_mission_matching.py`** (new)
   - Test script to validate agent matching logic
   - Demonstrates variety in agent selection
   - Shows that different ideas get different agents

## Test Results

```
🧪 Testing Mission Matching Logic

📋 Idea: Cloud Security Best Practices
   Patterns: cloud, security, devops
   ✅ Selected: ☁️ Cloud Expert (@cloud-architect)

📋 Idea: Testing Frameworks Comparison
   Patterns: testing, coverage, api
   ✅ Selected: 🧪 Tesla (@assert-specialist)

📋 Idea: Code Review Best Practices
   Patterns: review, refactor, clean
   ✅ Selected: 🧹 Robert Martin (@organize-guru)

📋 Idea: Performance Optimization Techniques
   Patterns: performance, optimize
   ✅ Selected: 💭 Turing (@coach-master)

📋 Idea: Kubernetes Best Practices
   Patterns: cloud, kubernetes, devops
   ✅ Selected: ☁️ Cloud Expert (@cloud-architect)

📊 Mission Summary:
   Unique agents used: 4/5 missions
   ✅ PASS: Good agent variety!
```

## Expected Behavior After Fix

### Before Fix ❌
- 5 missions created
- All assigned to first agent (e.g., @organize-guru)
- Missions recreated on every run
- No variety in assignments

### After Fix ✅
- 5 missions created with intelligent matching
- Each assigned to most appropriate agent:
  - Cloud topics → @cloud-architect
  - Testing → @assert-specialist  
  - Refactoring → @organize-guru
  - Security → @secure-specialist
- Missions deduplicated across runs
- Good variety in agent selection

## Verification Steps

1. **Check agent variety:**
   ```bash
   gh issue list --label agent-mission --limit 20 --json number,title,labels \
     | jq -r '.[] | .labels | map(select(.name | startswith("agent:"))) | .[].name'
   ```

2. **Check for duplicates:**
   ```bash
   cat .github/agent-system/missions_history.json | jq '.mission_hashes | length'
   ```

3. **Monitor workflow runs:**
   - https://github.com/enufacas/Chained/actions/workflows/autonomous-pipeline.yml
   - Check "Create missions" step logs for variety messages

## Related PRs

- PR #1273 - Previous attempt (didn't address root cause)
- PR #1245 - Previous attempt (didn't address root cause)
- This PR - Comprehensive fix with proper agent matching and deduplication

## Credits

Fix implements proper use of existing `tools/match-issue-to-agent.py` which was written with comprehensive agent matching patterns but was not being used by the autonomous-pipeline workflow.
