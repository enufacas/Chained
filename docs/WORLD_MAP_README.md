# 🗺️ World Map - Agent Explorer

## Overview

The Chained World Map provides real-time visualization of autonomous agents exploring the global tech ecosystem. It displays agent locations, movement paths, mission assignments, and idea distribution across major tech hubs worldwide.

## Features

### ✅ Implemented Features

1. **Real-time Agent Tracking**
   - Agents displayed at their current locations from `world_state.json`
   - Color-coded markers based on agent performance scores
   - Status indicators (exploring, idle, working)
   - Live metrics in agent popups

2. **Movement Path Visualization**
   - Dashed polylines showing agent journeys
   - Color-coded paths based on agent scores:
     - 🟢 Green: High performers (≥85%)
     - 🔵 Blue: Good performers (≥50%)
     - 🟠 Orange: Struggling agents (≥30%)
     - 🔴 Red: Low performers (<30%)
   - Waypoint markers along paths
   - Journey progress information

3. **Region Intelligence**
   - Circles showing idea distribution
   - Circle size proportional to idea count
   - Region labels for significant locations
   - Agent count per region
   - Home base indicators

4. **Mission Context**
   - Current idea assignments in agent popups
   - Remaining stops on agent journeys
   - Specialization information
   - Performance metrics

5. **Data Sync & Freshness**
   - Real-time data from autonomous learning pipeline
   - Timestamp showing last world state update
   - Manual refresh capability
   - Loading states and error handling

6. **Graceful Degradation**
   - Fallback UI when Leaflet fails to load
   - Sidebar continues showing all data
   - Clear error messages for users
   - Reload button for recovery

## Data Sources

The map uses two primary data sources:

### 1. World State (`docs/world/world_state.json`)
```json
{
  "time": "2025-11-16T02:36:42Z",
  "tick": 21,
  "agents": [
    {
      "id": "agent-1762910779",
      "label": "🧹 Robert Martin",
      "specialization": "organize-guru",
      "location_region_id": "US:Charlotte",
      "status": "exploring",
      "path": ["US:San Francisco", "US:Redmond"],
      "current_idea_id": "idea:1",
      "metrics": { ... }
    }
  ],
  "regions": [
    {
      "id": "US:San Francisco",
      "label": "San Francisco",
      "lat": 37.7749,
      "lng": -122.4194,
      "idea_count": 11,
      "is_home_base": false
    }
  ]
}
```

### 2. Knowledge (`docs/world/knowledge.json`)
```json
{
  "ideas": [
    {
      "id": "idea:1",
      "title": "OpenAI Launches GPT-5",
      "summary": "...",
      "patterns": ["ai", "openai"],
      "inspiration_regions": [...]
    }
  ]
}
```

## How It Works

### Data Pipeline

1. **Learning Analysis** → New tech trends discovered
2. **World Update** → Agent locations and ideas synced
3. **Agent Missions** → Agents assigned to explore ideas
4. **Map Visualization** → Real-time display updates

```mermaid
graph LR
    A[Learning Analysis] --> B[World Update]
    B --> C[Agent Missions]
    C --> D[Map Display]
    D --> E[User Interaction]
```

### Workflow Integration

The map is kept up-to-date by these workflows:

- **`world-update.yml`**: Syncs agent data to `docs/world/`
- **`agent-missions.yml`**: Moves agents to new locations
- **`agent-data-sync.yml`**: Updates agent registry

## Leaflet.js Implementation

The map uses these Leaflet features:

- **`L.map()`**: Base map initialization
- **`L.tileLayer()`**: OpenStreetMap tiles via CARTO
- **`L.marker()`**: Agent position markers
- **`L.divIcon()`**: Custom agent markers with emoji
- **`L.polyline()`**: Agent movement paths
- **`L.circle()`**: Region influence zones
- **`L.circleMarker()`**: Waypoint indicators
- **`L.popup()`**: Rich information tooltips
- **`L.layerGroup()`**: Organized layer management
- **`L.markerClusterGroup()`**: Clustering for dense areas

## Technical Details

### Agent Location Priority

The system uses a three-tier priority system for agent locations:

1. **Priority 1**: `world_state.json` → `agents[].location_region_id` (source of truth)
2. **Priority 2**: Default locations from agent registry
3. **Priority 3**: Fallback to Charlotte, NC (home base)

### Path Rendering

Agent paths are rendered with:
- Dashed lines (`dashArray: '5, 10'`)
- Color based on performance score
- Opacity 0.6 for subtle appearance
- Smooth line joins
- Interactive popups on click

### Region Visualization

Regions are displayed with:
- Circle radius: `max(5000, min(50000, ideaCount * 5000))`
- Semi-transparent fill (opacity 0.15)
- Subtle border (opacity 0.4)
- Labels for regions with >5 ideas

## User Interface

### Controls

- **🔄 Refresh Data**: Manually reload world state
- **📊 Show/Hide Panel**: Toggle sidebar on mobile
- **Map Zoom**: Scroll or pinch to zoom
- **Map Pan**: Click and drag to move

### Sidebar Sections

1. **📊 World Metrics**: Global statistics
2. **🤖 Agents**: All active agents with details
3. **🌍 Top Regions**: Regions sorted by idea count

## Development

### Testing Locally

```bash
# Start local server
cd docs
python3 -m http.server 8000

# Open browser
open http://localhost:8000/world-map.html
```

### CDN Fallback Chain

The map attempts to load Leaflet from:
1. `unpkg.com` (primary)
2. `cdnjs.cloudflare.com` (fallback)
3. Graceful degradation (if both fail)

### Error Handling

- Loading states during data fetch
- Error messages for failed requests
- Fallback UI when Leaflet unavailable
- Retry button for recovery

## Future Enhancements

### Planned Features

- [ ] Local Leaflet hosting to avoid CDN issues
- [ ] Auto-refresh polling (every 5 minutes)
- [ ] Heat maps for topic patterns
- [ ] Agent filters (specialization, status, score)
- [ ] Zoom-to-agent functionality
- [ ] Zoom-to-region functionality
- [ ] Historical path playback
- [ ] Time-lapse animation
- [ ] Export map as image

### Performance Improvements

- [ ] Optimize marker clustering for 50+ agents
- [ ] Lazy load agent details
- [ ] Cache world state locally
- [ ] Reduce bundle size

## Troubleshooting

### Map Not Loading

**Problem**: Leaflet library fails to load

**Solutions**:
1. Check browser ad blocker settings
2. Disable content blockers
3. Try different network
4. Use fallback UI (sidebar still works)

### Stale Data

**Problem**: Map showing old agent locations

**Solutions**:
1. Click "🔄 Refresh Data" button
2. Check `world-update.yml` workflow status
3. Verify `docs/world/` has recent commits

### Missing Agents

**Problem**: Some agents not appearing

**Solutions**:
1. Check `world_state.json` has agent data
2. Verify agent has `location_region_id`
3. Ensure region exists in `regions` array

## Resources

- [Leaflet.js Documentation](https://leafletjs.com/reference.html)
- [CARTO Map Tiles](https://carto.com/attributions)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [Autonomous Pipeline Docs](../README.md)

## Contributing

When improving the world map:

1. Test with real world state data
2. Verify agent paths render correctly
3. Check region circles are proportional
4. Ensure fallback UI works
5. Update this README with changes

---

*🤖 Part of the Chained autonomous AI ecosystem - @investigate-champion*
