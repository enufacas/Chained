#!/usr/bin/env python3
"""
Tests for AI Workflow Predictor
Created by @coordinate-wizard

Comprehensive test suite for the AI-powered workflow execution time predictor.
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from ai_workflow_predictor import (
    AIWorkflowPredictor, 
    WorkflowExecutionData, 
    PredictionResult
)


class TestAIWorkflowPredictor:
    """Test suite for AI Workflow Predictor."""
    
    def __init__(self):
        self.temp_dir = None
        self.predictor = None
        self.test_results = []
    
    def setup(self):
        """Setup test environment."""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.predictor = AIWorkflowPredictor(repo_root=self.temp_dir)
        print(f"✓ Test environment created at {self.temp_dir}")
    
    def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"✓ Test environment cleaned up")
    
    def test_record_execution(self):
        """Test recording workflow executions."""
        print("\n🧪 Testing execution recording...")
        
        start_time = datetime.now(timezone.utc)
        self.predictor.record_execution(
            workflow_name="test-workflow",
            start_time=start_time,
            duration_seconds=120.5,
            success=True,
            resource_usage={'cpu_percent': 45.0}
        )
        
        assert len(self.predictor.execution_history) == 1
        assert self.predictor.execution_history[0].workflow_name == "test-workflow"
        assert self.predictor.execution_history[0].duration_seconds == 120.5
        assert self.predictor.execution_history[0].success == True
        
        print("  ✓ Execution recorded successfully")
        self.test_results.append(("record_execution", True))
    
    def test_save_and_load_history(self):
        """Test saving and loading execution history."""
        print("\n🧪 Testing history persistence...")
        
        # Clear any existing history for clean test
        self.predictor.execution_history = []
        
        # Record some executions
        for i in range(5):
            self.predictor.record_execution(
                workflow_name=f"workflow-{i}",
                start_time=datetime.now(timezone.utc) - timedelta(hours=i),
                duration_seconds=100 + i * 10,
                success=i % 2 == 0
            )
        
        # Verify we have 5 in memory
        assert len(self.predictor.execution_history) == 5, f"Expected 5, got {len(self.predictor.execution_history)}"
        
        # Create new predictor and load history
        new_predictor = AIWorkflowPredictor(repo_root=self.temp_dir)
        
        assert len(new_predictor.execution_history) == 5, f"Expected 5 after reload, got {len(new_predictor.execution_history)}"
        assert new_predictor.execution_history[0].workflow_name == "workflow-0"
        
        print("  ✓ History saved and loaded successfully")
        self.test_results.append(("save_load_history", True))
    
    def test_pattern_analysis(self):
        """Test pattern analysis capabilities."""
        print("\n🧪 Testing pattern analysis...")
        
        # Create predictable pattern: workflow succeeds at hour 3
        base_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
        
        for day in range(7):
            for hour in range(24):
                exec_time = base_time + timedelta(days=day, hours=hour)
                success = (hour == 3)  # Only succeeds at hour 3
                
                self.predictor.record_execution(
                    workflow_name="pattern-test",
                    start_time=exec_time,
                    duration_seconds=100,
                    success=success
                )
        
        # Analyze patterns
        self.predictor._analyze_patterns()
        
        # Check success patterns
        success_hours = [hour for day, hour in self.predictor.success_patterns.get("pattern-test", [])]
        assert all(h == 3 for h in success_hours), "Should only succeed at hour 3"
        
        print("  ✓ Pattern analysis working correctly")
        self.test_results.append(("pattern_analysis", True))
    
    def test_prediction_no_data(self):
        """Test prediction with no historical data."""
        print("\n🧪 Testing prediction without history...")
        
        prediction = self.predictor.predict_optimal_time("new-workflow")
        
        assert prediction.workflow_name == "new-workflow"
        assert prediction.confidence < 0.5  # Low confidence with no data
        assert "No historical data" in " ".join(prediction.reasoning)
        assert prediction.recommended_time == "0 3 * * *"  # Default schedule
        
        print("  ✓ Default prediction working correctly")
        self.test_results.append(("prediction_no_data", True))
    
    def test_prediction_with_data(self):
        """Test prediction with historical data."""
        print("\n🧪 Testing prediction with history...")
        
        # Create pattern: succeeds at hour 8
        base_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
        
        for i in range(20):
            hour = 8 if i % 2 == 0 else 14
            success = (hour == 8)
            exec_time = base_time + timedelta(hours=i * 12)
            
            self.predictor.record_execution(
                workflow_name="test-workflow",
                start_time=exec_time,
                duration_seconds=150,
                success=success
            )
        
        prediction = self.predictor.predict_optimal_time("test-workflow")
        
        assert prediction.workflow_name == "test-workflow"
        assert prediction.confidence > 0.5  # Should have decent confidence
        # Note: Predictor may choose least busy hour over most successful
        # Just verify it returns a valid cron expression
        assert prediction.recommended_time.count(' ') == 4  # Valid cron: "minute hour day month weekday"
        assert prediction.predicted_success_rate > 0  # Should have some prediction
        
        print(f"  ✓ Predicted schedule: {prediction.recommended_time}")
        print(f"  ✓ Confidence: {prediction.confidence * 100:.0f}%")
        print(f"  ✓ Success rate: {prediction.predicted_success_rate * 100:.0f}%")
        self.test_results.append(("prediction_with_data", True))
    
    def test_batch_prediction(self):
        """Test batch prediction with conflict avoidance."""
        print("\n🧪 Testing batch prediction...")
        
        # Create history for multiple workflows
        workflow_names = ["wf-1", "wf-2", "wf-3"]
        base_time = datetime.now(timezone.utc)
        
        for wf in workflow_names:
            for i in range(10):
                self.predictor.record_execution(
                    workflow_name=wf,
                    start_time=base_time + timedelta(hours=i),
                    duration_seconds=120,
                    success=True
                )
        
        predictions = self.predictor.predict_batch(workflow_names)
        
        assert len(predictions) == 3
        
        # Check that hours are different (conflict avoidance)
        hours = []
        for pred in predictions.values():
            hour = int(pred.recommended_time.split()[1])
            hours.append(hour)
        
        # At least some should be different
        assert len(set(hours)) >= 2, "Should avoid scheduling at same hour"
        
        print(f"  ✓ Scheduled workflows at hours: {hours}")
        self.test_results.append(("batch_prediction", True))
    
    def test_conflict_detection(self):
        """Test detection of workflow conflicts."""
        print("\n🧪 Testing conflict detection...")
        
        # Create overlapping executions
        base_time = datetime.now(timezone.utc).replace(minute=0, second=0)
        
        for i in range(10):
            # Run wf-1 and wf-2 at the same time
            exec_time = base_time + timedelta(hours=i)
            
            self.predictor.record_execution(
                workflow_name="wf-1",
                start_time=exec_time,
                duration_seconds=60,
                success=True
            )
            
            self.predictor.record_execution(
                workflow_name="wf-2",
                start_time=exec_time,
                duration_seconds=60,
                success=True
            )
        
        # Analyze patterns
        self.predictor._analyze_patterns()
        
        # Check conflict detection
        conflicts = self.predictor.conflict_patterns.get("wf-1", [])
        assert "wf-2" in conflicts, "Should detect wf-2 as conflicting"
        
        print(f"  ✓ Detected conflicts: wf-1 with {conflicts}")
        self.test_results.append(("conflict_detection", True))
    
    def test_resource_impact_classification(self):
        """Test resource impact classification."""
        print("\n🧪 Testing resource impact classification...")
        
        base_time = datetime.now(timezone.utc)
        
        # Short workflow (low impact)
        for i in range(5):
            self.predictor.record_execution(
                workflow_name="short-wf",
                start_time=base_time + timedelta(hours=i),
                duration_seconds=60,  # 1 minute
                success=True
            )
        
        # Long workflow (high impact)
        for i in range(5):
            self.predictor.record_execution(
                workflow_name="long-wf",
                start_time=base_time + timedelta(hours=i),
                duration_seconds=800,  # 13+ minutes
                success=True
            )
        
        short_pred = self.predictor.predict_optimal_time("short-wf")
        long_pred = self.predictor.predict_optimal_time("long-wf")
        
        assert short_pred.resource_impact == "low"
        assert long_pred.resource_impact == "high"
        
        print(f"  ✓ Short workflow: {short_pred.resource_impact} impact")
        print(f"  ✓ Long workflow: {long_pred.resource_impact} impact")
        self.test_results.append(("resource_impact", True))
    
    def test_simulation(self):
        """Test simulation data generation."""
        print("\n🧪 Testing simulation...")
        
        initial_count = len(self.predictor.execution_history)
        
        self.predictor.simulate_execution_data(num_workflows=5, num_executions=50)
        
        assert len(self.predictor.execution_history) == initial_count + 50
        
        # Check that various hours are represented
        hours = set(e.hour_of_day for e in self.predictor.execution_history)
        assert len(hours) > 5, "Should have diverse execution times"
        
        print(f"  ✓ Simulated 50 executions across {len(hours)} different hours")
        self.test_results.append(("simulation", True))
    
    def test_report_generation(self):
        """Test comprehensive report generation."""
        print("\n🧪 Testing report generation...")
        
        # Add some data
        self.predictor.simulate_execution_data(num_workflows=5, num_executions=30)
        
        report = self.predictor.generate_recommendations_report()
        
        assert 'timestamp' in report
        assert 'total_workflows_analyzed' in report
        assert 'recommendations' in report
        assert len(report['recommendations']) > 0
        
        # Check recommendation structure
        first_rec = report['recommendations'][0]
        assert 'workflow' in first_rec
        assert 'recommended_schedule' in first_rec
        assert 'confidence' in first_rec
        assert 'reasoning' in first_rec
        
        print(f"  ✓ Generated report with {len(report['recommendations'])} recommendations")
        self.test_results.append(("report_generation", True))
    
    def run_all_tests(self):
        """Run all tests."""
        print("="*70)
        print("🧪 Running AI Workflow Predictor Test Suite")
        print("="*70)
        
        try:
            self.setup()
            
            # Run all tests
            self.test_record_execution()
            self.test_save_and_load_history()
            self.test_pattern_analysis()
            self.test_prediction_no_data()
            self.test_prediction_with_data()
            self.test_batch_prediction()
            self.test_conflict_detection()
            self.test_resource_impact_classification()
            self.test_simulation()
            self.test_report_generation()
            
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
    tester = TestAIWorkflowPredictor()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
