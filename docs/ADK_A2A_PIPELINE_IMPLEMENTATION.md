# ADK A2A Blog Pipeline - Implementation Plan

## Overview

This document outlines the complete implementation plan for deploying Google ADK sample Python agents to GCP Infrastructure using the A2A (Agent-to-Agent) protocol.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GitHub Actions Orchestration                         │
│                        (Every 6 hours scheduled run)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Cloud Run Services                              │
│                           (GCP Infrastructure)                               │
│                                                                              │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│   │   Academic      │    │    Google       │    │     Blog        │        │
│   │   Research      │───▶│    Trends       │───▶│    Writer       │        │
│   │   Agent         │    │    Agent        │    │    Agent        │        │
│   │   (8081)        │    │   (8083)        │    │   (8082)        │        │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│                                                                              │
│   A2A Protocol:                                                              │
│   • /.well-known/agent.json (discovery)                                     │
│   • POST /a2a/tasks (send message)                                          │
│   • GET /health (observability)                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            GitHub Pages Website                              │
│                     (https://enufacas.github.io/Chained)                    │
│                                                                              │
│   • Published blog posts                                                     │
│   • Pipeline status page (a2a-pipeline.html)                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. ADK Agents (Python/FastAPI)

Each agent implements the A2A protocol specification:

| Agent | Purpose | Port | Skills |
|-------|---------|------|--------|
| academic-research | Discovers research topics | 8081 | discover-topics, analyze-topic |
| blog-writer | Writes blog posts | 8082 | write-blog, deploy-blog |
| google-trends | Analyzes SEO trends | 8083 | analyze-trends, get-keywords |

**Location:** `infrastructure/docker/adk-agents/`

### 2. Cloud Run Deployment (Terraform)

Provisions GCP infrastructure:
- Service accounts with minimal permissions
- Cloud Run services for each agent
- Secret Manager integration for API keys
- Health checks and auto-scaling

**Location:** `infrastructure/terraform/adk-agents.tf`

### 3. GitHub Actions Workflows

| Workflow | Purpose | Schedule |
|----------|---------|----------|
| `deploy-adk-agents.yml` | Build and deploy agents | On push to main |
| `adk-a2a-blog-pipeline.yml` | Run blog pipeline | Every 6 hours |

**Location:** `.github/workflows/`

### 4. Observability

- **Health Checks:** Each agent exposes `/health` endpoint
- **ADK Dev UI:** Available at service root URL
- **Cloud Monitoring:** Latency, error rates, request counts
- **Cloud Trace:** Distributed tracing between agents
- **GitHub Actions:** Pipeline success/failure tracking

## A2A Protocol Implementation

### Agent Card (§4.4.1)

```json
{
  "name": "academic-research",
  "description": "Discovers research topics",
  "url": "https://chained-academic-research-xxx.run.app",
  "version": "1.0.0",
  "protocolVersion": "0.3.0",
  "skills": [...],
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  }
}
```

### SendMessage (§3.1.1)

```http
POST /a2a/tasks
Content-Type: application/json

{
  "message": {
    "role": "user",
    "parts": [{"text": "Find AI research topics"}]
  },
  "contextId": "blog-pipeline-20251127-120000"
}
```

### Task Response (§4.1.1)

```json
{
  "id": "task-abc123",
  "status": {
    "state": "completed",
    "timestamp": "2025-11-27T12:00:00Z",
    "message": {...}
  },
  "artifacts": [
    {"name": "research-findings", "type": "application/json", "data": "..."}
  ]
}
```

## Deployment Steps

### Prerequisites

1. GCP Project with billing enabled
2. Required APIs enabled:
   - Cloud Run
   - Cloud Build
   - Artifact Registry
   - Secret Manager

3. GitHub Secrets configured:
   - `GCP_PROJECT_ID`
   - `GCP_SA_KEY`
   - `GCP_REGION` (optional, default: us-central1)

### Initial Deployment

```bash
# 1. Build and push agent containers
gh workflow run deploy-adk-agents.yml

# 2. Apply Terraform
cd infrastructure/terraform
terraform init
terraform apply -var="project_id=YOUR_PROJECT"

# 3. Verify deployment
curl https://chained-academic-research-xxx.run.app/health
```

### Scheduled Pipeline

The pipeline runs automatically every 6 hours via `adk-a2a-blog-pipeline.yml`:

1. **00:00 UTC** - First run
2. **06:00 UTC** - Second run
3. **12:00 UTC** - Third run
4. **18:00 UTC** - Fourth run

Manual trigger available via workflow_dispatch.

## Monitoring & Troubleshooting

### Health Check URLs

```bash
curl $ACADEMIC_RESEARCH_URL/health
curl $BLOG_WRITER_URL/health
curl $GOOGLE_TRENDS_URL/health
```

### Agent Discovery

```bash
curl $AGENT_URL/.well-known/agent.json
```

### View Logs

```bash
gcloud run services logs read chained-academic-research --region=us-central1
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Agent unhealthy | Container startup failed | Check Cloud Run logs |
| Pipeline timeout | Agent unresponsive | Increase timeout, check health |
| No topics found | Research agent issue | Check agent card, verify skills |

## Security Considerations

1. **Secrets:** Stored in Secret Manager, not in code
2. **Service Accounts:** Minimal permissions per agent
3. **Public Access:** Consider restricting to authenticated users
4. **API Keys:** Rotate regularly, use per-environment keys

## Future Enhancements

1. **Gemini Integration:** Use Gemini API for real content generation
2. **Streaming:** Enable streaming responses for long-running tasks
3. **Multi-Agent Discussion:** Implement back-and-forth agent communication
4. **Real Google Trends:** Integrate actual Google Trends API
5. **Content Review:** Add review step before publishing

## References

- [Google ADK Samples](https://github.com/google/adk-samples)
- [A2A Protocol Specification](https://a2a-protocol.org/)
- [ADK Cloud Run Deployment](https://google.github.io/adk-docs/deploy/cloud-run/)
- [ADK Documentation](https://google.github.io/adk-docs/)
