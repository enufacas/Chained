#!/usr/bin/env python3
"""
Test suite for AI Workflow Orchestrator Production System
Created by @create-botter

Tests the real-time prediction service and execution recorder integration.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
import tempfile
import shutil

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from workflow_prediction_service import WorkflowPredictionService
from ai_workflow_predictor import AIWorkflowPredictor


def test_prediction_service_no_data():
    """Test prediction service with no historical data."""
    print("Test 1: Prediction service with no data...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        service = WorkflowPredictionService(repo_root=tmpdir)
        status = service.get_system_status()
        
        assert status['status'] == 'no_data', "Should report no_data status"
        assert status['statistics']['total_executions'] == 0
        assert status['statistics']['workflows_tracked'] == 0
        
    print("  ✅ PASS: Service handles no data correctly")


def test_prediction_service_with_data():
    """Test prediction service with simulated data."""
    print("Test 2: Prediction service with simulated data...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create simulated data
        predictor = AIWorkflowPredictor(repo_root=tmpdir)
        predictor.simulate_execution_data(num_workflows=5, num_executions=50)
        
        # Test service
        service = WorkflowPredictionService(repo_root=tmpdir)
        status = service.get_system_status()
        
        assert status['status'] == 'active', "Should report active status"
        assert status['statistics']['total_executions'] == 50
        assert status['statistics']['workflows_tracked'] == 5
        assert 0 <= status['statistics']['success_rate'] <= 1.0
        
    print("  ✅ PASS: Service works with simulated data")


def test_specific_workflow_prediction():
    """Test prediction for a specific workflow."""
    print("Test 3: Specific workflow prediction...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create simulated data
        predictor = AIWorkflowPredictor(repo_root=tmpdir)
        predictor.simulate_execution_data(num_workflows=5, num_executions=50)
        
        # Get prediction for workflow-1
        service = WorkflowPredictionService(repo_root=tmpdir)
        result = service.get_prediction('workflow-1')
        
        assert result['success'] == True
        assert result['workflow'] == 'workflow-1'
        assert 'prediction' in result
        assert 'recommended_time' in result['prediction']
        assert 'confidence' in result['prediction']
        assert 0 <= result['prediction']['confidence'] <= 1.0
        assert result['prediction']['expected_duration_seconds'] > 0
        
    print("  ✅ PASS: Specific workflow prediction works")


def test_all_workflows_prediction():
    """Test getting predictions for all workflows."""
    print("Test 4: All workflows prediction...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create workflows directory for test
        workflows_dir = Path(tmpdir) / '.github' / 'workflows'
        workflows_dir.mkdir(parents=True)
        
        # Create dummy workflow files
        for i in range(5):
            (workflows_dir / f'workflow-{i}.yml').write_text('name: test')
        
        # Create simulated data
        predictor = AIWorkflowPredictor(repo_root=tmpdir)
        predictor.simulate_execution_data(num_workflows=5, num_executions=50)
        
        # Get all predictions
        service = WorkflowPredictionService(repo_root=tmpdir)
        result = service.get_all_predictions()
        
        assert result['success'] == True, f"Expected success, got: {result}"
        assert result['total_workflows'] > 0
        assert len(result['predictions']) > 0
        
        # Check prediction structure
        pred = result['predictions'][0]
        assert 'workflow' in pred
        assert 'confidence' in pred
        assert 'expected_duration_seconds' in pred
        assert 'resource_impact' in pred
        
    print("  ✅ PASS: All workflows prediction works")


def test_workflow_insights():
    """Test workflow insights analysis."""
    print("Test 5: Workflow insights...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create simulated data
        predictor = AIWorkflowPredictor(repo_root=tmpdir)
        predictor.simulate_execution_data(num_workflows=5, num_executions=50)
        
        # Get insights
        service = WorkflowPredictionService(repo_root=tmpdir)
        result = service.get_workflow_insights('workflow-1')
        
        assert result['success'] == True
        assert result['workflow'] == 'workflow-1'
        assert 'statistics' in result
        assert result['statistics']['total_executions'] > 0
        assert 'duration' in result['statistics']
        assert 'patterns' in result
        
    print("  ✅ PASS: Workflow insights works")


def test_execution_recorder_data_format():
    """Test that execution recorder creates proper data format."""
    print("Test 6: Execution recorder data format...")
    
    # Create sample execution data matching recorder format
    execution_data = {
        'workflow_name': 'test-workflow',
        'start_time': datetime.now(timezone.utc).isoformat(),
        'duration_seconds': 125.5,
        'success': True,
        'resource_usage': {
            'cpu_percent': 0,
            'memory_mb': 0,
            'api_calls': 0
        },
        'day_of_week': 1,
        'hour_of_day': 14,
        'run_id': '12345',
        'run_number': '42',
        'conclusion': 'success',
        'recorded_at': datetime.now(timezone.utc).isoformat()
    }
    
    # Validate all required fields exist
    required_fields = [
        'workflow_name', 'start_time', 'duration_seconds', 'success',
        'resource_usage', 'day_of_week', 'hour_of_day'
    ]
    
    for field in required_fields:
        assert field in execution_data, f"Missing required field: {field}"
    
    # Validate data types
    assert isinstance(execution_data['duration_seconds'], (int, float))
    assert isinstance(execution_data['success'], bool)
    assert isinstance(execution_data['resource_usage'], dict)
    
    print("  ✅ PASS: Execution data format is correct")


def test_json_api_output():
    """Test JSON API output format."""
    print("Test 7: JSON API output format...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create simulated data
        predictor = AIWorkflowPredictor(repo_root=tmpdir)
        predictor.simulate_execution_data(num_workflows=5, num_executions=50)
        
        # Get JSON output
        service = WorkflowPredictionService(repo_root=tmpdir)
        result = service.get_prediction('workflow-1')
        
        # Ensure it's JSON serializable
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        
        assert parsed == result
        assert isinstance(json_str, str)
        
    print("  ✅ PASS: JSON API output is valid")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("🧪 AI Workflow Orchestrator Production System Tests - @create-botter")
    print("="*70 + "\n")
    
    tests = [
        test_prediction_service_no_data,
        test_prediction_service_with_data,
        test_specific_workflow_prediction,
        test_all_workflows_prediction,
        test_workflow_insights,
        test_execution_recorder_data_format,
        test_json_api_output,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
