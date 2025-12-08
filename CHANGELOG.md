# Changelog

All notable changes to the Chained project are documented in this file.

The format captures:
- **Features** (feat): New capabilities and enhancements
- **Bug Fixes** (fix): Corrections and fixes
- **Chores & Maintenance**: Routine updates and housekeeping

Actor indicators:
- 👤 User-initiated (from issues or direct commits)
- 🤖 Bot-generated (autonomous system)

Codebase areas:
- ⚙️ Workflows - GitHub Actions
- 🔧 Agents/Tools - Custom agents and utilities
- 📋 Instructions - Copilot instructions
- 🏗️ Infrastructure - GCP, Terraform, Docker
- 📚 Docs - Documentation
- 🧠 Learning - Analytics and learning systems
- 📊 GitHub Pages - Timeline and public site

Note: Repeated similar tasks are collapsed with count (e.g., x12 means 12 occurrences).

This changelog excludes automated data syncs and routine maintenance commits.

---

## 2025-12-08

### 🧹 Chores & Maintenance

- 🤖 **Documentation**: Update CHANGELOG.md after PR merge (x3) [#3705](https://github.com/enufacas/Chained/pull/3705)

---

## 2025-12-07

### ✨ Features

- 👤 🏗️ Infrastructure Separate AI control plane from base infrastructure deployment [#3704](https://github.com/enufacas/Chained/pull/3704)
- 👤 🏗️ Infrastructure Complete AI-Native Control Plane with Terraform, CI/CD, and production GCP integration [#3679](https://github.com/enufacas/Chained/pull/3679)
- 👤 Migrate AG-Organism to React Three Fiber with futuristic factory theme, Drei components, procedurally-generated animated robot models, and A2A protocol visualization [#3672](https://github.com/enufacas/Chained/pull/3672)
- 🤖 🧠 Learning 🧠 Learn from GitHub Copilot sources - 2025-12-07 [#3686](https://github.com/enufacas/Chained/pull/3686)

### 🐛 Bug Fixes

- 👤 Replace Three.js 3D rendering with Canvas 2D to fix camera crash [#3700](https://github.com/enufacas/Chained/pull/3700)

### 🧹 Chores & Maintenance

- 👤 🏗️ Infrastructure **Documentation**: Add deployed AG-UI URLs reference + fix Terraform state import [#3703](https://github.com/enufacas/Chained/pull/3703)
- 🤖 **Documentation**: Update CHANGELOG.md after PR merge [#3694](https://github.com/enufacas/Chained/pull/3694)

---

## 2025-12-06

### ✨ Features

- 👤 🏗️ Infrastructure Implement GCP SDK integration for AI-NATIVE control plane (Phase 6 Step 4) [#3675](https://github.com/enufacas/Chained/pull/3675)
- 👤 🔧 Agents UI: Add per-agent completion status to multi-agent session display [#3676](https://github.com/enufacas/Chained/pull/3676)
- 👤 Implement Phase 6 Step 3 - Vector Database Integration for AI-Native Control Plane [#3671](https://github.com/enufacas/Chained/pull/3671)
- 👤 AI-Native Control Plane Phase 6: Production database schemas and LLM integration [#3669](https://github.com/enufacas/Chained/pull/3669)
- 👤 Complete AI-Native Control Plane Phase 5 MVP with end-to-end examples [#3666](https://github.com/enufacas/Chained/pull/3666)
- 👤 AI-Native Control Plane Phase 4: Execution layer skeleton services [#3662](https://github.com/enufacas/Chained/pull/3662)
- 👤 🔧 Agents Phase 3: AI-Native Control Plane agent design (LangChain tools + LangGraph orchestration) [#3658](https://github.com/enufacas/Chained/pull/3658)
- 🤖 🧠 Learning 🧠 Learn from GitHub Copilot sources - 2025-12-06 [#3647](https://github.com/enufacas/Chained/pull/3647)
- 👤 🏗️ Infrastructure Host AG-Organism visualization on Cloud Run with dynamic environment injection [#3634](https://github.com/enufacas/Chained/pull/3634)
- 👤 🔧 Agents Add AG-Organism: 3D cyberpunk visualization frontend for A2A agent coordination [#3632](https://github.com/enufacas/Chained/pull/3632)

### 🐛 Bug Fixes

- 👤 Use heredoc syntax for error_message in handle-cloudrun-errors.yml [#3664](https://github.com/enufacas/Chained/pull/3664)
- 👤 🏗️ Infrastructure Fix ag-organism-frontend deployment: add missing Terraform targets [#3655](https://github.com/enufacas/Chained/pull/3655)
- 👤 Add CORS headers to AG-UI Frontend API endpoints (x2) [#3642](https://github.com/enufacas/Chained/pull/3642)
- 👤 ⚙️ Workflows Fix: ag-organism-frontend not deployed by Terraform workflow [#3638](https://github.com/enufacas/Chained/pull/3638)
- 👤 Fix AG-Organism frontend: bundle Three.js locally and add error logging [#3636](https://github.com/enufacas/Chained/pull/3636)

### 🧹 Chores & Maintenance

- 🤖 **Documentation**: Update CHANGELOG.md after PR merge (x20) [#3678](https://github.com/enufacas/Chained/pull/3678)
- 👤 **Documentation**: AI-Native Control Plane Phase 1 (Foundations) [#3645](https://github.com/enufacas/Chained/pull/3645)
- 👤 **Test**: Phase 2: AI-Native Control Plane service architecture and API specifications (x2) [#3656](https://github.com/enufacas/Chained/pull/3656)
- 👤 **Test**: Bootstrap AI-Native Control Plane: Create master control specification [#3643](https://github.com/enufacas/Chained/pull/3643)

---

## 2025-12-05

### ✨ Features

- 🤖 🧠 Learning 🧠 Learn from GitHub Copilot sources - 2025-12-05 [#3617](https://github.com/enufacas/Chained/pull/3617)

### 🐛 Bug Fixes

- 👤 Fix AG-UI pipeline state updates and error observer configuration [#3629](https://github.com/enufacas/Chained/pull/3629)

---

## 2025-12-04

### ✨ Features

- 👤 🔧 Agents Add intentional ZeroDivisionError to code-reviewer agent for error_observer testing [#3603](https://github.com/enufacas/Chained/pull/3603)
- 🤖 🧠 Learning 🧠 Learn from GitHub Copilot sources - 2025-12-04 [#3596](https://github.com/enufacas/Chained/pull/3596)
- 👤 Restructure Copilot section for demo/presentation format [#3218](https://github.com/enufacas/Chained/pull/3218)
- 👤 Streamline A2A section and remove production-ready language [#3520](https://github.com/enufacas/Chained/pull/3520)

### 🐛 Bug Fixes

- 👤 Fix ERROR_OBSERVER_URL runtime access via Next.js dynamic export [#3591](https://github.com/enufacas/Chained/pull/3591)
- 👤 Fix ERROR_OBSERVER_URL not set: remove fallback, add diagnostics, verify deployment [#3587](https://github.com/enufacas/Chained/pull/3587)
- 👤 Add dual test buttons for Error Observer: internal dispatch + GitHub webhook pipeline [#3582](https://github.com/enufacas/Chained/pull/3582)

### 🧹 Chores & Maintenance

- 🤖 **Documentation**: Update CHANGELOG.md after PR merge (x7) [#3604](https://github.com/enufacas/Chained/pull/3604)
- 👤 📚 Docs **Documentation**: Add dedicated Demo & Deep Dive documentation page [#3579](https://github.com/enufacas/Chained/pull/3579)

---

## 2025-12-03

### ✨ Features

- 👤 🔧 Agents Rename @create-guru agent to @create-botter [#3575](https://github.com/enufacas/Chained/pull/3575)
- 🤖 🧠 Learning 🧠 Learn from GitHub Copilot sources - 2025-12-03 [#3562](https://github.com/enufacas/Chained/pull/3562)

### 🐛 Bug Fixes

- 👤 🔧 Tools Fix TypeScript build error: use shared Pipeline interface in PipelineOutcomes [#3580](https://github.com/enufacas/Chained/pull/3580)
- 👤 Fix AG-UI frontend: ERROR_OBSERVER_URL runtime config, localStorage quota, and pipeline detail persistence [#3558](https://github.com/enufacas/Chained/pull/3558)
- 👤 Fix session timestamp preservation in work history page [#3555](https://github.com/enufacas/Chained/pull/3555)
- 👤 Fix AG-UI Error Observer config race condition and session persistence data loss [#3554](https://github.com/enufacas/Chained/pull/3554)
- 👤 Fix localStorage quota exceeded in AG-UI team runs and add E2E tests [#3552](https://github.com/enufacas/Chained/pull/3552)

### 🧹 Chores & Maintenance

- 🤖 **Documentation**: Update CHANGELOG.md after PR merge (x11) [#3569](https://github.com/enufacas/Chained/pull/3569)
- 👤 📋 Instructions **Documentation**: Update A2A README with error observer system and add maintenance instructions [#3520](https://github.com/enufacas/Chained/pull/3520)

---

## 2025-12-02

### ✨ Features

- 👤 🔧 Agents Add missing agents to AG-UI activity monitoring, implement end-to-end error reporting, and update A2A documentation [#3546](https://github.com/enufacas/Chained/pull/3546)
- 👤 Implement main-branch-only automated changelog with 100% PR coverage, codebase area grouping, actor differentiation, auto-merge, and smart deduplication [#3519](https://github.com/enufacas/Chained/pull/3519)
- 🤖 🧠 Learning 🧠 Learn from GitHub Copilot sources - 2025-12-02 [#3524](https://github.com/enufacas/Chained/pull/3524)

### 🐛 Bug Fixes

- 👤 resolve ESLint errors in AG-UI Frontend storage.ts [#3550](https://github.com/enufacas/Chained/pull/3550)
- 👤 🔧 Agents Fix error-observer GitHub dispatch, agent display, localStorage quota, concurrent writes, and A2A protocol compliance [#3548](https://github.com/enufacas/Chained/pull/3548)
- 👤 🔧 Agents Enable Vertex AI API for ADK agent authentication [#3542](https://github.com/enufacas/Chained/pull/3542)
- 👤 ⚙️ Workflows Add missing Cloud Run service imports to Terraform workflow [#3540](https://github.com/enufacas/Chained/pull/3540)
- 👤 🔧 Tools Fix TypeScript ESLint errors in AG-UI frontend and add configurable GitHub repo for error-observer [#3537](https://github.com/enufacas/Chained/pull/3537)
- 👤 ⚙️ Workflows Fix critical error observer issues: Terraform data source, missing workflow, security vulnerability [#3535](https://github.com/enufacas/Chained/pull/3535)
- 👤 Implement A2A-native error observer system with GitHub dispatch integration [#3520](https://github.com/enufacas/Chained/pull/3520)

### 🧹 Chores & Maintenance

- 🤖 **Documentation**: Update CHANGELOG.md after PR merge (x2) [#3534](https://github.com/enufacas/Chained/pull/3534)

---

## 2025-12-01

### ✨ Features

- 👤 Add "ask gemini" escalation standard for Copilot sessions [#3510](https://github.com/enufacas/Chained/pull/3510)
- 👤 📋 Instructions Add instruction source diagram generator for PR transparency [#3506](https://github.com/enufacas/Chained/pull/3506)
- 👤 ⚙️ Workflows Add daily schedule and auto-merge to learn-from-copilot workflow (x2) [#3503](https://github.com/enufacas/Chained/pull/3503)
- 👤 ⚙️ Workflows update-context-summaries workflow to daily with auto-merge [#3502](https://github.com/enufacas/Chained/pull/3502)
- 🤖 🧠 Learning 🧠 Learn from GitHub Copilot sources - 2025-12-01 [#3499](https://github.com/enufacas/Chained/pull/3499)
- 👤 ⚙️ Workflows Add auto-merge to agentops-data-sync workflow [#3496](https://github.com/enufacas/Chained/pull/3496)
- 👤 ⚙️ Workflows Add A2A protocol artifacts to AG-UI and improve workflow UX [#3487](https://github.com/enufacas/Chained/pull/3487)
- 👤 🔧 Agents Design proposal: Agent as Code infrastructure management [#3475](https://github.com/enufacas/Chained/pull/3475)
- 👤 AG-UI: Artifact preview overlay, localStorage persistence, expandable steps [#3470](https://github.com/enufacas/Chained/pull/3470)
- 👤 mobile-friendly AG-UI redesign with combined progress/outcomes [#3469](https://github.com/enufacas/Chained/pull/3469)

### 🐛 Bug Fixes

- 👤 🔧 Agents Transform gemini-consultant from analysis provider to code-fixing agent with full repository access via MCP [#3514](https://github.com/enufacas/Chained/pull/3514)
- 👤 Add frontend error logging and retry logic to A2A UI [#3516](https://github.com/enufacas/Chained/pull/3516)
- 👤 Fix AG-UI Frontend OOM crashes causing missing artifacts and progress failures [#3512](https://github.com/enufacas/Chained/pull/3512)
- 👤 🏗️ Infrastructure Fix: Move max_instance_request_concurrency to template level in Terraform [#3509](https://github.com/enufacas/Chained/pull/3509)
- 👤 🏗️ Infrastructure Fix: Add max_instance_request_concurrency=1 for Cloud Run services with CPU < 1 [#3508](https://github.com/enufacas/Chained/pull/3508)
- 👤 🏗️ Infrastructure Fix: Reduce Cloud Run CPU allocation to resolve quota exceeded error [#3507](https://github.com/enufacas/Chained/pull/3507)
- 👤 [WIP] Fix blank session data in history section [#3501](https://github.com/enufacas/Chained/pull/3501)
- 👤 Add graceful fallback to direct Anthropic API when Vertex AI auth fails [#3416](https://github.com/enufacas/Chained/pull/3416)
- 👤 Fix artifact persistence and parallel execution dependencies in A2A pipeline [#3497](https://github.com/enufacas/Chained/pull/3497)
- 👤 Fix: Persist full turnResults in team session storage [#3495](https://github.com/enufacas/Chained/pull/3495)
- 👤 Fix session state race conditions causing stuck progress and stale data on refresh [#3493](https://github.com/enufacas/Chained/pull/3493)
- 👤 Fix session state tracking race conditions and progress display issues (PR ) [#3492](https://github.com/enufacas/Chained/pull/3492)
- 👤 Fix AG-UI session persistence and filter terminology [#3492](https://github.com/enufacas/Chained/pull/3492)
- 👤 ⚙️ Workflows Fix AG-UI team workflow completion tracking and add A2A artifact persistence [#3491](https://github.com/enufacas/Chained/pull/3491)
- 👤 🏗️ Infrastructure Fix npm ci failure in AG-UI Frontend Docker build [#3490](https://github.com/enufacas/Chained/pull/3490)
- 👤 Fix AG-UI real-time progress updates, session accumulation, and artifact streaming [#3476](https://github.com/enufacas/Chained/pull/3476)

### 🧹 Chores & Maintenance

- 👤 ⚙️ Workflows **Documentation**: Remove goal-and-idea-system workflow and cleanup related documentation [#3504](https://github.com/enufacas/Chained/pull/3504)
- 👤 ⚙️ Workflows **Documentation**: Add disabled workflows report documenting purpose, triggers, and artifacts [#3431](https://github.com/enufacas/Chained/pull/3431)
- 👤 🔧 Agents **Documentation**: streamline README and document Agent Canvas features [#3489](https://github.com/enufacas/Chained/pull/3489)

---
