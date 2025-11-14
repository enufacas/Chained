#!/usr/bin/env python3
"""
Tests for the atomic registry updater.

This test suite validates that the atomic registry updater can handle
concurrent modifications and resolve conflicts correctly.
"""

import json
import os
import sys
import tempfile
import shutil
import subprocess
import unittest
from pathlib import Path
from datetime import datetime

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

# Import the module by loading it directly
import importlib.util
spec = importlib.util.spec_from_file_location(
    "atomic_registry_update",
    Path(__file__).parent.parent / "tools" / "atomic-registry-update.py"
)
atomic_registry_update = importlib.util.module_from_spec(spec)
spec.loader.exec_module(atomic_registry_update)

AtomicRegistryUpdater = atomic_registry_update.AtomicRegistryUpdater
RegistryUpdateError = atomic_registry_update.RegistryUpdateError


class TestAtomicRegistryUpdater(unittest.TestCase):
    """Test atomic registry updates"""
    
    def setUp(self):
        """Set up test environment with a temporary git repository"""
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize a git repository
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True)
        
        # Create the agent-system directory structure
        agent_system_dir = Path(self.test_dir) / ".github" / "agent-system"
        agent_system_dir.mkdir(parents=True)
        
        # Create an initial registry
        self.registry_path = agent_system_dir / "registry.json"
        initial_registry = {
            "version": "2.0.0",
            "agents": [],
            "hall_of_fame": [],
            "system_lead": None,
            "config": {
                "spawn_interval_hours": 3,
                "max_active_agents": 10,
                "elimination_threshold": 0.3,
                "promotion_threshold": 0.85
            },
            "last_spawn": None,
            "last_evaluation": None,
            "specializations_note": "Test registry"
        }
        
        with open(self.registry_path, 'w') as f:
            json.dump(initial_registry, f, indent=2)
        
        # Initial commit
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True, capture_output=True)
        
        # Create a main branch
        subprocess.run(["git", "branch", "-M", "main"], check=True, capture_output=True)
        
        self.updater = AtomicRegistryUpdater(verbose=False)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_add_single_agent(self):
        """Test adding a single agent to the registry"""
        agent_data = {
            "id": "agent-test-001",
            "name": "Test Agent",
            "specialization": "test-specialist",
            "status": "active",
            "spawned_at": datetime.utcnow().isoformat() + "Z",
            "metrics": {
                "issues_resolved": 0,
                "prs_merged": 0,
                "overall_score": 0.0
            }
        }
        
        # Add the agent
        success = self.updater.add_agent(agent_data, commit_message="Test add agent")
        self.assertTrue(success)
        
        # Verify the agent was added
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        self.assertEqual(len(registry['agents']), 1)
        self.assertEqual(registry['agents'][0]['id'], 'agent-test-001')
    
    def test_add_duplicate_agent(self):
        """Test that adding a duplicate agent is idempotent"""
        agent_data = {
            "id": "agent-test-002",
            "name": "Test Agent 2",
            "specialization": "test-specialist",
            "status": "active",
            "spawned_at": datetime.utcnow().isoformat() + "Z",
            "metrics": {"overall_score": 0.0}
        }
        
        # Add the agent twice
        self.updater.add_agent(agent_data, commit_message="Add agent first time")
        self.updater.add_agent(agent_data, commit_message="Add agent second time")
        
        # Verify only one agent exists
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        self.assertEqual(len(registry['agents']), 1)
    
    def test_merge_agents_arrays(self):
        """Test merging agent arrays with no conflicts"""
        base_agents = [
            {"id": "agent-001", "name": "Agent 1", "spawned_at": "2025-01-01T00:00:00Z"},
            {"id": "agent-002", "name": "Agent 2", "spawned_at": "2025-01-02T00:00:00Z"},
        ]
        
        incoming_agents = [
            {"id": "agent-002", "name": "Agent 2", "spawned_at": "2025-01-02T00:00:00Z"},
            {"id": "agent-003", "name": "Agent 3", "spawned_at": "2025-01-03T00:00:00Z"},
        ]
        
        merged = self.updater._merge_agents_arrays(base_agents, incoming_agents)
        
        # Should have 3 unique agents, sorted by spawn time
        self.assertEqual(len(merged), 3)
        self.assertEqual([a['id'] for a in merged], ['agent-001', 'agent-002', 'agent-003'])
    
    def test_merge_agents_with_duplicate_different_timestamps(self):
        """Test merging agents where same ID has different timestamps (keep most recent)"""
        base_agents = [
            {"id": "agent-001", "name": "Agent 1", "spawned_at": "2025-01-01T00:00:00Z"},
        ]
        
        incoming_agents = [
            {"id": "agent-001", "name": "Agent 1 Updated", "spawned_at": "2025-01-02T00:00:00Z"},
        ]
        
        merged = self.updater._merge_agents_arrays(base_agents, incoming_agents)
        
        # Should have 1 agent with the later timestamp
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]['spawned_at'], "2025-01-02T00:00:00Z")
        self.assertEqual(merged[0]['name'], "Agent 1 Updated")
    
    def test_remove_agents(self):
        """Test removing agents from the registry"""
        # First add some agents
        for i in range(3):
            agent_data = {
                "id": f"agent-test-{i:03d}",
                "name": f"Test Agent {i}",
                "specialization": "test-specialist",
                "status": "active",
                "spawned_at": datetime.utcnow().isoformat() + "Z",
                "metrics": {"overall_score": 0.0}
            }
            self.updater.add_agent(agent_data)
        
        # Remove one agent
        success = self.updater.remove_agents(
            ["agent-test-001"],
            reason="Test removal",
            commit_message="Remove test agent"
        )
        self.assertTrue(success)
        
        # Verify it was removed
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        self.assertEqual(len(registry['agents']), 2)
        agent_ids = [a['id'] for a in registry['agents']]
        self.assertNotIn('agent-test-001', agent_ids)
    
    def test_update_metrics(self):
        """Test updating agent metrics"""
        # Add an agent
        agent_data = {
            "id": "agent-metrics-test",
            "name": "Metrics Test Agent",
            "specialization": "test-specialist",
            "status": "active",
            "spawned_at": datetime.utcnow().isoformat() + "Z",
            "metrics": {
                "issues_resolved": 0,
                "overall_score": 0.0
            }
        }
        self.updater.add_agent(agent_data)
        
        # Update metrics
        new_metrics = {
            "issues_resolved": 5,
            "prs_merged": 3,
            "overall_score": 0.75
        }
        success = self.updater.update_metrics(
            "agent-metrics-test",
            new_metrics,
            commit_message="Update metrics"
        )
        self.assertTrue(success)
        
        # Verify metrics were updated
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        agent = registry['agents'][0]
        self.assertEqual(agent['metrics']['issues_resolved'], 5)
        self.assertEqual(agent['metrics']['overall_score'], 0.75)
    
    def test_custom_update_function(self):
        """Test using a custom update function"""
        def custom_update(registry):
            # Add a custom field
            registry['custom_field'] = 'test_value'
            return registry
        
        success = self.updater.update_registry(
            custom_update,
            commit_message="Custom update"
        )
        self.assertTrue(success)
        
        # Verify custom field was added
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        
        self.assertEqual(registry['custom_field'], 'test_value')


def run_tests():
    """Run the test suite"""
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAtomicRegistryUpdater)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
