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


def add_agent_path_entry(
    state: Dict[str, Any],
    agent_id: str,
    region_id: str,
    purpose: Optional[str] = None
) -> bool:
    """
    Add a path entry for an agent's journey to a region.
    
    Args:
        state: World state dict
        agent_id: Agent ID or specialization
        region_id: Destination region ID
        purpose: Optional description of why agent is traveling
    
    Returns:
        True if path was added, False if not found
    """
    agent = get_agent_by_id(state, agent_id)
    
    if not agent:
        for a in state.get('agents', []):
            if a.get('specialization') == agent_id:
                agent = a
                break
    
    if not agent:
        return False
    
    # Initialize path if needed
    if 'path' not in agent:
        agent['path'] = []
    
    # Add new path entry
    current_tick = state.get('tick', 0)
    path_entry = {
        'region_id': region_id,
        'arrival_tick': current_tick + 3,  # Takes 3 ticks to travel
        'purpose': purpose or 'exploring'
    }
    
    agent['path'].append(path_entry)
    agent['status'] = 'traveling'
    
    return True


def record_agent_arrival(
    state: Dict[str, Any],
    agent_id: str,
    region_id: str
) -> bool:
    """
    Record an agent's arrival at a destination region.
    Updates location and moves current path to history.
    
    Args:
        state: World state dict
        agent_id: Agent ID or specialization
        region_id: Region where agent arrived
    
    Returns:
        True if recorded, False if not found
    """
    agent = get_agent_by_id(state, agent_id)
    
    if not agent:
        for a in state.get('agents', []):
            if a.get('specialization') == agent_id:
                agent = a
                break
    
    if not agent:
        return False
    
    current_tick = state.get('tick', 0)
    
    # Initialize path_history if needed
    if 'path_history' not in agent:
        agent['path_history'] = []
    
    # Record previous location in history
    if agent.get('location_region_id'):
        history_entry = {
            'region_id': agent['location_region_id'],
            'arrival_tick': agent.get('arrival_tick', current_tick - 1),
            'departure_tick': current_tick,
            'discoveries': [],
            'collaborations': []
        }
        agent['path_history'].append(history_entry)
        
        # Keep only last 10 history entries
        if len(agent['path_history']) > 10:
            agent['path_history'] = agent['path_history'][-10:]
    
    # Update location
    agent['location_region_id'] = region_id
    agent['arrival_tick'] = current_tick
    agent['status'] = 'exploring'
    
    # Remove completed path entry
    if agent.get('path'):
        agent['path'] = [p for p in agent['path'] if p['region_id'] != region_id]
    
    return True


def add_agent_discovery(
    state: Dict[str, Any],
    agent_id: str,
    discovery: str
) -> bool:
    """
    Add a discovery to the agent's current location history.
    
    Args:
        state: World state dict
        agent_id: Agent ID or specialization
        discovery: Description of what was discovered
    
    Returns:
        True if added, False if not found
    """
    agent = get_agent_by_id(state, agent_id)
    
    if not agent:
        for a in state.get('agents', []):
            if a.get('specialization') == agent_id:
                agent = a
                break
    
    if not agent:
        return False
    
    # Add to current session discoveries (will be moved to history on departure)
    if 'current_discoveries' not in agent:
        agent['current_discoveries'] = []
    
    agent['current_discoveries'].append(discovery)
    return True


# =============================================================================
# GCP Infrastructure Region Management
# =============================================================================

def get_infrastructure_regions(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get all regions that are cloud infrastructure regions.
    
    Returns:
        List of regions with region_type == 'cloud_infrastructure'
    """
    return [
        region for region in state.get('regions', [])
        if region.get('region_type') == 'cloud_infrastructure'
    ]


def get_infrastructure_services(state: Dict[str, Any], region_id: str) -> List[Dict[str, Any]]:
    """
    Get all infrastructure services deployed in a specific region.
    
    Args:
        state: World state dict
        region_id: Region ID (e.g., 'GCP:us-central1')
    
    Returns:
        List of service dictionaries, or empty list if not found
    """
    region = get_region_by_id(state, region_id)
    if not region:
        return []
    
    infrastructure = region.get('infrastructure', {})
    return infrastructure.get('services', [])


def update_infrastructure_service_status(
    state: Dict[str, Any],
    region_id: str,
    service_name: str,
    status: str
) -> bool:
    """
    Update the status of an infrastructure service.
    
    Args:
        state: World state dict
        region_id: Region ID (e.g., 'GCP:us-central1')
        service_name: Name of the service to update
        status: New status (e.g., 'deployed', 'stopped', 'error')
    
    Returns:
        True if service was updated, False if not found
    """
    region = get_region_by_id(state, region_id)
    if not region:
        return False
    
    infrastructure = region.get('infrastructure', {})
    services = infrastructure.get('services', [])
    
    for service in services:
        if service.get('name') == service_name:
            service['status'] = status
            return True
    
    return False


def add_infrastructure_service(
    state: Dict[str, Any],
    region_id: str,
    service: Dict[str, Any]
) -> bool:
    """
    Add a new infrastructure service to a region.
    
    Args:
        state: World state dict
        region_id: Region ID (e.g., 'GCP:us-central1')
        service: Service dict with name, type, description, status
    
    Returns:
        True if service was added, False if region not found
    """
    region = get_region_by_id(state, region_id)
    if not region:
        return False
    
    # Initialize infrastructure structure if not present
    if 'infrastructure' not in region:
        region['infrastructure'] = {
            'provider': 'gcp',
            'services': [],
            'supporting_services': []
        }
    
    if 'services' not in region['infrastructure']:
        region['infrastructure']['services'] = []
    
    # Check if service already exists
    existing_services = region['infrastructure']['services']
    for existing in existing_services:
        if existing.get('name') == service.get('name'):
            # Update existing service
            existing.update(service)
            return True
    
    # Add new service
    existing_services.append(service)
    return True


def remove_infrastructure_service(
    state: Dict[str, Any],
    region_id: str,
    service_name: str
) -> bool:
    """
    Remove an infrastructure service from a region.
    
    Args:
        state: World state dict
        region_id: Region ID (e.g., 'GCP:us-central1')
        service_name: Name of the service to remove
    
    Returns:
        True if service was removed, False if not found
    """
    region = get_region_by_id(state, region_id)
    if not region:
        return False
    
    infrastructure = region.get('infrastructure', {})
    services = infrastructure.get('services', [])
    
    original_length = len(services)
    infrastructure['services'] = [
        s for s in services if s.get('name') != service_name
    ]
    
    return len(infrastructure['services']) < original_length


def get_infrastructure_region_summary(state: Dict[str, Any], region_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a summary of infrastructure in a specific region.
    
    Args:
        state: World state dict
        region_id: Region ID (e.g., 'GCP:us-central1')
    
    Returns:
        Summary dict with service counts and status breakdown, or None if not found
    """
    region = get_region_by_id(state, region_id)
    if not region or region.get('region_type') != 'cloud_infrastructure':
        return None
    
    infrastructure = region.get('infrastructure', {})
    services = infrastructure.get('services', [])
    supporting_services = infrastructure.get('supporting_services', [])
    
    # Count services by status
    status_counts = {}
    for service in services:
        status = service.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        'region_id': region_id,
        'provider': infrastructure.get('provider', 'unknown'),
        'total_services': len(services),
        'total_supporting_services': len(supporting_services),
        'services_by_status': status_counts,
        'services': [s.get('name') for s in services],
        'supporting_services': [s.get('name') for s in supporting_services]
    }


if __name__ == '__main__':
    # Test the module
    state = load_world_state()
    print("Current world state:")
    print(f"  Tick: {state['tick']}")
    print(f"  Agents: {len(state.get('agents', []))}")
    print(f"  Regions: {len(state.get('regions', []))}")
    print(f"  Total Ideas: {state['metrics']['total_ideas']}")
    
    # Test infrastructure functions
    infra_regions = get_infrastructure_regions(state)
    print(f"\n  Infrastructure Regions: {len(infra_regions)}")
    for region in infra_regions:
        summary = get_infrastructure_region_summary(state, region['id'])
        if summary:
            print(f"    - {region['id']}: {summary['total_services']} services")
