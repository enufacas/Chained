# 🚀 How to Trigger the Autonomous Agent System

> **Quick Answer**: Yes! You can create an issue to trigger the system. While there's no "complex" label specifically, the system automatically analyzes your issue and assigns the best agent based on the content.

## 🎯 How It Works

The Chained autonomous system works like this:

1. **You create an issue** describing what you want
2. **The system analyzes** your issue title and body using intelligent pattern matching
3. **An agent is automatically assigned** based on the content (within 15 minutes)
4. **Copilot works on it** using the selected agent's specialized approach
5. **A PR is created** and auto-merged if tests pass
6. **Your issue is closed** with the implemented solution

## ✨ Creating an Issue to Try It

### Simple Method: Just Create an Issue

The easiest way to trigger the system is to **create a regular GitHub issue**:

```markdown
Title: Add dark mode toggle to GitHub Pages

Description:
The documentation site would benefit from a dark mode option.
This should:
- Add a toggle button in the navigation
- Save preference to localStorage
- Apply dark theme styles
```

**That's it!** The system will:
- Automatically match this to an appropriate agent (likely `@designer-engineer` or `@create-guru`)
- Assign Copilot within 15 minutes
- Start working on implementation

### Advanced Method: Guide Agent Selection with Keywords

You can influence which agent is selected by using specific keywords in your issue:

#### For Code Quality & Refactoring
```markdown
Title: Refactor the agent matching system for better maintainability

Keywords to use: refactor, cleanup, simplify, organize, complexity, 
                 duplication, code structure, maintainable
→ Triggers: @cleaner-master, @organize-specialist, @refactor-champion
```

#### For Performance Issues
```markdown
Title: Optimize the pattern matching algorithm - too slow

Keywords to use: performance, slow, optimize, speed, bottleneck,
                 efficiency, accelerate, faster
→ Triggers: @accelerate-master, @accelerate-specialist
```

#### For Testing
```markdown
Title: Add comprehensive test coverage for agent system

Keywords to use: test, testing, coverage, unit test, e2e,
                 quality assurance, validation
→ Triggers: @assert-specialist, @assert-whiz
```

#### For Security
```markdown
Title: Fix security vulnerability in workflow permissions

Keywords to use: security, vulnerability, access control, permissions,
                 authentication, secure
→ Triggers: @secure-specialist, @guardian-master
```

#### For Documentation
```markdown
Title: Document the agent spawning system

Keywords to use: documentation, tutorial, explain, guide,
                 readme, docs, examples
→ Triggers: @clarify-champion, @document-ninja, @communicator-maestro
```

#### For 3D/Rendering Work
```markdown
Title: Improve the organism.html 3D visualization performance

Keywords to use: 3d, three.js, webgl, rendering, canvas,
                 graphics, fps, particle, animation
→ Triggers: @render-3d-master
```

## 🏷️ About Labels and Tags

### Current Label System

The system uses these **automatic labels**:

| Label | Purpose | Applied By |
|-------|---------|------------|
| `copilot-assigned` | Issue assigned to Copilot | Automatic when agent selected |
| `agent:agent-name` | Identifies which agent profile to use | Automatic based on matching |
| `ai-generated` | Issue created by AI idea generator | AI workflows |
| `automated` | Automated process | Various workflows |
| `enhancement` | Feature request | Manual or automatic |
| `bug` | Bug report | Manual or automatic |
| `documentation` | Documentation work | Manual or automatic |

### Can I Add a "Complex" Label?

**Short answer**: Labels don't currently affect agent selection, but you can add them!

**Long answer**: 
- The system uses **content analysis** (keywords in title/body) to match agents, not labels
- You can add any labels you want to organize issues
- If you want to indicate complexity, just add it to the issue description:
  ```markdown
  Title: Implement multi-agent coordination system
  
  **Complexity**: High - requires distributed coordination
  
  Description: ...
  ```

### Want Complexity-Based Routing?

If you want the system to consider complexity levels, you have options:

#### Option 1: Use Keywords in Description
```markdown
Title: Feature request

**Complexity**: High
This is a complex task requiring coordination between multiple systems...
```
The keyword "complex" will be picked up by agents specializing in complex problems.

#### Option 2: Create a Complexity Label System

You could create labels like:
- `complexity:low`
- `complexity:medium`
- `complexity:high`

Then request a feature to have the agent matcher consider these labels.

#### Option 3: Request an Enhancement

Create an issue requesting complexity-aware routing:
```markdown
Title: Add complexity-based agent routing

The system should consider issue complexity when matching agents.

Suggested approach:
- Parse complexity indicators from issue body
- Weight agent selection based on complexity
- Prefer experienced agents for complex tasks
```

## 🎮 Try It Now!

### Beginner: Simple Feature Request
```markdown
Title: Add a search box to the documentation page

Description:
Users need a way to search the documentation.
Please add a search box to the docs index page.
```
→ System will assign an appropriate agent and implement it!

### Intermediate: Performance Issue
```markdown
Title: The workflow runs are taking too long

Description:
The agent-spawning workflow takes 5+ minutes.
Please optimize it to run faster.

Keywords: performance, slow, optimize, workflow
```
→ Likely assigned to `@accelerate-master` or `@align-wizard`

### Advanced: Complex System Change
```markdown
Title: Implement intelligent workflow scheduling based on usage patterns

Description:
The system should analyze workflow execution patterns and
dynamically adjust scheduling to optimize resource usage.

This is a complex task requiring:
- Historical data analysis
- Pattern recognition
- Dynamic scheduling algorithm
- Testing and validation

Keywords: complex, orchestration, optimization, analysis, workflow
```
→ Could trigger `@meta-coordinator`, `@orchestrator-guru`, or `@investigate-champion`

## 🔍 How Agent Matching Works

The intelligent matching system (`tools/match-issue-to-agent.py`) works like this:

1. **Extracts keywords** from your issue title and body
2. **Scores each agent** based on keyword matches:
   - Simple keywords: 1 point each
   - Pattern matches (regex): 2 points each
3. **Selects the best match**:
   - High confidence: score ≥ 5
   - Medium confidence: score ≥ 3
   - Low confidence: score < 3 (defaults to @create-guru)
4. **Adds labels** and **updates issue** with agent assignment

### Behind the Scenes Example

For this issue:
```
Title: Optimize the 3D rendering in organism.html
Body: The Three.js scene is slow on mobile devices...
```

**Scoring**:
- `@render-3d-master`: 18 points (3d, rendering, three.js, mobile, organism.html)
- `@accelerate-master`: 5 points (optimize, slow, performance)
- Winner: `@render-3d-master` (highest score)

## 📋 Available Agent Specializations

Here are all the agents and what they specialize in:

### Infrastructure & Development (9 agents)
- `@APIs-architect` - API construction and design
- `@create-guru` - Infrastructure creation (default agent)
- `@create-champion` - Tool creation
- `@construct-specialist` - System construction
- `@develop-specialist` - API development
- `@engineer-master` - API engineering (systematic)
- `@engineer-wizard` - API engineering (creative)
- `@infrastructure-specialist` - Infrastructure work
- `@tools-analyst` - Tool construction

### Performance (2 agents)
- `@accelerate-master` - Performance optimization
- `@accelerate-specialist` - Algorithm acceleration

### Testing & Quality (4 agents)
- `@assert-specialist` - Test coverage
- `@assert-whiz` - Test coverage (proof-oriented)
- `@edge-cases-pro` - Edge case validation
- `@validator-pro` - Coverage validation

### Security (5 agents)
- `@secure-specialist` - Security implementation
- `@secure-ninja` - Access control
- `@secure-pro` - Vulnerability fixes
- `@guardian-master` - Security protection
- `@monitor-champion` - Security monitoring

### Code Organization (8 agents)
- `@organize-guru` - Duplication removal
- `@organize-specialist` - Code structure
- `@organize-expert` - Maintainability
- `@refactor-champion` - Complexity refactoring
- `@restructure-master` - Complexity restructuring
- `@cleaner-master` - Code cleanup
- `@simplify-pro` - Code simplification

### Documentation (4 agents)
- `@support-master` - Skill building
- `@document-ninja` - Tutorial documentation
- `@clarify-champion` - Tutorial clarification
- `@communicator-maestro` - Teaching examples

### CI/CD & Workflows (3 agents)
- `@align-wizard` - CI/CD alignment
- `@coordinate-wizard` - Team coordination
- `@troubleshoot-expert` - GitHub Actions debugging (protected)

### Innovation (4 agents)
- `@pioneer-pro` - New technologies
- `@pioneer-sage` - New technologies
- `@steam-machine` - Emerging tech
- `@cloud-architect` - Cloud architecture

### Special (3 agents)
- `@meta-coordinator` - Multi-agent coordination
- `@render-3d-master` - 3D web rendering with Three.js
- `@investigate-champion` - Metrics and pattern investigation

## ⚡ Quick Examples

### "I want to try this on a simple task"
```markdown
Title: Add a footer to the documentation page
Labels: (none needed)
```
→ System automatically handles it!

### "I want a specific agent to work on this"
```markdown
Title: Refactor the agent matching code

Use keywords like: refactor, organize, cleanup, simplify
These trigger @cleaner-master or @organize-specialist
```

### "I have a complex multi-system task"
```markdown
Title: Build an intelligent workflow orchestration system

Keywords: complex, orchestration, coordination, multi-agent
→ Triggers @meta-coordinator or @orchestrator-guru
```

## 🤔 Common Questions

### Q: Do I need to add any labels manually?
**A:** No! The system automatically adds all necessary labels.

### Q: Can I request a specific agent?
**A:** Not directly, but you can use keywords that match that agent's specialization. Or mention the agent name in your issue description.

### Q: What if I just want to see it work?
**A:** Create any issue! Even a simple "Add a comment to README" will trigger the system.

### Q: How long does it take?
**A:** Usually 15-30 minutes from issue creation to PR merge (if tests pass).

### Q: Can I add a "complex" label?
**A:** Yes, you can add any labels you want! They won't affect agent selection currently, but you could request that feature.

### Q: What if I disagree with the agent selection?
**A:** You can comment on the issue to explain why a different agent would be better, or close and recreate with different keywords.

## 🎯 Next Steps

Ready to try it?

1. **Click** [Create New Issue](../../issues/new)
2. **Write** your issue title and description
3. **Submit** - that's all!
4. **Watch** the Actions tab to see the agent assignment workflow run
5. **Monitor** your issue for the Copilot assignment comment
6. **Review** the PR that Copilot creates
7. **Celebrate** when it auto-merges!

## 📚 Related Documentation

- **[LABELS.md](./guides/LABELS.md)** - Complete label reference
- **[AGENT_QUICKSTART.md](../AGENT_QUICKSTART.md)** - Agent system overview
- **[AUTONOMOUS_CYCLE.md](./AUTONOMOUS_CYCLE.md)** - How the full cycle works
- **[FAQ.md](./FAQ.md)** - Frequently asked questions

---

*🤖 Part of the Chained autonomous AI motion machine*  
*For questions, create an issue and the system will respond automatically!*
