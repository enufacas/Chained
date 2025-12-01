# AG-UI Artifact Persistence Fix

**Date**: 2025-12-01  
**Status**: ✅ **Complete**  
**Issue**: Sessions expanding in history page showed no artifacts; need to verify A2A multi-agent chaining

---

## Problem Statement

### Issue 1: No Artifacts Displayed
When expanding a session on the AG-UI history page (`/history`), no artifacts were shown even though pipelines had completed successfully.

**Root Cause**: Pipeline execution in `/api/pipeline/route.ts` did not save artifacts to localStorage, unlike the team API which properly persisted artifacts.

### Issue 2: A2A Multi-Agent Chaining Unclear
Need to verify that the A2A process truly receives input from multiple agents to create an ultimate artifact.

**Finding**: A2A chaining was already correctly implemented via `referenceTaskIds`, but not documented in artifacts.

---

## Solution Implemented

### 1. Artifact Persistence

**File**: `/src/app/api/pipeline/route.ts`

Added storage functions:
```typescript
import {
  saveArtifact,
  saveSession,
  saveA2ATask,
} from "@/lib/storage";
```

**Implementation** (lines 843-951):
```typescript
// Persist Artifacts and Session to localStorage
const savedArtifactIds: string[] = [];

// 1. Save artifacts from each A2A step
for (const step of pipeline.a2aSteps) {
  for (const artifact of step.artifacts) {
    const saved = saveArtifact({
      name: artifact.name,
      type: artifact.type,
      data: artifact.data,
      preview: artifact.preview,
      source: "workflow",
      sourceId: pipelineId,
      sourceName: pipeline.topic,
      agentName: step.agentName,
      phase: step.phase,
    });
    savedArtifactIds.push(saved.id);
  }
  
  // 2. Save A2A task as artifact for protocol compliance
  if (step.rawResponse) {
    const taskArtifact = saveA2ATask(
      step.rawResponse,
      step.agentName,
      "workflow",
      pipelineId,
      pipeline.topic,
      step.phase
    );
    savedArtifactIds.push(taskArtifact.id);
  }
}

// 3. Create ultimate artifact combining all outputs
const ultimateArtifact = {
  name: "pipeline-summary",
  type: "application/json",
  data: JSON.stringify({
    pipelineId: pipeline.id,
    topic: pipeline.topic,
    status: pipeline.status,
    a2aChaining: {
      description: "Each agent receives previous task IDs via A2A protocol referenceTaskIds field",
      taskIdChain: taskIds,
      agentSequence: [
        "Academic Research Agent → Research data and keywords",
        "Google Trends Agent (refs research) → SEO analysis",
        "Blog Writer Agent (refs research + trends) → Content creation"
      ],
      ultimateArtifactCombines: "All outputs from the agent chain"
    },
    phases: { /* ... */ },
    agentSteps: [ /* ... */ ],
    summary: "Pipeline completed with N agent steps..."
  }, null, 2)
};

// 4. Save session record
saveSession({
  id: pipelineId,
  type: "workflow",
  name: "A2A Pipeline",
  topic: pipeline.topic,
  status: pipeline.status,
  artifacts: savedArtifactIds,
  taskIds: taskIds,
});
```

### 2. UI Display Enhancement

**File**: `/src/components/PipelineOutcomes.tsx`

Added artifact count display:
```typescript
import { getArtifactsBySourceId } from "@/lib/storage";

// In component:
const artifacts = getArtifactsBySourceId(pipeline.id);
const artifactCount = artifacts.length;

// Display:
{artifactCount > 0 && (
  <a href="/history">
    📦 {artifactCount} artifact{artifactCount !== 1 ? 's' : ''} saved
    • includes ultimate summary
  </a>
)}
```

### 3. A2A Chaining Documentation

**Evidence in Code**:

**Agent Call Function** (line 105-125):
```typescript
async function callA2AAgent(
  agentUrl: string,
  message: string,
  metadata?: Record<string, unknown>,
  referenceTaskIds?: string[]  // ← Passed to each agent
): Promise<A2ATask | null> {
  const request: A2ASendMessageRequest = {
    message: { /* ... */ },
    contextId: `pipeline-${Date.now()}...`,
    metadata,
    referenceTaskIds,  // ← Included in A2A request
  };
  // POST to /a2a/tasks
}
```

**Research Phase** (line 442):
```typescript
const researchTask = await callA2AAgent(
  AGENT_URLS.research,
  "Conduct research...",
  { topic: pipeline.topic },
  // No referenceTaskIds - first agent
);
taskIds.push(researchTask.id);
```

**Trends Phase** (line 545-568):
```typescript
const trendsTask = await callA2AAgent(
  AGENT_URLS.trends,
  "Analyze trends...",
  { keywords: pipeline.results.research.keywords },
  taskIds  // ← Receives research task ID
);
```

**Writing Phase** (line 642-729):
```typescript
const writerTask = await callA2AAgent(
  AGENT_URLS.writer,
  "Write blog post...",
  { research_keywords, trending_keywords },
  taskIds  // ← Receives both research and trends task IDs
);
```

---

## A2A Protocol Compliance

### How Agent Chaining Works

1. **Research Agent** executes → produces `task-1`
2. **Trends Agent** receives:
   ```json
   {
     "message": { "role": "user", "parts": [{"text": "..."}] },
     "referenceTaskIds": ["task-1"],
     "metadata": { "keywords": ["from", "research"] }
   }
   ```
3. **Blog Writer Agent** receives:
   ```json
   {
     "message": { "role": "user", "parts": [{"text": "..."}] },
     "referenceTaskIds": ["task-1", "task-2"],
     "metadata": { "research_keywords": [...], "trending_keywords": [...] }
   }
   ```

### Ultimate Artifact Structure

The ultimate artifact documents the entire chain:

```json
{
  "pipelineId": "pipeline-123...",
  "topic": "AI in Healthcare",
  "status": "completed",
  "totalDurationMs": 45232,
  "a2aChaining": {
    "description": "Each agent receives previous task IDs via A2A protocol referenceTaskIds field",
    "taskIdChain": [
      "task-academic-research-abc123",
      "task-google-trends-def456",
      "task-blog-writer-ghi789"
    ],
    "agentSequence": [
      "Academic Research Agent → Research data and keywords",
      "Google Trends Agent (refs research) → SEO analysis and trending topics",
      "Blog Writer Agent (refs research + trends) → Content creation and publishing"
    ],
    "ultimateArtifactCombines": "All outputs from the agent chain into a single comprehensive summary"
  },
  "phases": {
    "research": {
      "topic": "AI in Healthcare",
      "domain": "Healthcare Technology",
      "keywords": ["artificial intelligence", "healthcare", "medical AI"]
    },
    "trends": {
      "trendingKeywords": ["AI diagnostics", "medical automation"],
      "recommendedFocus": "AI-powered diagnostic tools"
    },
    "blog": {
      "title": "How AI is Revolutionizing Healthcare Diagnostics",
      "url": "https://storage.googleapis.com/.../ai-in-healthcare.html",
      "wordCount": 2345
    }
  },
  "agentSteps": [
    {
      "agentName": "Academic Research Agent",
      "phase": "research",
      "taskId": "task-academic-research-abc123",
      "status": "completed",
      "durationMs": 12453,
      "artifactCount": 3
    },
    {
      "agentName": "Google Trends Agent",
      "phase": "trends",
      "taskId": "task-google-trends-def456",
      "status": "completed",
      "durationMs": 8932,
      "artifactCount": 2
    },
    {
      "agentName": "Blog Writer Agent",
      "phase": "writing",
      "taskId": "task-blog-writer-ghi789",
      "status": "completed",
      "durationMs": 23847,
      "artifactCount": 4
    }
  ],
  "summary": "Pipeline 'AI in Healthcare' completed successfully with 3 agent steps. Each agent received outputs from previous agents via A2A protocol referenceTaskIds. Research domain: Healthcare Technology. Blog published at: https://storage.googleapis.com/.../ai-in-healthcare.html"
}
```

---

## What Changed

### Before Fix

| Component | Behavior |
|-----------|----------|
| Pipeline Execution | ❌ Artifacts existed only in memory |
| localStorage | ❌ No persistence of pipeline artifacts |
| History Page | ❌ Sessions expanded with 0 artifacts |
| A2A Chaining | ✅ Worked but undocumented |
| Ultimate Artifact | ❌ Did not exist |

### After Fix

| Component | Behavior |
|-----------|----------|
| Pipeline Execution | ✅ Saves all artifacts to localStorage |
| localStorage | ✅ Persists artifacts across page reloads |
| History Page | ✅ Sessions show all artifacts when expanded |
| A2A Chaining | ✅ Works and fully documented in artifacts |
| Ultimate Artifact | ✅ Comprehensive summary of all agent work |

---

## Testing Verification

### Manual Test Steps

1. **Create a Pipeline**:
   ```bash
   # Via chat or API
   POST /api/pipeline
   { "topic": "Machine Learning in Finance" }
   ```

2. **Check localStorage**:
   ```javascript
   // In browser console
   JSON.parse(localStorage.getItem('ag-ui-artifacts'))
   JSON.parse(localStorage.getItem('ag-ui-sessions'))
   ```

3. **Navigate to History Page**:
   - Go to `/history`
   - Click on a session to expand
   - Verify artifacts are displayed

4. **Verify Ultimate Artifact**:
   - Find "pipeline-summary" artifact
   - Click to view
   - Verify contains:
     - All phase results
     - A2A chaining documentation
     - Task ID chain
     - Agent sequence

5. **Check PipelineOutcomes**:
   - Go to `/` (main page)
   - Find completed pipeline
   - Verify shows "📦 N artifacts" badge
   - Click "View Artifacts & Session Details"
   - Redirects to `/history`

### Expected Results

- ✅ Artifacts persist across page refreshes
- ✅ Session expansion shows all artifacts
- ✅ Ultimate artifact contains comprehensive data
- ✅ A2A chaining clearly documented
- ✅ All agent outputs included in ultimate summary

---

## Technical Details

### Storage Location

**localStorage Keys**:
- `ag-ui-artifacts` - Array of all stored artifacts
- `ag-ui-sessions` - Array of all stored sessions

**Artifact Schema**:
```typescript
interface StoredArtifact {
  id: string;
  name: string;
  type: string;
  data: string;
  preview?: string;
  source: "workflow" | "team" | "recipe" | "chat";
  sourceId: string;
  sourceName: string;
  createdAt: string;
  agentName?: string;
  phase?: string;
  a2aType?: "agent-card" | "task" | "message" | "artifact";
  taskId?: string;
  contextId?: string;
}
```

**Session Schema**:
```typescript
interface StoredSession {
  id: string;
  type: "workflow" | "team" | "recipe";
  name: string;
  topic: string;
  status: string;
  createdAt: string;
  completedAt?: string;
  artifacts: string[]; // artifact IDs
  metadata?: {
    totalDurationMs?: number;
    agentStepsCount?: number;
    blogUrl?: string;
  };
  a2aContextId?: string;
  taskIds?: string[]; // A2A task IDs
}
```

### Performance Considerations

- **Storage Limits**: localStorage typically 5-10MB per origin
- **Artifact Limit**: Capped at 100 artifacts (MAX_ARTIFACTS)
- **Session Limit**: Capped at 50 sessions (MAX_SESSIONS)
- **Auto-Pruning**: Oldest items removed when limits exceeded

### Error Handling

```typescript
try {
  // Save artifacts
} catch (storageError) {
  logWithTimestamp("WARN", "Failed to persist artifacts to localStorage");
  // Continue - pipeline still succeeded
}
```

Pipeline execution succeeds even if localStorage persistence fails (e.g., quota exceeded, browser restrictions).

---

## Benefits

### For Users
1. **Persistence**: Artifacts survive page refreshes
2. **History**: Complete audit trail of all work
3. **Transparency**: Clear view of multi-agent collaboration
4. **Discovery**: Find past work via history page

### For Developers
1. **Debugging**: Full artifact history for troubleshooting
2. **Analysis**: Can inspect A2A protocol exchanges
3. **Compliance**: Proper A2A protocol implementation
4. **Documentation**: Self-documenting pipeline execution

### For the A2A Ecosystem
1. **Protocol Adherence**: Correct use of `referenceTaskIds`
2. **Traceability**: Full chain of agent interactions
3. **Proof of Coordination**: Demonstrates multi-agent collaboration
4. **Ultimate Synthesis**: Combined output from all agents

---

## Future Enhancements

### Potential Improvements

1. **Backend Persistence**: Store artifacts in database instead of localStorage
2. **Search**: Add search functionality for artifacts
3. **Filtering**: Filter by agent, phase, or artifact type
4. **Export**: Download artifacts as ZIP
5. **Visualization**: Graph view of A2A task chains
6. **Analytics**: Pipeline execution metrics and trends

### Known Limitations

1. **localStorage Quota**: Limited to ~5-10MB
2. **No Sync**: Artifacts not synchronized across devices
3. **Browser-Specific**: Data tied to single browser
4. **No Versioning**: No history of artifact changes

---

## Related Documentation

- [A2A UI README](./README.md) - Overall feature documentation
- [A2A UI Changelog](./CHANGELOG.md) - Change history
- [Storage Library](../../infrastructure/docker/ag-ui-frontend/src/lib/storage.ts) - Storage implementation
- [Pipeline API](../../infrastructure/docker/ag-ui-frontend/src/app/api/pipeline/route.ts) - API implementation
- [History Page](../../infrastructure/docker/ag-ui-frontend/src/app/history/page.tsx) - UI implementation

---

## Conclusion

This fix ensures that:
1. ✅ All pipeline artifacts are persisted to localStorage
2. ✅ Sessions display artifacts correctly when expanded
3. ✅ A2A multi-agent chaining is verified and documented
4. ✅ Ultimate artifact combines all agent outputs
5. ✅ Users can view complete history of all work

The A2A protocol implementation was already correct - each agent receives previous task IDs via `referenceTaskIds`. This fix adds visibility and documentation of that coordination through persistent artifacts and the ultimate summary artifact.
