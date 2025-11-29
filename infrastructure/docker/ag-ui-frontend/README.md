# AG-UI Frontend with CopilotKit

A Next.js application using CopilotKit for Agentic Generative UI to visualize the A2A pipeline.

## Overview

This frontend provides an interactive visualization of the A2A (Agent-to-Agent) pipeline using CopilotKit's Agentic Generative UI patterns. It connects to the ADK API Server to interact with deployed agents.

## Features

- **Agent Cards**: Visual representation of each agent in the pipeline
- **Pipeline Flow**: Shows the flow from Research → Trends → Blog Writer
- **Real-time Chat**: Interactive chat with agents via CopilotKit
- **Data Preview**: View artifacts and task data from each agent
- **Run History**: Browse historical pipeline runs

## Technology Stack

- **Next.js 14+**: React framework with App Router
- **CopilotKit**: Agentic Generative UI framework
- **Tailwind CSS**: Styling
- **TypeScript**: Type safety

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

```env
# ADK API Server URL
NEXT_PUBLIC_ADK_API_URL=https://chained-adk-api-server-sguacxy5gq-uc.a.run.app

# CopilotKit Configuration (optional - for cloud features)
COPILOTKIT_RUNTIME_URL=/api/copilotkit
```

## Deployment to GCP Cloud Run

```bash
# Build Docker image
docker build -t ag-ui-frontend .

# Tag for GCR
docker tag ag-ui-frontend gcr.io/PROJECT_ID/ag-ui-frontend

# Push to GCR
docker push gcr.io/PROJECT_ID/ag-ui-frontend

# Deploy to Cloud Run
gcloud run deploy ag-ui-frontend \
  --image gcr.io/PROJECT_ID/ag-ui-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## References

- [CopilotKit Documentation](https://docs.copilotkit.ai/)
- [CopilotKit GitHub](https://github.com/CopilotKit/CopilotKit)
- [AG-UI Protocol](https://docs.ag-ui.com/)
- [A2A Protocol](https://a2a-protocol.org/)
