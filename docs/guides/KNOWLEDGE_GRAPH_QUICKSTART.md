# 🎯 Enhanced Knowledge Graph - Quick Start Guide

**@investigate-champion** has transformed the knowledge graph into an intelligent analysis system!

## 🚀 Quick Start

### 1. Generate the Enhanced Graph

```bash
cd /home/runner/work/Chained/Chained
python tools/knowledge_graph_builder.py
```

This will create `docs/data/codebase-graph.json` with all the intelligence built in.

### 2. Query the Graph

#### Interactive Mode (Recommended for Exploration)

```bash
python tools/knowledge_graph_query.py --interactive
```

Try these queries:
- `Show technical debt`
- `Show optimization opportunities`
- `What is the bug likelihood for tools/knowledge_graph_builder.py?`
- `Which agent worked on tools/code-analyzer.py?`
- `Show impact of tools/validation_utils.py`

#### Command Line Mode

```bash
# Show overall statistics
python tools/knowledge_graph_query.py --stats

# Analyze a specific file
python tools/knowledge_graph_query.py --file tools/knowledge_graph_builder.py

# Run a natural language query
python tools/knowledge_graph_query.py --query "Show technical debt"
```

### 3. View the Visualization

Open `docs/ai-knowledge-graph.html` in a browser and navigate to the "Codebase Graph" tab.

Hover over nodes to see:
- Complexity scores
- Code smells (⚠️)
- Refactoring history (🔄)
- Standard metrics

## 📋 Common Use Cases

### Pre-merge Quality Check

Before merging a PR:

```python
from knowledge_graph_query import KnowledgeGraphQuery

kgq = KnowledgeGraphQuery('docs/data/codebase-graph.json')

# Check file being changed
file = 'tools/my_module.py'

# Analyze impact
impact = kgq.impact_analysis(file)
print(f"Blast radius: {impact['blast_radius']} files")
print(f"Tests to run: {impact['tests_to_run']}")

# Check bug risk
risk = kgq.predict_bug_likelihood(file)
print(f"Bug likelihood: {risk['likelihood']}")
print(f"Risk factors: {risk['risk_factors']}")
```

### Assign Issue to Best Agent

When a new issue is created:

```python
file = 'database/query_optimizer.py'

# Get agent suggestion
expert = kgq.suggest_expert_agent(file)

print(f"Suggested agent: {expert['suggestions'][0]['agent']}")
print(f"Reason: {expert['suggestions'][0]['reason']}")
print(f"Confidence: {expert['suggestions'][0]['confidence']}")
```

### Identify Refactoring Priorities

Find files that need attention:

```python
# Get technical debt ranking
debt = kgq.identify_technical_debt(min_score=8)

print("High-priority refactoring targets:")
for item in debt[:5]:
    print(f"\n{item['file']}:")
    print(f"  Debt score: {item['debt_score']}")
    print(f"  Priority: {item['priority']}")
    print(f"  Issues: {', '.join(item['indicators'])}")
```

### Generate Quality Dashboard

Create a project health report:

```python
stats = kgq.get_statistics()
patterns = kgq.get_patterns()
debt = kgq.identify_technical_debt()
opportunities = kgq.find_optimization_opportunities()

print("📊 Code Quality Dashboard")
print(f"Total files: {stats['total_nodes']}")
print(f"Total functions: {stats['total_functions']}")
print(f"Files with code smells: {len(patterns['code_smells'])}")
print(f"High-priority debt: {len([d for d in debt if d['priority']=='high'])}")
print(f"Optimization opportunities: {len(opportunities)}")
```

## 🎨 What's New

### Pattern Recognition
- **Error patterns**: Tracks 6 types of historical bugs (security, performance, runtime, syntax, test, general)
- **Refactoring history**: Counts refactorings per file
- **Code evolution**: Understands how code changes over time

### Quality Metrics
- **Complexity scoring**: Mathematical formula based on functions, classes, LOC, imports
- **Code smell detection**: 4 types (large_file, too_many_functions, god_class, high_coupling)
- **Risk assessment**: Multi-factor analysis for bug likelihood

### Predictive Intelligence
- **Bug likelihood**: Estimates probability of bugs (low/medium/high)
- **Expert routing**: Suggests best agent for each file
- **Technical debt**: Identifies files needing attention with priority scores
- **Optimization**: Finds improvement opportunities

### Enhanced Queries
- Natural language support
- New query types: debt, optimization, risk, expert
- Existing queries still work (imports, tests, agents, impact)

## 📚 Learn More

- **Full Documentation**: `docs/KNOWLEDGE_GRAPH_ENHANCEMENTS.md`
- **Use Cases**: See examples in the documentation
- **API Reference**: Check function docstrings in `tools/knowledge_graph_query.py`

## 🧪 Testing

Run the test suite to verify everything works:

```bash
# Test the builder
PYTHONPATH=tools python tests/test_knowledge_graph_builder.py

# Test the query interface (includes predictive tests)
PYTHONPATH=tools python tests/test_knowledge_graph_query.py
```

Expected: **51 tests pass** (16 builder + 35 query)

## 🎯 Next Steps

1. **Generate the graph** for your repository
2. **Try interactive queries** to explore capabilities
3. **Integrate into workflows** for automated quality checks
4. **View the visualization** to see code relationships

---

**Built by @investigate-champion** 🔍✨

Following Ada Lovelace's analytical approach to understanding complex systems through data and patterns.
