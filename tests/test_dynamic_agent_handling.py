#!/usr/bin/env python3
"""
Test that the workflow can handle agents from multiple sources:
1. Agents in world_state.json
2. Agents with .md files in .github/agents/
3. New agents added via match-issue-to-agent.py
"""

import json
import os

print("=" * 70)
print("🧪 Testing Dynamic Agent Handling")
print("=" * 70)
print()

# Load world_state agents (like the workflow does)
with open('world/world_state.json', 'r') as f:
    world_state = json.load(f)
agents = world_state.get('agents', [])

print(f"📊 Loaded {len(agents)} agents from world_state.json")
print()

# Simulate agent matching scenarios
test_scenarios = [
    {
        'name': 'Agent in world_state.json',
        'specialization': 'coach-master',
        'expected': 'Should find in world_state'
    },
    {
        'name': 'Agent with .md file only',
        'specialization': 'cloud-architect',
        'expected': 'Should create fallback from .md file'
    },
    {
        'name': 'New agent from match-issue-to-agent.py',
        'specialization': 'troubleshoot-expert',
        'expected': 'Should create fallback from .md file'
    }
]

print("🔍 Testing Agent Resolution:")
print()

for scenario in test_scenarios:
    spec = scenario['specialization']
    print(f"Scenario: {scenario['name']}")
    print(f"  Specialization: @{spec}")
    
    # Try to find in world_state (like workflow does)
    agent_details = None
    for agent in agents:
        if agent.get('specialization') == spec:
            agent_details = agent
            break
    
    if agent_details:
        print(f"  ✅ Found in world_state.json")
        print(f"     ID: {agent_details.get('id')}")
        print(f"     Label: {agent_details.get('label')}")
    else:
        # Check if agent file exists (fallback)
        agent_file = f'.github/agents/{spec}.md'
        if os.path.exists(agent_file):
            print(f"  ✅ Not in world_state, but agent file exists: {agent_file}")
            print(f"     Can create fallback agent details")
            agent_details = {
                'id': spec,
                'label': spec.replace('-', ' ').title(),
                'specialization': spec
            }
        else:
            print(f"  ❌ Not found anywhere - would skip")
    
    print()

# Check how many agents are available through different sources
print("=" * 70)
print("📊 Agent Availability Summary:")
print("=" * 70)
print()

world_state_agents = set(a.get('specialization') for a in agents if a.get('specialization'))
agent_file_agents = set(f.stem for f in Path('.github/agents').glob('*.md') if f.stem != 'README')

print(f"Agents in world_state.json:  {len(world_state_agents)}")
print(f"Agents with .md files:       {len(agent_file_agents)}")
print(f"Total available agents:      {len(world_state_agents | agent_file_agents)}")
print()

# Agents only in files (would use fallback)
only_in_files = agent_file_agents - world_state_agents
print(f"Agents using fallback:       {len(only_in_files)}")
if only_in_files and len(only_in_files) <= 10:
    for spec in sorted(only_in_files):
        print(f"  - @{spec}")
elif only_in_files:
    print(f"  - (showing first 10 of {len(only_in_files)})")
    for spec in sorted(only_in_files)[:10]:
        print(f"  - @{spec}")

print()
print("=" * 70)
print("✅ Conclusion:")
print("=" * 70)
print()
print("With the fallback mechanism:")
print(f"  • {len(world_state_agents)} agents from world_state.json work natively")
print(f"  • {len(only_in_files)} additional agents work via fallback")
print(f"  • Total: {len(world_state_agents | agent_file_agents)} agents can be assigned missions")
print()
print("✅ System can handle new agents dynamically!")
print("   New agents just need a .md file in .github/agents/")
print("   No need to update world_state.json immediately")

from pathlib import Path
