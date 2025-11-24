# 🧠 Enhanced Sub-Agent Spawning Tools

> **Intelligent, learning-driven sub-agent spawning system**

Created by **@create-guru** for the Chained autonomous AI ecosystem.

## Quick Start

```bash
# Run the interactive demo
python3 tools/demo_enhanced_spawning.py

# Spawn sub-agents with intelligence
python3 tools/enhanced_subagent_spawner.py --max-spawns 5

# Select optimal parent for specialization
python3 tools/intelligent_parent_selector.py engineer-master --top-n 3

# Learn from past sub-agent performance
python3 tools/subagent_performance_learner.py --learn

# Get spawning recommendation
python3 tools/subagent_performance_learner.py \
  --recommend secure-specialist \
  --workload 8.5
```

## Tools Overview

### 1. 🎯 Intelligent Parent Selector

**File**: `intelligent_parent_selector.py` (522 lines)

Selects optimal parent agents for sub-agent spawning using multi-criteria scoring.

**Scoring Factors**:
- Performance (35%) - Historical success metrics
- Workload (25%) - Current capacity and sub-agent count
- Compatibility (20%) - Trait matching
- Experience (20%) - Agent maturity

**Usage**:
```bash
# Basic usage
python3 tools/intelligent_parent_selector.py <specialization>

# Options
--top-n N           # Return top N candidates (default: 3)
--format json       # JSON output
--exclude ID1,ID2   # Exclude specific agents
```

**Example Output**:
```
🎯 Parent Selection for: engineer-master
============================================================

#1 🛠️  Sarah (engineer-001)
   Total Score: 87.5/100
   - Performance: 92.0/100
   - Workload: 85.0/100
   - Compatibility: 85.0/100
   - Experience: 88.0/100
   Current Workload: 4 items
   Sub-Agents: 2
   Recommendation: Excellent parent candidate
```

### 2. 🧠 Sub-Agent Performance Learner

**File**: `subagent_performance_learner.py` (639 lines)

Learns from historical sub-agent performance to improve future spawning decisions.

**Features**:
- Success/failure pattern recognition
- Optimal threshold recommendations
- Parent effectiveness tracking
- Confidence-based insights

**Usage**:
```bash
# Analyze all sub-agents
python3 tools/subagent_performance_learner.py --analyze

# Learn insights
python3 tools/subagent_performance_learner.py --learn

# Get recommendation
python3 tools/subagent_performance_learner.py \
  --recommend <specialization> \
  --workload <value>

# Options
--format json       # JSON output
```

**Example Insights**:
```
🧠 Learning Insights
============================================================

📌 Sub-agents for secure-specialist are highly successful
   Type: success_pattern
   Confidence: 85.0%
   Impact: 85.0/100
   💡 Continue spawning at workload ~7.2

📌 Optimal spawning threshold for engineer-master
   Type: threshold_recommendation
   Confidence: 65.0%
   💡 Set threshold to 6.8 items/agent
```

### 3. 🚀 Enhanced Sub-Agent Spawner

**File**: `enhanced_subagent_spawner.py` (432 lines)

Orchestrates intelligent sub-agent spawning by combining workload monitoring, parent selection, and performance learning.

**Process**:
1. Learn from past performance
2. Analyze current workload
3. Make intelligent decisions (apply learning)
4. Select optimal parents
5. Spawn sub-agents with reasoning

**Usage**:
```bash
# Spawn with intelligence
python3 tools/enhanced_subagent_spawner.py

# Options
--max-spawns N      # Maximum agents to spawn (default: 5)
--no-learning       # Disable performance learning
--dry-run           # Simulate without creating
--format json       # JSON output
```

**Example Session**:
```
🤖 Enhanced Sub-Agent Spawner
============================================================

🧠 Learning from past performance...
   ✅ Generated 8 insights

📊 Analyzing current workload...
   ✅ Found 3 spawning recommendations

🎯 Evaluating: security
   Workload: 8.5 items/agent
   Bottleneck: high
   Priority: 4
   🧠 Learning suggests: true
   👥 Selecting parent agents...
      ✅ Found 3 suitable parents
   Decision: ✅ SPAWN
   Confidence: 85.0%

📊 Summary
============================================================
Decisions Made: 3
Agents Spawned: 2/5
```

### 4. 🎭 Demo Script

**File**: `demo_enhanced_spawning.py` (289 lines)

Interactive demonstration of all enhanced spawning features.

**Usage**:
```bash
python3 tools/demo_enhanced_spawning.py
```

**Demos**:
1. Intelligent parent selection
2. Performance learning
3. Spawning recommendations
4. Adaptive weight adjustment

## How It Works

### Intelligent Parent Selection

```python
selector = IntelligentParentSelector()

# Select top 3 parents for security work
parents = selector.select_parent(
    specialization='secure-specialist',
    top_n=3
)

for parent in parents:
    print(f"{parent.agent_name}: {parent.total_score}/100")
    print(f"  Recommendation: {parent.recommendation}")
```

**Scoring Algorithm**:
```
total_score = (
    performance × 0.35 +
    workload × 0.25 +
    compatibility × 0.20 +
    experience × 0.20
)
```

**Constraints**:
- Max 5 sub-agents per parent
- Minimum 24 hours agent age
- Not a sub-agent itself
- Must be active

### Performance Learning

```python
learner = SubAgentPerformanceLearner()

# Analyze all sub-agents
analyses = learner.analyze_all_subagents()

# Learn insights
insights = learner.learn_from_performance()

# Get recommendation
rec = learner.get_spawning_recommendations(
    'secure-specialist',
    workload=8.5
)
```

**Success Criteria**:
- Lifetime ≥ 6 hours
- Contributions ≥ 1
- Overall score ≥ 0.4

**Learning Output**:
- Optimal thresholds per specialization
- Success/failure patterns
- Parent effectiveness scores
- Confidence-based recommendations

### Enhanced Spawning

```python
spawner = EnhancedSubAgentSpawner()

results = spawner.spawn_with_intelligence(
    max_spawns=5,
    use_learning=True,
    dry_run=False
)
```

**Decision Flow**:
```
1. Learn from history
   ↓
2. Analyze workload
   ↓
3. Make intelligent decision
   ├─> Apply learned patterns
   ├─> Adjust thresholds
   └─> Override if learning conflicts
   ↓
4. Select optimal parents
   ├─> Score candidates
   └─> Choose best fit
   ↓
5. Spawn sub-agents
   └─> Record reasoning
```

## Learning Data Format

Stored in `.github/agent-system/subagent_learning.json`:

```json
{
  "by_specialization": {
    "secure-specialist": {
      "optimal_threshold": 7.2,
      "success_rate": 0.85,
      "avg_workload_at_spawn": 7.4
    }
  },
  "insights": [
    {
      "type": "success_pattern",
      "specialization": "secure-specialist",
      "confidence": 0.85,
      "description": "Sub-agents highly successful",
      "recommendation": "Continue at workload ~7.2",
      "timestamp": "2025-11-24T20:00:00"
    }
  ],
  "last_updated": "2025-11-24T20:00:00"
}
```

## Integration Examples

### Workflow Integration

Add to `.github/workflows/agent-spawning.yml`:

```yaml
- name: Spawn with enhanced intelligence
  run: |
    python3 tools/enhanced_subagent_spawner.py \
      --max-spawns 5 \
      --format json > /tmp/spawn_results.json
    
    # Process results
    cat /tmp/spawn_results.json | jq '.spawned_agents'
```

### Programmatic Usage

```python
from enhanced_subagent_spawner import EnhancedSubAgentSpawner

spawner = EnhancedSubAgentSpawner()
results = spawner.spawn_with_intelligence(max_spawns=5)

print(f"Spawned: {results['total_spawned']}")
for agent in results['spawned_agents']:
    print(f"  - {agent['parent_name']} → sub-agent")
```

## Configuration

### Parent Selection Weights

Edit `intelligent_parent_selector.py`:

```python
DEFAULT_WEIGHTS = {
    'performance': 0.35,    # Historical success
    'workload': 0.25,       # Current capacity
    'compatibility': 0.20,  # Trait matching
    'experience': 0.20      # Agent maturity
}
```

### Learning Thresholds

Edit `subagent_performance_learner.py`:

```python
MIN_SUCCESSFUL_LIFETIME_HOURS = 6
MIN_SUCCESSFUL_CONTRIBUTIONS = 1
MIN_SUCCESS_RATE_FOR_INSIGHT = 0.7
MIN_SAMPLE_SIZE = 5
```

### Spawning Constraints

Edit `intelligent_parent_selector.py`:

```python
MAX_SUB_AGENTS_PER_PARENT = 5
OPTIMAL_WORKLOAD_RANGE = (2, 8)
MIN_PARENT_EXPERIENCE_HOURS = 24
```

## Troubleshooting

### No parent candidates found

**Cause**: All potential parents are overloaded or inexperienced

**Solutions**:
- Wait for agents to mature (24h minimum)
- Reduce sub-agent count per parent
- Lower workload requirements temporarily

### Insufficient learning data

**Cause**: Less than 5 sub-agents spawned per specialization

**Solution**: This is normal for new systems. The system will:
- Fall back to workload-only decisions
- Collect data as sub-agents spawn
- Improve recommendations over time

### Learning suggests opposite of workload

**Cause**: Historical success rate low at current workload

**Solution**: Trust the learning! If confidence > 70%, the system is preventing ineffective spawns based on past outcomes.

## Performance Characteristics

**Time Complexity**:
- Parent selection: O(n) where n = active agents
- Performance learning: O(m) where m = total sub-agents
- Enhanced spawning: O(n + m + k) where k = recommendations

**Space Complexity**:
- Learning data: ~1KB per specialization
- Parent scores: ~500 bytes per candidate
- Decision history: ~2KB per spawning session

**Typical Runtimes** (on standard hardware):
- Parent selection (50 agents): ~100ms
- Performance learning (20 sub-agents): ~200ms
- Enhanced spawning (3 recommendations): ~500ms

## Best Practices

### 1. Let Learning Accumulate
- Don't override learning recommendations
- Wait for 5+ sub-agents before trusting insights
- Higher sample size = better decisions

### 2. Monitor Parent Load
- Check parent workload distribution
- Rebalance if some parents overloaded
- Adjust MAX_SUB_AGENTS_PER_PARENT as needed

### 3. Review Learning Data
- Check `.github/agent-system/subagent_learning.json`
- Verify learned thresholds make sense
- Adjust if patterns seem off

### 4. Use Dry Run for Testing
- Test decisions without spawning: `--dry-run`
- Verify parent selection makes sense
- Check confidence scores

### 5. Combine with Workload Analysis
- Use both enhanced and original spawners
- Enhanced for intelligent decisions
- Original for simple workload-only spawning

## Testing

### Run Demos
```bash
# Full demo suite
python3 tools/demo_enhanced_spawning.py

# Individual tests
python3 tools/intelligent_parent_selector.py --help
python3 tools/subagent_performance_learner.py --help
python3 tools/enhanced_subagent_spawner.py --help
```

### Dry Run Spawning
```bash
# Simulate spawning without creating agents
python3 tools/enhanced_subagent_spawner.py --dry-run --max-spawns 10
```

### Test Learning
```bash
# Analyze and learn (safe, read-only initially)
python3 tools/subagent_performance_learner.py --analyze
python3 tools/subagent_performance_learner.py --learn
```

## Related Documentation

- [Enhanced Sub-Agent Spawning Guide](../docs/ENHANCED_SUBAGENT_SPAWNING.md)
- [Original Sub-Agent Spawning](../docs/AI_SUBAGENT_SPAWNING.md)
- [Workload Monitor](./README_WORKLOAD_SPAWNER.md)
- [Agent System](../docs/AGENT_QUICKSTART.md)

## Credits

**Created by**: @create-guru
- Intelligent parent selection algorithm
- Performance learning system
- Enhanced spawning orchestration
- Comprehensive documentation

**Built on**: Existing workload spawning system by @workflows-tech-lead and @APIs-architect

---

*Part of the Chained autonomous AI ecosystem*  
*@create-guru - Inventive and visionary, building the future*  
*Last updated: 2025-11-24*
