# A2A UI Changelog

All notable changes to the A2A UI are documented in this file.

Format: `## [Date] PR #XXX - Title`

---

## [2025-12-10] PR #TBD - Fix Real-Time Updates and Unify UI Display Styles

### Problem
Production AG-UI at https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/ had two critical issues:
1. **Real-time updates unreliable**: Progress not updating during agent execution without page refresh
2. **Inconsistent UI styles**: Historical runs showed minimal "summary" styles while live runs showed full detail

### Root Causes
1. **Polling too slow**: 5s for pipelines, 2s for sessions - not fast enough for user perception
2. **Different display components**: Completed items used minimal summaries while active items used full details
3. **Max-height restrictions**: Historical displays limited to 48px/264px while needing much more space

### Fixed
- **Unified Display Styles**:
  - Completed team sessions now use SAME detailed view as active sessions
    * Full agent statistics grid showing all agents
    * Turn-by-turn progress with expandable steps
    * Individual artifact displays with preview functionality
    * Session configuration details (turns, execution mode)
    * Increased max-height from 48px to 600px (12.5x more space)
  
  - Completed pipelines now use SAME detailed view as active pipelines
    * Full phase visualization showing all 5 phases
    * Detailed research/trends/blog result cards
    * All keywords visible, not just first 3
    * Increased max-height from 264px to 600px (2.3x more space)
  
  - **Removed ALL "smaller summary styles"** as requested
    * No more truncated displays
    * No more minimal artifact lists  
    * Consistent component structure throughout
    * Historical data now as useful as live data

- **Improved Polling Frequency**:
  - Pipeline polling: 5s → 2s interval (2.5x faster)
  - Session polling: 2s → 1s interval (2x faster)
  - Initial poll delay: 1s → 0.5s (2x faster first update)

### Technical Details
**Files Modified:**
- `src/app/page.tsx` - Unified display components, improved polling intervals

**Key Changes:**
1. Completed sessions now render full detail with agent stats, turn results, and artifacts
2. Completed pipelines now render full detail with phase visualization and result cards
3. All polling intervals reduced for more responsive updates
4. Max-height restrictions increased from 48px/264px to 600px

**What Gets Displayed Now:**
- Agent stats grid (all agents, not just summary count)
- Turn-by-turn results with expandable artifact inspection
- All artifacts (not just first 4)
- Full configuration details (turns per agent, execution mode)
- Complete phase visualization for pipelines
- Full research/trends/blog data with proper cards

### Benefits
1. **Real-time updates work reliably** - Users see progress within 0.5-2 seconds
2. **No page refresh needed** - Polling continues throughout execution
3. **Consistent UX** - Active and completed items look identical
4. **Better information density** - All data visible, not truncated
5. **Historical data useful** - Past runs show same detail as live runs

### Testing
- ✅ Build: Compiled successfully with no errors
- ✅ Type checking: All TypeScript types valid
- ✅ UI consistency: Active and completed displays use same components

---

## [2025-12-02] PR #TBD - Enhanced Frontend Error Logging and Monitoring

### Problem
After memory fix deployment, need better visibility into frontend errors:
1. **Client-side errors invisible**: React errors, API failures not in GCP logs
2. **Hard to debug**: Missing artifacts and progress issues difficult to trace
3. **No retry logic**: Single API failures cause step failures
4. **Limited monitoring**: Can't proactively detect issues

### Analysis & Findings
**Memory Fix Status**: ✅ Successfully deployed
- Increased from 512Mi to 1Gi on 2025-12-02 01:35 UTC
- Last OOM error: 2025-12-02 01:09:27 (before deployment)
- Current status: No errors in logs after 1Gi deployment
- Service revisions 00078, 00079 running with 1Gi

**Root Cause of "1/8 steps showing" issue:**
- OOM crashes **before fix** caused service restarts
- In-memory pipeline data lost on restart
- Frontend polling got empty responses
- After reload: Backend empty + localStorage has old artifacts = inconsistent state

### Implemented Solutions
1. **Error Boundary Component** (`src/components/ErrorBoundary.tsx`)
   - Catches React component errors
   - Logs to GCP Cloud Run
   - Displays user-friendly fallback UI
   - Provides recovery options

2. **Frontend Error Logging API** (`src/app/api/debug/log-error/route.ts`)
   - Accepts error logs from frontend
   - Persistent logging to GCP
   - Supports: react-error, api-error, storage-error, generic

3. **Structured Error Utilities** (`src/lib/error-logging.ts`)
   - `logError()`, `logApiError()`, `logStorageError()`
   - `setupGlobalErrorHandlers()` for unhandled errors
   - Automatic backend error reporting

4. **Pipeline API Enhancements** (`src/app/api/pipeline/route.ts`)
   - Retry logic: 2 retries with exponential backoff
   - 60-second timeout for agent calls
   - Retry on 5xx errors and 429 (rate limiting)
   - Detailed attempt tracking in logs

5. **Storage Error Logging** (`src/lib/storage.ts`)
   - Artifact save failures logged to backend
   - Session save failures logged to backend
   - Includes context for debugging

### Technical Details
**Files Modified:**
- `src/components/ErrorBoundary.tsx` - NEW: Error boundary component
- `src/app/api/debug/log-error/route.ts` - NEW: Error logging endpoint
- `src/lib/error-logging.ts` - NEW: Error logging utilities
- `src/app/api/pipeline/route.ts` - Enhanced with retry logic and timeouts
- `src/app/page.tsx` - Integrated ErrorBoundary and global error handlers
- `src/components/PipelineOutcomes.tsx` - Enhanced API error logging
- `src/lib/storage.ts` - Enhanced storage error logging

**Build Status:**
- ✅ Linting: No ESLint warnings or errors
- ✅ Build: Compiled successfully

**Memory Verification:**
```bash
gcloud run services describe chained-ag-ui-frontend
# memory: 1Gi ✅

gcloud logging read 'severity>=ERROR AND timestamp>="2025-12-02T01:35:00Z"'
# (empty - no errors) ✅
```

### Benefits
1. **Better debugging**: All frontend errors visible in GCP logs
2. **Proactive monitoring**: Can detect issues before users report
3. **Improved resilience**: Automatic retry on transient failures
4. **Enhanced UX**: Graceful error handling with recovery options

### Monitoring
Watch for these log patterns:
- `Frontend Error Logger` - Frontend errors sent to backend
- `React component error` - Component crashes
- `API call error` - API failures with retry attempts
- `Storage operation error` - localStorage issues

### Related Documentation
- ERROR_LOGGING_IMPROVEMENTS.md - Detailed implementation guide
- MEMORY_OOM_FIX.md - Memory fix documentation
- README.md - A2A UI architecture

---

## [2025-12-02] PR #TBD - Fix Memory Exhaustion and Artifact Display Issues

### Problem
AG-UI Frontend experiencing multiple critical issues:
1. **Memory Exhaustion**: Service crashes with OOM errors (using 680 MiB with 512 MiB limit)
2. **Missing Artifacts**: Artifacts not appearing in pipeline outcomes or sessions on artifacts page
3. **Progress Updates Failing**: Pipeline progress not updating due to service instability
4. **Data Loss**: Service restarts cause loss of in-memory pipeline data

GCP Logs showed: `Memory limit of 512 MiB exceeded with 680 MiB used`

### Root Causes
1. **Insufficient Memory**: Cloud Run service limited to 512 MiB
2. **Client-Side Storage**: localStorage is browser-only - artifacts don't survive server restarts
3. **Service Restarts**: OOM kills cause loss of in-memory activePipelines Map
4. **No Server Persistence**: No backend storage for pipeline/artifact state

### Fixed
- **Increased Memory Limit**: 512Mi → 1Gi in Terraform configuration
  - Prevents OOM crashes during pipeline execution
  - Allows service to handle concurrent operations
  - Improves overall stability and reliability
  
- **Infrastructure Change**: Updated `adk-agents.tf`
  - Line 1072: `memory = "1Gi"  # Increased from 512Mi to prevent OOM errors`
  - Requires Terraform apply and service redeployment

### Technical Details
**Files Modified:**
- `infrastructure/terraform/adk-agents.tf` - Increased AG-UI Frontend memory limit

**Key Changes:**
1. Memory allocation: 512Mi → 1Gi (100% increase)
2. Prevents OOM-induced service crashes
3. Improves artifact persistence and retrieval
4. Enables stable progress updates

**Why This Fixes Artifacts Issue:**
- Service stays alive longer, preserving in-memory pipeline data
- localStorage artifacts can be properly saved during pipeline execution
- Reduced service restarts mean fewer data loss events
- More memory for Next.js SSR and API route processing

### Known Limitations
- localStorage remains client-side only (by design)
- Long-term solution may require backend database persistence
- Artifacts still lost if user clears browser cache

### Deployment Notes
After merging, the CI/CD pipeline will:
1. Run `terraform apply` to update Cloud Run configuration
2. Deploy new revision with 1Gi memory limit
3. Service will scale to zero when idle (cpu_idle=true unchanged)

---

## [2025-12-01] PR #TBD - Fix Low Fidelity Team Session Persistence

### Problem
Recent Team Sessions displayed low fidelity data after page reload:
- **During runtime**: Full `turnResults` with all A2A protocol data (agent cards, tasks, messages, artifacts)
- **After reload**: Only basic metadata (status, timing) - missing the rich protocol data
- Old runs were not properly persisted for viewing between app restarts

### Fixed
- **Complete turnResults Persistence**:
  - Backend now saves full `turnResults` array to localStorage in metadata
  - Includes all A2A protocol objects: agentCard, task, userMessage, agentMessage
  - Progressive saving during execution (not just at completion)
  - Ensures high-fidelity data available after page reload

- **Enhanced Session Metadata**:
  - Added `config` (execution configuration: maxTurnsPerAgent, executionMode)
  - Added `finalResult` (session outcome summary)
  - Added `turnNumber` to individual turn results
  - All fields properly typed in TeamSession interface

- **Improved Data Restoration**:
  - Frontend restoration logic handles all new fields
  - Backward compatible (gracefully handles missing data)
  - Proper type casting ensures IDE support and type safety

- **Comprehensive Testing**:
  - Added 6 tests for localStorage persistence
  - Verified turnResults with A2A objects persist correctly
  - Tested config and finalResult persistence
  - Validated session updates work properly

### Technical Details
**Files Modified:**
- `src/app/api/team/route.ts` - Added turnResults, config to session metadata (lines 528, 757)
- `src/app/page.tsx` - Enhanced TeamSession interface, updated save/restore logic
- `__tests__/lib/storage.test.ts` - NEW: Comprehensive storage tests

**Key Changes:**
1. Backend persistence: `metadata: { turnResults, config, finalResult, ... }`
2. Frontend save: Includes all new fields when saving sessions
3. Frontend restore: Properly casts and restores all fields with backward compatibility
4. TypeScript interface: Added optional fields to TeamSession

**What Gets Persisted Now:**
```typescript
metadata: {
  currentTurn: number,
  totalTurns: number,
  recipeId: string,
  turnResults: TurnResult[],  // ✅ Full array with A2A objects
  config: ExecutionConfig,     // ✅ Execution configuration
  finalResult: object,         // ✅ Final session result
}
```

**TurnResult includes:**
- Basic: stepIndex, agentId, agentName, status, timing, turnNumber
- A2A Protocol: agentCard, task, userMessage, agentMessage
- Content: artifacts array, message, error

### Why This Matters
- **High fidelity history**: Recent sessions show complete details after page reload
- **A2A compliance**: Full protocol objects preserved for inspection and debugging
- **Better UX**: Users can explore past execution details, artifacts, and agent interactions
- **Persistence guarantee**: Data survives page reloads and server restarts (localStorage is client-side)

### Test Results
✅ All 6 storage tests pass:
- ✓ Basic session save/retrieve
- ✓ turnResults persistence with A2A protocol objects
- ✓ Config and finalResult persistence
- ✓ Session updates
- ✓ Artifact persistence
- ✓ Storage cleanup

---

## [2025-12-01] PR #3492 - Fix Session State Tracking and Progress Display Issues

### Problem
When testing team execution, the progress indicator first advanced to 6/6, then never ended. After page refresh, it showed turn 2/6. This was caused by race conditions in status updates and lack of backend session verification.

### Fixed
- **Race Condition in Sequential Execution**:
  - `currentTurn` now updates AFTER turn execution completes (not before)
  - Prevents showing progress that hasn't been achieved yet
  - Ensures consistency with parallel mode timing

- **Atomic Status Updates**:
  - Status and currentTurn are now updated together atomically
  - Prevents polling from seeing inconsistent state (e.g., currentTurn=6 but status="running")
  - Final session state persists only after both values are set

- **Backend Session Verification**:
  - On page load, restored sessions are verified with backend API
  - If session not found (server restart), mark as completed to avoid confusion
  - Prevents showing stale "turn 2/6" when backend has lost the session
  - Backend state becomes source of truth when session still exists

- **Improved Polling Logic**:
  - Polling explicitly checks status field instead of relying on currentTurn
  - Handles 404 response when session doesn't exist on backend
  - Stops polling on errors to avoid infinite error loops
  - Better handling of completed/failed state transitions

- **Session Recovery**:
  - Restored sessions can now resume polling if still active on backend
  - Uses state-based signaling to avoid circular dependencies
  - Properly handles both fresh executions and page reloads

### Technical Details
**Files Modified:**
- `src/app/api/team/route.ts` - Fixed sequential mode currentTurn update timing, added atomic status transition comments
- `src/app/page.tsx` - Added backend verification, improved polling logic, added resumePollingSessionId state

**Key Changes:**
1. Sequential mode: Move `session.currentTurn = stepIndex` to AFTER `executeTurn()` completes
2. Backend verification: New useEffect to verify restored sessions with `/api/team?session=ID`
3. Polling termination: Check `isSessionActive(session)` based on status, not currentTurn
4. Error handling: Handle 404 responses when session doesn't exist

### Why This Matters
- **No more stuck sessions**: Sessions properly complete when all turns finish
- **Accurate progress**: UI shows actual execution state, not predicted state
- **Page refresh works**: Backend verification prevents showing stale localStorage data
- **Server restart resilience**: Gracefully handles lost sessions from backend restarts

---

## [2025-12-01] PR #TBD - AG-UI Refinements: Artifacts, Persistence, Preview Overlay

### Added
- **Artifact Preview Overlay**:
  - New `ArtifactPreviewOverlay` component for full-screen artifact viewing
  - Supports navigation between artifacts with prev/next buttons
  - Press Escape to close, click outside to dismiss
  - Shows artifact name, type, size info in header
  - Uses existing `AssetPreview` component for rich rendering

- **Artifact Stream Component**:
  - New `ArtifactStream` component at bottom of main page
  - Shows stream of all artifacts produced during execution
  - Expandable/collapsible with artifact count and storage size
  - Click any artifact to open preview overlay
  - Storage stats display (count, estimated size)
  - Clear all button with confirmation

- **Persistence Layer (localStorage)**:
  - New `src/lib/storage.ts` utility module
  - Saves artifacts between page reloads and browser sessions
  - Supports up to 100 artifacts and 50 sessions
  - Automatic pruning of old items
  - Storage statistics tracking
  - Clear all functionality

- **History Page (`/history`)**:
  - New dedicated page for viewing all persisted artifacts and sessions
  - Filter by source type (pipeline, team, recipe, chat)
  - Filter by view mode (all, artifacts only, sessions only)
  - Grid view of artifacts with preview
  - Delete individual items or clear all
  - Responsive design with empty states

- **Enhanced Progress & Outcomes**:
  - Expandable steps with artifact selection
  - Click a step to see details and artifacts
  - Click any artifact to open preview overlay
  - Overall session artifacts section when completed
  - Artifact count badges on each step

### Changed
- **AgentCanvas Component**:
  - Added `isExecuting` prop for external control
  - Clears goal input immediately on execution start
  - Disables execute button while running
  - Better execution state management

- **RecipeBuilder Component**:
  - Added `isExecuting` prop for external control
  - Clears goal input immediately on execution start
  - Disables submit button while running

- **UnifiedOutcomes Component**:
  - Added `onSelectArtifact` callback prop
  - Expandable step details with nested artifact grid
  - Step status, timing, and error display
  - Overall artifacts section for completed sessions

- **Main Page (`page.tsx`)**:
  - Added artifact selection state management
  - Added ArtifactStream component
  - Added ArtifactPreviewOverlay
  - Artifacts saved to localStorage on session completion
  - Passes `isExecuting` to AgentCanvas and RecipeBuilder

### Files Added
- `src/lib/storage.ts` - localStorage persistence utilities
- `src/components/ArtifactPreviewOverlay.tsx` - Full-screen preview overlay
- `src/components/ArtifactStream.tsx` - Artifacts stream display
- `src/app/history/page.tsx` - Dedicated history page

### Files Modified
- `src/app/page.tsx` - Main page with new components and state
- `src/components/AgentCanvas.tsx` - isExecuting prop, clear input
- `src/components/RecipeBuilder.tsx` - isExecuting prop, clear input
- `docs/a2a-ui/CHANGELOG.md` - This file

### Screenshots
| Main Page with Artifact Stream | History Page |
|-------------------------------|--------------|
| Artifact Stream at bottom, expandable | Grid view of all artifacts |

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
