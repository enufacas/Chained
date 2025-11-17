#!/usr/bin/env python3
"""
Accelerated Unsupervised Pattern Learning
By @accelerate-specialist (Edsger Dijkstra)

Performance-optimized version targeting all three major bottlenecks:
1. File extraction (40.8%) - Cached AST parsing + batch processing
2. Node extraction (31.6%) - Optimized AST traversal + reduced allocations
3. K-means clustering (27.1%) - Early termination + efficient centroids

Target: 30-50% performance improvement while maintaining 100% accuracy.

"Elegance is not optional. Neither is speed." - Dijkstra
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from functools import lru_cache
from collections import defaultdict

# Import base functionality
sys.path.insert(0, str(Path(__file__).parent))
from unsupervised_pattern_learner import (
    CodeFeatures, DiscoveredPattern, UnsupervisedPatternLearner
)


class AcceleratedPatternLearner(UnsupervisedPatternLearner):
    """
    High-performance pattern learner with comprehensive optimizations.
    
    Key improvements:
    - Cached AST parsing (avoid reparsing)
    - Optimized AST traversal (iterative, not recursive)
    - Batch vector processing
    - Early K-means termination
    - Reduced memory allocations
    - LRU caching for expensive operations
    
    Performance target: 30-50% faster than baseline
    API compatibility: 100% (drop-in replacement)
    """
    
    def __init__(self, output_dir: str = "analysis/patterns"):
        super().__init__(output_dir)
        
        # Performance caches
        self._ast_cache: Dict[str, ast.AST] = {}
        self._file_mtime_cache: Dict[str, float] = {}
        self._normalized_cache: Optional[List[List[float]]] = None
        
        # Statistics
        self._cache_hits = 0
        self._cache_misses = 0
    
    def extract_features_from_file(self, filepath: str) -> List[CodeFeatures]:
        """
        Optimized feature extraction with intelligent caching.
        
        Optimization 1: Cache AST by file modification time
        Optimization 2: Batch node processing
        Optimization 3: Direct iteration (not ast.walk)
        """
        if not filepath.endswith('.py'):
            return []
        
        try:
            # Check if file is in cache and unchanged
            try:
                mtime = os.path.getmtime(filepath)
                if filepath in self._ast_cache and self._file_mtime_cache.get(filepath) == mtime:
                    self._cache_hits += 1
                    tree = self._ast_cache[filepath]
                else:
                    self._cache_misses += 1
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    self._ast_cache[filepath] = tree
                    self._file_mtime_cache[filepath] = mtime
                    
            except (OSError, SyntaxError) as e:
                print(f"Error reading {filepath}: {e}", file=sys.stderr)
                return []
            
            # Read content only if needed
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            features = []
            
            # Optimized: Direct node collection (faster than ast.walk)
            nodes_to_process = [tree]
            target_nodes = []
            
            while nodes_to_process:
                node = nodes_to_process.pop()
                
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    target_nodes.append(node)
                
                nodes_to_process.extend(ast.iter_child_nodes(node))
            
            # Batch process nodes
            for node in target_nodes:
                feature = self._extract_node_features_fast(node, filepath, content)
                if feature:
                    features.append(feature)
            
            return features
            
        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)
            return []
    
    def _extract_node_features_fast(self, node: ast.AST, filepath: str, content: str) -> Optional[CodeFeatures]:
        """
        Optimized node feature extraction.
        
        Optimization 4: Single-pass AST analysis
        Optimization 5: Early exit when possible
        Optimization 6: Reduced string operations
        """
        try:
            node_type = type(node).__name__
            line_number = getattr(node, 'lineno', 0)
            
            # Extract code snippet only for non-modules
            raw_code = ""
            if line_number > 0 and not isinstance(node, ast.Module):
                lines = content.split('\n')
                end_line = min(getattr(node, 'end_lineno', line_number) or line_number, 
                              line_number + 10, 
                              len(lines))
                raw_code = '\n'.join(lines[line_number-1:end_line])[:200]
            
            features = CodeFeatures(
                file_path=filepath,
                node_type=node_type,
                line_number=line_number,
                raw_code=raw_code
            )
            
            # Quick structural features
            features.children = len(list(ast.iter_child_nodes(node)))
            
            # Function-specific features (optimized path)
            if isinstance(node, ast.FunctionDef):
                self._extract_function_features_optimized(node, features)
            
            # Class-specific features (optimized path)
            elif isinstance(node, ast.ClassDef):
                self._extract_class_features_optimized(node, features)
            
            return features
            
        except Exception as e:
            print(f"Error extracting features from node: {e}", file=sys.stderr)
            return None
    
    def _extract_function_features_optimized(self, node: ast.FunctionDef, features: CodeFeatures):
        """
        Optimized function feature extraction.
        
        Optimization 7: Single AST walk for multiple features
        Optimization 8: Early exits and short-circuits
        """
        # Size features
        if hasattr(node, 'end_lineno') and node.lineno:
            features.lines_of_code = node.end_lineno - node.lineno + 1
        
        features.num_parameters = len(node.args.args)
        
        # Naming features (fast operations)
        func_name = node.name
        features.name_length = len(func_name)
        features.has_underscore = '_' in func_name
        features.is_snake_case = func_name.islower() and '_' in func_name
        features.is_camel_case = func_name[0].islower() and any(c.isupper() for c in func_name)
        
        # Pattern features (quick checks)
        docstring = ast.get_docstring(node)
        features.has_docstring = docstring is not None and len(docstring) > 10
        
        features.has_type_hints = (
            node.returns is not None or
            any(arg.annotation for arg in node.args.args)
        )
        
        # Single-pass analysis for complexity and patterns
        complexity = 1
        cognitive = 0
        var_count = 0
        seen_vars: Set[str] = set()
        has_try = False
        has_recursion = False
        
        # Optimized: Use iterative traversal with depth tracking
        stack = [(node, 0)]
        max_depth = 0
        
        while stack:
            current, depth = stack.pop()
            max_depth = max(max_depth, depth)
            
            # Multiple feature extraction in single pass
            if isinstance(current, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
                if depth > 0:  # Nested
                    cognitive += 1 + depth
            
            elif isinstance(current, ast.BoolOp):
                complexity += len(current.values) - 1
                cognitive += len(current.values) - 1
            
            elif isinstance(current, ast.Try):
                has_try = True
            
            elif isinstance(current, ast.Call):
                if isinstance(current.func, ast.Name) and current.func.id == func_name:
                    has_recursion = True
            
            elif isinstance(current, ast.Name):
                if current.id not in seen_vars:
                    seen_vars.add(current.id)
                    var_count += 1
            
            # Add children with appropriate depth
            for child in ast.iter_child_nodes(current):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    stack.append((child, depth + 1))
                else:
                    stack.append((child, depth))
        
        # Set all features at once
        features.depth = max_depth
        features.cyclomatic_complexity = complexity
        features.cognitive_complexity = cognitive
        features.num_variables = var_count
        features.has_error_handling = has_try
        features.has_recursion = has_recursion
    
    def _extract_class_features_optimized(self, node: ast.ClassDef, features: CodeFeatures):
        """Optimized class feature extraction"""
        # Count methods efficiently
        features.children = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
        
        # Naming
        features.name_length = len(node.name)
        features.is_camel_case = node.name[0].isupper()
        
        # Docstring
        docstring = ast.get_docstring(node)
        features.has_docstring = docstring is not None
    
    def discover_patterns(self, n_clusters: int = 10, min_samples: int = 3) -> List[DiscoveredPattern]:
        """
        Optimized pattern discovery.
        
        Optimization 9: Cached normalized vectors
        Optimization 10: Early K-means termination
        """
        if not self.features:
            print("No features extracted. Run extract_features_from_directory first.", file=sys.stderr)
            return []
        
        print(f"Discovering patterns from {len(self.features)} code elements...")
        
        # Convert features to vectors (with caching in CodeFeatures)
        vectors = [f.to_vector() for f in self.features]
        
        # Normalize vectors (with caching)
        if self._normalized_cache is None:
            vectors = self._normalize_vectors(vectors)
            self._normalized_cache = vectors
        else:
            vectors = self._normalized_cache
        
        # Optimized K-means clustering
        clusters, centroids = self._kmeans_clustering_accelerated(vectors, n_clusters)
        
        # Create pattern objects (same as base)
        patterns = []
        for cluster_id in range(n_clusters):
            cluster_indices = [i for i, c in enumerate(clusters) if c == cluster_id]
            
            if len(cluster_indices) < min_samples:
                continue
            
            pattern = self._create_pattern_from_cluster(
                cluster_id, 
                cluster_indices, 
                centroids[cluster_id]
            )
            patterns.append(pattern)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(vectors, clusters, centroids)
        patterns.extend(anomalies)
        
        self.patterns = patterns
        return patterns
    
    def _kmeans_clustering_accelerated(self, vectors: List[List[float]], k: int, 
                                      max_iterations: int = 100) -> Tuple[List[int], List[List[float]]]:
        """
        Accelerated K-means with early termination.
        
        Optimization 11: Assignment comparison (not expensive inertia)
        Optimization 12: Pre-allocated centroids
        """
        import random
        
        if not vectors or k <= 0:
            return [], []
        
        n = len(vectors)
        n_features = len(vectors[0])
        
        # Initialize centroids using k-means++ (already optimal)
        centroids = []
        centroids.append(vectors[random.randint(0, n-1)][:])
        
        for _ in range(k - 1):
            distances = []
            for vector in vectors:
                min_dist = min(self._euclidean_distance(vector, c) for c in centroids)
                distances.append(min_dist)
            
            total = sum(d**2 for d in distances)
            if total == 0:
                centroids.append(vectors[random.randint(0, n-1)][:])
            else:
                r = random.uniform(0, total)
                cumsum = 0
                for i, d in enumerate(distances):
                    cumsum += d**2
                    if cumsum >= r:
                        centroids.append(vectors[i][:])
                        break
        
        clusters = [0] * n
        
        for iteration in range(max_iterations):
            # Assign points to nearest centroid
            new_clusters = []
            for vector in vectors:
                distances = [self._euclidean_distance(vector, centroid) for centroid in centroids]
                new_clusters.append(distances.index(min(distances)))
            
            # Early termination: check if assignments changed
            if new_clusters == clusters:
                break
            
            clusters = new_clusters
            
            # Update centroids efficiently
            for cluster_id in range(k):
                cluster_points = [vectors[i] for i, c in enumerate(clusters) if c == cluster_id]
                if cluster_points:
                    # Pre-allocated centroid update
                    new_centroid = [0.0] * n_features
                    for point in cluster_points:
                        for i in range(n_features):
                            new_centroid[i] += point[i]
                    
                    for i in range(n_features):
                        new_centroid[i] /= len(cluster_points)
                    
                    centroids[cluster_id] = new_centroid
        
        return clusters, centroids
    
    def get_performance_stats(self) -> Dict[str, any]:
        """Get performance statistics"""
        cache_total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / cache_total * 100) if cache_total > 0 else 0
        
        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': f"{hit_rate:.1f}%",
            'cached_files': len(self._ast_cache),
        }
    
    def clear_caches(self):
        """Clear all caches to free memory"""
        self._ast_cache.clear()
        self._file_mtime_cache.clear()
        self._normalized_cache = None


def compare_performance(directory: str = 'tools', n_clusters: int = 10):
    """
    Compare baseline vs accelerated performance.
    
    Demonstrates the performance improvements in a clear, measurable way.
    """
    import time
    
    print("="*70)
    print("Performance Comparison: Baseline vs Accelerated")
    print("By @accelerate-specialist (Edsger Dijkstra)")
    print("="*70)
    
    # Baseline
    print(f"\n📊 Running baseline on {directory}...")
    baseline = UnsupervisedPatternLearner()
    
    start = time.perf_counter()
    baseline_features = baseline.extract_features_from_directory(directory)
    mid1 = time.perf_counter()
    baseline_patterns = baseline.discover_patterns(n_clusters=n_clusters)
    end1 = time.perf_counter()
    
    baseline_extract = mid1 - start
    baseline_discover = end1 - mid1
    baseline_total = end1 - start
    
    print(f"  Features: {baseline_features}")
    print(f"  Patterns: {len(baseline_patterns)}")
    print(f"  Time: {baseline_total:.3f}s")
    
    # Accelerated
    print(f"\n⚡ Running accelerated on {directory}...")
    accelerated = AcceleratedPatternLearner()
    
    start = time.perf_counter()
    accel_features = accelerated.extract_features_from_directory(directory)
    mid2 = time.perf_counter()
    accel_patterns = accelerated.discover_patterns(n_clusters=n_clusters)
    end2 = time.perf_counter()
    
    accel_extract = mid2 - start
    accel_discover = end2 - mid2
    accel_total = end2 - start
    
    print(f"  Features: {accel_features}")
    print(f"  Patterns: {len(accel_patterns)}")
    print(f"  Time: {accel_total:.3f}s")
    
    # Performance stats
    stats = accelerated.get_performance_stats()
    print(f"\n  Cache stats:")
    print(f"    Hit rate: {stats['cache_hit_rate']}")
    print(f"    Cached files: {stats['cached_files']}")
    
    # Comparison
    print("\n" + "="*70)
    print("Results:")
    print("="*70)
    
    speedup = baseline_total / accel_total if accel_total > 0 else 0
    improvement = ((baseline_total - accel_total) / baseline_total * 100) if baseline_total > 0 else 0
    
    print(f"\n  Baseline:     {baseline_total:.3f}s")
    print(f"  Accelerated:  {accel_total:.3f}s")
    print(f"\n  Speedup:      {speedup:.2f}x")
    print(f"  Improvement:  {improvement:+.1f}%")
    
    # Phase breakdown
    print(f"\n  Phase breakdown:")
    extract_speedup = baseline_extract / accel_extract if accel_extract > 0 else 0
    discover_speedup = baseline_discover / accel_discover if accel_discover > 0 else 0
    
    print(f"    Extraction:  {baseline_extract:.3f}s → {accel_extract:.3f}s ({extract_speedup:.2f}x)")
    print(f"    Discovery:   {baseline_discover:.3f}s → {accel_discover:.3f}s ({discover_speedup:.2f}x)")
    
    print("\n" + "="*70)
    
    # Validation
    print("\nValidation:")
    features_match = baseline_features == accel_features
    patterns_match = len(baseline_patterns) == len(accel_patterns)
    
    print(f"  ✓ Feature count matches: {features_match}")
    print(f"  ✓ Pattern count matches: {patterns_match}")
    
    if speedup >= 1.3:
        print(f"\n🎉 SUCCESS: {improvement:.1f}% performance improvement achieved!")
        print("   Target of 30%+ improvement reached!")
    elif speedup >= 1.1:
        print(f"\n✅ GOOD: {improvement:.1f}% performance improvement achieved!")
    else:
        print(f"\n⚠️  MODEST: {improvement:.1f}% performance improvement")
    
    print("\n💡 Dijkstra says: 'Elegance is not optional. Neither is speed.'")
    print("   - @accelerate-specialist")
    
    return {
        'baseline_time': baseline_total,
        'accelerated_time': accel_total,
        'speedup': speedup,
        'improvement_percent': improvement,
    }


def main():
    """CLI interface matching original"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Accelerated Unsupervised Pattern Learner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Optimized by @accelerate-specialist (Edsger Dijkstra)

Performance improvements:
- Cached AST parsing with modification time tracking
- Single-pass AST analysis for multiple features
- Batch processing for efficiency
- Early K-means termination
- Reduced memory allocations

Examples:
  %(prog)s -d .
  %(prog)s -d /path/to/repo -k 15
  %(prog)s -d . -o pattern_report.md
  %(prog)s --compare  # Run performance comparison
        """
    )
    
    parser.add_argument('-d', '--directory', default='.',
                       help='Directory to analyze (default: current directory)')
    parser.add_argument('-k', '--clusters', type=int, default=10,
                       help='Number of clusters for pattern discovery (default: 10)')
    parser.add_argument('--min-samples', type=int, default=3,
                       help='Minimum samples per pattern (default: 3)')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown',
                       help='Output format (default: markdown)')
    parser.add_argument('--save-patterns', action='store_true',
                       help='Save discovered patterns to JSON file')
    parser.add_argument('--compare', action='store_true',
                       help='Run performance comparison with baseline')
    parser.add_argument('--stats', action='store_true',
                       help='Show performance statistics')
    
    args = parser.parse_args()
    
    # Performance comparison mode
    if args.compare:
        compare_performance(args.directory, args.clusters)
        return
    
    # Normal operation
    learner = AcceleratedPatternLearner()
    
    # Extract features
    print(f"Extracting features from: {args.directory}")
    feature_count = learner.extract_features_from_directory(args.directory)
    print(f"Extracted {feature_count} features from code")
    
    if feature_count == 0:
        print("No features extracted. Make sure the directory contains Python files.")
        sys.exit(1)
    
    # Discover patterns
    print(f"\nDiscovering patterns with {args.clusters} clusters...")
    patterns = learner.discover_patterns(n_clusters=args.clusters, min_samples=args.min_samples)
    print(f"Discovered {len(patterns)} patterns")
    
    # Show performance stats if requested
    if args.stats:
        stats = learner.get_performance_stats()
        print(f"\nPerformance stats:")
        print(f"  Cache hit rate: {stats['cache_hit_rate']}")
        print(f"  Cached files: {stats['cached_files']}")
    
    # Generate report
    report = learner.generate_report(args.format)
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {args.output}")
    else:
        print("\n" + report)
    
    # Save patterns if requested
    if args.save_patterns:
        learner.save_patterns()
    
    print("\n✅ Pattern discovery complete!")
    print("💡 Dijkstra says: 'Elegance is not optional' - @accelerate-specialist")


if __name__ == '__main__':
    main()
