# Deployed AG-UI URLs on GCP

## Quick Answer

Your deployed AG-UI with the **organism style** (3D cyberpunk visualization) is at:

**🎨 https://chained-ag-organism-frontend-sguacxy5gq-uc.a.run.app**

## Two AG-UI Interfaces

The project has **two** different frontends for the AG-UI system, both deployed on Google Cloud Run:

### 1. AG-UI Frontend (Standard)
**URL:** https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app

**Description:**
- CopilotKit-powered A2A Pipeline Visualization UI
- Clean, modern interface with cards and timelines
- Production-focused interface for real work
- 2D card-based agent display

**Best for:** Production workflows, detailed pipeline management

### 2. AG-Organism Frontend (Cyberpunk 3D) ⭐
**URL:** https://chained-ag-organism-frontend-sguacxy5gq-uc.a.run.app

**Description:**
- 3D visualization of A2A agent coordination
- **Cyberpunk aesthetic** with dark theme and cyan/magenta colors
- Agents displayed as **3D humanoid figures** using Three.js
- Real-time animation with bloom effects and post-processing
- Built with React + react-three-fiber

**Best for:** Visual exploration, demonstrations, monitoring agent coordination

## What is the "Organism Style"?

The **organism style** refers to the AG-Organism frontend's unique visual approach:

### Visual Features
- 🎨 **Cyberpunk Aesthetic**: Dark background (#0a0e1a) with bright cyan (#00ffff) accents
- 🤖 **3D Humanoid Agents**: Agents rendered as 3D robot models with 6 variants (scientist, analyst, writer, engineer, artist, worker)
- ✨ **Animated Effects**: Floating animations, bloom post-processing, fog, shadows
- 🔗 **Connection Lines**: Visual links between selected agents
- 💎 **Floating Artifacts**: Task results displayed as 3D gems
- 📊 **Real-time Status**: Color-coded states (cyan=idle, yellow=processing, green=completed, red=failed)

### Interactive Elements
- **Left Panel**: Agent selection (multi-select supported)
- **Right Panel**: Prompt input
- **Bottom Panel**: Camera controls, visual toggles
- **3D Scene**: Orbit controls, zoom, pan

## Technical Details

### Cloud Run Services
Both services are deployed via Terraform in `infrastructure/terraform/adk-agents.tf`:

```
Service Name: chained-ag-organism-frontend
Region: us-central1
CPU: 0.5
Memory: 512Mi
Port: 8080
```

### Architecture
```
AG-Organism Frontend (Cloud Run)
├── Express Server (Node.js)
├── React + Vite (Built)
│   ├── React Three Fiber (3D)
│   ├── Procedural robot models
│   ├── Factory environment
│   └── Post-processing effects
└── API Integration with AG-UI Backend
```

### Get URLs Programmatically

```bash
# AG-Organism (3D Cyberpunk)
gcloud run services describe chained-ag-organism-frontend \
  --region=us-central1 \
  --format="get(status.url)"

# AG-UI (Standard)
gcloud run services describe chained-ag-ui-frontend \
  --region=us-central1 \
  --format="get(status.url)"
```

## Related Documentation

- **AG-Organism README**: `infrastructure/docker/ag-organism-frontend/README.md`
- **AG-Organism Guide**: `docs/AG_ORGANISM_README.md`
- **Implementation Summary**: `AG_ORGANISM_IMPLEMENTATION_SUMMARY.md`
- **Terraform Config**: `infrastructure/terraform/adk-agents.tf`

## Deployment

Both services are automatically deployed via GitHub Actions workflow:
- **Workflow**: `.github/workflows/deploy-adk-agents.yml`
- **Trigger**: Push to main branch or manual workflow_dispatch
- **Process**: Build Docker image → Push to Artifact Registry → Deploy via Terraform

## Testing & Verification

### E2E Test Suite

Comprehensive Playwright tests validate the live deployment:

**Location**: `tests/e2e/`
**Target**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app

**Test Coverage**:
- ✅ Homepage load and UI rendering
- ✅ Agent canvas and selection
- ✅ Multi-agent blog writing workflow
- ✅ UI polling and status updates
- ✅ Pipeline history
- ✅ Multi-agent coordination (A2A protocol)
- ✅ Error handling
- ✅ Real-time agent activity

**Latest Test Results** (2025-12-10):
- **Status**: All tests passing (8/8) ✅
- **Duration**: 2.8 minutes
- **System Health**: 9/9 agents healthy
- **See**: `docs/E2E_TEST_EXECUTION_SUMMARY.md`

**Run Tests**:
```bash
cd tests/e2e
npm install
npx playwright install chromium
npm test
```

## Summary

**Your question**: "What is the url of my deployed ag-ui with the organism style to gcp?"

**Answer**: https://chained-ag-organism-frontend-sguacxy5gq-uc.a.run.app

This is the 3D cyberpunk visualization with humanoid agents, bloom effects, and the distinctive cyan/magenta color scheme. It provides an alternate, visually striking interface to the standard AG-UI for exploring and executing A2A agent pipelines.
