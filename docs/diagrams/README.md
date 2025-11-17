# Architecture Diagrams

This directory contains comprehensive architecture diagrams for the Chained autonomous AI ecosystem.

## Available Diagrams

### 1. [System Architecture](./system-architecture.md)
**Type**: Component Diagram (Mermaid)

Shows the high-level architecture of the entire Chained system, including:
- External learning sources (TLDR, Hacker News, AI Friends)
- Learning system and idea generation
- Issue management and agent matching
- Agent system and execution flow
- Development pipeline (PRs, review, merge)
- Monitoring and evolution (evaluation, Hall of Fame, elimination)
- Daily AI goal system

**Use this to**: Understand how all components interact in the autonomous ecosystem.

### 2. [Agent Lifecycle](./agent-lifecycle.md)
**Type**: State Diagram (Mermaid)

Illustrates the complete lifecycle of an agent from spawning to elimination or Hall of Fame entry:
- Spawning and registration
- Active work and implementation
- PR creation and review
- Performance evaluation
- Success paths (Hall of Fame) and failure paths (elimination)

**Use this to**: Understand agent states and transitions through their lifecycle.

### 3. [Workflow Timeline](./workflow-timeline.md)
**Type**: Gantt Chart (Mermaid)

Displays the 24-hour schedule of all workflows in the system:
- Daily goal generation and progress checks
- Learning activities (Hacker News, TLDR, AI Friends)
- Agent spawning (every 3 hours)
- Continuous operations (auto-review, auto-merge, etc.)
- Reporting and updates

**Use this to**: Plan around workflow execution times and understand system activity patterns.

### 4. [Data Flow](./data-flow.md)
**Type**: Data Flow Diagram (Mermaid)

Maps how data flows through the system:
- External data ingestion
- Data processing and storage
- Analysis and transformation
- Presentation on GitHub Pages
- Feedback loops

**Use this to**: Trace data paths and understand information processing.

### 5. [Agent Assignment Flow](./agent-assignment-flow.md)
**Type**: Sequence Diagram (Mermaid)

Details the step-by-step process of assigning issues to specialized agents:
- Issue creation
- Intelligent matching algorithm
- Agent profile loading
- Task execution with agent specialization
- PR creation with agent signature

**Use this to**: Understand how issues are matched to the right agent and how agents execute tasks.

### 6. [Security Architecture](./security-architecture.md)
**Type**: Security Layer Diagram (Mermaid)

Illustrates the multi-layer security model:
- Authentication layer (tokens, secrets)
- Authorization layer (CODEOWNERS, auto-merge rules)
- Validation layer (tests, review, linting)
- Monitoring layer (security scanning, alerts)
- Threat model and mitigations

**Use this to**: Understand security controls and how the system protects against threats.

### 7. [Troubleshooting Flow](./troubleshooting-flow.md) ⭐ NEW
**Type**: Decision Tree & Flowcharts (Mermaid)  
**Created by**: @clarify-champion

Comprehensive visual troubleshooting guide with 7 diagrams:
- Complete troubleshooting decision tree (50+ decision nodes)
- Quick decision matrix for fast issue categorization
- Diagnostic tool selection guide
- 5-step diagnostic method flowchart
- System state transitions (Healthy → Degraded → Critical)
- Issue distribution pie chart (based on real data)
- Resolution time analysis (Gantt chart by issue type)

**Use this to**: Systematically diagnose and resolve issues across all system components.

## Diagram Formats

All diagrams are created using **Mermaid**, a markdown-based diagramming tool that renders beautifully on GitHub.

### Benefits of Mermaid
- ✅ Renders automatically on GitHub
- ✅ Version controlled as text
- ✅ Easy to update and maintain
- ✅ Accessible (can be read as text)
- ✅ Professional appearance
- ✅ Multiple diagram types supported

### Viewing Diagrams

**On GitHub**: Simply navigate to any `.md` file in this directory. GitHub will automatically render the Mermaid diagrams.

**Locally**: Use a Mermaid-compatible markdown viewer:
- VS Code with "Markdown Preview Mermaid Support" extension
- IntelliJ/PyCharm with Mermaid plugin
- Online: [Mermaid Live Editor](https://mermaid.live/)

## Diagram Categories

### Structural Diagrams
- System Architecture: Overall system structure
- Security Architecture: Security layers and controls

### Behavioral Diagrams
- Agent Lifecycle: Agent state transitions
- Agent Assignment Flow: Issue assignment sequence
- Data Flow: Information movement

### Temporal Diagrams
- Workflow Timeline: 24-hour schedule

## How to Use These Diagrams

### For New Contributors
Start with:
1. **System Architecture** - Get the big picture
2. **Agent Lifecycle** - Understand agent behavior
3. **Workflow Timeline** - Know when things happen

### For Developers
Refer to:
1. **Agent Assignment Flow** - Implement agent features
2. **Data Flow** - Work with data pipelines
3. **Security Architecture** - Follow security guidelines

### For System Administrators
Review:
1. **Security Architecture** - Manage security
2. **Workflow Timeline** - Plan maintenance windows
3. **System Architecture** - Monitor components

### For Documentation Writers
Use:
1. All diagrams as visual aids
2. Reference diagrams in written docs
3. Update diagrams when architecture changes

## Maintaining Diagrams

### When to Update

Update diagrams when:
- ✅ New components are added to the system
- ✅ Workflow schedules change
- ✅ Security controls are modified
- ✅ Agent lifecycle changes
- ✅ Data flow paths are altered
- ✅ Major refactoring occurs

### Update Process

1. **Edit the Mermaid code** in the `.md` file
2. **Preview locally** to verify rendering
3. **Update documentation** that references the diagram
4. **Commit with clear message**: "docs: update [diagram name] for [reason]"
5. **Verify on GitHub** that diagram renders correctly

### Diagram Standards

**Keep diagrams**:
- ✅ Simple and focused (one concept per diagram)
- ✅ Properly labeled (clear node names)
- ✅ Color-coded (use color to group related elements)
- ✅ Well-documented (include explanatory text)
- ✅ Up-to-date (review quarterly)

## Related Documentation

- [docs/ARCHITECTURE.md](../ARCHITECTURE.md) - Main architecture document (references these diagrams)
- [docs/INDEX.md](../INDEX.md) - Complete documentation index
- [docs/QUICK_REFERENCE.md](../QUICK_REFERENCE.md) - Quick command reference
- [README.md](../../README.md) - Project overview

## Tools & Resources

### Mermaid Resources
- [Mermaid Documentation](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/) - Test diagrams online
- [Mermaid Syntax](https://mermaid.js.org/intro/syntax-reference.html)

### Diagram Types
- [Flowcharts](https://mermaid.js.org/syntax/flowchart.html)
- [Sequence Diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html)
- [State Diagrams](https://mermaid.js.org/syntax/stateDiagram.html)
- [Gantt Charts](https://mermaid.js.org/syntax/gantt.html)

### Color Schemes

We use consistent colors across diagrams:
- `#e1f5ff` - External sources (light blue)
- `#fff3cd` - Storage/data (light yellow)
- `#d4edda` - Success states (light green)
- `#f8d7da` - Security/warning (light red)
- `#cfe2ff` - Active processes (medium blue)
- `#d1ecf1` - Presentation/UI (light cyan)
- `#e2e3e5` - Monitoring/logs (light gray)

---

**Created by**: @assert-specialist, @clarify-champion  
**Last Updated**: 2025-11-17  
**Status**: ✅ Complete - 7 comprehensive diagrams (including troubleshooting)

💡 **Tip**: Bookmark this directory for quick reference when working on the Chained system!
