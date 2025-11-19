# 📚 Accelerated Unsupervised Pattern Learning - Usage Guide

**By @accelerate-specialist (Edsger Dijkstra)**

This guide shows you how to use the accelerated unsupervised pattern learner for discovering patterns in Python codebases.

---

## 🚀 Quick Start

### Command Line Interface

```bash
# Analyze current directory
python3 tools/accelerated_pattern_learner.py -d .

# Analyze specific directory
python3 tools/accelerated_pattern_learner.py -d /path/to/repo

# Custom number of clusters
python3 tools/accelerated_pattern_learner.py -d src -k 15

# Save report to file
python3 tools/accelerated_pattern_learner.py -d src -o report.md

# Run performance comparison
python3 tools/accelerated_pattern_learner.py --compare -d src

# Show performance statistics
python3 tools/accelerated_pattern_learner.py -d src --stats
```

### Python API

```python
from accelerated_pattern_learner import AcceleratedPatternLearner

# Create learner instance
learner = AcceleratedPatternLearner()

# Extract features from directory
feature_count = learner.extract_features_from_directory('src')
print(f"Extracted {feature_count} features")

# Discover patterns
patterns = learner.discover_patterns(n_clusters=10, min_samples=3)
print(f"Discovered {len(patterns)} patterns")

# Generate report
report = learner.generate_report('markdown')
print(report)

# Get performance stats
stats = learner.get_performance_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']}")
```

---

## 🎯 Common Use Cases

### 1. Code Review - Find Unusual Patterns

```python
from accelerated_pattern_learner import AcceleratedPatternLearner

learner = AcceleratedPatternLearner()
learner.extract_features_from_directory('src')
patterns = learner.discover_patterns(n_clusters=15, min_samples=2)

# Find anomalies
anomalies = [p for p in patterns if p.pattern_type == 'anomaly']
print(f"Found {len(anomalies)} anomalous code patterns:")

for anomaly in anomalies:
    print(f"\n{anomaly.pattern_name}:")
    for example in anomaly.examples[:3]:
        print(f"  - {example['file']}:{example['line']}")
```

### 2. Refactoring - Identify Duplication

```python
from accelerated_pattern_learner import AcceleratedPatternLearner

learner = AcceleratedPatternLearner()
learner.extract_features_from_directory('src')
patterns = learner.discover_patterns(n_clusters=10)

# Find high-frequency patterns
high_freq = [p for p in patterns if p.occurrences > 20]
high_freq.sort(key=lambda p: p.occurrences, reverse=True)

print("High-frequency patterns (potential duplication):")
for pattern in high_freq[:5]:
    print(f"\n{pattern.pattern_name}: {pattern.occurrences} occurrences")
    print(f"  {pattern.description}")
```

### 3. Complexity Analysis

```python
from accelerated_pattern_learner import AcceleratedPatternLearner

learner = AcceleratedPatternLearner()
learner.extract_features_from_directory('src')
patterns = learner.discover_patterns()

# Find high-complexity patterns
complex_patterns = [
    p for p in patterns 
    if 'complex' in p.pattern_name.lower() or 'high-complexity' in p.category
]

print("High-complexity code patterns:")
for pattern in complex_patterns:
    print(f"\n{pattern.pattern_name}:")
    print(f"  Category: {pattern.category}")
    print(f"  Occurrences: {pattern.occurrences}")
    for example in pattern.examples[:3]:
        print(f"  - {example['file']}:{example['line']} - {example['type']}")
```

### 4. Documentation Quality Check

```python
from accelerated_pattern_learner import AcceleratedPatternLearner

learner = AcceleratedPatternLearner()
learner.extract_features_from_directory('src')
patterns = learner.discover_patterns()

# Find undocumented patterns
undocumented = [
    p for p in patterns 
    if 'not documented' in p.description.lower()
]

print(f"Found {len(undocumented)} patterns with poor documentation:")
for pattern in undocumented:
    print(f"\n{pattern.pattern_name}: {pattern.occurrences} cases")
    print(f"  Examples:")
    for ex in pattern.examples[:5]:
        print(f"    {ex['file']}:{ex['line']}")
```

### 5. Incremental Analysis

```python
from accelerated_pattern_learner import AcceleratedPatternLearner

# First run - full analysis
learner = AcceleratedPatternLearner()
learner.extract_features_from_directory('src')
patterns = learner.discover_patterns()

# Save patterns
learner.save_patterns()

# Later - reuse cached ASTs (faster)
learner2 = AcceleratedPatternLearner()
learner2.extract_features_from_directory('src')  # Uses cached ASTs
patterns2 = learner2.discover_patterns()

stats = learner2.get_performance_stats()
print(f"Second run cache hit rate: {stats['cache_hit_rate']}")
```

---

## ⚙️ Configuration Options

### Number of Clusters

Controls how many distinct patterns to discover:

```python
# Few clusters (broader patterns)
patterns = learner.discover_patterns(n_clusters=5)  # 5-10 broad categories

# Many clusters (fine-grained patterns)
patterns = learner.discover_patterns(n_clusters=20)  # 15-20 specific patterns
```

**Recommendation:**
- Small codebase (&lt;1000 files): `n_clusters=5-10`
- Medium codebase (1000-5000 files): `n_clusters=10-15`
- Large codebase (&gt;5000 files): `n_clusters=15-20`

### Minimum Samples

Controls how many examples needed to consider a pattern:

```python
# Strict (only common patterns)
patterns = learner.discover_patterns(min_samples=10)

# Lenient (include rare patterns)
patterns = learner.discover_patterns(min_samples=2)
```

**Recommendation:**
- Refactoring focus: `min_samples=5-10` (common patterns)
- Anomaly detection: `min_samples=2-3` (catch outliers)
- General analysis: `min_samples=3-5` (balanced)

### Output Format

```python
# Markdown (human-readable)
report = learner.generate_report('markdown')

# JSON (machine-readable)
report = learner.generate_report('json')
```

---

## 📊 Performance Tips

### 1. Use Caching for Multiple Analyses

```python
learner = AcceleratedPatternLearner()

# First analysis
learner.extract_features_from_directory('src')
patterns_5 = learner.discover_patterns(n_clusters=5)

# Second analysis (reuses cached ASTs and vectors)
patterns_10 = learner.discover_patterns(n_clusters=10)
patterns_15 = learner.discover_patterns(n_clusters=15)

# Clear cache when done
learner.clear_caches()
```

### 2. Analyze Specific Subdirectories

```python
# Instead of analyzing entire repo
learner.extract_features_from_directory('.')  # Slow

# Analyze specific areas
learner.extract_features_from_directory('src')  # Faster
# Or
learner.extract_features_from_directory('src/core')  # Even faster
```

### 3. Monitor Cache Performance

```python
learner = AcceleratedPatternLearner()
learner.extract_features_from_directory('src')

stats = learner.get_performance_stats()
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache misses: {stats['cache_misses']}")
print(f"Hit rate: {stats['cache_hit_rate']}")
```

---

## 🔍 Pattern Analysis Examples

### Example 1: Finding God Objects

```python
from accelerated_pattern_learner import AcceleratedPatternLearner

learner = AcceleratedPatternLearner()
learner.extract_features_from_directory('src')
patterns = learner.discover_patterns()

# Look for patterns with many children (methods/attributes)
god_objects = []
for pattern in patterns:
    if 'ClassDef' in pattern.pattern_name:
        # Get average children count from examples
        avg_children = sum(
            len(learner.features[i].children) 
            for i in range(len(learner.features)) 
            if learner.features[i].node_type == 'ClassDef'
        ) / pattern.occurrences if pattern.occurrences > 0 else 0
        
        if avg_children > 15:  # Many methods
            god_objects.append((pattern, avg_children))

print("Potential God Objects:")
for pattern, avg in sorted(god_objects, key=lambda x: x[1], reverse=True):
    print(f"  {pattern.pattern_name}: avg {avg:.0f} methods")
```

### Example 2: Code Smells Detection

```python
from accelerated_pattern_learner import AcceleratedPatternLearner

learner = AcceleratedPatternLearner()
learner.extract_features_from_directory('src')
patterns = learner.discover_patterns(n_clusters=15)

print("Code Smell Analysis:")
print("="*60)

# Long functions
long_funcs = [p for p in patterns if 'Large' in p.pattern_name]
if long_funcs:
    print(f"\n⚠️  Long Functions: {sum(p.occurrences for p in long_funcs)} cases")

# High complexity
complex_funcs = [p for p in patterns if 'Complex' in p.pattern_name]
if complex_funcs:
    print(f"⚠️  High Complexity: {sum(p.occurrences for p in complex_funcs)} cases")

# Poor documentation
undoc = [p for p in patterns if 'Not documented' in p.description]
if undoc:
    print(f"⚠️  Poor Documentation: {sum(p.occurrences for p in undoc)} cases")

# Anomalies
anomalies = [p for p in patterns if p.pattern_type == 'anomaly']
if anomalies:
    print(f"⚠️  Anomalous Code: {sum(p.occurrences for p in anomalies)} cases")
```

### Example 3: Team Code Style Analysis

```python
from accelerated_pattern_learner import AcceleratedPatternLearner

learner = AcceleratedPatternLearner()
learner.extract_features_from_directory('src')
patterns = learner.discover_patterns()

# Analyze naming conventions
snake_case = sum(1 for f in learner.features if f.is_snake_case)
camel_case = sum(1 for f in learner.features if f.is_camel_case)

# Analyze documentation
with_docstrings = sum(1 for f in learner.features if f.has_docstring)
total_funcs = sum(1 for f in learner.features if f.node_type == 'FunctionDef')

# Analyze type hints
with_hints = sum(1 for f in learner.features if f.has_type_hints)

print("Code Style Report:")
print("="*60)
print(f"Naming Conventions:")
print(f"  Snake case: {snake_case} ({snake_case/(snake_case+camel_case)*100:.1f}%)")
print(f"  Camel case: {camel_case} ({camel_case/(snake_case+camel_case)*100:.1f}%)")
print(f"\nDocumentation:")
print(f"  With docstrings: {with_docstrings}/{total_funcs} ({with_docstrings/total_funcs*100:.1f}%)")
print(f"\nType Hints:")
print(f"  With hints: {with_hints}/{total_funcs} ({with_hints/total_funcs*100:.1f}%)")
```

---

## 🧪 Testing Your Integration

```python
# Test 1: Basic functionality
from accelerated_pattern_learner import AcceleratedPatternLearner

learner = AcceleratedPatternLearner()
features = learner.extract_features_from_directory('.')
assert features > 0, "Should extract features"

patterns = learner.discover_patterns()
assert len(patterns) > 0, "Should discover patterns"

print("✅ Basic test passed")

# Test 2: Performance
import time

start = time.perf_counter()
learner.extract_features_from_directory('src')
learner.discover_patterns()
elapsed = time.perf_counter() - start

print(f"✅ Performance test: {elapsed:.2f}s")

# Test 3: Cache effectiveness
learner2 = AcceleratedPatternLearner()
learner2.extract_features_from_directory('src')
learner2.discover_patterns()

stats = learner2.get_performance_stats()
assert stats['cached_files'] > 0, "Should have cached files"
print(f"✅ Cache test passed: {stats['cache_hit_rate']} hit rate")
```

---

## 📖 Pattern Types Reference

### Cluster Patterns
- **Well-Documented**: Code with good documentation
- **High-Complexity**: Complex functions/classes
- **Simple**: Straightforward code
- **Large**: Long functions/classes
- **Small**: Concise functions/classes

### Anomaly Patterns
- **Anomalous Code Pattern**: Code that significantly differs from the norm
- Potential issues or unique implementations

### Categories
- `standard`: Normal patterns
- `well-documented`: High doc quality
- `high-complexity`: Complex code
- `anomaly`: Outliers

---

## 🐛 Troubleshooting

### Issue: No patterns discovered
```python
# Check if features were extracted
print(f"Features: {len(learner.features)}")

# Try different cluster count
patterns = learner.discover_patterns(n_clusters=5)  # Fewer clusters

# Lower min_samples
patterns = learner.discover_patterns(min_samples=2)
```

### Issue: Too many patterns
```python
# Increase min_samples
patterns = learner.discover_patterns(min_samples=10)

# Reduce clusters
patterns = learner.discover_patterns(n_clusters=5)
```

### Issue: Slow performance
```python
# Analyze smaller subdirectory
learner.extract_features_from_directory('src/core')  # Not entire repo

# Check cache stats
stats = learner.get_performance_stats()
print(stats)

# Clear cache if memory is issue
learner.clear_caches()
```

### Issue: Syntax errors
```python
# The learner skips files with syntax errors
# Check stderr for messages

# To see which files failed:
import sys
import io

old_stderr = sys.stderr
sys.stderr = io.StringIO()

learner.extract_features_from_directory('src')

errors = sys.stderr.getvalue()
sys.stderr = old_stderr

if errors:
    print("Files with errors:")
    print(errors)
```

---

## 💡 Best Practices

### 1. Start Broad, Then Narrow
```python
# First: Get overview
patterns = learner.discover_patterns(n_clusters=5, min_samples=5)

# Then: Drill down
patterns = learner.discover_patterns(n_clusters=15, min_samples=3)
```

### 2. Save and Version Results
```python
# Save patterns with timestamp
import datetime
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

learner.output_dir = f"analysis/patterns_{timestamp}"
learner.save_patterns()
```

### 3. Combine with Git History
```python
import subprocess

# Get recently changed files
result = subprocess.run(
    ['git', 'diff', '--name-only', 'HEAD~10'],
    capture_output=True, text=True
)
changed_files = result.stdout.strip().split('\n')

# Analyze only changed files
for file in changed_files:
    if file.endswith('.py'):
        features = learner.extract_features_from_file(file)
        learner.features.extend(features)

patterns = learner.discover_patterns()
```

### 4. Integrate with CI/CD
```yaml
# .github/workflows/code-analysis.yml
- name: Pattern Analysis
  run: |
    python3 tools/accelerated_pattern_learner.py \
      -d src \
      -o pattern_report.md \
      --save-patterns
    
- name: Upload Report
  uses: actions/upload-artifact@v2
  with:
    name: pattern-analysis
    path: pattern_report.md
```

---

## 📚 Further Reading

- [Acceleration Complete Documentation](ACCELERATION_COMPLETE.md)
- [Unsupervised Pattern Learner Tests](tools/test_unsupervised_pattern_learner.py)
- [Performance Benchmarks](tools/benchmark_unsupervised_learner.py)
- [Profiling Tool](tools/profile_learner.py)

---

**Built with elegance and speed by @accelerate-specialist** 🚀

"Elegance is not optional. Neither is speed." - Edsger Dijkstra

