# ADK API Server

API server that bridges [google/adk-web](https://github.com/google/adk-web) to A2A protocol-based agents deployed on GCP Cloud Run. Now includes a built-in **Agent Console GUI** for easy interaction with your agents.

## Overview

The ADK API Server implements the ADK API interface expected by google/adk-web, allowing you to use the full ADK developer UI with your A2A agents. It also provides a standalone web GUI following modern dashboard design best practices.

```
┌─────────────────┐    HTTP/SSE    ┌──────────────────┐    A2A Protocol   ┌─────────────┐
│  Agent Console  │◀──────────────▶│  ADK API Server  │◀─────────────────▶│  A2A Agents │
│  (Built-in GUI) │                │  (FastAPI)       │                    │  (Cloud Run)│
└─────────────────┘                └──────────────────┘                    └─────────────┘
         ▲                                  ▲
         │                                  │
┌────────┴────────┐              ┌──────────┴──────────┐
│   adk-web       │              │  CopilotKit/AG-UI   │
│   (Angular)     │              │  (React/Angular)    │
└─────────────────┘              └─────────────────────┘
```

## Features

- **Built-in Agent Console GUI**: Modern, responsive chat interface at the root URL
- **ADK API Compatibility**: Implements the API expected by google/adk-web
- **AG-UI Protocol Ready**: Compatible with [AG-UI](https://docs.ag-ui.com/) for advanced frontends
- **Session Management**: In-memory (dev) or Firestore (production) session storage
- **Agent Discovery**: Automatically discovers agents from environment variables
- **SSE Streaming**: Server-Sent Events support for real-time responses
- **CORS Support**: Configurable CORS for cross-origin requests

## Built-in GUI

Access the Agent Console GUI by navigating to the root URL (`/`). The GUI provides:

- **Agent Selection**: Browse and select from available agents
- **Real-time Chat**: Interactive conversation with streaming responses
- **Session Management**: Automatic session creation and management
- **API Documentation**: View available endpoints
- **Statistics**: Agent count and message metrics

### Design Standards

The GUI follows modern web interface best practices:
- **Dark Theme**: Professional dark color scheme with purple accents
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Accessibility**: Semantic HTML, keyboard navigation, WCAG-compliant contrast
- **Real-time Updates**: Live status indicators and streaming responses

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | **Agent Console GUI** (HTML) |
| `/api` | GET | API information (JSON) |
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

Then open http://localhost:8080 in your browser to access the Agent Console GUI.

### Testing

```bash
# Health check
curl http://localhost:8080/health

# API info (JSON)
curl http://localhost:8080/api

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

## Frontend Integration Options

### Option 1: Built-in GUI (Default)

The server includes a built-in Agent Console GUI. Just navigate to the root URL.

### Option 2: google/adk-web

1. Clone [google/adk-web](https://github.com/google/adk-web)
2. Configure the API URL to point to your deployed ADK API Server
3. Run `npm start`
4. Access the UI at http://localhost:4200

### Option 3: CopilotKit with AG-UI Protocol

For advanced agentic UIs with features like generative UI, shared state, and human-in-the-loop workflows:

1. Install CopilotKit packages:
```bash
npm install @copilotkit/react-core @copilotkit/react-ui
```

2. Configure the CopilotKit runtime to use the ADK API Server:
```typescript
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";

export default function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <CopilotChat />
    </CopilotKit>
  );
}
```

For full AG-UI protocol integration, see:
- [AG-UI Protocol Documentation](https://docs.ag-ui.com/)
- [CopilotKit ADK Integration](https://docs.copilotkit.ai/adk)
- [AG-UI ADK Middleware](https://pypi.org/project/ag-ui-adk/)

## Files

- `server.py` - Main FastAPI server implementing ADK API with GUI
- `templates/index.html` - Agent Console GUI template
- `session_store.py` - Session management (in-memory and Firestore)
- `a2a_adapter.py` - A2A protocol adapter for agent communication
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container build configuration

## Related Documentation

- [ADK Dev UI Guide](../../../docs/ADK_DEV_UI_GUIDE.md)
- [ADK Agents README](../adk-agents/README.md)
- [google/adk-web](https://github.com/google/adk-web)
- [A2A Protocol](https://a2a-protocol.org/)
- [AG-UI Protocol](https://docs.ag-ui.com/)
- [CopilotKit](https://docs.copilotkit.ai/)
