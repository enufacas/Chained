---
applyTo:
  - "infrastructure/docker/ag-ui-frontend/**"
---

# A2A UI Data Sources - Meta Rule

## CRITICAL: Avoid GitHub API Integration Unless Explicitly Requested

The A2A UI frontend (`infrastructure/docker/ag-ui-frontend/`) should **ALWAYS** source data from **GCP Cloud Run deployed agents**, not GitHub.

### Default Data Sources (Use These)

1. **GCP Cloud Run Agents** - Primary source for all agent activity
   - Academic Research Agent: `/health`, `/.well-known/agent.json`
   - Google Trends Agent: `/health`, `/.well-known/agent.json`
   - Blog Writer Agent: `/health`, `/.well-known/agent.json`
   - ADK API Server: `/health`

2. **GCP Cloud Storage** - For blog posts and artifacts
   - Blog URL format: `https://storage.googleapis.com/${GCP_PROJECT_ID}-chained-blog/posts/${slug}.html`

3. **Local Pipeline State** - In-memory pipeline tracking

### Forbidden Data Sources (Unless Explicitly Requested)

❌ **DO NOT USE** without explicit user request:
- GitHub Actions API (`api.github.com/repos/.../actions/runs`)
- GitHub Workflow runs
- GitHub Issues API
- Any GitHub API integration for activity tracking

### Why This Matters

1. **The chat talks to GCP agents** - The UI should reflect what's actually running
2. **GitHub workflows are CI/CD** - They're not the production system
3. **Consistency** - Users see the same agents the chat interacts with
4. **Accuracy** - GCP agent health is real-time factual data

### Implementation Pattern

```typescript
// ✅ CORRECT: Source from GCP Cloud Run agents
const agentHealth = await fetch(`${AGENT_URL}/health`);
const agentCard = await fetch(`${AGENT_URL}/.well-known/agent.json`);

// ❌ INCORRECT: Don't source from GitHub unless explicitly asked
// const workflows = await fetch('https://api.github.com/repos/.../actions/runs');
```

### Environment Variables

Required for GCP integration:
- `NEXT_PUBLIC_ADK_API_URL` - ADK API Server URL
- `AGENT_ACADEMIC_RESEARCH_URL` - Research agent URL
- `AGENT_GOOGLE_TRENDS_URL` - Trends agent URL  
- `AGENT_BLOG_WRITER_URL` - Blog writer agent URL
- `GCP_PROJECT_ID` - For blog bucket URL construction

### When GitHub Integration IS Appropriate

Only use GitHub API when the user **explicitly** asks for:
- "Show me GitHub workflow runs"
- "What's happening in GitHub Actions?"
- "Check the CI/CD status"
- "Look at the workflow history"

Otherwise, always default to GCP Cloud Run agent data.
