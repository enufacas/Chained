#!/usr/bin/env python3
"""
Lazy Evaluation Integration Example

Demonstrates integration of lazy-workflow-evaluator with existing Chained tools:
- workflow-orchestrator.py integration
- dependency-flow-analyzer.py integration
- Real-world workflow optimization examples

Created by: @investigate-champion
Purpose: Show practical lazy evaluation patterns in the Chained ecosystem
"""

import os
import sys
import time
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib.util

# Load lazy evaluator
spec = importlib.util.spec_from_file_location(
    "lazy_workflow_evaluator",
    Path(__file__).parent.parent / "lazy-workflow-evaluator.py"
)
evaluator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator_module)

EvaluationEngine = evaluator_module.EvaluationEngine


class WorkflowOptimizer:
    """
    Wraps existing workflows with lazy evaluation.
    
    This class shows how to integrate lazy evaluation into the existing
    Chained workflow infrastructure without major refactoring.
    """
    
    def __init__(self, cache_dir: str = None):
        """Initialize optimizer with lazy evaluation engine"""
        self.engine = EvaluationEngine(cache_dir=cache_dir)
        self.workflow_registry = {}
    
    def register_expensive_workflow(self, name: str, workflow_fn, 
                                   dependencies=None, cache_ttl=3600):
        """
        Register a workflow that should be lazily evaluated.
        
        Args:
            name: Workflow identifier
            workflow_fn: Function to execute workflow
            dependencies: List of dependency workflow names
            cache_ttl: Cache time-to-live in seconds
        """
        self.workflow_registry[name] = {
            'function': workflow_fn,
            'dependencies': dependencies or [],
            'cache_ttl': cache_ttl
        }
        
        self.engine.register_workflow(
            node_id=name,
            compute_fn=workflow_fn,
            dependencies=dependencies or [],
            cache_ttl=cache_ttl,
            metadata={'type': 'workflow'}
        )
    
    def run_workflow(self, name: str, force_refresh: bool = False):
        """
        Run a workflow with lazy evaluation.
        
        Args:
            name: Workflow to run
            force_refresh: Skip cache and re-compute
            
        Returns:
            Workflow result
        """
        if name not in self.workflow_registry:
            raise ValueError(f"Workflow '{name}' not registered")
        
        return self.engine.evaluate(name, force=force_refresh)
    
    def get_performance_report(self):
        """Get performance metrics for all workflows"""
        return {
            'metrics': self.engine.get_metrics(),
            'summary': self.engine.get_summary(),
            'graph': self.engine.visualize_graph()
        }


def example_1_simple_caching():
    """Example 1: Simple workflow caching"""
    print("\n" + "="*70)
    print("Example 1: Simple Workflow Caching")
    print("="*70 + "\n")
    
    optimizer = WorkflowOptimizer()
    
    # Simulate expensive API call
    call_count = [0]
    
    def fetch_github_data():
        """Simulate fetching data from GitHub API"""
        call_count[0] += 1
        print(f"  🌐 API Call #{call_count[0]}: Fetching from GitHub...")
        time.sleep(0.5)  # Simulate network delay
        return {
            'repos': ['repo1', 'repo2', 'repo3'],
            'stars': 150,
            'timestamp': time.time()
        }
    
    # Register workflow with 1-hour cache
    optimizer.register_expensive_workflow(
        'fetch-github',
        fetch_github_data,
        cache_ttl=3600
    )
    
    # First call - hits API
    print("First call (should hit API):")
    result1 = optimizer.run_workflow('fetch-github')
    print(f"  ✅ Got {len(result1['repos'])} repos\n")
    
    # Second call - uses cache
    print("Second call (should use cache):")
    result2 = optimizer.run_workflow('fetch-github')
    print(f"  ✅ Got {len(result2['repos'])} repos\n")
    
    # Verify caching worked
    print(f"API calls made: {call_count[0]}")
    print(f"Expected: 1 (second call used cache)")
    
    # Show performance
    report = optimizer.get_performance_report()
    print(f"\nCache hit rate: {report['summary']['cache_hit_rate']:.1%}")


def example_2_dependency_chain():
    """Example 2: Workflow dependency chain"""
    print("\n" + "="*70)
    print("Example 2: Workflow Dependency Chain")
    print("="*70 + "\n")
    
    optimizer = WorkflowOptimizer()
    
    # Step 1: Fetch raw data
    def fetch_data():
        print("  📥 Fetching raw data...")
        time.sleep(0.3)
        return {'values': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    
    # Step 2: Clean and transform (depends on fetch)
    def clean_data(fetch):  # Parameter name must match dependency ID
        print("  🧹 Cleaning data...")
        time.sleep(0.2)
        values = fetch['values']
        return {'clean_values': [v for v in values if v % 2 == 0]}
    
    # Step 3: Analyze (depends on clean)
    def analyze_data(clean):  # Parameter name must match dependency ID
        print("  📊 Analyzing data...")
        time.sleep(0.2)
        values = clean['clean_values']
        return {
            'count': len(values),
            'sum': sum(values),
            'avg': sum(values) / len(values)
        }
    
    # Step 4: Generate report (depends on analyze)
    def generate_report(analyze):  # Parameter name must match dependency ID
        print("  📝 Generating report...")
        time.sleep(0.1)
        return f"Analysis Report: {analyze['count']} items, avg={analyze['avg']:.1f}"
    
    # Register workflows with dependencies
    optimizer.register_expensive_workflow('fetch', fetch_data, cache_ttl=300)
    optimizer.register_expensive_workflow('clean', clean_data, 
                                         dependencies=['fetch'], cache_ttl=300)
    optimizer.register_expensive_workflow('analyze', analyze_data,
                                         dependencies=['clean'], cache_ttl=300)
    optimizer.register_expensive_workflow('report', generate_report,
                                         dependencies=['analyze'], cache_ttl=300)
    
    # First run - everything executes
    print("First run (all steps execute):")
    result1 = optimizer.run_workflow('report')
    print(f"  ✅ {result1}\n")
    
    # Second run - everything cached
    print("Second run (all steps cached):")
    result2 = optimizer.run_workflow('report')
    print(f"  ✅ {result2}\n")
    
    # Show dependency graph
    print("Dependency Graph:")
    print(optimizer.engine.visualize_graph())


def example_3_conditional_evaluation():
    """Example 3: Conditional workflow evaluation"""
    print("\n" + "="*70)
    print("Example 3: Conditional Evaluation (Only What's Needed)")
    print("="*70 + "\n")
    
    optimizer = WorkflowOptimizer()
    
    # These workflows are expensive but may not be needed
    def expensive_ml_training():
        print("  🤖 Training ML model (expensive!)...")
        time.sleep(1.0)
        return {'model': 'trained', 'accuracy': 0.95}
    
    def quick_analysis():
        print("  ⚡ Quick analysis...")
        time.sleep(0.1)
        return {'result': 'quick_result'}
    
    def generate_simple_report(quick):  # Parameter matches dependency ID
        print("  📝 Simple report...")
        return f"Report: {quick['result']}"
    
    def generate_advanced_report(quick, ml_training):  # Parameters match dependency IDs
        print("  📝 Advanced report...")
        return f"Report: {quick['result']}, ML: {ml_training['accuracy']}"
    
    # Register workflows
    optimizer.register_expensive_workflow('ml_training', expensive_ml_training, cache_ttl=7200)
    optimizer.register_expensive_workflow('quick', quick_analysis, cache_ttl=300)
    optimizer.register_expensive_workflow('simple_report', generate_simple_report,
                                         dependencies=['quick'], cache_ttl=300)
    optimizer.register_expensive_workflow('advanced_report', generate_advanced_report,
                                         dependencies=['quick', 'ml_training'], cache_ttl=300)
    
    # Run simple report - ML training NOT executed
    print("Running simple report (ML training should NOT run):")
    result1 = optimizer.run_workflow('simple_report')
    print(f"  ✅ {result1}\n")
    
    # Run advanced report - NOW ML training executes
    print("Running advanced report (ML training should run now):")
    result2 = optimizer.run_workflow('advanced_report')
    print(f"  ✅ {result2}\n")
    
    print("📊 This demonstrates lazy evaluation: expensive_ml_training")
    print("   only executed when advanced-report needed it!")


def example_4_workflow_orchestrator_integration():
    """Example 4: Integration with workflow orchestrator patterns"""
    print("\n" + "="*70)
    print("Example 4: Workflow Orchestrator Integration")
    print("="*70 + "\n")
    
    optimizer = WorkflowOptimizer()
    
    # Simulate workflow-orchestrator.py patterns
    def check_api_quota():
        """Check GitHub API quota"""
        print("  🔍 Checking API quota...")
        time.sleep(0.1)
        return {'remaining': 4500, 'limit': 5000}
    
    def calculate_burn_rate(quota_check):  # Parameter matches dependency ID
        """Calculate API burn rate"""
        print("  📉 Calculating burn rate...")
        time.sleep(0.1)
        return {'burn_rate': (quota_check['limit'] - quota_check['remaining']) / 24.0}
    
    def recommend_schedule(burn_rate):  # Parameter matches dependency ID
        """Recommend workflow schedule based on burn rate"""
        print("  🎯 Recommending schedule...")
        time.sleep(0.1)
        rate = burn_rate['burn_rate']
        
        if rate < 50:
            mode = 'aggressive'
        elif rate < 150:
            mode = 'normal'
        else:
            mode = 'conservative'
        
        return {'mode': mode, 'burn_rate': rate}
    
    # Register workflows (simulating orchestrator logic)
    optimizer.register_expensive_workflow('quota_check', check_api_quota, cache_ttl=300)
    optimizer.register_expensive_workflow('burn_rate', calculate_burn_rate,
                                         dependencies=['quota_check'], cache_ttl=300)
    optimizer.register_expensive_workflow('schedule', recommend_schedule,
                                         dependencies=['burn_rate'], cache_ttl=300)
    
    # Multiple calls to get schedule - only computes once
    print("Multiple schedule checks (should cache):")
    for i in range(3):
        result = optimizer.run_workflow('schedule')
        print(f"  Check #{i+1}: Mode={result['mode']}, Burn Rate={result['burn_rate']:.1f}")
    
    # Show performance improvement
    report = optimizer.get_performance_report()
    summary = report['summary']
    
    print(f"\n📊 Performance Summary:")
    print(f"  Total evaluations: {summary['evaluated_nodes']}")
    print(f"  Cache hits: {summary['cache_hits']}")
    print(f"  Cache hit rate: {summary['cache_hit_rate']:.1%}")
    print(f"  Total time: {summary['total_evaluation_time']:.3f}s")
    print(f"  Avg time per eval: {summary['avg_evaluation_time']:.3f}s")


def main():
    """Run all integration examples"""
    print("\n" + "="*70)
    print("🚀 Lazy Evaluation Integration Examples")
    print("   Created by: @investigate-champion")
    print("="*70)
    
    try:
        example_1_simple_caching()
        example_2_dependency_chain()
        example_3_conditional_evaluation()
        example_4_workflow_orchestrator_integration()
        
        print("\n" + "="*70)
        print("✅ All integration examples completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
