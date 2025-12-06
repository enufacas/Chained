# AI-Native Control Plane — Copilot Task Runner Instructions

This file defines **what we are building**, **why**, and **how Copilot should build it incrementally**.

It is the **project brain**.  
Copilot MUST save this file into the repository before doing any other work.

---

# 🚨 STEP ZERO — BOOTSTRAP INSTRUCTIONS (MUST RUN FIRST)

When this prompt is first pasted into Copilot:

1. Copilot MUST check if the file:

   `.github/copilot/tasks/ai-native-control-plane.md`

   already exists.

2. If **NOT** present:  
   - Create it.  
   - Populate it with **this entire document verbatim**.  
   - Respond with:  
     - "Master control file created."  
     - "Next: Start the AI-Native Control Plane tasks when ready."  
   - Then STOP.

3. If the file **already exists**:  
   - Respond:  
     - "Master control file detected — ready to continue."  
   - Identify next incomplete step.  
   - Wait for user instruction.

This ensures the system always has a stable, versioned master specification.

---

# 🌍 0. BIG PICTURE — WHAT WE ARE BUILDING (NORTH STAR)

We are building a **fully AI-native cloud operating system**.

A system where:

- **AIs operate cloud infrastructure, not humans**
- The only human interface is **voice or natural-language prompts**
- AI builds:
  - dynamic web forums
  - news/content aggregation systems
  - multi-page CRUD applications
  - microservices with REST/GraphQL APIs
  - event-driven workers and pipelines
  - dashboards and real-time feeds
  - embedding-based products (semantic search, personalized feeds)
  - *improved versions of itself* (self-evolving infra)

The platform grows in capability over time through:

- world state stored in **structured DBs**
- learned patterns stored in **vector memory**
- incremental **agent planning**
- reusable **semantic patterns**
- deterministic **infra actuation**

The end-state system should be able to handle requests like:

- "Create a web forum with posts, comments, upvotes, auth, and admin tools. Deploy it."
- "Build a news site that automatically pulls infrastructure announcements and displays them with tags."
- "Deploy version 0.2 of this control plane with improved planning and stronger validation."

The system is designed for:

- extensibility  
- observability  
- resiliency  
- self-improvement  

Everything in this multi-step plan advances toward that vision.

---

# 🤖 1. HOW COPILOT SHOULD WORK TOWARD THE BIG PICTURE

Copilot should:

- Treat this file as the **source of truth**.
- Execute tasks **incrementally** and **modularly**.
- Automate cloud deployment, planning, and application generation.
- Respect all architecture, naming conventions, schemas, and principles defined here.
- Ensure ALL generated code is:
  - deterministic  
  - typed  
  - documented  
  - modular  
  - tested or testable  

## 🔥 HIGH-LEVEL REQUIREMENTS FOR THE SYSTEM

### **Design Principles**
- AI-first  
- Modular  
- Extensible  
- Observable  
- Fault-tolerant  
- Deterministic planning  
- No Git required unless optional  
- No Terraform or IaC unless optional  

### **Emergent Behavior Guardrails**
Copilot must:
- Not invent new subsystems unless patterns exist in memory or prior artifacts.
- Prefer simple, composable designs.
- Use failure embeddings to avoid repeating mistakes.
- Offer incremental improvements, NOT sweeping redesigns.

### **Self-Improvement Capability**
Copilot may propose incremental self-upgrades **with user approval**, such as:
- new LangChain tools
- better validation logic
- plan optimization
- improved state schemas
- better infra-runner error recovery

The system should evolve safely.

---

# ⚙️ 2. GLOBAL EXECUTION RULES FOR COPILOT

1. **Dynamic Batching (1–3 Steps per Session)**  
   Copilot chooses how many consecutive steps it can complete safely.

2. **Hard Cutoff**  
   Copilot must stop early when:
   - output gets long  
   - step complexity is high  
   - commit boundaries make sense  

3. **User Override**  
   "Run Step X" → Only run Step X.

4. **Consistency Rules**
   Copilot must ensure:
   - naming conventions remain the same
   - all references to tools/agents match prior steps
   - schemas remain consistent
   - diagrams align with architecture

5. **Mandatory Session Footer**
   Every run ends with:
   - `Completed Steps: …`
   - `Next Step: …`
   - Resume command  
     > "Run Step X of the AI-Native Control Plane tasks."

6. **No Rewriting of This File**  
   Only modify earlier artifacts with explicit user approval.

---

# 🏗️ 3. PHASE 1 — FOUNDATIONS

## Step 1 — High-Level Project Overview

**File:**  
`/docs/ai-native/01_overview.md`

**Must Include:**

### Overview
- What an AI-native control plane is  
- Why it removes the need for:
  - Terraform
  - Git-based workflows
  - CI/CD
  - manual infrastructure ops  

### Components Summary
- ai-control-plane  
- infra-runner  
- state-db  
- vector-db  
- static-app-host  
- dynamic-app-host  
- event logs  
- observability layer  
- versioning scheme (system and schema)

### Architecture Diagrams
ASCII representations of:
- Request flow  
- Data access  
- Plan execution lifecycle  

### Design Principles
- Determinism
- Idempotency
- Pattern recognition
- High traceability
- Extensible tool system

---

## Step 2 — World State Data Model

**File:**  
`/docs/ai-native/02_state_and_memory.md`

**Must Include:**

### Structured DB Tables
- apps  
- infra_objects  
- operations (event log)  
- users  
- policies  
- plan_versions  
- schema_versions  

### Field-Level Requirements
- types  
- constraints  
- indexes  
- deterministic IDs  

### Operation Events
Each infra mutation MUST log:
- actor  
- plan_hash  
- before/after snapshots  
- timestamps  
- associated vector embeddings  

### Vector DB Schema
Enhanced metadata classification:
- pattern  
- template  
- style  
- intent  
- system upgrade proposal  
- migration plan  
- error+repair cases  

### Why Semantic Memory Matters
- enables planning reuse  
- enables system self-improvement  
- replaces Git history  
- removes need for file diffs  

---

# 🖧 4. PHASE 2 — SERVICE DESIGN

## Step 3 — Services Layout

**File:**  
`/docs/ai-native/03_services_layout.md`

**Must Include:**

### Service Responsibilities
- ai-control-plane: planning, memory, tool orchestration  
- infra-runner: deterministic GCP mutation  
- state-db: ground truth  
- vector-db: semantic memory  
- static-app-host: bucket hosting  
- dynamic-app-host: Cloud Run services  
- event-log: structured record of all actions  

### Networking Requirements
- private Cloud Run  
- service-to-service IAM  
- egress restrictions  
- endpoint protections  

### Observability
Every service MUST log:
- trace IDs  
- correlation IDs  
- OpenTelemetry spans  
- structured logs  

### Versioning Requirements
- Each service has an internal version  
- state-db schema versioning  
- tool version compatibility  

---

## Step 4 — Infra Runner API Contract

**File:**  
`/docs/ai-native/04_infra_runner_api.md`

**Must Include:**

### Endpoints
- `/deploy_static_site`
- `/deploy_dynamic_service`
- `/scale_service`
- `/attach_domain`
- `/validate_plan`
- `/check_service_health`
- `/check_bucket_health`

### Requirements
- Request/response schemas  
- Plan validation  
- Health checks  
- Error codes  
- Retry rules  
- Safe-mode behavior  

---

# 🧩 5. PHASE 3 — AGENT DESIGN

## Step 5 — LangChain Tool Definitions

**File:**  
`/docs/ai-native/05_langchain_tools.md`

**Tools to Define:**
- create_app_spec  
- build_static_app  
- build_dynamic_app  
- deploy_static_site  
- deploy_dynamic_service  
- update_app_state  
- fetch_memory_context  
- write_memory_context  
- propose_system_upgrade  
- evaluate_upgrade_proposal  

**Tool Requirements**
- deterministic schemas  
- structured JSON I/O  
- safe error escalation  
- logging  
- versioning  

---

## Step 6 — Agent Graph (LangGraph)

**File:**  
`/docs/ai-native/06_agent_graph.md`

**Must Include:**

### Agents
- Planner  
- Policy Agent  
- Memory Agent  
- App Builder Agent  
- Infra Agent  
- State Manager  
- Output Agent  

### State Modes
- Normal  
- Repair  
- Migration  
- Self-upgrade proposal  

### Planning Mechanics
- vector retrieval  
- plan scoring  
- deterministic hashing  
- fallback strategies  

### Failure Handling
- backoff  
- replan with error embeddings  
- operation rollback (if feasible)  

---

# 🧱 6. PHASE 4 — EXECUTION LAYER

## Step 7 — Infra Runner Skeleton

**File:**  
`/services/infra-runner/main.py`

Must include:
- typed endpoints  
- structured logs  
- retries  
- validation  
- deterministic IDs  
- TODO markers for full GCP integration  

---

## Step 8 — AI Control Plane Skeleton

**File:**  
`/services/ai-control-plane/main.py`

Must include:
- chain/graph scaffolding  
- tool calls  
- basic intent classification  
- stubs for state/vector DBs  
- operational telemetry  
- TODO for multi-step planning  

---

# 🚀 7. PHASE 5 — END-TO-END MVP

## Step 9 — Dynamic Site Flow Example

**File:**  
`/examples/dynamic_site_flow.md`

Include:
- request  
- plan  
- builder stub outputs  
- infra-runner stub outputs  
- final AI response  
- future extensions  

---

## Step 10 — Release Notes (v0.1.0)

**File:**  
`/docs/ai-native/10_release_notes_v0.1.0.md`

Include:
- implemented features  
- limitations  
- how to run  
- how to deploy  
- roadmap for dynamic apps and self-improvement  

---

# 🔁 8. RESUME INSTRUCTIONS

To batch steps:

> "Start the AI-Native Control Plane tasks."

To run a specific step:

> "Run Step X of the AI-Native Control Plane tasks."

---

# END OF MASTER CONTROL FILE
