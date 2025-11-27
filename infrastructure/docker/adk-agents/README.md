# ADK A2A Blog Pipeline

This directory contains ADK-based A2A (Agent-to-Agent) agents for an autonomous blog writing pipeline.

## Overview

The pipeline consists of three specialized agents that communicate using the A2A protocol:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Academic      │     │    Google       │     │     Blog        │
│   Research      │────▶│    Trends       │────▶│    Writer       │
│   Agent         │     │    Agent        │     │    Agent        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
     Discover             Analyze SEO           Write & Publish
     Topics               Trends                Blog Post
```

## Agents

### 1. Academic Research Agent
**Purpose**: Discovers and analyzes academic research topics for blog content.

- **Port**: 8081
- **Skills**:
  - `discover-topics`: Find trending research topics
  - `analyze-topic`: Analyze a topic for blog potential

### 2. Google Trends Agent
**Purpose**: Analyzes Google Trends data to identify trending topics for SEO.

- **Port**: 8083
- **Skills**:
  - `analyze-trends`: Analyze Google Trends data
  - `get-keywords`: Extract trending keywords

### 3. Blog Writer Agent
**Purpose**: Writes engaging blog posts from research and trend data.

- **Port**: 8082
- **Skills**:
  - `write-blog`: Generate a complete blog post
  - `deploy-blog`: Deploy to the website

## A2A Protocol Compliance

Each agent implements the A2A Protocol specification:

| Spec Section | Element | Implementation |
|--------------|---------|----------------|
| §4.4.1 | AgentCard | `GET /.well-known/agent.json` |
| §3.1.1 | SendMessage | `POST /a2a/tasks` |
| §4.1.1 | Task | Response with id, status, artifacts |
| §4.1.9 | Artifact | JSON/text outputs |

## Running Locally

### Prerequisites
```bash
pip install fastapi uvicorn httpx pydantic
```

### Start Agents
```bash
# Terminal 1 - Academic Research
python academic-research/agent.py

# Terminal 2 - Google Trends
python google-trends/agent.py

# Terminal 3 - Blog Writer
python blog-writer/agent.py
```

### Run Pipeline
```bash
python orchestrator.py
```

## Deployment to Cloud Run

### Using Terraform
```bash
cd infrastructure/terraform

terraform init
terraform plan -var="project_id=YOUR_PROJECT"
terraform apply
```

### Using GitHub Actions
The `deploy-adk-agents.yml` workflow automatically deploys agents when changes are pushed.

## Scheduled Pipeline

The `adk-a2a-blog-pipeline.yml` workflow runs every 6 hours:

```yaml
schedule:
  - cron: '0 */6 * * *'
```

## Observability

### Health Checks
Each agent exposes a `/health` endpoint:
```bash
curl http://localhost:8081/health
```

### Agent Cards
Discover agent capabilities:
```bash
curl http://localhost:8081/.well-known/agent.json
```

### ADK Dev UI
When deployed to Cloud Run, the ADK Dev UI is accessible at each service's root URL.

### Cloud Monitoring
- Latency metrics: Cloud Run → Metrics
- Error rates: Cloud Run → Logs
- Traces: Cloud Trace → Traces

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Agent port | 8081/8082/8083 |
| `GEMINI_API_KEY` | Gemini API key (optional) | - |
| `GOOGLE_API_KEY` | Google API key (optional) | - |
| `WEBSITE_DEPLOY_URL` | Blog deployment URL | GitHub Pages URL |

### Secrets (Cloud Run)
Store API keys in Secret Manager and reference in Terraform:
```hcl
variable "gemini_api_key_secret" {
  description = "Secret Manager resource for Gemini API key"
  type        = string
}
```

## Pipeline Flow

1. **Academic Research Agent** receives a request to find topics
2. Returns research findings as A2A artifacts
3. **Google Trends Agent** analyzes trends for the discovered topics
4. Returns SEO recommendations as artifacts
5. **Blog Writer Agent** writes a blog post incorporating both
6. Deploys the post to GitHub Pages
7. Returns deployment confirmation

## Example Usage

### Send Message to Agent
```python
import httpx

response = httpx.post(
    "http://localhost:8081/a2a/tasks",
    json={
        "message": {
            "role": "user",
            "parts": [{"text": "Find AI research topics"}]
        }
    }
)
task = response.json()
print(task["artifacts"])
```

### Run Full Pipeline
```python
from orchestrator import BlogPipelineOrchestrator
import asyncio

async def main():
    orchestrator = BlogPipelineOrchestrator()
    result = await orchestrator.run_pipeline()
    print(f"Success: {result['success']}")

asyncio.run(main())
```

## References

- [Google ADK Samples](https://github.com/google/adk-samples)
- [A2A Protocol](https://a2a-protocol.org/)
- [Cloud Run Deployment](https://google.github.io/adk-docs/deploy/cloud-run/)
- [ADK Documentation](https://google.github.io/adk-docs/)
