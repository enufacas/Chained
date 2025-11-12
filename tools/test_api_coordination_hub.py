#!/usr/bin/env python3
"""
Tests for API Coordination Hub

Comprehensive tests for circuit breaker, rate limiting, health monitoring,
and coordination features.
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch
import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from api_coordination_hub import (
    APICoordinationHub,
    APIConfig,
    CircuitBreaker,
    CircuitState,
    TokenBucket,
    APIHealthMonitor,
    HealthStatus,
    RateLimitExceeded,
    CircuitBreakerOpen,
    get_hub
)


class TestTokenBucket(unittest.TestCase):
    """Test token bucket rate limiter"""
    
    def test_initial_tokens(self):
        """Test initial token count"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        self.assertEqual(bucket.get_available(), 10)
    
    def test_consume_tokens(self):
        """Test consuming tokens"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        self.assertTrue(bucket.consume(5))
        self.assertEqual(bucket.get_available(), 5)
    
    def test_consume_too_many_tokens(self):
        """Test consuming more tokens than available"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        self.assertFalse(bucket.consume(15))
        self.assertEqual(bucket.get_available(), 10)
    
    def test_refill_tokens(self):
        """Test token refill over time"""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens/second
        bucket.consume(10)  # Empty the bucket
        self.assertEqual(bucket.get_available(), 0)
        
        time.sleep(0.5)  # Wait for refill
        available = bucket.get_available()
        self.assertGreater(available, 3)  # Should have refilled ~5 tokens
        self.assertLess(available, 7)
    
    def test_max_capacity(self):
        """Test that tokens don't exceed capacity"""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)
        time.sleep(2)  # Wait longer than needed for full refill
        self.assertEqual(bucket.get_available(), 10)
    
    def test_time_until_tokens(self):
        """Test calculating time until tokens available"""
        bucket = TokenBucket(capacity=10, refill_rate=2.0)  # 2 tokens/second
        bucket.consume(10)
        
        time_until = bucket.time_until_tokens(5)
        self.assertAlmostEqual(time_until, 2.5, places=1)
    
    def test_thread_safety(self):
        """Test thread-safe token consumption"""
        bucket = TokenBucket(capacity=100, refill_rate=10.0)
        results = []
        
        def consume_tokens():
            for _ in range(10):
                results.append(bucket.consume(1))
        
        threads = [threading.Thread(target=consume_tokens) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All 50 consumptions should succeed (50 < 100)
        self.assertEqual(sum(results), 50)


class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker pattern"""
    
    def test_initial_state(self):
        """Test initial circuit breaker state"""
        cb = CircuitBreaker(failure_threshold=3)
        self.assertEqual(cb.get_state(), CircuitState.CLOSED)
    
    def test_successful_calls(self):
        """Test successful calls keep circuit closed"""
        cb = CircuitBreaker(failure_threshold=3)
        
        for _ in range(5):
            result = cb.call(lambda: "success")
            self.assertEqual(result, "success")
        
        self.assertEqual(cb.get_state(), CircuitState.CLOSED)
    
    def test_open_circuit_on_failures(self):
        """Test circuit opens after threshold failures"""
        cb = CircuitBreaker(failure_threshold=3, timeout=1)
        
        # Cause failures
        for i in range(3):
            with self.assertRaises(Exception):
                cb.call(lambda: (_ for _ in ()).throw(Exception("error")))
        
        self.assertEqual(cb.get_state(), CircuitState.OPEN)
    
    def test_open_circuit_fails_fast(self):
        """Test open circuit fails fast without calling function"""
        cb = CircuitBreaker(failure_threshold=2, timeout=1)
        mock_func = Mock(side_effect=Exception("error"))
        
        # Cause failures to open circuit
        for _ in range(2):
            with self.assertRaises(Exception):
                cb.call(mock_func)
        
        self.assertEqual(cb.get_state(), CircuitState.OPEN)
        self.assertEqual(mock_func.call_count, 2)
        
        # Next call should fail fast without calling function
        with self.assertRaises(Exception) as context:
            cb.call(mock_func)
        
        self.assertIn("Circuit breaker is OPEN", str(context.exception))
        self.assertEqual(mock_func.call_count, 2)  # Not called again
    
    def test_half_open_on_timeout(self):
        """Test circuit transitions to half-open after timeout"""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.5)
        
        # Open the circuit
        for _ in range(2):
            with self.assertRaises(Exception):
                cb.call(lambda: (_ for _ in ()).throw(Exception("error")))
        
        self.assertEqual(cb.get_state(), CircuitState.OPEN)
        
        # Wait for timeout
        time.sleep(0.6)
        
        # Next calls should transition to half-open then closed
        # Default success_threshold is 2, so need 2 successful calls
        cb.call(lambda: "success")
        cb.call(lambda: "success")
        
        # State should be CLOSED after enough successes in half-open
        self.assertEqual(cb.get_state(), CircuitState.CLOSED)
    
    def test_half_open_to_closed(self):
        """Test half-open transitions to closed after successes"""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.5, success_threshold=2)
        
        # Open the circuit
        for _ in range(2):
            with self.assertRaises(Exception):
                cb.call(lambda: (_ for _ in ()).throw(Exception("error")))
        
        time.sleep(0.6)
        
        # Make successful calls in half-open
        for _ in range(2):
            cb.call(lambda: "success")
        
        self.assertEqual(cb.get_state(), CircuitState.CLOSED)
    
    def test_half_open_to_open_on_failure(self):
        """Test half-open transitions back to open on failure"""
        cb = CircuitBreaker(failure_threshold=2, timeout=0.5)
        
        # Open the circuit
        for _ in range(2):
            with self.assertRaises(Exception):
                cb.call(lambda: (_ for _ in ()).throw(Exception("error")))
        
        time.sleep(0.6)
        
        # Fail in half-open state
        with self.assertRaises(Exception):
            cb.call(lambda: (_ for _ in ()).throw(Exception("error")))
        
        self.assertEqual(cb.get_state(), CircuitState.OPEN)
    
    def test_reset(self):
        """Test manual circuit breaker reset"""
        cb = CircuitBreaker(failure_threshold=2)
        
        # Open the circuit
        for _ in range(2):
            with self.assertRaises(Exception):
                cb.call(lambda: (_ for _ in ()).throw(Exception("error")))
        
        self.assertEqual(cb.get_state(), CircuitState.OPEN)
        
        # Reset
        cb.reset()
        self.assertEqual(cb.get_state(), CircuitState.CLOSED)


class TestAPIHealthMonitor(unittest.TestCase):
    """Test API health monitoring"""
    
    def test_initial_status_unknown(self):
        """Test initial status is unknown"""
        monitor = APIHealthMonitor()
        self.assertEqual(monitor.get_health_status(), HealthStatus.UNKNOWN)
    
    def test_healthy_status(self):
        """Test healthy status with good success rate"""
        monitor = APIHealthMonitor()
        
        # Record successful requests
        for _ in range(20):
            monitor.record_result(True, 0.1)
        
        self.assertEqual(monitor.get_health_status(), HealthStatus.HEALTHY)
        self.assertGreaterEqual(monitor.get_health_score(), 0.95)
    
    def test_degraded_status(self):
        """Test degraded status with moderate success rate"""
        monitor = APIHealthMonitor()
        
        # Record mixed results (85% success)
        for _ in range(17):
            monitor.record_result(True, 0.1)
        for _ in range(3):
            monitor.record_result(False, 0.1)
        
        self.assertEqual(monitor.get_health_status(), HealthStatus.DEGRADED)
        score = monitor.get_health_score()
        self.assertGreaterEqual(score, 0.80)
        self.assertLess(score, 0.95)
    
    def test_unhealthy_status(self):
        """Test unhealthy status with low success rate"""
        monitor = APIHealthMonitor()
        
        # Record mostly failures (50% success)
        for _ in range(10):
            monitor.record_result(True, 0.1)
        for _ in range(10):
            monitor.record_result(False, 0.1)
        
        self.assertEqual(monitor.get_health_status(), HealthStatus.UNHEALTHY)
        self.assertLess(monitor.get_health_score(), 0.80)
    
    def test_window_size(self):
        """Test health monitor respects window size"""
        monitor = APIHealthMonitor(window_size=10)
        
        # Record 20 failures
        for _ in range(20):
            monitor.record_result(False, 0.1)
        
        # Then record 10 successes (should fill window)
        for _ in range(10):
            monitor.record_result(True, 0.1)
        
        # Should be healthy (only last 10 matter)
        self.assertEqual(monitor.get_health_status(), HealthStatus.HEALTHY)


class TestAPICoordinationHub(unittest.TestCase):
    """Test API Coordination Hub"""
    
    def setUp(self):
        """Create fresh hub for each test"""
        self.hub = APICoordinationHub()
    
    def test_register_api(self):
        """Test registering an API"""
        self.hub.register_api('test', APIConfig(rate_limit=100))
        self.assertTrue(self.hub.is_registered('test'))
    
    def test_register_api_with_defaults(self):
        """Test registering API with default config"""
        self.hub.register_api('test')
        self.assertTrue(self.hub.is_registered('test'))
    
    def test_execute_successful_call(self):
        """Test executing successful API call"""
        self.hub.register_api('test', APIConfig(rate_limit=10))
        
        def api_call():
            return {'status': 'ok'}
        
        result = self.hub.execute('test', api_call)
        self.assertEqual(result, {'status': 'ok'})
        
        metrics = self.hub.get_metrics('test')
        self.assertEqual(metrics['successful_requests'], 1)
        self.assertEqual(metrics['failed_requests'], 0)
    
    def test_execute_failed_call(self):
        """Test executing failed API call"""
        self.hub.register_api('test', APIConfig(rate_limit=10))
        
        def api_call():
            raise Exception("API error")
        
        with self.assertRaises(Exception):
            self.hub.execute('test', api_call)
        
        metrics = self.hub.get_metrics('test')
        self.assertEqual(metrics['successful_requests'], 0)
        self.assertEqual(metrics['failed_requests'], 1)
    
    def test_rate_limit_enforcement(self):
        """Test rate limit is enforced"""
        self.hub.register_api('test', APIConfig(
            rate_limit=5,
            time_window=60
        ))
        
        def api_call():
            return "ok"
        
        # Make 5 successful calls
        for _ in range(5):
            self.hub.execute('test', api_call)
        
        # 6th call should hit rate limit
        with self.assertRaises(RateLimitExceeded):
            self.hub.execute('test', api_call)
        
        metrics = self.hub.get_metrics('test')
        self.assertEqual(metrics['rate_limited_requests'], 1)
    
    def test_circuit_breaker_integration(self):
        """Test circuit breaker integration"""
        self.hub.register_api('test', APIConfig(
            rate_limit=100,
            circuit_breaker_threshold=3
        ))
        
        def failing_call():
            raise Exception("API error")
        
        # Cause 3 failures to open circuit
        for _ in range(3):
            with self.assertRaises(Exception):
                self.hub.execute('test', failing_call)
        
        self.assertEqual(
            self.hub.get_circuit_state('test'),
            CircuitState.OPEN
        )
        
        # Next call should trigger circuit breaker
        with self.assertRaises(CircuitBreakerOpen):
            self.hub.execute('test', failing_call)
    
    def test_decorator_usage(self):
        """Test using decorator for coordination"""
        self.hub.register_api('test', APIConfig(rate_limit=10))
        
        @self.hub.coordinate('test')
        def api_call():
            return "success"
        
        result = api_call()
        self.assertEqual(result, "success")
        
        metrics = self.hub.get_metrics('test')
        self.assertEqual(metrics['total_requests'], 1)
    
    def test_health_status_tracking(self):
        """Test health status is tracked"""
        self.hub.register_api('test', APIConfig(rate_limit=100))
        
        # Make successful calls
        for _ in range(20):
            self.hub.execute('test', lambda: "ok")
        
        self.assertEqual(
            self.hub.get_health_status('test'),
            HealthStatus.HEALTHY
        )
        self.assertGreaterEqual(self.hub.get_health_score('test'), 0.95)
    
    def test_metrics_collection(self):
        """Test metrics are collected correctly"""
        self.hub.register_api('test', APIConfig(rate_limit=100))
        
        def slow_call():
            time.sleep(0.01)
            return "ok"
        
        # Make some calls
        for _ in range(5):
            self.hub.execute('test', slow_call)
        
        metrics = self.hub.get_metrics('test')
        self.assertEqual(metrics['total_requests'], 5)
        self.assertEqual(metrics['successful_requests'], 5)
        self.assertGreater(metrics['average_latency'], 0)
        self.assertIsNotNone(metrics['last_request_time'])
    
    def test_get_all_metrics(self):
        """Test getting metrics for all APIs"""
        self.hub.register_api('api1', APIConfig(rate_limit=10))
        self.hub.register_api('api2', APIConfig(rate_limit=20))
        
        self.hub.execute('api1', lambda: "ok")
        self.hub.execute('api2', lambda: "ok")
        
        all_metrics = self.hub.get_all_metrics()
        self.assertIn('api1', all_metrics)
        self.assertIn('api2', all_metrics)
        self.assertEqual(all_metrics['api1']['total_requests'], 1)
        self.assertEqual(all_metrics['api2']['total_requests'], 1)
    
    def test_reset_circuit_breaker(self):
        """Test resetting circuit breaker"""
        self.hub.register_api('test', APIConfig(
            rate_limit=100,
            circuit_breaker_threshold=2
        ))
        
        # Open the circuit
        for _ in range(2):
            with self.assertRaises(Exception):
                self.hub.execute('test', lambda: (_ for _ in ()).throw(Exception("error")))
        
        self.assertEqual(
            self.hub.get_circuit_state('test'),
            CircuitState.OPEN
        )
        
        # Reset
        success = self.hub.reset_circuit_breaker('test')
        self.assertTrue(success)
        self.assertEqual(
            self.hub.get_circuit_state('test'),
            CircuitState.CLOSED
        )
    
    def test_export_metrics(self):
        """Test exporting metrics as JSON"""
        self.hub.register_api('test', APIConfig(rate_limit=10))
        self.hub.execute('test', lambda: "ok")
        
        metrics_json = self.hub.export_metrics()
        self.assertIn('test', metrics_json)
        self.assertIn('timestamp', metrics_json)
        self.assertIn('metrics', metrics_json)
    
    def test_unregistered_api_error(self):
        """Test error when using unregistered API"""
        with self.assertRaises(ValueError):
            self.hub.execute('nonexistent', lambda: "ok")
    
    def test_concurrent_access(self):
        """Test thread-safe concurrent access"""
        self.hub.register_api('test', APIConfig(rate_limit=100))
        results = []
        
        def make_calls():
            for _ in range(10):
                try:
                    result = self.hub.execute('test', lambda: "ok")
                    results.append(result)
                except:
                    pass
        
        threads = [threading.Thread(target=make_calls) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All 50 calls should succeed
        self.assertEqual(len(results), 50)
        
        metrics = self.hub.get_metrics('test')
        self.assertEqual(metrics['total_requests'], 50)


class TestSingletonHub(unittest.TestCase):
    """Test singleton hub instance"""
    
    def test_get_hub_returns_same_instance(self):
        """Test get_hub returns singleton"""
        hub1 = get_hub()
        hub2 = get_hub()
        self.assertIs(hub1, hub2)


class TestAPIConfig(unittest.TestCase):
    """Test API configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = APIConfig()
        self.assertEqual(config.rate_limit, 1000)
        self.assertEqual(config.time_window, 3600)
        self.assertEqual(config.circuit_breaker_threshold, 5)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 3)
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = APIConfig(
            rate_limit=500,
            time_window=1800,
            circuit_breaker_threshold=3,
            priority=5
        )
        self.assertEqual(config.rate_limit, 500)
        self.assertEqual(config.time_window, 1800)
        self.assertEqual(config.circuit_breaker_threshold, 3)
        self.assertEqual(config.priority, 5)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_workflow(self):
        """Test complete workflow with multiple APIs"""
        hub = APICoordinationHub()
        
        # Register multiple APIs
        hub.register_api('github', APIConfig(
            rate_limit=50,
            time_window=60,
            circuit_breaker_threshold=3
        ))
        
        hub.register_api('web', APIConfig(
            rate_limit=30,
            time_window=60,
            circuit_breaker_threshold=5
        ))
        
        # Define API functions
        @hub.coordinate('github')
        def get_user():
            return {'user': 'test'}
        
        @hub.coordinate('web')
        def fetch_content(url):
            return {'content': f'Content from {url}'}
        
        # Make calls
        user = get_user()
        self.assertEqual(user['user'], 'test')
        
        content = fetch_content('http://example.com')
        self.assertIn('Content from', content['content'])
        
        # Check metrics
        github_metrics = hub.get_metrics('github')
        web_metrics = hub.get_metrics('web')
        
        self.assertEqual(github_metrics['total_requests'], 1)
        self.assertEqual(web_metrics['total_requests'], 1)
        
        # Check health
        self.assertEqual(hub.get_health_status('github'), HealthStatus.UNKNOWN)
        self.assertEqual(hub.get_health_status('web'), HealthStatus.UNKNOWN)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTokenBucket))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreaker))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIHealthMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestAPICoordinationHub))
    suite.addTests(loader.loadTestsFromTestCase(TestSingletonHub))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
