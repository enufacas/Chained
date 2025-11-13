#!/usr/bin/env python3
"""
Comprehensive tests for Lazy Workflow Evaluation System

Tests cover:
- LazyWorkflowNode creation and state management
- ComputationCache with TTL and persistence
- DependencyGraph with cycle detection
- EvaluationEngine with lazy evaluation
- Cache hit/miss scenarios
- Topological sorting
- Error handling

Created by: @investigate-champion
Test Philosophy: Thorough, systematic validation of all components
"""

import os
import sys
import time
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
import importlib.util

# Load the lazy evaluator module
spec = importlib.util.spec_from_file_location(
    "lazy_workflow_evaluator",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "lazy-workflow-evaluator.py")
)
evaluator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator_module)

# Import classes
NodeState = evaluator_module.NodeState
EvaluationMetrics = evaluator_module.EvaluationMetrics
LazyWorkflowNode = evaluator_module.LazyWorkflowNode
ComputationCache = evaluator_module.ComputationCache
DependencyGraph = evaluator_module.DependencyGraph
EvaluationEngine = evaluator_module.EvaluationEngine


# Test fixtures
class TestCounter:
    """Helper to count function calls"""
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1
        return self.count


def test_node_state_enum():
    """Test NodeState enum values"""
    assert NodeState.PENDING.value == "pending"
    assert NodeState.EVALUATING.value == "evaluating"
    assert NodeState.COMPLETED.value == "completed"
    assert NodeState.FAILED.value == "failed"
    assert NodeState.CACHED.value == "cached"
    print("✅ test_node_state_enum passed")


def test_evaluation_metrics():
    """Test EvaluationMetrics dataclass"""
    metrics = EvaluationMetrics(
        node_id="test-node",
        state=NodeState.COMPLETED,
        evaluation_time=1.23,
        cache_hit=False,
        dependencies_count=2
    )
    
    assert metrics.node_id == "test-node"
    assert metrics.state == NodeState.COMPLETED
    assert metrics.evaluation_time == 1.23
    assert not metrics.cache_hit
    assert metrics.dependencies_count == 2
    
    # Test serialization
    data = metrics.to_dict()
    assert data['state'] == 'completed'
    assert data['evaluation_time'] == 1.23
    
    print("✅ test_evaluation_metrics passed")


def test_lazy_workflow_node_creation():
    """Test creating a LazyWorkflowNode"""
    def my_compute():
        return 42
    
    node = LazyWorkflowNode(
        node_id="test-node",
        compute_fn=my_compute,
        dependencies=["dep1", "dep2"],
        cache_ttl=3600,
        metadata={"type": "test"}
    )
    
    assert node.node_id == "test-node"
    assert node.compute_fn == my_compute
    assert node.dependencies == ["dep1", "dep2"]
    assert node.cache_ttl == 3600
    assert node.metadata["type"] == "test"
    assert node._state == NodeState.PENDING
    assert not node.is_evaluated()
    
    print("✅ test_lazy_workflow_node_creation passed")


def test_lazy_workflow_node_state_management():
    """Test node state transitions"""
    node = LazyWorkflowNode(node_id="test", compute_fn=lambda: 42)
    
    # Initial state
    assert node._state == NodeState.PENDING
    assert not node.is_evaluated()
    
    # Set result
    node.set_result(100)
    assert node.is_evaluated()
    assert node._state == NodeState.COMPLETED
    assert node.get_result() == 100
    
    # Check cache validity
    assert node.is_cache_valid()
    
    print("✅ test_lazy_workflow_node_state_management passed")


def test_lazy_workflow_node_cache_expiry():
    """Test cache TTL expiration"""
    node = LazyWorkflowNode(node_id="test", compute_fn=lambda: 42, cache_ttl=1)
    
    # Set result
    node.set_result(100)
    assert node.is_cache_valid()
    
    # Wait for cache to expire
    time.sleep(1.1)
    assert not node.is_cache_valid()
    
    print("✅ test_lazy_workflow_node_cache_expiry passed")


def test_lazy_workflow_node_serialization():
    """Test node serialization"""
    node = LazyWorkflowNode(
        node_id="test",
        dependencies=["dep1"],
        cache_ttl=60,
        metadata={"key": "value"}
    )
    
    data = node.to_dict()
    assert data['node_id'] == "test"
    assert data['dependencies'] == ["dep1"]
    assert data['cache_ttl'] == 60
    assert data['metadata']['key'] == "value"
    assert data['state'] == 'pending'
    
    print("✅ test_lazy_workflow_node_serialization passed")


def test_computation_cache_initialization():
    """Test ComputationCache initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ComputationCache(cache_dir=tmpdir)
        
        assert cache.cache_dir == Path(tmpdir)
        assert cache.cache_dir.exists()
        assert len(cache._memory_cache) == 0
    
    print("✅ test_computation_cache_initialization passed")


def test_computation_cache_set_and_get():
    """Test caching and retrieval"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ComputationCache(cache_dir=tmpdir)
        
        # Store a value
        cache.set("node1", "hash123", {"result": 42}, ttl=3600)
        
        # Retrieve it
        result = cache.get("node1", "hash123", ttl=3600)
        assert result == {"result": 42}
        
        # Different hash should return None
        result2 = cache.get("node1", "hash456", ttl=3600)
        assert result2 is None
    
    print("✅ test_computation_cache_set_and_get passed")


def test_computation_cache_expiry():
    """Test cache TTL expiration"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ComputationCache(cache_dir=tmpdir)
        
        # Store with short TTL
        cache.set("node1", "hash123", {"result": 42}, ttl=1)
        
        # Should be available immediately
        result = cache.get("node1", "hash123", ttl=1)
        assert result == {"result": 42}
        
        # Wait for expiry
        time.sleep(1.1)
        
        # Should return None after expiry
        result2 = cache.get("node1", "hash123", ttl=1)
        assert result2 is None
    
    print("✅ test_computation_cache_expiry passed")


def test_computation_cache_persistence():
    """Test cache persistence to disk"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create cache and store value
        cache1 = ComputationCache(cache_dir=tmpdir)
        cache1.set("node1", "hash123", {"result": 99}, ttl=3600)
        
        # Create new cache instance (simulating process restart)
        cache2 = ComputationCache(cache_dir=tmpdir)
        
        # Should load from disk
        result = cache2.get("node1", "hash123", ttl=3600)
        assert result == {"result": 99}
    
    print("✅ test_computation_cache_persistence passed")


def test_computation_cache_invalidation():
    """Test cache invalidation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ComputationCache(cache_dir=tmpdir)
        
        # Store values
        cache.set("node1", "hash1", {"result": 1}, ttl=3600)
        cache.set("node1", "hash2", {"result": 2}, ttl=3600)
        cache.set("node2", "hash3", {"result": 3}, ttl=3600)
        
        # Invalidate node1
        cache.invalidate("node1")
        
        # node1 entries should be gone
        assert cache.get("node1", "hash1", ttl=3600) is None
        assert cache.get("node1", "hash2", ttl=3600) is None
        
        # node2 should still exist
        assert cache.get("node2", "hash3", ttl=3600) == {"result": 3}
    
    print("✅ test_computation_cache_invalidation passed")


def test_computation_cache_clear_all():
    """Test clearing entire cache"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ComputationCache(cache_dir=tmpdir)
        
        # Store multiple values
        cache.set("node1", "hash1", {"result": 1}, ttl=3600)
        cache.set("node2", "hash2", {"result": 2}, ttl=3600)
        
        # Clear all
        cache.clear_all()
        
        # All should be gone
        assert cache.get("node1", "hash1", ttl=3600) is None
        assert cache.get("node2", "hash2", ttl=3600) is None
        assert len(cache._memory_cache) == 0
    
    print("✅ test_computation_cache_clear_all passed")


def test_computation_cache_stats():
    """Test cache statistics"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = ComputationCache(cache_dir=tmpdir)
        
        # Store values
        cache.set("node1", "hash1", {"result": 1}, ttl=3600)
        cache.set("node2", "hash2", {"result": 2}, ttl=3600)
        
        stats = cache.get_stats()
        assert stats['memory_entries'] == 2
        assert stats['disk_entries'] >= 2
        assert stats['total_size_bytes'] > 0
    
    print("✅ test_computation_cache_stats passed")


def test_dependency_graph_add_node():
    """Test adding nodes to graph"""
    graph = DependencyGraph()
    
    node1 = LazyWorkflowNode(node_id="node1", dependencies=[])
    node2 = LazyWorkflowNode(node_id="node2", dependencies=["node1"])
    
    graph.add_node(node1)
    graph.add_node(node2)
    
    assert len(graph.nodes) == 2
    assert graph.get_node("node1") == node1
    assert graph.get_node("node2") == node2
    
    print("✅ test_dependency_graph_add_node passed")


def test_dependency_graph_relationships():
    """Test dependency and dependent relationships"""
    graph = DependencyGraph()
    
    node1 = LazyWorkflowNode(node_id="node1", dependencies=[])
    node2 = LazyWorkflowNode(node_id="node2", dependencies=["node1"])
    node3 = LazyWorkflowNode(node_id="node3", dependencies=["node1", "node2"])
    
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    
    # Check dependencies
    assert graph.get_dependencies("node1") == []
    assert graph.get_dependencies("node2") == ["node1"]
    assert set(graph.get_dependencies("node3")) == {"node1", "node2"}
    
    # Check dependents
    assert set(graph.get_dependents("node1")) == {"node2", "node3"}
    assert graph.get_dependents("node2") == ["node3"]
    assert graph.get_dependents("node3") == []
    
    print("✅ test_dependency_graph_relationships passed")


def test_dependency_graph_cycle_detection():
    """Test cycle detection in graph"""
    graph = DependencyGraph()
    
    # Create cycle: node1 -> node2 -> node3 -> node1
    node1 = LazyWorkflowNode(node_id="node1", dependencies=["node3"])
    node2 = LazyWorkflowNode(node_id="node2", dependencies=["node1"])
    node3 = LazyWorkflowNode(node_id="node3", dependencies=["node2"])
    
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    
    has_cycle, cycle = graph.has_cycles()
    assert has_cycle
    assert cycle is not None
    assert len(cycle) > 0
    
    print("✅ test_dependency_graph_cycle_detection passed")


def test_dependency_graph_no_cycles():
    """Test graph without cycles"""
    graph = DependencyGraph()
    
    node1 = LazyWorkflowNode(node_id="node1", dependencies=[])
    node2 = LazyWorkflowNode(node_id="node2", dependencies=["node1"])
    node3 = LazyWorkflowNode(node_id="node3", dependencies=["node2"])
    
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    
    has_cycle, cycle = graph.has_cycles()
    assert not has_cycle
    assert cycle is None
    
    print("✅ test_dependency_graph_no_cycles passed")


def test_dependency_graph_topological_sort():
    """Test topological sorting"""
    graph = DependencyGraph()
    
    node1 = LazyWorkflowNode(node_id="node1", dependencies=[])
    node2 = LazyWorkflowNode(node_id="node2", dependencies=["node1"])
    node3 = LazyWorkflowNode(node_id="node3", dependencies=["node1"])
    node4 = LazyWorkflowNode(node_id="node4", dependencies=["node2", "node3"])
    
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    
    order = graph.topological_sort()
    
    # node1 should come before node2, node3, node4
    assert order.index("node1") < order.index("node2")
    assert order.index("node1") < order.index("node3")
    assert order.index("node1") < order.index("node4")
    
    # node2 and node3 should come before node4
    assert order.index("node2") < order.index("node4")
    assert order.index("node3") < order.index("node4")
    
    print("✅ test_dependency_graph_topological_sort passed")


def test_dependency_graph_transitive_dependencies():
    """Test finding transitive dependencies"""
    graph = DependencyGraph()
    
    node1 = LazyWorkflowNode(node_id="node1", dependencies=[])
    node2 = LazyWorkflowNode(node_id="node2", dependencies=["node1"])
    node3 = LazyWorkflowNode(node_id="node3", dependencies=["node2"])
    node4 = LazyWorkflowNode(node_id="node4", dependencies=["node3"])
    
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    
    # node4 transitively depends on all others
    trans_deps = graph.get_transitive_dependencies("node4")
    assert trans_deps == {"node1", "node2", "node3"}
    
    # node2 depends only on node1
    trans_deps2 = graph.get_transitive_dependencies("node2")
    assert trans_deps2 == {"node1"}
    
    print("✅ test_dependency_graph_transitive_dependencies passed")


def test_dependency_graph_serialization():
    """Test graph serialization"""
    graph = DependencyGraph()
    
    node1 = LazyWorkflowNode(node_id="node1", dependencies=[])
    node2 = LazyWorkflowNode(node_id="node2", dependencies=["node1"])
    
    graph.add_node(node1)
    graph.add_node(node2)
    
    data = graph.to_dict()
    
    assert 'nodes' in data
    assert 'edges' in data
    assert 'node1' in data['nodes']
    assert 'node2' in data['nodes']
    assert data['edges']['node2'] == ['node1']
    
    print("✅ test_dependency_graph_serialization passed")


def test_evaluation_engine_initialization():
    """Test EvaluationEngine initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = EvaluationEngine(cache_dir=tmpdir, enable_cache=True)
        
        assert engine.enable_cache
        assert engine.cache is not None
        assert isinstance(engine.graph, DependencyGraph)
        assert len(engine.metrics) == 0
    
    print("✅ test_evaluation_engine_initialization passed")


def test_evaluation_engine_register_workflow():
    """Test registering workflows"""
    engine = EvaluationEngine(enable_cache=False)
    
    def compute():
        return 42
    
    node = engine.register_workflow(
        node_id="test-workflow",
        compute_fn=compute,
        dependencies=[],
        cache_ttl=60,
        metadata={"type": "test"}
    )
    
    assert node.node_id == "test-workflow"
    assert node.compute_fn == compute
    assert engine.graph.get_node("test-workflow") == node
    
    print("✅ test_evaluation_engine_register_workflow passed")


def test_evaluation_engine_simple_evaluation():
    """Test simple evaluation without dependencies"""
    engine = EvaluationEngine(enable_cache=False)
    
    counter = TestCounter()
    
    def compute():
        counter.increment()
        return 100
    
    engine.register_workflow("simple", compute)
    
    result = engine.evaluate("simple")
    assert result == 100
    assert counter.count == 1
    
    print("✅ test_evaluation_engine_simple_evaluation passed")


def test_evaluation_engine_dependency_chain():
    """Test evaluation with dependency chain"""
    engine = EvaluationEngine(enable_cache=False)
    
    def step1():
        return 10
    
    def step2(step1):
        return step1 * 2
    
    def step3(step2):
        return step2 + 5
    
    engine.register_workflow("step1", step1)
    engine.register_workflow("step2", step2, dependencies=["step1"])
    engine.register_workflow("step3", step3, dependencies=["step2"])
    
    result = engine.evaluate("step3")
    assert result == 25  # (10 * 2) + 5
    
    print("✅ test_evaluation_engine_dependency_chain passed")


def test_evaluation_engine_multiple_dependencies():
    """Test evaluation with multiple dependencies"""
    engine = EvaluationEngine(enable_cache=False)
    
    def fetch_a():
        return 10
    
    def fetch_b():
        return 20
    
    def combine(fetch_a, fetch_b):
        return fetch_a + fetch_b
    
    engine.register_workflow("fetch_a", fetch_a)
    engine.register_workflow("fetch_b", fetch_b)
    engine.register_workflow("combine", combine, dependencies=["fetch_a", "fetch_b"])
    
    result = engine.evaluate("combine")
    assert result == 30
    
    print("✅ test_evaluation_engine_multiple_dependencies passed")


def test_evaluation_engine_caching():
    """Test that caching prevents re-evaluation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = EvaluationEngine(cache_dir=tmpdir, enable_cache=True)
        
        counter = TestCounter()
        
        def expensive_compute():
            counter.increment()
            return 42
        
        engine.register_workflow("expensive", expensive_compute, cache_ttl=3600)
        
        # First evaluation
        result1 = engine.evaluate("expensive")
        assert result1 == 42
        assert counter.count == 1
        
        # Second evaluation (should use cache)
        result2 = engine.evaluate("expensive")
        assert result2 == 42
        assert counter.count == 1  # Not incremented again
        
        # Check metrics
        metrics = engine.get_metrics()
        assert "expensive" in metrics
        # Second evaluation should be a cache hit
        assert metrics["expensive"]["cache_hit"]
    
    print("✅ test_evaluation_engine_caching passed")


def test_evaluation_engine_force_re_evaluation():
    """Test forcing re-evaluation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = EvaluationEngine(cache_dir=tmpdir, enable_cache=True)
        
        counter = TestCounter()
        
        def compute():
            return counter.increment()
        
        engine.register_workflow("counter", compute, cache_ttl=3600)
        
        # First evaluation
        result1 = engine.evaluate("counter")
        assert result1 == 1
        
        # Second evaluation (cached)
        result2 = engine.evaluate("counter")
        assert result2 == 1
        
        # Force re-evaluation
        result3 = engine.evaluate("counter", force=True)
        assert result3 == 2  # Counter incremented again
    
    print("✅ test_evaluation_engine_force_re_evaluation passed")


def test_evaluation_engine_error_handling():
    """Test error handling during evaluation"""
    engine = EvaluationEngine(enable_cache=False)
    
    def failing_compute():
        raise ValueError("Test error")
    
    engine.register_workflow("failing", failing_compute)
    
    try:
        engine.evaluate("failing")
        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "Failed to evaluate" in str(e)
        
        # Check metrics
        metrics = engine.get_metrics()
        assert "failing" in metrics
        assert metrics["failing"]["state"] == "failed"
        assert "Test error" in metrics["failing"]["error_message"]
    
    print("✅ test_evaluation_engine_error_handling passed")


def test_evaluation_engine_evaluate_all():
    """Test evaluating all nodes"""
    engine = EvaluationEngine(enable_cache=False)
    
    engine.register_workflow("a", lambda: 1)
    engine.register_workflow("b", lambda a: a + 1, dependencies=["a"])
    engine.register_workflow("c", lambda b: b * 2, dependencies=["b"])
    
    results = engine.evaluate_all()
    
    assert results["a"] == 1
    assert results["b"] == 2
    assert results["c"] == 4
    
    print("✅ test_evaluation_engine_evaluate_all passed")


def test_evaluation_engine_summary():
    """Test getting evaluation summary"""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = EvaluationEngine(cache_dir=tmpdir, enable_cache=True)
        
        engine.register_workflow("a", lambda: 1)
        engine.register_workflow("b", lambda a: a + 1, dependencies=["a"])
        
        # Evaluate twice to get cache hit
        engine.evaluate("b")
        engine.evaluate("b")
        
        summary = engine.get_summary()
        
        assert summary['total_nodes'] == 2
        assert summary['evaluated_nodes'] >= 2
        assert summary['cache_hits'] >= 1
        assert summary['cache_hit_rate'] > 0
    
    print("✅ test_evaluation_engine_summary passed")


def test_evaluation_engine_cache_invalidation():
    """Test cache invalidation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = EvaluationEngine(cache_dir=tmpdir, enable_cache=True)
        
        counter = TestCounter()
        
        def compute():
            return counter.increment()
        
        engine.register_workflow("counter", compute, cache_ttl=3600)
        
        # First evaluation
        result1 = engine.evaluate("counter")
        assert result1 == 1
        
        # Invalidate cache
        engine.invalidate_cache("counter")
        
        # Next evaluation should re-compute
        result2 = engine.evaluate("counter")
        assert result2 == 2
    
    print("✅ test_evaluation_engine_cache_invalidation passed")


def test_evaluation_engine_export_graph():
    """Test exporting dependency graph"""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = EvaluationEngine(enable_cache=False)
        
        engine.register_workflow("a", lambda: 1)
        engine.register_workflow("b", lambda a: a + 1, dependencies=["a"])
        
        engine.evaluate("b")
        
        output_path = os.path.join(tmpdir, "graph.json")
        engine.export_graph(output_path)
        
        # Check file was created
        assert os.path.exists(output_path)
        
        # Check contents
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        assert 'nodes' in data
        assert 'edges' in data
        assert 'metrics' in data
        assert 'summary' in data
    
    print("✅ test_evaluation_engine_export_graph passed")


def test_evaluation_engine_visualize_graph():
    """Test graph visualization"""
    engine = EvaluationEngine(enable_cache=False)
    
    engine.register_workflow("a", lambda: 1)
    engine.register_workflow("b", lambda a: a + 1, dependencies=["a"])
    
    engine.evaluate("b")
    
    viz = engine.visualize_graph()
    
    assert "Lazy Evaluation Dependency Graph" in viz
    assert "a" in viz
    assert "b" in viz
    assert "✅" in viz  # Completed icon
    
    print("✅ test_evaluation_engine_visualize_graph passed")


def test_evaluation_engine_cycle_detection_error():
    """Test that evaluation fails with cycles"""
    engine = EvaluationEngine(enable_cache=False)
    
    # Create a cycle (won't work with lambda, but for testing)
    # We need to manually create nodes with circular dependencies
    node_a = LazyWorkflowNode("a", lambda b: b + 1, dependencies=["b"])
    node_b = LazyWorkflowNode("b", lambda a: a + 1, dependencies=["a"])
    
    engine.register(node_a)
    engine.register(node_b)
    
    try:
        engine.evaluate("a")
        assert False, "Should have raised ValueError for cycle"
    except ValueError as e:
        assert "cycle" in str(e).lower()
    
    print("✅ test_evaluation_engine_cycle_detection_error passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("🧪 Running Lazy Workflow Evaluator Tests")
    print("   Created by: @investigate-champion")
    print("=" * 70)
    print()
    
    test_functions = [
        test_node_state_enum,
        test_evaluation_metrics,
        test_lazy_workflow_node_creation,
        test_lazy_workflow_node_state_management,
        test_lazy_workflow_node_cache_expiry,
        test_lazy_workflow_node_serialization,
        test_computation_cache_initialization,
        test_computation_cache_set_and_get,
        test_computation_cache_expiry,
        test_computation_cache_persistence,
        test_computation_cache_invalidation,
        test_computation_cache_clear_all,
        test_computation_cache_stats,
        test_dependency_graph_add_node,
        test_dependency_graph_relationships,
        test_dependency_graph_cycle_detection,
        test_dependency_graph_no_cycles,
        test_dependency_graph_topological_sort,
        test_dependency_graph_transitive_dependencies,
        test_dependency_graph_serialization,
        test_evaluation_engine_initialization,
        test_evaluation_engine_register_workflow,
        test_evaluation_engine_simple_evaluation,
        test_evaluation_engine_dependency_chain,
        test_evaluation_engine_multiple_dependencies,
        test_evaluation_engine_caching,
        test_evaluation_engine_force_re_evaluation,
        test_evaluation_engine_error_handling,
        test_evaluation_engine_evaluate_all,
        test_evaluation_engine_summary,
        test_evaluation_engine_cache_invalidation,
        test_evaluation_engine_export_graph,
        test_evaluation_engine_visualize_graph,
        test_evaluation_engine_cycle_detection_error,
    ]
    
    passed = 0
    failed = 0
    
    for test_fn in test_functions:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"❌ {test_fn.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 70)
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(f"📊 Total Tests:  {passed + failed}")
    print("=" * 70)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
