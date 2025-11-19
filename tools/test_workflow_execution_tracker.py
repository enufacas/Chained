#!/usr/bin/env python3
"""
Tests for Workflow Execution Tracker
Created by @workflows-tech-lead

Test suite for the workflow execution time tracking and accuracy measurement system.
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from workflow_execution_tracker import WorkflowExecutionTracker, ExecutionComparison


class TestWorkflowExecutionTracker:
    """Test suite for Workflow Execution Tracker."""
    
    def __init__(self):
        self.temp_dir = None
        self.tracker = None
        self.test_results = []
    
    def setup(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = WorkflowExecutionTracker(repo_root=self.temp_dir)
        print(f"✓ Test environment created at {self.temp_dir}")
    
    def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"✓ Test environment cleaned up")
    
    def test_track_execution(self):
        """Test tracking a single execution."""
        print("\n🧪 Testing execution tracking...")
        
        # First, add some history so predictor has data
        self.tracker.predictor.simulate_execution_data(num_workflows=1, num_executions=10)
        
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(seconds=150)
        
        comparison = self.tracker.track_execution(
            workflow_name="test-workflow",
            start_time=start_time,
            end_time=end_time,
            success=True
        )
        
        assert isinstance(comparison, ExecutionComparison)
        assert comparison.workflow_name == "test-workflow"
        assert comparison.actual_duration == 150.0
        assert comparison.predicted_duration > 0
        assert len(self.tracker.comparisons) == 1
        
        print("  ✓ Execution tracked successfully")
        print(f"  ✓ Predicted: {comparison.predicted_duration:.0f}s, Actual: {comparison.actual_duration:.0f}s")
        print(f"  ✓ Error: {comparison.prediction_error:.1f}%")
        self.test_results.append(("track_execution", True))
    
    def test_save_and_load(self):
        """Test saving and loading comparisons."""
        print("\n🧪 Testing save and load...")
        
        # Clear existing comparisons from previous test
        self.tracker.comparisons = []
        
        # Add predictor data first so predictions work
        self.tracker.predictor.simulate_execution_data(num_workflows=5, num_executions=20)
        
        # Add some tracked executions
        base_time = datetime.now(timezone.utc)
        for i in range(5):
            start = base_time + timedelta(hours=i)
            end = start + timedelta(seconds=100 + i * 10)
            self.tracker.track_execution(
                workflow_name=f"wf-{i}",
                start_time=start,
                end_time=end,
                success=True
            )
        
        assert len(self.tracker.comparisons) == 5
        
        # Create new tracker and verify it loads data
        new_tracker = WorkflowExecutionTracker(repo_root=self.temp_dir)
        assert len(new_tracker.comparisons) == 5
        assert new_tracker.comparisons[0].workflow_name == "wf-0"
        
        print("  ✓ Comparisons saved and loaded successfully")
        self.test_results.append(("save_load", True))
    
    def test_accuracy_metrics_no_data(self):
        """Test accuracy metrics with no data."""
        print("\n🧪 Testing metrics with no data...")
        
        # Create fresh tracker with no data
        temp_dir2 = tempfile.mkdtemp()
        fresh_tracker = WorkflowExecutionTracker(repo_root=temp_dir2)
        
        metrics = fresh_tracker.get_accuracy_metrics()
        
        assert metrics['total_comparisons'] == 0
        assert 'message' in metrics
        
        # Clean up
        shutil.rmtree(temp_dir2)
        
        print("  ✓ Handles no data correctly")
        self.test_results.append(("metrics_no_data", True))
    
    def test_accuracy_metrics_with_data(self):
        """Test accuracy metrics calculation."""
        print("\n🧪 Testing accuracy metrics...")
        
        # Reset comparisons for clean test
        self.tracker.comparisons = []
        
        # Create some predictions with known accuracy
        base_time = datetime.now(timezone.utc)
        
        # Add predictor data first
        self.tracker.predictor.simulate_execution_data(num_workflows=3, num_executions=20)
        
        # Track some executions with controlled accuracy
        test_cases = [
            ("accurate-wf", 100, 105),    # 5% error - excellent
            ("accurate-wf", 100, 115),    # 15% error - good
            ("moderate-wf", 200, 240),    # 20% error - good
            ("moderate-wf", 200, 260),    # 30% error - fair
            ("poor-wf", 300, 480),        # 60% error - poor
        ]
        
        for i, (wf_name, predicted, actual) in enumerate(test_cases):
            # Record history that will lead to predicted duration
            for j in range(5):
                self.tracker.predictor.record_execution(
                    workflow_name=wf_name,
                    start_time=base_time - timedelta(days=j+1),
                    duration_seconds=predicted,
                    success=True
                )
            
            # Now track actual execution
            start = base_time + timedelta(hours=i)
            end = start + timedelta(seconds=actual)
            self.tracker.track_execution(
                workflow_name=wf_name,
                start_time=start,
                end_time=end,
                success=True
            )
        
        # Get metrics
        metrics = self.tracker.get_accuracy_metrics()
        
        print(f"  Debug: Found {metrics['total_comparisons']} comparisons")
        assert metrics['total_comparisons'] == 5, f"Expected 5, got {metrics['total_comparisons']}"
        assert 'mean_error_percent' in metrics
        assert 'accuracy_distribution' in metrics
        assert 'overall_accuracy_score' in metrics
        
        # Check distribution
        dist = metrics['accuracy_distribution']
        assert dist['excellent_10_percent'] > 0
        assert dist['poor_over_50_percent'] > 0
        
        print(f"  ✓ Mean error: {metrics['mean_error_percent']:.1f}%")
        print(f"  ✓ Overall accuracy: {metrics['overall_accuracy_score']:.1f}%")
        print(f"  ✓ Excellent: {dist['excellent_10_percent']}, "
              f"Good: {dist['good_25_percent']}, "
              f"Fair: {dist['fair_50_percent']}, "
              f"Poor: {dist['poor_over_50_percent']}")
        self.test_results.append(("accuracy_metrics", True))
    
    def test_per_workflow_metrics(self):
        """Test per-workflow accuracy metrics."""
        print("\n🧪 Testing per-workflow metrics...")
        
        # Add data for specific workflow
        base_time = datetime.now(timezone.utc)
        
        # Setup predictor
        self.tracker.predictor.simulate_execution_data(num_workflows=1, num_executions=20)
        
        for i in range(5):
            start = base_time + timedelta(hours=i)
            end = start + timedelta(seconds=100 + i * 5)
            self.tracker.track_execution(
                workflow_name="specific-wf",
                start_time=start,
                end_time=end,
                success=True
            )
        
        # Get metrics for specific workflow
        metrics = self.tracker.get_accuracy_metrics("specific-wf")
        
        assert metrics['total_comparisons'] == 5
        assert 'mean_error_percent' in metrics
        
        print(f"  ✓ Workflow-specific metrics working")
        print(f"  ✓ Mean error for specific-wf: {metrics['mean_error_percent']:.1f}%")
        self.test_results.append(("per_workflow_metrics", True))
    
    def test_best_worst_predictions(self):
        """Test getting best and worst predictions."""
        print("\n🧪 Testing best/worst predictions...")
        
        # Add varied accuracy data
        base_time = datetime.now(timezone.utc)
        
        self.tracker.predictor.simulate_execution_data(num_workflows=5, num_executions=30)
        
        # Create some with different errors
        for i in range(10):
            start = base_time + timedelta(hours=i)
            # Vary actual duration to create different errors
            actual = 100 + i * 20
            end = start + timedelta(seconds=actual)
            self.tracker.track_execution(
                workflow_name=f"wf-{i}",
                start_time=start,
                end_time=end,
                success=True
            )
        
        worst = self.tracker.get_worst_predictions(limit=3)
        best = self.tracker.get_best_predictions(limit=3)
        
        assert len(worst) == 3
        assert len(best) == 3
        assert worst[0].prediction_error >= worst[1].prediction_error
        assert best[0].prediction_error <= best[1].prediction_error
        
        print(f"  ✓ Worst prediction error: {worst[0].prediction_error:.1f}%")
        print(f"  ✓ Best prediction error: {best[0].prediction_error:.1f}%")
        self.test_results.append(("best_worst", True))
    
    def test_export_metrics(self):
        """Test exporting metrics to JSON."""
        print("\n🧪 Testing metrics export...")
        
        # Add some data
        base_time = datetime.now(timezone.utc)
        self.tracker.predictor.simulate_execution_data(num_workflows=3, num_executions=20)
        
        for i in range(5):
            start = base_time + timedelta(hours=i)
            end = start + timedelta(seconds=100)
            self.tracker.track_execution(
                workflow_name=f"wf-{i}",
                start_time=start,
                end_time=end,
                success=True
            )
        
        # Export
        output_file = Path(self.temp_dir) / 'test_export.json'
        result = self.tracker.export_metrics(str(output_file))
        
        assert os.path.exists(output_file)
        
        # Verify structure
        import json
        with open(output_file) as f:
            data = json.load(f)
            assert 'timestamp' in data
            assert 'overall_metrics' in data
            assert 'per_workflow_metrics' in data
            assert 'recent_comparisons' in data
        
        print(f"  ✓ Metrics exported to {output_file}")
        self.test_results.append(("export_metrics", True))
    
    def test_integration_with_predictor(self):
        """Test integration with AI predictor."""
        print("\n🧪 Testing predictor integration...")
        
        # Tracked execution should update predictor history
        initial_count = len(self.tracker.predictor.execution_history)
        
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(seconds=200)
        
        self.tracker.track_execution(
            workflow_name="integration-test",
            start_time=start_time,
            end_time=end_time,
            success=True,
            resource_usage={'cpu_percent': 50}
        )
        
        # Should have added to predictor history
        assert len(self.tracker.predictor.execution_history) == initial_count + 1
        
        # Verify the added execution
        last_exec = self.tracker.predictor.execution_history[-1]
        assert last_exec.workflow_name == "integration-test"
        assert last_exec.duration_seconds == 200.0
        
        print("  ✓ Tracker properly updates predictor history")
        self.test_results.append(("predictor_integration", True))
    
    def run_all_tests(self):
        """Run all tests."""
        print("="*70)
        print("🧪 Running Workflow Execution Tracker Test Suite")
        print("="*70)
        
        try:
            self.setup()
            
            # Run all tests
            self.test_track_execution()
            self.test_save_and_load()
            self.test_accuracy_metrics_no_data()
            self.test_accuracy_metrics_with_data()
            self.test_per_workflow_metrics()
            self.test_best_worst_predictions()
            self.test_export_metrics()
            self.test_integration_with_predictor()
            
            # Summary
            print("\n" + "="*70)
            print("📊 Test Results Summary")
            print("="*70)
            
            passed = sum(1 for _, result in self.test_results if result)
            total = len(self.test_results)
            
            for test_name, result in self.test_results:
                status = "✓ PASS" if result else "✗ FAIL"
                print(f"{status}: {test_name}")
            
            print("\n" + "="*70)
            print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
            print("="*70 + "\n")
            
            return passed == total
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.teardown()


def main():
    """Main entry point."""
    tester = TestWorkflowExecutionTracker()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
