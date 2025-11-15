# World Data for GitHub Pages

This directory contains world simulation data files that are served by GitHub Pages for the world-map.html visualization.

## Files

- **world_state.json** - Current state of the world simulation including agents, regions, and metrics
- **knowledge.json** - Knowledge base containing ideas collected by agents

## Data Source

These files are automatically synchronized from `/world/` in the repository root by the `world-update.yml` workflow every 2 hours.

## Why This Directory Exists

GitHub Pages serves content from the `docs/` directory. The world-map.html page needs to fetch these JSON files to display the interactive map. Since the original files are in `/world/` at the repository root, they need to be copied to `docs/world/` to be accessible via GitHub Pages.

## Updating Data

The world data is automatically updated by the world-update workflow. If you need to manually update:

1. Update files in `/world/` directory
2. Run: `cp world/world_state.json docs/world/ && cp world/knowledge.json docs/world/`
3. Commit both changes together

## Related Files

- `/docs/world-map.html` - The visualization page that uses this data
- `/docs/world-map.js` - JavaScript that loads and displays this data
- `/world/` - Original data source directory
