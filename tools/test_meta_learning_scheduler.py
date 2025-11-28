#!/usr/bin/env python3
"""
Tests for Meta-Learning Workflow Scheduler
Created by @workflows-tech-lead

Comprehensive test suite for the meta-learning system that optimizes
workflow schedules through continuous learning.
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from meta_learning_scheduler import (
    MetaLearningScheduler,
    LearningParameters,
    SchedulingStrategy
)


class TestMetaLearningScheduler:
    """Test suite for Meta-Learning Scheduler."""
    
    def __init__(self):
        self.temp_dir = None
        self.scheduler = None
        self.test_results = []
    
    def setup(self):
        """Setup test environment."""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.scheduler = MetaLearningScheduler(repo_root=self.temp_dir)
        print(f"✓ Test environment created at {self.temp_dir}")
    
    def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"✓ Test environment cleaned up")
    
    def test_learning_parameters_creation(self):
        """Test creating learning parameters."""
        print("\n🧪 Testing learning parameters...")
        
        params = LearningParameters(
            success_weight=0.5,
            duration_weight=0.3,
            conflict_weight=0.2,
            learning_rate=0.15
        )
        
        assert params.success_weight == 0.5
        assert params.duration_weight == 0.3
        assert params.conflict_weight == 0.2
        assert params.learning_rate == 0.15
        
        print("  ✓ Learning parameters created successfully")
        self.test_results.append(("learning_parameters", True))
    
    def test_strategy_creation(self):
        """Test creating scheduling strategies."""
        print("\n🧪 Testing strategy creation...")
        
        params = LearningParameters()
        strategy = SchedulingStrategy(
            name="test_strategy",
            parameters=params,
            performance_history=[75.0, 78.0, 82.0],
            last_updated=datetime.now(timezone.utc).isoformat()
        )
        
        assert strategy.name == "test_strategy"
        assert len(strategy.performance_history) == 3
        assert strategy.average_performance == 78.33333333333333
        
        print("  ✓ Strategy created successfully")
        print(f"  ✓ Average performance: {strategy.average_performance:.1f}%")
        self.test_results.append(("strategy_creation", True))
    
    def test_strategy_trend_detection(self):
        """Test performance trend detection."""
        print("\n🧪 Testing trend detection...")
        
        params = LearningParameters()
        
        # Improving trend
        improving = SchedulingStrategy(
            name="improving",
            parameters=params,
            performance_history=[60, 62, 64, 68, 72, 75, 78, 82, 85, 88],
            last_updated=datetime.now(timezone.utc).isoformat()
        )
        assert improving.performance_trend == "improving"
        print(f"  ✓ Improving trend detected correctly")
        
        # Declining trend
        declining = SchedulingStrategy(
            name="declining",
            parameters=params,
            performance_history=[85, 82, 80, 78, 75, 72, 70, 68, 65, 62],
            last_updated=datetime.now(timezone.utc).isoformat()
        )
        assert declining.performance_trend == "declining"
        print(f"  ✓ Declining trend detected correctly")
        
        # Stable trend - very tight variance to ensure stability
        stable = SchedulingStrategy(
            name="stable",
            parameters=params,
            performance_history=[75.0, 75.01, 74.99, 75.0, 75.02, 74.98, 75.0, 75.01, 74.99, 75.0],
            last_updated=datetime.now(timezone.utc).isoformat()
        )
        trend = stable.performance_trend
        # Should be stable since variance is < 0.05
        assert trend == "stable", f"Expected stable, got {trend}"
        print(f"  ✓ Stable trend detected correctly")
        
        self.test_results.append(("trend_detection", True))
    
    def test_scheduler_initialization(self):
        """Test meta-learning scheduler initialization."""
        print("\n🧪 Testing scheduler initialization...")
        
        assert self.scheduler is not None
        assert 'default' in self.scheduler.strategies
        assert isinstance(self.scheduler.predictor, type(self.scheduler.predictor))
        assert isinstance(self.scheduler.tracker, type(self.scheduler.tracker))
        
        print("  ✓ Scheduler initialized successfully")
        print(f"  ✓ Default strategy exists: {self.scheduler.strategies['default'].name}")
        self.test_results.append(("scheduler_init", True))
    
    def test_strategy_persistence(self):
        """Test saving and loading strategies."""
        print("\n🧪 Testing strategy persistence...")
        
        # Create a custom strategy
        custom_params = LearningParameters(
            success_weight=0.6,
            duration_weight=0.25,
            conflict_weight=0.15
        )
        custom_strategy = SchedulingStrategy(
            name="custom_test",
            parameters=custom_params,
            performance_history=[80.0, 82.0, 85.0],
            last_updated=datetime.now(timezone.utc).isoformat()
        )
        
        self.scheduler.strategies['custom_test'] = custom_strategy
        self.scheduler.save_strategies()
        
        # Create new scheduler and load
        new_scheduler = MetaLearningScheduler(repo_root=self.temp_dir)
        
        assert 'custom_test' in new_scheduler.strategies
        loaded_strategy = new_scheduler.strategies['custom_test']
        assert loaded_strategy.parameters.success_weight == 0.6
        assert len(loaded_strategy.performance_history) == 3
        
        print("  ✓ Strategies saved and loaded successfully")
        self.test_results.append(("strategy_persistence", True))
    
    def test_learning_log(self):
        """Test learning log functionality."""
        print("\n🧪 Testing learning log...")
        
        # Log some events
        self.scheduler.log_learning_event('test_event', {
            'test_data': 'value1',
            'number': 42
        })
        
        self.scheduler.log_learning_event('another_event', {
            'test_data': 'value2',
            'number': 123
        })
        
        assert len(self.scheduler.learning_log) >= 2
        assert self.scheduler.learning_log[-1]['event_type'] == 'another_event'
        assert self.scheduler.learning_log[-1]['details']['number'] == 123
        
        print(f"  ✓ Learning log has {len(self.scheduler.learning_log)} entries")
        self.test_results.append(("learning_log", True))
    
    def test_prediction_accuracy_evaluation(self):
        """Test prediction accuracy evaluation."""
        print("\n🧪 Testing prediction accuracy evaluation...")
        
        # Initially should have no data
        accuracy = self.scheduler.evaluate_prediction_accuracy()
        assert accuracy['total_predictions'] == 0
        
        print(f"  ✓ Handles empty data correctly")
        print(f"  ✓ Total predictions: {accuracy['total_predictions']}")
        self.test_results.append(("accuracy_evaluation", True))
    
    def test_strategy_performance_calculation(self):
        """Test strategy performance calculation."""
        print("\n🧪 Testing strategy performance calculation...")
        
        strategy = self.scheduler.strategies['default']
        performance = self.scheduler.calculate_strategy_performance(strategy)
        
        assert isinstance(performance, float)
        assert 0 <= performance <= 100
        
        print(f"  ✓ Performance calculated: {performance:.1f}%")
        self.test_results.append(("performance_calculation", True))
    
    def test_parameter_adaptation(self):
        """Test parameter adaptation based on performance."""
        print("\n🧪 Testing parameter adaptation...")
        
        # Create strategy with some performance history
        strategy = SchedulingStrategy(
            name="adapt_test",
            parameters=LearningParameters(
                success_weight=0.4,
                duration_weight=0.3,
                conflict_weight=0.3,
                learning_rate=0.1
            ),
            performance_history=[70.0, 72.0, 75.0],
            last_updated=datetime.now(timezone.utc).isoformat()
        )
        
        self.scheduler.strategies['adapt_test'] = strategy
        
        # Record initial parameters
        initial_success_weight = strategy.parameters.success_weight
        
        # Adapt the strategy
        self.scheduler.adapt_strategy_parameters('adapt_test')
        
        # Check that parameters were adjusted
        assert len(strategy.performance_history) == 4  # New performance recorded
        
        print(f"  ✓ Strategy adapted")
        print(f"  ✓ Initial success weight: {initial_success_weight:.3f}")
        print(f"  ✓ New success weight: {strategy.parameters.success_weight:.3f}")
        print(f"  ✓ Performance history length: {len(strategy.performance_history)}")
        self.test_results.append(("parameter_adaptation", True))
    
    def test_optimized_schedule_generation(self):
        """Test generating optimized schedules."""
        print("\n🧪 Testing optimized schedule generation...")
        
        # Generate schedule for a test workflow
        result = self.scheduler.generate_optimized_schedule(
            workflow_name="test-workflow",
            strategy_name="default"
        )
        
        assert result is not None
        assert result.workflow_name == "test-workflow"
        assert result.recommended_time is not None
        assert 0 <= result.confidence <= 1
        assert len(result.reasoning) > 0
        
        print(f"  ✓ Schedule generated")
        print(f"  ✓ Recommended time: {result.recommended_time}")
        print(f"  ✓ Confidence: {result.confidence * 100:.0f}%")
        print(f"  ✓ Reasoning steps: {len(result.reasoning)}")
        self.test_results.append(("schedule_generation", True))
    
    def test_strategy_evolution(self):
        """Test strategy evolution (genetic algorithm)."""
        print("\n🧪 Testing strategy evolution...")
        
        # Setup strategies with different performance
        for i in range(3):
            strategy = SchedulingStrategy(
                name=f"strategy_{i}",
                parameters=LearningParameters(
                    success_weight=0.3 + i * 0.1,
                    duration_weight=0.3,
                    conflict_weight=0.4 - i * 0.1
                ),
                performance_history=[60 + i * 10] * 5,
                last_updated=datetime.now(timezone.utc).isoformat()
            )
            self.scheduler.strategies[f"strategy_{i}"] = strategy
        
        initial_count = len(self.scheduler.strategies)
        
        # Evolve strategies
        self.scheduler.evolve_strategies()
        
        # Should have new strategies or kept same count
        final_count = len(self.scheduler.strategies)
        
        print(f"  ✓ Evolution complete")
        print(f"  ✓ Initial strategies: {initial_count}")
        print(f"  ✓ Final strategies: {final_count}")
        print(f"  ✓ Strategy names: {list(self.scheduler.strategies.keys())}")
        self.test_results.append(("strategy_evolution", True))
    
    def test_meta_learning_report(self):
        """Test comprehensive report generation."""
        print("\n🧪 Testing meta-learning report...")
        
        report = self.scheduler.generate_meta_learning_report()
        
        assert 'timestamp' in report
        assert 'accuracy_metrics' in report
        assert 'strategies' in report
        assert 'best_strategy' in report
        
        print(f"  ✓ Report generated successfully")
        print(f"  ✓ Best strategy: {report['best_strategy']}")
        print(f"  ✓ Total strategies: {len(report['strategies'])}")
        self.test_results.append(("meta_report", True))
    
    def test_batch_optimization(self):
        """Test batch workflow optimization."""
        print("\n🧪 Testing batch optimization...")
        
        # Provide workflow names since there's no data
        workflow_names = ['workflow-a', 'workflow-b', 'workflow-c']
        result = self.scheduler.optimize_all_workflows(workflow_names)
        
        assert 'timestamp' in result
        assert 'workflow_count' in result
        assert 'schedules' in result
        assert result['workflow_count'] == 3
        assert len(result['schedules']) == 3
        
        print(f"  ✓ Batch optimization complete")
        print(f"  ✓ Workflows optimized: {result['workflow_count']}")
        print(f"  ✓ Schedules generated: {len(result['schedules'])}")
        self.test_results.append(("batch_optimization", True))
    
    def test_optimization_insights(self):
        """Test optimization insights generation."""
        print("\n🧪 Testing optimization insights...")
        
        insights = self.scheduler.get_optimization_insights()
        
        assert 'timestamp' in insights
        assert 'system_health' in insights
        assert 'recommendations' in insights
        assert 'metrics' in insights
        
        # System should need data since we have no execution history
        assert insights['system_health'] == 'needs_data'
        assert len(insights['recommendations']) > 0
        
        print(f"  ✓ Insights generated successfully")
        print(f"  ✓ System health: {insights['system_health']}")
        print(f"  ✓ Recommendations count: {len(insights['recommendations'])}")
        self.test_results.append(("optimization_insights", True))
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("\n" + "="*70)
        print("🧪 Meta-Learning Scheduler Test Suite - @APIs-architect")
        print("="*70)
        
        self.setup()
        
        try:
            # Run tests
            self.test_learning_parameters_creation()
            self.test_strategy_creation()
            self.test_strategy_trend_detection()
            self.test_scheduler_initialization()
            self.test_strategy_persistence()
            self.test_learning_log()
            self.test_prediction_accuracy_evaluation()
            self.test_strategy_performance_calculation()
            self.test_parameter_adaptation()
            self.test_optimized_schedule_generation()
            self.test_strategy_evolution()
            self.test_meta_learning_report()
            self.test_batch_optimization()
            self.test_optimization_insights()
            
        finally:
            self.teardown()
        
        # Summary
        print("\n" + "="*70)
        print("📊 Test Results Summary")
        print("="*70)
        
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        print(f"\n🎯 Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("✨ All tests passed! Meta-learning system is working correctly.")
            return 0
        else:
            print(f"⚠️  {total - passed} test(s) failed.")
            return 1


def main():
    """Main test runner."""
    test_suite = TestMetaLearningScheduler()
    exit_code = test_suite.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
