#!/usr/bin/env python3
"""
Example: Generate learning recommendations for all agents

This script demonstrates how to use the Agent Learning Matcher to:
1. Load all available learnings
2. Match learnings to each agent
3. Generate a summary report
4. Save recommendations to a file

Created by: @investigate-champion
"""

import json
from pathlib import Path
from agent_learning_matcher import AgentLearningMatcher, load_all_learnings

def main():
    print("🔍 Agent Learning Recommendation Generator")
    print("=" * 70)
    print()
    
    # Initialize matcher
    print("⚙️  Initializing matcher...")
    matcher = AgentLearningMatcher()
    print(f"✅ Loaded {len(matcher.agents)} agents")
    print(f"✅ Loaded {len(matcher.categories)} categories")
    print()
    
    # Load all learnings
    print("📚 Loading learnings...")
    learnings = load_all_learnings()
    print(f"✅ Loaded {len(learnings)} learnings")
    print()
    
    # Analyze learning sources
    sources = {}
    for learning in learnings:
        source = learning.get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print("📊 Learning Sources:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {source}: {count}")
    print()
    
    # Generate recommendations for each agent
    print("🎯 Generating recommendations for agents...")
    print()
    
    recommendations = {}
    
    for agent_name in sorted(matcher.agents.keys()):
        # Get top matches
        matches = matcher.match_agent_to_learnings(
            agent_name,
            learnings,
            max_results=10,
            min_score=0.25
        )
        
        # Get summary
        summary = matcher.get_agent_learning_summary(agent_name, learnings)
        
        # Store recommendations
        recommendations[agent_name] = {
            'summary': {
                'total_relevant': summary['total_relevant'],
                'high_relevance': summary['high_relevance'],
                'perfect_matches': summary['perfect_matches'],
                'average_score': round(summary['average_score'], 3),
                'top_categories': summary['top_categories'][:3],
                'top_sources': summary['top_sources']
            },
            'top_learnings': [
                {
                    'title': m['title'],
                    'score': round(m['relevance_score'], 3),
                    'categories': m.get('matched_categories', [])[:3],
                    'url': m.get('url', ''),
                    'source': m.get('source', 'Unknown')
                }
                for m in matches
            ]
        }
        
        # Print progress
        if matches:
            top_score = matches[0]['relevance_score']
            print(f"  ✓ @{agent_name:<25} {len(matches):>2} matches (top: {top_score:.2f})")
    
    print()
    print("💾 Saving recommendations...")
    
    # Save to JSON
    output_file = Path(__file__).parent / 'agent_learning_recommendations.json'
    with open(output_file, 'w') as f:
        json.dump(recommendations, f, indent=2)
    
    print(f"✅ Saved to {output_file}")
    print()
    
    # Print summary statistics
    print("📈 Summary Statistics:")
    total_matches = sum(len(r['top_learnings']) for r in recommendations.values())
    avg_matches = total_matches / len(recommendations) if recommendations else 0
    
    print(f"   Total agents: {len(recommendations)}")
    print(f"   Total recommendations: {total_matches}")
    print(f"   Average per agent: {avg_matches:.1f}")
    print()
    
    # Top agents by matches
    print("🏆 Top Agents by Learning Matches:")
    sorted_agents = sorted(
        recommendations.items(),
        key=lambda x: len(x[1]['top_learnings']),
        reverse=True
    )
    
    for i, (agent, data) in enumerate(sorted_agents[:10], 1):
        count = len(data['top_learnings'])
        avg_score = data['summary']['average_score']
        categories = ' | '.join(data['summary']['top_categories'][:2])
        print(f"   {i:2d}. @{agent:<25} {count:>2} matches | avg: {avg_score:.2f} | {categories}")
    
    print()
    print("✨ Generation complete!")

if __name__ == '__main__':
    main()
