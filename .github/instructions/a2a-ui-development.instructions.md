---
applyTo:
  - "infrastructure/docker/ag-ui-frontend/**"
---

# A2A UI Development Instructions

## MANDATORY: Read Documentation First

When working on the A2A UI (`infrastructure/docker/ag-ui-frontend/`), **you MUST read the feature documentation** before making changes:

- **[docs/a2a-ui/README.md](../../../docs/a2a-ui/README.md)** - Architecture, components, data model
- **[docs/a2a-ui/CHANGELOG.md](../../../docs/a2a-ui/CHANGELOG.md)** - Recent changes and context

## Key Principles

### 1. Real Data Only
**NO simulated, fake, mock, or demo data.** All pipeline data must come from actual A2A agent execution.

See: `.github/instructions/a2a-ui-real-data.instructions.md`

### 2. GCP Cloud Run Agents
Data sources should be GCP Cloud Run deployed agents, not GitHub APIs (unless explicitly requested).

### 3. Update Documentation
After making changes:
1. Update `docs/a2a-ui/CHANGELOG.md` with your PR
2. Update `docs/a2a-ui/README.md` if architecture changes
3. Add PR to the "Related PRs" table

## Architecture Quick Reference

```
API Routes:
├── /api/pipeline    → Pipeline CRUD, A2A step tracking
├── /api/agent       → Direct agent interaction
├── /api/activity    → Agent health monitoring
└── /api/copilotkit  → AI chat backend

Components:
├── page.tsx                  → Main page with CopilotKit
├── PipelineDetailView.tsx    → Deep dive modal
├── PipelineOutcomes.tsx      → Pipeline results list
└── RealTimeAgentActivity.tsx → Agent health display
```

## Data Model

Key interfaces to understand:

```typescript
// Pipeline with A2A step tracking
interface Pipeline {
  id: string;
  topic: string;
  status: PipelineStatus;
  a2aSteps?: A2AStepDetail[];  // Deep dive data
  totalDurationMs?: number;
  // ... see route.ts for full interface
}

// A2A Step for detailed tracking
interface A2AStepDetail {
  taskId: string;
  agentName: string;
  artifacts: Array<{ name, type, data, preview }>;
  // ... see route.ts for full interface
}
```

## Common Tasks

### Adding a New CopilotKit Action
1. Add to `page.tsx` using `useCopilotAction()`
2. Define parameters and handler
3. Return markdown-formatted response
4. Test via chat interface

### Modifying Pipeline Data
1. Update `Pipeline` interface in `route.ts`
2. Update `executePipelineWithAgents()` to capture data
3. Update `PipelineDetailView` to display new data
4. Update docs with data model changes

### Adding UI Components
1. Create in `/src/components/`
2. Use existing Tailwind classes for consistency
3. Include loading and error states
4. Add polling if real-time updates needed

## Testing Checklist

Before committing changes:
- [ ] `npm run lint` passes
- [ ] `npm run build` succeeds
- [ ] Tested in browser (local dev server)
- [ ] No console errors
- [ ] Documentation updated

## Related Documentation

- [A2A Success History](../../../docs/a2a/A2A_SUCCESS_HISTORY.md)
- [A2A Status](../../../docs/a2a/A2A_STATUS.md)
- [Path Instructions - Real Data](./a2a-ui-real-data.instructions.md)
- [Path Instructions - Data Sources](./a2a-ui-data-sources.instructions.md)
