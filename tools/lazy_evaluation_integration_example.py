#!/usr/bin/env python3
"""
Integration Example: Lazy Evaluation with Workflow Orchestrator

Demonstrates how the lazy evaluation system integrates with existing
workflow orchestration for optimized resource usage.
"""

import sys
import os
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from lazy_evaluation_system import LazyEvaluationSystem


def analyze_workflow_changes(workflows_dir: str = '.github/workflows'):
    """
    Example: Analyze impact of workflow changes before modification.
    
    This demonstrates how the orchestrator can use lazy evaluation
    to understand dependencies without loading all workflows.
    """
    print("=" * 70)
    print("🔍 Workflow Change Impact Analysis (Lazy Evaluation)")
    print("=" * 70)
    
    # Initialize lazy evaluation system
    system = LazyEvaluationSystem(workflows_dir)
    system.initialize()
    
    # Workflows that might be modified by orchestrator
    # Use actual workflow names from YAML 'name' field
    all_workflows = list(system.dependency_graph.nodes.keys())
    critical_workflows = [
        name for name in all_workflows
        if any(keyword in name.lower() for keyword in ['learn', 'idea', 'agent', 'spawner'])
    ][:4]  # Take first 4 matches
    
    print(f"\n📋 Analyzing impact of changes to {len(critical_workflows)} workflows...\n")
    
    for workflow in critical_workflows:
        # Get impact WITHOUT loading all workflows
        impact = system.get_impact_analysis(workflow)
        
        if impact:
            print(f"📊 {workflow}")
            print(f"   Direct dependents: {len(impact['direct_dependents'])}")
            print(f"   Total affected: {impact['total_affected']}")
            
            if impact['affected_workflows']:
                print(f"   Affected workflows:")
                for affected in impact['affected_workflows'][:3]:
                    print(f"     • {affected}")
                if len(impact['affected_workflows']) > 3:
                    print(f"     ... and {len(impact['affected_workflows']) - 3} more")
            print()
    
    # Show resource savings
    metrics = system.get_system_metrics()
    print("\n💰 Resource Savings from Lazy Evaluation:")
    print(f"   Lazy savings: {metrics['efficiency']['lazy_savings']:.1%}")
    print(f"   Workflows analyzed: {metrics['system']['evaluated_workflows']}")
    print(f"   Workflows loaded: {metrics['system']['loaded_workflows']}")
    print(f"   Total workflows: {metrics['system']['total_workflows']}")


def optimize_workflow_schedule(workflows_dir: str = '.github/workflows'):
    """
    Example: Optimize workflow schedules using dependency analysis.
    
    Shows how to use critical path analysis to understand
    workflow execution order without loading all content.
    """
    print("\n" + "=" * 70)
    print("⚡ Workflow Schedule Optimization (Lazy Evaluation)")
    print("=" * 70)
    
    system = LazyEvaluationSystem(workflows_dir)
    system.initialize()
    
    # Key workflows for the autonomous system - use actual workflow names
    all_workflows = list(system.dependency_graph.nodes.keys())
    key_workflows = [w for w in all_workflows if 'Agent' in w or 'Learn' in w or 'Idea' in w][:3]
    
    print(f"\n📈 Analyzing critical paths for {len(key_workflows)} workflows...\n")
    
    for workflow in key_workflows:
        # Get critical path (longest dependency chain)
        path = system.get_critical_path(workflow)
        
        print(f"🎯 {workflow}")
        print(f"   Critical path length: {len(path)}")
        print(f"   Dependencies: {len(path) - 1}")
        
        if len(path) > 1:
            print(f"   Execution order:")
            for i, step in enumerate(path, 1):
                print(f"     {i}. {step}")
        print()
    
    # Show evaluation efficiency
    metrics = system.get_system_metrics()
    print("\n⚡ Evaluation Efficiency:")
    print(f"   Evaluation ratio: {metrics['efficiency']['evaluation_ratio']:.1%}")
    print(f"   Cache hit rate: {metrics['efficiency']['cache_hit_rate']:.1%}")


def batch_workflow_analysis(workflows_dir: str = '.github/workflows'):
    """
    Example: Batch analyze multiple workflows efficiently.
    
    Demonstrates efficient batch processing with lazy evaluation.
    """
    print("\n" + "=" * 70)
    print("📦 Batch Workflow Analysis (Lazy Evaluation)")
    print("=" * 70)
    
    system = LazyEvaluationSystem(workflows_dir)
    system.initialize()
    
    # Workflows to analyze - use actual workflow names
    all_workflows = list(system.dependency_graph.nodes.keys())
    workflows = all_workflows[:4] if len(all_workflows) >= 4 else all_workflows
    
    print(f"\n🔄 Batch analyzing {len(workflows)} workflows...\n")
    
    # Batch evaluation (efficient)
    results = system.evaluate_batch(workflows, load_dependencies=False)
    
    print(f"✅ Batch Analysis Results:")
    print(f"   Total: {results['total']}")
    print(f"   Successful: {results['successful']}")
    print()
    
    # Show individual results
    for result in results['results']:
        if result['success']:
            node = result['node']
            print(f"   📄 {node['name']}")
            print(f"      Triggers: {', '.join(node['triggers'][:3])}")
            print(f"      Dependencies: {len(node['dependencies'])}")
            print(f"      Dependents: {len(node['dependents'])}")
            print(f"      Schedule: {node['schedule'] or 'manual'}")
            print(f"      Eval time: {result['evaluation_time_ms']:.2f}ms")
            print()
    
    # Overall metrics
    metrics = system.get_system_metrics()
    print(f"📊 Overall System Metrics:")
    print(f"   Total evaluation time: {metrics['system']['evaluation_time_ms']:.2f}ms")
    if results['successful'] > 0:
        print(f"   Avg time per workflow: {metrics['system']['evaluation_time_ms'] / results['successful']:.2f}ms")
    else:
        print(f"   Avg time per workflow: N/A (no successful evaluations)")


def demonstrate_caching_benefits(workflows_dir: str = '.github/workflows'):
    """
    Example: Demonstrate caching benefits with repeated access.
    
    Shows how lazy evaluation with caching improves performance
    on repeated workflow access.
    """
    print("\n" + "=" * 70)
    print("💾 Caching Benefits (Lazy Evaluation)")
    print("=" * 70)
    
    system = LazyEvaluationSystem(workflows_dir)
    system.initialize()
    
    # Use first available workflow
    all_workflows = list(system.dependency_graph.nodes.keys())
    workflow = all_workflows[0] if all_workflows else 'agent-spawner'
    
    print(f"\n🔄 Evaluating '{workflow}' multiple times...\n")
    
    # First evaluation (cold)
    result1 = system.evaluate_workflow(workflow, load_dependencies=True)
    time1 = result1['evaluation_time_ms']
    
    # Second evaluation (cached)
    result2 = system.evaluate_workflow(workflow, load_dependencies=True)
    time2 = result2['evaluation_time_ms']
    
    # Third evaluation (cached)
    result3 = system.evaluate_workflow(workflow, load_dependencies=True)
    time3 = result3['evaluation_time_ms']
    
    print(f"📈 Performance Comparison:")
    print(f"   1st eval (cold): {time1:.2f}ms")
    print(f"   2nd eval (cached): {time2:.2f}ms")
    print(f"   3rd eval (cached): {time3:.2f}ms")
    
    if time1 > 0:
        speedup2 = time1 / max(time2, 0.01)
        speedup3 = time1 / max(time3, 0.01)
        print(f"\n⚡ Speedup from caching:")
        print(f"   2nd eval: {speedup2:.1f}x faster")
        print(f"   3rd eval: {speedup3:.1f}x faster")
    
    # Show cache metrics
    metrics = system.get_system_metrics()
    print(f"\n💾 Cache Statistics:")
    print(f"   Cache hit rate: {metrics['efficiency']['cache_hit_rate']:.1%}")
    print(f"   Total loads: {metrics['loader']['total_loads']}")
    print(f"   Cache hits: {metrics['loader']['cache_hits']}")


def main():
    """Run all integration examples."""
    print("\n")
    print("🚀 Lazy Evaluation System - Integration Examples")
    print("=" * 70)
    print("\nThese examples demonstrate how @investigate-champion's lazy")
    print("evaluation system integrates with existing workflows for")
    print("optimized resource usage in the Chained autonomous AI ecosystem.")
    print()
    
    workflows_dir = os.path.join(
        os.path.dirname(__file__),
        '..',
        '.github',
        'workflows'
    )
    
    try:
        # Example 1: Impact Analysis
        analyze_workflow_changes(workflows_dir)
        
        # Example 2: Schedule Optimization
        optimize_workflow_schedule(workflows_dir)
        
        # Example 3: Batch Analysis
        batch_workflow_analysis(workflows_dir)
        
        # Example 4: Caching Benefits
        demonstrate_caching_benefits(workflows_dir)
        
        print("\n" + "=" * 70)
        print("✅ All integration examples completed successfully!")
        print("=" * 70)
        print("\nKey Takeaways:")
        print("• Lazy evaluation reduces resource usage significantly")
        print("• Impact analysis possible without loading all workflows")
        print("• Caching improves performance on repeated access")
        print("• Batch operations are efficient with lazy loading")
        print("• System scales well with large workflow collections")
        print("\n🎯 Ready for production integration with workflow orchestrator!")
        print()
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
