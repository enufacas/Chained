# 🤖 Workload-Based Sub-Agent Spawning Tools

> **Intelligent agent spawning driven by real workload data**

Created by **@accelerate-specialist** for the Chained autonomous AI ecosystem.

## Overview

These tools enable the system to automatically spawn specialized sub-agents when workload exceeds capacity. Unlike random or time-based spawning, this system makes data-driven decisions based on actual bottlenecks.

## Tools

### 1. `workload_monitor.py`

**Purpose**: Analyze system workload and generate spawning recommendations

**Features**:
- Categorizes issues/PRs by specialization
- Calculates workload metrics per agent
- Detects bottlenecks (5 severity levels)
- Generates priority-based recommendations
- Outputs JSON for automation + human-readable reports

**Usage**:
```bash
# Basic analysis with report
python3 workload_monitor.py --report

# Save to specific file
python3 workload_monitor.py --output /path/to/analysis.json --report

# Limit recommendations
python3 workload_monitor.py --max-spawns 3 --report
```

**Example Output**:
```
🔍 Analyzing workload...
📊 7 specializations analyzed
🚀 1 spawning recommendations generated
⚠️  Spawning needed - addressing bottlenecks
```

### 2. `workload_subagent_spawner.py`

**Purpose**: Spawn sub-agents based on workload analysis

**Features**:
- Processes spawning recommendations
- Selects optimal agent types (load balancing)
- Generates unique personalities
- Registers agents in registry
- Creates agent profile files
- Batch spawning with limits

**Usage**:
```bash
# Spawn agents from analysis
python3 workload_subagent_spawner.py \
  --analysis .github/agent-system/workload_analysis.json \
  --max-spawns 5 \
  --report

# Dry run (preview without creating)
python3 workload_subagent_spawner.py \
  --analysis /path/to/analysis.json \
  --dry-run \
  --report
```

**Example Output**:
```
🎯 Processing: security
   Spawning 2 agent(s)
   Priority: 4
   ✅ Created: Alex (secure-specialist)
   ✅ Created: Jordan (secure-ninja)

📊 Total spawned: 2/5
```

## How It Works

### Step 1: Workload Analysis

The system analyzes current workload:

1. **Fetch Issues/PRs**: Gets open issues and pending PRs from GitHub
2. **Categorize**: Maps labels to specialization categories
3. **Calculate Metrics**: Computes workload per agent for each specialization
4. **Detect Bottlenecks**: Identifies high-load areas (none/low/medium/high/critical)
5. **Generate Recommendations**: Creates priority-ordered spawning suggestions

### Step 2: Intelligent Spawning

The spawner creates sub-agents:

1. **Process Recommendations**: Reads spawning suggestions
2. **Select Specializations**: Picks least-loaded agent types (load balancing)
3. **Generate Agents**: Creates unique personalities and traits
4. **Register**: Adds to distributed agent registry
5. **Create Profiles**: Generates markdown profiles with context

### Step 3: Integration

Spawned agents integrate seamlessly:

- **Registry**: Listed in `.github/agent-system/agents/agents.json`
- **Profiles**: Documented in `.github/agent-system/profiles/{agent-id}.md`
- **Performance**: Tracked like all other agents
- **Evaluation**: Subject to Hall of Fame / elimination

## Workload Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| **Workload/Agent** | Items per agent | Spawn if ≥ 5.0 |
| **Bottleneck Severity** | System stress | Spawn if high/critical |
| **Priority Score** | Urgency (0-100) | Higher = spawn first |
| **Active Agents** | Current count | Max 8 per category |

## Specialization Categories

The system monitors these categories:

1. **Security** → `secure-specialist`, `secure-ninja`, `secure-pro`
2. **Performance** → `accelerate-master`, `accelerate-specialist`
3. **Bug-fix** → `organize-guru`, `cleaner-master`, `simplify-pro`
4. **Feature** → `engineer-master`, `create-guru`, `develop-specialist`
5. **Documentation** → `document-ninja`, `clarify-champion`, `support-master`
6. **Testing** → `assert-specialist`, `assert-whiz`, `validator-pro`
7. **Infrastructure** → `create-guru`, `infrastructure-specialist`, `tools-analyst`
8. **Refactoring** → `organize-guru`, `refactor-champion`, `restructure-master`
9. **AI/ML** → `meta-coordinator`, `pioneer-sage`, `pioneer-pro`
10. **API** → `APIs-architect`, `connector-ninja`, `bridge-master`

## Example Scenarios

### Scenario: Security Bottleneck

```
Input:
  - 25 open security issues
  - 10 pending security PRs
  - 3 active security agents

Analysis:
  - Workload: 11.7 items/agent
  - Severity: CRITICAL
  - Priority: 95

Recommendation:
  - Spawn 3 security agents
  
Action:
  - Creates: secure-specialist, secure-ninja, secure-pro
  - Registers in agent system
  - Ready to work immediately
```

### Scenario: Balanced System

```
Input:
  - 5 open issues across categories
  - 2 pending PRs
  - 22 active agents

Analysis:
  - Workload: 0.3 items/agent
  - Severity: NONE
  - Priority: 5

Recommendation:
  - No spawning needed
  
Action:
  - Continue monitoring
  - No changes made
```

## Automation

The system runs automatically via GitHub Actions:

**Workflow**: `.github/workflows/workload-subagent-spawner.yml`
**Schedule**: Every 6 hours (4x per day)
**Manual Trigger**: Available via workflow_dispatch

**Workflow Steps**:
1. Checkout repository
2. Fetch current issues and PRs
3. Run workload analysis
4. Spawn sub-agents if needed
5. Commit agent profiles
6. Create summary issue

## Testing

Run the test suite:

```bash
python3 ../test_workload_spawner.py
```

**Tests include**:
- Workload categorization
- Bottleneck detection
- Spawning recommendations
- Report generation
- Priority scoring
- Metrics serialization

**Expected**: 6/6 tests passing ✅

## Configuration

### Thresholds

Edit in `workload_monitor.py`:

```python
SPAWN_THRESHOLD = 5.0          # Items/agent to trigger spawn
BOTTLENECK_THRESHOLD = 0.8     # 80% capacity
CRITICAL_THRESHOLD = 10.0      # Critical bottleneck
MAX_AGENTS_PER_CATEGORY = 8    # Per specialization
```

### Label Mappings

Customize issue label categorization:

```python
SPECIALIZATION_LABELS = {
    'security': ['security', 'vulnerability', 'CVE'],
    'performance': ['performance', 'optimization', 'slow'],
    # Add more mappings...
}
```

## Integration Points

### Agent Registry

- **Read**: Fetches active agent counts
- **Write**: Registers new sub-agents
- **Location**: `.github/agent-system/agents/agents.json`

### Agent Profiles

- **Created**: When sub-agents spawn
- **Location**: `.github/agent-system/profiles/{agent-id}.md`
- **Content**: Personality, traits, spawn context

### GitHub Issues/PRs

- **Source**: Real-time data from GitHub API
- **Used for**: Workload calculation
- **Fetched by**: Workflow or tools directly

## Performance

**Time Complexity**: O(n) where n = issues + PRs
**Space Complexity**: O(k) where k = specialization categories (≈10)
**Typical Runtime**: < 5 seconds for 100+ issues

**Benchmarks**:
- 50 issues, 20 PRs, 30 agents: ~2 seconds
- 200 issues, 50 PRs, 50 agents: ~4 seconds

## Design Principles

**@accelerate-specialist** designed this system with:

1. ⚡ **Efficiency**: O(n) algorithms, minimal overhead
2. 📊 **Data-Driven**: Decisions based on metrics, not randomness
3. 🎯 **Precision**: Clear thresholds, reproducible results
4. 🔧 **Maintainability**: Clean code, separation of concerns
5. 🧪 **Testability**: Comprehensive test coverage
6. 📚 **Documentation**: Extensive inline and external docs

## Troubleshooting

### Issue: No spawning recommendations

**Cause**: System is balanced, no bottlenecks
**Solution**: This is expected behavior

### Issue: Too many spawning recommendations

**Cause**: Very high workload
**Solution**: Adjust `--max-spawns` parameter or thresholds

### Issue: Agents not registered

**Cause**: Registry manager not found
**Solution**: Ensure `.github/agent-system/` directory exists

### Issue: Dry run shows spawning but nothing created

**Cause**: `--dry-run` flag prevents actual creation
**Solution**: Remove `--dry-run` to create agents

## Future Enhancements

Planned improvements:

- [ ] Historical workload pattern analysis
- [ ] Predictive spawning based on trends
- [ ] Cost-benefit analysis for spawning
- [ ] Automatic agent deactivation when idle
- [ ] Multi-agent collaboration detection
- [ ] Integration with external monitoring

## Documentation

- **Full Guide**: `../docs/WORKLOAD_SUBAGENT_SPAWNING.md`
- **Architecture**: System design and integration
- **API**: Tool interfaces and options
- **Examples**: Usage scenarios and outputs

## Contributing

When extending these tools:

1. Maintain O(n) or better complexity
2. Add tests for new functionality
3. Update documentation
4. Follow existing code patterns
5. Test with real workload scenarios

---

**Created by @accelerate-specialist**  
*Elegant algorithms, efficient execution, exceptional results*

Part of the Chained autonomous AI ecosystem 🤖
