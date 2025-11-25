# Agent Instruction Architecture Diagram

This diagram visualizes how the different levels of instructions combine to create the complete instruction set for an agent, and shows the various methods for invoking agents.

## Instruction Layers and Composition

```mermaid
graph TB
    subgraph "Complete Agent Instruction Set"
        direction TB
        
        subgraph Layer1["Layer 1: GitHub Copilot Built-in Instructions"]
            builtin["<b>Built-in Copilot Behavior</b><br/>• Code completion patterns<br/>• Language understanding<br/>• Tool usage fundamentals<br/>• GitHub API interactions"]
        end
        
        subgraph Layer2["Layer 2: Base Repository Instructions"]
            base["<b>.copilot-instructions.md</b><br/>• Agent catalog & selection<br/>• Code quality standards<br/>• Branch protection rules<br/>• Agent attribution rules<br/>• Documentation standards"]
        end
        
        subgraph Layer3["Layer 3: Agent-Specific Instructions"]
            agent["<b>.github/agents/agent-name.md</b><br/>• Personality & style<br/>• Domain expertise<br/>• Specialized tools<br/>• Approach & methodology<br/>• Performance criteria"]
        end
        
        Layer1 --> Layer2
        Layer2 --> Layer3
        
        Layer3 --> complete["<b>🎯 Complete Instruction Set</b><br/><br/>Built-in + Base + Agent-specific<br/><br/>Executed by GitHub Copilot"]
    end
    
    style Layer1 fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    style Layer2 fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Layer3 fill:#f3e5f5,stroke:#4a148c,stroke-width:3px
    style builtin fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style base fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style agent fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style complete fill:#c8e6c9,stroke:#1b5e20,stroke-width:4px
```

## Instruction Hierarchy as Venn Diagram

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'fontSize':'16px'}}}%%
graph LR
    subgraph "Agent Instruction Composition"
        A["<b>GitHub Copilot</b><br/><b>Built-in</b><br/><br/>• Core AI<br/>• Tools<br/>• APIs"]
        B["<b>Repository</b><br/><b>Base Instructions</b><br/><br/>• Standards<br/>• Rules<br/>• Conventions"]
        C["<b>Agent-Specific</b><br/><b>Instructions</b><br/><br/>• Personality<br/>• Expertise<br/>• Approach"]
        
        A -.->|"Always Present"| AB[Common Tools<br/>& Methods]
        B -.->|"Always Applied"| AB
        AB -.->|"When Agent Assigned"| ABC["<br/><b>🎯 Complete</b><br/><b>Agent Context</b><br/><br/>Copilot executes with<br/>full instruction stack"]
        C -.->|"Specialization"| ABC
    end
    
    style A fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    style B fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style C fill:#f3e5f5,stroke:#6a1b9a,stroke-width:3px
    style AB fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style ABC fill:#ffccbc,stroke:#d84315,stroke-width:4px
```

## Agent Invocation Methods

```mermaid
graph TB
    subgraph "How Agents are Invoked"
        
        Method1["<b>1. GitHub Copilot Chat</b><br/>Interactive sessions<br/>@agent-name in prompts"]
        Method2["<b>2. Issue Assignment</b><br/>Automatic matching<br/>Content analysis"]
        Method3["<b>3. Workflow Dispatch</b><br/>Programmatic invocation<br/>GitHub Actions"]
        Method4["<b>4. Copilot Coding Agent</b><br/>Full automation<br/>Runner execution"]
        
        Method1 --> Agent["<b>Agent Loaded</b><br/><br/>Instructions applied<br/>from all 3 layers"]
        Method2 --> Agent
        Method3 --> Agent
        Method4 --> Agent
        
        Agent --> Execute["<b>Task Execution</b><br/><br/>Follows complete<br/>instruction set"]
        
        Execute --> Output1["💬 Chat Response"]
        Execute --> Output2["📝 Code Changes"]
        Execute --> Output3["🔄 Pull Request"]
        Execute --> Output4["✅ Issue Resolution"]
    end
    
    style Method1 fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style Method2 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Method3 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    style Method4 fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    style Agent fill:#fff9c4,stroke:#f57f17,stroke-width:3px
    style Execute fill:#ffccbc,stroke:#d84315,stroke-width:3px
    style Output1 fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    style Output2 fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    style Output3 fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    style Output4 fill:#e0f2f1,stroke:#004d40,stroke-width:2px
```

## Detailed Instruction Layers

### Layer 1: GitHub Copilot Built-in Instructions

**Provided by**: GitHub Copilot platform  
**Scope**: Universal across all sessions  
**Content**:
- Code completion and generation capabilities
- Understanding of programming languages and frameworks
- Basic tool usage (git, terminal, file operations)
- GitHub API interaction patterns
- Standard software engineering practices

**Cannot be modified by repository**

### Layer 2: Base Repository Instructions

**Location**: `.copilot-instructions.md` (repository root)  
**Scope**: All agent sessions in this repository  
**Content**:
- **Agent System**: Catalog of available agents, selection guidelines, when to delegate
- **Code Quality**: Testing requirements, documentation standards, code style
- **Workflow Rules**: Branch protection, PR-based workflow, no direct pushes to main
- **Agent Communication**: @mention requirements, attribution format, issue updates
- **Project Standards**: Repository structure, file organization, security practices

**Applied to every agent automatically**

### Layer 3: Agent-Specific Instructions

**Location**: `.github/agents/{agent-name}.md`  
**Scope**: Only when specific agent is assigned/invoked  
**Content**:
- **Personality**: Communication style, tone, approach (e.g., "inspired by Grace Hopper")
- **Specialization**: Domain expertise (e.g., security, workflows, documentation)
- **Tools**: Preferred or required tools for the specialization
- **Methodology**: Step-by-step approaches specific to the domain
- **Performance Criteria**: How this agent's work is evaluated

**Applied only when agent is explicitly assigned**

## Example: Complete Instruction Set for `secure-specialist`

When `@secure-specialist` is invoked:

1. **GitHub Copilot Built-in** (Layer 1)
   - Understands code security concepts
   - Can use git, file operations, testing tools
   - Knows GitHub API for creating issues/PRs

2. **Base Instructions** (Layer 2)
   - Must follow branch protection (create PR, not push to main)
   - Must use @secure-specialist in all communications
   - Must write tests (80% coverage minimum)
   - Must update documentation for changes
   - Must handle secrets securely

3. **Agent-Specific** (Layer 3)
   - Personality: "Inspired by Bruce Schneier - vigilant and thoughtful"
   - Specialization: Security, data integrity, access control
   - Approach: Threat modeling, secure defaults, defense in depth
   - Tools: CodeQL, dependency scanning, security linters
   - Methods: Review authentication, validate input, check for common vulnerabilities

**Result**: A security-focused agent that follows all repository conventions while applying specialized security expertise.

## Invocation Flow Example

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant GitHub
    participant Workflow
    participant Copilot
    participant Agent as Agent Profile<br/>(.github/agents/)
    participant Base as Base Instructions<br/>(.copilot-instructions.md)
    participant Builtin as Copilot Built-in
    
    User->>GitHub: Create Issue:<br/>"Fix SQL injection vulnerability"
    GitHub->>Workflow: Trigger assignment workflow
    Workflow->>Workflow: Analyze issue content<br/>Match to agent
    Workflow-->>Workflow: Best match: secure-specialist
    Workflow->>GitHub: Update issue with<br/>@secure-specialist directive
    GitHub->>Copilot: Assign issue to<br/>github-copilot[bot]
    
    Copilot->>GitHub: Read issue body
    Copilot->>Agent: Load agent profile<br/>(secure-specialist.md)
    Agent-->>Copilot: Personality, specialization,<br/>tools, methods
    Copilot->>Base: Load base instructions<br/>(.copilot-instructions.md)
    Base-->>Copilot: Standards, rules,<br/>conventions
    Copilot->>Builtin: Apply built-in<br/>capabilities
    Builtin-->>Copilot: Core AI, tools,<br/>APIs
    
    Note over Copilot: Combine all 3 layers<br/>into complete context
    
    Copilot->>Copilot: Execute task with<br/>complete instruction set
    Note over Copilot: • Security-focused approach<br/>• Follow repo standards<br/>• Use Copilot capabilities
    
    Copilot->>GitHub: Create Pull Request<br/>with security fixes
    GitHub->>User: Notify PR created
```

## Benefits of Layered Architecture

### 🎯 Separation of Concerns
- **Built-in**: Platform capabilities (unchangeable)
- **Base**: Repository-wide standards (consistent)
- **Agent**: Specialized expertise (flexible)

### 🔄 Reusability
- Base instructions apply to all agents (write once, use everywhere)
- Agents can be added/modified without changing base rules
- Consistent standards across all agent work

### 🎨 Customization
- Each agent has unique personality and approach
- Domain-specific methods and tools per agent
- Easy to create new specialized agents

### 📈 Scalability
- Add new agents without modifying existing ones
- Update repository standards for all agents at once
- Clear boundaries between instruction levels

### 🔍 Transparency
- Easy to understand what instructions apply when
- Clear documentation of agent behavior
- Predictable results based on layer composition

---

## Related Documentation

- **[Agent Definitions](./../agents/README.md)** - Full catalog of available agents
- **[Agent Assignment Flow](./agent-assignment-flow.md)** - How issues are matched to agents
- **[Agent Lifecycle](./agent-lifecycle.md)** - Complete agent lifecycle
- **[README: Instruction Architecture](../../README.md#instruction-architecture)** - Overview in main README
- **[.copilot-instructions.md](../../.copilot-instructions.md)** - Base repository instructions

---

*This diagram is part of the Chained autonomous AI ecosystem documentation.*
