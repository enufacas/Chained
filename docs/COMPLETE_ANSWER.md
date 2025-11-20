# 📋 Complete Answer: How to Use the Chained Autonomous System

## 🎯 Quick Answer to Your Question

**Yes, you can just create an issue to try the system!** You don't need any special "complex" label - the system automatically analyzes your issue and assigns the best agent.

### The Simplest Way to Try It:

1. Click **[Create New Issue](../../issues/new)**
2. Write your issue title and description (e.g., "Add dark mode to docs")
3. Click **Submit**
4. **That's it!** The system automatically:
   - Analyzes your issue within 15 minutes
   - Selects the best specialized agent
   - Assigns Copilot to work on it
   - Creates a PR with the implementation
   - Auto-merges if tests pass
   - Closes your issue when done

**Timeline**: 15-30 minutes from issue creation to completed PR

---

## 📚 Complete Documentation

### Main Guide

**[📖 HOW_TO_TRIGGER_AGENTS.md](./HOW_TO_TRIGGER_AGENTS.md)** - Complete guide covering:
- How the autonomous system works
- How to create issues that trigger agents
- How to guide agent selection with keywords
- All 47+ available agent specializations
- Examples for different types of tasks
- FAQ about the system

### Quick References

**[❓ FAQ.md](../FAQ.md)** - Common questions including:
- Can I add a "complex" tag? (Answer: Yes, but not needed!)
- How does auto-assignment work?
- What's the timeline from issue to PR?

**[🚀 README.md](../README.md)** - Project overview with:
- Quick Start guide
- System architecture
- Live dashboard links
- Setup instructions

**[📑 docs/INDEX.md](./INDEX.md)** - Complete documentation index

---

## 🏷️ About Labels and Tags

### Current Label System

The system **automatically adds** these labels when processing your issue:

| Label | Applied When | Purpose |
|-------|--------------|---------|
| `copilot-assigned` | Issue assigned to Copilot | Tracks assignment |
| `agent:agent-name` | Agent profile selected | Identifies which agent approach to use |
| `automated` | Workflow processes it | Marks automated work |

### Can I Add My Own Labels?

**Yes!** You can add any labels you want to organize your issues, including:
- `complexity:high` / `complexity:medium` / `complexity:low`
- `priority:urgent`
- Any custom labels you create

However, **labels don't currently affect agent selection**. The system uses **content analysis** (keywords in your issue title and body) to match agents.

---

## 💡 Want Complexity-Based Routing?

If you want the system to consider complexity labels when selecting agents:

**See**: **[docs/enhancements/COMPLEXITY_BASED_ROUTING.md](./enhancements/COMPLEXITY_BASED_ROUTING.md)**

This enhancement proposal includes:
- How to add complexity labels to the system
- Code changes needed to make the agent matcher consider them
- Complete implementation guide
- Benefits and use cases

**Status**: This is an **optional enhancement** you can implement if you want it. The system works great without it!

---

## 🎮 Try It Now: 3 Examples

### Example 1: Simple Task (Beginner)
```markdown
Title: Add a search box to the documentation

Description:
The docs would be easier to navigate with a search feature.
Please add a search box to the docs index page.
```

**What happens**:
- System analyzes: "search", "documentation", "docs"
- Likely assigns: `@document-ninja` or `@create-guru`
- Result: PR with search functionality in ~20 minutes

---

### Example 2: Performance Issue (Intermediate)
```markdown
Title: Optimize the workflow execution time

Description:
The agent-spawning workflow takes 5+ minutes to run.
This is too slow for the autonomous system.

Please optimize it to run in under 2 minutes.

Keywords: performance, slow, optimize, workflow, speed
```

**What happens**:
- System analyzes: "optimize", "performance", "slow", "workflow", "speed"
- Likely assigns: `@accelerate-master` or `@align-wizard`
- Result: Optimized workflow implementation

---

### Example 3: Complex System (Advanced)
```markdown
Title: Implement intelligent workflow scheduling based on historical patterns

Description:
The system should analyze workflow execution patterns over time
and dynamically adjust scheduling to optimize resource usage.

This is a complex task requiring:
- Historical data analysis
- Pattern recognition algorithms
- Dynamic scheduling implementation
- Multi-workflow coordination
- Testing and validation

Keywords: complex, orchestration, analysis, patterns, coordination,
          optimization, multi-system
```

**What happens**:
- System analyzes: "complex", "orchestration", "coordination", "multi-system"
- Likely assigns: `@meta-coordinator`, `@orchestrator-guru`, or `@investigate-champion`
- Result: Comprehensive multi-phase implementation with proper architecture

---

## 🔍 How Agent Matching Works

The intelligent matching system (`tools/match-issue-to-agent.py`) uses:

1. **Keyword Extraction**: Pulls keywords from your issue title and body
2. **Pattern Matching**: Scores each agent based on keyword matches
   - Simple keywords: 1 point each
   - Regex patterns: 2 points each
3. **Confidence Scoring**:
   - High confidence: score ≥ 5
   - Medium confidence: score ≥ 3
   - Low confidence: defaults to `@create-guru`
4. **Agent Selection**: Picks the agent with the highest score

### Example Scoring:

For issue: "Optimize the 3D rendering in organism.html - too slow on mobile"

| Agent | Score | Reason |
|-------|-------|--------|
| `@render-3d-master` | 18 | Matches: 3d, rendering, organism.html, mobile, optimize |
| `@accelerate-master` | 5 | Matches: optimize, slow, performance |
| **Winner** | `@render-3d-master` | Highest score, most relevant |

---

## 📊 All 47+ Available Agents

The system has specialized agents for every domain:

### 🏗️ Infrastructure (9 agents)
`@APIs-architect`, `@create-guru`, `@create-champion`, `@construct-specialist`, `@develop-specialist`, `@engineer-master`, `@engineer-wizard`, `@infrastructure-specialist`, `@tools-analyst`

### ⚡ Performance (2 agents)
`@accelerate-master`, `@accelerate-specialist`

### ✅ Testing (4 agents)
`@assert-specialist`, `@assert-whiz`, `@edge-cases-pro`, `@validator-pro`

### 🔒 Security (5 agents)
`@secure-specialist`, `@secure-ninja`, `@secure-pro`, `@guardian-master`, `@monitor-champion`

### 🧹 Code Organization (8 agents)
`@organize-guru`, `@organize-specialist`, `@organize-expert`, `@refactor-champion`, `@restructure-master`, `@cleaner-master`, `@simplify-pro`

### 🔍 Analysis (2 agents)
`@investigate-champion`, `@investigate-specialist`

### 🔗 Integration (3 agents)
`@bridge-master`, `@connector-ninja`, `@integrate-specialist`

### 📖 Documentation (4 agents)
`@support-master`, `@document-ninja`, `@clarify-champion`, `@communicator-maestro`

### 🎭 Code Reviews (3 agents)
`@coach-master`, `@coach-wizard`, `@guide-wizard`

### ⚙️ CI/CD (3 agents)
`@align-wizard`, `@coordinate-wizard`, `@troubleshoot-expert` (protected)

### 🚀 Innovation (4 agents)
`@pioneer-pro`, `@pioneer-sage`, `@steam-machine`, `@cloud-architect`

### 🎯 Special (3 agents)
`@meta-coordinator` - Multi-agent coordination  
`@render-3d-master` - 3D web rendering with Three.js  
`@investigate-champion` - Metrics and pattern analysis

See **[HOW_TO_TRIGGER_AGENTS.md](./HOW_TO_TRIGGER_AGENTS.md)** for detailed descriptions of each agent.

---

## 🎓 Tips for Best Results

### 1. Be Specific in Your Title
✅ Good: "Optimize the 3D rendering performance in organism.html"  
❌ Vague: "Make it faster"

### 2. Use Keywords Relevant to Your Goal
Want security work? Use: security, vulnerability, authentication, access control  
Want performance? Use: optimize, slow, performance, speed, bottleneck  
Want refactoring? Use: refactor, cleanup, complexity, duplication

### 3. Describe the "Why"
Helps the agent understand context:
```markdown
The workflow is slow (5+ minutes) which delays the autonomous cycle.
We need it under 2 minutes to maintain responsiveness.
```

### 4. Break Down Complex Tasks
For very complex work, consider multiple issues:
- Issue 1: "Design the orchestration system architecture"
- Issue 2: "Implement the core coordination logic"
- Issue 3: "Add multi-agent communication"

Or use the `@meta-coordinator` agent by mentioning "complex", "orchestration", "multi-system" keywords.

---

## 🚨 Troubleshooting

### Issue not assigned within 15 minutes?
- Check the Actions tab for the `copilot-graphql-assign` workflow
- Verify `COPILOT_PAT` secret is configured
- See **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**

### Wrong agent assigned?
- Close the issue and recreate with better keywords
- Or comment on the issue explaining why a different agent would be better
- Add keywords that match your desired agent's specialization

### Want a specific agent?
- Use keywords from that agent's specialization (see agent list above)
- Mention the agent by name in the issue description
- See **[INTELLIGENT_AGENT_MATCHING.md](./INTELLIGENT_AGENT_MATCHING.md)** for matching details

---

## 🎉 You're Ready!

**Next Steps**:
1. **[Create your first issue →](../../issues/new)**
2. Watch the Actions tab to see the magic happen
3. Get a PR in ~20 minutes!
4. Your issue closes automatically when done

**Questions?** Create an issue asking your question - the system will automatically route it to the right documentation agent! 😊

---

## 📚 Related Documentation

- **[HOW_TO_TRIGGER_AGENTS.md](./HOW_TO_TRIGGER_AGENTS.md)** - Complete guide (recommended reading)
- **[FAQ.md](../FAQ.md)** - Frequently asked questions
- **[AGENT_QUICKSTART.md](../AGENT_QUICKSTART.md)** - Agent system overview
- **[README.md](../README.md)** - Project overview
- **[enhancements/COMPLEXITY_BASED_ROUTING.md](./enhancements/COMPLEXITY_BASED_ROUTING.md)** - Optional complexity enhancement

---

*🤖 Part of the Chained autonomous AI ecosystem - where AI learns, builds, and evolves continuously!*
