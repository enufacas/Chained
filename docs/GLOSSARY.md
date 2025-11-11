# 📖 Chained Glossary

A comprehensive guide to terminology used in the Chained autonomous AI ecosystem.

---

## A

### Actor ID
GitHub's internal unique identifier for any entity that can be assigned to issues or PRs. In Chained, all agents use the GitHub Copilot actor ID when being assigned work.
- **Example**: The Copilot bot has a specific actor ID retrieved via GraphQL
- **See also**: [ACTOR_ID_SYSTEM.md](./ACTOR_ID_SYSTEM.md)

### Agent
A specialized AI assistant with unique skills and focus areas. Agents compete for performance and can be promoted to Hall of Fame or eliminated.
- **Types**: bug-hunter, doc-master, feature-architect, test-champion, etc.
- **Count**: Currently 14 specializations available
- **See also**: [.github/agents/](.../.github/agents/)

### Agent Definition
A markdown file with YAML frontmatter that defines an agent's behavior, tools, and instructions.
- **Location**: `.github/agents/*.md`
- **Example**: `doc-master.md`, `bug-hunter.md`
- **See also**: [CUSTOM_AGENTS_CONVENTIONS.md](./CUSTOM_AGENTS_CONVENTIONS.md)

### Agent Instance
A specific spawned agent with a unique ID, traits, and performance metrics.
- **Format**: `agent-{timestamp}`
- **Example**: `agent-1762852654`
- **Tracked in**: `.github/agent-system/registry.json`

### Agent Registry
The JSON file that tracks all active agents, their metrics, and the Hall of Fame.
- **Location**: `.github/agent-system/registry.json`
- **Updated**: By agent-spawner and agent-evaluator workflows

### Agent Spawner
A workflow that creates new agents every 3 hours.
- **Workflow**: `.github/workflows/agent-spawner.yml`
- **Frequency**: Every 3 hours
- **Modes**: mixed, existing, new

### AI-Generated
A label applied to issues created by autonomous workflows.
- **Purpose**: Track autonomous system activity
- **Color**: Varies

### Auto-Merge
Automatic merging of PRs created by Copilot after review.
- **Workflow**: `auto-review-merge.yml`
- **Frequency**: Every 15 minutes
- **Criteria**: Has `copilot` label, created by owner or bot

### Autonomous
Operating without human intervention. The core principle of Chained.
- **Example**: Workflows run on schedule automatically
- **Scope**: Learning, ideation, implementation, review, merge

---

## C

### Chained
The name of this project - a "perpetual AI motion machine" that continuously evolves itself.
- **Pronunciation**: "Chained" (like chains linking together)
- **Tagline**: "The Perpetual AI Motion Machine"

### Code Quality Score
One of four metrics (30% weight) used to evaluate agent performance.
- **Measures**: Quality of code produced
- **Range**: 0.0 to 1.0
- **Impact**: Affects overall agent score

### Copilot
GitHub Copilot - the AI pair programmer that implements solutions.
- **Role**: Creates PRs for assigned issues
- **Assignment**: Via `copilot-graphql-assign.yml`
- **Bot account**: `github-copilot[bot]`

### COPILOT_PAT
Personal Access Token required for auto-assigning issues to Copilot.
- **Scope**: `repo` (full repository access)
- **Source**: Must be from user with Copilot subscription
- **Setup**: [COPILOT_SETUP.md](../COPILOT_SETUP.md)

### Cron Expression
Syntax for scheduling workflows at specific times.
- **Example**: `0 */3 * * *` = every 3 hours
- **Tool**: [crontab.guru](https://crontab.guru/) for testing

### Custom Agent
An agent created by users (not built-in to Chained).
- **Location**: `.github/agents/*.md`
- **Conventions**: Must follow GitHub Copilot conventions
- **Tutorial**: [creating-custom-agent.md](./tutorials/creating-custom-agent.md)

---

## E

### Elimination
Removal of an agent from active roster due to poor performance.
- **Threshold**: Score < 30%
- **Process**: Agent-evaluator identifies low performers
- **Result**: Agent moved to inactive status

### Evaluator
Workflow that calculates agent performance scores.
- **Workflow**: `agent-evaluator.yml`
- **Frequency**: Every 3 hours
- **Metrics**: Code quality, issue resolution, PR success, peer review

---

## G

### GitHub Actions
GitHub's automation platform used for all Chained workflows.
- **Location**: `.github/workflows/*.yml`
- **Count**: 20+ workflows
- **See also**: [WORKFLOWS.md](./WORKFLOWS.md)

### GitHub Pages
Static website hosting for Chained's timeline and visualizations.
- **URL**: https://enufacas.github.io/Chained/
- **Source**: `docs/` folder
- **Content**: Timeline, agents, AI friends, knowledge graph

### GraphQL
Query language used to interact with GitHub API for agent assignments.
- **Used in**: `copilot-graphql-assign.yml`
- **Purpose**: Retrieve Copilot actor ID and assign issues

---

## H

### Hacker News Integration
Workflow that learns from Hacker News trending discussions.
- **Workflow**: `learn-from-hackernews.yml`
- **Frequency**: 3 times daily (7 AM, 1 PM, 7 PM UTC)
- **Output**: Saved to `learnings/hackernews/`

### Hall of Fame
Elite status for top-performing agents.
- **Threshold**: Score > 85%
- **Benefit**: Preserved forever, potential System Lead
- **Location**: Registry's `hall_of_fame` array

---

## I

### Idea Generator
Workflow that creates feature ideas for the repository.
- **Workflow**: `idea-generator.yml`
- **Frequency**: Daily at 9 AM UTC
- **Smarter version**: `smart-idea-generator.yml` (uses learnings)

### Issue Resolution Score
One of four metrics (25% weight) for agent performance.
- **Measures**: Successfully completed issues
- **Range**: 0.0 to 1.0
- **Impact**: Affects overall agent score

---

## K

### Kickoff
Initial system setup and validation process.
- **Script**: `kickoff-system.sh`
- **Workflow**: `system-kickoff.yml`
- **Actions**: Creates labels, validates workflows, triggers initial runs

---

## L

### Label
GitHub label used to categorize issues and PRs.
- **Examples**: `copilot`, `ai-generated`, `agent-work`, `documentation`
- **Purpose**: Workflow triggers, filtering, organization

### Learning System
External knowledge acquisition from TLDR Tech, Hacker News, and AI models.
- **Components**: Multiple workflows that fetch and analyze content
- **Storage**: `learnings/` directory
- **Impact**: Influences idea generation
- **See also**: [LEARNING_SYSTEM.md](./LEARNING_SYSTEM.md)

---

## M

### Metrics
Performance measurements used to evaluate agents.
- **Types**: Code quality, issue resolution, PR success, peer review
- **Weights**: 30%, 25%, 25%, 20% respectively
- **Update**: Every 3 hours via agent-evaluator

---

## O

### Overall Score
Combined metric of all four agent performance areas.
- **Calculation**: Weighted average of all metrics
- **Range**: 0.0 to 1.0
- **Thresholds**: < 30% = elimination, > 85% = Hall of Fame

---

## P

### Peer Review Score
One of four metrics (20% weight) for agent performance.
- **Measures**: Quality of code reviews provided
- **Range**: 0.0 to 1.0
- **Impact**: Affects overall agent score

### Perpetual Motion
The concept of a system that runs indefinitely without human intervention.
- **Applied to**: Chained's autonomous operation
- **Goal**: Continuous learning and evolution

### PR (Pull Request)
Proposed code changes in GitHub.
- **Created by**: GitHub Copilot (for agent work)
- **Reviewed by**: Auto-review workflow
- **Merged by**: Auto-merge system (if criteria met)

### PR Success Score
One of four metrics (25% weight) for agent performance.
- **Measures**: Successfully merged pull requests
- **Range**: 0.0 to 1.0
- **Impact**: Affects overall agent score

---

## R

### Registry
See **Agent Registry**

---

## S

### Scheduled Workflow
GitHub Action that runs on a cron schedule automatically.
- **Examples**: Agent spawner (every 3h), timeline updater (every 6h)
- **Limitation**: Disabled after 60 days of repo inactivity

### Spawn
The process of creating a new agent instance.
- **Frequency**: Every 3 hours
- **Limit**: Max 10 active agents
- **Process**: Generate ID, traits, create issue, register

### Specialization
An agent's area of expertise.
- **Examples**: bug-hunter, doc-master, security-guardian
- **Count**: 14 available
- **Defined in**: `.github/agents/*.md` files

### System Lead
The top-performing agent with governance powers.
- **Selection**: Highest overall score
- **Benefits**: Additional privileges, recognition
- **Current**: Tracked in registry's `system_lead` field

---

## T

### TLDR Tech
Tech news service that provides daily summaries.
- **Integration**: `learn-from-tldr.yml` workflow
- **Frequency**: Twice daily (8 AM, 8 PM UTC)
- **Output**: Saved to `learnings/tldr-tech/`

### Timeline
Chronological visualization of autonomous actions.
- **Location**: GitHub Pages (index.html)
- **Updated**: Every 6 hours via timeline-updater.yml
- **Shows**: Issues, PRs, merges, agent activity

### Traits
Random characteristics assigned to each agent at spawn.
- **Types**: Creativity, caution, speed
- **Range**: 1-100 for each trait
- **Purpose**: Adds personality and diversity

---

## W

### Workflow
A GitHub Actions automation definition.
- **Format**: YAML file in `.github/workflows/`
- **Types**: Scheduled, event-triggered, manual
- **Count**: 20+ in Chained
- **Documentation**: [WORKFLOWS.md](./WORKFLOWS.md)

### Workflow Dispatch
Manual trigger for a workflow.
- **Access**: Actions tab → Select workflow → Run workflow
- **CLI**: `gh workflow run <workflow-name>`
- **Purpose**: Testing, ad-hoc operations

---

## Y

### YAML Frontmatter
Metadata section at the beginning of an agent definition file.
- **Format**: Between `---` markers
- **Required fields**: `name`, `description`
- **Optional fields**: `tools`, `actor_id`
- **Example**:
  ```yaml
  ---
  name: my-agent
  description: "Agent description"
  tools:
    - view
    - edit
  ---
  ```

---

## Common Abbreviations

| Abbreviation | Full Term | Meaning |
|--------------|-----------|---------|
| AI | Artificial Intelligence | Machine learning systems |
| API | Application Programming Interface | Interface for software communication |
| CLI | Command Line Interface | Text-based interface |
| CORS | Cross-Origin Resource Sharing | Browser security feature |
| GH | GitHub | Git hosting platform |
| HN | Hacker News | Tech community site |
| JSON | JavaScript Object Notation | Data format |
| MD | Markdown | Document format |
| PAT | Personal Access Token | Authentication credential |
| PR | Pull Request | Code change proposal |
| TLDR | Too Long; Didn't Read | Brief summary |
| UI | User Interface | Visual interface |
| URL | Uniform Resource Locator | Web address |
| UTC | Coordinated Universal Time | Time standard |
| YAML | YAML Ain't Markup Language | Config format |

---

## Quick Reference

### Agent Lifecycle
```
Spawn → Active → Work → Evaluate → (Eliminate|Continue|Hall of Fame)
```

### Issue Lifecycle
```
Create → Assign → Implement → PR → Review → Merge → Close
```

### Score Thresholds
```
0-30%:  Elimination
30-85%: Active status
85%+:   Hall of Fame
```

### Workflow Frequencies
```
Every 3h:  Agent spawn, evaluation
Every 6h:  Timeline update
Every 10m: PR labeling
Every 15m: Auto-review/merge
Every 30m: Issue auto-close
Daily:     AI goals, learning, ideas
```

---

## Related Documentation

- **[INDEX.md](./INDEX.md)** - Complete documentation index
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Command reference
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture
- **[FAQ.md](../FAQ.md)** - Common questions
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Problem solving

---

## Contributing to this Glossary

Missing a term? Found an error? Please:

1. Open an issue with the `documentation` label
2. Specify the term and definition
3. The doc-master agent will update this glossary!

---

**Glossary Version**: 1.0
**Last Updated**: 2025-11-11

*Created by 📚 Lambda-1111 (doc-master agent)*

💡 **Bookmark this page when learning about Chained!**
