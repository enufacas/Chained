# PR #3800 Deployed URL

## Quick Answer

The 3D AG-UI organism implementation from PR #3800 is deployed at:

**🎨 https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/organism**

## What Was Implemented

PR #3800 added a complete 3D visualization redesign of the AG-UI using react-three-fiber, featuring:

### 3D Features
- **Humanoid Agents**: Each agent represented as a 3D humanoid figure with capsule-based body parts
- **Dynamic Positioning**: Agents arranged in a circle formation for easy viewing
- **Status Indicators**: Color-coded animations based on agent status (idle, working, completed, failed)
- **Connection Lines**: Visual connections between selected agents showing the workflow
- **Artifact Visualization**: 3D octahedron artifacts floating near agents to represent created outputs
- **Camera Controls**: Orbit, zoom, and pan controls for exploring the 3D scene

### Visual Theme
The 3D organism maintains the standard AG-UI professional aesthetic:
- **Color Scheme**: Slate-based theme (slate-900, slate-800, slate-700 backgrounds)
- **Text Hierarchy**: White, slate-300, slate-400 text
- **Status Colors**: Blue-500, green-500, purple-500, yellow-500 for different states
- **Effects**: Minimal emissive glow (0.1-0.3 intensity), professional studio lighting

### Technology Stack
- **react-three-fiber** (`@react-three/fiber`): React renderer for Three.js
- **drei** (`@react-three/drei`): Helper components (OrbitControls, Html, PerspectiveCamera)
- **Three.js**: 3D graphics library
- **Next.js**: React framework with dynamic imports for SSR compatibility

## How to Access

### Direct URL
Simply visit: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/organism

### From Homepage
1. Go to: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app
2. Look for the `/organism` route or navigation link

## Components Added

PR #3800 added these new components:

1. **`src/app/organism/page.tsx`** - Main 3D organism page (421 lines)
2. **`src/components/3d/AgentCanvas3D.tsx`** - Main 3D scene container (173 lines)
3. **`src/components/3d/AgentHumanoid3D.tsx`** - Reusable 3D humanoid agent (185 lines)
4. **`src/components/3d/SceneSetup.tsx`** - Lighting, camera, and controls (65 lines)
5. **`src/components/3d/ConnectionLines3D.tsx`** - Agent connection lines (41 lines)
6. **`src/components/3d/ArtifactVisualization3D.tsx`** - Floating 3D artifacts (100 lines)

## Agent Color Coding

Different agent types have unique colors from the Tailwind palette:
- **Academic Research**: Blue (#3b82f6 - blue-500)
- **Google Trends**: Green (#10b981 - green-500)
- **Blog Writer**: Purple (#8b5cf6 - purple-500)
- **Code Reviewer**: Yellow (#f59e0b - yellow-500)
- **Data Analyst**: Cyan (#06b6d4 - cyan-500)
- **Image Generator**: Pink (#ec4899 - pink-500)

## Usage Instructions

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

## Deployment Details

### Cloud Run Service
- **Service Name**: chained-ag-ui-frontend
- **Region**: us-central1
- **URL**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app
- **Route**: `/organism`

### Infrastructure
Deployed via Terraform configuration in `infrastructure/terraform/base/adk-agents.tf`:
- CPU: 0.5
- Memory: 512Mi
- Port: 8080
- Image: `us-central1-docker.pkg.dev/PROJECT_ID/chained/ag-ui-frontend:TAG`

## Real Data Only Policy

This 3D UI follows the "real data only" principle:
- No simulated or fake data
- All pipeline data comes from actual A2A agent execution
- Artifacts are real outputs from agents
- Status updates reflect actual agent processing states
- Empty states shown when no data exists (no fake placeholders)

## Documentation References

- **PR #3800**: https://github.com/enufacas/Chained/pull/3800
- **3D Organism README**: `infrastructure/docker/ag-ui-frontend/README_3D_ORGANISM.md`
- **Deployment Config**: `infrastructure/terraform/base/adk-agents.tf`
- **Package Dependencies**: `infrastructure/docker/ag-ui-frontend/package.json`

## Dependencies Added

```json
{
  "@react-three/fiber": "^8.18.0",
  "@react-three/drei": "^9.120.0",
  "three": "^0.160.0"
}
```

## PR Statistics

- **Commits**: 5
- **Files Changed**: 10
- **Additions**: 1,909 lines
- **Deletions**: 635 lines
- **Merged**: 2025-12-10T04:07:01Z
- **Status**: Merged and Deployed

## Related URLs

- **Standard AG-UI**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app (2D card-based interface)
- **3D Organism**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/organism (3D humanoid visualization)
- **GitHub PR**: https://github.com/enufacas/Chained/pull/3800
- **GitHub Pages Timeline**: https://enufacas.github.io/Chained/

---

**Last Updated**: 2025-12-10

**PR Author**: Copilot

**Reviewers**: enufacas

**Status**: ✅ Merged and Deployed
