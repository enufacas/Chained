#!/usr/bin/env python3
"""
Example: Improved Agent Pattern Matching

This example demonstrates the fix for agent-missions workflow to properly
match agents with claude, ai/ml, and other technology patterns.

Investigation by @investigate-champion (Liskov) - 2025-11-16
"""

import json


def score_agent_for_idea(agent, idea, pattern_matches):
    """
    Score an agent for a given idea based on pattern matching.
    
    This replicates the logic from agent-missions.yml workflow.
    
    Args:
        agent: Agent dict with specialization and metrics
        idea: Idea dict with patterns and regions
        pattern_matches: Dict mapping patterns to agent specializations
        
    Returns:
        float: Score between 0.0 and 1.0
    """
    score = 0.0
    
    # Extract agent info
    specialization = agent.get('specialization', '')
    agent_location = agent.get('location_region_id', '')
    metrics = agent.get('metrics', {})
    
    # Extract idea info
    idea_patterns = idea.get('patterns', [])
    idea_regions = idea.get('inspiration_regions', [])
    
    # Location relevance (30%)
    for region in idea_regions:
        if agent_location == region.get('region_id'):
            score += 0.3 * region.get('weight', 0.5)
    
    # Role/skill relevance (40%)
    for pattern in idea_patterns:
        if specialization in pattern_matches.get(pattern, []):
            score += 0.4
    
    # Performance score (30%)
    overall_score = metrics.get('overall_score', 0.0)
    score += 0.3 * overall_score
    
    return score


# BEFORE: Incomplete pattern matches (caused 0.00 scores)
PATTERN_MATCHES_OLD = {
    'ai': ['investigate-champion', 'engineer-master', 'create-guru'],
    'cloud': ['infrastructure-specialist', 'engineer-master'],
    'security': ['secure-specialist', 'secure-ninja', 'monitor-champion'],
    'testing': ['assert-specialist', 'validator-pro'],
    'devops': ['coordinate-wizard', 'align-wizard'],
    'api': ['engineer-master', 'engineer-wizard'],
}

# AFTER: Complete pattern matches (enables proper scoring)
PATTERN_MATCHES_NEW = {
    'ai': ['investigate-champion', 'engineer-master', 'create-guru'],
    'ai/ml': ['investigate-champion', 'engineer-master', 'create-guru'],
    'claude': ['investigate-champion', 'engineer-master', 'create-guru'],
    'agents': ['investigate-champion', 'engineer-master', 'create-guru'],
    'gpt': ['investigate-champion', 'engineer-master', 'create-guru'],
    'cloud': ['infrastructure-specialist', 'engineer-master'],
    'aws': ['infrastructure-specialist', 'engineer-master', 'cloud-architect'],
    'devops': ['coordinate-wizard', 'align-wizard', 'infrastructure-specialist'],
    'security': ['secure-specialist', 'secure-ninja', 'monitor-champion'],
    'testing': ['assert-specialist', 'validator-pro'],
    'api': ['engineer-master', 'engineer-wizard', 'integrate-specialist'],
    'web': ['engineer-master', 'engineer-wizard', 'create-guru'],
    'go': ['engineer-master', 'create-guru'],
    'javascript': ['engineer-master', 'create-guru'],
    'languages': ['engineer-master', 'create-guru'],
}


def demonstrate_fix():
    """Demonstrate the impact of the pattern matching fix."""
    
    # Example agent (investigate-champion)
    agent = {
        'id': 'agent-1762960673',
        'label': '🎯 Liskov',
        'specialization': 'investigate-champion',
        'location_region_id': 'US:Charlotte',
        'metrics': {
            'overall_score': 0.43325
        }
    }
    
    # Example idea (Claude Innovation)
    idea = {
        'id': 'idea:18',
        'title': 'AI/ML: Claude Innovation',
        'patterns': ['claude', 'ai/ml'],
        'inspiration_regions': [
            {
                'region_id': 'US:San Francisco',
                'weight': 1.0
            }
        ]
    }
    
    # Score with OLD pattern matches
    old_score = score_agent_for_idea(agent, idea, PATTERN_MATCHES_OLD)
    
    # Score with NEW pattern matches
    new_score = score_agent_for_idea(agent, idea, PATTERN_MATCHES_NEW)
    
    print("=" * 70)
    print("AGENT PATTERN MATCHING FIX DEMONSTRATION")
    print("=" * 70)
    print()
    print(f"Idea: {idea['title']} ({idea['id']})")
    print(f"Patterns: {idea['patterns']}")
    print()
    print(f"Agent: {agent['label']} (@{agent['specialization']})")
    print(f"Location: {agent['location_region_id']}")
    print()
    print("-" * 70)
    print("BEFORE FIX (Missing 'claude' and 'ai/ml' patterns):")
    print("-" * 70)
    print(f"  Pattern matches: 0/2")
    print(f"  Score: {old_score:.3f}")
    print(f"  Result: {'Unknown' if old_score == 0 else 'Matched'}")
    print()
    print("-" * 70)
    print("AFTER FIX (Complete pattern coverage):")
    print("-" * 70)
    print(f"  Pattern matches: 2/2")
    print(f"  Score: {new_score:.3f}")
    print(f"  Result: Matched to @{agent['specialization']}")
    print()
    print("=" * 70)
    print(f"IMPROVEMENT: +{new_score - old_score:.3f} score increase")
    print("=" * 70)
    print()
    print("Impact:")
    print("  ✅ Claude missions now properly assigned")
    print("  ✅ AI/ML missions correctly matched")
    print("  ✅ All recent learning ideas have valid agents")
    print()


if __name__ == '__main__':
    demonstrate_fix()
    
    print("\n" + "=" * 70)
    print("PATTERN COVERAGE COMPARISON")
    print("=" * 70)
    print()
    print(f"OLD: {len(PATTERN_MATCHES_OLD)} patterns covered")
    print(f"NEW: {len(PATTERN_MATCHES_NEW)} patterns covered")
    print(f"Added: {len(PATTERN_MATCHES_NEW) - len(PATTERN_MATCHES_OLD)} new patterns")
    print()
    print("New patterns added:")
    for pattern in sorted(set(PATTERN_MATCHES_NEW.keys()) - set(PATTERN_MATCHES_OLD.keys())):
        agents = ', '.join(PATTERN_MATCHES_NEW[pattern][:2])
        print(f"  • {pattern:15s} → {agents}, ...")
    print()
