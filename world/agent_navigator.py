#!/usr/bin/env python3
"""
Agent Navigator
Handles agent movement and navigation through inspiration regions.
"""

import random
from typing import Dict, List, Optional, Any


def build_navigation_path(inspiration_regions: List[Dict[str, Any]]) -> List[str]:
    """
    Build a navigation path from inspiration regions.
    Currently uses simple weight-based ordering.
    
    Args:
        inspiration_regions: List of region dicts with region_id, lat, lng, weight
    
    Returns:
        List of region IDs in navigation order
    """
    if not inspiration_regions:
        return []
    
    # Sort by weight (highest first)
    sorted_regions = sorted(
        inspiration_regions,
        key=lambda r: r.get('weight', 0),
        reverse=True
    )
    
    return [r['region_id'] for r in sorted_regions]


def move_agent_one_step(agent: Dict[str, Any]) -> Optional[str]:
    """
    Move agent one step along its path.
    Returns the new location or None if path is complete.
    
    Args:
        agent: Agent dict with path and location_region_id
    
    Returns:
        New location region_id or None if no more moves
    """
    path = agent.get('path', [])
    if not path:
        return None
    
    # Get next location in path
    next_location = path[0]
    
    # Remove from path
    agent['path'] = path[1:]
    
    # Update agent location
    agent['location_region_id'] = next_location
    
    # Update status
    if not agent['path']:
        agent['status'] = 'idle'
    else:
        agent['status'] = 'traveling'
    
    return next_location


def assign_idea_to_agent(
    agent: Dict[str, Any],
    idea: Dict[str, Any]
) -> None:
    """
    Assign an idea to an agent and set up navigation path.
    
    Args:
        agent: Agent dict to update
        idea: Idea dict with inspiration_regions
    """
    agent['current_idea_id'] = idea.get('id')
    agent['status'] = 'exploring'
    
    # Build navigation path from inspiration regions
    inspiration_regions = idea.get('inspiration_regions', [])
    path = build_navigation_path(inspiration_regions)
    agent['path'] = path


def select_next_idea_for_agent(
    agent: Dict[str, Any],
    ideas: List[Dict[str, Any]],
    strategy: str = 'random'
) -> Optional[Dict[str, Any]]:
    """
    Select the next idea for an agent.
    
    Args:
        agent: Agent dict
        ideas: List of available ideas
        strategy: Selection strategy ('random', 'nearest', 'most_patterns')
    
    Returns:
        Selected idea or None if no ideas available
    """
    if not ideas:
        return None
    
    if strategy == 'random':
        return random.choice(ideas)
    
    elif strategy == 'most_patterns':
        # Select idea with most patterns
        return max(ideas, key=lambda i: len(i.get('patterns', [])))
    
    elif strategy == 'nearest':
        # Select idea with region nearest to current location
        current_location = agent.get('location_region_id')
        if not current_location:
            return random.choice(ideas)
        
        # Find idea with current location in inspiration regions
        for idea in ideas:
            for region in idea.get('inspiration_regions', []):
                if region.get('region_id') == current_location:
                    return idea
        
        # Fallback to random
        return random.choice(ideas)
    
    return random.choice(ideas)


def get_agent_status_summary(agent: Dict[str, Any]) -> str:
    """Get a human-readable status summary for an agent."""
    status = agent.get('status', 'unknown')
    location = agent.get('location_region_id', 'unknown')
    path_len = len(agent.get('path', []))
    idea_id = agent.get('current_idea_id')
    
    parts = [f"Status: {status}", f"Location: {location}"]
    
    if idea_id:
        parts.append(f"Exploring: {idea_id}")
    
    if path_len > 0:
        parts.append(f"Path remaining: {path_len} stops")
    
    return " | ".join(parts)


if __name__ == '__main__':
    # Test the module
    test_regions = [
        {'region_id': 'US:San Francisco', 'lat': 37.7749, 'lng': -122.4194, 'weight': 0.6},
        {'region_id': 'TW:Hsinchu', 'lat': 24.8138, 'lng': 120.9675, 'weight': 0.4}
    ]
    
    path = build_navigation_path(test_regions)
    print(f"Navigation path: {path}")
    
    test_agent = {
        'id': 'test-1',
        'location_region_id': 'US:Seattle',
        'path': path.copy(),
        'status': 'traveling'
    }
    
    print(f"Agent before move: {get_agent_status_summary(test_agent)}")
    move_agent_one_step(test_agent)
    print(f"Agent after move: {get_agent_status_summary(test_agent)}")
