#!/usr/bin/env python3
"""
Lazy Workflow Evaluation System
================================

A sophisticated lazy evaluation system for workflow dependencies that:
- Defers computation until results are actually needed
- Caches computed values to avoid redundant work
- Tracks dependency graphs for intelligent evaluation
- Supports both workflow-level and step-level lazy evaluation

Created by: @investigate-champion
Inspired by: Ada Lovelace's visionary approach to computation
Purpose: Optimize workflow execution through intelligent lazy evaluation

Architecture:
    LazyWorkflowNode -> Represents a computation that can be deferred
    DependencyGraph  -> Manages dependency relationships
    ComputationCache -> Stores and retrieves cached results
    EvaluationEngine -> Orchestrates lazy evaluation

Example:
    >>> engine = EvaluationEngine()
    >>> node = LazyWorkflowNode('analyze-code', lambda: expensive_analysis())
    >>> engine.register(node)
    >>> # Computation not executed yet
    >>> result = engine.evaluate('analyze-code')  # Now it executes
    >>> result2 = engine.evaluate('analyze-code')  # Returns cached value
"""

import os
import sys
import json
import hashlib
import pickle
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from enum import Enum
import threading


class NodeState(Enum):
    """States a lazy node can be in"""
    PENDING = "pending"          # Not yet evaluated
    EVALUATING = "evaluating"    # Currently being evaluated
    COMPLETED = "completed"      # Successfully evaluated
    FAILED = "failed"            # Evaluation failed
    CACHED = "cached"            # Result loaded from cache


@dataclass
class EvaluationMetrics:
    """Metrics about evaluation performance"""
    node_id: str
    state: NodeState
    evaluation_time: float = 0.0
    cache_hit: bool = False
    dependencies_count: int = 0
    evaluation_timestamp: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['state'] = self.state.value
        return data


@dataclass
class LazyWorkflowNode:
    """
    Represents a computation that can be lazily evaluated.
    
    The node holds a computation function and dependencies, but doesn't
    execute until explicitly evaluated. Results are cached for reuse.
    
    Attributes:
        node_id: Unique identifier for this node
        compute_fn: Function to execute when evaluation is needed
        dependencies: List of node IDs this depends on
        cache_ttl: Time-to-live for cached results (seconds)
        metadata: Additional metadata about the node
    """
    node_id: str
    compute_fn: Optional[Callable[..., Any]] = None
    dependencies: List[str] = field(default_factory=list)
    cache_ttl: int = 3600  # 1 hour default
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Runtime state (not serialized)
    _result: Any = field(default=None, init=False, repr=False)
    _state: NodeState = field(default=NodeState.PENDING, init=False, repr=False)
    _evaluation_time: float = field(default=0.0, init=False, repr=False)
    _cache_timestamp: Optional[datetime] = field(default=None, init=False, repr=False)
    _error: Optional[Exception] = field(default=None, init=False, repr=False)
    
    def is_evaluated(self) -> bool:
        """Check if this node has been evaluated"""
        return self._state in (NodeState.COMPLETED, NodeState.CACHED)
    
    def is_cache_valid(self) -> bool:
        """Check if cached result is still valid"""
        if not self.is_evaluated() or self._cache_timestamp is None:
            return False
        
        age = (datetime.now(timezone.utc) - self._cache_timestamp).total_seconds()
        return age < self.cache_ttl
    
    def get_result(self) -> Any:
        """Get the computed result (if available)"""
        if not self.is_evaluated():
            raise RuntimeError(f"Node '{self.node_id}' has not been evaluated yet")
        
        if not self.is_cache_valid():
            raise RuntimeError(f"Cached result for '{self.node_id}' has expired")
        
        return self._result
    
    def set_result(self, result: Any, from_cache: bool = False):
        """Set the result after computation"""
        self._result = result
        self._state = NodeState.CACHED if from_cache else NodeState.COMPLETED
        self._cache_timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (excluding compute function)"""
        return {
            'node_id': self.node_id,
            'dependencies': self.dependencies,
            'cache_ttl': self.cache_ttl,
            'metadata': self.metadata,
            'state': self._state.value,
            'is_evaluated': self.is_evaluated(),
            'evaluation_time': self._evaluation_time
        }


class ComputationCache:
    """
    Persistent cache for computation results.
    
    Stores results on disk with TTL-based invalidation.
    Thread-safe for concurrent access.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory to store cache files (default: .cache/lazy-eval)
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Default to repo root .cache directory
            repo_root = self._find_repo_root()
            self.cache_dir = repo_root / ".cache" / "lazy-eval"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        
        # In-memory cache for faster access
        self._memory_cache: Dict[str, Tuple[Any, datetime, int]] = {}
    
    def _find_repo_root(self) -> Path:
        """Find repository root by looking for .git directory"""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _get_cache_key(self, node_id: str, dependencies_hash: str) -> str:
        """Generate cache key from node ID and dependencies"""
        combined = f"{node_id}:{dependencies_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def _get_cache_metadata_path(self, node_id: str) -> Path:
        """Get metadata file path for tracking node cache files"""
        return self.cache_dir / f"metadata_{node_id}.json"
    
    def get(self, node_id: str, dependencies_hash: str, ttl: int) -> Optional[Any]:
        """
        Retrieve cached result if valid.
        
        Args:
            node_id: Node identifier
            dependencies_hash: Hash of dependency values
            ttl: Time-to-live in seconds
            
        Returns:
            Cached result or None if not found/expired
        """
        cache_key = self._get_cache_key(node_id, dependencies_hash)
        
        with self._lock:
            # Check memory cache first
            if cache_key in self._memory_cache:
                result, timestamp, cached_ttl = self._memory_cache[cache_key]
                age = (datetime.now(timezone.utc) - timestamp).total_seconds()
                if age < ttl:
                    return result
                else:
                    # Expired, remove from memory cache
                    del self._memory_cache[cache_key]
            
            # Check disk cache
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                try:
                    with open(cache_path, 'rb') as f:
                        cached_data = pickle.load(f)
                    
                    timestamp = cached_data['timestamp']
                    age = (datetime.now(timezone.utc) - timestamp).total_seconds()
                    
                    if age < ttl:
                        result = cached_data['result']
                        # Load into memory cache
                        self._memory_cache[cache_key] = (result, timestamp, ttl)
                        return result
                    else:
                        # Expired, delete file
                        cache_path.unlink()
                
                except Exception as e:
                    print(f"Warning: Error reading cache for {node_id}: {e}", file=sys.stderr)
        
        return None
    
    def set(self, node_id: str, dependencies_hash: str, result: Any, ttl: int):
        """
        Store result in cache.
        
        Args:
            node_id: Node identifier
            dependencies_hash: Hash of dependency values
            result: Result to cache
            ttl: Time-to-live in seconds
        """
        cache_key = self._get_cache_key(node_id, dependencies_hash)
        timestamp = datetime.now(timezone.utc)
        
        with self._lock:
            # Store in memory
            self._memory_cache[cache_key] = (result, timestamp, ttl)
            
            # Store on disk
            cache_path = self._get_cache_path(cache_key)
            try:
                cached_data = {
                    'node_id': node_id,
                    'timestamp': timestamp,
                    'result': result,
                    'ttl': ttl
                }
                with open(cache_path, 'wb') as f:
                    pickle.dump(cached_data, f)
                
                # Track this cache file in metadata
                metadata_path = self._get_cache_metadata_path(node_id)
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                else:
                    metadata = {'node_id': node_id, 'cache_files': []}
                
                if cache_key not in metadata['cache_files']:
                    metadata['cache_files'].append(cache_key)
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f)
                    
            except Exception as e:
                print(f"Warning: Error writing cache for {node_id}: {e}", file=sys.stderr)
    
    def invalidate(self, node_id: str):
        """Invalidate all cache entries for a node"""
        with self._lock:
            # Read metadata to find cache files
            metadata_path = self._get_cache_metadata_path(node_id)
            cache_keys_to_remove = []
            
            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    cache_keys_to_remove = metadata.get('cache_files', [])
                    
                    # Delete metadata file
                    metadata_path.unlink()
                except Exception:
                    pass
            
            # Clear memory cache entries
            for key in cache_keys_to_remove:
                if key in self._memory_cache:
                    del self._memory_cache[key]
            
            # Clear disk cache entries
            for cache_key in cache_keys_to_remove:
                cache_path = self._get_cache_path(cache_key)
                try:
                    if cache_path.exists():
                        cache_path.unlink()
                except Exception:
                    pass
    
    def clear_all(self):
        """Clear entire cache"""
        with self._lock:
            self._memory_cache.clear()
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                except Exception:
                    pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            disk_files = list(self.cache_dir.glob("*.cache"))
            total_size = sum(f.stat().st_size for f in disk_files)
            
            return {
                'memory_entries': len(self._memory_cache),
                'disk_entries': len(disk_files),
                'total_size_bytes': total_size,
                'cache_dir': str(self.cache_dir)
            }


class DependencyGraph:
    """
    Manages dependency relationships between workflow nodes.
    
    Provides topological sorting, cycle detection, and dependency resolution.
    """
    
    def __init__(self):
        """Initialize empty dependency graph"""
        self.nodes: Dict[str, LazyWorkflowNode] = {}
        self.adjacency_list: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)
    
    def add_node(self, node: LazyWorkflowNode):
        """Add a node to the graph"""
        if node.node_id in self.nodes:
            raise ValueError(f"Node '{node.node_id}' already exists in graph")
        
        self.nodes[node.node_id] = node
        
        # Build adjacency lists
        for dep_id in node.dependencies:
            self.adjacency_list[node.node_id].add(dep_id)
            self.reverse_adjacency[dep_id].add(node.node_id)
    
    def get_node(self, node_id: str) -> Optional[LazyWorkflowNode]:
        """Retrieve a node by ID"""
        return self.nodes.get(node_id)
    
    def get_dependencies(self, node_id: str) -> List[str]:
        """Get direct dependencies of a node"""
        return list(self.adjacency_list.get(node_id, set()))
    
    def get_dependents(self, node_id: str) -> List[str]:
        """Get nodes that depend on this node"""
        return list(self.reverse_adjacency.get(node_id, set()))
    
    def has_cycles(self) -> Tuple[bool, Optional[List[str]]]:
        """
        Check for circular dependencies.
        
        Returns:
            Tuple of (has_cycle, cycle_path)
        """
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str, path: List[str]) -> Optional[List[str]]:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            for dep_id in self.adjacency_list.get(node_id, set()):
                if dep_id not in visited:
                    result = dfs(dep_id, path.copy())
                    if result:
                        return result
                elif dep_id in rec_stack:
                    # Found cycle
                    cycle_start = path.index(dep_id)
                    return path[cycle_start:] + [dep_id]
            
            rec_stack.remove(node_id)
            return None
        
        for node_id in self.nodes:
            if node_id not in visited:
                cycle = dfs(node_id, [])
                if cycle:
                    return True, cycle
        
        return False, None
    
    def topological_sort(self) -> List[str]:
        """
        Return nodes in topological order (dependencies first).
        
        Returns:
            List of node IDs in evaluation order
            
        Raises:
            ValueError: If graph contains cycles
        """
        has_cycle, cycle = self.has_cycles()
        if has_cycle:
            raise ValueError(f"Cannot sort graph with cycles: {' -> '.join(cycle)}")
        
        # Kahn's algorithm
        in_degree = {node_id: len(deps) for node_id, deps in self.adjacency_list.items()}
        for node_id in self.nodes:
            if node_id not in in_degree:
                in_degree[node_id] = 0
        
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            for dependent in self.reverse_adjacency.get(node_id, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(result) != len(self.nodes):
            raise ValueError("Graph contains cycles or disconnected components")
        
        return result
    
    def get_transitive_dependencies(self, node_id: str) -> Set[str]:
        """Get all transitive dependencies (recursive)"""
        all_deps = set()
        visited = set()
        
        def dfs(current_id: str):
            if current_id in visited:
                return
            visited.add(current_id)
            
            for dep_id in self.adjacency_list.get(current_id, set()):
                all_deps.add(dep_id)
                dfs(dep_id)
        
        dfs(node_id)
        return all_deps
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary"""
        return {
            'nodes': {nid: node.to_dict() for nid, node in self.nodes.items()},
            'edges': {nid: list(deps) for nid, deps in self.adjacency_list.items()}
        }


class EvaluationEngine:
    """
    Main engine for lazy evaluation of workflow dependencies.
    
    Orchestrates the evaluation process:
    1. Resolves dependencies using topological sort
    2. Checks cache for previously computed results
    3. Evaluates nodes only when needed
    4. Caches results for future use
    5. Tracks metrics and performance
    """
    
    def __init__(self, cache_dir: Optional[str] = None, enable_cache: bool = True):
        """
        Initialize evaluation engine.
        
        Args:
            cache_dir: Directory for cache storage
            enable_cache: Whether to use caching
        """
        self.graph = DependencyGraph()
        self.cache = ComputationCache(cache_dir) if enable_cache else None
        self.enable_cache = enable_cache
        self.metrics: Dict[str, EvaluationMetrics] = {}
        self._evaluation_context: Dict[str, Any] = {}
    
    def register(self, node: LazyWorkflowNode):
        """
        Register a node for lazy evaluation.
        
        Args:
            node: Node to register
        """
        self.graph.add_node(node)
    
    def register_workflow(self, node_id: str, compute_fn: Callable[..., Any],
                         dependencies: Optional[List[str]] = None,
                         cache_ttl: int = 3600,
                         metadata: Optional[Dict[str, Any]] = None) -> LazyWorkflowNode:
        """
        Convenience method to create and register a node.
        
        Args:
            node_id: Unique identifier
            compute_fn: Function to execute
            dependencies: List of dependency node IDs
            cache_ttl: Cache time-to-live in seconds
            metadata: Additional metadata
            
        Returns:
            Created node
        """
        node = LazyWorkflowNode(
            node_id=node_id,
            compute_fn=compute_fn,
            dependencies=dependencies or [],
            cache_ttl=cache_ttl,
            metadata=metadata or {}
        )
        self.register(node)
        return node
    
    def _compute_dependencies_hash(self, node: LazyWorkflowNode) -> str:
        """Compute hash of dependency values"""
        dep_values = []
        for dep_id in node.dependencies:
            dep_node = self.graph.get_node(dep_id)
            if dep_node and dep_node.is_evaluated():
                # Hash the result
                result_str = json.dumps(dep_node._result, sort_keys=True, default=str)
                dep_values.append(result_str)
            else:
                dep_values.append(f"unevaluated:{dep_id}")
        
        combined = "|".join(sorted(dep_values))
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def evaluate(self, node_id: str, force: bool = False) -> Any:
        """
        Evaluate a node and its dependencies lazily.
        
        Args:
            node_id: ID of node to evaluate
            force: Force re-evaluation even if cached
            
        Returns:
            Computed result
            
        Raises:
            ValueError: If node doesn't exist or has cycles
            RuntimeError: If evaluation fails
        """
        node = self.graph.get_node(node_id)
        if not node:
            raise ValueError(f"Node '{node_id}' not found in graph")
        
        # Check if already evaluated and cache is valid
        if not force and node.is_evaluated() and node.is_cache_valid():
            self.metrics[node_id] = EvaluationMetrics(
                node_id=node_id,
                state=NodeState.CACHED,
                cache_hit=True,
                dependencies_count=len(node.dependencies),
                evaluation_timestamp=datetime.now(timezone.utc).isoformat()
            )
            return node.get_result()
        
        # Get evaluation order (topological sort of dependencies)
        try:
            all_deps = self.graph.get_transitive_dependencies(node_id)
            eval_order = [nid for nid in self.graph.topological_sort() 
                         if nid in all_deps or nid == node_id]
        except ValueError as e:
            raise ValueError(f"Cannot evaluate '{node_id}': {e}")
        
        # Evaluate dependencies in order
        for dep_id in eval_order:
            dep_node = self.graph.get_node(dep_id)
            if not dep_node:
                continue
            
            # Skip if already evaluated and valid
            if not force and dep_node.is_evaluated() and dep_node.is_cache_valid():
                continue
            
            # Try to load from cache
            if self.enable_cache and not force:
                deps_hash = self._compute_dependencies_hash(dep_node)
                cached_result = self.cache.get(dep_id, deps_hash, dep_node.cache_ttl)
                
                if cached_result is not None:
                    dep_node.set_result(cached_result, from_cache=True)
                    self.metrics[dep_id] = EvaluationMetrics(
                        node_id=dep_id,
                        state=NodeState.CACHED,
                        cache_hit=True,
                        dependencies_count=len(dep_node.dependencies),
                        evaluation_timestamp=datetime.now(timezone.utc).isoformat()
                    )
                    continue
            
            # Need to evaluate
            if dep_node.compute_fn is None:
                raise RuntimeError(f"Node '{dep_id}' has no compute function")
            
            dep_node._state = NodeState.EVALUATING
            start_time = time.time()
            
            try:
                # Collect dependency results to pass to compute function
                dep_results = {}
                for dep_dep_id in dep_node.dependencies:
                    dep_dep_node = self.graph.get_node(dep_dep_id)
                    if dep_dep_node and dep_dep_node.is_evaluated():
                        dep_results[dep_dep_id] = dep_dep_node.get_result()
                
                # Execute computation
                if dep_results:
                    result = dep_node.compute_fn(**dep_results)
                else:
                    result = dep_node.compute_fn()
                
                eval_time = time.time() - start_time
                dep_node._evaluation_time = eval_time
                dep_node.set_result(result, from_cache=False)
                
                # Cache the result
                if self.enable_cache:
                    deps_hash = self._compute_dependencies_hash(dep_node)
                    self.cache.set(dep_id, deps_hash, result, dep_node.cache_ttl)
                
                self.metrics[dep_id] = EvaluationMetrics(
                    node_id=dep_id,
                    state=NodeState.COMPLETED,
                    evaluation_time=eval_time,
                    cache_hit=False,
                    dependencies_count=len(dep_node.dependencies),
                    evaluation_timestamp=datetime.now(timezone.utc).isoformat()
                )
                
            except Exception as e:
                dep_node._state = NodeState.FAILED
                dep_node._error = e
                self.metrics[dep_id] = EvaluationMetrics(
                    node_id=dep_id,
                    state=NodeState.FAILED,
                    error_message=str(e),
                    dependencies_count=len(dep_node.dependencies),
                    evaluation_timestamp=datetime.now(timezone.utc).isoformat()
                )
                raise RuntimeError(f"Failed to evaluate '{dep_id}': {e}") from e
        
        # Return the requested node's result
        return node.get_result()
    
    def evaluate_all(self, force: bool = False) -> Dict[str, Any]:
        """
        Evaluate all registered nodes.
        
        Args:
            force: Force re-evaluation even if cached
            
        Returns:
            Dictionary of node_id -> result
        """
        results = {}
        eval_order = self.graph.topological_sort()
        
        for node_id in eval_order:
            try:
                results[node_id] = self.evaluate(node_id, force=force)
            except Exception as e:
                print(f"Error evaluating '{node_id}': {e}", file=sys.stderr)
                results[node_id] = None
        
        return results
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get evaluation metrics for all nodes"""
        return {nid: metric.to_dict() for nid, metric in self.metrics.items()}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        total_nodes = len(self.graph.nodes)
        evaluated_nodes = len([m for m in self.metrics.values() 
                              if m.state in (NodeState.COMPLETED, NodeState.CACHED)])
        cache_hits = len([m for m in self.metrics.values() if m.cache_hit])
        total_time = sum(m.evaluation_time for m in self.metrics.values())
        
        return {
            'total_nodes': total_nodes,
            'evaluated_nodes': evaluated_nodes,
            'cache_hits': cache_hits,
            'cache_hit_rate': cache_hits / evaluated_nodes if evaluated_nodes > 0 else 0,
            'total_evaluation_time': total_time,
            'avg_evaluation_time': total_time / evaluated_nodes if evaluated_nodes > 0 else 0
        }
    
    def invalidate_cache(self, node_id: str):
        """Invalidate cache for a node"""
        if self.cache:
            self.cache.invalidate(node_id)
        
        node = self.graph.get_node(node_id)
        if node:
            node._state = NodeState.PENDING
            node._result = None
            node._cache_timestamp = None
    
    def clear_all_cache(self):
        """Clear all cached results"""
        if self.cache:
            self.cache.clear_all()
        
        for node in self.graph.nodes.values():
            node._state = NodeState.PENDING
            node._result = None
            node._cache_timestamp = None
    
    def export_graph(self, output_path: str):
        """Export dependency graph to JSON"""
        graph_data = self.graph.to_dict()
        graph_data['metrics'] = self.get_metrics()
        graph_data['summary'] = self.get_summary()
        
        with open(output_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
    
    def visualize_graph(self) -> str:
        """
        Generate a text-based visualization of the dependency graph.
        
        Returns:
            ASCII graph representation
        """
        lines = ["Lazy Evaluation Dependency Graph", "=" * 50, ""]
        
        eval_order = self.graph.topological_sort()
        
        for node_id in eval_order:
            node = self.graph.get_node(node_id)
            if not node:
                continue
            
            state_icon = {
                NodeState.PENDING: "⏳",
                NodeState.EVALUATING: "⚙️",
                NodeState.COMPLETED: "✅",
                NodeState.FAILED: "❌",
                NodeState.CACHED: "💾"
            }.get(node._state, "❓")
            
            lines.append(f"{state_icon} {node_id}")
            
            if node.dependencies:
                for dep_id in node.dependencies:
                    dep_node = self.graph.get_node(dep_id)
                    dep_state = dep_node._state if dep_node else NodeState.PENDING
                    dep_icon = {
                        NodeState.COMPLETED: "✅",
                        NodeState.CACHED: "💾",
                        NodeState.FAILED: "❌"
                    }.get(dep_state, "⏳")
                    lines.append(f"  ↳ {dep_icon} {dep_id}")
            
            if node_id in self.metrics:
                metric = self.metrics[node_id]
                if metric.cache_hit:
                    lines.append(f"     [CACHED]")
                elif metric.evaluation_time > 0:
                    lines.append(f"     [Eval: {metric.evaluation_time:.3f}s]")
            
            lines.append("")
        
        return "\n".join(lines)


def main():
    """CLI entry point with examples"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Lazy Workflow Evaluation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run example workflow
  python lazy-workflow-evaluator.py --example
  
  # Export graph
  python lazy-workflow-evaluator.py --export graph.json
  
  # Clear cache
  python lazy-workflow-evaluator.py --clear-cache
        """
    )
    
    parser.add_argument('--example', action='store_true',
                       help='Run example workflow evaluation')
    parser.add_argument('--export', metavar='FILE',
                       help='Export dependency graph to JSON file')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear evaluation cache')
    parser.add_argument('--cache-dir', metavar='DIR',
                       help='Cache directory (default: .cache/lazy-eval)')
    
    args = parser.parse_args()
    
    if args.clear_cache:
        cache = ComputationCache(args.cache_dir)
        cache.clear_all()
        print("✅ Cache cleared")
        return
    
    if args.example:
        print("🚀 Running Example Workflow Evaluation")
        print("=" * 60)
        
        # Create engine
        engine = EvaluationEngine(cache_dir=args.cache_dir)
        
        # Define example workflows
        def fetch_data():
            """Simulate expensive data fetching"""
            print("  📥 Fetching data...")
            time.sleep(0.5)
            return {"data": [1, 2, 3, 4, 5]}
        
        def analyze_data(fetch_data):
            """Analyze fetched data"""
            print("  📊 Analyzing data...")
            time.sleep(0.3)
            return {"sum": sum(fetch_data["data"]), "count": len(fetch_data["data"])}
        
        def generate_report(analyze_data):
            """Generate report from analysis"""
            print("  📝 Generating report...")
            time.sleep(0.2)
            return f"Report: Sum={analyze_data['sum']}, Count={analyze_data['count']}"
        
        # Register workflows
        engine.register_workflow('fetch_data', fetch_data, cache_ttl=30)
        engine.register_workflow('analyze_data', analyze_data, 
                                dependencies=['fetch_data'], cache_ttl=30)
        engine.register_workflow('generate_report', generate_report,
                                dependencies=['analyze_data'], cache_ttl=30)
        
        # First evaluation
        print("\n🔄 First Evaluation (should compute everything):")
        result1 = engine.evaluate('generate_report')
        print(f"\n✅ Result: {result1}")
        
        # Second evaluation (should use cache)
        print("\n🔄 Second Evaluation (should use cache):")
        result2 = engine.evaluate('generate_report')
        print(f"\n✅ Result: {result2}")
        
        # Print summary
        print("\n📈 Evaluation Summary:")
        summary = engine.get_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # Visualize graph
        print("\n" + engine.visualize_graph())
        
        if args.export:
            engine.export_graph(args.export)
            print(f"\n📄 Graph exported to: {args.export}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
