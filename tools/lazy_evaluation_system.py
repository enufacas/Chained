#!/usr/bin/env python3
"""
Lazy Evaluation System for Workflow Dependencies

Integrates dependency graph analysis with lazy loading for optimal resource usage.
Main entry point for the lazy evaluation system.
"""

import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from workflow_dependency_graph import WorkflowDependencyGraph, WorkflowNode
from lazy_workflow_loader import LazyWorkflowLoader, LazyDependencyResolver


@dataclass
class EvaluationMetrics:
    """Tracks metrics for lazy evaluation system."""
    total_workflows: int = 0
    evaluated_workflows: int = 0
    loaded_workflows: int = 0
    cache_hits: int = 0
    total_loads: int = 0
    evaluation_time_ms: float = 0.0
    memory_saved_mb: float = 0.0
    
    def calculate_efficiency(self) -> Dict[str, float]:
        """Calculate efficiency metrics."""
        return {
            'evaluation_ratio': self.evaluated_workflows / max(self.total_workflows, 1),
            'load_ratio': self.loaded_workflows / max(self.total_workflows, 1),
            'cache_hit_rate': self.cache_hits / max(self.total_loads, 1),
            'lazy_savings': 1.0 - (self.loaded_workflows / max(self.total_workflows, 1))
        }


class LazyEvaluationSystem:
    """
    Comprehensive lazy evaluation system for workflow dependencies.
    
    This system provides:
    - Lazy dependency resolution: only evaluate when needed
    - Intelligent caching: avoid redundant computations
    - Dependency tracking: understand workflow relationships
    - Performance monitoring: track resource savings
    - On-demand loading: minimize I/O operations
    """
    
    def __init__(self, workflows_dir: str = ".github/workflows"):
        self.workflows_dir = workflows_dir
        
        # Core components
        self.loader = LazyWorkflowLoader(workflows_dir)
        self.dependency_graph = WorkflowDependencyGraph(workflows_dir)
        self.resolver = LazyDependencyResolver(self.loader)
        
        # Metrics
        self.metrics = EvaluationMetrics()
        self.evaluation_log: List[Dict[str, Any]] = []
        
        # Initialized flag
        self._initialized = False
    
    def initialize(self) -> None:
        """
        Initialize the system lazily.
        
        Only builds minimal index, doesn't load all workflows.
        """
        if self._initialized:
            return
        
        print("🚀 Initializing lazy evaluation system...")
        
        # Discover workflows (metadata only)
        self.loader.discover()
        self.metrics.total_workflows = len(self.loader.workflows)
        
        # Build dependency graph (minimal parsing)
        self.dependency_graph.build_graph()
        
        self._initialized = True
        print(f"✅ System initialized with {self.metrics.total_workflows} workflows")
    
    def evaluate_workflow(
        self,
        workflow_name: str,
        load_dependencies: bool = False,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate a workflow lazily with optional dependency loading.
        
        Args:
            workflow_name: Workflow to evaluate
            load_dependencies: Whether to load dependency content
            recursive: Include transitive dependencies
            
        Returns:
            Evaluation result with workflow info and dependencies
        """
        start_time = datetime.utcnow()
        
        # Lazy evaluate the dependency graph node
        node = self.dependency_graph.lazy_evaluate(workflow_name)
        if not node:
            return {
                'success': False,
                'error': f'Workflow not found: {workflow_name}'
            }
        
        self.metrics.evaluated_workflows += 1
        
        # Optionally load dependencies
        loaded_deps = []
        if load_dependencies:
            deps = self.resolver.get_dependencies(workflow_name, recursive=recursive)
            for dep in deps:
                content = self.loader.load_workflow(dep)
                if content:
                    loaded_deps.append(dep)
                    self.metrics.loaded_workflows += 1
        
        # Load the workflow itself if requested
        workflow_content = None
        if load_dependencies:
            workflow_content = self.loader.load_workflow(workflow_name)
            if workflow_content:
                self.metrics.loaded_workflows += 1
        
        # Calculate evaluation time
        end_time = datetime.utcnow()
        eval_time_ms = (end_time - start_time).total_seconds() * 1000
        self.metrics.evaluation_time_ms += eval_time_ms
        
        # Log evaluation
        self._log_evaluation(workflow_name, eval_time_ms, len(loaded_deps))
        
        result = {
            'success': True,
            'workflow': workflow_name,
            'node': {
                'name': node.name,
                'path': node.path,
                'triggers': node.triggers,
                'dependencies': list(node.dependencies),
                'dependents': list(node.dependents),
                'schedule': node.schedule,
                'is_loaded': node.is_loaded
            },
            'loaded_dependencies': loaded_deps,
            'evaluation_time_ms': eval_time_ms
        }
        
        if workflow_content:
            result['content'] = workflow_content
        
        return result
    
    def evaluate_batch(
        self,
        workflow_names: List[str],
        load_dependencies: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate multiple workflows efficiently.
        
        Args:
            workflow_names: List of workflows to evaluate
            load_dependencies: Whether to load dependencies
            
        Returns:
            Batch evaluation results
        """
        results = []
        
        for name in workflow_names:
            result = self.evaluate_workflow(name, load_dependencies=load_dependencies)
            results.append(result)
        
        return {
            'total': len(workflow_names),
            'successful': sum(1 for r in results if r.get('success')),
            'results': results
        }
    
    def get_critical_path(self, workflow_name: str) -> List[str]:
        """
        Get the critical path (longest dependency chain) for a workflow.
        
        This is useful for understanding bottlenecks without loading all content.
        """
        return self.dependency_graph.get_dependency_chain(workflow_name)
    
    def get_impact_analysis(self, workflow_name: str) -> Dict[str, Any]:
        """
        Analyze the impact of a workflow change.
        
        Returns all workflows that could be affected, without loading them.
        """
        # Get all dependents
        dependents = self.dependency_graph.get_dependent_chain(workflow_name)
        
        return {
            'workflow': workflow_name,
            'direct_dependents': list(
                self.dependency_graph.nodes[workflow_name].dependents
                if workflow_name in self.dependency_graph.nodes
                else []
            ),
            'total_affected': len(dependents),
            'affected_workflows': dependents
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        # Get loader metrics
        loader_metrics = self.loader.get_metrics()
        
        # Get graph stats
        graph_stats = self.dependency_graph.get_evaluation_stats()
        
        # Calculate efficiency
        efficiency = self.metrics.calculate_efficiency()
        
        return {
            'system': {
                'total_workflows': self.metrics.total_workflows,
                'evaluated_workflows': self.metrics.evaluated_workflows,
                'loaded_workflows': self.metrics.loaded_workflows,
                'evaluation_time_ms': self.metrics.evaluation_time_ms
            },
            'loader': loader_metrics,
            'graph': graph_stats,
            'efficiency': efficiency,
            'evaluation_log_size': len(self.evaluation_log)
        }
    
    def export_report(self, output_path: str) -> None:
        """Export comprehensive system report."""
        report = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'metrics': self.get_system_metrics(),
            'evaluation_log': self.evaluation_log,
            'workflows': {
                name: {
                    'name': node.name,
                    'dependencies': list(node.dependencies),
                    'dependents': list(node.dependents),
                    'is_loaded': node.is_loaded,
                    'schedule': node.schedule
                }
                for name, node in self.dependency_graph.nodes.items()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    def _log_evaluation(self, workflow_name: str, eval_time_ms: float, deps_loaded: int) -> None:
        """Log an evaluation event."""
        self.evaluation_log.append({
            'workflow': workflow_name,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'eval_time_ms': eval_time_ms,
            'dependencies_loaded': deps_loaded
        })


def main():
    """CLI interface for lazy evaluation system."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Lazy evaluation system for workflow dependencies'
    )
    parser.add_argument(
        '--workflows-dir',
        default='.github/workflows',
        help='Path to workflows directory'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize the system')
    
    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Evaluate a workflow')
    eval_parser.add_argument('workflow', help='Workflow name to evaluate')
    eval_parser.add_argument(
        '--load-deps',
        action='store_true',
        help='Load dependency content'
    )
    eval_parser.add_argument(
        '--recursive',
        action='store_true',
        help='Include transitive dependencies'
    )
    
    # Critical path command
    path_parser = subparsers.add_parser('critical-path', help='Get critical path')
    path_parser.add_argument('workflow', help='Workflow name')
    
    # Impact analysis command
    impact_parser = subparsers.add_parser('impact', help='Analyze workflow impact')
    impact_parser.add_argument('workflow', help='Workflow name')
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Show system metrics')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Export system report')
    report_parser.add_argument('output', help='Output file path')
    
    args = parser.parse_args()
    
    # Create system
    system = LazyEvaluationSystem(args.workflows_dir)
    
    # Execute command
    if args.command == 'init':
        system.initialize()
        print("✅ System initialized")
    
    elif args.command == 'evaluate':
        system.initialize()
        result = system.evaluate_workflow(
            args.workflow,
            load_dependencies=args.load_deps,
            recursive=args.recursive
        )
        
        if result['success']:
            print(f"\n✅ Evaluation successful")
            print(f"Workflow: {result['workflow']}")
            print(f"Dependencies: {len(result['node']['dependencies'])}")
            print(f"Dependents: {len(result['node']['dependents'])}")
            print(f"Evaluation time: {result['evaluation_time_ms']:.2f}ms")
            
            if result.get('loaded_dependencies'):
                print(f"Loaded dependencies: {len(result['loaded_dependencies'])}")
        else:
            print(f"❌ Evaluation failed: {result.get('error')}")
    
    elif args.command == 'critical-path':
        system.initialize()
        path = system.get_critical_path(args.workflow)
        print(f"\n🎯 Critical Path for {args.workflow}:")
        for i, workflow in enumerate(path, 1):
            print(f"  {i}. {workflow}")
    
    elif args.command == 'impact':
        system.initialize()
        impact = system.get_impact_analysis(args.workflow)
        print(f"\n📊 Impact Analysis for {impact['workflow']}:")
        print(f"Direct dependents: {len(impact['direct_dependents'])}")
        print(f"Total affected: {impact['total_affected']}")
        print(f"\nAffected workflows:")
        for workflow in impact['affected_workflows']:
            print(f"  • {workflow}")
    
    elif args.command == 'metrics':
        system.initialize()
        metrics = system.get_system_metrics()
        
        print("\n📈 Lazy Evaluation System Metrics:")
        print("\n System:")
        for key, value in metrics['system'].items():
            print(f"  {key}: {value}")
        
        print("\n Efficiency:")
        for key, value in metrics['efficiency'].items():
            print(f"  {key}: {value:.2%}")
    
    elif args.command == 'report':
        system.initialize()
        system.export_report(args.output)
        print(f"✅ Report exported to: {args.output}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
