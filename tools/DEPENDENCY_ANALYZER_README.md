# 🔍 Dependency & Data Flow Analyzer

**Created by**: Liskov (Ada Lovelace), Investigate Champion  
**Purpose**: Illuminate the invisible architecture of autonomous systems  
**Status**: Production Ready ✅

## Overview

The Dependency & Data Flow Analyzer is a sophisticated analytical tool that investigates and visualizes the complex relationships within the Chained autonomous agent system. It provides deep insights into:

- **Code Dependencies**: Python module import graphs and relationships
- **Workflow Orchestration**: GitHub Actions workflow triggers and execution patterns
- **Data Flows**: How information moves through the system
- **Bottlenecks**: Performance and maintainability issues
- **Recommendations**: Actionable insights for system improvement

## Features

### 🔬 Deep Analysis Capabilities

1. **Python Module Dependency Graph**
   - Extracts import relationships using AST parsing
   - Identifies high-dependency modules (potential bottlenecks)
   - Calculates module centrality and popularity metrics
   - Detects circular dependencies

2. **Workflow Orchestration Mapping**
   - Parses GitHub Actions YAML workflows
   - Identifies trigger patterns (schedule, manual, event-based)
   - Maps workflow dependencies and tool calls
   - Tracks secret usage across workflows

3. **Data Flow Tracing**
   - Traces metrics collection flows
   - Maps event-driven interactions
   - Tracks data storage patterns
   - Identifies information bottlenecks

4. **Bottleneck Identification**
   - Detects high-complexity workflows
   - Identifies tightly-coupled modules
   - Finds circular dependencies
   - Highlights maintenance risks

5. **Smart Recommendations**
   - Generates actionable improvement suggestions
   - Prioritizes by impact and severity
   - Provides context-aware guidance
   - Supports evolutionary architecture

## Usage

### Basic Analysis

```bash
# Run analysis on current directory
cd /path/to/Chained
python3 tools/dependency-flow-analyzer.py

# Specify repository location
python3 tools/dependency-flow-analyzer.py --repo /path/to/repo

# Verbose output with detailed bottleneck analysis
python3 tools/dependency-flow-analyzer.py --verbose
```

### Output Formats

```bash
# Text output to console (default)
python3 tools/dependency-flow-analyzer.py --format text

# JSON output to file
python3 tools/dependency-flow-analyzer.py --format json --output report.json

# Both text and JSON
python3 tools/dependency-flow-analyzer.py --format both --output report.json
```

### Integration with CI/CD

```yaml
# Add to GitHub Actions workflow
- name: Analyze Dependencies
  run: |
    python3 tools/dependency-flow-analyzer.py \
      --format json \
      --output analysis/dependency-report.json

- name: Upload Analysis
  uses: actions/upload-artifact@v3
  with:
    name: dependency-analysis
    path: analysis/dependency-report.json
```

## Output Structure

### Text Report

```
================================================================================
📊 ANALYSIS SUMMARY
================================================================================

🐍 Python Modules:
  Total modules:         74
  Avg dependencies:      6.9
  Avg lines of code:     297

⚙️  Workflows:
  Total workflows:       28
  Scheduled:             19
  Manual dispatch:       28
  Event triggered:       26

🌊 Data Flows:
  Total flows:           35
    metrics              4
    event                29
    secret               2

⚠️  Bottlenecks:
  Total identified:      7

💡 RECOMMENDATIONS:
  1. Consider refactoring high-dependency modules...
  2. Break complex workflows into smaller components...
```

### JSON Report Structure

```json
{
  "timestamp": "2025-11-12T15:26:50.054862",
  "summary": {
    "modules": {
      "total": 74,
      "avg_dependencies": 6.9,
      "avg_lines": 297
    },
    "workflows": {
      "total": 28,
      "scheduled": 19
    },
    "data_flows": {
      "total": 35,
      "by_type": {
        "metrics": 4,
        "event": 29
      }
    },
    "bottlenecks": {
      "total": 7,
      "by_severity": {
        "low": 7
      }
    }
  },
  "dependency_graph": {
    "module-name": {
      "name": "module-name",
      "type": "module",
      "dependencies": ["dep1", "dep2"],
      "dependents": ["user1"],
      "metrics": {
        "lines_of_code": 297,
        "popularity": 3
      }
    }
  },
  "data_flows": [
    {
      "source": "GitHub API",
      "destination": "agent-metrics-collector.py",
      "data_type": "metrics",
      "intermediate_nodes": ["github_integration.py"]
    }
  ],
  "bottlenecks": [
    {
      "type": "complex_workflow",
      "severity": "low",
      "component": "system-monitor",
      "description": "Workflow has 25 steps",
      "impact": "May be slow to execute"
    }
  ],
  "recommendations": [
    "Consider breaking complex workflows into smaller components..."
  ]
}
```

## Analysis Methodology

### Dependency Graph Construction

The analyzer uses Python's `ast` module to parse source files without executing them:

1. **Import Extraction**: Identifies all `import` and `from ... import` statements
2. **Normalization**: Converts module names to consistent format (handles hyphens vs underscores)
3. **Graph Building**: Constructs bidirectional dependency relationships
4. **Metric Calculation**: Computes popularity, centrality, and complexity metrics

### Workflow Orchestration Analysis

Workflows are analyzed through pattern matching and YAML parsing:

1. **Trigger Detection**: Identifies schedule patterns, manual triggers, and event-based activation
2. **Tool Extraction**: Finds Python scripts called by workflows
3. **Secret Tracking**: Maps secret usage across the system
4. **Complexity Metrics**: Counts jobs, steps, and dependencies

### Data Flow Tracing

Data flows are traced through multiple analysis passes:

1. **Source Identification**: Locates data entry points (APIs, user input, storage)
2. **Path Tracing**: Follows data through processing pipelines
3. **Destination Mapping**: Identifies storage and output locations
4. **Intermediate Nodes**: Tracks transformations and processing steps

### Bottleneck Detection

Multiple heuristics identify potential issues:

1. **High Dependency**: Modules used by 4+ other modules
2. **High Complexity**: Workflows with 10+ steps
3. **Circular Dependencies**: Detected through DFS graph traversal
4. **Tight Coupling**: Components with high bidirectional dependencies

## Interpreting Results

### Severity Levels

- 🔴 **High**: Critical issues requiring immediate attention
- 🟡 **Medium**: Important issues affecting maintainability
- 🟢 **Low**: Minor issues or optimization opportunities

### Bottleneck Types

1. **high_dependency_module**: Module used by many others
   - **Impact**: Changes affect many components
   - **Solution**: Extract interfaces, use dependency injection

2. **complex_workflow**: Workflow with many steps
   - **Impact**: Slow execution, hard to maintain
   - **Solution**: Break into smaller workflows or composite actions

3. **circular_dependency**: Circular import relationship
   - **Impact**: Import failures, hard to refactor
   - **Solution**: Restructure modules, extract shared dependencies

## Use Cases

### 1. Architecture Review

Regularly run the analyzer to understand system evolution:

```bash
# Generate monthly architecture reports
python3 tools/dependency-flow-analyzer.py \
  --output reports/arch-$(date +%Y-%m).json \
  --format both \
  --verbose
```

### 2. Pre-Refactoring Analysis

Before major refactoring, understand current dependencies:

```bash
python3 tools/dependency-flow-analyzer.py --verbose > pre-refactor-analysis.txt
# Review bottlenecks and high-dependency modules
# Plan refactoring to reduce coupling
```

### 3. Onboarding New Contributors

Help new team members understand the codebase:

```bash
python3 tools/dependency-flow-analyzer.py --format json --output docs/architecture.json
# Share JSON with visualization tools
# Review data flows and module relationships
```

### 4. CI/CD Health Monitoring

Track architectural metrics over time:

```bash
# In CI workflow
python3 tools/dependency-flow-analyzer.py \
  --format json \
  --output metrics/dependency-metrics-${{ github.run_id }}.json

# Track metrics trends:
# - Average module dependencies (should decrease)
# - Circular dependencies (should be zero)
# - Workflow complexity (should be moderate)
```

## Advanced Features

### Custom Metrics

The analyzer calculates several derived metrics:

- **Module Popularity**: Number of modules that depend on this one
- **Module Centrality**: Sum of dependencies + dependents (hub score)
- **Workflow Complexity**: Steps × Jobs × Tools Called
- **Data Flow Density**: Flows per component

### Extensibility

The analyzer is designed for extension:

```python
from dependency_flow_analyzer import DependencyAnalyzer

# Custom analysis
analyzer = DependencyAnalyzer('/path/to/repo')
report = analyzer.run_full_analysis()

# Access raw data
for module_name, node in report.dependency_graph.items():
    if node.type == 'module':
        print(f"{module_name}: {len(node.dependents)} users")

# Custom bottleneck detection
custom_bottlenecks = [
    node for node in report.dependency_graph.values()
    if node.metrics.get('lines_of_code', 0) > 500
]
```

## Performance

- **Typical Analysis Time**: 2-5 seconds for Chained repository
- **Memory Usage**: < 100MB for large repositories
- **Scalability**: Tested with 100+ modules and workflows

## Limitations

1. **Static Analysis Only**: Cannot detect runtime dependencies
2. **Python Focus**: Only analyzes Python code (not JavaScript, Go, etc.)
3. **Workflow Parsing**: Uses pattern matching, not full YAML parsing
4. **No Cross-Repo**: Analyzes single repository at a time

## Future Enhancements

- 📊 **Visualization**: Generate interactive dependency graphs
- 🔄 **Trend Analysis**: Track metrics over time
- 🔗 **Cross-Repo**: Analyze dependencies across multiple repositories
- 🎯 **Impact Analysis**: Predict refactoring impact
- 🤖 **Auto-Fix**: Suggest and apply automated fixes

## Contributing

Improvements welcome! Key areas:

1. Additional bottleneck detection heuristics
2. Better circular dependency resolution algorithms
3. Enhanced data flow tracing
4. Visualization generation
5. Performance optimizations

## Testing

Comprehensive test suite included:

```bash
# Run all tests
python3 tools/test_dependency_flow_analyzer.py

# Expected output: 12 tests, all passing
```

Tests cover:
- Dataclass creation and serialization
- Dependency graph construction
- Workflow parsing
- Data flow tracing
- Bottleneck detection
- Report generation
- Edge cases and error handling

## Inspiration

> "The Analytical Engine has no pretensions whatever to originate anything. It can do whatever we know how to order it to perform." - Ada Lovelace

This tool embodies Ada's vision: not just executing commands, but revealing patterns and insights that help us understand and improve our systems.

---

**Created with analytical rigor and occasional wit by Liskov (Ada Lovelace)**  
*Investigate Champion • Pattern Detective • Architecture Illuminator*
