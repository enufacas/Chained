#!/usr/bin/env python3
"""
Sub-Agent Spawning API Service - RESTful API for Sub-Agent Management

Provides HTTP API endpoints for triggering and querying sub-agent spawning.
Part of the AI spawning specialized sub-agents system.

Created by @APIs-architect - Rigorous and innovative, ensuring reliability first.

Features:
- POST /api/v1/spawning/trigger - Trigger sub-agent spawning
- GET /api/v1/spawning/status - Get spawning status
- GET /api/v1/spawning/agents - List spawned agents
- POST /api/v1/spawning/deactivate/{agent_id} - Deactivate an agent
- Thread-safe operations
- Comprehensive validation
- Detailed response formats

Usage:
    python3 tools/subagent_spawning_api.py --port 8081
    
    curl -X POST http://localhost:8081/api/v1/spawning/trigger \
      -H "Content-Type: application/json" \
      -d '{"max_spawns": 5}'
"""

import json
import sys
import threading
import time
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import argparse

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from workload_monitor import WorkloadMonitor
    from workload_subagent_spawner import WorkloadSubAgentSpawner, SubAgentSpec
except ImportError as e:
    print(f"Error: Required module not found: {e}")
    sys.exit(1)


class SpawningAPIHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for Sub-Agent Spawning API.
    
    Designed by @APIs-architect with rigorous validation
    and comprehensive error handling.
    """
    
    # Shared state (thread-safe via locks)
    _spawner: Optional[WorkloadSubAgentSpawner] = None
    _monitor: Optional[WorkloadMonitor] = None
    _lock = threading.Lock()
    _spawning_history: List[Dict] = []
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        params = parse_qs(parsed_path.query)
        
        try:
            if path == '/api/v1/spawning/status':
                self._handle_get_status(params)
            elif path == '/api/v1/spawning/agents':
                self._handle_get_agents(params)
            elif path == '/health' or path == '/':
                self._handle_root()
            else:
                self._send_error(404, "Endpoint not found")
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            data = json.loads(body.decode('utf-8')) if body else {}
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON in request body")
            return
        
        try:
            if path == '/api/v1/spawning/trigger':
                self._handle_trigger_spawning(data)
            elif path.startswith('/api/v1/spawning/deactivate/'):
                agent_id = path.split('/')[-1]
                self._handle_deactivate_agent(agent_id, data)
            else:
                self._send_error(404, "Endpoint not found")
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def _handle_trigger_spawning(self, data: Dict):
        """
        POST /api/v1/spawning/trigger
        
        Trigger sub-agent spawning based on current workload.
        
        Request body:
            {
                "max_spawns": 5,        // Optional, default: 5
                "dry_run": false,       // Optional, default: false
                "force": false          // Optional, force spawn even if not needed
            }
        
        Response:
            {
                "success": true,
                "spawned_count": 2,
                "agents": [...],
                "message": "Spawned 2 agents",
                "timestamp": "2024-11-21T00:00:00"
            }
        """
        # Validate and extract parameters
        max_spawns = data.get('max_spawns', 5)
        dry_run = data.get('dry_run', False)
        force = data.get('force', False)
        
        # Validate max_spawns
        if not isinstance(max_spawns, int) or max_spawns < 1 or max_spawns > 20:
            self._send_error(400, "max_spawns must be an integer between 1 and 20")
            return
        
        # Run workload analysis
        monitor = self._get_monitor()
        
        # Create temporary analysis file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            analysis_file = f.name
            
            # Get analysis
            metrics_dict = monitor.analyze_workload()
            recommendations = monitor.generate_spawning_recommendations(
                metrics=metrics_dict,
                max_spawns=max_spawns
            )
            
            analysis = {
                'summary': {
                    'spawning_needed': any(r.should_spawn for r in recommendations),
                    'recommended_spawns': len([r for r in recommendations if r.should_spawn]),
                    'timestamp': datetime.now().isoformat()
                },
                'metrics': [
                    {**asdict(m), 'specialization': spec}
                    for spec, m in metrics_dict.items()
                ],
                'recommendations': [
                    {
                        'should_spawn': r.should_spawn,
                        'specialization': r.specialization,
                        'count': r.count,
                        'reason': r.reason,
                        'priority': r.priority,
                        'metrics': asdict(r.metrics)
                    }
                    for r in recommendations
                ]
            }
            
            json.dump(analysis, f, indent=2)
        
        try:
            # Check if spawning is needed (unless forced)
            if not force and not analysis['summary']['spawning_needed']:
                response = {
                    'success': False,
                    'spawned_count': 0,
                    'agents': [],
                    'message': 'No spawning needed based on current workload',
                    'analysis': analysis['summary'],
                    'timestamp': datetime.now().isoformat()
                }
                self._send_json(response)
                return
            
            # Trigger spawning
            spawner = self._get_spawner()
            spawned_agents = spawner.spawn_from_analysis(
                analysis_file,
                max_total_spawns=max_spawns,
                dry_run=dry_run
            )
            
            # Convert agents to dicts
            agent_dicts = [asdict(agent) for agent in spawned_agents]
            
            # Record in history
            spawn_event = {
                'timestamp': datetime.now().isoformat(),
                'spawned_count': len(spawned_agents),
                'agents': agent_dicts,
                'max_spawns': max_spawns,
                'dry_run': dry_run,
                'forced': force
            }
            
            with self._lock:
                self._spawning_history.append(spawn_event)
                # Keep only last 100 events
                if len(self._spawning_history) > 100:
                    self._spawning_history = self._spawning_history[-100:]
            
            response = {
                'success': True,
                'spawned_count': len(spawned_agents),
                'agents': agent_dicts,
                'message': f"Spawned {len(spawned_agents)} agent(s)" if not dry_run else f"Dry run: Would spawn {len(spawned_agents)} agent(s)",
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_json(response, status=201)
            
        finally:
            # Clean up temp file
            try:
                Path(analysis_file).unlink()
            except:
                pass
    
    def _handle_get_status(self, params: Dict):
        """
        GET /api/v1/spawning/status
        
        Get current spawning status and history.
        
        Query params:
            limit: Number of recent events to return (default: 10)
        """
        limit = int(params.get('limit', [10])[0])
        
        with self._lock:
            recent_history = self._spawning_history[-limit:]
        
        # Get current recommendations
        monitor = self._get_monitor()
        metrics_dict = monitor.analyze_workload()
        recommendations = monitor.generate_spawning_recommendations(
            metrics=metrics_dict,
            max_spawns=10
        )
        
        spawning_needed = any(r.should_spawn for r in recommendations)
        
        response = {
            'spawning_needed': spawning_needed,
            'recommended_count': len([r for r in recommendations if r.should_spawn]),
            'recent_spawns': recent_history,
            'timestamp': datetime.now().isoformat()
        }
        
        self._send_json(response)
    
    def _handle_get_agents(self, params: Dict):
        """
        GET /api/v1/spawning/agents
        
        List all spawned agents (sub-agents).
        
        Query params:
            status: Filter by status (active/inactive, default: all)
            specialization: Filter by specialization (optional)
        """
        status_filter = params.get('status', [None])[0]
        spec_filter = params.get('specialization', [None])[0]
        
        spawner = self._get_spawner()
        
        # Get agents from registry
        if not spawner.registry:
            agents = []
        else:
            try:
                if status_filter:
                    agents = spawner.registry.list_agents(status=status_filter)
                else:
                    agents = spawner.registry.list_agents()
            except Exception as e:
                self._send_error(500, f"Failed to list agents: {str(e)}")
                return
        
        # Filter by specialization if requested
        if spec_filter:
            agents = [a for a in agents if a.get('specialization') == spec_filter]
        
        response = {
            'total': len(agents),
            'agents': agents,
            'timestamp': datetime.now().isoformat()
        }
        
        self._send_json(response)
    
    def _handle_deactivate_agent(self, agent_id: str, data: Dict):
        """
        POST /api/v1/spawning/deactivate/{agent_id}
        
        Deactivate a specific sub-agent.
        
        Request body:
            {
                "reason": "Manual deactivation"  // Optional
            }
        """
        reason = data.get('reason', 'Manual deactivation via API')
        
        spawner = self._get_spawner()
        
        if not spawner.registry:
            self._send_error(500, "Agent registry not available")
            return
        
        try:
            # Deactivate agent
            success = spawner.registry.deactivate_agent(agent_id, reason=reason)
            
            if success:
                response = {
                    'success': True,
                    'agent_id': agent_id,
                    'message': f"Agent {agent_id} deactivated",
                    'reason': reason,
                    'timestamp': datetime.now().isoformat()
                }
                self._send_json(response)
            else:
                self._send_error(404, f"Agent {agent_id} not found or already inactive")
                
        except Exception as e:
            self._send_error(500, f"Failed to deactivate agent: {str(e)}")
    
    def _handle_root(self):
        """Handle root endpoint - API info"""
        response = {
            'service': 'Sub-Agent Spawning API Service',
            'version': '1.0.0',
            'created_by': '@APIs-architect',
            'endpoints': {
                'POST /api/v1/spawning/trigger': 'Trigger sub-agent spawning',
                'GET /api/v1/spawning/status': 'Get spawning status and history',
                'GET /api/v1/spawning/agents': 'List spawned agents',
                'POST /api/v1/spawning/deactivate/{agent_id}': 'Deactivate an agent',
                '/health': 'Service health check'
            },
            'status': 'operational',
            'timestamp': datetime.now().isoformat()
        }
        self._send_json(response)
    
    def _get_spawner(self) -> WorkloadSubAgentSpawner:
        """Get or create WorkloadSubAgentSpawner instance (singleton)"""
        if self._spawner is None:
            self._spawner = WorkloadSubAgentSpawner()
        return self._spawner
    
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


def run_server(port: int = 8081, host: str = '0.0.0.0'):
    """
    Run the Sub-Agent Spawning API server.
    
    Args:
        port: Port to listen on
        host: Host to bind to
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, SpawningAPIHandler)
    
    print(f"🚀 Sub-Agent Spawning API Service starting on {host}:{port}")
    print(f"🤖 Created by @APIs-architect - Ensuring reliability first")
    print(f"\nAvailable endpoints:")
    print(f"  POST http://{host}:{port}/api/v1/spawning/trigger")
    print(f"  GET  http://{host}:{port}/api/v1/spawning/status")
    print(f"  GET  http://{host}:{port}/api/v1/spawning/agents")
    print(f"  POST http://{host}:{port}/api/v1/spawning/deactivate/{{agent_id}}")
    print(f"  GET  http://{host}:{port}/health")
    print(f"\nPress Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
        httpd.shutdown()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Sub-Agent Spawning API Service - RESTful API for sub-agent management'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8081,
        help='Port to listen on (default: 8081)'
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
