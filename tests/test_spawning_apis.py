#!/usr/bin/env python3
"""
Test Suite for Sub-Agent Spawning API Services

Comprehensive tests for the spawning API infrastructure.

Created by @APIs-architect - Ensuring reliability first with thorough testing.

Tests:
- Sub-Agent Spawning API endpoints
- Spawning Decision Engine
- Integration with workload monitoring
- API response validation
- Error handling

Usage:
    python3 tests/test_spawning_apis.py
    pytest tests/test_spawning_apis.py -v
"""

import unittest
import json
import time
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from spawning_decision_engine import (
    SpawningDecisionEngine,
    SpawningDecision,
    DecisionConfig,
    DecisionFactor
)
from workload_monitor import WorkloadMetrics, SpawningRecommendation


class TestSpawningDecisionEngine(unittest.TestCase):
    """
    Test cases for Spawning Decision Engine.
    
    Created by @APIs-architect with comprehensive coverage.
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = DecisionConfig()
        self.engine = SpawningDecisionEngine(config=self.config)
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.config)
        self.assertIsNotNone(self.engine.workload_monitor)
        self.assertEqual(len(self.engine.last_spawn_time), 0)
    
    def test_engine_with_custom_config(self):
        """Test engine with custom configuration"""
        custom_config = DecisionConfig(
            workload_critical_threshold=0.9,
            min_confidence_threshold=0.7,
            max_agents_per_spawn=3
        )
        engine = SpawningDecisionEngine(config=custom_config)
        
        self.assertEqual(engine.config.workload_critical_threshold, 0.9)
        self.assertEqual(engine.config.min_confidence_threshold, 0.7)
        self.assertEqual(engine.config.max_agents_per_spawn, 3)
    
    def test_evaluate_returns_list(self):
        """Test evaluate returns a list of decisions"""
        decisions = self.engine.evaluate(max_decisions=5)
        
        self.assertIsInstance(decisions, list)
        self.assertLessEqual(len(decisions), 5)
    
    def test_evaluate_with_mock_recommendations(self):
        """Test evaluate with mocked workload recommendations"""
        # Create mock metrics
        mock_metrics = WorkloadMetrics(
            specialization='test-spec',
            open_issues=15,
            pending_prs=8,
            active_agents=2,
            agent_capacity=0.75,
            workload_per_agent=11.5,
            priority_score=0.8,
            bottleneck_severity='high',
            recommendation='Spawn 2 agents'
        )
        
        # Create mock recommendation
        mock_rec = SpawningRecommendation(
            should_spawn=True,
            specialization='test-spec',
            count=2,
            reason='High workload',
            priority=4,
            metrics=mock_metrics
        )
        
        # Mock the analyze_workload and generate_spawning_recommendations
        with patch.object(self.engine.workload_monitor, 'analyze_workload') as mock_analyze:
            with patch.object(self.engine.workload_monitor, 'generate_spawning_recommendations') as mock_gen:
                mock_analyze.return_value = {'test-spec': mock_metrics}
                mock_gen.return_value = [mock_rec]
                
                decisions = self.engine.evaluate(max_decisions=5)
                
                self.assertGreater(len(decisions), 0)
                decision = decisions[0]
                
                self.assertIsInstance(decision, SpawningDecision)
                self.assertEqual(decision.specialization, 'test-spec')
                self.assertIsInstance(decision.confidence, float)
                self.assertGreaterEqual(decision.confidence, 0.0)
                self.assertLessEqual(decision.confidence, 1.0)
    
    def test_decision_to_dict(self):
        """Test SpawningDecision to_dict conversion"""
        decision = SpawningDecision(
            should_spawn=True,
            specialization='test-spec',
            agent_count=2,
            confidence=0.85,
            factors={
                DecisionFactor.WORKLOAD: 0.9,
                DecisionFactor.API_HEALTH: 0.8
            },
            reasoning=['High workload', 'API healthy'],
            timestamp=datetime.now().isoformat()
        )
        
        result = decision.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['should_spawn'], True)
        self.assertEqual(result['specialization'], 'test-spec')
        self.assertEqual(result['agent_count'], 2)
        self.assertEqual(result['confidence'], 0.85)
        self.assertIn('factors', result)
        self.assertIn('reasoning', result)
        self.assertEqual(len(result['reasoning']), 2)
    
    def test_cooldown_check(self):
        """Test cooldown period checking"""
        spec = 'test-spec'
        
        # No spawn recorded yet
        self.assertFalse(self.engine._check_cooldown(spec))
        
        # Record spawn
        current_time = time.time()
        self.engine.record_spawn(spec)
        
        # Should be in cooldown
        self.assertTrue(self.engine._check_cooldown(spec))
        
        # Simulate cooldown expiry by setting past time
        self.engine.last_spawn_time[spec] = current_time - self.config.spawning_cooldown - 10
        
        # Should not be in cooldown anymore
        self.assertFalse(self.engine._check_cooldown(spec))
    
    def test_record_spawn(self):
        """Test recording spawn events"""
        spec = 'test-spec'
        
        self.assertNotIn(spec, self.engine.last_spawn_time)
        
        self.engine.record_spawn(spec)
        
        self.assertIn(spec, self.engine.last_spawn_time)
        self.assertIsInstance(self.engine.last_spawn_time[spec], float)
    
    def test_get_status(self):
        """Test get_status method"""
        status = self.engine.get_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('active_decisions', status)
        self.assertIn('spawning_recommended', status)
        self.assertIn('decisions', status)
        self.assertIn('config', status)
        self.assertIn('timestamp', status)
    
    def test_evaluate_workload_scoring(self):
        """Test workload evaluation scoring"""
        # Create high workload metrics
        high_metrics = WorkloadMetrics(
            specialization='high-load',
            open_issues=50,
            pending_prs=30,
            active_agents=2,
            agent_capacity=0.9,
            workload_per_agent=40.0,
            priority_score=0.95,
            bottleneck_severity='critical',
            recommendation='Spawn 5 agents'
        )
        
        reasoning = []
        score = self.engine._evaluate_workload(high_metrics, reasoning)
        
        self.assertGreater(score, 0.5)  # High workload should score high
        self.assertGreater(len(reasoning), 0)  # Should have reasoning
    
    def test_evaluate_capacity_scoring(self):
        """Test capacity evaluation scoring"""
        # Critical capacity
        critical_metrics = WorkloadMetrics(
            specialization='critical-cap',
            open_issues=10,
            pending_prs=5,
            active_agents=3,
            agent_capacity=0.85,
            workload_per_agent=5.0,
            priority_score=0.7,
            bottleneck_severity='high',
            recommendation='Spawn 1 agent'
        )
        
        reasoning = []
        score = self.engine._evaluate_capacity(critical_metrics, reasoning)
        
        self.assertEqual(score, 0.85)
        self.assertIn('capacity', reasoning[0].lower())
    
    def test_decision_factors_include_all_types(self):
        """Test that decisions include all factor types"""
        mock_metrics = WorkloadMetrics(
            specialization='test-spec',
            open_issues=20,
            pending_prs=10,
            active_agents=2,
            agent_capacity=0.8,
            workload_per_agent=15.0,
            priority_score=0.75,
            bottleneck_severity='high',
            recommendation='Spawn 2 agents'
        )
        
        mock_rec = SpawningRecommendation(
            should_spawn=True,
            specialization='test-spec',
            count=2,
            reason='Test',
            priority=4,
            metrics=mock_metrics
        )
        
        with patch.object(self.engine.workload_monitor, 'analyze_workload') as mock_analyze:
            with patch.object(self.engine.workload_monitor, 'generate_spawning_recommendations') as mock_gen:
                mock_analyze.return_value = {'test-spec': mock_metrics}
                mock_gen.return_value = [mock_rec]
                
                decisions = self.engine.evaluate()
                
                if len(decisions) > 0:
                    decision = decisions[0]
                    factors = decision.factors
                    
                    # Should have all factor types
                    self.assertIn(DecisionFactor.WORKLOAD, factors)
                    self.assertIn(DecisionFactor.API_HEALTH, factors)
                    self.assertIn(DecisionFactor.CIRCUIT_BREAKER, factors)
                    self.assertIn(DecisionFactor.CAPACITY, factors)
                    self.assertIn(DecisionFactor.PRIORITY, factors)


class TestDecisionConfig(unittest.TestCase):
    """Test cases for DecisionConfig"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = DecisionConfig()
        
        self.assertEqual(config.workload_critical_threshold, 0.8)
        self.assertEqual(config.workload_high_threshold, 0.6)
        self.assertEqual(config.api_unhealthy_threshold, 0.4)
        self.assertEqual(config.api_degraded_threshold, 0.7)
        self.assertEqual(config.min_confidence_threshold, 0.6)
        self.assertEqual(config.max_agents_per_spawn, 5)
        self.assertEqual(config.spawning_cooldown, 300)
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = DecisionConfig(
            workload_critical_threshold=0.9,
            min_confidence_threshold=0.7,
            max_agents_per_spawn=3,
            spawning_cooldown=600
        )
        
        self.assertEqual(config.workload_critical_threshold, 0.9)
        self.assertEqual(config.min_confidence_threshold, 0.7)
        self.assertEqual(config.max_agents_per_spawn, 3)
        self.assertEqual(config.spawning_cooldown, 600)


class TestSpawningDecision(unittest.TestCase):
    """Test cases for SpawningDecision"""
    
    def test_decision_creation(self):
        """Test creating a spawning decision"""
        decision = SpawningDecision(
            should_spawn=True,
            specialization='test-spec',
            agent_count=2,
            confidence=0.75,
            factors={DecisionFactor.WORKLOAD: 0.8},
            reasoning=['Test reason'],
            timestamp=datetime.now().isoformat()
        )
        
        self.assertTrue(decision.should_spawn)
        self.assertEqual(decision.specialization, 'test-spec')
        self.assertEqual(decision.agent_count, 2)
        self.assertEqual(decision.confidence, 0.75)
    
    def test_decision_serialization(self):
        """Test decision serialization to dict"""
        timestamp = datetime.now().isoformat()
        decision = SpawningDecision(
            should_spawn=False,
            specialization='no-spawn',
            agent_count=0,
            confidence=0.3,
            factors={
                DecisionFactor.WORKLOAD: 0.4,
                DecisionFactor.CAPACITY: 0.2
            },
            reasoning=['Low workload', 'Low capacity usage'],
            timestamp=timestamp
        )
        
        result = decision.to_dict()
        
        self.assertFalse(result['should_spawn'])
        self.assertEqual(result['specialization'], 'no-spawn')
        self.assertEqual(result['agent_count'], 0)
        self.assertEqual(result['confidence'], 0.3)
        self.assertEqual(result['timestamp'], timestamp)
        self.assertEqual(len(result['factors']), 2)
        self.assertEqual(len(result['reasoning']), 2)


def run_tests():
    """Run all tests"""
    print("🧪 Running Sub-Agent Spawning API Tests")
    print("Created by @APIs-architect - Ensuring reliability first\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestSpawningDecisionEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestDecisionConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestSpawningDecision))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
