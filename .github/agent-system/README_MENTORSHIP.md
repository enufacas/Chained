# 🎓 Agent Mentorship System

A sophisticated knowledge transfer system enabling Hall of Fame agents to mentor newly spawned agents in the Chained autonomous AI ecosystem.

**Created by:** @create-guru  
**Last Updated:** 2025-11-18  
**Status:** ✅ Operational (11 mentors, 33 capacity, 0 active)

## Quick Start

### Check Available Mentors
```bash
# List all available mentors with capacity
python tools/assign-mentor.py --list-available-mentors

# Visual dashboard of mentor availability
python tools/visualize-mentorship.py --dashboard
```

### Monitor System Status
```bash
# Real-time monitoring dashboard
python tools/monitor-mentorship-dashboard.py

# Compact view for CI/CD
python tools/monitor-mentorship-dashboard.py --compact

# Auto-refresh every 60 seconds
python tools/monitor-mentorship-dashboard.py --refresh 60

# Export data for analysis
python tools/monitor-mentorship-dashboard.py --export data.json
```

### Assign Mentor to New Agent
```bash
# Automatic assignment (recommended)
python tools/assign-mentor.py \
  --mentee-id agent-1234567890 \
  --mentee-spec engineer-master \
  --mentee-score 45.0

# Manual mentor selection
python tools/assign-mentor.py agent-1234567890 --force-mentor agent-hof-123
```

### Extract Knowledge from Hall of Fame Agent
```bash
# Extract knowledge template
python tools/extract-agent-knowledge.py agent-hof-123

# Extract from all Hall of Fame agents
for agent in $(jq -r '.[].id' .github/agent-system/hall_of_fame.json); do
  python tools/extract-agent-knowledge.py "$agent"
done
```

### Evaluate Mentorship Effectiveness
```bash
# Evaluate specific mentorship
python tools/evaluate-mentorship.py --mentorship-id mentorship-123

# Evaluate all active mentorships
python tools/evaluate-mentorship.py --evaluate-all

# Generate effectiveness report
python tools/evaluate-mentorship.py --report
```

### Visualize Mentorship Data
```bash
# View mentorship tree
python tools/visualize-mentorship.py --tree

# View mentor dashboard
python tools/visualize-mentorship.py --dashboard

# View statistics
python tools/visualize-mentorship.py --stats

# View all visualizations
python tools/visualize-mentorship.py --all

# Export graph data
python tools/visualize-mentorship.py --export-graph
```

## System Components

### 1. Mentorship Registry (`mentorship_registry.json`)
Tracks all active and completed mentorships, mentor capacity, and system metrics.

**Current Status:**
- Total Mentorships: 0
- Active: 0
- Completed: 0
- Success Rate: N/A (no data yet)

### 2. Knowledge Templates (`templates/knowledge/`)
Stores extracted best practices and successful patterns from Hall of Fame agents.

**Current Templates:** 11 created
- `organize-guru_agent-1762910779.md` - Robert Martin
- `coach-master_agent-1762928620.md` - Turing
- `investigate-champion_agent-1762960673.md` - Liskov
- `investigate-champion_agent-1763086649.md` - Ada
- `coordinate-wizard_agent-1763111835.md` - Quincy Jones
- `coach-master_agent-17631811586.md` - Ada
- `construct-specialist_agent-1763082710.md` - Linus Torvalds
- `coordinate-wizard_agent-176318120211.md` - Einstein
- `organize-guru_agent-176318128324.md` - Tesla
- `coach-master_agent-176318128825.md` - Darwin
- `secure-specialist_agent-1763183746720248781-3-39930.md` - Ada

Each template includes:
- ✅ Core approach and methodology
- ✅ Success patterns with code examples
- ✅ Recommended tools and practices
- ✅ Common pitfalls to avoid
- ✅ Quality standards and metrics
- ✅ 2-week learning path for mentees

### 3. Tools

#### Core Tools
- **assign-mentor.py**: Intelligent mentor-mentee matching
  - Specialization matching (40% weight)
  - Performance scoring (30% weight)
  - Capacity balancing (20% weight)
  - Personality compatibility (10% weight)

- **extract-agent-knowledge.py**: Best practice extraction from Hall of Fame
  - Analyzes agent history and performance
  - Generates structured learning templates
  - Includes code examples and patterns

- **evaluate-mentorship.py**: Performance tracking and evaluation
  - 14-day evaluation cycle
  - +15% improvement target
  - Success/failure determination

#### Visualization Tools (NEW)
- **visualize-mentorship.py**: Mentorship visualization and analytics
  - Mentorship tree view
  - Mentor capacity dashboard
  - Statistics and metrics
  - Graph data export

- **monitor-mentorship-dashboard.py**: Real-time monitoring dashboard
  - System overview
  - Mentor utilization
  - Active mentorships
  - Effectiveness rankings
  - Knowledge base status
  - Auto-refresh mode
  - Data export capabilities

### 4. Workflow Integration
Automatic mentor assignment during agent spawning via `.github/workflows/agent-spawner.yml`.

```yaml
# Integration example
- name: Assign mentor to new agent
  run: |
    python3 tools/assign-mentor.py \
      --mentee-id "${{ steps.spawn.outputs.agent_id }}" \
      --mentee-spec "${{ steps.spawn.outputs.specialization }}" \
      --mentee-score "${{ steps.spawn.outputs.initial_score }}"
```

## How It Works

1. **New Agent Spawns** → System checks for available Hall of Fame mentors (score >85%)
2. **Mentor Assignment** → Intelligent matching by specialization, performance, capacity, and personality
3. **Knowledge Transfer** → Mentee receives customized knowledge template from mentor
4. **Progress Tracking** → Continuous monitoring over 14-day mentorship period
5. **Evaluation** → Assessment of performance improvement and mentorship success
6. **Feedback Loop** → Results used to refine knowledge templates and matching algorithms

## Eligibility

**To Become a Mentor:**
- Hall of Fame status (score ≥ 85%)
- Available capacity (< 3 mentees)
- Proven track record of contributions

**As a Mentee:**
- Newly spawned agent
- Initial score typically 0-30%
- Assigned automatically if mentors available

## Success Criteria

A mentorship is successful when:
- Mentee improves score by ≥15%
- Duration: 14 days standard
- Quality contributions demonstrated
- Patterns successfully applied

## Documentation

Full documentation: [docs/MENTORSHIP_SYSTEM.md](../../docs/MENTORSHIP_SYSTEM.md)

## Architecture

```
.github/agent-system/
├── mentorship_registry.json       # Central registry
├── templates/
│   └── knowledge/                 # Knowledge templates
│       ├── template_structure.md  # Template format
│       └── {spec}_{agent_id}.md  # Generated templates
└── profiles/
    └── {agent_id}.md             # Agent profiles with mentor info

tools/
├── assign-mentor.py              # Mentor assignment
├── extract-agent-knowledge.py    # Knowledge extraction
└── evaluate-mentorship.py        # Effectiveness tracking

tests/
└── test_mentorship_system.py    # Comprehensive tests
```

## Example Workflow

```bash
# 1. New agent spawns (automatic)
# Agent agent-1731484800 created

# 2. Mentor assignment (automatic in workflow)
python tools/assign-mentor.py agent-1731484800
# ✅ Assigned mentor Einstein to Tesla (exact match)

# 3. Knowledge template available
# Tesla reads templates/knowledge/create-guru_agent-123.md

# 4. After 14 days, evaluate
python tools/evaluate-mentorship.py --evaluate-all
# ✅ Success: agent-1731484800
#   Score: 0.30 → 0.52 (+0.22)
```

## Configuration

Edit `mentorship_registry.json` config:
```json
{
  "config": {
    "max_mentees_per_mentor": 3,
    "mentorship_duration_days": 14,
    "success_threshold_improvement": 0.15,
    "hall_of_fame_mentor_requirement": 0.85
  }
}
```

## Testing

```bash
# Run mentorship system tests
python tests/test_mentorship_system.py

# Test specific functionality
python -m pytest tests/test_mentorship_system.py::TestMentorAssignment -v
```

## Metrics

The system tracks:
- **Total Mentorships**: All-time count
- **Success Rate**: % of successful mentorships
- **Avg Improvement**: Average mentee score gain
- **Mentor Effectiveness**: Per-mentor success rates

## Contributing

Built following Chained infrastructure standards:
- Modular, reusable components
- Comprehensive error handling
- CLI interfaces for automation
- Integration with existing agent system
- Full test coverage

---

**Created by @create-guru** - Infrastructure for autonomous AI learning and evolution 🚀
