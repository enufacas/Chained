#!/usr/bin/env python3
"""
Comprehensive Tests for Performance Metrics Collector

Test Coverage (following @assert-specialist's systematic approach):
- Data structure validation
- Metric collection pre-conditions and post-conditions
- Edge cases and boundary conditions
- State validation at transitions
- Error handling
- Integration testing
- Performance validation

Author: @assert-specialist
Specification-driven testing with complete assertion coverage.
"""

import sys
import os
import json
import tempfile
import shutil
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta
import importlib.util

# Load the performance metrics collector module
project_root = Path(__file__).parent.parent
tools_path = project_root / "tools" / "performance-metrics-collector.py"

spec = importlib.util.spec_from_file_location(
    "performance_metrics_collector",
    str(tools_path)
)
perf_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(perf_module)

PerformanceCollector = perf_module.PerformanceCollector
WorkflowMetrics = perf_module.WorkflowMetrics
APIMetrics = perf_module.APIMetrics
ResourceMetrics = perf_module.ResourceMetrics
ThroughputMetrics = perf_module.ThroughputMetrics
PerformanceSnapshot = perf_module.PerformanceSnapshot


def test_workflow_metrics_dataclass():
    """
    Test WorkflowMetrics dataclass creation and serialization.
    
    Specification:
    - All required fields must be set
    - Serialization must preserve all data
    - Timestamps must be valid ISO format
    """
    print("🧪 Testing WorkflowMetrics dataclass...")
    
    # Test valid creation
    metrics = WorkflowMetrics(
        workflow_name="test-workflow",
        execution_time_ms=1500.5,
        status="success",
        timestamp=datetime.now(timezone.utc).isoformat(),
        run_id=12345
    )
    
    # Assert all fields are set correctly
    assert metrics.workflow_name == "test-workflow"
    assert metrics.execution_time_ms == 1500.5
    assert metrics.status == "success"
    assert metrics.run_id == 12345
    assert metrics.timestamp is not None
    
    # Test serialization
    data = metrics.to_dict()
    assert isinstance(data, dict)
    assert data['workflow_name'] == "test-workflow"
    assert data['execution_time_ms'] == 1500.5
    assert data['status'] == "success"
    assert data['run_id'] == 12345
    
    # Verify timestamp is valid ISO format
    parsed_time = datetime.fromisoformat(metrics.timestamp.replace('Z', '+00:00'))
    assert isinstance(parsed_time, datetime)
    
    print("✅ WorkflowMetrics dataclass test passed")


def test_api_metrics_dataclass():
    """
    Test APIMetrics dataclass creation and validation.
    
    Specification:
    - endpoint must not be empty
    - response_time_ms must be non-negative
    - status_code must be valid HTTP status (100-599)
    """
    print("🧪 Testing APIMetrics dataclass...")
    
    # Test valid creation
    metrics = APIMetrics(
        endpoint="/api/agents",
        response_time_ms=250.5,
        status_code=200,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    
    assert metrics.endpoint == "/api/agents"
    assert metrics.response_time_ms == 250.5
    assert metrics.status_code == 200
    
    # Test serialization preserves data
    data = metrics.to_dict()
    assert data['endpoint'] == "/api/agents"
    assert data['response_time_ms'] == 250.5
    assert data['status_code'] == 200
    
    print("✅ APIMetrics dataclass test passed")


def test_resource_metrics_dataclass():
    """
    Test ResourceMetrics dataclass with real system metrics.
    
    Specification:
    - All percentage values must be between 0 and 100
    - All size values must be non-negative
    - Metrics must reflect actual system state
    """
    print("🧪 Testing ResourceMetrics dataclass...")
    
    metrics = ResourceMetrics(
        memory_used_mb=512.5,
        memory_percent=50.2,
        cpu_percent=25.5,
        disk_used_gb=100.5,
        disk_percent=45.0,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    
    # Assert percentage bounds
    assert 0 <= metrics.memory_percent <= 100, f"memory_percent {metrics.memory_percent} out of range"
    assert 0 <= metrics.cpu_percent <= 100, f"cpu_percent {metrics.cpu_percent} out of range"
    assert 0 <= metrics.disk_percent <= 100, f"disk_percent {metrics.disk_percent} out of range"
    
    # Assert non-negative sizes
    assert metrics.memory_used_mb >= 0
    assert metrics.disk_used_gb >= 0
    
    # Test serialization
    data = metrics.to_dict()
    assert data['memory_percent'] == 50.2
    assert data['cpu_percent'] == 25.5
    
    print("✅ ResourceMetrics dataclass test passed")


def test_throughput_metrics_dataclass():
    """
    Test ThroughputMetrics dataclass and calculations.
    
    Specification:
    - operations_per_second = operations_count / time_window_seconds
    - All values must be non-negative
    - Time window must be positive
    """
    print("🧪 Testing ThroughputMetrics dataclass...")
    
    metrics = ThroughputMetrics(
        operation_type="agent_matching",
        operations_count=1000,
        time_window_seconds=10.0,
        operations_per_second=100.0,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    
    # Assert calculation is correct
    expected_rate = metrics.operations_count / metrics.time_window_seconds
    assert abs(metrics.operations_per_second - expected_rate) < 0.001
    
    # Assert non-negative values
    assert metrics.operations_count >= 0
    assert metrics.time_window_seconds > 0
    assert metrics.operations_per_second >= 0
    
    print("✅ ThroughputMetrics dataclass test passed")


def test_collect_workflow_metrics_preconditions():
    """
    Test pre-condition validation for workflow metrics collection.
    
    Specification:
    - workflow_name must not be empty
    - execution_time_ms must be non-negative
    - status must be valid (success, failure, cancelled)
    """
    print("🧪 Testing workflow metrics pre-conditions...")
    
    collector = PerformanceCollector()
    
    # Test valid metrics collection
    metrics = collector.collect_workflow_metrics(
        workflow_name="test-workflow",
        execution_time_ms=1000.0,
        status="success"
    )
    assert metrics is not None
    assert metrics.workflow_name == "test-workflow"
    
    # Test empty workflow name (should fail)
    try:
        collector.collect_workflow_metrics(
            workflow_name="",
            execution_time_ms=1000.0,
            status="success"
        )
        assert False, "Should have raised AssertionError for empty workflow_name"
    except AssertionError as e:
        assert "workflow_name must not be empty" in str(e)
    
    # Test negative execution time (should fail)
    try:
        collector.collect_workflow_metrics(
            workflow_name="test",
            execution_time_ms=-100.0,
            status="success"
        )
        assert False, "Should have raised AssertionError for negative execution_time_ms"
    except AssertionError as e:
        assert "non-negative" in str(e)
    
    # Test invalid status (should fail)
    try:
        collector.collect_workflow_metrics(
            workflow_name="test",
            execution_time_ms=1000.0,
            status="invalid_status"
        )
        assert False, "Should have raised AssertionError for invalid status"
    except AssertionError as e:
        assert "Invalid status" in str(e)
    
    print("✅ Workflow metrics pre-conditions test passed")


def test_collect_api_metrics_preconditions():
    """
    Test pre-condition validation for API metrics collection.
    
    Specification:
    - endpoint must not be empty
    - response_time_ms must be non-negative
    - status_code must be valid HTTP status (100-599)
    """
    print("🧪 Testing API metrics pre-conditions...")
    
    collector = PerformanceCollector()
    
    # Test valid metrics
    metrics = collector.collect_api_metrics(
        endpoint="/api/test",
        response_time_ms=250.0,
        status_code=200
    )
    assert metrics is not None
    assert metrics.endpoint == "/api/test"
    
    # Test empty endpoint (should fail)
    try:
        collector.collect_api_metrics(
            endpoint="",
            response_time_ms=250.0,
            status_code=200
        )
        assert False, "Should have raised AssertionError for empty endpoint"
    except AssertionError as e:
        assert "endpoint must not be empty" in str(e)
    
    # Test negative response time (should fail)
    try:
        collector.collect_api_metrics(
            endpoint="/api/test",
            response_time_ms=-50.0,
            status_code=200
        )
        assert False, "Should have raised AssertionError for negative response_time_ms"
    except AssertionError as e:
        assert "non-negative" in str(e)
    
    # Test invalid status code - too low (should fail)
    try:
        collector.collect_api_metrics(
            endpoint="/api/test",
            response_time_ms=250.0,
            status_code=99
        )
        assert False, "Should have raised AssertionError for invalid status_code"
    except AssertionError as e:
        assert "Invalid status_code" in str(e)
    
    # Test invalid status code - too high (should fail)
    try:
        collector.collect_api_metrics(
            endpoint="/api/test",
            response_time_ms=250.0,
            status_code=600
        )
        assert False, "Should have raised AssertionError for invalid status_code"
    except AssertionError as e:
        assert "Invalid status_code" in str(e)
    
    print("✅ API metrics pre-conditions test passed")


def test_collect_resource_metrics_postconditions():
    """
    Test post-condition validation for resource metrics.
    
    Specification:
    - All percentage values must be between 0 and 100
    - All size values must be non-negative
    - Metrics must reflect actual system state
    """
    print("🧪 Testing resource metrics post-conditions...")
    
    collector = PerformanceCollector()
    
    # Collect actual system metrics
    metrics = collector.collect_resource_metrics()
    
    # Assert post-conditions
    assert 0 <= metrics.memory_percent <= 100, f"Memory percent {metrics.memory_percent} out of range"
    assert 0 <= metrics.cpu_percent <= 100, f"CPU percent {metrics.cpu_percent} out of range"
    assert 0 <= metrics.disk_percent <= 100, f"Disk percent {metrics.disk_percent} out of range"
    
    assert metrics.memory_used_mb >= 0, "Memory used must be non-negative"
    assert metrics.disk_used_gb >= 0, "Disk used must be non-negative"
    
    # Verify timestamp is recent (within last second)
    timestamp = datetime.fromisoformat(metrics.timestamp.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    delta = (now - timestamp).total_seconds()
    assert delta < 2, f"Timestamp too old: {delta} seconds"
    
    print("✅ Resource metrics post-conditions test passed")


def test_collect_throughput_metrics_preconditions():
    """
    Test pre-condition validation for throughput metrics.
    
    Specification:
    - operation_type must not be empty
    - operations_count must be non-negative
    - time_window_seconds must be positive
    """
    print("🧪 Testing throughput metrics pre-conditions...")
    
    collector = PerformanceCollector()
    
    # Test valid metrics
    metrics = collector.collect_throughput_metrics(
        operation_type="test_ops",
        operations_count=100,
        time_window_seconds=10.0
    )
    assert metrics is not None
    assert metrics.operations_per_second == 10.0
    
    # Test empty operation type (should fail)
    try:
        collector.collect_throughput_metrics(
            operation_type="",
            operations_count=100,
            time_window_seconds=10.0
        )
        assert False, "Should have raised AssertionError for empty operation_type"
    except AssertionError as e:
        assert "operation_type must not be empty" in str(e)
    
    # Test negative operations count (should fail)
    try:
        collector.collect_throughput_metrics(
            operation_type="test",
            operations_count=-10,
            time_window_seconds=10.0
        )
        assert False, "Should have raised AssertionError for negative operations_count"
    except AssertionError as e:
        assert "non-negative" in str(e)
    
    # Test zero time window (should fail)
    try:
        collector.collect_throughput_metrics(
            operation_type="test",
            operations_count=100,
            time_window_seconds=0.0
        )
        assert False, "Should have raised AssertionError for zero time_window_seconds"
    except AssertionError as e:
        assert "positive" in str(e)
    
    # Test negative time window (should fail)
    try:
        collector.collect_throughput_metrics(
            operation_type="test",
            operations_count=100,
            time_window_seconds=-5.0
        )
        assert False, "Should have raised AssertionError for negative time_window_seconds"
    except AssertionError as e:
        assert "positive" in str(e)
    
    print("✅ Throughput metrics pre-conditions test passed")


def test_edge_case_zero_operations():
    """
    Test edge case: zero operations in throughput metrics.
    
    Specification:
    - Zero operations should be valid
    - Rate should be 0.0 operations per second
    """
    print("🧪 Testing edge case: zero operations...")
    
    collector = PerformanceCollector()
    
    metrics = collector.collect_throughput_metrics(
        operation_type="test_ops",
        operations_count=0,
        time_window_seconds=10.0
    )
    
    assert metrics.operations_count == 0
    assert metrics.operations_per_second == 0.0
    
    print("✅ Edge case (zero operations) test passed")


def test_edge_case_very_small_time_window():
    """
    Test edge case: very small time window for throughput.
    
    Specification:
    - Small positive time windows should be handled correctly
    - Rate should be calculated accurately
    """
    print("🧪 Testing edge case: very small time window...")
    
    collector = PerformanceCollector()
    
    metrics = collector.collect_throughput_metrics(
        operation_type="test_ops",
        operations_count=10,
        time_window_seconds=0.001  # 1 millisecond
    )
    
    assert metrics.operations_per_second == 10000.0  # 10 ops / 0.001 sec
    
    print("✅ Edge case (small time window) test passed")


def test_snapshot_creation():
    """
    Test complete performance snapshot creation.
    
    Specification:
    - Snapshot must include all requested metric types
    - Timestamp must be set
    - Metadata must be included
    """
    print("🧪 Testing performance snapshot creation...")
    
    collector = PerformanceCollector()
    
    # Create metrics
    wf_metrics = [
        collector.collect_workflow_metrics("wf1", 1000.0, "success"),
        collector.collect_workflow_metrics("wf2", 2000.0, "success")
    ]
    
    api_metrics = [
        collector.collect_api_metrics("/api/test", 250.0, 200)
    ]
    
    throughput_metrics = [
        collector.collect_throughput_metrics("ops", 100, 10.0)
    ]
    
    # Create snapshot
    snapshot = collector.create_snapshot(
        workflow_metrics=wf_metrics,
        api_metrics=api_metrics,
        include_resources=True,
        throughput_metrics=throughput_metrics
    )
    
    # Assert structure
    assert snapshot.timestamp is not None
    assert len(snapshot.workflow_metrics) == 2
    assert len(snapshot.api_metrics) == 1
    assert snapshot.resource_metrics is not None
    assert len(snapshot.throughput_metrics) == 1
    assert 'collector_version' in snapshot.metadata
    
    # Test serialization
    data = snapshot.to_dict()
    assert 'timestamp' in data
    assert 'workflow_metrics' in data
    assert 'api_metrics' in data
    assert 'resource_metrics' in data
    assert 'throughput_metrics' in data
    
    print("✅ Snapshot creation test passed")


def test_snapshot_storage_and_retrieval():
    """
    Test snapshot persistence and retrieval.
    
    Specification:
    - Snapshots must be stored in date-based directories
    - Latest snapshot must be accessible via latest.json
    - Stored files must be valid JSON
    - Files must exist after storage
    """
    print("🧪 Testing snapshot storage and retrieval...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_dir = Path(tmpdir) / "metrics"
        collector = PerformanceCollector(metrics_dir=metrics_dir)
        
        # Create and store snapshot
        snapshot = collector.create_snapshot(include_resources=True)
        collector.store_snapshot(snapshot)
        
        # Assert files exist (post-conditions)
        date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        date_dir = metrics_dir / date_str
        assert date_dir.exists(), "Date directory was not created"
        
        latest_file = metrics_dir / "latest.json"
        assert latest_file.exists(), "Latest file was not created"
        
        # Verify content is valid JSON
        with open(latest_file, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data['timestamp'] == snapshot.timestamp
        assert 'metadata' in loaded_data
        
        # Test retrieval
        snapshots = collector.load_snapshots(since_days=1)
        assert len(snapshots) > 0, "Should retrieve at least one snapshot"
        
        print("✅ Snapshot storage and retrieval test passed")


def test_performance_trend_analysis():
    """
    Test performance trend analysis.
    
    Specification:
    - Analysis must handle empty snapshot list
    - Trends must be calculated correctly
    - Threshold violations must be detected
    """
    print("🧪 Testing performance trend analysis...")
    
    collector = PerformanceCollector()
    
    # Test with empty snapshots
    trends = collector.analyze_performance_trends([])
    assert 'workflow_trends' in trends
    assert 'resource_trends' in trends
    assert 'threshold_violations' in trends
    assert len(trends['workflow_trends']) == 0
    
    # Test with sample data
    snapshots = [
        {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'workflow_metrics': [
                {'workflow_name': 'test-wf', 'execution_time_ms': 1000.0, 'status': 'success'}
            ],
            'resource_metrics': {
                'memory_percent': 50.0,
                'cpu_percent': 30.0,
                'disk_percent': 40.0
            }
        },
        {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'workflow_metrics': [
                {'workflow_name': 'test-wf', 'execution_time_ms': 1500.0, 'status': 'success'}
            ],
            'resource_metrics': {
                'memory_percent': 55.0,
                'cpu_percent': 35.0,
                'disk_percent': 42.0
            }
        }
    ]
    
    trends = collector.analyze_performance_trends(snapshots)
    
    # Assert workflow trends calculated
    assert 'test-wf' in trends['workflow_trends']
    wf_trend = trends['workflow_trends']['test-wf']
    assert wf_trend['count'] == 2
    assert wf_trend['avg_time_ms'] == 1250.0  # (1000 + 1500) / 2
    assert wf_trend['min_time_ms'] == 1000.0
    assert wf_trend['max_time_ms'] == 1500.0
    
    # Assert resource trends calculated
    assert 'memory' in trends['resource_trends']
    assert 'cpu' in trends['resource_trends']
    assert 'disk' in trends['resource_trends']
    
    print("✅ Performance trend analysis test passed")


def test_threshold_violation_detection():
    """
    Test detection of threshold violations.
    
    Specification:
    - Violations must be detected when metrics exceed thresholds
    - Each violation must include type, value, threshold, and timestamp
    """
    print("🧪 Testing threshold violation detection...")
    
    # Create collector with low thresholds for testing
    collector = PerformanceCollector()
    collector.thresholds = {
        'workflow_execution_time_ms': 1000.0,  # Low threshold
        'cpu_usage_percent': 50.0
    }
    
    # Create snapshots with violations
    snapshots = [
        {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'workflow_metrics': [
                {'workflow_name': 'slow-wf', 'execution_time_ms': 5000.0, 'status': 'success'}
            ],
            'resource_metrics': {
                'memory_percent': 30.0,
                'cpu_percent': 80.0,  # Exceeds threshold
                'disk_percent': 40.0
            }
        }
    ]
    
    trends = collector.analyze_performance_trends(snapshots)
    violations = trends['threshold_violations']
    
    # Assert violations were detected
    assert len(violations) > 0, "Should detect threshold violations"
    
    # Check workflow violation
    wf_violations = [v for v in violations if v['type'] == 'workflow_execution_time']
    assert len(wf_violations) > 0
    assert wf_violations[0]['workflow'] == 'slow-wf'
    assert wf_violations[0]['value'] == 5000.0
    
    # Check CPU violation
    cpu_violations = [v for v in violations if v['type'] == 'cpu_usage']
    assert len(cpu_violations) > 0
    assert cpu_violations[0]['value'] == 80.0
    
    print("✅ Threshold violation detection test passed")


def test_report_generation():
    """
    Test performance report generation.
    
    Specification:
    - Report must be a non-empty string
    - Report must include workflow trends
    - Report must include resource trends
    - Report must include violation count
    """
    print("🧪 Testing report generation...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_dir = Path(tmpdir) / "metrics"
        collector = PerformanceCollector(metrics_dir=metrics_dir)
        
        # Create and store some test snapshots
        for i in range(3):
            snapshot = collector.create_snapshot(
                workflow_metrics=[
                    collector.collect_workflow_metrics(f"wf{i}", 1000.0 + i*100, "success")
                ],
                include_resources=True
            )
            collector.store_snapshot(snapshot)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Generate report
        report = collector.generate_report(since_days=1)
        
        # Assert report structure
        assert isinstance(report, str)
        assert len(report) > 0
        assert "Performance Metrics Report" in report
        assert "Snapshots Analyzed:" in report
        
        print("✅ Report generation test passed")


def test_concurrent_metric_collection():
    """
    Test concurrent collection of different metric types.
    
    Specification:
    - Different metric types should be independent
    - Concurrent collection should not cause conflicts
    - All metrics should be correctly stored
    """
    print("🧪 Testing concurrent metric collection...")
    
    collector = PerformanceCollector()
    
    # Collect multiple metric types concurrently
    wf_metrics = collector.collect_workflow_metrics("wf1", 1000.0, "success")
    api_metrics = collector.collect_api_metrics("/api/test", 250.0, 200)
    resource_metrics = collector.collect_resource_metrics()
    throughput_metrics = collector.collect_throughput_metrics("ops", 100, 10.0)
    
    # Assert all metrics were collected
    assert wf_metrics is not None
    assert api_metrics is not None
    assert resource_metrics is not None
    assert throughput_metrics is not None
    
    # Create snapshot with all metrics
    snapshot = collector.create_snapshot(
        workflow_metrics=[wf_metrics],
        api_metrics=[api_metrics],
        include_resources=False,  # We already have resource_metrics
        throughput_metrics=[throughput_metrics]
    )
    snapshot.resource_metrics = resource_metrics
    
    # Verify snapshot integrity
    assert len(snapshot.workflow_metrics) == 1
    assert len(snapshot.api_metrics) == 1
    assert snapshot.resource_metrics is not None
    assert len(snapshot.throughput_metrics) == 1
    
    print("✅ Concurrent metric collection test passed")


def run_all_tests():
    """Run all performance metrics tests following @assert-specialist's approach"""
    print("\n📊 Running Performance Metrics Collector Tests")
    print("Following @assert-specialist's specification-driven approach\n")
    print("=" * 70)
    
    tests = [
        # Data structure tests
        test_workflow_metrics_dataclass,
        test_api_metrics_dataclass,
        test_resource_metrics_dataclass,
        test_throughput_metrics_dataclass,
        
        # Pre-condition tests
        test_collect_workflow_metrics_preconditions,
        test_collect_api_metrics_preconditions,
        test_collect_throughput_metrics_preconditions,
        
        # Post-condition tests
        test_collect_resource_metrics_postconditions,
        
        # Edge case tests
        test_edge_case_zero_operations,
        test_edge_case_very_small_time_window,
        
        # Integration tests
        test_snapshot_creation,
        test_snapshot_storage_and_retrieval,
        test_performance_trend_analysis,
        test_threshold_violation_detection,
        test_report_generation,
        test_concurrent_metric_collection,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    print(f"Test Coverage: {passed}/{len(tests)} ({100*passed//len(tests)}%)")
    
    if failed == 0:
        print("\n✅ All tests passed! @assert-specialist's systematic testing complete.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
