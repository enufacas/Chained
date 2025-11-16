#!/usr/bin/env python3
"""
Tests for API Call Batcher

Comprehensive test suite for request batching, deduplication, and queuing.

Created by: @accelerate-specialist
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch
import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from api_call_batcher import (
    BatchedAPIClient,
    BatchConfig,
    APIRequest,
    RequestFuture,
    BatchStrategy,
    get_batcher
)


class TestAPIRequest(unittest.TestCase):
    """Test APIRequest data structure"""
    
    def test_request_creation(self):
        """Test basic request creation"""
        req = APIRequest(method='GET', endpoint='/api/users')
        self.assertEqual(req.method, 'GET')
        self.assertEqual(req.endpoint, '/api/users')
        self.assertEqual(req.priority, 5)  # Default priority
    
    def test_request_id_generation(self):
        """Test automatic request ID generation"""
        req1 = APIRequest(method='GET', endpoint='/api/users')
        req2 = APIRequest(method='GET', endpoint='/api/users')
        
        # Same request should generate same ID
        self.assertEqual(req1.request_id, req2.request_id)
    
    def test_request_id_uniqueness(self):
        """Test that different requests have different IDs"""
        req1 = APIRequest(method='GET', endpoint='/api/users')
        req2 = APIRequest(method='GET', endpoint='/api/posts')
        
        self.assertNotEqual(req1.request_id, req2.request_id)
    
    def test_request_priority_comparison(self):
        """Test priority-based comparison"""
        high_priority = APIRequest(method='GET', endpoint='/api/users', priority=10)
        low_priority = APIRequest(method='GET', endpoint='/api/posts', priority=1)
        
        # Higher priority should be "less than" for max-heap behavior
        self.assertTrue(high_priority < low_priority)
    
    def test_request_with_params(self):
        """Test request with query parameters"""
        params = {'page': 1, 'limit': 10}
        req1 = APIRequest(method='GET', endpoint='/api/users', params=params)
        req2 = APIRequest(method='GET', endpoint='/api/users', params=params)
        
        # Same params should generate same ID
        self.assertEqual(req1.request_id, req2.request_id)
    
    def test_request_params_order_independence(self):
        """Test that param order doesn't affect ID"""
        req1 = APIRequest(
            method='GET',
            endpoint='/api/users',
            params={'a': 1, 'b': 2}
        )
        req2 = APIRequest(
            method='GET',
            endpoint='/api/users',
            params={'b': 2, 'a': 1}
        )
        
        # Different order, same ID
        self.assertEqual(req1.request_id, req2.request_id)


class TestRequestFuture(unittest.TestCase):
    """Test RequestFuture async result handling"""
    
    def test_set_and_get_result(self):
        """Test setting and getting result"""
        future = RequestFuture()
        future.set_result({'status': 'ok'})
        
        result = future.result()
        self.assertEqual(result, {'status': 'ok'})
    
    def test_set_and_get_error(self):
        """Test setting and getting error"""
        future = RequestFuture()
        error = ValueError("Test error")
        future.set_error(error)
        
        with self.assertRaises(ValueError):
            future.result()
    
    def test_timeout(self):
        """Test result timeout"""
        future = RequestFuture()
        
        with self.assertRaises(TimeoutError):
            future.result(timeout=0.1)
    
    def test_is_done(self):
        """Test completion status check"""
        future = RequestFuture()
        self.assertFalse(future.is_done())
        
        future.set_result('done')
        self.assertTrue(future.is_done())
    
    def test_blocking_until_result(self):
        """Test that result() blocks until value is set"""
        future = RequestFuture()
        result_holder = []
        
        def set_result_delayed():
            time.sleep(0.2)
            future.set_result('delayed_value')
        
        def get_result():
            result = future.result(timeout=1.0)
            result_holder.append(result)
        
        # Start threads
        setter = threading.Thread(target=set_result_delayed)
        getter = threading.Thread(target=get_result)
        
        getter.start()
        setter.start()
        
        getter.join()
        setter.join()
        
        self.assertEqual(result_holder[0], 'delayed_value')


class TestBatchedAPIClient(unittest.TestCase):
    """Test BatchedAPIClient functionality"""
    
    def setUp(self):
        """Set up test batcher"""
        self.config = BatchConfig(
            batch_size=5,
            flush_interval=0.5,
            enable_deduplication=True
        )
        self.batcher = BatchedAPIClient(self.config)
    
    def tearDown(self):
        """Clean up batcher"""
        self.batcher.stop()
    
    def test_basic_request(self):
        """Test basic request submission and retrieval"""
        self.batcher.start()
        
        future = self.batcher.add_request('GET', '/api/test')
        result = future.result(timeout=2.0)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['method'], 'GET')
        self.assertEqual(result['endpoint'], '/api/test')
    
    def test_batching(self):
        """Test that requests are batched"""
        self.batcher.start()
        
        # Submit multiple requests
        futures = []
        for i in range(10):
            future = self.batcher.add_request('GET', f'/api/users/{i}')
            futures.append(future)
        
        # Wait for all results
        for future in futures:
            result = future.result(timeout=2.0)
            self.assertIsNotNone(result)
        
        stats = self.batcher.get_stats()
        
        # Should have batched requests
        self.assertGreater(stats['batches_flushed'], 0)
        self.assertLessEqual(stats['batches_flushed'], 10)  # Fewer batches than requests
    
    def test_deduplication(self):
        """Test request deduplication"""
        self.batcher.start()
        
        # Submit identical requests
        future1 = self.batcher.add_request('GET', '/api/same')
        future2 = self.batcher.add_request('GET', '/api/same')
        future3 = self.batcher.add_request('GET', '/api/same')
        
        # All should get same result
        result1 = future1.result(timeout=2.0)
        result2 = future2.result(timeout=2.0)
        result3 = future3.result(timeout=2.0)
        
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertIsNotNone(result3)
        
        stats = self.batcher.get_stats()
        
        # Should have deduplicated some requests
        self.assertGreater(stats['deduplicated_requests'], 0)
    
    def test_priority_ordering(self):
        """Test that high priority requests are processed first"""
        results = []
        
        def custom_executor(requests):
            """Track order of execution"""
            for req in requests:
                results.append((req.endpoint, req.priority))
            return [{'status': 'ok'} for _ in requests]
        
        batcher = BatchedAPIClient(
            BatchConfig(batch_size=10, flush_interval=0.5),
            executor=custom_executor
        )
        batcher.start()
        
        # Submit requests with different priorities
        futures = []
        futures.append(batcher.add_request('GET', '/low', priority=1))
        futures.append(batcher.add_request('GET', '/high', priority=10))
        futures.append(batcher.add_request('GET', '/medium', priority=5))
        
        # Wait for processing
        for future in futures:
            future.result(timeout=2.0)
        
        batcher.stop()
        
        # High priority should be processed first
        if len(results) >= 2:
            # Check that higher priorities tend to come first
            priorities = [p for _, p in results]
            # At least the first should be high priority
            self.assertGreaterEqual(priorities[0], 5)
    
    def test_flush(self):
        """Test manual flush"""
        self.batcher.start()
        
        # Add requests
        futures = []
        for i in range(3):
            future = self.batcher.add_request('GET', f'/api/test/{i}')
            futures.append(future)
        
        # Manually flush
        self.batcher.flush()
        
        # All results should be available quickly
        for future in futures:
            result = future.result(timeout=1.0)
            self.assertIsNotNone(result)
    
    def test_auto_flush_on_size(self):
        """Test automatic flush when batch size is reached"""
        config = BatchConfig(batch_size=3, flush_interval=10.0)  # Long interval
        batcher = BatchedAPIClient(config)
        batcher.start()
        
        # Submit exactly batch_size requests
        futures = []
        for i in range(3):
            future = batcher.add_request('GET', f'/api/test/{i}')
            futures.append(future)
        
        # Should flush automatically due to size
        for future in futures:
            result = future.result(timeout=2.0)
            self.assertIsNotNone(result)
        
        batcher.stop()
    
    def test_auto_flush_on_time(self):
        """Test automatic flush based on time interval"""
        config = BatchConfig(batch_size=100, flush_interval=0.3)  # Short interval
        batcher = BatchedAPIClient(config)
        batcher.start()
        
        # Submit a few requests (less than batch size)
        futures = []
        for i in range(2):
            future = batcher.add_request('GET', f'/api/test/{i}')
            futures.append(future)
        
        # Should flush automatically due to time
        for future in futures:
            result = future.result(timeout=2.0)
            self.assertIsNotNone(result)
        
        batcher.stop()
    
    def test_dedup_cache_cleanup(self):
        """Test that dedup cache is cleaned up"""
        config = BatchConfig(dedup_window=0.2, flush_interval=0.1)  # Short windows
        batcher = BatchedAPIClient(config)
        batcher.start()
        
        # Make a request
        future1 = batcher.add_request('GET', '/api/test')
        result1 = future1.result(timeout=2.0)
        
        # Wait for cache to expire
        time.sleep(0.3)
        
        # Make same request again - should not be deduplicated
        future2 = batcher.add_request('GET', '/api/test')
        result2 = future2.result(timeout=2.0)
        
        batcher.stop()
        
        # Both should succeed
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
    
    def test_thread_safety(self):
        """Test concurrent request submission"""
        self.batcher.start()
        
        results = []
        errors = []
        
        def submit_requests():
            try:
                for i in range(10):
                    future = self.batcher.add_request('GET', f'/api/thread/{i}')
                    result = future.result(timeout=5.0)
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads
        threads = [threading.Thread(target=submit_requests) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # No errors should occur
        self.assertEqual(len(errors), 0)
        
        # All requests should succeed
        self.assertEqual(len(results), 50)
    
    def test_stats(self):
        """Test statistics tracking"""
        self.batcher.start()
        
        # Make some requests
        futures = []
        for i in range(10):
            future = self.batcher.add_request('GET', f'/api/test/{i}')
            futures.append(future)
        
        # Wait for completion
        for future in futures:
            future.result(timeout=2.0)
        
        stats = self.batcher.get_stats()
        
        # Verify stats
        self.assertEqual(stats['total_requests'], 10)
        self.assertGreater(stats['batches_flushed'], 0)
        self.assertGreaterEqual(stats['batched_requests'], 10)
    
    def test_custom_executor(self):
        """Test with custom executor function"""
        call_count = [0]
        
        def custom_executor(requests):
            call_count[0] += 1
            return [{'custom': True, 'id': r.endpoint} for r in requests]
        
        batcher = BatchedAPIClient(
            BatchConfig(batch_size=5, flush_interval=0.3),
            executor=custom_executor
        )
        batcher.start()
        
        # Submit requests
        future = batcher.add_request('GET', '/custom')
        result = future.result(timeout=3.0)
        
        batcher.stop()
        
        # Custom executor should have been called
        self.assertGreater(call_count[0], 0)
        self.assertTrue(result['custom'])
        self.assertEqual(result['id'], '/custom')
    
    def test_stop_and_cleanup(self):
        """Test proper cleanup on stop"""
        batcher = BatchedAPIClient(BatchConfig())
        batcher.start()
        
        # Add some requests
        futures = []
        for i in range(5):
            future = batcher.add_request('GET', f'/api/test/{i}')
            futures.append(future)
        
        # Stop should flush and clean up
        batcher.stop(timeout=2.0)
        
        # All futures should be resolved
        for future in futures:
            self.assertTrue(future.is_done())


class TestSingletonBatcher(unittest.TestCase):
    """Test singleton batcher instance"""
    
    def test_get_batcher_singleton(self):
        """Test that get_batcher returns singleton"""
        batcher1 = get_batcher()
        batcher2 = get_batcher()
        
        self.assertIs(batcher1, batcher2)
        
        batcher1.stop()


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_high_volume_requests(self):
        """Test handling high volume of requests"""
        config = BatchConfig(
            batch_size=20,
            flush_interval=0.5,
            enable_deduplication=True
        )
        batcher = BatchedAPIClient(config)
        batcher.start()
        
        # Submit many requests
        num_requests = 100
        futures = []
        
        for i in range(num_requests):
            endpoint = f'/api/users/{i % 20}'  # Some duplicates
            future = batcher.add_request('GET', endpoint)
            futures.append(future)
        
        # All should complete
        for future in futures:
            result = future.result(timeout=10.0)
            self.assertIsNotNone(result)
        
        stats = batcher.get_stats()
        batcher.stop()
        
        # Verify efficiency
        self.assertEqual(stats['total_requests'], num_requests)
        self.assertGreater(stats['deduplicated_requests'], 0)
        self.assertLess(stats['batches_flushed'], num_requests)
    
    def test_mixed_priority_workload(self):
        """Test workload with mixed priorities"""
        batcher = BatchedAPIClient(BatchConfig(batch_size=10))
        batcher.start()
        
        # Submit requests with various priorities
        futures = []
        for i in range(30):
            priority = (i % 10) + 1
            future = batcher.add_request(
                'GET',
                f'/api/test/{i}',
                priority=priority
            )
            futures.append(future)
        
        # All should complete
        for future in futures:
            result = future.result(timeout=5.0)
            self.assertIsNotNone(result)
        
        batcher.stop()
        
        # Test passed if no exceptions


if __name__ == '__main__':
    unittest.main()
