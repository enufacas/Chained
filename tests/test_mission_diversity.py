#!/usr/bin/env python3
"""
Test mission assignment diversity to ensure:
1. Different agents are selected for different missions
2. Ideas are marked as processed to prevent duplicates
3. AgentLearningMatcher is used correctly
"""

import json
import sys
from pathlib import Path

# Add world directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'world'))

from agent_learning_matcher import AgentLearningMatcher


def test_diversity_assignment():
    """Test that diversity constraints work correctly."""
    matcher = AgentLearningMatcher()
    
    # Create 5 similar learnings (all about AI)
    # This tests that diversity forces different agents despite similarity
    learnings = [
        {
            'id': f'test_{i}',
            'title': f'AI Innovation {i}',
            'description': f'Exploring AI trends {i}',
            'content': 'ai machine learning artificial intelligence',
            'patterns': ['ai', 'ai/ml']
        }
        for i in range(5)
    ]
    
    # Test with high diversity weight
    assignments = matcher.assign_learnings_to_agents_diverse(
        learnings,
        max_assignments=5,
        min_score=0.1,
        diversity_weight=0.7
    )
    
    # Verify we got 5 assignments
    assert len(assignments) == 5, f"Expected 5 assignments, got {len(assignments)}"
    
    # Count unique agents
    agent_ids = [a['agent_id'] for a in assignments]
    unique_agents = set(agent_ids)
    
    # With high diversity weight, we should get mostly unique agents
    # Allow for some overlap (at least 4 unique out of 5)
    assert len(unique_agents) >= 4, f"Expected at least 4 unique agents, got {len(unique_agents)}: {unique_agents}"
    
    # Verify assignment ranks increase for repeated agents
    agent_ranks = {}
    for assignment in assignments:
        agent = assignment['agent_id']
        rank = assignment['assignment_rank']
        
        if agent in agent_ranks:
            # If same agent appears, rank should increase
            assert rank > agent_ranks[agent], f"Agent {agent} rank should increase: {agent_ranks[agent]} -> {rank}"
        
        agent_ranks[agent] = rank
    
    print(f"✅ Diversity test passed: {len(unique_agents)} unique agents for 5 assignments")
    print(f"   Agent distribution: {dict((k, agent_ids.count(k)) for k in unique_agents)}")
    
    return True


def test_idea_marking():
    """Test that ideas can be marked as processed."""
    # Simulate knowledge.json structure
    knowledge = {
        'ideas': [
            {
                'id': 'idea:1',
                'title': 'Test Idea 1',
                'source': 'learning_analysis',
                'mission_created': False
            },
            {
                'id': 'idea:2',
                'title': 'Test Idea 2',
                'source': 'learning_analysis',
                'mission_created': False
            },
            {
                'id': 'idea:3',
                'title': 'Test Idea 3',
                'source': 'learning_analysis',
                'mission_created': True  # Already processed
            }
        ]
    }
    
    # Filter unprocessed ideas
    unprocessed = [
        idea for idea in knowledge['ideas']
        if idea.get('source') == 'learning_analysis'
        and not idea.get('mission_created', False)
    ]
    
    # Should only get ideas 1 and 2
    assert len(unprocessed) == 2, f"Expected 2 unprocessed ideas, got {len(unprocessed)}"
    assert unprocessed[0]['id'] == 'idea:1'
    assert unprocessed[1]['id'] == 'idea:2'
    
    # Mark as processed
    for idea in knowledge['ideas']:
        if idea['id'] in ['idea:1', 'idea:2']:
            idea['mission_created'] = True
    
    # Re-filter
    unprocessed = [
        idea for idea in knowledge['ideas']
        if idea.get('source') == 'learning_analysis'
        and not idea.get('mission_created', False)
    ]
    
    # Should now get 0 unprocessed ideas
    assert len(unprocessed) == 0, f"Expected 0 unprocessed ideas, got {len(unprocessed)}"
    
    print("✅ Idea marking test passed: Ideas correctly filtered by mission_created flag")
    
    return True


def test_fallback_mode():
    """Test that fallback mode works when matcher is unavailable."""
    from collections import defaultdict
    
    # Simulate agents list
    agents = [
        {'id': 'agent1', 'label': 'Agent 1', 'specialization': 'engineer-master'},
        {'id': 'agent2', 'label': 'Agent 2', 'specialization': 'secure-specialist'},
        {'id': 'agent3', 'label': 'Agent 3', 'specialization': 'organize-guru'},
        {'id': 'agent4', 'label': 'Agent 4', 'specialization': 'investigate-champion'},
        {'id': 'agent5', 'label': 'Agent 5', 'specialization': 'create-guru'},
    ]
    
    # Simulate ideas
    ideas = [
        {'id': f'idea:{i}', 'title': f'Idea {i}'} 
        for i in range(5)
    ]
    
    agent_assignment_count = defaultdict(int)
    selected_agents = []
    
    # Simple diverse selection (fallback logic from workflow)
    for idea in ideas:
        agent_scores = []
        
        for agent in agents:
            specialization = agent['specialization']
            base_score = 0.5
            
            # Apply diversity penalty
            diversity_penalty = agent_assignment_count[specialization] * 0.7
            adjusted_score = base_score * (1.0 - min(diversity_penalty, 0.9))
            
            agent_scores.append({
                'agent': agent,
                'score': adjusted_score
            })
        
        # Sort by score
        agent_scores.sort(key=lambda x: x['score'], reverse=True)
        
        best = agent_scores[0]
        selected_agents.append(best['agent']['specialization'])
        agent_assignment_count[best['agent']['specialization']] += 1
    
    # Count unique agents
    unique_agents = set(selected_agents)
    
    # Should get 5 unique agents with 0.7 diversity weight
    assert len(unique_agents) == 5, f"Expected 5 unique agents, got {len(unique_agents)}: {unique_agents}"
    
    print(f"✅ Fallback mode test passed: {len(unique_agents)} unique agents selected")
    
    return True


if __name__ == '__main__':
    print("🧪 Testing Mission Diversity")
    print("=" * 60)
    
    try:
        test_diversity_assignment()
        print()
        test_idea_marking()
        print()
        test_fallback_mode()
        print()
        print("=" * 60)
        print("✅ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
