#!/usr/bin/env python3
"""
API Call Batcher Integration Example

Demonstrates real-world integration with GitHub API, showing:
- Request batching to reduce API calls
- Integration with API Coordination Hub
- Deduplication of common requests
- Priority-based processing

Created by: @accelerate-specialist
"""

import time
import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api_call_batcher import BatchedAPIClient, BatchConfig
from api_coordination_hub import APICoordinationHub, APIConfig


def simulate_github_api_call(request):
    """Simulate a GitHub API call"""
    # In real scenario, this would be: requests.get(f"https://api.github.com{request.endpoint}")
    time.sleep(0.01)  # Simulate network latency
    
    return {
        'method': request.method,
        'endpoint': request.endpoint,
        'params': request.params,
        'status': 200,
        'data': {
            'login': 'user',
            'id': 12345,
            'type': 'User'
        }
    }


def batch_executor(requests):
    """Execute a batch of GitHub API requests"""
    print(f"  🔄 Executing batch of {len(requests)} requests")
    
    results = []
    for req in requests:
        result = simulate_github_api_call(req)
        results.append(result)
    
    return results


def example_basic_batching():
    """Example 1: Basic request batching"""
    print("\n" + "="*70)
    print("📦 Example 1: Basic Request Batching")
    print("="*70)
    
    config = BatchConfig(
        batch_size=5,
        flush_interval=1.0,
        enable_deduplication=True
    )
    
    batcher = BatchedAPIClient(config, executor=batch_executor)
    batcher.start()
    
    print("\n📤 Submitting 15 requests...")
    futures = []
    
    for i in range(15):
        future = batcher.add_request('GET', f'/users/user{i}')
        futures.append(future)
    
    print("⏳ Waiting for results...")
    for i, future in enumerate(futures):
        result = future.result(timeout=5.0)
        print(f"  ✓ Request {i+1} completed: {result['endpoint']}")
    
    # Show statistics
    print("\n📊 Statistics:")
    stats = batcher.get_stats()
    print(f"  • Total requests: {stats['total_requests']}")
    print(f"  • Batches flushed: {stats['batches_flushed']}")
    print(f"  • Requests per batch: {stats['total_requests'] / max(stats['batches_flushed'], 1):.1f}")
    
    batcher.stop()
    print("\n✅ Example complete!")


def example_deduplication():
    """Example 2: Request deduplication"""
    print("\n" + "="*70)
    print("🔍 Example 2: Request Deduplication")
    print("="*70)
    
    config = BatchConfig(
        batch_size=10,
        flush_interval=0.5,
        enable_deduplication=True,
        dedup_window=5.0
    )
    
    batcher = BatchedAPIClient(config, executor=batch_executor)
    batcher.start()
    
    print("\n📤 Submitting requests (many duplicates)...")
    
    # Submit many duplicate requests
    futures = []
    endpoints = ['/users/alice', '/users/bob', '/repos/owner/repo']
    
    for i in range(30):
        endpoint = endpoints[i % len(endpoints)]  # Cycle through endpoints
        future = batcher.add_request('GET', endpoint)
        futures.append(future)
        print(f"  + Request {i+1}: {endpoint}")
    
    print("\n⏳ Processing...")
    for future in futures:
        future.result(timeout=5.0)
    
    # Show deduplication results
    print("\n📊 Deduplication Results:")
    stats = batcher.get_stats()
    print(f"  • Total requests submitted: {stats['total_requests']}")
    print(f"  • Deduplicated requests: {stats['deduplicated_requests']}")
    print(f"  • Actual API calls: {stats['total_requests'] - stats['deduplicated_requests']}")
    print(f"  • Reduction rate: {stats['reduction_rate']:.1%}")
    print(f"  • API calls saved: {stats['deduplicated_requests']}")
    
    batcher.stop()
    print("\n✅ Deduplication example complete!")


def example_priority_queuing():
    """Example 3: Priority-based processing"""
    print("\n" + "="*70)
    print("⚡ Example 3: Priority-Based Processing")
    print("="*70)
    
    execution_order = []
    
    def tracking_executor(requests):
        """Track execution order"""
        for req in requests:
            execution_order.append((req.endpoint, req.priority))
        return batch_executor(requests)
    
    config = BatchConfig(batch_size=20, flush_interval=0.5)
    batcher = BatchedAPIClient(config, executor=tracking_executor)
    batcher.start()
    
    print("\n📤 Submitting requests with different priorities...")
    
    # Submit requests with mixed priorities
    futures = []
    
    # Low priority background tasks
    for i in range(5):
        future = batcher.add_request('GET', f'/repos/repo{i}', priority=2)
        futures.append(future)
        print(f"  🔵 Low priority: /repos/repo{i}")
    
    # Medium priority tasks
    for i in range(5):
        future = batcher.add_request('GET', f'/issues/{i}', priority=5)
        futures.append(future)
        print(f"  🟡 Medium priority: /issues/{i}")
    
    # High priority urgent tasks
    for i in range(5):
        future = batcher.add_request('GET', f'/alerts/{i}', priority=10)
        futures.append(future)
        print(f"  🔴 High priority: /alerts/{i}")
    
    print("\n⏳ Processing...")
    for future in futures:
        future.result(timeout=5.0)
    
    # Show execution order
    print("\n📊 Execution Order (by priority):")
    for endpoint, priority in execution_order[:10]:  # Show first 10
        print(f"  • {endpoint} (priority: {priority})")
    
    batcher.stop()
    print("\n✅ Priority queuing example complete!")


def example_with_coordination_hub():
    """Example 4: Integration with API Coordination Hub"""
    print("\n" + "="*70)
    print("🔗 Example 4: Integration with API Coordination Hub")
    print("="*70)
    
    # Set up coordination hub for rate limiting
    hub = APICoordinationHub()
    hub.register_api('github', APIConfig(
        rate_limit=100,
        time_window=60,
        circuit_breaker_threshold=5
    ))
    
    print("\n🔧 Coordination Hub configured:")
    print("  • Rate limit: 100 requests/minute")
    print("  • Circuit breaker threshold: 5 failures")
    
    def coordinated_executor(requests):
        """Execute with hub coordination"""
        results = []
        for req in requests:
            try:
                # Use hub for rate limiting and circuit breaking
                @hub.coordinate('github')
                def make_call():
                    return simulate_github_api_call(req)
                
                result = make_call()
                results.append(result)
            except Exception as e:
                print(f"  ⚠️  Request failed: {e}")
                results.append({'error': str(e)})
        
        return results
    
    # Create batcher with coordinated executor
    config = BatchConfig(batch_size=10, flush_interval=1.0)
    batcher = BatchedAPIClient(config, executor=coordinated_executor)
    batcher.start()
    
    print("\n📤 Submitting requests through both batcher and hub...")
    futures = []
    
    for i in range(20):
        future = batcher.add_request('GET', f'/users/user{i}')
        futures.append(future)
    
    print("⏳ Processing...")
    for future in futures:
        future.result(timeout=5.0)
    
    # Show combined statistics
    print("\n📊 Combined Statistics:")
    
    print("\n  Batcher Stats:")
    batcher_stats = batcher.get_stats()
    print(f"    • Total requests: {batcher_stats['total_requests']}")
    print(f"    • Batches flushed: {batcher_stats['batches_flushed']}")
    
    print("\n  Hub Stats:")
    hub_metrics = hub.get_metrics('github')
    if hub_metrics:
        print(f"    • Total requests: {hub_metrics['total_requests']}")
        print(f"    • Success rate: {hub_metrics['success_rate']:.1%}")
        print(f"    • Available tokens: {hub.get_available_tokens('github')}")
    
    batcher.stop()
    print("\n✅ Integration example complete!")


def example_high_volume_simulation():
    """Example 5: High-volume request simulation"""
    print("\n" + "="*70)
    print("🚀 Example 5: High-Volume Request Simulation")
    print("="*70)
    
    config = BatchConfig(
        batch_size=50,
        flush_interval=2.0,
        enable_deduplication=True,
        dedup_window=10.0
    )
    
    batcher = BatchedAPIClient(config, executor=batch_executor)
    batcher.start()
    
    print("\n📤 Simulating 500 requests (with duplicates)...")
    
    # Simulate realistic workload
    endpoints = [
        '/users/alice',
        '/users/bob',
        '/repos/owner/repo1',
        '/repos/owner/repo2',
        '/issues/123',
        '/pulls/456'
    ]
    
    futures = []
    start_time = time.time()
    
    for i in range(500):
        # Many requests to same endpoints
        endpoint = endpoints[i % len(endpoints)]
        priority = (i % 10) + 1  # Varied priorities
        
        future = batcher.add_request('GET', endpoint, priority=priority)
        futures.append(future)
        
        # Show progress every 100 requests
        if (i + 1) % 100 == 0:
            print(f"  • Submitted {i+1}/500 requests")
    
    print("\n⏳ Processing...")
    for future in futures:
        future.result(timeout=30.0)
    
    elapsed = time.time() - start_time
    
    # Final statistics
    print("\n📊 High-Volume Results:")
    stats = batcher.get_stats()
    print(f"  • Total requests: {stats['total_requests']}")
    print(f"  • Deduplicated: {stats['deduplicated_requests']}")
    print(f"  • Batches flushed: {stats['batches_flushed']}")
    print(f"  • Reduction rate: {stats['reduction_rate']:.1%}")
    print(f"  • Time elapsed: {elapsed:.2f}s")
    print(f"  • Throughput: {stats['total_requests']/elapsed:.1f} req/s")
    print(f"  • API calls saved: {stats['deduplicated_requests']}")
    
    batcher.stop()
    print("\n✅ High-volume simulation complete!")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("🚀 API Call Batcher Integration Examples")
    print("   Created by: @accelerate-specialist")
    print("="*70)
    
    try:
        example_basic_batching()
        time.sleep(0.5)
        
        example_deduplication()
        time.sleep(0.5)
        
        example_priority_queuing()
        time.sleep(0.5)
        
        example_with_coordination_hub()
        time.sleep(0.5)
        
        example_high_volume_simulation()
        
        print("\n" + "="*70)
        print("✅ All examples completed successfully!")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
