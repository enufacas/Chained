#!/usr/bin/env python3
"""
Example usage of the Agent Investment Tracker

This script demonstrates common usage patterns and workflows.

Created by: @organize-guru
"""

import sys
from pathlib import Path

# Add world directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent_investment_tracker import (
    AgentInvestmentTracker,
    InvestmentLevel,
    record_learning_work,
    get_top_agents_for_category
)


def example_basic_cultivation():
    """Example: Record basic cultivation events."""
    print("=" * 60)
    print("Example 1: Basic Cultivation Recording")
    print("=" * 60)
    
    tracker = AgentInvestmentTracker()
    
    # Record a cultivation event
    investment = tracker.record_cultivation(
        agent_name="secure-specialist",
        category="Security",
        impact=0.8,
        learning_id="sec-vuln-2025-001",
        context="Fixed critical authentication vulnerability"
    )
    
    print(f"\n✅ Cultivation recorded!")
    print(f"   Agent: secure-specialist")
    print(f"   Category: Security")
    print(f"   Level: {investment.level.name}")
    print(f"   Score: {investment.score:.1f}")
    print(f"   Total events: {investment.cultivation_count}")
    

def example_agent_portfolio():
    """Example: View agent's investment portfolio."""
    print("\n" + "=" * 60)
    print("Example 2: Agent Investment Portfolio")
    print("=" * 60)
    
    tracker = AgentInvestmentTracker()
    
    # Get all investments for an agent
    agent = "troubleshoot-expert"
    investments = tracker.get_agent_investments(agent)
    
    print(f"\n📊 Portfolio for {agent}:")
    print(f"   Total investments: {len(investments)}")
    print()
    
    for category, investment in sorted(
        investments.items(),
        key=lambda x: x[1].score,
        reverse=True
    ):
        print(f"   {category:15} {investment.level.name:12} Score: {investment.score:5.1f}")


def example_find_experts():
    """Example: Find experts in a category."""
    print("\n" + "=" * 60)
    print("Example 3: Find Category Experts")
    print("=" * 60)
    
    tracker = AgentInvestmentTracker()
    
    category = "DevOps"
    experts = tracker.get_category_experts(
        category,
        min_level=InvestmentLevel.PRACTICING
    )
    
    print(f"\n🎯 {category} Experts:")
    for agent, investment in experts:
        print(f"   {agent:25} Level: {investment.level.name:12} Score: {investment.score:.1f}")


def example_investment_summary():
    """Example: Get detailed investment summary."""
    print("\n" + "=" * 60)
    print("Example 4: Investment Summary")
    print("=" * 60)
    
    tracker = AgentInvestmentTracker()
    
    agent = "engineer-master"
    summary = tracker.get_investment_summary(agent)
    
    print(f"\n📈 Summary for {agent}:")
    print(f"   Total investments: {summary['total_investments']}")
    print(f"   Categories: {', '.join(summary['categories'])}")
    print()
    print(f"   Expertise distribution:")
    for level, count in summary['expertise_levels'].items():
        print(f"      {level:12} {count} categories")
    
    if summary['most_cultivated']:
        mc = summary['most_cultivated']
        print(f"\n   Most cultivated: {mc['category']} ({mc['count']} events)")
    
    if summary['needs_cultivation']:
        print(f"\n   ⚠️  Needs cultivation:")
        for item in summary['needs_cultivation'][:3]:
            print(f"      {item['category']:15} (Last: {item['days_since']} days ago)")


def example_cultivation_opportunities():
    """Example: Find cultivation opportunities."""
    print("\n" + "=" * 60)
    print("Example 5: Cultivation Opportunities")
    print("=" * 60)
    
    tracker = AgentInvestmentTracker()
    
    # Sample learning items
    available_learnings = [
        {
            'title': 'Advanced Python Performance Optimization',
            'categories': ['Performance', 'Programming'],
            'score': 0.75,
            'id': 'learn-001'
        },
        {
            'title': 'Modern DevOps Practices',
            'categories': ['DevOps', 'Tools'],
            'score': 0.68,
            'id': 'learn-002'
        },
        {
            'title': 'Security Best Practices 2025',
            'categories': ['Security', 'Web'],
            'score': 0.82,
            'id': 'learn-003'
        },
        {
            'title': 'Database Performance Tuning',
            'categories': ['Database', 'Performance'],
            'score': 0.71,
            'id': 'learn-004'
        }
    ]
    
    agent = "accelerate-master"
    opportunities = tracker.find_cultivation_opportunities(
        agent_name=agent,
        available_learnings=available_learnings,
        top_n=3
    )
    
    print(f"\n🎯 Top cultivation opportunities for {agent}:")
    for i, opp in enumerate(opportunities, 1):
        invested = ', '.join(opp['invested_categories']) if opp['invested_categories'] else 'New area'
        print(f"\n   {i}. {opp['title']}")
        print(f"      Categories: {', '.join(opp['categories'])}")
        print(f"      Cultivation score: {opp['cultivation_score']:.2f}")
        print(f"      Investment status: {invested}")


def example_batch_recording():
    """Example: Batch record cultivation across categories."""
    print("\n" + "=" * 60)
    print("Example 6: Batch Cultivation Recording")
    print("=" * 60)
    
    tracker = AgentInvestmentTracker()
    
    # Record work that spans multiple categories
    categories = ["Programming", "DevOps", "Tools"]
    investments = record_learning_work(
        agent_name="engineer-master",
        categories=categories,
        learning_id="ci-pipeline-implementation",
        impact=0.75,
        tracker=tracker
    )
    
    print(f"\n✅ Recorded cultivation across {len(categories)} categories:")
    for investment in investments:
        print(f"   {investment.category:15} New score: {investment.score:.1f}")


def example_decay_application():
    """Example: Apply time-based decay."""
    print("\n" + "=" * 60)
    print("Example 7: Apply Investment Decay")
    print("=" * 60)
    
    tracker = AgentInvestmentTracker()
    
    stats = tracker.apply_decay()
    
    print(f"\n⏰ Decay applied:")
    print(f"   Agents processed: {stats['agents_processed']}")
    print(f"   Investments decayed: {stats['investments_decayed']}")
    print(f"   Investments removed: {stats['investments_removed']}")


def example_helper_functions():
    """Example: Use convenience helper functions."""
    print("\n" + "=" * 60)
    print("Example 8: Helper Functions")
    print("=" * 60)
    
    # Find top agents for a task
    category = "Security"
    top_agents = get_top_agents_for_category(
        category,
        min_level=InvestmentLevel.LEARNING
    )
    
    print(f"\n🔍 Best agents for {category} tasks:")
    for i, agent in enumerate(top_agents[:5], 1):
        print(f"   {i}. {agent}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Agent Investment Tracker - Usage Examples")
    print("Created by: @organize-guru")
    print("=" * 60)
    
    examples = [
        example_basic_cultivation,
        example_agent_portfolio,
        example_find_experts,
        example_investment_summary,
        example_cultivation_opportunities,
        example_batch_recording,
        example_decay_application,
        example_helper_functions
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {example_func.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
