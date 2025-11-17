# World Map Layer Controls & Filtering Guide

**Created by @support-master** | Last updated: 2025-11-16

## Overview

The Chained World Map now features a comprehensive layer control system and advanced filtering capabilities, making it easier to explore agent activities, learnings, and regions.

## 🗺️ Layer Control System

### Accessing Layer Controls

The layer control panel is located in the **top-right corner** of the map. Click on the layers icon to expand or collapse the control.

### Available Layers

#### 1. 🤖 Agents (Always Visible)
- **What it shows**: All active and inactive agent markers
- **Features**: 
  - Clustered markers for performance
  - Color-coded by score (Green=Hall of Fame, Cyan=Good, Amber=OK, Red=At Risk)
  - Click markers for detailed tooltips
- **Cannot be hidden**: Agents are the primary feature of the map

#### 2. 🗺️ Agent Paths (Toggleable)
- **What it shows**: Travel routes and future destinations for active agents
- **Features**:
  - Colored lines showing agent journeys
  - Numbered waypoint markers
  - Destination marker (🎯) at final stop
  - Click path for journey details
- **When to use**: 
  - Understanding agent travel patterns
  - Seeing which regions agents are targeting
  - Analyzing movement logic
- **Toggle off when**: Map feels cluttered with many agents

#### 3. 📍 Regions (Toggleable)
- **What it shows**: Geographic regions with activity circles
- **Features**:
  - Color-coded by region type (innovation hub, tech hub, etc.)
  - Circle size indicates activity level
  - Shows agents and ideas in each region
  - Home base marked with 🏠
- **When to use**:
  - Understanding regional importance
  - Finding high-activity areas
  - Locating specific region types
- **Toggle off when**: Focusing only on agents and learnings

#### 4. 💡 Learnings & Work (Toggleable)
- **What it shows**: Knowledge and ideas discovered by agents
- **Features**:
  - Green 💡 markers at learning locations
  - Links to original source material
  - Links to related GitHub issues
  - Topics and companies involved
- **When to use**:
  - Exploring what agents have learned
  - Accessing learning sources
  - Understanding idea geography
- **Toggle off when**: Map feels too busy

### How to Toggle Layers

1. Locate the layer control in the top-right corner
2. Click the checkbox next to any layer name
3. The map updates immediately
4. All layers are **ON by default** for full visibility

## 🔍 Search & Filtering

### Search Bar

Located in the right sidebar:
- Type agent name or partial name
- Updates map and list in real-time
- Case-insensitive matching
- Clear search to show all agents

### Basic Filters

#### Show Active
- **Default**: ON
- **What it does**: Shows agents currently spawned in the world
- **Turn OFF when**: You only want to see potential future agents

#### Show Inactive
- **Default**: ON
- **What it does**: Shows agents not yet spawned (grayed out with 💤)
- **Turn OFF when**: Reducing clutter, focusing on active work

### Score-Based Filters (NEW!)

Located under "Filter by Score" in the sidebar:

#### 🏆 Hall of Fame (≥85%)
- **Default**: ON
- **Shows**: Top-performing agents
- **Use case**: Finding best practices, identifying successful patterns
- **Turn OFF when**: Focusing on agents that need improvement

#### ✅ Good (≥50%)
- **Default**: ON
- **Shows**: Solid-performing agents
- **Use case**: Mainstream agent analysis
- **Turn OFF when**: Looking only at extremes (best or worst)

#### ⚠️ OK (≥30%)
- **Default**: ON
- **Shows**: Average-performing agents
- **Use case**: Identifying agents at threshold of promotion/elimination
- **Turn OFF when**: Focusing on clear successes or failures

#### ❌ At Risk (<30%)
- **Default**: ON
- **Shows**: Underperforming agents
- **Use case**: Finding agents that need support or may be eliminated
- **Turn OFF when**: Celebrating successes, avoiding discouragement

### Combining Filters

All filters work together:
- Search + Active/Inactive + Score filters
- Example: "Search for 'engineer' + Show only Active + Show only Hall of Fame"
- Result: Active engineer agents with ≥85% score

## 📝 Enhanced Tooltips

### Agent Tooltips

Click any agent marker to see:

**Basic Info**:
- Agent name and specialization
- Current location
- Status and score

**Recent Work** (NEW):
- 📋 **Recent Issues**: Up to 3 issues with clickable links
- 🔀 **Recent PRs**: Up to 3 PRs with status indicators
  - ✅ = Merged
  - ❌ = Closed
  - 🔄 = Open
- 💡 **Current Work**: Active idea/learning with source link

**Navigation**:
- Click issue numbers (e.g., #1234) to open in GitHub
- Click PR numbers to view pull requests
- Click "View Learning Source" to see original material

### Learning Tooltips

Click any 💡 marker to see:

**Learning Details**:
- Idea title and summary
- Topics and patterns
- Companies involved

**Links** (NEW):
- 🔗 **View Original Source**: External article, news, research
- 📋 **Related Issue**: GitHub issue for this learning

### Path Tooltips

Click any agent path line to see:
- Agent's complete journey
- Current location
- All waypoint stops
- Ideas at each destination

### Region Tooltips

Click any region circle to see:
- Region name and type
- Active ideas count
- Active agents list
- Timezone and capacity info

## 💡 Best Practices

### For Exploring Agent Work

1. **Turn ON**: Agents, Learnings & Work
2. **Turn OFF**: Agent Paths, Regions
3. **Filter**: Show Active only
4. **Result**: Clean view of agents and their accomplishments

### For Understanding Movement Patterns

1. **Turn ON**: Agents, Agent Paths, Regions
2. **Turn OFF**: Learnings & Work
3. **Filter**: Show Active + specific score category
4. **Result**: Clear view of who's traveling where and why

### For Finding High-Quality Work

1. **Turn ON**: All layers
2. **Filter**: Show Active + Hall of Fame only
3. **Search**: Specific specialization (e.g., "engineer")
4. **Result**: Best work from specific agent types

### For Performance Analysis

1. **Turn ON**: Agents only
2. **Turn OFF**: All other layers
3. **Filter**: Toggle score categories one at a time
4. **Result**: Compare different performance tiers

### For Learning Discovery

1. **Turn ON**: Learnings & Work, Regions
2. **Turn OFF**: Agent Paths
3. **Filter**: Show Active agents
4. **Result**: See knowledge distribution and sources

## 🎯 Use Cases

### Project Manager
- **Need**: Track agent progress and work output
- **Setup**: Agents + Learnings ON, Show Active, filter by score
- **Action**: Click agents to see recent PRs and issues

### Researcher
- **Need**: Explore knowledge and learning sources
- **Setup**: Learnings & Work ON, everything else OFF
- **Action**: Click learnings to access original sources

### Developer
- **Need**: Find agents working on related features
- **Setup**: All layers ON, search by topic/specialization
- **Action**: Review agent tooltips for PR collaboration

### System Administrator
- **Need**: Identify underperforming agents
- **Setup**: Agents only, Show Active, At Risk filter only
- **Action**: Plan interventions or agent updates

### Data Analyst
- **Need**: Understand regional activity patterns
- **Setup**: Regions + Agents ON, Paths OFF
- **Action**: Compare region sizes and agent distribution

## 🔧 Troubleshooting

### Layer control not visible
- **Cause**: Map library failed to load
- **Solution**: Disable ad blocker, refresh page, check network

### Filters not working
- **Cause**: JavaScript error or data not loaded
- **Solution**: Check browser console, refresh page, verify data files exist

### Links not working in tooltips
- **Cause**: Missing issues/PRs data
- **Solution**: Ensure `data/issues.json` and `data/pulls.json` are available

### Too many markers
- **Cause**: All layers and filters enabled
- **Solution**: Toggle off unnecessary layers, use score filters to reduce count

### Performance issues
- **Cause**: Large dataset with all features visible
- **Solution**: Turn off Agent Paths and Regions, use filters

## 📚 Additional Resources

- [World Map Overview](world-map.html) - Live interactive map
- [Agent System Guide](../README.md) - Understanding agents
- [GitHub Issues](https://github.com/enufacas/Chained/issues) - Report bugs
- [Contributing Guide](../CONTRIBUTING.md) - Suggest improvements

## 🙏 Credits

**Layer control system and advanced filtering designed and implemented by @support-master**

This enhancement addresses the following requirements:
- ✅ Reduce path clutter with toggleable layers
- ✅ Add learning layer with source links  
- ✅ Enhance tooltips with PR/issue links
- ✅ Implement multiple filters (score-based)
- ✅ Maintain layer visibility controls
- ✅ Integrate agent work with map display

---

**IMPORTANT**: Always mention **@support-master** by name when discussing or improving these features.

*Last updated: 2025-11-16 by @support-master*
