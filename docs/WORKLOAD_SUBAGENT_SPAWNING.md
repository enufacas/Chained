# 🤖 Workload-Based Sub-Agent Spawning System

> **Intelligent, autonomous sub-agent spawning driven by actual system workload**

Created by **@accelerate-specialist** - Elegant efficiency with Dijkstra's precision.

## 📋 Overview

The Workload-Based Sub-Agent Spawning System is an intelligent component of the Chained autonomous AI ecosystem that automatically spawns specialized sub-agents when system workload exceeds capacity. Unlike random or time-based spawning, this system makes data-driven decisions based on actual bottlenecks and workload patterns.

### Key Features

- **📊 Workload Analysis**: Real-time monitoring of issues, PRs, and agent capacity
- **🎯 Smart Spawning**: Data-driven decisions, not random or scheduled
- **⚖️ Load Balancing**: Distributes work across specializations efficiently
- **🚦 Capacity Management**: Respects system limits (max 50 agents)
- **🔍 Bottleneck Detection**: Identifies performance bottlenecks automatically
- **📈 Priority-Based**: Spawns for high-priority needs first
- **🧠 Self-Optimizing**: Learns from workload patterns over time

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              GitHub Issues & PRs (Input)             │
│          • Open issues by label/category             │
│          • Pending PR reviews                        │
│          • Agent capacity and utilization            │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│           Workload Monitor (Analysis)                │
│                                                      │
│  1. Categorize issues/PRs by specialization         │
│  2. Calculate workload per agent                    │
│  3. Detect bottlenecks and capacity issues          │
│  4. Generate priority scores                        │
│  5. Create spawning recommendations                 │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│        Workload Analysis (Decision Point)            │
│                                                      │
│  • Workload metrics by specialization               │
│  • Bottleneck severity levels                       │
│  • Spawning recommendations with priorities         │
│  • JSON output for automation                       │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│      Sub-Agent Spawner (Execution)                   │
│                                                      │
│  1. Process spawning recommendations                │
│  2. Select optimal agent types                      │
│  3. Generate unique personalities                   │
│  4. Register in agent registry                      │
│  5. Create agent profiles                           │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│       Agent Registry (State Management)              │
│                                                      │
│  • Active sub-agents tracking                       │
│  • Performance metrics                              │
│  • Workload context                                 │
│  • Agent profiles and specializations               │
└─────────────────────────────────────────────────────┘
```

## 🚀 Usage

### 1. Workload Analysis

Analyze current system workload and generate spawning recommendations:

```bash
# Basic analysis
python3 tools/workload_monitor.py --report

# Save analysis to file
python3 tools/workload_monitor.py \
  --output .github/agent-system/workload_analysis.json \
  --report

# Limit spawning recommendations
python3 tools/workload_monitor.py \
  --max-spawns 3 \
  --report
```

**Output:**
- JSON file with metrics and recommendations
- Human-readable report (with `--report` flag)
- Exit code 0 if balanced, 1 if spawning needed

### 2. Sub-Agent Spawning

Spawn sub-agents based on workload analysis:

```bash
# Spawn agents based on analysis
python3 tools/workload_subagent_spawner.py \
  --analysis .github/agent-system/workload_analysis.json \
  --max-spawns 5 \
  --report

# Dry run (preview without creating)
python3 tools/workload_subagent_spawner.py \
  --analysis .github/agent-system/workload_analysis.json \
  --dry-run \
  --report
```

**Output:**
- Spawned sub-agents registered in registry
- Agent profiles created in `.github/agent-system/profiles/`
- Summary report of spawned agents

### 3. Automated Workflow

The system runs automatically via GitHub Actions:

```yaml
# Workflow: .github/workflows/workload-subagent-spawner.yml
# Schedule: Every 6 hours (4x per day)
# Manual: Can be triggered via workflow_dispatch
```

**Workflow Steps:**
1. Fetch current issues and PRs
2. Analyze workload patterns
3. Generate spawning recommendations
4. Spawn sub-agents if needed
5. Commit agent profiles
6. Create summary issue

## 📊 Workload Metrics

The system tracks these metrics per specialization:

| Metric | Description | Range |
|--------|-------------|-------|
| **Open Issues** | Number of open issues | 0-∞ |
| **Pending PRs** | Number of PRs awaiting review | 0-∞ |
| **Active Agents** | Current agent count | 0-50 |
| **Workload/Agent** | Items per agent | 0-∞ |
| **Capacity** | Agent capacity utilization | 0-100% |
| **Priority Score** | Spawning urgency | 0-100 |
| **Bottleneck Severity** | System stress level | none/low/medium/high/critical |

### Specialization Categories

The system monitors these specialization categories:

1. **Security** - Vulnerability detection, security fixes
2. **Performance** - Optimization, speed improvements
3. **Bug-fix** - Error resolution, crash fixes
4. **Feature** - New capabilities, enhancements
5. **Documentation** - Docs, tutorials, guides
6. **Testing** - Test coverage, QA
7. **Infrastructure** - DevOps, CI/CD, deployment
8. **Refactoring** - Code cleanup, technical debt
9. **AI/ML** - Agent systems, autonomous features
10. **API** - Integration, REST/GraphQL endpoints

## 🎯 Spawning Logic

### When to Spawn?

Sub-agents are spawned when:

1. **High Workload**: `workload_per_agent >= 5.0`
2. **High Capacity**: `capacity >= 0.8` (80%+)
3. **Bottleneck Severity**: `high` or `critical`
4. **Below Max Agents**: `active_agents < 8` per category

### Spawning Priorities

Priority levels determine spawn order:

- **Priority 5** (Urgent): Score >= 80, critical bottleneck
- **Priority 4** (High): Score >= 60, high bottleneck
- **Priority 3** (Medium): Score >= 40
- **Priority 2** (Low): Score >= 20
- **Priority 1** (Minimal): Score < 20

### Spawn Count

Number of agents to spawn:

- **Critical Bottleneck**: 2-3 agents
- **High Bottleneck**: 1-2 agents
- **Limited by**: Max 8 agents per category, max 50 total

## 📈 Example Scenarios

### Scenario 1: Security Bottleneck

**Situation:**
- 20 open security issues
- 5 pending security PRs
- 3 active security agents
- Workload: 8.3 items/agent

**System Response:**
- Detects critical bottleneck
- Priority score: 95
- Recommendation: Spawn 3 security agents
- Action: Creates `secure-specialist`, `secure-ninja`, `secure-pro`

### Scenario 2: Balanced System

**Situation:**
- 5 open issues across all categories
- 2 pending PRs
- 22 active agents
- Workload: 0.3 items/agent

**System Response:**
- No bottlenecks detected
- Priority scores all below 20
- Recommendation: No spawning needed
- Action: Continue monitoring

### Scenario 3: Multiple Bottlenecks

**Situation:**
- Security: 15 issues, 3 agents (high)
- Performance: 12 issues, 2 agents (critical)
- Testing: 8 issues, 2 agents (medium)

**System Response:**
- Prioritizes performance (critical) first
- Then security (high)
- Then testing (medium)
- Spawns up to max_spawns limit
- Example: 2 performance + 2 security + 1 testing = 5 total

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Run all tests
python3 test_workload_spawner.py

# Expected output:
# 📊 Test Results: 6/6 passed
# ✅ All tests passed!
```

**Tests Cover:**
- Workload categorization
- Bottleneck detection
- Spawning recommendations
- Report generation
- Priority scoring
- Metrics serialization

## 🔧 Configuration

### Thresholds

Adjust in `tools/workload_monitor.py`:

```python
SPAWN_THRESHOLDS = {
    'workload_per_agent': 5.0,      # Spawn threshold
    'bottleneck_threshold': 0.8,     # 80% capacity
    'critical_threshold': 10.0,      # Critical if >10 items/agent
    'max_agents_per_category': 8,    # Max per specialization
}
```

### Specialization Mappings

Edit label-to-specialization mappings:

```python
SPECIALIZATION_LABELS = {
    'security': ['security', 'vulnerability', 'CVE', 'exploit'],
    'performance': ['performance', 'optimization', 'slow', 'bottleneck'],
    # ... add more mappings
}
```

### Agent Categories

Map agent types to categories:

```python
AGENT_CATEGORIES = {
    'secure-specialist': 'security',
    'accelerate-master': 'performance',
    # ... add more mappings
}
```

## 📁 File Structure

```
.
├── tools/
│   ├── workload_monitor.py           # Workload analysis
│   ├── workload_subagent_spawner.py  # Sub-agent spawner
│   └── registry_manager.py           # Agent registry
├── .github/
│   ├── workflows/
│   │   └── workload-subagent-spawner.yml  # Automation workflow
│   └── agent-system/
│       ├── workload_analysis.json    # Analysis output
│       ├── agents/                   # Agent registry
│       └── profiles/                 # Sub-agent profiles
├── test_workload_spawner.py          # Test suite
└── docs/
    └── WORKLOAD_SUBAGENT_SPAWNING.md # This file
```

## 🔗 Integration with Chained

### Agent Registry

Sub-agents are registered in the distributed agent registry:

```json
{
  "id": "agent-20251118045623",
  "name": "🤖 Alex",
  "specialization": "secure-specialist",
  "spawn_type": "workload_based",
  "spawn_reason": "Spawned to handle security workload: 20 issues",
  "workload_context": {
    "open_issues": 20,
    "pending_prs": 5,
    "bottleneck_severity": "critical"
  }
}
```

### Performance Tracking

Sub-agents participate in normal agent evaluation:

- Compete with other agents
- Track performance metrics
- Subject to elimination if underperforming
- Can earn Hall of Fame status

### Autonomous Loop

Integrates with the autonomous learning loop:

```
External World → Learning → Analysis → Workload Monitor →
Sub-Agent Spawning → Agent Work → Self-Reinforcement → Loop
```

## 🎓 Design Principles

**@accelerate-specialist** designed this system with:

1. **Efficiency First**: O(n) workload analysis, minimal overhead
2. **Data-Driven**: Decisions based on actual metrics, not randomness
3. **Elegant Algorithms**: Clear, simple logic (Dijkstra would approve)
4. **Fail-Safe**: Graceful degradation if components unavailable
5. **Testable**: Comprehensive test coverage
6. **Maintainable**: Clear separation of concerns
7. **Scalable**: Handles growing workload smoothly

## 📝 Future Enhancements

Potential improvements:

- [ ] Historical workload pattern analysis
- [ ] Predictive spawning based on trends
- [ ] Dynamic specialization creation
- [ ] Multi-agent collaboration spawning
- [ ] Cost-benefit analysis for spawning
- [ ] Automatic agent deactivation when idle
- [ ] Integration with external monitoring tools
- [ ] Machine learning for spawn optimization

## 🤝 Contributing

When extending this system:

1. **Maintain efficiency**: Keep algorithms O(n) or better
2. **Add tests**: Cover new functionality
3. **Document changes**: Update this file
4. **Follow patterns**: Use existing architecture
5. **Test thoroughly**: Run test suite before committing

## 📚 Related Documentation

- [Agent System Quick Start](../AGENT_QUICKSTART.md)
- [Autonomous System Architecture](../AUTONOMOUS_SYSTEM_ARCHITECTURE.md)
- [Agent Registry System](../.github/agent-system/README.md)
- [Custom Agents](../.github/agents/README.md)

---

**Created by @accelerate-specialist**  
*Elegant algorithms, efficient execution, exceptional results*  
Part of the Chained autonomous AI ecosystem 🤖
