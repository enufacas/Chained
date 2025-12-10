# AG-UI 3D Organism

A complete 3D visualization redesign of the AG-UI using react-three-fiber, featuring humanoid agents in a cyberpunk-styled environment.

## Overview

This implementation recreates the standard AG-UI page component-by-component using 3D objects instead of 2D elements, while maintaining the same functionality and visual style.

## Features

### 3D Visualization
- **Humanoid Agents**: Each agent is represented as a 3D humanoid figure with cyberpunk aesthetics
- **Dynamic Positioning**: Agents arranged in a circle formation for easy viewing
- **Status Indicators**: Color-coded and animated based on agent status (idle, working, completed, failed)
- **Connection Lines**: Visual connections between selected agents showing the workflow
- **Artifact Visualization**: 3D gems/objects floating near agents to represent created artifacts

### Components

#### Core 3D Components (`src/components/3d/`)
1. **AgentCanvas3D.tsx** - Main 3D scene container using react-three-fiber
2. **AgentHumanoid3D.tsx** - Reusable humanoid agent with cyberpunk styling
3. **SceneSetup.tsx** - Lighting, camera, and controls configuration
4. **ConnectionLines3D.tsx** - Lines connecting selected agents
5. **ArtifactVisualization3D.tsx** - Floating 3D artifacts

#### Page Implementation (`src/app/organism/`)
- **page.tsx** - Complete AG-UI with 3D visualization, maintaining all functionality from the standard version

### Visual Parity

The 3D organism maintains visual similarity to the standard AG-UI:
- **Color Scheme**: Slate-based professional theme (slate-900, slate-800, slate-700)
- **Text**: White, slate-300, slate-400 hierarchy
- **Accents**: Blue-500, green-500, purple-500, yellow-500 for status
- **Layout**: Same three-panel layout (agent selection, 3D canvas, prompt/activity)
- **Animations**: Floating agents, subtle pulsing for working agents, rotating artifacts
- **Effects**: Minimal emissive glow, professional studio lighting

### Technology Stack

- **react-three-fiber** (`@react-three/fiber`): React renderer for Three.js
- **drei** (`@react-three/drei`): Helper components (OrbitControls, Html, PerspectiveCamera)
- **Three.js**: 3D graphics library
- **Next.js**: React framework with dynamic imports for SSR compatibility
- **CopilotKit**: AI chat integration

## Usage

### Accessing the 3D Organism

Navigate to `/organism` route:
```
http://localhost:3000/organism
```

### Selecting Agents

1. Click on agent cards in the left panel to select/deselect
2. Selected agents will be highlighted in both the UI and 3D scene
3. Connection lines will appear between selected agents

### Executing a Pipeline

1. Select one or more agents
2. Enter a prompt in the right panel
3. Click "Execute Pipeline"
4. Watch agents animate and change status in real-time
5. See artifacts appear as floating 3D objects

### Camera Controls

- **Orbit**: Left-click and drag to rotate around the scene
- **Zoom**: Scroll to zoom in/out (limited between 20 and 100 units)
- **Pan**: Right-click and drag to pan
- **Reset**: Click "Reset View" button to return to default camera position

### Visual Settings

- **Bloom**: Toggle glow effects on/off
- **Connections**: Toggle connection lines between agents

## Implementation Details

### Humanoid Agent Structure

Each humanoid consists of:
- Head (sphere) with visor (plane) in blue-500
- Torso (capsule) with chest light
- Arms (capsules) at 15° angles
- Legs (capsules) for stability
- Subtle highlight (minimal outer sphere, translucent)

### Animations

- **Floating**: Sine wave motion for idle agents
- **Working**: Gentle swaying + subtle pulsing emissive intensity (0.1 to 0.3)
- **Artifacts**: Rotation + upward floating, fade out after 10 seconds

### Color Coding

Different agent types have unique colors (Tailwind palette):
- Academic Research: Blue (#3b82f6 - blue-500)
- Google Trends: Green (#10b981 - green-500)
- Blog Writer: Purple (#8b5cf6 - purple-500)
- Code Reviewer: Yellow (#f59e0b - yellow-500)
- Data Analyst: Cyan (#06b6d4 - cyan-500)
- Image Generator: Pink (#ec4899 - pink-500)

## Real Data Integration

This 3D UI follows the same "real data only" principle as the standard AG-UI:
- No simulated or fake data
- All pipeline data comes from actual A2A agent execution
- Artifacts are real outputs from agents
- Status updates reflect actual agent processing states

## Development

### File Structure

```
infrastructure/docker/ag-ui-frontend/
├── src/
│   ├── app/
│   │   └── organism/
│   │       └── page.tsx          # 3D organism page
│   └── components/
│       └── 3d/
│           ├── AgentCanvas3D.tsx
│           ├── AgentHumanoid3D.tsx
│           ├── SceneSetup.tsx
│           ├── ConnectionLines3D.tsx
│           ├── ArtifactVisualization3D.tsx
│           └── index.ts
├── package.json                   # Added react-three-fiber deps
└── README_3D_ORGANISM.md          # This file
```

### Key Dependencies Added

```json
{
  "@react-three/fiber": "^8.18.0",
  "@react-three/drei": "^9.120.0",
  "three": "^0.160.0"
}
```

### SSR Considerations

The 3D components are dynamically imported with `{ ssr: false }` to avoid server-side rendering issues with Three.js.

## Future Enhancements

Potential improvements:
- [ ] VR/AR support
- [ ] More agent shapes (based on specialization)
- [ ] Advanced particle effects
- [ ] Physics-based interactions
- [ ] Agent "talking" animations during execution
- [ ] 3D graph visualization of agent dependencies
- [ ] Custom shaders for more dramatic effects

## Credits

Based on:
- `docs/organism.html` - Original 3D humanoid design (structure only, not theme)
- Standard AG-UI frontend - Component structure, data flow, and visual theme
- [react-three-fiber](https://github.com/pmndrs/react-three-fiber) - React Three.js integration
