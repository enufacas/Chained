# 🎯 Agent Learning Matcher

> Intelligent matching system connecting custom agents with relevant learning content

**Created by:** @investigate-champion  
**Version:** 1.0  
**Last Updated:** 2025-11-15

---

## 📋 Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Scoring Algorithm](#scoring-algorithm)
- [Extending the System](#extending-the-system)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Agent Learning Matcher is an intelligent system that connects the **44 specialized agents** in the Chained ecosystem with relevant learning content from multiple sources:

- 🔥 **Hacker News** - Community-driven tech discussions
- 📰 **TLDR Tech** - Curated tech news and trends
- 🌐 **GitHub Trending** - Popular repositories and projects
- 🛡️ **Security Analyses** - Security vulnerability reports
- 🔍 **Investigations** - Deep-dive technical analyses

### Key Features

✅ **Multi-Factor Scoring** - Combines category matching, keyword analysis, and agent affinity  
✅ **Semantic Understanding** - Categorizes content based on topics and keywords  
✅ **Bidirectional Matching** - Match agents to learnings OR learnings to agents  
✅ **Configurable** - Easily adjust weights, thresholds, and categories  
✅ **Extensible** - Add new agents, categories, or learning sources  
✅ **Performance Optimized** - Efficient keyword indexing and caching  

---

## How It Works

### 1. Learning Categorization

Each learning item is analyzed and categorized into one or more categories:

```
📚 Learning Categories:
  • AI_ML - AI, machine learning, LLMs, neural networks
  • Programming - Languages, frameworks, libraries
  • DevOps - CI/CD, containers, infrastructure automation
  • Database - SQL, NoSQL, data management
  • Web - Web development, APIs, browsers
  • Security - Vulnerabilities, encryption, authentication
  • Performance - Optimization, benchmarking, profiling
  • Tools - Developer tools, IDEs, productivity
  • OpenSource - Open source projects and community
  • Other - General tech insights
```

### 2. Agent Specialization Mapping

Each agent has defined specializations:

```python
{
  "agent_name": {
    "focus_areas": ["performance", "optimization"],
    "primary_categories": ["Performance", "Programming"],
    "secondary_categories": ["DevOps", "Database"],
    "keywords": ["benchmark", "profiling", "speed"],
    "learning_affinity_score": 0.95
  }
}
```

### 3. Scoring Algorithm

The matcher calculates relevance scores using multiple factors:

```
Final Score = (
  Category_Match_Score * weight
  + Keyword_Match_Score * weight  
  + Learning_Affinity * weight
  + Recency_Boost * weight
) * Source_Preference_Multiplier

Normalized to 0.0 - 1.0 range
```

**Scoring Factors:**

| Factor | Weight | Description |
|--------|--------|-------------|
| Primary Category Match | 1.0 | Learning matches agent's primary focus |
| Secondary Category Match | 0.5 | Learning matches agent's secondary areas |
| Keyword Match | 0.3 | Agent keywords found in learning content |
| Learning Affinity | 0.2 | Agent's general learning capability |
| Recency Boost | 0.15 | Newer learnings get slight boost |
| Source Preference | multiplier | Different sources weighted differently |

### 4. Relevance Thresholds

```
🌟 Perfect Match: 0.9+ - Highly relevant, agent should definitely see this
⭐ High Relevance: 0.7+ - Very relevant, strongly recommended
• Relevant: 0.3+ - Somewhat relevant, optional reading
```

---

## Quick Start

### Installation

```bash
cd /home/runner/work/Chained/Chained/world
```

The matcher is ready to use - no additional dependencies needed beyond Python 3.7+.

### Basic Usage

```python
from agent_learning_matcher import AgentLearningMatcher, load_all_learnings

# Initialize matcher
matcher = AgentLearningMatcher()

# Load learnings
learnings = load_all_learnings()

# Find learnings for an agent
matches = matcher.match_agent_to_learnings(
    agent_name="secure-specialist",
    learnings=learnings,
    max_results=10
)

# Print results
for match in matches:
    print(f"[{match['relevance_score']:.2f}] {match['title']}")
```

### Command Line Usage

```bash
# Match specific agent to all learnings
python agent_learning_matcher.py secure-specialist

# Output:
# 🔍 Agent Learning Matcher - @investigate-champion
# ✅ Loaded config with 44 agents
# ✅ Loaded 10 learning categories
# 
# 🤖 Finding learnings for agent: secure-specialist
# 📚 Loaded 434 total learnings
# 
# 🎯 Top 10 matches for @secure-specialist:
# 
# 🌟 1. [0.92] Disrupting AI-orchestrated cyber espionage
#    Categories: Security, AI_ML
#    Source: Hacker News
#    URL: https://www.anthropic.com/...
```

---

## Configuration

### Configuration File Structure

The matching system is configured via `agent_learning_matching_config.json`:

```json
{
  "learning_categories": {
    "Security": {
      "display_name": "Security & Privacy",
      "keywords": ["security", "vulnerability", "encryption", ...],
      "priority_weight": 1.3
    }
  },
  
  "agent_specializations": {
    "secure-specialist": {
      "focus_areas": ["security", "data integrity"],
      "primary_categories": ["Security", "Programming"],
      "keywords": ["vulnerability", "encryption", ...]
    }
  },
  
  "scoring_weights": {
    "category_match_primary": 1.0,
    "keyword_match": 0.3,
    ...
  }
}
```

### Adding a New Agent

1. Open `agent_learning_matching_config.json`
2. Add agent entry to `agent_specializations`:

```json
"my-new-agent": {
  "focus_areas": ["specific", "focus", "areas"],
  "primary_categories": ["Primary", "Categories"],
  "secondary_categories": ["Secondary", "Categories"],
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "learning_affinity_score": 0.85
}
```

### Adding a New Category

1. Add to `learning_categories`:

```json
"MyNewCategory": {
  "display_name": "My New Category",
  "keywords": ["keyword1", "keyword2", ...],
  "file_patterns": ["MyNewCategory.md"],
  "priority_weight": 1.0
}
```

2. Update agents to reference the new category

### Tuning Scoring Weights

Adjust weights in the `scoring_weights` section:

```json
"scoring_weights": {
  "category_match_primary": 1.0,      // Higher = categories matter more
  "category_match_secondary": 0.5,
  "keyword_match": 0.3,               // Higher = keywords matter more
  "learning_affinity": 0.2,
  "recency_boost": 0.15,              // Higher = prefer newer content
  "source_preference": {
    "hn": 1.0,
    "security_analysis": 1.1          // Security analyses weighted higher
  }
}
```

---

## API Reference

### Class: `AgentLearningMatcher`

Main matching engine.

#### `__init__(config_path=None)`

Initialize the matcher.

**Args:**
- `config_path` (str, optional): Path to config JSON. Default: auto-detect

**Example:**
```python
matcher = AgentLearningMatcher()
# or
matcher = AgentLearningMatcher("/path/to/custom/config.json")
```

#### `match_agent_to_learnings(agent_name, learnings, max_results=10, min_score=None)`

Find relevant learnings for an agent.

**Args:**
- `agent_name` (str): Agent identifier (e.g., "secure-specialist")
- `learnings` (List[Dict]): List of learning dictionaries
- `max_results` (int): Maximum matches to return (default: 10)
- `min_score` (float, optional): Minimum relevance score (default: 0.3)

**Returns:**
List[Dict] with added `relevance_score` and `matched_categories` fields

**Example:**
```python
matches = matcher.match_agent_to_learnings(
    "accelerate-master",
    learnings,
    max_results=5,
    min_score=0.7
)
```

#### `match_learning_to_agents(learning, agent_names=None, max_results=5, min_score=None)`

Find suitable agents for a learning item.

**Args:**
- `learning` (Dict): Learning dictionary
- `agent_names` (List[str], optional): Agents to consider (default: all)
- `max_results` (int): Maximum matches to return (default: 5)
- `min_score` (float, optional): Minimum relevance score (default: 0.3)

**Returns:**
List[(agent_name, score)] tuples, sorted by score

**Example:**
```python
best_agents = matcher.match_learning_to_agents(
    learning=my_learning,
    max_results=3,
    min_score=0.7
)
# Returns: [("secure-specialist", 0.92), ("monitor-champion", 0.85), ...]
```

#### `get_agent_learning_summary(agent_name, learnings)`

Get comprehensive statistics about agent-learning matches.

**Args:**
- `agent_name` (str): Agent identifier
- `learnings` (List[Dict]): All available learnings

**Returns:**
Dict with statistics:
```python
{
  'agent_name': 'secure-specialist',
  'total_relevant': 123,
  'high_relevance': 45,
  'perfect_matches': 12,
  'top_categories': ['Security', 'Web', 'Programming'],
  'top_sources': ['Hacker News', 'TLDR'],
  'average_score': 0.68
}
```

#### `suggest_learning_distribution(learnings, max_agents_per_learning=3)`

Suggest optimal distribution of learnings to agents.

**Args:**
- `learnings` (List[Dict]): All learnings to distribute
- `max_agents_per_learning` (int): Max agents per learning (default: 3)

**Returns:**
Dict mapping agent_name -> list of learning assignments

**Example:**
```python
distribution = matcher.suggest_learning_distribution(learnings)
# Returns:
# {
#   "secure-specialist": [
#     {"learning_id": 1, "title": "...", "score": 0.92},
#     {"learning_id": 5, "title": "...", "score": 0.87}
#   ],
#   "accelerate-master": [...]
# }
```

### Utility Functions

#### `load_learnings_from_file(filepath)`

Load learnings from a single JSON file.

**Args:**
- `filepath` (str): Path to JSON file

**Returns:**
List[Dict] of learnings

#### `load_all_learnings(learnings_dir=None)`

Load all learnings from the learnings directory.

**Args:**
- `learnings_dir` (str, optional): Directory path (default: auto-detect)

**Returns:**
List[Dict] of all learnings from all JSON files

---

## Usage Examples

### Example 1: Find Security Learnings for Security Agents

```python
from agent_learning_matcher import AgentLearningMatcher, load_all_learnings

matcher = AgentLearningMatcher()
learnings = load_all_learnings()

# Get security learnings for all security-focused agents
security_agents = [
    "secure-specialist",
    "secure-ninja", 
    "secure-pro",
    "monitor-champion"
]

for agent in security_agents:
    matches = matcher.match_agent_to_learnings(
        agent,
        learnings,
        max_results=5,
        min_score=0.8  # Only high-relevance matches
    )
    
    print(f"\n🛡️ Top security learnings for @{agent}:")
    for match in matches:
        print(f"  [{match['relevance_score']:.2f}] {match['title']}")
```

### Example 2: Distribute New Learning to Appropriate Agents

```python
# New learning just arrived
new_learning = {
    "title": "New Zero-Day Vulnerability in Popular Framework",
    "description": "Critical security flaw discovered...",
    "source": "Hacker News",
    "url": "https://...",
    "timestamp": "2025-11-15T10:00:00Z"
}

# Find best agents for this learning
best_agents = matcher.match_learning_to_agents(
    new_learning,
    max_results=5,
    min_score=0.7
)

print("📢 Notify these agents:")
for agent_name, score in best_agents:
    print(f"  @{agent_name} (relevance: {score:.2f})")
```

### Example 3: Generate Agent Learning Report

```python
# Generate comprehensive report for an agent
agent_name = "investigate-champion"
summary = matcher.get_agent_learning_summary(agent_name, learnings)

print(f"📊 Learning Report for @{agent_name}")
print(f"=" * 60)
print(f"Total Relevant Learnings: {summary['total_relevant']}")
print(f"High Relevance: {summary['high_relevance']}")
print(f"Perfect Matches: {summary['perfect_matches']}")
print(f"Average Relevance: {summary['average_score']:.2f}")
print(f"\nTop Categories:")
for i, cat in enumerate(summary['top_categories'], 1):
    print(f"  {i}. {cat}")
print(f"\nTop Sources:")
for i, src in enumerate(summary['top_sources'], 1):
    print(f"  {i}. {src}")
```

### Example 4: Filter Learnings by Category

```python
# Get all AI/ML learnings for pioneer agents
ai_agents = ["pioneer-pro", "pioneer-sage", "meta-coordinator"]

for agent in ai_agents:
    matches = matcher.match_agent_to_learnings(agent, learnings)
    
    # Filter for AI/ML category
    ai_ml_matches = [
        m for m in matches 
        if "AI_ML" in m.get('matched_categories', [])
    ]
    
    print(f"\n🤖 AI/ML learnings for @{agent}: {len(ai_ml_matches)}")
```

### Example 5: Batch Processing New Learnings

```python
import json
from pathlib import Path

# Process all new learnings from a directory
new_learnings_dir = Path("learnings/new")
matcher = AgentLearningMatcher()

assignments = {}

for learning_file in new_learnings_dir.glob("*.json"):
    with open(learning_file) as f:
        learnings = json.load(f)
    
    for learning in learnings:
        # Find top 3 agents for each learning
        agents = matcher.match_learning_to_agents(
            learning,
            max_results=3,
            min_score=0.7
        )
        
        for agent_name, score in agents:
            if agent_name not in assignments:
                assignments[agent_name] = []
            assignments[agent_name].append({
                'title': learning['title'],
                'score': score,
                'file': learning_file.name
            })

# Save assignments
with open('agent_learning_assignments.json', 'w') as f:
    json.dump(assignments, f, indent=2)
```

---

## Scoring Algorithm

### Detailed Breakdown

The scoring algorithm uses a weighted combination of multiple factors:

#### 1. Category Matching (60% of base score)

```python
# Primary categories: full weight (1.0)
for category in agent.primary_categories:
    if category in learning.categories:
        score += 1.0 * learning.category_score[category]

# Secondary categories: half weight (0.5)
for category in agent.secondary_categories:
    if category in learning.categories:
        score += 0.5 * learning.category_score[category]
```

**Example:**
- Learning categorized as: Security (0.8), Programming (0.5)
- Agent primary: [Security, Programming]
- Score += (1.0 * 0.8) + (1.0 * 0.5) = 1.3

#### 2. Keyword Matching (30% of base score)

```python
agent_keywords = {"security", "vulnerability", "encryption"}
learning_text = "New security vulnerability discovered..."
learning_keywords = {"new", "security", "vulnerability", "discovered"}

matches = agent_keywords & learning_keywords  # {"security", "vulnerability"}
keyword_score = len(matches) / len(agent_keywords)  # 2/3 = 0.67
score += 0.3 * keyword_score
```

#### 3. Learning Affinity (20% of base score)

Each agent has an inherent learning affinity score (0.0-1.0) representing how well they process and apply learnings:

- **High affinity (0.9+)**: Agents like `investigate-champion`, `accelerate-master`
- **Medium affinity (0.85-0.89)**: Most specialized agents
- **Lower affinity (0.75-0.84)**: Highly focused agents with narrow scope

```python
score += 0.2 * agent.learning_affinity_score
```

#### 4. Recency Boost (15% of base score)

Newer learnings get a boost to ensure agents see fresh content:

```python
age_days = (now - learning.timestamp).days
recency_factor = max(0.1, 1.0 / (1 + age_days / 7))
score += 0.15 * recency_factor

# Examples:
# 0 days old: recency = 1.0 (full boost)
# 7 days old: recency = 0.5 (half boost)
# 14 days old: recency = 0.33
# 30+ days old: recency ≈ 0.1 (minimal boost)
```

#### 5. Source Preference (multiplier)

Different learning sources are weighted based on quality and relevance:

```python
source_multipliers = {
    "security_analysis": 1.1,    # Security analyses prioritized
    "investigation": 1.05,       # Investigations valued
    "hn": 1.0,                   # Hacker News baseline
    "github_trending": 0.95,     # GitHub trending slightly lower
    "tldr": 0.9                  # TLDR compact format
}

final_score = base_score * source_multiplier
```

### Normalization

Final scores are normalized to 0.0-1.0 range:

```python
# Theoretical max score ≈ 2.5 (all factors maxed + multipliers)
normalized_score = min(raw_score / 2.5, 1.0)
```

### Score Interpretation

| Range | Meaning | Action |
|-------|---------|--------|
| 0.9 - 1.0 | 🌟 Perfect Match | Must-read for this agent |
| 0.7 - 0.89 | ⭐ High Relevance | Strongly recommended |
| 0.5 - 0.69 | • Relevant | Good optional reading |
| 0.3 - 0.49 | • Somewhat Relevant | Consider if time permits |
| 0.0 - 0.29 | (not shown) | Not recommended |

---

## Extending the System

### Adding a New Learning Source

1. **Create a loader function:**

```python
def load_my_source_learnings(filepath):
    """Load learnings from my custom source."""
    with open(filepath) as f:
        data = json.load(f)
    
    learnings = []
    for item in data['items']:
        learnings.append({
            'title': item['headline'],
            'description': item['summary'],
            'source': 'My Custom Source',
            'url': item['link'],
            'timestamp': item['date']
        })
    return learnings
```

2. **Add source preference to config:**

```json
"source_preference": {
  "my_custom_source": 1.05
}
```

3. **Use in matching:**

```python
custom_learnings = load_my_source_learnings('data.json')
all_learnings = load_all_learnings() + custom_learnings
matches = matcher.match_agent_to_learnings(agent_name, all_learnings)
```

### Adding Custom Scoring Factors

Extend the `_score_match` method:

```python
class CustomMatcher(AgentLearningMatcher):
    def _score_match(self, agent_name, learning, categories, recency):
        # Get base score
        score = super()._score_match(agent_name, learning, categories, recency)
        
        # Add custom factor: sentiment analysis
        sentiment = self._analyze_sentiment(learning['description'])
        if sentiment == 'positive':
            score *= 1.1  # Boost positive content
        
        # Add custom factor: length preference
        word_count = len(learning['description'].split())
        if 100 <= word_count <= 500:  # Sweet spot
            score += 0.05
        
        return score
```

### Creating Agent Learning Profiles

Build learning profiles over time:

```python
class AgentLearningProfile:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.viewed_learnings = []
        self.feedback_scores = {}  # learning_id -> usefulness (0-1)
    
    def record_view(self, learning_id):
        self.viewed_learnings.append(learning_id)
    
    def record_feedback(self, learning_id, usefulness):
        self.feedback_scores[learning_id] = usefulness
    
    def adjust_preferences(self, matcher):
        """Adjust agent preferences based on feedback."""
        # Analyze which categories got best feedback
        category_scores = defaultdict(list)
        
        for learning_id, score in self.feedback_scores.items():
            learning = self._get_learning(learning_id)
            for category in learning['matched_categories']:
                category_scores[category].append(score)
        
        # Update agent config based on performance
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score > 0.8:
                # This category is valuable, boost it
                pass  # Implement preference adjustment
```

---

## Troubleshooting

### Issue: Low Match Scores

**Symptoms:** All matches have scores < 0.5

**Solutions:**
1. Check if agent keywords match learning content
2. Verify agent categories are properly configured
3. Adjust scoring weights to emphasize different factors
4. Ensure learning content has sufficient text for analysis

### Issue: Too Many Irrelevant Matches

**Symptoms:** High-scoring matches aren't actually relevant

**Solutions:**
1. Increase `min_score` threshold
2. Add more specific keywords to agent configuration
3. Adjust category weights (lower secondary category weight)
4. Review and refine learning categorization

### Issue: Agent Gets No Matches

**Symptoms:** `match_agent_to_learnings` returns empty list

**Solutions:**
1. Verify agent name is spelled correctly
2. Check if agent exists in config
3. Lower `min_score` parameter
4. Ensure learnings list is not empty
5. Check that agent has keywords and categories defined

### Issue: Learning Not Categorized

**Symptoms:** Learning gets "Other" category or no category

**Solutions:**
1. Add more keywords to relevant categories
2. Check learning has title/description text
3. Verify category keywords are comprehensive
4. Manually review learning content

### Issue: Performance Slow with Many Learnings

**Symptoms:** Matching takes too long

**Solutions:**
1. Filter learnings by recency before matching
2. Implement caching for categorization
3. Pre-categorize learnings and save results
4. Use multiprocessing for batch operations

```python
# Example: Pre-cache categorizations
categorization_cache = {}

def get_categories(learning):
    learning_id = learning.get('id', learning['title'])
    if learning_id not in categorization_cache:
        categorization_cache[learning_id] = matcher._categorize_learning(learning)
    return categorization_cache[learning_id]
```

### Debug Mode

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('agent_learning_matcher')

# In matcher code, add:
logger.debug(f"Categorized {learning['title']}: {categories}")
logger.debug(f"Agent {agent_name} score: {score}")
```

---

## Best Practices

### 1. Regular Configuration Updates

- Review and update agent specializations quarterly
- Add new keywords based on emerging trends
- Adjust weights based on matching effectiveness

### 2. Validate Matches

- Periodically review top matches manually
- Collect feedback on match quality
- Use feedback to tune the system

### 3. Balanced Distribution

- Use `suggest_learning_distribution()` for fair assignment
- Ensure no agent is overwhelmed or starved
- Consider agent capacity and expertise

### 4. Monitor Performance

```python
# Track matching statistics
stats = {
    'total_learnings': len(learnings),
    'matched_learnings': len([l for l in learnings if has_match(l)]),
    'average_matches_per_agent': calculate_average(),
    'coverage_by_category': category_coverage()
}
```

### 5. Documentation

- Document custom agents thoroughly
- Maintain changelog for configuration updates
- Share insights from matching patterns

---

## Contributing

To contribute improvements to the Agent Learning Matcher:

1. Test changes thoroughly with real data
2. Validate that scoring remains balanced
3. Update configuration schema if needed
4. Document any new features
5. Add usage examples

---

## Appendix: Full Example Workflow

```python
#!/usr/bin/env python3
"""
Complete workflow: Load learnings, match to agents, generate report
"""
from agent_learning_matcher import (
    AgentLearningMatcher,
    load_all_learnings
)
import json

# Initialize
print("🔍 Initializing Agent Learning Matcher...")
matcher = AgentLearningMatcher()

# Load all learnings
print("📚 Loading learnings...")
learnings = load_all_learnings()
print(f"✅ Loaded {len(learnings)} learnings")

# Analyze learnings distribution
print("\n📊 Learning Distribution:")
sources = {}
for learning in learnings:
    source = learning.get('source', 'Unknown')
    sources[source] = sources.get(source, 0) + 1

for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
    print(f"  • {source}: {count}")

# Generate reports for top agents
top_agents = [
    "secure-specialist",
    "accelerate-master",
    "investigate-champion",
    "create-guru",
    "engineer-master"
]

print("\n🎯 Generating Agent Reports...")
reports = {}

for agent in top_agents:
    summary = matcher.get_agent_learning_summary(agent, learnings)
    matches = matcher.match_agent_to_learnings(agent, learnings, max_results=5)
    
    reports[agent] = {
        'summary': summary,
        'top_matches': [
            {
                'title': m['title'],
                'score': m['relevance_score'],
                'categories': m['matched_categories']
            }
            for m in matches
        ]
    }
    
    print(f"\n📝 @{agent}")
    print(f"  Relevant: {summary['total_relevant']}")
    print(f"  High Relevance: {summary['high_relevance']}")
    print(f"  Perfect: {summary['perfect_matches']}")
    print(f"  Avg Score: {summary['average_score']:.2f}")
    print(f"  Top Categories: {', '.join(summary['top_categories'][:3])}")

# Save reports
with open('agent_learning_reports.json', 'w') as f:
    json.dump(reports, f, indent=2)

print("\n✅ Reports saved to agent_learning_reports.json")

# Distribution suggestion
print("\n🎪 Suggesting optimal learning distribution...")
distribution = matcher.suggest_learning_distribution(learnings)

print(f"\nLearnings distributed to {len(distribution)} agents")
for agent, assigned in sorted(distribution.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
    print(f"  • @{agent}: {len(assigned)} learnings")

print("\n✨ Analysis complete!")
```

---

**🔍 Built with analytical precision by @investigate-champion**  
*"Understanding patterns, connecting knowledge, illuminating insights"*
