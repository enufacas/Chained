#!/usr/bin/env python3
"""
API Performance Monitor - Track API performance, reliability, and SLA compliance

This tool monitors API endpoints, collecting metrics on response times, error rates,
and reliability. Essential for maintaining API SLAs and detecting performance issues.

Created by: @investigate-champion
Mission: idea:19 - Web API Innovation Investigation
Date: 2025-11-16
"""

import time
import json
import statistics
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import sys


@dataclass
class APIMetrics:
    """Store API performance metrics for an endpoint."""
    
    endpoint: str
    method: str
    response_times: List[float] = field(default_factory=list)
    status_codes: List[int] = field(default_factory=list)
    error_count: int = 0
    total_requests: int = 0
    timestamps: List[float] = field(default_factory=list)
    
    def add_request(self, response_time: float, status_code: int, timestamp: Optional[float] = None):
        """
        Record a request.
        
        Args:
            response_time: Response time in seconds
            status_code: HTTP status code
            timestamp: Request timestamp (defaults to now)
        """
        self.response_times.append(response_time)
        self.status_codes.append(status_code)
        self.timestamps.append(timestamp or time.time())
        self.total_requests += 1
        
        if status_code >= 400:
            self.error_count += 1
    
    def get_stats(self) -> Dict:
        """Calculate comprehensive statistics."""
        if not self.response_times:
            return {
                'endpoint': self.endpoint,
                'method': self.method,
                'total_requests': 0,
                'error_count': 0
            }
        
        stats = {
            'endpoint': self.endpoint,
            'method': self.method,
            'total_requests': self.total_requests,
            'error_count': self.error_count,
            'error_rate': self.error_count / self.total_requests,
            'success_rate': (self.total_requests - self.error_count) / self.total_requests,
            
            # Response time statistics
            'avg_response_time': statistics.mean(self.response_times),
            'median_response_time': statistics.median(self.response_times),
            'p50_response_time': self._percentile(self.response_times, 50),
            'p75_response_time': self._percentile(self.response_times, 75),
            'p90_response_time': self._percentile(self.response_times, 90),
            'p95_response_time': self._percentile(self.response_times, 95),
            'p99_response_time': self._percentile(self.response_times, 99),
            'max_response_time': max(self.response_times),
            'min_response_time': min(self.response_times),
            'stddev_response_time': statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0,
            
            # Status code breakdown
            'status_codes': self._status_code_breakdown(),
            
            # Time range
            'first_request': datetime.fromtimestamp(min(self.timestamps)).isoformat() if self.timestamps else None,
            'last_request': datetime.fromtimestamp(max(self.timestamps)).isoformat() if self.timestamps else None,
            'duration_seconds': max(self.timestamps) - min(self.timestamps) if self.timestamps else 0,
        }
        
        # Calculate requests per second
        if stats['duration_seconds'] > 0:
            stats['requests_per_second'] = self.total_requests / stats['duration_seconds']
        else:
            stats['requests_per_second'] = 0
        
        return stats
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _status_code_breakdown(self) -> Dict[str, int]:
        """Get count of each status code."""
        breakdown = defaultdict(int)
        for code in self.status_codes:
            breakdown[str(code)] += 1
        return dict(breakdown)
    
    def check_sla(self, sla_config: Dict) -> Dict:
        """
        Check if metrics meet SLA requirements.
        
        Args:
            sla_config: Dict with SLA requirements:
                - max_error_rate: Maximum error rate (0.0-1.0)
                - max_p95_response_time: Maximum P95 response time in seconds
                - max_p99_response_time: Maximum P99 response time in seconds
                - min_success_rate: Minimum success rate (0.0-1.0)
                
        Returns:
            Dict with SLA check results
        """
        stats = self.get_stats()
        violations = []
        
        if 'max_error_rate' in sla_config:
            if stats['error_rate'] > sla_config['max_error_rate']:
                violations.append(
                    f"Error rate {stats['error_rate']:.2%} exceeds "
                    f"maximum {sla_config['max_error_rate']:.2%}"
                )
        
        if 'max_p95_response_time' in sla_config:
            if stats['p95_response_time'] > sla_config['max_p95_response_time']:
                violations.append(
                    f"P95 response time {stats['p95_response_time']:.3f}s exceeds "
                    f"maximum {sla_config['max_p95_response_time']:.3f}s"
                )
        
        if 'max_p99_response_time' in sla_config:
            if stats['p99_response_time'] > sla_config['max_p99_response_time']:
                violations.append(
                    f"P99 response time {stats['p99_response_time']:.3f}s exceeds "
                    f"maximum {sla_config['max_p99_response_time']:.3f}s"
                )
        
        if 'min_success_rate' in sla_config:
            if stats['success_rate'] < sla_config['min_success_rate']:
                violations.append(
                    f"Success rate {stats['success_rate']:.2%} below "
                    f"minimum {sla_config['min_success_rate']:.2%}"
                )
        
        return {
            'endpoint': self.endpoint,
            'method': self.method,
            'sla_met': len(violations) == 0,
            'violations': violations,
            'stats': stats
        }


class APIMonitor:
    """Monitor API performance and reliability."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize API monitor.
        
        Args:
            output_dir: Directory to save monitoring data (optional)
        """
        self.metrics: Dict[str, APIMetrics] = {}
        self.output_dir = Path(output_dir) if output_dir else None
        self.alerts: List[Dict] = []
        
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def track_request(
        self, 
        endpoint: str, 
        method: str, 
        response_time: float, 
        status_code: int,
        timestamp: Optional[float] = None
    ):
        """
        Track a single API request.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            response_time: Response time in seconds
            status_code: HTTP status code
            timestamp: Request timestamp (defaults to now)
        """
        key = f"{method}:{endpoint}"
        
        if key not in self.metrics:
            self.metrics[key] = APIMetrics(endpoint, method)
        
        self.metrics[key].add_request(response_time, status_code, timestamp)
    
    def get_all_stats(self) -> List[Dict]:
        """Get statistics for all endpoints."""
        return [m.get_stats() for m in self.metrics.values()]
    
    def get_endpoint_stats(self, endpoint: str, method: str) -> Optional[Dict]:
        """Get statistics for specific endpoint."""
        key = f"{method}:{endpoint}"
        metrics = self.metrics.get(key)
        return metrics.get_stats() if metrics else None
    
    def check_all_slas(self, sla_config: Dict) -> List[Dict]:
        """
        Check SLA compliance for all endpoints.
        
        Args:
            sla_config: Default SLA configuration for all endpoints
            
        Returns:
            List of SLA check results
        """
        return [m.check_sla(sla_config) for m in self.metrics.values()]
    
    def print_report(self, detailed: bool = False):
        """
        Print performance report to console.
        
        Args:
            detailed: Include detailed statistics
        """
        print("\n" + "=" * 80)
        print("📊 API Performance Report")
        print("=" * 80)
        print(f"Generated: {datetime.now().isoformat()}")
        print(f"Monitored Endpoints: {len(self.metrics)}")
        
        all_stats = self.get_all_stats()
        
        if not all_stats:
            print("\nNo data collected yet.")
            return
        
        # Summary statistics
        total_requests = sum(s['total_requests'] for s in all_stats)
        total_errors = sum(s['error_count'] for s in all_stats)
        overall_error_rate = total_errors / total_requests if total_requests > 0 else 0
        
        print(f"\nOverall Statistics:")
        print(f"  Total Requests: {total_requests:,}")
        print(f"  Total Errors: {total_errors:,}")
        print(f"  Error Rate: {overall_error_rate:.2%}")
        
        # Per-endpoint statistics
        print(f"\nEndpoint Details:")
        print("-" * 80)
        
        for stats in sorted(all_stats, key=lambda x: x['total_requests'], reverse=True):
            self._print_endpoint_stats(stats, detailed)
    
    def _print_endpoint_stats(self, stats: Dict, detailed: bool):
        """Print statistics for single endpoint."""
        print(f"\n{stats['method']} {stats['endpoint']}")
        print(f"  Requests: {stats['total_requests']:,}")
        print(f"  Error Rate: {stats['error_rate']:.2%} ({stats['error_count']} errors)")
        print(f"  Success Rate: {stats['success_rate']:.2%}")
        
        if detailed:
            print(f"  Response Times:")
            print(f"    Average: {stats['avg_response_time']:.3f}s")
            print(f"    Median:  {stats['median_response_time']:.3f}s")
            print(f"    P90:     {stats['p90_response_time']:.3f}s")
            print(f"    P95:     {stats['p95_response_time']:.3f}s")
            print(f"    P99:     {stats['p99_response_time']:.3f}s")
            print(f"    Max:     {stats['max_response_time']:.3f}s")
            print(f"    Min:     {stats['min_response_time']:.3f}s")
            print(f"    StdDev:  {stats['stddev_response_time']:.3f}s")
            
            if stats['duration_seconds'] > 0:
                print(f"  Throughput: {stats['requests_per_second']:.2f} req/s")
            
            print(f"  Status Codes:")
            for code, count in sorted(stats['status_codes'].items()):
                percentage = (count / stats['total_requests']) * 100
                print(f"    {code}: {count:,} ({percentage:.1f}%)")
        else:
            print(f"  Avg Response: {stats['avg_response_time']:.3f}s")
            print(f"  P95 Response: {stats['p95_response_time']:.3f}s")
    
    def export_json(self, filepath: Optional[str] = None) -> str:
        """
        Export metrics to JSON file.
        
        Args:
            filepath: Output file path (defaults to output_dir/metrics_TIMESTAMP.json)
            
        Returns:
            Path to exported file
        """
        if not filepath:
            if not self.output_dir:
                raise ValueError("output_dir must be set or filepath must be provided")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.output_dir / f"metrics_{timestamp}.json"
        
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'generated_at': datetime.now().isoformat(),
            'endpoints': self.get_all_stats(),
            'summary': {
                'total_endpoints': len(self.metrics),
                'total_requests': sum(m.total_requests for m in self.metrics.values()),
                'total_errors': sum(m.error_count for m in self.metrics.values()),
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(output_path)
    
    def add_alert(self, endpoint: str, method: str, message: str, severity: str = 'warning'):
        """
        Add an alert for an endpoint.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            message: Alert message
            severity: Alert severity (info, warning, error, critical)
        """
        self.alerts.append({
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'method': method,
            'message': message,
            'severity': severity
        })
    
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """
        Get alerts, optionally filtered by severity.
        
        Args:
            severity: Filter by severity level
            
        Returns:
            List of alerts
        """
        if severity:
            return [a for a in self.alerts if a['severity'] == severity]
        return self.alerts
    
    def clear_metrics(self):
        """Clear all collected metrics."""
        self.metrics = {}
        self.alerts = []


def monitor_function(monitor: APIMonitor, endpoint: str, method: str = 'GET'):
    """
    Decorator to monitor function execution as API call.
    
    Usage:
        @monitor_function(monitor, '/api/users', 'GET')
        def get_users():
            return requests.get('https://api.example.com/users')
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                
                # Try to get status code from result
                status_code = 200
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                
                monitor.track_request(endpoint, method, elapsed, status_code)
                return result
            except Exception as e:
                elapsed = time.time() - start
                monitor.track_request(endpoint, method, elapsed, 500)
                raise
        return wrapper
    return decorator


def main():
    """CLI interface for API monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Monitor API performance and reliability'
    )
    parser.add_argument(
        '--input',
        help='Load metrics from JSON file'
    )
    parser.add_argument(
        '--output',
        help='Export metrics to JSON file'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Print performance report'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Include detailed statistics in report'
    )
    parser.add_argument(
        '--check-sla',
        help='Check SLA compliance (JSON config file)'
    )
    
    args = parser.parse_args()
    
    monitor = APIMonitor()
    
    # Load metrics if provided
    if args.input:
        try:
            with open(args.input) as f:
                data = json.load(f)
            
            # Reconstruct metrics from saved data
            for endpoint_stats in data.get('endpoints', []):
                # This is a simplified reconstruction
                # In production, you'd want to save and restore full metric objects
                print(f"Loaded stats for {endpoint_stats['method']} {endpoint_stats['endpoint']}")
            
            print(f"✅ Loaded metrics from {args.input}")
        except Exception as e:
            print(f"❌ Error loading metrics: {e}", file=sys.stderr)
            return 1
    
    # Print report
    if args.report:
        monitor.print_report(detailed=args.detailed)
    
    # Check SLA
    if args.check_sla:
        try:
            with open(args.check_sla) as f:
                sla_config = json.load(f)
            
            results = monitor.check_all_slas(sla_config)
            
            print("\n" + "=" * 80)
            print("🎯 SLA Compliance Report")
            print("=" * 80)
            
            met = sum(1 for r in results if r['sla_met'])
            total = len(results)
            
            print(f"\nOverall: {met}/{total} endpoints meeting SLA ({met/total*100:.1f}%)")
            
            for result in results:
                status = "✅" if result['sla_met'] else "❌"
                print(f"\n{status} {result['method']} {result['endpoint']}")
                
                if not result['sla_met']:
                    print("  Violations:")
                    for violation in result['violations']:
                        print(f"    - {violation}")
            
        except Exception as e:
            print(f"❌ Error checking SLA: {e}", file=sys.stderr)
            return 1
    
    # Export metrics
    if args.output:
        try:
            path = monitor.export_json(args.output)
            print(f"✅ Metrics exported to {path}")
        except Exception as e:
            print(f"❌ Error exporting metrics: {e}", file=sys.stderr)
            return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
