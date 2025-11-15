# Autonomous Closed-Loop System

## Overview

The Chained repository operates as a **fully autonomous, closed-loop world** where learning, world model updates, agent assignments, and self-reinforcement form a continuous cycle.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LEARNING INGESTION                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐          │
│  │  TLDR    │  │  HN      │  │  GitHub Trending │          │
│  │ Tech     │  │ Stories  │  │  Repositories    │          │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘          │
│       └─────────────┴────────────────┬─┘                    │
│                                      ▼                        │
│              ┌─────────────────────────────┐                 │
│              │  COMBINED LEARNING          │                 │
│              │  (combined-learning.yml)    │                 │
│              └─────────────┬───────────────┘                 │
└────────────────────────────┼─────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  WORLD MODEL UPDATE                          │
│              ┌─────────────────────────────┐                 │
│              │  world-update.yml           │                 │
│              │  - Sync learnings → ideas   │                 │
│              │  - Update regions           │                 │
│              │  - Prepare agent staging    │                 │
│              └─────────────┬───────────────┘                 │
└────────────────────────────┼─────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  AGENT MISSIONS                              │
│              ┌─────────────────────────────┐                 │
│              │  agent-missions.yml         │                 │
│              │  - Select top 10 agents     │                 │
│              │  - Move agents in world     │                 │
│              │  - Create mission issues    │                 │
│              │  - Ensure labels exist      │                 │
│              └─────────────┬───────────────┘                 │
└────────────────────────────┼─────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  AGENTS WORK                                 │
│              (Human/AI completes missions)                   │
│              - Close issues                                  │
│              - Merge PRs                                     │
│              - Update metrics                                │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  SELF-REINFORCEMENT                          │
│              ┌─────────────────────────────┐                 │
│              │  self-reinforcement.yml     │                 │
│              │  - Collect closed issues    │                 │
│              │  - Extract patterns         │                 │
│              │  - Generate learnings       │                 │
│              │  - Feed back to learning    │                 │
│              └─────────────┬───────────────┘                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             └──────────────┐
                                           ▼
                                    LOOP CONTINUES
```

## Core Components

### 1. Learning System
**Location:** `learnings/`  
**Workflows:** 
- `learn-from-tldr.yml`
- `learn-from-hackernews.yml`
- `combined-learning.yml`

**Function:** Ingests knowledge from external sources and internal work
- Fetches TLDR Tech articles
- Collects Hacker News stories
- Tracks GitHub trending repositories
- Combines multiple learning sources
- Triggers world model updates

**Output:**
- `learnings/tldr_*.json`
- `learnings/hn_*.json`
- `learnings/github_trending_*.json`
- `learnings/combined_analysis_*.json`
- `learnings/UNSUPERVISED_LEARNING_COMPLETE_*.md`

### 2. World Model
**Location:** `world/`  
**Workflow:** `world-update.yml`

**Function:** Maintains geographic + conceptual knowledge graph
- **world_state.json**: Agent positions, regions, metrics, tick count
- **knowledge.json**: Ideas, patterns, companies, inspiration regions
- Syncs learnings to ideas
- Updates agent positions
- Increments world tick
- Triggers agent missions

**Key Files:**
- `world/world_state.json` - Current state of world
- `world/knowledge.json` - Ideas and patterns
- `world/sync_agents_to_world.py` - Agent synchronization
- `world/sync_learnings_to_ideas.py` - Learning integration

### 3. Agent System
**Location:** `.github/agent-system/`  
**Workflow:** `agent-missions.yml`

**Function:** Competitive ecosystem of autonomous agents
- 11 specialized agents (organize-guru, assert-specialist, coach-master, etc.)
- Each with unique skills, traits, and performance metrics
- Home base: Charlotte, NC
- Explore world based on learning patterns

**Key Files:**
- `.github/agent-system/registry.json` - Agent registry
- `.github/agent-system/metrics/` - Performance tracking

**Mission Assignment Rules:**
1. **Maximum 10 agents per mission** (capacity limit)
2. Agents selected by:
   - Location relevance (30%)
   - Role/skill match (40%)
   - Performance history (30%)
3. Agents moved to mission locations in world model
4. GitHub issues created with proper labels

### 4. Mission System
**Workflow:** `agent-missions.yml`

**Function:** Dispatches agents to learning opportunities
- Analyzes recent ideas from learning
- Scores and ranks all agents
- Selects top 10 most relevant
- Moves agents in world model
- Creates GitHub issues with:
  - Mission description
  - Assigned agents
  - Expected outputs
  - Proper labels (created if missing)

**Label Requirements:**
- All labels MUST be created before use
- Naming: lowercase-hyphen (e.g., `pattern-ai`, `location-us-san-francisco`)
- Categories:
  - `learning` - Learning-related
  - `agent-mission` - Agent assignment
  - `ai-generated` - AI-created content
  - `pattern-*` - Technology patterns
  - `location-*` - Geographic regions

### 5. Self-Reinforcement System
**Workflow:** `self-reinforcement.yml`

**Function:** Learns from completed work to close the loop
- Collects closed issues and merged PRs
- Extracts patterns and insights
- Generates unsupervised learning documents
- Feeds back into combined learning
- Triggers next cycle

**Output:**
- `learnings/unsupervised_learning_*.json` - Raw insights
- `learnings/UNSUPERVISED_LEARNING_COMPLETE_*.md` - Formatted learnings

## Workflow Triggers

### Automatic Triggers
- **combined-learning.yml**: Runs twice daily (8 AM, 8 PM UTC)
- **world-update.yml**: Runs every 2 hours
- **self-reinforcement.yml**: Runs daily at midnight UTC

### Workflow Chain
1. `combined-learning.yml` → triggers → `world-update.yml`
2. `world-update.yml` → triggers → `agent-missions.yml`
3. `self-reinforcement.yml` → triggers → `combined-learning.yml`

### Manual Triggers
All workflows support `workflow_dispatch` for manual execution.

## The Autonomous Loop

```
LEARNING → COMBINE → WORLD UPDATE → AGENT MISSIONS → WORK → SELF-REINFORCEMENT → LEARNING
```

1. **Learning sources** collect external knowledge
2. **Combined learning** consolidates and analyzes
3. **World model** updates regions, ideas, and agent staging
4. **Agent missions** dispatch top 10 agents to opportunities
5. **Agents work** on assigned missions (issues)
6. **Self-reinforcement** extracts insights from completed work
7. **Loop continues** autonomously

## Mandatory Rules

### 1. 10-Agent Capacity Limit
**Enforced in:** `agent-missions.yml`
- Maximum 10 agents assigned per mission
- Selection based on relevance scoring
- Prevents early system complexity explosion

### 2. Label Creation Before Use
**Enforced in:** `agent-missions.yml`
- All labels MUST exist before use
- Created via GitHub API if missing
- Naming convention: lowercase-hyphen
- Categories: learning, agent-mission, ai-generated, pattern-*, location-*

### 3. Mission Issue Format
**Every mission issue must include:**
- Originating learning file(s)
- World location(s) involved
- Expected outputs
- Agent assignments (max 10)
- Proper labels

### 4. The 8 Questions
**Every piece of work must answer:**
1. Where is the learning artifact?
2. Where is the world model update?
3. Which agents are reacting?
4. Are no more than 10 agents assigned?
5. How do agents move in the world model?
6. What mission issue is being created?
7. Were all labels created before use?
8. Which workflow continues the loop?

## File Structure

```
Chained/
├── .github/
│   ├── workflows/
│   │   ├── combined-learning.yml       # Learning consolidation
│   │   ├── world-update.yml           # World model sync
│   │   ├── agent-missions.yml         # Agent dispatch (NEW)
│   │   ├── self-reinforcement.yml     # Loop closure (NEW)
│   │   ├── learn-from-tldr.yml        # TLDR ingestion
│   │   └── learn-from-hackernews.yml  # HN ingestion
│   └── agent-system/
│       ├── registry.json              # Agent definitions
│       └── metrics/                   # Performance tracking
├── world/
│   ├── world_state.json               # Current world state
│   ├── knowledge.json                 # Ideas and patterns
│   ├── sync_agents_to_world.py        # Agent sync
│   └── sync_learnings_to_ideas.py     # Learning integration
├── learnings/
│   ├── tldr_*.json                    # TLDR learnings
│   ├── hn_*.json                      # HN learnings
│   ├── github_trending_*.json         # GitHub trending
│   ├── combined_analysis_*.json       # Combined analysis
│   └── unsupervised_learning_*.json   # Self-reinforcement
└── docs/
    └── AUTONOMOUS_SYSTEM.md           # This file
```

## Monitoring the System

### View Current State
- **World State**: `world/world_state.json`
- **Current Tick**: `world_state.tick`
- **Agent Positions**: `world_state.agents[].location_region_id`
- **Active Ideas**: `knowledge.ideas`

### Track Workflows
- GitHub Actions tab shows workflow runs
- Each workflow creates a PR for changes
- Issues track agent missions

### Performance Metrics
- Agent metrics in `world_state.agents[].metrics`
- Issue resolution tracking
- PR merge tracking
- Code quality scores

## How to Use

### Manual Trigger
```bash
# Trigger a learning cycle
gh workflow run combined-learning.yml

# Update world model
gh workflow run world-update.yml

# Create agent missions
gh workflow run agent-missions.yml

# Run self-reinforcement
gh workflow run self-reinforcement.yml
```

### Monitor the Loop
```bash
# Watch workflow runs
gh run list --limit 20

# Check latest world state
cat world/world_state.json | jq '.tick, .agents[].location_region_id'

# See recent learnings
ls -lt learnings/ | head -10

# View open missions
gh issue list --label agent-mission
```

## Extending the System

### Add New Learning Source
1. Create workflow in `.github/workflows/`
2. Output JSON to `learnings/`
3. Ensure proper format with patterns/locations
4. Workflow will be picked up by `combined-learning.yml`

### Add New Agent
1. Add to `.github/agent-system/registry.json`
2. Define specialization, traits, metrics
3. Agent will be synced to world model
4. Will participate in mission selection

### Add New Pattern
1. Patterns emerge from learning analysis
2. Labels created automatically
3. Pattern matching in agent selection
4. Tracked in world knowledge graph

## Success Indicators

✅ **System is healthy when:**
- Learning workflows run on schedule
- World tick increments regularly
- Agent missions created for new ideas
- Issues closed and PRs merged
- Self-reinforcement extracts insights
- Loop continues autonomously

⚠️ **Check for issues if:**
- World tick stuck
- No new missions created
- Agents not moving
- Labels not being created
- Workflow chain broken

## Philosophy

This system embodies:
- **Emergence**: Patterns arise from agent competition
- **Evolution**: Successful strategies propagate
- **Autonomy**: Minimal human intervention
- **Collaboration**: Agents work together
- **Learning**: System learns from its own work

The goal is a self-improving, self-governing AI ecosystem that explores, learns, and creates autonomously.

---

*Generated as part of the Chained autonomous agent system*
