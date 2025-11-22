#!/usr/bin/env python3
"""
Tests for Universal Truth Evaluator

Tests the discovery, validation, and insight generation capabilities
of the universal truth evaluation system.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.universal_truth_evaluator import (
    UniversalTruthEvaluator,
    UniversalTruth
)


class TestUniversalTruthEvaluator(unittest.TestCase):
    """Test suite for Universal Truth Evaluator."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory structure
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create directory structure
        (self.test_path / "world").mkdir()
        (self.test_path / "learnings").mkdir()
        (self.test_path / "learnings" / "discussions").mkdir()
        (self.test_path / "analysis").mkdir()
        
        # Create test data
        self._create_test_world_state()
        self._create_test_learnings()
        self._create_test_collaborations()
        self._create_test_analysis()
        
        # Initialize evaluator
        self.evaluator = UniversalTruthEvaluator(repo_root=self.test_path)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def _create_test_world_state(self):
        """Create test world state data."""
        world_state = {
            "time": datetime.now().isoformat(),
            "tick": 42,
            "agents": [
                {
                    "id": "agent-1",
                    "specialization": "engineer-master",
                    "location_region_id": "US:Charlotte",
                    "status": "exploring",
                    "metrics": {
                        "overall_score": 0.85,
                        "issues_resolved": 5,
                        "prs_merged": 3
                    }
                },
                {
                    "id": "agent-2",
                    "specialization": "secure-specialist",
                    "location_region_id": "US:San Francisco",
                    "status": "working",
                    "metrics": {
                        "overall_score": 0.72,
                        "issues_resolved": 3,
                        "prs_merged": 2
                    }
                },
                {
                    "id": "agent-3",
                    "specialization": "organize-guru",
                    "location_region_id": "US:Charlotte",
                    "status": "exploring",
                    "metrics": {
                        "overall_score": 0.35,
                        "issues_resolved": 1,
                        "prs_merged": 0
                    }
                },
                {
                    "id": "agent-4",
                    "specialization": "test-specialist",
                    "location_region_id": "EU:London",
                    "status": "exploring",
                    "metrics": {
                        "overall_score": 0.91,
                        "issues_resolved": 8,
                        "prs_merged": 7
                    }
                }
            ]
        }
        
        with open(self.test_path / "world" / "world_state.json", 'w') as f:
            json.dump(world_state, f, indent=2)
    
    def _create_test_learnings(self):
        """Create test learning data."""
        # Create learning files with dates
        dates = [
            (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
            for i in range(10)
        ]
        
        for date in dates:
            learning_file = self.test_path / "learnings" / f"hn_{date}.json"
            with open(learning_file, 'w') as f:
                json.dump({"articles": [{"title": "Test", "date": date}]}, f)
        
        # Create knowledge graph
        knowledge_graph = {
            "insights": {
                f"insight_{i}": {
                    "content": f"Test insight {i}",
                    "confidence": 0.8
                }
                for i in range(5)
            },
            "connections": [
                {"from": "insight_0", "to": "insight_1"},
                {"from": "insight_1", "to": "insight_2"},
                {"from": "insight_2", "to": "insight_3"}
            ]
        }
        
        kg_file = self.test_path / "learnings" / "discussions" / "knowledge_graph.json"
        with open(kg_file, 'w') as f:
            json.dump(knowledge_graph, f, indent=2)
    
    def _create_test_collaborations(self):
        """Create test collaboration data."""
        collaborations = {
            "collaborations": {
                "collab_1": {
                    "agents": ["agent-1", "agent-2"],
                    "status": "active"
                },
                "collab_2": {
                    "agents": ["agent-1", "agent-3"],
                    "status": "active"
                },
                "collab_3": {
                    "agents": ["agent-2", "agent-4"],
                    "status": "active"
                }
            }
        }
        
        with open(self.test_path / "world" / "agent_collaborations.json", 'w') as f:
            json.dump(collaborations, f, indent=2)
    
    def _create_test_analysis(self):
        """Create test analysis data."""
        patterns = {
            "pattern_1": {"type": "workflow", "frequency": 10},
            "pattern_2": {"type": "code", "frequency": 5}
        }
        
        with open(self.test_path / "analysis" / "actions-patterns.json", 'w') as f:
            json.dump(patterns, f, indent=2)
    
    def test_initialization(self):
        """Test evaluator initialization."""
        self.assertIsNotNone(self.evaluator)
        self.assertEqual(self.evaluator.repo_root, self.test_path)
        self.assertTrue(self.evaluator.world_dir.exists())
    
    def test_discover_agent_truths(self):
        """Test discovery of agent behavior truths."""
        truths = self.evaluator.discover_truths_from_agents()
        
        self.assertGreater(len(truths), 0, "Should discover at least one truth")
        
        # Check for specific truths
        truth_ids = [t.truth_id for t in truths]
        self.assertIn('agent_performance_distribution', truth_ids)
        self.assertIn('specialization_diversity', truth_ids)
        
        # Verify truth properties
        for truth in truths:
            self.assertIsInstance(truth, UniversalTruth)
            self.assertGreater(truth.confidence, 0)
            self.assertLessEqual(truth.confidence, 1.0)
            self.assertIn(truth.category, ['agent_behavior', 'system_dynamics', 'collaboration', 'evolution'])
    
    def test_discover_learning_truths(self):
        """Test discovery of learning pattern truths."""
        truths = self.evaluator.discover_truths_from_learnings()
        
        self.assertGreater(len(truths), 0, "Should discover learning truths")
        
        # Check for learning-specific truths
        truth_ids = [t.truth_id for t in truths]
        self.assertTrue(
            any('learning' in tid for tid in truth_ids),
            "Should have learning-related truths"
        )
    
    def test_discover_collaboration_truths(self):
        """Test discovery of collaboration truths."""
        truths = self.evaluator.discover_truths_from_collaboration()
        
        self.assertGreater(len(truths), 0, "Should discover collaboration truths")
        
        for truth in truths:
            self.assertEqual(truth.category, 'collaboration')
    
    def test_discover_analysis_truths(self):
        """Test discovery of truths from analysis data."""
        truths = self.evaluator.discover_truths_from_analysis()
        
        self.assertGreater(len(truths), 0, "Should discover analysis truths")
        
        # Check for pattern-related truths
        truth_ids = [t.truth_id for t in truths]
        self.assertTrue(
            any('pattern' in tid for tid in truth_ids),
            "Should have pattern-related truths"
        )
    
    def test_truth_validation(self):
        """Test truth validation mechanism."""
        # Create a test truth
        truth = self.evaluator._create_or_update_truth(
            'test_truth',
            'agent_behavior',
            'Test statement',
            0.7,
            {'test': 'data'}
        )
        
        # Validate it
        is_valid, new_confidence = self.evaluator.validate_truth(
            'test_truth',
            {'validation': 'data'}
        )
        
        self.assertTrue(is_valid)
        self.assertGreater(new_confidence, 0.7, "Confidence should increase")
        self.assertEqual(self.evaluator.truths['test_truth'].evidence_count, 2)
    
    def test_truth_challenge(self):
        """Test truth challenge mechanism."""
        # Create a test truth
        truth = self.evaluator._create_or_update_truth(
            'test_truth',
            'agent_behavior',
            'Test statement',
            0.7,
            {'test': 'data'}
        )
        
        initial_confidence = truth.confidence
        
        # Challenge it
        new_confidence = self.evaluator.challenge_truth(
            'test_truth',
            {'counter': 'evidence'}
        )
        
        self.assertLess(new_confidence, initial_confidence, "Confidence should decrease")
        self.assertGreater(len(self.evaluator.truths['test_truth'].counter_examples), 0)
    
    def test_truth_persistence(self):
        """Test saving and loading truths."""
        # Create some truths
        self.evaluator._create_or_update_truth(
            'test_truth_1',
            'agent_behavior',
            'Test statement 1',
            0.8,
            {'test': 'data'}
        )
        
        # Save
        self.evaluator._save_truths()
        
        # Create new evaluator and load
        new_evaluator = UniversalTruthEvaluator(repo_root=self.test_path)
        
        self.assertIn('test_truth_1', new_evaluator.truths)
        self.assertEqual(new_evaluator.truths['test_truth_1'].confidence, 0.8)
    
    def test_truth_relationships(self):
        """Test relationship discovery between truths."""
        # Create multiple truths in same category
        self.evaluator._create_or_update_truth(
            'truth_1',
            'agent_behavior',
            'Statement 1',
            0.8,
            {}
        )
        self.evaluator._create_or_update_truth(
            'truth_2',
            'agent_behavior',
            'Statement 2',
            0.7,
            {}
        )
        
        # Discover relationships
        self.evaluator.discover_relationships()
        
        # Check relationships
        truth1 = self.evaluator.truths['truth_1']
        truth2 = self.evaluator.truths['truth_2']
        
        self.assertIn('truth_2', truth1.related_truths)
        self.assertIn('truth_1', truth2.related_truths)
    
    def test_insight_generation(self):
        """Test insight generation."""
        # Run discovery
        self.evaluator.discover_truths_from_agents()
        
        # Generate insights
        insights = self.evaluator.generate_insights()
        
        self.assertIn('timestamp', insights)
        self.assertIn('total_truths', insights)
        self.assertIn('stable_truths', insights)
        self.assertIn('key_discoveries', insights)
        self.assertIn('recommendations', insights)
        self.assertIn('meta_observations', insights)
        
        self.assertGreater(insights['total_truths'], 0)
        self.assertIsInstance(insights['key_discoveries'], list)
        self.assertIsInstance(insights['recommendations'], list)
        self.assertIsInstance(insights['meta_observations'], list)
    
    def test_full_discovery_cycle(self):
        """Test complete discovery cycle."""
        insights = self.evaluator.run_full_discovery()
        
        self.assertIsInstance(insights, dict)
        self.assertGreater(insights['total_truths'], 0)
        
        # Verify truths were saved
        self.assertTrue(self.evaluator.truths_file.exists())
    
    def test_truth_stability(self):
        """Test truth stability detection."""
        # Create stable truth (no counter-examples, high confidence)
        stable_truth = UniversalTruth(
            truth_id='stable',
            category='agent_behavior',
            statement='Stable statement',
            confidence=0.9,
            evidence_count=10,
            first_observed=datetime.now().isoformat(),
            last_validated=datetime.now().isoformat(),
            supporting_data=[],
            counter_examples=[],
            evolution_history=[],
            related_truths=[]
        )
        
        self.assertTrue(stable_truth.is_stable())
        
        # Create unstable truth
        unstable_truth = UniversalTruth(
            truth_id='unstable',
            category='agent_behavior',
            statement='Unstable statement',
            confidence=0.5,
            evidence_count=2,
            first_observed=datetime.now().isoformat(),
            last_validated=datetime.now().isoformat(),
            supporting_data=[],
            counter_examples=[{'data': 'counter'}],
            evolution_history=[],
            related_truths=[]
        )
        
        self.assertFalse(unstable_truth.is_stable())
    
    def test_truth_revalidation_needed(self):
        """Test revalidation detection."""
        # Create old truth
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        old_truth = UniversalTruth(
            truth_id='old',
            category='agent_behavior',
            statement='Old statement',
            confidence=0.8,
            evidence_count=5,
            first_observed=old_date,
            last_validated=old_date,
            supporting_data=[],
            counter_examples=[],
            evolution_history=[],
            related_truths=[]
        )
        
        self.assertTrue(old_truth.needs_revalidation(days=7))
        
        # Create recent truth
        recent_truth = UniversalTruth(
            truth_id='recent',
            category='agent_behavior',
            statement='Recent statement',
            confidence=0.8,
            evidence_count=5,
            first_observed=datetime.now().isoformat(),
            last_validated=datetime.now().isoformat(),
            supporting_data=[],
            counter_examples=[],
            evolution_history=[],
            related_truths=[]
        )
        
        self.assertFalse(recent_truth.needs_revalidation(days=7))


class TestTruthCategories(unittest.TestCase):
    """Test truth categorization and classification."""
    
    def test_category_distribution(self):
        """Test category distribution calculation."""
        test_dir = tempfile.mkdtemp()
        test_path = Path(test_dir)
        (test_path / "world").mkdir()
        (test_path / "learnings").mkdir()
        (test_path / "analysis").mkdir()
        
        evaluator = UniversalTruthEvaluator(repo_root=test_path)
        
        # Create truths in different categories
        evaluator._create_or_update_truth('t1', 'agent_behavior', 'S1', 0.8, {})
        evaluator._create_or_update_truth('t2', 'agent_behavior', 'S2', 0.7, {})
        evaluator._create_or_update_truth('t3', 'system_dynamics', 'S3', 0.9, {})
        evaluator._create_or_update_truth('t4', 'collaboration', 'S4', 0.75, {})
        
        dist = evaluator._get_category_distribution()
        
        self.assertEqual(dist['agent_behavior'], 2)
        self.assertEqual(dist['system_dynamics'], 1)
        self.assertEqual(dist['collaboration'], 1)
        
        shutil.rmtree(test_dir)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()
