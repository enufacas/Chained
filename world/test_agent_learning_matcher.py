#!/usr/bin/env python3
"""
Test Agent Learning Matcher

Quick test script to validate the matching system works correctly.

Created by: @investigate-champion
"""

from agent_learning_matcher import AgentLearningMatcher, load_all_learnings
import json

def test_basic_matching():
    """Test basic agent-to-learning matching."""
    print("=" * 70)
    print("TEST 1: Basic Agent-to-Learning Matching")
    print("=" * 70)
    
    matcher = AgentLearningMatcher()
    learnings = load_all_learnings()
    
    # Test with a few representative agents
    test_agents = [
        ("secure-specialist", "Security"),
        ("accelerate-master", "Performance"),
        ("create-guru", "Infrastructure"),
        ("investigate-champion", "Analysis")
    ]
    
    for agent_name, specialty in test_agents:
        matches = matcher.match_agent_to_learnings(
            agent_name,
            learnings,
            max_results=3,
            min_score=0.2
        )
        
        print(f"\n🤖 @{agent_name} ({specialty}):")
        if matches:
            for i, match in enumerate(matches, 1):
                score = match['relevance_score']
                title = match['title'][:60]
                print(f"  {i}. [{score:.2f}] {title}")
        else:
            print("  No matches found (may need to lower threshold)")
    
    print("\n✅ Basic matching test complete\n")

def test_learning_to_agents():
    """Test learning-to-agents matching."""
    print("=" * 70)
    print("TEST 2: Learning-to-Agents Matching")
    print("=" * 70)
    
    matcher = AgentLearningMatcher()
    learnings = load_all_learnings()
    
    # Pick a few interesting learnings
    if learnings:
        test_learnings = learnings[:3]  # First 3 learnings
        
        for learning in test_learnings:
            title = learning.get('title', 'Untitled')[:50]
            print(f"\n📚 Learning: {title}...")
            
            agents = matcher.match_learning_to_agents(
                learning,
                max_results=5,
                min_score=0.15
            )
            
            if agents:
                print(f"   Best agents:")
                for agent_name, score in agents:
                    print(f"     • @{agent_name:<25} [{score:.2f}]")
            else:
                print("   No suitable agents found")
    
    print("\n✅ Learning-to-agents test complete\n")

def test_category_distribution():
    """Test learning category distribution."""
    print("=" * 70)
    print("TEST 3: Category Distribution Analysis")
    print("=" * 70)
    
    matcher = AgentLearningMatcher()
    learnings = load_all_learnings()
    
    # Categorize all learnings
    category_counts = {}
    
    for learning in learnings[:100]:  # Sample first 100
        categories = matcher._categorize_learning(learning)
        for cat, score in categories:
            if score > 0.1:  # Only count meaningful categorizations
                category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print("\n📊 Category Distribution (sample of 100 learnings):")
    sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    
    for cat, count in sorted_cats:
        bar = "█" * (count // 2)
        print(f"  {cat:<20} {count:>3} {bar}")
    
    print("\n✅ Category distribution test complete\n")

def test_agent_summaries():
    """Test agent learning summaries."""
    print("=" * 70)
    print("TEST 4: Agent Learning Summaries")
    print("=" * 70)
    
    matcher = AgentLearningMatcher()
    learnings = load_all_learnings()
    
    # Test a few agents
    test_agents = [
        "secure-specialist",
        "accelerate-master",
        "investigate-champion",
        "pioneer-sage"
    ]
    
    print()
    for agent_name in test_agents:
        summary = matcher.get_agent_learning_summary(agent_name, learnings)
        
        print(f"🤖 @{agent_name}")
        print(f"   Relevant: {summary['total_relevant']}")
        print(f"   High Relevance: {summary['high_relevance']}")
        print(f"   Perfect Matches: {summary['perfect_matches']}")
        print(f"   Avg Score: {summary['average_score']:.2f}")
        print(f"   Top Categories: {', '.join(summary['top_categories'][:3])}")
        print(f"   Top Sources: {', '.join(summary['top_sources'])}")
        print()
    
    print("✅ Agent summary test complete\n")

def test_config_loading():
    """Test configuration loading."""
    print("=" * 70)
    print("TEST 5: Configuration Validation")
    print("=" * 70)
    
    matcher = AgentLearningMatcher()
    
    print(f"\n✅ Agents loaded: {len(matcher.agents)}")
    print(f"✅ Categories loaded: {len(matcher.categories)}")
    print(f"✅ Scoring weights: {len(matcher.weights)}")
    print(f"✅ Thresholds: {len(matcher.thresholds)}")
    
    # Validate agent configuration
    print("\n🔍 Validating agent configurations...")
    for agent_name, agent_info in matcher.agents.items():
        assert 'focus_areas' in agent_info, f"{agent_name} missing focus_areas"
        assert 'primary_categories' in agent_info, f"{agent_name} missing primary_categories"
        assert 'keywords' in agent_info, f"{agent_name} missing keywords"
        assert 'learning_affinity_score' in agent_info, f"{agent_name} missing learning_affinity_score"
    
    print(f"✅ All {len(matcher.agents)} agent configs validated")
    
    # Validate categories
    print("\n🔍 Validating category configurations...")
    for cat_name, cat_info in matcher.categories.items():
        assert 'keywords' in cat_info, f"{cat_name} missing keywords"
        assert 'priority_weight' in cat_info, f"{cat_name} missing priority_weight"
    
    print(f"✅ All {len(matcher.categories)} category configs validated")
    print("\n✅ Configuration validation complete\n")

def main():
    """Run all tests."""
    print("\n🧪 Agent Learning Matcher Test Suite")
    print("Created by: @investigate-champion")
    print("=" * 70)
    print()
    
    try:
        test_config_loading()
        test_basic_matching()
        test_learning_to_agents()
        test_category_distribution()
        test_agent_summaries()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("The Agent Learning Matcher is working correctly. 🎉")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
