#!/usr/bin/env python3
"""
Integration Examples for API Coordination Hub

Demonstrates how to integrate the API Coordination Hub with existing
Chained tools like github_integration.py and fetch-web-content.py.
"""

import sys
import os

# Add tools directory to path
tools_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, tools_dir)

from api_coordination_hub import get_hub, APIConfig
from github_integration import GitHubAPIClient


def example_github_integration():
    """Example: Integrate with GitHub API client"""
    print("\n" + "="*70)
    print("Example 1: GitHub API Integration")
    print("="*70 + "\n")
    
    # Get hub and register GitHub API
    hub = get_hub()
    hub.register_api('github', APIConfig(
        rate_limit=5000,
        time_window=3600,
        circuit_breaker_threshold=5,
        priority=10
    ))
    
    # Create GitHub client
    client = GitHubAPIClient()
    
    # Wrap GitHub calls with coordination
    @hub.coordinate('github')
    def get_repo_info(owner, repo):
        """Get repository information with coordination"""
        return client.get(f'/repos/{owner}/{repo}')
    
    @hub.coordinate('github')
    def list_issues(owner, repo, state='open'):
        """List issues with coordination"""
        return client.get(f'/repos/{owner}/{repo}/issues', params={'state': state})
    
    try:
        # Make coordinated API calls
        print("Fetching repository information...")
        repo = get_repo_info('enufacas', 'Chained')
        print(f"✓ Repository: {repo['full_name']}")
        print(f"  Stars: {repo['stargazers_count']}")
        print(f"  Language: {repo['language']}")
        print()
        
        print("Fetching issues...")
        issues = list_issues('enufacas', 'Chained', state='open')
        print(f"✓ Found {len(issues)} open issues")
        for issue in issues[:3]:
            print(f"  #{issue['number']}: {issue['title']}")
        print()
        
        # Show metrics
        metrics = hub.get_metrics('github')
        print(f"API Metrics:")
        print(f"  Total requests: {metrics['total_requests']}")
        print(f"  Success rate: {metrics['success_rate']:.2%}")
        print(f"  Average latency: {metrics['average_latency']:.3f}s")
        print(f"  Available tokens: {hub.get_available_tokens('github')}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True


def example_multi_api_coordination():
    """Example: Coordinate multiple APIs"""
    print("\n" + "="*70)
    print("Example 2: Multi-API Coordination")
    print("="*70 + "\n")
    
    hub = get_hub()
    
    # Register multiple APIs with different configurations
    hub.register_api('github', APIConfig(
        rate_limit=5000,
        time_window=3600,
        priority=10
    ))
    
    hub.register_api('web', APIConfig(
        rate_limit=60,
        time_window=60,
        priority=5
    ))
    
    hub.register_api('database', APIConfig(
        rate_limit=1000,
        time_window=60,
        priority=8
    ))
    
    # Create mock functions for demonstration
    @hub.coordinate('github')
    def fetch_github_data():
        return {'source': 'github', 'data': 'sample'}
    
    @hub.coordinate('web')
    def fetch_web_data():
        return {'source': 'web', 'data': 'sample'}
    
    @hub.coordinate('database')
    def store_data(data):
        return {'stored': True, 'count': len(data)}
    
    try:
        # Orchestrate workflow
        print("Orchestrating multi-API workflow...")
        
        gh_data = fetch_github_data()
        print(f"✓ Fetched from GitHub: {gh_data}")
        
        web_data = fetch_web_data()
        print(f"✓ Fetched from web: {web_data}")
        
        result = store_data({**gh_data, **web_data})
        print(f"✓ Stored data: {result}")
        print()
        
        # Show status for all APIs
        print("API Status:")
        for api_name in ['github', 'web', 'database']:
            health = hub.get_health_status(api_name)
            tokens = hub.get_available_tokens(api_name)
            circuit = hub.get_circuit_state(api_name)
            print(f"  {api_name}: {health.value} | circuit: {circuit.value} | tokens: {tokens}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True


def example_error_handling():
    """Example: Error handling and resilience"""
    print("\n" + "="*70)
    print("Example 3: Error Handling and Resilience")
    print("="*70 + "\n")
    
    from api_coordination_hub import RateLimitExceeded, CircuitBreakerOpen
    
    hub = get_hub()
    hub.register_api('unreliable', APIConfig(
        rate_limit=5,
        time_window=60,
        circuit_breaker_threshold=3
    ))
    
    call_count = [0]
    
    @hub.coordinate('unreliable')
    def unreliable_call(should_fail=False):
        call_count[0] += 1
        if should_fail:
            raise Exception("Service error")
        return f"Success #{call_count[0]}"
    
    print("1. Demonstrating successful calls...")
    for i in range(3):
        try:
            result = unreliable_call()
            print(f"  ✓ Call {i+1}: {result}")
        except Exception as e:
            print(f"  ✗ Call {i+1}: {e}")
    
    print("\n2. Demonstrating rate limiting...")
    for i in range(5):
        try:
            result = unreliable_call()
            print(f"  ✓ Call {i+1}: Success")
        except RateLimitExceeded as e:
            print(f"  ⚠ Call {i+1}: Rate limited")
        except Exception as e:
            print(f"  ✗ Call {i+1}: {e}")
    
    print("\n3. Demonstrating circuit breaker...")
    # Reset for clean test
    hub.reset_circuit_breaker('unreliable')
    
    # Cause failures
    for i in range(4):
        try:
            result = unreliable_call(should_fail=True)
            print(f"  ✓ Call {i+1}: Success")
        except CircuitBreakerOpen as e:
            print(f"  ⚠ Call {i+1}: Circuit breaker open")
        except Exception as e:
            print(f"  ✗ Call {i+1}: Failed ({type(e).__name__})")
    
    print()
    print(f"Circuit state: {hub.get_circuit_state('unreliable').value}")
    print(f"Health status: {hub.get_health_status('unreliable').value}")
    
    return True


def example_metrics_export():
    """Example: Metrics collection and export"""
    print("\n" + "="*70)
    print("Example 4: Metrics Collection and Export")
    print("="*70 + "\n")
    
    hub = get_hub()
    
    # Ensure APIs are registered
    if not hub.is_registered('monitored'):
        hub.register_api('monitored', APIConfig(rate_limit=100))
    
    import time
    
    @hub.coordinate('monitored')
    def monitored_call(latency=0.1):
        time.sleep(latency)
        return "ok"
    
    print("Making monitored API calls...")
    for i in range(10):
        try:
            monitored_call(latency=0.05)
        except:
            pass
    
    print("✓ Completed 10 API calls")
    print()
    
    # Get metrics
    metrics = hub.get_metrics('monitored')
    print("Collected Metrics:")
    print(f"  Total requests: {metrics['total_requests']}")
    print(f"  Successful: {metrics['successful_requests']}")
    print(f"  Failed: {metrics['failed_requests']}")
    print(f"  Success rate: {metrics['success_rate']:.2%}")
    print(f"  Average latency: {metrics['average_latency']:.3f}s")
    print(f"  Min latency: {metrics['min_latency']:.3f}s")
    print(f"  Max latency: {metrics['max_latency']:.3f}s")
    print()
    
    # Export to file
    export_path = '/tmp/api_metrics_example.json'
    hub.export_metrics(export_path)
    print(f"✓ Metrics exported to {export_path}")
    
    # Read back to verify
    import json
    with open(export_path, 'r') as f:
        exported = json.load(f)
    
    print(f"  Exported {len(exported['apis'])} API(s)")
    print(f"  Timestamp: {exported['timestamp']}")
    
    return True


def example_status_dashboard():
    """Example: Status dashboard"""
    print("\n" + "="*70)
    print("Example 5: Status Dashboard")
    print("="*70 + "\n")
    
    hub = get_hub()
    
    # Register multiple APIs if not already registered
    api_configs = {
        'github': APIConfig(rate_limit=5000, time_window=3600, priority=10),
        'web': APIConfig(rate_limit=60, time_window=60, priority=5),
        'database': APIConfig(rate_limit=1000, time_window=60, priority=8)
    }
    
    for name, config in api_configs.items():
        if not hub.is_registered(name):
            hub.register_api(name, config)
    
    # Print status dashboard
    hub.print_status()
    
    return True


def main():
    """Run all examples"""
    print("="*70)
    print("API Coordination Hub - Integration Examples")
    print("="*70)
    
    examples = [
        ("Multi-API Coordination", example_multi_api_coordination),
        ("Error Handling", example_error_handling),
        ("Metrics Export", example_metrics_export),
        ("Status Dashboard", example_status_dashboard),
    ]
    
    # Note: GitHub integration requires valid token
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        examples.insert(0, ("GitHub Integration", example_github_integration))
    else:
        print("\nNote: Skipping GitHub integration example (no token found)")
        print("Set GITHUB_TOKEN or GH_TOKEN environment variable to enable")
    
    results = []
    for name, example_func in examples:
        try:
            success = example_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Example failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("Examples Summary")
    print("="*70 + "\n")
    
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
    
    print()
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"Passed: {passed}/{total}")
    
    return all(s for _, s in results)


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
