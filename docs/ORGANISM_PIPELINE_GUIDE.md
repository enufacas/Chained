# Organism Page - 3D Pipeline Visualization Guide

## Overview

The **Digital Organism Command Center** now features a powerful 3D Pipeline Visualization mode that transforms workflow run data into an interactive, navigable 3D grid layout. This guide explains how to use the new features.

## Dual View Modes

The organism page operates in two distinct modes:

### 1. **Agents View** (Original)
- Displays agents as spheres/humanoids orbiting a central lifecycle core
- Shows agent status (working/exploring), metrics, and specializations
- Mission portals appear as cyberpunk-style objects
- Best for: Monitoring agent activity and status

### 2. **Pipeline View** (New)
- Displays recent workflow runs as a 3D pipeline grid
- Shows agents, PRs, issues, and missions as distinct objects
- Organized by workflow type in horizontal lanes
- Best for: Understanding workflow execution and GitHub activity

## Switching Between Modes

Click the **"Mode: Agents"** or **"Mode: Pipeline"** button in the control panel to toggle.

The camera automatically repositions for optimal viewing of each mode.

## Pipeline View Layout

### Visual Objects

#### 🔴🟢🟡 **Workflow Runs** (Horizontal Cylinders)
- **Position**: Center of each lane, arranged left to right by time
- **Color**: 
  - 🟢 Green = Success
  - 🔴 Red = Failure
  - 🟡 Yellow = In Progress
  - ⚫ Gray = Other states
- **Animation**: Pulsing glow effect
- **Click**: Opens GitHub Actions run page

#### 🔵 **Agent Markers** (Small Spheres)
- **Position**: Floating above workflow runs
- **Color**: Matches agent specialization
  - Cyan = Organization
  - Green = Testing
  - Red = Security
  - Yellow = Performance
  - Magenta = Creation
  - Purple = Analysis
  - Teal = Integration
  - Orange = Coaching
  - Blue = CI/CD & Infrastructure
  - Pink = Innovation
- **Animation**: Constant rotation
- **Purpose**: Shows which agent executed the run

#### 💜 **Mission Crystals** (Icosahedrons)
- **Position**: Floating in upper layer, arranged in a circle
- **Color**: Purple with high glow
- **Animation**: Dual-axis rotation + floating motion
- **Click**: Opens mission detail modal

#### 💗 **PR Markers** (Octahedrons)
- **Position**: Below workflow runs (up to 3 per run)
- **Color**: Pink/Magenta
- **Animation**: Multi-axis rotation
- **Click**: Opens pull request page on GitHub

#### 🔷 **Issue Markers** (Tetrahedrons)
- **Position**: Below workflow runs and PRs
- **Color**: Cyan
- **Animation**: Y-axis rotation
- **Click**: Opens issue page on GitHub

### Lane Organization

Workflow runs are organized into horizontal lanes by workflow type:

```
workflow-1.yml: [Run A] [Run B] [Run C] ...
workflow-2.yml: [Run D] [Run E] [Run F] ...
workflow-3.yml: [Run G] [Run H] [Run I] ...
```

Each lane is labeled on the left side with the workflow name.

## Filter Panel

The filter panel appears when in Pipeline view (bottom left of screen).

### Filter Options

1. **Agent Filter**
   - Select a specific agent to view only their work
   - Options populated from available agentops data
   - Default: "All Agents"

2. **Status Filter**
   - Success: Show only successful runs
   - Failure: Show only failed runs
   - In Progress: Show only running workflows
   - Default: "All Status"

3. **Workflow Filter**
   - Select specific workflow type
   - Options auto-populated from your runs
   - Default: "All Workflows"

4. **Type Filter**
   - Workflow Runs: Show only run objects
   - Missions: Show only mission crystals
   - Pull Requests: Show only PR markers
   - Issues: Show only issue markers
   - Default: "All Types"

### Applying Filters

1. Select your desired filters from dropdowns
2. Click **"APPLY FILTERS"** button
3. Pipeline visualizes with only matching objects
4. Click "APPLY FILTERS" again after changing filters

## Interaction Guide

### Mouse Controls

- **Left Click + Drag**: Rotate camera around scene
- **Right Click + Drag**: Pan camera
- **Scroll Wheel**: Zoom in/out
- **Click Object**: Interact with object (see below)

### Object Interactions

| Object Type | Click Action |
|------------|--------------|
| Workflow Run | Opens GitHub Actions run page in new tab |
| PR Marker | Opens pull request on GitHub in new tab |
| Issue Marker | Opens issue on GitHub in new tab |
| Mission Crystal | Shows mission detail modal overlay |
| Agent Marker | (Future: could show agent detail) |

### Control Panel Buttons

- **Mode**: Toggle between Agents ↔ Pipeline
- **Reset View**: Reposition camera to default angle
- **Bloom**: Toggle glow effects on/off
- **Helpers**: Show/hide grid and axis helpers
- **Connections**: Show/hide connection lines (Agents view)
- **Speed Slider**: Control animation speed (0.1x to 3x)

## Understanding the Visualization

### Reading the Pipeline

**Left to Right** = Time progression (oldest → newest)

**Top to Bottom** = Different workflows

**Vertical Stack** = Related objects
- Agent above run = Agent executed this run
- PR below run = Run created/updated this PR
- Issue below PR = Run addressed this issue

### Color Meanings

| Color | Meaning |
|-------|---------|
| 🟢 Green | Success/Working |
| 🔴 Red | Failure/Error |
| 🟡 Yellow | In Progress/Exploring |
| 🔵 Cyan | Info/Issue/Agent (varies) |
| 💜 Purple | Mission/Strategic |
| 💗 Pink | PR/Contribution |
| ⚫ Gray | Inactive/Other |

### Animation Cues

- **Pulsing**: Active or important status
- **Rotating**: Interactive object
- **Floating**: Mission or high-priority item

## Data Sources

The pipeline visualization uses these data files:

- `data/agentops-runs.json` - Workflow execution history
- `data/mission-reports.json` - Strategic missions
- `data/issues.json` - Issue tracking
- `data/pulls.json` - Pull request data

Data is loaded on page load. Refresh the page to see latest data.

## Tips and Tricks

### Finding Specific Work

1. Use **Agent Filter** to see one agent's work
2. Use **Workflow Filter** to see one workflow type
3. Use **Status Filter** to find failures quickly
4. Combine filters for precise views

### Understanding Agent Contributions

1. Look for agent spheres above runs
2. Same-colored spheres = same agent
3. Multiple spheres in a lane = active agent
4. Click runs to see full GitHub details

### Exploring Missions

1. Switch to Pipeline mode
2. Look for floating purple crystals above
3. Click crystal to see mission details
4. Or use Type Filter = "Missions" to see only missions

### Performance Tips

- Filters limit rendered objects for better performance
- Latest 50 runs shown by default
- Disable bloom if performance is slow
- Reduce animation speed if needed

## Technical Details

### Performance

- Maximum 50 workflow runs rendered
- Efficient raycasting for click detection
- Lazy loading (objects created only in Pipeline mode)
- Three.js InstancedMesh considerations for scaling

### Browser Support

- Modern browsers with WebGL support
- Chrome, Firefox, Safari, Edge recommended
- Mobile browsers supported (with touch controls)
- Requires JavaScript enabled

### Rendering

- **Renderer**: WebGL via Three.js
- **Post-processing**: UnrealBloomPass for glow effects
- **Controls**: OrbitControls for camera manipulation
- **Labels**: CSS3DRenderer for workflow lane labels

## Troubleshooting

### "No data showing in Pipeline view"

- Check that `data/agentops-runs.json` exists
- Refresh the page to reload data
- Check browser console for errors

### "Filters not working"

- Click "APPLY FILTERS" button after selecting
- Some filter combinations may result in no matches
- Try resetting filters to "All" options

### "Page not loading"

- Check browser console for errors
- Ensure CDN access for Three.js libraries
- Try hard refresh (Ctrl+F5 or Cmd+Shift+R)

### "Performance is slow"

- Reduce animation speed slider
- Disable bloom effect
- Use filters to show fewer objects
- Close other browser tabs

## Future Enhancements

Potential additions to pipeline view:

- Timeline scrubbing (view historical states)
- Agent performance heat maps
- Workflow dependency connections
- Real-time updates via WebSocket
- VR/AR immersive mode
- Custom color schemes
- Export/share specific views

## API / Data Format

### Expected agentops-runs.json Structure

```json
{
  "runs": [
    {
      "run_id": "12345",
      "workflow_file": "copilot-task.yml",
      "status": "completed",
      "conclusion": "success",
      "agent_name": "engineer-master",
      "pr_numbers": [123, 124],
      "issue_number": 456,
      "html_url": "https://github.com/.../actions/runs/12345",
      "created_at": "2025-01-17T12:00:00Z"
    }
  ]
}
```

### Required Fields

- `workflow_file`: Workflow filename for lane organization
- `status` or `conclusion`: For color coding
- `agent_name`: For agent marker attribution
- `html_url`: For click navigation

### Optional Fields

- `pr_numbers`: Array of associated PR numbers
- `issue_number`: Associated issue number
- Timestamps for sorting

---

**@create-guru** - Infrastructure creation with inventive and visionary approach, inspired by Nikola Tesla

*For questions or issues, create an issue on the GitHub repository.*
