#!/usr/bin/env python3
"""
Workflow Dependency Graph Analyzer

Analyzes workflow dependencies and creates a dependency graph for lazy evaluation.
Part of the lazy evaluation system for workflow dependencies.
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class WorkflowNode:
    """Represents a workflow in the dependency graph."""
    name: str
    path: str
    triggers: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    schedule: Optional[str] = None
    is_loaded: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_evaluated: Optional[str] = None


class WorkflowDependencyGraph:
    """
    Analyzes and builds a dependency graph for GitHub Actions workflows.
    
    This enables lazy evaluation of workflow dependencies by:
    - Mapping workflow relationships
    - Identifying trigger chains
    - Tracking evaluation state
    - Supporting on-demand loading
    """
    
    def __init__(self, workflows_dir: str = ".github/workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.nodes: Dict[str, WorkflowNode] = {}
        self.evaluation_cache: Dict[str, Any] = {}
        
    def discover_workflows(self) -> List[Path]:
        """Discover all workflow files in the workflows directory."""
        if not self.workflows_dir.exists():
            return []
        
        workflow_files = []
        for ext in ["*.yml", "*.yaml"]:
            workflow_files.extend(self.workflows_dir.glob(ext))
        
        return sorted(workflow_files)
    
    def parse_workflow_triggers(self, workflow_data: Dict[str, Any]) -> List[str]:
        """Extract trigger types from workflow definition."""
        triggers = []
        on_config = workflow_data.get('on', {})
        
        if isinstance(on_config, str):
            triggers.append(on_config)
        elif isinstance(on_config, list):
            triggers.extend(on_config)
        elif isinstance(on_config, dict):
            triggers.extend(on_config.keys())
        
        return triggers
    
    def extract_workflow_dependencies(self, workflow_data: Dict[str, Any]) -> Set[str]:
        """
        Extract workflow dependencies by analyzing:
        - workflow_run triggers
        - workflow_call triggers
        - uses statements in jobs
        """
        dependencies = set()
        on_config = workflow_data.get('on', {})
        
        # Check for workflow_run dependencies
        if isinstance(on_config, dict):
            if 'workflow_run' in on_config:
                workflow_run = on_config['workflow_run']
                workflows = workflow_run.get('workflows', [])
                if isinstance(workflows, list):
                    dependencies.update(workflows)
                elif isinstance(workflows, str):
                    dependencies.add(workflows)
        
        # Check for workflow_call in uses
        jobs = workflow_data.get('jobs', {})
        for job_name, job_config in jobs.items():
            if isinstance(job_config, dict):
                uses = job_config.get('uses', '')
                if uses and '.github/workflows/' in uses:
                    # Extract workflow name from uses
                    workflow_ref = uses.split('.github/workflows/')[-1].split('@')[0]
                    dependencies.add(workflow_ref)
        
        return dependencies
    
    def build_graph(self) -> None:
        """Build the complete workflow dependency graph."""
        workflow_files = self.discover_workflows()
        
        # First pass: create nodes
        for workflow_path in workflow_files:
            try:
                with open(workflow_path, 'r') as f:
                    workflow_data = yaml.safe_load(f)
                
                if not workflow_data:
                    continue
                
                name = workflow_data.get('name', workflow_path.stem)
                triggers = self.parse_workflow_triggers(workflow_data)
                dependencies = self.extract_workflow_dependencies(workflow_data)
                
                # Extract schedule if present
                schedule = None
                on_config = workflow_data.get('on', {})
                if isinstance(on_config, dict) and 'schedule' in on_config:
                    schedule_list = on_config['schedule']
                    if schedule_list and isinstance(schedule_list, list):
                        schedule = schedule_list[0].get('cron', '')
                
                node = WorkflowNode(
                    name=name,
                    path=str(workflow_path),
                    triggers=triggers,
                    dependencies=dependencies,
                    schedule=schedule,
                    metadata={
                        'file': workflow_path.name,
                        'jobs_count': len(workflow_data.get('jobs', {}))
                    }
                )
                
                self.nodes[name] = node
                
            except Exception as e:
                print(f"Warning: Failed to parse {workflow_path}: {e}")
                continue
        
        # Second pass: establish dependents (reverse dependencies)
        for name, node in self.nodes.items():
            for dep in node.dependencies:
                # Find the dependent workflow by name
                for dep_node_name, dep_node in self.nodes.items():
                    if dep in dep_node_name or dep_node.metadata.get('file', '') == dep:
                        dep_node.dependents.add(name)
    
    def lazy_evaluate(self, workflow_name: str) -> Optional[WorkflowNode]:
        """
        Lazily evaluate a workflow node and its dependencies.
        
        This is the core of lazy evaluation:
        - Only loads/evaluates when requested
        - Caches results for subsequent access
        - Recursively evaluates dependencies on-demand
        """
        # Check cache first
        if workflow_name in self.evaluation_cache:
            cache_entry = self.evaluation_cache[workflow_name]
            if cache_entry.get('is_valid', False):
                return cache_entry.get('node')
        
        # Find the node
        node = self.nodes.get(workflow_name)
        if not node:
            return None
        
        # Mark as evaluated
        node.is_loaded = True
        node.last_evaluated = datetime.utcnow().isoformat() + 'Z'
        
        # Recursively evaluate dependencies (lazy)
        for dep in node.dependencies:
            if dep in self.nodes and not self.nodes[dep].is_loaded:
                self.lazy_evaluate(dep)
        
        # Cache the result
        self.evaluation_cache[workflow_name] = {
            'node': node,
            'is_valid': True,
            'evaluated_at': node.last_evaluated
        }
        
        return node
    
    def get_dependency_chain(self, workflow_name: str) -> List[str]:
        """Get the full dependency chain for a workflow (lazy loaded)."""
        visited = set()
        chain = []
        
        def traverse(name: str):
            if name in visited:
                return
            visited.add(name)
            
            # Lazy evaluate this node
            node = self.lazy_evaluate(name)
            if not node:
                return
            
            # Add dependencies first (depth-first)
            for dep in node.dependencies:
                traverse(dep)
            
            chain.append(name)
        
        traverse(workflow_name)
        return chain
    
    def get_dependent_chain(self, workflow_name: str) -> List[str]:
        """Get all workflows that depend on this workflow (lazy loaded)."""
        visited = set()
        chain = []
        
        def traverse(name: str):
            if name in visited:
                return
            visited.add(name)
            
            # Lazy evaluate this node
            node = self.lazy_evaluate(name)
            if not node:
                return
            
            chain.append(name)
            
            # Traverse dependents
            for dependent in node.dependents:
                traverse(dependent)
        
        traverse(workflow_name)
        return chain
    
    def get_evaluation_stats(self) -> Dict[str, Any]:
        """Get statistics about lazy evaluation performance."""
        total_nodes = len(self.nodes)
        loaded_nodes = sum(1 for node in self.nodes.values() if node.is_loaded)
        cached_nodes = len(self.evaluation_cache)
        
        return {
            'total_workflows': total_nodes,
            'loaded_workflows': loaded_nodes,
            'cached_evaluations': cached_nodes,
            'lazy_load_ratio': loaded_nodes / total_nodes if total_nodes > 0 else 0,
            'cache_hit_potential': cached_nodes / max(loaded_nodes, 1)
        }
    
    def invalidate_cache(self, workflow_name: Optional[str] = None) -> None:
        """Invalidate cache for a specific workflow or all workflows."""
        if workflow_name:
            if workflow_name in self.evaluation_cache:
                self.evaluation_cache[workflow_name]['is_valid'] = False
            if workflow_name in self.nodes:
                self.nodes[workflow_name].is_loaded = False
        else:
            # Invalidate all
            for entry in self.evaluation_cache.values():
                entry['is_valid'] = False
            for node in self.nodes.values():
                node.is_loaded = False
    
    def export_graph(self, output_path: str) -> None:
        """Export the dependency graph to JSON."""
        graph_data = {
            'nodes': {
                name: {
                    'name': node.name,
                    'path': node.path,
                    'triggers': node.triggers,
                    'dependencies': list(node.dependencies),
                    'dependents': list(node.dependents),
                    'schedule': node.schedule,
                    'is_loaded': node.is_loaded,
                    'metadata': node.metadata,
                    'last_evaluated': node.last_evaluated
                }
                for name, node in self.nodes.items()
            },
            'stats': self.get_evaluation_stats(),
            'generated_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        with open(output_path, 'w') as f:
            json.dump(graph_data, f, indent=2)


def main():
    """CLI interface for workflow dependency graph analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze workflow dependencies with lazy evaluation'
    )
    parser.add_argument(
        '--workflows-dir',
        default='.github/workflows',
        help='Path to workflows directory'
    )
    parser.add_argument(
        '--workflow',
        help='Analyze a specific workflow'
    )
    parser.add_argument(
        '--export',
        help='Export graph to JSON file'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show evaluation statistics'
    )
    parser.add_argument(
        '--deps',
        action='store_true',
        help='Show dependency chain for workflow'
    )
    parser.add_argument(
        '--dependents',
        action='store_true',
        help='Show dependent chain for workflow'
    )
    
    args = parser.parse_args()
    
    # Build the dependency graph
    graph = WorkflowDependencyGraph(args.workflows_dir)
    print(f"🔍 Discovering workflows in {args.workflows_dir}...")
    graph.build_graph()
    print(f"✅ Found {len(graph.nodes)} workflows")
    
    # Handle specific workflow analysis
    if args.workflow:
        print(f"\n📊 Analyzing workflow: {args.workflow}")
        node = graph.lazy_evaluate(args.workflow)
        
        if node:
            print(f"  Name: {node.name}")
            print(f"  Path: {node.path}")
            print(f"  Triggers: {', '.join(node.triggers)}")
            print(f"  Schedule: {node.schedule or 'None'}")
            print(f"  Dependencies: {len(node.dependencies)}")
            print(f"  Dependents: {len(node.dependents)}")
            
            if args.deps:
                chain = graph.get_dependency_chain(args.workflow)
                print(f"\n  Dependency Chain ({len(chain)} workflows):")
                for i, dep in enumerate(chain, 1):
                    print(f"    {i}. {dep}")
            
            if args.dependents:
                chain = graph.get_dependent_chain(args.workflow)
                print(f"\n  Dependent Chain ({len(chain)} workflows):")
                for i, dep in enumerate(chain, 1):
                    print(f"    {i}. {dep}")
        else:
            print(f"  ❌ Workflow not found: {args.workflow}")
    
    # Show stats
    if args.stats:
        stats = graph.get_evaluation_stats()
        print(f"\n📈 Lazy Evaluation Statistics:")
        print(f"  Total Workflows: {stats['total_workflows']}")
        print(f"  Loaded Workflows: {stats['loaded_workflows']}")
        print(f"  Cached Evaluations: {stats['cached_evaluations']}")
        print(f"  Lazy Load Ratio: {stats['lazy_load_ratio']:.2%}")
        print(f"  Cache Hit Potential: {stats['cache_hit_potential']:.2%}")
    
    # Export graph
    if args.export:
        graph.export_graph(args.export)
        print(f"\n💾 Graph exported to: {args.export}")


if __name__ == '__main__':
    main()
