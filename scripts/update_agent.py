#!/usr/bin/env python3
"""
Agent Update Script
Updates agent state in the world model, moving agents along their paths.
"""

import sys
import os
import json

# Add world directory to path
WORLD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'world')
sys.path.insert(0, WORLD_DIR)

from world_state_manager import (
    load_world_state, save_world_state, get_agent_by_id,
    get_all_agents, increment_tick
)
from knowledge_manager import load_knowledge, get_all_ideas
from agent_navigator import (
    move_agent_one_step, assign_idea_to_agent,
    select_next_idea_for_agent, get_agent_status_summary
)


def update_single_agent(agent: dict, ideas: list) -> dict:
    """
    Update a single agent's state.
    
    Returns:
        Dict with update status and details
    """
    agent_id = agent.get('id')
    original_location = agent.get('location_region_id')
    
    # If agent has no current idea, assign one
    if not agent.get('current_idea_id'):
        if ideas:
            selected_idea = select_next_idea_for_agent(agent, ideas, strategy='random')
            if selected_idea:
                assign_idea_to_agent(agent, selected_idea)
                return {
                    'agent_id': agent_id,
                    'action': 'assigned_idea',
                    'idea_id': selected_idea.get('id'),
                    'path_length': len(agent.get('path', []))
                }
        else:
            return {
                'agent_id': agent_id,
                'action': 'idle',
                'reason': 'no_ideas_available'
            }
    
    # If agent has a path, move one step
    if agent.get('path'):
        new_location = move_agent_one_step(agent)
        if new_location:
            return {
                'agent_id': agent_id,
                'action': 'moved',
                'from': original_location,
                'to': new_location,
                'remaining_path': len(agent.get('path', []))
            }
    
    # If path is complete and agent has idea, clear it for next assignment
    if agent.get('current_idea_id') and not agent.get('path'):
        agent['current_idea_id'] = None
        agent['status'] = 'idle'
        return {
            'agent_id': agent_id,
            'action': 'completed_exploration',
            'ready_for_new_idea': True
        }
    
    return {
        'agent_id': agent_id,
        'action': 'no_change',
        'status': agent.get('status')
    }


def update_all_agents() -> dict:
    """
    Update all agents in the world state.
    
    Returns:
        Summary of all updates
    """
    print("🌍 Loading world state...")
    world_state = load_world_state()
    
    print("📚 Loading knowledge base...")
    knowledge = load_knowledge()
    ideas = get_all_ideas(knowledge)
    
    print(f"🤖 Found {len(world_state.get('agents', []))} agents")
    print(f"💡 Found {len(ideas)} ideas")
    
    # Increment tick
    new_tick = increment_tick(world_state)
    print(f"⏰ Tick: {new_tick}")
    
    updates = []
    agents = get_all_agents(world_state)
    
    for agent in agents:
        print(f"\n📍 Updating agent: {agent.get('id')}")
        print(f"   Before: {get_agent_status_summary(agent)}")
        
        update_result = update_single_agent(agent, ideas)
        updates.append(update_result)
        
        print(f"   Action: {update_result.get('action')}")
        print(f"   After: {get_agent_status_summary(agent)}")
    
    # Save updated world state
    print("\n💾 Saving world state...")
    save_world_state(world_state)
    
    return {
        'tick': new_tick,
        'agents_updated': len(agents),
        'updates': updates,
        'timestamp': world_state.get('time')
    }


def main():
    print("=" * 60)
    print("🚀 Chained World Model - Agent Update")
    print("=" * 60)
    
    try:
        summary = update_all_agents()
        
        print("\n" + "=" * 60)
        print("✅ Update Complete!")
        print("=" * 60)
        print(f"Tick: {summary['tick']}")
        print(f"Agents updated: {summary['agents_updated']}")
        print(f"Timestamp: {summary['timestamp']}")
        
        # Show action summary
        action_counts = {}
        for update in summary['updates']:
            action = update.get('action')
            action_counts[action] = action_counts.get(action, 0) + 1
        
        print("\nAction Summary:")
        for action, count in action_counts.items():
            print(f"  {action}: {count}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during update: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
