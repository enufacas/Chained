# AG-Organism Frontend

A Cloud Run service that serves the AG-Organism 3D visualization with environment variable injection.

## Overview

This service serves the `ag-organism.html` file as a dynamic web application on Cloud Run, enabling:
- Dynamic environment variable injection (API URLs)
- Proper integration with the AG-UI backend
- Access to Cloud Run infrastructure features

## Architecture

```
┌─────────────────────────────────────┐
│   AG-Organism Frontend (Cloud Run)  │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Express Server (Node.js)     │ │
│  │  - Serves ag-organism.html    │ │
│  │  - Injects environment vars   │ │
│  │  - Health check endpoint      │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
              │
              │ API Calls
              ▼
┌─────────────────────────────────────┐
│    AG-UI Frontend (Cloud Run)       │
│    /api/pipeline, /api/registry     │
└─────────────────────────────────────┘
```

## Environment Variables

### Required
- `NEXT_PUBLIC_ADK_API_URL` - ADK API Server URL
- `AG_UI_FRONTEND_URL` - AG-UI Frontend URL (for API calls)

### Optional
- `PORT` - Server port (default: 8080)
- `NODE_ENV` - Environment mode (default: production)

## Deployment

### Build Docker Image
```bash
cd infrastructure/docker/ag-organism-frontend
docker build -t ag-organism-frontend .
```

### Test Locally
```bash
docker run -p 8080:8080 \
  -e NEXT_PUBLIC_ADK_API_URL=https://chained-adk-api-server-xxx.run.app \
  -e AG_UI_FRONTEND_URL=https://chained-ag-ui-frontend-xxx.run.app \
  ag-organism-frontend
```

Open http://localhost:8080 in your browser.

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

## Files

```
ag-organism-frontend/
├── Dockerfile              # Multi-stage build for Node.js Express app
├── package.json           # Node.js dependencies
├── server.js              # Express server with env injection
└── public/
    └── ag-organism.html   # 3D visualization HTML (copied from docs/)
```

## Development

### Local Development
```bash
npm install
NEXT_PUBLIC_ADK_API_URL=http://localhost:8080 \
AG_UI_FRONTEND_URL=http://localhost:3000 \
npm start
```

### Update HTML
When updating the visualization, modify `public/ag-organism.html` and redeploy.

## Integration with Terraform

The service is defined in `infrastructure/terraform/adk-agents.tf` as `google_cloud_run_v2_service.ag_organism_frontend`.

Key configuration:
- CPU: 0.5
- Memory: 512Mi
- Port: 8080
- Service Account: `chained-adk-agents`
- Public access: enabled

## Differences from Static Version

| Aspect | Static (GitHub Pages) | Cloud Run |
|--------|----------------------|-----------|
| API URLs | Hardcoded | Environment variables |
| Deployment | Git push to docs/ | Docker + Terraform |
| Environment | Static file server | Node.js Express |
| Configuration | Fixed at build | Dynamic at runtime |
| Health checks | N/A | /health endpoint |

## Endpoints

- `GET /` - Main visualization page
- `GET /health` - Health check (JSON response)

## Monitoring

View logs in Google Cloud Console:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chained-ag-organism-frontend" --limit 50
```

Check service status:
```bash
gcloud run services describe chained-ag-organism-frontend --region us-central1
```
