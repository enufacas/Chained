# Knowledge Graph System - Documentation

## Overview

The Chained Knowledge Graph system provides intelligent analysis of the codebase, tracking file dependencies, test coverage, agent contributions, and collaborative patterns. This system enables impact analysis, expert identification, and code navigation.

## Components

### 1. Knowledge Graph Builder (`tools/knowledge_graph_builder.py`)

Analyzes the repository to extract relationships:

**Features:**
- **Code-Level Relationships**: Analyzes Python files to extract imports, function calls, and dependencies
- **File Dependencies**: Maps which files import which, creating a dependency graph
- **Test Coverage**: Identifies test files and maps them to the code they test
- **Agent Contributions**: Analyzes git history to track agent work (when agent names are in commits)
- **Collaborative Patterns**: Finds files that frequently change together

**Usage:**
```bash
# Generate knowledge graph
python tools/knowledge_graph_builder.py

# Specify output location
python tools/knowledge_graph_builder.py --output custom/path.json

# Specify repo path
python tools/knowledge_graph_builder.py --repo-path /path/to/repo
```

**Output:** `docs/data/codebase-graph.json`

### 2. Knowledge Graph Query Interface (`tools/knowledge_graph_query.py`)

Query the knowledge graph to answer questions about the codebase:

**Features:**
- Natural language-style queries
- File dependency lookup
- Impact analysis (blast radius calculation)
- Agent expertise tracking
- Test coverage queries
- Central file identification

**Usage:**

```bash
# Show statistics
python tools/knowledge_graph_query.py --stats

# Query a specific file
python tools/knowledge_graph_query.py --file tools/knowledge_graph_builder.py

# Query an agent
python tools/knowledge_graph_query.py --agent feature-architect

# Natural language query
python tools/knowledge_graph_query.py --query "What imports tools/code-analyzer.py?"

# Interactive mode
python tools/knowledge_graph_query.py --interactive
```

**Example Queries:**
- "What imports tools/code-analyzer.py?"
- "Which agent worked on test_agent_system.py?"
- "What tests cover tools/knowledge_graph_builder.py?"
- "Show impact of tools/knowledge_graph_query.py"
- "What does test_ai_knowledge_graph.py cover?"

### 3. Web Visualization (`docs/ai-knowledge-graph.html`)

Interactive D3.js visualization with two views:

**AI Learnings View:**
- Visualizes AI-related stories from Hacker News and TLDR Tech
- Shows topic relationships and trending concepts
- Interactive graph with zoom and filtering

**Codebase View:**
- Visualizes file dependencies and relationships
- Color-coded by type (code files, test files, agents)
- Filter by relationship type (imports, tests, agents)
- Hover for file details (functions, classes, lines of code)
- Interactive exploration of codebase structure

**Access:** Open `docs/ai-knowledge-graph.html` in a browser or visit the GitHub Pages site.

## Relationship Types

The knowledge graph tracks multiple relationship types:

1. **imports**: File A imports File B
2. **tests**: Test File tests Code File
3. **worked_on**: Agent worked on File (from git history)
4. **changes_with**: Files that frequently change together (co-change pattern)

## Data Structure

The generated graph (`docs/data/codebase-graph.json`) contains:

```json
{
  "metadata": {
    "generated_at": "timestamp",
    "total_files": 59,
    "total_test_files": 26
  },
  "nodes": [
    {
      "id": "filepath",
      "type": "code_file|test_file|agent",
      "label": "filename",
      "functions": 10,
      "classes": 2,
      "lines_of_code": 200,
      "contributors": ["user1", "user2"]
    }
  ],
  "relationships": [
    {
      "source": "file1.py",
      "target": "file2.py",
      "type": "imports",
      "weight": 1
    }
  ],
  "statistics": {
    "total_nodes": 59,
    "total_relationships": 267,
    "relationship_types": {
      "imports": 231,
      "tests": 36
    }
  }
}
```

## Integration

### Automated Graph Updates

To keep the knowledge graph up-to-date, add to your CI/CD pipeline:

```yaml
- name: Update Knowledge Graph
  run: |
    python tools/knowledge_graph_builder.py
    git add docs/data/codebase-graph.json
    git commit -m "Update knowledge graph"
```

### Query in Scripts

```python
from tools.knowledge_graph_query import KnowledgeGraphQuery

kgq = KnowledgeGraphQuery('docs/data/codebase-graph.json')

# Find dependencies
deps = kgq.find_dependencies('tools/code-analyzer.py')
print(f"Direct dependencies: {deps['direct']}")

# Impact analysis
impact = kgq.impact_analysis('tools/knowledge_graph_builder.py')
print(f"Blast radius: {impact['blast_radius']} files")
print(f"Tests to run: {impact['tests_to_run']}")
```

## Testing

Run tests to ensure the system works correctly:

```bash
# Test the builder
python test_knowledge_graph_builder.py

# Test the query interface
python test_knowledge_graph_query.py

# Run all knowledge graph tests
python test_knowledge_graph_builder.py && python test_knowledge_graph_query.py
```

## Use Cases

### 1. Impact Analysis
Before making changes, understand the impact:
```bash
python tools/knowledge_graph_query.py --file tools/agent_system.py
```

### 2. Find Expert Agents
Identify which agents have expertise in a topic:
```bash
python tools/knowledge_graph_query.py --interactive
# Then: "Find agents with expertise in testing"
```

### 3. Code Navigation
Explore file dependencies:
```bash
python tools/knowledge_graph_query.py --interactive
# Then: "What imports tools/code-analyzer.py?"
```

### 4. Test Coverage Review
Check what tests cover a file:
```bash
python tools/knowledge_graph_query.py --query "What tests cover tools/validation_utils.py?"
```

### 5. Refactoring Planning
Find files that change together (refactoring candidates):
```bash
python tools/knowledge_graph_query.py --file tools/agent_system.py
# Look at "Files that change together" section
```

## Performance

- Graph generation: ~5-10 seconds for 60+ files
- Query execution: < 100ms for most queries
- Web visualization: Handles 100+ nodes smoothly

## Future Enhancements

Potential additions:
- Semantic code analysis (function call chains)
- Issue/PR linking (connect issues to code changes)
- Complexity metrics (cyclomatic complexity, coupling)
- Architecture violation detection
- ML-based code recommendations
- Real-time graph updates via git hooks

## Troubleshooting

**Graph file not found:**
```bash
# Generate the graph first
python tools/knowledge_graph_builder.py
```

**Empty or minimal graph:**
- Ensure you're in the repository root
- Check that Python files are accessible
- Verify git history exists

**Import errors:**
```bash
# Ensure you're in the repo directory
cd /path/to/Chained
python tools/knowledge_graph_builder.py
```

## Contributing

To extend the knowledge graph system:

1. Add new relationship types in `KnowledgeGraphBuilder._generate_relationships()`
2. Add new query methods in `KnowledgeGraphQuery`
3. Update visualization in `docs/ai-knowledge-graph.js`
4. Add tests in `test_knowledge_graph_*.py`

## License

Part of the Chained project. See main LICENSE file.
