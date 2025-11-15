#!/usr/bin/env python3
"""
Sync Agents to World State
Synchronizes all agents from the registry into the world model with Charlotte, NC as home base.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Path constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(SCRIPT_DIR, '..', '.github', 'agent-system', 'registry.json')
WORLD_STATE_PATH = os.path.join(SCRIPT_DIR, 'world_state.json')

# Charlotte, NC coordinates - Home base for all agents
CHARLOTTE_NC = {
    "id": "US:Charlotte",
    "label": "Charlotte, NC",
    "lat": 35.2271,
    "lng": -80.8431
}


def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(filepath: str, data: Dict[str, Any]) -> None:
    """Save data to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def create_world_agent_from_registry(registry_agent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a registry agent to a world state agent format.
    All agents start at Charlotte, NC home base.
    """
    agent_id = registry_agent.get('id')
    name = registry_agent.get('name', 'Unknown Agent')
    specialization = registry_agent.get('specialization', 'general')
    status = registry_agent.get('status', 'active')
    metrics = registry_agent.get('metrics', {})
    
    # Create world agent with Charlotte as home base
    world_agent = {
        "id": agent_id,
        "label": name,
        "specialization": specialization,
        "location_region_id": CHARLOTTE_NC["id"],
        "status": "idle" if status == "active" else "inactive",
        "path": [],
        "current_idea_id": None,
        "home_base": CHARLOTTE_NC["id"],
        "metrics": {
            "issues_resolved": metrics.get('issues_resolved', 0),
            "prs_merged": metrics.get('prs_merged', 0),
            "reviews_given": metrics.get('reviews_given', 0),
            "code_quality_score": metrics.get('code_quality_score', 0.5),
            "overall_score": metrics.get('overall_score', 0.0)
        },
        "traits": registry_agent.get('traits', {
            "creativity": 70,
            "caution": 70,
            "speed": 70
        })
    }
    
    return world_agent


def ensure_charlotte_region_exists(world_state: Dict[str, Any]) -> None:
    """Ensure Charlotte, NC exists as a region in world state."""
    regions = world_state.get('regions', [])
    
    # Check if Charlotte already exists
    charlotte_exists = any(r.get('id') == CHARLOTTE_NC['id'] for r in regions)
    
    if not charlotte_exists:
        # Add Charlotte as home base region
        charlotte_region = {
            "id": CHARLOTTE_NC["id"],
            "label": CHARLOTTE_NC["label"],
            "lat": CHARLOTTE_NC["lat"],
            "lng": CHARLOTTE_NC["lng"],
            "idea_count": 0,
            "is_home_base": True,
            "description": "Home base for all Chained autonomous agents"
        }
        regions.insert(0, charlotte_region)  # Add at beginning
        world_state['regions'] = regions
        print(f"✅ Added Charlotte, NC as home base region")
    else:
        # Update existing Charlotte to mark as home base
        for region in regions:
            if region.get('id') == CHARLOTTE_NC['id']:
                region['is_home_base'] = True
                region['description'] = "Home base for all Chained autonomous agents"
                print(f"✅ Updated Charlotte, NC as home base")
                break


def sync_agents_to_world() -> Dict[str, Any]:
    """
    Main sync function: Load registry, convert agents, update world state.
    
    Returns:
        Summary of sync operation
    """
    print("=" * 70)
    print("🌍 Syncing Agents to World State")
    print("=" * 70)
    
    # Load registry
    print(f"\n📖 Loading agent registry from: {REGISTRY_PATH}")
    registry = load_json_file(REGISTRY_PATH)
    registry_agents = registry.get('agents', [])
    print(f"   Found {len(registry_agents)} agents in registry")
    
    # Load world state
    print(f"\n🌍 Loading world state from: {WORLD_STATE_PATH}")
    world_state = load_json_file(WORLD_STATE_PATH)
    current_world_agents = world_state.get('agents', [])
    print(f"   Current agents in world: {len(current_world_agents)}")
    
    # Ensure Charlotte, NC exists as home base
    print("\n🏠 Ensuring Charlotte, NC home base...")
    ensure_charlotte_region_exists(world_state)
    
    # Convert all registry agents to world agents
    print(f"\n🤖 Converting {len(registry_agents)} agents to world format...")
    world_agents = []
    for reg_agent in registry_agents:
        world_agent = create_world_agent_from_registry(reg_agent)
        world_agents.append(world_agent)
        print(f"   ✓ {world_agent['label']} ({world_agent['specialization']}) - Score: {world_agent['metrics']['overall_score']:.2f}")
    
    # Update world state
    world_state['agents'] = world_agents
    world_state['time'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Update metrics
    world_state['metrics']['active_agents'] = len([a for a in world_agents if a.get('status') == 'idle' or a.get('status') == 'traveling'])
    world_state['metrics']['total_agent_count'] = len(world_agents)
    
    # Add scoring thresholds to metrics
    config = registry.get('config', {})
    world_state['metrics']['elimination_threshold'] = config.get('elimination_threshold', 0.3)
    world_state['metrics']['promotion_threshold'] = config.get('promotion_threshold', 0.85)
    
    # Add Hall of Fame info
    hall_of_fame = registry.get('hall_of_fame', [])
    world_state['metrics']['hall_of_fame_count'] = len(hall_of_fame)
    
    # Save updated world state
    print(f"\n💾 Saving updated world state...")
    save_json_file(WORLD_STATE_PATH, world_state)
    print(f"   ✓ Saved to: {WORLD_STATE_PATH}")
    
    summary = {
        'agents_synced': len(world_agents),
        'home_base': CHARLOTTE_NC['label'],
        'active_agents': world_state['metrics']['active_agents'],
        'timestamp': world_state['time']
    }
    
    print("\n" + "=" * 70)
    print("✅ Sync Complete!")
    print("=" * 70)
    print(f"Total agents synced: {summary['agents_synced']}")
    print(f"Active agents: {summary['active_agents']}")
    print(f"Home base: {summary['home_base']}")
    print(f"Timestamp: {summary['timestamp']}")
    print("=" * 70)
    
    return summary


def main():
    """Main entry point."""
    try:
        summary = sync_agents_to_world()
        return 0
    except Exception as e:
        print(f"\n❌ Error during sync: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
