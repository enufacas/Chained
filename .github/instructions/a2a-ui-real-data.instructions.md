---
applyTo:
  - "infrastructure/docker/ag-ui-frontend/**"
---

# A2A UI - Real Data Only Policy

## CRITICAL: No Simulated or Fake Data

The A2A UI (`infrastructure/docker/ag-ui-frontend/`) must **ALWAYS** use real data from actual A2A agent execution. **NO simulated, fake, mock, or demo data is permitted.**

## What This Means

### ❌ PROHIBITED
- Hardcoded demo pipeline data
- Simulated agent responses
- Mock API responses
- Fake blog URLs
- Canned/template responses in agent handlers
- `SAMPLE_DATA` or similar static data structures
- Demo IDs like `pipeline-demo-001`

### ✅ REQUIRED
- All pipeline data comes from real API calls
- All agent responses come from actual Cloud Run agents
- Blog posts are actually created and deployed to GCP Cloud Storage
- If an agent is unavailable, show an error - don't fake a response
- Empty states are OK - show "No pipelines" rather than fake data

## Implementation Guidelines

### Pipeline API (`/api/pipeline`)
```typescript
// ❌ BAD - Static demo data
const demoData = { id: "demo-001", topic: "Demo Topic" };

// ✅ GOOD - Only real data from activePipelines
const pipelines = Array.from(activePipelines.values());
```

### Agent API (`/api/agent`)
```typescript
// ❌ BAD - Canned responses
if (query.includes("trend")) {
  return "Here are some trends: AI, ML, etc.";
}

// ✅ GOOD - Call real A2A agent
const response = await fetch(`${agentUrl}/a2a/tasks`, {
  method: "POST",
  body: JSON.stringify(request),
});
```

### Frontend Components
```typescript
// ❌ BAD - Static initial data
const [data] = useState(SAMPLE_DATA);

// ✅ GOOD - Fetch from API
const [data, setData] = useState(null);
useEffect(() => {
  fetch("/api/pipeline").then(r => r.json()).then(setData);
}, []);
```

## Empty States

When no data is available, display appropriate empty states:
- "No pipelines yet. Create one to get started!"
- "Agent unavailable. Configure AGENT_*_URL to enable."
- Show loading states during actual API calls

## Error Handling

When real agents fail, show actual errors:
```typescript
// ✅ GOOD - Show real error
return `⚠️ Agent ${name} returned error: ${response.status}`;

// ❌ BAD - Hide error with fake success
return "Here's your analysis..."; // Fake response
```

## Why This Policy Exists

1. **Trust**: Users expect real data, not demonstrations
2. **Testing**: Simulated data masks real bugs
3. **Production**: What runs locally should match production
4. **Transparency**: Users should know when systems are unavailable

## Environment Configuration

Real functionality requires proper configuration:
```bash
# Agent URLs (required for agent calls)
AGENT_ACADEMIC_RESEARCH_URL=https://...
AGENT_GOOGLE_TRENDS_URL=https://...
AGENT_BLOG_WRITER_URL=https://...

# GCP configuration (required for blog deployment)
GCP_PROJECT_ID=your-project
BLOG_BUCKET_NAME=your-project-chained-blog
```

## Verification Checklist

Before merging changes to A2A UI:
- [ ] No `SAMPLE_DATA`, `demoData`, `mockData` variables
- [ ] No hardcoded demo IDs
- [ ] No canned/template agent responses
- [ ] All API routes call real services
- [ ] Empty states are shown when no data exists
- [ ] Errors from real services are displayed, not hidden

---

**Remember**: If an agent isn't available, show it's unavailable. Never fake a response.
