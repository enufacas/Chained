#!/usr/bin/env python3
"""
Test suite for agent learning assignment diversity.
Validates that learnings are distributed across different agents
and not all assigned to a single agent.

Created to address: https://github.com/enufacas/Chained/actions/runs/19402402000/job/55511844369#step:6:1
"""

import sys
import json
from pathlib import Path
from collections import Counter

# Add world directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'world'))

from agent_learning_matcher import AgentLearningMatcher


def test_diverse_assignment_basic():
    """Test that diverse learnings get assigned to different agents."""
    matcher = AgentLearningMatcher()
    
    # Create learnings with different topics
    learnings = [
        {
            'title': 'Machine Learning Basics',
            'description': 'Introduction to AI and neural networks',
            'content': 'artificial intelligence machine learning neural networks',
            'source': 'Tech News'
        },
        {
            'title': 'Kubernetes Tutorial',
            'description': 'Container orchestration guide',
            'content': 'kubernetes docker containers devops deployment',
            'source': 'DevOps Weekly'
        },
        {
            'title': 'SQL Optimization',
            'description': 'Database performance tuning',
            'content': 'database sql performance optimization queries',
            'source': 'Database Weekly'
        },
        {
            'title': 'Security Best Practices',
            'description': 'Secure coding guidelines',
            'content': 'security vulnerability authentication encryption',
            'source': 'Security News'
        },
        {
            'title': 'React Performance',
            'description': 'Frontend optimization tips',
            'content': 'react javascript frontend performance optimization',
            'source': 'Web Dev'
        },
    ]
    
    # Get diverse assignments
    assignments = matcher.assign_learnings_to_agents_diverse(
        learnings=learnings,
        max_assignments=5,
        min_score=0.05,
        diversity_weight=0.7
    )
    
    # Check we got assignments
    assert len(assignments) == 5, f"Expected 5 assignments, got {len(assignments)}"
    
    # Check agent diversity
    agent_ids = [a['agent_id'] for a in assignments]
    unique_agents = set(agent_ids)
    
    print(f"✅ Got {len(unique_agents)} unique agents for 5 learnings")
    print(f"   Agents: {', '.join(sorted(unique_agents))}")
    
    # With diversity_weight=0.7, we should get mostly different agents
    assert len(unique_agents) >= 4, f"Expected at least 4 different agents, got {len(unique_agents)}"
    
    # Check that no agent got more than 2 assignments
    agent_counts = Counter(agent_ids)
    max_count = max(agent_counts.values())
    
    print(f"   Max assignments to one agent: {max_count}")
    assert max_count <= 2, f"One agent got {max_count} assignments, should be <= 2"
    
    return True


def test_similar_learnings_diversity():
    """Test diversity even when learnings are similar and might favor one agent."""
    matcher = AgentLearningMatcher()
    
    # Create learnings that might all match to create-guru or similar
    learnings = [
        {
            'title': 'Building New Features',
            'description': 'Feature development process',
            'content': 'create build feature development implement new',
            'source': 'Engineering'
        },
        {
            'title': 'Creating Infrastructure',
            'description': 'Infrastructure as code',
            'content': 'create infrastructure build system tools automation',
            'source': 'DevOps'
        },
        {
            'title': 'Innovative API Design',
            'description': 'Building modern APIs',
            'content': 'create api build design innovation feature',
            'source': 'Tech'
        },
        {
            'title': 'System Architecture',
            'description': 'Building scalable systems',
            'content': 'create build system architecture infrastructure',
            'source': 'Engineering'
        },
        {
            'title': 'New Framework Development',
            'description': 'Creating development frameworks',
            'content': 'create build framework development tools',
            'source': 'Tech'
        },
    ]
    
    # Get diverse assignments
    assignments = matcher.assign_learnings_to_agents_diverse(
        learnings=learnings,
        max_assignments=5,
        min_score=0.05,
        diversity_weight=0.7
    )
    
    # Check we got assignments
    assert len(assignments) > 0, "Expected at least some assignments"
    
    # Check agent diversity
    agent_ids = [a['agent_id'] for a in assignments]
    unique_agents = set(agent_ids)
    
    print(f"✅ Got {len(unique_agents)} unique agents for {len(assignments)} similar learnings")
    print(f"   Agents: {', '.join(sorted(unique_agents))}")
    
    # Even with similar learnings, diversity should prevent all going to one agent
    if len(assignments) >= 3:
        assert len(unique_agents) >= 2, "Expected at least 2 different agents for similar learnings"
    
    # Print distribution
    agent_counts = Counter(agent_ids)
    print("   Distribution:")
    for agent_id, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"     - @{agent_id}: {count}")
    
    return True


def test_diversity_weight_effect():
    """Test that diversity_weight parameter actually affects distribution."""
    matcher = AgentLearningMatcher()
    
    # Create test learnings
    learnings = [
        {
            'title': f'Test Learning {i}',
            'description': 'Generic learning content',
            'content': 'test learning content development',
            'source': 'Test'
        }
        for i in range(5)
    ]
    
    # Test with LOW diversity weight (should allow more repeats)
    assignments_low = matcher.assign_learnings_to_agents_diverse(
        learnings=learnings,
        max_assignments=5,
        min_score=0.01,
        diversity_weight=0.1  # Low diversity preference
    )
    
    agent_ids_low = [a['agent_id'] for a in assignments_low]
    unique_low = len(set(agent_ids_low))
    
    # Test with HIGH diversity weight (should force more variety)
    assignments_high = matcher.assign_learnings_to_agents_diverse(
        learnings=learnings,
        max_assignments=5,
        min_score=0.01,
        diversity_weight=0.9  # High diversity preference
    )
    
    agent_ids_high = [a['agent_id'] for a in assignments_high]
    unique_high = len(set(agent_ids_high))
    
    print(f"✅ Low diversity (0.1): {unique_low} unique agents")
    print(f"✅ High diversity (0.9): {unique_high} unique agents")
    
    # High diversity should give more unique agents (or at least not fewer)
    assert unique_high >= unique_low, "High diversity should give at least as many unique agents"
    
    return True


def test_assignment_rank_tracking():
    """Test that assignment_rank is properly tracked."""
    matcher = AgentLearningMatcher()
    
    # Create learnings that might match to the same agent
    learnings = [
        {
            'title': f'Performance Optimization {i}',
            'description': 'Speed up the application',
            'content': 'performance optimization speed latency throughput',
            'source': 'Tech'
        }
        for i in range(3)
    ]
    
    assignments = matcher.assign_learnings_to_agents_diverse(
        learnings=learnings,
        max_assignments=3,
        min_score=0.05,
        diversity_weight=0.3  # Lower to allow some repeats
    )
    
    # Check that ranks are assigned
    for assignment in assignments:
        assert 'assignment_rank' in assignment, "assignment_rank should be present"
        assert assignment['assignment_rank'] >= 1, "rank should be >= 1"
    
    # If any agent got multiple assignments, their ranks should increment
    agent_ranks = {}
    for assignment in assignments:
        agent_id = assignment['agent_id']
        rank = assignment['assignment_rank']
        if agent_id not in agent_ranks:
            agent_ranks[agent_id] = []
        agent_ranks[agent_id].append(rank)
    
    # Check that ranks are consecutive for each agent
    for agent_id, ranks in agent_ranks.items():
        if len(ranks) > 1:
            ranks.sort()
            print(f"   Agent @{agent_id} got ranks: {ranks}")
            assert ranks == list(range(1, len(ranks) + 1)), f"Ranks should be consecutive for {agent_id}"
    
    print(f"✅ Assignment ranks properly tracked")
    
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("🧪 Testing Agent Learning Assignment Diversity")
    print("=" * 70)
    print()
    
    tests = [
        ("Basic diverse assignment", test_diverse_assignment_basic),
        ("Similar learnings diversity", test_similar_learnings_diversity),
        ("Diversity weight effect", test_diversity_weight_effect),
        ("Assignment rank tracking", test_assignment_rank_tracking),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"📋 Test: {test_name}")
        print("-" * 70)
        try:
            result = test_func()
            if result:
                print(f"✅ PASS: {test_name}")
                passed += 1
            else:
                print(f"❌ FAIL: {test_name}")
                failed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 ERROR: {test_name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 70)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
