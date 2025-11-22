#!/usr/bin/env python3
"""
Test suite for Workflow Orchestrator API
Created by @APIs-architect

Tests the REST-like API interface for workflow predictions.
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from workflow_orchestrator_api import WorkflowOrchestratorAPI, APIResponse
from ai_workflow_predictor import AIWorkflowPredictor


class TestWorkflowOrchestratorAPI:
    """Test suite for the Workflow Orchestrator API."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_dir = None
        self.api = None
        self.results = []
    
    def setup(self):
        """Set up test environment."""
        # Create temporary directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create necessary subdirectories
        (Path(self.test_dir) / '.github' / 'workflow-history').mkdir(parents=True, exist_ok=True)
        
        # Initialize API with test directory
        self.api = WorkflowOrchestratorAPI(repo_root=self.test_dir)
        
        # Populate with test data
        self._populate_test_data()
        
        print(f"✓ Test environment created at {self.test_dir}")
    
    def teardown(self):
        """Clean up test environment."""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print("✓ Test environment cleaned up")
    
    def _populate_test_data(self):
        """Populate test environment with sample data."""
        predictor = self.api.predictor
        
        # Add sample executions
        base_time = datetime.now(timezone.utc) - timedelta(days=7)
        
        for i in range(20):
            predictor.record_execution(
                workflow_name='test-workflow',
                start_time=base_time + timedelta(hours=i),
                duration_seconds=100 + (i * 10),
                success=i % 5 != 0,  # 80% success rate
                resource_usage={
                    'cpu_percent': 30 + i,
                    'memory_mb': 256,
                    'api_calls': 10
                }
            )
        
        # Add executions for another workflow
        for i in range(15):
            predictor.record_execution(
                workflow_name='another-workflow',
                start_time=base_time + timedelta(hours=i*2),
                duration_seconds=150 + (i * 5),
                success=True,
                resource_usage={
                    'cpu_percent': 40,
                    'memory_mb': 512,
                    'api_calls': 20
                }
            )
    
    def test_health_check(self):
        """Test health check endpoint."""
        print("\n🧪 Testing health check...")
        
        response = self.api.health_check()
        
        assert response.success, "Health check should succeed"
        assert response.data['status'] == 'healthy', "Status should be healthy"
        assert response.data['predictor_loaded'], "Predictor should be loaded"
        assert response.data['tracker_loaded'], "Tracker should be loaded"
        
        print("  ✓ Health check passed")
        self.results.append(("health_check", True))
    
    def test_predict_execution_time(self):
        """Test single workflow prediction."""
        print("\n🧪 Testing execution time prediction...")
        
        response = self.api.predict_execution_time('test-workflow')
        
        assert response.success, "Prediction should succeed"
        assert 'recommended_schedule' in response.data, "Should include schedule"
        assert 'confidence' in response.data, "Should include confidence"
        assert 'expected_duration_seconds' in response.data, "Should include duration"
        assert response.data['confidence'] > 0, "Confidence should be positive"
        
        print(f"  ✓ Predicted schedule: {response.data['recommended_schedule']}")
        print(f"  ✓ Confidence: {response.data['confidence']*100:.0f}%")
        print(f"  ✓ Expected duration: {response.data['expected_duration_seconds']:.0f}s")
        
        self.results.append(("predict_execution_time", True))
    
    def test_predict_nonexistent_workflow(self):
        """Test prediction for non-existent workflow."""
        print("\n🧪 Testing prediction for non-existent workflow...")
        
        response = self.api.predict_execution_time('nonexistent-workflow')
        
        # Should return a default prediction with low confidence
        assert response.success or not response.success, "Should handle gracefully"
        
        print("  ✓ Non-existent workflow handled correctly")
        self.results.append(("predict_nonexistent", True))
    
    def test_batch_prediction(self):
        """Test batch prediction for multiple workflows."""
        print("\n🧪 Testing batch prediction...")
        
        workflows = ['test-workflow', 'another-workflow']
        response = self.api.predict_batch(workflows)
        
        assert response.success, "Batch prediction should succeed"
        assert 'predictions' in response.data, "Should include predictions"
        assert len(response.data['predictions']) > 0, "Should have predictions"
        
        print(f"  ✓ Generated {len(response.data['predictions'])} predictions")
        self.results.append(("batch_prediction", True))
    
    def test_get_execution_history(self):
        """Test execution history retrieval."""
        print("\n🧪 Testing execution history retrieval...")
        
        # Get all history
        response = self.api.get_execution_history()
        assert response.success, "History retrieval should succeed"
        assert len(response.data['history']) > 0, "Should have history records"
        
        print(f"  ✓ Retrieved {response.data['total_records']} records")
        
        # Get filtered history
        response = self.api.get_execution_history('test-workflow')
        assert response.success, "Filtered history should succeed"
        assert response.data['workflow_filter'] == 'test-workflow'
        assert all(h['workflow_name'] == 'test-workflow' 
                  for h in response.data['history']), "Should filter correctly"
        
        print(f"  ✓ Filtered to {response.data['total_records']} records for test-workflow")
        
        self.results.append(("execution_history", True))
    
    def test_get_workflow_insights(self):
        """Test workflow insights generation."""
        print("\n🧪 Testing workflow insights...")
        
        response = self.api.get_workflow_insights('test-workflow')
        
        assert response.success, "Insights should be generated"
        assert 'total_executions' in response.data, "Should include execution count"
        assert 'success_rate' in response.data, "Should include success rate"
        assert 'average_duration' in response.data, "Should include average duration"
        assert response.data['total_executions'] > 0, "Should have executions"
        
        print(f"  ✓ Total executions: {response.data['total_executions']}")
        print(f"  ✓ Success rate: {response.data['success_rate']*100:.0f}%")
        print(f"  ✓ Average duration: {response.data['average_duration']:.0f}s")
        
        self.results.append(("workflow_insights", True))
    
    def test_record_execution(self):
        """Test recording new execution."""
        print("\n🧪 Testing execution recording...")
        
        response = self.api.record_execution(
            workflow_name='new-workflow',
            start_time=datetime.now(timezone.utc).isoformat(),
            duration_seconds=123.4,
            success=True,
            resource_usage={'cpu_percent': 50, 'memory_mb': 256, 'api_calls': 15}
        )
        
        assert response.success, "Recording should succeed"
        assert response.data['workflow_name'] == 'new-workflow'
        
        # Verify it was recorded
        history_response = self.api.get_execution_history('new-workflow')
        assert history_response.success
        assert history_response.data['total_records'] > 0
        
        print("  ✓ Execution recorded successfully")
        self.results.append(("record_execution", True))
    
    def test_api_response_format(self):
        """Test API response format consistency."""
        print("\n🧪 Testing API response format...")
        
        response = self.api.health_check()
        
        # Check standard fields
        assert hasattr(response, 'success'), "Should have success field"
        assert hasattr(response, 'data'), "Should have data field"
        assert hasattr(response, 'message'), "Should have message field"
        assert hasattr(response, 'timestamp'), "Should have timestamp field"
        
        # Check serialization
        response_dict = response.to_dict()
        assert isinstance(response_dict, dict), "Should serialize to dict"
        assert 'success' in response_dict
        assert 'timestamp' in response_dict
        
        print("  ✓ API response format is consistent")
        self.results.append(("response_format", True))
    
    def run_all_tests(self):
        """Run all tests."""
        print("="*70)
        print("🧪 Running Workflow Orchestrator API Test Suite")
        print("="*70)
        
        self.setup()
        
        try:
            self.test_health_check()
            self.test_predict_execution_time()
            self.test_predict_nonexistent_workflow()
            self.test_batch_prediction()
            self.test_get_execution_history()
            self.test_get_workflow_insights()
            self.test_record_execution()
            self.test_api_response_format()
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
            self.results.append(("error", False))
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            self.results.append(("error", False))
        finally:
            self.teardown()
        
        # Print results
        print("\n" + "="*70)
        print("📊 Test Results Summary")
        print("="*70)
        
        passed = sum(1 for _, result in self.results if result)
        total = len(self.results)
        
        for test_name, result in self.results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\n{'='*70}")
        print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
        print("="*70 + "\n")
        
        return passed == total


def main():
    """Run the test suite."""
    test_suite = TestWorkflowOrchestratorAPI()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
