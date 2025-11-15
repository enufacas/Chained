# 📈 Agent Investment Tracker

> Track and cultivate agent expertise in learning categories

**Created by:** @organize-guru  
**Version:** 1.0  
**Last Updated:** 2025-11-15

---

## 📋 Table of Contents

- [Overview](#overview)
- [Investment Model](#investment-model)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Investment Levels](#investment-levels)
- [Scoring Algorithm](#scoring-algorithm)
- [Cultivation Opportunities](#cultivation-opportunities)
- [Data Structure](#data-structure)
- [Best Practices](#best-practices)

---

## Overview

The Agent Investment Tracker manages agent specialization and expertise development in learning categories. It tracks cultivation events, calculates investment scores, and identifies opportunities for further growth.

### Key Features

✅ **Investment Tracking** - Record agent work in learning categories  
✅ **Expertise Levels** - Six-level progression from None to Expert  
✅ **Time Decay** - Investment naturally decays without cultivation  
✅ **Recency Boost** - Recent work contributes more to investment score  
✅ **Opportunity Finder** - Suggest next steps for invested agents  
✅ **Portfolio View** - Comprehensive agent investment summaries  

### Philosophy

> "Clean code is simple and direct. Clean code reads like well-written prose."  
> — Robert C. Martin

This tracker follows SOLID principles:
- **Single Responsibility** - Each class has one clear purpose
- **Open/Closed** - Extensible without modification
- **Liskov Substitution** - Consistent interfaces
- **Interface Segregation** - Focused, minimal APIs
- **Dependency Inversion** - Depend on abstractions

---

## Investment Model

### Core Concepts

**Investment**: An agent's accumulated expertise in a learning category, measured by:
- **Score** (0-100): Numerical representation of expertise
- **Level**: Categorical expertise level (Curious → Expert)
- **Cultivation Events**: Historical record of work in the category

**Cultivation**: When an agent works on a learning item in a category:
- Creates a cultivation event with timestamp and impact
- Increases investment score
- Updates investment level if threshold crossed
- Recorded in cultivation history

**Decay**: Investment naturally decays over time if not cultivated:
- Starts after 30 days of inactivity
- Decays at 2% per day
- Ensures investment reflects current expertise
- Can be recovered through new cultivation

### Investment Growth

```
Investment Score Progression:

0 ──────> 5 ──────> 15 ──────> 35 ──────> 60 ──────> 85 ──────> 100
NONE     CURIOUS   LEARNING   PRACTICING  PROFICIENT  EXPERT    MAX
```

**Growth Factors:**
- Impact of cultivation events (0.0 - 1.0)
- Frequency of cultivation
- Recency of activity
- Time-based decay

---

## Quick Start

### Basic Usage

```python
from world.agent_investment_tracker import AgentInvestmentTracker

# Initialize tracker
tracker = AgentInvestmentTracker()

# Record cultivation event
investment = tracker.record_cultivation(
    agent_name="secure-specialist",
    category="Security",
    impact=0.8,
    learning_id="security-vuln-001",
    context="Fixed authentication vulnerability"
)

print(f"Level: {investment.level.name}")
print(f"Score: {investment.score}")
```

### Get Agent Portfolio

```python
# Get all investments for an agent
investments = tracker.get_agent_investments("secure-specialist")

for category, investment in investments.items():
    print(f"{category}: {investment.level.name} (Score: {investment.score})")
```

### Find Experts

```python
from world.agent_investment_tracker import InvestmentLevel

# Get experts in a category
experts = tracker.get_category_experts(
    category="Security",
    min_level=InvestmentLevel.PROFICIENT
)

for agent, investment in experts:
    print(f"{agent}: {investment.score}")
```

---

## API Reference

### AgentInvestmentTracker

Main class for managing agent investments.

#### Constructor

```python
tracker = AgentInvestmentTracker(data_path: Optional[str] = None)
```

**Parameters:**
- `data_path`: Path to JSON data file (default: `world/agent_investments.json`)

#### Methods

##### record_cultivation()

Record a cultivation event when an agent works on a learning category.

```python
investment = tracker.record_cultivation(
    agent_name: str,
    category: str,
    impact: float = 0.5,
    learning_id: Optional[str] = None,
    context: str = ""
) -> CategoryInvestment
```

**Parameters:**
- `agent_name`: Name of the agent
- `category`: Learning category (e.g., "Security", "Performance")
- `impact`: Cultivation strength (0.0 - 1.0), default 0.5
- `learning_id`: Optional ID of specific learning item
- `context`: Optional context description

**Returns:** Updated `CategoryInvestment` object

**Example:**
```python
investment = tracker.record_cultivation(
    agent_name="accelerate-master",
    category="Performance",
    impact=0.7,
    learning_id="perf-optimization-001",
    context="Optimized database query performance"
)
```

##### get_agent_investments()

Get all investments for an agent.

```python
investments = tracker.get_agent_investments(
    agent_name: str,
    min_level: Optional[InvestmentLevel] = None
) -> Dict[str, CategoryInvestment]
```

**Parameters:**
- `agent_name`: Name of the agent
- `min_level`: Optional minimum investment level filter

**Returns:** Dictionary mapping category → CategoryInvestment

**Example:**
```python
# Get all investments
all_investments = tracker.get_agent_investments("engineer-master")

# Get only proficient+ investments
expert_areas = tracker.get_agent_investments(
    "engineer-master",
    min_level=InvestmentLevel.PROFICIENT
)
```

##### get_category_experts()

Get all agents invested in a category.

```python
experts = tracker.get_category_experts(
    category: str,
    min_level: InvestmentLevel = InvestmentLevel.PROFICIENT
) -> List[Tuple[str, CategoryInvestment]]
```

**Parameters:**
- `category`: Learning category
- `min_level`: Minimum investment level (default: PROFICIENT)

**Returns:** List of (agent_name, CategoryInvestment) tuples, sorted by score

**Example:**
```python
security_experts = tracker.get_category_experts("Security")
for agent, investment in security_experts:
    print(f"{agent}: {investment.score}")
```

##### find_cultivation_opportunities()

Identify cultivation opportunities for an agent.

```python
opportunities = tracker.find_cultivation_opportunities(
    agent_name: str,
    available_learnings: List[Dict],
    top_n: int = 10
) -> List[Dict]
```

**Parameters:**
- `agent_name`: Name of the agent
- `available_learnings`: List of available learning items
- `top_n`: Number of top opportunities to return

**Returns:** List of learning opportunities with cultivation scores

**Example:**
```python
# Get learning recommendations
learnings = load_available_learnings()
opportunities = tracker.find_cultivation_opportunities(
    agent_name="organize-guru",
    available_learnings=learnings,
    top_n=5
)

for opp in opportunities:
    print(f"{opp['title']}: {opp['cultivation_score']}")
```

##### get_investment_summary()

Get a summary of an agent's investment portfolio.

```python
summary = tracker.get_investment_summary(agent_name: str) -> Dict
```

**Parameters:**
- `agent_name`: Name of the agent

**Returns:** Summary dictionary with statistics

**Example:**
```python
summary = tracker.get_investment_summary("troubleshoot-expert")
print(f"Total investments: {summary['total_investments']}")
print(f"Expertise levels: {summary['expertise_levels']}")
print(f"Needs cultivation: {summary['needs_cultivation']}")
```

##### apply_decay()

Apply time-based decay to all investments.

```python
stats = tracker.apply_decay() -> Dict[str, int]
```

**Returns:** Dictionary with decay statistics

**Example:**
```python
stats = tracker.apply_decay()
print(f"Processed: {stats['agents_processed']} agents")
print(f"Decayed: {stats['investments_decayed']} investments")
```

---

## Investment Levels

### Level Progression

| Level | Score Range | Description | Typical Cultivation Events |
|-------|-------------|-------------|----------------------------|
| **NONE** | 0.0 - 5.0 | No investment | N/A |
| **CURIOUS** | 5.0 - 15.0 | Initial interest | 1-3 events |
| **LEARNING** | 15.0 - 35.0 | Active learning | 4-10 events |
| **PRACTICING** | 35.0 - 60.0 | Regular practice | 11-25 events |
| **PROFICIENT** | 60.0 - 85.0 | Demonstrated competence | 26-50 events |
| **EXPERT** | 85.0+ | Deep expertise | 51+ events |

### Level Characteristics

**CURIOUS (5-15)**
- Just starting to explore the category
- Limited practical experience
- Interested in learning more

**LEARNING (15-35)**
- Actively building skills
- Some practical application
- Growing confidence

**PRACTICING (35-60)**
- Regular application of skills
- Building consistency
- Developing depth

**PROFICIENT (60-85)**
- Strong competence demonstrated
- Can handle complex scenarios
- Reliable expertise

**EXPERT (85+)**
- Deep domain expertise
- Consistent high-quality work
- Can mentor others

---

## Scoring Algorithm

### Score Calculation

Investment score is calculated based on cultivation history:

```python
score = Σ(event_contribution) for all events

where:
  event_contribution = base_impact × time_factor
  base_impact = event.impact × 10.0  # Scale to 0-10 range
  
  time_factor = 
    if days_ago > 30:
      (1.0 - 0.02)^(days_ago - 30)  # 2% daily decay
    else:
      1.0 + 0.2 × (1.0 - days_ago/30)  # Recency boost up to 20%
```

### Factors Affecting Score

**Impact (0.0 - 1.0)**
- High impact (0.8-1.0): Major contribution, significant learning
- Medium impact (0.5-0.7): Regular work, steady progress
- Low impact (0.2-0.4): Minor contribution, initial exploration

**Recency**
- Recent events (< 30 days): Boosted contribution (up to +20%)
- Older events (> 30 days): Gradual decay (2% per day)

**Frequency**
- More cultivation events = higher score
- Consistent cultivation maintains high scores

### Example Score Progression

```python
# Initial cultivation
Event 1 (Day 0): impact=0.5 → contribution=5.0 → score=5.0 (CURIOUS)

# Regular cultivation
Event 2 (Day 3): impact=0.6 → contribution=6.6 → score=11.6 (CURIOUS)
Event 3 (Day 7): impact=0.7 → contribution=7.7 → score=19.3 (LEARNING)

# Building expertise
Events 4-10: Various impacts → score=42.5 (PRACTICING)
Events 11-25: Consistent work → score=68.2 (PROFICIENT)
Events 26+: Deep expertise → score=87.5 (EXPERT)

# Decay without cultivation
Day 45 (no events): score=68.2 → 58.4 (PROFICIENT, declining)
Day 60 (no events): score=58.4 → 46.8 (PRACTICING)
```

---

## Cultivation Opportunities

### Finding Opportunities

The tracker identifies learning opportunities that align with agent investments:

```python
opportunities = tracker.find_cultivation_opportunities(
    agent_name="secure-specialist",
    available_learnings=learnings,
    top_n=10
)
```

### Prioritization Strategy

1. **Existing Investments**: Categories where agent already invested
2. **Cultivation Needs**: Categories not cultivated recently (>7 days)
3. **High-Impact Learnings**: Base learning relevance score
4. **Growth Potential**: Balance between mastery and exploration

### Opportunity Scoring

```python
cultivation_score = 
  investment_bonus +      # Based on current investment level
  neglect_bonus +         # For categories needing cultivation
  base_learning_score     # Inherent learning relevance
```

**Example Output:**
```json
{
  "title": "Advanced Security Patterns",
  "categories": ["Security", "Programming"],
  "score": 0.75,
  "cultivation_score": 1.45,
  "invested_categories": ["Security"],
  "url": "https://example.com/security-patterns"
}
```

---

## Data Structure

### File Format

**Location:** `world/agent_investments.json`

```json
{
  "last_updated": "2025-11-15T07:47:00.000000",
  "version": "1.0",
  "investments": {
    "agent-name": {
      "Category": {
        "category": "Category",
        "level": "PROFICIENT",
        "score": 65.3,
        "first_invested": "2025-11-01T08:00:00.000000",
        "last_cultivated": "2025-11-14T16:20:00.000000",
        "cultivation_count": 24,
        "cultivation_events": [
          {
            "timestamp": "2025-11-14T16:20:00.000000",
            "category": "Category",
            "learning_id": "learning-001",
            "impact": 0.8,
            "context": "Description of work"
          }
        ]
      }
    }
  }
}
```

### Data Classes

#### CategoryInvestment

```python
@dataclass
class CategoryInvestment:
    category: str                          # Category name
    level: InvestmentLevel                 # Current level
    score: float                           # Investment score (0-100)
    first_invested: Optional[str]          # ISO timestamp
    last_cultivated: Optional[str]         # ISO timestamp
    cultivation_count: int                 # Total events
    cultivation_events: List[CultivationEvent]  # Recent history
```

#### CultivationEvent

```python
@dataclass
class CultivationEvent:
    timestamp: str              # ISO format
    category: str               # Category name
    learning_id: Optional[str]  # Learning item ID
    impact: float               # Impact score (0.0-1.0)
    context: str                # Description
```

---

## Best Practices

### Recording Cultivation

**DO:**
✅ Record cultivation when agent completes work on a learning category  
✅ Use appropriate impact values (0.8-1.0 for major work)  
✅ Include meaningful context descriptions  
✅ Link to specific learning items when possible  

**DON'T:**
❌ Record every minor interaction (reserve for meaningful work)  
❌ Use maximum impact (1.0) unless truly exceptional  
❌ Leave context empty (always describe what was done)  

### Impact Guidelines

```python
# Major contribution - significant learning, complex work
impact = 0.8 - 1.0
context = "Implemented complex security feature"

# Regular work - steady progress, standard difficulty
impact = 0.5 - 0.7
context = "Reviewed and applied security patterns"

# Minor exploration - initial investigation, simple tasks
impact = 0.2 - 0.4
context = "Explored security documentation"
```

### Maintenance

**Run decay regularly:**
```python
# Recommended: Daily or weekly
from world.agent_investment_tracker import AgentInvestmentTracker

tracker = AgentInvestmentTracker()
stats = tracker.apply_decay()
print(f"Decay applied to {stats['investments_decayed']} investments")
```

**Monitor investment health:**
```python
summary = tracker.get_investment_summary(agent_name)
if summary['needs_cultivation']:
    print("Categories needing cultivation:")
    for item in summary['needs_cultivation']:
        print(f"  {item['category']}: {item['days_since']} days ago")
```

### Integration Examples

**With Agent Learning Matcher:**
```python
from world.agent_learning_matcher import AgentLearningMatcher
from world.agent_investment_tracker import AgentInvestmentTracker

matcher = AgentLearningMatcher()
tracker = AgentInvestmentTracker()

# Get matched learnings
recommendations = matcher.match_agent_to_learnings("secure-specialist")

# Find cultivation opportunities
opportunities = tracker.find_cultivation_opportunities(
    agent_name="secure-specialist",
    available_learnings=recommendations['top_learnings'],
    top_n=5
)

# When agent works on a learning
for learning in opportunities[:1]:  # Take top opportunity
    tracker.record_cultivation(
        agent_name="secure-specialist",
        category=learning['categories'][0],
        impact=0.7,
        learning_id=learning.get('id'),
        context=f"Worked on: {learning['title']}"
    )
```

**Batch Cultivation Recording:**
```python
from world.agent_investment_tracker import record_learning_work

# Record work across multiple categories
categories = ["Programming", "DevOps", "Tools"]
record_learning_work(
    agent_name="engineer-master",
    categories=categories,
    learning_id="api-implementation-001",
    impact=0.75
)
```

**Finding Best Agent for Task:**
```python
from world.agent_investment_tracker import get_top_agents_for_category

# Get best agents for a security task
security_experts = get_top_agents_for_category(
    category="Security",
    min_level=InvestmentLevel.PROFICIENT
)

print(f"Assign to: {security_experts[0]}")
```

---

## Extending the System

### Adding Custom Logic

**Custom Impact Calculator:**
```python
class CustomImpactCalculator:
    @staticmethod
    def calculate_impact(work_type: str, complexity: int) -> float:
        base_impact = {
            'bugfix': 0.5,
            'feature': 0.7,
            'refactor': 0.6,
            'documentation': 0.4
        }.get(work_type, 0.5)
        
        complexity_multiplier = min(1.0, 1.0 + (complexity - 3) * 0.1)
        return min(1.0, base_impact * complexity_multiplier)

# Use in cultivation
impact = CustomImpactCalculator.calculate_impact('feature', complexity=5)
tracker.record_cultivation(
    agent_name="create-guru",
    category="Programming",
    impact=impact
)
```

### Custom Decay Strategy

The decay constants can be adjusted:

```python
# In agent_investment_tracker.py

class AgentInvestmentTracker:
    DECAY_DAYS = 30        # Adjust grace period
    DECAY_RATE = 0.02      # Adjust decay speed
    
    # More aggressive decay for fast-moving fields
    CATEGORY_DECAY_RATES = {
        'AI_ML': 0.03,      # 3% daily decay
        'Security': 0.025,  # 2.5% daily decay
        'Programming': 0.02 # 2% daily decay (default)
    }
```

---

## Troubleshooting

### Common Issues

**Issue: Scores not updating**
```python
# Check if events are being recorded
investment = tracker.get_agent_investments("agent-name")["Category"]
print(f"Events: {len(investment.cultivation_events)}")
print(f"Last: {investment.last_cultivated}")
```

**Issue: Decay too aggressive**
```python
# Adjust decay rate
tracker.DECAY_RATE = 0.01  # Reduce from 2% to 1%
tracker.apply_decay()
```

**Issue: Investment file corrupted**
```python
# Backup and reset
import shutil
shutil.copy('world/agent_investments.json', 'world/agent_investments.backup.json')

# Start fresh
tracker = AgentInvestmentTracker()
# Re-record recent cultivations
```

---

## Contributing

When extending the investment tracker:

1. **Follow SOLID principles** - Keep components focused and clean
2. **Write tests** - Ensure reliability
3. **Document changes** - Update this README
4. **Maintain backward compatibility** - Don't break existing data

---

## License

Part of the Chained autonomous AI ecosystem.

**Created by:** @organize-guru  
**Date:** 2025-11-15  
**Version:** 1.0

---

*Clean code is not written by following a set of rules. You don't become a software craftsman by learning a list of what to do and what not to do. Professionalism and craftsmanship come from values that drive disciplines.*  
— Robert C. Martin
