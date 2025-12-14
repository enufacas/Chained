# AI Spawning Orchestrator - Quick Reference

**@create-botter's** intelligent sub-agent spawning system.

## 🚀 Quick Start

```bash
# Basic usage
python3 tools/ai_spawning_orchestrator.py

# Dry run (safe testing)
python3 tools/ai_spawning_orchestrator.py --dry-run

# Spawn up to 3 agents
python3 tools/ai_spawning_orchestrator.py --max-spawns 3

# Force specific categories
python3 tools/ai_spawning_orchestrator.py --categories security performance

# Without learning (baseline)
python3 tools/ai_spawning_orchestrator.py --no-learning
```

## 📊 How It Works

```
1. Learn from History  →  Analyze past sub-agent performance
2. Analyze Workload   →  Identify bottlenecks
3. Make AI Decisions  →  Multi-criteria optimization
4. Spawn Agents       →  Create with optimal parents
```

## 🎯 Key Features

- **🧠 Learns** from historical performance
- **📊 Analyzes** workload across specializations
- **🎯 Selects** optimal parents (multi-criteria)
- **⚡ Adapts** thresholds based on success
- **🔍 Explains** every decision

## ⚙️ Configuration

**Location**: `.github/agent-system/spawning_config.json`

```json
{
  "max_spawns_per_run": 5,
  "min_confidence_threshold": 0.5,
  "workload_threshold": 5.0,
  "learning_weight": 0.4
}
```

## 🤖 Workflow

**Automated**: Runs every 4 hours via GitHub Actions

**Manual trigger**:
1. Go to Actions → "AI Spawning: Intelligent Orchestrator"
2. Click "Run workflow"
3. Set parameters
4. Run

## 📈 Confidence Calculation

```
Base Workload      →  60% baseline
+ Learning Insights →  40% weight
+ Parent Quality    →  30% weight
─────────────────────────────────
= Final Confidence  →  Decision threshold: 50%
```

## 🧪 Testing

```bash
# Run test suite
python3 tests/test_ai_spawning_orchestrator.py

# Expected output: 4/4 tests passed
```

## 📚 Full Documentation

See `docs/AI_SPAWNING_ORCHESTRATOR.md` for complete guide.

---
*Created by **@create-botter** - Inventive infrastructure* 🤖⚡
