# 🧠 Knowledge Graph Enhancements

**@investigate-champion** has enhanced the knowledge graph system with intelligent analysis, predictive capabilities, and deeper relationship tracking.

## 📋 Overview

The enhanced knowledge graph goes beyond basic code structure analysis to provide:

- **Pattern Recognition**: Identifies error patterns, refactoring history, and code evolution
- **Quality Metrics**: Calculates complexity scores and detects code smells
- **Predictive Intelligence**: Estimates bug likelihood and suggests expert agents
- **Technical Debt Analysis**: Identifies files needing attention
- **Optimization Opportunities**: Highlights areas for improvement

## 🚀 New Features

### 1. Enhanced Data Collection

#### Pattern Analysis
- **Error-Fix Patterns**: Tracks historical bugs and their classifications
  - Security vulnerabilities
  - Performance issues
  - Runtime errors
  - Test failures
  
- **Refactoring History**: Counts how many times files have been refactored
- **Complexity Metrics**: Calculates complexity scores based on:
  - Number of functions and classes
  - Lines of code
  - Import dependencies
  - Average function size

- **Code Smell Detection**: Identifies potential issues:
  - Large files (>500 lines)
  - Too many functions (>20)
  - God classes (>15 methods)
  - High coupling (excessive imports)

### 2. Predictive Intelligence

#### Bug Likelihood Prediction
Estimates the probability of bugs in a file based on:
- Complexity score
- Code smells
- File size
- Historical error patterns
- Refactoring frequency

Example:
```python
from knowledge_graph_query import KnowledgeGraphQuery

kgq = KnowledgeGraphQuery('docs/data/codebase-graph.json')
result = kgq.predict_bug_likelihood('tools/complex_module.py')

# Result:
# {
#   'likelihood': 'high',
#   'risk_score': 12,
#   'risk_factors': [
#     'High complexity (12.5)',
#     'Code smells detected: large_file, too_many_functions',
#     'Frequently refactored (5 times)',
#     'Historical errors (3 fixes)'
#   ],
#   'recommendation': '⚠️ High risk: Consider refactoring...'
# }
```

#### Expert Agent Suggestions
Recommends which agent should work on a file based on:
- Agents who previously worked on the file
- Agent expertise matching file characteristics
- File type and domain

Example:
```python
result = kgq.suggest_expert_agent('tools/workflow_analyzer.py')

# Result:
# {
#   'file': 'tools/workflow_analyzer.py',
#   'suggestions': [
#     {
#       'agent': 'investigate-champion',
#       'reason': 'Previously worked on this file',
#       'confidence': 'high',
#       'expertise': ['analysis', 'metrics', 'data-flows']
#     }
#   ]
# }
```

#### Technical Debt Identification
Finds files that need attention:
- Files with code smells
- High complexity without tests
- Error-prone files
- Large files without proper structure

Example:
```python
debt_files = kgq.identify_technical_debt(min_score=5)

# Returns list sorted by debt score:
# [
#   {
#     'file': 'tools/legacy_module.py',
#     'debt_score': 13,
#     'indicators': ['large_file', 'no_test_coverage', 'error_prone'],
#     'priority': 'high'
#   }
# ]
```

#### Optimization Opportunities
Identifies potential improvements:
- Large functions that could be split
- Files with too many functions
- High coupling that could be reduced
- Complex code needing simplification

### 3. Enhanced Querying

#### Natural Language Queries

The query interface now supports more natural questions:

```python
# Technical debt analysis
result = kgq.query("Show technical debt")
result = kgq.query("Find files with issues")

# Bug risk analysis
result = kgq.query("What is the bug likelihood for module.py?")

# Optimization
result = kgq.query("Show optimization opportunities")

# Existing queries still work
result = kgq.query("What imports utils.py?")
result = kgq.query("Which agent worked on test.py?")
result = kgq.query("Show impact of changes to api.py")
```

#### Programmatic API

All features are available programmatically:

```python
from knowledge_graph_query import KnowledgeGraphQuery

kgq = KnowledgeGraphQuery('docs/data/codebase-graph.json')

# Predictive intelligence
bug_risk = kgq.predict_bug_likelihood('file.py')
expert = kgq.suggest_expert_agent('file.py')
debt = kgq.identify_technical_debt()
opportunities = kgq.find_optimization_opportunities()

# Pattern and metric access
patterns = kgq.get_patterns()  # error_fixes, refactorings, code_smells
metrics = kgq.get_metrics()    # complexity data

# Existing features
impact = kgq.impact_analysis('file.py')
dependencies = kgq.find_dependencies('file.py')
```

### 4. Enhanced Visualization

The HTML visualization now shows:

**In Node Tooltips:**
- Complexity score
- Code smells (with ⚠️ warnings)
- Refactoring count (🔄)
- Standard metrics (functions, classes, lines)

**In Console Insights:**
- Most complex files
- Files with code smells
- Frequently refactored files
- Average complexity statistics

## 📊 Data Structure

The enhanced graph JSON now includes:

```json
{
  "metadata": { ... },
  "nodes": [
    {
      "id": "tools/module.py",
      "type": "code_file",
      "label": "module.py",
      "functions": 15,
      "classes": 2,
      "lines_of_code": 350,
      "complexity_score": 8.2,
      "avg_function_size": 23.3,
      "code_smells": ["large_file"],
      "quality_issues": 1,
      "refactoring_count": 3,
      ...
    }
  ],
  "relationships": [ ... ],
  "patterns": {
    "error_fixes": {
      "file.py": [
        {"type": "security", "date": "2025-11-10", "hash": "abc123"}
      ]
    },
    "refactorings": {
      "file.py": 5
    },
    "code_smells": {
      "file.py": ["large_file", "high_coupling"]
    }
  },
  "metrics": {
    "complexity": {
      "file.py": {
        "complexity_score": 12.5,
        "functions": 25,
        "avg_function_size": 24.0
      }
    }
  }
}
```

## 🎯 Use Cases

### Use Case 1: Pre-merge Impact Analysis
```python
# Before merging a PR that touches auth.py
impact = kgq.impact_analysis('auth.py')
bug_risk = kgq.predict_bug_likelihood('auth.py')

print(f"Blast radius: {impact['blast_radius']} files")
print(f"Bug risk: {bug_risk['likelihood']}")
print(f"Tests to run: {len(impact['tests_to_run'])}")
```

### Use Case 2: Issue Assignment
```python
# New issue about database performance
expert = kgq.suggest_expert_agent('database/query_optimizer.py')

# Assign to suggested agent
print(f"Assign to: {expert['suggestions'][0]['agent']}")
print(f"Reason: {expert['suggestions'][0]['reason']}")
```

### Use Case 3: Refactoring Planning
```python
# Identify technical debt
debt = kgq.identify_technical_debt(min_score=8)

print("Priority refactoring targets:")
for item in debt[:5]:
    print(f"  {item['file']}: {item['debt_score']} points")
    print(f"    Issues: {', '.join(item['indicators'])}")
```

### Use Case 4: Code Quality Dashboard
```python
# Generate quality report
stats = kgq.get_statistics()
patterns = kgq.get_patterns()
debt = kgq.identify_technical_debt()

print(f"Total files: {stats['total_nodes']}")
print(f"Files with issues: {len(patterns['code_smells'])}")
print(f"High-priority debt: {len([d for d in debt if d['priority']=='high'])}")
```

## 🔧 Command Line Usage

### Build Enhanced Graph
```bash
python tools/knowledge_graph_builder.py
```

### Query the Graph
```bash
# Show statistics
python tools/knowledge_graph_query.py --stats

# Query specific file
python tools/knowledge_graph_query.py --file tools/module.py

# Natural language query
python tools/knowledge_graph_query.py --query "Show technical debt"

# Interactive mode
python tools/knowledge_graph_query.py --interactive
```

## 🧪 Testing

All features are fully tested:

```bash
# Run builder tests
PYTHONPATH=tools python tests/test_knowledge_graph_builder.py

# Run query tests (includes predictive intelligence tests)
PYTHONPATH=tools python tests/test_knowledge_graph_query.py
```

## 📈 Performance

The enhanced analysis adds approximately:
- **Build time**: +10-20% (depends on repository size and git history)
- **Graph size**: +15-25% (additional metrics and patterns)
- **Query time**: Negligible (indices are pre-built)

Performance optimizations:
- Limits git history analysis to recent commits
- Processes only a subset of files for expensive operations
- Caches computed metrics
- Uses efficient data structures for queries

## 🎨 Visualization

Open the enhanced visualization:
```bash
# Generate graph first
python tools/knowledge_graph_builder.py

# Then open in browser
open docs/ai-knowledge-graph.html
# Navigate to "Codebase Graph" tab
```

Features:
- Hover over nodes to see complexity and quality metrics
- Code smells shown with ⚠️ warnings
- Refactoring history displayed
- Console shows detailed quality insights

## 🔮 Future Enhancements

Potential additions for the knowledge graph:

1. **Machine Learning Integration**
   - Train models on historical data to improve predictions
   - Cluster similar files using embeddings
   - Recommend refactoring patterns

2. **Real-time Updates**
   - Incremental graph updates on git commits
   - Live quality metrics during development
   - Continuous monitoring dashboard

3. **Cross-repository Analysis**
   - Compare patterns across multiple repositories
   - Identify best practices from successful projects
   - Learn from organizational patterns

4. **Enhanced Visualizations**
   - 3D graph visualization
   - Timeline view of code evolution
   - Heat maps for problem areas

5. **Integration Features**
   - GitHub Actions workflow integration
   - Pull request quality checks
   - Automated agent assignment

## 📚 References

- **Code Analysis**: Python AST module for static analysis
- **Git History**: Git log parsing for historical patterns
- **Complexity Metrics**: Based on cyclomatic complexity principles
- **Code Smells**: Inspired by Martin Fowler's refactoring patterns

## 🤝 Contributing

To extend the knowledge graph:

1. Add new analyzers in `knowledge_graph_builder.py`
2. Add new queries in `knowledge_graph_query.py`
3. Update tests to cover new features
4. Update visualization if needed

Example - adding a new analyzer:

```python
class SecurityAnalyzer:
    """Analyzes security patterns"""
    
    def analyze_security_patterns(self, files):
        # Your analysis logic
        return patterns
```

Then integrate in `KnowledgeGraphBuilder.build_graph()`.

---

**Built by @investigate-champion** with inspiration from Ada Lovelace's analytical approach to understanding complex systems. 🔍✨
