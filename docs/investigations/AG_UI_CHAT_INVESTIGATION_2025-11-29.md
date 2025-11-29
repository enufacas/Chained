# AG-UI Frontend Chat Investigation

**Date:** 2025-11-29  
**URL:** https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/interactive  
**Component:** AG-UI Frontend (CopilotKit + A2A Pipeline)

## Executive Summary

Investigation into why the chat feature is not working on the interactive page of the AG-UI Frontend. The analysis reveals **two root causes** and confirms that the **main page uses static/sample data**.

## Issues Identified

### Issue 1: Missing LLM API Key (Primary Cause)

**Status:** ⚠️ Configuration Required  
**Severity:** High  
**Impact:** Chat feature completely non-functional

The CopilotKit chat requires either a `GEMINI_API_KEY` or `OPENAI_API_KEY` environment variable to be set. Without this, the backend returns a 503 Service Unavailable error.

**Evidence:**
```json
{
  "llmProvider": "none"
}
```

**Console Error:**
```
Failed to load resource: the server responded with a status of 503 (Service Unavailable)
```

**Build Warning:**
```
Warning: Neither GEMINI_API_KEY nor OPENAI_API_KEY environment variable is set. CopilotKit chat will not work.
```

**Resolution:**
Set one of the following environment variables in Cloud Run deployment:
- `GEMINI_API_KEY` (preferred) - Uses Google Gemini 1.5 Flash
- `OPENAI_API_KEY` (fallback) - Uses OpenAI GPT-4

### Issue 2: A2A Backend Agents Unavailable

**Status:** ⚠️ Backend Services Down or Unreachable  
**Severity:** Medium  
**Impact:** Even with an LLM key, the A2A agent orchestration won't work

The A2A middleware requires connection to deployed backend agents:
- `https://chained-adk-api-server-sguacxy5gq-uc.a.run.app`
- `https://chained-academic-research-sguacxy5gq-uc.a.run.app`
- `https://chained-google-trends-sguacxy5gq-uc.a.run.app`
- `https://chained-blog-writer-sguacxy5gq-uc.a.run.app`

**Evidence:**
```json
{
  "adkApiServer": {"url": "...", "available": false},
  "agents": {
    "academicResearch": {"available": false},
    "googleTrends": {"available": false},
    "blogWriter": {"available": false}
  }
}
```

**Server Logs:**
```
Error fetching or parsing Agent Card:
TypeError: fetch failed
  cause: Error: getaddrinfo ENOTFOUND chained-academic-research-sguacxy5gq-uc.a.run.app
```

**UI Feedback:**
The UI correctly shows: "⚠️ A2A agents not available. Some features may be limited."

**Resolution:**
1. Verify the A2A backend services are deployed and running on Cloud Run
2. Check service account permissions and IAM roles
3. Ensure the agents expose `/health` endpoints correctly

## Data Source Analysis

### Main Page (`/`) - STATIC DATA

The main page uses **hardcoded sample data** for demonstration purposes:

```typescript
// Sample data - will be replaced with real API calls
const SAMPLE_RUNS: PipelineRun[] = [
  { id: 19776783774, runNumber: 9, createdAt: "2025-11-29T01:04:33Z", ... },
  { id: 19776000000, runNumber: 8, createdAt: "2025-11-28T18:04:33Z", ... },
  { id: 19775000000, runNumber: 7, createdAt: "2025-11-28T12:04:33Z", ... },
];

const SAMPLE_RESULT: PipelineData = {
  contextId: "blog-pipeline-20251129-010433",
  success: true,
  tasksCompleted: 3,
  research: { ... },
  trends: { ... },
  blog: { ... },
};
```

**Note:** There's a TODO comment indicating this should be replaced with API calls:
```typescript
// TODO: Replace sample data with API calls to fetch actual pipeline data
```

### Interactive Page (`/interactive`) - DYNAMIC DATA (when working)

The interactive page is designed to use **real-time data** from:
1. CopilotKit chat responses
2. A2A agent execution results

When working correctly, the page:
- Accepts user commands like "Write a blog post about AI agents"
- Orchestrates 3 specialized A2A agents (Research, Trends, Blog Writer)
- Shows real-time status updates as agents work
- Displays actual results from agent execution

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AG-UI Frontend (Next.js)                     │
│  ┌─────────────┐    ┌─────────────────────────────────────────┐ │
│  │   Main (/)  │    │        Interactive (/interactive)       │ │
│  │   Static    │    │    ┌─────────────────────────────┐      │ │
│  │   Sample    │    │    │   CopilotKit Chat + A2A     │      │ │
│  │   Data      │    │    │   Middleware Integration    │      │ │
│  └─────────────┘    │    └─────────────────────────────┘      │ │
│                     └─────────────────────────────────────────┘ │
│                                      │                          │
│                     ┌────────────────┼────────────────┐         │
│                     ▼                ▼                ▼         │
│              /api/copilotkit  /api/copilotkit-a2a              │
│                     │                │                          │
└─────────────────────┼────────────────┼──────────────────────────┘
                      │                │
                      ▼                ▼
              ┌───────────────┐  ┌──────────────────────┐
              │  LLM Provider │  │   A2A Backend        │
              │  (Gemini/     │  │   - ADK API Server   │
              │   OpenAI)     │  │   - Research Agent   │
              │               │  │   - Trends Agent     │
              │  ❌ NOT SET   │  │   - Blog Writer      │
              └───────────────┘  │                      │
                                 │  ❌ UNAVAILABLE      │
                                 └──────────────────────┘
```

## Recommendations

### Immediate Actions

1. **Set LLM API Key in Cloud Run:**
   ```bash
   gcloud run services update chained-ag-ui-frontend \
     --update-env-vars GEMINI_API_KEY=your_key \
     --region us-central1
   ```

2. **Verify A2A Backend Deployment:**
   ```bash
   # Check if services are running
   gcloud run services list --region us-central1
   
   # Check service logs
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chained-academic-research" --limit 50
   ```

### Future Improvements

1. **Replace Static Data on Main Page:**
   - Implement API calls to fetch actual pipeline run history
   - Connect to GitHub Actions API for real workflow run data
   - Consider caching for performance

2. **Add Better Error Handling:**
   - Show clearer error messages when LLM key is missing
   - Provide setup instructions directly in the UI
   - Add retry logic for A2A agent connections

3. **Health Check Enhancements:**
   - Add a dedicated status page showing all backend service health
   - Implement automatic reconnection when agents become available
   - Add monitoring/alerting for service availability

## Files Analyzed

- `infrastructure/docker/ag-ui-frontend/src/app/page.tsx` - Main page with static data
- `infrastructure/docker/ag-ui-frontend/src/app/interactive/page.tsx` - Interactive page
- `infrastructure/docker/ag-ui-frontend/src/components/InteractivePipelineChat.tsx` - Chat component
- `infrastructure/docker/ag-ui-frontend/src/app/api/copilotkit-a2a/route.ts` - A2A API route
- `infrastructure/docker/ag-ui-frontend/src/lib/copilotkit-config.ts` - LLM configuration
- `infrastructure/docker/ag-ui-frontend/README.md` - Documentation

## Test Results

| Test | Result | Notes |
|------|--------|-------|
| Build | ✅ Pass | With warning about missing API keys |
| Lint | ✅ Pass | No ESLint errors |
| Main Page Load | ✅ Pass | Static data displays correctly |
| Interactive Page Load | ✅ Pass | Chat UI renders |
| A2A Status Check | ⚠️ Warning | Shows "agents not available" banner |
| Send Chat Message | ❌ Fail | 503 error - no LLM key |

## Conclusion

The chat feature on the interactive page is not working due to **missing LLM API configuration** (GEMINI_API_KEY or OPENAI_API_KEY) and **unavailable A2A backend agents**. The main page displays static sample data for demonstration, while the interactive page is designed for real-time agent orchestration when properly configured.

---

*Investigation performed by @investigate-champion*
