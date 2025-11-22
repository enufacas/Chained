#!/usr/bin/env python3
"""
🌌 Universal Truth Evaluator - Example Usage

Demonstrates various ways to use the Universal Truth Evaluator
for discovering and analyzing fundamental principles.

Run: python3 tools/example_truth_discovery.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.universal_truth_evaluator import UniversalTruthEvaluator


def example_basic_discovery():
    """Example 1: Basic truth discovery."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Truth Discovery")
    print("=" * 60)
    
    evaluator = UniversalTruthEvaluator()
    insights = evaluator.run_full_discovery()
    
    print(f"\n✅ Discovered {insights['total_truths']} truths")
    print(f"   Stable: {insights['stable_truths']}")
    print(f"   High Confidence: {insights['high_confidence_truths']}")


def example_query_specific_truths():
    """Example 2: Query specific types of truths."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Query Specific Truths")
    print("=" * 60)
    
    evaluator = UniversalTruthEvaluator()
    evaluator.run_full_discovery()
    
    # Find agent behavior truths
    agent_truths = [
        t for t in evaluator.truths.values()
        if t.category == 'agent_behavior'
    ]
    
    print(f"\n🤖 Agent Behavior Truths: {len(agent_truths)}")
    for truth in agent_truths:
        print(f"\n   {truth.truth_id}")
        print(f"   Statement: {truth.statement[:100]}...")
        print(f"   Confidence: {truth.confidence:.2f}")


def example_high_confidence_truths():
    """Example 3: Find high-confidence truths."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: High-Confidence Truths")
    print("=" * 60)
    
    evaluator = UniversalTruthEvaluator()
    evaluator.run_full_discovery()
    
    high_conf = [
        t for t in evaluator.truths.values()
        if t.confidence > 0.8
    ]
    
    print(f"\n⭐ Found {len(high_conf)} high-confidence truths:")
    for truth in high_conf:
        print(f"\n   [{truth.category}] {truth.confidence:.2f}")
        print(f"   {truth.statement}")


def example_truth_relationships():
    """Example 4: Explore truth relationships."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Truth Relationships")
    print("=" * 60)
    
    evaluator = UniversalTruthEvaluator()
    evaluator.run_full_discovery()
    
    connected = [
        t for t in evaluator.truths.values()
        if len(t.related_truths) > 0
    ]
    
    print(f"\n🔗 {len(connected)} truths are interconnected:")
    for truth in connected:
        print(f"\n   {truth.truth_id}")
        print(f"   Related to: {', '.join(truth.related_truths)}")


def example_truth_evolution():
    """Example 5: Track truth evolution."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Truth Evolution")
    print("=" * 60)
    
    evaluator = UniversalTruthEvaluator()
    evaluator.run_full_discovery()
    
    evolving = [
        t for t in evaluator.truths.values()
        if len(t.evolution_history) > 1
    ]
    
    print(f"\n📈 {len(evolving)} truths show evolution:")
    for truth in evolving:
        print(f"\n   {truth.truth_id}")
        print(f"   Evolution steps: {len(truth.evolution_history)}")
        print(f"   First observed: {truth.first_observed}")
        print(f"   Last validated: {truth.last_validated}")


def example_actionable_insights():
    """Example 6: Generate actionable insights."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Actionable Insights")
    print("=" * 60)
    
    evaluator = UniversalTruthEvaluator()
    insights = evaluator.run_full_discovery()
    
    print("\n💡 Recommendations:")
    for i, rec in enumerate(insights['recommendations'], 1):
        print(f"\n{i}. {rec[:150]}...")
    
    print("\n\n🔮 Meta-Observations:")
    for i, obs in enumerate(insights['meta_observations'], 1):
        print(f"\n{i}. {obs}")


def example_truth_validation():
    """Example 7: Validate a truth with new evidence."""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Truth Validation")
    print("=" * 60)
    
    evaluator = UniversalTruthEvaluator()
    evaluator.run_full_discovery()
    
    # Pick first truth
    if evaluator.truths:
        truth_id = list(evaluator.truths.keys())[0]
        truth = evaluator.truths[truth_id]
        
        print(f"\n📊 Validating: {truth_id}")
        print(f"   Initial confidence: {truth.confidence:.3f}")
        
        # Validate with new evidence
        is_valid, new_conf = evaluator.validate_truth(
            truth_id,
            {'validation_source': 'example', 'data': 'supporting evidence'}
        )
        
        print(f"   After validation: {new_conf:.3f}")
        print(f"   Evidence count: {truth.evidence_count}")


def example_custom_truth():
    """Example 8: Create a custom truth."""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Create Custom Truth")
    print("=" * 60)
    
    evaluator = UniversalTruthEvaluator()
    
    # Create custom truth
    custom = evaluator._create_or_update_truth(
        truth_id='custom_example',
        category='evolution',
        statement='Custom truth: The system exhibits emergent creativity in agent interactions',
        confidence=0.7,
        evidence={
            'observation': 'Novel solutions from agent collaboration',
            'frequency': 5,
            'sample_size': 10
        }
    )
    
    print(f"\n✨ Created custom truth:")
    print(f"   ID: {custom.truth_id}")
    print(f"   Statement: {custom.statement}")
    print(f"   Confidence: {custom.confidence}")
    
    # Save to disk
    evaluator._save_truths()
    print(f"\n💾 Saved to: {evaluator.truths_file}")


def example_category_analysis():
    """Example 9: Analyze truth distribution by category."""
    print("\n" + "=" * 60)
    print("EXAMPLE 9: Category Analysis")
    print("=" * 60)
    
    evaluator = UniversalTruthEvaluator()
    insights = evaluator.run_full_discovery()
    
    print("\n📊 Truth Distribution by Category:")
    for category, count in insights['category_distribution'].items():
        percentage = (count / insights['total_truths'] * 100) if insights['total_truths'] > 0 else 0
        print(f"   {category:20} {count:3} ({percentage:5.1f}%)")


def example_system_health():
    """Example 10: System health assessment using truths."""
    print("\n" + "=" * 60)
    print("EXAMPLE 10: System Health Assessment")
    print("=" * 60)
    
    evaluator = UniversalTruthEvaluator()
    insights = evaluator.run_full_discovery()
    
    # Calculate health metrics
    total = insights['total_truths']
    stable = insights['stable_truths']
    high_conf = insights['high_confidence_truths']
    
    stability_ratio = stable / total if total > 0 else 0
    confidence_ratio = high_conf / total if total > 0 else 0
    
    print("\n🏥 System Health Metrics:")
    print(f"   Stability Ratio:   {stability_ratio:.1%} {'✅' if stability_ratio > 0.7 else '⚠️'}")
    print(f"   Confidence Ratio:  {confidence_ratio:.1%} {'✅' if confidence_ratio > 0.5 else '⚠️'}")
    print(f"   Total Truths:      {total}")
    
    if stability_ratio > 0.7 and confidence_ratio > 0.5:
        print("\n✅ System showing healthy, predictable behavior")
    elif stability_ratio > 0.5:
        print("\n⚠️ System stable but needs confidence building")
    else:
        print("\n⚠️ System showing unstable patterns - investigate")


def main():
    """Run all examples."""
    print("\n🌌 Universal Truth Evaluator - Example Usage")
    print("=" * 60)
    
    examples = [
        example_basic_discovery,
        example_query_specific_truths,
        example_high_confidence_truths,
        example_truth_relationships,
        example_truth_evolution,
        example_actionable_insights,
        example_truth_validation,
        example_custom_truth,
        example_category_analysis,
        example_system_health
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {example_func.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("✨ All examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
