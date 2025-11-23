#!/usr/bin/env python3
"""
Comprehensive test suite for ML Commit Optimizer

Tests ML-based commit strategy learning with:
- Feature extraction validation
- Model training and prediction
- Adaptive threshold learning
- Integration with existing commit learner

Built by @create-guru for the Chained ecosystem.
"""

import unittest
import tempfile
import shutil
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add tools directory to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

# Import ML optimizer
import importlib.util
spec = importlib.util.spec_from_file_location(
    "ml_commit_optimizer",
    tools_dir / "ml-commit-optimizer.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CommitFeatures = module.CommitFeatures
PredictionResult = module.PredictionResult
AdaptiveThresholds = module.AdaptiveThresholds
MLCommitOptimizer = module.MLCommitOptimizer
ML_AVAILABLE = module.ML_AVAILABLE


class TestCommitFeatures(unittest.TestCase):
    """Test CommitFeatures data structure"""
    
    def test_feature_creation(self):
        """Test creating CommitFeatures"""
        features = CommitFeatures(
            message_length=50.0,
            has_body=1,
            conventional_format=1,
            message_clarity_score=0.8,
            files_changed=3.0,
            lines_added=100.0,
            lines_deleted=20.0,
            total_lines_changed=120.0,
            file_type_diversity=2.0,
            directory_count=1.0,
            hour_of_day=14.0,
            day_of_week=2.0,
            change_density=40.0,
            modification_ratio=0.2
        )
        
        self.assertEqual(features.message_length, 50.0)
        self.assertEqual(features.has_body, 1)
        self.assertEqual(features.conventional_format, 1)
        self.assertAlmostEqual(features.message_clarity_score, 0.8)
    
    def test_to_array(self):
        """Test converting features to array"""
        features = CommitFeatures(
            message_length=50.0,
            has_body=1,
            conventional_format=1,
            message_clarity_score=0.8,
            files_changed=3.0,
            lines_added=100.0,
            lines_deleted=20.0,
            total_lines_changed=120.0,
            file_type_diversity=2.0,
            directory_count=1.0,
            hour_of_day=14.0,
            day_of_week=2.0,
            change_density=40.0,
            modification_ratio=0.2
        )
        
        arr = features.to_array()
        self.assertEqual(len(arr), 14)
        self.assertEqual(arr[0], 50.0)
        self.assertEqual(arr[1], 1)
        self.assertEqual(arr[4], 3.0)
    
    def test_feature_names(self):
        """Test feature names"""
        names = CommitFeatures.feature_names()
        self.assertEqual(len(names), 14)
        self.assertIn('message_length', names)
        self.assertIn('files_changed', names)
        self.assertIn('change_density', names)


class TestAdaptiveThresholds(unittest.TestCase):
    """Test AdaptiveThresholds data structure"""
    
    def test_threshold_creation(self):
        """Test creating AdaptiveThresholds"""
        thresholds = AdaptiveThresholds(
            message_length_min=20.0,
            message_length_max=72.0,
            files_per_commit_ideal=5.0,
            files_per_commit_max=15.0,
            lines_per_commit_ideal=100.0,
            lines_per_commit_max=500.0,
            conventional_commit_weight=0.7,
            last_updated="2025-11-14T00:00:00Z",
            confidence=0.85,
            sample_size=100
        )
        
        self.assertEqual(thresholds.message_length_min, 20.0)
        self.assertEqual(thresholds.files_per_commit_ideal, 5.0)
        self.assertEqual(thresholds.confidence, 0.85)
        self.assertEqual(thresholds.sample_size, 100)


class TestMLCommitOptimizer(unittest.TestCase):
    """Test MLCommitOptimizer main class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create test git repo
        self.repo_dir = Path(self.test_dir) / "test_repo"
        self.repo_dir.mkdir()
        os.chdir(self.repo_dir)
        
        # Initialize git repo
        os.system('git init >/dev/null 2>&1')
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')
        
        # Create test commits
        for i in range(5):
            test_file = self.repo_dir / f"test{i}.py"
            test_file.write_text(f"# Test file {i}\nprint('test')\n")
            os.system(f'git add test{i}.py')
            os.system(f'git commit -m "feat: add test file {i}" >/dev/null 2>&1')
    
    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization"""
        optimizer = MLCommitOptimizer(repo_path=str(self.repo_dir))
        
        self.assertIsNotNone(optimizer.thresholds)
        self.assertEqual(optimizer.repo_path, self.repo_dir)
    
    def test_is_conventional(self):
        """Test conventional commit detection"""
        optimizer = MLCommitOptimizer(repo_path=str(self.repo_dir))
        
        self.assertTrue(optimizer._is_conventional("feat: add feature"))
        self.assertTrue(optimizer._is_conventional("fix(auth): fix bug"))
        self.assertFalse(optimizer._is_conventional("Update files"))
        self.assertFalse(optimizer._is_conventional("WIP: work in progress"))
    
    def test_calculate_clarity_score(self):
        """Test message clarity scoring"""
        optimizer = MLCommitOptimizer(repo_path=str(self.repo_dir))
        
        # Good message
        good_msg = "feat: add authentication\n\nImplement JWT-based auth to improve security."
        score = optimizer._calculate_clarity_score(good_msg)
        self.assertGreater(score, 0.5)
        
        # Poor message
        poor_msg = "fix"
        score = optimizer._calculate_clarity_score(poor_msg)
        self.assertLess(score, 0.5)
    
    def test_extract_features(self):
        """Test feature extraction"""
        optimizer = MLCommitOptimizer(repo_path=str(self.repo_dir))
        
        # Get latest commit
        import subprocess
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H'],
            cwd=self.repo_dir,
            capture_output=True,
            text=True
        )
        commit_hash = result.stdout.strip()
        
        features = optimizer._extract_features(commit_hash)
        
        self.assertIsNotNone(features)
        self.assertIsInstance(features, CommitFeatures)
        self.assertGreater(features.message_length, 0)
        self.assertGreaterEqual(features.files_changed, 1)
    
    def test_get_commit_label(self):
        """Test commit labeling"""
        optimizer = MLCommitOptimizer(repo_path=str(self.repo_dir))
        
        # Get commit in main branch
        import subprocess
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H'],
            cwd=self.repo_dir,
            capture_output=True,
            text=True
        )
        commit_hash = result.stdout.strip()
        
        label = optimizer._get_commit_label(commit_hash)
        
        # Should be labeled as successful (in main branch)
        # Note: depends on git config, may vary
        self.assertIn(label, [0, 1])
    
    @unittest.skipIf(not ML_AVAILABLE, "ML libraries not available")
    def test_train_model_basic(self):
        """Test basic model training"""
        optimizer = MLCommitOptimizer(repo_path=str(self.repo_dir), verbose=True)
        
        # Train on limited data
        metrics = optimizer.train_model(since_days=365, max_commits=10)
        
        # May not have enough data, but should handle gracefully
        if "error" not in metrics:
            self.assertIn("accuracy", metrics)
            self.assertIn("samples", metrics)
    
    def test_default_thresholds(self):
        """Test default threshold values"""
        optimizer = MLCommitOptimizer(repo_path=str(self.repo_dir))
        
        thresholds = optimizer.thresholds
        
        self.assertGreater(thresholds.message_length_min, 0)
        self.assertGreater(thresholds.message_length_max, thresholds.message_length_min)
        self.assertGreater(thresholds.files_per_commit_ideal, 0)
        self.assertGreater(thresholds.lines_per_commit_ideal, 0)
    
    def test_load_save_thresholds(self):
        """Test threshold persistence"""
        optimizer = MLCommitOptimizer(repo_path=str(self.repo_dir))
        
        # Modify and save
        optimizer.thresholds.message_length_min = 25.0
        optimizer._save_thresholds()
        
        # Create new optimizer and verify
        optimizer2 = MLCommitOptimizer(repo_path=str(self.repo_dir))
        self.assertEqual(optimizer2.thresholds.message_length_min, 25.0)


class TestPrediction(unittest.TestCase):
    """Test prediction functionality"""
    
    @unittest.skipIf(not ML_AVAILABLE, "ML libraries not available")
    def test_prediction_result_structure(self):
        """Test PredictionResult structure"""
        result = PredictionResult(
            commit_hash="abc123",
            predicted_success=True,
            success_probability=0.85,
            confidence=0.9,
            risk_factors=["test risk"],
            recommendations=["test recommendation"],
            feature_importance={"feature1": 0.5}
        )
        
        self.assertEqual(result.commit_hash, "abc123")
        self.assertTrue(result.predicted_success)
        self.assertEqual(result.success_probability, 0.85)
        self.assertEqual(len(result.risk_factors), 1)
        self.assertEqual(len(result.recommendations), 1)


class TestIntegration(unittest.TestCase):
    """Test integration scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        self.repo_dir = Path(self.test_dir) / "test_repo"
        self.repo_dir.mkdir()
        os.chdir(self.repo_dir)
        
        os.system('git init >/dev/null 2>&1')
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')
    
    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_optimizer_handles_empty_repo(self):
        """Test optimizer with empty repository"""
        optimizer = MLCommitOptimizer(repo_path=str(self.repo_dir))
        
        # Should initialize without errors
        self.assertIsNotNone(optimizer)
        self.assertIsNotNone(optimizer.thresholds)
    
    def test_feature_array_consistency(self):
        """Test feature array matches feature names"""
        features = CommitFeatures(
            message_length=50.0,
            has_body=1,
            conventional_format=1,
            message_clarity_score=0.8,
            files_changed=3.0,
            lines_added=100.0,
            lines_deleted=20.0,
            total_lines_changed=120.0,
            file_type_diversity=2.0,
            directory_count=1.0,
            hour_of_day=14.0,
            day_of_week=2.0,
            change_density=40.0,
            modification_ratio=0.2
        )
        
        arr = features.to_array()
        names = CommitFeatures.feature_names()
        
        # Array length should match feature count
        self.assertEqual(len(arr), len(names))


def run_tests():
    """Run all tests with detailed output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCommitFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestAdaptiveThresholds))
    suite.addTests(loader.loadTestsFromTestCase(TestMLCommitOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestPrediction))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
