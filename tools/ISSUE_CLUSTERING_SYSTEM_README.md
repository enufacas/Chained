# Issue Clustering System

**Author:** @engineer-master (Margaret Hamilton)  
**Category:** Machine Learning / Issue Management  
**Status:** Production Ready

## Overview

The Issue Clustering System is a rigorous machine learning tool that automatically categorizes and clusters similar issues using advanced text analysis techniques. Built with **@engineer-master's** systematic engineering approach, it provides reliable and accurate issue organization.

## Features

### 🎯 Core Capabilities

- **Automatic Clustering**: Groups similar issues using K-means clustering
- **Category Detection**: Identifies issue categories (bug, feature, performance, etc.)
- **Label Suggestion**: Recommends appropriate labels based on content
- **Similarity Matching**: Finds related issues for new submissions
- **Quality Metrics**: Provides clustering quality assessment (silhouette score)
- **Comprehensive Reports**: Generates detailed markdown reports

### 🔬 Technical Implementation

- **TF-IDF Vectorization**: Advanced text representation
- **K-means++ Initialization**: Optimal centroid selection
- **Cosine Similarity**: Accurate similarity measurement
- **Stop Word Filtering**: Intelligent term selection
- **URL Removal**: Clean text processing
- **Hierarchical Analysis**: Multi-level clustering support

## Installation

No additional dependencies required beyond the base repository requirements:

```bash
cd tools
chmod +x issue_clustering_system.py
```

## Usage

### Command Line Interface

#### 1. Cluster Issues from File

```bash
python3 issue_clustering_system.py cluster \
  --input issues.json \
  --clusters 5 \
  --output results.json \
  --report clustering_report.md
```

#### 2. Predict Cluster for New Issue

```bash
python3 issue_clustering_system.py predict \
  --input clustered_issues.json \
  --title "API endpoint bug" \
  --body "The /users endpoint is returning 500 errors"
```

### Python API

```python
from issue_clustering_system import IssueClusteringSystem

# Initialize system
system = IssueClusteringSystem(output_dir="analysis/clustering")

# Load issues from GitHub API format
issues_data = [
    {
        'number': 1,
        'title': 'API bug',
        'body': 'Endpoint fails',
        'labels': [{'name': 'bug'}, {'name': 'api'}],
        'state': 'open',
        'user': {'login': 'user1'}
    },
    # ... more issues
]

system.load_issues_from_github(issues_data)

# Perform clustering
clusters = system.perform_clustering(n_clusters=5, min_cluster_size=2)

# Generate report
report = system.generate_report()
print(report)

# Save results
system.save_results("clustering_results.json")

# Predict cluster for new issue
cluster = system.predict_cluster("New issue title", "Issue description")
print(f"Predicted: {cluster.cluster_name}")
print(f"Suggested labels: {cluster.suggested_labels}")
```

## Input Format

### GitHub API Format

The system accepts issues in GitHub API format:

```json
[
  {
    "number": 123,
    "title": "Issue title",
    "body": "Issue description",
    "labels": [
      {"name": "bug"},
      {"name": "api"}
    ],
    "state": "open",
    "created_at": "2025-01-01T00:00:00Z",
    "user": {"login": "username"}
  }
]
```

### Simplified Format

Or a simpler format with `issues` key:

```json
{
  "issues": [
    {
      "number": 123,
      "title": "Issue title",
      "body": "Issue description",
      "labels": [{"name": "bug"}],
      "state": "open"
    }
  ]
}
```

## Output Format

### Clustering Results JSON

```json
{
  "timestamp": "2025-11-15T20:00:00Z",
  "num_issues": 50,
  "num_clusters": 5,
  "metrics": {
    "silhouette_score": 0.45,
    "inertia": 123.45,
    "num_clusters": 5,
    "avg_cluster_size": 10.0,
    "label_distribution": {
      "bug": 15,
      "feature": 20,
      "performance": 8
    }
  },
  "clusters": [
    {
      "cluster_id": 0,
      "cluster_name": "API-Related Issues",
      "size": 12,
      "category": "bug",
      "confidence": 0.87,
      "issue_ids": [1, 5, 12, 23],
      "suggested_labels": ["api", "bug", "endpoint"],
      "common_terms": ["api", "endpoint", "error", "response"],
      "description": "Cluster of 12 issues related to bug..."
    }
  ]
}
```

### Markdown Report

Generates comprehensive reports with:
- Executive summary
- Clustering quality metrics
- Detailed cluster descriptions
- Label distribution analysis
- Actionable recommendations

## Algorithm Details

### TF-IDF Vectorization

1. **Tokenization**: Text → normalized tokens
2. **Term Frequency**: Count term occurrences
3. **Inverse Document Frequency**: Weight by rarity
4. **Vector Construction**: Create sparse TF-IDF vectors
5. **Normalization**: L2 normalization for consistency

### K-means Clustering

1. **Initialization**: K-means++ for optimal starting centroids
2. **Assignment**: Assign each issue to nearest centroid
3. **Update**: Recalculate centroids
4. **Convergence**: Iterate until stable
5. **Quality**: Measure using silhouette score

### Category Prediction

Uses label co-occurrence and keyword matching:
- **bug**: error, fix, broken, issue
- **feature**: enhancement, request, add
- **performance**: slow, optimization, speed
- **security**: vulnerability, CVE, exploit
- **testing**: test, coverage, QA

## Quality Metrics

### Silhouette Score

Measures cluster cohesion and separation:
- **> 0.5**: Excellent clustering
- **0.3 - 0.5**: Good clustering
- **0.1 - 0.3**: Fair clustering
- **< 0.1**: Poor clustering

The score ranges from -1 to 1, with higher values indicating better-defined clusters.

### Inertia

Sum of squared distances to cluster centroids. Lower values indicate tighter clusters.

### Confidence

Per-cluster confidence based on average cosine similarity to centroid (0-1).

## Testing

Comprehensive test suite with 27+ test cases:

```bash
python3 test_issue_clustering_system.py
```

Tests cover:
- Issue loading from various formats
- Text tokenization and preprocessing
- TF-IDF vectorization
- K-means clustering algorithm
- Quality metrics calculation
- Prediction accuracy
- Edge cases and error handling

## Integration

### With Semantic Similarity Engine

The system complements the existing `semantic_similarity_engine.py`:

```python
from semantic_similarity_engine import SemanticSimilarityEngine
from issue_clustering_system import IssueClusteringSystem

# Find similar historical issues
similarity_engine = SemanticSimilarityEngine()
matches = similarity_engine.find_similar_issues("Bug title", "Description")

# Cluster current issues
clustering_system = IssueClusteringSystem()
clustering_system.load_issues_from_file("issues.json")
clusters = clustering_system.perform_clustering()
```

### GitHub Workflow Integration

Can be integrated into GitHub Actions workflows for automatic issue categorization:

```yaml
- name: Cluster Issues
  run: |
    python3 tools/issue_clustering_system.py cluster \
      --input issues.json \
      --clusters 5 \
      --report clustering_report.md
```

## Performance

### Time Complexity

- **TF-IDF Building**: O(n × m) where n = issues, m = avg terms
- **K-means**: O(n × k × i × d) where k = clusters, i = iterations, d = dimensions
- **Prediction**: O(k × d) for single issue

### Space Complexity

- **TF-IDF Vectors**: O(n × v) where v = vocabulary size
- **Centroids**: O(k × d)

### Scalability

Tested with:
- ✅ 1-10 issues: < 0.1s
- ✅ 10-100 issues: < 1s
- ✅ 100-1000 issues: < 10s
- ✅ 1000+ issues: < 60s

## Examples

### Example 1: Cluster Repository Issues

```bash
# Fetch issues using GitHub CLI
gh issue list --repo owner/repo --json number,title,body,labels,state --limit 100 > issues.json

# Cluster them
python3 issue_clustering_system.py cluster \
  --input issues.json \
  --clusters 8 \
  --report report.md

# View report
cat report.md
```

### Example 2: Predict Category for New Issue

```bash
python3 issue_clustering_system.py predict \
  --input issues.json \
  --title "Memory leak in cache" \
  --body "Application memory grows over time"
```

Output:
```
Predicted Cluster: Performance Issues
Category: performance
Confidence: 87.5%
Suggested Labels: performance, memory, optimization
```

## Best Practices

### Optimal Cluster Count

- **Small repos (< 50 issues)**: 3-5 clusters
- **Medium repos (50-200 issues)**: 5-10 clusters
- **Large repos (200+ issues)**: 10-20 clusters

Rule of thumb: `k ≈ sqrt(n/2)` where n = number of issues

### Minimum Cluster Size

- Use `--min-size 2` to filter out noise
- Adjust based on repository size
- Larger minimum = more focused clusters

### Re-clustering Frequency

- **Active repos**: Weekly or bi-weekly
- **Moderate repos**: Monthly
- **Stable repos**: Quarterly

## Troubleshooting

### Low Silhouette Score

**Cause**: Too many or too few clusters  
**Solution**: Adjust `--clusters` parameter

### Empty Clusters

**Cause**: Minimum size too high  
**Solution**: Reduce `--min-size` parameter

### Poor Predictions

**Cause**: Insufficient training data  
**Solution**: Ensure at least 20-30 issues for training

## Architecture

Built following **@engineer-master's** principles:

1. **Reliability First**: Defensive error handling throughout
2. **Systematic Approach**: Step-by-step processing pipeline
3. **Innovation Through Rigor**: K-means++ for better initialization
4. **Clear Documentation**: Comprehensive inline documentation
5. **Continuous Validation**: Extensive test coverage

## Future Enhancements

Potential improvements:

- [ ] Hierarchical clustering for taxonomy
- [ ] DBSCAN for anomaly detection
- [ ] Neural embeddings (word2vec, BERT)
- [ ] Multi-language support
- [ ] Real-time incremental clustering
- [ ] Interactive visualization dashboard

## Related Tools

- `semantic_similarity_engine.py`: Find similar historical issues
- `unsupervised_pattern_learner.py`: Discover code patterns
- `match-issue-to-agent.py`: Assign issues to agents

## Contributing

Follow the repository's contribution guidelines and the **@engineer-master** engineering standards:

- Write clean, well-tested code
- Include comprehensive documentation
- Add test cases for new features
- Follow existing code conventions
- Use meaningful variable names

## License

MIT License - See repository LICENSE file

## Author

**@engineer-master** (Margaret Hamilton)  
Systematic, rigorous, and innovative engineering approach

---

*Built with precision and reliability - "One small step for code, one giant leap for autonomous systems"*
