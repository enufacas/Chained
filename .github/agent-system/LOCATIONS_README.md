# Agent System Locations

## Overview

The `locations.json` file serves as the **single source of truth** for all agent specialization locations in the Chained autonomous AI ecosystem.

## Purpose

- **Unified Data Source**: All agent location data is centralized here
- **Consistency**: Ensures all systems (world map, dashboards, etc.) use the same location data
- **Easy Maintenance**: Update agent locations in one place
- **Regional Distribution**: Agents are distributed globally across major tech hubs

## Structure

```json
{
  "version": "1.0.0",
  "locations": {
    "agent-specialization": {
      "lat": <latitude>,
      "lng": <longitude>,
      "city": "<City, Region/Country>",
      "region": "<Continental Region>"
    }
  }
}
```

## Regional Distribution

Agents are distributed across 5 major regions:
- **North America**: 24 agent types (San Francisco, Seattle, New York, etc.)
- **Europe**: 9 agent types (London, Paris, Stockholm, etc.)
- **Asia**: 9 agent types (Tokyo, Seoul, Beijing, Bangalore, etc.)
- **South America**: 2 agent types (São Paulo, Rio de Janeiro)
- **Oceania**: 2 agent types (Sydney, Melbourne)

## Usage

### In World Map (docs/world-map.js)

The world map should load locations from this file to ensure consistency:

```javascript
// Load locations from unified source
fetch('.github/agent-system/locations.json')
  .then(response => response.json())
  .then(data => {
    const locations = data.locations;
    // Use locations...
  });
```

### In Agent Registry

When spawning new agents or updating registry data, reference this file for location assignments.

## Maintenance

When adding a new agent specialization:
1. Add entry to `locations.json` with appropriate coordinates
2. Choose a tech hub city that makes sense for the specialization
3. Assign to one of the 5 regions
4. Ensure all consuming systems are updated

## Location Selection Criteria

Locations were chosen based on:
- **Tech Hub Significance**: Major technology centers worldwide
- **Specialization Alignment**: Security agents near major security companies, etc.
- **Geographic Diversity**: Spread across all inhabited continents
- **Cultural Representation**: Include cities from different regions and cultures

## Synced With

This file is the master source for:
- `docs/world-map.js` - Visual world map display
- `docs/data/agent-registry.json` - Agent metadata
- Future: Real-time agent tracking systems

## Version History

- **1.0.0** (2025-11-16): Initial unified location database created
  - Extracted from docs/world-map.js
  - Added all 45 agent specializations
  - Added regional categorization
