#!/usr/bin/env python3
"""
Integration Example: Self-Documenting AI

This script demonstrates how to use the Self-Documenting AI system
to learn from issue discussions and apply that knowledge.

Author: @engineer-master
"""

import json
import os
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, 'tools')

# Import the learner (handle hyphenated filename)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "issue_discussion_learner",
    "tools/issue-discussion-learner.py"
)
learner_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(learner_module)


def example_1_analyze_single_issue():
    """Example 1: Analyze a single issue discussion."""
    print("=" * 70)
    print("Example 1: Analyzing a Single Issue Discussion")
    print("=" * 70)
    
    # Sample issue data (you would fetch this from GitHub API)
    issue_data = {
        'number': 999,
        'title': 'Implement caching system for improved performance',
        'body': '''We need to implement a caching layer to improve the performance of our API.
        
        Requirements:
        - Redis-based caching
        - Configurable TTL
        - Cache invalidation strategy
        ''',
        'labels': [
            {'name': 'enhancement'},
            {'name': 'performance'}
        ],
        'user': {'login': 'developer1'},
        'created_at': '2024-01-15T10:00:00Z',
        'comments': [
            {
                'body': 'I suggest we use Redis for this. The implementation should focus on performance optimization.',
                'user': {'login': 'engineer-master'},
                'created_at': '2024-01-15T11:00:00Z'
            },
            {
                'body': 'After careful analysis, we decided to implement a two-tier caching strategy with both memory and Redis.',
                'user': {'login': 'architect-agent'},
                'created_at': '2024-01-15T12:00:00Z'
            },
            {
                'body': 'The testing workflow should include cache hit rate monitoring and performance benchmarks.',
                'user': {'login': 'test-agent'},
                'created_at': '2024-01-15T13:00:00Z'
            },
            {
                'body': 'Agent collaboration was excellent here. The systematic approach led to a great design.',
                'user': {'login': 'coach-master'},
                'created_at': '2024-01-15T14:00:00Z'
            }
        ]
    }
    
    # Create learner
    learner = learner_module.IssueDiscussionLearner('/tmp/example_learnings')
    
    # Analyze the discussion
    print("\n📊 Analyzing discussion...")
    analysis = learner.analyze_issue_discussion(issue_data)
    
    # Print results
    print(f"\n✅ Analysis Complete!")
    print(f"   Issue: #{analysis.issue_number} - {analysis.issue_title}")
    print(f"   Participants: {', '.join(analysis.participants)}")
    print(f"   Duration: {analysis.duration_hours} hours")
    print(f"   Comments: {analysis.total_comments}")
    print(f"   Learning Quality: {analysis.learning_quality:.1%}")
    
    print(f"\n💡 Insights Extracted: {len(analysis.insights)}")
    
    # Show insights by type
    from collections import defaultdict
    insights_by_type = defaultdict(list)
    for insight in analysis.insights:
        insights_by_type[insight.insight_type].append(insight)
    
    for insight_type, insights in sorted(insights_by_type.items()):
        print(f"\n   {insight_type.upper()} ({len(insights)} insights):")
        for insight in insights[:2]:  # Show first 2 of each type
            print(f"   - {insight.content[:80]}...")
            print(f"     Confidence: {insight.confidence:.1%}, Tags: {', '.join(insight.tags)}")
    
    print(f"\n🎯 Key Decisions: {len(analysis.key_decisions)}")
    for decision in analysis.key_decisions[:3]:
        print(f"   - {decision}")
    
    print(f"\n🔍 Patterns: {len(analysis.patterns_identified)}")
    for pattern in analysis.patterns_identified[:3]:
        print(f"   - {pattern}")
    
    return analysis


def example_2_generate_documentation(analysis):
    """Example 2: Generate documentation from analysis."""
    print("\n" + "=" * 70)
    print("Example 2: Generating Self-Documentation")
    print("=" * 70)
    
    learner = learner_module.IssueDiscussionLearner('/tmp/example_learnings')
    
    print("\n📄 Generating markdown documentation...")
    doc = learner.generate_documentation(analysis)
    
    print(f"✅ Generated {len(doc)} characters of documentation")
    print("\nPreview (first 500 characters):")
    print("-" * 70)
    print(doc[:500])
    print("...")
    print("-" * 70)
    
    # Save to file
    doc_path = '/tmp/example_documentation.md'
    with open(doc_path, 'w') as f:
        f.write(doc)
    
    print(f"\n💾 Saved full documentation to: {doc_path}")
    
    return doc


def example_3_consolidate_knowledge():
    """Example 3: Consolidate knowledge from multiple discussions."""
    print("\n" + "=" * 70)
    print("Example 3: Consolidating Knowledge Across Discussions")
    print("=" * 70)
    
    learner = learner_module.IssueDiscussionLearner('/tmp/example_learnings')
    
    # Create several example analyses
    print("\n📚 Creating sample discussion learnings...")
    
    for i in range(5):
        issue_data = {
            'number': 1000 + i,
            'title': f'Example Issue {i + 1}',
            'body': f'Body for issue {i + 1}',
            'labels': [{'name': 'enhancement'}],
            'user': {'login': 'user1'},
            'created_at': '2024-01-15T10:00:00Z',
            'comments': [
                {
                    'body': f'This is a technical comment about Python implementation for issue {i + 1}',
                    'user': {'login': 'agent1'},
                    'created_at': '2024-01-15T11:00:00Z'
                },
                {
                    'body': f'We decided to use approach X for issue {i + 1}',
                    'user': {'login': 'agent2'},
                    'created_at': '2024-01-15T12:00:00Z'
                }
            ]
        }
        
        analysis = learner.analyze_issue_discussion(issue_data)
        learner.save_analysis(analysis)
        print(f"   ✅ Saved analysis for issue {1000 + i}")
    
    # Consolidate learnings
    print("\n🔄 Consolidating learnings...")
    summary = learner.consolidate_learnings(days=30)
    
    print(f"\n📊 Consolidated Summary:")
    print(f"   Period: Last {summary['period_days']} days")
    print(f"   Issues Analyzed: {summary['issues_analyzed']}")
    print(f"   Total Insights: {summary['total_insights']}")
    print(f"   Total Decisions: {summary['total_decisions']}")
    print(f"   Total Patterns: {summary['total_patterns']}")
    
    print(f"\n🏷️  Top Tags:")
    for tag, count in list(summary['top_tags'].items())[:5]:
        print(f"   - {tag}: {count} mentions")
    
    print(f"\n📈 Insight Type Distribution:")
    for itype, count in summary['insight_type_distribution'].items():
        print(f"   - {itype}: {count}")
    
    return summary


def example_4_query_learnings():
    """Example 4: Query and use learned knowledge."""
    print("\n" + "=" * 70)
    print("Example 4: Querying and Using Learned Knowledge")
    print("=" * 70)
    
    learner = learner_module.IssueDiscussionLearner('/tmp/example_learnings')
    
    # Load all learnings
    print("\n🔍 Searching for insights about 'python'...")
    
    python_insights = []
    for filepath in Path('/tmp/example_learnings').glob('discussion_issue_*.json'):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            for insight in data.get('insights', []):
                if isinstance(insight, dict) and 'python' in ' '.join(insight.get('tags', [])).lower():
                    python_insights.append({
                        'issue': data['issue_number'],
                        'content': insight.get('content', ''),
                        'confidence': insight.get('confidence', 0)
                    })
        except Exception as e:
            print(f"   Warning: Could not load {filepath}: {e}")
    
    print(f"\n✅ Found {len(python_insights)} insights related to Python:")
    for insight in python_insights[:5]:
        print(f"\n   Issue #{insight['issue']}:")
        print(f"   {insight['content'][:100]}...")
        print(f"   Confidence: {insight['confidence']:.1%}")
    
    # Example: Find decisions made about performance
    print("\n\n🔍 Searching for decisions about 'performance'...")
    
    perf_decisions = []
    for filepath in Path('/tmp/example_learnings').glob('discussion_issue_*.json'):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            for decision in data.get('key_decisions', []):
                if 'performance' in decision.lower():
                    perf_decisions.append({
                        'issue': data['issue_number'],
                        'decision': decision
                    })
        except Exception:
            pass
    
    print(f"\n✅ Found {len(perf_decisions)} decisions about performance:")
    for item in perf_decisions[:3]:
        print(f"   - Issue #{item['issue']}: {item['decision']}")


def example_5_apply_learnings():
    """Example 5: Apply learnings to new situations."""
    print("\n" + "=" * 70)
    print("Example 5: Applying Learnings to New Situations")
    print("=" * 70)
    
    print("\n🎯 Scenario: New issue about implementing authentication")
    print("   The AI can use past learnings to inform its approach...")
    
    # Load consolidated summary
    learner = learner_module.IssueDiscussionLearner('/tmp/example_learnings')
    summary = learner.consolidate_learnings(days=30)
    
    # Simulate applying learnings
    print("\n🧠 Applying past learnings:")
    
    print("\n   1. Technical Insights:")
    tech_count = summary['insight_type_distribution'].get('technical', 0)
    print(f"      - Found {tech_count} technical insights from past discussions")
    print(f"      - Common technologies: {', '.join(list(summary['top_tags'].keys())[:3])}")
    print(f"      - Recommendation: Use proven technologies from past successes")
    
    print("\n   2. Process Insights:")
    process_count = summary['insight_type_distribution'].get('process', 0)
    print(f"      - Found {process_count} process insights")
    print(f"      - Recommendation: Follow established workflows and testing procedures")
    
    print("\n   3. Agent Collaboration:")
    agent_count = summary['insight_type_distribution'].get('agent_behavior', 0)
    print(f"      - Found {agent_count} collaboration insights")
    print(f"      - Recommendation: Engage multiple agents for comprehensive discussion")
    
    print("\n   4. Decision Making:")
    decision_count = summary['total_decisions']
    print(f"      - Analyzed {decision_count} past decisions")
    print(f"      - Recommendation: Document decisions clearly for future reference")
    
    print("\n✅ The AI can now make more informed decisions based on past experience!")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("🧠 SELF-DOCUMENTING AI: Integration Examples")
    print("   by @engineer-master")
    print("=" * 70)
    
    try:
        # Run examples
        analysis = example_1_analyze_single_issue()
        doc = example_2_generate_documentation(analysis)
        summary = example_3_consolidate_knowledge()
        example_4_query_learnings()
        example_5_apply_learnings()
        
        # Final summary
        print("\n" + "=" * 70)
        print("✅ All Examples Completed Successfully!")
        print("=" * 70)
        
        print("\n📚 Key Takeaways:")
        print("   1. The system automatically learns from every discussion")
        print("   2. Insights are classified and scored for quality")
        print("   3. Documentation is generated automatically")
        print("   4. Knowledge consolidates over time")
        print("   5. Past learnings inform future decisions")
        
        print("\n🚀 Next Steps:")
        print("   - Integrate with your GitHub workflows")
        print("   - Start learning from real issue discussions")
        print("   - Query learnings to inform agent behavior")
        print("   - Build on the knowledge base over time")
        
        print("\n💡 The more discussions the AI analyzes,")
        print("   the smarter and more capable it becomes!")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
