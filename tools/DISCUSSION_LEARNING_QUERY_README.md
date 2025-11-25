# 🔍 Discussion Learning Query API

## Overview

**@create-guru** has created a powerful query interface for the self-documenting AI system, enabling programmatic access to discussion learnings, insights, and patterns. This API serves as the foundation for future enhancements including semantic search, machine learning integration, and cross-repository learning.

## 🎯 Purpose

The Discussion Learning Query API addresses the need for:

1. **Programmatic Access**: Query insights without manual file parsing
2. **Flexible Filtering**: Find specific insights by type, tags, confidence, and date
3. **Knowledge Discovery**: Search the knowledge graph for related insights
4. **Data Export**: Export learnings in JSON, Markdown, or CSV formats
5. **Summary Statistics**: Get aggregated learning metrics

## ✨ Features

### Query Insights

Filter insights by multiple criteria:

```python
from discussion_learning_query import DiscussionLearningQuery, InsightType, SortOrder

query = DiscussionLearningQuery()

# Query technical insights with high confidence
result = query.query_insights(
    insight_type=InsightType.TECHNICAL,
    min_confidence=0.8,
    tags=['python', 'algorithm'],
    limit=10
)

print(f"Found {result.total_matches} insights in {result.query_time_ms}ms")
for insight in result.insights:
    print(f"- {insight['content'][:100]}...")
```

### Get Learning Summary

Generate aggregate statistics:

```python
summary = query.get_summary(days=30)

print(f"Discussions Analyzed: {summary.total_discussions}")
print(f"Total Insights: {summary.total_insights}")
print(f"Average Quality: {summary.average_quality_score:.1%}")
print(f"Top Tags: {', '.join(t for t, _ in summary.top_tags[:5])}")
```

### Search Knowledge Graph

Find related insights using text similarity:

```python
results = query.search_knowledge_graph("neural network performance")

for result in results:
    print(f"[{result['similarity_score']:.1%}] {result['content'][:80]}...")
```

### Export Learnings

Export in multiple formats:

```python
# JSON export
json_data = query.export_learnings(format='json', days=30)

# Markdown export
markdown_report = query.export_learnings(format='markdown', days=30)

# CSV export
csv_data = query.export_learnings(format='csv', days=30)
```

## 🖥️ Command-Line Interface

### Query Command

```bash
# Query all insights
python3 tools/discussion-learning-query.py query

# Query technical insights with high confidence
python3 tools/discussion-learning-query.py query --type technical --min-confidence 0.7

# Query insights by tags
python3 tools/discussion-learning-query.py query --tags python api --limit 5

# Search within content
python3 tools/discussion-learning-query.py query --search "algorithm" --limit 10
```

### Summary Command

```bash
# Get summary of last 30 days
python3 tools/discussion-learning-query.py summary --days 30

# Get summary of last week
python3 tools/discussion-learning-query.py summary --days 7
```

### Search Command

```bash
# Search knowledge graph
python3 tools/discussion-learning-query.py search "neural network optimization" --limit 5
```

### Export Command

```bash
# Export as Markdown
python3 tools/discussion-learning-query.py export --format markdown --days 30

# Export as JSON
python3 tools/discussion-learning-query.py export --format json --days 7

# Export as CSV
python3 tools/discussion-learning-query.py export --format csv --days 30 > learnings.csv
```

## 📊 Query Filters

### Insight Types

- `technical`: Implementation, algorithms, performance
- `process`: Workflows, procedures, methodologies
- `agent_behavior`: Agent collaboration, coordination
- `decision`: Key decisions and conclusions
- `all`: All insight types

### Sort Orders

- `confidence_desc`: Highest confidence first
- `confidence_asc`: Lowest confidence first
- `date_desc`: Most recent first (default)
- `date_asc`: Oldest first

### Filter Options

| Filter | Description |
|--------|-------------|
| `insight_type` | Filter by insight category |
| `tags` | Filter by any matching tag |
| `min_confidence` | Minimum confidence score (0.0-1.0) |
| `max_confidence` | Maximum confidence score (0.0-1.0) |
| `date_from` | Start date (ISO format) |
| `date_to` | End date (ISO format) |
| `search_text` | Text to search in content |
| `limit` | Maximum results to return |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           DiscussionLearningQuery               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌────────────────┐  ┌────────────────┐       │
│  │  Query Engine  │  │  Index Cache   │       │
│  └────────────────┘  └────────────────┘       │
│                                                 │
│  ┌────────────────┐  ┌────────────────┐       │
│  │ Knowledge Graph │  │   Exporter    │       │
│  │    Search      │  │               │       │
│  └────────────────┘  └────────────────┘       │
│                                                 │
└─────────────────────────────────────────────────┘
          │                    │
          ▼                    ▼
    ┌───────────┐        ┌───────────┐
    │ Discussion│        │ Knowledge │
    │   Files   │        │   Graph   │
    └───────────┘        └───────────┘
```

## 🔮 Future Enhancements

This API is designed to support:

1. **Semantic Search**
   - Vector embeddings integration
   - Neural similarity matching
   - Multi-language support

2. **Machine Learning**
   - Train classifiers on historical insights
   - Predict valuable discussion topics
   - Automatic insight categorization

3. **Cross-Repository Learning**
   - Query insights from multiple repos
   - Share anonymized patterns
   - Build universal AI knowledge

4. **Real-Time Streaming**
   - Subscribe to new insights
   - Live learning notifications
   - Trending topic alerts

## 🧪 Testing

Run the test suite:

```bash
python3 -m pytest tools/test_discussion_learning_query.py -v
```

Test coverage includes:
- ✅ Query filtering and sorting
- ✅ Summary generation
- ✅ Knowledge graph search
- ✅ Export formats
- ✅ Edge cases and error handling
- ✅ Full workflow integration

## 📚 Integration

### With Existing Self-Documenting AI

The Query API works alongside:
- `issue-discussion-learner.py` (base learner)
- `enhanced-discussion-learner.py` (enhanced features)
- `self-documenting-ai.yml` (basic workflow)
- `self-documenting-ai-enhanced.yml` (enhanced workflow)

### With Future Systems

The API is designed to integrate with:
- Semantic search engines
- ML training pipelines
- Dashboard visualizations
- Cross-repo learning systems

## 🤝 Contributing

To extend the Query API:

1. **Add New Filters**: Extend `_matches_filters()` method
2. **New Export Formats**: Add format handler in `export_learnings()`
3. **Enhanced Search**: Improve similarity algorithms
4. **New Commands**: Add subparsers in `main()`

## 📝 Credits

**Designed and Implemented by @create-guru**

Following Tesla-inspired principles:
- Inventive infrastructure design
- Visionary architecture
- Creative solutions to complex problems
- Elegant and powerful interfaces

---

*This query API enables programmatic access to the self-documenting AI's knowledge base, serving as the foundation for advanced learning and discovery capabilities.*

**The power of knowledge lies in its accessibility.**
