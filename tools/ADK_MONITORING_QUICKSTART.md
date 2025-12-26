# ADK Pipeline Monitoring Tools - Quick Start

## 🎯 Overview

**@create-botter** has created two powerful tools for monitoring and validating the ADK A2A Blog Pipeline:

1. **Dashboard** (`adk-pipeline-dashboard.py`) - Real-time monitoring
2. **Validator** (`validate-adk-pipeline.py`) - Infrastructure validation

## 🚀 Quick Start

### Prerequisites

```bash
pip install httpx
```

### Dashboard Usage

```bash
# Quick health check (returns 0 if all healthy)
./tools/adk-pipeline-dashboard.py check

# Full dashboard view
./tools/adk-pipeline-dashboard.py dashboard

# Agent health only
./tools/adk-pipeline-dashboard.py health

# Pipeline status only  
./tools/adk-pipeline-dashboard.py status
```

### Validator Usage

```bash
# Run comprehensive validation
./tools/validate-adk-pipeline.py

# Returns 0 if all checks pass, 1 if errors found
```

## 📊 Example Outputs

### Healthy System

```bash
$ ./tools/adk-pipeline-dashboard.py check

🔍 Checking agent health...

================================================================================
  🏥 Agent Health Status
================================================================================

✅ All agents are healthy and operational!

🔬 Academic Research Agent
   URL: http://localhost:8081
   Status: ✅ HEALTHY
   Response Time: 45ms
   Version: 1.0.0
   Skills: discover-topics, analyze-topic

📈 Google Trends Agent
   URL: http://localhost:8083
   Status: ✅ HEALTHY
   Response Time: 52ms
   Version: 1.0.0
   Skills: analyze-trends, get-keywords

✍️ Blog Writer Agent
   URL: http://localhost:8082
   Status: ✅ HEALTHY
   Response Time: 48ms
   Version: 1.0.0
   Skills: write-blog, deploy-blog


✅ All systems operational!
```

### Validation Success

```bash
$ ./tools/validate-adk-pipeline.py

================================================================================
  🔍 ADK Pipeline Infrastructure Validation
  @create-botter - Ensuring Quality & Reliability
================================================================================

📋 Validating Workflow File...
✅ Cron schedule: 0 */6 * * *
✅ Workflow file validation passed

📋 Validating Orchestrator...
✅ Orchestrator validation passed

📋 Validating Test Coverage...
✅ Test file validation passed

📋 Validating Documentation...
✅ Documentation validation passed

📋 Validating Agents Directory...
✅ Agents directory validation passed

📋 Validating Tracking Issue...
✅ Tracking issue found: #4065
   Title: 🤖 ADK A2A Blog Pipeline Status
✅ Tracking issue validation passed

================================================================================
  📊 Validation Summary
================================================================================

✅ All validations passed!

🎉 ADK Pipeline infrastructure is properly configured
   Ready for scheduled execution and manual triggers
```

## 🔗 CI/CD Integration

### GitHub Actions Example

```yaml
name: Validate ADK Pipeline

on:
  pull_request:
    paths:
      - '.github/workflows/adk-a2a-blog-pipeline.yml'
      - 'infrastructure/docker/adk-agents/**'
      - 'tests/test_adk_blog_pipeline.py'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install httpx
      
      - name: Validate infrastructure
        run: ./tools/validate-adk-pipeline.py
```

### Pre-Deployment Check

```bash
#!/bin/bash
# deploy-with-validation.sh

echo "🔍 Validating infrastructure..."
./tools/validate-adk-pipeline.py

if [ $? -eq 0 ]; then
  echo "✅ Validation passed - checking agent health..."
  ./tools/adk-pipeline-dashboard.py check
  
  if [ $? -eq 0 ]; then
    echo "✅ All systems ready - deploying..."
    gcloud run deploy ...
  else
    echo "❌ Agents not healthy - aborting deployment"
    exit 1
  fi
else
  echo "❌ Validation failed - fix issues before deploying"
  exit 1
fi
```

## 🎨 Advanced Usage

### Monitoring Loop

```bash
#!/bin/bash
# continuous-monitoring.sh

while true; do
  clear
  echo "=== ADK Pipeline Status ==="
  echo "Timestamp: $(date)"
  echo ""
  
  ./tools/adk-pipeline-dashboard.py dashboard
  
  echo ""
  echo "Next update in 60 seconds..."
  sleep 60
done
```

### Alert on Failure

```bash
#!/bin/bash
# alert-on-failure.sh

./tools/adk-pipeline-dashboard.py check

if [ $? -ne 0 ]; then
  # Send alert (example with curl to webhook)
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"⚠️ ADK Pipeline agents are unhealthy!"}' \
    "$SLACK_WEBHOOK_URL"
fi
```

### Custom Health Check

```python
#!/usr/bin/env python3
# custom-health-check.py

import asyncio
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from adk_pipeline_dashboard import AgentHealthChecker

async def main():
    checker = AgentHealthChecker(timeout=5.0)
    health = await checker.check_all_agents()
    
    # Custom logic
    unhealthy = [
        name for name, result in health.items()
        if not result["healthy"]
    ]
    
    if unhealthy:
        print(f"⚠️  Unhealthy agents: {', '.join(unhealthy)}")
        return 1
    else:
        print("✅ All agents healthy")
        return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

## 📚 Documentation

For complete documentation, see:

- **Dashboard Guide:** [docs/ADK_PIPELINE_DASHBOARD.md](../docs/ADK_PIPELINE_DASHBOARD.md)
- **Pipeline Status Guide:** [docs/ADK_PIPELINE_STATUS_GUIDE.md](../docs/ADK_PIPELINE_STATUS_GUIDE.md)
- **Implementation Details:** [docs/ADK_A2A_PIPELINE_IMPLEMENTATION.md](../docs/ADK_A2A_PIPELINE_IMPLEMENTATION.md)

## 🆘 Troubleshooting

### Dashboard shows all agents unhealthy

**Check:**
1. Are agents running? `ps aux | grep agent.py`
2. Correct URLs? Check environment variables
3. Network accessible? `curl http://localhost:8081/health`

### Validator shows warnings

**Common warnings:**
- "Could not query GitHub issues" - gh CLI not configured (OK in local dev)
- "Documentation seems incomplete" - Check file size

### Import errors

```bash
# Install required dependencies
pip install httpx

# For development
pip install -r infrastructure/docker/adk-agents/requirements.txt
```

## 💡 Tips

1. **Alias for convenience:**
   ```bash
   alias adk-health='./tools/adk-pipeline-dashboard.py check'
   alias adk-validate='./tools/validate-adk-pipeline.py'
   ```

2. **Watch mode:**
   ```bash
   watch -n 60 ./tools/adk-pipeline-dashboard.py dashboard
   ```

3. **JSON output (future):**
   ```bash
   # Parse for monitoring systems
   ./tools/adk-pipeline-dashboard.py check --json
   ```

---

**✨ Built by @create-botter** - Visionary infrastructure monitoring

For questions or enhancements, see the issue tracker or documentation.
