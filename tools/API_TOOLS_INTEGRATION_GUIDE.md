# 🌉 API Tools Integration Guide

**Created by:** @bridge-master (Tim Berners-Lee persona)  
**Mission:** idea:19 - Web API Innovation  
**Date:** 2025-11-16  
**Status:** Production Ready

> *"The power of the Web is in its universality. Access by everyone regardless of disability is an essential aspect."*  
> Let's make these APIs universally accessible! 🌐

---

## 🎯 Overview

Welcome, fellow bridge builders! This guide shows you how to integrate the API Contract Validator and API Performance Monitor into your workflows. Think of these tools as the **cables and supports** that hold your API bridges together.

**What you'll build:**
- Validated API contracts (no more surprise breaking changes!)
- Performance monitoring (catch slowdowns before users do!)
- Integration with existing Chained workflows
- A complete API testing pipeline

**Time to build:** 15-30 minutes  
**Complexity:** Intermediate  
**Humor level:** Collaborative with a twist 😄

---

## 📦 What's in the Toolkit?

### 1. API Contract Validator (`api_contract_validator.py`)
- **Created by:** @investigate-champion
- **Purpose:** Validate API responses against OpenAPI specs
- **Superpower:** Catches breaking changes before deployment
- **Best for:** CI/CD integration, contract testing

### 2. API Performance Monitor (`api_performance_monitor.py`)
- **Created by:** @investigate-champion  
- **Purpose:** Track response times, error rates, SLA compliance
- **Superpower:** Real-time performance insights
- **Best for:** Production monitoring, SLA validation

### 3. API Coordination Hub (`api_coordination_hub.py`)
- **Created by:** Coordinate Wizard (already exists!)
- **Purpose:** Rate limiting, circuit breakers, health monitoring
- **Superpower:** Service resilience and coordination
- **Best for:** Multi-API orchestration

---

## 🚀 Quick Start: Your First Integration

### Step 1: Set Up Your Environment

```bash
# Navigate to Chained repository
cd /home/runner/work/Chained/Chained

# Ensure tools are in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/tools"

# Install dependencies (if needed)
pip install pyyaml  # For YAML OpenAPI specs
```

### Step 2: Create an OpenAPI Specification

```yaml
# api_spec.yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
paths:
  /users/{id}:
    get:
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                type: object
                required:
                  - id
                  - name
                  - email
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  email:
                    type: string
                    format: email
                  created_at:
                    type: string
                    format: date-time
```

### Step 3: Validate Your First Response

```python
from tools.api_contract_validator import APIContractValidator

# Load spec
validator = APIContractValidator('api_spec.yaml')

# Your API response
response = {
    'id': 123,
    'name': 'Tim Berners-Lee',
    'email': 'tim@web.org',
    'created_at': '2025-11-16T10:00:00Z'
}

# Validate!
errors = validator.validate_response(
    endpoint='/users/123',
    method='GET',
    status_code=200,
    response=response
)

if errors:
    print("❌ Validation failed:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ API contract validated successfully!")
```

### Step 4: Monitor Performance

```python
from tools.api_performance_monitor import APIMonitor, monitor_function
import requests

# Create monitor
monitor = APIMonitor(output_dir='metrics')

# Decorate your API function
@monitor_function(monitor, '/api/users', 'GET')
def get_users():
    return requests.get('https://api.example.com/users')

# Make some calls
for _ in range(100):
    get_users()

# Check the results
monitor.print_report(detailed=True)
```

**Output:**
```
📊 API Performance Report
================================================
GET /api/users
  Requests: 100
  Error Rate: 2.00% (2 errors)
  Success Rate: 98.00%
  Avg Response: 0.234s
  P95 Response: 0.456s
```

---

## 🏗️ Integration Patterns

### Pattern 1: CI/CD Contract Testing

Perfect for **preventing breaking changes** before they reach production.

```python
#!/usr/bin/env python3
"""
CI/CD API Contract Test
Add this to your GitHub Actions workflow!
"""

import sys
import json
from api_contract_validator import APIContractValidator

def test_api_contracts():
    """Test all API endpoints against spec"""
    validator = APIContractValidator('openapi.yaml')
    
    # Load test cases
    with open('test_cases.json') as f:
        test_cases = json.load(f)
    
    # Validate all
    results = validator.validate_multiple(test_cases)
    
    # Report
    failed = sum(1 for errors in results.values() if errors)
    passed = len(results) - failed
    
    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print("\nFailures:")
        for name, errors in results.items():
            if errors:
                print(f"\n{name}:")
                for error in errors:
                    print(f"  - {error}")
        sys.exit(1)
    
    print("\n🎉 All API contracts validated!")
    sys.exit(0)

if __name__ == '__main__':
    test_api_contracts()
```

**GitHub Actions Integration:**
```yaml
# .github/workflows/api-contract-tests.yml
name: API Contract Tests
on: [push, pull_request]

jobs:
  validate-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pyyaml requests
      
      - name: Run contract tests
        run: |
          export PYTHONPATH="${PYTHONPATH}:${PWD}/tools"
          python tests/test_api_contracts.py
```

### Pattern 2: Real-Time Production Monitoring

Perfect for **catching performance issues** as they happen.

```python
"""
Production API Monitor
Run this alongside your production API to track performance
"""

from api_performance_monitor import APIMonitor
from api_coordination_hub import get_hub, APIConfig
import time

# Initialize monitors
monitor = APIMonitor(output_dir='metrics/production')
hub = get_hub()

# Register API
hub.register_api('production', APIConfig(
    rate_limit=10000,
    time_window=3600,
    circuit_breaker_threshold=10
))

# Coordinate and monitor
@hub.coordinate('production')
@monitor_function(monitor, '/api/data', 'GET')
def fetch_data():
    # Your API logic
    return data

# Check SLA every minute
def check_sla():
    sla_config = {
        'max_error_rate': 0.01,      # 1% error rate
        'max_p95_response_time': 0.5, # 500ms P95
        'min_success_rate': 0.99      # 99% success
    }
    
    results = monitor.check_all_slas(sla_config)
    
    for result in results:
        if not result['sla_met']:
            # Alert the team!
            alert_team(result['violations'])

# Run continuous monitoring
while True:
    time.sleep(60)
    check_sla()
    monitor.export_json()
```

### Pattern 3: Chained Workflow Integration

Perfect for **integrating with Chained's agent system**.

```python
"""
Chained Agent API Integration
Use this in your agent workflows!
"""

from api_contract_validator import APIContractValidator
from api_performance_monitor import APIMonitor
from api_coordination_hub import get_hub, APIConfig

class ChainedAPIBridge:
    """Bridge between Chained agents and external APIs"""
    
    def __init__(self, spec_path: str, api_name: str):
        self.validator = APIContractValidator(spec_path)
        self.monitor = APIMonitor(output_dir=f'metrics/{api_name}')
        self.hub = get_hub()
        
        # Register with hub
        self.hub.register_api(api_name, APIConfig(
            rate_limit=5000,
            time_window=3600
        ))
        
        self.api_name = api_name
    
    def call_api(self, endpoint: str, method: str, func, **kwargs):
        """
        Make coordinated, validated, monitored API call
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            func: Function that makes the actual API call
            **kwargs: Arguments to pass to func
        """
        # Coordinate through hub (rate limiting, circuit breaker)
        @self.hub.coordinate(self.api_name)
        @monitor_function(self.monitor, endpoint, method)
        def coordinated_call():
            return func(**kwargs)
        
        # Make the call
        response = coordinated_call()
        
        # Validate response
        if hasattr(response, 'json'):
            data = response.json()
            status = response.status_code
            
            errors = self.validator.validate_response(
                endpoint, method, status, data
            )
            
            if errors:
                print(f"⚠️  Contract validation warnings:")
                for error in errors:
                    print(f"  - {error}")
        
        return response
    
    def get_health_report(self):
        """Get comprehensive health report"""
        return {
            'health': self.hub.get_health_status(self.api_name),
            'metrics': self.monitor.get_all_stats(),
            'circuit': self.hub.get_circuit_state(self.api_name)
        }

# Usage in agent workflow
bridge = ChainedAPIBridge('specs/github.yaml', 'github')

def agent_task():
    """Example agent task using the bridge"""
    response = bridge.call_api(
        endpoint='/repos/owner/repo',
        method='GET',
        func=lambda: requests.get('https://api.github.com/repos/owner/repo')
    )
    
    # Check health
    health = bridge.get_health_report()
    if health['health'] != 'healthy':
        print(f"⚠️  API health degraded: {health}")
    
    return response
```

### Pattern 4: Multi-API Orchestration

Perfect for **coordinating multiple APIs** in a workflow.

```python
"""
Multi-API Workflow Orchestrator
Bridge multiple APIs together seamlessly
"""

from api_coordination_hub import get_hub, APIConfig
from api_performance_monitor import APIMonitor

class MultiAPIOrchestrator:
    """Orchestrate calls across multiple APIs"""
    
    def __init__(self):
        self.hub = get_hub()
        self.monitors = {}
        
        # Register APIs
        self._register_apis()
    
    def _register_apis(self):
        """Register all APIs used in workflow"""
        apis = {
            'github': APIConfig(rate_limit=5000, time_window=3600),
            'web': APIConfig(rate_limit=60, time_window=60),
            'storage': APIConfig(rate_limit=1000, time_window=60)
        }
        
        for name, config in apis.items():
            self.hub.register_api(name, config)
            self.monitors[name] = APIMonitor(output_dir=f'metrics/{name}')
    
    def execute_workflow(self):
        """Execute multi-API workflow"""
        results = {}
        
        # Step 1: Fetch from GitHub (high rate limit)
        @self.hub.coordinate('github')
        def fetch_github():
            return github_client.get('/data')
        
        results['github'] = fetch_github()
        
        # Step 2: Fetch from web (low rate limit)
        @self.hub.coordinate('web')
        def fetch_web():
            return web_client.get('/data')
        
        results['web'] = fetch_web()
        
        # Step 3: Store combined data (medium rate limit)
        @self.hub.coordinate('storage')
        def store_data():
            combined = {**results['github'], **results['web']}
            return storage_client.put(combined)
        
        results['storage'] = store_data()
        
        return results
    
    def get_orchestration_report(self):
        """Get health report for all APIs"""
        report = {}
        for name, monitor in self.monitors.items():
            report[name] = {
                'health': self.hub.get_health_status(name),
                'stats': monitor.get_all_stats(),
                'available_tokens': self.hub.get_available_tokens(name)
            }
        return report
```

---

## 🧪 Testing Strategies

### Unit Testing with Validation

```python
import unittest
from api_contract_validator import APIContractValidator

class TestAPIContracts(unittest.TestCase):
    def setUp(self):
        self.validator = APIContractValidator('spec.yaml')
    
    def test_valid_response(self):
        """Test that valid response passes validation"""
        response = {'id': 1, 'name': 'Test', 'email': 'test@example.com'}
        errors = self.validator.validate_response(
            '/users/1', 'GET', 200, response
        )
        self.assertEqual(len(errors), 0)
    
    def test_missing_required_field(self):
        """Test that missing required field is caught"""
        response = {'id': 1, 'name': 'Test'}  # Missing email
        errors = self.validator.validate_response(
            '/users/1', 'GET', 200, response
        )
        self.assertGreater(len(errors), 0)
        self.assertIn('email', str(errors))

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing with Monitoring

```python
import unittest
from api_performance_monitor import APIMonitor

class TestAPIPerformance(unittest.TestCase):
    def setUp(self):
        self.monitor = APIMonitor()
    
    def test_performance_tracking(self):
        """Test that performance is tracked correctly"""
        # Simulate requests
        for i in range(10):
            self.monitor.track_request(
                '/test', 'GET', 0.1 + i * 0.01, 200
            )
        
        stats = self.monitor.get_endpoint_stats('/test', 'GET')
        
        self.assertEqual(stats['total_requests'], 10)
        self.assertEqual(stats['error_count'], 0)
        self.assertAlmostEqual(stats['avg_response_time'], 0.145, places=2)
    
    def test_sla_compliance(self):
        """Test SLA checking"""
        # Add fast requests
        for _ in range(95):
            self.monitor.track_request('/test', 'GET', 0.1, 200)
        
        # Add slow requests
        for _ in range(5):
            self.monitor.track_request('/test', 'GET', 1.0, 200)
        
        sla_config = {
            'max_p95_response_time': 0.5,
            'min_success_rate': 0.99
        }
        
        results = self.monitor.check_all_slas(sla_config)
        self.assertEqual(len(results), 1)
        # P95 should fail (will be ~1.0s)

if __name__ == '__main__':
    unittest.main()
```

---

## 📊 Monitoring Dashboard

### Create a Simple Dashboard

```python
#!/usr/bin/env python3
"""
API Health Dashboard
Real-time monitoring of all your APIs
"""

import time
from api_coordination_hub import get_hub
from api_performance_monitor import APIMonitor

def print_dashboard():
    """Print beautiful dashboard to console"""
    hub = get_hub()
    
    print("\n" + "=" * 80)
    print("🌉 Bridge Master API Dashboard".center(80))
    print("=" * 80)
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Print status for each API
    hub.print_status()
    
    print("\n" + "=" * 80)
    print("Press Ctrl+C to stop monitoring")
    print("=" * 80)

def main():
    """Run dashboard in loop"""
    try:
        while True:
            print("\033[2J\033[H")  # Clear screen
            print_dashboard()
            time.sleep(5)  # Update every 5 seconds
    except KeyboardInterrupt:
        print("\n\nDashboard stopped. Thanks for monitoring! 🌉")

if __name__ == '__main__':
    main()
```

---

## 🚨 Error Handling Best Practices

### Graceful Degradation

```python
from api_coordination_hub import RateLimitExceeded, CircuitBreakerOpen

def robust_api_call():
    """Example of robust API calling with fallbacks"""
    try:
        # Try primary API
        return call_primary_api()
        
    except RateLimitExceeded as e:
        print(f"⚠️  Rate limited: {e}")
        # Wait and retry or use cache
        return get_cached_data()
        
    except CircuitBreakerOpen as e:
        print(f"🔴 Circuit breaker open: {e}")
        # Use fallback service
        return call_fallback_api()
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        # Last resort: return default data
        return get_default_data()
```

### Comprehensive Validation

```python
def validate_and_log(validator, endpoint, method, status, response):
    """Validate and log all issues"""
    errors = validator.validate_response(endpoint, method, status, response)
    
    if errors:
        print(f"\n⚠️  Validation issues for {method} {endpoint}:")
        
        # Categorize errors
        critical = [e for e in errors if 'required' in e.lower()]
        warnings = [e for e in errors if e not in critical]
        
        if critical:
            print("\n🔴 Critical Issues:")
            for error in critical:
                print(f"  - {error}")
        
        if warnings:
            print("\n⚠️  Warnings:")
            for error in warnings:
                print(f"  - {error}")
        
        return False
    
    return True
```

---

## 📚 Complete Example: GitHub Integration

Here's a **production-ready** example integrating all three tools:

```python
#!/usr/bin/env python3
"""
Complete GitHub API Integration Example
Demonstrates validation, monitoring, and coordination
"""

import requests
import json
from api_contract_validator import APIContractValidator
from api_performance_monitor import APIMonitor
from api_coordination_hub import get_hub, APIConfig

class GitHubAPIBridge:
    """Complete GitHub API integration with all tools"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = 'https://api.github.com'
        
        # Initialize tools
        self.validator = APIContractValidator('specs/github_openapi.yaml')
        self.monitor = APIMonitor(output_dir='metrics/github')
        self.hub = get_hub()
        
        # Register API
        self.hub.register_api('github', APIConfig(
            rate_limit=5000,
            time_window=3600,
            circuit_breaker_threshold=10,
            priority=10
        ))
    
    def _make_request(self, endpoint: str, method: str = 'GET'):
        """Make HTTP request with authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        if method == 'GET':
            return requests.get(url, headers=headers)
        # Add other methods as needed
    
    def get_repository(self, owner: str, repo: str):
        """
        Get repository information
        With validation, monitoring, and coordination!
        """
        endpoint = f'/repos/{owner}/{repo}'
        
        # Coordinate through hub
        @self.hub.coordinate('github')
        @monitor_function(self.monitor, endpoint, 'GET')
        def fetch():
            return self._make_request(endpoint, 'GET')
        
        # Make the call
        response = fetch()
        
        # Validate contract
        if response.status_code == 200:
            data = response.json()
            errors = self.validator.validate_response(
                endpoint, 'GET', 200, data
            )
            
            if errors:
                print(f"⚠️  Contract validation issues:")
                for error in errors:
                    print(f"  - {error}")
        
        return response.json()
    
    def get_health_report(self):
        """Get comprehensive health report"""
        stats = self.monitor.get_all_stats()
        health_status = self.hub.get_health_status('github')
        circuit_state = self.hub.get_circuit_state('github')
        
        return {
            'health_status': health_status.value,
            'circuit_state': circuit_state.value,
            'statistics': stats,
            'available_requests': self.hub.get_available_tokens('github')
        }
    
    def print_report(self):
        """Print beautiful report"""
        report = self.get_health_report()
        
        print("\n" + "=" * 60)
        print("🐙 GitHub API Health Report".center(60))
        print("=" * 60)
        
        print(f"\n🔗 Status: {report['health_status']}")
        print(f"⚡ Circuit: {report['circuit_state']}")
        print(f"🎫 Available Requests: {report['available_requests']}")
        
        if report['statistics']:
            stats = report['statistics'][0]
            print(f"\n📊 Performance:")
            print(f"  Total Requests: {stats['total_requests']}")
            print(f"  Success Rate: {stats['success_rate']:.2%}")
            print(f"  Avg Response: {stats['avg_response_time']:.3f}s")
            print(f"  P95 Response: {stats['p95_response_time']:.3f}s")
        
        print("\n" + "=" * 60)

# Usage
if __name__ == '__main__':
    bridge = GitHubAPIBridge(token='your_token_here')
    
    # Get repository info
    repo = bridge.get_repository('enufacas', 'Chained')
    print(f"\n✅ Repository: {repo['name']}")
    print(f"⭐ Stars: {repo['stargazers_count']}")
    
    # Print health report
    bridge.print_report()
```

---

## 🎓 Best Practices Summary

### ✅ DO:
1. **Always validate** contracts in CI/CD
2. **Monitor SLAs** in production
3. **Use coordination** for rate limiting
4. **Log errors** with context
5. **Export metrics** regularly
6. **Test error scenarios**
7. **Document your specs**

### ❌ DON'T:
1. **Skip validation** "because it works now"
2. **Ignore P95/P99** metrics (P50 lies!)
3. **Hardcode rate limits** (use config)
4. **Forget circuit breakers**
5. **Mix concerns** (separate validation/monitoring/coordination)

---

## 🔗 Integration Checklist

Before going to production, verify:

- [ ] OpenAPI spec is up-to-date
- [ ] All endpoints have test cases
- [ ] CI/CD pipeline includes contract tests
- [ ] Production monitoring is configured
- [ ] SLA thresholds are defined
- [ ] Alert system is connected
- [ ] Circuit breakers are tuned
- [ ] Rate limits have safety margins
- [ ] Metrics are exported to dashboard
- [ ] Error handling covers all scenarios
- [ ] Documentation is updated
- [ ] Team is trained on tools

---

## 🆘 Troubleshooting

### "Validation always fails"
- Check OpenAPI spec matches actual API
- Verify response structure
- Look for type mismatches
- Check required vs optional fields

### "Too many rate limit errors"
- Increase rate_limit in config
- Add request queuing
- Implement caching
- Use multiple API keys/tokens

### "Circuit breaker opens too often"
- Increase threshold
- Check API service health
- Add retry logic
- Tune timeout settings

### "Metrics show high latency"
- Optimize API calls
- Check network conditions
- Consider caching
- Use regional endpoints

---

## 📖 Further Reading

- [OpenAPI Specification](https://swagger.io/specification/)
- [API Design Best Practices](https://swagger.io/resources/articles/best-practices-in-api-design/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Rate Limiting Strategies](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

---

## 🎉 Conclusion

You're now equipped to build robust API integrations! These tools work together like the **cables, towers, and deck of a suspension bridge** - each component essential, all working in harmony.

Remember:
- **Validate** to prevent breaking changes
- **Monitor** to catch performance issues
- **Coordinate** to ensure resilience

Now go forth and build amazing API bridges! 🌉

---

**Questions? Ideas? Found a bug?**  
Open an issue in the Chained repository or ping **@bridge-master**!

*Built with collaboration and a twist of humor by @bridge-master* 🌐✨
