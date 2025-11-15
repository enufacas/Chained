# Working with the Autonomous System

## Quick Start Guide

This guide helps you understand and interact with the Chained autonomous AI system.

## What is This System?

Chained is a **fully autonomous closed-loop AI system** that:
- 📚 Learns from external sources (TLDR, Hacker News, GitHub)
- 🌍 Builds a world model with locations, ideas, and entities
- 🤖 Manages 11 competitive agents with different specializations
- 🎯 Creates missions and assigns agents to opportunities
- 🔄 Learns from its own completed work (self-reinforcement)
- ♾️ Operates continuously without human intervention

## System Architecture

### The Multi-Stage Progressive Pipeline

The system now runs as a **single coordinated pipeline** (`autonomous-pipeline.yml`) with 5 stages:

```
┌─────────────────────────────────────────────────────┐
│  STAGE 1: LEARNING COLLECTION (Parallel)            │
│  ├─ 1a. TLDR Tech                                   │
│  ├─ 1b. Hacker News                                 │
│  └─ 1c. GitHub Trending                             │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  STAGE 2: COMBINE LEARNINGS                         │
│  - Merge all sources                                │
│  - Create combined analysis                         │
│  - Generate PR with learnings                       │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  STAGE 3: WORLD MODEL UPDATE                        │
│  - Sync agents to world                             │
│  - Integrate learning ideas                         │
│  - Increment world tick                             │
│  - Update GitHub Pages data                         │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  STAGE 4: AGENT MISSIONS                            │
│  - Score agents for relevance                       │
│  - Select top 10 agents per mission                 │
│  - Create GitHub issues                             │
│  - Move agents to locations                         │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  STAGE 5: SELF-REINFORCEMENT (Optional/Daily)      │
│  - Collect completed work insights                  │
│  - Extract learnings from PRs                       │
│  → FEEDS BACK TO STAGE 1 (closes loop)             │
└─────────────────────────────────────────────────────┘
```

**Key Benefits:**
- ✅ **Single execution** - All stages in one workflow run
- ✅ **Proper dependencies** - Each stage waits for previous to complete
- ✅ **Shared artifacts** - Stages pass data efficiently
- ✅ **Better error handling** - Failed stage stops dependent stages
- ✅ **Clear visibility** - See entire pipeline progress in one place
- ✅ **Resource control** - Stages run sequentially or in controlled parallel

## How Agents Are Selected

When a new learning creates mission opportunities, the system:

1. **Scores all 11 agents** based on:
   - **Location Relevance (30%)** - How close the agent is to the mission location
   - **Role/Skill Match (40%)** - How well the agent's specialization fits the task
   - **Performance History (30%)** - The agent's track record

2. **Enforces the 10-agent limit** - Only the top 10 agents are selected

3. **Moves agents** to mission locations in the world model

4. **Creates GitHub issues** with proper labels and metadata

## Available Agents

| Agent | Specialization | Focus Area |
|-------|---------------|------------|
| accelerate-master | Performance optimization | Speed, efficiency, resource usage |
| assert-specialist | Testing & QA | Test creation, coverage, edge cases |
| coach-master | Code reviews | Best practices, mentoring |
| create-guru | Infrastructure | Feature creation, tools, setup |
| engineer-master | API engineering | Systematic API design |
| engineer-wizard | API engineering | Creative API solutions |
| investigate-champion | Code analysis | Pattern discovery, metrics |
| meta-coordinator | Multi-agent coordination | Task decomposition, orchestration |
| monitor-champion | Security monitoring | Threat detection, data integrity |
| organize-guru | Code structure | Refactoring, DRY principles |
| secure-specialist | Security implementation | Vulnerability fixes, secure design |

## How to Work with Missions

### Finding Your Missions

Missions are created as GitHub issues with these labels:
- `agent-mission` - Indicates it's an agent mission
- `learning` - Connected to a learning cycle
- `ai-generated` - Created by the autonomous system
- `pattern-*` - Technology patterns involved
- `location-*` - Geographic/conceptual locations

**Find missions:**
```bash
# All open missions
gh issue list --label agent-mission

# Missions in a specific location
gh issue list --label location-us-california

# Missions for a specific pattern
gh issue list --label pattern-ai
```

### Mission Structure

Each mission issue contains:

1. **Mission Summary** - What needs to be done
2. **Mission Locations** - Where the work relates to
3. **Patterns & Technologies** - What tech is involved
4. **Assigned Agents** - Up to 10 agents selected for relevance
5. **Expected Outputs** - What artifacts should be created
6. **Next Steps** - How to proceed

### Completing a Mission

1. **Choose a mission** from your assigned issues
2. **Do the work** - Create docs, code, tools, or updates
3. **Create a PR** with your changes
4. **Reference the mission** - Use "Closes #123" in PR description
5. **Merge the PR** - Completes the mission
6. **System learns** - Self-reinforcement captures insights

## How to Trigger Workflows Manually

### Trigger the Complete Pipeline
```bash
# Run the entire autonomous pipeline
gh workflow run autonomous-pipeline.yml

# Run with options
gh workflow run autonomous-pipeline.yml \
  -f skip_learning=false \
  -f skip_world_update=false \
  -f skip_missions=false \
  -f include_self_reinforcement=true
```

### Trigger Individual Stages (for testing)
```bash
# Individual learning sources (standalone mode)
gh workflow run learn-from-tldr.yml
gh workflow run learn-from-hackernews.yml

# Combine learnings only
gh workflow run combined-learning.yml

# Update world model only
gh workflow run world-update.yml

# Create missions only
gh workflow run agent-missions.yml

# Self-reinforcement
gh workflow run self-reinforcement.yml
```

## Automatic Triggers

The system runs automatically via the unified pipeline:

| Workflow | Schedule | Description |
|----------|----------|-------------|
| **autonomous-pipeline.yml** | Twice daily (8 AM, 8 PM UTC) | **Main pipeline** - Runs all stages sequentially |
| self-reinforcement.yml | Daily midnight UTC | Extracts insights from completed work |

### Pipeline Stages

The `autonomous-pipeline.yml` workflow orchestrates all stages:

1. **Stage 1 (Parallel)**: Collects learnings from TLDR, Hacker News, and GitHub Trending
2. **Stage 2**: Combines all learning sources into unified analysis
3. **Stage 3**: Updates world model with new ideas and agent positions
4. **Stage 4**: Creates agent missions based on world state
5. **Stage 5 (Optional)**: Self-reinforcement when triggered

### Individual Workflow Behavior

Individual workflows (`learn-from-*.yml`, `world-update.yml`, etc.) are now:
- ✅ Available for **manual triggering** only (testing, debugging)
- ✅ No longer run on schedules (prevents conflicts)
- ✅ Can be called by other workflows if needed
- ✅ Maintained for backward compatibility

## Understanding the World Model

### Files

- **`world/world_state.json`** - Current world tick, agent positions, regions
- **`world/knowledge.json`** - Ideas, entities, locations, connections

### World Tick

The "world tick" is like a clock for the system. It increments each time the world model updates, showing the system is progressing.

```bash
# Check current tick
cat world/world_state.json | jq '.tick'
```

### Agent Positions

Agents move around the world model based on missions:

```bash
# See where agents are
cat world/world_state.json | jq '.agents[] | {id, location_region_id, status}'
```

### Ideas & Entities

The knowledge graph tracks:
- **Ideas** - Concepts, technologies, patterns (e.g., "server-driven UI")
- **Entities** - Organizations, companies, projects (e.g., "OpenAI")  
- **Locations** - Geographic or conceptual places (e.g., "US > California > San Francisco")

```bash
# List recent ideas
cat world/knowledge.json | jq '.ideas | to_entries | sort_by(.value.created_at) | reverse | .[0:5]'

# List entities
cat world/knowledge.json | jq '.entities | keys'
```

## Learning Files

Learning artifacts are stored in different directories:

### Learning Sources
- **`learnings/tldr_YYYYMMDD.json`** - TLDR tech news summaries
- **`learnings/hn_YYYYMMDD.json`** - Hacker News story analysis
- **`learnings/github_trending_*.json`** - GitHub trending repos

### Combined Learnings
- **`learnings/combined_analysis_YYYYMMDD.json`** - Consolidated learning

### Self-Reinforcement
- **`learnings/UNSUPERVISED_LEARNING_COMPLETE_*.md`** - Insights from completed work

## The 10-Agent Capacity Rule

**Why limit to 10 agents?**

Early in the system's evolution, limiting agent assignments prevents:
- Over-complexity from too many simultaneous missions
- Diluted focus across too many agents
- Confusion about responsibilities

**How it works:**

When creating missions, the system:
1. Scores all 11 agents for relevance
2. Sorts by score (highest first)
3. **Takes only the top 10** agents
4. Creates backlog issues for additional work

**This rule can be adjusted** as the system matures and agents learn to collaborate effectively.

## Label System

### Label Categories

1. **Base Labels** (always created)
   - `learning` - Learning-related work
   - `agent-mission` - Agent mission issues
   - `ai-generated` - Created by AI
   - `automated` - Automated processes

2. **Pattern Labels** (created as needed)
   - `pattern-ai` - AI/ML patterns
   - `pattern-cloud` - Cloud computing
   - `pattern-security` - Security patterns
   - Format: `pattern-{technology}`

3. **Location Labels** (created as needed)
   - `location-us-california` - US > California
   - `location-europe-uk` - Europe > UK
   - Format: `location-{region}`

### Label Creation

Labels are **automatically created** before use via GitHub API. You don't need to manually create them.

## Monitoring System Health

### Quick Health Check

```bash
# Run the test script
cd /home/runner/work/Chained/Chained
python3 << 'TEST'
import os, json

# Check world tick
with open('world/world_state.json') as f:
    state = json.load(f)
    print(f"World Tick: {state['tick']}")
    print(f"Active Agents: {len([a for a in state['agents'] if a['status'] == 'active'])}")

# Check recent learnings
learnings = [f for f in os.listdir('learnings/') if f.endswith('.json')]
print(f"Learning Files: {len(learnings)}")

# Check open missions
import subprocess
result = subprocess.run(['gh', 'issue', 'list', '--label', 'agent-mission'], 
                       capture_output=True, text=True)
mission_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
print(f"Open Missions: {mission_count}")
TEST
```

### Watch for Issues

🚨 **Red flags:**
- World tick not incrementing
- No new learning files
- No mission issues being created
- Agents stuck at same locations
- Workflow failures

✅ **Good signs:**
- World tick increases every 2 hours
- New learning files appear twice daily
- Mission issues created regularly
- Agents move to new locations
- Issues are closed and PRs merged

## Advanced Usage

### Custom Learning Sources

Add your own learning sources:

1. Create a new workflow in `.github/workflows/learn-from-{source}.yml`
2. Follow the pattern of existing learning workflows
3. Output to `learnings/{source}_{date}.json`
4. The system will automatically:
   - Combine your learning with others
   - Update the world model
   - Create missions

### Agent Performance Tracking

Agent performance is tracked in `.github/agent-system/metrics/`:

```bash
# View agent scores
cat .github/agent-system/registry.json | jq '.agents[] | {id, overall_score}'

# View detailed metrics
ls -la .github/agent-system/metrics/
```

### Extending the System

To add new capabilities:

1. **New agent specialization** - Add to `.github/agent-system/registry.json`
2. **New learning source** - Create new workflow following pattern
3. **New world regions** - Add to `world/world_state.json`
4. **New idea categories** - System auto-discovers from learnings

## Troubleshooting

### Workflow Not Triggering

**Check workflow trigger conditions:**
```bash
# View workflow file
cat .github/workflows/{workflow-name}.yml

# Check recent runs
gh run list --workflow={workflow-name}.yml --limit 5
```

**Manually trigger:**
```bash
gh workflow run {workflow-name}.yml
```

### No Missions Created

**Possible causes:**
- No new learnings in recent cycles
- No ideas with sufficient relevance scores
- All agents already assigned to other missions

**Debug:**
```bash
# Check for recent combined learnings
ls -lt learnings/combined_* | head -3

# Check world update logs
gh run view --log --workflow=world-update.yml

# Check agent missions logs  
gh run view --log --workflow=agent-missions.yml
```

### Agents Not Moving

**Check agent status:**
```bash
cat world/world_state.json | jq '.agents[] | {id, status, location_region_id}'
```

**Verify missions were created:**
```bash
gh issue list --label agent-mission
```

### Labels Not Created

**Check GitHub permissions:**
- Workflow needs `contents: write` and `issues: write` permissions

**Verify label creation step:**
```bash
gh run view --log --workflow=agent-missions.yml | grep "Ensure required labels"
```

## Best Practices

### 1. Let the System Run Autonomously

The system is designed to operate without intervention. Avoid:
- Manually closing mission issues (let agents complete them)
- Deleting learning files (they feed future cycles)
- Modifying world state directly (let workflows update it)

### 2. Monitor, Don't Micromanage

Check system health periodically but let it self-correct:
- Review world tick progression
- Check mission completion rates
- Monitor agent performance trends

### 3. Add Value Through Missions

The best way to help:
- Complete assigned missions
- Create quality artifacts (docs, code, tools)
- Close issues properly (triggers self-reinforcement)

### 4. Trust the Loop

The system learns from everything:
- Completed missions → Self-reinforcement
- Self-reinforcement → Better learnings
- Better learnings → Better missions

## Getting Help

### Documentation
- `docs/AUTONOMOUS_SYSTEM.md` - Complete system documentation
- `docs/SYSTEM_FLOW_GUIDE.md` - Visual guide with diagrams
- This file - Working guide

### Workflow Logs
```bash
# View logs for any workflow
gh run list --workflow={workflow-name}.yml
gh run view {run-id} --log
```

### Ask Meta-Coordinator

The `meta-coordinator` agent specializes in multi-agent coordination and can help understand system behavior.

Look for issues labeled `agent:meta-coordinator` or create one to ask questions about system operation.

---

**Welcome to the autonomous world of Chained! 🌍🤖**

The system is now continuously learning, exploring, and improving itself. Your role is to guide it by completing missions and letting the loop run.
