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

## 2025-12-06

### ✨ Features

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

- 🤖 **Documentation**: Update CHANGELOG.md after PR merge (x15) [#3667](https://github.com/enufacas/Chained/pull/3667)
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

## 2025-11-30

### ✨ Features

- 👤 Unified single page with progressive disclosure for Team Mode [#3468](https://github.com/enufacas/Chained/pull/3468)
- 👤 ⚙️ Workflows Configure data-analyst & image-generator agents, add Agent Canvas workflow execution with turn-based config [#3460](https://github.com/enufacas/Chained/pull/3460)
- 👤 🔧 Agents Add dynamic multi-agent team system with turn-based orchestration [#3459](https://github.com/enufacas/Chained/pull/3459)
- 🤖 🧠 Learning 🧠 Learn from GitHub Copilot sources - 2025-11-30 [#3435](https://github.com/enufacas/Chained/pull/3435)
- 👤 🔧 Agents Enable Vertex AI model calls in A2A agents with interaction logging [#3448](https://github.com/enufacas/Chained/pull/3448)
- 👤 🔧 Agents Enhanced A2A UI with detailed agent prompts, step tracking, and docs [#3447](https://github.com/enufacas/Chained/pull/3447)
- 👤 🔧 Agents Enhanced A2A UI with real agent integration, pipeline analysis, faster polling, and detailed views [#3445](https://github.com/enufacas/Chained/pull/3445)
- 👤 🔧 Agents Side-by-side A2A UI with GCP Cloud Run agent activity and pipeline outcomes [#3444](https://github.com/enufacas/Chained/pull/3444)
- 👤 🔧 Agents Implement A2A Pipeline features - creation, agent interaction, and real-time status [#3438](https://github.com/enufacas/Chained/pull/3438)
- 👤 ⚙️ Workflows [WIP] Troubleshoot workflow failure in CI/CD pipeline [#3433](https://github.com/enufacas/Chained/pull/3433)
- 👤 🏗️ Infrastructure Add GCP infrastructure and A2A visualization to world model [#3424](https://github.com/enufacas/Chained/pull/3424)

### 🐛 Bug Fixes

- 👤 🔧 Agents [WIP] Fix failure in action runs and add separate jobs for agents [#3465](https://github.com/enufacas/Chained/pull/3465)
- 👤 [WIP] Fix Vertex AI generation failed error for model access [#3457](https://github.com/enufacas/Chained/pull/3457)
- 👤 🔧 Agents use gemini-3-pro-preview for ADK agents Vertex AI [#3456](https://github.com/enufacas/Chained/pull/3456)
- 👤 Fix Gemini API 401 error: Add unified client supporting Vertex AI mode [#3455](https://github.com/enufacas/Chained/pull/3455)
- 👤 ⚙️ Workflows [WIP] Fix issue in the action step of the workflow [#3453](https://github.com/enufacas/Chained/pull/3453)
- 👤 🏗️ Infrastructure Fix Terraform dynamic for_each invalid value error [#3450](https://github.com/enufacas/Chained/pull/3450)
- 👤 🔧 Agents Fix A2A agents to require Gemini AI - remove silent fallback to templates [#3449](https://github.com/enufacas/Chained/pull/3449)
- 👤 Change Vertex AI API from v1beta to v1 to resolve chat 404 errors [#3432](https://github.com/enufacas/Chained/pull/3432)
- 👤 Update Vertex AI model to gemini-2.0-flash (1.5 deprecated) [#3430](https://github.com/enufacas/Chained/pull/3430)
- 👤 Revert invalid Gemini model name causing 404 errors in AG-UI chat [#3428](https://github.com/enufacas/Chained/pull/3428)
- 👤 Update Gemini model from 1.5-flash to 2.0-flash-001 (1.5 deprecated) [#3425](https://github.com/enufacas/Chained/pull/3425)
- 👤 Add custom VertexAIAdapter for CopilotKit Vertex AI support [#3423](https://github.com/enufacas/Chained/pull/3423)
- 👤 Resolve ESLint unused variable errors blocking AG-UI Frontend deployment [#3422](https://github.com/enufacas/Chained/pull/3422)

### 🧹 Chores & Maintenance

- 👤 ⚙️ Workflows **Documentation**: Restructure README around three themes: Copilot conventions, A2A workflows, GCP experiments [#3462](https://github.com/enufacas/Chained/pull/3462)
- 👤 🔧 Agents **Documentation**: Complete GitHub MCP server tool reference and remove redundant tool restrictions from agents [#3421](https://github.com/enufacas/Chained/pull/3421)
- 👤 **Documentation**: Document gcloud-mcp server configuration requirement for Copilot [#3420](https://github.com/enufacas/Chained/pull/3420)

---

## 2025-11-29

### ✨ Features

- 👤 Add gcloud-mcp server integration for Copilot [#3413](https://github.com/enufacas/Chained/pull/3413)
- 👤 Add Claude/Anthropic A2A provider with Vertex AI support [#3407](https://github.com/enufacas/Chained/pull/3407)
- 👤 🔧 Agents Select unique implementing agent that hasn't participated in upstream analysis [#3400](https://github.com/enufacas/Chained/pull/3400)
- 👤 🔧 Agents Assign implementing agent to implement job and increase maxSessionTurns [#3394](https://github.com/enufacas/Chained/pull/3394)

### 🐛 Bug Fixes

- 👤 Fix chat failure: Add missing Vertex AI IAM role for service account [#3419](https://github.com/enufacas/Chained/pull/3419)
- 👤 Add gcloud-mcp server pre-install and verification to Copilot setup [#3418](https://github.com/enufacas/Chained/pull/3418)
- 👤 🏗️ Infrastructure Fix GCP MCP setup: Node.js version and JSON parsing issues [#3417](https://github.com/enufacas/Chained/pull/3417)
- 👤 Fix AG-UI chat: Support Vertex AI authentication with ADC [#3403](https://github.com/enufacas/Chained/pull/3403)
- 👤 Add retry logic for Gemini API transient errors in A2A implement step [#3404](https://github.com/enufacas/Chained/pull/3404)
- 👤 🏗️ Infrastructure Fix: Pass google_api_key_secret to Terraform for AG-UI Frontend [#3401](https://github.com/enufacas/Chained/pull/3401)
- 👤 🏗️ Infrastructure Fix: Pass GOOGLE_API_KEY to AG-UI Frontend Cloud Run service [#3396](https://github.com/enufacas/Chained/pull/3396)
- 👤 Simplify AG-UI Frontend with enhanced API key debugging [#3393](https://github.com/enufacas/Chained/pull/3393)
- 👤 Fix chat not displaying on interactive page and simplify A2A integration [#3387](https://github.com/enufacas/Chained/pull/3387)
- 👤 ⚙️ Workflows Fix bash arithmetic causing workflow failure in a2a-parallel-agents.yml [#3390](https://github.com/enufacas/Chained/pull/3390)

### 🧹 Chores & Maintenance

- 👤 📚 Docs **Documentation**: Add AG-UI Frontend troubleshooting guide with root cause discovery [#3408](https://github.com/enufacas/Chained/pull/3408)

---
