# A2A UI Feature Documentation

**Last Updated**: 2025-11-30  
**Status**: 🚀 **Active Development**  
**Live URL**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/

---

## Overview

The A2A UI (Agent-to-Agent User Interface) is a Next.js application that provides:
- **Interactive Chat** with AI assistant powered by CopilotKit and Vertex AI
- **Real-time Pipeline Visualization** showing A2A agent coordination
- **Deep Dive Capabilities** for inspecting pipeline runs and artifacts
- **Agent Health Monitoring** for deployed GCP Cloud Run agents

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AG-UI Frontend (Next.js)                      │
│                  CopilotKit v1.8.14 + Vertex AI                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Chat Panel    │  │  Agent Status   │  │ Pipeline        │ │
│  │   (CopilotKit)  │  │  (Health Check) │  │ Outcomes        │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                     │                     │          │
│           ▼                     ▼                     ▼          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    API Routes                                ││
│  │  /api/copilotkit  /api/pipeline  /api/agent  /api/activity  ││
│  └─────────────────────────────────────────────────────────────┘│
│                               │                                  │
└───────────────────────────────┼──────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GCP Cloud Run Agents                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🔬 Academic Research    📈 Google Trends    ✍️ Blog Writer      │
│     Agent                   Agent               Agent            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. API Routes (`/src/app/api/`)

| Route | Purpose | Data Source |
|-------|---------|-------------|
| `/api/pipeline` | Pipeline CRUD operations | In-memory store |
| `/api/agent` | Direct agent interaction | Cloud Run agents |
| `/api/activity` | Agent health monitoring | Cloud Run health endpoints |
| `/api/copilotkit` | AI chat backend | Vertex AI / Gemini |

### 2. UI Components (`/src/components/`)

| Component | Purpose |
|-----------|---------|
| `RealTimeAgentActivity` | Shows live agent health status |
| `PipelineOutcomes` | Lists pipeline results and blog posts |
| `PipelineDetailView` | Deep dive into individual pipeline runs |
| `InteractivePipelineChat` | A2A middleware chat component |

### 3. Main Page (`/src/app/page.tsx`)

The unified single-page application with:
- CopilotKit actions for pipeline operations
- Real-time status updates
- API status monitoring

## Features

### ✅ Implemented

1. **Pipeline Creation** - Create pipelines via chat
2. **Agent Interaction** - Direct @agent-name communication
3. **Pipeline Status** - Real-time progress tracking
4. **Pipeline Analysis** - Query any pipeline by topic/ID
5. **Agent Health Monitoring** - Live Cloud Run status
6. **Pipeline Detail View** - Click-to-expand with lifecycle visualization
7. **A2A Steps Deep Dive** - Task IDs, artifacts, execution times
8. **Enhanced Agent Prompts** - Detailed prompts for quality content (NEW)

### 🚧 In Progress

- Run history persistence
- Artifact expansion and inspection

### 📋 Planned

- Multi-topic pipeline orchestration
- Content review and editing
- Historical pipeline browser with search
- Voice/multi-modal interface

## Content Quality

### Improved Agent Prompts

The pipeline now uses **detailed, structured prompts** to get better content from agents:

#### Research Agent Prompt
Requests 10 specific categories:
- Comprehensive overview, key concepts, current state
- Domain classification, target audience
- Key statistics/facts, notable examples
- Important keywords, expert perspectives, future directions

#### Trends Agent Prompt  
Requests detailed SEO analysis:
- Top 10-15 trending keywords, related queries
- Rising trends, geographic interest, seasonal patterns
- Competitor keywords, long-tail opportunities
- Content gaps, title suggestions

#### Blog Writer Agent Prompt
Structured 7-section template (2000-2500 words):
1. Compelling Introduction (150-200 words)
2. Background & Context (300-400 words)
3. Deep Dive: Core Concepts (500-600 words)
4. Practical Applications (400-500 words)
5. Challenges & Considerations (200-300 words)
6. Future Outlook (200-300 words)
7. Conclusion & Call to Action (100-150 words)

Plus quality checklist: no generic content, require examples, specific data points.

## Data Model

### Pipeline Interface

```typescript
interface Pipeline {
  id: string;
  topic: string;
  status: "pending" | "running" | "completed" | "failed";
  createdAt: string;
  updatedAt: string;
  progress: number;
  currentPhase: "research" | "trends" | "writing" | "publishing" | "complete";
  results?: {
    research?: { topic: string; domain: string; keywords: string[] };
    trends?: { trendingKeywords: string[]; recommendedFocus: string };
    blog?: { title: string; url: string; wordCount: number };
  };
  // Enhanced A2A step details for deep dive
  a2aSteps?: A2AStepDetail[];
  totalDurationMs?: number;
}

interface A2AStepDetail {
  taskId: string;
  agentName: string;
  phase: string;
  status: "pending" | "running" | "completed" | "failed";
  startTime: string;
  endTime?: string;
  durationMs?: number;
  message?: string;
  artifacts: Array<{
    name: string;
    type: string;
    data: string;
    preview?: string;
  }>;
  rawResponse?: object;
}
```

## Environment Variables

Required for full functionality:

```bash
# Vertex AI (for Cloud Run deployment)
USE_VERTEX_AI=true
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1

# Agent URLs (Cloud Run service URLs)
AGENT_ACADEMIC_RESEARCH_URL=https://chained-academic-research-xxx-uc.a.run.app
AGENT_GOOGLE_TRENDS_URL=https://chained-google-trends-xxx-uc.a.run.app
AGENT_BLOG_WRITER_URL=https://chained-blog-writer-xxx-uc.a.run.app

# Alternative: Direct API keys (for local development)
GEMINI_API_KEY=your-key
# or
OPENAI_API_KEY=your-key
```

## Development

### Local Setup

```bash
cd infrastructure/docker/ag-ui-frontend
npm install
npm run dev
```

### Build & Deploy

```bash
# Build Docker image
docker build -t ag-ui-frontend .

# Deploy to Cloud Run
gcloud run deploy chained-ag-ui-frontend \
  --image gcr.io/PROJECT_ID/ag-ui-frontend \
  --platform managed \
  --region us-central1
```

### Testing

```bash
npm run lint
npm run build
```

## Related PRs

| PR | Description | Impact |
|----|-------------|--------|
| #3430 | Update Vertex AI model to gemini-2.0-flash | Fixed 404 errors |
| #3432 | Change Vertex AI API from v1beta to v1 | Resolved API issues |
| #3433 | Regenerate package-lock.json | Fixed CI/CD |
| #3438 | Fix agent response canned fallbacks | Real data only |
| #3444 | Add pipeline detail view click-to-expand | Better UX |
| #3445 | Enhance outcomes with real-time polling | Live updates |
| #3446 | A2A steps deep dive, artifacts (this PR) | Deep dive capability |

## Troubleshooting

### Chat Not Working

1. Check `/api/copilotkit` GET endpoint returns `available: true`
2. Verify `USE_VERTEX_AI=true` for Cloud Run
3. Check GCP service account permissions

### Agents Showing Offline

1. Verify Cloud Run service is deployed
2. Check agent URL environment variables
3. Test health endpoint directly: `curl $AGENT_URL/health`

### Pipeline Stuck

1. Check Cloud Run logs for agent errors
2. Verify agent can reach external APIs (Google Trends, etc.)
3. Check `/api/pipeline?id=xxx` for error details

## Documentation

- [A2A Success History](../a2a/A2A_SUCCESS_HISTORY.md) - Milestone tracking
- [A2A Status](../a2a/A2A_STATUS.md) - Overall implementation status
- [A2A Integration Design](../a2a/A2A_INTEGRATION_DESIGN.md) - Architecture details

---

*This documentation should be kept up-to-date with each PR that modifies the A2A UI.*
