#!/usr/bin/env python3
"""
Verify that all agents are candidates and the system dynamically handles new agents.
"""

import json
import os
import subprocess
from pathlib import Path

print("=" * 70)
print("🔍 Agent Sourcing Verification")
print("=" * 70)
print()

# 1. Check world_state.json agents
print("1️⃣  Checking world_state.json...")
with open('world/world_state.json', 'r') as f:
    world_state = json.load(f)

world_agents = world_state.get('agents', [])
print(f"   Found {len(world_agents)} agents in world_state.json")

# 2. Check .github/agents/ directory
print()
print("2️⃣  Checking .github/agents/ directory...")
agents_dir = Path('.github/agents')
agent_files = list(agents_dir.glob('*.md'))
print(f"   Found {len(agent_files)} agent files")

# 3. Check agent registry
print()
print("3️⃣  Checking agent registry...")
registry_file = Path('.github/agent-system/registry.json')
if registry_file.exists():
    with open(registry_file, 'r') as f:
        registry = json.load(f)
    registry_agents = registry.get('agents', [])
    print(f"   Found {len(registry_agents)} agents in registry")
else:
    print("   ⚠️  Registry file not found")
    registry_agents = []

# 4. Check tools/match-issue-to-agent.py agent definitions
print()
print("4️⃣  Checking match-issue-to-agent.py agent patterns...")
with open('tools/match-issue-to-agent.py', 'r') as f:
    content = f.read()
    # Count agent specializations in the SPECIALIZATIONS dict
    import re
    spec_matches = re.findall(r'"([a-z-]+)":\s*{', content)
    print(f"   Found {len(spec_matches)} agent specializations in match-issue-to-agent.py")

# 5. Test match-issue-to-agent.py returns all agents
print()
print("5️⃣  Testing match-issue-to-agent.py returns all agent scores...")
result = subprocess.run(
    ['python3', 'tools/match-issue-to-agent.py', 'test issue about cloud performance'],
    capture_output=True,
    text=True
)
match_data = json.loads(result.stdout)
all_scores = match_data.get('all_scores', {})
print(f"   match-issue-to-agent.py returns scores for {len(all_scores)} agents")

# 6. Compare sources
print()
print("=" * 70)
print("📊 Comparison:")
print("=" * 70)
print()

# Extract agent IDs/specializations from each source
world_specs = set(agent.get('specialization', agent.get('id', '')) for agent in world_agents)
file_specs = set(f.stem for f in agent_files)
registry_specs = set(agent.get('id', '') for agent in registry_agents) if registry_agents else set()
matcher_specs = set(all_scores.keys())

print(f"world_state.json:          {len(world_specs)} agents")
print(f".github/agents/ files:     {len(file_specs)} agents")
print(f"registry.json:             {len(registry_specs)} agents")
print(f"match-issue-to-agent.py:   {len(matcher_specs)} agents")
print()

# Find discrepancies
print("🔍 Checking for discrepancies...")
print()

# Agents in world_state but not in matcher
missing_in_matcher = world_specs - matcher_specs
if missing_in_matcher:
    print(f"❌ {len(missing_in_matcher)} agents in world_state but NOT in match-issue-to-agent.py:")
    for spec in sorted(missing_in_matcher):
        print(f"   - {spec}")
    print()
else:
    print("✅ All world_state agents are in match-issue-to-agent.py")
    print()

# Agents in matcher but not in world_state
extra_in_matcher = matcher_specs - world_specs
if extra_in_matcher:
    print(f"ℹ️  {len(extra_in_matcher)} agents in match-issue-to-agent.py but NOT in world_state:")
    for spec in sorted(extra_in_matcher):
        print(f"   - {spec}")
    print()

# Agents in files but not in world_state
missing_in_world = file_specs - world_specs
if missing_in_world:
    print(f"⚠️  {len(missing_in_world)} agent files exist but NOT in world_state:")
    for spec in sorted(missing_in_world):
        print(f"   - {spec}")
    print()

# 7. Test dynamic agent handling
print("=" * 70)
print("🧪 Testing Dynamic Agent Handling")
print("=" * 70)
print()

print("Testing if autonomous-pipeline correctly sources agents from world_state.json...")
print()

# Check the workflow code
with open('.github/workflows/autonomous-pipeline.yml', 'r') as f:
    workflow_content = f.read()

# Look for world_state loading
if 'world/world_state.json' in workflow_content:
    print("✅ Workflow loads from world/world_state.json")
else:
    print("❌ Workflow does NOT load from world/world_state.json")

# Look for agent iteration
if 'for agent in agents:' in workflow_content:
    print("✅ Workflow iterates through agents dynamically")
else:
    print("❌ Workflow does NOT iterate through agents")

# Check if it uses match-issue-to-agent.py
if 'tools/match-issue-to-agent.py' in workflow_content:
    print("✅ Workflow uses match-issue-to-agent.py for matching")
else:
    print("❌ Workflow does NOT use match-issue-to-agent.py")

print()

# 8. Verify all agents are candidates
print("=" * 70)
print("✅ Verification Summary")
print("=" * 70)
print()

all_verified = True

if missing_in_matcher:
    print("❌ FAIL: Some agents in world_state are not candidates in match-issue-to-agent.py")
    all_verified = False
else:
    print("✅ PASS: All world_state agents are candidates in match-issue-to-agent.py")

if 'world/world_state.json' in workflow_content and 'for agent in agents:' in workflow_content:
    print("✅ PASS: Workflow dynamically sources agents from world_state.json")
else:
    print("❌ FAIL: Workflow does not dynamically source agents correctly")
    all_verified = False

if 'tools/match-issue-to-agent.py' in workflow_content:
    print("✅ PASS: Workflow uses comprehensive matching tool")
else:
    print("❌ FAIL: Workflow does not use matching tool")
    all_verified = False

print()

if all_verified:
    print("🎉 All verifications passed! System can handle new agents dynamically.")
    exit(0)
else:
    print("⚠️  Some verifications failed. See details above.")
    exit(1)
