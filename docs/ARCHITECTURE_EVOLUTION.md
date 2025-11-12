# 🏗️ Architecture Evolution System

**Automated tracking and visualization of the Chained ecosystem's architectural changes over time**

## Overview

The Architecture Evolution System is a comprehensive solution for monitoring how the Chained codebase structure evolves. It automatically analyzes the repository, tracks changes, and generates visual diagrams to help understand the system's growth and transformation.

## Features

### 1. **Automated Architecture Analysis** 🔍
- Tracks directory structure and file organization
- Analyzes Python module dependencies and imports
- Monitors component growth and complexity
- Calculates architectural metrics (coupling, complexity)

### 2. **Historical Tracking** 📊
- Maintains snapshots of architecture at each significant change
- Tracks metrics over time
- Compares current state with previous snapshots
- Stores up to 100 historical snapshots

### 3. **Visual Diagrams** 🎨
- Generates Mermaid diagrams for documentation
- Creates interactive D3.js visualizations
- Displays evolution timeline with metrics
- Shows component distribution and relationships

### 4. **GitHub Integration** 🤖
- Runs automatically on PR merges to main
- Commits architecture data to the repository
- Posts summaries to PR comments
- Publishes to GitHub Pages dashboard

## Components

### Core Tool: `tools/architecture-tracker.py`

A Python tool that analyzes the repository and generates architecture data.

**Usage:**
```bash
# Basic analysis
python3 tools/architecture-tracker.py

# With comparison to previous snapshot
python3 tools/architecture-tracker.py --compare

# Generate Mermaid diagram
python3 tools/architecture-tracker.py --mermaid

# Custom output directory
python3 tools/architecture-tracker.py --output-dir custom/path

# Output as JSON
python3 tools/architecture-tracker.py --json
```

**Command-line Options:**
- `--repo-path PATH`: Path to repository (default: current directory)
- `--output-dir DIR`: Output directory for snapshots (default: analysis/architecture)
- `--compare`: Compare with previous snapshot
- `--mermaid`: Generate Mermaid diagram
- `--json`: Output results as JSON

### Visualization: `docs/architecture-evolution.html`

An interactive web-based dashboard displaying architecture evolution.

**Features:**
- Real-time metrics display
- Interactive timeline chart showing file/line/component growth
- Component distribution bar chart
- Live Mermaid architecture diagram
- Responsive design with dark theme

**Access:**
Visit [https://enufacas.github.io/Chained/architecture-evolution.html](https://enufacas.github.io/Chained/architecture-evolution.html)

### Workflow: `.github/workflows/architecture-evolution.yml`

GitHub Actions workflow that automates tracking.

**Triggers:**
- On push to main branch
- On PR merge to main
- Manual workflow dispatch

**Actions:**
1. Runs architecture analysis
2. Generates comparison with previous snapshot
3. Creates Mermaid diagram
4. Copies data to GitHub Pages
5. Commits results to repository
6. Posts summary to PR (if applicable)

## Data Format

### Snapshot Structure (`latest.json`)

```json
{
  "timestamp": "2025-11-12T06:36:48.122Z",
  "commit": "abc123...",
  "structure": {
    "directories": {
      "tools": {
        "file_count": 45,
        "line_count": 12500,
        "files": ["tool1.py", "tool2.py", ...]
      },
      ...
    },
    "total_files": 150,
    "total_lines": 50000
  },
  "dependencies": {
    "internal_imports": {
      "module1.py": ["module2", "module3"],
      ...
    },
    "external_imports": {
      "requests": 15,
      "json": 30,
      ...
    },
    "module_graph": [
      {"source": "module1.py", "target": "module2.py", "type": "imports"}
    ]
  },
  "metrics": {
    "total_components": 6,
    "total_files": 150,
    "total_lines": 50000,
    "total_dependencies": 45,
    "external_libraries": 5,
    "coupling_score": 0.35,
    "complexity_score": 0.42
  },
  "components": {
    "learning_system": {
      "file_count": 12,
      "line_count": 5000,
      "files": [...]
    },
    ...
  }
}
```

### Evolution History (`evolution.json`)

```json
{
  "snapshots": [
    {
      "timestamp": "2025-11-12T06:36:48.122Z",
      "commit": "abc123...",
      "commit_message": "Add new feature",
      "metrics": {...},
      "component_count": 6,
      "file_count": 150
    },
    ...
  ]
}
```

## Metrics Explained

### Coupling Score (0-1)
Measures how interconnected modules are. Lower is better.
- **0.0-0.3**: Low coupling (good)
- **0.3-0.6**: Moderate coupling (acceptable)
- **0.6-1.0**: High coupling (consider refactoring)

### Complexity Score (0-1)
Measures average code complexity. Normalized by lines per file.
- **0.0-0.3**: Low complexity (maintainable)
- **0.3-0.6**: Moderate complexity (acceptable)
- **0.6-1.0**: High complexity (may need simplification)

### Component Count
Number of major architectural components identified:
- Learning System
- Agent System
- Analysis Tools
- Workflows
- Documentation
- Testing

### Dependency Count
Total number of import relationships between internal modules.

## Integration with Existing Systems

### Knowledge Graph Integration
The architecture tracker complements the existing knowledge graph system:
- Architecture data feeds into knowledge graph
- Structural relationships enhance graph connections
- Component evolution tracked alongside code patterns

### GitHub Pages Dashboard
Architecture evolution is displayed alongside other metrics:
- Add link from main dashboard to architecture-evolution.html
- Metrics displayed in unified style
- Timeline integrated with other historical views

### Workflow Coordination
Runs after code merges alongside:
- Code analyzer
- Pattern matcher
- Agent metrics collector

## Development

### Running Tests

```bash
# Run the test suite
python3 test_architecture_tracker.py

# Run with verbose output
python3 test_architecture_tracker.py -v
```

**Test Coverage:**
- Tool existence and executability
- Analysis functionality
- Metrics calculation
- Mermaid diagram generation
- Evolution history tracking
- Comparison functionality
- Visualization files
- Workflow configuration

### Adding New Metrics

To add a new metric to track:

1. Update `calculate_metrics()` in `architecture-tracker.py`:
```python
def calculate_metrics(self) -> Dict[str, Any]:
    metrics = {
        ...
        "new_metric": self._calculate_new_metric()
    }
    return metrics
```

2. Update the visualization in `architecture-evolution.html`:
```javascript
const metricsToShow = [
    ...
    { key: 'new_metric', label: 'New Metric', icon: '📊' }
];
```

3. Update tests in `test_architecture_tracker.py`:
```python
checks = [
    ...
    ("new_metric", (int, float), lambda x: x >= 0)
]
```

### Adding New Components

To track a new component type:

1. Update `component_patterns` in `identify_components()`:
```python
component_patterns = {
    ...
    "new_component": ["pattern1", "pattern2"]
}
```

2. Component will automatically appear in:
   - Snapshot data
   - Visualization charts
   - Mermaid diagrams

## Troubleshooting

### No Data Showing in Visualization

**Problem:** The web page loads but shows "Loading architecture data..."

**Solutions:**
1. Ensure the tracker has run at least once: `python3 tools/architecture-tracker.py`
2. Check that data files exist: `ls analysis/architecture/`
3. Verify GitHub Pages is serving from correct directory
4. Check browser console for fetch errors

### Workflow Not Running

**Problem:** Architecture tracking workflow doesn't run on PR merge

**Solutions:**
1. Verify workflow is enabled in repository settings
2. Check workflow triggers in `.github/workflows/architecture-evolution.yml`
3. Ensure PR was merged (not just closed)
4. Check Actions tab for error logs

### Metrics Seem Incorrect

**Problem:** Coupling or complexity scores don't match expectations

**Solutions:**
1. Review metric calculation logic in `architecture-tracker.py`
2. Check that all relevant files are being analyzed
3. Verify Python files can be parsed (no syntax errors)
4. Run with `--json` flag to inspect raw data

### Snapshot Count Not Increasing

**Problem:** New runs don't add to evolution history

**Solutions:**
1. Check that `evolution.json` is writable
2. Verify commit hash is changing between runs
3. Ensure output directory is correct
4. Check for JSON parsing errors in logs

## Future Enhancements

Potential improvements for the system:

1. **Dependency Visualization**
   - Interactive module dependency graph
   - Circular dependency detection
   - Import path analysis

2. **Trend Analysis**
   - Automatic anomaly detection
   - Growth rate predictions
   - Health score trends

3. **Comparison Views**
   - Side-by-side snapshot comparison
   - Diff visualization for components
   - Change impact analysis

4. **Integration Enhancements**
   - Link to specific commits in GitHub
   - Correlate with PR metadata
   - Integration with agent metrics

5. **Advanced Metrics**
   - Code churn by component
   - Technical debt tracking
   - Refactoring recommendations

## References

- **Codebase:** `/home/runner/work/Chained/Chained`
- **Tool:** `tools/architecture-tracker.py`
- **Visualization:** `docs/architecture-evolution.html`
- **Workflow:** `.github/workflows/architecture-evolution.yml`
- **Tests:** `test_architecture_tracker.py`
- **Data:** `analysis/architecture/` and `docs/data/architecture/`

## Contributing

To contribute improvements:

1. Test changes locally with test suite
2. Ensure backward compatibility with existing data
3. Update documentation for new features
4. Add tests for new functionality
5. Follow existing code style and patterns

## License

Part of the Chained autonomous AI ecosystem. See repository LICENSE for details.

---

*Built with ❤️ by the Feature Architect agent as part of the self-evolving Chained ecosystem*
