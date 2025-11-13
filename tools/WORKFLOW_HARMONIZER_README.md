# 🎼 Workflow Harmonizer

**Created by @harmonize-wizard (George Martin)**

A comprehensive workflow orchestration and health monitoring tool for GitHub Actions workflows.

## Overview

The Workflow Harmonizer brings harmony to your workflow ecosystem by analyzing, monitoring, and providing insights for workflow optimization. With a producer's mindset, it helps you bring out the best in each workflow component.

## Features

### 📊 Workflow Analysis
- **Total Workflow Count**: Track all workflows in your repository
- **Schedule Distribution**: Understand when workflows run
- **Trigger Analysis**: Identify event-based workflow patterns
- **Categorization**: Distinguish between scheduled, event-triggered, and manual workflows

### ⚠️ Conflict Detection
- **Schedule Congestion**: Identify workflows running at the same time
- **Trigger Overload**: Detect multiple workflows on the same triggers
- **Resource Contention**: Find potential GitHub Actions usage bottlenecks

### 💡 Coordination Recommendations
- Stagger daily workflows for better resource distribution
- Consolidate high-frequency workflows
- Add concurrency control to prevent duplicate runs
- Optimize workflow scheduling patterns

### 📈 Health Reporting
- Generate comprehensive JSON reports
- Export detailed workflow metadata
- Track workflow dependencies
- Monitor ecosystem health over time

## Installation

```bash
# Install required dependency
pip install pyyaml

# Run the harmonizer
python tools/workflow_harmonizer.py
```

## Usage

### Basic Usage

```python
from tools.workflow_harmonizer import WorkflowHarmonizer

# Create harmonizer instance
harmonizer = WorkflowHarmonizer()

# Print summary to console
harmonizer.print_summary()

# Export detailed report
harmonizer.export_report("workflow_health_report.json")
```

### Command Line

```bash
# Generate report and print summary
cd /path/to/repository
python tools/workflow_harmonizer.py

# Output will be saved to workflow_health_report.json
```

### Programmatic Access

```python
# Load and analyze workflows
harmonizer.load_workflows()

# Get schedule analysis
schedules = harmonizer.analyze_schedules()
# Returns: {frequency: [(workflow_name, cron_expression), ...]}

# Get trigger analysis
triggers = harmonizer.analyze_triggers()
# Returns: {trigger_type: [workflow_names, ...]}

# Detect conflicts
conflicts = harmonizer.detect_conflicts()
# Returns: [{'type': ..., 'severity': ..., 'recommendation': ...}, ...]

# Generate full report
report = harmonizer.generate_health_report()

# Get recommendations
recommendations = harmonizer.generate_coordination_recommendations()
```

## Output Format

### Console Summary

```
======================================================================
🎼 Workflow Harmonizer - Ecosystem Summary
======================================================================

📊 Workflow Statistics:
   Total Workflows: 29
   Scheduled: 21
   Event-Triggered: 9
   Manual Only: 4

⏰ Schedule Distribution:
   every_15_minutes: 2 workflow(s)
   daily_at_9:0: 3 workflow(s)
   ...

🎯 Trigger Distribution:
   schedule: 21 workflow(s)
   workflow_dispatch: 29 workflow(s)
   ...

⚠️  Detected 2 Potential Conflicts:
   - trigger_overload: 21 workflows

💡 Coordination Recommendations:
   💡 Multiple daily workflows detected...
   🔧 Many workflows lack concurrency control...
======================================================================
```

### JSON Report Structure

```json
{
  "timestamp": "2025-11-13T06:28:34.335430",
  "summary": {
    "total_workflows": 29,
    "scheduled_workflows": 21,
    "event_triggered": 9,
    "manual_only": 4
  },
  "schedule_analysis": {
    "every_15_minutes": [
      ["Auto Review & Merge", "*/15 * * * *"],
      ["Copilot Assignment", "*/15 * * * *"]
    ]
  },
  "trigger_analysis": {
    "schedule": ["Workflow1", "Workflow2", ...],
    "pull_request": ["Workflow3", "Workflow4", ...]
  },
  "conflicts": [
    {
      "type": "schedule_congestion",
      "severity": "medium",
      "frequency": "daily_at_9:0",
      "workflows": [...],
      "recommendation": "Consider staggering..."
    }
  ],
  "workflow_list": [
    {
      "id": "agent-spawner",
      "name": "Agent System: Spawner",
      "file": "agent-spawner.yml",
      "triggers": ["schedule", "workflow_dispatch"],
      "schedules": ["0 */3 * * *"],
      "concurrency": {}
    }
  ],
  "recommendations": [...]
}
```

## Use Cases

### 1. Workflow Health Monitoring
Run the harmonizer regularly to track workflow ecosystem health:
```bash
python tools/workflow_harmonizer.py
git add workflow_health_report.json
git commit -m "Update workflow health report"
```

### 2. Pre-deployment Analysis
Before adding new workflows, check for potential conflicts:
```python
harmonizer = WorkflowHarmonizer()
harmonizer.load_workflows()
conflicts = harmonizer.detect_conflicts()
if conflicts:
    print("⚠️ Review these conflicts before deploying")
```

### 3. Optimization Planning
Use recommendations to optimize your CI/CD:
```python
recommendations = harmonizer.generate_coordination_recommendations()
for rec in recommendations:
    print(f"TODO: {rec}")
```

### 4. Documentation Generation
Generate workflow documentation:
```python
report = harmonizer.generate_health_report()
# Use report['workflow_list'] to create documentation
```

## Workflow Schedule Frequencies

The harmonizer recognizes these schedule patterns:

- `every_X_minutes`: Workflows running every X minutes (e.g., `*/15 * * * *`)
- `every_X_hours`: Workflows running every X hours (e.g., `0 */3 * * *`)
- `daily_at_H:M`: Daily workflows at specific time (e.g., `0 9 * * *`)
- `weekly_on_day_N`: Weekly workflows on specific day
- `custom_schedule`: Complex or irregular schedules

## Conflict Types

### Schedule Congestion
**Severity**: Medium  
**Description**: Multiple workflows (>3) scheduled at the same frequency  
**Impact**: Potential resource contention, longer queue times  
**Recommendation**: Stagger execution times

### Trigger Overload
**Severity**: Low  
**Description**: Many workflows (>5) using the same trigger  
**Impact**: May slow down event processing  
**Recommendation**: Review necessity of all triggers

## Best Practices

1. **Run Regular Health Checks**: Schedule the harmonizer to run weekly
2. **Review Conflicts**: Address medium/high severity conflicts promptly
3. **Implement Recommendations**: Use output to guide workflow optimization
4. **Track Changes**: Commit health reports to track ecosystem evolution
5. **Concurrency Control**: Add concurrency groups to all workflows

## Integration

### GitHub Actions Workflow

```yaml
name: "Workflow Health Check"
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  harmonize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install pyyaml
      
      - name: Run Workflow Harmonizer
        run: python tools/workflow_harmonizer.py
      
      - name: Commit report
        run: |
          git config user.name "Workflow Harmonizer"
          git config user.email "harmonizer@chained.ai"
          git add workflow_health_report.json
          git commit -m "Update workflow health report" || echo "No changes"
          git push
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run harmonizer on workflow changes
if git diff --cached --name-only | grep -q "^.github/workflows/"; then
    echo "🎼 Running Workflow Harmonizer..."
    python tools/workflow_harmonizer.py
    
    # Check for high-severity conflicts
    if python -c "import json; conflicts = json.load(open('workflow_health_report.json'))['conflicts']; exit(any(c['severity'] == 'high' for c in conflicts))"; then
        echo "❌ High-severity workflow conflicts detected!"
        echo "Review workflow_health_report.json before committing"
        exit 1
    fi
fi
```

## Technical Details

### YAML Parsing

The harmonizer handles GitHub Actions YAML quirks:
- The `on:` key is parsed as `True` (boolean) by PyYAML
- Automatically detects and handles this edge case
- Supports all GitHub Actions trigger types

### Cron Parsing

Simple cron expression parser:
- Extracts frequency from cron expressions
- Groups workflows by execution frequency
- Identifies potential scheduling conflicts

## Philosophy

**@harmonize-wizard** brings a producer's mindset to workflow orchestration:

> "Like a music producer brings out the best in each instrument, the Workflow Harmonizer brings out the best in each workflow component. It's about creating harmony in the CI/CD ecosystem."

## Future Enhancements

- [ ] Workflow dependency graph visualization
- [ ] Performance metrics integration
- [ ] Workflow cost estimation
- [ ] Automated optimization suggestions
- [ ] Historical trend analysis
- [ ] Integration with GitHub Actions API
- [ ] Real-time monitoring dashboard

## Contributing

Contributions welcome! This tool was created by **@harmonize-wizard** as part of the Chained autonomous AI ecosystem.

## License

MIT License - Part of the Chained project

---

**Created by**: @harmonize-wizard (George Martin)  
**Specialization**: Workflow orchestration and CI/CD harmonization  
**Philosophy**: Bringing out the best in each component with a producer mindset
