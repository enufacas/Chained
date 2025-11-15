#!/usr/bin/env python3
"""
Integration Example: Issue Clustering with Semantic Similarity
Author: @engineer-master

Demonstrates how to combine the Issue Clustering System with the 
Semantic Similarity Engine for comprehensive issue analysis.
"""

import json
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from issue_clustering_system import IssueClusteringSystem


def example_clustering_workflow():
    """Example workflow for issue clustering"""
    
    print("=" * 80)
    print("Issue Clustering System - Integration Example")
    print("Author: @engineer-master")
    print("=" * 80)
    
    # Sample issues data
    sample_issues = [
        {
            'number': 1,
            'title': 'API endpoint returning 500 errors',
            'body': 'The /users API endpoint fails with internal server error',
            'labels': [{'name': 'bug'}, {'name': 'api'}],
            'state': 'open',
            'user': {'login': 'user1'}
        },
        {
            'number': 2,
            'title': 'Database query performance issues',
            'body': 'Queries on products table are very slow',
            'labels': [{'name': 'performance'}, {'name': 'database'}],
            'state': 'open',
            'user': {'login': 'user2'}
        },
        {
            'number': 3,
            'title': 'Add unit tests for authentication',
            'body': 'Need comprehensive test coverage for login functionality',
            'labels': [{'name': 'testing'}, {'name': 'enhancement'}],
            'state': 'open',
            'user': {'login': 'user3'}
        },
        {
            'number': 4,
            'title': 'Fix authentication bug',
            'body': 'Users cannot login with correct credentials',
            'labels': [{'name': 'bug'}, {'name': 'authentication'}],
            'state': 'open',
            'user': {'login': 'user4'}
        },
        {
            'number': 5,
            'title': 'Improve API response time',
            'body': 'API endpoints are responding slowly',
            'labels': [{'name': 'performance'}, {'name': 'api'}],
            'state': 'open',
            'user': {'login': 'user5'}
        }
    ]
    
    # Initialize clustering system
    print("\n1️⃣ Initializing Issue Clustering System...")
    system = IssueClusteringSystem(output_dir="/tmp/clustering_example")
    
    # Load issues
    print("2️⃣ Loading sample issues...")
    system.load_issues_from_github(sample_issues)
    print(f"   Loaded {len(system.issues)} issues")
    
    # Perform clustering
    print("\n3️⃣ Performing clustering analysis...")
    clusters = system.perform_clustering(n_clusters=2, min_cluster_size=1)
    print(f"   Created {len(clusters)} clusters")
    
    # Display cluster details
    print("\n4️⃣ Cluster Details:")
    print("-" * 80)
    for i, cluster in enumerate(clusters, 1):
        print(f"\n   Cluster {i}: {cluster.cluster_name}")
        print(f"   - Category: {cluster.category}")
        print(f"   - Size: {cluster.size} issues")
        print(f"   - Confidence: {cluster.confidence:.2%}")
        print(f"   - Issues: #{', #'.join(map(str, cluster.issue_ids))}")
        print(f"   - Suggested Labels: {', '.join(cluster.suggested_labels[:3])}")
        print(f"   - Key Terms: {', '.join(cluster.common_terms[:5])}")
    
    # Predict cluster for new issue
    print("\n5️⃣ Predicting cluster for new issue...")
    print("-" * 80)
    new_issue_title = "Memory leak in cache module"
    new_issue_body = "Application memory grows over time"
    
    predicted_cluster = system.predict_cluster(new_issue_title, new_issue_body)
    
    if predicted_cluster:
        print(f"\n   New Issue: '{new_issue_title}'")
        print(f"   Predicted Cluster: {predicted_cluster.cluster_name}")
        print(f"   Category: {predicted_cluster.category}")
        print(f"   Confidence: {predicted_cluster.confidence:.2%}")
        print(f"   Suggested Labels: {', '.join(predicted_cluster.suggested_labels[:3])}")
    
    # Generate and display report
    print("\n6️⃣ Generating Clustering Report...")
    print("-" * 80)
    report = system.generate_report()
    
    # Show first part of report
    report_lines = report.split('\n')
    for line in report_lines[:25]:
        print(f"   {line}")
    
    if len(report_lines) > 25:
        print(f"   ... ({len(report_lines) - 25} more lines)")
    
    # Save results
    print("\n7️⃣ Saving Results...")
    filepath = system.save_results("example_clustering_results.json")
    print(f"   Results saved to: {filepath}")
    
    # Display quality metrics
    if system.metrics:
        print("\n8️⃣ Quality Metrics:")
        print("-" * 80)
        print(f"   Silhouette Score: {system.metrics.silhouette_score:.3f}")
        print(f"   Inertia: {system.metrics.inertia:.3f}")
        print(f"   Avg Cluster Size: {system.metrics.avg_cluster_size:.1f}")
        
        quality = "Excellent" if system.metrics.silhouette_score > 0.5 else \
                 "Good" if system.metrics.silhouette_score > 0.3 else \
                 "Fair" if system.metrics.silhouette_score > 0.1 else "Poor"
        print(f"   Quality Assessment: {quality}")
    
    print("\n" + "=" * 80)
    print("✅ Example workflow complete!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("- Issues are automatically grouped by similarity")
    print("- Categories are detected from labels and content")
    print("- New issues can be classified into existing clusters")
    print("- Quality metrics help assess clustering performance")
    print("\n@engineer-master - Systematic, rigorous, and reliable")


if __name__ == '__main__':
    example_clustering_workflow()
