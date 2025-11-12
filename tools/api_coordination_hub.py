#!/usr/bin/env python3
"""
API Coordination Hub

Centralized system for coordinating API calls across multiple services.
Provides circuit breaker pattern, unified rate limiting, and health monitoring.

Features:
- Circuit breaker pattern for service resilience
- Token bucket rate limiting with multiple tiers
- API health monitoring and scoring
- Metrics collection and export
- Thread-safe operations
- Automatic recovery mechanisms

Example:
    from api_coordination_hub import APICoordinationHub, APIConfig
    
    # Create hub
    hub = APICoordinationHub()
    
    # Register API
    hub.register_api('github', APIConfig(
        rate_limit=5000,
        time_window=3600,
        circuit_breaker_threshold=5
    ))
    
    # Execute API call with coordination
    @hub.coordinate('github')
    def make_github_call():
        return client.get('/user')
    
    result = make_github_call()
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable, Any, List
from enum import Enum
from functools import wraps
from collections import deque
import json
import sys


class CircuitState(Enum):
    """States for circuit breaker pattern"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service recovered


class HealthStatus(Enum):
    """API health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class APIConfig:
    """Configuration for an API endpoint"""
    rate_limit: int = 1000              # Requests per time window
    time_window: int = 3600             # Time window in seconds (default: 1 hour)
    circuit_breaker_threshold: int = 5  # Failures before opening circuit
    circuit_breaker_timeout: int = 60   # Seconds before trying half-open
    circuit_breaker_success_threshold: int = 2  # Successes in half-open to close
    timeout: int = 30                   # Request timeout in seconds
    max_retries: int = 3                # Maximum retry attempts
    priority: int = 1                   # Priority level (1-10, higher = more important)


@dataclass
class APIMetrics:
    """Metrics for an API endpoint"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    circuit_breaker_trips: int = 0
    total_latency: float = 0.0
    min_latency: float = float('inf')
    max_latency: float = 0.0
    last_request_time: Optional[float] = None
    last_error_time: Optional[float] = None
    last_error_message: Optional[str] = None
    
    def record_success(self, latency: float):
        """Record a successful request"""
        self.total_requests += 1
        self.successful_requests += 1
        self.total_latency += latency
        self.min_latency = min(self.min_latency, latency)
        self.max_latency = max(self.max_latency, latency)
        self.last_request_time = time.time()
    
    def record_failure(self, error_message: str):
        """Record a failed request"""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_request_time = time.time()
        self.last_error_time = time.time()
        self.last_error_message = error_message
    
    def record_rate_limit(self):
        """Record a rate-limited request"""
        self.rate_limited_requests += 1
    
    def record_circuit_breaker_trip(self):
        """Record a circuit breaker trip"""
        self.circuit_breaker_trips += 1
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def average_latency(self) -> float:
        """Calculate average latency"""
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency / self.successful_requests
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'rate_limited_requests': self.rate_limited_requests,
            'circuit_breaker_trips': self.circuit_breaker_trips,
            'success_rate': round(self.success_rate, 4),
            'average_latency': round(self.average_latency, 4),
            'min_latency': round(self.min_latency, 4) if self.min_latency != float('inf') else None,
            'max_latency': round(self.max_latency, 4),
            'last_request_time': self.last_request_time,
            'last_error_time': self.last_error_time,
            'last_error_message': self.last_error_message
        }


class TokenBucket:
    """Token bucket rate limiter"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if not enough tokens
        """
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_available(self) -> int:
        """Get number of available tokens"""
        with self.lock:
            self._refill()
            return int(self.tokens)
    
    def time_until_tokens(self, tokens: int) -> float:
        """
        Calculate time until specified tokens are available.
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Seconds until tokens are available
        """
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                return 0.0
            tokens_needed = tokens - self.tokens
            return tokens_needed / self.refill_rate


class CircuitBreaker:
    """Circuit breaker for API resilience"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening
            timeout: Seconds before trying half-open state
            success_threshold: Successes needed in half-open to close
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments for function
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        with self.lock:
            # Check if we should transition from open to half-open
            if self.state == CircuitState.OPEN:
                if self.last_failure_time and \
                   time.time() - self.last_failure_time >= self.timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise Exception(
                        f"Circuit breaker is OPEN. "
                        f"Retry after {self.timeout - (time.time() - self.last_failure_time):.0f}s"
                    )
        
        # Try to execute the function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
    
    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        with self.lock:
            return self.state
    
    def reset(self):
        """Reset circuit breaker to closed state"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0


class APIHealthMonitor:
    """Monitor API health and provide status"""
    
    def __init__(self, window_size: int = 100):
        """
        Initialize health monitor.
        
        Args:
            window_size: Number of recent requests to track
        """
        self.window_size = window_size
        self.recent_results = deque(maxlen=window_size)
        self.lock = threading.Lock()
    
    def record_result(self, success: bool, latency: float = 0.0):
        """
        Record a request result.
        
        Args:
            success: Whether request was successful
            latency: Request latency in seconds
        """
        with self.lock:
            self.recent_results.append({
                'success': success,
                'latency': latency,
                'timestamp': time.time()
            })
    
    def get_health_status(self) -> HealthStatus:
        """
        Get current health status based on recent results.
        
        Returns:
            Health status enum
        """
        with self.lock:
            if len(self.recent_results) < 5:
                return HealthStatus.UNKNOWN
            
            # Calculate success rate
            success_count = sum(1 for r in self.recent_results if r['success'])
            success_rate = success_count / len(self.recent_results)
            
            # Determine status
            if success_rate >= 0.95:
                return HealthStatus.HEALTHY
            elif success_rate >= 0.80:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.UNHEALTHY
    
    def get_health_score(self) -> float:
        """
        Get numerical health score (0.0 - 1.0).
        
        Returns:
            Health score
        """
        with self.lock:
            if len(self.recent_results) == 0:
                return 0.0
            
            success_count = sum(1 for r in self.recent_results if r['success'])
            return success_count / len(self.recent_results)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class APICoordinationHub:
    """
    Central coordination hub for managing API calls across services.
    
    Provides:
    - Unified rate limiting
    - Circuit breaker pattern
    - Health monitoring
    - Metrics collection
    """
    
    def __init__(self):
        """Initialize the coordination hub"""
        self.apis: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def register_api(self, name: str, config: Optional[APIConfig] = None):
        """
        Register an API for coordination.
        
        Args:
            name: API identifier
            config: API configuration (uses defaults if None)
        """
        if config is None:
            config = APIConfig()
        
        with self.lock:
            self.apis[name] = {
                'config': config,
                'rate_limiter': TokenBucket(
                    capacity=config.rate_limit,
                    refill_rate=config.rate_limit / config.time_window
                ),
                'circuit_breaker': CircuitBreaker(
                    failure_threshold=config.circuit_breaker_threshold,
                    timeout=config.circuit_breaker_timeout,
                    success_threshold=config.circuit_breaker_success_threshold
                ),
                'health_monitor': APIHealthMonitor(),
                'metrics': APIMetrics()
            }
    
    def is_registered(self, name: str) -> bool:
        """Check if an API is registered"""
        return name in self.apis
    
    def coordinate(self, api_name: str, tokens: int = 1):
        """
        Decorator for coordinating API calls.
        
        Args:
            api_name: Name of registered API
            tokens: Number of rate limit tokens to consume
            
        Example:
            @hub.coordinate('github')
            def get_user():
                return client.get('/user')
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.execute(api_name, func, tokens, *args, **kwargs)
            return wrapper
        return decorator
    
    def execute(
        self,
        api_name: str,
        func: Callable,
        tokens: int = 1,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with API coordination.
        
        Args:
            api_name: Name of registered API
            func: Function to execute
            tokens: Number of rate limit tokens to consume
            *args, **kwargs: Arguments for function
            
        Returns:
            Function result
            
        Raises:
            ValueError: If API not registered
            RateLimitExceeded: If rate limit exceeded
            CircuitBreakerOpen: If circuit breaker is open
        """
        if api_name not in self.apis:
            raise ValueError(f"API '{api_name}' not registered")
        
        api = self.apis[api_name]
        rate_limiter = api['rate_limiter']
        circuit_breaker = api['circuit_breaker']
        health_monitor = api['health_monitor']
        metrics = api['metrics']
        
        # Check rate limit
        if not rate_limiter.consume(tokens):
            metrics.record_rate_limit()
            wait_time = rate_limiter.time_until_tokens(tokens)
            raise RateLimitExceeded(
                f"Rate limit exceeded for '{api_name}'. "
                f"Retry after {wait_time:.1f} seconds"
            )
        
        # Execute with circuit breaker
        start_time = time.time()
        try:
            result = circuit_breaker.call(func, *args, **kwargs)
            latency = time.time() - start_time
            
            # Record success
            metrics.record_success(latency)
            health_monitor.record_result(True, latency)
            
            return result
            
        except Exception as e:
            latency = time.time() - start_time
            
            # Check if circuit breaker error
            if "Circuit breaker is OPEN" in str(e):
                metrics.record_circuit_breaker_trip()
                raise CircuitBreakerOpen(str(e))
            
            # Record failure
            metrics.record_failure(str(e))
            health_monitor.record_result(False, latency)
            
            raise
    
    def get_health_status(self, api_name: str) -> HealthStatus:
        """Get health status for an API"""
        if api_name not in self.apis:
            return HealthStatus.UNKNOWN
        return self.apis[api_name]['health_monitor'].get_health_status()
    
    def get_health_score(self, api_name: str) -> float:
        """Get health score for an API (0.0 - 1.0)"""
        if api_name not in self.apis:
            return 0.0
        return self.apis[api_name]['health_monitor'].get_health_score()
    
    def get_circuit_state(self, api_name: str) -> Optional[CircuitState]:
        """Get circuit breaker state for an API"""
        if api_name not in self.apis:
            return None
        return self.apis[api_name]['circuit_breaker'].get_state()
    
    def get_metrics(self, api_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for an API"""
        if api_name not in self.apis:
            return None
        return self.apis[api_name]['metrics'].to_dict()
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all registered APIs"""
        return {
            name: self.get_metrics(name)
            for name in self.apis.keys()
        }
    
    def get_available_tokens(self, api_name: str) -> Optional[int]:
        """Get available rate limit tokens for an API"""
        if api_name not in self.apis:
            return None
        return self.apis[api_name]['rate_limiter'].get_available()
    
    def reset_circuit_breaker(self, api_name: str) -> bool:
        """
        Reset circuit breaker for an API.
        
        Args:
            api_name: Name of API
            
        Returns:
            True if reset successful, False if API not found
        """
        if api_name not in self.apis:
            return False
        self.apis[api_name]['circuit_breaker'].reset()
        return True
    
    def export_metrics(self, filepath: Optional[str] = None) -> str:
        """
        Export all metrics as JSON.
        
        Args:
            filepath: Optional file path to write metrics
            
        Returns:
            JSON string of metrics
        """
        metrics_data = {
            'timestamp': time.time(),
            'apis': {}
        }
        
        for api_name in self.apis.keys():
            metrics_data['apis'][api_name] = {
                'metrics': self.get_metrics(api_name),
                'health_status': self.get_health_status(api_name).value,
                'health_score': self.get_health_score(api_name),
                'circuit_state': self.get_circuit_state(api_name).value,
                'available_tokens': self.get_available_tokens(api_name)
            }
        
        json_str = json.dumps(metrics_data, indent=2)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
        
        return json_str
    
    def print_status(self):
        """Print status of all registered APIs"""
        print("\n" + "="*70)
        print("🔗 API Coordination Hub Status")
        print("="*70 + "\n")
        
        for api_name in sorted(self.apis.keys()):
            health = self.get_health_status(api_name)
            score = self.get_health_score(api_name)
            circuit = self.get_circuit_state(api_name)
            tokens = self.get_available_tokens(api_name)
            metrics = self.get_metrics(api_name)
            
            # Health icon
            health_icons = {
                HealthStatus.HEALTHY: "✓",
                HealthStatus.DEGRADED: "⚠",
                HealthStatus.UNHEALTHY: "✗",
                HealthStatus.UNKNOWN: "?"
            }
            icon = health_icons.get(health, "?")
            
            print(f"{icon} {api_name.upper()}")
            print(f"  Health: {health.value} ({score:.2%})")
            print(f"  Circuit: {circuit.value}")
            print(f"  Tokens: {tokens}")
            print(f"  Requests: {metrics['total_requests']} "
                  f"(success: {metrics['success_rate']:.2%})")
            if metrics['average_latency'] > 0:
                print(f"  Latency: avg={metrics['average_latency']:.3f}s")
            print()
        
        print("="*70 + "\n")


# Singleton instance
_hub_instance = None


def get_hub() -> APICoordinationHub:
    """Get singleton hub instance"""
    global _hub_instance
    if _hub_instance is None:
        _hub_instance = APICoordinationHub()
    return _hub_instance


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='API Coordination Hub Demo')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--export', help='Export metrics to file')
    
    args = parser.parse_args()
    
    hub = get_hub()
    
    if args.demo:
        print("Running API Coordination Hub demo...\n")
        
        # Register APIs
        hub.register_api('github', APIConfig(
            rate_limit=100,
            time_window=60,
            circuit_breaker_threshold=3
        ))
        
        hub.register_api('web', APIConfig(
            rate_limit=50,
            time_window=60,
            circuit_breaker_threshold=5
        ))
        
        # Simulate some API calls
        @hub.coordinate('github')
        def github_call(success=True):
            time.sleep(0.1)  # Simulate latency
            if not success:
                raise Exception("API error")
            return {'status': 'ok'}
        
        # Make successful calls
        print("Making successful API calls...")
        for i in range(10):
            try:
                result = github_call()
                print(f"  Call {i+1}: ✓")
            except Exception as e:
                print(f"  Call {i+1}: ✗ {e}")
        
        # Make some failed calls
        print("\nSimulating failures...")
        for i in range(3):
            try:
                result = github_call(success=False)
            except Exception as e:
                print(f"  Failure {i+1}: {type(e).__name__}")
        
        # Show status
        hub.print_status()
    
    elif args.status:
        hub.print_status()
    
    elif args.export:
        metrics = hub.export_metrics(args.export)
        print(f"Metrics exported to {args.export}")
    
    else:
        parser.print_help()
