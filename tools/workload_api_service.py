#!/usr/bin/env python3
"""
Workload API Service - RESTful API for Workload Monitoring

Provides HTTP API endpoints for querying workload metrics and recommendations.
Part of the AI spawning specialized sub-agents system.

Created by @APIs-architect - Rigorous and innovative, ensuring reliability first.

Features:
- GET /api/v1/workload/metrics - Get current workload metrics
- GET /api/v1/workload/recommendations - Get spawning recommendations
- GET /api/v1/workload/health - Get workload health status
- GET /api/v1/workload/history - Get historical workload data
- Thread-safe operations
- Caching for performance
- Comprehensive error handling

Usage:
    python3 tools/workload_api_service.py --port 8080
    
    curl http://localhost:8080/api/v1/workload/metrics
"""

import json
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import argparse

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from workload_monitor import WorkloadMonitor, WorkloadMetrics, SpawningRecommendation
except ImportError as e:
    print(f"Error: Required module not found: {e}")
    sys.exit(1)


class WorkloadAPIHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for Workload API.
    
    Designed by @APIs-architect with rigorous error handling
    and clear response formats.
    """
    
    # Shared state (thread-safe via locks)
    _monitor: Optional[WorkloadMonitor] = None
    _cache: Dict[str, Any] = {}
    _cache_lock = threading.Lock()
    _cache_ttl = 60  # seconds
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        params = parse_qs(parsed_path.query)
        
        try:
            if path == '/api/v1/workload/metrics':
                self._handle_metrics(params)
            elif path == '/api/v1/workload/recommendations':
                self._handle_recommendations(params)
            elif path == '/api/v1/workload/health':
                self._handle_health(params)
            elif path == '/api/v1/workload/history':
                self._handle_history(params)
            elif path == '/health' or path == '/':
                self._handle_root()
            else:
                self._send_error(404, "Endpoint not found")
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def _handle_metrics(self, params: Dict):
        """
        GET /api/v1/workload/metrics
        
        Returns current workload metrics across all specializations.
        
        Query params:
            specialization: Filter by specific specialization (optional)
            format: 'json' or 'summary' (default: json)
        """
        specialization = params.get('specialization', [None])[0]
        format_type = params.get('format', ['json'])[0]
        
        # Get or refresh metrics
        metrics = self._get_cached_metrics()
        
        if specialization:
            # Filter to specific specialization
            filtered = [m for m in metrics if m['specialization'] == specialization]
            if not filtered:
                self._send_error(404, f"No metrics for specialization: {specialization}")
                return
            metrics = filtered
        
        if format_type == 'summary':
            # Return summarized view
            response = {
                'total_specializations': len(metrics),
                'total_open_issues': sum(m['open_issues'] for m in metrics),
                'total_pending_prs': sum(m['pending_prs'] for m in metrics),
                'total_active_agents': sum(m['active_agents'] for m in metrics),
                'avg_capacity': sum(m['agent_capacity'] for m in metrics) / len(metrics) if metrics else 0,
                'bottlenecks': [m['specialization'] for m in metrics 
                              if m['bottleneck_severity'] in ['high', 'critical']],
                'timestamp': datetime.now().isoformat()
            }
        else:
            response = {
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
        
        self._send_json(response)
    
    def _handle_recommendations(self, params: Dict):
        """
        GET /api/v1/workload/recommendations
        
        Returns spawning recommendations based on current workload.
        
        Query params:
            max_spawns: Maximum number of spawning recommendations (default: 10)
            priority_min: Minimum priority level (1-5, default: 1)
        """
        max_spawns = int(params.get('max_spawns', [10])[0])
        priority_min = int(params.get('priority_min', [1])[0])
        
        # Get recommendations
        recommendations = self._get_cached_recommendations(max_spawns)
        
        # Filter by priority
        filtered_recs = [
            r for r in recommendations 
            if r.get('priority', 0) >= priority_min
        ]
        
        response = {
            'should_spawn': len(filtered_recs) > 0,
            'total_recommendations': len(filtered_recs),
            'recommendations': filtered_recs,
            'timestamp': datetime.now().isoformat()
        }
        
        self._send_json(response)
    
    def _handle_health(self, params: Dict):
        """
        GET /api/v1/workload/health
        
        Returns overall workload health status.
        """
        metrics = self._get_cached_metrics()
        
        # Calculate health indicators
        total_issues = sum(m['open_issues'] for m in metrics)
        total_prs = sum(m['pending_prs'] for m in metrics)
        avg_capacity = sum(m['agent_capacity'] for m in metrics) / len(metrics) if metrics else 0
        
        critical_bottlenecks = [
            m for m in metrics 
            if m['bottleneck_severity'] == 'critical'
        ]
        high_bottlenecks = [
            m for m in metrics 
            if m['bottleneck_severity'] == 'high'
        ]
        
        # Determine overall health
        if critical_bottlenecks:
            status = 'critical'
            message = f"{len(critical_bottlenecks)} critical bottlenecks detected"
        elif high_bottlenecks:
            status = 'degraded'
            message = f"{len(high_bottlenecks)} high-severity bottlenecks"
        elif avg_capacity > 0.8:
            status = 'degraded'
            message = "Agent capacity at 80%+"
        else:
            status = 'healthy'
            message = "System operating normally"
        
        response = {
            'status': status,
            'message': message,
            'metrics': {
                'total_open_issues': total_issues,
                'total_pending_prs': total_prs,
                'avg_agent_capacity': round(avg_capacity, 2),
                'critical_bottlenecks': len(critical_bottlenecks),
                'high_bottlenecks': len(high_bottlenecks)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self._send_json(response)
    
    def _handle_history(self, params: Dict):
        """
        GET /api/v1/workload/history
        
        Returns historical workload data (if available).
        
        Note: This is a placeholder for future implementation.
        """
        response = {
            'status': 'not_implemented',
            'message': 'Historical data storage not yet implemented',
            'timestamp': datetime.now().isoformat()
        }
        self._send_json(response, status=501)
    
    def _handle_root(self):
        """Handle root endpoint - API info"""
        response = {
            'service': 'Workload API Service',
            'version': '1.0.0',
            'created_by': '@APIs-architect',
            'endpoints': {
                '/api/v1/workload/metrics': 'Get current workload metrics',
                '/api/v1/workload/recommendations': 'Get spawning recommendations',
                '/api/v1/workload/health': 'Get workload health status',
                '/api/v1/workload/history': 'Get historical workload data (not implemented)',
                '/health': 'Service health check'
            },
            'status': 'operational',
            'timestamp': datetime.now().isoformat()
        }
        self._send_json(response)
    
    def _get_cached_metrics(self) -> List[Dict]:
        """
        Get workload metrics from cache or refresh.
        
        Thread-safe caching with TTL.
        """
        cache_key = 'metrics'
        
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached and time.time() - cached['timestamp'] < self._cache_ttl:
                return cached['data']
        
        # Refresh cache
        monitor = self._get_monitor()
        metrics_dict = monitor.analyze_workload()
        
        # Convert dict to list of dicts
        metrics_dicts = []
        for spec, metric in metrics_dict.items():
            metric_dict = metric.to_dict() if hasattr(metric, 'to_dict') else asdict(metric)
            metric_dict['specialization'] = spec  # Ensure specialization is in the dict
            metrics_dicts.append(metric_dict)
        
        with self._cache_lock:
            self._cache[cache_key] = {
                'data': metrics_dicts,
                'timestamp': time.time()
            }
        
        return metrics_dicts
    
    def _get_cached_recommendations(self, max_spawns: int) -> List[Dict]:
        """
        Get spawning recommendations from cache or refresh.
        
        Thread-safe caching with TTL.
        """
        cache_key = f'recommendations_{max_spawns}'
        
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached and time.time() - cached['timestamp'] < self._cache_ttl:
                return cached['data']
        
        # Refresh cache
        monitor = self._get_monitor()
        metrics_dict = monitor.analyze_workload()
        recommendations = monitor.generate_spawning_recommendations(
            metrics=metrics_dict,
            max_spawns=max_spawns
        )
        
        # Convert to dicts
        rec_dicts = []
        for rec in recommendations:
            rec_dict = {
                'should_spawn': rec.should_spawn,
                'specialization': rec.specialization,
                'count': rec.count,
                'reason': rec.reason,
                'priority': rec.priority,
                'metrics': rec.metrics.to_dict() if hasattr(rec.metrics, 'to_dict') else asdict(rec.metrics)
            }
            rec_dicts.append(rec_dict)
        
        with self._cache_lock:
            self._cache[cache_key] = {
                'data': rec_dicts,
                'timestamp': time.time()
            }
        
        return rec_dicts
    
    def _get_monitor(self) -> WorkloadMonitor:
        """Get or create WorkloadMonitor instance (singleton)"""
        if self._monitor is None:
            self._monitor = WorkloadMonitor()
        return self._monitor
    
    def _send_json(self, data: Dict, status: int = 200):
        """
        Send JSON response.
        
        Args:
            data: Response data
            status: HTTP status code
        """
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # CORS
        self.end_headers()
        
        json_str = json.dumps(data, indent=2)
        self.wfile.write(json_str.encode('utf-8'))
    
    def _send_error(self, status: int, message: str):
        """
        Send error response.
        
        Args:
            status: HTTP status code
            message: Error message
        """
        error_response = {
            'error': True,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self._send_json(error_response, status=status)
    
    def log_message(self, format, *args):
        """Override to provide cleaner logging"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def run_server(port: int = 8080, host: str = '0.0.0.0'):
    """
    Run the Workload API server.
    
    Args:
        port: Port to listen on
        host: Host to bind to
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, WorkloadAPIHandler)
    
    print(f"🚀 Workload API Service starting on {host}:{port}")
    print(f"📊 Created by @APIs-architect - Ensuring reliability first")
    print(f"\nAvailable endpoints:")
    print(f"  GET http://{host}:{port}/api/v1/workload/metrics")
    print(f"  GET http://{host}:{port}/api/v1/workload/recommendations")
    print(f"  GET http://{host}:{port}/api/v1/workload/health")
    print(f"  GET http://{host}:{port}/health")
    print(f"\nPress Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
        httpd.shutdown()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Workload API Service - RESTful API for workload monitoring'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8080,
        help='Port to listen on (default: 8080)'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    
    args = parser.parse_args()
    
    run_server(port=args.port, host=args.host)


if __name__ == '__main__':
    main()
