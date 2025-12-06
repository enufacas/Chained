# AG-Organism Frontend - React Three Fiber

A Cloud Run service that serves the AG-Organism 3D visualization built with **React** and **react-three-fiber**.

## Overview

This service provides a modern React-based 3D visualization for the AG-Organism agent coordination system, featuring:
- **React** UI with component-based architecture
- **react-three-fiber** for declarative 3D rendering
- **@react-three/drei** for helpers (OrbitControls, Html labels)
- **@react-three/postprocessing** for bloom effects
- Dynamic environment variable injection
- Real-time pipeline execution monitoring
- Integration with AG-UI backend

## Documentation

📚 **Quick Links:**
- **[PROCEDURAL_MODELS_IMPLEMENTATION.md](./PROCEDURAL_MODELS_IMPLEMENTATION.md)** - Procedurally generated robot models and factory environment (NEW)
- **[ANIMATED_MODELS_GUIDE.md](./ANIMATED_MODELS_GUIDE.md)** - Guide for incorporating animated 3D models (reference)
- **[DREI_COMPONENTS.md](./DREI_COMPONENTS.md)** - Drei components usage guide
- **[FACTORY_THEME.md](./FACTORY_THEME.md)** - Factory theme specifications and color palette
- **[R3F_REFERENCE.md](./R3F_REFERENCE.md)** - Comprehensive React Three Fiber patterns and examples
- **[ITERATION_GUIDE.md](./ITERATION_GUIDE.md)** - Quick guide for iterating on features
- **[MIGRATION.md](./MIGRATION.md)** - Details on vanilla Three.js → R3F migration
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Complete implementation details

## Migration from Vanilla Three.js

This service was migrated from vanilla Three.js to react-three-fiber. See [MIGRATION.md](./MIGRATION.md) for details.

**Key improvements:**
- Declarative 3D scene composition
- Component-based architecture for better maintainability
- React hooks for animation and state management
- Easier testing and debugging with React DevTools
- Modern development experience with Vite

**For development**: Always refer to [R3F_REFERENCE.md](./R3F_REFERENCE.md) when adding new features or effects.

## Architecture

```
┌─────────────────────────────────────────┐
│  AG-Organism Frontend (Cloud Run)       │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Express Server (Node.js)         │ │
│  │  - Serves built React app         │ │
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
├── Dockerfile              # Multi-stage build (React build + Express)
├── package.json           # Dependencies (React, R3F, Express, Vite)
├── vite.config.js         # Vite configuration
├── index.html             # HTML entry point
├── server.js              # Express server serving React build
├── MIGRATION.md           # Migration documentation
├── PROCEDURAL_MODELS_IMPLEMENTATION.md  # Procedural models docs (NEW)
└── src/
    ├── main.jsx           # React entry point
    ├── App.jsx            # Main application
    ├── App.css
    ├── index.css          # Global styles
    ├── api/
    │   └── agentApi.js   # Backend API integration
    └── components/
        ├── Scene3D.jsx                      # Main 3D scene
        ├── AgentHumanoid.jsx                # Agent wrapper (uses ProceduralRobotModel)
        ├── ProceduralRobotModel.jsx         # Procedural robot models (NEW)
        ├── ProceduralFactoryEnvironment.jsx # Factory environment (NEW)
        ├── AgentLabel.jsx                   # CSS3D labels (drei/Html)
        ├── ConnectionLines.jsx              # Connection visualization
        ├── PostProcessing.jsx               # Bloom effect (R3F postprocessing)
        ├── AgentPanel.jsx                   # Left sidebar
        ├── PromptPanel.jsx                  # Right sidebar
        ├── ControlPanel.jsx                 # Bottom controls
        ├── Header.jsx                       # Top header
        └── LoadingScreen.jsx                # Loading screen
```

## Environment Variables

### Required
- `NEXT_PUBLIC_ADK_API_URL` - ADK API Server URL (for future use)
- `AG_UI_FRONTEND_URL` - AG-UI Frontend URL (for API calls)

### Optional
- `PORT` - Server port (default: 8080)
- `NODE_ENV` - Environment mode (default: production)

## Development

### Install Dependencies
```bash
npm install
```

### Run Development Server (Vite)
```bash
npm run dev
```
This starts Vite dev server with hot reload at http://localhost:5173

### Build for Production
```bash
npm run build
```
Builds React app to `dist/` folder using Vite.

### Run Production Server
```bash
npm run serve
```
Starts Express server serving the built React app at http://localhost:8080

## Deployment

### Docker Build

The Dockerfile uses a **multi-stage build**:

**Stage 1 (Builder):**
- Installs all dependencies (including dev)
- Builds React app with Vite
- Outputs to `dist/`

**Stage 2 (Production):**
- Copies built `dist/` folder
- Installs only production dependencies (Express)
- Runs Express server

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
- ✅ State-driven animations (idle, processing, completed, failed)
- ✅ **Animated factory environment**: Robotic arms, conveyor belts, drones, data pods
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
