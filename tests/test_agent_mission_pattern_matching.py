#!/usr/bin/env python3
"""
Comprehensive test suite for agent-missions pattern matching.
Tests that all patterns correctly match to existing agents.
"""

import json
import sys

# Pattern matching from updated workflow
# NOTE: Only lists agents that actually exist in registry/world_state
PATTERN_MATCHES = {
    'ai': ['investigate-champion', 'engineer-master'],
    'ai/ml': ['investigate-champion', 'engineer-master'],
    'claude': ['investigate-champion', 'engineer-master'],
    'agents': ['investigate-champion', 'engineer-master'],
    'gpt': ['investigate-champion', 'engineer-master'],
    'cloud': ['investigate-champion', 'engineer-master', 'construct-specialist'],
    'aws': ['investigate-champion', 'engineer-master', 'construct-specialist'],
    'devops': ['investigate-champion', 'engineer-master', 'construct-specialist'],
    'security': ['secure-ninja', 'investigate-champion'],
    'testing': ['assert-specialist', 'investigate-champion'],
    'api': ['engineer-master', 'investigate-champion', 'construct-specialist'],
    'web': ['engineer-master', 'investigate-champion', 'construct-specialist'],
    'go': ['engineer-master', 'investigate-champion'],
    'javascript': ['engineer-master', 'investigate-champion'],
    'languages': ['engineer-master', 'investigate-champion'],
}

# Load actual agents from world_state
try:
    with open('world/world_state.json', 'r') as f:
        world_state = json.load(f)
    EXISTING_AGENTS = set(agent['specialization'] for agent in world_state.get('agents', []))
except FileNotFoundError:
    print("⚠️  Could not load world/world_state.json, using fallback agent list")
    EXISTING_AGENTS = {
        'organize-guru', 'assert-specialist', 'coach-master', 'investigate-champion',
        'secure-ninja', 'construct-specialist', 'engineer-master', 'support-master',
        'steam-machine', 'restructure-master'
    }

# Test scenarios
TEST_SCENARIOS = [
    {
        'name': 'DevOps: Cloud Innovation (Original Issue)',
        'patterns': ['cloud', 'devops'],
        'expected_match': True,
        'expected_agents': ['investigate-champion', 'engineer-master', 'construct-specialist'],
    },
    {
        'name': 'AI/ML Innovation',
        'patterns': ['ai', 'ai/ml'],
        'expected_match': True,
        'expected_agents': ['investigate-champion', 'engineer-master'],
    },
    {
        'name': 'Security Vulnerability',
        'patterns': ['security'],
        'expected_match': True,
        'expected_agents': ['secure-ninja', 'investigate-champion'],
    },
    {
        'name': 'Testing Framework',
        'patterns': ['testing'],
        'expected_match': True,
        'expected_agents': ['assert-specialist', 'investigate-champion'],
    },
    {
        'name': 'API Development',
        'patterns': ['api'],
        'expected_match': True,
        'expected_agents': ['engineer-master', 'investigate-champion', 'construct-specialist'],
    },
    {
        'name': 'Web Application',
        'patterns': ['web', 'javascript'],
        'expected_match': True,
        'expected_agents': ['engineer-master', 'investigate-champion'],
    },
    {
        'name': 'Cloud Architecture',
        'patterns': ['cloud', 'aws'],
        'expected_match': True,
        'expected_agents': ['investigate-champion', 'engineer-master', 'construct-specialist'],
    },
]

def get_matching_agents(patterns):
    """Get all agents that match any of the given patterns."""
    matching = set()
    for pattern in patterns:
        agents = PATTERN_MATCHES.get(pattern, [])
        matching.update(agents)
    return matching

def test_pattern_matching():
    """Run all test scenarios."""
    print("=" * 70)
    print("🧪 Testing Agent Mission Pattern Matching")
    print("=" * 70)
    print(f"\nExisting agents in world_state: {len(EXISTING_AGENTS)}")
    print(f"Agents: {', '.join(sorted(EXISTING_AGENTS))}")
    print()
    
    passed = 0
    failed = 0
    warnings = 0
    
    # Test 1: Validate all referenced agents exist
    print("=" * 70)
    print("Test 1: Validating Pattern Match References")
    print("=" * 70)
    
    all_referenced = set()
    for pattern, agents in PATTERN_MATCHES.items():
        all_referenced.update(agents)
    
    missing_agents = all_referenced - EXISTING_AGENTS
    
    if missing_agents:
        print(f"⚠️  WARNING: {len(missing_agents)} referenced agents don't exist in world_state:")
        for agent in sorted(missing_agents):
            print(f"   - {agent}")
            # Check which patterns reference this missing agent
            patterns_with_agent = [p for p, a in PATTERN_MATCHES.items() if agent in a]
            print(f"     Used in patterns: {', '.join(patterns_with_agent)}")
        warnings += 1
    else:
        print("✅ All referenced agents exist in world_state")
        passed += 1
    
    print()
    
    # Test 2: Run scenarios
    print("=" * 70)
    print("Test 2: Mission Matching Scenarios")
    print("=" * 70)
    print()
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"Scenario {i}: {scenario['name']}")
        print(f"  Patterns: {', '.join(scenario['patterns'])}")
        
        matching_agents = get_matching_agents(scenario['patterns'])
        existing_matches = matching_agents & EXISTING_AGENTS
        
        if existing_matches:
            print(f"  ✅ Matches found: {', '.join(sorted(existing_matches))}")
            
            # Check if expected agents are in matches
            expected = scenario.get('expected_agents', [])
            if expected:
                expected_found = [a for a in expected if a in existing_matches]
                if expected_found:
                    print(f"  ✓ Expected agents present: {', '.join(expected_found)}")
                    passed += 1
                else:
                    print(f"  ⚠️  Expected agents not found: {', '.join(expected)}")
                    failed += 1
            else:
                passed += 1
        else:
            print(f"  ❌ NO MATCHES found (score would be 0.00)")
            print(f"  Referenced agents: {', '.join(matching_agents)}")
            failed += 1
        
        print()
    
    # Test 3: Specific fix validation
    print("=" * 70)
    print("Test 3: Validating Original Issue Fix")
    print("=" * 70)
    
    cloud_devops_matches = get_matching_agents(['cloud', 'devops']) & EXISTING_AGENTS
    
    if cloud_devops_matches:
        print(f"✅ Cloud/DevOps missions will match to: {', '.join(sorted(cloud_devops_matches))}")
        if 'investigate-champion' in cloud_devops_matches:
            print(f"✓ @investigate-champion is included (perfect for innovation exploration)")
            passed += 1
        else:
            print(f"⚠️  @investigate-champion not in cloud/devops matches")
            warnings += 1
    else:
        print("❌ Cloud/DevOps missions still have no matches!")
        failed += 1
    
    print()
    
    # Summary
    print("=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Warnings: {warnings}")
    print()
    
    if failed == 0:
        print("🎉 All critical tests passed!")
        if warnings > 0:
            print(f"⚠️  But {warnings} warning(s) found - check agents referenced in patterns")
        return 0 if warnings == 0 else 1
    else:
        print(f"💥 {failed} test(s) failed")
        return 1

def main():
    """Main entry point."""
    return test_pattern_matching()

if __name__ == '__main__':
    sys.exit(main())
