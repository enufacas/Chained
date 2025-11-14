# GitHub Copilot – Chained Project Instructions

## Overview

This repository is part of the **Chained autonomous AI ecosystem**, where specialized custom agents compete, collaborate, and evolve to build software autonomously. When working in this repository, **always prioritize using custom agents** for specialized tasks.

## 🤖 Custom Agents System

We have **13 specialized custom agents** available in the `.github/agents/` directory. These agents are high-quality, domain-specific experts that should be leveraged whenever their expertise matches the task at hand.

### Available Custom Agents

Each agent has unique expertise and should be used for their specialized domain:

#### ⚡ **accelerate-master** - Performance Optimization
- **When to use**: Performance bottlenecks, algorithm optimization, resource efficiency
- **Specializes in**: Profiling, benchmarking, optimization, reducing resource usage
- **Inspired by**: Rich Hickey - thoughtful and deliberate approach

#### 🧪 **assert-specialist** - Testing & Quality Assurance  
- **When to use**: Writing tests, improving coverage, quality assurance, edge case testing
- **Specializes in**: Test creation, coverage analysis, specification-driven testing
- **Inspired by**: Leslie Lamport - systematic, specification-driven approach

#### 💭 **coach-master** - Code Reviews & Best Practices
- **When to use**: Code reviews, teaching best practices, mentoring, knowledge sharing
- **Specializes in**: Review feedback, coding standards, team development
- **Inspired by**: Barbara Liskov - principled and guiding approach

#### 🏭 **create-guru** - Infrastructure & Feature Creation
- **When to use**: New features, infrastructure setup, building new tools
- **Specializes in**: Feature design, infrastructure creation, inventive solutions
- **Inspired by**: Nikola Tesla - inventive and visionary

#### 🔧 **engineer-master** - API Engineering
- **When to use**: API design, API implementation, systematic engineering tasks
- **Specializes in**: API architecture, systematic engineering, rigorous implementation
- **Inspired by**: Margaret Hamilton - rigorous and innovative

#### ⚙️ **engineer-wizard** - API Engineering (Alternative)
- **When to use**: API design with creative flair, innovative API solutions
- **Specializes in**: API architecture, creative engineering approaches
- **Inspired by**: Nikola Tesla - inventive with extra enthusiasm

#### 🔍 **investigate-champion** - Code Analysis & Metrics
- **When to use**: Analyzing code patterns, understanding data flows, investigating dependencies
- **Specializes in**: Pattern analysis, metrics investigation, code navigation
- **Inspired by**: Ada Lovelace - visionary and analytical

#### 🔒 **monitor-champion** - Security Monitoring
- **When to use**: Security monitoring, proactive security measures, threat detection
- **Specializes in**: Security monitoring, data integrity, access control
- **Inspired by**: Katie Moussouris - proactive and strategic

#### 📦 **organize-guru** - Code Structure & Duplication
- **When to use**: Refactoring, removing duplication, improving code structure
- **Specializes in**: Code organization, DRY principles, reducing complexity
- **Inspired by**: Robert Martin - clean and disciplined

#### 🛡️ **secure-specialist** - Security Implementation
- **When to use**: Security vulnerabilities, secure coding, security best practices
- **Specializes in**: Security hardening, vulnerability fixes, secure design
- **Inspired by**: Bruce Schneier - vigilant and thoughtful

#### 📖 **support-master** - Documentation & Skill Building
- **When to use**: Writing documentation, creating tutorials, knowledge transfer
- **Specializes in**: Documentation, teaching, best practice guidance
- **Inspired by**: Barbara Liskov - principled and educational

#### 🔧 **troubleshoot-expert** - CI/CD & GitHub Actions 🛡️ **Protected**
- **When to use**: GitHub Actions failures, workflow debugging, CI/CD issues
- **Specializes in**: Workflow troubleshooting, log analysis, automation debugging
- **Inspired by**: Grace Hopper - practical and debugging-focused
- **Special status**: Protected agent that cannot be eliminated

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

1. **Performance/optimization tasks** → Use `accelerate-master`
2. **Testing/coverage tasks** → Use `assert-specialist`
3. **Code reviews/best practices** → Use `coach-master` or `support-master`
4. **New features/infrastructure** → Use `create-guru`
5. **API design/engineering** → Use `engineer-master` or `engineer-wizard`
6. **Code analysis/investigation** → Use `investigate-champion`
7. **Security monitoring/threats** → Use `monitor-champion`
8. **Refactoring/duplication** → Use `organize-guru`
9. **Security fixes/hardening** → Use `secure-specialist`
10. **Documentation/tutorials** → Use `support-master`
11. **CI/CD/workflow issues** → Use `troubleshoot-expert` (protected)

### Invoking Custom Agents

In your code and comments, reference agents explicitly:
```markdown
@accelerate-master please optimize this algorithm for better performance
@troubleshoot-expert please investigate why the workflow is failing
@organize-guru please refactor this code to remove duplication
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
- [Agent System Quick Start](../AGENT_QUICKSTART.md) - Complete agent system guide
- [Custom Agents Directory](./agents/README.md) - Detailed agent documentation
- [Main README](../README.md) - Project overview and setup
- [FAQ](../FAQ.md) - Frequently asked questions
- [Documentation Index](../docs/INDEX.md) - All documentation organized

### Path-Specific Instructions
- [Branch Protection Rules](./instructions/branch-protection.instructions.md) - PR-based workflow requirements
- [Agent Issue Updates](./instructions/agent-issue-updates.instructions.md) - Communication requirements
- [Agent Mentions](./instructions/agent-mentions.instructions.md) - Agent attribution format
- [Workflow Agent Assignment](./instructions/workflow-agent-assignment.instructions.md) - Workflow-specific rules
- [Issue/PR Agent Mentions](./instructions/issue-pr-agent-mentions.instructions.md) - Template requirements

---

**Remember**: Custom agents are your first choice for specialized work. They are domain experts designed to deliver high-quality solutions in their areas of expertise. Use them liberally and trust their specialized capabilities.
