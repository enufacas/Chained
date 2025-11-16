#!/usr/bin/env python3
"""
API Monitoring Bridge for Chained
Created by @bridge-master for Mission idea:30

Real-time monitoring of API performance with SLA tracking and reporting.
Like monitoring traffic on a bridge - we need to know when things slow down or break.

Usage:
    from api_monitoring_bridge import APIMonitoringBridge
    
    monitor = APIMonitoringBridge()
    monitor.record_request('/api/users', 'GET', 245.5, 200)
    
    # Check SLA compliance
    sla_status = monitor.check_sla('/api/users', 'GET')
    
    # Generate report
    print(monitor.generate_report())
"""

import time
import statistics
import json
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
import math


@dataclass
class RequestMetric:
    """Represents a single API request metric"""
    timestamp: float
    duration_ms: float
    status_code: int
    success: bool
    error: Optional[str] = None


@dataclass
class EndpointStats:
    """Statistics for an API endpoint"""
    endpoint: str
    method: str
    total_requests: int
    success_count: int
    error_count: int
    success_rate: float
    error_rate: float
    avg_duration_ms: float
    median_duration_ms: float
    p50_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float
    requests_per_second: float


@dataclass
class SLAResult:
    """SLA compliance check result"""
    sla_met: bool
    violations: List[str]
    stats: EndpointStats
    timestamp: str


class APIMonitoringBridge:
    """
    Monitor API performance and SLA compliance
    
    Built by @bridge-master to ensure our API bridges stay healthy and fast.
    Tracks response times, error rates, and SLA compliance in real-time.
    """
    
    def __init__(self):
        """Initialize the monitoring bridge"""
        self.metrics: Dict[str, List[RequestMetric]] = defaultdict(list)
        self.errors: Dict[str, List[Dict]] = defaultdict(list)
        self.start_time = time.time()
        self.endpoint_count: Dict[str, int] = defaultdict(int)
    
    def record_request(
        self,
        endpoint: str,
        method: str,
        duration_ms: float,
        status_code: int,
        error: Optional[str] = None
    ):
        """
        Record an API request for monitoring
        
        Args:
            endpoint: API endpoint (e.g., '/api/users' or full URL)
            method: HTTP method (GET, POST, etc.)
            duration_ms: Request duration in milliseconds
            status_code: HTTP status code
            error: Optional error message
        
        Example:
            monitor.record_request('/api/users', 'GET', 245.5, 200)
            monitor.record_request('/api/login', 'POST', 1250.0, 500, 'timeout')
        """
        key = self._make_key(endpoint, method)
        
        metric = RequestMetric(
            timestamp=time.time(),
            duration_ms=duration_ms,
            status_code=status_code,
            success=200 <= status_code < 400,
            error=error
        )
        
        self.metrics[key].append(metric)
        self.endpoint_count[key] += 1
        
        # Record errors separately for easy access
        if error or status_code >= 400:
            self.errors[key].append({
                'timestamp': metric.timestamp,
                'status_code': status_code,
                'error': error,
                'duration_ms': duration_ms
            })
    
    def get_endpoint_stats(self, endpoint: str, method: str) -> Optional[EndpointStats]:
        """
        Get comprehensive statistics for an endpoint
        
        Args:
            endpoint: API endpoint
            method: HTTP method
        
        Returns:
            EndpointStats object with all metrics, or None if no data
        """
        key = self._make_key(endpoint, method)
        metrics = self.metrics.get(key, [])
        
        if not metrics:
            return None
        
        durations = [m.duration_ms for m in metrics]
        successes = [m for m in metrics if m.success]
        
        # Calculate percentiles
        sorted_durations = sorted(durations)
        
        # Calculate requests per second
        elapsed_time = time.time() - self.start_time
        rps = len(metrics) / elapsed_time if elapsed_time > 0 else 0
        
        return EndpointStats(
            endpoint=endpoint,
            method=method,
            total_requests=len(metrics),
            success_count=len(successes),
            error_count=len(metrics) - len(successes),
            success_rate=len(successes) / len(metrics) if metrics else 0,
            error_rate=1 - (len(successes) / len(metrics)) if metrics else 0,
            avg_duration_ms=statistics.mean(durations),
            median_duration_ms=statistics.median(durations),
            p50_duration_ms=self._percentile(sorted_durations, 50),
            p95_duration_ms=self._percentile(sorted_durations, 95),
            p99_duration_ms=self._percentile(sorted_durations, 99),
            min_duration_ms=min(durations),
            max_duration_ms=max(durations),
            requests_per_second=rps
        )
    
    def check_sla(
        self,
        endpoint: str,
        method: str,
        max_error_rate: float = 0.01,  # 1%
        max_p95_ms: float = 500,  # 500ms
        max_p99_ms: float = 1000,  # 1000ms
        min_success_rate: float = 0.99,  # 99%
        min_rps: Optional[float] = None
    ) -> SLAResult:
        """
        Check if endpoint meets SLA requirements
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            max_error_rate: Maximum acceptable error rate (default 1%)
            max_p95_ms: Maximum acceptable P95 latency (default 500ms)
            max_p99_ms: Maximum acceptable P99 latency (default 1000ms)
            min_success_rate: Minimum acceptable success rate (default 99%)
            min_rps: Optional minimum requests per second
        
        Returns:
            SLAResult with compliance status and violations
        
        Example:
            sla = monitor.check_sla('/api/users', 'GET')
            if not sla.sla_met:
                print(f"SLA violations: {sla.violations}")
        """
        stats = self.get_endpoint_stats(endpoint, method)
        
        if not stats:
            return SLAResult(
                sla_met=False,
                violations=['No data available for endpoint'],
                stats=None,
                timestamp=datetime.now().isoformat()
            )
        
        violations = []
        
        # Check error rate
        if stats.error_rate > max_error_rate:
            violations.append(
                f"Error rate {stats.error_rate:.2%} exceeds {max_error_rate:.2%}"
            )
        
        # Check P95 latency
        if stats.p95_duration_ms > max_p95_ms:
            violations.append(
                f"P95 latency {stats.p95_duration_ms:.0f}ms exceeds {max_p95_ms:.0f}ms"
            )
        
        # Check P99 latency
        if stats.p99_duration_ms > max_p99_ms:
            violations.append(
                f"P99 latency {stats.p99_duration_ms:.0f}ms exceeds {max_p99_ms:.0f}ms"
            )
        
        # Check success rate
        if stats.success_rate < min_success_rate:
            violations.append(
                f"Success rate {stats.success_rate:.2%} below {min_success_rate:.2%}"
            )
        
        # Check minimum RPS if specified
        if min_rps is not None and stats.requests_per_second < min_rps:
            violations.append(
                f"RPS {stats.requests_per_second:.2f} below minimum {min_rps:.2f}"
            )
        
        return SLAResult(
            sla_met=len(violations) == 0,
            violations=violations,
            stats=stats,
            timestamp=datetime.now().isoformat()
        )
    
    def get_recent_errors(
        self,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent errors, optionally filtered by endpoint/method
        
        Args:
            endpoint: Optional endpoint filter
            method: Optional method filter
            limit: Maximum number of errors to return
        
        Returns:
            List of recent error dictionaries
        """
        if endpoint and method:
            key = self._make_key(endpoint, method)
            errors = self.errors.get(key, [])
        else:
            # Get all errors
            errors = []
            for error_list in self.errors.values():
                errors.extend(error_list)
        
        # Sort by timestamp (most recent first)
        errors.sort(key=lambda e: e['timestamp'], reverse=True)
        
        return errors[:limit]
    
    def get_slowest_requests(
        self,
        limit: int = 10,
        endpoint: Optional[str] = None,
        method: Optional[str] = None
    ) -> List[Dict]:
        """
        Get slowest requests
        
        Args:
            limit: Maximum number of requests to return
            endpoint: Optional endpoint filter
            method: Optional method filter
        
        Returns:
            List of slowest request metrics
        """
        if endpoint and method:
            key = self._make_key(endpoint, method)
            metrics = self.metrics.get(key, [])
        else:
            # Get all metrics
            metrics = []
            for metric_list in self.metrics.values():
                metrics.extend(metric_list)
        
        # Sort by duration (slowest first)
        metrics.sort(key=lambda m: m.duration_ms, reverse=True)
        
        # Convert to dicts for easier consumption
        return [asdict(m) for m in metrics[:limit]]
    
    def generate_report(
        self,
        format: str = 'markdown',
        include_sla: bool = True
    ) -> str:
        """
        Generate a comprehensive monitoring report
        
        Args:
            format: Report format ('markdown', 'json', 'text')
            include_sla: Include SLA compliance checks
        
        Returns:
            Formatted report string
        """
        if format == 'json':
            return self._generate_json_report(include_sla)
        elif format == 'text':
            return self._generate_text_report(include_sla)
        else:  # markdown
            return self._generate_markdown_report(include_sla)
    
    def _generate_markdown_report(self, include_sla: bool) -> str:
        """Generate Markdown formatted report"""
        report = []
        report.append("# 🌉 API Performance Report")
        report.append(f"*Generated by @bridge-master's Monitoring Bridge*\n")
        
        # Overall stats
        elapsed = time.time() - self.start_time
        total_requests = sum(len(metrics) for metrics in self.metrics.values())
        
        report.append(f"**Monitoring Duration:** {elapsed:.2f}s")
        report.append(f"**Total Requests:** {total_requests:,}")
        report.append(f"**Endpoints Monitored:** {len(self.metrics)}")
        report.append("")
        
        # Per-endpoint stats
        report.append("## 📊 Endpoint Statistics\n")
        
        for key in sorted(self.metrics.keys()):
            endpoint, method = self._split_key(key)
            stats = self.get_endpoint_stats(endpoint, method)
            
            if not stats:
                continue
            
            # Endpoint header
            report.append(f"### {method} `{endpoint}`")
            report.append("")
            
            # Metrics table
            report.append("| Metric | Value |")
            report.append("|--------|-------|")
            report.append(f"| Total Requests | {stats.total_requests:,} |")
            report.append(f"| Success Rate | {stats.success_rate:.2%} |")
            report.append(f"| Error Rate | {stats.error_rate:.2%} |")
            report.append(f"| Requests/sec | {stats.requests_per_second:.2f} |")
            report.append(f"| Avg Response | {stats.avg_duration_ms:.0f}ms |")
            report.append(f"| P50 Response | {stats.p50_duration_ms:.0f}ms |")
            report.append(f"| P95 Response | {stats.p95_duration_ms:.0f}ms |")
            report.append(f"| P99 Response | {stats.p99_duration_ms:.0f}ms |")
            report.append(f"| Min Response | {stats.min_duration_ms:.0f}ms |")
            report.append(f"| Max Response | {stats.max_duration_ms:.0f}ms |")
            report.append("")
            
            # SLA compliance
            if include_sla:
                sla = self.check_sla(endpoint, method)
                status_icon = '✅' if sla.sla_met else '❌'
                report.append(f"**SLA Status:** {status_icon} {'Met' if sla.sla_met else 'Violated'}")
                
                if not sla.sla_met:
                    report.append("\n**Violations:**")
                    for violation in sla.violations:
                        report.append(f"- ⚠️ {violation}")
                
                report.append("")
            
            # Recent errors
            errors = self.get_recent_errors(endpoint, method, limit=3)
            if errors:
                report.append("**Recent Errors:**")
                for error in errors:
                    ts = datetime.fromtimestamp(error['timestamp']).strftime('%H:%M:%S')
                    report.append(
                        f"- {ts} - Status {error['status_code']}: "
                        f"{error.get('error', 'Unknown error')}"
                    )
                report.append("")
        
        # Slowest requests
        report.append("\n## 🐌 Slowest Requests (Top 5)")
        report.append("")
        slowest = self.get_slowest_requests(limit=5)
        
        if slowest:
            report.append("| Timestamp | Duration | Status | Error |")
            report.append("|-----------|----------|--------|-------|")
            for req in slowest:
                ts = datetime.fromtimestamp(req['timestamp']).strftime('%H:%M:%S')
                report.append(
                    f"| {ts} | {req['duration_ms']:.0f}ms | "
                    f"{req['status_code']} | {req.get('error', '-')} |"
                )
            report.append("")
        else:
            report.append("*No requests recorded*\n")
        
        # Summary
        report.append("\n## 📈 Summary")
        report.append("")
        
        # Overall success rate
        all_metrics = []
        for metrics in self.metrics.values():
            all_metrics.extend(metrics)
        
        if all_metrics:
            total_success = sum(1 for m in all_metrics if m.success)
            overall_success_rate = total_success / len(all_metrics)
            
            report.append(f"- **Overall Success Rate:** {overall_success_rate:.2%}")
            report.append(f"- **Total Errors:** {len(all_metrics) - total_success}")
            
            all_durations = [m.duration_ms for m in all_metrics]
            report.append(f"- **Average Response Time:** {statistics.mean(all_durations):.0f}ms")
            report.append(f"- **Median Response Time:** {statistics.median(all_durations):.0f}ms")
        
        report.append("")
        report.append("---")
        report.append("*🌉 Built by @bridge-master - Keeping API bridges healthy and fast*")
        
        return "\n".join(report)
    
    def _generate_json_report(self, include_sla: bool) -> str:
        """Generate JSON formatted report"""
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'monitoring_duration_s': time.time() - self.start_time,
                'total_requests': sum(len(m) for m in self.metrics.values()),
                'endpoints_monitored': len(self.metrics)
            },
            'endpoints': []
        }
        
        for key in self.metrics.keys():
            endpoint, method = self._split_key(key)
            stats = self.get_endpoint_stats(endpoint, method)
            
            if not stats:
                continue
            
            endpoint_data = asdict(stats)
            
            if include_sla:
                sla = self.check_sla(endpoint, method)
                endpoint_data['sla'] = {
                    'met': sla.sla_met,
                    'violations': sla.violations
                }
            
            report['endpoints'].append(endpoint_data)
        
        return json.dumps(report, indent=2)
    
    def _generate_text_report(self, include_sla: bool) -> str:
        """Generate plain text report"""
        report = []
        report.append("="*60)
        report.append("API PERFORMANCE REPORT")
        report.append("Generated by @bridge-master's Monitoring Bridge")
        report.append("="*60)
        report.append("")
        
        elapsed = time.time() - self.start_time
        total_requests = sum(len(metrics) for metrics in self.metrics.values())
        
        report.append(f"Monitoring Duration: {elapsed:.2f}s")
        report.append(f"Total Requests: {total_requests}")
        report.append(f"Endpoints Monitored: {len(self.metrics)}")
        report.append("")
        
        for key in sorted(self.metrics.keys()):
            endpoint, method = self._split_key(key)
            stats = self.get_endpoint_stats(endpoint, method)
            
            if not stats:
                continue
            
            report.append(f"\n{method} {endpoint}")
            report.append("-" * 60)
            report.append(f"Total Requests:  {stats.total_requests}")
            report.append(f"Success Rate:    {stats.success_rate:.2%}")
            report.append(f"Error Rate:      {stats.error_rate:.2%}")
            report.append(f"Avg Response:    {stats.avg_duration_ms:.0f}ms")
            report.append(f"P95 Response:    {stats.p95_duration_ms:.0f}ms")
            report.append(f"P99 Response:    {stats.p99_duration_ms:.0f}ms")
            
            if include_sla:
                sla = self.check_sla(endpoint, method)
                status = "PASS" if sla.sla_met else "FAIL"
                report.append(f"SLA Status:      {status}")
                
                if not sla.sla_met:
                    for violation in sla.violations:
                        report.append(f"  ! {violation}")
        
        report.append("")
        report.append("="*60)
        return "\n".join(report)
    
    def export_metrics(self, filepath: str, format: str = 'json'):
        """
        Export all metrics to a file
        
        Args:
            filepath: Path to save metrics
            format: Export format ('json' or 'csv')
        """
        if format == 'json':
            self._export_json(filepath)
        elif format == 'csv':
            self._export_csv(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self, filepath: str):
        """Export metrics as JSON"""
        data = {
            'start_time': self.start_time,
            'end_time': time.time(),
            'metrics': {}
        }
        
        for key, metrics in self.metrics.items():
            data['metrics'][key] = [asdict(m) for m in metrics]
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _export_csv(self, filepath: str):
        """Export metrics as CSV"""
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'endpoint', 'method', 'timestamp', 'duration_ms',
                'status_code', 'success', 'error'
            ])
            
            for key, metrics in self.metrics.items():
                endpoint, method = self._split_key(key)
                for metric in metrics:
                    writer.writerow([
                        endpoint, method, metric.timestamp, metric.duration_ms,
                        metric.status_code, metric.success, metric.error or ''
                    ])
    
    def _make_key(self, endpoint: str, method: str) -> str:
        """Create a unique key for endpoint+method"""
        return f"{method.upper()}:{endpoint}"
    
    def _split_key(self, key: str) -> tuple:
        """Split key back into endpoint and method"""
        method, endpoint = key.split(':', 1)
        return endpoint, method
    
    def _percentile(self, sorted_data: List[float], percentile: int) -> float:
        """Calculate percentile from sorted data"""
        if not sorted_data:
            return 0.0
        
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        lower = math.floor(index)
        upper = math.ceil(index)
        
        if lower == upper:
            return sorted_data[int(index)]
        
        # Interpolate between values
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
    
    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()
        self.errors.clear()
        self.endpoint_count.clear()
        self.start_time = time.time()


# Example usage
def example_monitoring():
    """
    Example of API monitoring with @bridge-master's Bridge
    """
    print("🌉 Bridge Master API Monitoring Demo\n")
    
    monitor = APIMonitoringBridge()
    
    # Simulate API calls
    print("Recording sample API metrics...\n")
    
    # Successful requests
    for i in range(100):
        monitor.record_request('/api/users', 'GET', 150 + i * 2, 200)
    
    # Some errors
    for i in range(5):
        monitor.record_request('/api/users', 'GET', 5000, 500, 'timeout')
    
    # Different endpoint
    for i in range(50):
        monitor.record_request('/api/auth/login', 'POST', 300 + i, 200)
    
    # Print report
    print(monitor.generate_report())
    
    # Check SLA
    print("\n" + "="*60)
    print("SLA Compliance Check")
    print("="*60 + "\n")
    
    sla = monitor.check_sla('/api/users', 'GET')
    if sla.sla_met:
        print("✅ /api/users GET - SLA compliant!")
    else:
        print("❌ /api/users GET - SLA violations:")
        for violation in sla.violations:
            print(f"  - {violation}")
    
    # Export metrics
    print("\n📁 Exporting metrics to files...")
    monitor.export_metrics('/tmp/api_metrics.json', format='json')
    print("  ✅ Exported to /tmp/api_metrics.json")


if __name__ == '__main__':
    example_monitoring()
