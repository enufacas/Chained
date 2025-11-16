#!/usr/bin/env python3
"""
Test script to validate the improved mission matching logic
"""

import json
import random
import hashlib
from datetime import datetime, timezone

# Simulate loading world state and knowledge
def load_test_data():
    agents = [
        {'id': 'agent-1', 'label': '🧹 Robert Martin', 'specialization': 'organize-guru', 'metrics': {'overall_score': 0.43}},
        {'id': 'agent-2', 'label': '🧪 Tesla', 'specialization': 'assert-specialist', 'metrics': {'overall_score': 0.43}},
        {'id': 'agent-3', 'label': '💭 Turing', 'specialization': 'coach-master', 'metrics': {'overall_score': 0.43}},
        {'id': 'agent-4', 'label': '🔒 Schneier', 'specialization': 'secure-specialist', 'metrics': {'overall_score': 0.45}},
        {'id': 'agent-5', 'label': '☁️ Cloud Expert', 'specialization': 'cloud-architect', 'metrics': {'overall_score': 0.48}},
    ]
    
    ideas = [
        {
            'id': 'idea:1',
            'title': 'Cloud Security Best Practices',
            'summary': 'Exploring cloud security with 25 mentions...',
            'patterns': ['cloud', 'security', 'devops'],
            'source': 'learning_analysis',
            'inspiration_regions': [{'region_id': 'US:Seattle'}]
        },
        {
            'id': 'idea:2', 
            'title': 'Testing Frameworks Comparison',
            'summary': 'Comparing modern testing frameworks...',
            'patterns': ['testing', 'coverage', 'api'],
            'source': 'learning_analysis',
            'inspiration_regions': [{'region_id': 'US:San Francisco'}]
        },
        {
            'id': 'idea:3',
            'title': 'Code Review Best Practices',
            'summary': 'Best practices for effective code reviews...',
            'patterns': ['review', 'refactor', 'clean'],
            'source': 'learning_analysis',
            'inspiration_regions': [{'region_id': 'GB:London'}]
        },
        {
            'id': 'idea:4',
            'title': 'Performance Optimization Techniques',
            'summary': 'Advanced performance optimization strategies...',
            'patterns': ['performance', 'optimize'],
            'source': 'learning_analysis',
            'inspiration_regions': [{'region_id': 'US:New York'}]
        },
        {
            'id': 'idea:5',
            'title': 'Kubernetes Best Practices',
            'summary': 'Cloud-native deployment with Kubernetes...',
            'patterns': ['cloud', 'kubernetes', 'devops'],
            'source': 'learning_analysis',
            'inspiration_regions': [{'region_id': 'US:Seattle'}]
        }
    ]
    
    return agents, ideas

# Pattern to specialization mapping
PATTERN_TO_SPECIALIZATIONS = {
    'performance': ['accelerate-master', 'accelerate-specialist'],
    'optimize': ['accelerate-master', 'accelerate-specialist'],
    'test': ['assert-specialist', 'assert-whiz'],
    'testing': ['assert-specialist', 'assert-whiz'],
    'coverage': ['assert-specialist', 'assert-whiz'],
    'ci': ['align-wizard', 'coordinate-wizard'],
    'cd': ['align-wizard', 'coordinate-wizard'],
    'pipeline': ['align-wizard', 'coordinate-wizard'],
    'workflow': ['align-wizard', 'coordinate-wizard'],
    'api': ['bridge-master', 'engineer-master', 'engineer-wizard'],
    'integration': ['bridge-master', 'connector-ninja'],
    'documentation': ['clarify-champion', 'communicator-maestro', 'document-ninja'],
    'tutorial': ['clarify-champion', 'communicator-maestro'],
    'cloud': ['cloud-architect'],
    'aws': ['cloud-architect'],
    'azure': ['cloud-architect'],
    'gcp': ['cloud-architect'],
    'devops': ['cloud-architect', 'align-wizard'],
    'kubernetes': ['cloud-architect'],
    'docker': ['cloud-architect'],
    'review': ['coach-master', 'coach-wizard', 'guide-wizard'],
    'refactor': ['organize-guru', 'organize-specialist', 'restructure-master'],
    'clean': ['cleaner-master', 'organize-guru', 'simplify-pro'],
    'security': ['secure-specialist', 'secure-ninja', 'secure-pro', 'monitor-champion'],
    'infrastructure': ['create-guru', 'infrastructure-specialist', 'construct-specialist'],
    'build': ['create-champion', 'create-guru', 'construct-specialist'],
}

def test_mission_matching():
    print("🧪 Testing Mission Matching Logic\n")
    print("=" * 60)
    
    agents, ideas = load_test_data()
    
    missions = []
    used_agents = set()
    
    for idea in ideas[:5]:
        idea_id = idea['id']
        idea_title = idea['title']
        idea_patterns = idea['patterns']
        
        print(f"\n📋 Idea: {idea_title}")
        print(f"   Patterns: {', '.join(idea_patterns)}")
        
        # Score agents
        agent_scores = []
        for agent in agents:
            specialization = agent['specialization']
            
            score = 0.3  # Base score
            
            # Match patterns
            matches = []
            for pattern in idea_patterns:
                pattern_lower = pattern.lower()
                if pattern_lower in PATTERN_TO_SPECIALIZATIONS:
                    matching_specs = PATTERN_TO_SPECIALIZATIONS[pattern_lower]
                    if specialization in matching_specs:
                        score += 0.4
                        matches.append(f"{pattern}→{specialization}")
                elif pattern_lower in specialization:
                    score += 0.2
                    matches.append(f"{pattern}~{specialization}")
            
            # Randomness
            random_bonus = random.uniform(-0.1, 0.1)
            score += random_bonus
            
            # Variety penalty
            if specialization in used_agents:
                score -= 0.3
            
            # Performance bonus
            overall_score = agent['metrics']['overall_score']
            score += overall_score * 0.1
            
            agent_scores.append({
                'agent_name': agent['label'],
                'specialization': specialization,
                'score': score,
                'matches': matches
            })
        
        # Sort and select best
        agent_scores.sort(key=lambda x: x['score'], reverse=True)
        
        print("\n   Agent Scores:")
        for i, agent in enumerate(agent_scores[:3], 1):
            used_marker = " [USED]" if agent['specialization'] in used_agents else ""
            matches_str = ", ".join(agent['matches']) if agent['matches'] else "no direct match"
            print(f"   {i}. {agent['agent_name']:20} (@{agent['specialization']:20}) "
                  f"Score: {agent['score']:.3f}{used_marker}")
            if agent['matches']:
                print(f"      Matches: {matches_str}")
        
        best_agent = agent_scores[0]
        used_agents.add(best_agent['specialization'])
        
        print(f"\n   ✅ Selected: {best_agent['agent_name']} (@{best_agent['specialization']})")
        
        missions.append({
            'idea': idea_title,
            'agent': best_agent['specialization']
        })
    
    print("\n" + "=" * 60)
    print("\n📊 Mission Summary:\n")
    
    for mission in missions:
        print(f"   • {mission['idea'][:40]:40} → @{mission['agent']}")
    
    # Check for variety
    unique_agents = len(set(m['agent'] for m in missions))
    print(f"\n   Unique agents used: {unique_agents}/{len(missions)} missions")
    
    if unique_agents == 1:
        print("   ❌ FAIL: All missions assigned to the same agent!")
        return False
    elif unique_agents >= len(missions) * 0.6:
        print("   ✅ PASS: Good agent variety!")
        return True
    else:
        print("   ⚠️  WARN: Some agent variety, but could be better")
        return True

if __name__ == '__main__':
    success = test_mission_matching()
    exit(0 if success else 1)
