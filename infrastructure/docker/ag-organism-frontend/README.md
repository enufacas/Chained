# AG-Organism Frontend - 2D Canvas Visualization

A Cloud Run service that serves the AG-Organism **2D canvas visualization** with lightweight HTML and JavaScript.

## Overview

This service provides a fast, lightweight 2D visualization for the AG-Organism agent coordination system, featuring:
- **Pure HTML/CSS/JavaScript** - No framework overhead
- **2D Canvas rendering** - Stable and performant
- **Dynamic environment variable injection** via Express server
- Real-time agent status monitoring
- Integration with AG-UI backend and ADK API

## Why 2D?

The service was converted from 3D (React Three Fiber) to 2D (Canvas) to address camera stability issues and reduce resource usage. The 2D version provides:
- **Better stability** - No 3D camera crashes
- **Faster load times** - No heavy JavaScript frameworks
- **Lower resource usage** - Reduced memory and CPU consumption
- **Simpler maintenance** - Plain HTML/CSS/JavaScript

## Architecture

```
┌─────────────────────────────────────────┐
│  AG-Organism Frontend (Cloud Run)       │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Express Server (Node.js)         │ │
│  │  - Serves static HTML             │ │
│  │  - Injects environment vars       │ │
│  │  - Health check endpoint          │ │
│  │  - Error logging endpoint         │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  React + Vite (Built)             │ │
│  │  - React Three Fiber (3D)         │ │
│  │  - Component-based UI             │ │
│  │  - Post-processing effects        │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
              │
              │ API Calls
              ▼
┌─────────────────────────────────────────┐
│    AG-UI Frontend (Cloud Run)           │
│    /api/pipeline, /api/registry         │
└─────────────────────────────────────────┘
```

## Project Structure

```
ag-organism-frontend/
├── Dockerfile              # Single-stage lightweight build
├── package.json           # Dependencies (Express only)
├── server.js              # Express server serving static HTML
├── README.md              # This file
└── public/
    ├── ag-organism.html   # Main 2D visualization
    └── assets/            # Static assets (if any)
```

## Environment Variables

### Required
- `NEXT_PUBLIC_ADK_API_URL` - ADK API Server URL
- `AG_UI_FRONTEND_URL` - AG-UI Frontend URL

### Optional
- `PORT` - Server port (default: 8080)
- `NODE_ENV` - Environment mode (default: production)

## Development

### Install Dependencies
```bash
npm install
```

### Run Production Server
```bash
npm run serve
```
Starts Express server serving the 2D HTML at http://localhost:8080

## Deployment

### Docker Build

The Dockerfile uses a **single-stage build** for simplicity:

- Installs production dependencies (Express only)
- Copies `public/` directory with HTML
- Runs Express server with environment injection

```bash
# Build image
docker build -t ag-organism-frontend .

# Test locally
docker run -p 8080:8080 \
  -e NEXT_PUBLIC_ADK_API_URL=https://chained-adk-api-server-xxx.run.app \
  -e AG_UI_FRONTEND_URL=https://chained-ag-ui-frontend-xxx.run.app \
  ag-organism-frontend
```

### Deploy to Cloud Run

Deployment is automated via GitHub Actions workflow `deploy-adk-agents.yml`.

Manual deployment:
```bash
# Build and push to Artifact Registry
gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT_ID/chained/ag-organism-frontend:latest

# Deploy to Cloud Run
gcloud run deploy chained-ag-organism-frontend \
  --image us-central1-docker.pkg.dev/PROJECT_ID/chained/ag-organism-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_ADK_API_URL=https://...,AG_UI_FRONTEND_URL=https://..."
```

## API Integration

The frontend integrates with the AG-UI backend:

### Endpoints Used
- `GET /api/registry` - Load available agents
- `POST /api/pipeline` - Execute agent pipeline
- `GET /api/pipeline?id=xxx` - Poll pipeline status
- `POST /api/log-error` - Frontend error logging

### Frontend Endpoints
- `GET /` - Main React application
- `GET /health` - Health check (JSON)
- `POST /api/log-error` - Error logging to GCP

## Features

### 3D Visualization (react-three-fiber)
- ✅ **Procedural robot models** with 6 variants (scientist, analyst, writer, engineer, artist, worker)
- ✅ **Improved robot scale** (1.5x) for better visibility 🔍
- ✅ State-driven animations (idle, processing, completed, failed)
- ✅ **Animated factory environment**: Robotic arms, conveyor belts, drones, data pods
- ✅ **A2A protocol visualization**: Animated message particles, task indicators, handoff animations 🎯
- ✅ Floating animation with sine waves
- ✅ Color-coded agent states (idle, processing, completed, failed)
- ✅ CSS3D labels with @react-three/drei Html
- ✅ Connection lines between selected agents
- ✅ Orbit controls for camera manipulation
- ✅ Post-processing bloom effect
- ✅ Fog and atmospheric lighting
- ✅ Shadow mapping

### UI Components
- ✅ Agent selection panel (left sidebar)
- ✅ Prompt input panel (right sidebar)
- ✅ Activity log with real-time updates
- ✅ Control panel (bottom) for camera reset, bloom, connections
- ✅ Loading screen
- ✅ Collapsible sidebars

### Pipeline Execution
- ✅ Select multiple agents
- ✅ Enter custom prompts
- ✅ Execute pipeline via API
- ✅ Real-time status polling (2s interval)
- ✅ Agent state updates (idle → processing → completed/failed)
- ✅ **A2A message visualization** during execution 🎯
- ✅ **Task handoff animations** between agents
- ✅ **Floating task indicators** above processing agents
- ✅ Artifact logging
- ✅ Error handling and logging

## Performance

**Target: 60fps on mid-range devices**

Optimizations:
- Efficient geometry reuse in AgentHumanoid component
- Conditional post-processing (bloom can be toggled)
- Proper shadow map configuration
- React Three Fiber's automatic disposal of Three.js objects
- Minimal draw calls with instanced geometries where applicable

## Monitoring

### View Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chained-ag-organism-frontend" --limit 50
```

### Check Service Status
```bash
gcloud run services describe chained-ag-organism-frontend --region us-central1
```

### Frontend Error Logging
Frontend errors are automatically sent to the backend `/api/log-error` endpoint and logged to GCP Cloud Logging with structured format.

## Terraform Configuration

The service is defined in `infrastructure/terraform/adk-agents.tf` as `google_cloud_run_v2_service.ag_organism_frontend`.

**Key configuration:**
- CPU: 0.5
- Memory: 512Mi
- Port: 8080
- Service Account: `chained-adk-agents`
- Public access: enabled

## Differences from Static Version

| Aspect | Vanilla Three.js (docs/) | React Three Fiber (Cloud Run) |
|--------|--------------------------|-------------------------------|
| Framework | Vanilla JS | React + R3F |
| 3D Rendering | Imperative Three.js | Declarative R3F components |
| UI | Manual DOM manipulation | React components |
| Build Tool | None (ES modules) | Vite |
| Deployment | GitHub Pages | Docker + Cloud Run |
| Environment | Static CDN | Dynamic env injection |
| Development | File editing | Hot reload with Vite |

## Troubleshooting

### Build fails
- Ensure Node.js >= 18.0.0
- Run `npm install` to ensure all dependencies are installed
- Check for TypeScript/JSX syntax errors

### 3D scene not rendering
- Check browser console for Three.js errors
- Ensure WebGL is supported in the browser
- Verify Canvas component has proper `gl` props

### API calls failing
- Check environment variables are correctly injected
- Verify AG_UI_FRONTEND_URL is accessible
- Check CORS configuration on backend

### Performance issues
- Toggle bloom effect off
- Reduce number of agents if possible
- Check browser GPU acceleration is enabled

---

**Built by @3d-render-master** (John Carmack agent)  
React + react-three-fiber migration: ✅  
60fps performance target maintained: ✅  
All features preserved: ✅
