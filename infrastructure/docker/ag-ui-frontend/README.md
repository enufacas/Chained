# AG-UI Frontend with CopilotKit

A Next.js application using CopilotKit for Agentic Generative UI to visualize the A2A pipeline.

## Overview

This frontend provides an interactive visualization of the A2A (Agent-to-Agent) pipeline using CopilotKit's Agentic Generative UI patterns. It connects to the ADK API Server to interact with deployed agents.

## Features

- **Agent Cards**: Visual representation of each agent in the pipeline
- **Pipeline Flow**: Shows the flow from Research → Trends → Blog Writer
- **Real-time Chat**: Interactive chat with agents via CopilotKit (supports Gemini and OpenAI)
- **Data Preview**: View artifacts and task data from each agent
- **Run History**: Browse historical pipeline runs
- **LLM Provider Status**: Visual indicator showing which LLM provider is active

## Technology Stack

- **Next.js 14+**: React framework with App Router
- **CopilotKit**: Agentic Generative UI framework
- **Tailwind CSS**: Styling
- **TypeScript**: Type safety

## Supported LLM Providers

The chat feature supports two LLM providers (in order of preference):

1. **Google Gemini** (preferred) - Set `GEMINI_API_KEY` environment variable
2. **OpenAI** (fallback) - Set `OPENAI_API_KEY` environment variable

If both are set, Gemini will be used. If neither is set, the chat feature will be disabled but the UI will still work.

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
# LLM API Keys (at least one required for chat feature)
# Gemini is preferred if both are set
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# ADK API Server URL
NEXT_PUBLIC_ADK_API_URL=https://chained-adk-api-server-sguacxy5gq-uc.a.run.app

# CopilotKit Configuration (optional - for cloud features)
COPILOTKIT_RUNTIME_URL=/api/copilotkit
```

## Automated Deployment (CI/CD)

This application is automatically deployed via the `deploy-adk-agents.yml` GitHub Actions workflow.

### Automatic Deployment Triggers

Deployment is triggered automatically when:

1. **Push to main branch** with changes to:
   - `infrastructure/docker/ag-ui-frontend/**`
   - `infrastructure/terraform/adk-agents.tf`
   - `.github/workflows/deploy-adk-agents.yml`

2. **Manual workflow dispatch** via GitHub Actions UI

### What the Pipeline Does

1. **Builds** the Docker image using multi-stage build
2. **Pushes** to Google Artifact Registry
3. **Deploys** to Cloud Run via Terraform
4. **Configures** environment variables (GEMINI_API_KEY or OPENAI_API_KEY from Secret Manager)
5. **Verifies** the deployment is healthy

### Required Secrets

The following secrets must be configured in GitHub:

- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_SA_KEY`: Service account key JSON
- `GCP_REGION`: Deployment region (default: us-central1)

### LLM API Key Setup

> **Note**: An LLM API key is **optional**. Without it, the AG-UI Frontend will work fine for visualizing the A2A pipeline. Only the CopilotKit chat feature will be disabled.

#### Option 1: Using Google Gemini (Recommended)

If you already have a Gemini API key configured in GCP Secret Manager (e.g., for other agents), it will be automatically used:

```bash
# If not already created, create the secret
gcloud secrets create gemini-api-key --replication-policy="automatic"

# Add the API key value
echo -n "your-gemini-api-key" | gcloud secrets versions add gemini-api-key --data-file=-

# Grant the service account access
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:chained-adk-agents@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Then set `gemini_api_key_secret = "gemini-api-key"` in your Terraform variables.

#### Option 2: Using OpenAI

```bash
# Create the secret
gcloud secrets create openai-api-key --replication-policy="automatic"

# Add the API key value
echo -n "your-openai-api-key" | gcloud secrets versions add openai-api-key --data-file=-

# Grant the service account access
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:chained-adk-agents@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Then set `openai_api_key_secret = "openai-api-key"` in your Terraform variables.

## Manual Deployment to GCP Cloud Run

For manual deployment without the CI/CD pipeline:

```bash
# Build Docker image
docker build -t ag-ui-frontend .

# Tag for GCR
docker tag ag-ui-frontend gcr.io/PROJECT_ID/ag-ui-frontend

# Push to GCR
docker push gcr.io/PROJECT_ID/ag-ui-frontend

# Deploy to Cloud Run (without LLM key - chat feature disabled)
gcloud run deploy ag-ui-frontend \
  --image gcr.io/PROJECT_ID/ag-ui-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# OR deploy with Gemini key for chat feature (recommended)
gcloud run deploy ag-ui-frontend \
  --image gcr.io/PROJECT_ID/ag-ui-frontend \
  --set-env-vars GEMINI_API_KEY=your_key \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# OR deploy with OpenAI key for chat feature
gcloud run deploy ag-ui-frontend \
  --image gcr.io/PROJECT_ID/ag-ui-frontend \
  --set-env-vars OPENAI_API_KEY=your_key \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## References

- [CopilotKit Documentation](https://docs.copilotkit.ai/)
- [CopilotKit GitHub](https://github.com/CopilotKit/CopilotKit)
- [AG-UI Protocol](https://docs.ag-ui.com/)
- [A2A Protocol](https://a2a-protocol.org/)
