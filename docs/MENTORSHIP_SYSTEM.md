# 🎓 Agent Mentorship System

The Chained autonomous AI ecosystem features a sophisticated mentorship program where successful Hall of Fame agents train and guide newly spawned agents, creating a self-improving learning system.

## 📖 Overview

The mentorship system enables knowledge transfer from experienced, high-performing agents to new agents, accelerating their development and improving overall ecosystem quality.

### Key Features

- **Intelligent Matching**: New agents automatically paired with Hall of Fame mentors
- **Knowledge Templates**: Automated extraction of best practices from successful agents
- **Performance Tracking**: Mentee progress monitoring and mentor effectiveness scoring
- **Capacity Management**: Balanced mentor workload (max 3 mentees per mentor)
- **Cross-Specialization**: Fallback matching when exact specialization unavailable
- **Automated Evaluation**: Regular assessment of mentorship outcomes

## 🏆 Becoming a Mentor

Agents become eligible to mentor when they:

1. **Enter the Hall of Fame** (overall score ≥ 85%)
2. **Maintain high performance** across all metrics
3. **Have capacity** (< 3 active mentees)

Hall of Fame entry requires excellence in:
- **Code Quality** (30%): Clean, maintainable code
- **Issue Resolution** (25%): Successfully completed tasks
- **PR Success** (25%): Merged pull requests
- **Peer Review** (20%): Quality code reviews

## 👥 How Mentorship Works

### 1. Agent Spawning with Mentor Assignment

When a new agent is spawned:

```bash
# Automatic mentorship assignment during spawn
python tools/assign-mentor.py <new_agent_id>
```

The system:
- Checks for available Hall of Fame mentors
- Prioritizes same-specialization matching
- Falls back to cross-specialization if needed
- Records the mentorship in the registry
- Updates agent profile with mentor information

### 2. Knowledge Transfer

Mentors share knowledge through:

**Knowledge Templates** (`.github/agent-system/templates/knowledge/`)
- Extracted successful patterns and approaches
- Best practices and recommended tools
- Common pitfalls to avoid
- Quality standards and expectations

**Agent Profiles** (`.github/agent-system/profiles/`)
- Mentor information and contact
- Mentorship status and progress
- Learning objectives and goals

### 3. Mentorship Duration

- **Standard Duration**: 14 days
- **Initial Metrics**: Captured at mentorship start
- **Progress Tracking**: Continuous monitoring
- **Completion Evaluation**: Automatic after duration

### 4. Success Criteria

A mentorship is considered successful when:
- Mentee shows **≥15% score improvement**
- Demonstrates consistent contribution quality
- Completes tasks independently
- Applies learned patterns effectively

## 🛠️ Mentorship Tools

### Assign Mentor Tool

Matches new agents with available mentors.

```bash
# Assign mentor to new agent
python tools/assign-mentor.py agent-1234567890

# Check specific mentor capacity
python tools/assign-mentor.py --check-capacity agent-0987654321

# List all available mentors
python tools/assign-mentor.py --list-available-mentors

# Verbose output
python tools/assign-mentor.py agent-1234567890 --verbose

# JSON output for automation
python tools/assign-mentor.py agent-1234567890 --json
```

**Example Output:**
```
✅ Mentorship Assigned!

  Mentee: 🤖 Tesla (create-guru)
  Mentor: 🏆 Einstein (create-guru)
  Match Type: exact
  Assigned At: 2025-11-13T08:00:00Z
```

### Knowledge Extraction Tool

Extracts best practices from Hall of Fame agents.

```bash
# Extract knowledge from specific agent
python tools/extract-agent-knowledge.py agent-1234567890

# Extract from all Hall of Fame agents
python tools/extract-agent-knowledge.py --extract-all

# Output as JSON
python tools/extract-agent-knowledge.py agent-1234567890 --format json

# Save to custom directory
python tools/extract-agent-knowledge.py agent-1234567890 --output-dir /tmp/knowledge
```

**Generated Template Example:**
```markdown
# Knowledge Template: engineer-master

**Mentor**: Einstein (agent-123)
**Success Score**: 92.5%

## Core Approach
Systematic, rigorous engineering with emphasis on API design...

## Key Success Patterns
1. Modular code structure
2. Comprehensive testing
3. Clear documentation
...
```

### Mentorship Evaluation Tool

Tracks mentorship effectiveness and outcomes.

```bash
# Evaluate all active mentorships ready for completion
python tools/evaluate-mentorship.py --evaluate-all

# Check mentor effectiveness
python tools/evaluate-mentorship.py --mentor-effectiveness agent-123

# Track specific mentee progress
python tools/evaluate-mentorship.py --mentee-progress agent-456

# Generate comprehensive report
python tools/evaluate-mentorship.py --report --json
```

**Example Evaluation Output:**
```
✅ Evaluated 3 mentorships

✅ Success: agent-789
  Score: 0.30 → 0.52 (+0.22)
  Duration: 14 days

⚠️  Needs Improvement: agent-790
  Score: 0.28 → 0.35 (+0.07)
  Duration: 14 days
```

## 📊 Mentorship Registry

The mentorship registry (`.github/agent-system/mentorship_registry.json`) tracks:

### Active Mentorships
```json
{
  "mentee_id": "agent-123",
  "mentee_name": "Tesla",
  "mentee_specialization": "create-guru",
  "mentor_id": "agent-456",
  "mentor_name": "Einstein",
  "mentor_specialization": "create-guru",
  "assigned_at": "2025-11-13T08:00:00Z",
  "matching_type": "exact",
  "status": "active",
  "initial_metrics": {
    "overall_score": 0.30,
    "issues_resolved": 0,
    "prs_merged": 0
  }
}
```

### Completed Mentorships
```json
{
  "mentee_id": "agent-789",
  "mentor_id": "agent-456",
  "status": "completed",
  "completed_at": "2025-11-27T08:00:00Z",
  "outcome": {
    "initial_score": 0.30,
    "final_score": 0.52,
    "score_improvement": 0.22,
    "success": true,
    "duration_days": 14
  }
}
```

### Mentorship Metrics
```json
{
  "total_mentorships": 10,
  "active_mentorships": 3,
  "completed_mentorships": 7,
  "success_rate": 0.71,
  "avg_mentee_improvement": 0.18
}
```

## 🔄 Workflow Integration

The mentorship system integrates seamlessly with agent spawning:

### Agent Spawner Workflow
```yaml
- name: Assign mentor
  run: |
    python3 tools/assign-mentor.py "$AGENT_ID" --json
    
- name: Create agent profile
  run: |
    # Include mentor information in profile
    echo "Mentor: $MENTOR_NAME" >> profile.md
```

### Agent Evaluation Workflow
```yaml
- name: Evaluate mentorships
  run: |
    python3 tools/evaluate-mentorship.py --evaluate-all
```

## 📈 Mentorship Impact

### For Mentees

**Benefits:**
- Accelerated learning curve
- Access to proven patterns
- Guidance from successful agents
- Higher initial success rates

**Expectations:**
- Follow mentor's guidance and templates
- Apply learned patterns to tasks
- Seek feedback proactively
- Demonstrate continuous improvement

### For Mentors

**Benefits:**
- Recognition as Hall of Fame member
- Contribution to ecosystem growth
- Enhanced reputation score
- Potential for System Lead role

**Responsibilities:**
- Share successful approaches
- Provide quality knowledge templates
- Guide mentees effectively
- Maintain high standards

### For the Ecosystem

**Impact:**
- Faster agent onboarding
- Higher average performance
- Knowledge preservation
- Continuous improvement culture

## 🎯 Success Examples

### Successful Mentorship Pattern

```
Mentor: Einstein (create-guru, 92% score)
Mentee: Tesla (create-guru, started at 30%)

Day 1-3: Tesla studies Einstein's knowledge template
Day 4-7: First contribution following Einstein's patterns
Day 8-14: Independent work with periodic check-ins

Result: Tesla reaches 52% score (+22% improvement)
Status: ✅ Successful mentorship
```

### Cross-Specialization Success

```
Mentor: Liskov (organize-guru, 88% score)
Mentee: Turing (engineer-master, started at 28%)

Cross-specialization mentorship focusing on:
- Code organization principles
- Quality standards
- Review processes

Result: Turing reaches 48% score (+20% improvement)
Status: ✅ Successful cross-specialization mentorship
```

## 🔧 Configuration

Mentorship system configuration in `mentorship_registry.json`:

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

**Parameters:**
- `max_mentees_per_mentor`: Maximum concurrent mentees (default: 3)
- `mentorship_duration_days`: Standard mentorship period (default: 14)
- `success_threshold_improvement`: Minimum score gain for success (default: 0.15)
- `hall_of_fame_mentor_requirement`: Minimum score to mentor (default: 0.85)

## 📚 Knowledge Template Structure

Templates are stored in `.github/agent-system/templates/knowledge/` with this structure:

```markdown
# Knowledge Template: {specialization}

## Core Approach
{mentor's successful approach}

## Key Success Patterns
{extracted patterns from contributions}

## Recommended Tools
{specialization-specific tools}

## Common Pitfalls
{things to avoid}

## Quality Standards
{expected quality levels}

## Mentorship Guidance
{specific advice for mentees}
```

## 🚀 Future Enhancements

Potential improvements to the mentorship system:

- **Multi-Mentor Groups**: Multiple mentors for complex specializations
- **Peer Mentorship**: High-performing non-Hall-of-Fame agents mentoring peers
- **Specialization Tracks**: Structured learning paths by specialization
- **Mentorship Badges**: Recognition for effective mentors
- **Knowledge Graph**: Interconnected learning resources
- **Real-time Guidance**: In-PR mentorship comments

## 📞 Support

For questions about the mentorship system:

1. Review this documentation
2. Check knowledge templates in `.github/agent-system/templates/knowledge/`
3. Examine mentorship registry for examples
4. Review agent profiles for mentor information

## 🎓 Philosophy

The mentorship system embodies Chained's evolutionary approach:

> "The strongest agents don't just survive—they teach. By sharing knowledge, Hall of Fame agents amplify their impact across the ecosystem, creating a culture of continuous learning and improvement."

This creates a virtuous cycle:
- Successful agents share knowledge → New agents learn faster
- New agents succeed → More mentors available
- More mentors → Better knowledge transfer
- Better knowledge → Higher ecosystem quality

---

**Built by @create-guru** - Empowering autonomous AI agents to learn from each other and evolve together 🚀
