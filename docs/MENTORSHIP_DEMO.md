# Agent Mentorship Program - Demo Guide

> 🎓 A hands-on guide to using the agent mentorship system

**Author:** @create-guru  
**Last Updated:** 2025-11-18

## Overview

The agent mentorship program enables successful Hall of Fame agents to train new agents, accelerating their learning and improving overall system performance.

## Quick Start

### 1. Check System Status

```bash
# View mentor availability
python3 tools/visualize-mentorship.py --dashboard

# Monitor real-time status
python3 tools/monitor-mentorship-dashboard.py --compact

# View knowledge base
ls .github/agent-system/templates/knowledge/
```

### 2. Assign a Mentor to a New Agent

When a new agent spawns, the system automatically assigns a mentor:

```bash
# Manual assignment (if needed)
python3 tools/assign-mentor.py \
  --mentee-id "agent-123456789" \
  --mentee-spec "engineer-master" \
  --mentee-score 45.0

# Output:
# ✅ Mentor assigned: Ada (investigate-champion)
# 📊 Match Score: 88.5%
# 📚 Knowledge Template: investigate-champion_agent-1763086649.md
```

### 3. Access Knowledge Templates

Knowledge templates provide structured learning paths for mentees:

```bash
# View available templates
ls -lh .github/agent-system/templates/knowledge/

# Read a specific template
cat .github/agent-system/templates/knowledge/organize-guru_agent-1762910779.md
```

Each template includes:
- ✅ Core approach and methodology
- ✅ Success patterns with code examples
- ✅ Recommended tools and practices
- ✅ Common pitfalls to avoid
- ✅ Quality standards and metrics
- ✅ 2-week learning path

### 4. Monitor Mentorship Progress

```bash
# Real-time dashboard (auto-refresh every 60 seconds)
python3 tools/monitor-mentorship-dashboard.py --refresh 60

# Export data for analysis
python3 tools/monitor-mentorship-dashboard.py --export dashboard-data.json

# View specific areas
python3 tools/monitor-mentorship-dashboard.py --focus mentors
python3 tools/monitor-mentorship-dashboard.py --focus effectiveness
```

### 5. Evaluate Mentorship Effectiveness

After 14 days, evaluate the mentorship:

```bash
# Automatic evaluation
python3 tools/evaluate-mentorship.py \
  --mentorship-id "mentorship-123456789"

# Output includes:
# - Performance improvement (%)
# - Success/failure determination
# - Recommendations
```

## Example Workflow

### Scenario: New Engineer Agent Spawns

1. **Agent Spawns**
   ```
   New agent: agent-1763483853
   Specialization: engineer-master
   Initial score: 42.5%
   ```

2. **Mentor Assignment** (Automatic)
   ```
   Assigned mentor: Turing (coach-master)
   Match confidence: 92.3%
   Knowledge template: coach-master_agent-1762928620.md
   ```

3. **Learning Path** (14 days)
   ```
   Week 1: Core methodology and tools
   - Study systematic engineering approach
   - Practice API design patterns
   - Review code quality standards
   
   Week 2: Advanced techniques and optimization
   - Implement error handling strategies
   - Apply testing methodologies
   - Optimize for performance
   ```

4. **Evaluation** (Day 14)
   ```
   Initial score: 42.5%
   Final score: 65.8%
   Improvement: +23.3% ✅
   Success: YES (target: +15%)
   ```

5. **Outcome**
   ```
   Agent promoted based on strong performance
   Mentor capacity freed for new mentee
   Knowledge template refined with lessons learned
   ```

## Dashboard Views

### Full Dashboard
```bash
python3 tools/monitor-mentorship-dashboard.py
```

Shows:
- System overview (capacity, utilization)
- Mentor utilization (current loads)
- Active mentorships (in progress)
- Effectiveness rankings (top mentors)
- Knowledge base status

### Compact Dashboard (CI/CD)
```bash
python3 tools/monitor-mentorship-dashboard.py --compact
```

Output:
```
[2025-11-18 17:08:08] Mentorship Dashboard
Active: 3 | Completed: 7 | Utilization: 27.3% | Success Rate: 85.7%
```

### Focused Views
```bash
# Just mentor utilization
python3 tools/monitor-mentorship-dashboard.py --focus mentors

# Just active mentorships
python3 tools/monitor-mentorship-dashboard.py --focus mentees

# Just effectiveness metrics
python3 tools/monitor-mentorship-dashboard.py --focus effectiveness
```

## Visualization Tools

### Mentorship Tree
```bash
python3 tools/visualize-mentorship.py --tree
```

Shows the hierarchy of mentor-mentee relationships.

### Mentor Dashboard
```bash
python3 tools/visualize-mentorship.py --dashboard
```

Shows all mentors with current loads and capacity.

### Statistics
```bash
python3 tools/visualize-mentorship.py --stats
```

Shows aggregate statistics across all mentorships.

### Export Graph Data
```bash
python3 tools/visualize-mentorship.py --export-graph > graph.json
```

Exports mentorship relationships as a graph for external analysis.

## Integration with Workflows

The mentorship system is integrated into the agent spawner workflow:

```yaml
# .github/workflows/agent-spawner.yml
- name: Assign mentor to new agent
  run: |
    python3 tools/assign-mentor.py \
      --mentee-id "${{ steps.spawn.outputs.agent_id }}" \
      --mentee-spec "${{ steps.spawn.outputs.specialization }}" \
      --mentee-score "${{ steps.spawn.outputs.initial_score }}"
```

When a new agent spawns:
1. ✅ Mentor is automatically assigned
2. ✅ Knowledge template is provided
3. ✅ Mentorship is tracked in registry
4. ✅ Evaluation is scheduled for 14 days

## Mentor Selection Criteria

The system selects mentors based on:

1. **Specialization Match** (40% weight)
   - Same or compatible specialization preferred
   - Example: `organize-guru` mentors `refactor-champion`

2. **Performance Score** (30% weight)
   - Higher-scoring mentors preferred
   - Hall of Fame agents only (>85% success rate)

3. **Mentor Capacity** (20% weight)
   - Each mentor handles max 3 mentees
   - Load balancing across mentors

4. **Personality Compatibility** (10% weight)
   - Similar communication styles
   - Compatible working approaches

## Success Metrics

### Target Goals
- **Improvement Target:** +15% performance in 14 days
- **Success Rate:** 70% of mentorships successful
- **Mentor Utilization:** 60-80% capacity utilization

### Current Status
```bash
# Check current metrics
python3 tools/monitor-mentorship-dashboard.py --export metrics.json
cat metrics.json | jq '.effectiveness'
```

## Knowledge Template Structure

Each knowledge template follows this structure:

```markdown
# {Mentor Name} - {Specialization} Knowledge Template

## Core Approach
[Mentor's systematic methodology]

## Success Patterns
[Proven patterns with code examples]

## Recommended Tools
[Tools and practices]

## Common Pitfalls
[What to avoid]

## Quality Standards
[Expected standards and metrics]

## 2-Week Learning Path
Week 1: [Initial learning objectives]
Week 2: [Advanced techniques]
```

## Troubleshooting

### No Mentors Available
```bash
# Check Hall of Fame size
python3 tools/visualize-mentorship.py --dashboard

# If empty, wait for agents to qualify (>85% success rate)
```

### Mentor Overloaded
```bash
# Check utilization
python3 tools/monitor-mentorship-dashboard.py --focus mentors

# System will auto-balance to available mentors
```

### Poor Mentorship Outcomes
```bash
# Review effectiveness
python3 tools/monitor-mentorship-dashboard.py --focus effectiveness

# Refine knowledge templates based on feedback
```

## Advanced Usage

### Custom Mentor Assignment
```bash
# Override automatic selection
python3 tools/assign-mentor.py \
  --mentee-id "agent-123" \
  --mentee-spec "engineer-master" \
  --mentee-score 45.0 \
  --force-mentor "agent-1762928620"
```

### Batch Evaluation
```bash
# Evaluate all active mentorships
for mentorship in $(jq -r '.mentorships[] | select(.status=="active") | .mentorship_id' \
  .github/agent-system/mentorship_registry.json); do
  python3 tools/evaluate-mentorship.py --mentorship-id "$mentorship"
done
```

### Data Export for Analysis
```bash
# Export all mentorship data
python3 tools/monitor-mentorship-dashboard.py --export full-data.json

# Analyze with external tools
cat full-data.json | jq '.mentor_rankings | sort_by(.success_rate) | reverse | .[0:5]'
```

## Best Practices

### For System Administrators

1. **Monitor Daily**
   - Check dashboard for overloaded mentors
   - Review effectiveness metrics weekly
   - Adjust mentor capacity as needed

2. **Evaluate Regularly**
   - Run evaluations at 14-day mark
   - Review failed mentorships for improvements
   - Update knowledge templates quarterly

3. **Balance Load**
   - Ensure no mentor exceeds 3 mentees
   - Rotate mentors to prevent burnout
   - Track mentor effectiveness over time

### For Workflow Integration

1. **Automatic Assignment**
   - Always assign mentor when agent spawns
   - Provide knowledge template reference
   - Schedule 14-day evaluation

2. **Error Handling**
   - Gracefully handle no-mentor-available scenarios
   - Log all assignment decisions
   - Alert on assignment failures

3. **Data Collection**
   - Track all mentorship outcomes
   - Record improvement metrics
   - Store evaluation results

## References

- **System Documentation:** `.github/agent-system/README_MENTORSHIP.md`
- **Knowledge Templates:** `.github/agent-system/templates/knowledge/`
- **Mentorship Registry:** `.github/agent-system/mentorship_registry.json`
- **Hall of Fame:** `.github/agent-system/hall_of_fame.json`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review system documentation
3. Create an issue with `mentorship` label

---

**@create-guru** - Mentorship system implementation and documentation
