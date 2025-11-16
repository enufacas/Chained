#!/usr/bin/env python3
"""
World State Manager
Handles reading and writing the persistent world state for the Chained world model.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

WORLD_DIR = os.path.dirname(os.path.abspath(__file__))
WORLD_STATE_FILE = os.path.join(WORLD_DIR, "world_state.json")


def load_world_state() -> Dict[str, Any]:
    """Load the current world state from disk."""
    if not os.path.exists(WORLD_STATE_FILE):
        return _create_default_world_state()
    
    with open(WORLD_STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_world_state(state: Dict[str, Any]) -> None:
    """Save the world state to disk."""
    # Update timestamp
    state['time'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    with open(WORLD_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def _create_default_world_state() -> Dict[str, Any]:
    """Create a default world state structure."""
    return {
        "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "tick": 0,
        "agents": [],
        "regions": [],
        "objectives": [],
        "metrics": {
            "total_ideas": 0,
            "total_regions": 0,
            "ticks_completed": 0
        }
    }


def get_agent_by_id(state: Dict[str, Any], agent_id: str) -> Optional[Dict[str, Any]]:
    """Get an agent by ID."""
    for agent in state.get('agents', []):
        if agent.get('id') == agent_id:
            return agent
    return None


def get_region_by_id(state: Dict[str, Any], region_id: str) -> Optional[Dict[str, Any]]:
    """Get a region by ID."""
    for region in state.get('regions', []):
        if region.get('id') == region_id:
            return region
    return None


def add_or_update_region(state: Dict[str, Any], region: Dict[str, Any]) -> None:
    """Add a new region or update an existing one."""
    existing = get_region_by_id(state, region['id'])
    if existing:
        # Update existing region
        existing.update(region)
    else:
        # Add new region
        state['regions'].append(region)
        state['metrics']['total_regions'] = len(state['regions'])


def update_agent_location(state: Dict[str, Any], agent_id: str, new_location_id: str) -> bool:
    """Update an agent's location."""
    agent = get_agent_by_id(state, agent_id)
    if not agent:
        return False
    
    agent['location_region_id'] = new_location_id
    return True


def increment_tick(state: Dict[str, Any]) -> int:
    """Increment the world tick counter and return new value."""
    state['tick'] += 1
    state['metrics']['ticks_completed'] = state['tick']
    return state['tick']


def update_region_idea_count(state: Dict[str, Any], region_id: str, idea_count: int) -> bool:
    """Update the idea count for a specific region."""
    region = get_region_by_id(state, region_id)
    if not region:
        return False
    
    region['idea_count'] = idea_count
    return True


def get_all_regions(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get all regions."""
    return state.get('regions', [])


def get_all_agents(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get all agents."""
    return state.get('agents', [])


def update_agent_mission(
    state: Dict[str, Any],
    agent_id: str,
    mission_id: str,
    mission_title: str,
    issue_number: Optional[int] = None
) -> bool:
    """
    Update an agent's current mission assignment.
    
    Args:
        state: World state dict
        agent_id: Agent ID (e.g., 'agent-123' or specialization like 'cloud-architect')
        mission_id: Mission/idea ID
        mission_title: Human-readable mission title
        issue_number: Optional GitHub issue number
    
    Returns:
        True if agent was updated, False if not found
    """
    # Try to find agent by ID first
    agent = get_agent_by_id(state, agent_id)
    
    # If not found by ID, try by specialization
    if not agent:
        for a in state.get('agents', []):
            if a.get('specialization') == agent_id:
                agent = a
                break
    
    if not agent:
        return False
    
    # Update agent's mission information
    agent['current_idea_id'] = mission_id
    agent['status'] = 'working'  # Changed from 'exploring' to 'working'
    
    # Add mission metadata if not present
    if 'current_mission' not in agent:
        agent['current_mission'] = {}
    
    agent['current_mission'] = {
        'mission_id': mission_id,
        'title': mission_title,
        'issue_number': issue_number,
        'assigned_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    return True


def clear_agent_mission(state: Dict[str, Any], agent_id: str) -> bool:
    """
    Clear an agent's current mission when completed or abandoned.
    
    Args:
        state: World state dict
        agent_id: Agent ID or specialization
    
    Returns:
        True if agent was updated, False if not found
    """
    agent = get_agent_by_id(state, agent_id)
    
    if not agent:
        for a in state.get('agents', []):
            if a.get('specialization') == agent_id:
                agent = a
                break
    
    if not agent:
        return False
    
    agent['status'] = 'exploring'
    if 'current_mission' in agent:
        del agent['current_mission']
    
    return True


if __name__ == '__main__':
    # Test the module
    state = load_world_state()
    print("Current world state:")
    print(f"  Tick: {state['tick']}")
    print(f"  Agents: {len(state.get('agents', []))}")
    print(f"  Regions: {len(state.get('regions', []))}")
    print(f"  Total Ideas: {state['metrics']['total_ideas']}")
