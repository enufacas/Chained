#!/usr/bin/env python3
"""
RL Resource Optimizer API Server
Created by @APIs-architect

REST API for real-time GitHub Actions resource optimization recommendations.
Provides endpoints for getting optimization recommendations, training the model,
and monitoring performance.

Features:
- GET /health - Health check endpoint
- GET /api/v1/recommend - Get optimization recommendation
- POST /api/v1/train - Train the RL model
- GET /api/v1/metrics - Get optimizer metrics and performance
- GET /api/v1/status - Get current model status
- POST /api/v1/apply - Apply recommendations (webhook support)

Example Usage:
    # Start the API server
    python3 tools/rl_optimizer_api.py

    # Get recommendation for a workflow
    curl http://localhost:5000/api/v1/recommend?workflow=code-quality

    # Train the model
    curl -X POST http://localhost:5000/api/v1/train -d '{"episodes": 100}'

    # Check metrics
    curl http://localhost:5000/api/v1/metrics
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from rl_resource_optimizer import RLResourceOptimizer, ResourceAction

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("ERROR: Flask not installed. Install with: pip install flask flask-cors")
    sys.exit(1)


class RLOptimizerAPI:
    """REST API for RL Resource Optimizer."""

    def __init__(self, repo_root: str = None, host: str = "0.0.0.0", port: int = 5000):
        """
        Initialize the API server.

        Args:
            repo_root: Repository root directory
            host: Host to bind to
            port: Port to listen on
        """
        self.optimizer = RLResourceOptimizer(repo_root=repo_root)
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for all routes
        self.host = host
        self.port = port

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register all API routes."""

        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'service': 'rl-optimizer-api',
                'version': '1.0.0',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

        @self.app.route('/api/v1/recommend', methods=['GET'])
        def recommend():
            """
            Get optimization recommendation for a workflow.

            Query Parameters:
                workflow (str): Workflow name (required)
                include_alternatives (bool): Include alternative actions (default: true)

            Returns:
                JSON with recommendation details
            """
            workflow = request.args.get('workflow')
            if not workflow:
                return jsonify({
                    'error': 'Missing required parameter: workflow'
                }), 400

            include_alternatives = request.args.get('include_alternatives', 'true').lower() == 'true'

            try:
                # Get recommendation
                rec = self.optimizer.get_recommendation(
                    workflow_name=workflow,
                    execution_history=None  # Will load from data if available
                )

                # Build response
                response = {
                    'workflow': rec.workflow_name,
                    'current_state': rec.current_state,
                    'recommended_action': rec.recommended_action,
                    'expected_improvement': rec.expected_improvement,
                    'confidence': rec.confidence,
                    'reasoning': rec.reasoning,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

                if include_alternatives:
                    response['alternative_actions'] = rec.alternative_actions

                return jsonify(response)

            except Exception as e:
                return jsonify({
                    'error': f'Failed to get recommendation: {str(e)}'
                }), 500

        @self.app.route('/api/v1/train', methods=['POST'])
        def train():
            """
            Train the RL model.

            Body Parameters:
                episodes (int): Number of training episodes (default: 100)
                save (bool): Save model after training (default: true)

            Returns:
                JSON with training results
            """
            data = request.get_json() or {}
            episodes = data.get('episodes', 100)
            save_model = data.get('save', True)

            try:
                # Validate episodes
                if not isinstance(episodes, int) or episodes <= 0:
                    return jsonify({
                        'error': 'Invalid episodes value. Must be positive integer.'
                    }), 400

                # Run training
                start_time = datetime.now(timezone.utc)
                self.optimizer.simulate_training(num_episodes=episodes)

                if save_model:
                    self.optimizer.save_q_table()
                    self.optimizer.save_experiences()

                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()

                return jsonify({
                    'success': True,
                    'episodes_trained': episodes,
                    'duration_seconds': duration,
                    'total_episodes': self.optimizer.total_episodes,
                    'epsilon': self.optimizer.epsilon,
                    'q_table_size': len(self.optimizer.q_table),
                    'timestamp': end_time.isoformat()
                })

            except Exception as e:
                return jsonify({
                    'error': f'Training failed: {str(e)}'
                }), 500

        @self.app.route('/api/v1/metrics', methods=['GET'])
        def metrics():
            """
            Get optimizer metrics and performance statistics.

            Returns:
                JSON with metrics
            """
            try:
                return jsonify({
                    'model_stats': {
                        'total_episodes': self.optimizer.total_episodes,
                        'epsilon': self.optimizer.epsilon,
                        'q_table_size': len(self.optimizer.q_table),
                        'experience_buffer_size': len(self.optimizer.experience_buffer),
                        'learning_rate': self.optimizer.LEARNING_RATE,
                        'discount_factor': self.optimizer.DISCOUNT_FACTOR
                    },
                    'metrics': self.optimizer.metrics,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                return jsonify({
                    'error': f'Failed to get metrics: {str(e)}'
                }), 500

        @self.app.route('/api/v1/status', methods=['GET'])
        def status():
            """
            Get current model status and configuration.

            Returns:
                JSON with status details
            """
            try:
                return jsonify({
                    'status': 'ready',
                    'model_loaded': len(self.optimizer.q_table) > 0,
                    'configuration': {
                        'learning_rate': self.optimizer.LEARNING_RATE,
                        'discount_factor': self.optimizer.DISCOUNT_FACTOR,
                        'epsilon': self.optimizer.epsilon,
                        'min_epsilon': self.optimizer.MIN_EPSILON,
                        'epsilon_decay': self.optimizer.EPSILON_DECAY,
                        'replay_buffer_size': self.optimizer.REPLAY_BUFFER_SIZE,
                        'batch_size': self.optimizer.BATCH_SIZE
                    },
                    'reward_weights': {
                        'duration': self.optimizer.REWARD_WEIGHT_DURATION,
                        'success': self.optimizer.REWARD_WEIGHT_SUCCESS,
                        'utilization': self.optimizer.REWARD_WEIGHT_UTILIZATION
                    },
                    'storage': {
                        'directory': str(self.optimizer.storage_dir),
                        'q_table_file': str(self.optimizer.q_table_file),
                        'experience_file': str(self.optimizer.experience_file),
                        'metrics_file': str(self.optimizer.metrics_file)
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                return jsonify({
                    'error': f'Failed to get status: {str(e)}'
                }), 500

        @self.app.route('/api/v1/apply', methods=['POST'])
        def apply_recommendation():
            """
            Apply optimization recommendation (webhook support).

            Body Parameters:
                workflow (str): Workflow name (required)
                action (str): Action to apply (optional, will recommend if not provided)
                dry_run (bool): Simulate only, don't apply (default: true)

            Returns:
                JSON with application result
            """
            data = request.get_json() or {}
            workflow = data.get('workflow')
            action = data.get('action')
            dry_run = data.get('dry_run', True)

            if not workflow:
                return jsonify({
                    'error': 'Missing required parameter: workflow'
                }), 400

            try:
                # Get recommendation if action not specified
                if not action:
                    rec = self.optimizer.get_recommendation(workflow_name=workflow)
                    action = rec.recommended_action

                # Validate action
                try:
                    action_enum = ResourceAction(action)
                except ValueError:
                    return jsonify({
                        'error': f'Invalid action: {action}'
                    }), 400

                # For now, this is a webhook endpoint that logs the application
                # In production, this would integrate with GitHub Actions API
                result = {
                    'workflow': workflow,
                    'action': action,
                    'applied': not dry_run,
                    'dry_run': dry_run,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

                if dry_run:
                    result['message'] = f'Would apply {action} to {workflow} (dry run)'
                else:
                    result['message'] = f'Applied {action} to {workflow}'
                    # TODO: Integrate with GitHub Actions API to actually apply changes
                    result['warning'] = 'Automatic application not yet implemented. Manual workflow update required.'

                return jsonify(result)

            except Exception as e:
                return jsonify({
                    'error': f'Failed to apply recommendation: {str(e)}'
                }), 500

        @self.app.route('/api/v1/workflows', methods=['GET'])
        def list_workflows():
            """
            List all workflows with their current states.

            Returns:
                JSON with workflow list
            """
            try:
                workflows = []
                for workflow_name, state in self.optimizer.workflow_states.items():
                    workflows.append({
                        'name': workflow_name,
                        'state': asdict(state)
                    })

                return jsonify({
                    'workflows': workflows,
                    'count': len(workflows),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                return jsonify({
                    'error': f'Failed to list workflows: {str(e)}'
                }), 500

    def run(self, debug: bool = False):
        """
        Start the API server.

        Args:
            debug: Enable debug mode
        """
        print(f"🚀 Starting RL Optimizer API Server")
        print(f"   Host: {self.host}")
        print(f"   Port: {self.port}")
        print(f"   Debug: {debug}")
        print(f"\n📚 API Endpoints:")
        print(f"   GET  /health                    - Health check")
        print(f"   GET  /api/v1/recommend          - Get recommendation")
        print(f"   POST /api/v1/train              - Train model")
        print(f"   GET  /api/v1/metrics            - Get metrics")
        print(f"   GET  /api/v1/status             - Get status")
        print(f"   POST /api/v1/apply              - Apply recommendation")
        print(f"   GET  /api/v1/workflows          - List workflows")
        print(f"\n🤖 Created by @APIs-architect")
        print("=" * 60)

        self.app.run(host=self.host, port=self.port, debug=debug)


def main():
    """Main entry point for API server."""
    parser = argparse.ArgumentParser(
        description='RL Resource Optimizer API Server by @APIs-architect'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to listen on (default: 5000)'
    )
    parser.add_argument(
        '--repo-root',
        help='Repository root directory'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    args = parser.parse_args()

    # Create and run API server
    api = RLOptimizerAPI(
        repo_root=args.repo_root,
        host=args.host,
        port=args.port
    )
    api.run(debug=args.debug)


if __name__ == '__main__':
    main()
