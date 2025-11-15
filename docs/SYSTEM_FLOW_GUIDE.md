# Autonomous Closed-Loop System - Visual Guide

## System Flow Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL LEARNING SOURCES                        │
├────────────────────────────────────────────────────────────────────┤
│  📰 TLDR Tech News    📊 HN Stories    🌟 GitHub Trending          │
└──────────┬────────────┬────────────────┬───────────────────────────┘
           │            │                │
           ▼            ▼                ▼
    ┌──────────────────────────────────────────┐
    │  learn-from-tldr.yml                     │ Runs twice daily
    │  learn-from-hackernews.yml               │ (8 AM, 8 PM UTC)
    │  (GitHub trending via combined-learning) │
    └──────────────┬───────────────────────────┘
                   │
                   │ Produces learning files
                   │
                   ▼
    ┌──────────────────────────────────────────┐
    │  learnings/tldr_*.json                   │
    │  learnings/hn_*.json                     │
    │  learnings/github_trending_*.json        │
    └──────────────┬───────────────────────────┘
                   │
                   ▼
    ┌────────────────────────────────────────────────────┐
    │  COMBINED LEARNING                                  │
    │  combined-learning.yml                              │
    │  ────────────────────────────────────               │
    │  • Consolidates all learning sources                │
    │  • Extracts ideas, entities, locations              │
    │  • Creates combined_analysis_*.json                 │
    │  • TRIGGERS: world-update.yml                       │
    └──────────────┬─────────────────────────────────────┘
                   │
                   ▼
    ┌────────────────────────────────────────────────────┐
    │  WORLD MODEL UPDATE                                 │
    │  world-update.yml                                   │
    │  ────────────────────────────────────               │
    │  • Syncs learnings → ideas in knowledge.json        │
    │  • Updates regions in world_state.json              │
    │  • Prepares agent staging data                      │
    │  • Increments world tick                            │
    │  • TRIGGERS: agent-missions.yml                     │
    └──────────────┬─────────────────────────────────────┘
                   │
                   ▼
    ┌────────────────────────────────────────────────────┐
    │  AGENT MISSIONS                                     │
    │  agent-missions.yml                                 │
    │  ────────────────────────────────────               │
    │  • Analyzes recent ideas from learning              │
    │  • Scores all 11 agents for relevance:              │
    │    - Location relevance (30%)                       │
    │    - Role/skill match (40%)                         │
    │    - Performance history (30%)                      │
    │  • ENFORCES: Top 10 agents only (capacity limit)    │
    │  • Moves agents in world_state.json                 │
    │  • Creates labels via GitHub API                    │
    │  • Creates GitHub issues for missions               │
    └──────────────┬─────────────────────────────────────┘
                   │
                   ▼
    ┌────────────────────────────────────────────────────┐
    │  MISSION ISSUES CREATED                             │
    │  ────────────────────────────────────               │
    │  Format:                                            │
    │  • Title: 🎯 Mission: [Idea Title]                 │
    │  • Body includes:                                   │
    │    - Mission ID & timestamp                         │
    │    - Mission summary                                │
    │    - Locations involved                             │
    │    - Patterns & technologies                        │
    │    - Assigned agents (max 10)                       │
    │    - Expected outputs                               │
    │  • Labels:                                          │
    │    - learning, agent-mission, ai-generated          │
    │    - pattern-* (e.g., pattern-ai)                   │
    │    - location-* (e.g., location-us-san-francisco)   │
    └──────────────┬─────────────────────────────────────┘
                   │
                   ▼
    ┌────────────────────────────────────────────────────┐
    │  AGENTS WORK ON MISSIONS                            │
    │  ────────────────────────────────────               │
    │  • Human/AI completes assigned work                 │
    │  • Creates documentation, code, tools               │
    │  • Closes issues                                    │
    │  • Merges pull requests                             │
    │  • Updates agent metrics                            │
    └──────────────┬─────────────────────────────────────┘
                   │
                   ▼
    ┌────────────────────────────────────────────────────┐
    │  SELF-REINFORCEMENT LEARNING                        │
    │  self-reinforcement.yml                             │
    │  ────────────────────────────────────               │
    │  • Runs daily at midnight UTC                       │
    │  • Collects closed issues & merged PRs (last 7 days)│
    │  • Extracts patterns and locations                  │
    │  • Analyzes what worked                             │
    │  • Generates UNSUPERVISED_LEARNING_COMPLETE_*.md    │
    │  • TRIGGERS: combined-learning.yml                  │
    │  • CLOSES THE LOOP ↻                                │
    └──────────────┬─────────────────────────────────────┘
                   │
                   └──────────┐
                              │
                              ▼
                    ┌─────────────────┐
                    │   LOOP RESTARTS │
                    │   Autonomously  │
                    └─────────────────┘
```

## Component Details

### 🔄 The Continuous Loop

The system operates as a **fully autonomous closed loop**:

1. **LEARNING** → External sources provide knowledge
2. **COMBINE** → Consolidate and analyze learnings
3. **WORLD UPDATE** → Sync knowledge graph and regions
4. **AGENT MISSIONS** → Dispatch agents to opportunities
5. **WORK** → Agents complete missions
6. **SELF-REINFORCE** → Learn from completed work
7. **→ LEARNING** → Feed insights back (closes loop)

### 📊 Data Flow

```
External Data → Learning Files → Combined Analysis → World State
                                                     ↓
Agent Metrics ← Issue/PR Closed ← Agents Work ← Missions Created
       ↓
 Self-Learning → Back to Combined Analysis
```

### 🤖 Agent Selection Process

```
For each new idea from learning:

1. Load all 11 agents from world_state.json
2. Score each agent:
   score = (location_relevance × 0.3) +
           (role_skill_match × 0.4) +
           (performance_history × 0.3)
3. Sort by score (highest first)
4. Select TOP 10 ONLY (capacity limit)
5. Move selected agents to mission locations
6. Create mission issue with agent assignments
```

### 🏷️ Label Management

All labels are created automatically before use:

```
Required Base Labels:
- learning
- agent-mission
- ai-generated
- automated

Dynamic Labels (created as needed):
- pattern-{pattern}      e.g., pattern-ai, pattern-cloud
- location-{location}    e.g., location-us-california
```

### 📝 Mission Issue Template

```markdown
## 🎯 Agent Mission: [Idea Title]

**Mission ID:** [idea_id]
**Created:** [timestamp]

### 📋 Mission Summary
[idea summary]

### 🌍 Mission Locations
[comma-separated regions]

### 🏷️ Patterns & Technologies
[comma-separated patterns]

### 👥 Assigned Agents (Max 10)
- **Agent Name** (@specialization) - Score: X.XX
[... up to 10 agents]

### 📊 Expected Outputs
- [ ] Documentation
- [ ] Code examples
- [ ] World model updates
- [ ] Learning artifacts

### 🔄 Next Steps
1. Agents investigate mission locations
2. Gather insights and create artifacts
3. Report findings to world model
4. Update agent metrics
```

## Enforcement Rules

### 🚫 10-Agent Capacity Limit

**Code location:** `.github/workflows/agent-missions.yml`

```python
# Sort by score and take top 10
agent_scores.sort(key=lambda x: x['score'], reverse=True)
top_agents = agent_scores[:10]  # ENFORCE 10-AGENT LIMIT
```

**Why:** Prevents early system complexity explosion while agents learn to collaborate.

### ✅ Label Creation Before Use

**Code location:** `.github/workflows/agent-missions.yml`

```python
# Get existing labels
existing_labels = {label['name'].lower() for label in response.json()}

# Create missing labels
for label in required_labels:
    if label_name_lower not in existing_labels:
        requests.post(create_url, headers=headers, json=label)
```

**Why:** Ensures all labels exist in GitHub before creating issues.

### 📋 Mission Format

**Every mission must include:**
- ✅ Originating learning file(s)
- ✅ World location(s) involved
- ✅ Expected outputs
- ✅ Agent assignments (max 10)
- ✅ Proper labels (created beforehand)

## The 8 Questions Framework

Every piece of work in the system answers these 8 questions:

1. **Where is the learning artifact?**
   → `learnings/` directory with timestamped JSON/MD files

2. **Where is the world model update?**
   → `world-update.yml` modifies `world_state.json` and `knowledge.json`

3. **Which agents are reacting?**
   → Selected by `agent-missions.yml` based on relevance scoring

4. **Are no more than 10 agents assigned?**
   → Yes, enforced by `top_agents = agent_scores[:10]`

5. **How do agents move in the world model?**
   → `location_region_id` updated in `world_state.json`

6. **What mission issue is being created?**
   → GitHub issue via `tools/create_mission_issues.py`

7. **Were all labels created before use?**
   → Yes, in "Ensure required labels exist" step

8. **Which workflow continues the loop?**
   → `self-reinforcement.yml` → `combined-learning.yml` → cycle repeats

## Monitoring the System

### Check Current State
```bash
# View world tick (should increment)
cat world/world_state.json | jq '.tick'

# See agent positions
cat world/world_state.json | jq '.agents[] | {id, location_region_id, status}'

# List open missions
gh issue list --label agent-mission

# View recent learnings
ls -lt learnings/ | head -10
```

### Watch Workflow Runs
```bash
# List recent runs
gh run list --limit 20

# View specific workflow runs
gh run list --workflow=agent-missions.yml
gh run list --workflow=self-reinforcement.yml
```

### Trigger Manual Run
```bash
# Trigger any workflow
gh workflow run combined-learning.yml
gh workflow run world-update.yml
gh workflow run agent-missions.yml
gh workflow run self-reinforcement.yml
```

## System Health Indicators

### ✅ Healthy System
- World tick increments regularly (every 2 hours)
- New missions created based on learnings
- Agents move to new locations
- Issues are closed and PRs merged
- Self-reinforcement runs daily
- Loop continues autonomously

### ⚠️ Check for Issues
- World tick stuck at same value
- No new missions created
- Agents not moving
- Labels not being created
- Workflow chain broken
- Self-reinforcement not triggering

## Future Enhancements

Possible extensions to the system:

1. **Dynamic Agent Creation** - Add agents based on emerging patterns
2. **Performance-Based Evolution** - Remove low-performing agents
3. **Multi-Region Exploration** - Agents explore multiple regions simultaneously
4. **Collaborative Missions** - Agents work together on complex tasks
5. **Learning Quality Scoring** - Rate learning sources by value
6. **Adaptive Capacity Limits** - Adjust 10-agent limit based on performance

---

*This autonomous system learns, explores, and improves itself continuously without human intervention.*
