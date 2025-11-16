#!/usr/bin/env python3
"""
API Bridge Integration Example

Demonstrates how to integrate API Contract Validator, API Performance Monitor,
and API Coordination Hub into a cohesive API management system.

This example shows:
1. How to set up all three tools together
2. Real-world usage patterns
3. Error handling and recovery
4. Metrics collection and reporting

Created by: @bridge-master (Tim Berners-Lee persona)
Mission: idea:19 - Web API Innovation
Date: 2025-11-16

"The Web as I envisaged it, we have not seen it yet. The future is still so much bigger than the past."
Let's build that future with robust API bridges! 🌉
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import our bridge-building tools
try:
    from api_contract_validator import APIContractValidator
    from api_performance_monitor import APIMonitor, monitor_function
    from api_coordination_hub import (
        APICoordinationHub, APIConfig, 
        RateLimitExceeded, CircuitBreakerOpen,
        HealthStatus, CircuitState
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure tools are in PYTHONPATH: export PYTHONPATH=$PYTHONPATH:$(pwd)/tools")
    sys.exit(1)


class APIBridge:
    """
    Universal API Bridge
    
    Connects your application to external APIs with:
    - Contract validation (prevent breaking changes)
    - Performance monitoring (track SLAs)
    - Service coordination (rate limiting, circuit breakers)
    
    Think of this as the complete bridge infrastructure for your API calls!
    """
    
    def __init__(
        self, 
        api_name: str,
        spec_path: Optional[str] = None,
        config: Optional[APIConfig] = None,
        output_dir: str = 'metrics'
    ):
        """
        Initialize API Bridge
        
        Args:
            api_name: Name of the API (e.g., 'github', 'web')
            spec_path: Path to OpenAPI specification (optional)
            config: API configuration (optional, uses defaults if not provided)
            output_dir: Directory for metrics output
        """
        self.api_name = api_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize validator if spec provided
        self.validator = None
        if spec_path:
            try:
                self.validator = APIContractValidator(spec_path)
                print(f"✅ Contract validator loaded for {api_name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not load spec: {e}")
        
        # Initialize monitor
        self.monitor = APIMonitor(output_dir=str(self.output_dir / api_name))
        print(f"✅ Performance monitor initialized for {api_name}")
        
        # Initialize coordination hub
        self.hub = APICoordinationHub()
        
        # Register API with hub
        if config is None:
            config = APIConfig(
                rate_limit=1000,
                time_window=3600,
                circuit_breaker_threshold=5
            )
        
        self.hub.register_api(api_name, config)
        print(f"✅ API registered with coordination hub: {api_name}")
        
        self.stats = {
            'calls': 0,
            'validated': 0,
            'validation_errors': 0,
            'circuit_breaker_trips': 0,
            'rate_limit_hits': 0
        }
    
    def call(
        self,
        func: callable,
        endpoint: str,
        method: str = 'GET',
        validate: bool = True,
        expected_status: int = 200,
        *args,
        **kwargs
    ) -> Any:
        """
        Make coordinated, monitored, validated API call
        
        This is the main bridge method - it ties everything together!
        
        Args:
            func: Function that makes the actual API call
            endpoint: API endpoint path
            method: HTTP method
            validate: Whether to validate response against contract
            expected_status: Expected status code for validation
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            API response (or raises exception)
        """
        self.stats['calls'] += 1
        
        try:
            # Coordinate through hub (rate limiting + circuit breaker)
            @self.hub.coordinate(self.api_name)
            @monitor_function(self.monitor, endpoint, method)
            def coordinated_call():
                return func(*args, **kwargs)
            
            # Make the call
            response = coordinated_call()
            
            # Validate contract if validator available and validation requested
            if self.validator and validate and hasattr(response, 'json'):
                try:
                    data = response.json()
                    status = response.status_code
                    
                    errors = self.validator.validate_response(
                        endpoint, method, status, data
                    )
                    
                    self.stats['validated'] += 1
                    
                    if errors:
                        self.stats['validation_errors'] += 1
                        print(f"\n⚠️  Contract validation issues for {method} {endpoint}:")
                        for error in errors:
                            print(f"  - {error}")
                    else:
                        print(f"✅ Contract validated: {method} {endpoint}")
                        
                except Exception as e:
                    print(f"⚠️  Validation error: {e}")
            
            return response
            
        except RateLimitExceeded as e:
            self.stats['rate_limit_hits'] += 1
            print(f"🚦 Rate limit exceeded: {e}")
            raise
            
        except CircuitBreakerOpen as e:
            self.stats['circuit_breaker_trips'] += 1
            print(f"🔴 Circuit breaker open: {e}")
            raise
            
        except Exception as e:
            print(f"❌ API call failed: {e}")
            raise
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        health_status = self.hub.get_health_status(self.api_name)
        circuit_state = self.hub.get_circuit_state(self.api_name)
        available_tokens = self.hub.get_available_tokens(self.api_name)
        
        monitor_stats = self.monitor.get_all_stats()
        
        return {
            'api_name': self.api_name,
            'timestamp': datetime.now().isoformat(),
            'coordination': {
                'health_status': health_status.value if health_status else 'unknown',
                'circuit_state': circuit_state.value if circuit_state else 'unknown',
                'available_tokens': available_tokens
            },
            'performance': monitor_stats,
            'bridge_stats': self.stats
        }
    
    def print_report(self, detailed: bool = False):
        """Print beautiful health report"""
        report = self.get_health_report()
        
        print("\n" + "=" * 80)
        print(f"🌉 API Bridge Health Report: {self.api_name}".center(80))
        print("=" * 80)
        print(f"Time: {report['timestamp']}")
        
        # Coordination status
        coord = report['coordination']
        print(f"\n🔗 Coordination Status:")
        print(f"  Health: {coord['health_status']}")
        print(f"  Circuit: {coord['circuit_state']}")
        print(f"  Available Requests: {coord['available_tokens']}")
        
        # Bridge stats
        bridge = report['bridge_stats']
        print(f"\n🌉 Bridge Statistics:")
        print(f"  Total Calls: {bridge['calls']}")
        print(f"  Validated: {bridge['validated']}")
        print(f"  Validation Errors: {bridge['validation_errors']}")
        print(f"  Rate Limit Hits: {bridge['rate_limit_hits']}")
        print(f"  Circuit Breaker Trips: {bridge['circuit_breaker_trips']}")
        
        # Performance metrics
        if report['performance']:
            print(f"\n📊 Performance Metrics:")
            self.monitor.print_report(detailed=detailed)
        
        print("\n" + "=" * 80)
    
    def check_sla(self, sla_config: Dict) -> Dict:
        """
        Check SLA compliance
        
        Args:
            sla_config: SLA requirements (e.g., max_error_rate, max_p95_response_time)
            
        Returns:
            SLA check results
        """
        results = self.monitor.check_all_slas(sla_config)
        
        if results:
            result = results[0]
            if not result['sla_met']:
                print(f"\n🚨 SLA VIOLATION: {self.api_name}")
                for violation in result['violations']:
                    print(f"  - {violation}")
            else:
                print(f"\n✅ SLA compliance: {self.api_name}")
            
            return result
        
        return {'sla_met': True, 'violations': []}
    
    def export_metrics(self, filepath: Optional[str] = None) -> str:
        """Export all metrics to JSON"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.output_dir / f"{self.api_name}_bridge_metrics_{timestamp}.json"
        
        report = self.get_health_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Metrics exported to: {filepath}")
        return str(filepath)


class MultiBridge:
    """
    Multi-API Bridge Orchestrator
    
    Manages multiple API bridges and provides unified reporting.
    Perfect for workflows that use multiple APIs!
    """
    
    def __init__(self):
        self.bridges: Dict[str, APIBridge] = {}
    
    def add_bridge(
        self,
        api_name: str,
        spec_path: Optional[str] = None,
        config: Optional[APIConfig] = None
    ) -> APIBridge:
        """Add a new API bridge"""
        bridge = APIBridge(api_name, spec_path, config)
        self.bridges[api_name] = bridge
        return bridge
    
    def get_bridge(self, api_name: str) -> Optional[APIBridge]:
        """Get bridge by name"""
        return self.bridges.get(api_name)
    
    def print_unified_report(self, detailed: bool = False):
        """Print unified report for all bridges"""
        print("\n" + "=" * 80)
        print("🌉 Multi-Bridge Health Dashboard".center(80))
        print("=" * 80)
        print(f"Time: {datetime.now().isoformat()}")
        print(f"Active Bridges: {len(self.bridges)}")
        
        for api_name, bridge in self.bridges.items():
            print(f"\n{'─' * 80}")
            bridge.print_report(detailed=detailed)
        
        print("\n" + "=" * 80)
    
    def export_all_metrics(self, directory: str = 'metrics/multi_bridge'):
        """Export metrics for all bridges"""
        output_dir = Path(directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for api_name, bridge in self.bridges.items():
            filepath = output_dir / f"{api_name}_{timestamp}.json"
            bridge.export_metrics(str(filepath))
        
        print(f"\n✅ All metrics exported to: {output_dir}")


# ============================================================================
# EXAMPLE USAGE SCENARIOS
# ============================================================================

def example_1_basic_usage():
    """Example 1: Basic API Bridge Usage"""
    print("\n" + "=" * 80)
    print("Example 1: Basic API Bridge Usage")
    print("=" * 80)
    
    # Create bridge
    bridge = APIBridge(
        api_name='example_api',
        spec_path=None,  # No validation for this simple example
        config=APIConfig(rate_limit=100, time_window=60)
    )
    
    # Simulate some API calls
    def mock_api_call():
        """Mock API call"""
        time.sleep(0.1)  # Simulate network delay
        return type('Response', (), {'status_code': 200, 'json': lambda: {'data': 'success'}})()
    
    print("\nMaking 5 API calls...")
    for i in range(5):
        try:
            response = bridge.call(
                func=mock_api_call,
                endpoint='/test/endpoint',
                method='GET',
                validate=False  # No validator in this example
            )
            print(f"  Call {i+1}: Success")
        except Exception as e:
            print(f"  Call {i+1}: Failed - {e}")
    
    # Print report
    bridge.print_report()


def example_2_multi_api_orchestration():
    """Example 2: Multi-API Orchestration"""
    print("\n" + "=" * 80)
    print("Example 2: Multi-API Orchestration")
    print("=" * 80)
    
    # Create multi-bridge orchestrator
    orchestrator = MultiBridge()
    
    # Add multiple APIs
    github_bridge = orchestrator.add_bridge(
        'github',
        config=APIConfig(rate_limit=5000, time_window=3600)
    )
    
    web_bridge = orchestrator.add_bridge(
        'web',
        config=APIConfig(rate_limit=60, time_window=60)
    )
    
    # Simulate calls to different APIs
    def mock_github_call():
        time.sleep(0.05)
        return type('Response', (), {'status_code': 200})()
    
    def mock_web_call():
        time.sleep(0.15)
        return type('Response', (), {'status_code': 200})()
    
    print("\nMaking calls to multiple APIs...")
    
    for i in range(3):
        github_bridge.call(mock_github_call, '/repos/owner/repo', validate=False)
        print(f"  GitHub call {i+1}: Success")
    
    for i in range(2):
        web_bridge.call(mock_web_call, '/web/page', validate=False)
        print(f"  Web call {i+1}: Success")
    
    # Print unified report
    orchestrator.print_unified_report()


def example_3_sla_monitoring():
    """Example 3: SLA Monitoring"""
    print("\n" + "=" * 80)
    print("Example 3: SLA Monitoring")
    print("=" * 80)
    
    bridge = APIBridge(
        'monitored_api',
        config=APIConfig(rate_limit=1000, time_window=60)
    )
    
    # Simulate varied performance
    def fast_call():
        time.sleep(0.05)
        return type('Response', (), {'status_code': 200})()
    
    def slow_call():
        time.sleep(0.5)
        return type('Response', (), {'status_code': 200})()
    
    def error_call():
        return type('Response', (), {'status_code': 500})()
    
    print("\nSimulating API calls with varied performance...")
    
    # 90 fast calls
    for i in range(90):
        bridge.call(fast_call, '/fast', validate=False)
    
    # 5 slow calls
    for i in range(5):
        bridge.call(slow_call, '/slow', validate=False)
    
    # 5 error calls
    for i in range(5):
        bridge.call(error_call, '/error', validate=False)
    
    print(f"\nMade 100 total calls (90 fast, 5 slow, 5 errors)")
    
    # Check SLA
    sla_config = {
        'max_error_rate': 0.01,      # 1% max error rate
        'max_p95_response_time': 0.3, # 300ms P95
        'min_success_rate': 0.99      # 99% success rate
    }
    
    print(f"\nChecking SLA compliance...")
    print(f"  Max Error Rate: {sla_config['max_error_rate']:.1%}")
    print(f"  Max P95 Response: {sla_config['max_p95_response_time']}s")
    print(f"  Min Success Rate: {sla_config['min_success_rate']:.1%}")
    
    bridge.check_sla(sla_config)
    bridge.print_report(detailed=True)


def example_4_error_handling():
    """Example 4: Error Handling and Recovery"""
    print("\n" + "=" * 80)
    print("Example 4: Error Handling and Recovery")
    print("=" * 80)
    
    # Create bridge with low rate limit to trigger rate limiting
    bridge = APIBridge(
        'rate_limited_api',
        config=APIConfig(
            rate_limit=5,
            time_window=10,
            circuit_breaker_threshold=3
        )
    )
    
    def api_call():
        return type('Response', (), {'status_code': 200})()
    
    print("\nAttempting 10 calls with rate limit of 5 per 10 seconds...")
    
    successful = 0
    rate_limited = 0
    
    for i in range(10):
        try:
            bridge.call(api_call, '/test', validate=False)
            successful += 1
            print(f"  Call {i+1}: ✅ Success")
        except RateLimitExceeded:
            rate_limited += 1
            print(f"  Call {i+1}: 🚦 Rate limited")
        except Exception as e:
            print(f"  Call {i+1}: ❌ Error: {e}")
    
    print(f"\nResults:")
    print(f"  Successful: {successful}")
    print(f"  Rate Limited: {rate_limited}")
    
    bridge.print_report()


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("🌉 API Bridge Integration Examples".center(80))
    print("by @bridge-master (Tim Berners-Lee persona)".center(80))
    print("=" * 80)
    print("\n\"The Web is more a social creation than a technical one.\"")
    print("Let's create social bridges between systems! 🌐\n")
    
    try:
        # Run examples
        example_1_basic_usage()
        time.sleep(1)
        
        example_2_multi_api_orchestration()
        time.sleep(1)
        
        example_3_sla_monitoring()
        time.sleep(1)
        
        example_4_error_handling()
        
        print("\n" + "=" * 80)
        print("✅ All examples completed successfully!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Review the API_TOOLS_INTEGRATION_GUIDE.md")
        print("2. Adapt these examples to your use case")
        print("3. Add OpenAPI specs for contract validation")
        print("4. Integrate into your CI/CD pipeline")
        print("\n🌉 Happy bridge building! 🌉\n")
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted. Thanks for watching!")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
