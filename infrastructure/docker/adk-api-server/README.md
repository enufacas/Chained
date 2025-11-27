# ADK API Server

API server that bridges [google/adk-web](https://github.com/google/adk-web) to A2A protocol-based agents deployed on GCP Cloud Run.

## Overview

The ADK API Server implements the ADK API interface expected by google/adk-web, allowing you to use the full ADK developer UI with your A2A agents.

```
┌─────────────┐    HTTP/SSE    ┌──────────────────┐    A2A Protocol   ┌─────────────┐
│  adk-web    │◀──────────────▶│  ADK API Server  │◀─────────────────▶│  A2A Agents │
│  (Angular)  │                │  (FastAPI)       │                    │  (Cloud Run)│
└─────────────┘                └──────────────────┘                    └─────────────┘
```

## Features

- **ADK API Compatibility**: Implements the API expected by google/adk-web
- **Session Management**: In-memory (dev) or Firestore (production) session storage
- **Agent Discovery**: Automatically discovers agents from environment variables
- **SSE Streaming**: Server-Sent Events support for real-time responses
- **CORS Support**: Configurable CORS for cross-origin requests

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/list-apps` | GET | List available agent applications |
| `/apps/{app}/users/{user}/sessions` | POST | Create a new session |
| `/apps/{app}/users/{user}/sessions` | GET | List user sessions |
| `/apps/{app}/users/{user}/sessions/{id}` | GET | Get session details |
| `/apps/{app}/users/{user}/sessions/{id}` | DELETE | Delete session |
| `/run` | POST | Run agent synchronously |
| `/run_sse` | POST | Run agent with SSE streaming |
| `/health` | GET | Health check |

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8080` |
| `HOST` | Server host | `0.0.0.0` |
| `ENVIRONMENT` | Environment name | `development` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `*` |
| `USE_FIRESTORE` | Use Firestore for session storage | `false` |
| `GCP_PROJECT_ID` | GCP Project ID (for Firestore) | - |

### Agent Configuration

Agents are discovered from environment variables:

```bash
# Format: AGENT_<NAME>_URL and AGENT_<NAME>_DESCRIPTION
AGENT_ACADEMIC_RESEARCH_URL=https://chained-academic-research-xxx.a.run.app
AGENT_ACADEMIC_RESEARCH_DESCRIPTION=Discovers research topics

AGENT_BLOG_WRITER_URL=https://chained-blog-writer-xxx.a.run.app
AGENT_BLOG_WRITER_DESCRIPTION=Writes blog posts

AGENT_GOOGLE_TRENDS_URL=https://chained-google-trends-xxx.a.run.app
AGENT_GOOGLE_TRENDS_DESCRIPTION=Analyzes Google Trends
```

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
cd infrastructure/docker/adk-api-server

# Install dependencies
pip install -r requirements.txt

# Configure agents (example)
export AGENT_ACADEMIC_RESEARCH_URL=http://localhost:8081
export AGENT_BLOG_WRITER_URL=http://localhost:8082
export AGENT_GOOGLE_TRENDS_URL=http://localhost:8083

# Run server
python server.py
```

### Testing

```bash
# Health check
curl http://localhost:8080/health

# List available apps
curl http://localhost:8080/list-apps

# Create session
curl -X POST http://localhost:8080/apps/academic-research/users/user-1/sessions

# Run agent
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{
    "appName": "academic-research",
    "userId": "user-1",
    "sessionId": "session-1",
    "newMessage": "Find AI research topics"
  }'
```

## Docker Build

```bash
cd infrastructure/docker/adk-api-server

docker build -t adk-api-server .

docker run -p 8080:8080 \
  -e AGENT_ACADEMIC_RESEARCH_URL=https://your-agent.run.app \
  adk-api-server
```

## Deployment

The ADK API Server is deployed to Cloud Run via the `deploy-adk-agents.yml` workflow. Terraform configuration is in `infrastructure/terraform/adk-agents.tf`.

## Using with adk-web

1. Clone [google/adk-web](https://github.com/google/adk-web)
2. Configure the API URL to point to your deployed ADK API Server
3. Run `npm start`
4. Access the UI at http://localhost:4200

## Files

- `server.py` - Main FastAPI server implementing ADK API
- `session_store.py` - Session management (in-memory and Firestore)
- `a2a_adapter.py` - A2A protocol adapter for agent communication
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container build configuration

## Related Documentation

- [ADK Dev UI Guide](../../../docs/ADK_DEV_UI_GUIDE.md)
- [ADK Agents README](../adk-agents/README.md)
- [google/adk-web](https://github.com/google/adk-web)
- [A2A Protocol](https://a2a-protocol.org/)
