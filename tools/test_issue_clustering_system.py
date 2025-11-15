#!/usr/bin/env python3
"""
Comprehensive test suite for Issue Clustering System
Author: @engineer-master

Tests cover:
- Issue loading from various formats
- TF-IDF vectorization
- K-means clustering
- Cluster quality metrics
- Category prediction
- Edge cases and error handling
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from issue_clustering_system import (
    IssueClusteringSystem,
    IssueData,
    IssueCluster,
    ClusteringMetrics
)


class TestIssueClusteringSystem(unittest.TestCase):
    """Test suite for Issue Clustering System"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.system = IssueClusteringSystem(output_dir=self.temp_dir)
        
        # Sample test issues
        self.test_issues = [
            {
                'number': 1,
                'title': 'API endpoint returning 500 errors',
                'body': 'The /users API endpoint fails with internal server error',
                'labels': [{'name': 'bug'}, {'name': 'api'}],
                'state': 'open',
                'created_at': '2025-01-01T00:00:00Z',
                'user': {'login': 'user1'}
            },
            {
                'number': 2,
                'title': 'Database query performance issues',
                'body': 'Queries on products table are very slow',
                'labels': [{'name': 'performance'}, {'name': 'database'}],
                'state': 'open',
                'created_at': '2025-01-02T00:00:00Z',
                'user': {'login': 'user2'}
            },
            {
                'number': 3,
                'title': 'Add unit tests for authentication',
                'body': 'Need comprehensive test coverage for login functionality',
                'labels': [{'name': 'testing'}, {'name': 'enhancement'}],
                'state': 'open',
                'created_at': '2025-01-03T00:00:00Z',
                'user': {'login': 'user3'}
            },
            {
                'number': 4,
                'title': 'Fix authentication bug',
                'body': 'Users cannot login with correct credentials',
                'labels': [{'name': 'bug'}, {'name': 'authentication'}],
                'state': 'open',
                'created_at': '2025-01-04T00:00:00Z',
                'user': {'login': 'user4'}
            },
            {
                'number': 5,
                'title': 'Improve API response time',
                'body': 'API endpoints are responding slowly',
                'labels': [{'name': 'performance'}, {'name': 'api'}],
                'state': 'open',
                'created_at': '2025-01-05T00:00:00Z',
                'user': {'login': 'user5'}
            },
            {
                'number': 6,
                'title': 'Add integration tests',
                'body': 'Need end-to-end tests for critical workflows',
                'labels': [{'name': 'testing'}],
                'state': 'open',
                'created_at': '2025-01-06T00:00:00Z',
                'user': {'login': 'user6'}
            }
        ]
    
    def tearDown(self):
        """Clean up test artifacts"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_issue_data_creation(self):
        """Test IssueData object creation"""
        issue = IssueData(
            issue_number=1,
            title="Test issue",
            body="Test body",
            labels=["bug", "api"],
            state="open"
        )
        
        self.assertEqual(issue.issue_number, 1)
        self.assertEqual(issue.title, "Test issue")
        self.assertEqual(len(issue.labels), 2)
        
        # Test to_dict and from_dict
        issue_dict = issue.to_dict()
        restored = IssueData.from_dict(issue_dict)
        self.assertEqual(restored.issue_number, issue.issue_number)
        self.assertEqual(restored.title, issue.title)
    
    def test_load_issues_from_github(self):
        """Test loading issues from GitHub API format"""
        self.system.load_issues_from_github(self.test_issues)
        
        self.assertEqual(len(self.system.issues), 6)
        self.assertEqual(self.system.issues[0].issue_number, 1)
        self.assertEqual(self.system.issues[0].title, 'API endpoint returning 500 errors')
        self.assertEqual(self.system.issues[0].labels, ['bug', 'api'])
    
    def test_load_issues_from_file(self):
        """Test loading issues from JSON file"""
        # Create temporary JSON file
        test_file = os.path.join(self.temp_dir, 'test_issues.json')
        with open(test_file, 'w') as f:
            json.dump(self.test_issues, f)
        
        self.system.load_issues_from_file(test_file)
        
        self.assertEqual(len(self.system.issues), 6)
        self.assertEqual(self.system.issues[1].issue_number, 2)
    
    def test_tokenization(self):
        """Test text tokenization"""
        text = "Fix the API endpoint bug with error handling"
        tokens = self.system._tokenize(text)
        
        # Should remove stop words and normalize
        self.assertIn('api', tokens)
        self.assertIn('endpoint', tokens)
        self.assertIn('bug', tokens)
        self.assertNotIn('the', tokens)  # Stop word
        self.assertNotIn('with', tokens)  # Stop word
    
    def test_tokenization_with_urls(self):
        """Test tokenization removes URLs"""
        text = "Check https://example.com/endpoint for API details"
        tokens = self.system._tokenize(text)
        
        # URL should be removed
        self.assertNotIn('https', tokens)
        self.assertNotIn('example', tokens)
        self.assertIn('api', tokens)
        self.assertIn('check', tokens)
    
    def test_term_frequency_calculation(self):
        """Test TF calculation"""
        tokens = ['api', 'bug', 'api', 'test', 'api']
        tf = self.system._calculate_term_frequency(tokens)
        
        # 'api' appears 3 times (max), so should have TF of 1.0
        self.assertEqual(tf['api'], 1.0)
        # 'bug' appears 1 time, so TF should be 1/3
        self.assertAlmostEqual(tf['bug'], 1/3, places=2)
    
    def test_tfidf_index_building(self):
        """Test TF-IDF index construction"""
        self.system.load_issues_from_github(self.test_issues)
        self.system._build_tfidf_index()
        
        # Should have document terms for each issue
        self.assertEqual(len(self.system.document_terms), 6)
        
        # Should have IDF scores
        self.assertGreater(len(self.system.idf_scores), 0)
        
        # Should have TF-IDF vectors
        self.assertEqual(len(self.system.tfidf_vectors), 6)
    
    def test_clustering_basic(self):
        """Test basic clustering functionality"""
        self.system.load_issues_from_github(self.test_issues)
        clusters = self.system.perform_clustering(n_clusters=3, min_cluster_size=1)
        
        # Should create clusters
        self.assertGreater(len(clusters), 0)
        self.assertLessEqual(len(clusters), 3)
        
        # Each cluster should have properties
        for cluster in clusters:
            self.assertIsInstance(cluster.cluster_id, int)
            self.assertIsInstance(cluster.cluster_name, str)
            self.assertGreater(cluster.size, 0)
            self.assertGreater(len(cluster.issue_ids), 0)
            self.assertGreaterEqual(cluster.confidence, 0)
            self.assertLessEqual(cluster.confidence, 1)
    
    def test_clustering_quality_metrics(self):
        """Test clustering quality metrics"""
        self.system.load_issues_from_github(self.test_issues)
        self.system.perform_clustering(n_clusters=2, min_cluster_size=1)
        
        # Should have metrics
        self.assertIsNotNone(self.system.metrics)
        self.assertIsInstance(self.system.metrics, ClusteringMetrics)
        
        # Silhouette score should be between -1 and 1
        self.assertGreaterEqual(self.system.metrics.silhouette_score, -1)
        self.assertLessEqual(self.system.metrics.silhouette_score, 1)
        
        # Should have cluster sizes
        self.assertEqual(len(self.system.metrics.cluster_sizes), len(self.system.clusters))
    
    def test_cluster_naming(self):
        """Test automatic cluster naming"""
        # Create issues with similar labels
        api_issues = [
            IssueData(i, f"API issue {i}", "API problem", ['api', 'bug'], 'open')
            for i in range(3)
        ]
        
        tokens = ['api', 'endpoint', 'bug', 'api', 'error', 'api']
        name = self.system._generate_cluster_name(api_issues, tokens)
        
        # Should generate meaningful name
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)
        # Should likely contain 'API' or 'Bug' based on labels
        self.assertTrue('API' in name or 'Bug' in name or 'api' in name.lower())
    
    def test_cluster_categorization(self):
        """Test cluster categorization"""
        # Test bug category
        bug_issues = [
            IssueData(1, "Bug 1", "error", ['bug'], 'open'),
            IssueData(2, "Bug 2", "broken", ['bug', 'error'], 'open')
        ]
        category = self.system._categorize_cluster(bug_issues)
        self.assertEqual(category, 'bug')
        
        # Test feature category
        feature_issues = [
            IssueData(3, "Feature", "add new", ['feature', 'enhancement'], 'open')
        ]
        category = self.system._categorize_cluster(feature_issues)
        self.assertEqual(category, 'feature')
    
    def test_predict_cluster(self):
        """Test cluster prediction for new issues"""
        self.system.load_issues_from_github(self.test_issues)
        self.system.perform_clustering(n_clusters=3, min_cluster_size=1)
        
        # Predict cluster for API-related issue
        cluster = self.system.predict_cluster(
            "New API endpoint bug",
            "The API is failing with errors"
        )
        
        self.assertIsNotNone(cluster)
        self.assertIsInstance(cluster, IssueCluster)
        # Should suggest api or bug related labels
        has_relevant_label = any(
            label in ['api', 'bug', 'performance'] 
            for label in cluster.suggested_labels
        )
        self.assertTrue(has_relevant_label or cluster.category in ['bug', 'general'])
    
    def test_save_results(self):
        """Test saving clustering results"""
        self.system.load_issues_from_github(self.test_issues)
        self.system.perform_clustering(n_clusters=2, min_cluster_size=1)
        
        output_file = "test_results.json"
        filepath = self.system.save_results(output_file)
        
        # File should exist
        self.assertTrue(os.path.exists(filepath))
        
        # Should be valid JSON
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.assertIn('timestamp', data)
        self.assertIn('num_clusters', data)
        self.assertIn('clusters', data)
        self.assertEqual(data['num_issues'], 6)
    
    def test_generate_report(self):
        """Test report generation"""
        self.system.load_issues_from_github(self.test_issues)
        self.system.perform_clustering(n_clusters=2, min_cluster_size=1)
        
        report = self.system.generate_report()
        
        # Should be non-empty string
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 100)
        
        # Should contain key sections
        self.assertIn('Issue Clustering Analysis', report)
        self.assertIn('Executive Summary', report)
        self.assertIn('Identified Clusters', report)
        self.assertIn('@engineer-master', report)
    
    def test_empty_issues(self):
        """Test behavior with no issues"""
        clusters = self.system.perform_clustering()
        self.assertEqual(len(clusters), 0)
        
        # Predict should return None
        cluster = self.system.predict_cluster("Test", "Body")
        self.assertIsNone(cluster)
    
    def test_single_issue(self):
        """Test behavior with single issue"""
        single_issue = [self.test_issues[0]]
        self.system.load_issues_from_github(single_issue)
        clusters = self.system.perform_clustering(n_clusters=1, min_cluster_size=1)
        
        # Should create one cluster
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0].size, 1)
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        v1 = [1.0, 0.0, 1.0]
        v2 = [1.0, 0.0, 1.0]
        
        similarity = self.system._cosine_similarity(v1, v2)
        self.assertAlmostEqual(similarity, 1.0, places=5)
        
        # Orthogonal vectors
        v3 = [1.0, 0.0, 0.0]
        v4 = [0.0, 1.0, 0.0]
        similarity = self.system._cosine_similarity(v3, v4)
        self.assertAlmostEqual(similarity, 0.0, places=5)
    
    def test_euclidean_distance(self):
        """Test Euclidean distance calculation"""
        v1 = [0.0, 0.0, 0.0]
        v2 = [3.0, 4.0, 0.0]
        
        distance = self.system._euclidean_distance(v1, v2)
        self.assertAlmostEqual(distance, 5.0, places=5)
    
    def test_suggested_labels(self):
        """Test label suggestion from clusters"""
        self.system.load_issues_from_github(self.test_issues)
        clusters = self.system.perform_clustering(n_clusters=3, min_cluster_size=1)
        
        # Should have suggested labels
        for cluster in clusters:
            self.assertIsInstance(cluster.suggested_labels, list)
            # Labels should be from actual issue labels
            for label in cluster.suggested_labels:
                self.assertIsInstance(label, str)
    
    def test_common_terms_extraction(self):
        """Test extraction of common terms"""
        self.system.load_issues_from_github(self.test_issues)
        clusters = self.system.perform_clustering(n_clusters=2, min_cluster_size=1)
        
        # Should have common terms
        for cluster in clusters:
            self.assertIsInstance(cluster.common_terms, list)
            self.assertGreater(len(cluster.common_terms), 0)
            # Terms should be relevant
            for term in cluster.common_terms:
                self.assertIsInstance(term, str)
                self.assertGreater(len(term), 2)
    
    def test_cluster_confidence(self):
        """Test cluster confidence scores"""
        self.system.load_issues_from_github(self.test_issues)
        clusters = self.system.perform_clustering(n_clusters=2, min_cluster_size=1)
        
        # All clusters should have confidence scores
        for cluster in clusters:
            self.assertGreaterEqual(cluster.confidence, 0)
            self.assertLessEqual(cluster.confidence, 1)
    
    def test_min_cluster_size(self):
        """Test minimum cluster size filtering"""
        self.system.load_issues_from_github(self.test_issues)
        
        # With high min size, should get fewer clusters
        clusters = self.system.perform_clustering(n_clusters=5, min_cluster_size=3)
        
        # All clusters should meet minimum size
        for cluster in clusters:
            self.assertGreaterEqual(cluster.size, 3)
    
    def test_label_distribution(self):
        """Test label distribution in metrics"""
        self.system.load_issues_from_github(self.test_issues)
        self.system.perform_clustering(n_clusters=2, min_cluster_size=1)
        
        # Should have label distribution
        self.assertIsNotNone(self.system.metrics)
        self.assertIsNotNone(self.system.metrics.label_distribution)
        self.assertGreater(len(self.system.metrics.label_distribution), 0)
        
        # Check expected labels are present
        expected_labels = ['bug', 'api', 'performance', 'testing']
        found_labels = list(self.system.metrics.label_distribution.keys())
        
        # At least some expected labels should be present
        common = set(expected_labels) & set(found_labels)
        self.assertGreater(len(common), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.system = IssueClusteringSystem(output_dir=self.temp_dir)
    
    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_empty_issue_body(self):
        """Test handling of issues with empty body"""
        issues = [
            {
                'number': 1,
                'title': 'Title only issue',
                'body': '',
                'labels': [{'name': 'bug'}],
                'state': 'open',
                'user': {'login': 'user1'}
            }
        ]
        
        self.system.load_issues_from_github(issues)
        self.assertEqual(len(self.system.issues), 1)
        
        # Should still be able to cluster
        clusters = self.system.perform_clustering(n_clusters=1, min_cluster_size=1)
        self.assertEqual(len(clusters), 1)
    
    def test_no_labels(self):
        """Test handling of issues without labels"""
        issues = [
            {
                'number': 1,
                'title': 'Unlabeled issue',
                'body': 'No labels',
                'labels': [],
                'state': 'open',
                'user': {'login': 'user1'}
            },
            {
                'number': 2,
                'title': 'Another unlabeled',
                'body': 'Also no labels',
                'labels': [],
                'state': 'open',
                'user': {'login': 'user2'}
            }
        ]
        
        self.system.load_issues_from_github(issues)
        clusters = self.system.perform_clustering(n_clusters=1, min_cluster_size=1)
        
        # Should still create clusters
        self.assertEqual(len(clusters), 1)
    
    def test_invalid_json_file(self):
        """Test handling of invalid JSON file"""
        test_file = os.path.join(self.temp_dir, 'invalid.json')
        with open(test_file, 'w') as f:
            f.write("{ invalid json }")
        
        # Should handle gracefully
        self.system.load_issues_from_file(test_file)
        self.assertEqual(len(self.system.issues), 0)
    
    def test_missing_file(self):
        """Test handling of missing file"""
        self.system.load_issues_from_file("nonexistent_file.json")
        self.assertEqual(len(self.system.issues), 0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestIssueClusteringSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
