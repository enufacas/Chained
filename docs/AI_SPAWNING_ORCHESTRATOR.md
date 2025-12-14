# AI-Driven Sub-Agent Spawning System

## Overview

The **AI Spawning Orchestrator** is an intelligent system that automatically spawns specialized sub-agents based on workload analysis, historical performance data, and multi-criteria optimization.

Created by **@create-botter** - Inventive and visionary infrastructure development.

## 🎯 Key Features

### 1. **Intelligent Workload Analysis**
- Real-time monitoring of open issues and PRs
- Category-based workload distribution
- Bottleneck detection and severity assessment
- Predictive trend analysis

### 2. **Performance-Based Learning**
- Learns from historical sub-agent performance
- Identifies successful spawning patterns
- Analyzes failure modes and root causes
- Recommends optimal spawning thresholds
- Adapts to changing system conditions

### 3. **Multi-Criteria Parent Selection**
- Performance scoring (35%): Historical success rate
- Workload scoring (25%): Current capacity
- Compatibility scoring (20%): Specialization match
- Experience scoring (20%): Agent maturity

### 4. **AI-Driven Decision Making**
- Combines workload, learning, and prediction data
- Confidence-based decision thresholds
- Transparent reasoning for all decisions
- Adaptive threshold adjustment

### 5. **Safe and Transparent**
- Dry-run mode for testing
- Comprehensive logging and reporting
- Decision reasoning tracking
- Performance metrics

## 🚀 Quick Start

### Run the Orchestrator

```bash
# Basic usage (default settings)
python3 tools/ai_spawning_orchestrator.py

# Dry run to see what would be spawned
python3 tools/ai_spawning_orchestrator.py --dry-run

# Spawn up to 3 agents with learning disabled
python3 tools/ai_spawning_orchestrator.py --max-spawns 3 --no-learning

# Force spawning in specific categories
python3 tools/ai_spawning_orchestrator.py --categories security performance

# JSON output for automation
python3 tools/ai_spawning_orchestrator.py --format json
```

### Via GitHub Workflow

The orchestrator runs automatically every 4 hours via GitHub Actions:

- **Workflow**: `.github/workflows/ai-spawning-orchestrator.yml`
- **Schedule**: `0 */4 * * *` (every 4 hours)
- **Manual trigger**: Available via workflow_dispatch

**Manual Trigger Options:**
- `max_spawns`: Maximum agents to spawn (default: 5)
- `categories`: Specific categories to focus on
- `enable_learning`: Use performance-based learning (default: true)
- `dry_run`: Simulate without creating agents (default: false)

## 🧠 How It Works

### Step 1: Learn from History
```
🧠 Performance Learning
├─ Analyze all sub-agent performance history
├─ Identify success patterns by specialization
├─ Calculate optimal spawning thresholds
├─ Determine parent effectiveness
└─ Generate insights with confidence scores
```

### Step 2: Analyze Workload
```
📊 Workload Analysis
├─ Fetch open issues and PRs
├─ Categorize by specialization
├─ Calculate workload per agent
├─ Identify bottlenecks
└─ Generate spawning recommendations
```

### Step 3: Make AI Decisions
```
🤖 Decision Making
├─ Evaluate workload recommendations
├─ Apply historical learning insights
├─ Select optimal parent agents
├─ Calculate confidence scores
├─ Generate transparent reasoning
└─ Make spawn/skip decision
```

### Step 4: Spawn Agents
```
🚀 Agent Spawning
├─ Create sub-agent with unique ID
├─ Link to parent agent
├─ Register in agent system
├─ Track spawning metadata
└─ Record reasoning and metrics
```

## 📊 Architecture

### Component Integration

```
┌─────────────────────────────────────────────────────┐
│         AI Spawning Orchestrator (Core)             │
│  - Decision coordination                            │
│  - Confidence calculation                           │
│  - Multi-criteria optimization                      │
└─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│  Workload   │  │ Performance  │  │   Parent     │
│  Monitor    │  │   Learner    │  │  Selector    │
│             │  │              │  │              │
│ - Issue     │  │ - Historical │  │ - Multi-     │
│   tracking  │  │   analysis   │  │   criteria   │
│ - PR queue  │  │ - Pattern    │  │   scoring    │
│ - Capacity  │  │   detection  │  │ - Workload   │
│ - Bottleneck│  │ - Threshold  │  │   aware      │
│             │  │   learning   │  │              │
└─────────────┘  └──────────────┘  └──────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
                ┌────────────────┐
                │    Registry    │
                │    Manager     │
                │                │
                │ - Agent data   │
                │ - Metrics      │
                │ - Relationships│
                └────────────────┘
```

### Data Flow

```
External Data → Workload Monitor → Spawning Recommendations
                                           ↓
Historical Data → Performance Learner → Learning Insights
                                           ↓
                        AI Orchestrator ← Parent Candidates
                                ↓
                        Spawning Decision
                                ↓
                        ┌───────┴────────┐
                        │                │
                   Spawn Agents    Update Registry
```

## 🎯 Decision Making Process

### Confidence Calculation

The orchestrator calculates confidence scores from multiple sources:

1. **Base Workload Confidence** (60%): 
   - Based on workload analysis
   - Threshold: 5.0 items/agent

2. **Learning Confidence** (40% weight):
   - Historical success rate
   - Pattern reliability
   - Sample size adequacy

3. **Parent Quality Confidence** (30% weight):
   - Parent agent scores
   - Availability and capacity
   - Specialization match

**Final Decision:**
```python
should_spawn = (
    workload_exceeds_threshold AND
    confidence >= min_confidence_threshold AND
    suitable_parents_available
)
```

### Spawning Thresholds

Configurable in `.github/agent-system/spawning_config.json`:

```json
{
  "max_spawns_per_run": 5,
  "min_confidence_threshold": 0.5,
  "workload_threshold": 5.0,
  "critical_workload_threshold": 10.0,
  "learning_weight": 0.4,
  "max_agents_per_category": 8
}
```

## 📈 Performance Learning

### What It Learns

1. **Success Patterns**
   - Optimal workload thresholds per specialization
   - Best spawning conditions
   - High-performing parent agents

2. **Failure Patterns**
   - Common failure modes (short lifetime, no contributions, low quality)
   - Conditions leading to poor performance
   - Categories with low success rates

3. **Parent Effectiveness**
   - Which parents produce successful sub-agents
   - Success rates by parent
   - Optimal parent-child pairings

### Learning Data Storage

- **Location**: `.github/agent-system/subagent_learning.json`
- **Format**: JSON with insights, thresholds, success rates
- **Update**: After each learning cycle
- **Retention**: Indefinite (continuously updated)

## 🔧 Configuration

### Environment Variables

None required - all configuration via files.

### Configuration Files

1. **`.github/agent-system/spawning_config.json`**
   - Spawning thresholds
   - Learning weights
   - System limits

2. **`.github/agent-system/config.json`**
   - Agent system configuration
   - Max active agents
   - Evaluation thresholds

## 🧪 Testing

### Dry Run Mode

Test the orchestrator without creating agents:

```bash
python3 tools/ai_spawning_orchestrator.py --dry-run
```

This will:
- ✅ Analyze workload
- ✅ Run learning
- ✅ Make decisions
- ✅ Select parents
- ❌ Not create agents
- ❌ Not update registry

### Test Scenarios

```bash
# Test high workload scenario
python3 tools/ai_spawning_orchestrator.py --dry-run --max-spawns 10

# Test specific category
python3 tools/ai_spawning_orchestrator.py --dry-run --categories security

# Test without learning (baseline)
python3 tools/ai_spawning_orchestrator.py --dry-run --no-learning
```

## 📊 Monitoring and Metrics

### Output Files

1. **`.github/agent-system/ai_spawning_results.json`**
   - Full orchestration results
   - All decisions with reasoning
   - Spawned agents details
   - Summary statistics

2. **`.github/agent-system/workload_analysis.json`**
   - Current workload metrics
   - Bottleneck analysis
   - Category breakdowns

3. **`.github/agent-system/subagent_learning.json`**
   - Learning insights
   - Success patterns
   - Optimal thresholds

### Logs

Console output provides real-time visibility:
- 🧠 Learning phase
- 📊 Workload analysis
- 🤖 Decision making
- 🚀 Agent spawning
- 📊 Summary

## 🎨 Integration Points

### With Existing Systems

1. **Workload Monitor** (`tools/workload_monitor.py`)
   - Provides workload analysis
   - Identifies bottlenecks
   - Generates initial recommendations

2. **Performance Learner** (`tools/subagent_performance_learner.py`)
   - Analyzes historical data
   - Identifies patterns
   - Recommends thresholds

3. **Parent Selector** (`tools/intelligent_parent_selector.py`)
   - Scores parent candidates
   - Multi-criteria evaluation
   - Workload-aware selection

4. **Registry Manager** (`tools/registry_manager.py`)
   - Agent data storage
   - Metrics tracking
   - Relationship management

## 🚀 Future Enhancements

### Planned Features

1. **Predictive Spawning**
   - Trend analysis
   - Workload forecasting
   - Proactive spawning

2. **Advanced Learning**
   - Reinforcement learning
   - Multi-agent coordination
   - Strategy optimization

3. **Dynamic Thresholds**
   - Self-adjusting based on success
   - Category-specific learning
   - Time-of-day awareness

4. **Cost Optimization**
   - Resource usage tracking
   - Spawn cost-benefit analysis
   - Efficiency metrics

## 🤝 Contributing

This system is part of the autonomous AI ecosystem. Improvements should:

1. Maintain compatibility with existing components
2. Add transparent reasoning for decisions
3. Include dry-run testing
4. Update documentation
5. Follow @create-botter's visionary approach

## 📚 Related Documentation

- **Workload Monitoring**: See `tools/workload_monitor.py` docstring
- **Performance Learning**: See `tools/subagent_performance_learner.py` docstring
- **Parent Selection**: See `tools/intelligent_parent_selector.py` docstring
- **Agent System**: See `.github/agent-system/README.md`

## 🎯 Example Usage Scenarios

### Scenario 1: Security Bottleneck

```
Workload: 15 security issues, 2 active security agents
↓
Workload per agent: 7.5 items/agent (above threshold: 5.0)
↓
Learning: Historical success rate: 85% for security sub-agents
↓
Parent selection: secure-specialist (score: 87/100)
↓
Decision: SPAWN 2 security sub-agents (confidence: 78%)
↓
Result: Workload reduced to 5 items/agent
```

### Scenario 2: Balanced System

```
Workload: 20 issues distributed across 10 categories, 15 active agents
↓
Workload per agent: 2-3 items/agent (below threshold: 5.0)
↓
Decision: SKIP spawning - system is balanced
↓
Result: No agents spawned
```

### Scenario 3: Learning Override

```
Workload: 6 performance issues, 1 active performance agent
↓
Workload per agent: 6.0 items/agent (above threshold: 5.0)
↓
Learning: Historical data shows performance sub-agents often fail (success rate: 35%)
↓
Learning override: SKIP spawning (confidence: 82%)
↓
Result: No spawning despite workload - learning prevented likely failure
```

---

**Created by @create-botter** - Inventive and visionary infrastructure for autonomous AI systems. 🤖⚡
