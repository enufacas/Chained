# 📊 AI Sub-Agent Spawning Analytics Dashboard

**Created by @create-botter** - Visionary infrastructure analytics for the Chained ecosystem.

## Overview

The Spawning Analytics Dashboard provides comprehensive insights into the effectiveness, patterns, and performance of the AI sub-agent spawning system. It helps understand:

- How well the spawning system is performing
- Whether spawned agents are being utilized effectively
- Patterns in spawning decisions over time
- Recommendations for optimization

## Features

### 📈 Real-Time Metrics

- **Total Spawns**: Complete count of all spawned agents
- **Spawning Types**: Breakdown by workload-based, learning-based, etc.
- **Active vs Deactivated**: Current sub-agent status distribution
- **Lifetime Analysis**: Average duration sub-agents remain active
- **Spawning Frequency**: How often new agents are spawned
- **Effectiveness Score**: Overall system performance (0-100%)

### 🎯 Effectiveness Analysis

- **Decision Quality**: Percentage of spawns that were workload-driven (higher is better)
- **Sub-Agent Utilization**: Ratio of active to total sub-agents (higher is better)
- **Workload Reduction**: How effectively spawning reduces bottlenecks
- **Performance Correlation**: Parent-child agent performance relationship

### 💡 Intelligent Recommendations

The dashboard automatically generates actionable recommendations:

- ⚠️  **High spawning frequency** - Adjust thresholds to reduce churn
- ⚠️  **Low utilization** - Review spawning criteria for better targeting
- ⚠️  **Short lifetime** - Consider longer cooldown periods
- 💡 **Optimization tips** - Suggestions for improving system efficiency

## Usage

### Basic Report

Generate a text report of spawning analytics:

```bash
python3 tools/spawning_analytics.py
```

### JSON Output

Get structured JSON data for programmatic access:

```bash
python3 tools/spawning_analytics.py --format json
```

### Save to File

Save report to a file:

```bash
python3 tools/spawning_analytics.py --output reports/spawning_$(date +%Y%m%d).md
```

### Custom Registry Path

Specify a different registry location:

```bash
python3 tools/spawning_analytics.py --registry-path /path/to/registry
```

## Example Output

### Text Format

```markdown
# 🤖 AI Sub-Agent Spawning Analytics Dashboard

**Generated**: 2025-12-20 10:30:00 UTC
**Period**: 47 spawning events tracked

## 📊 Overall Metrics

- **Total Spawns**: 47
- **Workload-Based**: 32 (68.1%)
- **Learning-Based**: 15
- **Active Sub-Agents**: 8
- **Deactivated Sub-Agents**: 39
- **Avg Sub-Agent Lifetime**: 18.3 hours
- **Spawning Frequency**: 1.85 spawns/day
- **Most Spawned**: secure-specialist
- **Effectiveness Score**: 17.0%

## 🎯 Effectiveness Analysis

- **Decision Quality**: 68.1%
- **Sub-Agent Utilization**: 17.0%

### 💡 Recommendations

- ⚠️  Low sub-agent utilization. Many sub-agents are being deactivated. Review spawning criteria.
- 💡 Increase focus on workload-based spawning for better system responsiveness.

## 📅 Recent Spawning Events

- **2025-12-18 14:23**: 🤖 Alex (secure-specialist) - workload_based
- **2025-12-18 20:15**: 🤖 Jordan (accelerate-master) - workload_based
- **2025-12-19 08:42**: 🤖 Taylor (engineer-master) - learning_based
- **2025-12-19 16:31**: 🤖 Casey (document-ninja) - workload_based
- **2025-12-20 02:18**: 🤖 Morgan (organize-guru) - workload_based
```

### JSON Format

```json
{
  "timestamp": "2025-12-20T10:30:00.000000",
  "metrics": {
    "total_spawns": 47,
    "workload_based_spawns": 32,
    "learning_based_spawns": 15,
    "active_sub_agents": 8,
    "deactivated_sub_agents": 39,
    "avg_sub_agent_lifetime_hours": 18.3,
    "avg_workload_per_agent": 0.0,
    "most_spawned_specialization": "secure-specialist",
    "least_spawned_specialization": "api-architect",
    "spawning_frequency_per_day": 1.85,
    "effectiveness_score": 0.17
  },
  "effectiveness": {
    "spawning_decision_quality": 0.681,
    "workload_reduction_rate": 0.0,
    "sub_agent_utilization": 0.17,
    "parent_child_performance_correlation": 0.0,
    "recommendations": [
      "⚠️  Low sub-agent utilization. Many sub-agents are being deactivated. Review spawning criteria."
    ]
  },
  "recent_events": [
    {
      "timestamp": "2025-12-20T02:18:45.123456",
      "agent_id": "agent-20251220021845-12345",
      "agent_name": "🤖 Morgan",
      "specialization": "organize-guru",
      "spawn_type": "workload_based",
      "spawn_reason": "Spawned to handle refactoring workload: 12 issues + 3 PRs",
      "parent_agent_id": "agent-base-organize-001",
      "workload_context": {
        "open_issues": 12,
        "pending_prs": 3,
        "active_agents": 2
      }
    }
  ]
}
```

## Integration with Existing System

The analytics dashboard integrates seamlessly with:

### 1. Spawning Workflows

View analytics before/after spawning runs:

```bash
# Before spawning
python3 tools/spawning_analytics.py > pre-spawn-report.md

# Run spawning
python3 tools/workload_subagent_spawner.py --analysis workload_analysis.json

# After spawning
python3 tools/spawning_analytics.py > post-spawn-report.md
```

### 2. Monitoring Systems

Export JSON for monitoring dashboards:

```bash
# Export metrics
python3 tools/spawning_analytics.py --format json > metrics.json

# Send to monitoring system
curl -X POST https://monitoring.example.com/metrics \
  -H "Content-Type: application/json" \
  -d @metrics.json
```

### 3. GitHub Actions

Integrate into workflows for automated reporting:

```yaml
- name: Generate Spawning Analytics
  run: |
    python3 tools/spawning_analytics.py \
      --format text \
      --output spawning-report-$(date +%Y%m%d).md
    
- name: Post to Issue
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh issue comment <issue-number> \
      --body-file spawning-report-$(date +%Y%m%d).md
```

## Metrics Explained

### Effectiveness Score

The effectiveness score combines multiple factors:

```
Effectiveness = (Active Sub-Agents / Total Sub-Agents) * 100%
```

**Interpretation:**
- **80%+**: Excellent - Most spawned agents remain active
- **50-79%**: Good - Reasonable utilization
- **30-49%**: Fair - Some optimization needed
- **Below 30%**: Poor - Review spawning criteria

### Decision Quality

Measures how many spawns were data-driven:

```
Decision Quality = (Workload-Based Spawns / Total Spawns) * 100%
```

**Interpretation:**
- **70%+**: Excellent - Most spawns are workload-driven
- **50-69%**: Good - Majority are data-driven
- **Below 50%**: Review - Too many random/learning spawns

### Sub-Agent Utilization

Percentage of sub-agents currently active:

```
Utilization = (Active / (Active + Deactivated)) * 100%
```

**Interpretation:**
- **40%+**: Good - Healthy retention
- **20-39%**: Fair - Some churn expected
- **Below 20%**: High churn - Review deactivation policies

## Recommendations Guide

### ⚠️  High Spawning Frequency (>3 spawns/day)

**Symptoms:**
- Many agents spawned daily
- Short agent lifetimes
- Rapid spawn/deactivate cycles

**Solutions:**
1. Increase workload thresholds in `workload_monitor.py`:
   ```python
   SPAWN_THRESHOLD = 7.0  # Was 5.0
   ```

2. Add cooldown periods between spawns
3. Review workload categorization accuracy

### ⚠️  Low Sub-Agent Utilization (<30%)

**Symptoms:**
- Most sub-agents quickly deactivated
- Low effectiveness score
- Spawning without sustained workload

**Solutions:**
1. Tighten spawning criteria:
   ```python
   BOTTLENECK_THRESHOLD = 0.9  # Was 0.8
   ```

2. Increase minimum idle time before deactivation:
   ```yaml
   min_idle_hours: 24  # Was 12
   ```

3. Review specialization matching accuracy

### ⚠️  Short Sub-Agent Lifetime (<6 hours)

**Symptoms:**
- Agents deactivated shortly after spawn
- Workload spikes quickly resolved
- System appears unstable

**Solutions:**
1. Add spawning cooldown:
   ```python
   SPAWNING_COOLDOWN = 3600  # 1 hour minimum between spawns
   ```

2. Consider predictive spawning (spawn before spike)
3. Batch workload processing

## Advanced Analysis

### Specialization Distribution

Get spawning counts by specialization:

```python
from spawning_analytics import SpawningAnalytics

analytics = SpawningAnalytics()
distribution = analytics.get_specialization_distribution()

for spec, count in distribution.items():
    print(f"{spec}: {count} spawns")
```

### Spawning Timeline

Analyze spawning patterns over time:

```python
analytics = SpawningAnalytics()
timeline = analytics.get_spawning_timeline(days=30)

for date, count in timeline:
    print(f"{date}: {count} spawns")
```

## API Reference

### SpawningAnalytics Class

```python
class SpawningAnalytics:
    def __init__(self, registry_path: str = ".github/agent-system")
    
    def collect_spawning_history(self) -> List[SpawningEvent]
    def calculate_metrics(self, events: List[SpawningEvent]) -> SpawningMetrics
    def analyze_effectiveness(self, events: List[SpawningEvent], 
                            metrics: SpawningMetrics) -> EffectivenessAnalysis
    def generate_report(self, format: str = 'text') -> str
    def get_specialization_distribution(self) -> Dict[str, int]
    def get_spawning_timeline(self, days: int = 30) -> List[Tuple[str, int]]
```

### Data Classes

#### SpawningEvent
```python
@dataclass
class SpawningEvent:
    timestamp: datetime
    agent_id: str
    agent_name: str
    specialization: str
    spawn_type: str
    spawn_reason: str
    parent_agent_id: Optional[str] = None
    workload_context: Optional[Dict[str, Any]] = None
```

#### SpawningMetrics
```python
@dataclass
class SpawningMetrics:
    total_spawns: int
    workload_based_spawns: int
    learning_based_spawns: int
    active_sub_agents: int
    deactivated_sub_agents: int
    avg_sub_agent_lifetime_hours: float
    spawning_frequency_per_day: float
    most_spawned_specialization: str
    effectiveness_score: float
```

#### EffectivenessAnalysis
```python
@dataclass
class EffectivenessAnalysis:
    spawning_decision_quality: float
    sub_agent_utilization: float
    workload_reduction_rate: float
    parent_child_performance_correlation: float
    recommendations: List[str]
```

## Troubleshooting

### No Spawning Events Found

**Cause:** Registry may not contain spawned agents or spawned_at timestamps missing

**Solution:**
```bash
# Verify registry has agents
python3 tools/list_agents_from_registry.py --status all

# Check agent data structure
jq '.agents[] | select(.spawned_at != null)' .github/agent-system/registry.json
```

### Metrics Show Zero Values

**Cause:** Registry manager initialization failed or data incomplete

**Solution:**
```bash
# Check registry path
ls -la .github/agent-system/

# Verify registry structure
python3 -c "
import sys
sys.path.insert(0, 'tools')
from registry_manager import RegistryManager
registry = RegistryManager()
print('Registry OK:', registry is not None)
"
```

## Future Enhancements

Planned improvements by @create-botter:

- [ ] Real-time dashboard with auto-refresh
- [ ] Grafana/Prometheus integration
- [ ] Predictive spawning recommendations
- [ ] Cost analysis (resource usage per spawn)
- [ ] A/B testing framework for spawning strategies
- [ ] Machine learning for optimal threshold tuning
- [ ] Comparative analysis across time periods
- [ ] Parent-child performance correlation analysis
- [ ] Workload pattern visualization

## Related Documentation

- [AI Sub-Agent Spawning](./AI_SUBAGENT_SPAWNING.md) - Main spawning system docs
- [Workload Monitor](../tools/workload_monitor.py) - Workload analysis tool
- [Workload Sub-Agent Spawner](../tools/workload_subagent_spawner.py) - Spawning implementation
- [AI Spawning Orchestrator](../tools/ai_spawning_orchestrator.py) - Intelligent orchestration
- [Spawning Decision Engine](../tools/spawning_decision_engine.py) - Decision logic

## Credits

**Created by @create-botter** - December 2025

Vision: Provide comprehensive, actionable insights into the AI sub-agent spawning system to enable continuous optimization and improvement.

Inspired by: Nikola Tesla's inventive spirit and visionary approach to infrastructure.

---

*Part of the Chained autonomous AI ecosystem* 🤖
*Empowering data-driven decisions for intelligent agent spawning*
