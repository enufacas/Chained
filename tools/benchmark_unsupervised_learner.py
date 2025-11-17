#!/usr/bin/env python3
"""
Benchmark Script for Unsupervised Pattern Learner
By @accelerate-specialist (Edsger Dijkstra)

Measures performance across different optimization stages.
"""

import time
import json
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from unsupervised_pattern_learner import UnsupervisedPatternLearner


def benchmark_feature_extraction(learner, directory, label="baseline"):
    """Benchmark feature extraction phase"""
    start = time.perf_counter()
    feature_count = learner.extract_features_from_directory(directory)
    elapsed = time.perf_counter() - start
    
    return {
        'phase': 'feature_extraction',
        'label': label,
        'features': feature_count,
        'time_seconds': elapsed,
        'features_per_second': feature_count / elapsed if elapsed > 0 else 0
    }


def benchmark_pattern_discovery(learner, n_clusters, label="baseline"):
    """Benchmark pattern discovery phase"""
    start = time.perf_counter()
    patterns = learner.discover_patterns(n_clusters=n_clusters, min_samples=3)
    elapsed = time.perf_counter() - start
    
    return {
        'phase': 'pattern_discovery',
        'label': label,
        'patterns': len(patterns),
        'clusters': n_clusters,
        'time_seconds': elapsed,
        'patterns_per_second': len(patterns) / elapsed if elapsed > 0 else 0
    }


def benchmark_report_generation(learner, label="baseline"):
    """Benchmark report generation phase"""
    start = time.perf_counter()
    report = learner.generate_report('markdown')
    elapsed = time.perf_counter() - start
    
    return {
        'phase': 'report_generation',
        'label': label,
        'report_size': len(report),
        'time_seconds': elapsed
    }


def run_full_benchmark(directory='tools', n_clusters=10, label="baseline"):
    """Run complete benchmark of all phases"""
    print(f"\n{'='*60}")
    print(f"Benchmark: {label}")
    print(f"{'='*60}")
    
    learner = UnsupervisedPatternLearner()
    
    # Phase 1: Feature Extraction
    print("\n📊 Phase 1: Feature Extraction...")
    result1 = benchmark_feature_extraction(learner, directory, label)
    print(f"  ⏱️  Time: {result1['time_seconds']:.3f}s")
    print(f"  📈 Features: {result1['features']}")
    print(f"  ⚡ Rate: {result1['features_per_second']:.1f} features/sec")
    
    # Phase 2: Pattern Discovery
    print("\n🔍 Phase 2: Pattern Discovery...")
    result2 = benchmark_pattern_discovery(learner, n_clusters, label)
    print(f"  ⏱️  Time: {result2['time_seconds']:.3f}s")
    print(f"  📈 Patterns: {result2['patterns']}")
    print(f"  ⚡ Rate: {result2['patterns_per_second']:.1f} patterns/sec")
    
    # Phase 3: Report Generation
    print("\n📝 Phase 3: Report Generation...")
    result3 = benchmark_report_generation(learner, label)
    print(f"  ⏱️  Time: {result3['time_seconds']:.3f}s")
    print(f"  📄 Size: {result3['report_size']} chars")
    
    # Total
    total_time = result1['time_seconds'] + result2['time_seconds'] + result3['time_seconds']
    print(f"\n{'='*60}")
    print(f"⏱️  Total Time: {total_time:.3f}s")
    print(f"{'='*60}\n")
    
    return {
        'label': label,
        'directory': directory,
        'n_clusters': n_clusters,
        'total_time': total_time,
        'phases': [result1, result2, result3]
    }


def compare_benchmarks(results):
    """Compare multiple benchmark results"""
    if len(results) < 2:
        print("Need at least 2 benchmark results to compare")
        return
    
    baseline = results[0]
    
    print("\n" + "="*60)
    print("📊 Performance Comparison")
    print("="*60)
    
    for i, result in enumerate(results[1:], 1):
        speedup = baseline['total_time'] / result['total_time']
        improvement = (baseline['total_time'] - result['total_time']) / baseline['total_time'] * 100
        
        print(f"\n{result['label']} vs {baseline['label']}:")
        print(f"  ⚡ Speedup: {speedup:.2f}x")
        print(f"  📈 Improvement: {improvement:+.1f}%")
        print(f"  ⏱️  Time: {baseline['total_time']:.3f}s → {result['total_time']:.3f}s")
        
        # Phase-by-phase comparison
        print("\n  Phase Breakdown:")
        for phase_baseline, phase_optimized in zip(baseline['phases'], result['phases']):
            phase_speedup = phase_baseline['time_seconds'] / phase_optimized['time_seconds']
            print(f"    {phase_baseline['phase']}: {phase_speedup:.2f}x")


def save_benchmark_results(results, filename='analysis/benchmark_results.json'):
    """Save benchmark results for later analysis"""
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")


def main():
    """Run benchmarks"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark unsupervised pattern learner')
    parser.add_argument('-d', '--directory', default='tools', help='Directory to analyze')
    parser.add_argument('-k', '--clusters', type=int, default=10, help='Number of clusters')
    parser.add_argument('-l', '--label', default='baseline', help='Benchmark label')
    parser.add_argument('--compare', action='store_true', help='Compare with previous results')
    
    args = parser.parse_args()
    
    # Run benchmark
    result = run_full_benchmark(args.directory, args.clusters, args.label)
    
    # Save results
    save_benchmark_results([result])
    
    print("\n✅ Benchmark complete!")
    print("\n💡 Dijkstra says: 'Elegance is not optional' - @accelerate-specialist")


if __name__ == '__main__':
    main()
