#!/usr/bin/env python3
"""
Integration Example: Agent Investment Tracker + Agent Learning Matcher

Demonstrates how to integrate the investment tracker with the learning matcher
to create a complete agent specialization and learning system.

Created by: @organize-guru
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent_investment_tracker import (
    AgentInvestmentTracker,
    InvestmentLevel,
    record_learning_work
)
from agent_learning_matcher import AgentLearningMatcher


def integrated_workflow_example():
    """
    Complete workflow: Match -> Cultivate -> Track -> Recommend
    """
    print("=" * 70)
    print("INTEGRATED WORKFLOW: Agent Learning + Investment Tracking")
    print("=" * 70)
    
    # Initialize both systems
    matcher = AgentLearningMatcher()
    tracker = AgentInvestmentTracker()
    
    agent_name = "accelerate-master"
    
    # Step 1: Get learning recommendations based on agent specialization
    print(f"\n📚 Step 1: Get learning recommendations for {agent_name}")
    print("-" * 70)
    
    # Get agent info directly from matcher
    agent_info = matcher.agents[agent_name]
    print(f"   Agent specialization: {', '.join(agent_info['primary_categories'])}")
    print(f"   Focus areas: {', '.join(agent_info['focus_areas'])}")
    
    # Step 2: Find cultivation opportunities based on existing investments
    print(f"\n🎯 Step 2: Find cultivation opportunities")
    print("-" * 70)
    
    # Get agent's current investments
    investments = tracker.get_agent_investments(agent_name)
    print(f"   Current investments:")
    for category, inv in sorted(investments.items(), key=lambda x: x[1].score, reverse=True):
        print(f"      {category:15} {inv.level.name:12} Score: {inv.score:5.1f}")
    
    # Create sample learnings (in real scenario, these come from knowledge.json)
    sample_learnings = [
        {
            'title': 'Advanced Database Performance Tuning',
            'categories': ['Database', 'Performance'],
            'score': 0.85,
            'id': 'learn-db-perf-001'
        },
        {
            'title': 'Modern Python Optimization Techniques',
            'categories': ['Programming', 'Performance'],
            'score': 0.78,
            'id': 'learn-py-opt-001'
        },
        {
            'title': 'Distributed Systems Performance',
            'categories': ['Performance', 'DevOps'],
            'score': 0.82,
            'id': 'learn-dist-perf-001'
        }
    ]
    
    opportunities = tracker.find_cultivation_opportunities(
        agent_name=agent_name,
        available_learnings=sample_learnings,
        top_n=3
    )
    
    print(f"\n   Top cultivation opportunities:")
    for i, opp in enumerate(opportunities, 1):
        invested = ', '.join(opp['invested_categories']) if opp['invested_categories'] else 'New area'
        print(f"   {i}. {opp['title']}")
        print(f"      Cultivation score: {opp['cultivation_score']:.2f} | Status: {invested}")
    
    # Step 3: Simulate agent working on a learning
    print(f"\n💼 Step 3: Agent works on selected learning")
    print("-" * 70)
    
    selected_learning = opportunities[0]
    print(f"   Working on: {selected_learning['title']}")
    print(f"   Categories: {', '.join(selected_learning['categories'])}")
    
    # Record cultivation with high impact (learned a lot!)
    investments = record_learning_work(
        agent_name=agent_name,
        categories=selected_learning['categories'],
        learning_id=selected_learning['id'],
        impact=0.8,  # High impact work
        tracker=tracker
    )
    
    print(f"\n   ✅ Cultivation recorded across {len(investments)} categories:")
    for inv in investments:
        print(f"      {inv.category:15} New level: {inv.level.name:12} Score: {inv.score:5.1f}")
    
    # Step 4: Track progress and identify next steps
    print(f"\n📊 Step 4: Review investment portfolio and next steps")
    print("-" * 70)
    
    summary = tracker.get_investment_summary(agent_name)
    
    print(f"\n   Portfolio summary:")
    print(f"      Total investments: {summary['total_investments']}")
    print(f"      Expertise levels: {summary['expertise_levels']}")
    
    if summary['most_cultivated']:
        mc = summary['most_cultivated']
        print(f"      Most cultivated: {mc['category']} ({mc['count']} events)")
    
    if summary['needs_cultivation']:
        print(f"\n   ⚠️  Categories needing cultivation:")
        for item in summary['needs_cultivation'][:3]:
            print(f"      {item['category']:15} Last: {item['days_since']} days ago")
    
    print("\n" + "=" * 70)


def agent_specialization_development():
    """
    Track how an agent develops specialization over time.
    """
    print("\n" + "=" * 70)
    print("AGENT SPECIALIZATION DEVELOPMENT")
    print("=" * 70)
    
    tracker = AgentInvestmentTracker()
    
    agent = "secure-specialist"
    
    print(f"\n🔒 Tracking {agent}'s specialization journey")
    print("-" * 70)
    
    # Get current state
    investments = tracker.get_agent_investments(agent)
    
    print(f"\n   Current expertise:")
    for category, inv in sorted(investments.items(), key=lambda x: x[1].score, reverse=True):
        days_since = "Unknown"
        if inv.last_cultivated:
            from datetime import datetime
            last = datetime.fromisoformat(inv.last_cultivated)
            days = (datetime.now() - last).days
            days_since = f"{days} days ago"
        
        print(f"      {category:15} {inv.level.name:12} Score: {inv.score:5.1f} | Last: {days_since}")
    
    # Find categories to deepen expertise
    print(f"\n   🎯 Recommended focus areas:")
    
    # Categories with existing investment that could be deepened
    for category, inv in investments.items():
        if inv.level.value < InvestmentLevel.EXPERT.value:
            events_to_next = "varies"
            if inv.level == InvestmentLevel.PROFICIENT:
                events_to_next = "~5-10 more events"
            elif inv.level == InvestmentLevel.PRACTICING:
                events_to_next = "~10-20 more events"
            
            print(f"      {category:15} → Next level: {events_to_next}")


def collaborative_learning():
    """
    Use investment data to identify collaboration opportunities.
    """
    print("\n" + "=" * 70)
    print("COLLABORATIVE LEARNING OPPORTUNITIES")
    print("=" * 70)
    
    tracker = AgentInvestmentTracker()
    
    category = "DevOps"
    
    print(f"\n🤝 Finding collaboration opportunities in {category}")
    print("-" * 70)
    
    # Get all experts
    all_experts = tracker.get_category_experts(
        category,
        min_level=InvestmentLevel.CURIOUS  # Get all levels
    )
    
    if len(all_experts) >= 2:
        print(f"\n   Expert agents:")
        for agent, inv in all_experts[:3]:
            if inv.level.value >= InvestmentLevel.PROFICIENT.value:
                print(f"      {agent:25} {inv.level.name:12} ({inv.score:.1f})")
        
        print(f"\n   Learning agents:")
        for agent, inv in all_experts:
            if inv.level.value < InvestmentLevel.PROFICIENT.value:
                print(f"      {agent:25} {inv.level.name:12} ({inv.score:.1f})")
        
        print(f"\n   💡 Collaboration suggestion:")
        if len(all_experts) > 0:
            expert = all_experts[0][0]
            learners = [a for a, i in all_experts[1:] if i.level.value < InvestmentLevel.PROFICIENT.value]
            if learners:
                print(f"      {expert} (expert) could mentor {learners[0]} (learning)")


def main():
    """Run all integration examples."""
    try:
        integrated_workflow_example()
        agent_specialization_development()
        collaborative_learning()
        
        print("\n" + "=" * 70)
        print("✅ Integration examples completed successfully!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
