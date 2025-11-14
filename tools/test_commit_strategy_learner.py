#!/usr/bin/env python3
"""
Comprehensive test suite for Git Commit Strategy Learning System

Tests all major components with rigorous validation:
- CommitMetrics data structure
- CommitPattern analysis
- StrategyRecommendation generation
- CommitStrategyLearner core functionality
- Pattern identification algorithms
- Recommendation generation
- Report generation

Follows repository testing patterns and best practices.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
import sys
import os

# Add tools directory to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

# Import using exec to handle the hyphenated module name
import importlib.util
spec = importlib.util.spec_from_file_location(
    "commit_strategy_learner", 
    tools_dir / "commit-strategy-learner.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CommitMetrics = module.CommitMetrics
CommitPattern = module.CommitPattern
StrategyRecommendation = module.StrategyRecommendation
CommitStrategyLearner = module.CommitStrategyLearner


class TestCommitMetrics(unittest.TestCase):
    """Test CommitMetrics data structure"""
    
    def test_commit_metrics_creation(self):
        """Test creating CommitMetrics with all fields"""
        metrics = CommitMetrics(
            commit_hash="abc123",
            author="Test Author",
            timestamp="2025-11-14T00:00:00+00:00",
            message="feat: add new feature",
            message_length=21,
            has_body=False,
            follows_conventional=True,
            conventional_type="feat",
            files_changed=3,
            lines_added=50,
            lines_deleted=10,
            total_lines_changed=60,
            file_types=["py", "md"],
            merge_status="success",
            merge_pr_number=123,
            merge_time_hours=2.5
        )
        
        self.assertEqual(metrics.commit_hash, "abc123")
        self.assertEqual(metrics.author, "Test Author")
        self.assertTrue(metrics.follows_conventional)
        self.assertEqual(metrics.conventional_type, "feat")
        self.assertEqual(metrics.merge_status, "success")
    
    def test_commit_metrics_to_dict(self):
        """Test converting CommitMetrics to dictionary"""
        metrics = CommitMetrics(
            commit_hash="def456",
            author="Another Author",
            timestamp="2025-11-14T01:00:00+00:00",
            message="fix: bug fix",
            message_length=13,
            has_body=True,
            follows_conventional=True,
            conventional_type="fix"
        )
        
        data = metrics.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["commit_hash"], "def456")
        self.assertTrue(data["follows_conventional"])


class TestCommitPattern(unittest.TestCase):
    """Test CommitPattern data structure"""
    
    def test_commit_pattern_creation(self):
        """Test creating CommitPattern"""
        pattern = CommitPattern(
            pattern_name="test_pattern",
            pattern_type="message",
            description="Test pattern description",
            success_rate=0.85,
            occurrence_count=42,
            average_merge_time_hours=3.5,
            common_attributes={"key": "value"},
            examples=["abc123", "def456"],
            confidence_score=0.9
        )
        
        self.assertEqual(pattern.pattern_name, "test_pattern")
        self.assertEqual(pattern.pattern_type, "message")
        self.assertEqual(pattern.success_rate, 0.85)
        self.assertEqual(pattern.confidence_score, 0.9)
    
    def test_commit_pattern_to_dict(self):
        """Test converting CommitPattern to dictionary"""
        pattern = CommitPattern(
            pattern_name="another_pattern",
            pattern_type="size",
            description="Size pattern",
            success_rate=0.75,
            occurrence_count=30,
            average_merge_time_hours=2.0,
            common_attributes={}
        )
        
        data = pattern.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["pattern_name"], "another_pattern")
        self.assertEqual(data["success_rate"], 0.75)


class TestStrategyRecommendation(unittest.TestCase):
    """Test StrategyRecommendation data structure"""
    
    def test_recommendation_creation(self):
        """Test creating StrategyRecommendation"""
        rec = StrategyRecommendation(
            recommendation_id="rec_001",
            title="Test Recommendation",
            description="This is a test",
            rationale="Because testing is important",
            expected_improvement="100% better",
            confidence_score=0.95,
            applicable_contexts=["general", "test"],
            supporting_patterns=["pattern1", "pattern2"],
            example_commits=["abc123"]
        )
        
        self.assertEqual(rec.recommendation_id, "rec_001")
        self.assertEqual(rec.confidence_score, 0.95)
        self.assertEqual(len(rec.applicable_contexts), 2)
    
    def test_recommendation_to_dict(self):
        """Test converting StrategyRecommendation to dictionary"""
        rec = StrategyRecommendation(
            recommendation_id="rec_002",
            title="Another Recommendation",
            description="Test description",
            rationale="Test rationale",
            expected_improvement="50% improvement",
            confidence_score=0.8,
            applicable_contexts=["feature"],
            supporting_patterns=["pattern3"]
        )
        
        data = rec.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["recommendation_id"], "rec_002")


class TestCommitStrategyLearner(unittest.TestCase):
    """Test CommitStrategyLearner main class"""
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create test git repo structure
        self.repo_dir = Path(self.test_dir) / "test_repo"
        self.repo_dir.mkdir()
        os.chdir(self.repo_dir)
        
        # Initialize git repo
        os.system('git init >/dev/null 2>&1')
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')
        
        # Create some test commits
        test_file = self.repo_dir / "test.txt"
        test_file.write_text("Initial content")
        os.system('git add test.txt')
        os.system('git commit -m "feat: initial commit" >/dev/null 2>&1')
        
        test_file.write_text("Updated content")
        os.system('git add test.txt')
        os.system('git commit -m "fix: update content" >/dev/null 2>&1')
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_learner_initialization(self):
        """Test CommitStrategyLearner initialization"""
        learner = CommitStrategyLearner(repo_path=str(self.repo_dir))
        
        self.assertIsNotNone(learner.strategies_data)
        self.assertIsNotNone(learner.patterns_data)
        self.assertEqual(learner.strategies_data["version"], "1.0.0")
    
    def test_initialize_strategies(self):
        """Test strategies database initialization"""
        learner = CommitStrategyLearner(repo_path=str(self.repo_dir))
        strategies = learner._initialize_strategies()
        
        self.assertIn("version", strategies)
        self.assertIn("total_commits_analyzed", strategies)
        self.assertIn("patterns_identified", strategies)
        self.assertEqual(strategies["total_commits_analyzed"], 0)
    
    def test_initialize_patterns(self):
        """Test patterns database initialization"""
        learner = CommitStrategyLearner(repo_path=str(self.repo_dir))
        patterns = learner._initialize_patterns()
        
        self.assertIn("version", patterns)
        self.assertIn("message_patterns", patterns)
        self.assertIn("size_patterns", patterns)
        self.assertIn("success_metrics", patterns)
    
    def test_is_conventional_commit(self):
        """Test conventional commit detection"""
        learner = CommitStrategyLearner(repo_path=str(self.repo_dir))
        
        # Test valid conventional commits
        is_conv, commit_type = learner._is_conventional_commit("feat: add feature")
        self.assertTrue(is_conv)
        self.assertEqual(commit_type, "feat")
        
        is_conv, commit_type = learner._is_conventional_commit("fix(auth): fix login bug")
        self.assertTrue(is_conv)
        self.assertEqual(commit_type, "fix")
        
        # Test invalid conventional commits
        is_conv, _ = learner._is_conventional_commit("Update some files")
        self.assertFalse(is_conv)
        
        is_conv, _ = learner._is_conventional_commit("WIP: work in progress")
        self.assertFalse(is_conv)
    
    def test_analyze_commit_message(self):
        """Test commit message analysis"""
        learner = CommitStrategyLearner(repo_path=str(self.repo_dir))
        
        # Test short message
        analysis = learner._analyze_commit_message("feat: add")
        self.assertFalse(analysis["is_descriptive"])
        self.assertTrue(analysis["is_concise"])
        self.assertTrue(analysis["follows_conventional"])
        
        # Test message with body
        message_with_body = "feat: add feature\n\nThis is a detailed explanation."
        analysis = learner._analyze_commit_message(message_with_body)
        self.assertTrue(analysis["has_body"])
        self.assertTrue(analysis["follows_conventional"])
        
        # Test long first line
        long_message = "feat: " + "x" * 100
        analysis = learner._analyze_commit_message(long_message)
        self.assertFalse(analysis["is_concise"])
    
    def test_get_commit_metrics(self):
        """Test extracting commit metrics"""
        learner = CommitStrategyLearner(repo_path=str(self.repo_dir))
        
        # Get latest commit hash
        import subprocess
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H'],
            cwd=self.repo_dir,
            capture_output=True,
            text=True
        )
        commit_hash = result.stdout.strip()
        
        metrics = learner._get_commit_metrics(commit_hash)
        
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.commit_hash, commit_hash)
        self.assertTrue(metrics.follows_conventional)
        self.assertEqual(metrics.conventional_type, "fix")
    
    def test_save_and_load_strategies(self):
        """Test saving and loading strategies database"""
        learner = CommitStrategyLearner(repo_path=str(self.repo_dir))
        
        # Modify strategies data
        learner.strategies_data["total_commits_analyzed"] = 42
        learner._save_strategies()
        
        # Create new learner and verify data persisted
        learner2 = CommitStrategyLearner(repo_path=str(self.repo_dir))
        self.assertEqual(learner2.strategies_data["total_commits_analyzed"], 42)
    
    def test_pattern_to_recommendation(self):
        """Test converting pattern to recommendation"""
        learner = CommitStrategyLearner(repo_path=str(self.repo_dir))
        
        pattern = CommitPattern(
            pattern_name="conventional_commits",
            pattern_type="message",
            description="Test pattern",
            success_rate=0.85,
            occurrence_count=50,
            average_merge_time_hours=2.0,
            common_attributes={},
            confidence_score=0.9
        )
        
        rec = learner._pattern_to_recommendation(pattern, "general")
        
        self.assertIsNotNone(rec)
        self.assertEqual(rec.title, "Use Conventional Commit Format")
        self.assertEqual(rec.confidence_score, 0.9)
        self.assertIn("general", rec.applicable_contexts)
    
    def test_generate_report(self):
        """Test report generation"""
        learner = CommitStrategyLearner(repo_path=str(self.repo_dir))
        
        # Add some test data
        learner.strategies_data["total_commits_analyzed"] = 10
        learner.strategies_data["successful_merges"] = 8
        learner.strategies_data["failed_merges"] = 2
        
        report = learner.generate_report()
        
        self.assertIsInstance(report, str)
        self.assertIn("Git Commit Strategy Learning Report", report)
        self.assertIn("Total commits analyzed: 10", report)
        self.assertIn("Successful merges: 8", report)


class TestPatternIdentification(unittest.TestCase):
    """Test pattern identification algorithms"""
    
    def test_identify_patterns_empty(self):
        """Test pattern identification with no data"""
        learner = CommitStrategyLearner()
        patterns = learner._identify_patterns([], [])
        
        self.assertEqual(len(patterns), 0)
    
    def test_identify_patterns_conventional(self):
        """Test identifying conventional commit pattern"""
        learner = CommitStrategyLearner()
        
        successful = [
            CommitMetrics(
                commit_hash=f"hash{i}",
                author="Test",
                timestamp="2025-11-14T00:00:00+00:00",
                message=f"feat: feature {i}",
                message_length=20,
                has_body=False,
                follows_conventional=True,
                conventional_type="feat",
                merge_status="success"
            )
            for i in range(10)
        ]
        
        patterns = learner._identify_patterns(successful, [])
        
        # Should find conventional commits pattern
        conv_patterns = [p for p in patterns if p.pattern_name == "conventional_commits"]
        self.assertGreater(len(conv_patterns), 0)
        
        if conv_patterns:
            pattern = conv_patterns[0]
            self.assertEqual(pattern.pattern_type, "message")
            self.assertGreater(pattern.success_rate, 0.5)
    
    def test_identify_patterns_size(self):
        """Test identifying optimal size pattern"""
        learner = CommitStrategyLearner()
        
        successful = [
            CommitMetrics(
                commit_hash=f"hash{i}",
                author="Test",
                timestamp="2025-11-14T00:00:00+00:00",
                message=f"fix: fix {i}",
                message_length=15,
                has_body=False,
                follows_conventional=True,
                conventional_type="fix",
                files_changed=3,
                lines_added=50,
                lines_deleted=20,
                total_lines_changed=70,
                merge_status="success"
            )
            for i in range(10)
        ]
        
        patterns = learner._identify_patterns(successful, [])
        
        # Should find size pattern
        size_patterns = [p for p in patterns if p.pattern_name == "optimal_commit_size"]
        self.assertGreater(len(size_patterns), 0)


class TestRecommendationGeneration(unittest.TestCase):
    """Test recommendation generation"""
    
    def setUp(self):
        """Set up test learner with sample data"""
        self.test_dir = tempfile.mkdtemp()
        self.learner = CommitStrategyLearner(repo_path=self.test_dir)
        
        # Add sample patterns
        sample_pattern = CommitPattern(
            pattern_name="conventional_commits",
            pattern_type="message",
            description="Conventional commit format",
            success_rate=0.85,
            occurrence_count=50,
            average_merge_time_hours=2.0,
            common_attributes={"most_common_types": ["feat", "fix"]},
            examples=["abc123", "def456"],
            confidence_score=0.9
        )
        
        self.learner.strategies_data["patterns_identified"] = [sample_pattern.to_dict()]
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir)
    
    def test_generate_recommendations_basic(self):
        """Test basic recommendation generation"""
        recommendations = self.learner.generate_recommendations(
            context="general",
            min_confidence=0.7
        )
        
        self.assertGreater(len(recommendations), 0)
        
        # Check first recommendation
        rec = recommendations[0]
        self.assertIsInstance(rec, StrategyRecommendation)
        self.assertGreaterEqual(rec.confidence_score, 0.7)
    
    def test_generate_recommendations_high_confidence(self):
        """Test filtering by confidence threshold"""
        recommendations = self.learner.generate_recommendations(
            context="general",
            min_confidence=0.95
        )
        
        # With high threshold, may get fewer or no recommendations
        for rec in recommendations:
            self.assertGreaterEqual(rec.confidence_score, 0.95)
    
    def test_generate_recommendations_context(self):
        """Test context-specific recommendations"""
        contexts = ["general", "feature", "bugfix", "refactor", "docs"]
        
        for context in contexts:
            recommendations = self.learner.generate_recommendations(
                context=context,
                min_confidence=0.5
            )
            
            # Verify all recommendations are applicable to context
            for rec in recommendations:
                self.assertIn(context, rec.applicable_contexts)


def run_tests():
    """Run all tests with detailed output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCommitMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestCommitPattern))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyRecommendation))
    suite.addTests(loader.loadTestsFromTestCase(TestCommitStrategyLearner))
    suite.addTests(loader.loadTestsFromTestCase(TestPatternIdentification))
    suite.addTests(loader.loadTestsFromTestCase(TestRecommendationGeneration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
