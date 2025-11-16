#!/usr/bin/env python3
"""
Test that agent mission assignments correctly update the world state.
"""

import json
import sys
import os
from datetime import datetime

# Add world to path
sys.path.insert(0, 'world')
from world_state_manager import (
    load_world_state, 
    save_world_state, 
    update_agent_mission,
    clear_agent_mission,
    get_agent_by_id
)

print("=" * 70)
print("🧪 Testing World State Agent Mission Updates")
print("=" * 70)
print()

# Load current world state
world_state = load_world_state()
original_tick = world_state.get('tick', 0)
agents = world_state.get('agents', [])

print(f"📊 Current World State:")
print(f"   Tick: {original_tick}")
print(f"   Agents: {len(agents)}")
print()

if len(agents) == 0:
    print("⚠️  No agents in world state, skipping test")
    sys.exit(0)

# Test 1: Update agent with mission by ID
print("Test 1: Update Agent by ID")
print("-" * 70)

test_agent = agents[0]
agent_id = test_agent.get('id')
agent_spec = test_agent.get('specialization')

print(f"Agent: {test_agent.get('label', 'Unknown')} (@{agent_spec})")
print(f"ID: {agent_id}")
print(f"Current status: {test_agent.get('status', 'unknown')}")
print()

# Update with a test mission
success = update_agent_mission(
    world_state,
    agent_id,
    "test-mission-001",
    "Test Mission: Cloud Security Implementation",
    issue_number=9999
)

if success:
    print("✅ Agent updated successfully")
    updated_agent = get_agent_by_id(world_state, agent_id)
    print(f"   New status: {updated_agent.get('status')}")
    print(f"   Current mission: {updated_agent.get('current_mission', {}).get('title')}")
    print(f"   Issue number: {updated_agent.get('current_mission', {}).get('issue_number')}")
else:
    print("❌ Failed to update agent")

print()

# Test 2: Update agent with mission by specialization
print("Test 2: Update Agent by Specialization")
print("-" * 70)

# Find an agent with different specialization
test_agent2 = None
for agent in agents:
    if agent.get('id') != agent_id:
        test_agent2 = agent
        break

if test_agent2:
    agent_spec2 = test_agent2.get('specialization')
    print(f"Agent: {test_agent2.get('label', 'Unknown')} (@{agent_spec2})")
    
    success = update_agent_mission(
        world_state,
        agent_spec2,  # Using specialization instead of ID
        "test-mission-002",
        "Test Mission: API Testing Framework",
        issue_number=10000
    )
    
    if success:
        print("✅ Agent updated by specialization successfully")
    else:
        print("❌ Failed to update agent by specialization")
else:
    print("ℹ️  Only one agent available, skipping specialization test")

print()

# Test 3: Update agent not in world_state (fallback scenario)
print("Test 3: Update Agent Not in World State (Fallback)")
print("-" * 70)

success = update_agent_mission(
    world_state,
    "cloud-architect",  # Agent likely not in world_state
    "test-mission-003",
    "Test Mission: Kubernetes Deployment",
    issue_number=10001
)

if success:
    print("✅ Fallback agent found and updated")
else:
    print("ℹ️  Agent 'cloud-architect' not in world_state (expected for fallback agents)")

print()

# Test 4: Clear agent mission
print("Test 4: Clear Agent Mission")
print("-" * 70)

success = clear_agent_mission(world_state, agent_id)

if success:
    print("✅ Agent mission cleared successfully")
    cleared_agent = get_agent_by_id(world_state, agent_id)
    print(f"   Status: {cleared_agent.get('status')}")
    print(f"   Has mission: {'current_mission' in cleared_agent}")
else:
    print("❌ Failed to clear agent mission")

print()

# Test 5: Simulate full workflow
print("Test 5: Simulate Full Workflow")
print("-" * 70)

# Create mock missions like autonomous-pipeline would
mock_missions = [
    {
        'idea_id': 'idea:test-1',
        'idea_title': 'Implement Cloud Monitoring',
        'agent': {
            'agent_id': agents[0].get('id'),
            'specialization': agents[0].get('specialization'),
            'agent_name': agents[0].get('label')
        }
    }
]

if len(agents) > 1:
    mock_missions.append({
        'idea_id': 'idea:test-2',
        'idea_title': 'Add Testing Coverage',
        'agent': {
            'agent_id': agents[1].get('id'),
            'specialization': agents[1].get('specialization'),
            'agent_name': agents[1].get('label')
        }
    })

print(f"Simulating {len(mock_missions)} mission assignments...")
print()

updated_count = 0
for mission in mock_missions:
    agent = mission['agent']
    agent_spec = agent.get('specialization')
    agent_id = agent.get('agent_id')
    
    success = update_agent_mission(
        world_state,
        agent_id,
        mission['idea_id'],
        mission['idea_title'],
        None  # No issue number in simulation
    )
    
    if success:
        updated_count += 1
        print(f"✅ @{agent_spec}: {mission['idea_title']}")

print()
print(f"Summary: {updated_count}/{len(mock_missions)} agents updated")

# Update world tick like workflow does
world_state['tick'] = world_state.get('tick', 0) + 1
world_state['time'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

if 'metrics' not in world_state:
    world_state['metrics'] = {}
world_state['metrics']['active_missions'] = len(mock_missions)

print()
print("=" * 70)
print("📊 Final World State Summary")
print("=" * 70)
print()
print(f"   Tick: {original_tick} → {world_state['tick']}")
print(f"   Active missions: {world_state['metrics'].get('active_missions', 0)}")
print()

# Count agents with missions
agents_with_missions = sum(1 for a in world_state['agents'] if 'current_mission' in a)
print(f"   Agents with missions: {agents_with_missions}/{len(agents)}")

print()

# Don't save to avoid modifying actual world state during testing
# save_world_state(world_state)
print("ℹ️  Test complete (world_state.json not modified)")
print()

if updated_count >= len(mock_missions) * 0.8:  # 80% success rate
    print("✅ PASS: World state updates working correctly!")
    sys.exit(0)
else:
    print("❌ FAIL: Too many agents failed to update")
    sys.exit(1)
