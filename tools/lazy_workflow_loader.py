#!/usr/bin/env python3
"""
Lazy Workflow Loader

Provides lazy loading capabilities for workflow dependencies.
Delays loading and parsing until absolutely necessary.
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
import hashlib


@dataclass
class LazyWorkflow:
    """
    A lazily-loaded workflow that defers parsing until accessed.
    
    Key features:
    - Lazy loading: content only parsed when needed
    - Caching: parsed content cached for reuse
    - Validation: hash-based cache invalidation
    - Metrics: tracks load times and cache hits
    """
    name: str
    path: str
    _content: Optional[Dict[str, Any]] = field(default=None, repr=False)
    _hash: Optional[str] = field(default=None, repr=False)
    _load_count: int = field(default=0, repr=False)
    _cache_hits: int = field(default=0, repr=False)
    _last_loaded: Optional[str] = field(default=None, repr=False)
    
    def _calculate_hash(self) -> str:
        """Calculate hash of workflow file for cache invalidation."""
        if not Path(self.path).exists():
            return ""
        
        with open(self.path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def _is_cache_valid(self) -> bool:
        """Check if cached content is still valid."""
        if self._content is None or self._hash is None:
            return False
        
        current_hash = self._calculate_hash()
        return current_hash == self._hash
    
    def load(self, force: bool = False) -> Dict[str, Any]:
        """
        Load workflow content lazily.
        
        Args:
            force: Force reload even if cached
            
        Returns:
            Parsed workflow content
        """
        # Check cache validity
        if not force and self._is_cache_valid():
            self._cache_hits += 1
            return self._content
        
        # Load and parse
        try:
            with open(self.path, 'r') as f:
                self._content = yaml.safe_load(f)
            
            self._hash = self._calculate_hash()
            self._load_count += 1
            self._last_loaded = datetime.utcnow().isoformat() + 'Z'
            
            return self._content
        except Exception as e:
            print(f"Error loading workflow {self.path}: {e}")
            return {}
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get workflow metadata without loading full content."""
        return {
            'name': self.name,
            'path': self.path,
            'is_loaded': self._content is not None,
            'load_count': self._load_count,
            'cache_hits': self._cache_hits,
            'last_loaded': self._last_loaded
        }
    
    def invalidate(self) -> None:
        """Invalidate cached content."""
        self._content = None
        self._hash = None


def lazy_property(func: Callable) -> property:
    """
    Decorator for creating lazy-loaded properties.
    
    Property is only computed once when first accessed,
    then cached for subsequent accesses.
    """
    attr_name = f'_lazy_{func.__name__}'
    
    @wraps(func)
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)
    
    return property(wrapper)


class LazyWorkflowLoader:
    """
    Manages lazy loading of workflows with intelligent caching.
    
    Features:
    - On-demand loading: workflows loaded only when accessed
    - Smart caching: intelligent cache invalidation based on file changes
    - Batch loading: efficiently load multiple workflows
    - Metrics tracking: monitor cache performance
    """
    
    def __init__(self, workflows_dir: str = ".github/workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.workflows: Dict[str, LazyWorkflow] = {}
        self.load_history: List[Dict[str, Any]] = []
        
    def discover(self) -> None:
        """Discover all workflows without loading them."""
        if not self.workflows_dir.exists():
            return
        
        for workflow_file in self.workflows_dir.glob("*.y*ml"):
            name = workflow_file.stem
            if name not in self.workflows:
                self.workflows[name] = LazyWorkflow(
                    name=name,
                    path=str(workflow_file)
                )
    
    def get_workflow(self, name: str, load: bool = False) -> Optional[LazyWorkflow]:
        """
        Get a workflow by name, optionally loading it.
        
        Args:
            name: Workflow name
            load: Whether to load content immediately
            
        Returns:
            LazyWorkflow instance or None
        """
        if name not in self.workflows:
            return None
        
        workflow = self.workflows[name]
        
        if load:
            workflow.load()
            self._record_load(name)
        
        return workflow
    
    def load_workflow(self, name: str, force: bool = False) -> Optional[Dict[str, Any]]:
        """
        Load and return workflow content.
        
        Args:
            name: Workflow name
            force: Force reload even if cached
            
        Returns:
            Workflow content or None
        """
        workflow = self.get_workflow(name)
        if not workflow:
            return None
        
        content = workflow.load(force=force)
        self._record_load(name, force=force)
        
        return content
    
    def load_batch(self, names: List[str], parallel: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Load multiple workflows efficiently.
        
        Args:
            names: List of workflow names
            parallel: Enable parallel loading (future enhancement)
            
        Returns:
            Dictionary mapping names to workflow content
        """
        results = {}
        
        for name in names:
            content = self.load_workflow(name)
            if content:
                results[name] = content
        
        return results
    
    def invalidate(self, name: Optional[str] = None) -> None:
        """
        Invalidate cached workflows.
        
        Args:
            name: Specific workflow to invalidate, or None for all
        """
        if name:
            workflow = self.workflows.get(name)
            if workflow:
                workflow.invalidate()
        else:
            for workflow in self.workflows.values():
                workflow.invalidate()
    
    def get_loaded_workflows(self) -> List[str]:
        """Get names of all currently loaded workflows."""
        return [
            name for name, workflow in self.workflows.items()
            if workflow._content is not None
        ]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get loader performance metrics."""
        total_workflows = len(self.workflows)
        loaded_workflows = len(self.get_loaded_workflows())
        
        total_loads = sum(w._load_count for w in self.workflows.values())
        total_cache_hits = sum(w._cache_hits for w in self.workflows.values())
        
        return {
            'total_workflows': total_workflows,
            'loaded_workflows': loaded_workflows,
            'unloaded_workflows': total_workflows - loaded_workflows,
            'total_loads': total_loads,
            'cache_hits': total_cache_hits,
            'cache_hit_rate': total_cache_hits / max(total_loads, 1),
            'lazy_load_savings': (total_workflows - loaded_workflows) / max(total_workflows, 1),
            'load_history_size': len(self.load_history)
        }
    
    def _record_load(self, name: str, force: bool = False) -> None:
        """Record a workflow load event for metrics."""
        self.load_history.append({
            'workflow': name,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'forced': force
        })
    
    def export_metrics(self, output_path: str) -> None:
        """Export loader metrics to JSON file."""
        metrics = self.get_metrics()
        
        # Add per-workflow details
        metrics['workflows'] = {
            name: workflow.get_metadata()
            for name, workflow in self.workflows.items()
        }
        
        metrics['load_history'] = self.load_history
        
        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2)


class LazyDependencyResolver:
    """
    Resolves workflow dependencies lazily.
    
    Only loads dependencies when they're actually needed,
    avoiding unnecessary I/O and parsing.
    """
    
    def __init__(self, loader: LazyWorkflowLoader):
        self.loader = loader
        self._dependency_cache: Dict[str, List[str]] = {}
    
    def get_dependencies(self, workflow_name: str, recursive: bool = False) -> List[str]:
        """
        Get dependencies for a workflow, loading lazily.
        
        Args:
            workflow_name: Workflow to analyze
            recursive: Include transitive dependencies
            
        Returns:
            List of dependency workflow names
        """
        # Check cache first
        cache_key = f"{workflow_name}:{'recursive' if recursive else 'direct'}"
        if cache_key in self._dependency_cache:
            return self._dependency_cache[cache_key]
        
        # Load workflow content lazily
        content = self.loader.load_workflow(workflow_name)
        if not content:
            return []
        
        dependencies = self._extract_dependencies(content)
        
        # Recursive resolution (lazy)
        if recursive:
            all_deps = set(dependencies)
            for dep in dependencies:
                transitive = self.get_dependencies(dep, recursive=True)
                all_deps.update(transitive)
            dependencies = list(all_deps)
        
        # Cache results
        self._dependency_cache[cache_key] = dependencies
        
        return dependencies
    
    def _extract_dependencies(self, workflow_content: Dict[str, Any]) -> List[str]:
        """Extract workflow dependencies from content."""
        dependencies = []
        on_config = workflow_content.get('on', {})
        
        # Check workflow_run triggers
        if isinstance(on_config, dict) and 'workflow_run' in on_config:
            workflow_run = on_config['workflow_run']
            workflows = workflow_run.get('workflows', [])
            if isinstance(workflows, list):
                dependencies.extend(workflows)
            elif isinstance(workflows, str):
                dependencies.append(workflows)
        
        return dependencies
    
    def resolve_lazy(self, workflow_name: str) -> Dict[str, Any]:
        """
        Resolve all dependencies lazily, returning load order.
        
        Returns:
            Dictionary with resolution plan and loaded workflows
        """
        dependencies = self.get_dependencies(workflow_name, recursive=True)
        
        # Topological sort for load order (simplified)
        load_order = dependencies + [workflow_name]
        
        return {
            'workflow': workflow_name,
            'dependencies': dependencies,
            'load_order': load_order,
            'total_dependencies': len(dependencies)
        }


def main():
    """CLI interface for lazy workflow loading."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Lazy workflow loader with intelligent caching'
    )
    parser.add_argument(
        '--workflows-dir',
        default='.github/workflows',
        help='Path to workflows directory'
    )
    parser.add_argument(
        '--workflow',
        help='Load a specific workflow'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List discovered workflows'
    )
    parser.add_argument(
        '--metrics',
        action='store_true',
        help='Show loader metrics'
    )
    parser.add_argument(
        '--export-metrics',
        help='Export metrics to JSON file'
    )
    parser.add_argument(
        '--load-all',
        action='store_true',
        help='Load all workflows (for testing)'
    )
    
    args = parser.parse_args()
    
    # Create loader
    loader = LazyWorkflowLoader(args.workflows_dir)
    print(f"🔍 Discovering workflows in {args.workflows_dir}...")
    loader.discover()
    print(f"✅ Discovered {len(loader.workflows)} workflows")
    
    # List workflows
    if args.list:
        print("\n📋 Discovered Workflows:")
        for name, workflow in sorted(loader.workflows.items()):
            status = "✓ loaded" if workflow._content is not None else "○ unloaded"
            print(f"  {status} {name}")
    
    # Load specific workflow
    if args.workflow:
        print(f"\n📂 Loading workflow: {args.workflow}")
        content = loader.load_workflow(args.workflow)
        if content:
            print(f"  ✅ Loaded successfully")
            print(f"  Name: {content.get('name', 'N/A')}")
            print(f"  Jobs: {len(content.get('jobs', {}))}")
        else:
            print(f"  ❌ Failed to load")
    
    # Load all (for testing)
    if args.load_all:
        print(f"\n🔄 Loading all workflows...")
        for name in loader.workflows.keys():
            loader.load_workflow(name)
        print(f"  ✅ Loaded {len(loader.get_loaded_workflows())} workflows")
    
    # Show metrics
    if args.metrics:
        metrics = loader.get_metrics()
        print(f"\n📊 Lazy Loading Metrics:")
        print(f"  Total Workflows: {metrics['total_workflows']}")
        print(f"  Loaded: {metrics['loaded_workflows']}")
        print(f"  Unloaded: {metrics['unloaded_workflows']}")
        print(f"  Total Loads: {metrics['total_loads']}")
        print(f"  Cache Hits: {metrics['cache_hits']}")
        print(f"  Cache Hit Rate: {metrics['cache_hit_rate']:.2%}")
        print(f"  Lazy Load Savings: {metrics['lazy_load_savings']:.2%}")
    
    # Export metrics
    if args.export_metrics:
        loader.export_metrics(args.export_metrics)
        print(f"\n💾 Metrics exported to: {args.export_metrics}")


if __name__ == '__main__':
    main()
