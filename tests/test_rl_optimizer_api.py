#!/usr/bin/env python3
"""
Tests for RL Optimizer API Server
Created by @APIs-architect

Comprehensive test suite for the REST API endpoints.
"""

import sys
import os
import json
import unittest
import tempfile
import shutil
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

try:
    from rl_optimizer_api import RLOptimizerAPI
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Warning: Flask not available, skipping API tests")


@unittest.skipIf(not FLASK_AVAILABLE, "Flask not installed")
class TestRLOptimizerAPI(unittest.TestCase):
    """Test RLOptimizerAPI server."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create .git directory to make it look like a repo
        git_dir = Path(self.test_dir) / '.git'
        git_dir.mkdir()

        # Initialize API with test directory
        self.api = RLOptimizerAPI(repo_root=self.test_dir, host='127.0.0.1', port=5001)
        self.client = self.api.app.test_client()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'rl-optimizer-api')
        self.assertIn('version', data)
        self.assertIn('timestamp', data)

    def test_status_endpoint(self):
        """Test status endpoint."""
        response = self.client.get('/api/v1/status')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('status', data)
        self.assertIn('configuration', data)
        self.assertIn('reward_weights', data)
        self.assertIn('storage', data)
        
        # Check configuration
        config = data['configuration']
        self.assertIn('learning_rate', config)
        self.assertIn('epsilon', config)

    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        response = self.client.get('/api/v1/metrics')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('model_stats', data)
        self.assertIn('metrics', data)
        
        # Check model stats
        stats = data['model_stats']
        self.assertIn('total_episodes', stats)
        self.assertIn('epsilon', stats)
        self.assertIn('q_table_size', stats)

    def test_recommend_endpoint_missing_workflow(self):
        """Test recommendation endpoint without workflow parameter."""
        response = self.client.get('/api/v1/recommend')
        
        self.assertEqual(response.status_code, 400)
        
        data = response.get_json()
        self.assertIn('error', data)
        self.assertIn('workflow', data['error'])

    def test_recommend_endpoint_with_workflow(self):
        """Test recommendation endpoint with workflow parameter."""
        response = self.client.get('/api/v1/recommend?workflow=test-workflow')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['workflow'], 'test-workflow')
        self.assertIn('recommended_action', data)
        self.assertIn('expected_improvement', data)
        self.assertIn('confidence', data)
        self.assertIn('reasoning', data)
        self.assertIn('current_state', data)

    def test_recommend_endpoint_no_alternatives(self):
        """Test recommendation endpoint without alternatives."""
        response = self.client.get('/api/v1/recommend?workflow=test-workflow&include_alternatives=false')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertNotIn('alternative_actions', data)

    def test_train_endpoint_default(self):
        """Test training endpoint with default parameters."""
        response = self.client.post(
            '/api/v1/train',
            json={}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('episodes_trained', data)
        self.assertIn('duration_seconds', data)
        self.assertIn('total_episodes', data)
        self.assertIn('epsilon', data)

    def test_train_endpoint_custom_episodes(self):
        """Test training endpoint with custom episodes."""
        response = self.client.post(
            '/api/v1/train',
            json={'episodes': 50, 'save': False}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['episodes_trained'], 50)

    def test_train_endpoint_invalid_episodes(self):
        """Test training endpoint with invalid episodes."""
        response = self.client.post(
            '/api/v1/train',
            json={'episodes': -10}
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = response.get_json()
        self.assertIn('error', data)

    def test_apply_endpoint_missing_workflow(self):
        """Test apply endpoint without workflow parameter."""
        response = self.client.post(
            '/api/v1/apply',
            json={}
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = response.get_json()
        self.assertIn('error', data)

    def test_apply_endpoint_dry_run(self):
        """Test apply endpoint in dry run mode."""
        response = self.client.post(
            '/api/v1/apply',
            json={
                'workflow': 'test-workflow',
                'dry_run': True
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['workflow'], 'test-workflow')
        self.assertTrue(data['dry_run'])
        self.assertFalse(data['applied'])
        self.assertIn('message', data)

    def test_apply_endpoint_with_action(self):
        """Test apply endpoint with specific action."""
        response = self.client.post(
            '/api/v1/apply',
            json={
                'workflow': 'test-workflow',
                'action': 'enable_caching',
                'dry_run': True
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['action'], 'enable_caching')

    def test_apply_endpoint_invalid_action(self):
        """Test apply endpoint with invalid action."""
        response = self.client.post(
            '/api/v1/apply',
            json={
                'workflow': 'test-workflow',
                'action': 'invalid_action'
            }
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = response.get_json()
        self.assertIn('error', data)

    def test_list_workflows_endpoint(self):
        """Test list workflows endpoint."""
        response = self.client.get('/api/v1/workflows')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('workflows', data)
        self.assertIn('count', data)
        self.assertIn('timestamp', data)
        self.assertIsInstance(data['workflows'], list)

    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = self.client.get('/health')
        
        # CORS headers should be present
        self.assertIn('Access-Control-Allow-Origin', response.headers)


class TestRLOptimizerAPIIntegration(unittest.TestCase):
    """Integration tests for API workflows."""

    def setUp(self):
        """Set up test fixtures."""
        if not FLASK_AVAILABLE:
            self.skipTest("Flask not available")
        
        self.test_dir = tempfile.mkdtemp()
        git_dir = Path(self.test_dir) / '.git'
        git_dir.mkdir()
        
        self.api = RLOptimizerAPI(repo_root=self.test_dir)
        self.client = self.api.app.test_client()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_train_then_recommend(self):
        """Test training model and then getting recommendation."""
        # First train
        train_response = self.client.post(
            '/api/v1/train',
            json={'episodes': 10, 'save': True}
        )
        self.assertEqual(train_response.status_code, 200)
        
        # Then get recommendation
        rec_response = self.client.get('/api/v1/recommend?workflow=test-workflow')
        self.assertEqual(rec_response.status_code, 200)
        
        rec_data = rec_response.get_json()
        self.assertIn('recommended_action', rec_data)

    def test_multiple_workflows(self):
        """Test handling multiple different workflows."""
        workflows = ['workflow-1', 'workflow-2', 'workflow-3']
        
        for workflow in workflows:
            response = self.client.get(f'/api/v1/recommend?workflow={workflow}')
            self.assertEqual(response.status_code, 200)
            
            data = response.get_json()
            self.assertEqual(data['workflow'], workflow)


if __name__ == '__main__':
    unittest.main()
