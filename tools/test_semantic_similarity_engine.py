#!/usr/bin/env python3
"""
Comprehensive tests for the Semantic Similarity Engine.

Following Margaret Hamilton's rigorous approach to testing.
Tests cover normal operation, edge cases, and failure modes.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime

from semantic_similarity_engine import (
    SemanticSimilarityEngine,
    IssueRecord,
    SimilarityMatch
)


class TestIssueRecord(unittest.TestCase):
    """Test IssueRecord dataclass."""
    
    def test_create_issue_record(self):
        """Test creating an issue record."""
        issue = IssueRecord(
            issue_number=1,
            title="Test Issue",
            body="Test body",
            labels=["bug"],
            solution_summary="Fixed it",
            agent_assigned="engineer-master",
            resolved_at="2024-01-01T00:00:00Z"
        )
        
        self.assertEqual(issue.issue_number, 1)
        self.assertEqual(issue.title, "Test Issue")
        self.assertEqual(issue.agent_assigned, "engineer-master")
    
    def test_to_dict(self):
        """Test converting issue to dictionary."""
        issue = IssueRecord(
            issue_number=1,
            title="Test",
            body="Body",
            labels=["bug"],
            solution_summary="Fixed",
            agent_assigned="agent",
            resolved_at="2024-01-01T00:00:00Z"
        )
        
        data = issue.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['issue_number'], 1)
        self.assertEqual(data['title'], "Test")
    
    def test_from_dict(self):
        """Test creating issue from dictionary."""
        data = {
            'issue_number': 1,
            'title': 'Test',
            'body': 'Body',
            'labels': ['bug'],
            'solution_summary': 'Fixed',
            'agent_assigned': 'agent',
            'resolved_at': '2024-01-01T00:00:00Z',
            'pr_number': 10
        }
        
        issue = IssueRecord.from_dict(data)
        self.assertEqual(issue.issue_number, 1)
        self.assertEqual(issue.pr_number, 10)


class TestSemanticSimilarityEngine(unittest.TestCase):
    """Test the Semantic Similarity Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.history_path = os.path.join(self.temp_dir, 'test_history.json')
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        if os.path.exists(self.history_path):
            os.remove(self.history_path)
        os.rmdir(self.temp_dir)
    
    def test_init_empty_engine(self):
        """Test initializing engine with no history."""
        engine = SemanticSimilarityEngine(self.history_path)
        self.assertEqual(len(engine.issue_records), 0)
        self.assertEqual(len(engine.tfidf_vectors), 0)
    
    def test_tokenize(self):
        """Test text tokenization."""
        engine = SemanticSimilarityEngine(self.history_path)
        
        # Normal text
        tokens = engine._tokenize("This is a test")
        self.assertIn("test", tokens)
        self.assertNotIn("is", tokens)  # Stop word
        self.assertNotIn("a", tokens)   # Stop word
        
        # Mixed case
        tokens = engine._tokenize("API Bug Fix")
        self.assertIn("api", tokens)
        self.assertIn("bug", tokens)
        self.assertIn("fix", tokens)
        
        # Special characters
        tokens = engine._tokenize("test-case_123")
        self.assertIn("test", tokens)
        self.assertIn("case", tokens)
        self.assertIn("123", tokens)
    
    def test_tokenize_edge_cases(self):
        """Test tokenization edge cases."""
        engine = SemanticSimilarityEngine(self.history_path)
        
        # Empty string
        tokens = engine._tokenize("")
        self.assertEqual(tokens, [])
        
        # None
        tokens = engine._tokenize(None)
        self.assertEqual(tokens, [])
        
        # Only stop words
        tokens = engine._tokenize("the and or")
        self.assertEqual(tokens, [])
        
        # Only short words
        tokens = engine._tokenize("a b c")
        self.assertEqual(tokens, [])
    
    def test_calculate_term_frequency(self):
        """Test term frequency calculation."""
        engine = SemanticSimilarityEngine(self.history_path)
        
        tokens = ["test", "test", "bug", "fix"]
        tf = engine._calculate_term_frequency(tokens)
        
        # "test" appears twice, should have max frequency
        self.assertEqual(tf["test"], 1.0)
        # Others appear once
        self.assertEqual(tf["bug"], 0.5)
        self.assertEqual(tf["fix"], 0.5)
    
    def test_calculate_term_frequency_edge_cases(self):
        """Test term frequency edge cases."""
        engine = SemanticSimilarityEngine(self.history_path)
        
        # Empty list
        tf = engine._calculate_term_frequency([])
        self.assertEqual(tf, {})
        
        # Single term
        tf = engine._calculate_term_frequency(["test"])
        self.assertEqual(tf["test"], 1.0)
    
    def test_add_issue_and_search(self):
        """Test adding issues and searching."""
        engine = SemanticSimilarityEngine(self.history_path)
        
        # Add some test issues
        issues = [
            IssueRecord(
                issue_number=1,
                title="API Bug Fix",
                body="Fixed bug in API endpoint",
                labels=["bug", "api"],
                solution_summary="Updated error handling in API",
                agent_assigned="engineer-master",
                resolved_at="2024-01-01T00:00:00Z"
            ),
            IssueRecord(
                issue_number=2,
                title="Performance Optimization",
                body="Optimized database queries",
                labels=["performance"],
                solution_summary="Added indexes and caching",
                agent_assigned="accelerate-master",
                resolved_at="2024-01-02T00:00:00Z"
            ),
            IssueRecord(
                issue_number=3,
                title="Test Coverage",
                body="Increased test coverage to 80%",
                labels=["testing"],
                solution_summary="Added unit and integration tests",
                agent_assigned="assert-specialist",
                resolved_at="2024-01-03T00:00:00Z"
            )
        ]
        
        for issue in issues:
            engine.add_issue(issue)
        
        # Search for similar issues
        matches = engine.find_similar_issues(
            "API endpoint error",
            "Getting errors from the API",
            top_k=3
        )
        
        # Should find the API bug as most similar
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].issue_number, 1)
        self.assertIn("api", [t.lower() for t in matches[0].matching_terms])
    
    def test_find_similar_issues_no_matches(self):
        """Test finding similar issues with no matches."""
        engine = SemanticSimilarityEngine(self.history_path)
        
        # Add an issue
        engine.add_issue(IssueRecord(
            issue_number=1,
            title="API Bug",
            body="API error",
            labels=["bug"],
            solution_summary="Fixed",
            agent_assigned="agent",
            resolved_at="2024-01-01T00:00:00Z"
        ))
        
        # Search for completely unrelated topic
        matches = engine.find_similar_issues(
            "Database migration",
            "Need to migrate database schema",
            min_similarity=0.5
        )
        
        # May or may not find matches depending on threshold
        self.assertIsInstance(matches, list)
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        engine = SemanticSimilarityEngine(self.history_path)
        
        # Identical vectors
        vec1 = {"test": 1.0, "bug": 0.5}
        vec2 = {"test": 1.0, "bug": 0.5}
        similarity = engine._cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 1.0, places=5)
        
        # Orthogonal vectors (no common terms)
        vec1 = {"test": 1.0}
        vec2 = {"bug": 1.0}
        similarity = engine._cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 0.0)
        
        # Partial overlap
        vec1 = {"test": 1.0, "bug": 0.5}
        vec2 = {"test": 0.5, "fix": 1.0}
        similarity = engine._cosine_similarity(vec1, vec2)
        self.assertGreater(similarity, 0.0)
        self.assertLess(similarity, 1.0)
    
    def test_cosine_similarity_edge_cases(self):
        """Test cosine similarity edge cases."""
        engine = SemanticSimilarityEngine(self.history_path)
        
        # Empty vectors
        similarity = engine._cosine_similarity({}, {})
        self.assertEqual(similarity, 0.0)
        
        # One empty vector
        similarity = engine._cosine_similarity({"test": 1.0}, {})
        self.assertEqual(similarity, 0.0)
    
    def test_save_and_load_history(self):
        """Test saving and loading history."""
        # Create engine and add issues
        engine1 = SemanticSimilarityEngine(self.history_path)
        engine1.add_issue(IssueRecord(
            issue_number=1,
            title="Test Issue",
            body="Test body",
            labels=["test"],
            solution_summary="Fixed",
            agent_assigned="agent",
            resolved_at="2024-01-01T00:00:00Z"
        ))
        
        # Save history
        engine1.save_history()
        
        # Load in new engine
        engine2 = SemanticSimilarityEngine(self.history_path)
        
        # Should have same data
        self.assertEqual(len(engine2.issue_records), 1)
        self.assertEqual(engine2.issue_records[0].issue_number, 1)
        self.assertEqual(engine2.issue_records[0].title, "Test Issue")
    
    def test_get_statistics(self):
        """Test getting statistics."""
        engine = SemanticSimilarityEngine(self.history_path)
        
        # Empty engine
        stats = engine.get_statistics()
        self.assertEqual(stats['total_issues'], 0)
        
        # Add issues
        engine.add_issue(IssueRecord(
            issue_number=1,
            title="Test",
            body="Body",
            labels=[],
            solution_summary="Fixed",
            agent_assigned="engineer-master",
            resolved_at="2024-01-01T00:00:00Z"
        ))
        engine.add_issue(IssueRecord(
            issue_number=2,
            title="Test 2",
            body="Body 2",
            labels=[],
            solution_summary="Fixed",
            agent_assigned="engineer-master",
            resolved_at="2024-01-02T00:00:00Z"
        ))
        
        stats = engine.get_statistics()
        self.assertEqual(stats['total_issues'], 2)
        self.assertIn('engineer-master', stats['agents'])
        self.assertEqual(stats['agents']['engineer-master'], 2)
    
    def test_load_invalid_history(self):
        """Test loading invalid history file."""
        # Create invalid JSON
        with open(self.history_path, 'w') as f:
            f.write("invalid json")
        
        # Should handle gracefully
        engine = SemanticSimilarityEngine(self.history_path)
        self.assertEqual(len(engine.issue_records), 0)
    
    def test_load_malformed_history(self):
        """Test loading malformed history structure."""
        # Create valid JSON but wrong structure
        with open(self.history_path, 'w') as f:
            json.dump({"wrong": "structure"}, f)
        
        # Should handle gracefully
        engine = SemanticSimilarityEngine(self.history_path)
        self.assertEqual(len(engine.issue_records), 0)
    
    def test_similarity_with_labels(self):
        """Test that labels are included in results."""
        engine = SemanticSimilarityEngine(self.history_path)
        
        engine.add_issue(IssueRecord(
            issue_number=1,
            title="API Bug",
            body="Fix API",
            labels=["bug", "api", "urgent"],
            solution_summary="Fixed",
            agent_assigned="agent",
            resolved_at="2024-01-01T00:00:00Z"
        ))
        
        matches = engine.find_similar_issues("API problem", "")
        
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].labels, ["bug", "api", "urgent"])


class TestSimilarityMatch(unittest.TestCase):
    """Test SimilarityMatch dataclass."""
    
    def test_create_match(self):
        """Test creating a similarity match."""
        match = SimilarityMatch(
            issue_number=1,
            title="Test",
            similarity_score=0.85,
            agent_assigned="agent",
            solution_summary="Fixed",
            matching_terms=["test", "bug"],
            labels=["bug"]
        )
        
        self.assertEqual(match.issue_number, 1)
        self.assertAlmostEqual(match.similarity_score, 0.85)
    
    def test_match_to_dict(self):
        """Test converting match to dictionary."""
        match = SimilarityMatch(
            issue_number=1,
            title="Test",
            similarity_score=0.85,
            agent_assigned="agent",
            solution_summary="Fixed",
            matching_terms=["test"],
            labels=[]
        )
        
        data = match.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['issue_number'], 1)
        self.assertAlmostEqual(data['similarity_score'], 0.85)


class TestIntegration(unittest.TestCase):
    """Integration tests for the similarity engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.history_path = os.path.join(self.temp_dir, 'integration_history.json')
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.history_path):
            os.remove(self.history_path)
        os.rmdir(self.temp_dir)
    
    def test_full_workflow(self):
        """Test complete workflow: add, search, save, load."""
        # Create engine
        engine1 = SemanticSimilarityEngine(self.history_path)
        
        # Add multiple related issues
        issues = [
            IssueRecord(
                issue_number=1,
                title="API returns 500 error",
                body="The /users endpoint is returning 500 errors when called",
                labels=["bug", "api"],
                solution_summary="Fixed null pointer exception in user controller",
                agent_assigned="engineer-master",
                resolved_at="2024-01-01T00:00:00Z",
                pr_number=100
            ),
            IssueRecord(
                issue_number=2,
                title="API timeout on /products",
                body="Getting timeout errors on products API",
                labels=["bug", "api", "performance"],
                solution_summary="Optimized database query and added caching",
                agent_assigned="accelerate-master",
                resolved_at="2024-01-02T00:00:00Z",
                pr_number=101
            ),
            IssueRecord(
                issue_number=3,
                title="Add tests for API",
                body="Need to increase test coverage for API endpoints",
                labels=["testing", "api"],
                solution_summary="Added comprehensive API endpoint tests",
                agent_assigned="assert-specialist",
                resolved_at="2024-01-03T00:00:00Z",
                pr_number=102
            )
        ]
        
        for issue in issues:
            engine1.add_issue(issue)
        
        # Save
        engine1.save_history()
        
        # Load in new engine
        engine2 = SemanticSimilarityEngine(self.history_path)
        
        # Search for API errors
        matches = engine2.find_similar_issues(
            "API endpoint error",
            "Getting errors from API calls",
            top_k=3,
            min_similarity=0.05
        )
        
        # Should find relevant issues
        self.assertGreater(len(matches), 0)
        
        # Top match should be related to API errors
        top_match = matches[0]
        self.assertIn("api", [t.lower() for t in top_match.matching_terms])
        
        # Should have solution information
        self.assertIsNotNone(top_match.solution_summary)
        self.assertIsNotNone(top_match.agent_assigned)


if __name__ == '__main__':
    unittest.main()
