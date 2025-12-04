#!/usr/bin/env python3
"""
Demo: Enhanced Sub-Agent Spawning

Demonstrates the intelligent sub-agent spawning system created by @create-botter.
Shows parent selection, performance learning, and enhanced spawning in action.

Run: python3 tools/demo_enhanced_spawning.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from intelligent_parent_selector import IntelligentParentSelector, ParentScore
    from subagent_performance_learner import SubAgentPerformanceLearner, SubAgentAnalysis
    from registry_manager import RegistryManager
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)


def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def demo_intelligent_parent_selection():
    """Demo: Intelligent parent selection"""
    print_header("🎯 DEMO 1: Intelligent Parent Selection")
    
    print("Creating parent selector...")
    selector = IntelligentParentSelector()
    
    # Select parents for different specializations
    specializations = ['engineer-master', 'secure-specialist', 'create-botter']
    
    for spec in specializations:
        print(f"\n🔍 Selecting parents for: {spec}")
        print("-" * 70)
        
        try:
            parents = selector.select_parent(
                specialization=spec,
                top_n=3
            )
            
            if not parents:
                print(f"   ⚠️  No suitable parents found")
                continue
            
            for i, parent in enumerate(parents, 1):
                print(f"\n   #{i} {parent.agent_name}")
                print(f"      ID: {parent.agent_id}")
                print(f"      Total Score: {parent.total_score:.1f}/100")
                print(f"      Performance: {parent.performance_score:.1f}/100")
                print(f"      Workload: {parent.workload_score:.1f}/100")
                print(f"      Experience: {parent.experience_score:.1f}/100")
                print(f"      Current Workload: {parent.current_workload} items")
                print(f"      Sub-Agents: {parent.sub_agents_count}")
                print(f"      💡 {parent.recommendation}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Parent selection demo complete")


def demo_performance_learning():
    """Demo: Performance learning from sub-agents"""
    print_header("🧠 DEMO 2: Performance Learning")
    
    print("Creating performance learner...")
    learner = SubAgentPerformanceLearner()
    
    # Analyze sub-agents
    print("\n📊 Analyzing sub-agent performance...")
    analyses = learner.analyze_all_subagents()
    
    if not analyses:
        print("   ℹ️  No sub-agents found to analyze")
        print("   💡 This is normal for a new system")
    else:
        successful = [a for a in analyses if a.success]
        print(f"   Total sub-agents: {len(analyses)}")
        print(f"   Successful: {len(successful)} ({len(successful)/len(analyses)*100:.1f}%)")
        
        # Show examples
        print("\n   📋 Example sub-agents:")
        for analysis in analyses[:3]:
            status = "✅" if analysis.success else "❌"
            print(f"   {status} {analysis.agent_name}")
            print(f"      Lifetime: {analysis.lifetime_hours:.1f}h")
            print(f"      Contributions: {analysis.issues_resolved + analysis.prs_merged}")
            if analysis.failure_reason:
                print(f"      Failure: {analysis.failure_reason}")
    
    # Learn insights
    print("\n🔍 Learning insights from performance...")
    try:
        insights = learner.learn_from_performance()
        
        if len(analyses) < 5:
            print("   ℹ️  Insufficient data for insights (need 5+ sub-agents)")
            print("   💡 System will collect data as sub-agents spawn")
        else:
            print(f"   ✅ Generated {len(insights)} insights")
            
            for insight in insights[:3]:
                print(f"\n   📌 {insight.description}")
                print(f"      Type: {insight.insight_type}")
                print(f"      Confidence: {insight.confidence*100:.1f}%")
                print(f"      💡 {insight.recommendation}")
    except Exception as e:
        print(f"   ⚠️  Learning error: {e}")
    
    print("\n✅ Performance learning demo complete")


def demo_spawning_recommendations():
    """Demo: Get spawning recommendations"""
    print_header("🎯 DEMO 3: Spawning Recommendations")
    
    print("Creating performance learner...")
    learner = SubAgentPerformanceLearner()
    
    # Test different specializations and workloads
    scenarios = [
        ('secure-specialist', 8.5),
        ('engineer-master', 6.0),
        ('document-ninja', 4.5),
    ]
    
    for spec, workload in scenarios:
        print(f"\n🔍 Recommendation for: {spec}")
        print(f"   Current Workload: {workload:.1f} items/agent")
        print("-" * 70)
        
        try:
            rec = learner.get_spawning_recommendations(spec, workload)
            
            should_spawn = rec.get('should_spawn')
            if should_spawn is None:
                print("   ℹ️  No historical data available")
                print("   💡 System will make workload-only decision")
            else:
                spawn_text = "✅ YES" if should_spawn else "❌ NO"
                print(f"   Should Spawn: {spawn_text}")
                print(f"   Confidence: {rec['confidence']*100:.1f}%")
                print(f"   Recommended Count: {rec.get('recommended_count', 1)}")
                
                if rec.get('optimal_threshold'):
                    print(f"   Optimal Threshold: {rec['optimal_threshold']:.1f}")
                if rec.get('success_rate'):
                    print(f"   Historical Success: {rec['success_rate']*100:.1f}%")
                
                print(f"\n   💬 {rec['reason']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Recommendations demo complete")


def demo_adaptive_weights():
    """Demo: Adaptive weight adjustment"""
    print_header("⚙️  DEMO 4: Adaptive Weight Adjustment")
    
    print("Creating parent selector...")
    selector = IntelligentParentSelector()
    
    # Show default weights
    print("📊 Default weights:")
    for factor, weight in selector.weights.items():
        print(f"   {factor}: {weight*100:.0f}%")
    
    # Test different system states
    states = [
        ('high_load', {'high_load': True}),
        ('new_system', {'new_system': True}),
        ('quality_focus', {'quality_focus': True}),
    ]
    
    for state_name, state_config in states:
        print(f"\n🔄 Adjusting for: {state_name}")
        selector.adjust_weights(state_config)
        
        print("   Updated weights:")
        for factor, weight in selector.weights.items():
            print(f"   {factor}: {weight*100:.0f}%")
        
        # Reset for next demo
        selector.weights = selector.DEFAULT_WEIGHTS.copy()
    
    print("\n✅ Adaptive weights demo complete")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  🚀 Enhanced Sub-Agent Spawning System Demo")
    print("     Created by @create-botter")
    print("=" * 70)
    
    print("\n💡 This demo showcases the intelligent sub-agent spawning features:")
    print("   1. Multi-criteria parent selection")
    print("   2. Performance learning from history")
    print("   3. Data-driven spawning recommendations")
    print("   4. Adaptive weight adjustment")
    
    print("\n⏱️  Starting demos...")
    
    try:
        # Demo 1: Parent selection
        demo_intelligent_parent_selection()
        
        # Demo 2: Performance learning
        demo_performance_learning()
        
        # Demo 3: Spawning recommendations
        demo_spawning_recommendations()
        
        # Demo 4: Adaptive weights
        demo_adaptive_weights()
        
        print_header("🎉 All Demos Complete!")
        
        print("📚 Learn more:")
        print("   • docs/ENHANCED_SUBAGENT_SPAWNING.md")
        print("   • tools/intelligent_parent_selector.py --help")
        print("   • tools/subagent_performance_learner.py --help")
        print("   • tools/enhanced_subagent_spawner.py --help")
        
        print("\n🚀 Try it yourself:")
        print("   python3 tools/enhanced_subagent_spawner.py --dry-run")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        raise


if __name__ == '__main__':
    main()
