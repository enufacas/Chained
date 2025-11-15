# 🚀 Quick Start: Agent Investment Tracker

Get started with the Agent Investment Tracker in 5 minutes!

**Created by:** @organize-guru

---

## Installation

No installation needed! The tracker is ready to use:

```python
from world.agent_investment_tracker import AgentInvestmentTracker
```

---

## 5-Minute Tutorial

### Step 1: Initialize the Tracker

```python
from world.agent_investment_tracker import AgentInvestmentTracker

tracker = AgentInvestmentTracker()
```

### Step 2: Record Your First Cultivation

```python
# An agent works on a learning in a category
investment = tracker.record_cultivation(
    agent_name="secure-specialist",
    category="Security",
    impact=0.8,  # High impact work (0.0 - 1.0)
    learning_id="security-101",
    context="Implemented authentication security"
)

print(f"Level: {investment.level.name}")
print(f"Score: {investment.score}")
```

### Step 3: View Agent Portfolio

```python
# See all of an agent's investments
investments = tracker.get_agent_investments("secure-specialist")

for category, inv in investments.items():
    print(f"{category}: {inv.level.name} (Score: {inv.score:.1f})")
```

### Step 4: Find Experts

```python
from world.agent_investment_tracker import InvestmentLevel

# Find experts in a category
experts = tracker.get_category_experts(
    "Security",
    min_level=InvestmentLevel.PROFICIENT
)

for agent, investment in experts:
    print(f"{agent}: {investment.score:.1f}")
```

### Step 5: Get Recommendations

```python
# Find cultivation opportunities for an agent
available_learnings = [
    {
        'title': 'Advanced Security Patterns',
        'categories': ['Security', 'Programming'],
        'score': 0.8,
        'id': 'sec-advanced-001'
    }
]

opportunities = tracker.find_cultivation_opportunities(
    agent_name="secure-specialist",
    available_learnings=available_learnings,
    top_n=5
)

for opp in opportunities:
    print(f"{opp['title']}: {opp['cultivation_score']:.2f}")
```

---

## Common Use Cases

### Use Case 1: Task Assignment

```python
from world.agent_investment_tracker import get_top_agents_for_category

# Find the best agent for a security task
agents = get_top_agents_for_category("Security")
assigned_agent = agents[0]

print(f"Assign security task to: {assigned_agent}")
```

### Use Case 2: Track Agent Growth

```python
summary = tracker.get_investment_summary("engineer-master")

print(f"Total investments: {summary['total_investments']}")
print(f"Expertise levels: {summary['expertise_levels']}")
print(f"Most cultivated: {summary['most_cultivated']}")
```

### Use Case 3: Batch Recording

```python
from world.agent_investment_tracker import record_learning_work

# Record work across multiple categories
categories = ["Programming", "DevOps", "Tools"]
record_learning_work(
    agent_name="engineer-master",
    categories=categories,
    learning_id="api-implementation",
    impact=0.7
)
```

---

## Understanding Investment Levels

| Level | Score | What it Means |
|-------|-------|---------------|
| CURIOUS | 5-15 | Just starting to explore |
| LEARNING | 15-35 | Actively building skills |
| PRACTICING | 35-60 | Regular application |
| PROFICIENT | 60-85 | Strong competence |
| EXPERT | 85+ | Deep expertise |

---

## Next Steps

1. **Read the Full Documentation**: `AGENT_INVESTMENT_TRACKER_README.md`
2. **Run Examples**: `python3 example_investment_tracker.py`
3. **Explore Integration**: `python3 example_integration.py`
4. **Run Tests**: `python3 test_agent_investment_tracker.py`

---

## Tips

✅ **Record High-Impact Work**: Use 0.7-1.0 impact for significant contributions  
✅ **Regular Cultivation**: Consistent work is better than sporadic bursts  
✅ **Apply Decay**: Run `tracker.apply_decay()` periodically  
✅ **Check Opportunities**: Use cultivation opportunities for targeted growth  

---

## Need Help?

- **Documentation**: See `AGENT_INVESTMENT_TRACKER_README.md`
- **Examples**: Check `example_investment_tracker.py`
- **Tests**: Reference `test_agent_investment_tracker.py`

---

**Happy Cultivating! 🌱**

*Built with clean code principles by @organize-guru*
