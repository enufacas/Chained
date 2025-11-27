# ADK Dev UI - Complete Guide

## Overview

The **ADK Dev UI** (Agent Development Kit Development User Interface) is a web-based interface provided by Google's Agent Development Kit for interacting with, testing, and debugging AI agents. In the Chained repository, the ADK Dev UI is automatically accessible when agents are deployed to Cloud Run.

## How ADK Dev UI Works in Chained

When you deploy ADK agents to Cloud Run (as seen in the [workflow run](https://github.com/enufacas/Chained/actions/runs/19739435100/job/56559442823)), each agent exposes endpoints that power the Dev UI experience:

```
ADK Dev UI is accessible at each agent's root endpoint:
- Academic Research: https://chained-academic-research-sguacxy5gq-uc.a.run.app
- Blog Writer: https://chained-blog-writer-sguacxy5gq-uc.a.run.app
- Google Trends: https://chained-google-trends-sguacxy5gq-uc.a.run.app

Health checks available at /health endpoint for each service.
A2A Agent Cards available at /.well-known/agent.json
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ADK Dev UI Flow                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌────────────────┐         ┌──────────────────────┐                   │
│   │   Browser UI   │◀───────▶│  Cloud Run Service   │                   │
│   │   (Dev UI)     │   HTTP  │  (Agent Backend)     │                   │
│   └────────────────┘         └──────────────────────┘                   │
│          │                              │                                │
│          │                              │                                │
│          ▼                              ▼                                │
│   ┌────────────────┐         ┌──────────────────────┐                   │
│   │   Interactive  │         │   A2A Protocol API   │                   │
│   │   Chat/Debug   │         │   ├─ /a2a/tasks      │                   │
│   │   Interface    │         │   ├─ /health         │                   │
│   └────────────────┘         │   └─ /.well-known/   │                   │
│                              │       agent.json     │                   │
│                              └──────────────────────┘                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Endpoints

Each deployed agent in Chained exposes these endpoints:

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `GET /` | Root endpoint with agent info | Agent description and API reference |
| `GET /.well-known/agent.json` | A2A Agent Card | Agent capabilities and skills |
| `POST /a2a/tasks` | Send message to agent | Submit tasks and receive results |
| `GET /health` | Health check | Service status verification |

## Using the Dev UI

### 1. Accessing an Agent

Visit any agent's Cloud Run URL in your browser:

```bash
# Check agent info
curl https://chained-academic-research-sguacxy5gq-uc.a.run.app/

# Response:
{
  "agent": "academic-research",
  "description": "Discovers and analyzes academic research topics for blog content",
  "version": "1.0.0",
  "a2a_protocol": "0.3.0",
  "endpoints": {
    "agent_card": "GET /.well-known/agent.json",
    "send_message": "POST /a2a/tasks",
    "health": "GET /health"
  }
}
```

### 2. Discovering Agent Capabilities

```bash
# Get the A2A Agent Card
curl https://chained-academic-research-sguacxy5gq-uc.a.run.app/.well-known/agent.json

# Response:
{
  "name": "academic-research",
  "description": "Discovers and analyzes academic research topics for blog content",
  "url": "https://chained-academic-research-sguacxy5gq-uc.a.run.app",
  "version": "1.0.0",
  "protocolVersion": "0.3.0",
  "skills": [
    {
      "id": "discover-topics",
      "name": "Discover Research Topics",
      "description": "Find trending academic research topics for blog content",
      "tags": ["research", "discovery", "topics"]
    },
    {
      "id": "analyze-topic",
      "name": "Analyze Topic for Blog",
      "description": "Analyze a research topic and suggest blog angles",
      "tags": ["analysis", "blog", "content"]
    }
  ],
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  }
}
```

### 3. Sending Messages to Agents

```bash
# Send a task to discover AI topics
curl -X POST https://chained-academic-research-sguacxy5gq-uc.a.run.app/a2a/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "parts": [{"text": "Find AI research topics"}]
    }
  }'

# Response:
{
  "id": "task-abc123",
  "status": {
    "state": "completed",
    "timestamp": "2025-11-27T14:00:00Z",
    "message": {
      "role": "agent",
      "parts": [{"text": "Found 3 research topics. Recommended: Large Language Model Reasoning Capabilities"}]
    }
  },
  "artifacts": [
    {
      "name": "research-findings",
      "type": "application/json",
      "data": "{...topics and analyses...}"
    }
  ]
}
```

## The Three ADK Agents in Chained

### 1. Academic Research Agent (Port 8081)
**Purpose:** Discovers and analyzes academic research topics for blog content

**Skills:**
- `discover-topics`: Find trending research topics
- `analyze-topic`: Analyze a topic for blog potential

**Use Case Example:**
```
User: "Find AI research topics"
Agent: Discovers LLM reasoning, multimodal models, AI safety topics
```

### 2. Blog Writer Agent (Port 8082)
**Purpose:** Writes engaging blog posts from research and trend data

**Skills:**
- `write-blog`: Generate a complete blog post
- `deploy-blog`: Deploy to the website

**Use Case Example:**
```
User: "Write a blog about LLM reasoning"
Agent: Creates structured blog with SEO optimization
```

### 3. Google Trends Agent (Port 8083)
**Purpose:** Analyzes Google Trends data to identify trending topics for SEO

**Skills:**
- `analyze-trends`: Analyze Google Trends data
- `get-keywords`: Extract trending keywords

**Use Case Example:**
```
User: "Get trending AI keywords"
Agent: Returns SEO-optimized keywords based on trends
```

## Local Development with Dev UI

You can run the ADK agents locally for development:

```bash
# Navigate to the agents directory
cd infrastructure/docker/adk-agents

# Install dependencies
pip install fastapi uvicorn httpx pydantic

# Start agents in separate terminals
# Terminal 1:
python academic-research/agent.py  # Runs on port 8081

# Terminal 2:
python google-trends/agent.py      # Runs on port 8083

# Terminal 3:
python blog-writer/agent.py        # Runs on port 8082

# Access the Dev UI locally
open http://localhost:8081/  # Academic Research
open http://localhost:8082/  # Blog Writer
open http://localhost:8083/  # Google Trends
```

## Pipeline Orchestration

The agents work together in a pipeline orchestrated by GitHub Actions:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Academic      │     │    Google       │     │     Blog        │
│   Research      │────▶│    Trends       │────▶│    Writer       │
│   Agent         │     │    Agent        │     │    Agent        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
     Discover             Analyze SEO           Write & Publish
     Topics               Trends                Blog Post
```

**Workflow:** `adk-a2a-blog-pipeline.yml` runs every 6 hours to:
1. Trigger Academic Research Agent to find topics
2. Send topics to Google Trends Agent for SEO analysis
3. Pass combined data to Blog Writer Agent
4. Blog Writer creates and optionally deploys content

## ADK Dev UI Features (Full Version)

The full Google ADK Web Dev UI (available at [github.com/google/adk-web](https://github.com/google/adk-web)) provides:

### Visual Development and Debugging
- Interactive cockpit for developers
- Visual flow of events, prompts, tool calls, and responses
- Chronological and hierarchical views for tracing logic

### Multi-Agent Support
- Build single agents or multi-agent hierarchies
- Coordinate delegations between agents
- Drag-and-drop workflow design

### Session Management
- Manage session histories (conversation context)
- Agent memory (long-term context)
- Artifacts (files, images, PDFs)

### Evaluation and Testing
- Run test cases
- Inspect inputs/outputs at each step
- Automated scoring tools

## Cloud Run Deployment

The agents are deployed via Terraform configuration in `infrastructure/terraform/adk-agents.tf`:

```hcl
resource "google_cloud_run_v2_service" "academic_research" {
  name     = "chained-academic-research"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/academic-research:latest"
      
      # Resources
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
      
      # Health probe
      startup_probe {
        http_get {
          path = "/health"
          port = 8080
        }
      }
    }
  }
}
```

## Monitoring and Observability

### Health Checks
```bash
# Check all agents
for agent in academic-research blog-writer google-trends; do
  curl https://chained-${agent}-sguacxy5gq-uc.a.run.app/health
done
```

### Cloud Monitoring
- **Latency metrics:** Cloud Run → Metrics
- **Error rates:** Cloud Run → Logs
- **Traces:** Cloud Trace → Traces

### GitHub Actions Logs
View pipeline execution at:
- [Workflow Runs](https://github.com/enufacas/Chained/actions/workflows/adk-a2a-blog-pipeline.yml)
- [Deploy Logs](https://github.com/enufacas/Chained/actions/workflows/deploy-adk-agents.yml)

## Security Considerations

1. **API Keys:** Stored in Secret Manager (GEMINI_API_KEY, GOOGLE_API_KEY)
2. **Service Accounts:** Minimal permissions per agent
3. **Public Access:** Currently public (roles/run.invoker for allUsers)
4. **HTTPS:** All Cloud Run endpoints use HTTPS

## Related Documentation

- [ADK A2A Pipeline Implementation](ADK_A2A_PIPELINE_IMPLEMENTATION.md) - Full pipeline details
- [Infrastructure README](../infrastructure/README.md) - GCP infrastructure
- [Agent Definitions](../infrastructure/docker/adk-agents/README.md) - Agent implementation details

## External References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Web UI (Full Dev UI)](https://github.com/google/adk-web)
- [A2A Protocol Specification](https://a2a-protocol.org/)
- [Cloud Run Deployment Guide](https://google.github.io/adk-docs/deploy/cloud-run/)
