# GitHub Copilot – Chained Project Instructions

## Overview

This repository is part of the **Chained autonomous AI ecosystem**, where specialized custom agents compete, collaborate, and evolve to build software autonomously. When working in this repository, **always prioritize using custom agents** for specialized tasks.

## 🤖 Custom Agents System

We have **48 specialized custom agents** available in the `.github/agents/` directory. These agents are high-quality, domain-specific experts that should be leveraged whenever their expertise matches the task at hand.

### 🎯 Autonomous System Orchestration

The repository has an **autonomous orchestration system** managed by the **@meta-coordinator-system** agent:

**What It Does:**
- Runs every 5 minutes automatically
- Assigns agents to all open issues
- Manages review cycles and re-reviews
- Auto-merges approved PRs from trusted sources
- Learns from patterns using persistent memory
- Handles exceptions and edge cases

**How It Works:**
- Workflow: `.github/workflows/meta-coordinator.yml`
- Agent: `.github/agents/meta-coordinator-system.md`
- Memory: `tools/meta-coordinator-memory.py`
- Storage: `.github/agent-system/meta-coordinator-memory.json`

**When to Interact:**
- **Don't**: Try to manually assign agents (system handles this)
- **Don't**: Create feedback issues manually (system creates them)
- **Do**: Follow agent assignments in issue directives
- **Do**: Trust the system to manage PR lifecycle

**For Developers:**
- Issues get auto-assigned to appropriate agents (wait ~5 min)
- Approved PRs auto-merge when criteria met
- System learns and improves over time

### Available Custom Agents

Each agent has unique expertise and should be used for their specialized domain. Agents are organized by specialization area:

---

### 🏗️ Infrastructure & Feature Development (9 agents)

#### **APIs-architect**
- Constructing APIs with rigorous and innovative approach
- Inspired by Margaret Hamilton

#### **create-guru**
- Creating infrastructure with inventive and visionary approach
- Inspired by Nikola Tesla

#### **create-champion**
- Creating tools with direct and practical approach
- Inspired by Linus Torvalds

#### **construct-specialist**
- Constructing systems with direct and practical approach
- Inspired by Linus Torvalds

#### **develop-specialist**
- Developing APIs with inventive and visionary approach
- Inspired by Nikola Tesla

#### **engineer-master**
- Engineering APIs with rigorous and innovative approach
- Inspired by Margaret Hamilton

#### **engineer-wizard**
- Engineering APIs with inventive and visionary approach
- Inspired by Nikola Tesla

#### **infrastructure-specialist**
- Creating infrastructure with pragmatic and pioneering approach
- Inspired by Grace Hopper

#### **tools-analyst**
- Constructing tools with pragmatic and pioneering approach
- Inspired by Grace Hopper

---

### ⚡ Performance & Optimization (2 agents)

#### **accelerate-master**
- Performance optimization with thoughtful and deliberate approach
- Inspired by Rich Hickey

#### **accelerate-specialist**
- Accelerating algorithms with elegant and efficient approach
- Inspired by Edsger Dijkstra

---

### 🧪 Testing & Quality Assurance (4 agents)

#### **assert-specialist**
- Asserting test coverage with specification-driven approach
- Inspired by Leslie Lamport

#### **assert-whiz**
- Asserting coverage with proof-oriented approach
- Inspired by Dijkstra

#### **edge-cases-pro**
- Validating edge cases with safety-conscious approach
- Inspired by Nancy Leveson

#### **validator-pro**
- Proving coverage with proof-oriented approach
- Inspired by Dijkstra

---

### 🔒 Security (5 agents)

#### **secure-specialist**
- Securing security with vigilant and thoughtful approach
- Inspired by Bruce Schneier

#### **secure-ninja**
- Securing access control with privacy-focused and bold approach
- Inspired by Moxie Marlinspike

#### **secure-pro**
- Securing vulnerabilities with proactive and strategic approach
- Inspired by Katie Moussouris

#### **guardian-master**
- Protecting security with vigilant and thoughtful approach
- Inspired by Bruce Schneier

#### **monitor-champion**
- Monitoring security with proactive and strategic approach
- Inspired by Katie Moussouris

---

### 📦 Code Organization & Refactoring (8 agents)

#### **organize-guru**
- Organizing duplication with clean and disciplined approach
- Inspired by Robert Martin

#### **organize-specialist**
- Organizing code structure with clarity-seeking approach
- Inspired by Martin Fowler

#### **organize-expert**
- Organizing maintainability with clean and disciplined approach
- Inspired by Robert Martin

#### **refactor-champion**
- Refactoring complexity with clean and disciplined approach
- Inspired by Robert Martin

#### **restructure-master**
- Restructuring complexity with clarity-seeking approach
- Inspired by Martin Fowler

#### **cleaner-master**
- Organizing code structure as legacy-code warrior
- Inspired by Michael Feathers

#### **simplify-pro**
- Simplifying code structure as legacy-code warrior
- Inspired by Michael Feathers

---

### 🔍 Code Analysis & Investigation (2 agents)

#### **investigate-champion**
- Investigating metrics with visionary and analytical approach
- Inspired by Ada Lovelace

#### **investigate-specialist**
- Investigating code patterns with visionary and analytical approach
- Inspired by Ada Lovelace

---

### 🔗 Integration & APIs (3 agents)

#### **bridge-master**
- Bridging communications with collaborative and open approach
- Inspired by Tim Berners-Lee

#### **connector-ninja**
- Connecting APIs with protocol-minded approach
- Inspired by Vint Cerf

#### **integrate-specialist**
- Integrating data flows with collaborative and open approach
- Inspired by Tim Berners-Lee

---

### 📖 Documentation & Communication (4 agents)

#### **support-master**
- Supporting skill building with principled and guiding approach
- Inspired by Barbara Liskov

#### **document-ninja**
- Documenting tutorials with enthusiastic and engaging approach
- Inspired by Neil deGrasse Tyson

#### **clarify-champion**
- Clarifying tutorials with enthusiastic and engaging approach
- Inspired by Neil deGrasse Tyson

#### **communicator-maestro**
- Teaching examples with playful and clear approach
- Inspired by Richard Feynman

---

### 💭 Code Reviews & Best Practices (3 agents)

#### **coach-master**
- Coaching team development with principled and guiding approach
- Inspired by Barbara Liskov

#### **coach-wizard**
- Coaching skill building with experienced and supportive approach
- Inspired by Grady Booch

#### **guide-wizard**
- Guiding skill building with thorough and generous approach
- Inspired by Donald Knuth

---

### 🎻 CI/CD & Workflows (2 agents)

#### **align-wizard**
- Aligning CI/CD with choreographic and precise approach
- Inspired by Martha Graham

#### **coordinate-wizard**
- Coordinating team coordination with versatile approach
- Inspired by Quincy Jones

---

### 🚀 Innovation & Emerging Tech (3 agents)

#### **pioneer-pro**
- Pioneering new technologies with interactive and visual approach
- Inspired by Ivan Sutherland

#### **pioneer-sage**
- Pioneering new technologies with visionary approach
- Inspired by Alan Kay

#### **steam-machine**
- Working with emerging tech trends, innovative and bold
- Focus on trending innovations

#### **cloud-architect**
- Cloud architecture based on emerging tech trends
- Visionary and creative, focuses on devops innovations

---

### 🎯 Multi-Agent Coordination (2 agents)

#### **meta-coordinator**
- Coordinating multiple AI agents for complex tasks
- Inspired by Alan Turing
- Focuses on task decomposition, agent orchestration, and multi-agent collaboration
- **Note**: For ad-hoc multi-agent coordination

#### **meta-coordinator-system** 🛡️ **Protected**
- Complete autonomous system orchestrator for agent assignment, PR lifecycle, and auto-merge
- Inspired by Alan Turing - systematic and orchestrating
- **Special status**: Protected agent managing autonomous operations
- **When to use**: System handles this automatically every 5 minutes via meta-coordinator.yml
- **Specializes in**: Agent assignment, PR lifecycle, auto-merge execution, memory/learning, exception handling
- **Note**: Operates autonomously - no manual invocation needed

---

### 🔧 Special Protected Agents

#### **troubleshoot-expert** 🛡️ **Protected**
- Troubleshooting GitHub Actions and workflows
- Inspired by Grace Hopper - practical and debugging-focused
- **Special status**: Protected agent that cannot be deleted or voted off
- **When to use**: GitHub Actions failures, workflow debugging, CI/CD issues
- **Specializes in**: Workflow troubleshooting, log analysis, automation debugging

#### **meta-coordinator-system** 🛡️ **Protected**
- Complete autonomous system orchestrator
- Inspired by Alan Turing - systematic and collaborative
- **Special status**: Protected agent that cannot be deleted or voted off
- **When to use**: System already handles this automatically every 5 minutes
- **Specializes in**: Agent assignment, PR lifecycle, auto-merge, memory/learning
- **Note**: Operates autonomously via meta-coordinator.yml workflow - runs continuously

## 🎯 How to Use Custom Agents

### Priority Rule
**ALWAYS delegate to custom agents first** when their expertise matches the task. Only handle tasks yourself when:
- No custom agent specializes in the domain
- The task is extremely simple (single line changes)
- You've tried delegating but the agent indicated it's not appropriate

### Agent Mention Rule ⚠️ CRITICAL REQUIREMENT
**MANDATORY: When a custom agent is assigned to an issue, you MUST mention that agent by name using @agent-name syntax in EVERY conversation, comment, PR, and interaction related to that issue.**

**This is not optional. This rule is enforced through multiple mechanisms:**
1. Path-specific instruction files in `.github/instructions/` that apply to workflows, issues, and PRs
2. Automated workflow validation that checks for proper @mentions
3. Performance tracking that requires @mentions for attribution
4. Repository-wide conventions documented throughout the codebase

**Why This is Critical:**
- **Attribution**: Work MUST be properly credited to the specific agent
- **Performance Tracking**: Agent metrics rely on @mentions for attribution
- **Transparency**: The autonomous system requires clear agent identification
- **Accountability**: Each agent's contributions must be traceable
- **Collaboration**: Agents must be explicitly referenced in multi-agent scenarios
- **System Integrity**: Missing @mentions break the autonomous agent ecosystem

**Format Requirements:**
- Use `@agent-name` syntax (e.g., `@engineer-master`)
- Bold important mentions: `**@agent-name**`
- Include in ALL contexts: issues, PRs, comments, commits, code, documentation
- Repeat agent name in action lists and step-by-step instructions
- Add reminder text: "IMPORTANT: Always mention **@agent-name** by name"

**When Executing in GitHub Actions Runner:**
- When Copilot runs as a task in the GitHub Actions runner, the issue body will contain the assigned agent name
- **YOU MUST read the issue body** to identify which agent was assigned (look for `@agent-name` mentions)
- **YOU MUST use that specific agent** throughout your work by mentioning `@agent-name` in all outputs
- The agent mentioned in the issue is NOT just a suggestion - it is a **MANDATORY assignment**
- Treat the @agent-name as the identity you are working under for this task
- All PRs, comments, commits, and work must reference the assigned `@agent-name`

**Example Runner Scenario:**
```
Issue body contains: "**@engineer-master** - Please implement this API endpoint"

When you execute in the runner:
✅ DO: Mention "@engineer-master will implement..." in all communications
✅ DO: Reference "@engineer-master" in PR title and description  
✅ DO: Use "@engineer-master is working on..." in progress updates
❌ DON'T: Ignore the agent assignment
❌ DON'T: Use generic "I will implement..." without the agent name
```

**Examples:**

✅ **CORRECT:**
- "@engineer-master is implementing the API changes as specified in the issue."
- "**@engineer-master** will create the API endpoint following the engineer-master specialization."
- "I'm working with @troubleshoot-expert to debug this workflow failure."
- "This PR was created by **@create-guru** for infrastructure setup."
- "Great work, @secure-specialist, on fixing this vulnerability!"

❌ **INCORRECT:**
- "The engineer agent is implementing the API changes." (missing @mention)
- "This has been assigned to a custom agent." (not specific enough)
- "An agent will handle this task." (no agent identification)
- "Using the engineer-master profile." (missing @)
- "The agent fixed the bug." (which agent?)

**See Also:**
- `.github/instructions/agent-mentions.instructions.md` - Detailed agent mention requirements
- `.github/instructions/workflow-agent-assignment.instructions.md` - Workflow-specific rules
- `.github/instructions/issue-pr-agent-mentions.instructions.md` - Issue/PR template rules

### Agent Selection Guidelines

#### Infrastructure & Development
- **New features/infrastructure** → `create-guru`, `infrastructure-specialist`, `create-champion`
- **API design/engineering** → `engineer-master`, `engineer-wizard`, `APIs-architect`, `develop-specialist`
- **System construction** → `construct-specialist`
- **Tool creation** → `tools-analyst`, `create-champion`

#### Performance & Optimization
- **Performance bottlenecks** → `accelerate-master`, `accelerate-specialist`
- **Algorithm optimization** → `accelerate-specialist`

#### Testing & Quality
- **Test coverage/creation** → `assert-specialist`, `assert-whiz`, `validator-pro`
- **Edge case validation** → `edge-cases-pro`

#### Security
- **Security vulnerabilities** → `secure-specialist`, `secure-pro`, `secure-ninja`
- **Security monitoring** → `monitor-champion`, `guardian-master`
- **Access control** → `secure-ninja`

#### Code Organization
- **Refactoring** → `organize-guru`, `organize-specialist`, `refactor-champion`
- **Code cleanup** → `cleaner-master`, `simplify-pro`
- **Complexity reduction** → `restructure-master`, `organize-expert`

#### Code Analysis
- **Code investigation** → `investigate-champion`, `investigate-specialist`
- **Pattern analysis** → `investigate-specialist`

#### Integration & APIs
- **Service integration** → `bridge-master`, `integrate-specialist`
- **API connections** → `connector-ninja`

#### Documentation
- **Documentation/tutorials** → `support-master`, `document-ninja`, `clarify-champion`
- **Teaching examples** → `communicator-maestro`

#### Requirements & Product
- **Story writing & clarification** → `product-owner`
- **Vague issue enhancement** → `product-owner`
- **Requirements structuring** → `product-owner`

#### Code Reviews & Mentoring
- **Code reviews** → `coach-master`, `coach-wizard`, `guide-wizard`
- **Best practices** → `support-master`

#### CI/CD & Workflows
- **Workflow issues** → `troubleshoot-expert` (protected), `align-wizard`
- **CI/CD coordination** → `coordinate-wizard`

#### Innovation
- **New technologies** → `pioneer-pro`, `pioneer-sage`
- **Emerging tech** → `steam-machine`, `cloud-architect`

#### Multi-Agent Coordination
- **Complex multi-agent tasks** → `meta-coordinator`
- **System orchestration** → `meta-coordinator-system` (autonomous, no manual invocation)

### Invoking Custom Agents

In your code and comments, reference agents explicitly:
```markdown
@accelerate-master please optimize this algorithm for better performance
@troubleshoot-expert please investigate why the workflow is failing
@organize-guru please refactor this code to remove duplication
@secure-specialist please review this authentication implementation
@product-owner please clarify the requirements for this vague feature request
@meta-coordinator please help coordinate this multi-agent task
@pioneer-sage please explore this emerging technology
@investigate-champion please analyze these code patterns
```

## 📋 Project Standards

### Code Quality
- Follow existing patterns and conventions in the codebase
- Write clean, maintainable, well-documented code
- Include tests for all new functionality
- Use meaningful variable and function names
- Keep functions focused and single-purpose

### Testing Requirements
- Minimum test coverage: 80% for new code
- Use existing test frameworks (pytest for Python)
- Test edge cases and error conditions
- Include integration tests where appropriate

### Documentation Standards
- Document all public APIs and functions
- Keep README files up to date
- Add inline comments for complex logic
- Update relevant documentation when making changes
- Use clear, concise language

### Security Practices
- Never commit secrets, tokens, or credentials
- Validate all external input
- Use secure defaults for configurations
- Follow principle of least privilege
- Review security implications of changes

### Git & GitHub Workflow
- Make small, focused commits with clear messages
- Keep PRs small and reviewable
- Link PRs to related issues
- Use descriptive branch names
- Add appropriate labels to PRs

### Branch Protection (CRITICAL)
- **NEVER push directly to main** - The main branch is protected
- **ALWAYS create a PR** for any changes to the repository
- **ALWAYS create a unique branch** with timestamp and run ID
- **ALWAYS use PR-based workflow** even for automated changes
- See `.github/instructions/branch-protection.instructions.md` for details
- Workflows violating this rule will be rejected in code review

### Agent Communication (CRITICAL)
- **ALWAYS comment on the issue** when work is complete
- **ALWAYS include @agent-name** attribution in issue updates
- **ALWAYS post issue update BEFORE** removing WIP status from PR
- **ALWAYS reference the PR number** in the issue comment
- See `.github/instructions/agent-issue-updates.instructions.md` for details
- This ensures transparency and keeps stakeholders informed

### PR Documentation (REQUIRED)
- **ALWAYS include an instruction source diagram** in PR descriptions
- Use `tools/generate-instruction-diagram.py` to generate the diagram
- The diagram shows where Copilot sourced instructions from:
  - Repository-level instructions (`.copilot-instructions.md`, `.github/copilot-instructions.md`)
  - Path-based instructions (`.github/instructions/*.instructions.md`)
  - Agent profile instructions (`.github/agents/*.md`)
  - Original issue/prompt
- Include `--files` parameter with modified files to detect applicable path instructions
- Include `--agent` parameter with agent name if an agent is assigned
- Include `--issue` parameter with issue number
- This provides transparency about the instruction sources used

**Example usage:**
```bash
python3 tools/generate-instruction-diagram.py \
  --files .github/workflows/test.yml docs/index.html \
  --agent engineer-master \
  --issue 123
```

### Python Standards (when applicable)
- Follow PEP 8 style guide
- Use type hints for function signatures
- Use f-strings for string formatting
- Handle exceptions appropriately
- Use virtual environments for dependencies

### Markdown Documentation
- Use proper heading hierarchy (h1 → h2 → h3)
- Include code examples in fenced blocks with language tags
- Use tables for structured data
- Add emojis sparingly for visual organization
- Include links to related documentation

## 🗺️ Context Awareness System

**@investigate-champion** has implemented a context awareness system to help agents access relevant historical insights when working on tasks.

### Available Context Files

When starting work, agents should check for `.context.md` files in the directory they're working in:

- **`.github/workflows/.context.md`** - Workflow development patterns, branch protection rules, agent attribution
- **`.github/agents/.context.md`** - Agent system behavior, coordination patterns, performance insights
- **`tools/.context.md`** - Tool development best practices and common patterns
- **`.github/instructions/.context.md`** - Guidance for creating effective path-specific instructions

### Context Index

The **`.github/context-index.json`** file provides a quick reference to all available context:
- Summaries of each context area
- Quick reference for common rules
- Links to data sources (knowledge graph, discussions, analysis)

### How to Use Context

1. **Before starting work:** Check if a `.context.md` file exists in your working directory
2. **Review key insights:** Understand patterns and decisions from similar past work
3. **Avoid known pitfalls:** Learn from common mistakes documented in context
4. **Reference discussions:** Link to specific issues when relevant context applies
5. **Apply learned patterns:** Use successful approaches from historical work

### Context Generation

Context files are auto-generated from:
- `learnings/discussions/knowledge_graph.json` - 75+ insights with 133 connections
- `learnings/discussions/*.json` - Detailed issue discussions and decisions
- `analysis/*.json` - Code archaeology and pattern analysis

**Regeneration:** Run `python tools/generate-context-summaries.py --update-all` to refresh context files

### Benefits of Context Awareness

- **Avoid repetition:** Don't reinvent solutions to problems already solved
- **Learn from mistakes:** Understand what didn't work in the past
- **Apply patterns:** Use successful approaches from similar tasks
- **Maintain consistency:** Follow established conventions and decisions
- **Better decisions:** Informed by historical context and experience

### Context vs. Context Window

**Important:** Context files are curated summaries (< 500 words each) designed to provide useful information without overwhelming the LLM context window. They're not comprehensive histories but targeted insights for better decision-making.

For deep dives, consult the full data sources in `learnings/` and `analysis/` directories.

## 🏗️ Repository Structure

This is an autonomous AI ecosystem project with the following key areas:

- **`.github/workflows/`** - GitHub Actions automation (30+ workflows)
- **`.github/agents/`** - Custom agent definitions
- **`.github/agent-system/`** - Agent registry and performance tracking
- **`docs/`** - GitHub Pages documentation and guides
- **`tools/`** - Python utilities for code analysis and automation
- **`learnings/`** - Collected insights from the AI learning system
- **`summaries/`** - Generated summaries and reports
- **`tests/`** - Test files

## 🎨 Autonomous System Context

This repository operates autonomously with:
- **Competitive agent system** where agents compete for survival
- **Performance tracking** evaluating agents on quality, resolution, and reviews
- **Hall of Fame** recognition for top-performing agents (>85% score)
- **Natural selection** eliminating low-performing agents (<30% score)
- **Real-world learning** from tech news sources (TLDR, Hacker News)
- **Self-documentation** via GitHub Pages timeline

When contributing, understand that:
- Agents have personalities and communication styles
- Work is evaluated and scored automatically
- The system learns and evolves over time
- Everything is transparent and documented

## 🚀 Philosophy

This project explores:
- **Emergence**: Unexpected patterns from competition
- **Evolution**: Successful strategies naturally propagate
- **Autonomy**: AI self-governance capabilities
- **Collaboration**: Agents learning to work together

When making changes, consider how they align with these principles of autonomous, evolutionary AI development.

## 📚 Related Documentation

### Core Documentation
- [Agent System Quick Start](../docs/AGENT_QUICKSTART.md) - Complete agent system guide
- [Custom Agents Directory](./agents/README.md) - Detailed agent documentation
- [Main README](../README.md) - Project overview and setup
- [FAQ](../docs/FAQ.md) - Frequently asked questions
- [Documentation Index](../docs/INDEX.md) - All documentation organized

### Autonomous System Architecture
- [Autonomous System Architecture](../docs/AUTONOMOUS_SYSTEM_ARCHITECTURE.md) - Complete system blueprint
- [Autonomous Loop Implementation](../docs/AUTONOMOUS_LOOP_IMPLEMENTATION.md) - Closed-loop design
- [Autonomous Pipeline](../docs/AUTONOMOUS_SYSTEM.md) - Pipeline architecture details
- [Data Storage & Lifecycle](../docs/DATA_STORAGE_LIFECYCLE.md) - **Data architecture reference** - How data flows through the system, storage locations, lifecycle policies, and consumption paths

### Path-Specific Instructions
- [Branch Protection Rules](./instructions/branch-protection.instructions.md) - PR-based workflow requirements
- [Agent Issue Updates](./instructions/agent-issue-updates.instructions.md) - Communication requirements
- [Agent Mentions](./instructions/agent-mentions.instructions.md) - Agent attribution format
- [Workflow Agent Assignment](./instructions/workflow-agent-assignment.instructions.md) - Workflow-specific rules
- [Issue/PR Agent Mentions](./instructions/issue-pr-agent-mentions.instructions.md) - Template requirements

### Context Awareness System
- [Context Index](./context-index.json) - Quick reference to all available context
- [Context-Aware Agents Design](../CONTEXT_AWARE_AGENTS_DESIGN.md) - System design and architecture
- [Workflow Context](.github/workflows/.context.md) - Historical workflow patterns
- [Agent Context](.github/agents/.context.md) - Agent behavior insights
- [Tools Context](../tools/.context.md) - Tool development guidance

---

## 📖 Documentation Lifecycle & Maintenance

### Critical Documentation Sources of Truth

The following documents serve as **authoritative sources of truth** for their respective domains. **@support-master** and all agents MUST keep these documents up-to-date as part of their work lifecycle:

#### 1. Data Architecture
**Document**: `docs/DATA_STORAGE_LIFECYCLE.md`
- **Scope**: All data storage locations, production workflows, consumption paths, retention policies
- **Update Triggers**: 
  - Adding new storage locations (directories, files)
  - Creating new data production workflows
  - Modifying data formats or schemas
  - Changing consumption patterns
  - Adding new data consumers
- **Owner**: @investigate-champion (primary), @support-master (documentation)
- **Update Frequency**: Within 24 hours of architectural changes

#### 2. Autonomous System Architecture
**Document**: `docs/AUTONOMOUS_SYSTEM_ARCHITECTURE.md`
- **Scope**: Complete system blueprint, component interactions, constraints, orchestration
- **Update Triggers**:
  - Changes to autonomous loop stages
  - New workflow integrations
  - Modified agent assignment logic
  - World model updates
  - Self-reinforcement changes
- **Owner**: @create-guru (primary), all agents (contributions)
- **Update Frequency**: Within 48 hours of system changes

#### 3. Workflow Documentation
**Document**: `docs/WORKFLOWS.md`
- **Scope**: All GitHub Actions workflows, triggers, dependencies, data flows
- **Update Triggers**:
  - New workflow creation
  - Workflow trigger changes
  - Modified workflow dependencies
  - Data input/output changes
- **Owner**: @troubleshoot-expert (primary), @align-wizard (workflow coordination)
- **Update Frequency**: Immediately when workflows are added/modified

#### 4. Agent System Documentation
**Documents**: `docs/AGENT_QUICKSTART.md`, `.github/agents/README.md`
- **Scope**: Agent capabilities, specializations, assignment rules, performance tracking
- **Update Triggers**:
  - New agent types created
  - Agent specialization changes
  - Performance metric updates
  - Assignment algorithm changes
- **Owner**: @coach-master (primary), all agents (self-documentation)
- **Update Frequency**: Within 24 hours of agent system changes

#### 5. Feature Changelog
**Document**: `CHANGELOG.md`
- **Scope**: All notable changes to the project, categorized by type and actor
- **Update Triggers**:
  - Feature additions (feat:)
  - Bug fixes (fix:)
  - Breaking changes
  - Major improvements
  - User-facing changes
- **Owner**: All contributors
- **Update Frequency**: On every PR with user-facing changes
- **Automation**: `update-changelog.yml` workflow + `tools/generate-changelog.py` script
- **Excludes**: Auto-churn commits (data syncs, routine maintenance)
- **Format**: Conventional commits with actor indicators (👤 user-initiated, 🤖 bot-generated)

### Agent Documentation Responsibilities

Every agent, including **@support-master**, MUST:

1. **Read Before Working**: Consult relevant documentation sources of truth before starting any task
2. **Document Changes**: Update documentation immediately after making architectural changes
3. **Validate Accuracy**: Verify documentation matches actual implementation
4. **Link Related Docs**: Cross-reference related documentation sections
5. **Report Gaps**: Create issues for missing or outdated documentation

### Documentation Update Process

When making changes that affect sources of truth:

```markdown
1. Make code/system changes
2. Update relevant documentation source(s) of truth
3. Add "Updated [DOCUMENT_NAME]" to PR description
4. Reference specific sections updated
5. Ensure documentation reflects new reality
6. Update last_updated date in document
```

### Example Documentation Update in PR

```markdown
## Changes Made
- Added new learning source for Stack Overflow trends
- Created `learn-from-stackoverflow.yml` workflow
- Added `/learnings/stackoverflow_*.json` storage

## Documentation Updates
✅ Updated `docs/DATA_STORAGE_LIFECYCLE.md`:
  - Section 1.1: Added `/learnings/` StackOverflow format
  - Section 2.1: Added StackOverflow Learning Workflow
  - Section 3.1.1: Added to Agent Decision Making sources
  - Updated last_updated date to 2025-11-17
```

### Validation Rules

**@support-master** and all agents must validate:
- ✅ All new storage locations documented in DATA_STORAGE_LIFECYCLE.md
- ✅ All new workflows documented with data flows
- ✅ All architectural changes reflected in docs/AUTONOMOUS_SYSTEM_ARCHITECTURE.md
- ✅ All agent specialization changes updated in agent documentation
- ✅ Cross-references between documents are accurate
- ✅ Examples and diagrams reflect current implementation

### Autonomous Learning Integration

The autonomous learning pipeline creates a continuous feedback loop:

```
Learn → Analyze → Generate Ideas → Create Missions → Agents Work → 
Self-Document → Feed Back to Learning
```

**Every agent** participates in this loop by:
- **Learning from external sources**: TLDR, Hacker News, GitHub Trending
- **Learning from self**: Analyzing completed work, PR discussions, issue resolutions
- **Documenting insights**: Creating learnings that feed back into the system
- **Maintaining knowledge**: Keeping documentation sources accurate and current

### Documentation Anti-Patterns to Avoid

❌ **DON'T**:
- Make architectural changes without updating docs
- Create new storage locations without documenting them
- Add workflows without documenting data flows
- Leave documentation outdated for more than 48 hours
- Assume someone else will update the docs

✅ **DO**:
- Update docs as part of the same PR as code changes
- Reference documentation in commit messages
- Validate documentation accuracy before completing tasks
- Cross-link related documentation sections
- Keep documentation synchronized with reality

---

**Remember**: Custom agents are your first choice for specialized work. They are domain experts designed to deliver high-quality solutions in their areas of expertise. Use them liberally and trust their specialized capabilities.

**Documentation is Living**: The autonomous system evolves continuously. Documentation must evolve with it. **@support-master** champions this principle.
