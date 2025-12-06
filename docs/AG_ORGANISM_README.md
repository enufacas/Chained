# AG-Organism: Interactive Agent Coordination Visualizer

## ⚠️ Deployment Notice

**AG-Organism is now deployed on Cloud Run!**

- **Cloud Run URL**: Available via Terraform output `ag_organism_frontend_url`
- **Static Version**: The static HTML version at `docs/ag-organism.html` is deprecated
- **Why Cloud Run**: Cloud Run deployment enables dynamic environment variable configuration, proper CORS handling, and integration with the full AG-UI infrastructure

See [Deployment](#deployment) section for details.

## Overview

AG-Organism is an alternate frontend for the AG-UI system that combines the cyberpunk visual style of the organism.html visualization with the full A2A protocol capabilities of the AG-UI backend.

## Features

### 🎨 Visual Style
- **Cyberpunk Aesthetic**: Dark theme with cyan/magenta color scheme
- **3D Visualization**: Agents displayed as humanoid figures using Three.js
- **Real-time Animation**: Agents float and animate during execution
- **Bloom Effects**: Post-processing effects for enhanced visuals

### 🤖 Agent Management
- **Multi-Agent Selection**: Click to select multiple agents for execution
- **Visual Feedback**: Selected agents highlighted in the 3D scene
- **Agent Registry**: Connects to AG-UI backend to load available agents
- **Real-time Status**: Agents change color/animation based on execution state

### 🔄 A2A Protocol Compliance
- **Pipeline Execution**: Full A2A protocol pipeline support
- **Artifact Visualization**: Artifacts appear as floating gems near agents
- **Message Display**: Agent messages logged in activity panel
- **Task Tracking**: Real-time task status updates

### 📝 Interactive Controls
- **Prompt Input**: Enter custom prompts for agent execution
- **Activity Log**: Real-time logging of system events
- **Camera Controls**: Orbit, zoom, and pan in 3D space
- **Visual Toggles**: Control bloom, connections, and other effects

## How to Use

### 1. Access the Interface
Navigate to: `https://YOUR_DOMAIN/ag-organism.html`

Or locally: `http://localhost:8000/ag-organism.html` (when serving docs/)

### 2. Select Agents
- View available agents in the left panel
- Click agents to select/deselect (supports multiple selection)
- Selected agents are highlighted and connected in 3D view

### 3. Enter Prompt
- Type your execution prompt in the right panel
- Prompt will be sent to all selected agents
- Example: "Research the latest AI trends and create a blog post"

### 4. Execute Pipeline
- Click "Execute Pipeline" button
- Watch agents animate as they work
- View artifacts and messages in activity log
- Pipeline status updates every 2 seconds

### 5. View Results
- Artifacts appear as floating gems
- Agent humanoids change color based on status:
  - **Cyan**: Idle
  - **Yellow**: Processing
  - **Green**: Completed
  - **Red**: Failed

## Architecture

### Frontend Components
```
ag-organism.html
├── Three.js Scene
│   ├── Agent Humanoids (3D models)
│   ├── Artifact Gems
│   ├── Connection Lines
│   └── CSS3D Labels
├── Agent Selection Panel (left)
├── Prompt Input Panel (right)
├── Control Panel (bottom)
└── Activity Log
```

### Backend Integration
```
AG-Organism → AG-UI Backend APIs
├── GET /api/registry (load agents)
├── POST /api/pipeline (start execution)
└── GET /api/pipeline?id=X (poll status)
```

### Data Flow
1. **Load Agents**: Fetch from `/api/registry`
2. **User Selection**: Track selected agents in UI
3. **Execute Pipeline**: POST to `/api/pipeline` with topic and agents
4. **Poll Status**: GET pipeline status every 2 seconds
5. **Update Visualization**: Animate agents, show artifacts, log messages

## A2A Protocol Support

AG-Organism fully implements the A2A protocol:

### Agent Cards
Loaded from registry with:
- Display name
- Icon
- Description
- Capabilities

### Tasks
Pipeline creates A2A tasks with:
- Task ID
- Context ID
- Status
- Messages
- Artifacts

### Messages
Agent messages displayed with:
- Role (user/agent)
- Content (parts array)
- Timestamp

### Artifacts
Visualized as 3D objects with:
- Name
- Type (text/json/etc)
- Data preview
- Visual representation

## Comparison with Current AG-UI

| Feature | Current AG-UI | AG-Organism |
|---------|--------------|-------------|
| Visual Style | Clean UI cards | Cyberpunk 3D |
| Agent Display | 2D cards | 3D humanoids |
| Selection | Predefined pipeline | Multi-select |
| Visualization | Timeline/cards | 3D animated scene |
| Backend | Same AG-UI APIs | Same AG-UI APIs |
| A2A Protocol | Full support | Full support |
| Use Case | Production work | Visual exploration |

## Technical Details

### Dependencies
- **Three.js 0.160.0**: 3D rendering engine
- **OrbitControls**: Camera controls
- **CSS3DRenderer**: Label rendering
- **EffectComposer**: Post-processing
- **UnrealBloomPass**: Bloom effects

All loaded via CDN, no build step required.

### Browser Compatibility
- Modern browsers with WebGL support
- ES6+ JavaScript features
- CSS Grid and Flexbox layouts

### Performance
- Efficient 3D rendering with Three.js
- Polling every 2 seconds (configurable)
- Artifact cleanup after 10 seconds
- Optimized for 20+ agents

## Configuration

### API Endpoint
Change `API_BASE_URL` in the script section:
```javascript
const API_BASE_URL = 'https://YOUR_DOMAIN/api';
```

### Polling Interval
Adjust pipeline status polling:
```javascript
pipelineInterval = setInterval(async () => {
    // Poll logic
}, 2000); // 2 seconds
```

### Visual Settings
- Bloom intensity: Adjust `UnrealBloomPass` parameters
- Camera position: Modify `camera.position.set()`
- Agent arrangement: Change circle radius

## Future Enhancements

Potential improvements:
- [ ] WebSocket support for real-time updates (no polling)
- [ ] Agent filtering and search
- [ ] Pipeline history view
- [ ] Export pipeline results
- [ ] Custom agent colors/shapes
- [ ] VR/AR support
- [ ] Performance metrics visualization

## Troubleshooting

### Agents Not Loading
- Check backend API is running
- Verify API_BASE_URL is correct
- Check browser console for errors

### 3D Scene Not Rendering
- Ensure WebGL is supported
- Check browser console for Three.js errors
- Try disabling browser extensions (ad blockers)

### Pipeline Not Executing
- Verify agents are selected
- Ensure prompt is entered
- Check backend logs for errors
- Confirm agent URLs are configured

## Deployment

### Cloud Run Deployment (Production)

AG-Organism is deployed as a Cloud Run service with dynamic environment variable injection.

**Architecture:**
```
AG-Organism Frontend (Cloud Run)
├── Express Server (Node.js)
├── Environment Variable Injection
└── Static HTML with Three.js

Environment Variables:
- NEXT_PUBLIC_ADK_API_URL: ADK API Server URL
- AG_UI_FRONTEND_URL: AG-UI Frontend URL (for /api endpoints)
```

**Deployment Process:**

1. **Automatic**: Triggered by GitHub Actions workflow `deploy-adk-agents.yml`
   - Builds Docker image
   - Pushes to Google Artifact Registry
   - Deploys via Terraform

2. **Manual**:
   ```bash
   # Build and push
   cd infrastructure/docker/ag-organism-frontend
   docker build -t us-central1-docker.pkg.dev/PROJECT_ID/chained/ag-organism-frontend:latest .
   gcloud docker -- push us-central1-docker.pkg.dev/PROJECT_ID/chained/ag-organism-frontend:latest

   # Deploy via Terraform
   cd infrastructure/terraform
   terraform apply -var="image_tag=latest"
   ```

**Get Service URL:**
```bash
terraform output ag_organism_frontend_url
# Or
gcloud run services describe chained-ag-organism-frontend --region us-central1 --format='value(status.url)'
```

### Local Development

#### Option 1: Serve Static HTML (Deprecated)
```bash
# Serve from docs directory
cd docs
python3 -m http.server 8000

# Open in browser
open http://localhost:8000/ag-organism.html
```

**Note**: Static version uses hardcoded API URLs and is deprecated. Use Cloud Run deployment for production.

#### Option 2: Run Docker Container Locally
```bash
cd infrastructure/docker/ag-organism-frontend

# Build
docker build -t ag-organism-frontend .

# Run with environment variables
docker run -p 8080:8080 \
  -e AG_UI_FRONTEND_URL=https://chained-ag-ui-frontend-xxx.run.app \
  -e NEXT_PUBLIC_ADK_API_URL=https://chained-adk-api-server-xxx.run.app \
  ag-organism-frontend

# Open in browser
open http://localhost:8080
```

### Modification

#### Updating the Visualization
1. Edit `infrastructure/docker/ag-organism-frontend/public/ag-organism.html`
2. Commit changes
3. Push to trigger automatic deployment via GitHub Actions

#### Local Testing After Changes
```bash
cd infrastructure/docker/ag-organism-frontend
docker build -t ag-organism-frontend:test .
docker run -p 8080:8080 \
  -e AG_UI_FRONTEND_URL=http://localhost:3000 \
  -e NEXT_PUBLIC_ADK_API_URL=http://localhost:8080 \
  ag-organism-frontend:test
```

### Files and Locations

| Purpose | Location |
|---------|----------|
| **Production Service** | `infrastructure/docker/ag-organism-frontend/` |
| - Dockerfile | `infrastructure/docker/ag-organism-frontend/Dockerfile` |
| - Express Server | `infrastructure/docker/ag-organism-frontend/server.js` |
| - HTML File | `infrastructure/docker/ag-organism-frontend/public/ag-organism.html` |
| **Deprecated Static** | `docs/ag-organism.html` (for GitHub Pages) |
| **Terraform Config** | `infrastructure/terraform/adk-agents.tf` |
| **Deployment Workflow** | `.github/workflows/deploy-adk-agents.yml` |

## Development

### Modification (Legacy)
The static file `docs/ag-organism.html` is self-contained HTML. Edit directly to:
- Adjust visual style (CSS section)
- Modify 3D rendering (Three.js code)
- Change API integration (fetch calls)

**Note**: For production changes, update the Cloud Run version instead.

## Credits

- **Visual Design**: Inspired by organism.html
- **Backend**: AG-UI with CopilotKit
- **3D Engine**: Three.js
- **Protocol**: A2A specification

## License

Same as the Chained project.
