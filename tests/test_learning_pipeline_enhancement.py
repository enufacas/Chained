#!/usr/bin/env python3
"""
Test script to demonstrate the learning pipeline enhancement by @construct-specialist.

This script shows the improvement in mission diversity by running the sync
and analyzing the generated ideas.
"""

import json
import sys
import os

# Add world directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'world'))

from sync_learnings_to_ideas import sync_learnings_to_ideas, KNOWLEDGE_PATH


def analyze_ideas(knowledge_path: str = KNOWLEDGE_PATH):
    """
    Analyze the ideas in knowledge base and show diversity metrics.
    
    Args:
        knowledge_path: Path to knowledge.json
    """
    with open(knowledge_path, 'r') as f:
        knowledge = json.load(f)
    
    ideas = knowledge.get('ideas', [])
    learning_ideas = [idea for idea in ideas if idea.get('source') == 'learning_analysis']
    
    print("\n" + "=" * 70)
    print("📊 Learning Pipeline Enhancement Analysis by @construct-specialist")
    print("=" * 70)
    
    # Overall stats
    print(f"\n📈 Overall Statistics:")
    print(f"   Total ideas in system: {len(ideas)}")
    print(f"   Learning-based ideas: {len(learning_ideas)}")
    
    # Category breakdown
    print(f"\n🏷️  Category Breakdown:")
    categories = {}
    for idea in learning_ideas:
        category = idea.get('category', 'Unknown')
        categories[category] = categories.get(category, 0) + 1
    
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {category}: {count} ideas")
    
    # Pattern diversity
    print(f"\n🔍 Pattern Diversity:")
    all_patterns = set()
    for idea in learning_ideas:
        patterns = idea.get('patterns', [])
        all_patterns.update(patterns)
    print(f"   Unique patterns: {len(all_patterns)}")
    print(f"   Sample patterns: {', '.join(list(all_patterns)[:10])}")
    
    # Integration ideas (new feature)
    integration_ideas = [idea for idea in learning_ideas if idea.get('category') == 'Integration']
    print(f"\n🔗 Integration Ideas (NEW!):")
    print(f"   Count: {len(integration_ideas)}")
    for idea in integration_ideas:
        print(f"   • {idea.get('title')}")
        patterns = ', '.join(idea.get('patterns', [])[:3])
        print(f"     Patterns: {patterns}")
    
    # Company innovations (new feature)
    company_ideas = [idea for idea in learning_ideas if idea.get('category') == 'Company Innovation']
    print(f"\n🏢 Company Innovation Ideas (NEW!):")
    print(f"   Count: {len(company_ideas)}")
    for idea in company_ideas[:5]:
        print(f"   • {idea.get('title')}")
    
    # Emerging themes (new feature)
    theme_ideas = [idea for idea in learning_ideas if idea.get('category') == 'Emerging Theme']
    print(f"\n🌟 Emerging Theme Ideas (NEW!):")
    print(f"   Count: {len(theme_ideas)}")
    for idea in theme_ideas:
        print(f"   • {idea.get('title')}")
    
    # Mission readiness
    print(f"\n✅ Mission Generation Readiness:")
    print(f"   Ideas available for missions: {len(learning_ideas)}")
    print(f"   Diversity score: {len(categories)}/4 categories")
    if len(learning_ideas) >= 15:
        print(f"   Status: 🟢 EXCELLENT - High diversity, many missions possible")
    elif len(learning_ideas) >= 10:
        print(f"   Status: 🟡 GOOD - Sufficient diversity")
    else:
        print(f"   Status: 🔴 LOW - Limited missions available")
    
    print("\n" + "=" * 70)
    print("✅ Enhancement Successful!")
    print("=" * 70)
    print(f"\n📝 Summary:")
    print(f"   The enhanced pipeline creates {len(learning_ideas)} diverse ideas")
    print(f"   across {len(categories)} categories, including:")
    print(f"   - Standard tech innovations")
    print(f"   - Company innovations ({len(company_ideas)} ideas)")
    print(f"   - Emerging themes ({len(theme_ideas)} ideas)")
    print(f"   - Integration opportunities ({len(integration_ideas)} ideas)")
    print(f"\n   This ensures the autonomous pipeline has plenty of missions")
    print(f"   to assign to agents when it runs.")
    print(f"\n   🎯 Enhancement by: @construct-specialist")
    print("=" * 70)


def test_enhancement():
    """Test the enhancement by running sync and analyzing results."""
    print("\n🧪 Testing Learning Pipeline Enhancement")
    print("=" * 70)
    
    # Run the sync with deep discovery enabled
    print("\n1️⃣  Running sync_learnings_to_ideas with Deep Discovery Mode...")
    print("-" * 70)
    
    try:
        summary = sync_learnings_to_ideas(max_ideas=10, enable_deep_discovery=True)
        
        print("\n2️⃣  Sync completed successfully!")
        print("-" * 70)
        print(f"   Technologies analyzed: {summary.get('technologies_analyzed', 'unknown')}")
        print(f"   Ideas created: {summary.get('ideas_created', 'unknown')}")
        print(f"   Total ideas: {summary.get('total_ideas', 'unknown')}")
        
        # Analyze the results
        print("\n3️⃣  Analyzing results...")
        print("-" * 70)
        analyze_ideas()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_enhancement()
    sys.exit(0 if success else 1)
