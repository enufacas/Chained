# A2A UI Changelog

All notable changes to the A2A UI are documented in this file.

Format: `## [Date] PR #XXX - Title`

---

## [2025-12-01] PR #TBD - Unified Single Page with Progressive Disclosure

### Added
- **Progressive Disclosure Team Mode**:
  - Team Mode is now an expandable/collapsible section on the main page
  - Click to expand and access Agent Canvas or Recipe Builder
  - Collapse to focus on chat and outcomes
  - No more navigation to separate `/team` page needed

- **Rich Asset Preview Component**:
  - New `AssetPreview` component for viewing artifacts
  - Supports Markdown rendering with basic styling
  - SVG images displayed with proper rendering
  - HTML content in sandboxed iframes
  - JSON formatted with syntax highlighting
  - Images (base64 or URL) displayed inline
  - Toggle between "Rendered" and "Raw" view modes
  - Character count and size info in footer

- **Enhanced Artifact Viewing**:
  - `TeamVisualization` now uses AssetPreview for rich artifact display
  - `PipelineDetailView` artifacts are expandable with rich preview
  - Click artifact to expand, click again to collapse
  - Proper rendering of markdown, SVG, HTML, JSON, images

### Changed
- **Unified Page Layout**:
  - Removed Team Mode link from header
  - Team Mode integrated as collapsible section in right sidebar
  - Updated Quick Links (removed /team, added Google ADK)
  - Chat instructions updated to reference "Team Mode section" instead of /team

- **Team Mode Section**:
  - Tab navigation between Agent Canvas and Recipe Builder
  - Active session progress shown inline when executing
  - Team count badge shows selected agents
  - Running indicator shows when session is active

### Removed
- Team Mode link from header navigation
- Team Mode from Quick Links section

### Files Modified
- `src/app/page.tsx` - Integrated Team Mode with progressive disclosure
- `src/components/AssetPreview.tsx` - NEW: Rich asset rendering component
- `src/components/TeamVisualization.tsx` - Uses AssetPreview for artifacts
- `src/components/PipelineDetailView.tsx` - Expandable artifacts with AssetPreview
- `docs/a2a-ui/CHANGELOG.md` - This file

### Screenshots
| Initial View | Team Mode Expanded |
|--------------|-------------------|
| Team Mode collapsed as clickable section | Agent Canvas/Recipe Builder visible |

---

## [2025-12-01] PR #3460 - Configure All Agents, Agent Canvas Input, Turn-Based Execution

### Added
- **Data Analyst & Image Generator Configuration**:
  - Added Cloud Run Terraform resources for code-reviewer, data-analyst, image-generator
  - Configured default URLs in registry and team API routes
  - All 6 agents now properly configured (no more "Not configured" warnings)

- **Agent Canvas Workflow Execution**:
  - Added goal/task text input field directly in Agent Canvas
  - Users can now start workflows immediately after building a team
  - Enter key submits, "Start" button executes

- **Turn-Based Execution Configuration**:
  - `maxTurnsPerAgent` setting: 1-5 turns (default 2)
  - Visual turn selector buttons in Agent Canvas
  - Each agent executes for specified number of turns

- **Execution Mode Option**:
  - **Sequential**: Agents run one at a time in order (default)
  - **Parallel**: All agents run simultaneously per turn
  - Toggle buttons in Agent Canvas configuration

- **Custom Team API Support**:
  - New `POST /api/team` body option: `agentIds` for custom teams
  - New `config` parameter with `maxTurnsPerAgent` and `executionMode`
  - `executeCustomTeam()` function for canvas-based workflows

### Changed
- **Terraform Configuration**:
  - Added 3 new Cloud Run services (code-reviewer, data-analyst, image-generator)
  - Updated ADK API Server with new agent URLs and descriptions
  - Updated AG-UI Frontend with new agent environment variables
  - Updated depends_on blocks for proper deployment order
  - Added new outputs for agent URLs

- **Environment Configuration**:
  - Updated `.env.example` with 3 new agent URLs
  - Default production URLs for all 6 agents

- **Team API Route**:
  - Extended `TeamSession` interface with `config?: ExecutionConfig`
  - Extended `TurnResult` interface with `turnNumber?: number`
  - Modified `executeSession()` to support parallel execution
  - Added `executeCustomTeam()` for AgentCanvas workflows

- **AgentCanvas Component**:
  - Added `onExecute` callback prop
  - Added `goal`, `maxTurnsPerAgent`, `executionMode` state
  - Added configuration panel when team is selected
  - Added "Start" button with loading state
  - Updated team preview to show execution mode

- **Team Page**:
  - Added `handleCanvasExecute` callback
  - Wired AgentCanvas `onExecute` to team execution

### Technical Details

**New Terraform Resources**:
- `google_cloud_run_v2_service.code_reviewer`
- `google_cloud_run_v2_service.data_analyst`
- `google_cloud_run_v2_service.image_generator`
- Corresponding IAM members for public access

**New Types**:
```typescript
interface ExecutionConfig {
  maxTurnsPerAgent: number;  // 1-5, default 2
  executionMode: "sequential" | "parallel";
}
```

**API Changes**:
```
POST /api/team
Body: {
  agentIds?: string[],  // NEW: custom team agents
  recipeId?: string,    // existing recipe-based
  goal: string,
  context?: object,
  config?: {            // NEW: execution configuration
    maxTurnsPerAgent: number,
    executionMode: "sequential" | "parallel"
  }
}
```

### Files Modified
- `infrastructure/terraform/adk-agents.tf` - New Cloud Run services + outputs
- `infrastructure/docker/ag-ui-frontend/.env.example` - New agent URLs
- `infrastructure/docker/ag-ui-frontend/src/app/api/registry/route.ts` - Default URLs
- `infrastructure/docker/ag-ui-frontend/src/app/api/team/route.ts` - Execution config support
- `infrastructure/docker/ag-ui-frontend/src/components/AgentCanvas.tsx` - UI updates
- `infrastructure/docker/ag-ui-frontend/src/app/team/page.tsx` - Canvas execution handler
- `docs/a2a-ui/README.md` - Documentation updates
- `docs/a2a-ui/CHANGELOG.md` - This file

---

## [2025-11-30] PR #3446 - Enhanced A2A Steps, Deep Dive, and Content Quality

### Added
- **A2A Step Details**: Pipeline now captures full A2A task information:
  - Task IDs from each agent
  - Execution timestamps and durations
  - Agent response messages
  - Full artifact data with previews

- **Deep Dive Section in PipelineDetailView**:
  - Expandable step cards showing task IDs
  - Artifact viewer with type and preview
  - Timing information (start, end, duration)
  - Raw data toggle for debugging

- **Documentation Structure**:
  - Created `docs/a2a-ui/` directory
  - Added README.md with architecture overview
  - Added CHANGELOG.md for tracking improvements
  - Added path-specific copilot instructions

- **Shared Types**:
  - Moved `Pipeline`, `A2AStepDetail`, `A2AStepArtifact` to `@/types`
  - Single source of truth for API and UI components

### Changed
- **CRITICAL: Improved Agent Prompts** for better content quality:
  - **Research Agent**: Now requests 10 specific categories of information including statistics, examples, expert perspectives, and future directions
  - **Trends Agent**: Now requests trending keywords, related queries, rising trends, geographic interest, long-tail opportunities, and title suggestions  
  - **Blog Writer Agent**: Complete structured prompt with:
    - 7-section blog structure (2000-2500 words)
    - Specific word counts per section
    - Quality checklist (no generic content, require examples)
    - SEO optimization with primary/secondary keywords
    - Writing style guidance (professional, concrete examples, data points)

- `Pipeline` interface extended with:
  - `a2aSteps?: A2AStepDetail[]`
  - `totalDurationMs?: number`

### Technical Details
- Files modified:
  - `/api/pipeline/route.ts` - Enhanced data model + improved prompts
  - `/components/PipelineDetailView.tsx` - New deep dive UI
  - `/types/index.ts` - Shared type definitions

### Why This Matters
The previous prompts were very basic (e.g., "Write a blog post about X") which resulted in generic, placeholder-like content. The new prompts provide detailed instructions that should produce:
- Specific, researched content with real data points
- Proper blog structure with introduction, body, conclusion
- SEO-optimized titles and keywords
- Higher word counts (2000-2500 vs generic)

---

## [2025-11-30] PR #3445 - Real-time Polling & Outcomes

### Added
- 5-second polling for live updates
- Creative state representations with animations
- Click-to-expand pipeline detail view

### Changed
- `PipelineOutcomes` refreshes every 5 seconds
- `RealTimeAgentActivity` visibility-aware polling

---

## [2025-11-30] PR #3444 - Pipeline Detail View

### Added
- `PipelineDetailView` component
- A2A Agent Cards section
- Pipeline lifecycle visualization
- Progress bar with phase markers

### Changed
- `PipelineOutcomes` now opens detail modal on click

---

## [2025-11-30] PR #3438 - Real Data Only Policy

### Changed
- Removed all simulated/canned agent responses
- Agent API now calls real Cloud Run endpoints
- Pipeline API returns only real pipeline data

### Removed
- `SAMPLE_DATA` static pipeline data
- Fallback canned responses in agent handlers

### Policy
All data in A2A UI must come from actual A2A agent execution.
No simulations, fake data, or demo content.

---

## [2025-11-30] PR #3433 - Docker Build Fix

### Fixed
- Regenerated `package-lock.json` for Docker builds
- CI/CD pipeline now works correctly

---

## [2025-11-30] PR #3432 - Vertex AI API Fix

### Changed
- API endpoint from `v1beta` to `v1`
- Fixed API endpoint resolution

---

## [2025-11-30] PR #3430 - Model Update

### Changed
- Model from deprecated to `gemini-2.0-flash`
- Fixed 404 errors from model endpoint

---

## [Initial] Chat Working

### Added
- CopilotKit integration
- Basic chat functionality
- Pipeline analysis actions
- Agent listing

---

## How to Update This File

When making changes to the A2A UI:

1. Add new entry at the top with date and PR number
2. Use sections: Added, Changed, Fixed, Removed
3. List specific files modified
4. Include technical details for complex changes
5. Reference related issues or PRs

Example:
```markdown
## [YYYY-MM-DD] PR #XXXX - Title

### Added
- New feature description

### Changed
- What was modified

### Files Modified
- `path/to/file.ts` - Description of changes
```
