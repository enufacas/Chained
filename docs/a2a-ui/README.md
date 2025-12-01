# A2A UI Feature Documentation

**Last Updated**: 2025-12-01  
**Status**: 🚀 **Active Development**  
**Live URL**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/

---

## Overview

The A2A UI (Agent-to-Agent User Interface) is a Next.js application that provides:
- **Interactive Chat** with AI assistant powered by CopilotKit and Vertex AI
- **Real-time Pipeline Visualization** showing A2A agent coordination
- **Deep Dive Capabilities** for inspecting pipeline runs and artifacts
- **Agent Health Monitoring** for deployed GCP Cloud Run agents
- **Agent Canvas** for visual team building with turn-based execution
- **Multi-Agent Team Orchestration** with configurable execution modes

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AG-UI Frontend (Next.js)                      │
│                  CopilotKit v1.8.14 + Vertex AI                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Chat Panel    │  │  Agent Canvas   │  │ Pipeline        │ │
│  │   (CopilotKit)  │  │  (Team Builder) │  │ Outcomes        │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                     │                     │          │
│           ▼                     ▼                     ▼          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    API Routes                                ││
│  │  /api/copilotkit  /api/pipeline  /api/team  /api/registry   ││
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
│  🔍 Code Reviewer       📊 Data Analyst      🎨 Image Generator  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. API Routes (`/src/app/api/`)

| Route | Purpose | Data Source |
|-------|---------|-------------|
| `/api/pipeline` | Pipeline CRUD operations | In-memory store |
| `/api/team` | Team orchestration & custom workflows | In-memory store |
| `/api/registry` | Agent registry & health status | Cloud Run agents |
| `/api/agent` | Direct agent interaction | Cloud Run agents |
| `/api/activity` | Agent health monitoring | Cloud Run health endpoints |
| `/api/copilotkit` | AI chat backend | Vertex AI / Gemini |

### 2. UI Components (`/src/components/`)

| Component | Purpose |
|-----------|---------|
| `AgentCanvas` | Visual team building with goal input & execution config |
| `RecipeBuilder` | Recipe-based workflow selection |
| `TeamVisualization` | Real-time team execution view |
| `TurnIndicator` | Turn progress and agent status |
| `RealTimeAgentActivity` | Shows live agent health status |
| `PipelineOutcomes` | Lists pipeline results and blog posts |
| `PipelineDetailView` | Deep dive into individual pipeline runs |
| `InteractivePipelineChat` | A2A middleware chat component |

### 3. Team Page (`/src/app/team/page.tsx`)

Multi-agent orchestration with:
- Agent Canvas for team selection
- Turn configuration (1-5 turns per agent)
- Execution mode (sequential/parallel)
- Real-time execution visualization

## Features

### ✅ Implemented

1. **Pipeline Creation** - Create pipelines via chat
2. **Agent Interaction** - Direct @agent-name communication
3. **Pipeline Status** - Real-time progress tracking
4. **Pipeline Analysis** - Query any pipeline by topic/ID
5. **Agent Health Monitoring** - Live Cloud Run status
6. **Pipeline Detail View** - Click-to-expand with lifecycle visualization
7. **A2A Steps Deep Dive** - Task IDs, artifacts, execution times
8. **Enhanced Agent Prompts** - Detailed prompts for quality content
9. **Agent Canvas** - Visual team builder with text input (NEW)
10. **Turn-Based Execution** - 2-5 turns per agent configuration (NEW)
11. **Execution Modes** - Sequential and parallel execution (NEW)
12. **All 6 Agents Configured** - Including data-analyst & image-generator (NEW)

### 🚧 In Progress

- Run history persistence
- Artifact expansion and inspection

### 📋 Planned

- Multi-topic pipeline orchestration
- Content review and editing
- Historical pipeline browser with search
- Voice/multi-modal interface

## Agent Canvas (New Feature)

### Team Building
The Agent Canvas allows visual team composition:
- Click agents to add/remove from team
- Drag-and-drop support
- Category filters (Research, SEO, Content, Development, Analytics, Visual)
- Real-time health status indicators

### Execution Configuration
When a team is selected, configure:

1. **Turns Per Agent** (1-5, default 2)
   - Each agent executes for the specified number of turns
   - More turns = more refined output

2. **Execution Mode**
   - **Sequential**: Agents run one at a time in order
   - **Parallel**: All agents run simultaneously per turn

### Starting Workflows
Enter a goal in the text input and click "Start" to begin execution.

Example:
```
Team: [Academic Research, Data Analyst, Blog Writer]
Turns: 2
Mode: Sequential
Goal: "Analyze trends in quantum computing and write an educational blog post"
```

## Configured Agents

All 6 agents are now configured with Cloud Run URLs:

| Agent | Icon | Category | URL |
|-------|------|----------|-----|
| Academic Research | 🔬 | Research | https://chained-academic-research-sguacxy5gq-uc.a.run.app |
| Google Trends | 📈 | SEO | https://chained-google-trends-sguacxy5gq-uc.a.run.app |
| Blog Writer | ✍️ | Content | https://chained-blog-writer-sguacxy5gq-uc.a.run.app |
| Code Reviewer | 🔍 | Development | https://chained-code-reviewer-sguacxy5gq-uc.a.run.app |
| Data Analyst | 📊 | Analytics | https://chained-data-analyst-sguacxy5gq-uc.a.run.app |
| Image Generator | 🎨 | Visual | https://chained-image-generator-sguacxy5gq-uc.a.run.app |

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

### Team Session Interface (New)

```typescript
interface TeamSession {
  id: string;
  recipeId: string;
  recipeName: string;
  goal: string;
  status: "pending" | "running" | "completed" | "failed";
  currentTurn: number;
  totalTurns: number;
  createdAt: string;
  updatedAt: string;
  context: Record<string, unknown>;
  turnResults: TurnResult[];
  config?: ExecutionConfig;
}

interface ExecutionConfig {
  maxTurnsPerAgent: number;  // 1-5, default 2
  executionMode: "sequential" | "parallel";
}

interface TurnResult {
  stepIndex: number;
  agentId: string;
  agentName: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  startedAt: string;
  completedAt?: string;
  durationMs?: number;
  taskId?: string;
  message?: string;
  artifacts: Array<{ name: string; type: string; data: string }>;
  error?: string;
  turnNumber?: number;
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
AGENT_CODE_REVIEWER_URL=https://chained-code-reviewer-xxx-uc.a.run.app
AGENT_DATA_ANALYST_URL=https://chained-data-analyst-xxx-uc.a.run.app
AGENT_IMAGE_GENERATOR_URL=https://chained-image-generator-xxx-uc.a.run.app

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
| #3446 | A2A steps deep dive, artifacts | Deep dive capability |
| #3459+ | Configure data-analyst & image-generator, Agent Canvas input, turn config | Team orchestration |

## Troubleshooting

### Chat Not Working

1. Check `/api/copilotkit` GET endpoint returns `available: true`
2. Verify `USE_VERTEX_AI=true` for Cloud Run
3. Check GCP service account permissions

### Agents Showing Not Configured

1. Verify Cloud Run service is deployed for that agent
2. Check agent URL environment variables in `.env.local`
3. For new agents (data-analyst, image-generator), ensure Terraform deployment is complete

### Agents Showing Offline

1. Verify Cloud Run service is deployed
2. Check agent URL environment variables
3. Test health endpoint directly: `curl $AGENT_URL/health`

### Pipeline Stuck

1. Check Cloud Run logs for agent errors
2. Verify agent can reach external APIs (Google Trends, etc.)
3. Check `/api/pipeline?id=xxx` for error details

### Team Execution Issues

1. Ensure agents are configured (not showing ⚠️ warning)
2. Check execution mode (sequential may take longer)
3. Monitor session status via `/api/team?session=xxx`

## Documentation

- [A2A Success History](../a2a/A2A_SUCCESS_HISTORY.md) - Milestone tracking
- [A2A Status](../a2a/A2A_STATUS.md) - Overall implementation status
- [A2A Integration Design](../a2a/A2A_INTEGRATION_DESIGN.md) - Architecture details

---

*This documentation should be kept up-to-date with each PR that modifies the A2A UI.*
