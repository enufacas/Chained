#!/usr/bin/env python3
"""
Tests for Workflow Anomaly Detector
Created by @create-botter

Comprehensive test suite for the workflow anomaly detection system.
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

from workflow_anomaly_detector import (
    WorkflowAnomalyDetector,
    AnomalyAlert,
    WorkflowHealthScore
)
from ai_workflow_predictor import AIWorkflowPredictor


class TestWorkflowAnomalyDetector:
    """Test suite for Workflow Anomaly Detector."""
    
    def __init__(self):
        self.temp_dir = None
        self.detector = None
        self.test_results = []
    
    def setup(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = WorkflowAnomalyDetector(repo_root=self.temp_dir)
        print(f"✓ Test environment created at {self.temp_dir}")
    
    def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"✓ Test environment cleaned up")
    
    def test_initialization(self):
        """Test detector initialization."""
        print("\n🧪 Testing initialization...")
        
        assert self.detector is not None
        assert self.detector.predictor is not None
        assert self.detector.alerts == []
        
        print("  ✓ Detector initialized correctly")
        self.test_results.append(("initialization", True))
    
    def test_duration_anomaly_detection(self):
        """Test detection of duration anomalies."""
        print("\n🧪 Testing duration anomaly detection...")
        
        # Create normal executions with slight variance (needed for std_dev calculation)
        base_time = datetime.now(timezone.utc)
        import random
        for i in range(20):
            # Add slight variance: 95-105 seconds
            duration = 100 + random.uniform(-5, 5)
            self.detector.predictor.record_execution(
                workflow_name="test-wf",
                start_time=base_time - timedelta(hours=i),
                duration_seconds=duration,  # Slightly varying duration
                success=True
            )
        
        # Test normal duration (no anomaly)
        alert = self.detector.detect_duration_anomaly("test-wf", 105)
        assert alert is None, "Should not detect anomaly for normal duration"
        
        # Test anomalous duration (very long - 5x normal)
        alert = self.detector.detect_duration_anomaly("test-wf", 500)
        assert alert is not None, "Should detect anomaly for extreme duration"
        assert alert.anomaly_type == "duration"
        assert alert.severity in ["medium", "high", "critical"]
        
        print(f"  ✓ Detected duration anomaly: {alert.message}")
        self.test_results.append(("duration_anomaly_detection", True))
    
    def test_failure_rate_anomaly_detection(self):
        """Test detection of failure rate anomalies."""
        print("\n🧪 Testing failure rate anomaly detection...")
        
        # Create historical executions with high success rate
        base_time = datetime.now(timezone.utc)
        for i in range(20):
            self.detector.predictor.record_execution(
                workflow_name="failure-test-wf",
                start_time=base_time - timedelta(hours=i+20),
                duration_seconds=100,
                success=(i % 10 != 0)  # 90% success rate
            )
        
        # Add recent executions with high failure rate
        for i in range(20):
            self.detector.predictor.record_execution(
                workflow_name="failure-test-wf",
                start_time=base_time - timedelta(hours=i),
                duration_seconds=100,
                success=(i % 2 == 0)  # 50% success rate (increase in failures)
            )
        
        alert = self.detector.detect_failure_rate_anomaly("failure-test-wf")
        assert alert is not None, "Should detect failure rate increase"
        assert alert.anomaly_type == "failure_rate"
        
        print(f"  ✓ Detected failure rate anomaly: {alert.message}")
        self.test_results.append(("failure_rate_anomaly_detection", True))
    
    def test_trend_anomaly_detection(self):
        """Test detection of performance trend anomalies."""
        print("\n🧪 Testing trend anomaly detection...")
        
        # Create executions with increasing duration (degrading performance)
        base_time = datetime.now(timezone.utc)
        for i in range(15):
            duration = 100 + (i * 20)  # Increasing duration: 100, 120, 140, ...
            self.detector.predictor.record_execution(
                workflow_name="trend-test-wf",
                start_time=base_time - timedelta(hours=15-i),
                duration_seconds=duration,
                success=True
            )
        
        alert = self.detector.detect_trend_anomaly("trend-test-wf")
        assert alert is not None, "Should detect upward trend"
        assert alert.anomaly_type == "trend"
        
        print(f"  ✓ Detected trend anomaly: {alert.message}")
        self.test_results.append(("trend_anomaly_detection", True))
    
    def test_health_score_calculation(self):
        """Test workflow health score calculation."""
        print("\n🧪 Testing health score calculation...")
        
        # Create healthy workflow executions
        base_time = datetime.now(timezone.utc)
        for i in range(30):
            self.detector.predictor.record_execution(
                workflow_name="healthy-wf",
                start_time=base_time - timedelta(hours=i),
                duration_seconds=100 + (i % 5),  # Slight variance
                success=True
            )
        
        health = self.detector.calculate_health_score("healthy-wf")
        
        assert health.overall_score > 70, f"Healthy workflow should have high score, got {health.overall_score}"
        assert health.success_score == 100.0, "All successful runs should have 100% success score"
        assert health.workflow_name == "healthy-wf"
        
        print(f"  ✓ Healthy workflow score: {health.overall_score}")
        
        # Create unhealthy workflow executions
        for i in range(30):
            self.detector.predictor.record_execution(
                workflow_name="unhealthy-wf",
                start_time=base_time - timedelta(hours=i),
                duration_seconds=100 + (i * 10),  # Increasing duration
                success=(i % 3 != 0)  # 66% success rate
            )
        
        unhealthy = self.detector.calculate_health_score("unhealthy-wf")
        
        assert unhealthy.overall_score < health.overall_score, "Unhealthy workflow should have lower score"
        assert unhealthy.success_score < 100, "Should reflect lower success rate"
        
        print(f"  ✓ Unhealthy workflow score: {unhealthy.overall_score}")
        self.test_results.append(("health_score_calculation", True))
    
    def test_insufficient_data_handling(self):
        """Test handling of workflows with insufficient data."""
        print("\n🧪 Testing insufficient data handling...")
        
        # Add only 2 executions (less than MIN_SAMPLES_FOR_ANALYSIS)
        base_time = datetime.now(timezone.utc)
        for i in range(2):
            self.detector.predictor.record_execution(
                workflow_name="insufficient-wf",
                start_time=base_time - timedelta(hours=i),
                duration_seconds=100,
                success=True
            )
        
        # Should not detect anomalies with insufficient data
        alert = self.detector.detect_duration_anomaly("insufficient-wf", 500)
        assert alert is None, "Should not detect anomaly with insufficient data"
        
        alert = self.detector.detect_failure_rate_anomaly("insufficient-wf")
        assert alert is None, "Should not detect anomaly with insufficient data"
        
        # Health score should return neutral values
        health = self.detector.calculate_health_score("new-wf")
        assert health.overall_score == 50.0, "Should return neutral score with no data"
        
        print("  ✓ Insufficient data handled correctly")
        self.test_results.append(("insufficient_data_handling", True))
    
    def test_alert_persistence(self):
        """Test alert saving and loading."""
        print("\n🧪 Testing alert persistence...")
        
        # Create some data and trigger an alert
        base_time = datetime.now(timezone.utc)
        for i in range(20):
            self.detector.predictor.record_execution(
                workflow_name="persist-test-wf",
                start_time=base_time - timedelta(hours=i),
                duration_seconds=100,
                success=True
            )
        
        # Trigger an anomaly
        self.detector.detect_duration_anomaly("persist-test-wf", 1000)
        
        # Verify alert was saved
        initial_alert_count = len(self.detector.alerts)
        assert initial_alert_count > 0, "Should have saved at least one alert"
        
        # Create new detector and verify alerts are loaded
        new_detector = WorkflowAnomalyDetector(repo_root=self.temp_dir)
        assert len(new_detector.alerts) == initial_alert_count, "Should load saved alerts"
        
        print(f"  ✓ {initial_alert_count} alert(s) persisted and loaded")
        self.test_results.append(("alert_persistence", True))
    
    def test_full_analysis(self):
        """Test full analysis run."""
        print("\n🧪 Testing full analysis...")
        
        # Create diverse workflow data
        self.detector.predictor.simulate_execution_data(num_workflows=5, num_executions=50)
        
        results = self.detector.run_full_analysis()
        
        assert 'timestamp' in results
        assert 'alerts' in results
        assert 'health_scores' in results
        assert 'summary' in results
        
        summary = results['summary']
        assert 'total_workflows' in summary
        assert 'average_health_score' in summary
        
        print(f"  ✓ Analyzed {summary['total_workflows']} workflows")
        print(f"  ✓ Average health score: {summary['average_health_score']}")
        self.test_results.append(("full_analysis", True))
    
    def test_export_results(self):
        """Test exporting results to JSON."""
        print("\n🧪 Testing export functionality...")
        
        # Create some data
        self.detector.predictor.simulate_execution_data(num_workflows=3, num_executions=30)
        
        # Export to file
        output_file = os.path.join(self.temp_dir, 'test_export.json')
        result_path = self.detector.export_results(output_file)
        
        assert os.path.exists(result_path), "Export file should exist"
        
        with open(result_path, 'r') as f:
            data = json.load(f)
        
        assert 'timestamp' in data
        assert 'health_scores' in data
        assert 'summary' in data
        
        print(f"  ✓ Successfully exported to {result_path}")
        self.test_results.append(("export_results", True))
    
    def run_all_tests(self):
        """Run all tests."""
        print("="*70)
        print("🧪 Running Workflow Anomaly Detector Test Suite")
        print("   Created by @create-botter")
        print("="*70)
        
        try:
            self.setup()
            
            self.test_initialization()
            self.test_duration_anomaly_detection()
            self.test_failure_rate_anomaly_detection()
            self.test_trend_anomaly_detection()
            self.test_health_score_calculation()
            self.test_insufficient_data_handling()
            self.test_alert_persistence()
            self.test_full_analysis()
            self.test_export_results()
            
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
    tester = TestWorkflowAnomalyDetector()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
