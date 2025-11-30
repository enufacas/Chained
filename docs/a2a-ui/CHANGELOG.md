# A2A UI Changelog

All notable changes to the A2A UI are documented in this file.

Format: `## [Date] PR #XXX - Title`

---

## [2025-11-30] PR #3446 - Enhanced A2A Steps & Deep Dive

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

### Changed
- `Pipeline` interface extended with:
  - `a2aSteps?: A2AStepDetail[]`
  - `totalDurationMs?: number`
- `executePipelineWithAgents()` now records step details

### Technical Details
- Files modified:
  - `/api/pipeline/route.ts` - Enhanced data model
  - `/components/PipelineDetailView.tsx` - New deep dive UI

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
