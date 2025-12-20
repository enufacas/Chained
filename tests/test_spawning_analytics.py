#!/usr/bin/env python3
"""
Test suite for Spawning Analytics Dashboard

Validates that the analytics tool correctly analyzes spawning history,
calculates metrics, and generates insights.

Created by @create-botter
"""

import unittest
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from spawning_analytics import (
    SpawningAnalytics,
    SpawningEvent,
    SpawningMetrics,
    EffectivenessAnalysis
)


class TestSpawningAnalytics(unittest.TestCase):
    """Test cases for SpawningAnalytics class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_registry_path = "/tmp/test-registry"
        
    def test_spawning_analytics_initialization(self):
        """Test SpawningAnalytics can be initialized"""
        with patch('spawning_analytics.RegistryManager'):
            analytics = SpawningAnalytics(registry_path=self.mock_registry_path)
            self.assertIsNotNone(analytics)
            self.assertEqual(str(analytics.registry_path), self.mock_registry_path)
    
    def test_collect_spawning_history_empty(self):
        """Test collecting spawning history with no events"""
        with patch('spawning_analytics.RegistryManager') as MockRegistry:
            mock_registry = MockRegistry.return_value
            mock_registry.list_agents.return_value = []
            
            analytics = SpawningAnalytics()
            events = analytics.collect_spawning_history()
            
            self.assertEqual(len(events), 0)
            self.assertIsInstance(events, list)
    
    def test_collect_spawning_history_with_events(self):
        """Test collecting spawning history with valid events"""
        with patch('spawning_analytics.RegistryManager') as MockRegistry:
            mock_registry = MockRegistry.return_value
            
            # Mock agent data
            mock_agents = [
                {
                    'id': 'agent-001',
                    'name': '🤖 TestAgent',
                    'specialization': 'test-spec',
                    'spawned_at': '2025-12-20T10:00:00Z',
                    'spawn_type': 'workload_based',
                    'spawn_reason': 'Test spawn',
                    'status': 'active'
                },
                {
                    'id': 'agent-002',
                    'name': '🤖 TestAgent2',
                    'specialization': 'test-spec2',
                    'spawned_at': '2025-12-20T11:00:00Z',
                    'spawn_type': 'learning_based',
                    'spawn_reason': 'Learning spawn',
                    'status': 'active'
                }
            ]
            
            mock_registry.list_agents.return_value = mock_agents
            
            analytics = SpawningAnalytics()
            events = analytics.collect_spawning_history()
            
            self.assertEqual(len(events), 2)
            self.assertIsInstance(events[0], SpawningEvent)
            self.assertEqual(events[0].agent_id, 'agent-001')
            self.assertEqual(events[1].agent_id, 'agent-002')
    
    def test_calculate_metrics_empty(self):
        """Test calculating metrics with no events"""
        with patch('spawning_analytics.RegistryManager'):
            analytics = SpawningAnalytics()
            metrics = analytics.calculate_metrics([])
            
            self.assertIsInstance(metrics, SpawningMetrics)
            self.assertEqual(metrics.total_spawns, 0)
            self.assertEqual(metrics.workload_based_spawns, 0)
            self.assertEqual(metrics.effectiveness_score, 0.0)
    
    def test_calculate_metrics_with_events(self):
        """Test calculating metrics with spawning events"""
        with patch('spawning_analytics.RegistryManager') as MockRegistry:
            mock_registry = MockRegistry.return_value
            mock_registry.list_agents.return_value = []
            
            analytics = SpawningAnalytics()
            
            # Create test events
            now = datetime.now()
            events = [
                SpawningEvent(
                    timestamp=now - timedelta(hours=2),
                    agent_id='agent-001',
                    agent_name='TestAgent1',
                    specialization='security',
                    spawn_type='workload_based',
                    spawn_reason='Test'
                ),
                SpawningEvent(
                    timestamp=now - timedelta(hours=1),
                    agent_id='agent-002',
                    agent_name='TestAgent2',
                    specialization='performance',
                    spawn_type='workload_based',
                    spawn_reason='Test'
                ),
                SpawningEvent(
                    timestamp=now,
                    agent_id='agent-003',
                    agent_name='TestAgent3',
                    specialization='security',
                    spawn_type='learning_based',
                    spawn_reason='Test'
                )
            ]
            
            metrics = analytics.calculate_metrics(events)
            
            self.assertEqual(metrics.total_spawns, 3)
            self.assertEqual(metrics.workload_based_spawns, 2)
            self.assertEqual(metrics.learning_based_spawns, 1)
            self.assertEqual(metrics.most_spawned_specialization, 'security')
    
    def test_analyze_effectiveness(self):
        """Test effectiveness analysis"""
        with patch('spawning_analytics.RegistryManager'):
            analytics = SpawningAnalytics()
            
            # Create test metrics
            metrics = SpawningMetrics(
                total_spawns=10,
                workload_based_spawns=7,
                learning_based_spawns=3,
                active_sub_agents=5,
                deactivated_sub_agents=5,
                avg_sub_agent_lifetime_hours=12.0,
                avg_workload_per_agent=4.5,
                most_spawned_specialization='security',
                least_spawned_specialization='api',
                spawning_frequency_per_day=2.0,
                effectiveness_score=0.5
            )
            
            # Analyze
            effectiveness = analytics.analyze_effectiveness([], metrics)
            
            self.assertIsInstance(effectiveness, EffectivenessAnalysis)
            self.assertEqual(effectiveness.spawning_decision_quality, 0.7)
            self.assertEqual(effectiveness.sub_agent_utilization, 0.5)
            self.assertIsInstance(effectiveness.recommendations, list)
            self.assertGreater(len(effectiveness.recommendations), 0)
    
    def test_generate_report_text_format(self):
        """Test generating text format report"""
        with patch('spawning_analytics.RegistryManager') as MockRegistry:
            mock_registry = MockRegistry.return_value
            mock_registry.list_agents.return_value = []
            
            analytics = SpawningAnalytics()
            report = analytics.generate_report(format='text')
            
            self.assertIsInstance(report, str)
            self.assertIn('AI Sub-Agent Spawning Analytics Dashboard', report)
            self.assertIn('Overall Metrics', report)
            self.assertIn('Effectiveness Analysis', report)
            self.assertIn('@create-botter', report)
    
    def test_generate_report_json_format(self):
        """Test generating JSON format report"""
        with patch('spawning_analytics.RegistryManager') as MockRegistry:
            mock_registry = MockRegistry.return_value
            mock_registry.list_agents.return_value = []
            
            analytics = SpawningAnalytics()
            report = analytics.generate_report(format='json')
            
            self.assertIsInstance(report, str)
            
            # Validate JSON structure
            data = json.loads(report)
            self.assertIn('timestamp', data)
            self.assertIn('metrics', data)
            self.assertIn('effectiveness', data)
            self.assertIn('recent_events', data)
    
    def test_get_specialization_distribution(self):
        """Test getting specialization distribution"""
        with patch('spawning_analytics.RegistryManager') as MockRegistry:
            mock_registry = MockRegistry.return_value
            
            mock_agents = [
                {
                    'id': f'agent-{i}',
                    'name': f'Agent{i}',
                    'specialization': 'security' if i < 3 else 'performance',
                    'spawned_at': '2025-12-20T10:00:00Z',
                    'spawn_type': 'workload_based',
                    'spawn_reason': 'Test'
                }
                for i in range(5)
            ]
            
            mock_registry.list_agents.return_value = mock_agents
            
            analytics = SpawningAnalytics()
            distribution = analytics.get_specialization_distribution()
            
            self.assertIsInstance(distribution, dict)
            self.assertEqual(distribution.get('security', 0), 3)
            self.assertEqual(distribution.get('performance', 0), 2)
    
    def test_get_spawning_timeline(self):
        """Test getting spawning timeline"""
        with patch('spawning_analytics.RegistryManager') as MockRegistry:
            mock_registry = MockRegistry.return_value
            
            now = datetime.now()
            mock_agents = [
                {
                    'id': f'agent-{i}',
                    'name': f'Agent{i}',
                    'specialization': 'test',
                    'spawned_at': (now - timedelta(days=i)).isoformat() + 'Z',
                    'spawn_type': 'workload_based',
                    'spawn_reason': 'Test'
                }
                for i in range(5)
            ]
            
            mock_registry.list_agents.return_value = mock_agents
            
            analytics = SpawningAnalytics()
            timeline = analytics.get_spawning_timeline(days=30)
            
            self.assertIsInstance(timeline, list)
            self.assertGreater(len(timeline), 0)
            
            # Each item should be a (date, count) tuple
            for date_str, count in timeline:
                self.assertIsInstance(date_str, str)
                self.assertIsInstance(count, int)
    
    def test_spawning_event_to_dict(self):
        """Test SpawningEvent serialization"""
        event = SpawningEvent(
            timestamp=datetime(2025, 12, 20, 10, 0, 0),
            agent_id='test-001',
            agent_name='TestAgent',
            specialization='test',
            spawn_type='workload_based',
            spawn_reason='Test reason',
            parent_agent_id='parent-001'
        )
        
        event_dict = event.to_dict()
        
        self.assertIsInstance(event_dict, dict)
        self.assertEqual(event_dict['agent_id'], 'test-001')
        self.assertEqual(event_dict['specialization'], 'test')
        self.assertIn('timestamp', event_dict)
    
    def test_recommendations_high_frequency(self):
        """Test recommendations for high spawning frequency"""
        with patch('spawning_analytics.RegistryManager'):
            analytics = SpawningAnalytics()
            
            metrics = SpawningMetrics(
                total_spawns=50,
                workload_based_spawns=40,
                learning_based_spawns=10,
                active_sub_agents=5,
                deactivated_sub_agents=45,
                avg_sub_agent_lifetime_hours=12.0,
                avg_workload_per_agent=4.5,
                most_spawned_specialization='security',
                least_spawned_specialization='api',
                spawning_frequency_per_day=4.5,  # High frequency
                effectiveness_score=0.1
            )
            
            effectiveness = analytics.analyze_effectiveness([], metrics)
            
            # Should have recommendation about high frequency
            freq_rec = any('High spawning frequency' in r for r in effectiveness.recommendations)
            self.assertTrue(freq_rec)
    
    def test_recommendations_low_utilization(self):
        """Test recommendations for low utilization"""
        with patch('spawning_analytics.RegistryManager'):
            analytics = SpawningAnalytics()
            
            metrics = SpawningMetrics(
                total_spawns=50,
                workload_based_spawns=40,
                learning_based_spawns=10,
                active_sub_agents=2,
                deactivated_sub_agents=48,  # Very low utilization
                avg_sub_agent_lifetime_hours=12.0,
                avg_workload_per_agent=4.5,
                most_spawned_specialization='security',
                least_spawned_specialization='api',
                spawning_frequency_per_day=2.0,
                effectiveness_score=0.04
            )
            
            effectiveness = analytics.analyze_effectiveness([], metrics)
            
            # Should have recommendation about low utilization
            util_rec = any('Low sub-agent utilization' in r for r in effectiveness.recommendations)
            self.assertTrue(util_rec)


def run_tests():
    """Run all tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSpawningAnalytics)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
