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

## 2025-12-10

### 🧹 Chores & Maintenance

- 🤖 **Documentation**: Update CHANGELOG.md after PR merge [#3740](https://github.com/enufacas/Chained/pull/3740)

---

## 2025-12-09

### ✨ Features

- 🤖 🧠 Learning 🧠 Learn from GitHub Copilot sources - 2025-12-09 [#3731](https://github.com/enufacas/Chained/pull/3731)

---

## 2025-12-08

### ✨ Features

- 🤖 🧠 Learning 🧠 Learn from GitHub Copilot sources - 2025-12-08 [#3714](https://github.com/enufacas/Chained/pull/3714)

### 🐛 Bug Fixes

- 👤 Fix ag-organism-frontend: Deploy 2D Canvas instead of crashing 3D React app [#3709](https://github.com/enufacas/Chained/pull/3709)
- 👤 ⚙️ Workflows Fix deployment separation: correct workflow paths and clean up deprecated terraform files [#3707](https://github.com/enufacas/Chained/pull/3707)

### 🧹 Chores & Maintenance

- 🤖 **Documentation**: Update CHANGELOG.md after PR merge (x6) [#3722](https://github.com/enufacas/Chained/pull/3722)

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

- 🤖 **Documentation**: Update CHANGELOG.md after PR merge (x8) [#3569](https://github.com/enufacas/Chained/pull/3569)
- 👤 📋 Instructions **Documentation**: Update A2A README with error observer system and add maintenance instructions [#3520](https://github.com/enufacas/Chained/pull/3520)

---

## 2025-12-02

### ✨ Features

- 👤 🔧 Agents Add missing agents to AG-UI activity monitoring, implement end-to-end error reporting, and update A2A documentation [#3546](https://github.com/enufacas/Chained/pull/3546)

### 🐛 Bug Fixes

- 👤 resolve ESLint errors in AG-UI Frontend storage.ts [#3550](https://github.com/enufacas/Chained/pull/3550)
- 👤 🔧 Agents Fix error-observer GitHub dispatch, agent display, localStorage quota, concurrent writes, and A2A protocol compliance [#3548](https://github.com/enufacas/Chained/pull/3548)
- 👤 🔧 Agents Enable Vertex AI API for ADK agent authentication [#3542](https://github.com/enufacas/Chained/pull/3542)

---
