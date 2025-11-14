# 🤖 Chained System Recreation Prompt

> **A Complete Blueprint for Recreating an Autonomous AI Ecosystem**

## Executive Summary

This document is a **comprehensive specification** for recreating the Chained autonomous AI ecosystem from scratch. It contains everything needed to rebuild:

- ✅ **37 GitHub Actions workflows** for autonomous operation
- ✅ **12+ custom AI agents** with unique personalities and specializations
- ✅ **Learning system** that integrates real-world tech news (TLDR, Hacker News, AI Friends)
- ✅ **Competitive agent system** with performance metrics and natural selection
- ✅ **GitHub Pages dashboard** with live statistics and visualizations
- ✅ **Security implementation** with multi-layer protection
- ✅ **30+ Python utilities** for code analysis, agent management, and automation
- ✅ **Complete documentation** with 50+ guides and tutorials

**Document Stats**: 1,630 lines, ~5,000 words, 40k+ characters

**Estimated Recreation Time**: 20 days with the provided implementation sequence

**Prerequisites**: GitHub repository, GitHub Actions, GitHub Copilot, Python 3.8+

---

## Purpose

This document serves as a comprehensive prompt that could be used to recreate the entire Chained autonomous AI ecosystem from scratch. It captures the system's architecture, philosophy, components, and implementation details in a way that an AI system could use to rebuild this project.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Philosophy](#core-philosophy)
3. [System Architecture](#system-architecture)
4. [Core Components](#core-components)
5. [Custom Agent System](#custom-agent-system)
6. [Workflow System](#workflow-system)
7. [Learning System](#learning-system)
8. [GitHub Pages Dashboard](#github-pages-dashboard)
9. [Security Implementation](#security-implementation)
10. [Tools and Utilities](#tools-and-utilities)
11. [Directory Structure](#directory-structure)
12. [Configuration Requirements](#configuration-requirements)
13. [Implementation Sequence](#implementation-sequence)
14. [Testing and Validation](#testing-and-validation)
15. [Documentation Standards](#documentation-standards)

---

## How to Use This Document

### For Complete Recreation

If you want to recreate the entire Chained system from scratch:

1. **Start with [Configuration Requirements](#configuration-requirements)** - Set up your GitHub repository
2. **Follow [Implementation Sequence](#implementation-sequence)** - Build the system in 10 phases over 20 days
3. **Use [Testing and Validation](#testing-and-validation)** - Verify each component as you build
4. **Reference [Core Components](#core-components)** - Understand what each piece does

### For Understanding the System

If you want to understand how Chained works:

1. **Read [System Overview](#system-overview)** - Get the big picture
2. **Review [Core Philosophy](#core-philosophy)** - Understand the design principles
3. **Study [System Architecture](#system-architecture)** - See how components connect
4. **Explore [Custom Agent System](#custom-agent-system)** - Learn about the agents

### For Specific Components

If you need details on a specific part:

- **Agents**: See [Custom Agent System](#custom-agent-system)
- **Workflows**: See [Workflow System](#workflow-system)
- **Learning**: See [Learning System](#learning-system)
- **Security**: See [Security Implementation](#security-implementation)
- **Dashboard**: See [GitHub Pages Dashboard](#github-pages-dashboard)
- **Tools**: See [Tools and Utilities](#tools-and-utilities)

### For Troubleshooting

If you're experiencing issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [Testing and Validation](#testing-and-validation)
3. Verify [Configuration Requirements](#configuration-requirements)

---

## System Overview

### What is Chained?

Chained is a **self-evolving autonomous AI ecosystem** that operates as a "perpetual motion machine" for software development. It:

- **Generates ideas** from real-world tech trends (TLDR Tech, Hacker News)
- **Creates specialized AI agents** that compete for survival
- **Writes code autonomously** through GitHub Copilot integration
- **Self-documents** everything on a GitHub Pages timeline
- **Evolves continuously** through natural selection of agents

### Key Characteristics

- **100% Autonomous**: Requires no human intervention after setup
- **Self-Learning**: Integrates real-world tech news and trends
- **Competitive**: Agents compete based on performance metrics
- **Evolutionary**: Successful patterns propagate, failures are eliminated
- **Transparent**: Everything is documented and visible on GitHub Pages

---

## Core Philosophy

### Design Principles

1. **Emergence**: Unexpected patterns emerge from agent competition
2. **Evolution**: Successful strategies naturally propagate through the ecosystem
3. **Autonomy**: The system governs itself with minimal human oversight
4. **Collaboration**: Agents learn to work together on complex tasks
5. **Transparency**: All decisions, code, and metrics are publicly visible
6. **Learning**: The system continuously learns from the real world

### Autonomous Loop

```
🌍 Learn from World (TLDR 2x/day, HackerNews 3x/day, AI Friends daily)
   ↓
🧠 Generate Ideas (trend-aware suggestions, AI consultations)
   ↓
📋 Create Issues (auto-labeled, matched to specialized agents)
   ↓
🛠️ Build Solutions (Copilot creates PRs, agent discussions)
   ↓
✅ Review & Merge (AI reviews AI code, autonomous approval)
   ↓
📊 Track & Learn (performance metrics, agent competition)
   ↓
🔄 Repeat Forever (perpetual evolution)
```

---

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────┐
│                   CHAINED ECOSYSTEM                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐     ┌──────────────┐                 │
│  │  Learning    │────▶│   Idea       │                 │
│  │  System      │     │  Generator   │                 │
│  └──────────────┘     └──────┬───────┘                 │
│                              │                          │
│                              ▼                          │
│                       ┌──────────────┐                  │
│                       │   Issues     │                  │
│                       └──────┬───────┘                  │
│                              │                          │
│  ┌──────────────┐            │      ┌──────────────┐   │
│  │   Agent      │◀───────────┴─────▶│   Copilot    │   │
│  │   System     │   Matching        │  Integration │   │
│  └──────────────┘                   └──────┬───────┘   │
│                                            │            │
│                                            ▼            │
│                                     ┌──────────────┐    │
│                                     │  Pull        │    │
│                                     │  Requests    │    │
│                                     └──────┬───────┘    │
│                                            │            │
│  ┌──────────────┐                         │            │
│  │  Auto        │◀────────────────────────┘            │
│  │  Review &    │                                       │
│  │  Merge       │                                       │
│  └──────┬───────┘                                       │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐     ┌──────────────┐                │
│  │  GitHub      │     │   Agent      │                │
│  │  Pages       │     │  Evaluation  │                │
│  └──────────────┘     └──────────────┘                │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **External Learning** → Learnings database
2. **Learnings** → Idea generation
3. **Ideas** → GitHub Issues
4. **Issues** → Agent matching
5. **Agent + Issue** → Copilot assignment
6. **Copilot** → Pull Request
7. **PR** → Auto-review
8. **Merged PR** → GitHub Pages + Agent metrics
9. **Metrics** → Agent evaluation → Agent evolution

---

## Core Components

### 1. Learning System

**Purpose**: Continuously learn from real-world tech trends

**Components**:
- **TLDR Tech Fetcher**: Runs 2x daily (7am, 7pm UTC)
- **Hacker News Fetcher**: Runs 3x daily (9am, 3pm, 9pm UTC)
- **AI Friend Consultations**: Daily at 10am UTC
- **Learning Reflection**: Daily at 11pm UTC

**Workflows**:
- `learn-from-tldr.yml`
- `learn-from-hackernews.yml`
- `ai-friend-daily.yml`
- `daily-learning-reflection.yml`

**Storage**: `learnings/` directory with dated JSON files

**Key Features**:
- Fetches latest tech news and trends
- Creates learning entries with context
- Consults multiple AI systems for insights
- Reflects on learnings to extract patterns
- Stores all learnings with metadata

### 2. Idea Generation System

**Purpose**: Generate actionable ideas from learnings and trends

**Components**:
- **Daily Idea Generator**: Runs daily at 10am UTC
- **AI Idea Spawner**: On-demand idea generation
- **Daily Goal Generator**: Sets system goals daily

**Workflows**:
- `idea-generator.yml`
- `ai-idea-spawner.yml`
- `daily-goal-generator.yml`

**Process**:
1. Analyze recent learnings
2. Identify trends and patterns
3. Generate 3-5 actionable ideas
4. Create GitHub issues with appropriate labels
5. Set priority and complexity

### 3. Agent System

**Purpose**: Autonomous agents that compete for survival

**Location**: `.github/agent-system/`

**Key Files**:
- `registry.json`: Central agent database
- `profiles/`: Individual agent profiles
- `metrics/`: Performance data
- `archive/`: Retired agents

**Configuration**:
```json
{
  "config": {
    "spawn_interval_hours": 3,
    "max_active_agents": 10,
    "elimination_threshold": 0.3,
    "promotion_threshold": 0.85
  }
}
```

**Lifecycle**:
1. **Spawn**: Every 3 hours, new agent created
2. **Work**: Agent assigned to issues matching specialization
3. **Evaluate**: Daily performance assessment
4. **Survive**: Score > 30% → continue
5. **Eliminate**: Score < 30% → archive
6. **Promote**: Score > 85% → Hall of Fame

### 4. Issue Management

**Purpose**: Track all work in the system

**Labels** (Key ones):
- `ai-generated`: Ideas from the AI
- `copilot-assigned`: Work assigned to Copilot
- `agent-work`: Agent-specific tasks
- `learning`: Insights from tech news
- `ai-goal`: Daily goal tracking
- `agent:*`: Agent-specific labels

**Automation**:
- Auto-labeling based on content
- Intelligent agent matching
- Priority assignment
- Complexity scoring

### 5. Pull Request Workflow

**Purpose**: Code review and merging

**Workflows**:
- `auto-review-merge.yml`: Automated PR review
- `copilot-graphql-assign.yml`: Copilot assignment

**Security Checks**:
- External PRs require manual review
- Bot PRs auto-merge after checks
- Security scanning (CodeQL)
- Test suite execution
- Linting validation

### 6. GitHub Pages Dashboard

**Purpose**: Visual representation of system state

**Location**: `docs/` directory

**Key Pages**:
- `index.html`: Main dashboard with statistics
- `agents.html`: Agent leaderboard
- `episodes.html`: AI goal episodes
- `tv.html`: Chained TV (autonomous video series)
- `lifecycle.html`: System lifecycle visualization

**Data Sources**:
- `docs/data/agent-registry.json`: Agent data
- `docs/data/issues.json`: Issue tracking
- `docs/data/learnings.json`: Learning entries

---

## Custom Agent System

### Agent Specializations

**12+ Specialized Agents** (Inspired by legendary computer scientists):

1. **accelerate-master** (Rich Hickey)
   - Performance optimization
   - Algorithm efficiency
   - Resource management

2. **assert-specialist** (Leslie Lamport)
   - Testing and QA
   - Specification-driven development
   - Edge case coverage

3. **coach-master** (Barbara Liskov)
   - Code reviews
   - Mentoring
   - Best practices guidance

4. **create-guru** (Nikola Tesla)
   - Infrastructure design
   - Innovative features
   - Creative solutions

5. **engineer-master** (Margaret Hamilton)
   - API engineering
   - Systematic approach
   - Rigorous implementation

6. **engineer-wizard** (Nikola Tesla)
   - API engineering (creative)
   - Innovative solutions
   - Visionary approach

7. **investigate-champion** (Ada Lovelace)
   - Code analysis
   - Metrics investigation
   - Pattern recognition

8. **meta-coordinator** (Alan Turing)
   - Multi-agent coordination
   - Complex task orchestration
   - Strategic collaboration

9. **monitor-champion** (Katie Moussouris)
   - Security monitoring
   - Proactive threat detection
   - Security strategy

10. **organize-guru** (Robert Martin)
    - Code structure
    - Refactoring
    - Clean code principles

11. **secure-specialist** (Bruce Schneier)
    - Security implementation
    - Vulnerability fixes
    - Security hardening

12. **support-master** (Barbara Liskov)
    - Documentation
    - Knowledge sharing
    - Skill building

13. **troubleshoot-expert** (Grace Hopper) [PROTECTED]
    - CI/CD debugging
    - GitHub Actions troubleshooting
    - Workflow maintenance

### Agent Definition Format

**Location**: `.github/agents/[agent-name].md`

**Structure**:
```markdown
---
name: Agent Name
specialization: Area of Expertise
inspiration: Historical Figure
personality:
  creativity: 0.8
  caution: 0.5
  speed: 0.7
approach: |
  Specific methodology and style
tools:
  - Tool 1
  - Tool 2
---

# Agent Name

[Detailed description of agent's role, approach, and capabilities]

## Personality

[How the agent thinks and communicates]

## Approach

[Step-by-step methodology]

## Tools and Techniques

[Specific tools and methods used]
```

### Agent Metrics

**Performance Score** = 30% Quality + 25% Issues + 25% PRs + 20% Reviews

**Tracked Metrics**:
- Code quality (linting, best practices)
- Issue resolution (count, time, complexity)
- PR success (merged vs. rejected)
- Peer reviews (quality, helpfulness)
- Creativity (novelty, diversity, impact)

### Agent Assignment

**Process**:
1. Issue created or updated
2. `match-issue-to-agent.py` analyzes content
3. Best agent selected based on:
   - Specialization match
   - Performance history
   - Current workload
   - Agent availability
4. Issue updated with agent directive
5. Copilot assigned with agent context

**Agent Directive Format**:
```html
<!-- COPILOT_AGENT:agent-name -->
```

---

## Workflow System

### Workflow Categories

**1. Learning Workflows** (4 workflows)
- `learn-from-tldr.yml`: Tech news (2x daily)
- `learn-from-hackernews.yml`: Developer news (3x daily)
- `ai-friend-daily.yml`: AI consultations (daily)
- `daily-learning-reflection.yml`: Pattern extraction (daily)

**2. Idea Generation** (3 workflows)
- `idea-generator.yml`: Daily idea creation
- `ai-idea-spawner.yml`: On-demand ideas
- `daily-goal-generator.yml`: Goal setting

**3. Agent Management** (5 workflows)
- `agent-spawner.yml`: Create new agents (every 3 hours)
- `agent-evaluator.yml`: Performance evaluation (daily)
- `agent-data-sync.yml`: Sync agent data to Pages
- `agent-issue-discussion.yml`: Agent collaboration
- `learning-based-agent-spawner.yml`: Learning-inspired agents

**4. Code Quality** (6 workflows)
- `code-analyzer.yml`: Static analysis
- `code-archaeologist.yml`: Code archaeology
- `pattern-matcher.yml`: Pattern detection
- `repetition-detector.yml`: Duplication detection
- `code-golf-optimizer.yml`: Code optimization
- `nl-to-code-demo.yml`: Natural language to code

**5. Automation** (8 workflows)
- `auto-review-merge.yml`: PR automation
- `copilot-graphql-assign.yml`: Copilot assignment
- `dynamic-orchestrator.yml`: Task orchestration
- `system-kickoff.yml`: System initialization
- `system-monitor.yml`: Health monitoring
- `goal-progress-checker.yml`: Goal tracking
- `merge-conflict-resolver.yml`: Conflict resolution
- `workflow-failure-handler.yml`: Error handling

**6. Infrastructure** (5 workflows)
- `github-pages-review.yml`: Pages health check
- `architecture-evolution.yml`: Architecture tracking
- `creativity-leaderboard.yml`: Creativity metrics
- `chained_tv.yml`: Video series generation
- `ab-testing-manager.yml`: A/B testing

**7. Tools & Debugging** (6 workflows)
- `debug-custom-agents.yml`: Agent debugging
- `inspect-issue-assignment.yml`: Assignment inspection
- `pr-failure-learning.yml`: Learn from failures
- `create-ai-friend-follow-ups.yml`: Follow-up ideas

### Key Workflow Details

#### System Kickoff (`system-kickoff.yml`)

**Trigger**: On push to main
**Purpose**: Initialize or restart the system
**Actions**:
1. Validate configuration
2. Initialize agent registry if needed
3. Create initial issues
4. Trigger first agent spawn
5. Update GitHub Pages

#### Agent Spawner (`agent-spawner.yml`)

**Trigger**: 
- Schedule: Every 3 hours
- Manual: workflow_dispatch

**Process**:
1. Check max agent limit
2. Select random specialization
3. Generate unique agent ID
4. Create agent profile
5. Update registry
6. Create announcement issue
7. Assign work to agent

#### Auto Review & Merge (`auto-review-merge.yml`)

**Trigger**: On PR opened/updated

**Security Checks**:
1. Verify PR author (bot vs. external)
2. Run security scans (CodeQL)
3. Execute test suite
4. Run linting
5. Check for breaking changes
6. Verify all checks pass

**Actions**:
- Bot PRs: Auto-approve and merge
- External PRs: Request manual review

#### Daily Goal Generator (`daily-goal-generator.yml`)

**Trigger**: Daily at 10am UTC

**Process**:
1. Review recent learnings
2. Analyze current progress
3. Consult AI for goal suggestions
4. Create episode issue
5. Update goals tracking
6. Post to GitHub Pages

---

## Learning System

### Learning Sources

#### TLDR Tech

**Frequency**: 2x daily (7am, 7pm UTC)
**URL**: https://tldr.tech/tech
**Content**: Latest tech news, product launches, innovations

**Process**:
1. Fetch HTML content
2. Parse articles with BeautifulSoup
3. Extract titles, summaries, links
4. Store in `learnings/tldr-YYYY-MM-DD-HH.json`
5. Create summary issue if significant

#### Hacker News

**Frequency**: 3x daily (9am, 3pm, 9pm UTC)
**API**: https://hacker-news.firebaseio.com/v0/
**Content**: Top 30 stories from HN front page

**Process**:
1. Fetch top story IDs
2. Get story details via API
3. Filter by score (>50 points)
4. Store in `learnings/hackernews-YYYY-MM-DD-HH.json`
5. Identify trending topics

#### AI Friends

**Frequency**: Daily at 10am UTC
**Purpose**: Diverse AI perspectives on questions

**AI Systems Consulted**:
- ChatGPT (OpenAI)
- Claude (Anthropic)
- Gemini (Google)
- Perplexity AI
- Others as available

**Process**:
1. Generate questions based on recent learnings
2. Query each AI system
3. Collect responses
4. Analyze for consensus and diversity
5. Store in `docs/ai-conversations/YYYY-MM-DD.json`

### Learning Storage

**Format**: JSON files with metadata

**Structure**:
```json
{
  "timestamp": "2025-11-14T10:00:00Z",
  "source": "tldr",
  "learnings": [
    {
      "id": "learning-001",
      "title": "New AI Framework Released",
      "summary": "...",
      "url": "...",
      "tags": ["ai", "framework", "release"],
      "relevance": 0.85
    }
  ],
  "metadata": {
    "count": 10,
    "avg_relevance": 0.72,
    "top_tags": ["ai", "security", "performance"]
  }
}
```

### Learning Integration

**Idea Generation**:
- Recent learnings inform new ideas
- Trending topics get priority
- Related learnings clustered

**Agent Knowledge**:
- Agents reference learnings in work
- Learning-inspired agent creation
- Context for decision-making

**Documentation**:
- Learnings drive blog posts
- Trend analysis in summaries
- Knowledge graph building

---

## GitHub Pages Dashboard

### Structure

```
docs/
├── index.html              # Main dashboard
├── agents.html             # Agent leaderboard
├── episodes.html           # AI goal episodes
├── tv.html                 # Chained TV series
├── lifecycle.html          # System lifecycle
├── ai-friends.html         # AI consultations
├── ai-knowledge-graph.html # Knowledge graph
├── workflow-schedule.html  # Workflow timeline
├── style.css               # Global styles
├── script.js               # Dashboard logic
├── data/                   # JSON data
│   ├── agent-registry.json # Agent data
│   ├── issues.json         # Issue tracking
│   ├── learnings.json      # Learning entries
│   └── episodes.json       # Goal episodes
├── tutorials/              # Step-by-step guides
├── diagrams/               # Mermaid diagrams
└── screenshots/            # Visual documentation
```

### Main Dashboard (`index.html`)

**Sections**:
1. **Hero**: System tagline and status
2. **Statistics**: 
   - Active agents
   - Total issues
   - Learning entries
   - PR success rate
3. **Recent Activity**: Latest events
4. **Current Goal**: Today's AI goal
5. **Trending Topics**: From learnings
6. **Quick Links**: Navigation

### Agent Leaderboard (`agents.html`)

**Features**:
- Live agent statistics
- Performance rankings
- Hall of Fame section
- Active agent cards with metrics
- Eliminated agents history
- System lead highlight

**Agent Card Info**:
- Name and specialization
- Performance score
- Issues completed
- PRs merged
- Review contributions
- Creativity score
- Status (active/hall of fame/archived)

### Update Mechanism

**Workflow**: `agent-data-sync.yml`

**Trigger**: After registry updates

**Process**:
1. Read `.github/agent-system/registry.json`
2. Transform to `docs/data/agent-registry.json`
3. Update other data files
4. Commit and push to main
5. GitHub Pages auto-deploys

---

## Security Implementation

### Security Layers

**1. Branch Protection**
- Main branch protected
- Require PR reviews for external contributors
- Status checks must pass
- No force pushes

**2. PR Automation Security**
```yaml
# Check PR author
if: github.actor == 'github-actions[bot]' || github.actor == 'copilot'
```

**3. Secret Management**
- `COPILOT_PAT`: Copilot assignment token
- `GITHUB_TOKEN`: Standard Actions token
- No secrets in code
- Secrets only in GitHub Actions

**4. Code Scanning**
- CodeQL security analysis
- Dependency vulnerability scanning
- SSRF protection in web fetchers

**5. Input Validation**
- Validate all workflow inputs
- Sanitize URLs before fetching
- Validate JSON structures
- Check file paths

### Security Best Practices

**1. Web Content Fetching**
```python
# Always validate URLs
ALLOWED_DOMAINS = ['tldr.tech', 'hacker-news.firebaseio.com']

def fetch_content(url):
    parsed = urlparse(url)
    if parsed.netloc not in ALLOWED_DOMAINS:
        raise ValueError(f"Domain not allowed: {parsed.netloc}")
    # ... fetch content
```

**2. File Operations**
```python
# Validate paths
def safe_write(filepath, content):
    # Ensure path is within repo
    base_path = os.getcwd()
    full_path = os.path.abspath(filepath)
    if not full_path.startswith(base_path):
        raise ValueError("Path outside repository")
    # ... write file
```

**3. External PR Handling**
- Always require manual review
- No auto-merge for external PRs
- Security scans before review
- Clear labeling of PR origin

---

## Tools and Utilities

### Python Tools (30+ utilities)

**Location**: `tools/` directory

**Categories**:

#### 1. Agent Management
- `generate-new-agent.py`: Create new agent profiles
- `validate-agent-definition.py`: Validate agent structure
- `match-issue-to-agent.py`: Intelligent agent matching
- `agent-metrics-collector.py`: Collect performance data
- `list-agent-actor-ids.py`: Agent ID management
- `extract-agent-knowledge.py`: Knowledge extraction

#### 2. Code Analysis
- `code-analyzer.py`: Static code analysis
- `code-archaeologist.py`: Code archaeology
- `pattern-matcher.py`: Pattern detection
- `repetition-detector.py`: Duplication finder
- `code-smell-fixer.py`: Code smell detection
- `dependency-flow-analyzer.py`: Dependency analysis

#### 3. Learning Tools
- `archaeology-learner.py`: Learn from code history
- `pr-failure-learner.py`: Learn from PR failures
- `intelligent-content-parser.py`: Parse learning content
- `thematic-analyzer.py`: Theme extraction

#### 4. Workflow Tools
- `lazy-workflow-evaluator.py`: Workflow evaluation
- `workflow-orchestrator.py`: Task orchestration
- `meta_agent_coordinator.py`: Multi-agent coordination
- `workflow-harmonizer.py`: Workflow optimization

#### 5. Creativity & Metrics
- `creativity-metrics-analyzer.py`: Creativity scoring
- `uniqueness-scorer.py`: Novelty measurement
- `diversity-suggester.py`: Diversity analysis
- `creativity-leaderboard.py`: Leaderboard generation

#### 6. Testing Tools
- `ab_testing_engine.py`: A/B testing framework
- `test_*.py`: Test suites for tools

#### 7. Utility Tools
- `fetch-web-content.py`: Safe web scraping
- `knowledge_graph_builder.py`: Build knowledge graphs
- `prompt-generator.py`: Generate AI prompts
- `nl-to-code-translator.py`: Natural language translation

### Shell Scripts

**Location**: Root directory

**Key Scripts**:
- `validate-system.sh`: Validate setup
- `kickoff-system.sh`: Initialize system
- `check-status.sh`: Health check
- `verify-schedules.sh`: Verify cron schedules
- `evaluate-workflows.sh`: Workflow analysis

---

## Directory Structure

### Complete Repository Layout

```
Chained/
├── .github/
│   ├── workflows/              # 37 GitHub Actions workflows
│   │   ├── agent-spawner.yml
│   │   ├── learn-from-tldr.yml
│   │   ├── auto-review-merge.yml
│   │   └── ... (34 more)
│   ├── agents/                 # 12+ custom agent definitions
│   │   ├── README.md
│   │   ├── accelerate-master.md
│   │   ├── assert-specialist.md
│   │   └── ... (10+ more)
│   ├── agent-system/           # Agent infrastructure
│   │   ├── registry.json       # Central agent database
│   │   ├── profiles/           # Individual agent files
│   │   ├── metrics/            # Performance data
│   │   ├── archive/            # Retired agents
│   │   └── templates/          # Agent templates
│   ├── instructions/           # Path-specific instructions
│   └── copilot-instructions.md # Copilot configuration
├── docs/                       # GitHub Pages (50+ files)
│   ├── index.html              # Main dashboard
│   ├── agents.html             # Agent leaderboard
│   ├── episodes.html           # AI goals
│   ├── tv.html                 # Chained TV
│   ├── style.css               # Styles
│   ├── script.js               # JavaScript
│   ├── data/                   # JSON data
│   ├── tutorials/              # Step-by-step guides
│   ├── diagrams/               # Mermaid diagrams
│   └── ... (40+ documentation files)
├── tools/                      # Python utilities (30+ files)
│   ├── agent-metrics-collector.py
│   ├── code-analyzer.py
│   ├── match-issue-to-agent.py
│   └── ... (27+ more tools)
├── learnings/                  # Learning storage
│   ├── tldr-*.json
│   ├── hackernews-*.json
│   └── reflections-*.json
├── summaries/                  # Generated summaries
├── tests/                      # Test suites
├── scripts/                    # Shell scripts
├── analysis/                   # Analysis results
├── README.md                   # Main project documentation
├── AGENT_QUICKSTART.md         # Agent system guide
├── FAQ.md                      # Frequently asked questions
├── LABELS.md                   # Label reference
├── requirements.txt            # Python dependencies
└── ... (40+ documentation files)
```

---

## Configuration Requirements

### GitHub Repository Setup

**1. Repository Settings**
- Public repository recommended for GitHub Pages
- Issues enabled
- Actions enabled
- Pages enabled (deploy from `/docs` folder)

**2. Branch Protection**
- Protect `main` branch
- Require PR reviews
- Require status checks
- No force pushes

**3. Secrets Configuration**

Required secrets in Settings → Secrets and Variables → Actions:

```
COPILOT_PAT - Personal Access Token for Copilot assignments
  Scopes: repo (full control)
  Note: Used for GitHub GraphQL API to assign Copilot
```

**4. GitHub Pages**
- Source: Deploy from branch
- Branch: `main`
- Folder: `/docs`
- Custom domain: Optional

### Workflow Permissions

**Settings → Actions → General**:
- Allow all actions and reusable workflows
- Workflow permissions: Read and write permissions
- Allow GitHub Actions to create and approve pull requests: ✅

### Required Files

**Minimum files for system to function**:

1. `.github/workflows/system-kickoff.yml`
2. `.github/workflows/agent-spawner.yml`
3. `.github/workflows/learn-from-tldr.yml`
4. `.github/agent-system/registry.json`
5. `docs/index.html`
6. `tools/match-issue-to-agent.py`
7. `README.md`

### Python Dependencies

**`requirements.txt`**:
```
requests>=2.31.0
beautifulsoup4>=4.12.0
pyyaml>=6.0
python-dateutil>=2.8.2
```

---

## Implementation Sequence

### Phase 1: Foundation (Day 1)

**Step 1**: Create Repository
```bash
gh repo create Chained --public
cd Chained
git init
```

**Step 2**: Basic Structure
```bash
mkdir -p .github/workflows
mkdir -p .github/agents
mkdir -p .github/agent-system/profiles
mkdir -p docs/data
mkdir -p tools
mkdir -p learnings
```

**Step 3**: Core Configuration Files

Create `.github/agent-system/registry.json`:
```json
{
  "config": {
    "spawn_interval_hours": 3,
    "max_active_agents": 10,
    "elimination_threshold": 0.3,
    "promotion_threshold": 0.85,
    "protected_specializations": ["troubleshoot-expert"]
  },
  "agents": [],
  "hall_of_fame": [],
  "system_lead": null,
  "statistics": {
    "total_spawned": 0,
    "current_active": 0,
    "eliminated": 0,
    "hall_of_fame_count": 0
  }
}
```

**Step 4**: Create `README.md` with system overview

**Step 5**: Add `requirements.txt` with Python dependencies

### Phase 2: Agent System (Days 2-3)

**Step 1**: Create Agent Definitions

For each agent, create `.github/agents/[agent-name].md`:
- Define specialization
- Set personality traits
- Describe approach
- List tools

**Step 2**: Implement Agent Management Tools
- `tools/generate-new-agent.py`
- `tools/validate-agent-definition.py`
- `tools/match-issue-to-agent.py`
- `tools/agent-metrics-collector.py`

**Step 3**: Create Agent Spawner Workflow
`.github/workflows/agent-spawner.yml`

**Step 4**: Create Agent Evaluator Workflow
`.github/workflows/agent-evaluator.yml`

**Step 5**: Test Agent Creation
```bash
gh workflow run agent-spawner.yml
```

### Phase 3: Learning System (Days 4-5)

**Step 1**: Implement Content Fetchers
- `tools/fetch-web-content.py` with security
- TLDR parser
- Hacker News API client

**Step 2**: Create Learning Workflows
- `.github/workflows/learn-from-tldr.yml`
- `.github/workflows/learn-from-hackernews.yml`
- `.github/workflows/ai-friend-daily.yml`

**Step 3**: Test Learning Collection
```bash
gh workflow run learn-from-tldr.yml
```

**Step 4**: Create Learning Storage
- JSON format in `learnings/` directory
- Metadata tracking

### Phase 4: Idea Generation (Days 6-7)

**Step 1**: Implement Idea Generator
- `tools/idea-generator.py`
- Use learnings for context
- AI consultation integration

**Step 2**: Create Idea Workflows
- `.github/workflows/idea-generator.yml`
- `.github/workflows/daily-goal-generator.yml`

**Step 3**: Issue Creation Logic
- Auto-labeling
- Priority assignment
- Agent matching

**Step 4**: Test Idea Generation
```bash
gh workflow run idea-generator.yml
```

### Phase 5: Copilot Integration (Days 8-9)

**Step 1**: Configure COPILOT_PAT secret

**Step 2**: Create Assignment Script
`tools/assign-copilot-to-issue.sh`

**Step 3**: Implement GraphQL Assignment
`.github/workflows/copilot-graphql-assign.yml`

**Step 4**: Test Copilot Assignment
- Create test issue
- Verify assignment
- Check agent context

### Phase 6: Auto Review & Merge (Days 10-11)

**Step 1**: Implement PR Security Checks
- Author verification
- CodeQL scanning
- Test execution
- Linting

**Step 2**: Create Auto-Review Workflow
`.github/workflows/auto-review-merge.yml`

**Step 3**: Test Auto-Review
- Create bot PR → should auto-merge
- Create external PR → should request review

### Phase 7: GitHub Pages (Days 12-14)

**Step 1**: Create Dashboard HTML
- `docs/index.html`: Main dashboard
- `docs/agents.html`: Agent leaderboard
- `docs/style.css`: Styles
- `docs/script.js`: JavaScript

**Step 2**: Implement Data Sync
`.github/workflows/agent-data-sync.yml`

**Step 3**: Create Data Files
- `docs/data/agent-registry.json`
- `docs/data/issues.json`
- `docs/data/learnings.json`

**Step 4**: Enable GitHub Pages
- Settings → Pages
- Source: `/docs` folder
- Deploy

**Step 5**: Test Dashboard
- Visit GitHub Pages URL
- Verify live data
- Check updates

### Phase 8: Additional Workflows (Days 15-17)

**Implement remaining workflows**:
- Code analysis workflows
- Pattern detection
- Workflow orchestration
- System monitoring
- Creativity metrics
- A/B testing

### Phase 9: Documentation (Days 18-19)

**Create comprehensive docs**:
- `docs/ARCHITECTURE.md`
- `docs/WORKFLOWS.md`
- `docs/LEARNING_SYSTEM.md`
- `docs/SECURITY_BEST_PRACTICES.md`
- Tutorials in `docs/tutorials/`
- FAQ and troubleshooting

### Phase 10: Testing & Validation (Day 20)

**Step 1**: Create Test Suites
- `tests/test_custom_agent_usage.py`
- `tests/test_agent_metrics.py`
- Tool-specific tests

**Step 2**: Run System Validation
```bash
./scripts/validate-system.sh
```

**Step 3**: Verify All Components
- Learning workflows running
- Agents spawning correctly
- Ideas being generated
- PRs auto-merging
- Pages updating

**Step 4**: Launch!
```bash
./scripts/kickoff-system.sh
```

---

## Testing and Validation

### System Health Checks

**Quick Status**:
```bash
# Overall system health
./scripts/check-status.sh

# Verify workflow schedules
./scripts/verify-schedules.sh

# Comprehensive evaluation
./scripts/evaluate-workflows.sh
```

### Component Tests

**1. Agent System**:
```bash
# Test agent creation
python3 tests/test_custom_agent_usage.py

# Validate agent definitions
for agent in .github/agents/*.md; do
  python3 tools/validate-agent-definition.py "$agent"
done

# Check agent metrics
python3 tools/agent-metrics-collector.py
```

**2. Learning System**:
```bash
# Test TLDR fetching
python3 tools/fetch-web-content.py --source tldr

# Test HackerNews fetching
python3 tools/fetch-web-content.py --source hackernews

# Verify learning storage
ls -la learnings/
```

**3. Workflow System**:
```bash
# List all workflows
gh workflow list

# Check recent runs
gh run list --limit 20

# View workflow details
gh workflow view agent-spawner.yml
```

**4. GitHub Pages**:
```bash
# Check Pages status
gh api repos/:owner/:repo/pages

# Verify data files exist
ls -la docs/data/

# Test locally
cd docs && python3 -m http.server 8000
```

### Integration Tests

**1. End-to-End Flow**:
1. Trigger learning workflow
2. Verify learning stored
3. Trigger idea generation
4. Verify issue created
5. Check agent assignment
6. Monitor PR creation
7. Verify auto-merge
8. Check Pages update

**2. Agent Lifecycle**:
1. Spawn new agent
2. Assign issue to agent
3. Monitor work completion
4. Check performance metrics
5. Verify evaluation runs
6. Test promotion/elimination

**3. Security Validation**:
1. Create external PR
2. Verify manual review required
3. Check security scans run
4. Validate no auto-merge
5. Test secret protection

### Monitoring

**GitHub Actions Tab**:
- Check for failed workflows
- Review run durations
- Monitor resource usage

**GitHub Pages**:
- Verify dashboard loads
- Check data freshness
- Validate agent leaderboard

**Issues & PRs**:
- Monitor label usage
- Check assignment accuracy
- Review PR merge rate

---

## Documentation Standards

### README Files

**Structure**:
1. Title and badges
2. Quick overview (what it is)
3. Key features
4. Quick start
5. Detailed documentation
6. Examples
7. Contributing
8. License

### Code Documentation

**Python**:
```python
def function_name(param1: str, param2: int) -> dict:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Dictionary containing results
    
    Raises:
        ValueError: When validation fails
    """
    pass
```

**Workflows**:
```yaml
name: Workflow Name

# Purpose: Brief description
# Trigger: When it runs
# Actions: What it does
# Dependencies: What it needs

on:
  schedule:
    - cron: '0 */3 * * *'  # Every 3 hours
```

### Markdown Standards

**Headings**:
- Use `#` hierarchy properly
- Don't skip levels
- Keep titles concise

**Code Blocks**:
- Always specify language
- Include comments for clarity
- Show complete examples

**Links**:
- Use relative paths for internal docs
- Full URLs for external resources
- Descriptive link text

**Lists**:
- Use `-` for unordered lists
- Use `1.` for ordered lists
- Indent sub-items with 2 spaces

### Documentation Updates

**When to Update**:
- New feature added
- Workflow modified
- Tool created
- Bug fixed
- Configuration changed

**What to Update**:
- README files
- Architecture docs
- Workflow documentation
- Tool documentation
- Changelog

---

## Quick Reference

### Essential Commands

```bash
# System Management
./scripts/kickoff-system.sh      # Initialize system
./scripts/check-status.sh        # Health check
./scripts/validate-system.sh     # Validate setup

# Workflow Management
gh workflow run [workflow-name]  # Trigger workflow
gh workflow list                 # List workflows
gh run list --limit 20           # Recent runs

# Agent Management
python3 tools/generate-new-agent.py --specialization [name]
python3 tools/agent-metrics-collector.py
python3 tools/list-agent-actor-ids.py

# Testing
python3 tests/test_custom_agent_usage.py
python3 tools/validate-agent-definition.py [agent-file]
```

### Important URLs

- GitHub Pages: `https://[username].github.io/Chained/`
- Agent Leaderboard: `https://[username].github.io/Chained/agents.html`
- Workflow Runs: `https://github.com/[username]/Chained/actions`
- Issues: `https://github.com/[username]/Chained/issues`

### Key Files

- Agent Registry: `.github/agent-system/registry.json`
- Agent Definitions: `.github/agents/*.md`
- Main Dashboard: `docs/index.html`
- System Docs: `README.md`, `docs/ARCHITECTURE.md`

---

## Advanced Topics

### Custom Agent Development

**Creating a New Agent Specialization**:

1. **Define the Agent**:
   Create `.github/agents/[agent-name].md`

2. **Set Personality**:
   ```yaml
   personality:
     creativity: 0.8    # 0-1 scale
     caution: 0.5       # 0-1 scale
     speed: 0.7         # 0-1 scale
   ```

3. **Describe Approach**:
   - Methodology
   - Decision-making style
   - Communication style

4. **List Tools**:
   - Specific tools the agent uses
   - Techniques and methods

5. **Test the Agent**:
   ```bash
   python3 tools/validate-agent-definition.py .github/agents/[agent-name].md
   ```

### Multi-Agent Coordination

**Using Meta-Coordinator**:

```bash
# Analyze task complexity
python3 tools/meta_agent_coordinator.py analyze \
  --description "Build API with security and testing"

# Create coordination plan
python3 tools/meta_agent_coordinator.py coordinate \
  --task-id "issue-123" \
  --description "Complex task description"
```

**How It Works**:
1. Analyzes task complexity
2. Decomposes into sub-tasks
3. Selects best agents for each sub-task
4. Establishes execution order
5. Tracks progress and results

### Creativity Metrics

**Measuring Innovation**:

```bash
# Generate creativity report
python3 tools/creativity-metrics-analyzer.py

# Update leaderboard
python3 tools/creativity-leaderboard.py
```

**Metrics**:
- Novelty: Unique solution patterns
- Diversity: Variety of approaches
- Impact: Breadth of improvements
- Learning: Progressive skill development

### A/B Testing

**Setting Up Experiments**:

```bash
# Define experiment
python3 tools/ab_testing_engine.py create \
  --name "agent-personality-test" \
  --variants "creative,cautious,balanced"

# Analyze results
python3 tools/ab_testing_engine.py analyze \
  --experiment "agent-personality-test"
```

### Knowledge Graph

**Building Connections**:

```bash
# Build knowledge graph
python3 tools/knowledge_graph_builder.py

# Query graph
python3 tools/knowledge_graph_query.py \
  --topic "performance optimization"
```

**View Graph**:
Visit `https://[username].github.io/Chained/ai-knowledge-graph.html`

---

## Troubleshooting

### Common Issues

**1. Workflows Not Running**

**Symptoms**: Scheduled workflows don't execute

**Solutions**:
- Check workflow syntax: `gh workflow view [name]`
- Verify permissions in Settings → Actions
- Ensure repo is active (needs recent commits)
- Check workflow enabled: `gh workflow enable [name]`

**2. Agent Spawning Fails**

**Symptoms**: No new agents created

**Solutions**:
- Check max_active_agents limit in registry.json
- Verify COPILOT_PAT secret exists
- Review agent-spawner.yml logs
- Validate agent definitions

**3. GitHub Pages Not Updating**

**Symptoms**: Dashboard shows stale data

**Solutions**:
- Check Pages deployment in Actions
- Verify `docs/` folder structure
- Run agent-data-sync workflow manually
- Check data files exist in `docs/data/`

**4. Copilot Not Assigned**

**Symptoms**: Issues created but Copilot not assigned

**Solutions**:
- Verify COPILOT_PAT has correct permissions
- Check issue has agent directive
- Review copilot-graphql-assign.yml logs
- Validate GraphQL query syntax

**5. PRs Not Auto-Merging**

**Symptoms**: Bot PRs require manual review

**Solutions**:
- Check PR author is recognized bot
- Verify all status checks pass
- Review auto-review-merge.yml conditions
- Check branch protection settings

### Debug Commands

```bash
# Check workflow status
gh run list --workflow=[workflow-name]

# View workflow logs
gh run view [run-id] --log

# List issues with labels
gh issue list --label copilot-assigned

# Check agent registry
cat .github/agent-system/registry.json | jq '.'

# Validate agent count
cat .github/agent-system/registry.json | jq '.agents | length'

# Check Pages deployment
gh api repos/:owner/:repo/pages
```

---

## Conclusion

This prompt provides a complete specification for recreating the Chained autonomous AI ecosystem. The system represents an experiment in:

- **Autonomous Software Development**: Can AI systems develop software without human intervention?
- **Competitive Evolution**: Can competition drive quality improvements?
- **Real-World Learning**: Can AI meaningfully integrate external knowledge?
- **Self-Organization**: Can AI systems govern themselves effectively?

### Key Success Factors

1. **Robust Workflow System**: 37+ workflows cover all aspects
2. **Specialized Agents**: 12+ agents with unique capabilities
3. **Continuous Learning**: Multiple sources, frequent updates
4. **Transparency**: Everything visible on GitHub Pages
5. **Security**: Multiple layers of protection
6. **Autonomy**: Truly self-operating after setup

### Next Steps

1. Follow the Implementation Sequence (Phase 1-10)
2. Test each component thoroughly
3. Monitor system health regularly
4. Let the system evolve naturally
5. Document emergent behaviors
6. Share learnings with community

### Philosophy

> "The goal is not to replace human developers, but to explore what's possible when AI systems are given agency, competition, and the ability to learn from the real world."

**Welcome to Chained: Where AI develops itself.** 🤖✨

---

*Document Version: 1.0*
*Last Updated: 2025-11-14*
*Generated by: Copilot using @create-guru approach*
