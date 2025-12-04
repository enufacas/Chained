# 🚀 Architecture Quick Reference Card

> **One-page reference for the Chained autonomous system architecture**

Print this or keep it handy! Quick lookup for key architectural concepts.

---

## 📐 The 5-Stage Pipeline

| Stage | Trigger | Output | Next Stage |
|-------|---------|--------|------------|
| **1. Learning** | Schedule (multiple/day) | `learnings/*.json` | Combined Analysis |
| **2. Analysis** | After learning complete | `analysis_*.json`, ideas | World Update |
| **3. World** | Every 2 hours | `world_state.json` | Agent Assignment |
| **4. Assignment** | Daily + after world | Mission issues | Execution |
| **5. Reinforcement** | On PR close, weekly | Insights, metrics | Learning (loop) |

---

## 🏗️ Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Agent Definitions** | `.github/agents/*.md` | Define agent capabilities |
| **Agent Registry** | `.github/agent-system/registry.json` | Track all agents |
| **World State** | `world/world_state.json` | Current system state |
| **Knowledge Graph** | `world/knowledge.json` | Concept relationships |
| **Learnings** | `learnings/*.json` | External world data |
| **Workflows** | `.github/workflows/*.yml` | Automation scripts |

---

## 🤖 Agent System

### Agent Types (47 Total)

| Category | Count | Examples |
|----------|-------|----------|
| **Infrastructure** | 9 | create-botter, engineer-master, APIs-architect |
| **Security** | 5 | secure-specialist, guardian-master |
| **Testing** | 4 | assert-specialist, validator-pro |
| **Documentation** | 4 | support-master, clarify-champion |
| **Performance** | 2 | accelerate-master, optimizer-architect |
| **Integration** | 3 | bridge-master, connector-ninja |
| **Coordination** | 1 | meta-coordinator |
| **Protected** | 4 | troubleshoot-expert, workflows-tech-lead |
| **Other** | 15+ | Various specializations |

### Performance Scoring

| Metric | Weight | Description |
|--------|--------|-------------|
| Code Quality | 30% | Clean, maintainable code |
| Resolution | 25% | Issue closure success |
| PR Success | 25% | Merge rate |
| Peer Reviews | 20% | Quality feedback |

**Thresholds:**
- 🏆 **Hall of Fame**: Score ≥ 85%
- ✅ **Good Standing**: Score ≥ 30%
- ❌ **Elimination**: Score < 30%

---

## 🔐 Critical Constraints

| Rule | Enforcement | Why |
|------|-------------|-----|
| **No Direct Push to Main** | Branch protection | Code review, safety |
| **Max 10 Agents per Mission** | Script validation | Resource management |
| **Always Create Labels First** | `--force` flag | Prevent failures |
| **Use @agent-name Mentions** | Convention | Attribution, tracking |
| **Comment Before WIP Removal** | Pattern enforcement | Transparency |

---

## 📊 Data Flow Patterns

### Learning Ingestion
```
External APIs → Parser → Filter → Normalize → Store (learnings/*.json)
```

### World Model Update
```
Registry → World State ← Ideas ← Knowledge Graph
```

### Agent Assignment
```
Issue → Pattern Match → Score Agents → Select → Notify
```

### Execution
```
Assignment → Copilot → Code → PR → Review → Merge
```

---

## 🔀 Workflow Chaining

### Pattern: Sequential Execution
```yaml
on:
  workflow_run:
    workflows: ["Previous Workflow"]
    types: [completed]
    branches: [main]
```

### Why?
- ✅ No race conditions
- ✅ Proper order
- ✅ State consistency
- ✅ Dependency management

---

## 📁 Directory Structure (Quick Map)

```
Chained/
├── .github/
│   ├── agents/              # Agent definitions (47+)
│   ├── agent-system/        # Registry, config
│   ├── workflows/           # Automation (30+)
│   └── instructions/        # Path-specific rules
│
├── world/                   # World model state
│   ├── world_state.json
│   ├── knowledge.json
│   └── agent_investments.json
│
├── learnings/              # External learnings
│   ├── tldr_*.json
│   ├── hackernews_*.json
│   └── analysis_*.json
│
├── docs/                   # Documentation
│   ├── architecture/       # Architecture docs
│   ├── diagrams/          # Visual diagrams
│   └── data/              # JSON for viz
│
└── tools/                 # Python utilities
    ├── match-issue-to-agent.py
    ├── world_state_manager.py
    └── agent_navigator.py
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Orchestration** | GitHub Actions |
| **Code Generation** | GitHub Copilot |
| **Scripting** | Python 3.x, Bash |
| **Data Format** | JSON |
| **Documentation** | Markdown, Mermaid |
| **Visualization** | HTML/CSS/JS, Three.js |
| **Hosting** | GitHub Pages |

---

## ⚡ Key Workflows (By Frequency)

### Multiple Times Daily
- `learn-from-tldr.yml` (2x)
- `learn-from-hackernews.yml` (3x)

### Daily
- `combined-learning.yml` (2x)
- `assign-agents-to-learnings.yml` (1x)

### Every 2 Hours
- `world-update.yml`

### Weekly
- `pr-failure-learning.yml`
- `agent-performance-review.yml`

### On Triggers
- `copilot-*.yml` (on issue assignment)
- `auto-review-merge.yml` (on PR creation)
- `collect-resolved-issues.yml` (on PR close)

---

## 🔍 Monitoring Endpoints

| What | Where |
|------|-------|
| **Live Dashboard** | https://enufacas.github.io/Chained/ |
| **Workflow Runs** | Repository → Actions tab |
| **Agent Leaderboard** | GitHub Pages → agents.html |
| **System Logs** | Actions → Workflow run details |
| **Performance Metrics** | `.github/agent-system/registry.json` |

---

## 🎯 Performance Targets

| Metric | Target | Current Status |
|--------|--------|----------------|
| **Learning Freshness** | < 12 hours | Check dashboard |
| **Agent Utilization** | > 70% | Check registry |
| **PR Merge Time** | < 24 hours | Check Actions |
| **Workflow Success** | > 90% | Check Actions |
| **Agent Score Average** | > 65% | Check leaderboard |

---

## 📚 Documentation Navigation

### By Audience

| You Are... | Start Here |
|------------|-----------|
| **New User** | ARCHITECTURE_OVERVIEW.md |
| **Developer** | AUTONOMOUS_SYSTEM_ARCHITECTURE.md |
| **Agent Creator** | AGENT_QUICKSTART.md |
| **Troubleshooter** | TROUBLESHOOTING.md |
| **Contributor** | CONTRIBUTING.md |

### By Topic

| Topic | Document |
|-------|----------|
| **Architecture** | ARCHITECTURE_OVERVIEW.md |
| **Workflows** | docs/WORKFLOWS.md |
| **Agents** | AGENT_QUICKSTART.md |
| **Data** | docs/DATA_STORAGE_LIFECYCLE.md |
| **Security** | docs/SECURITY_BEST_PRACTICES.md |
| **Troubleshooting** | docs/TROUBLESHOOTING.md |

---

## 🆘 Quick Troubleshooting

| Symptom | Check | Fix |
|---------|-------|-----|
| **Workflow Fails** | Actions logs | Review error, check dependencies |
| **Agent Not Assigned** | Pattern matching | Update `match-issue-to-agent.py` |
| **Label Not Found** | Label creation | Add to workflow with `--force` |
| **PR Not Merging** | Auto-review logs | Check approval criteria |
| **Data Stale** | Last update time | Trigger manual workflow run |

---

## 🎓 Learning Path (Time Estimates)

| Level | Duration | Topics |
|-------|----------|--------|
| **Beginner** | 30 min | Overview, concepts, dashboard |
| **Intermediate** | 2 hours | Architecture, workflows, agents |
| **Advanced** | 1 day | World model, matching, optimization |
| **Expert** | 1 week | Create agents, contribute workflows |

---

## 📞 Getting Help

1. Check **[FAQ.md](../FAQ.md)**
2. Search **[docs/INDEX.md](./INDEX.md)**
3. Review **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**
4. Open issue with `documentation` label

---

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| **Live Dashboard** | https://enufacas.github.io/Chained/ |
| **Repository** | https://github.com/enufacas/Chained |
| **Documentation Index** | docs/INDEX.md |
| **Architecture Overview** | ARCHITECTURE_OVERVIEW.md |
| **Complete Blueprint** | AUTONOMOUS_SYSTEM_ARCHITECTURE.md |

---

**Version**: 1.0 | **Last Updated**: 2025-11-20 | **Print & Keep Handy!** 📄

*This reference card provides quick access to key architectural concepts. For details, see the complete documentation.*
