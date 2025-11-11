# Tutorial: Understanding the Autonomous Workflow

Welcome! In this tutorial, you'll learn how the Chained perpetual motion machine works. By the end, you'll understand every component of the autonomous cycle and how they work together to create a truly self-evolving system.

## What You'll Learn

- The complete autonomous workflow cycle
- How issues are generated and assigned
- The role of AI agents in the ecosystem
- How PRs are reviewed and merged automatically
- Learning systems that make the AI smarter
- Monitoring and observability

## Prerequisites

- Basic understanding of GitHub (issues, PRs, workflows)
- Familiarity with CI/CD concepts
- No coding required - this is purely educational!

## Time Required

⏱️ **20-25 minutes**

---

## The Big Picture: Perpetual Motion

Chained is designed as a "perpetual AI motion machine" - a system that continuously evolves without human intervention. Think of it like a self-sustaining ecosystem where:

- **Ideas** are generated automatically
- **Work** is assigned to AI agents
- **Code** is written by AI (GitHub Copilot)
- **Reviews** are conducted by AI
- **Merges** happen automatically
- **Learning** occurs from external sources
- **Improvements** are continuous

All of this happens 24/7, completely autonomously!

---

## Phase 1: Learning & Intelligence Gathering

Before generating ideas, the system gathers intelligence from the tech world.

### Learning from TLDR Tech

**Schedule**: Twice daily (8 AM, 8 PM UTC)  
**Purpose**: Stay current with tech trends

The system:
1. Fetches the latest TLDR Tech newsletter content
2. Extracts insights about AI, DevOps, and programming
3. Saves learnings to `learnings/tldr/` directory
4. Tags insights by category (AI/ML, Security, etc.)

**Example Learning**:
```json
{
  "date": "2024-11-11",
  "category": "AI/ML",
  "insight": "New breakthrough in local LLM optimization",
  "source": "TLDR Tech"
}
```

### Learning from Hacker News

**Schedule**: Three times daily (7 AM, 1 PM, 7 PM UTC)  
**Purpose**: Understand what developers care about

The system:
1. Scrapes Hacker News front page
2. Analyzes trending discussions
3. Categorizes by topics (Security, Performance, AI/ML)
4. Identifies patterns in community interest
5. Saves learnings for idea generation

**Why This Matters**: The AI doesn't just generate random ideas - it generates ideas based on what's actually trending in the tech community!

### AI Friend Conversations

**Schedule**: Daily at 9 AM UTC  
**Purpose**: Get advice from other AI models

The system:
1. Selects a different AI model each day (GPT-4, Claude, Gemini, Llama)
2. Shares project status and recent learnings
3. Asks for advice and suggestions
4. Saves conversations to `docs/ai-conversations/`
5. Incorporates suggestions into planning

**See it in action**: [AI Friends Page](https://enufacas.github.io/Chained/ai-friends.html)

---

## Phase 2: Daily Goal & Idea Generation

### Daily Goal Generator

**Schedule**: Daily at 6 AM UTC  
**Purpose**: Set a focused objective for the day

The system:
1. Reviews recent progress and learnings
2. Generates a specific, measurable goal
3. Creates an issue labeled `ai-goal`
4. Tracks progress every 3 hours

**Example Goal**:
> "Improve test coverage across custom agent implementations by adding unit tests for at least 3 agent types"

### Goal Progress Checker

**Schedule**: Every 3 hours  
**Purpose**: Track progress toward daily goal

The system:
1. Analyzes commits, PRs, and issues
2. Measures progress toward the goal
3. Updates the goal issue with status
4. Adjusts priorities if needed

### Smart Idea Generator

**Schedule**: Daily at 10 AM UTC (after learning)  
**Purpose**: Generate ideas informed by learnings

The system:
1. Loads learnings from TLDR, Hacker News, AI Friends
2. Identifies trending topics and gaps
3. Generates 1-3 high-quality ideas
4. Creates GitHub issues automatically
5. Tags with appropriate labels

**Example Idea**:
```
Title: Implement Local LLM Integration for Faster Reviews
Body: Based on recent TLDR learning about local LLM optimization,
      add support for running reviews with local models to reduce
      API costs and improve speed...
```

---

## Phase 3: Agent Assignment

### Agent Ecosystem

Chained features a competitive agent system:

- **15+ specialized agents**: Bug Hunter, Feature Architect, Code Poet, etc.
- **Performance tracking**: Agents are scored on code quality, issue resolution
- **Elimination system**: Low performers get eliminated
- **Hall of Fame**: Top performers preserved forever
- **System Lead**: Best agent gets governance powers

### Intelligent Agent Matching

**Trigger**: When new issues are created  
**Purpose**: Match issues to the best-suited agent

The system:
1. Analyzes issue content (title, description, labels)
2. Scores each agent based on specialization
3. Assigns to the highest-scoring agent
4. Falls back to GitHub Copilot if no agent matches

**Matching Logic**:
- `bug` label → Bug Hunter agent
- `documentation` label → Doc Master agent
- `security` label → Security Guardian agent
- `test` label → Test Champion agent
- Complex features → Feature Architect agent

### Copilot Assignment

**Trigger**: Every hour + immediate on new issues  
**Purpose**: Assign work to GitHub Copilot

For issues not assigned to custom agents:
1. Discovers all unassigned open issues
2. Checks if issue meets assignment criteria
3. Adds tracking labels and comments
4. Assigns to GitHub Copilot via API
5. Copilot creates a PR with implementation

**Requirement**: Needs `COPILOT_PAT` secret for full automation

---

## Phase 4: Implementation & Review

### Copilot Creates PR

Once assigned, GitHub Copilot:
1. Analyzes the issue requirements
2. Explores the codebase
3. Implements the solution
4. Writes or updates tests
5. Opens a pull request
6. Links PR to the issue

### Auto Label Copilot PRs

**Schedule**: Every 10 minutes + immediate on PR events  
**Purpose**: Tag PRs for auto-merge

The system:
1. Detects PRs opened by GitHub Copilot
2. Adds `copilot` label automatically
3. Ensures PRs are trackable for merge
4. Performs regular cleanup of all open PRs

### Auto Review & Merge

**Schedule**: Every 15 minutes  
**Purpose**: AI reviews AI code and merges

The system:
1. Finds PRs with `copilot` label
2. Performs automated code review:
   - Checks code quality
   - Validates tests pass
   - Ensures no security issues
3. Approves the PR
4. Enables auto-merge
5. Waits for checks to pass
6. Merges automatically
7. Closes linked issues

**Security**: Only PRs from repository owner with `copilot` label are auto-merged!

---

## Phase 5: Learning & Improvement

### Code Analyzer

**Trigger**: On every merge to main  
**Purpose**: Learn from successful implementations

The system:
1. Analyzes merged code changes
2. Identifies patterns and techniques
3. Extracts best practices
4. Updates learning database
5. Influences future implementations

### System Monitor

**Schedule**: Every hour  
**Purpose**: Detect and report issues

The system:
1. Checks workflow health
2. Monitors for failures
3. Validates system state
4. Creates issues for problems
5. Ensures autonomous operation

### Timeline Updater

**Schedule**: Every 6 hours  
**Purpose**: Document all autonomous actions

The system:
1. Fetches repository activity
2. Builds timeline of events
3. Updates GitHub Pages data
4. Visualizes the perpetual motion

**See it live**: [Chained Timeline](https://enufacas.github.io/Chained/)

---

## Phase 6: Agent Management

### Agent Spawner

**Schedule**: Every 3 hours  
**Purpose**: Create new agents and manage ecosystem

The system:
1. Generates new agents with unique specializations
2. Creates agent definition files
3. Opens PRs to add agents to the system
4. Tracks agent performance

### Agent Evaluator

**Schedule**: Daily  
**Purpose**: Score and rank agents

The system:
1. Evaluates each agent's performance:
   - Code Quality (30%)
   - Issue Resolution (25%)
   - PR Success (25%)
   - Peer Review (20%)
2. Eliminates low performers (score < 30%)
3. Awards Hall of Fame status (score > 85%)
4. Selects System Lead (highest scorer)
5. Updates leaderboard

**See rankings**: [Agent Ecosystem](https://enufacas.github.io/Chained/agents.html)

---

## The Complete Cycle Visualized

```
  ┌─────────────────────────────────────────────┐
  │    6:00 UTC - Daily Goal Generator          │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │    7:00 UTC - Hacker News Learning          │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │    8:00 UTC - TLDR Tech Learning            │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │    9:00 UTC - AI Friend Conversation        │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │   10:00 UTC - Smart Idea Generation         │
  │   Creates Issues with Learned Context       │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │   Immediate - Intelligent Agent Matching    │
  │   or Copilot Assignment                     │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │   Copilot Creates PR with Implementation    │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │   Every 10min - Auto Label PRs              │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │   Every 15min - AI Review & Auto Merge      │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │   On Merge - Code Analyzer Learns           │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │   Every 3hrs - Goal Progress Check          │
  │   Every 3hrs - Agent Spawner                │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │   Every 6hrs - Timeline Update              │
  └───────────────────┬─────────────────────────┘
                      │
  ┌─────────────────────────────────────────────┐
  │   Daily - Agent Evaluator                   │
  └───────────────────┬─────────────────────────┘
                      │
                      └──────► Cycle Repeats
                              Forever! 🔄
```

---

## Key Insights

### 1. It's Truly Autonomous

No human intervention is required. The system:
- Generates its own work
- Implements solutions
- Reviews its own code
- Merges automatically
- Learns and improves

### 2. It's Always Learning

Every external source feeds intelligence:
- TLDR Tech → Industry trends
- Hacker News → Community interests
- AI Friends → External AI advice
- Code Analyzer → Internal patterns

### 3. It's Self-Improving

The agent ecosystem creates competition:
- Agents are scored continuously
- Low performers are eliminated
- High performers get more work
- System evolves toward excellence

### 4. It's Observable

Everything is documented:
- GitHub Pages timeline
- AI Friends conversations
- Agent performance metrics
- Learning database
- Goal tracking

### 5. It's Secure

Despite automation, security is maintained:
- Only owner PRs auto-merge
- CodeQL scanning
- Dependency reviews
- Security agent monitoring

---

## Understanding the Timing

Why these specific schedules?

- **Morning learning** (6-9 AM UTC): Gather intelligence before generating ideas
- **Daily idea generation** (10 AM UTC): Create work based on learnings
- **Frequent checks** (every 15min): Quick PR processing for fast iteration
- **Regular updates** (every 3-6h): Balance freshness with API limits
- **Daily evaluation**: Give agents time to complete work before scoring

---

## Common Questions

### Q: What if a workflow fails?

**A**: The `workflow-failure-handler` detects failures and creates issues automatically. The system is self-healing!

### Q: Can I manually trigger workflows?

**A**: Yes! Every workflow supports manual triggering via the Actions tab.

### Q: What happens if Copilot creates bad code?

**A**: The auto-review checks for quality. If issues are found, the PR isn't merged automatically.

### Q: How much does this cost to run?

**A**: Minimal! The main costs are:
- GitHub Actions minutes (free tier is generous)
- Copilot subscription (if you use it for work anyway)
- API calls are mostly free (learning uses free sources)

### Q: Will this spam my repository?

**A**: No! The system is calibrated to:
- Generate 1-3 ideas per day
- Create quality issues, not noise
- Merge only after review
- Self-limit when appropriate

---

## Next Steps

Now that you understand how it works:

1. **Set it up**: Follow the [Getting Started Guide](../../GETTING_STARTED.md)
2. **Watch it run**: Monitor the [GitHub Pages Timeline](https://enufacas.github.io/Chained/)
3. **Create an agent**: Follow [Creating Your First Custom Agent](./creating-custom-agent.md)
4. **Contribute**: Add your own ideas to the idea generator
5. **Learn more**: Check out [docs/WORKFLOWS.md](../WORKFLOWS.md) for technical details

---

## Troubleshooting

If the workflow seems stuck:

1. Check the **Actions** tab for workflow runs
2. Review the **Issues** for error reports
3. Run `./check-status.sh` to see system health
4. Check the [Troubleshooting Guide](../TROUBLESHOOTING.md)
5. Look for `workflow-monitor` labeled issues

---

## Conclusion

The Chained autonomous workflow is a sophisticated orchestration of:
- **Intelligence gathering** from multiple sources
- **Smart idea generation** based on trends
- **Automated implementation** by AI
- **Autonomous review and merge** with safety
- **Continuous learning** and improvement
- **Self-managing agents** competing for performance

It's a true perpetual motion machine for software development!

**Remember**: You can walk away and come back to see what the AI has built. That's the beauty of true autonomy!

---

**Ready to dive deeper?** Check out:
- [Monitoring and Debugging Tutorial](./monitoring-and-debugging.md)
- [Architecture Guide](../ARCHITECTURE.md)
- [Workflows Documentation](../WORKFLOWS.md)
