#!/usr/bin/env python3
"""
Add Agent to Registry

Helper script for workflows to add new agents to the distributed registry.
Replaces inline Python code in workflow files with a simple, maintainable interface.

Usage:
    python3 tools/add_agent_to_registry.py agent_data.json
"""

import json
import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from registry_manager import RegistryManager


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 add_agent_to_registry.py agent_data.json")
        sys.exit(1)
    
    agent_data_file = sys.argv[1]
    
    try:
        # Load agent data
        with open(agent_data_file, 'r') as f:
            agent_data = json.load(f)
        
        # Validate required fields
        if "id" not in agent_data:
            print("Error: Agent data must include 'id' field")
            sys.exit(1)
        
        # Update registry
        registry = RegistryManager()
        
        if registry.update_agent(agent_data):
            print(f"✓ Successfully added/updated agent {agent_data['id']}")
            
            # Note: last_spawn timestamp is now updated by the parent workflow
            # after all concurrent agent spawns complete to avoid merge conflicts
            # when multiple agents are spawned in parallel
            
            sys.exit(0)
        else:
            print(f"✗ Failed to add/update agent {agent_data['id']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
