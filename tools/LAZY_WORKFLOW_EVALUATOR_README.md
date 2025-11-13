# Lazy Workflow Evaluator

> **Created by:** @investigate-champion  
> **Inspired by:** Ada Lovelace's visionary approach to computation  
> **Purpose:** Optimize workflow execution through intelligent lazy evaluation

## Overview

The Lazy Workflow Evaluator is a sophisticated system for optimizing workflow dependencies through lazy evaluation and intelligent caching. It ensures that expensive computations are only performed when their results are actually needed, and caches results to avoid redundant work.

## Key Features

- 🚀 **Lazy Evaluation**: Defer computation until results are actually needed
- 💾 **Intelligent Caching**: Cache computed values with TTL-based invalidation
- 🔄 **Dependency Management**: Automatic dependency resolution with topological sorting
- 🔍 **Cycle Detection**: Prevents circular dependencies that would cause infinite loops
- 📊 **Performance Tracking**: Detailed metrics on evaluation time and cache efficiency
- 🎯 **Both Workflow & Step Level**: Support for coarse and fine-grained lazy evaluation
- 🔐 **Thread-Safe**: Safe for concurrent access with proper locking
- 💿 **Persistent Cache**: Results stored on disk for reuse across runs

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────┐
│           EvaluationEngine                      │
│  • Orchestrates lazy evaluation                │
│  • Manages dependency resolution                │
│  • Coordinates caching                          │
└────────────┬────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼──────┐    ┌────▼──────────┐
│Dependency│    │  Computation  │
│  Graph   │    │     Cache     │
│          │    │               │
│• Nodes   │    │• Memory Cache │
│• Edges   │    │• Disk Cache   │
│• Topo    │    │• TTL          │
└──────────┘    └───────────────┘
```

### Component Details

#### 1. LazyWorkflowNode
Represents a computation that can be deferred:
- **State Management**: PENDING → EVALUATING → COMPLETED/CACHED/FAILED
- **Cache Validation**: TTL-based expiration checking
- **Dependency Tracking**: Knows what it depends on and what depends on it

#### 2. DependencyGraph
Manages relationships between nodes:
- **Topological Sorting**: Ensures dependencies evaluate before dependents
- **Cycle Detection**: DFS-based cycle detection prevents infinite loops
- **Transitive Dependencies**: Computes full dependency closure

#### 3. ComputationCache
Two-tier caching system:
- **Memory Cache**: Fast in-memory lookups for hot data
- **Disk Cache**: Persistent storage using pickle
- **Metadata Tracking**: JSON metadata for cache invalidation

#### 4. EvaluationEngine
Main orchestrator:
- **Lazy Evaluation**: Only evaluate what's needed
- **Cache-First**: Check cache before computing
- **Metrics Collection**: Track performance and efficiency

## Usage

### Basic Example

```python
from lazy_workflow_evaluator import EvaluationEngine

# Create engine
engine = EvaluationEngine()

# Define workflows
def fetch_data():
    """Expensive data fetching"""
    return expensive_api_call()

def analyze_data(fetch_data):
    """Analysis depends on data"""
    return analyze(fetch_data)

def generate_report(analyze_data):
    """Report depends on analysis"""
    return create_report(analyze_data)

# Register workflows with dependencies
engine.register_workflow('fetch_data', fetch_data, cache_ttl=3600)
engine.register_workflow('analyze_data', analyze_data, 
                        dependencies=['fetch_data'], cache_ttl=1800)
engine.register_workflow('generate_report', generate_report,
                        dependencies=['analyze_data'], cache_ttl=900)

# Evaluate lazily - only computes when needed
result = engine.evaluate('generate_report')

# Second evaluation uses cache - much faster!
result2 = engine.evaluate('generate_report')
```

### Advanced Usage

#### Custom Cache Directory

```python
engine = EvaluationEngine(cache_dir='/path/to/cache')
```

#### Disable Caching

```python
engine = EvaluationEngine(enable_cache=False)
```

#### Force Re-evaluation

```python
# Ignore cache and re-compute
result = engine.evaluate('workflow_id', force=True)
```

#### Invalidate Specific Cache

```python
# Clear cache for specific workflow
engine.invalidate_cache('workflow_id')
```

#### Evaluate All Workflows

```python
# Evaluate entire dependency graph
results = engine.evaluate_all()
```

#### Get Performance Metrics

```python
# Detailed metrics per workflow
metrics = engine.get_metrics()

# Summary statistics
summary = engine.get_summary()
print(f"Cache hit rate: {summary['cache_hit_rate']:.1%}")
```

#### Visualize Dependency Graph

```python
# ASCII visualization
print(engine.visualize_graph())

# Export to JSON
engine.export_graph('workflow-graph.json')
```

## Integration with Workflow Orchestrator

The Lazy Workflow Evaluator integrates seamlessly with the existing workflow orchestrator:

```python
from workflow_orchestrator import WorkflowOrchestrator
from lazy_workflow_evaluator import EvaluationEngine

# Create both systems
orchestrator = WorkflowOrchestrator()
evaluator = EvaluationEngine()

# Register workflows that need lazy evaluation
def expensive_learning():
    # Only runs if results not cached
    return orchestrator.run_learning_workflow()

evaluator.register_workflow(
    'learn-from-tldr',
    expensive_learning,
    cache_ttl=7200  # 2 hours
)

# Evaluate lazily
result = evaluator.evaluate('learn-from-tldr')
```

## Performance Optimization

### When to Use Lazy Evaluation

✅ **Good Use Cases:**
- Expensive API calls that rarely change
- Complex data analysis that can be reused
- Workflows with optional branches
- Computations with many dependencies
- Workflows triggered frequently with same inputs

❌ **Poor Use Cases:**
- Real-time data that must be fresh
- Workflows with side effects that must always run
- Very fast computations (overhead not worth it)
- Workflows that always produce different results

### Cache TTL Guidelines

| Data Type | Recommended TTL | Reason |
|-----------|----------------|---------|
| External API calls | 1-6 hours | Balance freshness vs cost |
| Analysis results | 30-60 minutes | Data may change moderately |
| Generated reports | 15-30 minutes | Users expect recent data |
| Static data | 24 hours+ | Rarely changes |
| Real-time metrics | Disable cache | Must be current |

### Memory Management

The cache automatically manages memory through:
- **Two-tier storage**: Memory + Disk
- **TTL expiration**: Old entries automatically removed
- **Selective invalidation**: Clear specific nodes
- **Size monitoring**: Track cache size with `get_stats()`

## CLI Usage

### Run Example

```bash
python tools/lazy-workflow-evaluator.py --example
```

### Export Graph

```bash
python tools/lazy-workflow-evaluator.py --example --export graph.json
```

### Clear Cache

```bash
python tools/lazy-workflow-evaluator.py --clear-cache
```

### Custom Cache Directory

```bash
python tools/lazy-workflow-evaluator.py --example --cache-dir /tmp/my-cache
```

## Testing

Comprehensive test suite with 34 tests:

```bash
# Run all tests
python tools/test_lazy_workflow_evaluator.py
```

Test coverage includes:
- ✅ Node state management and transitions
- ✅ Cache storage, retrieval, and expiration
- ✅ Dependency graph construction and traversal
- ✅ Cycle detection and prevention
- ✅ Topological sorting
- ✅ Lazy evaluation with multiple dependencies
- ✅ Cache hit/miss scenarios
- ✅ Error handling and recovery
- ✅ Metrics collection and reporting
- ✅ Graph serialization and visualization

## API Reference

### EvaluationEngine

```python
EvaluationEngine(cache_dir: Optional[str] = None, enable_cache: bool = True)
```

**Methods:**
- `register_workflow(node_id, compute_fn, dependencies=[], cache_ttl=3600, metadata={})`
- `evaluate(node_id, force=False)` → Any
- `evaluate_all(force=False)` → Dict[str, Any]
- `get_metrics()` → Dict[str, Dict]
- `get_summary()` → Dict[str, Any]
- `invalidate_cache(node_id)`
- `clear_all_cache()`
- `export_graph(output_path)`
- `visualize_graph()` → str

### LazyWorkflowNode

```python
LazyWorkflowNode(
    node_id: str,
    compute_fn: Optional[Callable] = None,
    dependencies: List[str] = [],
    cache_ttl: int = 3600,
    metadata: Dict = {}
)
```

**Methods:**
- `is_evaluated()` → bool
- `is_cache_valid()` → bool
- `get_result()` → Any
- `set_result(result, from_cache=False)`
- `to_dict()` → Dict

### ComputationCache

```python
ComputationCache(cache_dir: Optional[str] = None)
```

**Methods:**
- `get(node_id, dependencies_hash, ttl)` → Optional[Any]
- `set(node_id, dependencies_hash, result, ttl)`
- `invalidate(node_id)`
- `clear_all()`
- `get_stats()` → Dict

### DependencyGraph

```python
DependencyGraph()
```

**Methods:**
- `add_node(node: LazyWorkflowNode)`
- `get_node(node_id)` → Optional[LazyWorkflowNode]
- `get_dependencies(node_id)` → List[str]
- `get_dependents(node_id)` → List[str]
- `has_cycles()` → Tuple[bool, Optional[List[str]]]
- `topological_sort()` → List[str]
- `get_transitive_dependencies(node_id)` → Set[str]
- `to_dict()` → Dict

## Performance Characteristics

### Time Complexity
- **Evaluation** (first time): O(V + E) where V = nodes, E = dependencies
- **Evaluation** (cached): O(1) for cache hit
- **Topological Sort**: O(V + E) using Kahn's algorithm
- **Cycle Detection**: O(V + E) using DFS

### Space Complexity
- **Memory Cache**: O(N) where N = number of cached results
- **Disk Cache**: Limited by available disk space
- **Dependency Graph**: O(V + E)

### Cache Performance
Based on typical usage patterns:
- **Cache Hit Rate**: 60-90% for repeated workflows
- **Speedup**: 10-100x for expensive computations
- **Memory Overhead**: ~10-50 KB per cached result

## Best Practices

### 1. Design for Idempotency
```python
# Good: Pure function
def analyze_data(input_data):
    return calculate_metrics(input_data)

# Bad: Side effects
def analyze_data(input_data):
    write_to_database(input_data)  # Side effect!
    return calculate_metrics(input_data)
```

### 2. Choose Appropriate TTLs
```python
# Fast-changing data - short TTL
engine.register_workflow('stock-prices', fetch_prices, cache_ttl=60)

# Slow-changing data - long TTL
engine.register_workflow('user-profiles', fetch_profiles, cache_ttl=3600)
```

### 3. Handle Dependencies Correctly
```python
# Good: Declare all dependencies
engine.register_workflow('report', generate_report, 
                        dependencies=['data', 'config'])

# Bad: Hidden dependencies
def generate_report():
    data = fetch_data()  # Should be a dependency!
    return create_report(data)
```

### 4. Monitor Cache Performance
```python
summary = engine.get_summary()
if summary['cache_hit_rate'] < 0.3:
    print("Warning: Low cache hit rate - review TTL settings")
```

### 5. Clean Up Old Cache
```python
# Periodically clear old cache files
if cache.get_stats()['total_size_bytes'] > 100_000_000:  # 100 MB
    engine.clear_all_cache()
```

## Troubleshooting

### Issue: Low Cache Hit Rate

**Symptoms:** Cache hit rate below 30%

**Causes:**
- TTL too short for data change frequency
- Dependencies change frequently
- Input data varies on each evaluation

**Solutions:**
1. Increase cache TTL for stable data
2. Review dependency hashing
3. Normalize input data

### Issue: High Memory Usage

**Symptoms:** Memory growing over time

**Causes:**
- Too many cached results
- Large result objects
- Memory cache not expiring

**Solutions:**
1. Reduce cache TTL
2. Clear cache periodically: `engine.clear_all_cache()`
3. Serialize large objects differently

### Issue: Circular Dependency Error

**Symptoms:** `ValueError: Cannot sort graph with cycles`

**Causes:**
- A depends on B, B depends on A
- More complex circular dependency chains

**Solutions:**
1. Review dependency declarations
2. Break cycles by extracting shared dependencies
3. Use `graph.has_cycles()` to identify the cycle

### Issue: Cache Not Persisting

**Symptoms:** Cache always misses after restart

**Causes:**
- Cache directory permissions
- Disk full
- Pickle serialization errors

**Solutions:**
1. Check cache directory exists and is writable
2. Verify disk space: `cache.get_stats()`
3. Check logs for pickle errors

## Future Enhancements

Potential improvements identified by @investigate-champion:

1. **Distributed Caching**: Redis/Memcached support for multi-node systems
2. **Async Evaluation**: Support for async/await compute functions
3. **Partial Re-evaluation**: Only re-compute changed sub-graphs
4. **Cache Warming**: Pre-populate cache with predicted needs
5. **Adaptive TTL**: Automatically adjust TTL based on change frequency
6. **Dependency Inference**: Automatically detect dependencies from function calls
7. **Visual Dashboard**: Web UI for monitoring evaluations
8. **Cost Tracking**: Estimate API costs saved through caching

## Contributing

When extending the lazy evaluator:

1. **Maintain test coverage** - Add tests for new features
2. **Document behavior** - Update this README
3. **Follow patterns** - Match existing code style
4. **Consider performance** - Profile before and after changes
5. **Think about edge cases** - Handle errors gracefully

## License

Part of the Chained autonomous AI ecosystem. See repository LICENSE.

## Credits

**Design & Implementation:** @investigate-champion  
**Inspiration:** Ada Lovelace's visionary computational thinking  
**Testing Philosophy:** Thorough, systematic validation  

---

*"The analytical engine weaves algebraic patterns just as the Jacquard loom weaves flowers and leaves."* - Ada Lovelace

This lazy evaluation system weaves efficient computation patterns through intelligent deferral and caching, optimizing the Chained autonomous AI ecosystem.
