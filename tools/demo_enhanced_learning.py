#!/usr/bin/env python3
"""
Demo: Enhanced Self-Documenting AI System

This script demonstrates the complete workflow of the enhanced learning system.
Shows real-time analysis, knowledge graph building, and proactive suggestions.

Author: @engineer-master
"""

import json
import os
import sys
from pathlib import Path

# Add tools to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

# Import the enhanced learner
import importlib.util
spec = importlib.util.spec_from_file_location(
    "enhanced_discussion_learner",
    tools_dir / "enhanced-discussion-learner.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

EnhancedDiscussionLearner = module.EnhancedDiscussionLearner


def print_banner(text):
    """Print a fancy banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def demo_real_time_learning():
    """Demonstrate real-time learning during a discussion."""
    print_banner("🔄 DEMO 1: Real-Time Learning During Active Discussion")
    
    # Simulate an ongoing discussion
    issue_data = {
        'number': 42,
        'title': 'Implement caching layer for API performance',
        'body': 'We need to add Redis caching to improve API response times',
        'labels': [{'name': 'performance'}, {'name': 'enhancement'}],
        'user': {'login': 'dev-lead'},
        'created_at': '2024-01-01T10:00:00Z',
        'comments': []
    }
    
    print("📝 Issue #42: Implement caching layer for API performance\n")
    
    # Create learner
    learner = EnhancedDiscussionLearner('/tmp/demo_learning')
    
    # Simulate discussion progressing
    discussion_stages = [
        {
            'user': 'accelerate-master',
            'body': 'I analyzed the performance bottleneck. We should use Redis for caching.'
        },
        {
            'user': 'engineer-master',
            'body': 'After considering alternatives, we decided Redis is the best choice for this use case.'
        },
        {
            'user': 'assert-specialist',
            'body': 'I learned that comprehensive cache invalidation testing is crucial here.'
        }
    ]
    
    for i, comment in enumerate(discussion_stages, 1):
        # Add comment to discussion
        issue_data['comments'].append({
            'user': {'login': comment['user']},
            'body': comment['body'],
            'created_at': f'2024-01-01T{10+i}:00:00Z'
        })
        
        print(f"💬 Comment {i} from {comment['user']}:")
        print(f"   '{comment['body'][:60]}...'\n")
        
        # Perform live analysis
        live = learner.analyze_live_discussion(42, issue_data['comments'])
        
        print(f"   🧠 Live Learning:")
        print(f"      - Insight: {live.insight_preview}")
        print(f"      - Confidence: {live.confidence:.0%}")
        print(f"      - Suggested Actions: {len(live.suggested_actions)}")
        if live.suggested_actions:
            for action in live.suggested_actions[:2]:
                print(f"        • {action}")
        print()
    
    print("✅ Real-time learning completed!")
    print(f"   Final confidence: {live.confidence:.0%}")
    print(f"   Total actions suggested: {len(live.suggested_actions)}")


def demo_knowledge_graph():
    """Demonstrate knowledge graph connection building."""
    print_banner("🔗 DEMO 2: Building Knowledge Graph Connections")
    
    learner = EnhancedDiscussionLearner('/tmp/demo_learning')
    
    # First discussion about performance
    issue1 = {
        'number': 100,
        'title': 'Optimize database query performance',
        'body': 'Database queries are slow, need to optimize with indexes',
        'labels': [{'name': 'performance'}, {'name': 'database'}],
        'user': {'login': 'dba'},
        'created_at': '2024-01-01T10:00:00Z',
        'comments': [
            {
                'user': {'login': 'accelerate-master'},
                'body': 'I discovered that adding indexes on frequently queried columns improves performance significantly.',
                'created_at': '2024-01-01T11:00:00Z'
            }
        ]
    }
    
    print("📝 Issue #100: Optimize database query performance\n")
    analysis1, enhancements1 = learner.analyze_with_enhancements(issue1)
    print(f"   ✅ Extracted {len(analysis1.insights)} insights")
    print(f"   📊 Learning quality: {analysis1.learning_quality:.0%}\n")
    
    # Second related discussion
    issue2 = {
        'number': 101,
        'title': 'Improve API response time',
        'body': 'API is slow, need performance optimization',
        'labels': [{'name': 'performance'}, {'name': 'api'}],
        'user': {'login': 'backend-dev'},
        'created_at': '2024-01-02T10:00:00Z',
        'comments': [
            {
                'user': {'login': 'accelerate-master'},
                'body': 'After analyzing, I found that optimizing queries and adding indexes will improve performance.',
                'created_at': '2024-01-02T11:00:00Z'
            }
        ]
    }
    
    print("📝 Issue #101: Improve API response time\n")
    analysis2, enhancements2 = learner.analyze_with_enhancements(issue2)
    print(f"   ✅ Extracted {len(analysis2.insights)} insights")
    print(f"   📊 Learning quality: {analysis2.learning_quality:.0%}")
    print(f"   🔗 Connections created: {len(enhancements2['knowledge_connections'])}\n")
    
    # Show connections
    if enhancements2['knowledge_connections']:
        print("   🔗 Knowledge Graph Connections:")
        for insight_id, connections in list(enhancements2['knowledge_connections'].items())[:2]:
            print(f"      {insight_id}")
            for conn in connections[:1]:
                print(f"         → {conn['target_id']} (similarity: {conn['similarity']:.0%})")
    
    # Show graph stats
    stats = enhancements2['knowledge_graph_stats']
    print(f"\n   📊 Knowledge Graph Statistics:")
    print(f"      - Total insights: {stats['total_insights']}")
    print(f"      - Total connections: {stats['total_connections']}")
    print(f"      - New insights: {stats['new_insights_added']}")


def demo_proactive_suggestions():
    """Demonstrate proactive suggestion generation."""
    print_banner("💡 DEMO 3: Proactive Suggestions Based on Context")
    
    learner = EnhancedDiscussionLearner('/tmp/demo_learning')
    
    # Different issue types
    test_issues = [
        {
            'title': 'Fix critical bug in authentication',
            'body': 'Users cannot log in due to session handling error',
            'type': '🐛 Bug'
        },
        {
            'title': 'Improve algorithm performance',
            'body': 'The sorting algorithm is too slow for large datasets',
            'type': '⚡ Performance'
        },
        {
            'title': 'Add user dashboard feature',
            'body': 'Implement a new dashboard for user analytics',
            'type': '✨ Feature'
        }
    ]
    
    for issue in test_issues:
        issue_data = {
            'title': issue['title'],
            'body': issue['body'],
            'number': 200
        }
        
        print(f"{issue['type']}: {issue['title']}\n")
        
        suggestions = learner.generate_proactive_suggestions(issue_data)
        
        print("   💡 Proactive Suggestions:")
        for suggestion in suggestions[:3]:
            print(f"      {suggestion}")
        print()


def demo_similarity_algorithm():
    """Demonstrate the similarity calculation algorithm."""
    print_banner("🎯 DEMO 4: Text Similarity Algorithm")
    
    learner = EnhancedDiscussionLearner('/tmp/demo_learning')
    
    test_pairs = [
        (
            "Optimize the neural network algorithm for better performance",
            "Improve neural network performance through optimization",
            "High similarity (same topic)"
        ),
        (
            "Fix bug in authentication system",
            "Resolve login error in auth module",
            "Moderate similarity (related topics)"
        ),
        (
            "Add new dashboard feature",
            "Weather is nice today",
            "Low similarity (unrelated)"
        )
    ]
    
    print("Comparing text pairs:\n")
    
    for text1, text2, description in test_pairs:
        similarity = learner.calculate_text_similarity(text1, text2)
        
        print(f"📝 {description}")
        print(f"   Text 1: '{text1}'")
        print(f"   Text 2: '{text2}'")
        print(f"   Similarity: {similarity:.0%}")
        
        # Visual representation
        bar_length = int(similarity * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"   [{bar}] {similarity:.1%}\n")


def main():
    """Run all demos."""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  🧠 Enhanced Self-Documenting AI System - Demonstration".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" + "  By @engineer-master".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    # Create demo directory
    os.makedirs('/tmp/demo_learning', exist_ok=True)
    
    try:
        # Run demos
        demo_real_time_learning()
        demo_knowledge_graph()
        demo_proactive_suggestions()
        demo_similarity_algorithm()
        
        # Final summary
        print_banner("✅ Demonstration Complete")
        
        print("The Enhanced Self-Documenting AI System provides:\n")
        print("  1️⃣  Real-time learning during active discussions")
        print("  2️⃣  Knowledge graph connecting related insights")
        print("  3️⃣  Proactive context-aware suggestions")
        print("  4️⃣  Advanced similarity algorithms\n")
        
        print("The system continuously learns and improves with every discussion!")
        print("\n" + "█" * 80 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
