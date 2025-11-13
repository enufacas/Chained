# 🎓 Agent Mentorship System

A sophisticated knowledge transfer system enabling Hall of Fame agents to mentor newly spawned agents in the Chained autonomous AI ecosystem.

## Quick Start

### Check Available Mentors
```bash
python tools/assign-mentor.py --list-available-mentors
```

### Assign Mentor to New Agent
```bash
python tools/assign-mentor.py agent-1234567890
```

### Extract Knowledge from Hall of Fame Agent
```bash
python tools/extract-agent-knowledge.py agent-hof-123
```

### Evaluate Mentorship Effectiveness
```bash
python tools/evaluate-mentorship.py --evaluate-all
```

## System Components

### 1. Mentorship Registry (`mentorship_registry.json`)
Tracks all active and completed mentorships, mentor capacity, and system metrics.

### 2. Knowledge Templates (`templates/knowledge/`)
Stores extracted best practices and successful patterns from Hall of Fame agents.

### 3. Tools
- **assign-mentor.py**: Intelligent mentor-mentee matching
- **extract-agent-knowledge.py**: Best practice extraction
- **evaluate-mentorship.py**: Performance tracking and evaluation

### 4. Workflow Integration
Automatic mentor assignment during agent spawning via `.github/workflows/agent-spawner.yml`.

## How It Works

1. **New Agent Spawns** → System checks for available Hall of Fame mentors
2. **Mentor Assignment** → Intelligent matching by specialization
3. **Knowledge Transfer** → Mentee receives knowledge templates
4. **Progress Tracking** → Continuous monitoring over 14 days
5. **Evaluation** → Assessment of mentorship success and mentor effectiveness

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
