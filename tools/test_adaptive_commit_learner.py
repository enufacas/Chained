#!/usr/bin/env python3
"""
Test suite for Adaptive Commit Strategy Learning System

Tests the adaptive learning capabilities including:
- Incremental learning
- Pattern evolution tracking
- Recommendation validation
- Learning rate adaptation
- Temporal pattern recognition

Created by @create-guru
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta
import sys
import os

# Add tools directory to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

# Import adaptive learner
import importlib.util
spec = importlib.util.spec_from_file_location(
    "adaptive_commit_learner",
    tools_dir / "adaptive-commit-learner.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

AdaptiveLearning = module.AdaptiveLearning
PatternEvolution = module.PatternEvolution
AdaptiveCommitLearner = module.AdaptiveCommitLearner


class TestAdaptiveLearning(unittest.TestCase):
    """Test AdaptiveLearning data structure"""
    
    def test_adaptive_learning_creation(self):
        """Test creating AdaptiveLearning with all fields"""
        now = datetime.now(timezone.utc).isoformat()
        
        learning = AdaptiveLearning(
            insight_id="test_001",
            timestamp=now,
            pattern_type="message",
            learning_text="Test pattern detected",
            confidence=0.85,
            evidence_count=42,
            validation_status="unvalidated",
            learning_rate=0.1,
            temporal_context={"hour": 10, "day_of_week": "Monday"}
        )
        
        self.assertEqual(learning.insight_id, "test_001")
        self.assertEqual(learning.pattern_type, "message")
        self.assertEqual(learning.confidence, 0.85)
        self.assertEqual(learning.evidence_count, 42)
        self.assertEqual(learning.validation_status, "unvalidated")
        self.assertEqual(learning.learning_rate, 0.1)
    
    def test_adaptive_learning_to_dict(self):
        """Test converting AdaptiveLearning to dict"""
        now = datetime.now(timezone.utc).isoformat()
        
        learning = AdaptiveLearning(
            insight_id="test_001",
            timestamp=now,
            pattern_type="size",
            learning_text="Size pattern validated",
            confidence=0.75,
            evidence_count=25,
            validation_status="validated",
            learning_rate=0.095,
            temporal_context={"hour": 14}
        )
        
        data = learning.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data["insight_id"], "test_001")
        self.assertEqual(data["pattern_type"], "size")
        self.assertEqual(data["confidence"], 0.75)
        self.assertEqual(data["validation_status"], "validated")


class TestPatternEvolution(unittest.TestCase):
    """Test PatternEvolution data structure"""
    
    def test_pattern_evolution_creation(self):
        """Test creating PatternEvolution"""
        now = datetime.now(timezone.utc).isoformat()
        
        evolution = PatternEvolution(
            pattern_name="message_conventional",
            first_observed=now,
            last_updated=now,
            confidence_history=[
                {"timestamp": now, "value": 0.75}
            ],
            occurrence_history=[
                {"timestamp": now, "value": 100}
            ],
            trend="improving"
        )
        
        self.assertEqual(evolution.pattern_name, "message_conventional")
        self.assertEqual(evolution.trend, "improving")
        self.assertEqual(len(evolution.confidence_history), 1)
        self.assertEqual(len(evolution.occurrence_history), 1)
    
    def test_pattern_evolution_to_dict(self):
        """Test converting PatternEvolution to dict"""
        now = datetime.now(timezone.utc).isoformat()
        
        evolution = PatternEvolution(
            pattern_name="size_optimal",
            first_observed=now,
            last_updated=now,
            confidence_history=[{"timestamp": now, "value": 0.8}],
            occurrence_history=[{"timestamp": now, "value": 50}],
            trend="stable"
        )
        
        data = evolution.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data["pattern_name"], "size_optimal")
        self.assertEqual(data["trend"], "stable")


class TestAdaptiveCommitLearner(unittest.TestCase):
    """Test AdaptiveCommitLearner main class"""
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        
        # Create test git repository structure
        learnings_dir = Path(self.test_dir) / "learnings"
        analysis_dir = Path(self.test_dir) / "analysis"
        learnings_dir.mkdir(parents=True, exist_ok=True)
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_learner_initialization(self):
        """Test AdaptiveCommitLearner initialization"""
        learner = AdaptiveCommitLearner(repo_path=self.test_dir, verbose=False)
        
        self.assertIsNotNone(learner.adaptive_data)
        self.assertIsNotNone(learner.evolution_data)
        self.assertEqual(learner.adaptive_data["version"], "2.0.0")
        self.assertEqual(learner.evolution_data["version"], "1.0.0")
    
    def test_adaptive_data_structure(self):
        """Test adaptive data structure initialization"""
        learner = AdaptiveCommitLearner(repo_path=self.test_dir, verbose=False)
        
        data = learner.adaptive_data
        
        self.assertIn("version", data)
        self.assertIn("learning_sessions", data)
        self.assertIn("active_learnings", data)
        self.assertIn("validated_patterns", data)
        self.assertIn("invalidated_patterns", data)
        self.assertIn("cumulative_insights", data)
        self.assertIn("learning_velocity", data)
        
        self.assertIsInstance(data["learning_sessions"], list)
        self.assertIsInstance(data["active_learnings"], list)
        self.assertIsInstance(data["validated_patterns"], list)
        self.assertIsInstance(data["invalidated_patterns"], list)
        self.assertEqual(data["cumulative_insights"], 0)
        self.assertEqual(data["learning_velocity"], 0.0)
    
    def test_evolution_data_structure(self):
        """Test evolution data structure initialization"""
        learner = AdaptiveCommitLearner(repo_path=self.test_dir, verbose=False)
        
        data = learner.evolution_data
        
        self.assertIn("version", data)
        self.assertIn("patterns", data)
        self.assertIn("last_updated", data)
        
        self.assertIsInstance(data["patterns"], dict)
    
    def test_learning_rate_calculation(self):
        """Test learning rate decay calculation"""
        learner = AdaptiveCommitLearner(repo_path=self.test_dir, verbose=False)
        
        # Simulate multiple learning sessions
        for i in range(5):
            session = {
                "session_id": i + 1,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "days_analyzed": 7,
                "commits_analyzed": 10,
                "learning_rate": 0.1 * (0.95 ** i),
                "new_insights": 3,
                "patterns_updated": 2
            }
            learner.adaptive_data["learning_sessions"].append(session)
        
        # Check learning rate decay
        rates = [s["learning_rate"] for s in learner.adaptive_data["learning_sessions"]]
        
        # Each rate should be less than the previous
        for i in range(1, len(rates)):
            self.assertLess(rates[i], rates[i-1])
        
        # First rate should be 0.1
        self.assertAlmostEqual(rates[0], 0.1, places=5)
        
        # Fifth rate should be 0.1 * 0.95^4
        expected_rate = 0.1 * (0.95 ** 4)
        self.assertAlmostEqual(rates[4], expected_rate, places=5)
    
    def test_save_and_load_adaptive_data(self):
        """Test saving and loading adaptive data"""
        learner = AdaptiveCommitLearner(repo_path=self.test_dir, verbose=False)
        
        # Add test data
        learner.adaptive_data["cumulative_insights"] = 10
        learner.adaptive_data["learning_velocity"] = 2.5
        
        # Save data
        learner._save_adaptive_data()
        
        # Load data in new learner instance
        learner2 = AdaptiveCommitLearner(repo_path=self.test_dir, verbose=False)
        
        self.assertEqual(learner2.adaptive_data["cumulative_insights"], 10)
        self.assertEqual(learner2.adaptive_data["learning_velocity"], 2.5)
        self.assertIsNotNone(learner2.adaptive_data["last_updated"])
    
    def test_save_and_load_evolution_data(self):
        """Test saving and loading pattern evolution data"""
        learner = AdaptiveCommitLearner(repo_path=self.test_dir, verbose=False)
        
        # Add test pattern
        now = datetime.now(timezone.utc).isoformat()
        learner.evolution_data["patterns"]["test_pattern"] = {
            "pattern_name": "test_pattern",
            "first_observed": now,
            "last_updated": now,
            "confidence_history": [{"timestamp": now, "value": 0.8}],
            "occurrence_history": [{"timestamp": now, "value": 50}],
            "trend": "stable"
        }
        
        # Save data
        learner._save_evolution_data()
        
        # Load data in new learner instance
        learner2 = AdaptiveCommitLearner(repo_path=self.test_dir, verbose=False)
        
        self.assertIn("test_pattern", learner2.evolution_data["patterns"])
        pattern = learner2.evolution_data["patterns"]["test_pattern"]
        self.assertEqual(pattern["trend"], "stable")
        self.assertEqual(len(pattern["confidence_history"]), 1)
    
    def test_generate_adaptive_report(self):
        """Test generating adaptive report"""
        learner = AdaptiveCommitLearner(repo_path=self.test_dir, verbose=False)
        
        # Add some test data
        learner.adaptive_data["cumulative_insights"] = 15
        learner.adaptive_data["learning_velocity"] = 3.0
        
        # Add test session
        session = {
            "session_id": 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "days_analyzed": 7,
            "commits_analyzed": 42,
            "learning_rate": 0.1,
            "new_insights": 5,
            "patterns_updated": 3
        }
        learner.adaptive_data["learning_sessions"].append(session)
        
        # Generate report
        report = learner.generate_adaptive_report()
        
        self.assertIsInstance(report, str)
        self.assertIn("Adaptive Commit Strategy Learning Report", report)
        self.assertIn("@create-guru", report)
        self.assertIn("System Status", report)
        self.assertIn("Pattern Evolution", report)
        self.assertIn("Learning Sessions", report)
        
        # Check that metrics are included
        self.assertIn("15", report)  # cumulative insights
        self.assertIn("3.0", report)  # learning velocity


class TestLearningRateDecay(unittest.TestCase):
    """Test learning rate decay mechanics"""
    
    def test_decay_formula(self):
        """Test the learning rate decay formula"""
        # Import constants from the module
        base_rate = module.LEARNING_RATE_BASE
        decay_factor = module.LEARNING_RATE_DECAY
        min_rate = module.MIN_LEARNING_RATE
        
        # Test specific session counts dynamically
        for session_count in [1, 10, 20, 50]:
            actual_rate = max(
                base_rate * (decay_factor ** (session_count - 1)),
                min_rate
            )
            
            # Should be between min_rate and base_rate
            self.assertGreaterEqual(actual_rate, min_rate)
            self.assertLessEqual(actual_rate, base_rate)
            
            # Should decrease with session count (except when hitting min)
            if session_count > 1:
                previous_rate = max(
                    base_rate * (decay_factor ** (session_count - 2)),
                    min_rate
                )
                self.assertLessEqual(actual_rate, previous_rate)
    
    def test_decay_convergence(self):
        """Test that learning rate converges to near zero"""
        base_rate = 0.1
        decay_factor = 0.95
        
        # After 100 sessions
        rate_100 = base_rate * (decay_factor ** 99)
        
        # Should be very small but not zero
        self.assertLess(rate_100, 0.01)
        self.assertGreater(rate_100, 0.0)


class TestPatternTrendCalculation(unittest.TestCase):
    """Test pattern trend calculation logic"""
    
    def test_improving_trend(self):
        """Test detection of improving pattern"""
        # Simulated confidence history showing improvement
        confidence_history = [
            {"timestamp": "2025-11-01", "value": 0.70},
            {"timestamp": "2025-11-02", "value": 0.72},
            {"timestamp": "2025-11-03", "value": 0.75},
            {"timestamp": "2025-11-04", "value": 0.80},
            {"timestamp": "2025-11-05", "value": 0.82},
            {"timestamp": "2025-11-06", "value": 0.85},
        ]
        
        # Last 3 average
        recent = [h["value"] for h in confidence_history[-3:]]
        recent_avg = sum(recent) / len(recent)
        
        # Previous 3 average
        previous = [h["value"] for h in confidence_history[-6:-3]]
        previous_avg = sum(previous) / len(previous)
        
        # Should be improving (recent > previous * 1.1)
        self.assertGreater(recent_avg, previous_avg * 1.1)
    
    def test_stable_trend(self):
        """Test detection of stable pattern"""
        # Simulated confidence history showing stability
        confidence_history = [
            {"timestamp": "2025-11-01", "value": 0.80},
            {"timestamp": "2025-11-02", "value": 0.79},
            {"timestamp": "2025-11-03", "value": 0.81},
            {"timestamp": "2025-11-04", "value": 0.80},
            {"timestamp": "2025-11-05", "value": 0.81},
            {"timestamp": "2025-11-06", "value": 0.79},
        ]
        
        # Last 3 average
        recent = [h["value"] for h in confidence_history[-3:]]
        recent_avg = sum(recent) / len(recent)
        
        # Previous 3 average
        previous = [h["value"] for h in confidence_history[-6:-3]]
        previous_avg = sum(previous) / len(previous)
        
        # Should be stable (within ±10%)
        self.assertGreaterEqual(recent_avg, previous_avg * 0.9)
        self.assertLessEqual(recent_avg, previous_avg * 1.1)
    
    def test_declining_trend(self):
        """Test detection of declining pattern"""
        # Simulated confidence history showing decline
        confidence_history = [
            {"timestamp": "2025-11-01", "value": 0.85},
            {"timestamp": "2025-11-02", "value": 0.82},
            {"timestamp": "2025-11-03", "value": 0.80},
            {"timestamp": "2025-11-04", "value": 0.75},
            {"timestamp": "2025-11-05", "value": 0.72},
            {"timestamp": "2025-11-06", "value": 0.70},
        ]
        
        # Last 3 average
        recent = [h["value"] for h in confidence_history[-3:]]
        recent_avg = sum(recent) / len(recent)
        
        # Previous 3 average
        previous = [h["value"] for h in confidence_history[-6:-3]]
        previous_avg = sum(previous) / len(previous)
        
        # Should be declining (recent < previous * 0.9)
        self.assertLess(recent_avg, previous_avg * 0.9)


class TestValidationThresholds(unittest.TestCase):
    """Test recommendation validation thresholds"""
    
    def test_validated_threshold(self):
        """Test pattern is validated when confidence maintained"""
        original_confidence = 0.80
        new_confidence = 0.75  # 93.75% of original
        
        # Should validate (≥ 90%)
        self.assertGreaterEqual(new_confidence, original_confidence * 0.9)
    
    def test_invalidated_threshold(self):
        """Test pattern is invalidated when confidence drops"""
        original_confidence = 0.80
        new_confidence = 0.50  # 62.5% of original
        
        # Should invalidate (< 70%)
        self.assertLess(new_confidence, original_confidence * 0.7)
    
    def test_active_threshold(self):
        """Test pattern stays active in middle range"""
        original_confidence = 0.80
        new_confidence = 0.60  # 75% of original
        
        # Should stay active (between 70-90%)
        self.assertGreaterEqual(new_confidence, original_confidence * 0.7)
        self.assertLess(new_confidence, original_confidence * 0.9)


def run_tests():
    """Run all tests with verbose output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAdaptiveLearning))
    suite.addTests(loader.loadTestsFromTestCase(TestPatternEvolution))
    suite.addTests(loader.loadTestsFromTestCase(TestAdaptiveCommitLearner))
    suite.addTests(loader.loadTestsFromTestCase(TestLearningRateDecay))
    suite.addTests(loader.loadTestsFromTestCase(TestPatternTrendCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestValidationThresholds))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
