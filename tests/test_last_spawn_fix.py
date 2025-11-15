#!/usr/bin/env python3
"""
Tests for the last_spawn update fix.

This test suite validates that:
1. add_agent_to_registry.py does NOT update last_spawn (to avoid conflicts)
2. update_last_spawn.py correctly updates the last_spawn timestamp
3. Multiple concurrent agent additions don't conflict on last_spawn
"""

import json
import os
import sys
import tempfile
import shutil
import subprocess
import unittest
from pathlib import Path
from datetime import datetime, timezone
import time

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from registry_manager import RegistryManager


class TestLastSpawnFix(unittest.TestCase):
    """Test that last_spawn updates don't cause conflicts"""
    
    def setUp(self):
        """Set up test environment with a temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create the agent-system directory structure
        agent_system_dir = Path(self.test_dir) / ".github" / "agent-system"
        agent_system_dir.mkdir(parents=True)
        
        # Create metadata directory
        metadata_dir = agent_system_dir / "metadata"
        metadata_dir.mkdir(exist_ok=True)
        
        # Create initial last_spawn.txt
        self.last_spawn_file = metadata_dir / "last_spawn.txt"
        initial_timestamp = "2025-01-01T00:00:00+00:00"
        with open(self.last_spawn_file, 'w') as f:
            f.write(initial_timestamp)
        
        # Create agents directory
        agents_dir = agent_system_dir / "agents"
        agents_dir.mkdir(exist_ok=True)
        
        # Create a simple registry.json to enable legacy mode or distributed mode
        # We'll use distributed mode since that's what the metadata files indicate
        registry_file = agent_system_dir / "registry.json"
        registry_data = {
            "version": "2.0.0",
            "agents": [],
            "hall_of_fame": [],
            "system_lead": None,
            "config": {
                "spawn_interval_hours": 3,
                "max_active_agents": 50
            },
            "last_spawn": initial_timestamp,
            "last_evaluation": None
        }
        with open(registry_file, 'w') as f:
            json.dump(registry_data, f, indent=2)
        
        self.initial_timestamp = initial_timestamp
        self.registry_file = registry_file
        
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_add_agent_does_not_update_last_spawn(self):
        """Test that adding an agent doesn't update last_spawn"""
        # Create test agent data
        agent_data = {
            "id": "test-agent-001",
            "name": "Test Agent",
            "specialization": "testing",
            "spawned_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Create temp file with agent data
        agent_file = Path(self.test_dir) / "test_agent.json"
        with open(agent_file, 'w') as f:
            json.dump(agent_data, f)
        
        # Run add_agent_to_registry.py
        tools_dir = Path(__file__).parent.parent / "tools"
        script = tools_dir / "add_agent_to_registry.py"
        
        result = subprocess.run(
            [sys.executable, str(script), str(agent_file)],
            cwd=self.test_dir,
            capture_output=True,
            text=True
        )
        
        # Check script succeeded
        self.assertEqual(result.returncode, 0, f"Script failed: {result.stderr}\nOutput: {result.stdout}")
        
        # Verify agent was added (check both distributed and legacy locations)
        agent_json_file = Path(self.test_dir) / ".github" / "agent-system" / "agents" / "test-agent-001.json"
        
        # In legacy mode, check registry.json
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        agent_found = any(a.get('id') == 'test-agent-001' for a in registry.get('agents', []))
        if not agent_found:
            agent_found = agent_json_file.exists()
        
        self.assertTrue(agent_found, "Agent should be added to registry")
        
        # CRITICAL: Verify last_spawn was NOT updated in the metadata file
        with open(self.last_spawn_file, 'r') as f:
            current_timestamp = f.read().strip()
        
        self.assertEqual(
            current_timestamp, 
            self.initial_timestamp,
            "last_spawn.txt should NOT be updated by add_agent_to_registry"
        )
    
    def test_update_last_spawn_script(self):
        """Test that update_last_spawn.py correctly updates the timestamp"""
        # Record initial timestamp
        with open(self.last_spawn_file, 'r') as f:
            initial = f.read().strip()
        
        # Small delay to ensure timestamp difference
        time.sleep(0.1)
        
        # Run update_last_spawn.py
        tools_dir = Path(__file__).parent.parent / "tools"
        script = tools_dir / "update_last_spawn.py"
        
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=self.test_dir,
            capture_output=True,
            text=True
        )
        
        # Check script succeeded
        self.assertEqual(result.returncode, 0, f"Script failed: {result.stderr}")
        self.assertIn("Updated last_spawn timestamp", result.stdout)
        
        # Verify timestamp was updated
        with open(self.last_spawn_file, 'r') as f:
            updated = f.read().strip()
        
        self.assertNotEqual(initial, updated, "Timestamp should be updated")
        
        # Verify it's a valid ISO timestamp
        try:
            parsed = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            self.assertIsNotNone(parsed)
        except ValueError:
            self.fail(f"Updated timestamp '{updated}' is not a valid ISO format")
    
    def test_concurrent_agent_additions_no_last_spawn_conflict(self):
        """
        Test that multiple concurrent agent additions don't conflict
        because they no longer update last_spawn
        """
        # Create multiple agent data files
        agent_count = 5
        agent_files = []
        
        for i in range(agent_count):
            agent_data = {
                "id": f"test-agent-{i:03d}",
                "name": f"Test Agent {i}",
                "specialization": "testing",
                "spawned_at": datetime.now(timezone.utc).isoformat()
            }
            
            agent_file = Path(self.test_dir) / f"test_agent_{i}.json"
            with open(agent_file, 'w') as f:
                json.dump(agent_data, f)
            agent_files.append(agent_file)
        
        # Simulate concurrent additions (sequential for testing)
        tools_dir = Path(__file__).parent.parent / "tools"
        script = tools_dir / "add_agent_to_registry.py"
        
        for agent_file in agent_files:
            result = subprocess.run(
                [sys.executable, str(script), str(agent_file)],
                cwd=self.test_dir,
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 0, f"Agent addition failed: {result.stderr}\nOutput: {result.stdout}")
        
        # Verify all agents were added (check registry.json in legacy mode)
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        agents_in_registry = len(registry.get('agents', []))
        
        # Also check distributed mode files
        agents_dir = Path(self.test_dir) / ".github" / "agent-system" / "agents"
        agent_files_created = list(agents_dir.glob("test-agent-*.json"))
        
        total_agents = max(agents_in_registry, len(agent_files_created))
        self.assertEqual(total_agents, agent_count, f"All {agent_count} agents should be added")
        
        # CRITICAL: Verify last_spawn was NOT changed by any of the additions
        with open(self.last_spawn_file, 'r') as f:
            final_timestamp = f.read().strip()
        
        self.assertEqual(
            final_timestamp,
            self.initial_timestamp,
            "last_spawn should remain unchanged despite multiple agent additions"
        )
    
    def test_registry_manager_atomic_update(self):
        """Test that RegistryManager.update_metadata_field is atomic for last_spawn"""
        registry = RegistryManager(str(Path(self.test_dir) / ".github" / "agent-system"))
        
        # Update last_spawn using the atomic method
        new_timestamp = datetime.now(timezone.utc).isoformat()
        success = registry.update_metadata_field("last_spawn", new_timestamp)
        
        self.assertTrue(success, "Atomic update should succeed")
        
        # Verify the update
        metadata = registry.get_metadata()
        self.assertEqual(metadata.get("last_spawn"), new_timestamp)


if __name__ == '__main__':
    unittest.main()
