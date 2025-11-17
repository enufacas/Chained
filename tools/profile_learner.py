#!/usr/bin/env python3
"""
Profiling Tool for Unsupervised Pattern Learner
By @accelerate-specialist (Edsger Dijkstra)

Identifies performance bottlenecks with detailed timing breakdowns.
"""

import time
import sys
from typing import Dict, List
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from unsupervised_pattern_learner import UnsupervisedPatternLearner


class ProfiledLearner(UnsupervisedPatternLearner):
    """Learner with detailed performance profiling"""
    
    def __init__(self, output_dir: str = "analysis/patterns"):
        super().__init__(output_dir)
        self.timings: Dict[str, List[float]] = {}
    
    def _record_time(self, operation: str, duration: float):
        """Record timing for an operation"""
        if operation not in self.timings:
            self.timings[operation] = []
        self.timings[operation].append(duration)
    
    def extract_features_from_file(self, filepath: str):
        """Profile feature extraction"""
        start = time.perf_counter()
        result = super().extract_features_from_file(filepath)
        self._record_time('extract_file', time.perf_counter() - start)
        return result
    
    def _extract_node_features(self, node, filepath, content):
        """Profile node feature extraction"""
        start = time.perf_counter()
        result = super()._extract_node_features(node, filepath, content)
        self._record_time('extract_node', time.perf_counter() - start)
        return result
    
    def _normalize_vectors(self, vectors):
        """Profile normalization"""
        start = time.perf_counter()
        result = super()._normalize_vectors(vectors)
        self._record_time('normalize', time.perf_counter() - start)
        return result
    
    def _kmeans_clustering(self, vectors, k, max_iterations=100):
        """Profile K-means"""
        start = time.perf_counter()
        result = super()._kmeans_clustering(vectors, k, max_iterations)
        self._record_time('kmeans', time.perf_counter() - start)
        return result
    
    def print_profile_report(self):
        """Print detailed profiling report"""
        print("\n" + "="*60)
        print("Performance Profile")
        print("="*60)
        
        total_time = sum(sum(times) for times in self.timings.values())
        
        # Sort by total time
        sorted_ops = sorted(
            self.timings.items(),
            key=lambda x: sum(x[1]),
            reverse=True
        )
        
        for operation, times in sorted_ops:
            total = sum(times)
            count = len(times)
            avg = total / count if count > 0 else 0
            percent = (total / total_time * 100) if total_time > 0 else 0
            
            print(f"\n{operation}:")
            print(f"  Total: {total:.3f}s ({percent:.1f}%)")
            print(f"  Calls: {count}")
            print(f"  Avg:   {avg*1000:.2f}ms per call")
            
            if count > 10:
                # Show percentiles
                sorted_times = sorted(times)
                p50 = sorted_times[len(sorted_times)//2]
                p95 = sorted_times[int(len(sorted_times)*0.95)]
                p99 = sorted_times[int(len(sorted_times)*0.99)]
                print(f"  p50:   {p50*1000:.2f}ms")
                print(f"  p95:   {p95*1000:.2f}ms")
                print(f"  p99:   {p99*1000:.2f}ms")
        
        print("\n" + "="*60)
        print(f"Total measured time: {total_time:.3f}s")
        print("="*60)


def main():
    """Run profiling analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Profile unsupervised pattern learner')
    parser.add_argument('-d', '--directory', default='tools', help='Directory to analyze')
    parser.add_argument('-k', '--clusters', type=int, default=10, help='Number of clusters')
    
    args = parser.parse_args()
    
    print(f"Profiling analysis on: {args.directory}")
    print("This will take a moment...")
    
    learner = ProfiledLearner()
    
    # Run with profiling
    overall_start = time.perf_counter()
    
    feature_count = learner.extract_features_from_directory(args.directory)
    print(f"\nExtracted {feature_count} features")
    
    patterns = learner.discover_patterns(n_clusters=args.clusters)
    print(f"Discovered {patterns} patterns")
    
    overall_time = time.perf_counter() - overall_start
    
    # Print report
    learner.print_profile_report()
    
    print(f"\n📊 Overall time: {overall_time:.3f}s")
    print("\n💡 Use these insights to target optimizations - @accelerate-specialist")


if __name__ == '__main__':
    main()
