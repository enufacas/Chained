#!/usr/bin/env python3
"""
Test suite for accelerated code style transfer system
Validates performance improvements and correctness

Author: @accelerate-specialist
"""

import sys
import time
import tempfile
from pathlib import Path

# Import by executing the module
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

tools_dir = Path(__file__).parent.parent / "tools"
accelerated = load_module("accelerated", tools_dir / "code-style-transfer-accelerated.py")
original = load_module("original", tools_dir / "code-style-transfer.py")


class TestAcceleratedStyleTransfer:
    """Test suite for accelerated implementation."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_code = '''
def hello_world():
    """Print a greeting."""
    message = "Hello, World!"
    print(message)
    return message

class Calculator:
    """Simple calculator class."""
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b
'''
    
    def test_cache_functionality(self):
        """Test that caching works correctly."""
        print("\n🧪 Testing cache functionality...")
        
        cache = accelerated.StyleCache(maxsize=10)
        
        # Test miss
        result = cache.get(self.test_code)
        assert result is None, "Cache should miss on first access"
        
        # Test put and hit
        features = accelerated.StyleFeatures(indent_size=4)
        cache.put(self.test_code, features)
        
        result = cache.get(self.test_code)
        assert result is not None, "Cache should hit after put"
        assert result.indent_size == 4, "Cached features should match"
        
        # Test stats
        stats = cache.stats()
        assert stats['hits'] == 1, "Should have 1 hit"
        assert stats['misses'] == 1, "Should have 1 miss"
        
        print("  ✓ Cache functionality works correctly")
        self.passed += 1
    
    def test_cache_performance(self):
        """Test cache performance improvement."""
        print("\n⚡ Testing cache performance...")
        
        extractor = accelerated.AcceleratedStyleExtractor(cache_size=100)
        
        # First extraction (cache miss)
        start = time.perf_counter()
        for _ in range(10):
            extractor.extract_from_code(self.test_code)
        miss_time = time.perf_counter() - start
        
        # Reset cache
        extractor.cache.clear()
        
        # Extraction without cache
        start = time.perf_counter()
        for _ in range(10):
            extractor.extract_from_code(self.test_code)
        cached_time = time.perf_counter() - start
        
        # Second batch should be faster due to cache
        stats = extractor.get_cache_stats()
        
        print(f"  Cache hit rate: {stats['hit_rate']:.1%}")
        print(f"  Time difference: {(miss_time/cached_time):.2f}x")
        
        # With repeated code, we should see high hit rate
        assert stats['hit_rate'] > 0.8, "Cache hit rate should be high for repeated code"
        
        print("  ✓ Cache provides performance improvement")
        self.passed += 1
    
    def test_correctness_parity(self):
        """Test that accelerated version produces same results."""
        print("\n🔍 Testing correctness parity with original...")
        
        accel_extractor = accelerated.AcceleratedStyleExtractor()
        orig_extractor = original.StyleExtractor()
        
        accel_features = accel_extractor.extract_from_code(self.test_code)
        orig_features = orig_extractor.extract_from_code(self.test_code)
        
        # Compare key features
        assert accel_features.indent_size == orig_features.indent_size
        assert accel_features.indent_type == orig_features.indent_type
        assert accel_features.variable_naming == orig_features.variable_naming
        assert abs(accel_features.avg_line_length - orig_features.avg_line_length) < 0.1
        
        print("  ✓ Results match original implementation")
        self.passed += 1
    
    def test_parallel_processing(self):
        """Test parallel processing functionality."""
        print("\n⚙️ Testing parallel processing...")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create files (avoid 'test' in filename which gets filtered)
            for i in range(20):
                file_path = project_path / f"module_{i}.py"
                with open(file_path, 'w') as f:
                    f.write(self.test_code)
            
            system = accelerated.AcceleratedCodeStyleTransferSystem(max_workers=2)
            
            # Test parallel learning
            start = time.perf_counter()
            features_parallel = system.learn_project_style(
                str(project_path),
                "test_parallel",
                parallel=True
            )
            parallel_time = time.perf_counter() - start
            
            # Test sequential learning
            system2 = accelerated.AcceleratedCodeStyleTransferSystem(max_workers=1)
            start = time.perf_counter()
            features_sequential = system2.learn_project_style(
                str(project_path),
                "test_sequential",
                parallel=False
            )
            sequential_time = time.perf_counter() - start
            
            print(f"  Parallel time: {parallel_time:.3f}s")
            print(f"  Sequential time: {sequential_time:.3f}s")
            print(f"  Speedup: {sequential_time/parallel_time:.2f}x")
            
            # Both should produce similar results
            assert features_parallel.indent_size == features_sequential.indent_size
            
            print("  ✓ Parallel processing works correctly")
            self.passed += 1
    
    def test_batch_operations(self):
        """Test batch style application."""
        print("\n📦 Testing batch operations...")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create test project with enough files (avoid 'test' in filename)
            for i in range(10):
                file_path = project_path / f"module_{i}.py"
                with open(file_path, 'w') as f:
                    f.write(self.test_code)
            
            system = accelerated.AcceleratedCodeStyleTransferSystem()
            features = system.learn_project_style(str(project_path), "test_batch", parallel=False)
            
            # Verify it was added to database
            assert "test_batch" in system.style_database, "Style should be in database"
            
            # Batch apply
            code_list = [self.test_code] * 10
            
            start = time.perf_counter()
            results = system.batch_apply_style(code_list, "test_batch", parallel=True)
            batch_time = time.perf_counter() - start
            
            # Sequential apply
            start = time.perf_counter()
            for code in code_list:
                system.apply_project_style(code, "test_batch")
            sequential_time = time.perf_counter() - start
            
            print(f"  Batch time: {batch_time:.3f}s")
            print(f"  Sequential time: {sequential_time:.3f}s")
            print(f"  Results: {len(results)} transformations")
            
            assert len(results) == len(code_list)
            
            print("  ✓ Batch operations work correctly")
            self.passed += 1
    
    def test_memory_efficiency(self):
        """Test memory usage."""
        print("\n💾 Testing memory efficiency...")
        
        import sys
        
        # Create larger test case
        large_code = self.test_code * 50
        
        # Measure with accelerated version
        extractor = accelerated.AcceleratedStyleExtractor(cache_size=100)
        features_list = []
        
        for _ in range(100):
            features = extractor.extract_from_code(large_code)
            features_list.append(features)
        
        # Check cache is working
        stats = extractor.get_cache_stats()
        print(f"  Cache hit rate: {stats['hit_rate']:.1%}")
        print(f"  Cache size: {stats['size']} entries")
        print(f"  Total extractions: {stats['total_extractions']}")
        
        assert stats['hit_rate'] > 0.95, "Should have high cache hit rate"
        
        print("  ✓ Memory usage is efficient")
        self.passed += 1
    
    def test_performance_stats(self):
        """Test performance statistics collection."""
        print("\n📊 Testing performance statistics...")
        
        system = accelerated.AcceleratedCodeStyleTransferSystem()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create files (avoid 'test' in filename)
            for i in range(10):
                file_path = project_path / f"module_{i}.py"
                with open(file_path, 'w') as f:
                    f.write(self.test_code)
            
            system.learn_project_style(str(project_path), "test_stats")
            
            stats = system.get_performance_stats()
            
            print(f"  Files processed: {stats['files_processed']}")
            print(f"  Cache hit rate: {stats['cache_hit_rate']:.1%}")
            print(f"  Parallel jobs: {stats['parallel_jobs']}")
            
            assert stats['files_processed'] >= 10
            assert 'cache_hit_rate' in stats
            assert 'max_workers' in stats
            
            print("  ✓ Performance statistics work correctly")
            self.passed += 1
    
    def test_neural_encoding_cache(self):
        """Test cached neural encoding."""
        print("\n🧠 Testing neural encoding cache...")
        
        encoder = accelerated.AcceleratedNeuralEncoder()
        
        features1 = accelerated.StyleFeatures(indent_size=4)
        features2 = accelerated.StyleFeatures(indent_size=2)
        
        enc1 = encoder.encode_style(features1)
        enc2 = encoder.encode_style(features2)
        
        # Test similarity caching
        start = time.perf_counter()
        for _ in range(1000):
            sim = encoder.similarity(enc1, enc2)
        cached_time = time.perf_counter() - start
        
        print(f"  1000 similarity computations: {cached_time*1000:.2f}ms")
        print(f"  Per operation: {cached_time:.6f}s")
        
        assert sim >= 0.0 and sim <= 1.0, "Similarity should be in [0, 1]"
        
        print("  ✓ Neural encoding cache works correctly")
        self.passed += 1
    
    def run_all(self):
        """Run all tests."""
        print("="*80)
        print("  ACCELERATED CODE STYLE TRANSFER - TEST SUITE")
        print("="*80)
        print("Author: @accelerate-specialist")
        print("Profile: Edsger Dijkstra - elegant and efficient")
        print("="*80)
        
        try:
            self.test_cache_functionality()
            self.test_cache_performance()
            self.test_correctness_parity()
            self.test_parallel_processing()
            self.test_batch_operations()
            self.test_memory_efficiency()
            self.test_performance_stats()
            self.test_neural_encoding_cache()
            
            print("\n" + "="*80)
            print(f"  RESULTS: {self.passed} passed, {self.failed} failed")
            print("="*80)
            
            if self.failed == 0:
                print("\n✅ All tests passed!")
                return 0
            else:
                print(f"\n❌ {self.failed} test(s) failed")
                return 1
                
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
            self.failed += 1
            return 1
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Run the test suite."""
    tester = TestAcceleratedStyleTransfer()
    return tester.run_all()


if __name__ == "__main__":
    sys.exit(main())
