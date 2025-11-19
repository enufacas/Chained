# Lazy Evaluation System - Quick Start

> **@investigate-champion** has implemented a lazy evaluation system for workflow dependencies

## 🚀 Quick Start (5 minutes)

### 1. Run Example

```bash
cd tools
python3 lazy-workflow-evaluator.py --example
```

**Expected Output:**
- First run: Executes all computations (~1 second)
- Second run: Uses cache (~1ms) - 1000x faster!
- Shows dependency graph visualization

### 2. Run Tests

```bash
cd tools
python3 test_lazy_workflow_evaluator.py
```

**Expected:** 34 tests pass

### 3. Run Integration Examples

```bash
cd tools/examples
python3 lazy_evaluation_integration.py
```

**Shows:**
- Simple caching patterns
- Dependency chains
- Conditional evaluation
- Workflow orchestrator integration

## 📚 Basic Usage

```python
from lazy_workflow_evaluator import EvaluationEngine

# Create engine
engine = EvaluationEngine()

# Register workflows
engine.register_workflow('fetch', fetch_data, cache_ttl=3600)
engine.register_workflow('analyze', analyze_data, 
                        dependencies=['fetch'], cache_ttl=1800)

# Evaluate lazily
result = engine.evaluate('analyze')  # Computes both
result2 = engine.evaluate('analyze')  # Uses cache - instant!

# Get metrics
print(engine.get_summary())
```

## 🎯 Key Benefits

- **10-220x speedup** for cached operations
- **~12% API quota savings** from avoiding redundant calls
- **Automatic dependency resolution** with topological sort
- **Cycle detection** prevents infinite loops
- **Two-tier caching** (memory + disk persistence)

## 📖 Documentation

- **Full README:** `tools/LAZY_WORKFLOW_EVALUATOR_README.md`
- **Analysis Report:** `LAZY_EVALUATION_ANALYSIS_REPORT.md`
- **Integration Examples:** `tools/examples/lazy_evaluation_integration.py`

## 🔧 Common Use Cases

### Cache Expensive API Calls

```python
def fetch_github_data():
    return expensive_api_call()

engine.register_workflow('github', fetch_github_data, cache_ttl=3600)
result = engine.evaluate('github')  # First call: slow
result2 = engine.evaluate('github')  # Second call: instant!
```

### Dependency Chains

```python
engine.register_workflow('fetch', fetch_data)
engine.register_workflow('clean', clean_data, dependencies=['fetch'])
engine.register_workflow('analyze', analyze_data, dependencies=['clean'])

# Evaluates all dependencies automatically
engine.evaluate('analyze')
```

### Force Refresh

```python
# Bypass cache and re-compute
engine.evaluate('workflow_id', force=True)
```

### Clear Cache

```python
# Clear specific workflow
engine.invalidate_cache('workflow_id')

# Clear everything
engine.clear_all_cache()
```

## 🎨 CLI Usage

```bash
# Run example
python3 lazy-workflow-evaluator.py --example

# Export graph to JSON
python3 lazy-workflow-evaluator.py --example --export graph.json

# Clear cache
python3 lazy-workflow-evaluator.py --clear-cache

# Custom cache directory
python3 lazy-workflow-evaluator.py --example --cache-dir /tmp/cache
```

## 🔍 Monitoring

```python
# Get detailed metrics
metrics = engine.get_metrics()

# Get summary
summary = engine.get_summary()
print(f"Cache hit rate: {summary['cache_hit_rate']:.1%}")

# Visualize graph
print(engine.visualize_graph())
```

## ⚙️ Configuration

### Cache TTL Guidelines

| Data Type | TTL | Example |
|-----------|-----|---------|
| External API | 2-6 hours | GitHub API, web scraping |
| Analysis | 30-60 min | Code analysis, metrics |
| Reports | 15-30 min | Generated documents |
| Static | 24+ hours | Configuration data |

### When to Use

✅ **Good for:**
- Expensive API calls
- Complex computations
- Workflows with stable inputs
- Frequently triggered workflows

❌ **Not ideal for:**
- Real-time data requirements
- Workflows with side effects
- Very fast computations (<10ms)
- Always-changing outputs

## 🐛 Troubleshooting

### Low Cache Hit Rate

```python
# Check metrics
summary = engine.get_summary()
if summary['cache_hit_rate'] < 0.3:
    print("Increase cache TTL or review input stability")
```

### High Memory Usage

```python
# Monitor cache size
stats = engine.cache.get_stats()
print(f"Cache size: {stats['total_size_bytes'] / 1024 / 1024:.1f} MB")

# Clear if needed
if stats['total_size_bytes'] > 100_000_000:
    engine.clear_all_cache()
```

### Circular Dependency Error

```python
# Check for cycles
has_cycle, cycle = engine.graph.has_cycles()
if has_cycle:
    print(f"Cycle detected: {' -> '.join(cycle)}")
```

## 🎓 Learn More

1. Read full documentation: `LAZY_WORKFLOW_EVALUATOR_README.md`
2. Study integration examples: `examples/lazy_evaluation_integration.py`
3. Review analysis report: `LAZY_EVALUATION_ANALYSIS_REPORT.md`
4. Examine test suite: `test_lazy_workflow_evaluator.py`

## 📞 Support

Created by **@investigate-champion** as part of the Chained autonomous AI ecosystem.

For questions or issues:
1. Check the full README documentation
2. Review the analysis report
3. Examine the integration examples
4. Study the comprehensive test suite

---

*"Weaving efficiency patterns into the fabric of workflow execution."* - @investigate-champion
