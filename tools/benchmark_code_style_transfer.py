#!/usr/bin/env python3
"""
Performance Benchmarking Tool for Code Style Transfer
Part of the Chained autonomous AI ecosystem

This tool benchmarks the neural network code style transfer system
to identify performance bottlenecks and measure optimization improvements.

Author: @accelerate-specialist (Edsger Dijkstra profile)
"""

import sys
import time
import statistics
from pathlib import Path
from typing import Dict, List, Callable
import tempfile
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import by executing the module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "code_style_transfer",
    Path(__file__).parent / "code-style-transfer.py"
)
code_style_transfer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_style_transfer)

CodeStyleTransferSystem = code_style_transfer.CodeStyleTransferSystem
StyleExtractor = code_style_transfer.StyleExtractor
NeuralStyleEncoder = code_style_transfer.NeuralStyleEncoder
StyleTransformer = code_style_transfer.StyleTransformer
StyleFeatures = code_style_transfer.StyleFeatures


class PerformanceBenchmark:
    """Benchmark suite for code style transfer performance."""
    
    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.test_code_small = '''
def hello():
    print("Hello, World!")
'''
        
        self.test_code_medium = '''
def calculate_fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class MathUtils:
    """Utility class for mathematical operations."""
    
    def __init__(self):
        self.cache = {}
    
    def factorial(self, n: int) -> int:
        """Calculate factorial of n."""
        if n in self.cache:
            return self.cache[n]
        if n <= 1:
            result = 1
        else:
            result = n * self.factorial(n - 1)
        self.cache[n] = result
        return result
'''
        
        self.test_code_large = self.test_code_medium * 20
    
    def benchmark(self, name: str, func: Callable, iterations: int = 100):
        """Run a benchmark and record results.
        
        Args:
            name: Benchmark name
            func: Function to benchmark
            iterations: Number of iterations
            
        Returns:
            Dictionary with timing statistics
        """
        times = []
        
        # Warmup
        for _ in range(min(5, iterations)):
            func()
        
        # Actual benchmark
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)
        
        # Calculate statistics
        result = {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0.0,
            'min': min(times),
            'max': max(times),
            'total': sum(times),
            'iterations': iterations
        }
        
        self.results[name] = result
        return result
    
    def benchmark_style_extraction(self):
        """Benchmark style extraction performance."""
        print("\n📊 Benchmarking Style Extraction...")
        extractor = StyleExtractor()
        
        # Small code
        self.benchmark(
            "extract_small",
            lambda: extractor.extract_from_code(self.test_code_small),
            iterations=1000
        )
        
        # Medium code
        self.benchmark(
            "extract_medium",
            lambda: extractor.extract_from_code(self.test_code_medium),
            iterations=500
        )
        
        # Large code
        self.benchmark(
            "extract_large",
            lambda: extractor.extract_from_code(self.test_code_large),
            iterations=100
        )
        
        print("  ✓ Style extraction benchmarked")
    
    def benchmark_neural_encoding(self):
        """Benchmark neural encoding performance."""
        print("\n🧠 Benchmarking Neural Encoding...")
        extractor = StyleExtractor()
        encoder = NeuralStyleEncoder()
        
        features = extractor.extract_from_code(self.test_code_medium)
        
        self.benchmark(
            "encode_style",
            lambda: encoder.encode_style(features),
            iterations=1000
        )
        
        # Test similarity computation
        enc1 = encoder.encode_style(features)
        enc2 = encoder.encode_style(features)
        
        self.benchmark(
            "similarity",
            lambda: encoder.similarity(enc1, enc2),
            iterations=1000
        )
        
        print("  ✓ Neural encoding benchmarked")
    
    def benchmark_style_transfer(self):
        """Benchmark style transfer performance."""
        print("\n🔄 Benchmarking Style Transfer...")
        transformer = StyleTransformer()
        extractor = StyleExtractor()
        
        target_style = extractor.extract_from_code(self.test_code_medium)
        
        # Transfer on small code
        self.benchmark(
            "transfer_small",
            lambda: transformer.transfer_style(self.test_code_small, target_style),
            iterations=500
        )
        
        # Transfer on medium code
        self.benchmark(
            "transfer_medium",
            lambda: transformer.transfer_style(self.test_code_medium, target_style),
            iterations=200
        )
        
        print("  ✓ Style transfer benchmarked")
    
    def benchmark_project_learning(self):
        """Benchmark project-wide style learning."""
        print("\n📚 Benchmarking Project Learning...")
        
        # Create temporary test project
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create test files
            for i in range(10):
                file_path = project_path / f"test_{i}.py"
                with open(file_path, 'w') as f:
                    f.write(self.test_code_medium)
            
            system = CodeStyleTransferSystem()
            
            self.benchmark(
                "learn_project_10_files",
                lambda: system.learn_project_style(str(project_path), "test_project"),
                iterations=10
            )
        
        print("  ✓ Project learning benchmarked")
    
    def benchmark_end_to_end(self):
        """Benchmark complete end-to-end workflow."""
        print("\n🎯 Benchmarking End-to-End Workflow...")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create source project
            for i in range(5):
                file_path = project_path / f"source_{i}.py"
                with open(file_path, 'w') as f:
                    f.write(self.test_code_medium)
            
            def end_to_end():
                system = CodeStyleTransferSystem()
                system.learn_project_style(str(project_path), "test")
                system.apply_project_style(self.test_code_small, "test")
            
            self.benchmark(
                "end_to_end_workflow",
                end_to_end,
                iterations=5
            )
        
        print("  ✓ End-to-end workflow benchmarked")
    
    def print_results(self):
        """Print benchmark results in a formatted table."""
        print("\n" + "="*80)
        print(" PERFORMANCE BENCHMARK RESULTS")
        print("="*80)
        
        print(f"\n{'Benchmark':<30} {'Mean':>12} {'Median':>12} {'Min':>12} {'Max':>12}")
        print("-" * 80)
        
        for name, stats in sorted(self.results.items()):
            mean_ms = stats['mean'] * 1000
            median_ms = stats['median'] * 1000
            min_ms = stats['min'] * 1000
            max_ms = stats['max'] * 1000
            
            print(f"{name:<30} {mean_ms:>11.2f}ms {median_ms:>11.2f}ms {min_ms:>11.2f}ms {max_ms:>11.2f}ms")
        
        print("\n" + "="*80)
        
        # Calculate total time and throughput
        total_time = sum(s['total'] for s in self.results.values())
        total_iterations = sum(s['iterations'] for s in self.results.values())
        
        print(f"\nTotal benchmark time: {total_time:.2f}s")
        print(f"Total operations: {total_iterations}")
        print(f"Average throughput: {total_iterations/total_time:.1f} ops/sec")
    
    def identify_bottlenecks(self):
        """Identify performance bottlenecks."""
        print("\n🔍 BOTTLENECK ANALYSIS")
        print("="*80)
        
        # Sort by mean time
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]['mean'],
            reverse=True
        )
        
        print("\nSlowest operations (by mean time):")
        for i, (name, stats) in enumerate(sorted_results[:5], 1):
            mean_ms = stats['mean'] * 1000
            print(f"{i}. {name}: {mean_ms:.2f}ms")
        
        # Calculate relative costs
        if len(self.results) > 1:
            fastest = min(s['mean'] for s in self.results.values())
            
            print("\nRelative performance (vs fastest operation):")
            for name, stats in sorted_results[:5]:
                ratio = stats['mean'] / fastest
                print(f"  {name}: {ratio:.1f}x slower")
        
        print("\n💡 OPTIMIZATION OPPORTUNITIES:")
        print("  1. Style extraction on large files could benefit from caching")
        print("  2. Neural encoding could be vectorized for batch operations")
        print("  3. Project learning could use parallel processing")
        print("  4. Repeated operations should leverage memoization")
    
    def run_all(self):
        """Run all benchmarks."""
        print("🚀 Starting Performance Benchmarks")
        print("="*80)
        print("Author: @accelerate-specialist")
        print("Profile: Edsger Dijkstra - elegant and efficient")
        print("="*80)
        
        try:
            self.benchmark_style_extraction()
            self.benchmark_neural_encoding()
            self.benchmark_style_transfer()
            self.benchmark_project_learning()
            self.benchmark_end_to_end()
            
            self.print_results()
            self.identify_bottlenecks()
            
            print("\n✅ All benchmarks completed successfully!")
            return 0
            
        except Exception as e:
            print(f"\n❌ Benchmark failed: {e}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Run the benchmark suite."""
    benchmark = PerformanceBenchmark()
    return benchmark.run_all()


if __name__ == "__main__":
    sys.exit(main())
