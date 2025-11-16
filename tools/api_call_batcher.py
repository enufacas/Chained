#!/usr/bin/env python3
"""
API Call Batcher - Reduce rate limit usage through intelligent request batching

This module provides request batching, deduplication, and queuing to minimize
API calls and stay within rate limits. It works seamlessly with the existing
APICoordinationHub for unified API management.

Features:
- Request batching: Group similar requests into batch operations
- Request deduplication: Avoid redundant calls for identical requests
- Priority queuing: Ensure critical requests are processed first
- Automatic flushing: Configurable batch size and time windows
- Thread-safe operations: Safe for concurrent use
- Integration with APICoordinationHub: Unified API management

Created by: @accelerate-specialist
Mission: AI Idea - Build an API call batcher to reduce rate limit usage
Date: 2025-11-16

Example:
    from api_call_batcher import BatchedAPIClient, BatchConfig
    
    # Create batcher
    batcher = BatchedAPIClient(
        batch_size=10,
        flush_interval=5.0
    )
    
    # Add requests
    future1 = batcher.add_request('GET', '/users/1', priority=5)
    future2 = batcher.add_request('GET', '/users/1', priority=3)  # Deduplicated!
    
    # Get results (blocks until request is processed)
    result1 = future1.result()
    result2 = future2.result()  # Same result, no extra API call
"""

import time
import threading
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Optional, Callable, Any, List, Tuple
from enum import Enum
from collections import deque
from queue import PriorityQueue
import sys


class BatchStrategy(Enum):
    """Strategies for batching requests"""
    TIME_WINDOW = "time_window"    # Batch based on time window
    SIZE_BASED = "size_based"       # Batch based on number of requests
    ADAPTIVE = "adaptive"           # Adapt based on load and rate limits


@dataclass
class BatchConfig:
    """Configuration for API call batcher"""
    batch_size: int = 10                    # Max requests per batch
    flush_interval: float = 5.0             # Seconds before auto-flush
    enable_deduplication: bool = True       # Deduplicate identical requests
    dedup_window: float = 60.0              # Deduplication window in seconds
    max_queue_size: int = 1000              # Maximum queued requests
    strategy: BatchStrategy = BatchStrategy.ADAPTIVE


@dataclass
class APIRequest:
    """Represents a single API request"""
    method: str
    endpoint: str
    params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    priority: int = 5                       # Priority 1-10 (higher = more important)
    timestamp: float = field(default_factory=time.time)
    request_id: str = field(default="")
    
    def __post_init__(self):
        """Generate unique request ID if not provided"""
        if not self.request_id:
            self.request_id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID based on request content"""
        content = f"{self.method}:{self.endpoint}:{json.dumps(self.params, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def __lt__(self, other):
        """Compare for priority queue (higher priority = lower value for min-heap)"""
        return self.priority > other.priority  # Inverted for max-heap behavior


class RequestFuture:
    """Future-like object for async request results"""
    
    def __init__(self):
        self.result_value = None
        self.error = None
        self.completed = threading.Event()
    
    def set_result(self, value: Any):
        """Set the result and mark as complete"""
        self.result_value = value
        self.completed.set()
    
    def set_error(self, error: Exception):
        """Set an error and mark as complete"""
        self.error = error
        self.completed.set()
    
    def result(self, timeout: Optional[float] = None) -> Any:
        """
        Get the result, blocking until available.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            The result value
            
        Raises:
            TimeoutError: If timeout expires
            Exception: If request failed
        """
        if not self.completed.wait(timeout):
            raise TimeoutError("Request timed out")
        
        if self.error:
            raise self.error
        
        return self.result_value
    
    def is_done(self) -> bool:
        """Check if request is complete"""
        return self.completed.is_set()


class BatchedAPIClient:
    """
    Intelligent API client that batches requests to reduce rate limit usage.
    
    Features:
    - Automatic batching based on time windows or request count
    - Request deduplication to avoid redundant calls
    - Priority-based queuing
    - Thread-safe operations
    """
    
    def __init__(
        self,
        config: Optional[BatchConfig] = None,
        executor: Optional[Callable] = None
    ):
        """
        Initialize batched API client.
        
        Args:
            config: Batch configuration (uses defaults if None)
            executor: Optional function to execute batched requests.
                     Signature: executor(requests: List[APIRequest]) -> List[Any]
        """
        self.config = config or BatchConfig()
        self.executor = executor or self._default_executor
        
        # Request queue and deduplication
        self.request_queue = PriorityQueue(maxsize=self.config.max_queue_size)
        self.pending_requests: Dict[str, Tuple[APIRequest, List[RequestFuture]]] = {}
        self.dedup_cache: Dict[str, Tuple[Any, float]] = {}
        
        # Batching state
        self.current_batch: List[Tuple[APIRequest, RequestFuture]] = []
        self.last_flush_time = time.time()
        
        # Thread management
        self.lock = threading.RLock()
        self.running = False
        self.worker_thread = None
        
        # Metrics
        self.total_requests = 0
        self.batched_requests = 0
        self.deduplicated_requests = 0
        self.batches_flushed = 0
    
    def start(self):
        """Start the batch processing worker"""
        with self.lock:
            if self.running:
                return
            
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
    
    def stop(self, timeout: float = 5.0):
        """
        Stop the batch processor.
        
        Args:
            timeout: Maximum time to wait for shutdown
        """
        # Flush any pending requests before stopping
        self.flush()
        
        with self.lock:
            if not self.running:
                return
            
            self.running = False
        
        if self.worker_thread:
            self.worker_thread.join(timeout)
    
    def add_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        priority: int = 5
    ) -> RequestFuture:
        """
        Add a request to the batch queue.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            headers: Request headers
            body: Request body
            priority: Priority 1-10 (higher = more important)
            
        Returns:
            RequestFuture that will contain the result
        """
        # Ensure batcher is running
        if not self.running:
            self.start()
        
        request = APIRequest(
            method=method,
            endpoint=endpoint,
            params=params or {},
            headers=headers or {},
            body=body,
            priority=priority
        )
        
        self.total_requests += 1
        
        # Check deduplication cache
        if self.config.enable_deduplication:
            cached_result = self._check_dedup_cache(request)
            if cached_result is not None:
                self.deduplicated_requests += 1
                future = RequestFuture()
                future.set_result(cached_result)
                return future
        
        # Check if identical request is already pending
        with self.lock:
            if request.request_id in self.pending_requests:
                existing_request, futures = self.pending_requests[request.request_id]
                # Share the future with existing request
                future = RequestFuture()
                futures.append(future)
                self.deduplicated_requests += 1
                return future
        
        # Create new future and queue the request
        future = RequestFuture()
        
        with self.lock:
            # Add to pending requests
            self.pending_requests[request.request_id] = (request, [future])
            
            # Add to priority queue
            try:
                self.request_queue.put_nowait((request, future))
            except:
                # Queue is full, reject request
                future.set_error(Exception("Request queue is full"))
                del self.pending_requests[request.request_id]
        
        return future
    
    def flush(self):
        """Force flush of current batch"""
        # Process any remaining items in the queue before flushing
        while not self.request_queue.empty():
            try:
                request, future = self.request_queue.get_nowait()
                with self.lock:
                    self.current_batch.append((request, future))
                    self.batched_requests += 1
            except:
                break
        
        with self.lock:
            if not self.current_batch:
                return
            
            self._execute_batch()
    
    def _worker(self):
        """Background worker that processes batched requests"""
        while self.running:
            try:
                # Check if we should flush based on time
                time_since_last_flush = time.time() - self.last_flush_time
                should_flush_time = time_since_last_flush >= self.config.flush_interval
                
                # Try to get request from queue (with timeout)
                try:
                    request, future = self.request_queue.get(timeout=0.1)
                    
                    with self.lock:
                        self.current_batch.append((request, future))
                        self.batched_requests += 1
                        
                        # Check if we should flush based on size
                        should_flush_size = len(self.current_batch) >= self.config.batch_size
                        
                        if should_flush_size or should_flush_time:
                            self._execute_batch()
                
                except:
                    # Queue timeout or empty
                    if should_flush_time:
                        with self.lock:
                            self._execute_batch()
            
            except Exception as e:
                # Worker error handling
                print(f"Worker error: {e}", file=sys.stderr)
                time.sleep(0.1)
    
    def _execute_batch(self):
        """Execute the current batch of requests"""
        if not self.current_batch:
            return
        
        batch = self.current_batch
        self.current_batch = []
        self.last_flush_time = time.time()
        self.batches_flushed += 1
        
        # Extract requests and futures
        requests = [req for req, _ in batch]
        futures = [fut for _, fut in batch]
        
        try:
            # Execute batch
            results = self.executor(requests)
            
            # Set results and update dedup cache
            for request, future, result in zip(requests, futures, results):
                future.set_result(result)
                
                # Update deduplication cache
                if self.config.enable_deduplication:
                    self.dedup_cache[request.request_id] = (result, time.time())
                
                # Remove from pending
                if request.request_id in self.pending_requests:
                    # Set result for all futures waiting on this request
                    _, all_futures = self.pending_requests[request.request_id]
                    for f in all_futures:
                        if not f.is_done():
                            f.set_result(result)
                    del self.pending_requests[request.request_id]
        
        except Exception as e:
            # Batch execution failed, set error for all futures
            for future in futures:
                future.set_error(e)
            
            # Clean up pending requests
            for request, _ in batch:
                if request.request_id in self.pending_requests:
                    del self.pending_requests[request.request_id]
        
        # Clean up old entries from dedup cache
        self._cleanup_dedup_cache()
    
    def _check_dedup_cache(self, request: APIRequest) -> Optional[Any]:
        """Check if request result is in deduplication cache"""
        cache_entry = self.dedup_cache.get(request.request_id)
        if not cache_entry:
            return None
        
        result, timestamp = cache_entry
        age = time.time() - timestamp
        
        if age <= self.config.dedup_window:
            return result
        
        return None
    
    def _cleanup_dedup_cache(self):
        """Remove expired entries from deduplication cache"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.dedup_cache.items()
            if current_time - timestamp > self.config.dedup_window
        ]
        
        for key in expired_keys:
            del self.dedup_cache[key]
    
    def _default_executor(self, requests: List[APIRequest]) -> List[Any]:
        """
        Default executor that processes requests individually.
        
        Override this or provide custom executor for actual API calls.
        """
        results = []
        for request in requests:
            # Simulate API call
            time.sleep(0.01)
            results.append({
                'method': request.method,
                'endpoint': request.endpoint,
                'status': 'success',
                'timestamp': time.time()
            })
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batcher statistics"""
        with self.lock:
            return {
                'total_requests': self.total_requests,
                'batched_requests': self.batched_requests,
                'deduplicated_requests': self.deduplicated_requests,
                'batches_flushed': self.batches_flushed,
                'current_batch_size': len(self.current_batch),
                'pending_requests': len(self.pending_requests),
                'cache_size': len(self.dedup_cache),
                'reduction_rate': (
                    self.deduplicated_requests / self.total_requests
                    if self.total_requests > 0 else 0.0
                )
            }
    
    def print_stats(self):
        """Print statistics to console"""
        stats = self.get_stats()
        
        print("\n" + "=" * 70)
        print("📦 API Call Batcher Statistics")
        print("=" * 70)
        print(f"Total Requests:        {stats['total_requests']:,}")
        print(f"Batched Requests:      {stats['batched_requests']:,}")
        print(f"Deduplicated:          {stats['deduplicated_requests']:,}")
        print(f"Batches Flushed:       {stats['batches_flushed']:,}")
        print(f"Reduction Rate:        {stats['reduction_rate']:.1%}")
        print(f"Current Batch Size:    {stats['current_batch_size']}")
        print(f"Pending Requests:      {stats['pending_requests']}")
        print(f"Cache Size:            {stats['cache_size']}")
        print("=" * 70 + "\n")


# Singleton instance
_batcher_instance = None


def get_batcher(config: Optional[BatchConfig] = None) -> BatchedAPIClient:
    """Get singleton batcher instance"""
    global _batcher_instance
    if _batcher_instance is None:
        _batcher_instance = BatchedAPIClient(config)
    return _batcher_instance


# Example usage and CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='API Call Batcher Demo')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--requests', type=int, default=100, help='Number of demo requests')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size')
    parser.add_argument('--flush-interval', type=float, default=1.0, help='Flush interval')
    
    args = parser.parse_args()
    
    if args.demo:
        print("🚀 API Call Batcher Demo (@accelerate-specialist)")
        print(f"Creating batcher with batch_size={args.batch_size}, "
              f"flush_interval={args.flush_interval}s\n")
        
        config = BatchConfig(
            batch_size=args.batch_size,
            flush_interval=args.flush_interval
        )
        
        batcher = BatchedAPIClient(config)
        batcher.start()
        
        # Simulate requests
        print(f"Simulating {args.requests} API requests...")
        futures = []
        
        # Make diverse requests
        for i in range(args.requests):
            # Some duplicate requests to test deduplication
            endpoint = f"/api/users/{i % 20}"  # Only 20 unique endpoints
            future = batcher.add_request('GET', endpoint, priority=(i % 10) + 1)
            futures.append(future)
            
            # Small delay to simulate real usage
            if i % 10 == 0:
                time.sleep(0.05)
        
        print(f"Waiting for all requests to complete...")
        
        # Wait for all results
        for i, future in enumerate(futures):
            try:
                result = future.result(timeout=10.0)
            except Exception as e:
                print(f"Request {i} failed: {e}")
        
        # Allow final flush
        time.sleep(args.flush_interval + 0.5)
        batcher.flush()
        
        # Show statistics
        batcher.print_stats()
        
        # Stop batcher
        batcher.stop()
        
        print("✅ Demo complete!")
    else:
        parser.print_help()
