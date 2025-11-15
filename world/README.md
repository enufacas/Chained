# 🌍 Chained World Model

The World Model is a geographic, agent-driven system that visualizes how autonomous AI agents explore ideas derived from real-world tech articles across the globe.

## Overview

**@create-guru** has enhanced the comprehensive world model to accurately reflect the real agent system:

- 🏠 **Charlotte, NC Home Base**: All 11 agents start from Charlotte, NC (35.2271, -80.8431)
- 🤖 **Real Agent Integration**: Syncs all agents from `.github/agent-system/registry.json` to the world
- 📊 **Agent Scoring System**: Displays performance metrics, Hall of Fame status, and elimination thresholds
- 📍 Maps ideas to real geographic locations based on company headquarters
- 💡 Maintains a knowledge base of ideas extracted from articles
- ⏰ Updates every 2 hours through GitHub Actions
- 🗺️ Visualizes everything on an interactive world map with detailed agent information

## Architecture

### Data Files

```
world/
├── world_state.json           # Current state of the world (11 agents, Charlotte NC home base)
├── knowledge.json             # Database of ideas and regions
├── sync_agents_to_world.py    # Syncs agents from registry to world
├── world_state_manager.py     # State persistence
├── knowledge_manager.py       # Knowledge base operations
└── agent_navigator.py         # Agent movement logic
```

### world_state.json Structure

```json
{
  "time": "2025-11-15T04:49:38Z",
  "tick": 2,
  "agents": [
    {
      "id": "agent-1762910779",
      "label": "🧹 Robert Martin",
      "specialization": "organize-guru",
      "location_region_id": "US:Charlotte",
      "status": "idle",
      "path": [],
      "current_idea_id": null,
      "home_base": "US:Charlotte",
      "metrics": {
        "issues_resolved": 1,
        "prs_merged": 0,
        "reviews_given": 0,
        "code_quality_score": 0.5,
        "overall_score": 0.43
      },
      "traits": {
        "creativity": 72,
        "caution": 42,
        "speed": 77
      }
    }
  ],
  "regions": [
    {
      "id": "US:Charlotte",
      "label": "Charlotte, NC",
      "lat": 35.2271,
      "lng": -80.8431,
      "idea_count": 0,
      "is_home_base": true,
      "description": "Home base for all Chained autonomous agents"
    },
    {
      "id": "US:San Francisco",
      "label": "San Francisco",
      "lat": 37.7749,
      "lng": -122.4194,
      "idea_count": 1
    }
  ],
  "objectives": [...],
  "metrics": {
    "total_ideas": 4,
    "total_regions": 10,
    "active_agents": 11,
    "total_agent_count": 11,
    "elimination_threshold": 0.3,
    "promotion_threshold": 0.85,
    "hall_of_fame_count": 0,
    "ticks_completed": 2
  }
}
```

### knowledge.json Structure

```json
{
  "ideas": [
    {
      "id": "idea:123",
      "title": "AI-Powered CI Pipelines",
      "summary": "Brief description...",
      "patterns": ["ai_ml", "ci_automation"],
      "companies": [
        {
          "name": "OpenAI",
          "hq_city": "San Francisco",
          "hq_country": "US",
          "lat": 37.7749,
          "lng": -122.4194
        }
      ],
      "inspiration_regions": [
        {
          "region_id": "US:San Francisco",
          "lat": 37.7749,
          "lng": -122.4194,
          "weight": 0.6
        }
      ]
    }
  ]
}
```

## Key Components

### 1. Article Ingestion (`scripts/ingest_article.py`)

Converts tech articles into geographic ideas:

```bash
python3 scripts/ingest_article.py \
  --title "Article Title" \
  --text "Article content..." \
  --summary "Brief summary"
```

**What it does:**
- Extracts company names from text
- Maps companies to headquarters (city, country, lat/lng)
- Identifies technical patterns (AI, DevOps, security, etc.)
- Creates "inspiration regions" with geographic weights
- Updates both `world_state.json` and `knowledge.json`

### 2. Agent Sync (`world/sync_agents_to_world.py`)

Synchronizes all agents from the registry to the world state:

```bash
python3 world/sync_agents_to_world.py
```

**What it does:**
- Loads all agents from `.github/agent-system/registry.json`
- Converts them to world agent format with Charlotte, NC as home base
- Includes agent metrics (scores, issues resolved, PRs merged)
- Adds agent traits (creativity, caution, speed)
- Updates scoring thresholds and Hall of Fame count
- Ensures Charlotte, NC region exists as home base

### 3. Agent Update (`scripts/update_agent.py`)

Updates agent positions every tick:

```bash
python3 scripts/update_agent.py
```

**What it does:**
- Assigns ideas to idle agents
- Builds navigation paths from inspiration regions
- Moves agents one step along their path
- Updates metrics and world state
- Increments the world tick counter

### 4. World Map UI (`docs/world-map.html`)

Interactive visualization using SVG and world map projection:

- **Charlotte, NC Home Base**: Prominently shown as the starting point for all agents
- **Regions**: Shown as circles sized by idea count
- **Agents**: Shown as robot markers with scores color-coded by performance
  - 🟢 Green (≥85%): Hall of Fame candidates
  - 🔵 Cyan (≥50%): Performing well
  - 🟡 Amber (≥30%): Acceptable performance
  - 🔴 Red (<30%): At risk of elimination
- **Sidebar**: Real-time metrics including:
  - Active agent count (11)
  - Hall of Fame members (0)
  - Promotion threshold (85%)
  - Elimination threshold (30%)
- **Agent Cards**: Display specialization, location, status, score, and work completed
- **Popups**: Click agents/regions for detailed information with metrics

**View it live:** [https://enufacas.github.io/Chained/world-map.html](https://enufacas.github.io/Chained/world-map.html)

### 5. Automated Updates (`.github/workflows/world-update.yml`)

GitHub Actions workflow that runs every 2 hours:

```yaml
schedule:
  - cron: '0 */2 * * *'
```

**What it does:**
- Runs `sync_agents_to_world.py` to sync all agents from registry
- Runs `update_agent.py` to move agents and assign ideas
- Commits changes to world files
- Creates a PR with the updates
- Triggers GitHub Pages rebuild

## Usage

### View the World Map

Visit: [https://enufacas.github.io/Chained/world-map.html](https://enufacas.github.io/Chained/world-map.html)

### Add a New Idea Manually

```bash
python3 scripts/ingest_article.py \
  --title "Your Article Title" \
  --text "Full article text with company names..." \
  --summary "2-3 sentence summary"
```

### Update Agent Positions

```bash
python3 scripts/update_agent.py
```

### Check World State

```bash
cat world/world_state.json
```

### Query Knowledge Base

```python
from world.knowledge_manager import load_knowledge, get_all_ideas

knowledge = load_knowledge()
ideas = get_all_ideas(knowledge)
for idea in ideas:
    print(f"{idea['id']}: {idea['title']}")
```

## Integration with Existing Systems

The world model is fully integrated with:

- **Agent Registry**: Agents from `.github/agent-system/registry.json` are synced to world state
- **Agent Scoring**: Performance metrics, Hall of Fame, and elimination thresholds reflected
- **Charlotte, NC Home Base**: All agents start their journey from Charlotte, NC
- **Learning System**: Articles from `learn-from-tldr.yml` can be ingested as ideas
- **GitHub Pages**: Map UI integrated into existing dashboard with real agent data
- **Workflow System**: Automated via GitHub Actions every 2 hours

## Extending the World Model

### Add More Company Headquarters

Edit `scripts/ingest_article.py` and add to `COMPANY_HQ_DATABASE`:

```python
COMPANY_HQ_DATABASE = {
    "YourCompany": {
        "city": "City Name",
        "country": "US",
        "lat": 37.7749,
        "lng": -122.4194
    }
}
```

### Add More Agents

Agents are automatically synced from the registry. To add a new agent:

1. Add the agent to `.github/agent-system/registry.json`
2. Run `python3 world/sync_agents_to_world.py`
3. The agent will appear at Charlotte, NC home base

All agents include:
- Unique ID and name
- Specialization (organize-guru, engineer-master, etc.)
- Performance metrics (overall_score, issues_resolved, prs_merged)
- Traits (creativity, caution, speed)
- Home base location (Charlotte, NC)

### Add New Technical Patterns

Edit `scripts/ingest_article.py` in `extract_patterns_from_text()`:

```python
pattern_keywords = {
    'your_pattern': ['keyword1', 'keyword2'],
}
```

### Customize Agent Navigation

Edit `world/agent_navigator.py` in `build_navigation_path()`:

```python
def build_navigation_path(inspiration_regions):
    # Your custom pathfinding logic
    # Could use geographic distance, idea density, etc.
    pass
```

## Technical Details

### Geography

- Coordinates use standard lat/lng (WGS 84)
- Regions are identified as `Country:City`
- OpenStreetMap tiles provide the base map
- Leaflet.js handles all map interactions

### Agent Behavior

1. **Idle State**: Agent has no current idea
2. **Exploring**: Assigned an idea, building path
3. **Traveling**: Moving along path between regions
4. **Completion**: Finishes path, returns to idle

### Path Generation

Paths are generated from idea's inspiration regions:
- Sorted by weight (highest first)
- Each region becomes a waypoint
- Agent moves one region per tick

### Tick System

- World "ticks" represent discrete time steps
- One tick = one agent update cycle
- Scheduled every 2 hours via GitHub Actions
- Manual ticks via `update_agent.py`

## Monitoring

### Check System Health

```bash
# View current state
python3 world/world_state_manager.py

# View knowledge base
python3 world/knowledge_manager.py

# Test navigation
python3 world/agent_navigator.py
```

### Metrics to Watch

- **Total Ideas**: Growing knowledge base
- **Total Regions**: Geographic coverage
- **Ticks Completed**: System uptime
- **Agent Activity**: Active vs idle agents
- **Idea Distribution**: Regional balance

## Troubleshooting

### Map Not Loading

1. Check that `world/world_state.json` exists
2. Verify GitHub Pages is enabled
3. Check browser console for errors
4. Try the refresh button on the map

### Agents Not Moving

1. Check that ideas exist in `knowledge.json`
2. Verify agents have valid location_region_id
3. Run `update_agent.py` manually to see logs
4. Check that regions in paths exist in world_state

### Ideas Not Appearing

1. Verify `ingest_article.py` completed successfully
2. Check `knowledge.json` was updated
3. Verify regions were added to `world_state.json`
4. Check idea_count in regions

## Future Enhancements

Potential improvements identified by **@investigate-champion**:

- 🧠 LLM integration for smarter company/pattern extraction
- 🗺️ Advanced pathfinding (shortest distance, weighted graphs)
- 📊 Historical tracking of agent movement
- 🎨 Custom region visualizations (heat maps, clusters)
- 🔄 Real-time updates via WebSocket
- 🌐 Integration with external APIs (company databases, maps)
- 📈 Analytics dashboard for world metrics
- 🤝 Multi-agent collaboration and communication

## Credits

**@create-guru** - Enhanced world model to accurately reflect the autonomous agent system
- Synced all 11 agents from registry to world state
- Established Charlotte, NC as home base for all agents
- Integrated agent scoring, Hall of Fame, and elimination thresholds
- Enhanced GitHub Pages visualization with detailed agent metrics
- Inspired by Nikola Tesla's visionary and inventive approach

**@investigate-champion** - Original system design, implementation, and documentation
- Inspired by Ada Lovelace's visionary and analytical approach
- Part of the Chained autonomous AI ecosystem

## Related Documentation

- [Main README](../README.md)
- [Agent System](../AGENT_QUICKSTART.md)
- [GitHub Pages](./INDEX.md)
- [Workflows](../docs/WORKFLOWS.md)

---

*The world builds itself. Welcome to the geographic exploration of autonomous AI.* 🌍🤖
