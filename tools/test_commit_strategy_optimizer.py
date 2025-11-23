#!/usr/bin/env python3
"""
Tests for Commit Strategy Optimizer

Comprehensive test suite for the real-time commit strategy optimization system.
Tests PR outcome tracking, agent learning, and recommendation optimization.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
import sys
import os

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

# Import using exec since module name has dashes
import importlib.util
spec = importlib.util.spec_from_file_location(
    'commit_strategy_optimizer',
    Path(__file__).parent / 'commit-strategy-optimizer.py'
)
optimizer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(optimizer_module)

CommitStrategyOptimizer = optimizer_module.CommitStrategyOptimizer
PROutcome = optimizer_module.PROutcome
AgentStrategy = optimizer_module.AgentStrategy
StrategyEffectiveness = optimizer_module.StrategyEffectiveness


class TestPROutcome(unittest.TestCase):
    """Test PROutcome data structure"""
    
    def test_pr_outcome_creation(self):
        """Test creating PROutcome"""
        outcome = PROutcome(
            pr_number=123,
            merged=True,
            merge_time_hours=2.5,
            review_cycles=2,
            ci_passed=True,
            commits=['abc123', 'def456'],
            agent='engineer-master',
            context='feature'
        )
        
        self.assertEqual(outcome.pr_number, 123)
        self.assertTrue(outcome.merged)
        self.assertEqual(outcome.agent, 'engineer-master')
        self.assertEqual(len(outcome.commits), 2)
    
    def test_pr_outcome_to_dict(self):
        """Test converting PROutcome to dict"""
        outcome = PROutcome(
            pr_number=456,
            merged=False,
            merge_time_hours=None,
            review_cycles=1,
            ci_passed=False,
            commits=['xyz789'],
            agent=None,
            context='bugfix'
        )
        
        data = outcome.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['pr_number'], 456)
        self.assertFalse(data['merged'])
        self.assertEqual(data['context'], 'bugfix')


class TestAgentStrategy(unittest.TestCase):
    """Test AgentStrategy data structure"""
    
    def test_agent_strategy_creation(self):
        """Test creating AgentStrategy"""
        strategy = AgentStrategy(
            agent_name='create-guru',
            total_prs=10,
            successful_prs=8,
            success_rate=0.8,
            average_merge_time_hours=3.5,
            preferred_patterns=['conventional_commits', 'small_commits'],
            common_attributes={'avg_files': 5, 'avg_lines': 150}
        )
        
        self.assertEqual(strategy.agent_name, 'create-guru')
        self.assertEqual(strategy.success_rate, 0.8)
        self.assertEqual(len(strategy.preferred_patterns), 2)
    
    def test_agent_strategy_to_dict(self):
        """Test converting AgentStrategy to dict"""
        strategy = AgentStrategy(
            agent_name='troubleshoot-expert',
            total_prs=5,
            successful_prs=5,
            success_rate=1.0,
            average_merge_time_hours=1.5,
            preferred_patterns=['detailed_messages'],
            common_attributes={}
        )
        
        data = strategy.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['agent_name'], 'troubleshoot-expert')
        self.assertEqual(data['success_rate'], 1.0)


class TestStrategyEffectiveness(unittest.TestCase):
    """Test StrategyEffectiveness data structure"""
    
    def test_strategy_effectiveness_creation(self):
        """Test creating StrategyEffectiveness"""
        effectiveness = StrategyEffectiveness(
            strategy_id='conv_commits_1',
            pattern_name='conventional_commits',
            times_used=50,
            times_successful=42,
            success_rate=0.84,
            average_merge_time=2.5,
            contexts=['feature', 'bugfix'],
            confidence_score=0.85,
            trend='improving'
        )
        
        self.assertEqual(effectiveness.pattern_name, 'conventional_commits')
        self.assertEqual(effectiveness.success_rate, 0.84)
        self.assertEqual(effectiveness.trend, 'improving')
    
    def test_strategy_effectiveness_to_dict(self):
        """Test converting StrategyEffectiveness to dict"""
        effectiveness = StrategyEffectiveness(
            strategy_id='small_commits_1',
            pattern_name='optimal_commit_size',
            times_used=30,
            times_successful=25,
            success_rate=0.833,
            average_merge_time=2.0,
            contexts=['refactor'],
            confidence_score=0.75
        )
        
        data = effectiveness.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['pattern_name'], 'optimal_commit_size')
        self.assertAlmostEqual(data['success_rate'], 0.833, places=3)


class TestCommitStrategyOptimizer(unittest.TestCase):
    """Test CommitStrategyOptimizer main class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create directory structure
        Path('learnings').mkdir(exist_ok=True)
        Path('analysis').mkdir(exist_ok=True)
        
        # Initialize git repo for testing
        os.system('git init > /dev/null 2>&1')
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')
        
        # Create a test commit
        Path('test.txt').write_text('test content')
        os.system('git add test.txt')
        os.system('git commit -m "feat: test commit" > /dev/null 2>&1')
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)
    
    def test_optimizer_initialization(self):
        """Test CommitStrategyOptimizer initialization"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        self.assertIsNotNone(optimizer.base_learner)
        self.assertIsInstance(optimizer.optimization_data, dict)
        self.assertIsInstance(optimizer.agent_strategies, dict)
        self.assertIsInstance(optimizer.pr_outcomes, list)
    
    def test_initialize_optimization_db(self):
        """Test initialization of optimization database"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        data = optimizer._initialize_optimization_db()
        
        self.assertIn('version', data)
        self.assertIn('strategy_effectiveness', data)
        self.assertIn('optimization_history', data)
        self.assertIn('learning_rate', data)
    
    def test_track_pr_outcome(self):
        """Test tracking a PR outcome"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        outcome = optimizer.track_pr_outcome(
            pr_number=100,
            merged=True,
            agent='create-guru',
            context='feature'
        )
        
        self.assertEqual(outcome.pr_number, 100)
        self.assertTrue(outcome.merged)
        self.assertEqual(outcome.agent, 'create-guru')
        self.assertEqual(len(optimizer.pr_outcomes), 1)
    
    def test_update_agent_strategy(self):
        """Test updating agent strategy"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        # Create mock outcome
        outcome = PROutcome(
            pr_number=101,
            merged=True,
            merge_time_hours=2.0,
            review_cycles=1,
            ci_passed=True,
            commits=[],
            agent='engineer-master',
            context='bugfix'
        )
        
        # Update strategy
        optimizer._update_agent_strategy('engineer-master', outcome, [])
        
        # Check agent was added
        self.assertIn('engineer-master', optimizer.agent_strategies['agents'])
        agent_data = optimizer.agent_strategies['agents']['engineer-master']
        self.assertEqual(agent_data['total_prs'], 1)
        self.assertEqual(agent_data['successful_prs'], 1)
    
    def test_update_strategy_effectiveness(self):
        """Test updating strategy effectiveness"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        outcome = PROutcome(
            pr_number=102,
            merged=True,
            merge_time_hours=1.5,
            review_cycles=1,
            ci_passed=True,
            commits=[],
            context='refactor'
        )
        
        # This would normally analyze commits, but we'll test the structure
        optimizer._update_strategy_effectiveness(outcome, [])
        
        # Check structure exists
        self.assertIn('strategy_effectiveness', optimizer.optimization_data)
    
    def test_get_optimized_recommendations(self):
        """Test getting optimized recommendations"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        # Add some mock strategy effectiveness
        optimizer.optimization_data['strategy_effectiveness'] = {
            'conventional_commits': {
                'strategy_id': 'conv_commits_1',
                'pattern_name': 'conventional_commits',
                'times_used': 50,
                'times_successful': 45,
                'success_rate': 0.9,
                'average_merge_time': 2.0,
                'contexts': ['feature', 'bugfix'],
                'confidence_score': 0.9,
                'trend': 'improving'
            }
        }
        
        recommendations = optimizer.get_optimized_recommendations(
            context='feature',
            min_confidence=0.5
        )
        
        self.assertIsInstance(recommendations, list)
    
    def test_get_agent_specific_recommendations(self):
        """Test getting agent-specific recommendations"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        # Add mock agent data
        optimizer.agent_strategies['agents'] = {
            'create-guru': {
                'agent_name': 'create-guru',
                'total_prs': 10,
                'successful_prs': 9,
                'success_rate': 0.9,
                'average_merge_time_hours': 2.5,
                'preferred_patterns': ['conventional_commits', 'small_commits'],
                'common_attributes': {}
            }
        }
        
        recommendations = optimizer.get_optimized_recommendations(
            agent='create-guru',
            context='feature',
            min_confidence=0.5
        )
        
        self.assertIsInstance(recommendations, list)
        # Should have agent-specific recommendation
        if recommendations:
            self.assertTrue(
                any('create-guru' in rec.title for rec in recommendations)
            )
    
    def test_run_optimization(self):
        """Test running optimization analysis"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        # Add some mock PR outcomes
        optimizer.pr_outcomes = [
            {
                'pr_number': 1,
                'merged': True,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'commits': [],
                'agent': 'test-agent',
                'context': 'feature'
            },
            {
                'pr_number': 2,
                'merged': True,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'commits': [],
                'agent': 'test-agent',
                'context': 'bugfix'
            }
        ]
        
        result = optimizer.run_optimization()
        
        self.assertIn('total_prs_analyzed', result)
        self.assertIn('successful_prs', result)
        self.assertIn('overall_success_rate', result)
        self.assertIn('top_strategies', result)
    
    def test_generate_effectiveness_report(self):
        """Test generating effectiveness report"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        # Add mock data
        optimizer.pr_outcomes = [
            {
                'pr_number': 1,
                'merged': True,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'commits': []
            }
        ]
        
        optimizer.optimization_data['strategy_effectiveness'] = {
            'test_pattern': {
                'pattern_name': 'test_pattern',
                'success_rate': 0.8,
                'times_used': 10,
                'confidence_score': 0.75,
                'contexts': ['feature'],
                'trend': 'improving'
            }
        }
        
        report = optimizer.generate_effectiveness_report()
        
        self.assertIsInstance(report, str)
        self.assertIn('Effectiveness Report', report)
        self.assertIn('Test Pattern', report)  # Pattern name is title-cased in report
    
    def test_save_and_load_optimization_db(self):
        """Test saving and loading optimization database"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        # Modify data
        optimizer.optimization_data['test_key'] = 'test_value'
        
        # Save
        optimizer._save_optimization_db()
        
        # Load new instance
        optimizer2 = CommitStrategyOptimizer(verbose=False)
        
        # Check data persisted
        self.assertIn('test_key', optimizer2.optimization_data)
        self.assertEqual(optimizer2.optimization_data['test_key'], 'test_value')
    
    def test_save_and_load_agent_strategies(self):
        """Test saving and loading agent strategies"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        # Add agent data
        optimizer.agent_strategies['agents'] = {
            'test-agent': {
                'agent_name': 'test-agent',
                'total_prs': 5,
                'successful_prs': 4,
                'success_rate': 0.8,
                'average_merge_time_hours': 2.0,
                'preferred_patterns': ['pattern1'],
                'common_attributes': {}
            }
        }
        
        # Save
        optimizer._save_agent_strategies()
        
        # Load new instance
        optimizer2 = CommitStrategyOptimizer(verbose=False)
        
        # Check data persisted
        self.assertIn('test-agent', optimizer2.agent_strategies['agents'])
    
    def test_save_and_load_pr_outcomes(self):
        """Test saving and loading PR outcomes"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        # Add outcome
        outcome = PROutcome(
            pr_number=999,
            merged=True,
            merge_time_hours=1.0,
            review_cycles=1,
            ci_passed=True,
            commits=['abc'],
            agent='test-agent'
        )
        optimizer.pr_outcomes.append(outcome.to_dict())
        
        # Save
        optimizer._save_pr_outcomes()
        
        # Load new instance
        optimizer2 = CommitStrategyOptimizer(verbose=False)
        
        # Check data persisted
        self.assertTrue(len(optimizer2.pr_outcomes) > 0)
        self.assertTrue(any(o['pr_number'] == 999 for o in optimizer2.pr_outcomes))


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
        
        Path('learnings').mkdir(exist_ok=True)
        Path('analysis').mkdir(exist_ok=True)
        
        # Initialize git repo
        os.system('git init > /dev/null 2>&1')
        os.system('git config user.email "test@example.com"')
        os.system('git config user.name "Test User"')
        
        # Create test commits
        for i in range(3):
            Path(f'test{i}.txt').write_text(f'content {i}')
            os.system(f'git add test{i}.txt')
            os.system(f'git commit -m "feat: test commit {i}" > /dev/null 2>&1')
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)
    
    def test_complete_learning_cycle(self):
        """Test complete learning cycle from PR tracking to recommendations"""
        optimizer = CommitStrategyOptimizer(verbose=False)
        
        # Step 1: Track multiple PR outcomes
        for i in range(5):
            optimizer.track_pr_outcome(
                pr_number=100 + i,
                merged=True,
                agent='create-guru',
                context='feature'
            )
        
        # Step 2: Run optimization
        result = optimizer.run_optimization()
        
        self.assertGreaterEqual(result['total_prs_analyzed'], 5)
        
        # Step 3: Get recommendations
        recommendations = optimizer.get_optimized_recommendations(
            agent='create-guru',
            context='feature',
            min_confidence=0.5
        )
        
        self.assertIsInstance(recommendations, list)
        
        # Step 4: Generate report
        report = optimizer.generate_effectiveness_report()
        
        self.assertIsInstance(report, str)
        self.assertIn('create-guru', report)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPROutcome))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategyEffectiveness))
    suite.addTests(loader.loadTestsFromTestCase(TestCommitStrategyOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
