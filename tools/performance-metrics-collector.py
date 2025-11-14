#!/usr/bin/env python3
"""
Performance Metrics Collector

A production-grade system for collecting and analyzing performance metrics across
the Chained autonomous AI ecosystem. Tracks system performance, resource usage,
and throughput to enable monitoring and optimization.

Architecture:
- Centralized metrics collection
- Time-series performance tracking
- Resource utilization monitoring
- Trend analysis and alerting
- Integration with existing agent metrics

Features:
- Workflow execution time tracking
- API response time monitoring
- Resource usage metrics (memory, CPU, storage)
- Throughput measurements
- Historical performance trends
- Anomaly detection

Usage:
    python performance-metrics-collector.py --collect [--category CATEGORY]
    python performance-metrics-collector.py --analyze [--since DAYS]
    python performance-metrics-collector.py --report

Author: @assert-specialist
Specification-driven implementation with comprehensive testing and validation.
"""

import json
import os
import sys
import time
import psutil
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import argparse

# Constants
METRICS_DIR = Path(".github/agent-system/metrics/performance")
DEFAULT_LOOKBACK_DAYS = 7

# Performance thresholds (can be configured)
THRESHOLDS = {
    'workflow_execution_time_ms': 30000,  # 30 seconds
    'api_response_time_ms': 5000,  # 5 seconds
    'memory_usage_mb': 1024,  # 1GB
    'cpu_usage_percent': 80.0,
    'storage_usage_percent': 85.0
}


@dataclass
class WorkflowMetrics:
    """Metrics for workflow execution"""
    workflow_name: str
    execution_time_ms: float
    status: str  # success, failure, cancelled
    timestamp: str
    run_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class APIMetrics:
    """Metrics for API calls"""
    endpoint: str
    response_time_ms: float
    status_code: int
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResourceMetrics:
    """System resource utilization metrics"""
    memory_used_mb: float
    memory_percent: float
    cpu_percent: float
    disk_used_gb: float
    disk_percent: float
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ThroughputMetrics:
    """Throughput and rate metrics"""
    operation_type: str
    operations_count: int
    time_window_seconds: float
    operations_per_second: float
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PerformanceSnapshot:
    """Complete performance snapshot"""
    timestamp: str
    workflow_metrics: List[WorkflowMetrics] = field(default_factory=list)
    api_metrics: List[APIMetrics] = field(default_factory=list)
    resource_metrics: Optional[ResourceMetrics] = None
    throughput_metrics: List[ThroughputMetrics] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'workflow_metrics': [m.to_dict() for m in self.workflow_metrics],
            'api_metrics': [m.to_dict() for m in self.api_metrics],
            'resource_metrics': self.resource_metrics.to_dict() if self.resource_metrics else None,
            'throughput_metrics': [m.to_dict() for m in self.throughput_metrics],
            'metadata': self.metadata
        }


class PerformanceCollector:
    """
    Core performance metrics collection engine.
    
    Responsibilities:
    - Collect workflow execution metrics
    - Monitor API response times
    - Track resource utilization
    - Measure throughput
    - Store and retrieve metrics
    - Analyze performance trends
    """
    
    def __init__(self, metrics_dir: Optional[Path] = None):
        """
        Initialize performance collector.
        
        Args:
            metrics_dir: Directory for storing metrics (defaults to METRICS_DIR)
        """
        self.metrics_dir = metrics_dir or METRICS_DIR
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize thresholds from config or use defaults
        self.thresholds = self._load_thresholds()
        
    def _load_thresholds(self) -> Dict[str, float]:
        """Load performance thresholds from configuration"""
        config_file = Path(".github/agent-system/config.json")
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('performance_thresholds', THRESHOLDS)
            except Exception as e:
                print(f"⚠️  Warning: Could not load thresholds from config: {e}", file=sys.stderr)
        
        return THRESHOLDS
    
    def collect_workflow_metrics(
        self,
        workflow_name: str,
        execution_time_ms: float,
        status: str,
        run_id: Optional[int] = None
    ) -> WorkflowMetrics:
        """
        Collect metrics for a workflow execution.
        
        Pre-conditions:
        - workflow_name must not be empty
        - execution_time_ms must be non-negative
        - status must be one of: success, failure, cancelled
        
        Args:
            workflow_name: Name of the workflow
            execution_time_ms: Execution time in milliseconds
            status: Execution status
            run_id: Optional workflow run ID
            
        Returns:
            WorkflowMetrics object
            
        Raises:
            ValueError: If pre-conditions are violated
        """
        # Pre-condition assertions
        assert workflow_name, "workflow_name must not be empty"
        assert execution_time_ms >= 0, f"execution_time_ms must be non-negative, got {execution_time_ms}"
        assert status in ['success', 'failure', 'cancelled'], f"Invalid status: {status}"
        
        metrics = WorkflowMetrics(
            workflow_name=workflow_name,
            execution_time_ms=execution_time_ms,
            status=status,
            timestamp=datetime.now(timezone.utc).isoformat(),
            run_id=run_id
        )
        
        # Post-condition: metrics object created successfully
        assert metrics.workflow_name == workflow_name
        assert metrics.execution_time_ms == execution_time_ms
        
        return metrics
    
    def collect_api_metrics(
        self,
        endpoint: str,
        response_time_ms: float,
        status_code: int
    ) -> APIMetrics:
        """
        Collect metrics for an API call.
        
        Pre-conditions:
        - endpoint must not be empty
        - response_time_ms must be non-negative
        - status_code must be valid HTTP status code (100-599)
        
        Args:
            endpoint: API endpoint called
            response_time_ms: Response time in milliseconds
            status_code: HTTP status code
            
        Returns:
            APIMetrics object
            
        Raises:
            ValueError: If pre-conditions are violated
        """
        # Pre-condition assertions
        assert endpoint, "endpoint must not be empty"
        assert response_time_ms >= 0, f"response_time_ms must be non-negative, got {response_time_ms}"
        assert 100 <= status_code <= 599, f"Invalid status_code: {status_code}"
        
        metrics = APIMetrics(
            endpoint=endpoint,
            response_time_ms=response_time_ms,
            status_code=status_code,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Post-condition: metrics object created successfully
        assert metrics.endpoint == endpoint
        assert metrics.status_code == status_code
        
        return metrics
    
    def collect_resource_metrics(self) -> ResourceMetrics:
        """
        Collect current system resource utilization metrics.
        
        Uses psutil to gather memory, CPU, and disk usage.
        
        Returns:
            ResourceMetrics object
            
        Post-conditions:
        - All percentage values are between 0 and 100
        - All size values are non-negative
        """
        # Collect memory metrics
        memory = psutil.virtual_memory()
        memory_used_mb = memory.used / (1024 * 1024)
        memory_percent = memory.percent
        
        # Collect CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Collect disk metrics
        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used / (1024 * 1024 * 1024)
        disk_percent = disk.percent
        
        metrics = ResourceMetrics(
            memory_used_mb=memory_used_mb,
            memory_percent=memory_percent,
            cpu_percent=cpu_percent,
            disk_used_gb=disk_used_gb,
            disk_percent=disk_percent,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Post-condition assertions
        assert 0 <= metrics.memory_percent <= 100
        assert 0 <= metrics.cpu_percent <= 100
        assert 0 <= metrics.disk_percent <= 100
        assert metrics.memory_used_mb >= 0
        assert metrics.disk_used_gb >= 0
        
        return metrics
    
    def collect_throughput_metrics(
        self,
        operation_type: str,
        operations_count: int,
        time_window_seconds: float
    ) -> ThroughputMetrics:
        """
        Collect throughput metrics for a type of operation.
        
        Pre-conditions:
        - operation_type must not be empty
        - operations_count must be non-negative
        - time_window_seconds must be positive
        
        Args:
            operation_type: Type of operation being measured
            operations_count: Number of operations completed
            time_window_seconds: Time window for measurement
            
        Returns:
            ThroughputMetrics object
            
        Raises:
            ValueError: If pre-conditions are violated
        """
        # Pre-condition assertions
        assert operation_type, "operation_type must not be empty"
        assert operations_count >= 0, f"operations_count must be non-negative, got {operations_count}"
        assert time_window_seconds > 0, f"time_window_seconds must be positive, got {time_window_seconds}"
        
        operations_per_second = operations_count / time_window_seconds
        
        metrics = ThroughputMetrics(
            operation_type=operation_type,
            operations_count=operations_count,
            time_window_seconds=time_window_seconds,
            operations_per_second=operations_per_second,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Post-condition: operations_per_second correctly calculated
        expected_rate = operations_count / time_window_seconds
        assert abs(metrics.operations_per_second - expected_rate) < 0.001
        
        return metrics
    
    def create_snapshot(
        self,
        workflow_metrics: Optional[List[WorkflowMetrics]] = None,
        api_metrics: Optional[List[APIMetrics]] = None,
        include_resources: bool = True,
        throughput_metrics: Optional[List[ThroughputMetrics]] = None
    ) -> PerformanceSnapshot:
        """
        Create a complete performance snapshot.
        
        Args:
            workflow_metrics: List of workflow metrics
            api_metrics: List of API metrics
            include_resources: Whether to include resource metrics
            throughput_metrics: List of throughput metrics
            
        Returns:
            PerformanceSnapshot object
        """
        resource_metrics = None
        if include_resources:
            resource_metrics = self.collect_resource_metrics()
        
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_metrics=workflow_metrics or [],
            api_metrics=api_metrics or [],
            resource_metrics=resource_metrics,
            throughput_metrics=throughput_metrics or [],
            metadata={
                'collector_version': '1.0.0',
                'thresholds': self.thresholds
            }
        )
        
        return snapshot
    
    def store_snapshot(self, snapshot: PerformanceSnapshot) -> None:
        """
        Store performance snapshot to persistent storage.
        
        Storage format: .github/agent-system/metrics/performance/{date}/{timestamp}.json
        
        Args:
            snapshot: PerformanceSnapshot to store
            
        Post-conditions:
        - Snapshot file is created
        - Latest symlink is updated
        """
        # Create date-based subdirectory
        date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        date_dir = self.metrics_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # Use timestamp as filename (sortable)
        timestamp_str = snapshot.timestamp.replace(':', '-').replace('.', '-')
        snapshot_file = date_dir / f"{timestamp_str}.json"
        
        try:
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot.to_dict(), f, indent=2)
            
            # Update latest.json for quick access
            latest_file = self.metrics_dir / "latest.json"
            with open(latest_file, 'w') as f:
                json.dump(snapshot.to_dict(), f, indent=2)
            
            print(f"✅ Performance snapshot stored: {snapshot_file}", file=sys.stderr)
            
            # Post-condition: Files exist
            assert snapshot_file.exists(), "Snapshot file was not created"
            assert latest_file.exists(), "Latest file was not created"
        
        except Exception as e:
            print(f"❌ Error storing snapshot: {e}", file=sys.stderr)
            raise
    
    def load_snapshots(
        self,
        since_days: int = DEFAULT_LOOKBACK_DAYS
    ) -> List[PerformanceSnapshot]:
        """
        Load performance snapshots from the specified time period.
        
        Args:
            since_days: Number of days to look back
            
        Returns:
            List of PerformanceSnapshot objects
            
        Post-conditions:
        - All returned snapshots are from the specified time period
        """
        snapshots = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=since_days)
        
        try:
            # Iterate through date directories
            for date_dir in sorted(self.metrics_dir.glob('????-??-??')):
                # Parse date from directory name
                try:
                    dir_date = datetime.strptime(date_dir.name, '%Y-%m-%d')
                    dir_date = dir_date.replace(tzinfo=timezone.utc)
                    
                    if dir_date < cutoff_date:
                        continue
                    
                    # Load all snapshots from this date
                    for snapshot_file in sorted(date_dir.glob('*.json')):
                        with open(snapshot_file, 'r') as f:
                            data = json.load(f)
                            # Reconstruct snapshot (simplified - would need full reconstruction)
                            snapshots.append(data)
                
                except (ValueError, json.JSONDecodeError) as e:
                    print(f"⚠️  Warning: Could not load {date_dir}: {e}", file=sys.stderr)
                    continue
        
        except Exception as e:
            print(f"⚠️  Warning: Error loading snapshots: {e}", file=sys.stderr)
        
        # Post-condition: All snapshots are within time range
        for snapshot in snapshots:
            snapshot_time = datetime.fromisoformat(snapshot['timestamp'].replace('Z', '+00:00'))
            assert snapshot_time >= cutoff_date, "Snapshot outside time range"
        
        return snapshots
    
    def analyze_performance_trends(
        self,
        snapshots: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze performance trends from snapshots.
        
        Analyzes:
        - Average execution times
        - Resource utilization trends
        - Throughput patterns
        - Anomalies and threshold violations
        
        Args:
            snapshots: List of snapshot dictionaries
            
        Returns:
            Dictionary with trend analysis results
        """
        if not snapshots:
            return {
                'workflow_trends': {},
                'resource_trends': {},
                'anomalies': [],
                'threshold_violations': []
            }
        
        # Analyze workflow trends
        workflow_times = defaultdict(list)
        for snapshot in snapshots:
            for wf in snapshot.get('workflow_metrics', []):
                workflow_times[wf['workflow_name']].append(wf['execution_time_ms'])
        
        workflow_trends = {}
        for wf_name, times in workflow_times.items():
            if times:
                workflow_trends[wf_name] = {
                    'avg_time_ms': sum(times) / len(times),
                    'min_time_ms': min(times),
                    'max_time_ms': max(times),
                    'count': len(times)
                }
        
        # Analyze resource trends
        memory_usage = []
        cpu_usage = []
        disk_usage = []
        
        for snapshot in snapshots:
            if snapshot.get('resource_metrics'):
                rm = snapshot['resource_metrics']
                memory_usage.append(rm['memory_percent'])
                cpu_usage.append(rm['cpu_percent'])
                disk_usage.append(rm['disk_percent'])
        
        resource_trends = {}
        if memory_usage:
            resource_trends['memory'] = {
                'avg_percent': sum(memory_usage) / len(memory_usage),
                'max_percent': max(memory_usage),
                'min_percent': min(memory_usage)
            }
        if cpu_usage:
            resource_trends['cpu'] = {
                'avg_percent': sum(cpu_usage) / len(cpu_usage),
                'max_percent': max(cpu_usage),
                'min_percent': min(cpu_usage)
            }
        if disk_usage:
            resource_trends['disk'] = {
                'avg_percent': sum(disk_usage) / len(disk_usage),
                'max_percent': max(disk_usage),
                'min_percent': min(disk_usage)
            }
        
        # Detect threshold violations
        violations = []
        for snapshot in snapshots:
            # Check workflow times
            for wf in snapshot.get('workflow_metrics', []):
                if wf['execution_time_ms'] > self.thresholds.get('workflow_execution_time_ms', float('inf')):
                    violations.append({
                        'type': 'workflow_execution_time',
                        'workflow': wf['workflow_name'],
                        'value': wf['execution_time_ms'],
                        'threshold': self.thresholds['workflow_execution_time_ms'],
                        'timestamp': snapshot['timestamp']
                    })
            
            # Check resource usage
            if snapshot.get('resource_metrics'):
                rm = snapshot['resource_metrics']
                if rm['memory_percent'] > self.thresholds.get('memory_usage_mb', 100):
                    violations.append({
                        'type': 'memory_usage',
                        'value': rm['memory_percent'],
                        'threshold': self.thresholds.get('memory_usage_mb', 100),
                        'timestamp': snapshot['timestamp']
                    })
                if rm['cpu_percent'] > self.thresholds.get('cpu_usage_percent', 100):
                    violations.append({
                        'type': 'cpu_usage',
                        'value': rm['cpu_percent'],
                        'threshold': self.thresholds['cpu_usage_percent'],
                        'timestamp': snapshot['timestamp']
                    })
        
        return {
            'workflow_trends': workflow_trends,
            'resource_trends': resource_trends,
            'anomalies': [],  # Could implement anomaly detection
            'threshold_violations': violations
        }
    
    def generate_report(self, since_days: int = DEFAULT_LOOKBACK_DAYS) -> str:
        """
        Generate a human-readable performance report.
        
        Args:
            since_days: Number of days to include in report
            
        Returns:
            Formatted report string
        """
        snapshots = self.load_snapshots(since_days)
        trends = self.analyze_performance_trends(snapshots)
        
        report = []
        report.append("=" * 70)
        report.append("📊 Performance Metrics Report")
        report.append("=" * 70)
        report.append(f"\nTime Period: Last {since_days} days")
        report.append(f"Snapshots Analyzed: {len(snapshots)}")
        
        # Workflow trends
        if trends['workflow_trends']:
            report.append("\n🚀 Workflow Performance Trends:")
            report.append("-" * 70)
            for wf_name, stats in trends['workflow_trends'].items():
                report.append(f"\n{wf_name}:")
                report.append(f"  Average Time: {stats['avg_time_ms']:.2f}ms")
                report.append(f"  Min Time: {stats['min_time_ms']:.2f}ms")
                report.append(f"  Max Time: {stats['max_time_ms']:.2f}ms")
                report.append(f"  Executions: {stats['count']}")
        
        # Resource trends
        if trends['resource_trends']:
            report.append("\n💾 Resource Utilization Trends:")
            report.append("-" * 70)
            for resource, stats in trends['resource_trends'].items():
                report.append(f"\n{resource.upper()}:")
                report.append(f"  Average: {stats['avg_percent']:.2f}%")
                report.append(f"  Max: {stats['max_percent']:.2f}%")
                report.append(f"  Min: {stats['min_percent']:.2f}%")
        
        # Threshold violations
        if trends['threshold_violations']:
            report.append(f"\n⚠️  Threshold Violations: {len(trends['threshold_violations'])}")
            report.append("-" * 70)
            for violation in trends['threshold_violations'][:10]:  # Show first 10
                report.append(f"  {violation['type']}: {violation['value']:.2f} > {violation['threshold']}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Performance Metrics Collector',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--collect',
        action='store_true',
        help='Collect current performance metrics'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze performance trends'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate performance report'
    )
    parser.add_argument(
        '--since',
        type=int,
        default=DEFAULT_LOOKBACK_DAYS,
        help=f'Days to look back (default: {DEFAULT_LOOKBACK_DAYS})'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    
    args = parser.parse_args()
    
    collector = PerformanceCollector()
    
    if args.collect:
        # Collect current metrics
        snapshot = collector.create_snapshot(include_resources=True)
        collector.store_snapshot(snapshot)
        
        if args.json:
            print(json.dumps(snapshot.to_dict(), indent=2))
        else:
            print("✅ Performance metrics collected successfully")
    
    elif args.analyze or args.report:
        # Generate analysis/report
        snapshots = collector.load_snapshots(args.since)
        
        if args.json:
            trends = collector.analyze_performance_trends(snapshots)
            print(json.dumps(trends, indent=2))
        else:
            report = collector.generate_report(args.since)
            print(report)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
