#!/usr/bin/env python3
"""
Batch Update Agents

Helper script to update multiple agents' metrics in the distributed registry.
Used by the agent evaluator workflow.

Usage:
    python3 tools/batch_update_agents.py agents_updates.json
    
Format of agents_updates.json:
    {
        "agent-123": {
            "metrics": {...},
            "status": "active"
        },
        "agent-456": {...}
    }
"""

import json
import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from registry_manager import RegistryManager


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 batch_update_agents.py agents_updates.json")
        sys.exit(1)
    
    updates_file = sys.argv[1]
    
    try:
        # Load updates
        with open(updates_file, 'r') as f:
            updates = json.load(f)
        
        registry = RegistryManager()
        
        success_count = 0
        fail_count = 0
        
        for agent_id, agent_updates in updates.items():
            # Get current agent data
            agent = registry.get_agent(agent_id)
            if not agent:
                print(f"⚠️  Agent {agent_id} not found, skipping")
                fail_count += 1
                continue
            
            # Merge updates
            agent.update(agent_updates)
            
            # Update registry
            if registry.update_agent(agent):
                print(f"✓ Updated agent {agent_id}")
                success_count += 1
            else:
                print(f"✗ Failed to update agent {agent_id}")
                fail_count += 1
        
        print(f"\n✅ Updated {success_count} agent(s)")
        if fail_count > 0:
            print(f"⚠️  Failed to update {fail_count} agent(s)")
            sys.exit(1)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
