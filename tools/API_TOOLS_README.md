# 🔧 API Testing & Monitoring Tools

Production-ready tools for API contract validation and performance monitoring.

**Created by:** @investigate-champion  
**Mission:** idea:19 - Web API Innovation Investigation  
**Date:** 2025-11-16

---

## 📦 Tools Included

### 1. API Contract Validator (`api_contract_validator.py`)

Validates API responses against OpenAPI 3.0 specifications to ensure APIs adhere to their documented contracts.

**Use Cases:**
- Validate API responses in CI/CD pipelines
- Prevent breaking changes before deployment
- Ensure API compliance with specifications
- Test contract adherence during development

### 2. API Performance Monitor (`api_performance_monitor.py`)

Tracks API performance, reliability, and SLA compliance with comprehensive metrics.

**Use Cases:**
- Monitor production API performance
- Track SLA compliance (response times, error rates)
- Detect performance degradation
- Generate performance reports

---

## 🚀 Quick Start

### API Contract Validator

#### Installation

```bash
# No dependencies for JSON specs
# For YAML specs:
pip install pyyaml
```

#### Basic Usage

```bash
# Validate single endpoint
python tools/api_contract_validator.py \
  openapi.json \
  --endpoint /users/{id} \
  --method GET \
  --response response.json

# Run test suite
python tools/api_contract_validator.py \
  openapi.json \
  --test-suite test_cases.json
```

#### Python API

```python
from tools.api_contract_validator import APIContractValidator

# Initialize validator
validator = APIContractValidator('openapi.json')

# Validate response
response = {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
}

errors = validator.validate_response(
    endpoint='/users/{id}',
    method='GET',
    status_code=200,
    response=response
)

if errors:
    print("❌ Validation failed:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ Validation passed")
```

#### Test Suite Format

```json
[
  {
    "name": "Get user by ID",
    "endpoint": "/users/{id}",
    "method": "GET",
    "status_code": 200,
    "response": {
      "id": "123",
      "name": "John Doe",
      "email": "john@example.com"
    }
  },
  {
    "name": "Create user",
    "endpoint": "/users",
    "method": "POST",
    "status_code": 201,
    "response": {
      "id": "124",
      "name": "Jane Smith",
      "email": "jane@example.com"
    }
  }
]
```

### API Performance Monitor

#### Installation

```bash
# No dependencies required
```

#### Basic Usage

```python
from tools.api_performance_monitor import APIMonitor, monitor_function
import requests
import time

# Initialize monitor
monitor = APIMonitor(output_dir='metrics')

# Option 1: Track requests manually
monitor.track_request(
    endpoint='/api/users',
    method='GET',
    response_time=0.123,
    status_code=200
)

# Option 2: Use decorator for automatic tracking
@monitor_function(monitor, '/api/users', 'GET')
def get_users():
    return requests.get('https://api.example.com/users')

# Make requests
for _ in range(100):
    get_users()
    time.sleep(0.1)

# Print report
monitor.print_report(detailed=True)

# Check SLA compliance
sla_config = {
    'max_error_rate': 0.01,  # 1%
    'max_p95_response_time': 0.5,  # 500ms
    'max_p99_response_time': 1.0,  # 1 second
    'min_success_rate': 0.99  # 99%
}

results = monitor.check_all_slas(sla_config)
for result in results:
    if not result['sla_met']:
        print(f"❌ SLA violation: {result['endpoint']}")
        for violation in result['violations']:
            print(f"  - {violation}")

# Export metrics
monitor.export_json('metrics/report.json')
```

#### CLI Usage

```bash
# Print report from saved metrics
python tools/api_performance_monitor.py \
  --input metrics/report.json \
  --report \
  --detailed

# Check SLA compliance
python tools/api_performance_monitor.py \
  --input metrics/report.json \
  --check-sla sla_config.json
```

---

## 📊 Metrics Tracked

### API Contract Validator

- ✅ Schema compliance (types, required fields)
- ✅ Status code validity
- ✅ Property constraints (min/max, patterns)
- ✅ Required field presence
- ✅ Additional properties check
- ✅ Array constraints (min/max items)
- ✅ String constraints (length, pattern, enum)
- ✅ Number constraints (min/max, multipleOf)

### API Performance Monitor

#### Response Time Statistics
- Average response time
- Median response time
- P50, P75, P90, P95, P99 percentiles
- Min and max response times
- Standard deviation

#### Reliability Metrics
- Total requests
- Error count
- Error rate
- Success rate
- Status code breakdown

#### Throughput
- Requests per second
- Duration (first to last request)

#### SLA Compliance
- Max error rate threshold
- Max P95/P99 response time thresholds
- Min success rate threshold

---

## 🔄 Integration Examples

### CI/CD Pipeline (GitHub Actions)

```yaml
name: API Contract Tests

on: [push, pull_request]

jobs:
  test-api-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Validate API Contracts
        run: |
          python tools/api_contract_validator.py \
            specs/openapi.json \
            --test-suite tests/api_test_suite.json
      
      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: api-test-results
          path: test-results.xml
```

### Production Monitoring

```python
# monitor_production.py
from tools.api_performance_monitor import APIMonitor
import requests
import time
import schedule

monitor = APIMonitor(output_dir='metrics/production')

def check_api_health():
    endpoints = [
        ('https://api.example.com/users', '/users', 'GET'),
        ('https://api.example.com/orders', '/orders', 'GET'),
        ('https://api.example.com/products', '/products', 'GET'),
    ]
    
    for url, endpoint, method in endpoints:
        start = time.time()
        try:
            response = requests.get(url, timeout=5)
            elapsed = time.time() - start
            monitor.track_request(endpoint, method, elapsed, response.status_code)
            
            # Alert on errors
            if response.status_code >= 400:
                monitor.add_alert(
                    endpoint, method,
                    f"HTTP {response.status_code} error",
                    severity='error'
                )
        except Exception as e:
            elapsed = time.time() - start
            monitor.track_request(endpoint, method, elapsed, 500)
            monitor.add_alert(
                endpoint, method,
                f"Request failed: {str(e)}",
                severity='critical'
            )

def generate_report():
    # Check SLA compliance
    sla_config = {
        'max_error_rate': 0.01,
        'max_p95_response_time': 0.5,
        'min_success_rate': 0.99
    }
    
    results = monitor.check_all_slas(sla_config)
    
    # Send alerts for violations
    for result in results:
        if not result['sla_met']:
            for violation in result['violations']:
                print(f"🚨 SLA VIOLATION: {result['endpoint']} - {violation}")
                # Send to alerting system (PagerDuty, Slack, etc.)
    
    # Export metrics
    monitor.export_json()
    
    # Print report
    monitor.print_report(detailed=True)
    
    # Clear metrics for next period
    monitor.clear_metrics()

# Run checks every minute
schedule.every(1).minutes.do(check_api_health)

# Generate report every hour
schedule.every(1).hours.do(generate_report)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### Development Testing

```python
# test_api_integration.py
import pytest
from tools.api_contract_validator import APIContractValidator
from tools.api_performance_monitor import APIMonitor
import requests

validator = APIContractValidator('specs/openapi.json')
monitor = APIMonitor()

def test_get_user():
    """Test GET /users/{id} endpoint."""
    # Make request
    start = time.time()
    response = requests.get('http://localhost:8000/users/123')
    elapsed = time.time() - start
    
    # Track performance
    monitor.track_request('/users/{id}', 'GET', elapsed, response.status_code)
    
    # Validate contract
    errors = validator.validate_response(
        '/users/{id}',
        'GET',
        response.status_code,
        response.json()
    )
    
    assert not errors, f"Contract violations: {errors}"
    assert response.status_code == 200

def test_create_user():
    """Test POST /users endpoint."""
    user_data = {
        "name": "Test User",
        "email": "test@example.com"
    }
    
    start = time.time()
    response = requests.post('http://localhost:8000/users', json=user_data)
    elapsed = time.time() - start
    
    monitor.track_request('/users', 'POST', elapsed, response.status_code)
    
    errors = validator.validate_response(
        '/users',
        'POST',
        response.status_code,
        response.json()
    )
    
    assert not errors
    assert response.status_code == 201

@pytest.fixture(scope='session', autouse=True)
def report_metrics():
    """Print performance report after all tests."""
    yield
    monitor.print_report(detailed=True)
```

---

## 📋 Best Practices

### Contract Validation

1. **Document APIs First** - Write OpenAPI specs before implementation
2. **Validate in CI/CD** - Run contract tests on every commit
3. **Test All Status Codes** - Include success and error cases
4. **Use Realistic Data** - Test with production-like payloads
5. **Version Specifications** - Track API changes over time

### Performance Monitoring

1. **Set Realistic SLAs** - Based on actual usage patterns
2. **Monitor Continuously** - Track metrics in production
3. **Alert on Violations** - Immediate notification for issues
4. **Track Trends** - Compare metrics over time
5. **Optimize Based on Data** - Use P95/P99 to identify problems

### General

1. **Start Simple** - Begin with critical endpoints
2. **Automate Everything** - Integrate into existing workflows
3. **Document Findings** - Share insights with team
4. **Iterate Quickly** - Add more tests as needed
5. **Export Metrics** - Archive for historical analysis

---

## 🎯 Example OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: Example API
  version: 1.0.0
paths:
  /users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful response
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
                    type: string
                  name:
                    type: string
                  email:
                    type: string
                    format: email
        '404':
          description: User not found
```

---

## 🐛 Troubleshooting

### Contract Validator Issues

**Problem:** "Endpoint not found in spec"
- **Solution:** Check path parameter syntax (use {id} not :id)
- **Solution:** Verify endpoint exists in OpenAPI spec

**Problem:** "Type mismatch"
- **Solution:** Ensure response matches schema types exactly
- **Solution:** Check for null values if not allowed

**Problem:** "$ref not found"
- **Solution:** Verify all $ref paths are correct
- **Solution:** Ensure referenced components exist in spec

### Performance Monitor Issues

**Problem:** "No data collected"
- **Solution:** Ensure track_request() is called
- **Solution:** Check that decorator is properly applied

**Problem:** "Invalid percentile calculation"
- **Solution:** Need at least 1 data point for statistics
- **Solution:** Collect more samples before generating report

---

## 📚 Additional Resources

### OpenAPI Specification
- [OpenAPI 3.0 Spec](https://spec.openapis.org/oas/v3.0.0)
- [Swagger Editor](https://editor.swagger.io/)
- [OpenAPI Generator](https://openapi-generator.tech/)

### API Testing
- [REST API Testing Best Practices](https://swagger.io/resources/articles/best-practices-in-api-testing/)
- [API Contract Testing](https://martinfowler.com/bliki/ContractTest.html)

### Performance Monitoring
- [SLA Best Practices](https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli)
- [API Performance Metrics](https://www.moesif.com/blog/technical/monitoring/API-Monitoring-and-Performance-Best-Practices/)

---

## 🤝 Contributing

These tools were created as part of the Chained autonomous AI ecosystem investigation into API innovation trends.

**Improvements Welcome:**
- Additional validation rules
- More metrics and statistics
- Better error messages
- Performance optimizations
- Additional output formats

---

## 📄 License

These tools are part of the Chained project and follow the project's licensing terms.

---

**Created by @investigate-champion as part of Mission idea:19 - Web API Innovation Investigation**

*"The Analytical Engine weaves algebraic patterns, just as the Jacquard loom weaves flowers and leaves." - Ada Lovelace*
