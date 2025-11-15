# 🌍 Chained World Model

The World Model is a geographic, agent-driven system that visualizes how autonomous AI agents explore ideas derived from real-world tech articles across the globe.

## Overview

**@investigate-champion** has implemented a comprehensive world model that:

- 📍 Maps ideas to real geographic locations based on company headquarters
- 🤖 Tracks autonomous agents as they navigate between inspiration regions
- 💡 Maintains a knowledge base of ideas extracted from articles
- ⏰ Updates every 2 hours through GitHub Actions
- 🗺️ Visualizes everything on an interactive world map

## Architecture

### Data Files

```
world/
├── world_state.json      # Current state of the world
├── knowledge.json        # Database of ideas and regions
├── world_state_manager.py    # State persistence
├── knowledge_manager.py      # Knowledge base operations
└── agent_navigator.py        # Agent movement logic
```

### world_state.json Structure

```json
{
  "time": "2025-11-15T03:26:00Z",
  "tick": 42,
  "agents": [
    {
      "id": "chained-explorer-1",
      "label": "Chained Explorer",
      "location_region_id": "US:San Francisco",
      "status": "exploring",
      "path": ["US:San Francisco", "TW:Hsinchu"],
      "current_idea_id": "idea:123"
    }
  ],
  "regions": [
    {
      "id": "US:San Francisco",
      "label": "San Francisco",
      "lat": 37.7749,
      "lng": -122.4194,
      "idea_count": 12
    }
  ],
  "objectives": [...],
  "metrics": {
    "total_ideas": 22,
    "total_regions": 10,
    "ticks_completed": 42
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

### 2. Agent Update (`scripts/update_agent.py`)

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

### 3. World Map UI (`docs/world-map.html`)

Interactive visualization using Leaflet.js and OpenStreetMap:

- **Regions**: Shown as circles sized by idea count
- **Agents**: Shown as custom markers with current location
- **Sidebar**: Real-time metrics and agent status
- **Popups**: Click regions/agents for detailed information

**View it live:** [https://enufacas.github.io/Chained/world-map.html](https://enufacas.github.io/Chained/world-map.html)

### 4. Automated Updates (`.github/workflows/world-update.yml`)

GitHub Actions workflow that runs every 2 hours:

```yaml
schedule:
  - cron: '0 */2 * * *'
```

**What it does:**
- Runs `update_agent.py` to move agents
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

The world model integrates with:

- **Learning System**: Articles from `learn-from-tldr.yml` can be ingested
- **Agent System**: Agents from `.github/agents/` can be added to the world
- **GitHub Pages**: Map UI integrated into existing dashboard
- **Workflow System**: Automated via GitHub Actions

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

Edit `world/world_state.json`:

```json
{
  "agents": [
    {
      "id": "new-agent-1",
      "label": "New Explorer",
      "location_region_id": "US:Seattle",
      "status": "idle",
      "path": [],
      "current_idea_id": null
    }
  ]
}
```

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

**@investigate-champion** - System design, implementation, and documentation
- Inspired by Ada Lovelace's visionary and analytical approach
- Part of the Chained autonomous AI ecosystem

## Related Documentation

- [Main README](../README.md)
- [Agent System](../AGENT_QUICKSTART.md)
- [GitHub Pages](./INDEX.md)
- [Workflows](../docs/WORKFLOWS.md)

---

*The world builds itself. Welcome to the geographic exploration of autonomous AI.* 🌍🤖
